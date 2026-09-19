'''
Main entry point for the Simple Space Invaders game using Pygame.
Gracefully handles missing pygame by showing an installation hint instead of crashing.
'''
import sys
def main():
    try:
        import pygame  # Imported here to gracefully handle missing dependency
    except ModuleNotFoundError:
        msg = (
            "Required dependency 'pygame' is not installed.\n"
            "Install it with:\n"
            "  pip install pygame\n"
            "Exiting gracefully."
        )
        print(msg)
        return
    from game import Game  # Safe to import after pygame is available
    pygame.init()
    try:
        game = Game()
        game.run()
    finally:
        pygame.quit()
if __name__ == "__main__":
    main()