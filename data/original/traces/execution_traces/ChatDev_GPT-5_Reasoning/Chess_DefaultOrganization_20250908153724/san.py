'''
SAN generation and parsing utilities. Generates SAN strings for legal moves and parses user input
(SAN or coordinate formats) into Move objects.
'''
import re
from typing import Dict, List, Optional
from board import Board
from move import Move
from utils import index_to_square, square_to_index
def _piece_letter(piece: str) -> str:
    u = piece.upper()
    return '' if u == 'P' else u
def _is_capture(move: Move) -> bool:
    return move.capture is not None or move.is_en_passant
def generate_san_for_move(board: Board, move: Move, legal_moves: Optional[List[Move]] = None) -> str:
    # Generate SAN for a legal move in current position (before making it)
    piece = move.piece
    if move.is_castling and piece.upper() == 'K':
        # Determine side
        to_col = move.to_sq % 8
        san = "O-O" if to_col == 6 else "O-O-O"
    else:
        capture = _is_capture(move)
        piece_letter = _piece_letter(piece)
        disamb = ''
        # Disambiguation for non-pawn moves
        if piece_letter:
            if legal_moves is None:
                legal_moves = board.generate_legal_moves()
            same_dests = [m for m in legal_moves if m.to_sq == move.to_sq and m.piece.upper() == piece.upper() and m.from_sq != move.from_sq]
            if same_dests:
                from_file = move.from_sq % 8
                from_rank = move.from_sq // 8
                file_conflict = any(m.from_sq % 8 == from_file for m in same_dests)
                rank_conflict = any(m.from_sq // 8 == from_rank for m in same_dests)
                if file_conflict and rank_conflict:
                    disamb = index_to_square(move.from_sq)
                elif file_conflict:
                    disamb = index_to_square(move.from_sq)[1]  # rank
                elif rank_conflict:
                    disamb = index_to_square(move.from_sq)[0]  # file
                else:
                    disamb = index_to_square(move.from_sq)[0]  # file usually suffices
        # Destination
        dest = index_to_square(move.to_sq)
        # Pawn capture requires source file letter
        if piece.upper() == 'P' and capture:
            src_file = index_to_square(move.from_sq)[0]
            san = f"{src_file}x{dest}"
        else:
            san = f"{piece_letter}{disamb}{'x' if capture else ''}{dest}"
        # Promotion
        if move.promotion:
            san += f"={move.promotion.upper()}"
    # Check/checkmate suffix
    state = board.make_move(move)
    if board.is_checkmate():
        san += "#"
    elif board.in_check(board.white_to_move):
        san += "+"
    board.undo_move(move, state)
    return san
def _normalize_castle(s: str) -> str:
    s = s.replace('0', 'O')
    s = s.replace('o', 'O')
    return s
def legal_moves_san_map(board: Board) -> Dict[str, Move]:
    # Returns mapping of sanitized SAN variants (lowercased) to moves
    moves = board.generate_legal_moves()
    mapping: Dict[str, Move] = {}
    for mv in moves:
        san = generate_san_for_move(board, mv, moves)
        # canonical
        mapping[san.lower()] = mv
        # Also allow without check/mate suffix
        base = san.rstrip('+#').lower()
        mapping[base] = mv
        # For castling accept variations
        if base in ("o-o", "o-o-o"):
            for var in ["o-o", "0-0", "O-O", "0-0-0", "o-o-o", "O-O-O"]:
                mapping[var.lower()] = mv
        # For promotion accept no '=' variant like e8q
        if '=' in base:
            noeq = base.replace('=', '')
            mapping[noeq] = mv
    return mapping
COORD_RE = re.compile(r'^[a-h][1-8][a-h][1-8][qrbnQRBN]?$')
def parse_user_input(board: Board, text: str) -> Optional[Move]:
    s = text.strip()
    if not s:
        return None
    # Try SAN mapping
    san_map = legal_moves_san_map(board)
    s_norm = _normalize_castle(s).strip()
    key = s_norm.lower()
    if key in san_map:
        return san_map[key]
    # Try coordinate notation like e2e4 or g7g8q
    if COORD_RE.match(key):
        src = square_to_index(key[0:2])
        dst = square_to_index(key[2:4])
        promo_piece = None
        if len(key) == 5:
            promo_char = key[4].upper()
            promo_piece = promo_char if board.white_to_move else promo_char.lower()
        for mv in board.generate_legal_moves():
            if mv.from_sq == src and mv.to_sq == dst:
                if mv.promotion is not None:
                    if promo_piece is None:
                        # default to queen if promotion not specified
                        if mv.promotion.upper() == 'Q':
                            return mv
                        else:
                            continue
                    else:
                        if promo_piece == mv.promotion:
                            return mv
                else:
                    return mv
        return None
    # If promotion omitted piece in SAN (like 'e8' when only promotions exist), default to queen
    base = s_norm.lower()
    if base and base[-1] in '+#':
        base = base[:-1]
    # try appending =q for promotions
    if base + "=q" in san_map:
        return san_map[base + "=q"]
    if base + "q" in san_map:
        return san_map[base + "q"]
    return None