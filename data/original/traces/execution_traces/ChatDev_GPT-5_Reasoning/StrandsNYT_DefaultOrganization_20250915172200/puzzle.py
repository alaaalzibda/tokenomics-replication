'''
Puzzle definition for a Strands-like game. Provides a built-in 6x8 puzzle with a
spangram and themed words covering the entire board without overlap.
Theme: Programming Languages
Spangram: SOFTWARE (touches left and right edges on the top row)
This puzzle's solution paths fill the grid completely and do not overlap.
'''
from typing import List, Tuple, Dict, Set
Coord = Tuple[int, int]
class Puzzle:
    def __init__(
        self,
        rows: int,
        cols: int,
        grid: List[List[str]],
        theme: str,
        spangram: str,
        spangram_path: List[Coord],
        word_paths: Dict[str, List[Coord]],
    ):
        self.rows = rows
        self.cols = cols
        self.grid = grid
        self.theme = theme
        self.spangram = spangram
        self.spangram_path = spangram_path
        self.word_paths = word_paths
        # Build theme words list from word_paths excluding spangram
        self.theme_words = [w for w in word_paths.keys() if w != spangram]
        self.validate_integrity()
    def get_letter(self, r: int, c: int) -> str:
        return self.grid[r][c]
    def all_solution_cells(self) -> Set[Coord]:
        cells = set()
        cells.update(self.spangram_path)
        for w in self.theme_words:
            cells.update(self.word_paths[w])
        return cells
    def validate_integrity(self):
        # Basic dimension checks
        assert len(self.grid) == self.rows
        for row in self.grid:
            assert len(row) == self.cols
        # Check paths spell the correct words
        # Spangram
        sg = "".join(self.get_letter(r, c) for (r, c) in self.spangram_path)
        assert sg == self.spangram, f"Spangram path does not spell {self.spangram}, got {sg}"
        used = set(self.spangram_path)
        for word, path in self.word_paths.items():
            if word == self.spangram:
                continue
            spelled = "".join(self.get_letter(r, c) for (r, c) in path)
            assert spelled == word, f"Path for {word} does not match letters (got {spelled})"
            # Ensure no overlap
            for coord in path:
                assert coord not in used, f"Overlap detected for word {word} at {coord}"
                used.add(coord)
        # Finally ensure every cell is used exactly once across all solution paths
        assert len(used) == self.rows * self.cols, f"Not all cells are used (used {len(used)} of {self.rows*self.cols})"
        # Adjacency check for each path (8-directional)
        def is_adj(a: Coord, b: Coord) -> bool:
            return max(abs(a[0]-b[0]), abs(a[1]-b[1])) == 1 and a != b
        # Check adjacency for spangram
        for i in range(1, len(self.spangram_path)):
            assert is_adj(self.spangram_path[i-1], self.spangram_path[i]), "Spangram path not adjacent step"
        # Check adjacency for theme words
        for word, path in self.word_paths.items():
            if word == self.spangram:
                continue
            for i in range(1, len(path)):
                assert is_adj(path[i-1], path[i]), f"Non-adjacent step in path for {word}"
def default_puzzle() -> "Puzzle":
    rows, cols = 6, 8
    # Grid letters (uppercase)
    # Row0: SOFTWARE (spangram)
    # Row1: PYTHONGO
    # Row2: KOTLINLU
    # Row3: SWIFTRUA
    # Row4: SCALARBY
    # Row5: JULIAUST
    grid = [
        list("SOFTWARE"),
        list("PYTHONGO"),
        list("KOTLINLU"),
        list("SWIFTRUA"),
        list("SCALARBY"),
        list("JULIAUST"),
    ]
    theme = "Programming Languages"
    spangram = "SOFTWARE"
    spangram_path = [(0, c) for c in range(8)]  # across top row touches left and right edges
    # Predefined canonical paths for each themed word to ensure a single, non-overlapping fill
    word_paths: Dict[str, List[Coord]] = {
        # Include spangram in word_paths for integrity checks (it is excluded in theme_words property)
        spangram: spangram_path,
        # Row1: PYTHON (1,0)-(1,5)
        "PYTHON": [(1, c) for c in range(6)],
        # Row1: GO (1,6)-(1,7)
        "GO": [(1, 6), (1, 7)],
        # Row2: KOTLIN (2,0)-(2,5)
        "KOTLIN": [(2, c) for c in range(6)],
        # LUA: L (2,6) -> U (2,7) -> A (3,7)
        "LUA": [(2, 6), (2, 7), (3, 7)],
        # Row3: SWIFT (3,0)-(3,4)
        "SWIFT": [(3, c) for c in range(5)],
        # RUBY: R (3,5) -> U (3,6) -> B (4,6) -> Y (4,7)
        "RUBY": [(3, 5), (3, 6), (4, 6), (4, 7)],
        # Row4: SCALA (4,0)-(4,4)
        "SCALA": [(4, c) for c in range(5)],
        # RUST: R (4,5) -> U (5,5) -> S (5,6) -> T (5,7)
        "RUST": [(4, 5), (5, 5), (5, 6), (5, 7)],
        # Row5: JULIA (5,0)-(5,4) to ensure full-board coverage
        "JULIA": [(5, c) for c in range(5)],
    }
    return Puzzle(
        rows=rows,
        cols=cols,
        grid=grid,
        theme=theme,
        spangram=spangram,
        spangram_path=spangram_path,
        word_paths=word_paths,
    )