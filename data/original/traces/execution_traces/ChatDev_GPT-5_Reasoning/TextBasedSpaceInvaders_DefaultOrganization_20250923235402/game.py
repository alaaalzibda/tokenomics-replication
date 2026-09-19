'''
Game controller and alien fleet manager for the Simple Space Invaders game.
Contains:
- AlienFleet: controls collective alien movement and descent behavior.
- Game: manages game loop, states, input, updates, collisions, and rendering.
Performance fix:
- Pre-renders a starfield background once to avoid reseeding the global RNG
  and regenerating stars every frame.
'''
import pygame
import random
import settings
from entities import Player, Bullet, Alien
class AlienFleet:
    def __init__(self, aliens_group: pygame.sprite.Group):
        self.aliens = aliens_group
        self.direction = 1  # 1: right, -1: left
        self.speed = settings.FLEET_START_SPEED
        self.drop_distance = settings.FLEET_DROP_DISTANCE
    def reset_speed(self):
        self.direction = 1
        self.speed = settings.FLEET_START_SPEED
    def bounds(self):
        # Return current leftmost x and rightmost x of the fleet; if empty, return None
        if len(self.aliens) == 0:
            return None
        min_x = min(alien.rect.left for alien in self.aliens)
        max_x = max(alien.rect.right for alien in self.aliens)
        return min_x, max_x
    def update(self):
        if len(self.aliens) == 0:
            return
        # Determine if a drop is needed based on edges
        min_x, max_x = self.bounds()
        hit_right = self.direction > 0 and max_x >= settings.WIDTH - settings.FLEET_MARGIN_X
        hit_left = self.direction < 0 and min_x <= settings.FLEET_MARGIN_X
        if hit_right or hit_left:
            for alien in self.aliens:
                alien.rect.y += self.drop_distance
            self.direction *= -1
            self.speed *= settings.FLEET_SPEEDUP_FACTOR
        # Move horizontally
        for alien in self.aliens:
            # Approximate sub-pixel movement by rounding speed each frame
            alien.rect.x += int(self.direction * round(self.speed))
    def reached_bottom(self, y_limit: int) -> bool:
        # y_limit is a vertical cutoff in screen coordinates. For "aliens reach the bottom",
        # pass settings.HEIGHT (the bottom edge of the screen).
        if len(self.aliens) == 0:
            return False
        max_bottom = max(alien.rect.bottom for alien in self.aliens)
        return max_bottom >= y_limit
class Game:
    def __init__(self):
        # Pygame core
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        # Pre-rendered background with starfield (deterministic)
        self.bg = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        self.bg.fill(settings.DARK_GRAY)
        rng = random.Random(1)
        for _ in range(80):
            x = rng.randint(0, settings.WIDTH - 1)
            y = rng.randint(0, settings.HEIGHT - 1)
            self.bg.fill((40, 40, 40), rect=pygame.Rect(x, y, 2, 2))
        # Fonts
        self.font_big = pygame.font.SysFont(None, settings.BIG_FONT_SIZE)
        self.font_hud = pygame.font.SysFont(None, settings.HUD_FONT_SIZE)
        self.font_small = pygame.font.SysFont(None, settings.SMALL_FONT_SIZE)
        # Game state
        self.running = True
        self.state = "START"  # START, PLAYING, GAME_OVER, VICTORY
        self.score = 0
        self.lives = settings.PLAYER_LIVES
        self.player_safe_until_ms = 0
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        # Entities
        self.player = None
        self.fleet = None
        # Initialize new game state
        self.new_game()
    def new_game(self):
        self.all_sprites.empty()
        self.aliens.empty()
        self.bullets.empty()
        # Player
        start_x = settings.WIDTH // 2
        start_y = settings.HEIGHT - settings.PLAYER_Y_OFFSET
        self.player = Player(start_x, start_y)
        self.all_sprites.add(self.player)
        # Aliens
        self.spawn_aliens(settings.ALIEN_ROWS, settings.ALIEN_COLS)
        self.fleet = AlienFleet(self.aliens)
        self.fleet.reset_speed()
        # Score and lives
        self.score = 0
        self.lives = settings.PLAYER_LIVES
        self.player_safe_until_ms = 0
        # State
        self.state = "START"
    def spawn_aliens(self, rows: int, cols: int):
        # Compute starting top-left for the grid
        grid_width = cols * settings.ALIEN_WIDTH + (cols - 1) * settings.ALIEN_X_SPACING
        start_x = (settings.WIDTH - grid_width) // 2
        y = settings.FLEET_TOP_OFFSET
        for r in range(rows):
            x = start_x
            for c in range(cols):
                alien = Alien(x, y, color_index=r)
                self.aliens.add(alien)
                self.all_sprites.add(alien)
                x += settings.ALIEN_WIDTH + settings.ALIEN_X_SPACING
            y += settings.ALIEN_HEIGHT + settings.ALIEN_Y_SPACING
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                if self.state in ("START", "GAME_OVER", "VICTORY"):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # Start or restart the game
                        self.all_sprites.empty()
                        self.aliens.empty()
                        self.bullets.empty()
                        self.new_game()
                        self.state = "PLAYING"
        # Shooting while playing
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                now = pygame.time.get_ticks()
                bullet = self.player.shoot(now)
                if bullet is not None:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
    def update(self):
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            # Update entities
            self.player.update(keys)
            self.bullets.update()
            self.fleet.update()
            # Collisions and rules
            self.resolve_collisions()
            # Check bottom reach condition against the screen's bottom edge
            if self.fleet.reached_bottom(settings.HEIGHT):
                # Aliens reached the bottom: immediate game over
                self.state = "GAME_OVER"
            # Win condition
            if len(self.aliens) == 0:
                self.state = "VICTORY"
        # Limit frame rate
        self.clock.tick(settings.FPS)
    def resolve_collisions(self):
        # Player bullets hit aliens
        hits = pygame.sprite.groupcollide(self.aliens, self.bullets, True, True)
        if hits:
            destroyed_aliens = len(hits)
            self.score += destroyed_aliens * settings.SCORE_PER_ALIEN
        # Alien collides with player: lose a life with temporary invulnerability
        now = pygame.time.get_ticks()
        if now >= self.player_safe_until_ms:
            # Do NOT remove aliens on collision; preserve challenge and rules
            collided = pygame.sprite.spritecollide(self.player, self.aliens, dokill=False)
            if collided:
                self.lose_life()
    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = "GAME_OVER"
            return
        # Reset player to center and grant invulnerability for a short time
        self.player.rect.centerx = settings.WIDTH // 2
        self.player.rect.centery = settings.HEIGHT - settings.PLAYER_Y_OFFSET
        self.player_safe_until_ms = pygame.time.get_ticks() + settings.INVULNERABLE_MS
        # Clear bullets to reduce immediate hazards
        for b in list(self.bullets):
            b.kill()
    def draw(self):
        # Background (pre-rendered)
        self.screen.blit(self.bg, (0, 0))
        # Draw sprites
        self.all_sprites.draw(self.screen)
        # HUD
        self._draw_hud()
        # Overlays for state
        if self.state == "START":
            self._draw_centered_message("Simple Space Invaders", "Press Enter or Space to Start")
        elif self.state == "GAME_OVER":
            self._draw_centered_message("Game Over", "Press Enter or Space to Restart")
        elif self.state == "VICTORY":
            self._draw_centered_message("You Win!", "Press Enter or Space to Play Again")
        pygame.display.flip()
    def _draw_hud(self):
        # Score
        score_surf = self.font_hud.render(f"Score: {self.score}", True, settings.WHITE)
        self.screen.blit(score_surf, (12, 10))
        # Lives
        lives_text = self.font_hud.render("Lives:", True, settings.WHITE)
        self.screen.blit(lives_text, (settings.WIDTH - 180, 10))
        # Draw life icons as small ship silhouettes
        icon_w, icon_h = 22, 14
        x = settings.WIDTH - 110
        y = 12
        for i in range(self.lives):
            pygame.draw.polygon(
                self.screen,
                settings.GREEN,
                [(x + i * 28 + icon_w // 2, y),
                 (x + i * 28, y + icon_h),
                 (x + i * 28 + icon_w, y + icon_h)],
            )
    def _draw_centered_message(self, title: str, subtitle: str):
        title_surf = self.font_big.render(title, True, settings.YELLOW)
        subtitle_surf = self.font_small.render(subtitle, True, settings.WHITE)
        title_rect = title_surf.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 30))
        subtitle_rect = subtitle_surf.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 20))
        self.screen.blit(title_surf, title_rect)
        self.screen.blit(subtitle_surf, subtitle_rect)
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()