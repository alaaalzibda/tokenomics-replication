'''
Tkinter GUI for the Dou Dizhu game. Provides visual hand display, bidding controls,
play/pass actions, last play info, and game status updates for a local human vs two AIs game.
'''
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Optional
from models import Card
from game import DouDizhuGame
class GameUI:
    """
    Tkinter-based UI for playing Dou Dizhu against two AI opponents.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dou Dizhu (Landlord) - ChatDev")
        self.game = DouDizhuGame()
        self.selected: Dict[int, bool] = {}  # card id(selected object) -> selected flag
        self.card_buttons: List[tk.Button] = []
        # Layout frames
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        self.center_frame = tk.Frame(self.root)
        self.center_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        # Top info labels
        self.status_label = tk.Label(self.top_frame, text="Welcome to Dou Dizhu!", font=("Arial", 14))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.new_game_btn = tk.Button(self.top_frame, text="New Round", command=self.new_round)
        self.new_game_btn.pack(side=tk.RIGHT, padx=8)
        # Left and right AI info
        self.left_info = tk.Label(self.center_frame, text="Left AI\nCards: 0", width=15, relief=tk.GROOVE)
        self.left_info.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        # Center play area
        self.play_area = tk.Frame(self.center_frame, relief=tk.RIDGE, borderwidth=2)
        self.play_area.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.last_play_label = tk.Label(self.play_area, text="No plays yet.", font=("Arial", 12))
        self.last_play_label.pack(pady=5)
        self.log_text = tk.Text(self.play_area, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.right_info = tk.Label(self.center_frame, text="Right AI\nCards: 0", width=15, relief=tk.GROOVE)
        self.right_info.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        # Bottom: human hand and controls
        self.hand_frame = tk.Frame(self.bottom_frame)
        self.hand_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.controls_frame = tk.Frame(self.bottom_frame)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        # Controls
        self.play_button = tk.Button(self.controls_frame, text="Play", command=self.on_play, state=tk.DISABLED)
        self.play_button.pack(side=tk.RIGHT, padx=5)
        self.pass_button = tk.Button(self.controls_frame, text="Pass", command=self.on_pass, state=tk.DISABLED)
        self.pass_button.pack(side=tk.RIGHT, padx=5)
        # Bidding controls
        self.bid_buttons = {}
        for val in [0, 1, 2, 3]:
            b = tk.Button(self.controls_frame, text=f"Bid {val}", command=lambda v=val: self.on_bid(v), state=tk.DISABLED)
            b.pack(side=tk.LEFT, padx=3)
            self.bid_buttons[val] = b
        self.new_round()
    def run(self):
        self.root.mainloop()
    def new_round(self):
        self.game.start_new_round()
        self.update_all()
        self.status_label.config(text="Bidding phase. Left AI starts.")
        self.enable_bidding_controls_if_needed()
        self.root.after(600, self.process_ai_bidding_loop)
    def process_ai_bidding_loop(self):
        # Continue auto-bidding for AI until it's human's turn or bidding ends
        while self.game.phase == "bidding":
            bidder_idx = self.game.bid_turn_idx
            bidder = self.game.players[bidder_idx]
            if bidder.is_human:
                self.status_label.config(text=f"Your turn to bid. Highest bid: {self.game.highest_bid}")
                self.enable_bidding_controls_if_needed()
                break
            else:
                res = self.game.process_ai_bid_if_needed()
                self.update_all()
                if self.game.phase != "bidding":
                    # Bidding finished
                    self.after_bidding_to_play()
                    return
        if self.game.phase == "bidding" and self.game.players[self.game.bid_turn_idx].is_human:
            # waiting for human bid
            return
        if self.game.phase == "play":
            self.after_bidding_to_play()
            return
    def enable_bidding_controls_if_needed(self):
        # Enable only during bidding and when it's human's turn
        enable = self.game.phase == "bidding" and self.game.players[self.game.bid_turn_idx].is_human
        for val, btn in self.bid_buttons.items():
            btn.config(state=tk.NORMAL if enable else tk.DISABLED)
            # Hide bids that cannot exceed current highest
            if enable and val > 0 and val <= self.game.highest_bid:
                btn.config(state=tk.DISABLED)
        # Always allow Bid 0 during human bid
        if enable:
            self.bid_buttons[0].config(state=tk.NORMAL)
    def on_bid(self, value: int):
        if self.game.phase != "bidding":
            return
        if not self.game.players[self.game.bid_turn_idx].is_human:
            return
        self.game.apply_bid(self.game.bid_turn_idx, value)
        self.update_all()
        # If bidding finished, go to play; else continue AI bidding loop
        if self.game.phase == "bidding":
            self.enable_bidding_controls_if_needed()
            self.root.after(400, self.process_ai_bidding_loop)
        elif self.game.phase == "play":
            self.after_bidding_to_play()
    def after_bidding_to_play(self):
        # Disable bidding controls
        for btn in self.bid_buttons.values():
            btn.config(state=tk.DISABLED)
        # Update status and start play
        if self.game.phase != "play":
            # redeal happened due to pass all
            self.status_label.config(text="All passed. New round dealt. Bidding again.")
            self.enable_bidding_controls_if_needed()
            self.root.after(600, self.process_ai_bidding_loop)
            return
        land = self.game.players[self.game.landlord_idx].name if self.game.landlord_idx is not None else "Unknown"
        self.status_label.config(text=f"Play phase. Landlord: {land}.")
        self.update_all()
        self.enable_play_controls_if_needed()
        self.root.after(600, self.ai_play_loop)
    def ai_play_loop(self):
        # Keep allowing AI to act while it's their turn and game not finished
        while self.game.phase == "play":
            if self.game.players[self.game.current_player_idx].is_human:
                self.enable_play_controls_if_needed()
                break
            action = self.game.ai_take_turn_if_needed()
            self.update_all()
            if self.game.phase == "finished":
                self.end_round_actions()
                break
        # if next to act is human, controls enabled by update_all
    def enable_play_controls_if_needed(self):
        enable = self.game.phase == "play" and self.game.players[self.game.current_player_idx].is_human
        # Pass enabled only if not starting the trick
        if enable:
            if self.game.is_start_of_trick():
                self.play_button.config(state=tk.NORMAL)
                self.pass_button.config(state=tk.DISABLED)
            else:
                self.play_button.config(state=tk.NORMAL)
                self.pass_button.config(state=tk.NORMAL)
        else:
            self.play_button.config(state=tk.DISABLED)
            self.pass_button.config(state=tk.DISABLED)
    def on_play(self):
        if self.game.phase != "play":
            return
        idx = 1  # human index fixed as middle
        selected_cards = self.get_selected_cards()
        if not selected_cards:
            messagebox.showinfo("Play", "Select cards to play.")
            return
        ok, msg = self.game.try_play(idx, selected_cards)
        if not ok:
            messagebox.showwarning("Invalid", msg)
        self.clear_selection()
        self.update_all()
        if self.game.phase == "finished":
            self.end_round_actions()
            return
        self.root.after(500, self.ai_play_loop)
    def on_pass(self):
        if self.game.phase != "play":
            return
        idx = 1
        ok, msg = self.game.try_pass(idx)
        if not ok:
            messagebox.showwarning("Cannot pass", msg)
            return
        self.clear_selection()
        self.update_all()
        if self.game.phase == "finished":
            self.end_round_actions()
            return
        self.root.after(500, self.ai_play_loop)
    def end_round_actions(self):
        # Disable controls, show messagebox of result
        self.play_button.config(state=tk.DISABLED)
        self.pass_button.config(state=tk.DISABLED)
        for btn in self.bid_buttons.values():
            btn.config(state=tk.DISABLED)
        res = self.game.message_log[-1] if self.game.message_log else "Round finished."
        if "wins" in res:
            messagebox.showinfo("Result", res)
        else:
            messagebox.showinfo("Result", "Round finished.")
        self.status_label.config(text="Round finished. Click 'New Round' to play again.")
    def update_all(self):
        # Update AI info labels
        left = self.game.players[0]
        you = self.game.players[1]
        right = self.game.players[2]
        left_text = f"{left.name}\nRole: {left.role}\nCards: {len(left.hand)}"
        right_text = f"{right.name}\nRole: {right.role}\nCards: {len(right.hand)}"
        self.left_info.config(text=left_text)
        self.right_info.config(text=right_text)
        # Update last play label
        if self.game.last_combination:
            last_p = self.game.players[self.game.last_player_idx].name if self.game.last_player_idx is not None else "Unknown"
            cards_str = self.game.format_cards(self.game.last_combination.cards)
            self.last_play_label.config(text=f"Last: {last_p} -> {cards_str} [{self.game.last_combination.type}]")
        else:
            self.last_play_label.config(text="No active combination. Start a new trick.")
        # Update log text
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        for line in self.game.message_log[-200:]:
            self.log_text.insert(tk.END, line + "\n")
        self.log_text.config(state=tk.DISABLED)
        # Render human hand
        self.render_hand(you.hand)
        # Update status line
        if self.game.phase == "bidding":
            who = self.game.players[self.game.bid_turn_idx].name
            self.status_label.config(text=f"Bidding: {who}'s turn. Highest bid: {self.game.highest_bid}")
        elif self.game.phase == "play":
            who = self.game.players[self.game.current_player_idx].name
            self.status_label.config(text=f"Play: {who}'s turn.")
        else:
            self.status_label.config(text="Round finished.")
        # Update controls
        self.enable_bidding_controls_if_needed()
        self.enable_play_controls_if_needed()
    def render_hand(self, hand: List[Card]):
        # Clear current hand frame
        for btn in self.card_buttons:
            btn.destroy()
        self.card_buttons = []
        self.selected.clear()
        # Create toggle buttons for each card
        for i, card in enumerate(hand):
            btn = tk.Button(self.hand_frame, text=card.display(), relief=tk.RAISED, width=4)
            btn.grid(row=0, column=i, padx=2, pady=4)
            self.selected[id(card)] = False
            btn.config(command=lambda b=btn, c=card: self.toggle_card(b, c))
            self.card_buttons.append(btn)
    def toggle_card(self, button: tk.Button, card: Card):
        cid = id(card)
        self.selected[cid] = not self.selected.get(cid, False)
        if self.selected[cid]:
            button.config(relief=tk.SUNKEN, bg="#d0f0d0")
        else:
            button.config(relief=tk.RAISED, bg=self.root.cget("bg"))
    def get_selected_cards(self) -> List[Card]:
        # Retrieve selected card objects from player's hand
        you = self.game.players[1]
        chosen = []
        for c in you.hand:
            if self.selected.get(id(c), False):
                chosen.append(c)
        return chosen
    def clear_selection(self):
        # Reset selections and button styles
        for btn in self.card_buttons:
            btn.config(relief=tk.RAISED, bg=self.root.cget("bg"))
        for k in list(self.selected.keys()):
            self.selected[k] = False