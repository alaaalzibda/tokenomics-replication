'''
Simple text input box for Pygame to allow entering moves in notation.
Handles keyboard input and renders a text field.
'''
import pygame
from typing import Optional
from constants import INPUT_BG_COLOR, INPUT_BORDER_COLOR, INPUT_ACTIVE_BORDER_COLOR, TEXT_COLOR
class InputBox:
    def __init__(self, x: int, y: int, w: int, h: int, font: pygame.font.Font, placeholder: str = ""):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self._cursor_visible = True
        self._cursor_timer = 0
        self._cursor_interval = 500  # ms
    def handle_event(self, event) -> Optional[str]:
        # Returns current text if Enter pressed; otherwise None
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                submitted = self.text
                self.text = ""
                return submitted
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                # Deactivate without submission
                self.active = False
            else:
                if event.unicode and event.unicode.isprintable():
                    self.text += event.unicode
        return None
    def draw(self, surface):
        # Background
        pygame.draw.rect(surface, INPUT_BG_COLOR, self.rect)
        border_color = INPUT_ACTIVE_BORDER_COLOR if self.active else INPUT_BORDER_COLOR
        pygame.draw.rect(surface, border_color, self.rect, 2)
        display_text = self.text if (self.text or self.active == True) else self.placeholder
        color = TEXT_COLOR if self.text or self.active else (150, 150, 150)
        text_surf = self.font.render(display_text, True, color)
        surface.blit(text_surf, (self.rect.x + 8, self.rect.y + (self.rect.h - text_surf.get_height()) // 2))
        # Cursor (simple static cursor)
        if self.active:
            cursor_x = self.rect.x + 8 + text_surf.get_width()
            cursor_y = self.rect.y + 6
            cursor_h = self.rect.h - 12
            pygame.draw.line(surface, color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)