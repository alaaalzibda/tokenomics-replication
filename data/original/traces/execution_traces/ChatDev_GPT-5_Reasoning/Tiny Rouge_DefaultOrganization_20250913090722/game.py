'''
Game management: event loop, rendering, movement, encounters, and level progression.
'''
import random
from typing import Optional, Tuple, Dict
import pygame
import constants as C
from entities import Player, Monster
from mapgen import generate_map, MapData
from ui import UI
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((C.WINDOW_WIDTH, C.WINDOW_HEIGHT))
        pygame.display.set_caption("Tower of the Sorcerer - Inspired Roguelike")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(C.FONT_NAME, C.FONT_SIZE)
        self.ui = UI(self.font)
        # Initialize state
        self.level = 1
        self.player = Player(x=1, y=1, hp=C.PLAYER_START_HP)
        self.map_data: Optional[MapData] = None
        self.last_monster_info: Optional[Dict[str, int]] = None
        self.message: str = ""
        self.game_over: bool = False
        # Load first level
        self._load_level()
    def _load_level(self):
        # Generate a new map with a per-level seed (does not affect global RNG)
        seed = random.randint(0, 1_000_000)
        self.map_data = generate_map(seed=seed)
        # Position player at start
        self.player.x, self.player.y = self.map_data.start
        self.last_monster_info = None
        self.message = f"Level {self.level} - Find the door!"
        self.game_over = False
    def run(self):
        while True:
            self.clock.tick(C.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        return
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self._restart_game()
                        # Ignore other keys when game over
                    else:
                        self.handle_input(event)
            self.draw()
            pygame.display.flip()
    def _restart_game(self):
        self.level = 1
        self.player.hp = C.PLAYER_START_HP
        self._load_level()
    def handle_input(self, event: pygame.event.Event):
        key = event.key
        dx = dy = 0
        if key == pygame.K_w:
            dy = -1
        elif key == pygame.K_s:
            dy = 1
        elif key == pygame.K_a:
            dx = -1
        elif key == pygame.K_d:
            dx = 1
        if dx != 0 or dy != 0:
            self.try_move(dx, dy)
    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < C.GRID_WIDTH and 0 <= y < C.GRID_HEIGHT
    def try_move(self, dx: int, dy: int):
        if not self.map_data:
            return
        target_x = self.player.x + dx
        target_y = self.player.y + dy
        if not self._in_bounds(target_x, target_y):
            return
        tile = self.map_data.grid[target_y][target_x]
        is_monster = (target_x, target_y) in self.map_data.monsters
        is_chest = (target_x, target_y) in self.map_data.chests
        # Walls are impassable
        if tile == C.TILE_WALL:
            self.message = "A solid wall blocks your path."
            return
        # Door is a special passable tile: proceed to next level
        if tile == C.TILE_DOOR:
            self.player.move(dx, dy)
            self.next_level()
            return
        # Only move on floors (with overlays handled before moving)
        if tile == C.TILE_FLOOR:
            if is_monster:
                self.fight_monster_at(target_x, target_y)
                if self.game_over:
                    return  # Don't move if you died to the monster
            if is_chest:
                self.open_chest_at(target_x, target_y)
            self.player.move(dx, dy)
            if not is_monster and not is_chest:
                self.message = ""
            return
        # Any other tile types (shouldn't occur) are treated as blocked
        self.message = "You can't move there."
    def fight_monster_at(self, x: int, y: int):
        if not self.map_data:
            return
        monster: Optional[Monster] = self.map_data.monsters.get((x, y))
        if monster is None:
            # No monster found; nothing to do
            self.message = ""
            return
        damage = monster.hp
        self.player.hp -= damage
        self.last_monster_info = {"hp": monster.hp, "damage": damage}
        self.message = f"You fought a monster (HP {monster.hp}) and took {damage} damage."
        # Remove monster from overlay
        del self.map_data.monsters[(x, y)]
        if self.player.hp <= 0:
            self.player.hp = 0
            self.game_over = True
            self.message = "You died! Press R to restart."
    def open_chest_at(self, x: int, y: int):
        if not self.map_data:
            return
        if (x, y) in self.map_data.chests:
            heal = random.randint(C.CHEST_HEAL_MIN, C.CHEST_HEAL_MAX)
            self.player.hp += heal
            self.map_data.chests.remove((x, y))
            self.message = f"You opened a chest and restored {heal} HP."
    def next_level(self):
        # Proceed to next level; keep player's current HP
        self.level += 1
        self._load_level()
    def draw(self):
        # Draw map region
        self.screen.fill(C.COLOR_BG)
        self._draw_grid()
        self._draw_entities()
        self._draw_player()
        # Draw UI
        self.ui.draw(
            self.screen,
            self.player,
            self.level,
            self.last_monster_info,
            self.message,
        )
        if self.game_over:
            self._draw_game_over_overlay()
    def _draw_grid(self):
        if not self.map_data:
            return
        # Draw base tiles only (WALL/FLOOR/DOOR)
        for y in range(C.GRID_HEIGHT):
            row = self.map_data.grid[y]
            for x in range(C.GRID_WIDTH):
                tile = row[x]
                if tile == C.TILE_WALL:
                    color = C.COLOR_WALL
                elif tile == C.TILE_DOOR:
                    color = C.COLOR_DOOR
                else:
                    color = C.COLOR_FLOOR
                rect = pygame.Rect(x * C.TILE_SIZE, y * C.TILE_SIZE, C.TILE_SIZE, C.TILE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
        # Optional grid lines
        for x in range(C.GRID_WIDTH + 1):
            px = x * C.TILE_SIZE
            pygame.draw.line(self.screen, C.COLOR_GRID_LINES, (px, 0), (px, C.WINDOW_HEIGHT))
        for y in range(C.GRID_HEIGHT + 1):
            py = y * C.TILE_SIZE
            pygame.draw.line(self.screen, C.COLOR_GRID_LINES, (0, py), (C.GRID_WIDTH * C.TILE_SIZE, py))
        # Draw door explicitly on top for clarity
        if self.map_data:
            dx, dy = self.map_data.door
            rect = pygame.Rect(dx * C.TILE_SIZE, dy * C.TILE_SIZE, C.TILE_SIZE, C.TILE_SIZE)
            pygame.draw.rect(self.screen, C.COLOR_DOOR, rect)
    def _draw_entities(self):
        if not self.map_data:
            return
        # Draw chests
        for (cx, cy) in self.map_data.chests:
            rect = pygame.Rect(cx * C.TILE_SIZE, cy * C.TILE_SIZE, C.TILE_SIZE, C.TILE_SIZE)
            pygame.draw.rect(self.screen, C.COLOR_CHEST, rect)
        # Draw monsters
        for (mx, my), _monster in self.map_data.monsters.items():
            rect = pygame.Rect(mx * C.TILE_SIZE, my * C.TILE_SIZE, C.TILE_SIZE, C.TILE_SIZE)
            pygame.draw.rect(self.screen, C.COLOR_MONSTER, rect)
    def _draw_player(self):
        rect = pygame.Rect(self.player.x * C.TILE_SIZE, self.player.y * C.TILE_SIZE, C.TILE_SIZE, C.TILE_SIZE)
        pygame.draw.rect(self.screen, C.COLOR_PLAYER, rect)
    def _draw_game_over_overlay(self):
        overlay = pygame.Surface((C.GRID_WIDTH * C.TILE_SIZE, C.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        text1 = self.font.render("Game Over", True, (255, 255, 255))
        text2 = self.font.render("Press R to restart", True, (200, 200, 200))
        cx = (C.GRID_WIDTH * C.TILE_SIZE) // 2
        cy = C.WINDOW_HEIGHT // 2
        self.screen.blit(text1, (cx - text1.get_width() // 2, cy - 30))
        self.screen.blit(text2, (cx - text2.get_width() // 2, cy + 10))