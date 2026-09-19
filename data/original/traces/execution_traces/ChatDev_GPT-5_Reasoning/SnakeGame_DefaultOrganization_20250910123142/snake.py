'''
Snake entity: manages position, movement, growth, direction changes, and self-collision.
'''
from collections import deque
class Snake:
    """
    Represents the snake on a grid. The snake is a deque of (x, y) positions.
    Direction is a (dx, dy) tuple.
    """
    def __init__(self, start_pos):
        """
        start_pos: (x, y) tuple for the initial head position.
        Initializes a snake with length 3 moving to the right.
        """
        x, y = start_pos
        self.body = deque()
        # Initial orientation to the right: tail -> ... -> head
        self.body.append((x - 2, y))
        self.body.append((x - 1, y))
        self.body.append((x, y))
        self.direction = (1, 0)  # moving right
    @property
    def head(self):
        return self.body[-1]
    def set_direction(self, new_dir):
        """
        Set the direction to new_dir if it is not a reverse of current direction.
        new_dir: (dx, dy)
        """
        cur_dx, cur_dy = self.direction
        new_dx, new_dy = new_dir
        # Prevent reverse into self if length > 1
        if len(self.body) > 1 and (cur_dx == -new_dx and cur_dy == -new_dy):
            return
        # Ignore no-op direction
        if cur_dx == new_dx and cur_dy == new_dy:
            return
        self.direction = new_dir
    def move(self, grow=False):
        """
        Moves the snake by one cell in the current direction.
        If grow is True, keeps the tail (thus increasing length by 1).
        Returns the new head position.
        """
        hx, hy = self.head
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.append(new_head)
        if not grow:
            self.body.popleft()
        return new_head
    def collides_with_self(self):
        """
        Returns True if the snake's head collides with its body (excluding head).
        """
        head = self.head
        # Check if head appears elsewhere in the body
        for segment in list(self.body)[:-1]:
            if segment == head:
                return True
        return False