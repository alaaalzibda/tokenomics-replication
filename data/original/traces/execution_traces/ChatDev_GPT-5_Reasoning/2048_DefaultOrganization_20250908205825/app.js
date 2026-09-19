'''
Client-side logic: initialize game, capture arrow keys, call backend, and render the board and scores.
'''
(function () {
  const boardEl = document.getElementById('board');
  const scoreEl = document.getElementById('score');
  const maxTileEl = document.getElementById('max-tile');
  const overlayEl = document.getElementById('overlay');
  const newGameBtn = document.getElementById('new-game');
  const tryAgainBtn = document.getElementById('try-again');
  // Local cache of size to build the grid
  let size = 4;
  let isGameOver = false;
  let isAnimating = false;
  function buildGrid(size) {
    boardEl.innerHTML = '';
    boardEl.style.setProperty('--size', size.toString());
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        const cell = document.createElement('div');
        cell.className = 'tile tile-empty';
        cell.dataset.row = r.toString();
        cell.dataset.col = c.toString();
        boardEl.appendChild(cell);
      }
    }
  }
  function valueClass(val) {
    return val > 0 ? `tile-${val}` : 'tile-empty';
  }
  function updateUI(state) {
    if (!state) return;
    const { board, score, max_tile, size: sz, game_over } = state;
    size = sz || 4;
    const cells = boardEl.children;
    if (cells.length !== size * size) {
      buildGrid(size);
    }
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        const idx = r * size + c;
        const cell = boardEl.children[idx];
        const v = board[r][c];
        cell.textContent = v > 0 ? String(v) : '';
        cell.className = `tile ${valueClass(v)}`;
      }
    }
    scoreEl.textContent = String(score);
    maxTileEl.textContent = String(max_tile);
    isGameOver = !!game_over;
    if (isGameOver) {
      overlayEl.classList.remove('hidden');
    } else {
      overlayEl.classList.add('hidden');
    }
  }
  async function fetchJSON(url, options) {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      ...options,
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    return await res.json();
  }
  async function initGame() {
    try {
      const data = await fetchJSON('/init', { method: 'POST', body: '{}' });
      updateUI(data.state);
    } catch (e) {
      console.error('Failed to init game:', e);
    }
  }
  async function refreshState() {
    try {
      const data = await fetchJSON('/state', { method: 'GET' });
      updateUI(data.state);
    } catch (e) {
      console.error('Failed to load state:', e);
    }
  }
  async function doMove(dir) {
    if (isGameOver || isAnimating) return;
    isAnimating = true;
    try {
      const data = await fetchJSON('/move', {
        method: 'POST',
        body: JSON.stringify({ dir }),
      });
      updateUI(data.state);
    } catch (e) {
      console.error('Failed to move:', e);
    } finally {
      isAnimating = false;
    }
  }
  function onKeyDown(e) {
    const key = e.key;
    if (key === 'ArrowUp' || key === 'ArrowDown' || key === 'ArrowLeft' || key === 'ArrowRight') {
      e.preventDefault();
      const dir = key.replace('Arrow', '').toLowerCase(); // up/down/left/right
      doMove(dir);
    }
  }
  // Event bindings
  document.addEventListener('keydown', onKeyDown);
  newGameBtn.addEventListener('click', initGame);
  tryAgainBtn.addEventListener('click', initGame);
  // Start: load existing state (or create one server-side if none exists)
  buildGrid(size);
  refreshState();
})();