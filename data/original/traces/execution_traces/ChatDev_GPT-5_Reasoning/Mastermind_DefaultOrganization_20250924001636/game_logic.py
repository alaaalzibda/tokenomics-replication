'''
Mastermind Game Logic
This module implements the core rules of the Mastermind game:
- Secret code generation from a given set of colors (or symbols).
- Guess evaluation producing exact and partial matches.
- Game state management, attempts counting, and history recording.
Algorithm for feedback:
- Exact matches count positions where guess[i] == secret[i].
- Partial matches count symbols present in both guess and secret but not already counted
  as exact matches. This uses min count over unmatched elements per symbol.
'''
from __future__ import annotations
import random
from collections import Counter
from typing import List, Tuple, Dict, Optional
class MastermindGame:
    """
    Core game logic for Mastermind.
    Attributes:
        code_length: Number of positions in the secret code.
        colors: List of available symbol keys (strings) (e.g., color names or digits as strings).
        max_attempts: Maximum number of attempts allowed.
        allow_duplicates: Whether the secret code can contain duplicate symbols.
    """
    def __init__(
        self,
        code_length: int = 4,
        colors: Optional[List[str]] = None,
        max_attempts: int = 10,
        allow_duplicates: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        if colors is None:
            colors = ["red", "green", "blue", "yellow", "orange", "purple"]
        if code_length <= 0:
            raise ValueError("code_length must be positive")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if not colors:
            raise ValueError("colors list must not be empty")
        if not allow_duplicates and code_length > len(colors):
            raise ValueError(
                "code_length cannot exceed number of colors when duplicates are not allowed"
            )
        self.code_length = code_length
        self.colors = colors
        self.max_attempts = max_attempts
        self.allow_duplicates = allow_duplicates
        self._rng = random.Random(seed)
        self._secret: List[str] = []
        self._attempts: int = 0
        self._won: bool = False
        self._history: List[Dict[str, object]] = []
        self.new_game()
    # --------- Game Lifecycle ---------
    def new_game(self) -> None:
        """Start a new game by generating a new secret code and resetting state."""
        if self.allow_duplicates:
            # choices allows duplicates
            self._secret = [self._rng.choice(self.colors) for _ in range(self.code_length)]
        else:
            # sample avoids duplicates
            self._secret = self._rng.sample(self.colors, self.code_length)
        self._attempts = 0
        self._won = False
        self._history.clear()
    # --------- State Queries ---------
    def remaining_attempts(self) -> int:
        """Return the number of attempts left."""
        return self.max_attempts - self._attempts
    def attempts_made(self) -> int:
        """Return the number of attempts used so far."""
        return self._attempts
    def is_over(self) -> bool:
        """Return True if the game is over (won or attempts exhausted)."""
        return self._won or self._attempts >= self.max_attempts
    def has_won(self) -> bool:
        """Return True if the player has already cracked the code."""
        return self._won
    def reveal_secret(self) -> List[str]:
        """Return the secret code (useful at end of game)."""
        return list(self._secret)
    def get_history(self) -> List[Dict[str, object]]:
        """
        Return the history of guesses and results.
        Each entry is a dict: {'guess': List[str], 'exact': int, 'partial': int}
        """
        return list(self._history)
    # --------- Core Mechanics ---------
    def evaluate_guess(self, guess: List[str]) -> Tuple[int, int]:
        """
        Evaluate a guess and return (exact_matches, partial_matches).
        Rules:
        - exact: correct symbol in the correct position.
        - partial: correct symbol but in the wrong position (not counting exact matches).
        """
        if self.is_over():
            raise RuntimeError("Game is already over.")
        if len(guess) != self.code_length:
            raise ValueError(f"Guess must have length {self.code_length}.")
        if any(g not in self.colors for g in guess):
            raise ValueError("Guess contains invalid symbols.")
        secret = self._secret
        # Count exact matches and collect unmatched pools
        exact = 0
        unmatched_secret: List[str] = []
        unmatched_guess: List[str] = []
        for s, g in zip(secret, guess):
            if s == g:
                exact += 1
            else:
                unmatched_secret.append(s)
                unmatched_guess.append(g)
        # Partial matches are the sum of min counts per symbol over unmatched items
        secret_counts = Counter(unmatched_secret)
        guess_counts = Counter(unmatched_guess)
        partial = sum(min(secret_counts[c], guess_counts[c]) for c in guess_counts)
        # Record attempt
        self._attempts += 1
        if exact == self.code_length:
            self._won = True
        record = {
            "guess": list(guess),
            "exact": exact,
            "partial": partial,
        }
        self._history.append(record)
        return exact, partial