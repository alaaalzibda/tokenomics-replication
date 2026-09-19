'''
Flask web app entry point for the NYT Strands-like puzzle (website modality).
Serves a browser-based UI that communicates with the backend game logic via JSON endpoints.
Routes:
- GET /         -> Render the main game page.
- GET /state    -> Return the current game state for this session.
- POST /select  -> Attempt to commit a dragged letter selection as a word.
- POST /hint    -> Reveal a themed word or spangram by consuming a hint.
- POST /reset   -> Reset the game state for this session.
- GET /remaining-> Return the list of remaining words not yet found.
Game state is kept server-side in memory per session id (signed cookie).
'''
from flask import Flask, render_template, jsonify, request, session
from uuid import uuid4
# Support running whether the core modules are in a 'strands' package folder
# or placed at the project root alongside this file.
try:
    from strands.puzzle import default_puzzle
    from strands.game import GameState
except ModuleNotFoundError:
    from puzzle import default_puzzle  # type: ignore
    from game import GameState  # type: ignore
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "dev-secret-change-me"
# Single shared puzzle instance (read-only)
PUZZLE = default_puzzle()
# In-memory game state storage keyed by session id
_SESSIONS = {}
def _ensure_session():
    if "sid" not in session:
        session["sid"] = str(uuid4())
    sid = session["sid"]
    if sid not in _SESSIONS:
        _SESSIONS[sid] = {"game": GameState(PUZZLE)}
    return sid
def _serialize_state(game: "GameState"):
    claimed_list = []
    for (r, c), meta in game.claimed.items():
        claimed_list.append(
            {"r": r, "c": c, "type": meta["type"], "word": meta["word"]}
        )
    state = {
        "rows": game.puzzle.rows,
        "cols": game.puzzle.cols,
        "grid": game.puzzle.grid,
        "theme": game.puzzle.theme,
        "spangram": game.puzzle.spangram,
        "foundWords": sorted(list(game.found_words)),
        "hints": game.hints,
        "nonThemeCount": len(game.non_theme_words),
        "claimed": claimed_list,
        "totalTheme": len(game.puzzle.theme_words),
        "completed": game.is_completed(),
    }
    return state
@app.get("/")
def index():
    _ensure_session()
    return render_template("index.html")
@app.get("/state")
def state():
    sid = _ensure_session()
    game = _SESSIONS[sid]["game"]
    return jsonify(_serialize_state(game))
@app.post("/select")
def select():
    sid = _ensure_session()
    game = _SESSIONS[sid]["game"]
    payload = request.get_json(silent=True) or {}
    coords = payload.get("coords", [])
    # Ensure coords are tuples of ints
    norm_coords = []
    for pair in coords:
        try:
            r, c = int(pair[0]), int(pair[1])
            norm_coords.append((r, c))
        except Exception:
            pass
    result = game.try_commit_selection(norm_coords)
    return jsonify({"result": result, "state": _serialize_state(game)})
@app.post("/hint")
def hint():
    sid = _ensure_session()
    game = _SESSIONS[sid]["game"]
    revealed = game.reveal_hint()
    if revealed:
        word, coords, kind = revealed
        result = {"type": kind, "word": word, "coords": coords}
    else:
        result = {"type": "none", "word": None, "coords": []}
    return jsonify({"result": result, "state": _serialize_state(game)})
@app.post("/reset")
def reset():
    sid = _ensure_session()
    _SESSIONS[sid]["game"] = GameState(PUZZLE)
    return jsonify({"state": _serialize_state(_SESSIONS[sid]["game"])})
@app.get("/remaining")
def remaining():
    sid = _ensure_session()
    game = _SESSIONS[sid]["game"]
    remaining_words = [w for w in game.puzzle.theme_words if w not in game.found_words]
    if game.puzzle.spangram not in game.found_words:
        remaining_words = [f"(spangram) {game.puzzle.spangram}"] + remaining_words
    return jsonify({"remaining": remaining_words})
if __name__ == "__main__":
    app.run(debug=True)