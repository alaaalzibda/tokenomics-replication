'''
Global configuration, colors, physics, and difficulty tuning for the game.
'''
# Screen and timing
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 720
FPS = 60
# Ground
GROUND_HEIGHT = 90
GROUND_COLOR = (200, 170, 90)
# Colors
BG_COLOR = (135, 206, 235)      # Sky blue
PIPE_COLOR = (70, 180, 80)      # Green pipe
PIPE_OUTLINE = (30, 120, 40)
BIRD_COLOR = (255, 215, 0)      # Gold
BIRD_OUTLINE = (120, 100, 0)
TEXT_COLOR = (255, 255, 255)
UI_COLOR = (20, 20, 20)
# Bird
BIRD_SIZE = 34
# Pipes
PIPE_WIDTH = 70
# Physics
GRAVITY = 0.50           # pixels per frame^2
FLAP_STRENGTH = -9.5     # pixels per frame impulse
MAX_DROP_SPEED = 12.0    # terminal velocity
# Difficulty (starting values and caps)
START_GAP = 180
MIN_GAP = 100
START_SPEED = 3.2
MAX_SPEED = 7.5
START_SPAWN_MS = 1500
MIN_SPAWN_MS = 900