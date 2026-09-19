'''
Food entity: manages spawning food on the grid away from the snake and rendering it.
'''
import random
import pygame
from settings import FOOD_COLOR, CELL_SIZE
class Food:
    """
    Represents a food item on the grid. Can spawn randomly on empty cells.
    """
    def __init__(self, grid_width, grid_height, cell_size=CELL_SIZE):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.position = None
    def spawn(self, snake_positions):
        """
        Spawns food at a random position not occupied by the snake.
        snake_positions: iterable of (x, y) tuples.
        Returns True if spawned, False if there was no free space.
        """
        all_cells = {(x, y) for x in range(self.grid_width) for y in range(self.grid_height)}
        free_cells = list(all_cells - set(snake_positions))
        if not free_cells:
            self.position = None
            return False
        self.position = random.choice(free_cells)
        return True
    def draw(self, surface):
        """
        Draw the food as a filled rectangle.
        """
        if self.position is None:
            return
        x, y = self.position
        rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
        pygame.draw.rect(surface, FOOD_COLOR, rect)