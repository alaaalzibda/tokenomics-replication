'''
Sprite-like game entities for the Flappy Bird clone.
Defines the Bird (player) and PipePair (obstacles).
Adds a safe import guard for pygame to provide clearer errors in environments without the dependency.
'''
from __future__ import annotations
try:
    import pygame  # type: ignore
except Exception:
    pygame = None  # type: ignore
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    GROUND_HEIGHT,
    PIPE_WIDTH,
    BIRD_SIZE,
    BIRD_COLOR, BIRD_OUTLINE,
    PIPE_COLOR, PIPE_OUTLINE,
    GRAVITY, FLAP_STRENGTH, MAX_DROP_SPEED,
)
class Bird:
    """
    The player's bird character with simple physics and drawing.
    """
    def __init__(self, x: int, y: int) -> None:
        """
        Initialize the bird at position (x, y).
        """
        if pygame is None:
            raise RuntimeError(
                "pygame is required to construct sprites. Please install it with: pip install pygame"
            )
        self.x: float = float(x)
        self.y: float = float(y)
        self.vy: float = 0.0
        self.rotation_deg: float = 0.0
        # Create a circular bird sprite with a simple outline
        self.base_image = pygame.Surface((BIRD_SIZE, BIRD_SIZE), pygame.SRCALPHA)
        center = BIRD_SIZE // 2
        radius = center - 2
        pygame.draw.circle(self.base_image, BIRD_COLOR, (center, center), radius)
        pygame.draw.circle(self.base_image, BIRD_OUTLINE, (center, center), radius, width=2)
        # Add a small beak for character
        beak_width = 8
        beak_height = 6
        beak = [
            (BIRD_SIZE - 6, center),
            (BIRD_SIZE - 6 - beak_width, center - beak_height // 2),
            (BIRD_SIZE - 6 - beak_width, center + beak_height // 2),
        ]
        pygame.draw.polygon(self.base_image, (250, 190, 20), beak)
        # Eye
        pygame.draw.circle(self.base_image, (255, 255, 255), (center - 3, center - 5), 5)
        pygame.draw.circle(self.base_image, (0, 0, 0), (center - 1, center - 5), 2)
    def flap(self) -> None:
        """
        Apply an upward impulse to the bird.
        """
        self.vy = FLAP_STRENGTH
    def update(self) -> None:
        """
        Apply gravity and update the position and rotation.
        """
        # Physics
        self.vy = min(self.vy + GRAVITY, MAX_DROP_SPEED)
        self.y += self.vy
        # Rotate up when moving up, down when falling; clamp rotation
        target_rot = -max(min(self.vy * 4.0, 20.0), -15.0) * 3.0  # scale for visual feedback
        self.rotation_deg = max(min(target_rot, 45.0), -45.0)
        # Clamp Y to screen bounds (top only; ground is handled by Game)
        top_limit = self.get_rect().height // 2
        if self.y < top_limit:
            self.y = float(top_limit)
            self.vy = 0.0
    def get_rect(self) -> 'pygame.Rect':
        """
        Get the current collision rectangle, centered at the bird's position.
        """
        rect = pygame.Rect(0, 0, self.base_image.get_width(), self.base_image.get_height())
        rect.center = (int(self.x), int(self.y))
        return rect
    def draw(self, surface: 'pygame.Surface') -> None:
        """
        Draw the rotated bird image on the given surface.
        """
        rotated = pygame.transform.rotate(self.base_image, self.rotation_deg)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect.topleft)
class PipePair:
    """
    Represents a pair of pipes with a vertical gap that moves horizontally.
    """
    def __init__(self, x: int, gap_y_top: int, gap_height: int, speed: float) -> None:
        """
        Create a new PipePair.
        - x: starting x position (right of the screen)
        - gap_y_top: the y coordinate of the top of the gap
        - gap_height: the size of the gap between top and bottom pipes
        - speed: horizontal speed (pixels per frame) moving left
        """
        if pygame is None:
            raise RuntimeError(
                "pygame is required to construct sprites. Please install it with: pip install pygame"
            )
        self.x: float = float(x)
        self.gap_y_top: int = gap_y_top
        self.gap_height: int = gap_height
        self.speed: float = float(speed)
        self.width: int = PIPE_WIDTH
        # Rectangles for collision are computed from x and gap
        self.top_rect = pygame.Rect(int(self.x), 0, self.width, self.gap_y_top)
        bottom_top_y = self.gap_y_top + self.gap_height
        bottom_height = max(0, SCREEN_HEIGHT - GROUND_HEIGHT - bottom_top_y)
        self.bottom_rect = pygame.Rect(int(self.x), bottom_top_y, self.width, bottom_height)
        self._passed: bool = False
    def _rebuild_rects(self) -> None:
        """
        Recalculate the top and bottom pipe rectangles from current position and gap.
        """
        self.top_rect.update(int(self.x), 0, self.width, self.gap_y_top)
        bottom_top_y = self.gap_y_top + self.gap_height
        bottom_height = max(0, SCREEN_HEIGHT - GROUND_HEIGHT - bottom_top_y)
        self.bottom_rect.update(int(self.x), bottom_top_y, self.width, bottom_height)
    def update(self) -> None:
        """
        Move pipes left according to speed and update rectangles.
        """
        self.x -= self.speed
        self._rebuild_rects()
    def is_offscreen(self) -> bool:
        """
        Return True if the pipe has entirely moved off the left side of the screen.
        """
        return int(self.x) + self.width < 0
    def collides(self, bird_rect: 'pygame.Rect') -> bool:
        """
        Check whether the bird collides with either pipe rect.
        """
        return bird_rect.colliderect(self.top_rect) or bird_rect.colliderect(self.bottom_rect)
    def check_and_flag_passed(self, bird_x: float) -> bool:
        """
        If the bird has passed the pipe (bird_x greater than pipe's right edge)
        and it wasn't already counted, flag as passed and return True.
        """
        if not self._passed and bird_x > self.x + self.width:
            self._passed = True
            return True
        return False
    def draw(self, surface: 'pygame.Surface') -> None:
        """
        Draw the pipes to the given surface.
        """
        # Draw filled rectangles
        pygame.draw.rect(surface, PIPE_COLOR, self.top_rect)
        pygame.draw.rect(surface, PIPE_COLOR, self.bottom_rect)
        # Optional outlines for contrast
        pygame.draw.rect(surface, PIPE_OUTLINE, self.top_rect, width=2)
        pygame.draw.rect(surface, PIPE_OUTLINE, self.bottom_rect, width=2)