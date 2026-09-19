/* Front-end logic for the Strands puzzle.
   Handles fetching puzzles, rendering draggable strands, assembling merges,
   submitting for verification, and updating UI based on server feedback. */
(function () {
  const bagEl = document.getElementById("bag");
  const assembleEl = document.getElementById("assemble");
  const feedbackEl = document.getElementById("feedback");
  const themeEl = document.getElementById("theme");
  const foundListEl = document.getElementById("found-list");
  const completeEl = document.getElementById("complete");
  const foundCountEl = document.getElementById("found-count");
  const totalCountEl = document.getElementById("total-count");
  const btnSubmit = document.getElementById("btn-submit");
  const btnUndo = document.getElementById("btn-undo");
  const btnClear = document.getElementById("btn-clear");
  const btnShuffle = document.getElementById("btn-shuffle");
  const btnReset = document.getElementById("btn-reset");
  const btnNew = document.getElementById("btn-new");
  const btnLoad = document.getElementById("btn-load");
  const selectPuzzle = document.getElementById("puzzle-select");
  let currentPuzzle = null;
  let selectedIds = [];
  function htmlToElement(html) {
    const template = document.createElement("template");
    template.innerHTML = html.trim();
    return template.content.firstChild;
  }
  function clearChildren(el) {
    while (el.firstChild) el.removeChild(el.firstChild);
  }
  function showFeedback(text, type = "info") {
    feedbackEl.textContent = text;
    feedbackEl.className = "feedback " + type;
  }
  function renderSegments(segments) {
    clearChildren(bagEl);
    segments.forEach((seg) => {
      const el = htmlToElement(
        `<div class="chip" draggable="true" data-id="${seg.id}">
          ${seg.text}
        </div>`
      );
      // Drag events
      el.addEventListener("dragstart", (e) => {
        e.dataTransfer.setData("text/plain", seg.id);
        e.dataTransfer.effectAllowed = "move";
      });
      // Click to add
      el.addEventListener("click", () => {
        addToAssembly(seg.id);
      });
      bagEl.appendChild(el);
    });
  }
  function renderAssembly() {
    clearChildren(assembleEl);
    selectedIds.forEach((id) => {
      const seg = currentPuzzle.segments.find((s) => s.id === id);
      if (!seg) return;
      const el = htmlToElement(
        `<div class="chip active" data-id="${seg.id}" title="Click to remove">${seg.text}</div>`
      );
      el.addEventListener("click", () => removeFromAssembly(seg.id));
      assembleEl.appendChild(el);
    });
  }
  function addToAssembly(id) {
    if (!currentPuzzle) return;
    if (selectedIds.includes(id)) {
      showFeedback("Already selected that strand.", "warn");
      return;
    }
    // Ensure the strand is still available in the bag
    const available = currentPuzzle.segments.some((s) => s.id === id);
    if (!available) {
      showFeedback("That strand has already been used.", "warn");
      return;
    }
    selectedIds.push(id);
    renderAssembly();
  }
  function removeFromAssembly(id) {
    selectedIds = selectedIds.filter((x) => x !== id);
    renderAssembly();
  }
  function undo() {
    selectedIds.pop();
    renderAssembly();
  }
  function clearAssembly() {
    selectedIds = [];
    renderAssembly();
  }
  function shuffleBag() {
    if (!currentPuzzle) return;
    // Fisher-Yates
    for (let i = currentPuzzle.segments.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [currentPuzzle.segments[i], currentPuzzle.segments[j]] = [
        currentPuzzle.segments[j],
        currentPuzzle.segments[i],
      ];
    }
    renderSegments(currentPuzzle.segments);
  }
  function updateProgress(solved, total, complete) {
    foundCountEl.textContent = solved.length;
    totalCountEl.textContent = total;
    clearChildren(foundListEl);
    solved.forEach((phrase) => {
      const li = document.createElement("li");
      li.textContent = phrase;
      foundListEl.appendChild(li);
    });
    completeEl.classList.toggle("hidden", !complete);
  }
  function fetchPuzzle(id = "") {
    const url = id ? `/api/puzzle?id=${encodeURIComponent(id)}` : "/api/puzzle";
    return fetch(url)
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          showFeedback(data.error, "error");
          return;
        }
        currentPuzzle = {
          id: data.id,
          theme: data.theme,
          segments: data.segments,
          phrases_total: data.phrases_total,
        };
        themeEl.textContent = data.theme;
        renderSegments(data.segments);
        updateProgress(data.solved || [], data.phrases_total || data.phrase_count || 0, data.complete || false);
        clearAssembly();
        showFeedback("Drag strands to assemble a word/phrase and submit.", "info");
      })
      .catch((e) => {
        console.error(e);
        showFeedback("Failed to load puzzle.", "error");
      });
  }
  function submitMerge() {
    if (!currentPuzzle) return;
    if (selectedIds.length === 0) {
      showFeedback("Select strands to submit a merge.", "warn");
      return;
    }
    fetch("/api/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        puzzle_id: currentPuzzle.id,
        segment_ids: selectedIds,
      }),
    })
      .then((r) => r.json())
      .then((res) => {
        if (res.status === "ok") {
          showFeedback(res.message, "success");
          // Update bag: replace with remaining segments
          if (Array.isArray(res.remaining_segments)) {
            currentPuzzle.segments = res.remaining_segments;
            renderSegments(currentPuzzle.segments);
          }
          // Update progress
          updateProgress(res.solved || [], currentPuzzle.phrases_total, res.complete || false);
          // Clear assembly on success
          clearAssembly();
        } else if (res.status === "partial") {
          showFeedback(res.message, "info");
        } else {
          showFeedback(res.message || "Invalid merge.", "warn");
        }
      })
      .catch((e) => {
        console.error(e);
        showFeedback("Submission failed.", "error");
      });
  }
  function resetPuzzle() {
    if (!currentPuzzle) return;
    fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ puzzle_id: currentPuzzle.id }),
    })
      .then((r) => r.json())
      .then((res) => {
        if (res.status === "ok") {
          fetchPuzzle(currentPuzzle.id);
        } else {
          showFeedback(res.error || "Failed to reset.", "error");
        }
      })
      .catch((e) => {
        console.error(e);
        showFeedback("Failed to reset.", "error");
      });
  }
  function newPuzzle() {
    fetch("/api/new")
      .then((r) => r.json())
      .then((res) => {
        if (res.status === "ok" && res.id) {
          fetchPuzzle(res.id);
          selectPuzzle.value = "";
        } else {
          showFeedback("Failed to start a new puzzle.", "error");
        }
      })
      .catch((e) => {
        console.error(e);
        showFeedback("Failed to start a new puzzle.", "error");
      });
  }
  // Drag-and-drop onto assembly
  assembleEl.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    assembleEl.classList.add("dropping");
  });
  assembleEl.addEventListener("dragleave", () => {
    assembleEl.classList.remove("dropping");
  });
  assembleEl.addEventListener("drop", (e) => {
    e.preventDefault();
    const id = e.dataTransfer.getData("text/plain");
    assembleEl.classList.remove("dropping");
    if (id) {
      addToAssembly(id);
    }
  });
  // Buttons
  btnSubmit.addEventListener("click", submitMerge);
  btnUndo.addEventListener("click", undo);
  btnClear.addEventListener("click", clearAssembly);
  btnShuffle.addEventListener("click", shuffleBag);
  btnReset.addEventListener("click", resetPuzzle);
  btnNew.addEventListener("click", newPuzzle);
  btnLoad.addEventListener("click", () => {
    const chosen = selectPuzzle.value;
    fetchPuzzle(chosen || "");
  });
  // Init
  fetchPuzzle();
})();