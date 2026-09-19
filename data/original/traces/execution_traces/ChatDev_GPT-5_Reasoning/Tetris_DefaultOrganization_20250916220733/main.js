'''
"Entry point for the Tetris game. It initializes the Game with canvas elements, centralizes pause/resume (KeyP) handling to keep RAF loop and UI in sync, binds UI buttons, and starts the animation loop."
'''
import { Game } from './game.js';
function setupCanvasHiDPI(canvas, width, height) {
  const dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 2));
  canvas.width = Math.floor(width * dpr);
  canvas.height = Math.floor(height * dpr);
  canvas.style.width = width + 'px';
  canvas.style.height = height + 'px';
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
}
const boardCanvas = document.getElementById('board');
const nextCanvas = document.getElementById('next');
const boardCtx = setupCanvasHiDPI(boardCanvas, 320, 640);
const nextCtx = setupCanvasHiDPI(nextCanvas, 128, 128);
const scoreEl = document.getElementById('score');
const linesEl = document.getElementById('lines');
const levelEl = document.getElementById('level');
const btnStart = document.getElementById('btn-start');
const btnPause = document.getElementById('btn-pause');
const btnRestart = document.getElementById('btn-restart');
const game = new Game({
  boardCtx,
  nextCtx,
  scoreEl,
  linesEl,
  levelEl,
  cols: 10,
  rows: 20,
  cellSize: 32, // logical cell size (canvas scaled via HiDPI helper)
});
let rafId = null;
let lastTime = 0;
function loop(timestamp) {
  if (!lastTime) lastTime = timestamp;
  const dt = timestamp - lastTime;
  lastTime = timestamp;
  game.update(dt);
  game.render();
  if (!game.stopped) {
    rafId = requestAnimationFrame(loop);
  } else {
    cancelAnimationFrame(rafId);
  }
}
function startLoop() {
  if (rafId) cancelAnimationFrame(rafId);
  lastTime = 0;
  game.resume();
  rafId = requestAnimationFrame(loop);
}
btnStart.addEventListener('click', () => {
  if (game.isNew || game.isOver) {
    game.reset();
  }
  startLoop();
});
btnPause.addEventListener('click', () => {
  if (game.paused) {
    startLoop();
    btnPause.textContent = 'Pause';
  } else {
    game.pause();
    btnPause.textContent = 'Resume';
  }
});
btnRestart.addEventListener('click', () => {
  game.reset();
  startLoop();
  btnPause.textContent = 'Pause';
});
// Keyboard shortcuts for pause and restart
document.addEventListener('keydown', (e) => {
  if (e.defaultPrevented) return;
  if (e.code === 'KeyP') {
    btnPause.click(); // ensures button label and RAF loop are managed
  } else if (e.code === 'KeyR') {
    btnRestart.click();
  } else if (e.code === 'Enter') {
    btnStart.click();
  }
});
// Auto-start
game.reset();
startLoop();