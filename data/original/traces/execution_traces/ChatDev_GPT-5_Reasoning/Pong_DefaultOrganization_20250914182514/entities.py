'''
Entity classes: Paddle and Ball with movement, rendering, and collision behavior.
'''
import math
import random
import pygame
from typing import Optional
def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a float value to the [lo, hi] range."""
    return max(lo, min(hi, value))
class Paddle:
    """
    Represents a vertical Pong paddle controlled by the player.
    """
    def __init__(self, x: int, y: int, width: int, height: int, speed: float, screen_height: int):
        """
        Initialize the paddle.
        Args:
            x: Left coordinate of the paddle.
            y: Top coordinate of the paddle.
            width: Paddle width in pixels.
            height: Paddle height in pixels.
            speed: Movement speed in pixels per second.
            screen_height: Screen height to clamp movement.
        """
        self._rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.screen_height = screen_height
        self._direction = 0  # -1 (up), 0 (idle), +1 (down)
    @property
    def rect(self) -> pygame.Rect:
        """Return the pygame.Rect of the paddle."""
        return self._rect
    @property
    def center_y(self) -> float:
        """Vertical center of the paddle."""
        return self._rect.centery
    def move(self, direction: int) -> None:
        """
        Set movement direction.
        Args:
            direction: -1 for up, 0 for idle, +1 for down.
        """
        if direction < 0:
            self._direction = -1
        elif direction > 0:
            self._direction = 1
        else:
            self._direction = 0
    def update(self, dt: float) -> None:
        """
        Move the paddle based on the current direction and clamp to screen bounds.
        Args:
            dt: Delta time in seconds.
        """
        dy = self.speed * dt * self._direction
        if dy != 0.0:
            self._rect.y += int(dy)
            # Continuous movement needs precise clamping
            if self._rect.top < 0:
                self._rect.top = 0
            if self._rect.bottom > self.screen_height:
                self._rect.bottom = self.screen_height
    def draw(self, surface: pygame.Surface, color=(240, 240, 240)) -> None:
        """
        Draw the paddle on the given surface.
        Args:
            surface: Destination surface.
            color: RGB color tuple.
        """
        pygame.draw.rect(surface, color, self._rect)
class Ball:
    """
    Represents the Pong ball with simple 2D physics and collision handling.
    """
    def __init__(self, x: float, y: float, radius: int, speed: float, screen_width: int, screen_height: int,
                 max_speed: float = 900.0, speedup_factor: float = 1.06):
        """
        Initialize the ball.
        Args:
            x: Initial x coordinate (center).
            y: Initial y coordinate (center).
            radius: Ball radius in pixels.
            speed: Initial speed magnitude.
            screen_width: Screen width boundary.
            screen_height: Screen height boundary.
            max_speed: Maximum speed magnitude.
            speedup_factor: Multiplier applied on paddle hits.
        """
        self.x = float(x)
        self.y = float(y)
        self.radius = int(radius)
        self.vx = float(speed)  # will be oriented by reset()
        self.vy = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.base_speed = float(speed)
        self.max_speed = float(max_speed)
        self.speedup_factor = float(speedup_factor)
        # Initialize with a random direction
        self.reset(self.screen_width / 2, self.screen_height / 2, direction=None)
    def get_rect(self) -> pygame.Rect:
        """
        Get a rect that bounds the ball for collision detection.
        """
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           self.radius * 2, self.radius * 2)
    def reset(self, center_x: float, center_y: float, direction: Optional[int] = None) -> None:
        """
        Reset ball to the center and set a new random or specified launch direction.
        Args:
            center_x: New center x.
            center_y: New center y.
            direction: If -1 launch left, +1 launch right, None to randomize.
        """
        self.x = float(center_x)
        self.y = float(center_y)
        # Determine horizontal direction
        if direction is None:
            dir_x = random.choice([-1, 1])
        else:
            dir_x = -1 if direction < 0 else 1
        # Randomize initial vertical component within a sensible range
        angle = random.uniform(-0.35, 0.35)  # about +/- 20 degrees
        speed = self.base_speed
        self.vx = math.cos(angle) * speed * dir_x
        self.vy = math.sin(angle) * speed
    def _normalize_velocity(self, speed: float) -> None:
        """
        Normalize current velocity to the given speed magnitude.
        """
        mag = math.hypot(self.vx, self.vy)
        if mag == 0:
            # Avoid division by zero; give a slight nudge
            self.vx, self.vy = speed, 0.0
            return
        scale = speed / mag
        self.vx *= scale
        self.vy *= scale
    def _increase_speed(self) -> None:
        """
        Increase speed after paddle hit, clamped to max_speed.
        """
        current_speed = math.hypot(self.vx, self.vy)
        new_speed = min(self.max_speed, current_speed * self.speedup_factor)
        self._normalize_velocity(new_speed)
    def _bounce_vertical(self) -> None:
        """
        Reflect vertical velocity and clamp within screen.
        """
        self.vy = -self.vy
        # Clamp inside screen to avoid sticking
        if self.y - self.radius < 0:
            self.y = self.radius
        if self.y + self.radius > self.screen_height:
            self.y = self.screen_height - self.radius
    def _handle_paddle_collision(self, paddle: Paddle, is_left: bool) -> None:
        """
        Reflect off the given paddle and adjust trajectory based on impact point.
        Args:
            paddle: The paddle collided with.
            is_left: True if left paddle, False if right paddle.
        """
        # Compute relative impact point (-1 at top, +1 at bottom)
        rel = (self.y - paddle.center_y) / (paddle.rect.height / 2.0)
        rel = _clamp(rel, -1.0, 1.0)
        # Increase speed and compute target magnitude
        self._increase_speed()
        speed = math.hypot(self.vx, self.vy)
        # Vertical component influenced by impact point
        self.vy = rel * speed * 0.8
        # Horizontal component must point away from the paddle
        horiz = max(0.2, math.sqrt(max(0.0, speed * speed - self.vy * self.vy)))
        self.vx = horiz * (1 if is_left else -1)
        # Nudge the ball outside the paddle to avoid sticking
        if is_left:
            self.x = paddle.rect.right + self.radius + 0.01
        else:
            self.x = paddle.rect.left - self.radius - 0.01
    def update(self, dt: float, left_paddle: Paddle, right_paddle: Paddle) -> None:
        """
        Update the ball position and handle collisions.
        Args:
            dt: Delta time in seconds.
            left_paddle: Left player's paddle.
            right_paddle: Right player's paddle.
        """
        # Move
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Top/bottom wall collisions
        if self.y - self.radius <= 0 or self.y + self.radius >= self.screen_height:
            self._bounce_vertical()
        # Paddle collisions: check rect overlap and direction to reduce false positives
        ball_rect = self.get_rect()
        # Left paddle collision
        if self.vx < 0 and ball_rect.colliderect(left_paddle.rect):
            self._handle_paddle_collision(left_paddle, is_left=True)
        # Right paddle collision
        ball_rect = self.get_rect()  # refresh after potential adjustment
        if self.vx > 0 and ball_rect.colliderect(right_paddle.rect):
            self._handle_paddle_collision(right_paddle, is_left=False)
    def draw(self, surface: pygame.Surface, color=(240, 240, 240)) -> None:
        """
        Draw the ball on the given surface.
        Args:
            surface: Destination surface.
            color: RGB color tuple.
        """
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)