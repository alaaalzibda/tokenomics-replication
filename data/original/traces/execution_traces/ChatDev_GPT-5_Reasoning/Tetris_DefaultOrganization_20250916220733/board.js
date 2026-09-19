'''
"Board class manages the Tetris grid, collision detection, line clearing, and integration of locked pieces."
'''
const __DOC__ = `
Board class
- grid: 2D array [rows][cols] of null or piece type string (e.g., 'T')
- isValid(matrix, x, y): checks collision/bounds
- merge(piece): locks the current piece into the grid
- clearLines(): removes full lines and returns number cleared
- reset(): resets the grid
`;
export class Board {
  constructor(cols = 10, rows = 20) {
    this.cols = cols;
    this.rows = rows;
    this.grid = this.createGrid();
  }
  createGrid() {
    const g = new Array(this.rows);
    for (let r = 0; r < this.rows; r++) {
      g[r] = new Array(this.cols).fill(null);
    }
    return g;
  }
  reset() {
    this.grid = this.createGrid();
  }
  isInside(x, y) {
    return x >= 0 && x < this.cols && y < this.rows;
  }
  // Check if matrix at position (x, y) is valid (no solid overlap and inside bounds)
  isValid(matrix, x, y) {
    for (let r = 0; r < matrix.length; r++) {
      for (let c = 0; c < matrix[r].length; c++) {
        if (!matrix[r][c]) continue;
        const nx = x + c;
        const ny = y + r;
        if (ny < 0) continue; // allow above visible top
        if (!this.isInside(nx, ny)) return false;
        if (this.grid[ny][nx]) return false;
      }
    }
    return true;
  }
  // Merge piece cells into grid
  merge(piece) {
    const { matrix, x, y, type } = piece;
    for (let r = 0; r < matrix.length; r++) {
      for (let c = 0; c < matrix[r].length; c++) {
        if (!matrix[r][c]) continue;
        const nx = x + c;
        const ny = y + r;
        if (ny >= 0 && ny < this.rows && nx >= 0 && nx < this.cols) {
          this.grid[ny][nx] = type;
        }
      }
    }
  }
  // Clear full lines and return number of lines cleared
  clearLines() {
    let cleared = 0;
    for (let r = this.rows - 1; r >= 0; r--) {
      if (this.grid[r].every((cell) => cell)) {
        this.grid.splice(r, 1);
        this.grid.unshift(new Array(this.cols).fill(null));
        cleared++;
        r++; // re-check same row index after unshift/splice effect
      }
    }
    return cleared;
  }
}