'''
Tkinter-based GUI for the simplified Monopoly Go! game.
Provides:
- Player setup dialog
- Board visualization
- Controls for rolling dice, handling jail options, buying properties, and ending turns
- Info panels for player status and game log
Integrates with the game logic implemented in game.py and chance_cards.py.
Update:
- Added game-over handling in controls and info panel.
- Buttons are disabled when the game is over and a one-time message is shown.
'''
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from game import Game, Player
from functools import partial
PLAYER_COLORS = ["red", "blue", "green", "purple"]
class SetupDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Game Setup")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        tk.Label(self, text="Number of Players (2-4):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.num_var = tk.IntVar(value=2)
        ttk.Spinbox(self, from_=2, to=4, textvariable=self.num_var, width=5).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.entries = []
        for i in range(4):
            tk.Label(self, text=f"Player {i+1} Name:").grid(row=i+1, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(self, width=20)
            entry.grid(row=i+1, column=1, sticky="w", padx=10, pady=5)
            if i < 2:
                entry.insert(0, f"Player {i+1}")
            self.entries.append(entry)
        ttk.Button(self, text="Start Game", command=self.on_start).grid(row=6, column=0, columnspan=2, pady=10)
    def on_start(self):
        n = self.num_var.get()
        names = []
        for i in range(n):
            name = self.entries[i].get().strip() or f"Player {i+1}"
            names.append(name)
        self.result = names
        self.destroy()
class BoardFrame(tk.Frame):
    def __init__(self, master, game: Game):
        super().__init__(master, bd=2, relief="groove")
        self.game = game
        self.tile_labels = []
        self.player_markers = {}  # (player -> label)
        # Configure grid weights correctly for 5 columns and 4 rows
        for c in range(5):
            self.grid_columnconfigure(c, weight=1)
        for r in range(4):
            self.grid_rowconfigure(r, weight=1)
        self._build_board()
    def _index_to_grid(self, idx):
        # Layout 20 tiles in a 5x4 grid, row-major
        row = idx // 5
        col = idx % 5
        return row, col
    def _build_board(self):
        for i, tile in enumerate(self.game.board.tiles):
            r, c = self._index_to_grid(i)
            frame = tk.Frame(self, bd=1, relief="ridge", bg="#f4f4f4")
            frame.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            name = tile.name
            label = tk.Label(frame, text=f"{i}: {name}", bg="#f4f4f4", anchor="w", justify="left", wraplength=140)
            label.pack(fill="x", padx=4, pady=(3, 0))
            owner_label = tk.Label(frame, text="", fg="black", bg="#f4f4f4", anchor="w", justify="left", wraplength=140)
            owner_label.pack(fill="x", padx=4, pady=(0, 3))
            marker_area = tk.Frame(frame, bg="#ffffff")
            marker_area.pack(fill="both", expand=True, padx=3, pady=3)
            self.tile_labels.append((label, owner_label, marker_area))
        self.update_board()
    def update_board(self):
        # Update owners and highlight current player position
        for i, tile in enumerate(self.game.board.tiles):
            label, owner_label, marker_area = self.tile_labels[i]
            # Set owner text for properties
            if hasattr(tile, "owner") and tile.owner is not None:
                owner_text = f"Owner: {tile.owner.name} | Rent: ${tile.rent} | Price: ${tile.price}"
            elif hasattr(tile, "price") and hasattr(tile, "rent"):
                owner_text = f"Unowned | Rent: ${tile.rent} | Price: ${tile.price}"
            else:
                owner_text = ""
            owner_label.config(text=owner_text)
            # Clear previous markers
            for child in list(marker_area.children.values()):
                child.destroy()
            # Place player markers on this tile
            players_here = [p for p in self.game.players if p.position == i and not p.bankrupt]
            for p in players_here:
                dot = tk.Canvas(marker_area, width=20, height=20, bg="#ffffff", highlightthickness=0)
                dot.create_oval(4, 4, 16, 16, fill=p.color, outline="black")
                dot.pack(side="left", padx=2, pady=2)
class InfoPanel(tk.Frame):
    def __init__(self, master, game: Game):
        super().__init__(master, bd=2, relief="groove")
        self.game = game
        self.status_text = tk.Text(self, height=12, width=40, state="disabled")
        self.status_text.pack(side="top", fill="x", padx=4, pady=4)
        self.log_text = tk.Text(self, height=16, width=40, state="disabled")
        self.log_text.pack(side="bottom", fill="both", expand=True, padx=4, pady=4)
        self.refresh()
    def refresh(self):
        # Update status
        self.status_text.config(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.insert("end", f"Free Parking Pot: ${self.game.free_parking_pot}\n")
        self.status_text.insert("end", "Players:\n")
        for p in self.game.players:
            status = "BANKRUPT" if p.bankrupt else "In Jail" if p.in_jail else "Active"
            self.status_text.insert("end", f"- {p.name} (${p.money}) | Pos {p.position} | {status} | GOOJF Cards: {p.get_out_of_jail_cards}\n")
        current = self.game.current_player
        self.status_text.insert("end", f"\nCurrent Turn: {current.name}\n")
        if self.game.last_roll:
            d1, d2 = self.game.last_roll
            self.status_text.insert("end", f"Last Roll: {d1} + {d2} = {d1+d2} ({'Doubles' if d1==d2 else 'No Doubles'})\n")
        if self.game.game_over:
            self.status_text.insert("end", "\nGAME OVER.\n")
        self.status_text.config(state="disabled")
        # Update log
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        for msg in self.game.log[-200:]:
            self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
class ControlPanel(tk.Frame):
    def __init__(self, master, game: Game, board_frame: BoardFrame, info_panel: InfoPanel):
        super().__init__(master, bd=2, relief="groove")
        self.game = game
        self.board_frame = board_frame
        self.info_panel = info_panel
        self.roll_btn = ttk.Button(self, text="Roll Dice", command=self.on_roll)
        self.roll_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.end_turn_btn = ttk.Button(self, text="End Turn", command=self.on_end_turn)
        self.end_turn_btn.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self.pay_jail_btn = ttk.Button(self, text="Pay $50 (Jail)", command=self.on_pay_jail)
        self.pay_jail_btn.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        self.attempt_doubles_btn = ttk.Button(self, text="Attempt Doubles (Jail)", command=self.on_attempt_doubles)
        self.attempt_doubles_btn.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        self.use_goojf_btn = ttk.Button(self, text="Use Get Out of Jail Free", command=self.on_use_goojf)
        self.use_goojf_btn.grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        # Track if we've already announced game over
        self.game_over_announced = False
        self.update_buttons()
    def prompt_purchase_if_needed(self):
        tile = self.game.pending_purchase_tile
        if tile is not None and tile.owner is None:
            player = self.game.current_player
            if player.bankrupt:
                self.game.log_message(f"{player.name} is bankrupt and cannot buy properties.")
                self.game.pending_purchase_tile = None
                return
            if player.money >= tile.price:
                buy = messagebox.askyesno("Buy Property?", f"{player.name}, do you want to buy {tile.name} for ${tile.price}? Rent: ${tile.rent}")
                if buy:
                    msg = self.game.attempt_purchase_current_tile()
                    self.game.log_message(msg)
                else:
                    self.game.log_message(f"{player.name} declined to purchase {tile.name}.")
            else:
                self.game.log_message(f"{player.name} cannot afford {tile.name} (${tile.price}).")
            self.game.pending_purchase_tile = None
    def on_roll(self):
        if self.game.game_over:
            messagebox.showinfo("Game Over", "The game has ended. See the log for details.")
            return
        player = self.game.current_player
        if player.in_jail:
            messagebox.showinfo("In Jail", "You must pay $50, use a Get Out of Jail Free card, or attempt to roll doubles.")
            return
        if player.bankrupt:
            messagebox.showwarning("Bankrupt", "This player is bankrupt. End the turn.")
            return
        result = self.game.roll_and_move()
        if result.get("jailed_due_to_doubles"):
            messagebox.showinfo("Go To Jail", f"{player.name} rolled three doubles in a row and was sent to Jail!")
        self.board_frame.update_board()
        self.info_panel.refresh()
        self.prompt_purchase_if_needed()
        self.board_frame.update_board()
        self.info_panel.refresh()
        self.update_buttons()
    def on_end_turn(self):
        if self.game.game_over:
            messagebox.showinfo("Game Over", "The game has ended. See the log for details.")
            return
        # Auto end if player cannot act further
        self.game.end_turn()
        self.board_frame.update_board()
        self.info_panel.refresh()
        self.update_buttons()
        current = self.game.current_player
        if self.game.game_over:
            # Announcement will be handled in update_buttons
            return
        if current.in_jail:
            # Prompt jail options
            self.game.log_message(f"{current.name} is in jail. Choose an option: Pay $50, Use GOOJF card, or Attempt Doubles.")
            self.info_panel.refresh()
    def on_pay_jail(self):
        if self.game.game_over:
            messagebox.showinfo("Game Over", "The game has ended. See the log for details.")
            return
        player = self.game.current_player
        if not player.in_jail:
            messagebox.showinfo("Not In Jail", "Current player is not in jail.")
            return
        if player.money < 50:
            messagebox.showwarning("Insufficient Funds", "You do not have $50 to pay.")
            return
        self.game.pay_jail_fine()
        self.board_frame.update_board()
        self.info_panel.refresh()
        self.update_buttons()
    def on_attempt_doubles(self):
        if self.game.game_over:
            messagebox.showinfo("Game Over", "The game has ended. See the log for details.")
            return
        player = self.game.current_player
        if not player.in_jail:
            messagebox.showinfo("Not In Jail", "Current player is not in jail.")
            return
        res = self.game.attempt_jail_roll()
        if res["freed_and_moved"]:
            self.board_frame.update_board()
            self.info_panel.refresh()
            self.prompt_purchase_if_needed()
        else:
            self.board_frame.update_board()
            self.info_panel.refresh()
        self.update_buttons()
    def on_use_goojf(self):
        if self.game.game_over:
            messagebox.showinfo("Game Over", "The game has ended. See the log for details.")
            return
        player = self.game.current_player
        if not player.in_jail:
            messagebox.showinfo("Not In Jail", "Current player is not in jail.")
            return
        if player.get_out_of_jail_cards <= 0:
            messagebox.showwarning("No Card", "You do not have a Get Out of Jail Free card.")
            return
        self.game.use_get_out_of_jail_card()
        self.board_frame.update_board()
        self.info_panel.refresh()
        self.update_buttons()
    def update_buttons(self):
        # If game is over, disable all actions and announce once
        if self.game.game_over:
            self.roll_btn.config(state="disabled")
            self.end_turn_btn.config(state="disabled")
            self.pay_jail_btn.config(state="disabled")
            self.attempt_doubles_btn.config(state="disabled")
            self.use_goojf_btn.config(state="disabled")
            if not self.game_over_announced:
                active = [p for p in self.game.players if not p.bankrupt]
                winner = active[0].name if active else "No one"
                messagebox.showinfo("Game Over", f"Game over! Winner: {winner}.")
                self.game_over_announced = True
            return
        p = self.game.current_player
        # If doubles were rolled, allow rolling again; else require end turn
        allow_roll_again = self.game.roll_again_allowed
        self.roll_btn.config(state=("normal" if (not p.in_jail and (allow_roll_again or self.game.turn_has_not_rolled)) else "disabled"))
        self.end_turn_btn.config(state=("normal" if (not allow_roll_again and not self.game.turn_has_not_rolled) or p.bankrupt else "disabled"))
        self.pay_jail_btn.config(state=("normal" if p.in_jail and p.money >= 50 else "disabled"))
        self.attempt_doubles_btn.config(state=("normal" if p.in_jail else "disabled"))
        self.use_goojf_btn.config(state=("normal" if p.in_jail and p.get_out_of_jail_cards > 0 else "disabled"))
class MonopolyApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Setup players
        names = self._prompt_players()
        players = []
        for i, name in enumerate(names):
            players.append(Player(name=name, color=PLAYER_COLORS[i % len(PLAYER_COLORS)]))
        self.game = Game(players)
        # Layout frames
        self.board_frame = BoardFrame(self, self.game)
        self.board_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=4, pady=4)
        self.info_panel = InfoPanel(self, self.game)
        self.info_panel.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self.controls = ControlPanel(self, self.game, self.board_frame, self.info_panel)
        self.controls.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        # Initial info
        self.game.log_message("Game started.")
        self.game.log_message(f"{self.game.current_player.name}'s turn.")
        self.info_panel.refresh()
    def _prompt_players(self):
        dlg = SetupDialog(self.master)
        self.wait_window(dlg)
        names = dlg.result or ["Player 1", "Player 2"]
        return names