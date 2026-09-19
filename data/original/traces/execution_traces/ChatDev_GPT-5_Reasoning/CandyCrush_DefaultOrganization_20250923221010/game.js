'''
Game controller and UI integration for the Match-3 game.
Manages input, state (score, moves/time), rendering, animations, and chain reactions.
'''
/*
Game controller and UI integration for the Match-3 game.
Manages input, state (score, moves/time), rendering, animations, and chain reactions.
*/
import { Board } from './board.js';
import { sleep, formatTime } from './utils.js';
class GameController {
  constructor() {
    // DOM
    this.boardEl = document.getElementById('board');
    this.scoreEl = document.getElementById('score');
    this.movesEl = document.getElementById('moves');
    this.timeEl = document.getElementById('time');
    this.messageEl = document.getElementById('message');
    this.overlayEl = document.getElementById('overlay');
    this.overlayTitleEl = document.getElementById('overlayTitle');
    this.overlaySubtitleEl = document.getElementById('overlaySubtitle');
    this.overlayNewGameBtn = document.getElementById('overlayNewGame');
    this.newGameBtn = document.getElementById('newGameBtn');
    this.shuffleBtn = document.getElementById('shuffleBtn');
    this.modeInputs = document.querySelectorAll('input[name="mode"]');
    // Settings
    this.rows = 8;
    this.cols = 8;
    this.candyTypes = 6;
    this.defaultMoves = 30;
    this.defaultTime = 120;
    // State
    this.board = new Board(this.rows, this.cols, this.candyTypes);
    this.selected = null;
    this.locked = false;
    this.score = 0;
    this.movesLeft = this.defaultMoves;
    this.timeLeft = this.defaultTime;
    this.mode = 'moves'; // 'moves' or 'time'
    this.timerHandle = null;
    this.gameOver = false;
    this.bindEvents();
    this.startNewGame({ mode: this.mode });
  }
  bindEvents() {
    this.newGameBtn.addEventListener('click', () => this.startNewGame({ mode: this.mode }));
    this.shuffleBtn.addEventListener('click', async () => {
      if (this.locked || this.gameOver) return;
      this.setMessage('Reshuffling...');
      this.setInteractivity(false);
      this.board.reshuffle();
      await sleep(150);
      this.renderBoard();
      this.setInteractivity(true);
      this.setMessage('');
    });
    this.overlayNewGameBtn.addEventListener('click', () => {
      this.overlayEl.classList.add('hidden');
      this.startNewGame({ mode: this.mode });
    });
    this.modeInputs.forEach(input => {
      input.addEventListener('change', (e) => {
        this.mode = e.target.value;
        this.updateModeDisplays();
      });
    });
  }
  updateModeDisplays() {
    const movesStat = document.querySelector('.stat.moves');
    const timeStat = document.querySelector('.stat.time');
    if (this.mode === 'moves') {
      movesStat.classList.remove('hidden');
      timeStat.classList.add('hidden');
    } else {
      movesStat.classList.add('hidden');
      timeStat.classList.remove('hidden');
    }
  }
  setMessage(msg) {
    this.messageEl.textContent = msg || '';
  }
  setInteractivity(enabled) {
    this.locked = !enabled;
    this.boardEl.style.pointerEvents = enabled ? 'auto' : 'none';
    this.newGameBtn.disabled = !enabled;
    this.shuffleBtn.disabled = !enabled;
  }
  async startNewGame({ mode = 'moves' } = {}) {
    // Reset state
    this.mode = mode;
    this.gameOver = false;
    this.score = 0;
    this.movesLeft = this.defaultMoves;
    this.timeLeft = this.defaultTime;
    this.selected = null;
    this.setMessage('');
    // Timer cleanup
    if (this.timerHandle) {
      clearInterval(this.timerHandle);
      this.timerHandle = null;
    }
    // Initialize board
    this.board = new Board(this.rows, this.cols, this.candyTypes);
    this.board.initializeBoard();
    // Safety: if invariants somehow failed, reshuffle until valid
    let guard = 0;
    while ((this.board.findAllMatches().size > 0 || !this.board.hasAnyValidMoves()) && guard++ < 50) {
      this.board.reshuffle();
    }
    // Render
    this.prepareBoardGrid();
    this.renderBoard();
    this.updateHUD();
    this.overlayEl.classList.add('hidden');
    this.updateModeDisplays();
    // Start timer if time mode
    if (this.mode === 'time') {
      this.timerHandle = setInterval(() => this.tickTimer(), 1000);
    }
  }
  prepareBoardGrid() {
    // Configure CSS grid
    this.boardEl.style.gridTemplateRows = `repeat(${this.rows}, var(--tile-size))`;
    this.boardEl.style.gridTemplateColumns = `repeat(${this.cols}, var(--tile-size))`;
    // Build cells once with listeners
    this.boardEl.innerHTML = '';
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        const tile = document.createElement('div');
        tile.className = 'tile';
        tile.setAttribute('role', 'gridcell');
        tile.dataset.r = r;
        tile.dataset.c = c;
        tile.addEventListener('click', () => this.onTileClick(r, c));
        this.boardEl.appendChild(tile);
      }
    }
  }
  renderBoard(highlightSet = null) {
    // Update tiles
    for (const tile of this.boardEl.children) {
      const r = parseInt(tile.dataset.r, 10);
      const c = parseInt(tile.dataset.c, 10);
      const val = this.board.grid[r][c];
      tile.className = 'tile'; // reset classes
      tile.style.background = ''; // reset inline background to allow class styles
      if (val !== null) {
        tile.classList.add(`candy-${val}`);
      } else {
        // Empty slot effect
        tile.style.background = 'linear-gradient(145deg, rgba(255,255,255,0.12), rgba(255,255,255,0.06))';
      }
      if (this.selected && this.selected.r === r && this.selected.c === c) {
        tile.classList.add('selected');
      }
      if (highlightSet && highlightSet.has(`${r},${c}`)) {
        tile.classList.add('clearing');
      } else {
        tile.classList.remove('clearing');
      }
    }
  }
  onTileClick(r, c) {
    if (this.locked || this.gameOver) return;
    const clicked = { r, c };
    if (!this.selected) {
      this.selected = clicked;
      this.renderBoard();
      return;
    }
    const s = this.selected;
    if (s.r === r && s.c === c) {
      // Deselect
      this.selected = null;
      this.renderBoard();
      return;
    }
    if (!this.board.areAdjacent(s.r, s.c, r, c)) {
      // Select a new tile if not adjacent
      this.selected = clicked;
      this.renderBoard();
      return;
    }
    // Try swap
    this.trySwap(s.r, s.c, r, c);
  }
  async trySwap(r1, c1, r2, c2) {
    if (this.locked) return;
    // Check validity
    const valid = this.board.willSwapCreateMatch(r1, c1, r2, c2);
    if (!valid) {
      // Flash invalid animation
      const idx1 = r1 * this.cols + c1;
      const idx2 = r2 * this.cols + c2;
      const t1 = this.boardEl.children[idx1];
      const t2 = this.boardEl.children[idx2];
      t1.classList.add('invalid');
      t2.classList.add('invalid');
      setTimeout(() => { t1.classList.remove('invalid'); t2.classList.remove('invalid'); }, 220);
      this.setMessage('Invalid move: must create a match.');
      // Keep selection on the second tile for convenience
      this.selected = { r: r2, c: c2 };
      this.renderBoard();
      return;
    }
    this.setInteractivity(false);
    this.setMessage('');
    // Perform swap
    this.board.swap(r1, c1, r2, c2);
    this.selected = null;
    this.renderBoard();
    await sleep(100);
    // Resolve chains
    await this.resolveChains();
    // Deduct move in moves mode
    if (this.mode === 'moves') {
      this.movesLeft = Math.max(0, this.movesLeft - 1);
    }
    // If no valid moves remain, reshuffle
    if (!this.board.hasAnyValidMoves() && !this.gameOver) {
      this.setMessage('No moves left. Reshuffling...');
      await sleep(350);
      this.board.reshuffle();
      this.renderBoard();
      await sleep(120);
      this.setMessage('');
    }
    this.updateHUD();
    // End conditions
    if (this.mode === 'moves' && this.movesLeft <= 0) {
      await this.finishAfterSettled('No moves left!');
    }
    this.setInteractivity(!this.gameOver);
  }
  async resolveChains() {
    let chain = 0;
    while (true) {
      const matches = this.board.findAllMatches();
      if (matches.size === 0) break;
      chain += 1;
      // Highlight matched cells
      this.renderBoard(matches);
      await sleep(220);
      // Clear matches
      const cleared = this.board.clearMatches(matches);
      // Score: 10 per candy * chain multiplier
      const points = cleared * 10 * chain;
      this.score += points;
      this.renderBoard();
      await sleep(100);
      // Gravity and refill
      this.board.applyGravity();
      this.renderBoard();
      await sleep(100);
      this.board.refill();
      this.renderBoard();
      await sleep(120);
    }
  }
  updateHUD() {
    this.scoreEl.textContent = String(this.score);
    this.movesEl.textContent = String(this.movesLeft);
    this.timeEl.textContent = formatTime(this.timeLeft);
  }
  async finishAfterSettled(reason) {
    // Wait a beat to finish any visual updates
    await sleep(200);
    this.endGame(reason);
  }
  endGame(reason) {
    if (this.gameOver) return;
    this.gameOver = true;
    this.setInteractivity(false);
    if (this.timerHandle) {
      clearInterval(this.timerHandle);
      this.timerHandle = null;
    }
    this.overlayTitleEl.textContent = 'Game Over';
    this.overlaySubtitleEl.textContent = `${reason} Final score: ${this.score}`;
    this.overlayEl.classList.remove('hidden');
  }
  tickTimer() {
    if (this.gameOver) return;
    this.timeLeft = Math.max(0, this.timeLeft - 1);
    this.updateHUD();
    if (this.timeLeft <= 0) {
      this.endGame('Time up!');
    }
  }
}
// Initialize game on load
window.addEventListener('DOMContentLoaded', () => {
  new GameController();
});