'''
Move and MoveState classes representing a chess move and the necessary state for undo operations.
'''
from dataclasses import dataclass
from typing import Optional, Dict
@dataclass
class Move:
    from_sq: int
    to_sq: int
    piece: str
    capture: Optional[str] = None
    promotion: Optional[str] = None
    is_en_passant: bool = False
    is_castling: bool = False
    def __repr__(self):
        promo = f"={self.promotion}" if self.promotion else ""
        ep = " e.p." if self.is_en_passant else ""
        cs = " castle" if self.is_castling else ""
        return f"Move({self.piece}@{self.from_sq}->{self.to_sq}{promo}{ep}{cs})"
@dataclass
class MoveState:
    prev_castling: Dict[str, bool]
    prev_en_passant: Optional[int]
    prev_white_to_move: bool
    captured_piece: Optional[str]
    moved_piece: str
    rook_move: Optional[tuple] = None  # (rook_from, rook_to, rook_piece)
    replaced_pawn_square: Optional[int] = None  # for en passant capture cleanup or promotion revert