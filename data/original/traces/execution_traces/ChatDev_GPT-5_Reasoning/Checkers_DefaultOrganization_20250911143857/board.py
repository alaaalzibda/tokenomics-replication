'''
Board and Piece definitions for Checkers (Draughts).
This module is safe to import even if Pygame is not installed. The Pygame
import is optional and only required for the draw() method. In environments
without Pygame (e.g., headless tests), the draw() method becomes a no-op,
while the board logic remains fully usable (e.g., via CLI).
'''
try:
    import pygame  # Optional; may be unavailable in headless environments
except ImportError:  # pragma: no cover - fallback for environments without pygame
    pygame = None
from constants import (
    ROWS, COLS, SQUARE_SIZE, BOARD_SIZE,
    LIGHT_COLOR, DARK_COLOR, RED_COLOR, BLACK_COLOR,
    HILITE_MOVE_COLOR, HILITE_CAPTURE_COLOR, KING_TEXT_COLOR
)
class Piece:
    def __init__(self, color: str, king: bool = False):
        self.color = color  # 'red' or 'black'
        self.king = king
    def clone(self):
        return Piece(self.color, self.king)
class Board:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.setup_initial()
    def setup_initial(self):
        # Place black pieces (top rows 0..2) on dark squares
        for r in range(3):
            for c in range(COLS):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Piece('black', king=False)
        # Place red pieces (bottom rows 5..7) on dark squares
        for r in range(5, 8):
            for c in range(COLS):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Piece('red', king=False)
    def copy(self):
        b = Board.__new__(Board)
        b.grid = [[p.clone() if p else None for p in row] for row in self.grid]
        return b
    @staticmethod
    def in_bounds(r, c):
        return 0 <= r < ROWS and 0 <= c < COLS
    def get(self, r, c):
        if not Board.in_bounds(r, c):
            return None
        return self.grid[r][c]
    def set(self, r, c, piece):
        if Board.in_bounds(r, c):
            self.grid[r][c] = piece
    def move_piece(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos
        piece = self.get(fr, fc)
        self.set(fr, fc, None)
        self.set(tr, tc, piece)
    def remove_piece(self, r, c):
        self.set(r, c, None)
    def draw(self, surface, font, last_move=None):
        # If pygame is unavailable (e.g., headless test), do nothing.
        if pygame is None:
            return
        # Draw board squares
        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                color = DARK_COLOR if (r + c) % 2 == 1 else LIGHT_COLOR
                pygame.draw.rect(surface, color, rect)
        # Highlight last move (if any)
        if last_move and len(last_move) >= 2:
            # Highlight path squares
            for i in range(len(last_move) - 1):
                r1, c1 = last_move[i]
                r2, c2 = last_move[i + 1]
                # Use different color for captures
                if abs(r2 - r1) == 2 and abs(c2 - c1) == 2:
                    col = HILITE_CAPTURE_COLOR
                else:
                    col = HILITE_MOVE_COLOR
                rect1 = pygame.Rect(c1 * SQUARE_SIZE, r1 * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                rect2 = pygame.Rect(c2 * SQUARE_SIZE, r2 * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, col, rect1, 3)
                pygame.draw.rect(surface, col, rect2, 3)
        # Draw pieces
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.grid[r][c]
                if piece:
                    center = (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2)
                    radius = int(SQUARE_SIZE * 0.4)
                    color = RED_COLOR if piece.color == 'red' else BLACK_COLOR
                    pygame.draw.circle(surface, color, center, radius)
                    pygame.draw.circle(surface, (20, 20, 20), center, radius, 2)  # border
                    # King mark
                    if piece.king:
                        text = font.render("K", True, KING_TEXT_COLOR)
                        text_rect = text.get_rect(center=center)
                        surface.blit(text, text_rect)