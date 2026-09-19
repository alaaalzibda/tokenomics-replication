'''
Crossword model: holds the puzzle state, computes numbering for across/down
entries, validates user answers, and tracks completion.
Enhancements:
- Supports number-based clue dictionaries (preferred), with backward-compatible
  fallback to answer-based clue dictionaries.
- Dynamic numbering based on the grid and black squares ('#').
- Mapping of entries by (number, direction).
- Placing answers with validation against the true solution.
- Reporting completion when all non-block cells match the solution.
- NEW: Recompute "filled" flags based on the current grid so clue checkmarks
  reflect actual grid state, even when entries are completed via crossings.
'''
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
@dataclass
class CrosswordEntry:
    number: int
    direction: str  # 'A' or 'D'
    row: int
    col: int
    length: int
    answer: str
    clue: str
    filled: bool = False
class CrosswordModel:
    def __init__(
        self,
        solution_rows: List[str],
        across_clues_by_answer: Optional[Dict[str, str]] = None,
        down_clues_by_answer: Optional[Dict[str, str]] = None,
        across_clues_by_number: Optional[Dict[int, str]] = None,
        down_clues_by_number: Optional[Dict[int, str]] = None,
        title: str = "Crossword",
    ):
        self.title = title
        self.solution_rows = [row.upper() for row in solution_rows]
        self.rows = len(self.solution_rows)
        self.cols = len(self.solution_rows[0]) if self.rows > 0 else 0
        # Validate rectangular grid
        for r in self.solution_rows:
            if len(r) != self.cols:
                raise ValueError("All solution rows must have the same length.")
        # Build solution grid and block grid
        self.solution_grid: List[List[Optional[str]]] = []
        self.block_grid: List[List[bool]] = []
        for r in range(self.rows):
            row_chars: List[Optional[str]] = []
            row_blocks: List[bool] = []
            for c in range(self.cols):
                ch = self.solution_rows[r][c]
                if ch == "#":
                    row_chars.append(None)
                    row_blocks.append(True)
                else:
                    row_chars.append(ch)
                    row_blocks.append(False)
            self.solution_grid.append(row_chars)
            self.block_grid.append(row_blocks)
        # Current grid (letters filled by user), blank string for empty cells, None for blocks
        self.current_grid: List[List[Optional[str]]] = []
        for r in range(self.rows):
            cur_row: List[Optional[str]] = []
            for c in range(self.cols):
                cur_row.append(None if self.block_grid[r][c] else "")
            self.current_grid.append(cur_row)
        # Store clue dicts (may be None)
        self.across_clues_by_answer = across_clues_by_answer or {}
        self.down_clues_by_answer = down_clues_by_answer or {}
        self.across_clues_by_number = across_clues_by_number or {}
        self.down_clues_by_number = down_clues_by_number or {}
        # Compute entries with numbering
        self.entries: List[CrosswordEntry] = []
        self.entry_map: Dict[Tuple[int, str], CrosswordEntry] = {}
        self._compute_entries()
    def _compute_entries(self):
        number = 1
        # iterate grid to assign numbers to starting cells
        for r in range(self.rows):
            for c in range(self.cols):
                if self.block_grid[r][c]:
                    continue
                starts_across = (c == 0 or self.block_grid[r][c - 1])
                starts_down = (r == 0 or self.block_grid[r - 1][c])
                if not (starts_across or starts_down):
                    continue
                if starts_across:
                    length, answer = self._read_across(r, c)
                    clue = self._resolve_clue(number, "A", answer, length)
                    entry = CrosswordEntry(
                        number=number,
                        direction="A",
                        row=r,
                        col=c,
                        length=length,
                        answer=answer,
                        clue=clue,
                    )
                    self.entries.append(entry)
                    self.entry_map[(number, "A")] = entry
                if starts_down:
                    length, answer = self._read_down(r, c)
                    clue = self._resolve_clue(number, "D", answer, length)
                    entry = CrosswordEntry(
                        number=number,
                        direction="D",
                        row=r,
                        col=c,
                        length=length,
                        answer=answer,
                        clue=clue,
                    )
                    self.entries.append(entry)
                    self.entry_map[(number, "D")] = entry
                number += 1
        # Sort entries by number then direction for consistent display
        self.entries.sort(key=lambda e: (e.number, e.direction))
    def _resolve_clue(self, number: int, direction: str, answer: str, length: int) -> str:
        # Preferred: number-based clue dict
        if direction == "A":
            if number in self.across_clues_by_number:
                return self.across_clues_by_number[number]
            # Fallback: answer-text-based dict
            if answer in self.across_clues_by_answer:
                return self.across_clues_by_answer[answer]
            return f"Across word ({length})"
        else:
            if number in self.down_clues_by_number:
                return self.down_clues_by_number[number]
            if answer in self.down_clues_by_answer:
                return self.down_clues_by_answer[answer]
            return f"Down word ({length})"
    def _read_across(self, r: int, c: int) -> Tuple[int, str]:
        chars: List[str] = []
        cc = c
        while cc < self.cols and not self.block_grid[r][cc]:
            ch = self.solution_grid[r][cc]
            if ch is None:
                break
            chars.append(ch)
            cc += 1
        return len(chars), "".join(chars)
    def _read_down(self, r: int, c: int) -> Tuple[int, str]:
        chars: List[str] = []
        rr = r
        while rr < self.rows and not self.block_grid[rr][c]:
            ch = self.solution_grid[rr][c]
            if ch is None:
                break
            chars.append(ch)
            rr += 1
        return len(chars), "".join(chars)
    def get_entries(self, direction: Optional[str] = None) -> List[CrosswordEntry]:
        if direction in ("A", "D"):
            return [e for e in self.entries if e.direction == direction]
        return list(self.entries)
    def get_entry(self, number: int, direction: str) -> Optional[CrosswordEntry]:
        return self.entry_map.get((number, direction.upper()))
    def place_answer(self, number: int, direction: str, word: str) -> Tuple[bool, str]:
        """
        Attempt to place an answer for a given clue number and direction.
        Validation:
          - Entry must exist
          - Word length must match
          - Word must match the true solution
        On success: letters are filled into the current grid; entry is marked filled.
        Returns (success, message).
        """
        direction = direction.upper().strip()
        if direction not in ("A", "D"):
            return False, "Direction must be 'A' (Across) or 'D' (Down)."
        entry = self.get_entry(number, direction)
        if not entry:
            return False, f"No entry found for {number}{direction}."
        user = word.upper().strip()
        if len(user) != entry.length:
            return False, f"Answer length mismatch: expected {entry.length} letters."
        if user != entry.answer:
            # Provide helpful mismatch details if overlapping letters already filled
            mismatch_positions = []
            for i in range(entry.length):
                rr = entry.row + (i if direction == "D" else 0)
                cc = entry.col + (i if direction == "A" else 0)
                existing = self.current_grid[rr][cc]
                if existing and existing != "" and existing != user[i]:
                    mismatch_positions.append((i + 1, existing, user[i]))
            if mismatch_positions:
                details = "; ".join(
                    [
                        f"pos {pos}: grid has '{grid}', you typed '{typed}'"
                        for (pos, grid, typed) in mismatch_positions
                    ]
                )
                return False, f"Letters conflict with filled cells ({details})."
            return False, "Incorrect answer."
        # All good: fill letters
        for i in range(entry.length):
            rr = entry.row + (i if direction == "D" else 0)
            cc = entry.col + (i if direction == "A" else 0)
            self.current_grid[rr][cc] = entry.answer[i]
        # Mark filled (will also be recomputed during refresh)
        entry.filled = True
        return True, f"Placed {number}{direction}."
    def is_block(self, r: int, c: int) -> bool:
        return self.block_grid[r][c]
    def get_cell(self, r: int, c: int) -> str:
        """
        Returns the current value at (r,c):
        - '#' if block
        - '' if empty
        - 'A'..'Z' if filled
        """
        if self.block_grid[r][c]:
            return "#"
        val = self.current_grid[r][c]
        return "" if (val is None or val == "") else val
    def get_dimensions(self) -> Tuple[int, int]:
        return self.rows, self.cols
    def min_number(self) -> int:
        return min(e.number for e in self.entries) if self.entries else 1
    def max_number(self) -> int:
        return max(e.number for e in self.entries) if self.entries else 1
    def is_complete(self) -> bool:
        for r in range(self.rows):
            for c in range(self.cols):
                if self.block_grid[r][c]:
                    continue
                cur = self.current_grid[r][c]
                sol = self.solution_grid[r][c]
                if not cur or cur != sol:
                    return False
        return True
    def reset(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.block_grid[r][c]:
                    self.current_grid[r][c] = None
                else:
                    self.current_grid[r][c] = ""
        for e in self.entries:
            e.filled = False
    # NEW: Derive filled status from the current grid, not only submissions
    def entry_is_filled(self, entry: CrosswordEntry) -> bool:
        """
        Returns True if every cell of the entry currently matches the solution grid.
        """
        for i in range(entry.length):
            rr = entry.row + (i if entry.direction == "D" else 0)
            cc = entry.col + (i if entry.direction == "A" else 0)
            cur = self.current_grid[rr][cc]
            sol = self.solution_grid[rr][cc]
            if cur != sol:
                return False
        return True
    def refresh_entry_flags(self) -> None:
        """
        Recomputes and updates the 'filled' flag for all entries based on the current grid.
        """
        for e in self.entries:
            e.filled = self.entry_is_filled(e)