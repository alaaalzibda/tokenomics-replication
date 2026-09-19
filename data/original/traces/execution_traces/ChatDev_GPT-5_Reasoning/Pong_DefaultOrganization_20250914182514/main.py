'''
Entry point for the two-player Pong game application.
Initializes and runs the game loop via the Game class.
'''
import sys
def main():
    """
    Create a Game instance and run it. Ensures pygame quits properly.
    Provides a clear message if pygame is not installed.
    """
    try:
        import pygame  # Import here to gracefully handle environments without pygame
    except Exception:
        print("Pygame is required to run this game. Please install it with:\n  pip install pygame")
        sys.exit(1)
    from game import Game
    game = Game()
    try:
        game.run()
    finally:
        pygame.quit()
if __name__ == "__main__":
    main()