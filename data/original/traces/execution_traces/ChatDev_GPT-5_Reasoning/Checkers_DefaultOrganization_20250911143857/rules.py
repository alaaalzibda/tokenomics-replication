'''
Rules and game state for Checkers (Draughts).
Implements legal move generation, forced captures, move application, kinging, and win detection.
Note: Men move and capture forward only; kings move and capture both directions (English/American rules).
'''
from typing import List, Tuple, Optional
from board import Board, Piece
from constants import ROWS, COLS
Coord = Tuple[int, int]
class GameState:
    def __init__(self, board: Board):
        self.board = board
        self.current_player = 'red'  # Red moves first
        self.last_move: Optional[List[Coord]] = None
    @staticmethod
    def _opponent(color: str) -> str:
        return 'black' if color == 'red' else 'red'
    def get_legal_moves(self, player: str):
        # Returns a tuple (captures, normals), each a list of sequences (list of coords)
        captures = []
        normals = []
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board.get(r, c)
                if piece and piece.color == player:
                    cap = self._capture_sequences_from((r, c), piece)
                    if cap:
                        captures.extend(cap)
                    else:
                        normals.extend(self._normal_moves_from((r, c), piece))
        if captures:
            return captures, []
        return [], normals
    def _normal_moves_from(self, pos: Coord, piece: Piece) -> List[List[Coord]]:
        r, c = pos
        steps = []
        directions = []
        if piece.king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            if piece.color == 'red':
                directions = [(-1, -1), (-1, 1)]
            else:
                directions = [(1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if Board.in_bounds(nr, nc) and self.board.get(nr, nc) is None:
                steps.append([pos, (nr, nc)])
        return steps
    def _capture_sequences_from(self, pos: Coord, piece: Piece) -> List[List[Coord]]:
        # Returns maximal capture sequences (forced jump chains). Each sequence is [start, ..., end].
        # Men capture forward only; kings capture in all four diagonal directions.
        sequences = []
        def recurse(board: Board, current: Coord, piece: Piece, path: List[Coord], any_jump: bool) -> None:
            r, c = current
            color = piece.color
            if piece.king:
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            else:
                # Forward-only capture directions for men
                if color == 'red':
                    directions = [(-1, -1), (-1, 1)]
                else:
                    directions = [(1, -1), (1, 1)]
            found = False
            for dr, dc in directions:
                mid_r, mid_c = r + dr, c + dc
                land_r, land_c = r + 2 * dr, c + 2 * dc
                if not Board.in_bounds(land_r, land_c) or not Board.in_bounds(mid_r, mid_c):
                    continue
                mid_piece = board.get(mid_r, mid_c)
                if mid_piece and mid_piece.color == self._opponent(color) and board.get(land_r, land_c) is None:
                    # Simulate jump
                    next_board = board.copy()
                    # Move piece
                    next_board.remove_piece(r, c)
                    next_board.remove_piece(mid_r, mid_c)
                    next_board.set(land_r, land_c, Piece(color, king=piece.king))
                    next_piece = next_board.get(land_r, land_c)
                    # Kinging: if a man reaches last row during capture, it becomes king and the move ends.
                    becomes_king_now = False
                    if not piece.king:
                        if color == 'red' and land_r == 0:
                            next_piece.king = True
                            becomes_king_now = True
                        elif color == 'black' and land_r == ROWS - 1:
                            next_piece.king = True
                            becomes_king_now = True
                    found = True
                    if becomes_king_now:
                        sequences.append(path + [(land_r, land_c)])
                    else:
                        recurse(next_board, (land_r, land_c), next_piece, path + [(land_r, land_c)], True)
            if not found and any_jump:
                sequences.append(path)
        recurse(self.board, pos, piece, [pos], False)
        # Keep sequences that performed at least one jump: length >= 2 (start and final square)
        sequences = [seq for seq in sequences if len(seq) >= 2]
        return sequences
    def try_move(self, seq: List[Coord]):
        # Validate starting square and turn
        if not seq or len(seq) < 2:
            return False, "Move must specify at least a source and a destination."
        sr, sc = seq[0]
        piece = self.board.get(sr, sc)
        if piece is None:
            return False, "No piece at the source square."
        if piece.color != self.current_player:
            return False, f"It is {self.current_player.capitalize()}'s turn."
        captures, normals = self.get_legal_moves(self.current_player)
        if captures:
            # Only captures are allowed
            # Check if this sequence exactly matches one of the legal capture sequences
            if not self._is_valid_capture_sequence(seq, captures):
                return False, "Invalid capture sequence or not maximal. Include full jump chain."
            self._apply_capture_sequence(seq)
            self.last_move = seq
            self._post_move_kinging(seq[-1])
            self._end_turn()
            return True, None
        else:
            # Check simple move validity
            if len(seq) != 2:
                return False, "Only a single step move is allowed (no captures available)."
            if not self._is_valid_normal_move(seq, normals):
                return False, "Invalid move."
            self._apply_normal_move(seq)
            self.last_move = seq
            self._post_move_kinging(seq[-1])
            self._end_turn()
            return True, None
    def _is_valid_capture_sequence(self, seq: List[Coord], legal_captures: List[List[Coord]]) -> bool:
        # seq must be exactly equal to one of the legal_captures
        return any(self._same_path(seq, legal) for legal in legal_captures)
    @staticmethod
    def _same_path(a: List[Coord], b: List[Coord]) -> bool:
        if len(a) != len(b):
            return False
        return all(x == y for x, y in zip(a, b))
    def _apply_capture_sequence(self, seq: List[Coord]):
        # Remove captured pieces along the path and move the piece
        for i in range(len(seq) - 1):
            fr = seq[i]
            to = seq[i + 1]
            self.board.move_piece(fr, to)
            # remove jumped piece
            r1, c1 = fr
            r2, c2 = to
            mid_r = (r1 + r2) // 2
            mid_c = (c1 + c2) // 2
            self.board.remove_piece(mid_r, mid_c)
    def _is_valid_normal_move(self, seq: List[Coord], legal_normals: List[List[Coord]]) -> bool:
        return any(self._same_path(seq, legal) for legal in legal_normals)
    def _apply_normal_move(self, seq: List[Coord]):
        self.board.move_piece(seq[0], seq[1])
    def _post_move_kinging(self, dest: Coord):
        # After a move, if a man reaches the king row, crown it
        r, c = dest
        piece = self.board.get(r, c)
        if piece and not piece.king:
            if piece.color == 'red' and r == 0:
                piece.king = True
            elif piece.color == 'black' and r == ROWS - 1:
                piece.king = True
    def _end_turn(self):
        self.current_player = self._opponent(self.current_player)
    def is_game_over(self):
        # Check if current player (who is about to move) has any legal moves
        red_pieces = self._count_pieces('red')
        black_pieces = self._count_pieces('black')
        if red_pieces == 0 and black_pieces == 0:
            return True, None, "No pieces remain."
        if red_pieces == 0:
            return True, 'black', "Red has no pieces."
        if black_pieces == 0:
            return True, 'red', "Black has no pieces."
        captures, normals = self.get_legal_moves(self.current_player)
        if not captures and not normals:
            winner = self._opponent(self.current_player)
            return True, winner, f"{self.current_player.capitalize()} has no legal moves."
        return False, None, ""
    def _count_pieces(self, color: str) -> int:
        total = 0
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board.get(r, c)
                if p and p.color == color:
                    total += 1
        return total