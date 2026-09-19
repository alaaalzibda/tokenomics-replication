'''
"Piece class encapsulates a tetromino, supporting movement, rotation with wall kicks, and matrix management."
'''
const __DOC__ = `
Piece class:
- Holds type, rotation index, position.
- Provides movement and rotation (with simple wall kicks).
- Exposes current matrix (shape) for board validation/merging.
`;
import { SHAPES } from './shapes.js';
export class Piece {
  constructor(type, spawnX, spawnY) {
    this.type = type;
    this.rotation = 0;
    this.x = spawnX;
    this.y = spawnY;
  }
  get matrix() {
    return SHAPES[this.type][this.rotation];
  }
  clone() {
    const p = new Piece(this.type, this.x, this.y);
    p.rotation = this.rotation;
    return p;
  }
  // Attempt to move by (dx, dy) if valid on the board
  tryMove(board, dx, dy) {
    const nx = this.x + dx;
    const ny = this.y + dy;
    if (board.isValid(this.matrix, nx, ny)) {
      this.x = nx;
      this.y = ny;
      return true;
    }
    return false;
  }
  // Rotate: dir = +1 (CW) or -1 (CCW)
  tryRotate(board, dir) {
    const len = SHAPES[this.type].length;
    const newRot = (this.rotation + dir + len) % len;
    const newMatrix = SHAPES[this.type][newRot];
    // wall kick attempts
    const kicks = [
      [0, 0],
      [-1, 0],
      [1, 0],
      [-2, 0],
      [2, 0],
      [0, -1],
    ];
    for (const [kx, ky] of kicks) {
      const nx = this.x + kx;
      const ny = this.y + ky;
      if (board.isValid(newMatrix, nx, ny)) {
        this.rotation = newRot;
        this.x = nx;
        this.y = ny;
        return true;
      }
    }
    return false;
  }
}