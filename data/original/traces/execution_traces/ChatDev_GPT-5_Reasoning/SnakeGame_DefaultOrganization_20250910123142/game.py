'''
Game controller: handles input, timing, movement, collisions, score, and rendering.
Implements input throttling to allow at most one direction change between movement ticks.
Adds Pause/Resume (P or Space) and shows overlay when paused.
'''
import pygame
from settings import (
    CELL_SIZE,
    GRID_WIDTH,
    GRID_HEIGHT,
    BG_COLOR,
    GRID_COLOR,
    SNAKE_HEAD_COLOR,
    SNAKE_BODY_COLOR,
    TEXT_COLOR,
    TEXT_SHADOW,
    FOOD_SCORE,
    DIFFICULTY_SPEEDS,
    TITLE,
)
from snake import Snake
    # Avoid UI imports to decouple core game logic from UI helpers
from food import Food
class Game:
    """
    Encapsulates the snake game logic and rendering.
    """
    def __init__(self, screen, difficulty):
        self.screen = screen
        self.difficulty = difficulty
        self.moves_per_second = DIFFICULTY_SPEEDS.get(difficulty, 12)
        self.clock = pygame.time.Clock()
        self.font_hud = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_big = pygame.font.SysFont("arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("arial", 18)
        # Movement timer event
        self.MOVE_EVENT = pygame.USEREVENT + 1
        interval_ms = max(40, int(1000 / self.moves_per_second))
        pygame.time.set_timer(self.MOVE_EVENT, interval_ms)
        # World entities
        start_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = Snake(start_pos)
        self.food = Food(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)
        self.food.spawn(self.snake.body)
        # Game state
        self.score = 0
        self.game_over = False
        self.victory = False  # True if the snake fills the board
        self.paused = False
        # Direction throttling: allow at most one direction change per movement tick
        self._dir_changed = False
        # Direction mapping for inputs
        self.key_dir_map = {
            pygame.K_UP: (0, -1),
            pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_s: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_d: (1, 0),
        }
        pygame.display.set_caption(f"{TITLE} - {self.difficulty}")
    def reset(self):
        """
        Resets the game state to start a new round with the same difficulty.
        """
        start_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = Snake(start_pos)
        self.food = Food(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)
        self.food.spawn(self.snake.body)
        self.score = 0
        self.game_over = False
        self.victory = False
        self.paused = False
        self._dir_changed = False  # reset throttle
    def handle_input(self, event):
        """
        Processes input events for direction changes and control keys.
        Throttles direction input to one accepted change per movement tick.
        """
        if event.type == pygame.KEYDOWN:
            # Pause/Resume
            if event.key in (pygame.K_p, pygame.K_SPACE) and not self.game_over:
                self.paused = not self.paused
                return None
            # Movement (ignored while paused or game over)
            if event.key in self.key_dir_map and not self.game_over and not self.paused and not self._dir_changed:
                self.snake.set_direction(self.key_dir_map[event.key])
                self._dir_changed = True
            elif event.key == pygame.K_r:
                self.reset()
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                # Will be handled in run loop as quit
                return "quit"
            elif event.key == pygame.K_m:
                return "menu"
        return None
    def step(self):
        """
        Performs one movement tick: move snake, handle food consumption,
        detect collisions, update score, and victory.
        Resets direction-change throttle at the start of the tick.
        """
        if self.game_over or self.paused:
            return
        # Allow one new direction change for the interval after this movement
        self._dir_changed = False
        next_head = self._next_head_pos()
        # Boundary collision
        if not (0 <= next_head[0] < GRID_WIDTH and 0 <= next_head[1] < GRID_HEIGHT):
            self.game_over = True
            return
        # Will we eat?
        will_eat = self.food.position == next_head
        # Move snake (grow if eating)
        self.snake.move(grow=will_eat)
        # Self collision
        if self.snake.collides_with_self():
            self.game_over = True
            return
        if will_eat:
            self.score += FOOD_SCORE
            spawned = self.food.spawn(self.snake.body)
            if not spawned:
                # No free cells left; player filled the board
                self.game_over = True
                self.victory = True
    def _next_head_pos(self):
        """
        Computes the next head position based on current direction, without moving the snake.
        """
        hx, hy = self.snake.head
        dx, dy = self.snake.direction
        return (hx + dx, hy + dy)
    def draw_grid(self, surface):
        """
        Draws a background grid to make movement clearer.
        """
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                surface,
                GRID_COLOR,
                (x * CELL_SIZE, 0),
                (x * CELL_SIZE, GRID_HEIGHT * CELL_SIZE),
                1,
            )
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                surface,
                GRID_COLOR,
                (0, y * CELL_SIZE),
                (GRID_WIDTH * CELL_SIZE, y * CELL_SIZE),
                1,
            )
    def draw(self, surface):
        """
        Renders the game state, including snake, food, score, and any overlays.
        """
        surface.fill(BG_COLOR)
        self.draw_grid(surface)
        # Draw food
        self.food.draw(surface)
        # Draw snake
        for i, (x, y) in enumerate(self.snake.body):
            color = SNAKE_BODY_COLOR if (i < len(self.snake.body) - 1) else SNAKE_HEAD_COLOR
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, rect)
        # HUD: Score and difficulty (include PAUSED tag)
        paused_tag = "  [PAUSED]" if self.paused and not self.game_over else ""
        score_surf = self.font_hud.render(f"Score: {self.score}    {self.difficulty}{paused_tag}", True, TEXT_COLOR)
        surface.blit(score_surf, (10, 8))
        # Overlays
        if self.paused and not self.game_over:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))
            title = "Paused"
            title_shadow = self.font_big.render(title, True, TEXT_SHADOW)
            title_surf = self.font_big.render(title, True, TEXT_COLOR)
            title_pos = title_surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 20))
            shadow_pos = title_shadow.get_rect(center=(title_pos.centerx + 2, title_pos.centery + 2))
            surface.blit(title_shadow, shadow_pos)
            surface.blit(title_surf, title_pos)
            hint = "Press P/Space to resume    R to restart    M for menu    ESC/Q to quit"
            hint1 = self.font_small.render(hint, True, (230, 230, 230))
            hint_pos = hint1.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 30))
            surface.blit(hint1, hint_pos)
        if self.game_over:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surface.blit(overlay, (0, 0))
            title = "You Win!" if self.victory else "Game Over"
            # Shadow
            title_shadow = self.font_big.render(title, True, TEXT_SHADOW)
            title_surf = self.font_big.render(title, True, TEXT_COLOR)
            title_pos = title_surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 40))
            shadow_pos = title_shadow.get_rect(center=(title_pos.centerx + 2, title_pos.centery + 2))
            surface.blit(title_shadow, shadow_pos)
            surface.blit(title_surf, title_pos)
            hint1 = self.font_small.render("Press R to restart    M for menu    ESC/Q to quit", True, (230, 230, 230))
            hint_pos = hint1.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 20))
            surface.blit(hint1, hint_pos)
    def run(self):
        """
        Main game loop for a single session. Returns "menu" to go back to the menu,
        or "quit" to exit the application.
        Ensures the MOVE_EVENT timer is stopped when leaving the loop to avoid
        ghost events during menus or other scenes.
        """
        try:
            while True:
                self.clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "quit"
                    result = self.handle_input(event)
                    if result == "quit":
                        return "quit"
                    if result == "menu":
                        return "menu"
                    if event.type == self.MOVE_EVENT and not self.game_over and not self.paused:
                        self.step()
                self.draw(self.screen)
                pygame.display.flip()
        finally:
            # Ensure the movement timer is stopped when leaving the game loop
            pygame.time.set_timer(self.MOVE_EVENT, 0)
            # Flush any pending MOVE_EVENTs from the queue before returning
            pygame.event.clear(self.MOVE_EVENT)