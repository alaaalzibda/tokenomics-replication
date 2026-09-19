'''
UI rendering: draws a minimal sidebar with player stats and last encountered monster info.
'''
import pygame
from typing import Optional, Tuple
import constants as C
from entities import Player
class UI:
    def __init__(self, font: pygame.font.Font):
        self.font = font
    def _draw_text(self, surface: pygame.Surface, text: str, pos: Tuple[int, int], color=(255, 255, 255)):
        img = self.font.render(text, True, color)
        surface.blit(img, pos)
    def draw(
        self,
        screen: pygame.Surface,
        player: Player,
        level: int,
        last_monster_info: Optional[dict],
        message: str,
    ):
        # UI background
        ui_rect = pygame.Rect(C.GRID_WIDTH * C.TILE_SIZE, 0, C.UI_WIDTH, C.WINDOW_HEIGHT)
        pygame.draw.rect(screen, C.COLOR_UI_BG, ui_rect)
        pad = 12
        x0 = ui_rect.x + pad
        y = pad
        # Headers and lines
        self._draw_text(screen, f"Roguelike", (x0, y), C.COLOR_UI_TEXT)
        y += 28
        pygame.draw.line(screen, C.COLOR_UI_HL, (x0, y), (ui_rect.right - pad, y))
        y += 12
        # Player stats
        self._draw_text(screen, f"Level: {level}", (x0, y), C.COLOR_UI_TEXT)
        y += 24
        self._draw_text(screen, f"HP: {player.hp}", (x0, y), C.COLOR_UI_TEXT)
        y += 32
        # Last monster info
        self._draw_text(screen, "Last Encounter:", (x0, y), C.COLOR_UI_TEXT)
        y += 24
        if last_monster_info is not None:
            hp = last_monster_info.get("hp", "?")
            dmg = last_monster_info.get("damage", "?")
            self._draw_text(screen, f"Monster HP: {hp}", (x0, y), C.COLOR_UI_TEXT)
            y += 22
            self._draw_text(screen, f"Damage taken: {dmg}", (x0, y), C.COLOR_UI_TEXT)
            y += 22
        else:
            self._draw_text(screen, f"(none)", (x0, y), C.COLOR_UI_TEXT)
            y += 22
        y += 10
        pygame.draw.line(screen, C.COLOR_UI_HL, (x0, y), (ui_rect.right - pad, y))
        y += 12
        # Messages
        if message:
            self._draw_text(screen, "Message:", (x0, y), C.COLOR_UI_TEXT)
            y += 22
            # Wrap message if too long
            max_width = C.UI_WIDTH - pad * 2
            words = message.split()
            line = ""
            for word in words:
                attempt = f"{line} {word}".strip()
                if self.font.size(attempt)[0] <= max_width:
                    line = attempt
                else:
                    self._draw_text(screen, line, (x0, y), C.COLOR_UI_TEXT)
                    y += 20
                    line = word
            if line:
                self._draw_text(screen, line, (x0, y), C.COLOR_UI_TEXT)
                y += 20
        # Controls
        y = C.WINDOW_HEIGHT - 120
        pygame.draw.line(screen, C.COLOR_UI_HL, (x0, y), (ui_rect.right - pad, y))
        y += 12
        self._draw_text(screen, "Controls:", (x0, y), C.COLOR_UI_TEXT)
        y += 22
        self._draw_text(screen, "W/A/S/D: Move", (x0, y), C.COLOR_UI_TEXT)
        y += 20
        self._draw_text(screen, "R: Restart", (x0, y), C.COLOR_UI_TEXT)
        y += 20
        self._draw_text(screen, "Esc/Q: Quit", (x0, y), C.COLOR_UI_TEXT)