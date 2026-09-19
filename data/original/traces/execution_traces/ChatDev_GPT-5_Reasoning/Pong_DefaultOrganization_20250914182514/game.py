'''
Game orchestration: input handling, game loop, scoring, serve cooldown,
rendering, and win state management.
'''
import time
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE,
    COLOR_BG, COLOR_FG, COLOR_DIM, COLOR_ACCENT,
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED,
    BALL_RADIUS, BALL_START_SPEED, BALL_MAX_SPEED, BALL_SPEEDUP_FACTOR,
    WINNING_SCORE, SERVE_COOLDOWN_MS, FPS,
    SCORE_FONT_SIZE, INFO_FONT_SIZE, WIN_FONT_SIZE,
    CENTER_DASH_HEIGHT, CENTER_DASH_GAP
)
from entities import Paddle, Ball
class Game:
    """
    Main game controller for Two-Player Pong.
    """
    def __init__(self):
        """Initialize pygame, window, entities, fonts, and game state."""
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        # Fonts
        self.score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)
        self.info_font = pygame.font.SysFont(None, INFO_FONT_SIZE)
        self.win_font = pygame.font.SysFont(None, WIN_FONT_SIZE)
        # Entities
        margin = 24
        left_x = margin
        right_x = SCREEN_WIDTH - margin - PADDLE_WIDTH
        center_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.left_paddle = Paddle(left_x, center_y, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, SCREEN_HEIGHT)
        self.right_paddle = Paddle(right_x, center_y, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, SCREEN_HEIGHT)
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        self.ball = Ball(center_x, center_y, BALL_RADIUS, BALL_START_SPEED,
                         SCREEN_WIDTH, SCREEN_HEIGHT, max_speed=BALL_MAX_SPEED, speedup_factor=BALL_SPEEDUP_FACTOR)
        # Game state
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        # Serve cooldown after scoring
        self.ball_active = True
        self.serve_resume_time = 0  # pygame time in ms when ball resumes
        # Movement directions
        self.left_dir = 0
        self.right_dir = 0
    def process_input(self) -> bool:
        """
        Process events and continuous keypress states.
        Returns:
            False to exit the game loop, True to continue running.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over and event.key == pygame.K_r:
                    self.reset_match()
        # Continuous key states
        keys = pygame.key.get_pressed()
        # Left paddle: W/S
        up_left = keys[pygame.K_w]
        down_left = keys[pygame.K_s]
        # Right paddle: Up/Down
        up_right = keys[pygame.K_UP]
        down_right = keys[pygame.K_DOWN]
        self.left_dir = (-1 if up_left else 0) + (1 if down_left else 0)
        self.right_dir = (-1 if up_right else 0) + (1 if down_right else 0)
        # Normalize directions to -1, 0, or 1
        self.left_dir = max(-1, min(1, self.left_dir))
        self.right_dir = max(-1, min(1, self.right_dir))
        return True
    def reset_round(self, scored_by: str) -> None:
        """
        Handle actions after a point is scored.
        Args:
            scored_by: "left" or "right" indicating who scored.
        """
        if scored_by == "left":
            self.left_score += 1
        elif scored_by == "right":
            self.right_score += 1
        # Check win condition
        if self.left_score >= WINNING_SCORE or self.right_score >= WINNING_SCORE:
            self.game_over = True
            self.ball_active = False
            return
        # Reset ball and start serve cooldown
        direction = -1 if scored_by == "right" else 1  # serve toward the player who conceded last
        self.ball.reset(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, direction=direction)
        self.ball_active = False
        self.serve_resume_time = pygame.time.get_ticks() + SERVE_COOLDOWN_MS
    def reset_match(self) -> None:
        """
        Reset scores, ball, paddles, and state for a new match.
        """
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.left_paddle.rect.centery = SCREEN_HEIGHT // 2
        self.right_paddle.rect.centery = SCREEN_HEIGHT // 2
        self.ball.reset(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, direction=None)
        self.ball_active = False
        self.serve_resume_time = pygame.time.get_ticks() + 800  # brief start delay
    def update(self, dt: float) -> None:
        """
        Update the game world for a single frame.
        Args:
            dt: Delta time in seconds.
        """
        # Move paddles
        self.left_paddle.move(self.left_dir)
        self.right_paddle.move(self.right_dir)
        self.left_paddle.update(dt)
        self.right_paddle.update(dt)
        if self.game_over:
            return
        # Handle serve cooldown
        if not self.ball_active:
            if pygame.time.get_ticks() >= self.serve_resume_time:
                self.ball_active = True
            else:
                return  # Wait until cooldown finishes
        # Update ball
        self.ball.update(dt, self.left_paddle, self.right_paddle)
        # Scoring: ball exits left or right
        if self.ball.x + self.ball.radius < 0:
            # Right player scores
            self.reset_round("right")
        elif self.ball.x - self.ball.radius > SCREEN_WIDTH:
            # Left player scores
            self.reset_round("left")
    def render_center_line(self) -> None:
        """
        Draw a dashed vertical center line.
        """
        dash_h = CENTER_DASH_HEIGHT
        gap = CENTER_DASH_GAP
        x = SCREEN_WIDTH // 2 - 2
        y = 0
        color = COLOR_DIM
        while y < SCREEN_HEIGHT:
            rect = pygame.Rect(x, y, 4, dash_h)
            pygame.draw.rect(self.screen, color, rect)
            y += dash_h + gap
    def render_scores(self) -> None:
        """
        Render the scores for both players at the top of the screen.
        """
        left_surf = self.score_font.render(str(self.left_score), True, COLOR_FG)
        right_surf = self.score_font.render(str(self.right_score), True, COLOR_FG)
        # Positions
        self.screen.blit(left_surf, (SCREEN_WIDTH * 0.25 - left_surf.get_width() / 2, 20))
        self.screen.blit(right_surf, (SCREEN_WIDTH * 0.75 - right_surf.get_width() / 2, 20))
    def render_status(self) -> None:
        """
        Render status messages (cooldown or win).
        """
        if self.game_over:
            winner = "Left Player" if self.left_score > self.right_score else "Right Player"
            win_text = f"{winner} Wins!"
            info_text = "Press R to restart • Esc to quit"
            win_surf = self.win_font.render(win_text, True, COLOR_ACCENT)
            info_surf = self.info_font.render(info_text, True, COLOR_DIM)
            cx = SCREEN_WIDTH // 2
            cy = SCREEN_HEIGHT // 2
            self.screen.blit(win_surf, (cx - win_surf.get_width() // 2, cy - 40))
            self.screen.blit(info_surf, (cx - info_surf.get_width() // 2, cy + 10))
            return
        if not self.ball_active:
            remaining_ms = max(0, self.serve_resume_time - pygame.time.get_ticks())
            remaining = int((remaining_ms / 1000.0) + 0.9)  # round up display
            ready_text = f"Get ready... {remaining}"
            info_surf = self.info_font.render(ready_text, True, COLOR_DIM)
            cx = SCREEN_WIDTH // 2
            cy = SCREEN_HEIGHT // 2
            self.screen.blit(info_surf, (cx - info_surf.get_width() // 2, cy - info_surf.get_height() // 2))
        # Controls hint at bottom
        hint_text = "Left: W/S • Right: ↑/↓ • Esc: Quit"
        hint_surf = self.info_font.render(hint_text, True, (100, 100, 110))
        self.screen.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, SCREEN_HEIGHT - 32))
    def render(self) -> None:
        """
        Render the entire frame (background, center line, entities, UI).
        """
        self.screen.fill(COLOR_BG)
        self.render_center_line()
        # Draw entities
        self.left_paddle.draw(self.screen, COLOR_FG)
        self.right_paddle.draw(self.screen, COLOR_FG)
        if self.ball_active or self.game_over or True:
            # Always draw ball (even during cooldown) so players see the serve position
            self.ball.draw(self.screen, COLOR_FG)
        # UI
        self.render_scores()
        self.render_status()
        pygame.display.flip()
    def run(self) -> None:
        """
        Main loop: process input, update simulation, and render at target FPS.
        """
        running = True
        # Brief initial delay to let players get ready
        self.ball_active = False
        self.serve_resume_time = pygame.time.get_ticks() + 800
        while running:
            running = self.process_input()
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.render()