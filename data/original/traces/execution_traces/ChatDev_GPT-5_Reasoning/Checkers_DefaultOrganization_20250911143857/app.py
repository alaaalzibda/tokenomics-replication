'''
Pygame application orchestration for Checkers (Draughts).
Manages the main loop, rendering, and user input for move notation.
'''
import pygame
from board import Board
from rules import GameState
from move_parser import MoveParser, MoveParseError
from ui import InputBox
from constants import (
    WIDTH, HEIGHT, BOARD_SIZE, PANEL_HEIGHT, FPS,
    BG_COLOR, TEXT_COLOR, INFO_TEXT_COLOR, STATUS_OK_COLOR, STATUS_ERR_COLOR
)
class GameApp:
    def __init__(self):
        pygame.display.set_caption("Checkers (Draughts)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        # Fonts
        self.font_small = pygame.font.SysFont("arial", 18)
        self.font_medium = pygame.font.SysFont("arial", 22, bold=True)
        self.font_large = pygame.font.SysFont("arial", 28, bold=True)
        # Game state and UI
        self.board = Board()
        self.state = GameState(self.board)
        self.input_box = InputBox(
            10, BOARD_SIZE + 10, WIDTH - 20, 36, self.font_medium,
            placeholder="Enter move (e.g., b6-c5 or c3:e5:g7), Enter to submit"
        )
        self.status_message = "Red to move. Forced captures are enforced."
        self.status_color = STATUS_OK_COLOR
        self.running = True
    def reset(self):
        self.board = Board()
        self.state = GameState(self.board)
        self.status_message = "New game started. Red to move."
        self.status_color = STATUS_OK_COLOR
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_h:
                        self._show_help_popup()
                submit = self.input_box.handle_event(event)
                if submit is not None:
                    text = submit.strip()
                    if text:
                        self.handle_move_input(text)
            self.draw()
            self.clock.tick(FPS)
    def _show_help_popup(self):
        # Simple console help; GUI shows quick help text already
        print("Help:")
        print("- Enter moves using coordinates a-h for columns and 1-8 for rows.")
        print("- Examples:")
        print("  b6-c5           (simple move)")
        print("  c3:e5:g7        (multiple captures)")
        print("- Separators '-', ':', 'x', 'to' and spaces are accepted.")
        print("- Forced captures are enforced.")
        print("- Men move and capture forward only; kings move and capture both ways.")
        print("- Press R to restart, ESC to quit.")
    def handle_move_input(self, text: str):
        try:
            seq = MoveParser.parse(text)
        except MoveParseError as e:
            self._set_status(f"Parse error: {e}", error=True)
            return
        # Validate and attempt to apply the move
        ok, msg = self.state.try_move(seq)
        if ok:
            self._set_status(msg or f"Move accepted. {'Black' if self.state.current_player == 'black' else 'Red'} to move.", error=False)
            # Check for game over
            over, winner, reason = self.state.is_game_over()
            if over:
                if winner:
                    self._set_status(f"Game over: {winner.capitalize()} wins! ({reason}) - Press R to restart.", error=False)
                else:
                    self._set_status(f"Game over: Draw. ({reason}) - Press R to restart.", error=False)
        else:
            self._set_status(msg or "Illegal move.", error=True)
    def _set_status(self, msg: str, error: bool = False):
        self.status_message = msg
        self.status_color = STATUS_ERR_COLOR if error else STATUS_OK_COLOR
    def draw(self):
        self.screen.fill(BG_COLOR)
        # Draw board and pieces
        self.board.draw(self.screen, self.font_medium, last_move=self.state.last_move)
        # Bottom panel
        panel_rect = pygame.Rect(0, BOARD_SIZE, WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 30), panel_rect)
        # Instructions on left
        instructions = "Type move and press Enter. R: restart, H: help, ESC: quit."
        text_surf = self.font_small.render(instructions, True, INFO_TEXT_COLOR)
        self.screen.blit(text_surf, (10, BOARD_SIZE + PANEL_HEIGHT - 22))
        # Current player
        turn_text = f"Turn: {'Red' if self.state.current_player == 'red' else 'Black'}"
        turn_surf = self.font_medium.render(turn_text, True, TEXT_COLOR)
        self.screen.blit(turn_surf, (10, BOARD_SIZE - 30))
        # Status message
        status_surf = self.font_small.render(self.status_message, True, self.status_color)
        self.screen.blit(status_surf, (10, BOARD_SIZE + 54))
        # Input box
        self.input_box.draw(self.screen)
        pygame.display.flip()