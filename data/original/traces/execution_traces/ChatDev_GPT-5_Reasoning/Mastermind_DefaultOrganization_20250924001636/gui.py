'''
Mastermind Game - Tkinter GUI
Provides an interface to play Mastermind using MastermindGame from game_logic.py.
Features:
- Choose game settings: code length, attempts, duplicates, and symbol set (colors or digits).
- Pick symbols for each position via dropdowns.
- Submit guesses and display feedback (exact and partial matches).
- Track remaining attempts and show win/lose outcomes.
- Start a new game with the chosen settings.
- Keyboard shortcuts: Enter to submit guess, Ctrl+N to start a new game.
'''
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional
from game_logic import MastermindGame
class MastermindGUI:
    """
    Tkinter GUI wrapper for the Mastermind game.
    """
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the GUI and start a new game.
        """
        self.root = root
        # Default game instance (will be recreated on New Game with chosen settings)
        self.game = MastermindGame()  # Defaults: 4 positions, 10 attempts, duplicates allowed
        # UI state holders
        self.guess_vars: List[tk.StringVar] = []
        self.guess_menus: List[tk.OptionMenu] = []
        self.pos_labels: List[tk.Label] = []  # Track position labels to avoid duplication on New Game
        # Settings variables
        self.var_code_length = tk.IntVar(value=self.game.code_length)
        self.var_attempts = tk.IntVar(value=self.game.max_attempts)
        self.var_allow_dups = tk.BooleanVar(value=self.game.allow_duplicates)
        self.var_symbol_set = tk.StringVar(value="Colors")  # "Colors" or "Digits"
        self.var_seed = tk.StringVar(value="")
        # UI elements
        self.header_frame = tk.Frame(self.root, padx=10, pady=10)
        self.settings_frame = tk.Frame(self.root, padx=10, pady=6)
        self.guess_frame = tk.Frame(self.root, padx=10, pady=10)
        self.controls_frame = tk.Frame(self.root, padx=10, pady=10)
        self.history_frame = tk.Frame(self.root, padx=10, pady=10)
        self.history_listbox = tk.Listbox(self.history_frame, height=20, width=70)
        self.scrollbar = tk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.config(yscrollcommand=self.scrollbar.set)
        self.title_label = tk.Label(self.header_frame, text="Mastermind", font=("Arial", 18, "bold"))
        self.subtitle_label = tk.Label(
            self.header_frame,
            text=(
                "Guess the hidden code of symbols.\n"
                "Feedback: Exact = right symbol & position, Partial = right symbol wrong position."
            ),
            wraplength=600,
            justify="left",
        )
        # Settings controls
        self.settings_title = tk.Label(self.settings_frame, text="Settings:", font=("Arial", 12, "bold"))
        self.lbl_len = tk.Label(self.settings_frame, text="Code length:")
        self.opt_len = tk.OptionMenu(self.settings_frame, self.var_code_length, *[3, 4, 5, 6])
        self.lbl_attempts = tk.Label(self.settings_frame, text="Attempts:")
        self.opt_attempts = tk.OptionMenu(self.settings_frame, self.var_attempts, *[6, 8, 10, 12])
        self.chk_dups = tk.Checkbutton(self.settings_frame, text="Allow duplicates", variable=self.var_allow_dups)
        self.lbl_symbols = tk.Label(self.settings_frame, text="Symbol set:")
        self.opt_symbols = tk.OptionMenu(self.settings_frame, self.var_symbol_set, "Colors", "Digits")
        self.lbl_seed = tk.Label(self.settings_frame, text="Seed (optional):")
        self.ent_seed = tk.Entry(self.settings_frame, textvariable=self.var_seed, width=10)
        self.attempts_label = tk.Label(self.controls_frame, text="", font=("Arial", 12))
        self.submit_btn = tk.Button(self.controls_frame, text="Submit Guess", command=self._on_submit_guess)
        self.new_game_btn = tk.Button(self.controls_frame, text="New Game", command=self._on_new_game_click)
        self._build_ui()
        self._new_game_init()
        # Convenience: Enter key submits guess, Ctrl+N starts new game
        self.root.bind("<Return>", self._on_submit_guess_event)
        self.root.bind("<Control-n>", self._on_new_game_event)
    # ------ UI Construction ------
    def _build_ui(self) -> None:
        """
        Build and layout static UI components.
        """
        # Header
        self.header_frame.pack(fill="x")
        self.title_label.pack(anchor="w")
        self.subtitle_label.pack(anchor="w", pady=(4, 0))
        # Settings
        self.settings_frame.pack(fill="x", pady=(8, 0))
        self.settings_title.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.lbl_len.grid(row=0, column=1, sticky="e")
        self.opt_len.grid(row=0, column=2, sticky="w", padx=(4, 12))
        self.lbl_attempts.grid(row=0, column=3, sticky="e")
        self.opt_attempts.grid(row=0, column=4, sticky="w", padx=(4, 12))
        self.chk_dups.grid(row=0, column=5, sticky="w", padx=(4, 12))
        self.lbl_symbols.grid(row=1, column=1, sticky="e", pady=(6, 0))
        self.opt_symbols.grid(row=1, column=2, sticky="w", padx=(4, 12), pady=(6, 0))
        self.lbl_seed.grid(row=1, column=3, sticky="e", pady=(6, 0))
        self.ent_seed.grid(row=1, column=4, sticky="w", padx=(4, 12), pady=(6, 0))
        # Guess inputs
        guess_title = tk.Label(self.guess_frame, text="Your Guess:", font=("Arial", 12, "bold"))
        guess_title.grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.guess_frame.pack(fill="x")
        # Controls (submit/new game + attempts)
        self.controls_frame.pack(fill="x", pady=(6, 0))
        self.submit_btn.grid(row=0, column=0, padx=(0, 8))
        self.new_game_btn.grid(row=0, column=1, padx=(0, 8))
        self.attempts_label.grid(row=0, column=2, padx=(12, 0))
        # History list
        history_title = tk.Label(self.history_frame, text="History:", font=("Arial", 12, "bold"))
        history_title.pack(anchor="w")
        self.history_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.history_frame.pack(fill="both", expand=True, pady=(8, 0))
    # ------ Game Setup Helpers ------
    @staticmethod
    def _color_symbols() -> List[str]:
        """
        Return a robust default set of color names recognized by Tkinter.
        """
        return [
            "red", "green", "blue", "yellow",
            "orange", "purple", "cyan", "magenta",
        ]
    @staticmethod
    def _digit_symbols() -> List[str]:
        """
        Return a default set of digit symbols as strings.
        """
        return [str(d) for d in range(10)]  # "0" through "9"
    def _symbols_from_setting(self) -> List[str]:
        """
        Determine symbol set based on current settings.
        """
        symset = self.var_symbol_set.get()
        if symset == "Digits":
            return self._digit_symbols()
        return self._color_symbols()
    def _parse_seed(self) -> Optional[int]:
        """
        Parse the optional seed field and return an int or None.
        """
        raw = self.var_seed.get().strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            messagebox.showerror("Invalid Seed", "Seed must be an integer or left blank.")
            return None
    # ------ New Game Initialization ------
    def _new_game_init(self) -> None:
        """
        Prepare a new game state with current settings and reset UI components accordingly.
        """
        # Read settings
        code_len = int(self.var_code_length.get())
        attempts = int(self.var_attempts.get())
        allow_dups = bool(self.var_allow_dups.get())
        symbols = self._symbols_from_setting()
        seed = self._parse_seed()
        # Validate symbols vs code length if duplicates are disallowed
        if not allow_dups and code_len > len(symbols):
            messagebox.showerror(
                "Invalid Settings",
                "Code length cannot exceed number of available symbols when duplicates are not allowed.\n"
                "Either enable duplicates, reduce code length, or choose a symbol set with more symbols."
            )
            return
        # Create a new game with selected settings
        self.game = MastermindGame(
            code_length=code_len,
            colors=symbols,
            max_attempts=attempts,
            allow_duplicates=allow_dups,
            seed=seed,
        )
        # Clear existing guess inputs: option menus and position labels
        for menu in self.guess_menus:
            menu.destroy()
        self.guess_menus.clear()
        for lbl in self.pos_labels:
            lbl.destroy()
        self.pos_labels.clear()
        # Build guess inputs for current code_length
        default_value = self.game.colors[0]
        self.guess_vars = [tk.StringVar(value=default_value) for _ in range(self.game.code_length)]
        # Create dropdowns and position labels
        for i, var in enumerate(self.guess_vars, start=1):
            om = tk.OptionMenu(self.guess_frame, var, *self.game.colors)
            om.grid(row=1, column=i, padx=5, pady=5)
            self.guess_menus.append(om)
            pos_lbl = tk.Label(self.guess_frame, text=f"Pos {i}")
            pos_lbl.grid(row=2, column=i, padx=5, pady=(0, 5))
            self.pos_labels.append(pos_lbl)
        # Reset history
        self.history_listbox.delete(0, tk.END)
        # Update status
        self._update_attempts_label()
        self._set_submit_enabled(True)
    # ------ UI State Helpers ------
    def _set_submit_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the Submit Guess button.
        """
        self.submit_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)
    def _update_attempts_label(self) -> None:
        """
        Update the attempts label to reflect remaining attempts.
        """
        self.attempts_label.config(
            text=f"Attempts left: {self.game.remaining_attempts()} / {self.game.max_attempts}"
        )
    # ------ Event Handlers ------
    def _on_new_game_click(self) -> None:
        """
        Handle the New Game button click.
        """
        self._new_game_init()
    def _on_new_game_event(self, event: tk.Event) -> None:
        """
        Handle the New Game keyboard shortcut (Ctrl+N).
        """
        self._on_new_game_click()
    def _on_submit_guess_event(self, event: tk.Event) -> None:
        """
        Submit guess via Enter key, if enabled.
        """
        if self.submit_btn.cget("state") == tk.NORMAL:
            self._on_submit_guess()
    def _on_submit_guess(self) -> None:
        """
        Handle the Submit Guess button click: evaluate guess, update history, and handle end-of-game.
        """
        guess = [var.get() for var in self.guess_vars]
        try:
            exact, partial = self.game.evaluate_guess(guess)
        except ValueError as e:
            messagebox.showerror("Invalid Guess", str(e))
            return
        except RuntimeError as e:
            # Should not occur because we disable the button when game is over,
            # but handle defensively.
            messagebox.showwarning("Game Over", str(e))
            self._set_submit_enabled(False)
            return
        # Record in history UI
        guess_str = " ".join(guess)
        guess_num = self.game.attempts_made()
        self.history_listbox.insert(
            tk.END,
            f"Guess {guess_num:2d}: {guess_str:<30} | Exact: {exact}  Partial: {partial}"
        )
        self.history_listbox.see(tk.END)
        # Update attempts label
        self._update_attempts_label()
        # Check game state and inform player
        if self.game.has_won():
            self._set_submit_enabled(False)
            messagebox.showinfo(
                "You Win!",
                f"Congratulations! You cracked the code in {self.game.attempts_made()} attempts."
            )
        elif self.game.is_over():
            self._set_submit_enabled(False)
            secret = " ".join(self.game.reveal_secret())
            messagebox.showinfo("Game Over", f"No attempts left. The secret was: {secret}")