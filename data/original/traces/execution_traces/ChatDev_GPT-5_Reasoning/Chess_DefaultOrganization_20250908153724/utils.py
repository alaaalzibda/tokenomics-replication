'''
Common utility functions for board indexing, square notation, piece color checks,
and Unicode rendering for pieces (used by the optional GUI).
'''
from typing import Optional, Tuple
def is_white(piece: str) -> bool:
    return piece.isupper()
def index_to_coord(idx: int) -> Tuple[int, int]:
    # 0..63 -> (row, col), where 0 is a8 and 63 is h1
    return idx // 8, idx % 8
def coord_to_index(row: int, col: int) -> int:
    return row * 8 + col
def index_to_square(idx: int) -> str:
    row, col = index_to_coord(idx)
    file_char = chr(ord('a') + col)
    rank_char = str(8 - row)
    return f"{file_char}{rank_char}"
def square_to_index(sq: str) -> int:
    if len(sq) != 2:
        raise ValueError(f"Invalid square: {sq}")
    file_char = sq[0].lower()
    rank_char = sq[1]
    if file_char < 'a' or file_char > 'h':
        raise ValueError(f"Invalid file in square: {sq}")
    if rank_char < '1' or rank_char > '8':
        raise ValueError(f"Invalid rank in square: {sq}")
    col = ord(file_char) - ord('a')
    row = 8 - int(rank_char)
    return coord_to_index(row, col)
def piece_unicode(piece: Optional[str]) -> str:
    if piece is None:
        return ''
    mapping = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
    }
    return mapping.get(piece, '?')