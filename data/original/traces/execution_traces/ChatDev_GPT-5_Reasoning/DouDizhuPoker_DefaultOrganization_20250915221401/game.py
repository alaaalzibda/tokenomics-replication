'''
Core game engine for Dou Dizhu. Manages dealing, bidding, landlord assignment, playing turns,
pass-or-beat logic, and win conditions.
'''
from typing import List, Optional, Tuple
from collections import deque
from models import Card, Deck, sort_cards
from rules import Combination, identify_combination, can_beat, ROCKET, BOMB
from ai import SimpleAI
class Player:
    """
    Represents a player with a hand of cards. Can be human or AI.
    """
    def __init__(self, name: str, is_human: bool = False):
        self.name = name
        self.is_human = is_human
        self.hand: List[Card] = []
        self.role: str = "farmer"  # 'landlord' or 'farmer'
    def add_cards(self, cards: List[Card]):
        self.hand.extend(cards)
        self.sort_hand()
    def sort_hand(self):
        self.hand = sort_cards(self.hand)
    def remove_cards(self, cards: List[Card]):
        # Remove by object identity; cards passed should be exact objects from self.hand
        for c in cards:
            self.hand.remove(c)
    def has_cards(self) -> bool:
        return len(self.hand) > 0
class DouDizhuGame:
    """
    Game engine managing the state and flow of a Dou Dizhu round.
    """
    def __init__(self):
        self.players: List[Player] = [
            Player("Left AI"), Player("You", is_human=True), Player("Right AI")
        ]
        self.ai = SimpleAI()
        self.deck = Deck()
        self.bottom_cards: List[Card] = []
        self.landlord_idx: Optional[int] = None
        self.current_player_idx: int = 0
        self.phase: str = "deal"  # 'deal' | 'bidding' | 'play' | 'finished'
        self.highest_bid: int = 0
        self.best_bidder_idx: Optional[int] = None
        self.bids_since_highest: int = 0
        self.bid_turn_idx: int = 0
        self.last_combination: Optional[Combination] = None
        self.last_player_idx: Optional[int] = None
        self.message_log: List[str] = []
    def log(self, msg: str):
        self.message_log.append(msg)
        # debug printing can be added if needed
    def start_new_round(self):
        self.deck = Deck()
        hands, bottom = self.deck.deal()
        self.bottom_cards = bottom
        for i, p in enumerate(self.players):
            p.role = "farmer"
            p.hand = hands[i]
            p.sort_hand()
        self.phase = "bidding"
        self.highest_bid = 0
        self.best_bidder_idx = None
        self.bids_since_highest = 0
        # decide random starting bidder: keep middle (You) as bidder to improve interaction
        self.bid_turn_idx = 0  # Left AI starts bidding
        self.landlord_idx = None
        self.last_combination = None
        self.last_player_idx = None
    def get_state(self):
        return {
            "phase": self.phase,
            "players": self.players,
            "bottom": self.bottom_cards,
            "landlord_idx": self.landlord_idx,
            "current_idx": self.current_player_idx,
            "highest_bid": self.highest_bid,
            "best_bidder": self.best_bidder_idx,
            "last_comb": self.last_combination,
            "last_player": self.last_player_idx
        }
    def next_bidder(self):
        self.bid_turn_idx = (self.bid_turn_idx + 1) % 3
    def process_ai_bid_if_needed(self) -> Optional[Tuple[int, int]]:
        """
        If current bidder is AI, return (idx, bid_value). Otherwise None for human input handling.
        """
        if not self.phase == "bidding":
            return None
        bidder = self.players[self.bid_turn_idx]
        if bidder.is_human:
            return None
        bid = self.ai.decide_bid(bidder.hand, self.highest_bid)
        self.apply_bid(self.bid_turn_idx, bid)
        return (self.bid_turn_idx, bid)
    def apply_bid(self, idx: int, bid: int):
        if self.phase != "bidding":
            return
        # Ensure valid bid
        if bid not in (0, 1, 2, 3):
            bid = 0
        if bid > 0 and bid <= self.highest_bid:
            bid = 0
        if bid == 3:
            # immediate landlord
            self.highest_bid = 3
            self.best_bidder_idx = idx
            self.log(f"{self.players[idx].name} bids 3!")
            self.finish_bidding()
            return
        if bid > 0:
            self.highest_bid = bid
            self.best_bidder_idx = idx
            self.bids_since_highest = 0
            self.log(f"{self.players[idx].name} bids {bid}.")
        else:
            self.bids_since_highest += 1
            self.log(f"{self.players[idx].name} passes bidding.")
        # If two passes after a highest bid, bidding ends
        if self.best_bidder_idx is not None and self.bids_since_highest >= 2:
            self.finish_bidding()
            return
        # If all passed without any bid, redeal
        if self.best_bidder_idx is None and self.bids_since_highest >= 3:
            # redeal a new round
            self.log("All players passed. Redealing...")
            self.start_new_round()
            return
        # move to next bidder
        self.next_bidder()
    def finish_bidding(self):
        if self.best_bidder_idx is None:
            # edge case, but handle gracefully: choose random landlord (here fallback to player 0)
            self.best_bidder_idx = 0
        self.assign_landlord(self.best_bidder_idx)
    def assign_landlord(self, idx: int):
        self.landlord_idx = idx
        land = self.players[idx]
        land.role = "landlord"
        land.add_cards(self.bottom_cards)
        self.bottom_cards = []
        self.phase = "play"
        self.current_player_idx = self.landlord_idx
        self.last_combination = None
        self.last_player_idx = self.current_player_idx
        self.log(f"{land.name} is the landlord and starts the play.")
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]
    def next_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % 3
    def is_start_of_trick(self) -> bool:
        # start of trick if no active last_combination or the last player to play was the next to move
        if self.last_combination is None:
            return True
        return self.last_player_idx == self.current_player_idx
    def try_play(self, idx: int, cards: List[Card]) -> (bool, str):
        """
        Attempt to play cards from player idx. Returns (success, message).
        """
        if self.phase != "play" or idx != self.current_player_idx:
            return False, "Not your turn."
        # Validate the cards are in hand
        for c in cards:
            if c not in self.players[idx].hand:
                return False, "You don't have those cards."
        comb = identify_combination(cards)
        if comb is None:
            return False, "Invalid combination."
        # If starting a trick, any valid comb is okay; else must beat last
        if not self.is_start_of_trick():
            if not can_beat(comb, self.last_combination):
                return False, "Your play does not beat the current combination."
        # Apply play
        self.players[idx].remove_cards(cards)
        self.last_combination = comb
        self.last_player_idx = idx
        self.log(f"{self.players[idx].name} plays: {self.format_cards(cards)} [{comb.type}]")
        # Win check
        if not self.players[idx].has_cards():
            self.phase = "finished"
            # Determine winners: landlord vs farmers
            if self.players[idx].role == "landlord":
                self.log("Landlord wins!")
            else:
                self.log("Farmers win!")
            return True, "Game over."
        # Move to next turn
        self.next_turn()
        return True, "Played."
    def try_pass(self, idx: int) -> (bool, str):
        """
        Attempt to pass turn. Only valid if there is an active combination and the player is not starting the trick.
        """
        if self.phase != "play" or idx != self.current_player_idx:
            return False, "Not your turn."
        if self.is_start_of_trick():
            return False, "You cannot pass when starting a trick."
        self.log(f"{self.players[idx].name} passes.")
        self.next_turn()
        # If the turn returns to the last player who played, reset the trick explicitly
        if self.last_player_idx is not None and self.current_player_idx == self.last_player_idx:
            self.last_combination = None
            self.log("All others passed. Trick resets; free lead.")
        return True, "Passed."
    def ai_take_turn_if_needed(self) -> Optional[tuple]:
        """
        If it's an AI turn during play phase, make a move. Returns (action, cards or None) for UI updates.
        """
        if self.phase != "play":
            return None
        if self.players[self.current_player_idx].is_human:
            return None
        is_start = self.is_start_of_trick()
        play = self.ai.choose_play(self.players[self.current_player_idx].hand, self.last_combination, is_start)
        if play is None:
            # Must check if passing is allowed
            if not is_start:
                self.try_pass(self.current_player_idx)
                return ("pass", None)
            else:
                # If AI is starting but can't find play (shouldn't happen), play lowest single
                c = [self.players[self.current_player_idx].hand[0]]
                self.try_play(self.current_player_idx, c)
                return ("play", c)
        else:
            self.try_play(self.current_player_idx, play)
            return ("play", play)
    def format_cards(self, cards: List[Card]) -> str:
        return " ".join(c.display() for c in sorted(cards, key=lambda c: c.sort_key()))