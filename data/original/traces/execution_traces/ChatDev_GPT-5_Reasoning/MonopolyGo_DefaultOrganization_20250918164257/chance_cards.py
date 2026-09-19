'''
Chance card mechanics for the simplified Monopoly Go! game.
Defines:
- ChanceCard: encapsulates a description and an action function
- ChanceDeck: manages a shuffled deck of chance cards, including handling a single
  "Get Out of Jail Free" card that is kept by a player until used
Card actions can manipulate player money, movement, and jail status via the Game API.
Update:
- Route movement through game.move_player_to/move_player_steps only.
- Avoid direct calls to process_current_tile to ensure the event chain guard is applied.
- Invoke game.check_bankruptcy(player) after any debit-causing action (fines, repairs, chairman).
'''
import random
from typing import Callable, List, Optional
class ChanceCard:
    def __init__(self, description: str, action: Callable[["Game", "Player"], List[str]], is_get_out_of_jail: bool = False):
        self.description = description
        self.action = action
        self.is_get_out_of_jail = is_get_out_of_jail
    def apply(self, game, player) -> List[str]:
        return self.action(game, player)
class ChanceDeck:
    def __init__(self):
        # Build a simplified deck
        self.cards: List[ChanceCard] = []
        self._get_out_card_in_deck: bool = True  # whether GOOJF is available to draw
        self._build_cards()
        self.shuffle()
    def _build_cards(self):
        def move_to_go(game, player):
            msgs = [f"Chance: Advance to GO (Collect $200)."]
            msgs += game.move_player_to(player, 0, award_go_salary=True)
            return msgs
        def bank_pays_dividend(game, player):
            amount = 100
            player.money += amount
            return [f"Chance: Bank pays you dividend of ${amount}."]
        def go_to_jail(game, player):
            game.send_to_jail(player)
            return [f"Chance: Go directly to Jail. Do not pass GO, do not collect $200."]
        def pay_fine(game, player):
            amount = 50
            player.money -= amount
            game.free_parking_pot += amount
            # Bankruptcy check after debit
            game.check_bankruptcy(player)
            return [f"Chance: Pay fine of ${amount}. Added to Free Parking pot."]
        def collect_money(game, player):
            amount = 100
            player.money += amount
            return [f"Chance: You inherit ${amount}."]
        def move_back_3(game, player):
            # Move backwards without awarding GO salary, using guarded movement
            new_pos = (player.position - 3) % len(game.board.tiles)
            msgs = [f"Chance: Move back 3 spaces."]
            msgs += game.move_player_to(player, new_pos, award_go_salary=False)
            return msgs
        def advance_5_spaces(game, player):
            msgs = [f"Chance: Advance 5 spaces."]
            msgs += game.move_player_steps(player, 5)
            return msgs
        def repairs(game, player):
            # Simplified: pay $25 per property owned
            per = 25
            count = len(player.properties)
            total = per * count
            if total > 0:
                player.money -= total
                game.free_parking_pot += total
                # Bankruptcy check after debit
                game.check_bankruptcy(player)
                return [f"Chance: Property repairs. Pay ${per} x {count} = ${total}. Added to Free Parking pot."]
            else:
                return [f"Chance: No properties. No repair costs."]
        def chairman(game, player):
            # Pay $50 to each other player
            amount_each = 50
            total_paid = 0
            for p in game.players:
                if p is not player and not p.bankrupt:
                    player.money -= amount_each
                    p.money += amount_each
                    total_paid += amount_each
            # Bankruptcy check after debits
            game.check_bankruptcy(player)
            return [f"Chance: Elected Chairman. Pay ${amount_each} to each player. Total paid: ${total_paid}."]
        def get_out_of_jail(game, player):
            player.get_out_of_jail_cards += 1
            # Remove this card from deck until returned
            self._get_out_card_in_deck = False
            return [f"Chance: Get Out of Jail Free card received. Hold until needed."]
        # Add cards
        self.cards.extend([
            ChanceCard("Advance to GO", move_to_go),
            ChanceCard("Bank pays you dividend of $100", bank_pays_dividend),
            ChanceCard("Go to Jail", go_to_jail),
            ChanceCard("Pay fine of $50", pay_fine),
            ChanceCard("Inherit $100", collect_money),
            ChanceCard("Move back 3 spaces", move_back_3),
            ChanceCard("Advance 5 spaces", advance_5_spaces),
            ChanceCard("Property repairs: $25 per property", repairs),
            ChanceCard("Chairman of the Board: pay each player $50", chairman),
            ChanceCard("Get Out of Jail Free", get_out_of_jail, is_get_out_of_jail=True),
        ])
    def shuffle(self):
        random.shuffle(self.cards)
    def draw(self, game, player) -> List[str]:
        # draw until you get a card that's available (handle GOOJF uniqueness)
        # To avoid infinite loops if only card left is GOOJF and it's held, we track attempts
        attempts = 0
        while attempts < len(self.cards):
            card = self.cards.pop(0)
            # If it's GOOJF and currently held, place it at bottom and draw next
            if card.is_get_out_of_jail and not self._get_out_card_in_deck:
                self.cards.append(card)
                attempts += 1
                continue
            # Apply card
            messages = [f"Card: {card.description}"]
            messages += card.apply(game, player)
            # Place non-GOOJF card to bottom of deck; GOOJF is removed until returned
            if card.is_get_out_of_jail:
                # Keep card in deck order but mark unavailable until returned
                self.cards.append(card)
            else:
                self.cards.append(card)
            return messages
        # If all attempts failed (shouldn't happen), return a default message
        return ["No available Chance card could be drawn."]
    def return_get_out_of_jail_card(self):
        # Mark that GOOJF can be drawn again
        self._get_out_card_in_deck = True