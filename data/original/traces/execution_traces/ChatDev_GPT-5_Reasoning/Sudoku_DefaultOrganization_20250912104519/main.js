'''
Frontend logic for rendering the Sudoku grid, handling user input, performing
client-side rule checks, and interacting with the backend verification APIs.
'''
/*
'''
Frontend logic for rendering the Sudoku grid, handling user input, performing
client-side rule checks, and interacting with the backend verification APIs.
'''
*/
(function () {
  const boardContainer = document.getElementById("board-container");
  const btnNew = document.getElementById("btn-new");
  const btnCheck = document.getElementById("btn-check");
  const btnValidate = document.getElementById("btn-validate");
  const messageEl = document.getElementById("message");
  let puzzle = window.SUDOKU_PUZZLE || createEmptyBoard();
  let givens = window.SUDOKU_GIVENS || createEmptyBoard();
  let inputs = []; // 2D array of input elements
  function createEmptyBoard() {
    const g = [];
    for (let r = 0; r < 9; r++) {
      const row = [];
      for (let c = 0; c < 9; c++) row.push(0);
      g.push(row);
    }
    return g;
  }
  function clearMessage() {
    messageEl.textContent = "";
    messageEl.className = "message";
  }
  function showMessage(text, type = "info") {
    messageEl.textContent = text;
    messageEl.className = "message " + type;
  }
  function buildBoard() {
    boardContainer.innerHTML = "";
    inputs = [];
    const table = document.createElement("table");
    table.className = "sudoku";
    for (let r = 0; r < 9; r++) {
      const tr = document.createElement("tr");
      const rowInputs = [];
      for (let c = 0; c < 9; c++) {
        const td = document.createElement("td");
        td.className = getCellClass(r, c);
        const input = document.createElement("input");
        input.type = "text";
        input.inputMode = "numeric";
        input.maxLength = 1;
        input.dataset.row = String(r);
        input.dataset.col = String(c);
        const val = puzzle[r][c];
        if (val !== 0) {
          input.value = String(val);
        } else {
          input.value = "";
        }
        if (givens[r][c] === 1) {
          input.disabled = true;
          input.classList.add("given");
        }
        input.addEventListener("input", onCellInput);
        input.addEventListener("keydown", onCellKeyDown);
        td.appendChild(input);
        tr.appendChild(td);
        rowInputs.push(input);
      }
      table.appendChild(tr);
      inputs.push(rowInputs);
    }
    boardContainer.appendChild(table);
    runRuleCheck();
  }
  function getCellClass(r, c) {
    const classes = [];
    if (r % 3 === 0) classes.push("thick-top");
    if (c % 3 === 0) classes.push("thick-left");
    if (r === 8) classes.push("thick-bottom");
    if (c === 8) classes.push("thick-right");
    return classes.join(" ");
  }
  function onCellInput(e) {
    const input = e.target;
    const v = input.value.replace(/[^\d]/g, "");
    if (v.length === 0) {
      input.value = "";
    } else {
      const d = v[v.length - 1];
      if (d === "0") {
        input.value = "";
      } else {
        input.value = d;
      }
    }
    // Remove incorrect/conflict styling on edit
    input.classList.remove("incorrect");
    runRuleCheck();
    clearMessage();
  }
  function onCellKeyDown(e) {
    const input = e.target;
    const r = parseInt(input.dataset.row, 10);
    const c = parseInt(input.dataset.col, 10);
    // Arrow keys navigation
    const moveFocus = (nr, nc) => {
      if (nr < 0 || nr > 8 || nc < 0 || nc > 8) return;
      inputs[nr][nc].focus();
      inputs[nr][nc].select();
    };
    switch (e.key) {
      case "ArrowUp":
        e.preventDefault();
        moveFocus(r - 1, c);
        break;
      case "ArrowDown":
        e.preventDefault();
        moveFocus(r + 1, c);
        break;
      case "ArrowLeft":
        e.preventDefault();
        moveFocus(r, c - 1);
        break;
      case "ArrowRight":
        e.preventDefault();
        moveFocus(r, c + 1);
        break;
      case "Backspace":
        if (!input.disabled && input.value === "") {
          // Move left if empty
          moveFocus(r, c - 1);
        }
        break;
      default:
        break;
    }
  }
  function getBoardFromInputs() {
    const board = createEmptyBoard();
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const val = inputs[r][c].value.trim();
        board[r][c] = val ? parseInt(val, 10) : 0;
      }
    }
    return board;
  }
  function runRuleCheck() {
    // Clear previous conflict classes
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        inputs[r][c].classList.remove("conflict");
      }
    }
    const board = getBoardFromInputs();
    // Check rows
    for (let r = 0; r < 9; r++) {
      const seen = {};
      for (let c = 0; c < 9; c++) {
        const v = board[r][c];
        if (v === 0) continue;
        if (!seen[v]) seen[v] = [];
        seen[v].push(c);
      }
      for (const cols of Object.values(seen)) {
        if (cols.length > 1) {
          cols.forEach((col) => inputs[r][col].classList.add("conflict"));
        }
      }
    }
    // Check columns
    for (let c = 0; c < 9; c++) {
      const seen = {};
      for (let r = 0; r < 9; r++) {
        const v = board[r][c];
        if (v === 0) continue;
        if (!seen[v]) seen[v] = [];
        seen[v].push(r);
      }
      for (const rows of Object.values(seen)) {
        if (rows.length > 1) {
          rows.forEach((row) => inputs[row][c].classList.add("conflict"));
        }
      }
    }
    // Check 3x3 boxes
    for (let br = 0; br < 9; br += 3) {
      for (let bc = 0; bc < 9; bc += 3) {
        const seen = {};
        for (let r = br; r < br + 3; r++) {
          for (let c = bc; c < bc + 3; c++) {
            const v = board[r][c];
            if (v === 0) continue;
            if (!seen[v]) seen[v] = [];
            seen[v].push([r, c]);
          }
        }
        for (const coords of Object.values(seen)) {
          if (coords.length > 1) {
            coords.forEach(([r, c]) => inputs[r][c].classList.add("conflict"));
          }
        }
      }
    }
  }
  async function postJSON(url, payload) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data && data.error ? data.error : "Request failed");
    }
    return data;
  }
  async function handleCheckMistakes() {
    clearMessage();
    // Remove old incorrect highlights
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        inputs[r][c].classList.remove("incorrect");
      }
    }
    const board = getBoardFromInputs();
    try {
      const result = await postJSON("/api/verify", { board });
      if (result.incorrect_cells && result.incorrect_cells.length > 0) {
        result.incorrect_cells.forEach(({ row, col }) => {
          inputs[row][col].classList.add("incorrect");
        });
        showMessage("Mistakes highlighted in red.", "warning");
      } else {
        showMessage("No mistakes detected so far.", "success");
      }
    } catch (err) {
      showMessage(err.message || "Error checking mistakes.", "error");
    }
  }
  async function handleValidateCompleted() {
    clearMessage();
    const board = getBoardFromInputs();
    try {
      const result = await postJSON("/api/verify", { board });
      if (result.solved) {
        showMessage(result.message, "success");
      } else if (result.complete) {
        showMessage(result.message, "warning");
      } else {
        showMessage(result.message, "info");
      }
      // Highlight incorrect if any
      if (result.incorrect_cells && result.incorrect_cells.length > 0) {
        result.incorrect_cells.forEach(({ row, col }) => {
          inputs[row][col].classList.add("incorrect");
        });
      }
    } catch (err) {
      showMessage(err.message || "Error validating board.", "error");
    }
  }
  async function handleNewGame() {
    clearMessage();
    try {
      const result = await postJSON("/api/new", {});
      puzzle = result.puzzle;
      givens = result.givens;
      buildBoard();
      showMessage("New puzzle loaded!", "info");
    } catch (err) {
      showMessage(err.message || "Error loading new puzzle.", "error");
    }
  }
  // Hook up event listeners
  btnCheck.addEventListener("click", handleCheckMistakes);
  btnValidate.addEventListener("click", handleValidateCompleted);
  btnNew.addEventListener("click", handleNewGame);
  // Initialize
  buildBoard();
})();