'''
Core game loop and state management for the Flappy Bird clone.
Handles input, updates, rendering, scoring, spawning, collision, and difficulty scaling.
Adds a safe import guard for pygame to provide clearer errors in environments without the dependency.
'''
from __future__ import annotations
import sys
import random
try:
    import pygame  # type: ignore
except Exception:
    pygame = None  # type: ignore
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BG_COLOR, GROUND_HEIGHT, GROUND_COLOR,
    TEXT_COLOR, UI_COLOR,
    START_GAP, MIN_GAP,
    START_SPEED, MAX_SPEED,
    START_SPAWN_MS, MIN_SPAWN_MS,
)
from sprites import Bird, PipePair
class Game:
    """
    Game encapsulates the main loop, game state, rendering, and input.
    """
    def __init__(self) -> None:
        """
        Initialize Pygame subsystems, screen, clock, fonts, and game entities.
        """
        if pygame is None:
            raise RuntimeError(
                "pygame is required to run this game. Please install it with: pip install pygame"
            )
        pygame.init()
        pygame.display.set_caption("Flappy Bird (Python)")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        # Fonts
        self.font_large = pygame.font.SysFont(None, 64)
        self.font_medium = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 24)
        # Game state
        self.state = "menu"  # menu, playing, gameover
        self.score = 0
        self.high_score = 0
        # Entities
        self.bird = None
        self.pipes: list[PipePair] = []
        # Difficulty
        self.pipe_gap = START_GAP
        self.pipe_speed = START_SPEED
        self.spawn_interval_ms = START_SPAWN_MS
        # Timers
        self.last_spawn_time = 0
        # Prepare initial state
        self.reset()
    def reset(self) -> None:
        """
        Reset the game to the initial configuration for a new session.
        """
        # Bird at 30% width, vertical center
        self.bird = Bird(x=int(SCREEN_WIDTH * 0.3), y=int(SCREEN_HEIGHT * 0.5))
        # Clear pipes and score
        self.pipes.clear()
        self.score = 0
        # Reset difficulty
        self.pipe_gap = START_GAP
        self.pipe_speed = START_SPEED
        self.spawn_interval_ms = START_SPAWN_MS
        self.last_spawn_time = pygame.time.get_ticks()
    def start_game(self) -> None:
        """
        Start playing from the menu or after game over.
        """
        self.reset()
        self.state = "playing"
    def update_difficulty(self) -> None:
        """
        Adjust difficulty progressively as score increases by tuning gap size, pipe speed, and spawn interval.
        """
        # Decrease gap and increase speed with score.
        # These linear scalings are balanced for approachable difficulty growth.
        self.pipe_gap = max(MIN_GAP, START_GAP - self.score * 6)
        self.pipe_speed = min(MAX_SPEED, START_SPEED + self.score * 0.20)
        self.spawn_interval_ms = max(MIN_SPAWN_MS, START_SPAWN_MS - self.score * 20)
    def spawn_pipe_pair(self) -> None:
        """
        Spawn a new pair of pipes with a random vertical gap within safe bounds.
        """
        top_margin = 50
        bottom_margin = 50
        max_top = SCREEN_HEIGHT - GROUND_HEIGHT - self.pipe_gap - bottom_margin
        if max_top <= top_margin:
            gap_y_top = top_margin
        else:
            gap_y_top = random.randint(top_margin, max_top)
        x = SCREEN_WIDTH + 20  # Spawn just off the right edge
        pipe = PipePair(x=x, gap_y_top=gap_y_top, gap_height=self.pipe_gap, speed=self.pipe_speed)
        self.pipes.append(pipe)
    def handle_events(self) -> None:
        """
        Process user input and system events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    pygame.quit()
                    raise SystemExit
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if self.state == "menu":
                        self.start_game()
                        self.bird.flap()
                    elif self.state == "playing":
                        self.bird.flap()
                    elif self.state == "gameover":
                        self.start_game()
                        self.bird.flap()
                if event.key == pygame.K_r and self.state == "gameover":
                    self.start_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "menu":
                    self.start_game()
                    self.bird.flap()
                elif self.state == "playing":
                    self.bird.flap()
                elif self.state == "gameover":
                    self.start_game()
                    self.bird.flap()
    def update(self) -> None:
        """
        Update game objects and logic depending on state.
        Ensures no scoring occurs on the same frame as a collision by separating
        collision detection from scoring and returning early upon collision.
        """
        if self.state == "menu":
            # Idle animation: minimal gravity update to show some motion
            self.bird.update()
            self.bird.y = max(50, min(self.bird.y, SCREEN_HEIGHT // 2))
            return
        if self.state != "playing":
            return
        # Update bird physics
        self.bird.update()
        # Spawn pipes over time
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_interval_ms:
            self.spawn_pipe_pair()
            self.last_spawn_time = now
        # Update pipes and check for collisions first
        bird_rect = self.bird.get_rect()
        collided = False
        for pipe in list(self.pipes):
            pipe.update()
            if pipe.collides(bird_rect):
                collided = True
                break
        # Ground collision
        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
        if bird_rect.bottom >= ground_y:
            collided = True
        if collided:
            # End the game immediately; no scoring this frame
            self.state = "gameover"
            return
        # If no collision this frame, handle scoring and difficulty
        bird_x = self.bird.x
        for pipe in list(self.pipes):
            if pipe.check_and_flag_passed(bird_x):
                self.score += 1
                if self.score > self.high_score:
                    self.high_score = self.score
                self.update_difficulty()
        # Remove offscreen pipes
        self.pipes = [p for p in self.pipes if not p.is_offscreen()]
        # Ceiling clamp (no game over for top, just clamp)
        if self.bird.get_rect().top <= 0:
            self.bird.y = self.bird.get_rect().height // 2
            self.bird.vy = 0.0
    def draw(self) -> None:
        """
        Draw the entire frame: background, pipes, ground, bird, score and overlays.
        """
        self.screen.fill(BG_COLOR)
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
        # Draw ground
        pygame.draw.rect(
            self.screen,
            GROUND_COLOR,
            pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT),
            border_radius=0,
        )
        # Draw bird
        self.bird.draw(self.screen)
        # UI: score and overlays
        if self.state == "playing":
            score_surf = self.font_large.render(str(self.score), True, TEXT_COLOR)
            self.screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 20))
        else:
            # Menu or Game Over overlays
            title_text = "Flappy Bird"
            subtitle_text = "Press Space/Click to Start" if self.state == "menu" else "Press Space/Click or R to Restart"
            title = self.font_large.render(title_text, True, UI_COLOR)
            subtitle = self.font_medium.render(subtitle_text, True, UI_COLOR)
            hs_text = self.font_small.render(f"High Score: {self.high_score}", True, UI_COLOR)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 3 + 70))
            self.screen.blit(hs_text, (SCREEN_WIDTH // 2 - hs_text.get_width() // 2, SCREEN_HEIGHT // 3 + 110))
            if self.state == "gameover":
                over = self.font_large.render("Game Over", True, UI_COLOR)
                score_text = self.font_medium.render(f"Score: {self.score}", True, UI_COLOR)
                self.screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, SCREEN_HEIGHT // 3 - 70))
                self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 3 - 20))
        pygame.display.flip()
    def run(self) -> None:
        """
        Main loop: handle events, update game state, and render at a fixed FPS.
        """
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)