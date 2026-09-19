'''
Core chess Board class with move generation, legality checking, making/undoing moves, and printing.
'''
from typing import List, Optional, Dict
from copy import deepcopy
from utils import index_to_coord, coord_to_index, is_white
from move import Move, MoveState
class Board:
    def __init__(self):
        # 8x8 board stored as 64-length list, index 0 = a8, index 63 = h1
        self.squares: List[Optional[str]] = [None] * 64
        self.white_to_move: bool = True
        self.castling: Dict[str, bool] = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant: Optional[int] = None
    def setup_start_position(self):
        # Setup standard chess starting position
        setup = [
            'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
            None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None,
            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R',
        ]
        self.squares = setup
        self.white_to_move = True
        self.castling = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant = None
    def print_board(self):
        # Print ASCII board
        print("  +------------------------+")
        for row in range(8):
            rank = 8 - row
            line = f"{rank} |"
            for col in range(8):
                idx = row * 8 + col
                p = self.squares[idx]
                char = p if p is not None else '.'
                line += f" {char} "
            line += "|"
            print(line)
        print("  +------------------------+")
        print("    a  b  c  d  e  f  g  h")
    def get_king_square(self, white: bool) -> int:
        target = 'K' if white else 'k'
        for i, p in enumerate(self.squares):
            if p == target:
                return i
        raise RuntimeError("King not found on board")
    def is_square_attacked(self, square: int, by_white: bool) -> bool:
        # Check if square is attacked by side by_white
        # Pawns
        r, c = index_to_coord(square)
        pawn_dirs = [(-1, -1), (-1, 1)] if by_white else [(1, -1), (1, 1)]
        for dr, dc in pawn_dirs:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                idx = rr * 8 + cc
                p = self.squares[idx]
                if p == ('P' if by_white else 'p'):
                    return True
        # Knights
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                p = self.squares[rr * 8 + cc]
                if p == ('N' if by_white else 'n'):
                    return True
        # Sliding bishops/queens
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            rr, cc = r + dr, c + dc
            while 0 <= rr < 8 and 0 <= cc < 8:
                p = self.squares[rr * 8 + cc]
                if p is not None:
                    if p == ('B' if by_white else 'b') or p == ('Q' if by_white else 'q'):
                        return True
                    break
                rr += dr
                cc += dc
        # Sliding rooks/queens
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            rr, cc = r + dr, c + dc
            while 0 <= rr < 8 and 0 <= cc < 8:
                p = self.squares[rr * 8 + cc]
                if p is not None:
                    if p == ('R' if by_white else 'r') or p == ('Q' if by_white else 'q'):
                        return True
                    break
                rr += dr
                cc += dc
        # King
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                p = self.squares[rr * 8 + cc]
                if p == ('K' if by_white else 'k'):
                    return True
        return False
    def in_check(self, white: bool) -> bool:
        king_sq = self.get_king_square(white)
        return self.is_square_attacked(king_sq, not white)
    def _add_move(self, moves: List[Move], from_idx: int, to_idx: int, promotion: Optional[str] = None,
                  is_en_passant: bool = False, is_castling: bool = False):
        piece = self.squares[from_idx]
        capture_piece = self.squares[to_idx]
        if is_en_passant:
            # destination is empty; captured pawn is behind to_idx relative to mover
            capture_piece = 'p' if piece.isupper() else 'P'  # placeholder to indicate capture type
        moves.append(Move(from_sq=from_idx, to_sq=to_idx, piece=piece, capture=capture_piece,
                          promotion=promotion, is_en_passant=is_en_passant, is_castling=is_castling))
    def generate_pseudo_legal_moves(self) -> List[Move]:
        moves: List[Move] = []
        side_white = self.white_to_move
        for idx, p in enumerate(self.squares):
            if p is None:
                continue
            if is_white(p) != side_white:
                continue
            r, c = index_to_coord(idx)
            if p.upper() == 'P':
                dirr = -1 if side_white else 1
                start_row = 6 if side_white else 1
                promo_row = 0 if side_white else 7
                # single forward
                rr, cc = r + dirr, c
                if 0 <= rr < 8:
                    forward_idx = rr * 8 + cc
                    if self.squares[forward_idx] is None:
                        if rr == promo_row:
                            for promo in ['Q', 'R', 'B', 'N']:
                                promo_piece = promo if side_white else promo.lower()
                                self._add_move(moves, idx, forward_idx, promotion=promo_piece)
                        else:
                            self._add_move(moves, idx, forward_idx)
                        # double forward
                        if r == start_row:
                            rr2 = r + 2 * dirr
                            if 0 <= rr2 < 8:
                                between_idx = (r + dirr) * 8 + c
                                to2 = rr2 * 8 + c
                                if self.squares[between_idx] is None and self.squares[to2] is None:
                                    self._add_move(moves, idx, to2)
                # captures
                for dc in [-1, 1]:
                    rr, cc = r + dirr, c + dc
                    if 0 <= rr < 8 and 0 <= cc < 8:
                        target_idx = rr * 8 + cc
                        target_piece = self.squares[target_idx]
                        if target_piece is not None and is_white(target_piece) != side_white:
                            if rr == (0 if side_white else 7):
                                for promo in ['Q', 'R', 'B', 'N']:
                                    promo_piece = promo if side_white else promo.lower()
                                    self._add_move(moves, idx, target_idx, promotion=promo_piece)
                            else:
                                self._add_move(moves, idx, target_idx)
                # en passant
                if self.en_passant is not None:
                    ep_r, ep_c = index_to_coord(self.en_passant)
                    if ep_r == r + dirr and abs(ep_c - c) == 1:
                        self._add_move(moves, idx, self.en_passant, is_en_passant=True)
            elif p.upper() == 'N':
                for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < 8 and 0 <= cc < 8:
                        to = rr * 8 + cc
                        tp = self.squares[to]
                        if tp is None or is_white(tp) != side_white:
                            self._add_move(moves, idx, to)
            elif p.upper() == 'B':
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < 8 and 0 <= cc < 8:
                        to = rr * 8 + cc
                        tp = self.squares[to]
                        if tp is None:
                            self._add_move(moves, idx, to)
                        else:
                            if is_white(tp) != side_white:
                                self._add_move(moves, idx, to)
                            break
                        rr += dr
                        cc += dc
            elif p.upper() == 'R':
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < 8 and 0 <= cc < 8:
                        to = rr * 8 + cc
                        tp = self.squares[to]
                        if tp is None:
                            self._add_move(moves, idx, to)
                        else:
                            if is_white(tp) != side_white:
                                self._add_move(moves, idx, to)
                            break
                        rr += dr
                        cc += dc
            elif p.upper() == 'Q':
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < 8 and 0 <= cc < 8:
                        to = rr * 8 + cc
                        tp = self.squares[to]
                        if tp is None:
                            self._add_move(moves, idx, to)
                        else:
                            if is_white(tp) != side_white:
                                self._add_move(moves, idx, to)
                            break
                        rr += dr
                        cc += dc
            elif p.upper() == 'K':
                for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < 8 and 0 <= cc < 8:
                        to = rr * 8 + cc
                        tp = self.squares[to]
                        if tp is None or is_white(tp) != side_white:
                            self._add_move(moves, idx, to)
                # Castling
                if side_white:
                    king_start = coord_to_index(7, 4)  # e1
                    if idx == king_start:
                        # kingside
                        if self.castling.get('K', False):
                            f1 = coord_to_index(7, 5)
                            g1 = coord_to_index(7, 6)
                            h1 = coord_to_index(7, 7)
                            if self.squares[f1] is None and self.squares[g1] is None and self.squares[h1] == 'R':
                                if not self.in_check(True) and not self.is_square_attacked(f1, False) and not self.is_square_attacked(g1, False):
                                    self._add_move(moves, idx, g1, is_castling=True)
                        # queenside
                        if self.castling.get('Q', False):
                            b1 = coord_to_index(7, 1)
                            c1 = coord_to_index(7, 2)
                            d1 = coord_to_index(7, 3)
                            a1 = coord_to_index(7, 0)
                            if self.squares[b1] is None and self.squares[c1] is None and self.squares[d1] is None and self.squares[a1] == 'R':
                                if not self.in_check(True) and not self.is_square_attacked(d1, False) and not self.is_square_attacked(c1, False):
                                    self._add_move(moves, idx, c1, is_castling=True)
                else:
                    king_start = coord_to_index(0, 4)  # e8
                    if idx == king_start:
                        if self.castling.get('k', False):
                            f8 = coord_to_index(0, 5)
                            g8 = coord_to_index(0, 6)
                            h8 = coord_to_index(0, 7)
                            if self.squares[f8] is None and self.squares[g8] is None and self.squares[h8] == 'r':
                                if not self.in_check(False) and not self.is_square_attacked(f8, True) and not self.is_square_attacked(g8, True):
                                    self._add_move(moves, idx, g8, is_castling=True)
                        if self.castling.get('q', False):
                            b8 = coord_to_index(0, 1)
                            c8 = coord_to_index(0, 2)
                            d8 = coord_to_index(0, 3)
                            a8 = coord_to_index(0, 0)
                            if self.squares[b8] is None and self.squares[c8] is None and self.squares[d8] is None and self.squares[a8] == 'r':
                                if not self.in_check(False) and not self.is_square_attacked(d8, True) and not self.is_square_attacked(c8, True):
                                    self._add_move(moves, idx, c8, is_castling=True)
        return moves
    def generate_legal_moves(self) -> List[Move]:
        legal: List[Move] = []
        for mv in self.generate_pseudo_legal_moves():
            state = self.make_move(mv)
            illegal = self.in_check(not self.white_to_move)  # after move, side to move switched
            self.undo_move(mv, state)
            if not illegal:
                legal.append(mv)
        return legal
    def _update_castling_rights_on_move(self, move: Move):
        # Update castling rights based on moved/captured pieces
        p = move.piece
        from_idx = move.from_sq
        to_idx = move.to_sq
        # Moving king removes both rights
        if p == 'K':
            self.castling['K'] = False
            self.castling['Q'] = False
        elif p == 'k':
            self.castling['k'] = False
            self.castling['q'] = False
        # Moving rooks removes side rights from that rook's starting square
        if from_idx == coord_to_index(7, 0):  # a1
            self.castling['Q'] = False
        if from_idx == coord_to_index(7, 7):  # h1
            self.castling['K'] = False
        if from_idx == coord_to_index(0, 0):  # a8
            self.castling['q'] = False
        if from_idx == coord_to_index(0, 7):  # h8
            self.castling['k'] = False
        # Capturing rooks also affects rights
        captured = move.capture
        if captured is not None:
            if to_idx == coord_to_index(7, 0) and captured == 'R':
                self.castling['Q'] = False
            if to_idx == coord_to_index(7, 7) and captured == 'R':
                self.castling['K'] = False
            if to_idx == coord_to_index(0, 0) and captured == 'r':
                self.castling['q'] = False
            if to_idx == coord_to_index(0, 7) and captured == 'r':
                self.castling['k'] = False
    def make_move(self, move: Move) -> MoveState:
        # Save state
        prev_castling = deepcopy(self.castling)
        prev_en_passant = self.en_passant
        prev_white_to_move = self.white_to_move
        captured_piece: Optional[str] = None
        rook_move = None
        replaced_pawn_square = None
        from_idx = move.from_sq
        to_idx = move.to_sq
        piece = self.squares[from_idx]
        assert piece is not None and piece == move.piece
        # Handle en passant capture
        if move.is_en_passant:
            # destination is empty; captured pawn is behind to_idx relative to mover
            if piece.isupper():
                cap_idx = to_idx + 8
            else:
                cap_idx = to_idx - 8
            captured_piece = self.squares[cap_idx]
            self.squares[cap_idx] = None
            replaced_pawn_square = cap_idx
        else:
            captured_piece = self.squares[to_idx]
        # Move the piece
        self.squares[to_idx] = piece
        self.squares[from_idx] = None
        # Handle castling rook move
        if move.is_castling and piece.upper() == 'K':
            # Determine side by to square
            r, c = index_to_coord(to_idx)
            if c == 6:  # kingside
                rook_from = coord_to_index(r, 7)
                rook_to = coord_to_index(r, 5)
            else:  # queenside
                rook_from = coord_to_index(r, 0)
                rook_to = coord_to_index(r, 3)
            rook_piece = self.squares[rook_from]
            self.squares[rook_to] = rook_piece
            self.squares[rook_from] = None
            rook_move = (rook_from, rook_to, rook_piece)
        # Handle promotion
        if move.promotion is not None:
            self.squares[to_idx] = move.promotion
            # replaced pawn is conceptually the to_idx to revert on undo
            replaced_pawn_square = to_idx
        # Update castling rights
        self._update_castling_rights_on_move(move)
        # Reset/set en passant
        self.en_passant = None
        # If pawn moved two squares, set en passant square
        if piece.upper() == 'P':
            fr, fc = index_to_coord(from_idx)
            tr, tc = index_to_coord(to_idx)
            if abs(fr - tr) == 2 and fc == tc:
                mid_r = (fr + tr) // 2
                self.en_passant = coord_to_index(mid_r, fc)
        # Toggle turn
        self.white_to_move = not self.white_to_move
        return MoveState(prev_castling=prev_castling,
                         prev_en_passant=prev_en_passant,
                         prev_white_to_move=prev_white_to_move,
                         captured_piece=captured_piece,
                         moved_piece=piece,
                         rook_move=rook_move,
                         replaced_pawn_square=replaced_pawn_square)
    def undo_move(self, move: Move, state: MoveState):
        # Restore turn
        self.white_to_move = state.prev_white_to_move
        # Move back piece
        from_idx = move.from_sq
        to_idx = move.to_sq
        # Undo promotion
        piece = state.moved_piece
        if move.promotion is not None:
            # The promoted piece at to_idx should be replaced with a pawn of the same color
            pawn = 'P' if piece.isupper() else 'p'
            self.squares[to_idx] = pawn
        # Move back
        self.squares[from_idx] = self.squares[to_idx]
        self.squares[to_idx] = None
        # Undo rook move for castling
        if state.rook_move is not None:
            rook_from, rook_to, rook_piece = state.rook_move
            self.squares[rook_from] = rook_piece
            self.squares[rook_to] = None
        # Restore captured piece (including en passant captured pawn)
        if move.is_en_passant and state.replaced_pawn_square is not None:
            self.squares[state.replaced_pawn_square] = state.captured_piece
        else:
            self.squares[to_idx] = state.captured_piece
        # Restore castling and en passant
        self.castling = state.prev_castling
        self.en_passant = state.prev_en_passant
    def is_checkmate(self) -> bool:
        if not self.in_check(self.white_to_move):
            return False
        if self.generate_legal_moves():
            return False
        return True
    def is_stalemate(self) -> bool:
        if self.in_check(self.white_to_move):
            return False
        if self.generate_legal_moves():
            return False
        return True
    def get_legal_moves_for_square(self, src_idx: int) -> List[Move]:
        return [m for m in self.generate_legal_moves() if m.from_sq == src_idx]