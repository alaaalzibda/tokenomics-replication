'''
Core Wordle game logic:
- evaluate_guess implements Wordle's feedback algorithm with correct handling of duplicate letters.
- WordleGame manages state, validation (including dictionary membership), submission, and knowledge of keyboard letters.
'''
from collections import Counter
from typing import List, Tuple, Dict, Optional
from words import get_daily_word, is_valid_guess
# Status constants
ABSENT = 'absent'    # letter not in word
PRESENT = 'present'  # letter in word but wrong position
CORRECT = 'correct'  # letter in correct position
STATUS_ORDER = {ABSENT: 0, PRESENT: 1, CORRECT: 2}
def evaluate_guess(secret: str, guess: str) -> List[str]:
    """
    Compare a guess against the secret word and return a list of statuses:
    'correct' (green), 'present' (yellow), or 'absent' (grey), per Wordle rules.
    Handles duplicate letters properly by first marking exact matches,
    then allocating remaining letters as 'present' up to their unused counts.
    """
    secret = secret.lower()
    guess = guess.lower()
    n = len(secret)
    if len(guess) != n:
        raise ValueError("Guess length must match secret length.")
    statuses = [ABSENT] * n
    secret_counts = Counter(secret)
    # First pass: mark correct positions
    for i in range(n):
        if guess[i] == secret[i]:
            statuses[i] = CORRECT
            secret_counts[guess[i]] -= 1
    # Second pass: mark present letters (wrong position) respecting remaining counts
    for i in range(n):
        if statuses[i] == CORRECT:
            continue
        ch = guess[i]
        if secret_counts.get(ch, 0) > 0:
            statuses[i] = PRESENT
            secret_counts[ch] -= 1
        else:
            statuses[i] = ABSENT
    return statuses
class WordleGame:
    """
    Manages a Wordle game state:
    - secret word
    - max attempts (6)
    - history of (guess, statuses)
    - keyboard knowledge (best status per letter)
    """
    def __init__(self, secret_word: Optional[str] = None, max_attempts: int = 6, word_provider=get_daily_word):
        self.max_attempts = max_attempts
        self._word_provider = word_provider
        self.secret = secret_word.lower() if secret_word else self._word_provider()
        if len(self.secret) != 5 or not self.secret.isalpha():
            raise ValueError("Secret word must be a 5-letter alphabetic word.")
        self.history: List[Tuple[str, List[str]]] = []
        self._keyboard_status: Dict[str, str] = {}
        self._won = False
    def reset_with_date(self, date=None):
        """Reset the secret word using the provider and clear history."""
        self.secret = self._word_provider(date=date).lower()
        self.history.clear()
        self._keyboard_status.clear()
        self._won = False
    @property
    def attempts_used(self) -> int:
        return len(self.history)
    @property
    def is_won(self) -> bool:
        return self._won
    @property
    def is_over(self) -> bool:
        return self._won or self.attempts_used >= self.max_attempts
    def validate_guess(self, guess: str) -> Tuple[bool, str]:
        """
        Ensure the guess is a valid 5-letter English word:
        - Exactly 5 ASCII alphabetic letters (A–Z)
        - Present in the allowed guess dictionary
        """
        if guess is None:
            return False, "Please enter a guess."
        guess = guess.strip()
        if len(guess) != 5:
            return False, "Your guess must be exactly 5 letters."
        # Enforce ASCII A–Z only (avoid accented letters, symbols)
        if not guess.isascii() or not guess.isalpha():
            return False, "Your guess must contain only letters (A-Z)."
        if not is_valid_guess(guess):
            return False, "Not in word list."
        return True, ""
    def submit_guess(self, guess: str) -> List[str]:
        """
        Validate and evaluate a guess.
        Returns the per-letter statuses. Updates history and keyboard.
        Raises ValueError if invalid or game already over.
        """
        if self.is_over:
            raise ValueError("The game is over. No more guesses allowed.")
        ok, msg = self.validate_guess(guess)
        if not ok:
            raise ValueError(msg)
        guess = guess.lower()
        statuses = evaluate_guess(self.secret, guess)
        self.history.append((guess, statuses))
        # Update win state
        if all(s == CORRECT for s in statuses):
            self._won = True
        # Update keyboard knowledge with best-known status for each letter
        for i, ch in enumerate(guess):
            current = self._keyboard_status.get(ch)
            new_status = statuses[i]
            if current is None or STATUS_ORDER[new_status] > STATUS_ORDER[current]:
                self._keyboard_status[ch] = new_status
        return statuses
    def get_keyboard_status(self) -> Dict[str, str]:
        """Return a mapping from letter -> best-known status."""
        return dict(self._keyboard_status)