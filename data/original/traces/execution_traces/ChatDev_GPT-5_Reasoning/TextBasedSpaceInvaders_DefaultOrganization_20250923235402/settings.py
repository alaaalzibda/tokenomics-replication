'''
Global configuration settings and constants for the Simple Space Invaders game.
'''
# Window
TITLE = "Simple Space Invaders"
WIDTH = 800
HEIGHT = 600
FPS = 60
# Colors (R, G, B)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
WHITE = (240, 240, 240)
GREEN = (50, 220, 120)
YELLOW = (255, 235, 59)
RED = (230, 70, 70)
CYAN = (50, 200, 220)
ALIEN_COLORS = [
    (120, 200, 255),
    (80, 170, 240),
    (160, 240, 160),
    (240, 200, 120),
    (240, 120, 160),
]
# Gameplay
PLAYER_SPEED = 6
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 30
PLAYER_Y_OFFSET = 60  # distance from bottom
PLAYER_LIVES = 3
BULLET_SPEED = -10
BULLET_WIDTH = 4
BULLET_HEIGHT = 14
SHOOT_COOLDOWN_MS = 300  # milliseconds between shots
# Aliens
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 28
ALIEN_COLS = 10
ALIEN_ROWS = 5
ALIEN_X_SPACING = 16
ALIEN_Y_SPACING = 16
FLEET_MARGIN_X = 30
FLEET_TOP_OFFSET = 60
FLEET_START_SPEED = 1.2     # pixels per frame
FLEET_SPEEDUP_FACTOR = 1.06 # speed multiplier each time they drop
FLEET_DROP_DISTANCE = 18
# UI
SCORE_PER_ALIEN = 10
BIG_FONT_SIZE = 48
HUD_FONT_SIZE = 24
SMALL_FONT_SIZE = 18
# Player respawn/invulnerability after being hit by an alien
INVULNERABLE_MS = 1200