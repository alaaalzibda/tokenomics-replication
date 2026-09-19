'''
Core game logic for Strands: validates selections, tracks found words, hint progress,
and enforces the non-overlapping fill of the entire board according to the puzzle.
'''
from typing import List, Tuple, Dict, Optional
# Support running whether this module is inside a package (relative import)
# or at project root (absolute import).
try:
    from .wordlist import WORDS as NON_THEME_WORDS
except ImportError:
    from wordlist import WORDS as NON_THEME_WORDS
Coord = Tuple[int, int]
class GameState:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.found_words = set()  # includes spangram when found
        self.claimed: Dict[Coord, Dict[str, str]] = {}  # coord -> {'word': str, 'type': 'theme'|'spangram'}
        self.non_theme_words = set()
        self.hints = 0
    @staticmethod
    def is_adjacent(a: Coord, b: Coord) -> bool:
        return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1 and a != b
    def can_select_cell(self, coord: Coord) -> bool:
        return coord not in self.claimed
    def selection_to_word(self, coords: List[Coord]) -> str:
        return "".join(self.puzzle.get_letter(r, c) for (r, c) in coords)
    def _claim_word(self, word: str, coords: List[Coord], kind: str):
        for coord in coords:
            self.claimed[coord] = {'word': word, 'type': kind}
        self.found_words.add(word)
    def is_completed(self) -> bool:
        # Completed when all themed words and spangram are found
        return self.puzzle.spangram in self.found_words and all(
            w in self.found_words for w in self.puzzle.theme_words
        )
    def try_commit_selection(self, coords: List[Coord]) -> Dict[str, Optional[str]]:
        # Empty or single-letter selections are invalid (require at least 2 letters)
        if not coords or len(coords) < 2:
            return {'type': 'invalid', 'word': None, 'coords': coords}
        # All must be unclaimed and consecutive adjacency
        for i in range(1, len(coords)):
            if coords[i] in self.claimed:
                return {'type': 'invalid', 'word': None, 'coords': coords}
            if not self.is_adjacent(coords[i - 1], coords[i]):
                return {'type': 'invalid', 'word': None, 'coords': coords}
        word = self.selection_to_word(coords)
        # Check against spangram and themed words using canonical paths to enforce non-overlap fill
        # Spangram
        if word == self.puzzle.spangram and coords == self.puzzle.spangram_path:
            # Accept only if not previously found
            if self.puzzle.spangram not in self.found_words:
                self._claim_word(self.puzzle.spangram, coords, 'spangram')
                return {'type': 'spangram', 'word': word, 'coords': coords}
            else:
                return {'type': 'invalid', 'word': None, 'coords': coords}
        # Themed words
        for tw in self.puzzle.theme_words:
            if word == tw and coords == self.puzzle.word_paths[tw]:
                if tw not in self.found_words:
                    self._claim_word(tw, coords, 'theme')
                    return {'type': 'theme', 'word': word, 'coords': coords}
                else:
                    return {'type': 'invalid', 'word': None, 'coords': coords}
        # Do not count a selection that spells a themed word but not on its canonical path
        if word in self.puzzle.theme_words or word == self.puzzle.spangram:
            return {'type': 'invalid', 'word': None, 'coords': coords}
        # Non-theme dictionary word for hints
        if len(word) >= 4 and word.lower() in NON_THEME_WORDS:
            # Count unique words only
            if word not in self.non_theme_words:
                self.non_theme_words.add(word)
                # Every 3 non-theme words -> +1 hint
                if len(self.non_theme_words) % 3 == 0:
                    self.hints += 1
            return {'type': 'non-theme', 'word': word, 'coords': coords}
        return {'type': 'invalid', 'word': None, 'coords': coords}
    def reveal_hint(self):
        # Reveal next unfound themed word (not spangram)
        if self.hints <= 0:
            return None
        for tw in self.puzzle.theme_words:
            if tw not in self.found_words:
                coords = self.puzzle.word_paths[tw]
                # Ensure cells are unclaimed (should be per puzzle design)
                if any(c in self.claimed for c in coords):
                    # This should not happen in a well-formed puzzle; skip to next just in case
                    continue
                self._claim_word(tw, coords, 'theme')
                self.hints -= 1
                return (tw, coords, 'theme')
        # If all themes are found, consider revealing spangram if not found yet
        if self.puzzle.spangram not in self.found_words:
            coords = self.puzzle.spangram_path
            if any(c in self.claimed for c in coords):
                return None
            self._claim_word(self.puzzle.spangram, coords, 'spangram')
            self.hints -= 1
            return (self.puzzle.spangram, coords, 'spangram')
        return None