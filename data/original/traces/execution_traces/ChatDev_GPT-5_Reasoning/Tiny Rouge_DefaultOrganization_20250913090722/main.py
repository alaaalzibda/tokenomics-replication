'''
Entry point for the roguelike game. Initializes and runs the Game.
'''
import pygame
from game import Game
def main():
    pygame.init()
    try:
        game = Game()
        game.run()
    finally:
        pygame.quit()
if __name__ == "__main__":
    main()