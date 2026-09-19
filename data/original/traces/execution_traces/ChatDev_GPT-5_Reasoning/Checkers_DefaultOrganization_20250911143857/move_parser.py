'''
Move notation parser for Checkers (Draughts).
Accepts inputs like "b6-c5" (move) or "c3:e5:g7" (multi-capture).
Supported separators: '-', ':', 'x', spaces, and 'to'.
'''
from typing import List, Tuple
class MoveParseError(Exception):
    pass
class MoveParser:
    @staticmethod
    def parse(text: str) -> List[Tuple[int, int]]:
        """
        Parse a move string into a list of board coordinates (row, col).
        Input squares are algebraic like 'a3', 'h8'. Columns a..h map to 0..7,
        rows 1..8 map to internal rows 7..0 (row 1 is bottom).
        Examples accepted:
          - 'b6-c5'
          - 'c3:e5:g7'
          - 'b6 to c5'
          - 'B6 X A5 x C4' (case-insensitive)
        """
        if not isinstance(text, str) or not text.strip():
            raise MoveParseError("Empty input.")
        # Normalize separators and case
        norm = text.lower().strip()
        # Replace common separators with spaces
        for sep in ['-', ':', 'x']:
            norm = norm.replace(sep, ' ')
        # Replace word 'to' with spaces even if surrounded by spaces or not
        norm = norm.replace(' to ', ' ')
        # Also handle cases like 'b6to c5' or 'b6 toc5'
        norm = norm.replace('to', ' ')
        # Split and filter empty tokens
        parts = [p for p in norm.split() if p]
        coords: List[Tuple[int, int]] = []
        for token in parts:
            # Each token must be exactly a file+rank like 'a1'..'h8'
            if len(token) != 2:
                raise MoveParseError(f"Invalid token length: '{token}'")
            col_char, row_char = token[0], token[1]
            if not ('a' <= col_char <= 'h') or not ('1' <= row_char <= '8'):
                raise MoveParseError(f"Invalid square: {token}")
            c = ord(col_char) - ord('a')  # a->0, h->7
            # Convert chess-like rank to 0-based row index (row '1' bottom -> 7)
            r = 8 - int(row_char)
            coords.append((r, c))
        if len(coords) < 2:
            raise MoveParseError("Specify at least source and destination squares.")
        return coords