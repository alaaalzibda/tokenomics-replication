'''
Client-side interactivity for the Strands puzzle.
Implements drag selection across adjacent cells, communicates with the Flask backend,
and applies the correct coloring for themed words and the spangram. Also handles hints,
reset, and “remaining words” interactions.
'''
(() => {
  const boardEl = document.getElementById("board");
  const themeEl = document.getElementById("theme");
  const foundEl = document.getElementById("found");
  const hintsEl = document.getElementById("hints");
  const hintBtn = document.getElementById("hintBtn");
  const resetBtn = document.getElementById("resetBtn");
  const remainingBtn = document.getElementById("remainingBtn");
  let state = null;
  let dragging = false;
  let selection = [];
  let selectionSet = new Set();
  let cells = []; // 2D array of cell elements [r][c]
  function idOf(rc) {
    return `${rc.r}-${rc.c}`;
  }
  function isAdjacent(a, b) {
    const dr = Math.abs(a.r - b.r);
    const dc = Math.abs(a.c - b.c);
    return Math.max(dr, dc) === 1 && (dr !== 0 || dc !== 0);
  }
  function buildGrid() {
    cells = [];
    boardEl.innerHTML = "";
    for (let r = 0; r < state.rows; r++) {
      const row = [];
      for (let c = 0; c < state.cols; c++) {
        const ch = state.grid[r][c];
        const div = document.createElement("div");
        div.className = "cell";
        div.textContent = ch;
        div.dataset.r = String(r);
        div.dataset.c = String(c);
        div.setAttribute("role", "gridcell");
        // Mouse events
        div.addEventListener("mousedown", onMouseDownCell);
        div.addEventListener("mouseenter", onMouseEnterCell);
        row.push(div);
        boardEl.appendChild(div);
      }
      cells.push(row);
    }
    document.addEventListener("mouseup", onGlobalMouseUp);
    // Touch support (basic): treat touchstart as mousedown, touchmove enters target, touchend as mouseup
    boardEl.addEventListener("touchstart", onTouchStart, { passive: false });
    boardEl.addEventListener("touchmove", onTouchMove, { passive: false });
    document.addEventListener("touchend", onTouchEnd, { passive: false });
  }
  function clearTempSelection() {
    for (const rc of selection) {
      const el = cellAt(rc.r, rc.c);
      if (el && !el.classList.contains("claimed-theme") && !el.classList.contains("claimed-spangram")) {
        el.classList.remove("temp");
      }
    }
    selection = [];
    selectionSet.clear();
  }
  function cellAt(r, c) {
    if (r < 0 || c < 0 || r >= state.rows || c >= state.cols) return null;
    return cells[r][c];
  }
  function coordFromEl(el) {
    return { r: parseInt(el.dataset.r, 10), c: parseInt(el.dataset.c, 10) };
  }
  function isClaimed(rc) {
    // Build a set of claimed coords for quick lookup
    if (!state._claimedSet) {
      state._claimedSet = new Set(state.claimed.map(({ r, c }) => `${r},${c}`));
    }
    return state._claimedSet.has(`${rc.r},${rc.c}`);
  }
  function onMouseDownCell(e) {
    e.preventDefault();
    const rc = coordFromEl(e.currentTarget);
    if (isClaimed(rc)) return;
    dragging = true;
    selection = [rc];
    selectionSet = new Set([`${rc.r},${rc.c}`]);
    const el = cellAt(rc.r, rc.c);
    el.classList.add("temp");
  }
  function onMouseEnterCell(e) {
    if (!dragging) return;
    const rc = coordFromEl(e.currentTarget);
    if (isClaimed(rc)) return;
    const key = `${rc.r},${rc.c}`;
    if (selectionSet.has(key)) return;
    if (selection.length === 0) return;
    const last = selection[selection.length - 1];
    if (!isAdjacent(last, rc)) return;
    selection.push(rc);
    selectionSet.add(key);
    const el = cellAt(rc.r, rc.c);
    el.classList.add("temp");
  }
  function onGlobalMouseUp() {
    if (!dragging) return;
    dragging = false;
    commitSelection();
  }
  function onTouchStart(e) {
    if (e.touches.length > 0) {
      e.preventDefault();
      const t = e.touches[0];
      const el = document.elementFromPoint(t.clientX, t.clientY);
      if (el && el.classList.contains("cell")) {
        const rc = coordFromEl(el);
        if (!isClaimed(rc)) {
          dragging = true;
          selection = [rc];
          selectionSet = new Set([`${rc.r},${rc.c}`]);
          el.classList.add("temp");
        }
      }
    }
  }
  function onTouchMove(e) {
    if (!dragging) return;
    e.preventDefault();
    const t = e.touches[0];
    const el = document.elementFromPoint(t.clientX, t.clientY);
    if (el && el.classList.contains("cell")) {
      const rc = coordFromEl(el);
      if (isClaimed(rc)) return;
      const key = `${rc.r},${rc.c}`;
      if (selectionSet.has(key)) return;
      if (selection.length === 0) return;
      const last = selection[selection.length - 1];
      if (!isAdjacent(last, rc)) return;
      selection.push(rc);
      selectionSet.add(key);
      el.classList.add("temp");
    }
  }
  function onTouchEnd() {
    if (!dragging) return;
    dragging = false;
    commitSelection();
  }
  async function commitSelection() {
    const coords = selection.map((rc) => [rc.r, rc.c]);
    clearTempSelection();
    if (coords.length < 2) return; // ignore single letter
    try {
      const res = await fetch("/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ coords }),
      });
      const data = await res.json();
      applyResultFlash(data.result);
      await updateStateFromData(data.state);
    } catch (err) {
      console.error("Commit failed", err);
    }
  }
  function applyResultFlash(result) {
    if (!result || !result.type) return;
    const coords = result.coords || [];
    if (result.type === "non-theme" || result.type === "invalid") {
      const cls = result.type === "non-theme" ? "flash-non-theme" : "flash-invalid";
      for (const [r, c] of coords) {
        const el = cellAt(r, c);
        if (el && !el.classList.contains("claimed-theme") && !el.classList.contains("claimed-spangram")) {
          el.classList.add(cls);
        }
      }
      setTimeout(() => {
        for (const [r, c] of coords) {
          const el = cellAt(r, c);
          if (el) {
            el.classList.remove("flash-non-theme", "flash-invalid", "temp");
          }
        }
      }, 250);
    }
  }
  async function useHint() {
    try {
      const res = await fetch("/hint", { method: "POST" });
      const data = await res.json();
      applyResultFlash(data.result); // not necessary but keeps behavior uniform
      await updateStateFromData(data.state);
      if (data.result.type === "none") {
        alert("No hints available or all words already found.");
      }
    } catch (err) {
      console.error("Hint failed", err);
    }
  }
  async function resetProgress() {
    if (!confirm("Reset your current progress?")) return;
    try {
      const res = await fetch("/reset", { method: "POST" });
      const data = await res.json();
      await updateStateFromData(data.state, true);
    } catch (err) {
      console.error("Reset failed", err);
    }
  }
  async function showRemaining() {
    try {
      const res = await fetch("/remaining");
      const data = await res.json();
      const remaining = data.remaining || [];
      if (remaining.length === 0) {
        alert("All words found!");
      } else {
        alert("Words remaining:\n" + remaining.join("\n"));
      }
    } catch (err) {
      console.error("Remaining failed", err);
    }
  }
  function applyClaimedColors() {
    // Clear all claimed classes first
    for (let r = 0; r < state.rows; r++) {
      for (let c = 0; c < state.cols; c++) {
        const el = cellAt(r, c);
        el.classList.remove("claimed-theme", "claimed-spangram", "temp", "flash-invalid", "flash-non-theme");
      }
    }
    // Apply claimed
    for (const item of state.claimed) {
      const el = cellAt(item.r, item.c);
      if (!el) continue;
      if (item.type === "theme") el.classList.add("claimed-theme");
      if (item.type === "spangram") el.classList.add("claimed-spangram");
    }
  }
  async function updateState() {
    const res = await fetch("/state");
    const data = await res.json();
    await updateStateFromData(data, true);
  }
  async function updateStateFromData(newState, rebuildIfNeeded = false) {
    state = newState;
    // Clear cached claimed set for lookup
    state._claimedSet = null;
    themeEl.textContent = `Theme: ${state.theme}`;
    const foundThemeCount = state.foundWords.filter((w) => w !== state.spangram).length;
    const spangramDone = state.foundWords.includes(state.spangram);
    foundEl.textContent = `Found: ${foundThemeCount}/${state.totalTheme} themes; Spangram: ${spangramDone ? "Yes" : "No"}`;
    hintsEl.textContent = `Hints: ${state.hints}; Non-theme words: ${state.nonThemeCount}`;
    if (!cells.length || rebuildIfNeeded) {
      buildGrid();
    }
    applyClaimedColors();
    if (state.completed) {
      setTimeout(() => {
        alert("Congratulations! You completed the puzzle and filled the board!");
      }, 10);
    }
  }
  // Wire controls
  hintBtn.addEventListener("click", useHint);
  resetBtn.addEventListener("click", resetProgress);
  remainingBtn.addEventListener("click", showRemaining);
  // Initialize
  updateState();
})();