'''
Core game logic for the simplified Monopoly Go! game.
Contains:
- Player, Dice classes
- Tile classes (Go, Property, Chance, Free Parking, Jail, Go To Jail, Tax)
- Board setup with 20 tiles
- Game class that manages turns, movement, purchasing, rent collection, jail rules, and chance events
This module is designed to be GUI-agnostic, exposing methods for the GUI to invoke actions and query state.
Update:
- Added internal event chain depth guard to prevent deep/infinite recursion from chained events.
- Unified tile processing via a guarded process_current_tile() method.
- Implemented immediate bankruptcy detection and property release via Game.check_bankruptcy.
- Added Game.game_over flag and game-over detection in end_turn; removed arbitrary -2000 threshold.
'''
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from chance_cards import ChanceDeck
START_MONEY = 1500
GO_SALARY = 200
JAIL_FINE = 50
MAX_DOUBLES_ALLOWED = 3
MAX_JAIL_ATTEMPTS = 3
class Dice:
    def roll(self) -> Tuple[int, int]:
        return random.randint(1, 6), random.randint(1, 6)
@dataclass
class Player:
    name: str
    color: str = "red"
    money: int = START_MONEY
    position: int = 0
    in_jail: bool = False
    jail_turns: int = 0
    get_out_of_jail_cards: int = 0
    properties: List[int] = field(default_factory=list)
    consecutive_doubles: int = 0
    bankrupt: bool = False
class Tile:
    def __init__(self, index: int, name: str):
        self.index = index
        self.name = name
    def land(self, game: "Game", player: Player) -> List[str]:
        return []
class GoTile(Tile):
    def __init__(self, index: int):
        super().__init__(index, "GO")
    def land(self, game: "Game", player: Player) -> List[str]:
        # Nothing special on landing; salary paid when passing handled by Game
        return [f"{player.name} landed on GO."]
class PropertyTile(Tile):
    def __init__(self, index: int, name: str, price: int, rent: int, color_group: str):
        super().__init__(index, name)
        self.price = price
        self.rent = rent
        self.color_group = color_group
        self.owner: Optional[Player] = None
    def land(self, game: "Game", player: Player) -> List[str]:
        messages = []
        if self.owner is None:
            game.pending_purchase_tile = self
            messages.append(f"{player.name} landed on unowned property {self.name}.")
        elif self.owner is player:
            messages.append(f"{player.name} landed on their own property {self.name}.")
        else:
            # Pay rent
            amount = self.rent
            player.money -= amount
            self.owner.money += amount
            messages.append(f"{player.name} pays ${amount} rent to {self.owner.name} for {self.name}.")
            # Check bankruptcy after rent payment
            game.check_bankruptcy(player)
        return messages
class ChanceTile(Tile):
    def __init__(self, index: int):
        super().__init__(index, "Chance")
    def land(self, game: "Game", player: Player) -> List[str]:
        messages = [f"{player.name} draws a Chance card..."]
        messages += game.chance_deck.draw(game, player)
        return messages
class FreeParkingTile(Tile):
    def __init__(self, index: int):
        super().__init__(index, "Free Parking")
    def land(self, game: "Game", player: Player) -> List[str]:
        collected = game.free_parking_pot
        game.free_parking_pot = 0
        player.money += collected
        return [f"{player.name} lands on Free Parking and collects ${collected}."]
class JailTile(Tile):
    def __init__(self, index: int):
        super().__init__(index, "Jail / Just Visiting")
    def land(self, game: "Game", player: Player) -> List[str]:
        return [f"{player.name} is just visiting jail."]
class GoToJailTile(Tile):
    def __init__(self, index: int, jail_index: int):
        super().__init__(index, "Go To Jail")
        self.jail_index = jail_index
    def land(self, game: "Game", player: Player) -> List[str]:
        game.send_to_jail(player)
        return [f"{player.name} is sent to Jail!"]
class TaxTile(Tile):
    def __init__(self, index: int, name: str, amount: int):
        super().__init__(index, name)
        self.amount = amount
    def land(self, game: "Game", player: Player) -> List[str]:
        player.money -= self.amount
        game.free_parking_pot += self.amount
        # Check bankruptcy after tax payment
        game.check_bankruptcy(player)
        return [f"{player.name} pays ${self.amount} in {self.name}. Added to Free Parking pot."]
class Board:
    def __init__(self):
        self.tiles: List[Tile] = []
        self.jail_index = 5
        self._build()
    def _build(self):
        # 20 tiles, indexes 0..19
        # 0: GO
        self.tiles.append(GoTile(0))
        # 1: Property
        self.tiles.append(PropertyTile(1, "Old Kent Road", 60, 2, "Brown"))
        # 2: Chance
        self.tiles.append(ChanceTile(2))
        # 3: Property
        self.tiles.append(PropertyTile(3, "Whitechapel Road", 60, 4, "Brown"))
        # 4: Tax
        self.tiles.append(TaxTile(4, "Income Tax", 100))
        # 5: Jail
        self.tiles.append(JailTile(5))
        # 6: Property
        self.tiles.append(PropertyTile(6, "The Angel Islington", 100, 6, "Light Blue"))
        # 7: Free Parking
        self.tiles.append(FreeParkingTile(7))
        # 8: Property
        self.tiles.append(PropertyTile(8, "Euston Road", 100, 6, "Light Blue"))
        # 9: Chance
        self.tiles.append(ChanceTile(9))
        # 10: Property
        self.tiles.append(PropertyTile(10, "Pentonville Road", 140, 10, "Pink"))
        # 11: Go To Jail
        self.tiles.append(GoToJailTile(11, self.jail_index))
        # 12: Property
        self.tiles.append(PropertyTile(12, "Pall Mall", 140, 10, "Pink"))
        # 13: Chance
        self.tiles.append(ChanceTile(13))
        # 14: Property
        self.tiles.append(PropertyTile(14, "Whitehall", 160, 12, "Orange"))
        # 15: Property
        self.tiles.append(PropertyTile(15, "Fleet Street", 160, 12, "Orange"))
        # 16: Chance
        self.tiles.append(ChanceTile(16))
        # 17: Property
        self.tiles.append(PropertyTile(17, "Trafalgar Square", 180, 14, "Red"))
        # 18: Tax
        self.tiles.append(TaxTile(18, "Luxury Tax", 100))
        # 19: Chance
        self.tiles.append(ChanceTile(19))
class Game:
    def __init__(self, players: List[Player]):
        self.players: List[Player] = players
        self.board = Board()
        self.dice = Dice()
        self.chance_deck = ChanceDeck()
        self.current_player_index: int = 0
        self.free_parking_pot: int = 0
        self.log: List[str] = []
        self.last_roll: Optional[Tuple[int, int]] = None
        self.pending_purchase_tile: Optional[PropertyTile] = None
        self.roll_again_allowed: bool = False
        self.turn_has_not_rolled: bool = True
        self.waiting_for_roll: Optional[bool] = True  # present for interface symmetry
        # Internal guard against deep event chains (e.g., chained Chance movements)
        self._event_chain_depth: int = 0
        self._event_chain_limit: int = 12
        # Game-over state
        self.game_over: bool = False
    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]
    def log_message(self, msg: str):
        self.log.append(msg)
    def check_bankruptcy(self, player: Player):
        # Immediate bankruptcy if money goes below 0
        if player.money < 0 and not player.bankrupt:
            player.bankrupt = True
            # Release owned properties back to bank
            for idx in list(player.properties):
                tile = self.board.tiles[idx]
                if hasattr(tile, "owner"):
                    tile.owner = None
            player.properties.clear()
            self.log_message(f"{player.name} is bankrupt and removed from play. Their properties return to the bank.")
    def move_player_steps(self, player: Player, steps: int) -> List[str]:
        messages = []
        old_pos = player.position
        new_pos = (player.position + steps) % len(self.board.tiles)
        # Handle passing GO (only for positive forward movement large enough to pass index 0)
        if steps > 0 and (player.position + steps) >= len(self.board.tiles):
            player.money += GO_SALARY
            messages.append(f"{player.name} passed GO and collected ${GO_SALARY}.")
        player.position = new_pos
        messages += self.process_current_tile(player)
        return messages
    def move_player_to(self, player: Player, target_index: int, award_go_salary: bool = True) -> List[str]:
        messages = []
        old_pos = player.position
        # Determine if GO should be awarded
        if award_go_salary and target_index < old_pos:
            player.money += GO_SALARY
            messages.append(f"{player.name} passed GO and collected ${GO_SALARY}.")
        player.position = target_index
        messages += self.process_current_tile(player)
        return messages
    def process_current_tile(self, player: Player) -> List[str]:
        # Guard against deep recursion due to chained events
        if self._event_chain_depth >= self._event_chain_limit:
            return ["Event chain limit reached."]
        self._event_chain_depth += 1
        try:
            tile = self.board.tiles[player.position]
            messages = tile.land(self, player)
            return messages
        finally:
            self._event_chain_depth -= 1
    def attempt_purchase_current_tile(self) -> str:
        tile = self.pending_purchase_tile
        player = self.current_player
        if tile is None or tile.owner is not None:
            return "No property available for purchase."
        if player.money < tile.price:
            return f"{player.name} cannot afford {tile.name} (${tile.price})."
        tile.owner = player
        player.money -= tile.price
        player.properties.append(tile.index)
        self.pending_purchase_tile = None
        return f"{player.name} bought {tile.name} for ${tile.price}."
    def send_to_jail(self, player: Player):
        player.in_jail = True
        player.jail_turns = 0
        player.position = self.board.jail_index
        player.consecutive_doubles = 0
        self.roll_again_allowed = False
        self.turn_has_not_rolled = False
        self.log_message(f"{player.name} is now in Jail.")
    def pay_jail_fine(self):
        player = self.current_player
        player.money -= JAIL_FINE
        self.free_parking_pot += JAIL_FINE
        # Check bankruptcy after paying the fine
        self.check_bankruptcy(player)
        player.in_jail = False
        player.jail_turns = 0
        self.log_message(f"{player.name} paid ${JAIL_FINE} to get out of Jail. You may now roll.")
        self.turn_has_not_rolled = True  # can roll now
    def use_get_out_of_jail_card(self):
        player = self.current_player
        if player.get_out_of_jail_cards > 0 and player.in_jail:
            player.get_out_of_jail_cards -= 1
            # Return card to deck
            self.chance_deck.return_get_out_of_jail_card()
            player.in_jail = False
            player.jail_turns = 0
            self.log_message(f"{player.name} used a Get Out of Jail Free card. You may now roll.")
            self.turn_has_not_rolled = True
    def attempt_jail_roll(self) -> Dict[str, Any]:
        player = self.current_player
        res = {"freed_and_moved": False}
        if not player.in_jail:
            return res
        d1, d2 = self.dice.roll()
        self.last_roll = (d1, d2)
        self.log_message(f"{player.name} attempts to roll doubles to get out of jail: rolled {d1} and {d2}.")
        if d1 == d2:
            # Freed and move the total
            player.in_jail = False
            player.jail_turns = 0
            total = d1 + d2
            self.log_message(f"Doubles! {player.name} is freed from Jail and moves {total} spaces.")
            msgs = self.move_player_steps(player, total)
            for m in msgs:
                self.log_message(m)
            # After moving on doubles out of jail, DO NOT get another roll in this turn
            self.roll_again_allowed = False
            self.turn_has_not_rolled = False
            res["freed_and_moved"] = True
        else:
            player.jail_turns += 1
            self.log_message(f"No doubles. Jail attempts used: {player.jail_turns}/{MAX_JAIL_ATTEMPTS}.")
            if player.jail_turns >= MAX_JAIL_ATTEMPTS:
                # Must pay fine and move by sum of dice rolled
                player.money -= JAIL_FINE
                self.free_parking_pot += JAIL_FINE
                # Check bankruptcy after paying the fine
                self.check_bankruptcy(player)
                player.in_jail = False
                player.jail_turns = 0
                total = d1 + d2
                self.log_message(f"Third failed attempt. {player.name} pays ${JAIL_FINE} and moves {total} spaces.")
                msgs = self.move_player_steps(player, total)
                for m in msgs:
                    self.log_message(m)
                self.turn_has_not_rolled = False
            else:
                # Turn ends
                self.turn_has_not_rolled = False
        return res
    def roll_and_move(self) -> Dict[str, Any]:
        player = self.current_player
        result: Dict[str, Any] = {}
        if player.in_jail:
            result["error"] = "Player is in jail."
            return result
        d1, d2 = self.dice.roll()
        self.last_roll = (d1, d2)
        total = d1 + d2
        self.log_message(f"{player.name} rolled {d1} and {d2} (total {total}).")
        # Handle doubles logic
        if d1 == d2:
            player.consecutive_doubles += 1
            if player.consecutive_doubles >= MAX_DOUBLES_ALLOWED:
                # Go to jail immediately
                self.log_message(f"{player.name} rolled doubles {MAX_DOUBLES_ALLOWED} times in a row!")
                self.send_to_jail(player)
                result["jailed_due_to_doubles"] = True
                self.roll_again_allowed = False
                self.turn_has_not_rolled = False
                return result
            else:
                self.roll_again_allowed = True
        else:
            player.consecutive_doubles = 0
            self.roll_again_allowed = False
        # Move player
        msgs = self.move_player_steps(player, total)
        for m in msgs:
            self.log_message(m)
        # After any landings, check if pending purchase is set for UI
        self.turn_has_not_rolled = False
        # If rolled doubles (and not jailed), allow another roll this turn
        if self.roll_again_allowed:
            self.log_message(f"{player.name} rolled doubles and may roll again.")
        return result
    def end_turn(self):
        # Advance to next active player
        next_index = self.current_player_index
        for i in range(len(self.players)):
            next_index = (next_index + 1) % len(self.players)
            if not self.players[next_index].bankrupt:
                break
        self.current_player_index = next_index
        # Reset per-turn flags
        self.roll_again_allowed = False
        self.turn_has_not_rolled = True
        self.pending_purchase_tile = None
        self.last_roll = None
        self.log_message(f"It is now {self.current_player.name}'s turn.")
        # Check for game over (one or zero active players remain)
        active = [p for p in self.players if not p.bankrupt]
        if len(active) <= 1:
            self.game_over = True
            winner = active[0].name if active else "No one"
            self.log_message(f"Game over! Winner: {winner}.")
    def return_get_out_of_jail_card_to_deck(self):
        self.chance_deck.return_get_out_of_jail_card()