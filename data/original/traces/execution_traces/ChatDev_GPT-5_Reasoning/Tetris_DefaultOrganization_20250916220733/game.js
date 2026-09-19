'''
"Game class orchestrates Tetris: piece generation, falling, locking, scoring, levels, rendering hooks, and input actions."
'''
const __DOC__ = `
Game class overview:
- Manages Board, active Piece, next queue (7-bag), timing (gravity/lock delay), and state (score/lines/level).
- Exposes action methods for Input: inputMove, inputRotate, inputSoftDrop, inputHardDrop, togglePause.
- update(dt): advances timers, applies gravity, locks pieces, clears lines, updates scoring and level/speed.
- render(): delegates to Renderer to draw.
Lock delay correctness:
- The lock delay timer is only accrued while the piece is on the ground (cannot move down).
- Gravity/soft drop do not directly modify the lock timer except resetting it upon successful movement.
`;
import { Board } from './board.js';
import { Piece } from './piece.js';
import { Renderer } from './renderer.js';
import { TYPES, SPAWN_OFFSETS } from './shapes.js';
import { shuffleArray } from './utils.js';
import { Input } from './input.js';
export class Game {
  constructor({ boardCtx, nextCtx, scoreEl, linesEl, levelEl, cols = 10, rows = 20, cellSize = 32 }) {
    this.cols = cols;
    this.rows = rows;
    this.cellSize = cellSize;
    this.board = new Board(cols, rows);
    this.renderer = new Renderer(boardCtx, nextCtx, { cols, rows, cellSize });
    this.input = new Input(this);
    this.scoreEl = scoreEl;
    this.linesEl = linesEl;
    this.levelEl = levelEl;
    this.reset();
  }
  reset() {
    this.board.reset();
    this.score = 0;
    this.lines = 0;
    this.level = 1;
    this.dropTimer = 0;
    this.lockDelay = 500; // ms
    this.lockTimer = 0;
    this.dropInterval = this.computeDropInterval(this.level);
    this.active = null;
    this.queue = [];
    this.fillBag();
    this.isNew = false;
    this.isOver = false;
    this.paused = false;
    this.stopped = false;
    this.spawnNewPiece();
    this.updateStats();
  }
  pause() {
    this.paused = true;
    this.stopped = true;
  }
  resume() {
    this.paused = false;
    this.stopped = false;
  }
  togglePause() {
    this.paused = !this.paused;
    this.stopped = this.paused;
  }
  updateStats() {
    if (this.scoreEl) this.scoreEl.textContent = String(this.score);
    if (this.linesEl) this.linesEl.textContent = String(this.lines);
    if (this.levelEl) this.levelEl.textContent = String(this.level);
  }
  computeDropInterval(level) {
    // Faster as level increases; clamp minimum
    // Start at ~1000ms; speed up by ~75ms per level, min ~90ms
    return Math.max(1000 - (level - 1) * 75, 90);
  }
  fillBag() {
    const bag = shuffleArray(TYPES.slice());
    this.queue.push(...bag);
  }
  getNextType() {
    if (this.queue.length < 7) {
      this.fillBag();
    }
    return this.queue.shift();
  }
  spawnNewPiece() {
    const type = this.getNextType();
    const spawnX = Math.floor(this.cols / 2) - 2 + (SPAWN_OFFSETS[type] || 0);
    const spawnY = -2; // allow above top
    const piece = new Piece(type, spawnX, spawnY);
    // Adjust up to the first valid position (y increasing)
    if (!this.board.isValid(piece.matrix, piece.x, piece.y)) {
      // If immediately invalid, game over
      this.isOver = true;
      this.stopped = true;
      return;
    }
    this.active = piece;
    this.lockTimer = 0;
    this.dropTimer = 0;
  }
  // Compute ghost Y by moving down until invalid then taking last valid
  computeGhostY() {
    if (!this.active) return null;
    let y = this.active.y;
    while (this.board.isValid(this.active.matrix, this.active.x, y + 1)) {
      y++;
    }
    return y;
  }
  // Input handlers
  inputMove(dir) {
    if (this.isOver || this.paused) return;
    if (!this.active) return;
    if (this.active.tryMove(this.board, dir, 0)) {
      this.lockTimer = 0; // movement resets lock timer
    }
  }
  inputRotate(dir) {
    if (this.isOver || this.paused) return;
    if (!this.active) return;
    if (this.active.tryRotate(this.board, dir)) {
      this.lockTimer = 0; // rotation resets lock timer
    }
  }
  inputSoftDrop() {
    if (this.isOver || this.paused) return;
    if (!this.active) return;
    if (this.active.tryMove(this.board, 0, 1)) {
      this.score += 1; // soft drop point per cell
      this.updateStats();
      this.dropTimer = 0;
    } else {
      // Do nothing; lock will be handled by on-ground logic in update()
    }
  }
  inputHardDrop() {
    if (this.isOver || this.paused) return;
    if (!this.active) return;
    let dropped = 0;
    while (this.active.tryMove(this.board, 0, 1)) {
      dropped++;
    }
    this.score += dropped * 2; // hard drop points
    this.updateStats();
    this.lockPiece(); // immediate lock after hard drop
  }
  lockPiece() {
    if (!this.active) return;
    this.board.merge(this.active);
    const cleared = this.board.clearLines();
    if (cleared > 0) {
      const base = [0, 100, 300, 500, 800][cleared] || 0;
      this.lines += cleared;
      this.level = Math.floor(this.lines / 10) + 1;
      this.dropInterval = this.computeDropInterval(this.level);
      this.score += base * this.level;
    }
    this.updateStats();
    this.active = null;
    this.spawnNewPiece();
    if (this.isOver) {
      // stop loop
      this.stopped = true;
    }
  }
  update(dt) {
    if (this.stopped || this.paused || this.isOver) return;
    this.dropTimer += dt;
    // Gravity step: only reset lock timer on successful descent
    if (this.dropTimer >= this.dropInterval) {
      this.dropTimer = 0;
      if (this.active) {
        if (this.active.tryMove(this.board, 0, 1)) {
          // successful gravity move resets lock timer
          this.lockTimer = 0;
        }
        // If move fails, do not modify lockTimer here; on-ground section handles it
      }
    }
    // On-ground handling: accrue lock timer exactly once per frame when on ground
    if (this.active) {
      const onGround = !this.board.isValid(this.active.matrix, this.active.x, this.active.y + 1);
      if (onGround) {
        this.lockTimer += dt;
        if (this.lockTimer >= this.lockDelay) {
          this.lockPiece();
          this.lockTimer = 0;
        }
      } else {
        this.lockTimer = 0;
      }
    }
  }
  render() {
    const nextType = this.queue[0];
    const ghostY = this.active ? this.computeGhostY() : null;
    this.renderer.render(this.board, this.active, ghostY, nextType);
    if (this.isOver) {
      this.drawOverlay('Game Over', 'Press Restart (R) to play again');
    } else if (this.paused) {
      this.drawOverlay('Paused', 'Press P to resume');
    }
  }
  drawOverlay(title, subtitle) {
    const ctx = this.renderer.boardCtx;
    const w = this.cols * this.cellSize;
    const h = this.rows * this.cellSize;
    ctx.save();
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.shadowColor = 'rgba(0,0,0,0.6)';
    ctx.shadowBlur = 8;
    ctx.font = 'bold 28px system-ui, sans-serif';
    ctx.fillText(title, w / 2, h / 2 - 8);
    ctx.font = '16px system-ui, sans-serif';
    ctx.fillText(subtitle, w / 2, h / 2 + 18);
    ctx.restore();
  }
}