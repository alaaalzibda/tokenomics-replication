'''
Main entry point for the Snake game application. Provides a menu to choose difficulty,
initializes Pygame and launches the game loop. Adds keyboard shortcuts (1-9) for difficulty
selection and improves vertical centering of buttons.
'''
import sys
import pygame
from settings import WIDTH, HEIGHT, BG_COLOR, TITLE, DIFFICULTY_SPEEDS
from ui import Button, draw_text
from game import Game
def choose_difficulty(screen):
    """
    Displays a difficulty selection menu and returns the chosen difficulty
    or None if the user quits.
    """
    pygame.display.set_caption(TITLE + " - Select Difficulty")
    clock = pygame.time.Clock()
    font_title = pygame.font.SysFont("arial", 48, bold=True)
    font_btn = pygame.font.SysFont("arial", 28, bold=True)
    font_hint = pygame.font.SysFont("arial", 18)
    # Create buttons
    button_width = 240
    button_height = 54
    spacing = 16
    difficulties = list(DIFFICULTY_SPEEDS.keys())
    total_height = len(difficulties) * button_height + (len(difficulties) - 1) * spacing
    start_y = HEIGHT // 2 - total_height // 2
    buttons = []
    for i, diff in enumerate(difficulties):
        rect = pygame.Rect(
            (WIDTH - button_width) // 2,
            start_y + i * (button_height + spacing),
            button_width,
            button_height,
        )
        btn = Button(
            rect,
            f"{i+1}. {diff}",
            font_btn,
            base_color=(40, 40, 40),
            hover_color=(70, 70, 70),
            text_color=(255, 255, 255),
        )
        buttons.append(btn)
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return None
                # Keyboard shortcuts 1..9 for difficulties
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if 0 <= idx < len(difficulties):
                        return difficulties[idx]
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                for btn, diff in zip(buttons, difficulties):
                    if btn.was_clicked(event, mouse):
                        return diff
        screen.fill(BG_COLOR)
        # Title
        draw_text(
            screen,
            "Snake by ChatDev",
            font_title,
            (255, 255, 255),
            (WIDTH // 2, HEIGHT // 2 - total_height // 2 - 60),
        )
        # Draw buttons
        for btn in buttons:
            btn.draw(screen)
        # Hints
        draw_text(
            screen,
            "Click or press 1-4 to choose difficulty. ESC to quit.",
            font_hint,
            (200, 200, 200),
            (WIDTH // 2, HEIGHT - 40),
        )
        pygame.display.flip()
def main():
    """
    Initializes Pygame, shows the difficulty menu, and runs the game.
    """
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    icon_surface = pygame.Surface((32, 32))
    icon_surface.fill((100, 200, 100))
    pygame.display.set_icon(icon_surface)
    while True:
        difficulty = choose_difficulty(screen)
        if difficulty is None:
            pygame.quit()
            sys.exit(0)
        game = Game(screen, difficulty)
        next_state = game.run()
        if next_state == "quit":
            pygame.quit()
            sys.exit(0)
        # If "menu", loop back to difficulty selection
if __name__ == "__main__":
    main()