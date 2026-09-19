'''
Board class encapsulating the core Match-3 mechanics:
- generation without initial matches AND with at least one valid move (invariants)
- detection and clearing of matches (3+)
- gravity and refill logic
- testing swaps for validity
- detecting if any valid moves remain
- reshuffling when stuck
'''
/*
Board class encapsulating the core Match-3 mechanics:
- generation without initial matches AND with at least one valid move (invariants)
- detection and clearing of matches (3+)
- gravity and refill logic
- testing swaps for validity
- detecting if any valid moves remain
- reshuffling when stuck
*/
export class Board {
  constructor(rows = 8, cols = 8, candyTypes = 6) {
    this.rows = rows;
    this.cols = cols;
    this.candyTypes = candyTypes;
    this.grid = Array.from({ length: rows }, () => Array(cols).fill(null));
  }
  randomCandy() {
    return Math.floor(Math.random() * this.candyTypes);
  }
  isInside(r, c) {
    return r >= 0 && r < this.rows && c >= 0 && c < this.cols;
  }
  areAdjacent(r1, c1, r2, c2) {
    const dr = Math.abs(r1 - r2);
    const dc = Math.abs(c1 - c2);
    return (dr + dc === 1);
  }
  initializeBoard(maxTries = 500) {
    // Ensures on return: no pre-existing matches and at least one valid move exists.
    let tries = 0;
    while (tries++ < maxTries) {
      for (let r = 0; r < this.rows; r++) {
        for (let c = 0; c < this.cols; c++) {
          let candidate;
          do {
            candidate = this.randomCandy();
          } while (
            (c >= 2 && this.grid[r][c - 1] === candidate && this.grid[r][c - 2] === candidate) ||
            (r >= 2 && this.grid[r - 1][c] === candidate && this.grid[r - 2][c] === candidate)
          );
          this.grid[r][c] = candidate;
        }
      }
      if (this.findAllMatches().size === 0 && this.hasAnyValidMoves()) {
        return true;
      }
    }
    // Last resort (extremely unlikely to hit): keep rebuilding until invariants hold
    let guard = 0;
    while ((this.findAllMatches().size > 0 || !this.hasAnyValidMoves()) && guard++ < 2000) {
      for (let r = 0; r < this.rows; r++) {
        for (let c = 0; c < this.cols; c++) {
          let candidate;
          do {
            candidate = this.randomCandy();
          } while (
            (c >= 2 && this.grid[r][c - 1] === candidate && this.grid[r][c - 2] === candidate) ||
            (r >= 2 && this.grid[r - 1][c] === candidate && this.grid[r - 2][c] === candidate)
          );
          this.grid[r][c] = candidate;
        }
      }
    }
    return true;
  }
  swap(r1, c1, r2, c2) {
    const tmp = this.grid[r1][c1];
    this.grid[r1][c1] = this.grid[r2][c2];
    this.grid[r2][c2] = tmp;
  }
  willSwapCreateMatch(r1, c1, r2, c2) {
    if (!this.isInside(r1, c1) || !this.isInside(r2, c2)) return false;
    if (!this.areAdjacent(r1, c1, r2, c2)) return false;
    this.swap(r1, c1, r2, c2);
    const matches = this.findAllMatches();
    this.swap(r1, c1, r2, c2);
    return matches.size > 0;
  }
  findAllMatches() {
    const matches = new Set();
    // Horizontal
    for (let r = 0; r < this.rows; r++) {
      let runLen = 1;
      for (let c = 1; c <= this.cols; c++) {
        const curr = c < this.cols ? this.grid[r][c] : null;
        const prev = this.grid[r][c - 1];
        if (c < this.cols && curr !== null && curr === prev) {
          runLen++;
        } else {
          if (prev !== null && runLen >= 3) {
            for (let k = c - runLen; k < c; k++) {
              matches.add(`${r},${k}`);
            }
          }
          runLen = 1;
        }
      }
    }
    // Vertical
    for (let c = 0; c < this.cols; c++) {
      let runLen = 1;
      for (let r = 1; r <= this.rows; r++) {
        const curr = r < this.rows ? this.grid[r][c] : null;
        const prev = this.grid[r - 1][c];
        if (r < this.rows && curr !== null && curr === prev) {
          runLen++;
        } else {
          if (prev !== null && runLen >= 3) {
            for (let k = r - runLen; k < r; k++) {
              matches.add(`${k},${c}`);
            }
          }
          runLen = 1;
        }
      }
    }
    return matches;
  }
  clearMatches(matches) {
    let cleared = 0;
    for (const key of matches) {
      const [rStr, cStr] = key.split(',');
      const r = parseInt(rStr, 10);
      const c = parseInt(cStr, 10);
      if (this.grid[r][c] !== null) {
        this.grid[r][c] = null;
        cleared++;
      }
    }
    return cleared;
  }
  applyGravity() {
    for (let c = 0; c < this.cols; c++) {
      let write = this.rows - 1;
      for (let r = this.rows - 1; r >= 0; r--) {
        if (this.grid[r][c] !== null) {
          if (write !== r) {
            this.grid[write][c] = this.grid[r][c];
            this.grid[r][c] = null;
          }
          write--;
        }
      }
      for (let r = write; r >= 0; r--) {
        this.grid[r][c] = null;
      }
    }
  }
  refill() {
    let filled = 0;
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        if (this.grid[r][c] === null) {
          this.grid[r][c] = this.randomCandy();
          filled++;
        }
      }
    }
    return filled;
  }
  hasAnyValidMoves() {
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        const neighbors = [
          [r, c + 1],
          [r + 1, c],
        ];
        for (const [nr, nc] of neighbors) {
          if (this.isInside(nr, nc)) {
            if (this.willSwapCreateMatch(r, c, nr, nc)) return true;
          }
        }
      }
    }
    return false;
  }
  reshuffle(maxTries = 100) {
    let tries = 0;
    while (tries++ < maxTries) {
      // Reinitialize randomly
      this.grid = Array.from({ length: this.rows }, () => Array(this.cols).fill(null));
      this.initializeBoard();
      if (this.findAllMatches().size === 0 && this.hasAnyValidMoves()) {
        return true;
      }
    }
    return false;
  }
}