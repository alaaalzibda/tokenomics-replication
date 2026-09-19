'''
UI utilities: Button widget and text drawing helper for menus and overlays.
'''
import pygame
class Button:
    """
    A simple rectangular button with hover and click detection.
    """
    def __init__(self, rect, text, font, base_color, hover_color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.is_hovered(mouse_pos) else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        # Draw border
        pygame.draw.rect(surface, (100, 100, 100), self.rect, width=2, border_radius=8)
        # Draw text centered
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    def was_clicked(self, event, mouse_pos):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(mouse_pos)
def draw_text(surface, text, font, color, center_pos):
    """
    Renders text centered at center_pos on the given surface.
    """
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center_pos)
    surface.blit(surf, rect)