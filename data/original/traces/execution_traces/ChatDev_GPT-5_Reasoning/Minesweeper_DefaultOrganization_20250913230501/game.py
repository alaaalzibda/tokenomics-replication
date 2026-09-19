'''
Game logic for Minesweeper, including the board, cells, and game state management.
No GUI code here. Provides deterministic operations for reveal and flag actions.
'''
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional
import random
import time
@dataclass
class Cell:
    """
    Represents a single cell in the Minesweeper grid.
    """
    has_mine: bool = False
    revealed: bool = False
    flagged: bool = False
    adjacent: int = 0  # number of adjacent mines
class Board:
    """
    Encapsulates the Minesweeper board: cells, mine placement, and reveal/flag logic.
    """
    def __init__(self, width: int, height: int, num_mines: int):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")
        total = width * height
        if not (0 < num_mines < total):
            raise ValueError("Number of mines must be between 1 and total cells - 1.")
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.grid: List[List[Cell]] = [[Cell() for _ in range(width)] for _ in range(height)]
        self.mines_placed = False
    def reset(self):
        self.grid = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        self.mines_placed = False
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
    def neighbors(self, x: int, y: int):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    yield nx, ny
    def place_mines(self, first_click: Tuple[int, int]):
        """
        Randomly place mines across the board, avoiding the first clicked cell.
        """
        all_cells = [(x, y) for y in range(self.height) for x in range(self.width)]
        # Exclude the first clicked cell from mine placement to ensure the first click is safe
        if first_click in all_cells:
            all_cells.remove(first_click)
        if self.num_mines > len(all_cells):
            raise ValueError("Too many mines for the board configuration.")
        mine_positions = set(random.sample(all_cells, self.num_mines))
        for (mx, my) in mine_positions:
            self.grid[my][mx].has_mine = True
        self._compute_adjacents()
        self.mines_placed = True
    def _compute_adjacents(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].has_mine:
                    self.grid[y][x].adjacent = -1
                else:
                    count = 0
                    for nx, ny in self.neighbors(x, y):
                        if self.grid[ny][nx].has_mine:
                            count += 1
                    self.grid[y][x].adjacent = count
    def reveal(self, x: int, y: int, first_click: Optional[Tuple[int, int]] = None) -> Tuple[str, Set[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """
        Reveal the cell at (x, y). Returns a tuple:
        - result: 'hit_mine', 'revealed', or 'ignore'
        - changed: set of coordinates that changed visibility
        - exploded_at: (x, y) if a mine exploded, else None
        """
        if not self.in_bounds(x, y):
            return "ignore", set(), None
        if not self.mines_placed:
            # Place mines on first reveal
            if first_click is None:
                first_click = (x, y)
            self.place_mines(first_click)
        cell = self.grid[y][x]
        if cell.flagged or cell.revealed:
            return "ignore", set(), None
        if cell.has_mine:
            cell.revealed = True
            return "hit_mine", {(x, y)}, (x, y)
        changed = set()
        # Flood fill reveal if empty
        self._flood_reveal(x, y, changed)
        return "revealed", changed, None
    def _flood_reveal(self, x: int, y: int, changed: Set[Tuple[int, int]]):
        """
        Reveal using BFS flood fill: reveal zeros and border numbers.
        """
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if not self.in_bounds(cx, cy):
                continue
            cell = self.grid[cy][cx]
            if cell.revealed or cell.flagged:
                continue
            cell.revealed = True
            changed.add((cx, cy))
            if cell.adjacent == 0 and not cell.has_mine:
                for nx, ny in self.neighbors(cx, cy):
                    ncell = self.grid[ny][nx]
                    if not ncell.revealed and not ncell.flagged and (nx, ny) not in changed:
                        stack.append((nx, ny))
    def toggle_flag(self, x: int, y: int) -> bool:
        """
        Toggle a flag on the cell at (x, y). Returns the new flagged state.
        """
        if not self.in_bounds(x, y):
            return False
        cell = self.grid[y][x]
        if cell.revealed:
            return cell.flagged
        cell.flagged = not cell.flagged
        return cell.flagged
    def reveal_all_mines(self) -> Set[Tuple[int, int]]:
        """
        Reveal all mines on the board. Returns set of coordinates changed.
        """
        changed = set()
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell.has_mine and not cell.revealed:
                    cell.revealed = True
                    changed.add((x, y))
        return changed
    def all_safe_cells_revealed(self) -> bool:
        """
        Check if all non-mine cells have been revealed.
        """
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if not cell.has_mine and not cell.revealed:
                    return False
        return True
    def get_cell(self, x: int, y: int) -> Cell:
        return self.grid[y][x]
    def flag_count(self) -> int:
        """
        Count the number of currently flagged cells.
        """
        c = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].flagged:
                    c += 1
        return c
class MinesweeperGame:
    """
    High-level game controller: manages state, integrates Board with timer and win/loss logic.
    """
    def __init__(self, width: int, height: int, mines: int):
        self.board = Board(width, height, mines)
        self.state = "playing"  # 'playing' | 'won' | 'lost'
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None  # freeze moment when game ends
        self.started = False
        self.exploded_at: Optional[Tuple[int, int]] = None
    def left_click(self, x: int, y: int) -> Tuple[str, Set[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """
        Handle a left-click at (x, y).
        Returns (result, changed, exploded_at):
        - result: 'ok', 'won', 'lost', 'ignore'
        """
        if self.state != "playing":
            return "ignore", set(), None
        first_click = None
        if not self.board.mines_placed:
            first_click = (x, y)
            self.started = True
            self.start_time = time.time()
        result, changed, exploded_at = self.board.reveal(x, y, first_click=first_click)
        if result == "hit_mine":
            self.state = "lost"
            self.exploded_at = exploded_at
            self.end_time = time.time()  # freeze timer on loss
            # Reveal all mines as final state
            changed |= self.board.reveal_all_mines()
            return "lost", changed, exploded_at
        if self.board.all_safe_cells_revealed():
            self.state = "won"
            self.end_time = time.time()  # freeze timer on win
            return "won", changed, None
        if result == "revealed":
            return "ok", changed, None
        return "ignore", set(), None
    def right_click(self, x: int, y: int) -> bool:
        """
        Handle a right-click at (x, y). Toggles flag.
        Returns the new flagged state.
        """
        if self.state != "playing":
            return False
        flagged = self.board.toggle_flag(x, y)
        return flagged
    def elapsed_time(self) -> float:
        if not self.started or self.start_time is None:
            return 0.0
        if self.state in ("won", "lost"):
            # Freeze time at end
            return max(0.0, (self.end_time or time.time()) - self.start_time)
        return time.time() - self.start_time