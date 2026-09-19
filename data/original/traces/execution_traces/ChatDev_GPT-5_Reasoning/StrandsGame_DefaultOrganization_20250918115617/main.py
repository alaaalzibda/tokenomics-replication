'''
Flask web app entry point for the "Strands" word-segmentation puzzle.
Serves the website UI and provides REST API endpoints for fetching puzzles,
submitting merges, resetting, and tracking progress.
'''
from flask import Flask, render_template, jsonify, request, session
from werkzeug.middleware.proxy_fix import ProxyFix
from puzzle import PuzzleBank, verify_merge
app = Flask(__name__, static_folder="static", template_folder="templates")
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = "change-this-secret-in-production"
bank = PuzzleBank()
def get_or_init_state():
    """
    Returns the session state dict, initializing if absent.
    The state structure is:
    {
        puzzle_id: {
            "solved_phrases": [indices],
            "used_segments": [segment_ids],
            "complete": bool
        },
        ...
    }
    """
    if "state" not in session:
        session["state"] = {}
    return session["state"]
@app.route("/")
def index():
    """
    Renders the main game page.
    """
    return render_template("index.html")
@app.get("/api/puzzle")
def api_puzzle():
    """
    Returns the puzzle data (segments, theme, target count). If an id is
    provided via query parameter, that puzzle is loaded, otherwise a random
    one is selected. Initializes session state for the puzzle if needed.
    """
    puzzle_id = request.args.get("id")
    if puzzle_id:
        puzzle = bank.get_by_id(puzzle_id)
        if not puzzle:
            return jsonify({"error": "Puzzle not found"}), 404
    else:
        puzzle = bank.random_puzzle()
    # Initialize state for this puzzle if missing
    state = get_or_init_state()
    pid = puzzle.id
    if pid not in state:
        state[pid] = {
            "solved_phrases": [],
            "used_segments": [],
            "complete": False,
        }
        session.modified = True
    # Filter out segments already used (after solving a phrase)
    used = set(state[pid]["used_segments"])
    segments = [seg.to_dict() for seg in puzzle.segments if seg.id not in used]
    response = {
        "id": puzzle.id,
        "theme": puzzle.theme,
        "phrase_count": len(puzzle.phrases),
        "segments": segments,
        "solved": [puzzle.phrases[i] for i in state[pid]["solved_phrases"]],
        "complete": state[pid]["complete"],
        "phrases_total": len(puzzle.phrases),
    }
    return jsonify(response)
@app.get("/api/state")
def api_state():
    """
    Returns the current session state for a given puzzle id.
    """
    puzzle_id = request.args.get("id")
    if not puzzle_id:
        return jsonify({"error": "Missing id"}), 400
    puzzle = bank.get_by_id(puzzle_id)
    if not puzzle:
        return jsonify({"error": "Puzzle not found"}), 404
    state = get_or_init_state().get(puzzle_id, None)
    if state is None:
        return jsonify({"error": "No state for puzzle"}), 404
    # Provide human-readable solved phrases
    solved_phrases = [puzzle.phrases[i] for i in state["solved_phrases"]]
    return jsonify(
        {
            "id": puzzle_id,
            "solved": solved_phrases,
            "complete": state["complete"],
            "used_segments": state["used_segments"],
        }
    )
@app.post("/api/submit")
def api_submit():
    """
    Validates a proposed merge (list of selected segment IDs in order).
    On full match, marks the phrase as solved and removes all of its segments.
    Returns feedback similar to NYT Strands:
    - "ok" for a valid full merge,
    - "partial" for a valid partial path,
    - "invalid" otherwise, with hints.
    """
    data = request.get_json(force=True, silent=True) or {}
    puzzle_id = data.get("puzzle_id")
    selected_ids = data.get("segment_ids", [])
    if not puzzle_id or not isinstance(selected_ids, list) or not selected_ids:
        return jsonify({"error": "Invalid payload"}), 400
    puzzle = bank.get_by_id(puzzle_id)
    if not puzzle:
        return jsonify({"error": "Puzzle not found"}), 404
    # Load session state
    all_state = get_or_init_state()
    if puzzle_id not in all_state:
        all_state[puzzle_id] = {"solved_phrases": [], "used_segments": [], "complete": False}
    state = all_state[puzzle_id]
    used = set(state["used_segments"])
    # Reject if any selected id is already used
    for sid in selected_ids:
        if sid in used:
            return jsonify(
                {
                    "status": "invalid",
                    "message": "One or more selected strands have already been used in a solved phrase.",
                }
            ), 200
    result = verify_merge(puzzle, selected_ids)
    if result["status"] == "ok":
        # Mark phrase solved
        phrase_index = result["phrase_index"]
        if phrase_index not in state["solved_phrases"]:
            state["solved_phrases"].append(phrase_index)
            # Mark all segments of this phrase as used (not just the ones submitted)
            to_use = [seg.id for seg in puzzle.segments if seg.phrase_index == phrase_index]
            state["used_segments"].extend(to_use)
            # Check completion
            state["complete"] = len(state["solved_phrases"]) == len(puzzle.phrases)
            session.modified = True
        # Return updated segments (remaining)
        remaining_segments = [
            seg.to_dict() for seg in puzzle.segments if seg.id not in set(state["used_segments"])
        ]
        return jsonify(
            {
                "status": "ok",
                "message": result["message"],
                "solved_phrase": result["solved_phrase"],
                "remaining_segments": remaining_segments,
                "solved": [puzzle.phrases[i] for i in state["solved_phrases"]],
                "complete": state["complete"],
            }
        )
    # For partial or invalid, just return the feedback
    return jsonify(result)
@app.post("/api/reset")
def api_reset():
    """
    Resets the session state for a given puzzle id, effectively starting it over.
    """
    data = request.get_json(force=True, silent=True) or {}
    puzzle_id = data.get("puzzle_id")
    if not puzzle_id:
        return jsonify({"error": "Missing puzzle_id"}), 400
    puzzle = bank.get_by_id(puzzle_id)
    if not puzzle:
        return jsonify({"error": "Puzzle not found"}), 404
    state = get_or_init_state()
    state[puzzle_id] = {"solved_phrases": [], "used_segments": [], "complete": False}
    session.modified = True
    return jsonify({"status": "ok", "message": "Puzzle reset."})
@app.get("/api/new")
def api_new():
    """
    Picks a new random puzzle and initializes its state.
    """
    puzzle = bank.random_puzzle()
    state = get_or_init_state()
    pid = puzzle.id
    state[pid] = {"solved_phrases": [], "used_segments": [], "complete": False}
    session.modified = True
    return jsonify({"status": "ok", "id": pid})
if __name__ == "__main__":
    # Development server
    # Visit http://127.0.0.1:5000 in your browser
    app.run(debug=True)