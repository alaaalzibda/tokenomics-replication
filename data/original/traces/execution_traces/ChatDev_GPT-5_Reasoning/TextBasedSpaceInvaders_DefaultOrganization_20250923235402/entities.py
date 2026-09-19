'''
Sprite entity classes for the Simple Space Invaders game:
- Player: controllable ship with movement and shooting.
- Bullet: projectile moving vertically.
- Alien: enemy sprite forming part of the fleet.
'''
import pygame
import settings
class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.width = settings.PLAYER_WIDTH
        self.height = settings.PLAYER_HEIGHT
        # Create a surface with transparent background for a simple ship shape
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_ship()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = settings.PLAYER_SPEED
        self.last_shot_ms = 0
    def _draw_ship(self):
        # Draw a simple triangular ship on self.image
        surf = self.image
        surf.fill((0, 0, 0, 0))  # transparent
        w, h = surf.get_size()
        hull_color = settings.GREEN
        # Body rectangle
        body_rect = pygame.Rect(w * 0.2, h * 0.4, w * 0.6, h * 0.5)
        pygame.draw.rect(surf, hull_color, body_rect, border_radius=6)
        # Nose triangle
        nose_points = [(w * 0.5, 0), (w * 0.15, h * 0.5), (w * 0.85, h * 0.5)]
        pygame.draw.polygon(surf, hull_color, nose_points)
        # Accent stripe
        pygame.draw.rect(surf, (255, 255, 255, 70), pygame.Rect(w * 0.45, h * 0.2, w * 0.1, h * 0.6))
    def update(self, keys: pygame.key.ScancodeWrapper):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        self.rect.x += dx
        # Confine within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > settings.WIDTH:
            self.rect.right = settings.WIDTH
    def shoot(self, now_ms: int):
        # Returns a Bullet if cooldown elapsed; otherwise, None.
        if now_ms - self.last_shot_ms >= settings.SHOOT_COOLDOWN_MS:
            self.last_shot_ms = now_ms
            x = self.rect.centerx
            y = self.rect.top - settings.BULLET_HEIGHT // 2
            return Bullet(x, y, dy=settings.BULLET_SPEED)
        return None
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, dy: int):
        super().__init__()
        self.image = pygame.Surface((settings.BULLET_WIDTH, settings.BULLET_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.image, settings.CYAN, self.image.get_rect(), border_radius=2)
        self.rect = self.image.get_rect(center=(x, y))
        self.dy = dy
    def update(self):
        self.rect.y += self.dy
        # Kill off-screen
        if self.rect.bottom < 0 or self.rect.top > settings.HEIGHT:
            self.kill()
class Alien(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, color_index: int = 0):
        super().__init__()
        w, h = settings.ALIEN_WIDTH, settings.ALIEN_HEIGHT
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self._draw_alien(settings.ALIEN_COLORS[color_index % len(settings.ALIEN_COLORS)])
        self.rect = self.image.get_rect(topleft=(x, y))
    def _draw_alien(self, color):
        surf = self.image
        surf.fill((0, 0, 0, 0))
        w, h = surf.get_size()
        body_rect = pygame.Rect(w * 0.1, h * 0.25, w * 0.8, h * 0.5)
        pygame.draw.rect(surf, color, body_rect, border_radius=4)
        # Eyes
        eye_w, eye_h = int(w * 0.15), int(h * 0.2)
        left_eye = pygame.Rect(int(w * 0.22), int(h * 0.32), eye_w, eye_h)
        right_eye = pygame.Rect(int(w * 0.63), int(h * 0.32), eye_w, eye_h)
        pygame.draw.rect(surf, settings.BLACK, left_eye, border_radius=3)
        pygame.draw.rect(surf, settings.BLACK, right_eye, border_radius=3)
        # Legs
        leg_w, leg_h = int(w * 0.18), int(h * 0.2)
        for i in range(4):
            x = int(w * (0.12 + i * 0.22))
            y = int(h * 0.75)
            pygame.draw.rect(surf, color, pygame.Rect(x, y, leg_w, leg_h), border_radius=3)
    def update(self):
        # Movement managed by AlienFleet
        return