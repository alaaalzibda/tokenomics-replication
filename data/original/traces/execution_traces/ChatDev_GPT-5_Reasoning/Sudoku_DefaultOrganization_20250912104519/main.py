'''
Flask application entry point for the Sudoku web app. Serves the web interface,
manages puzzle state in session, and provides API endpoints to verify solutions
and generate new puzzles.
'''
from flask import Flask, render_template, request, jsonify, session
from sudoku import generate_puzzle
import os
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)
# For demo purposes; in production use a secure random secret key via env var.
app.secret_key = os.environ.get("SUDOKU_SECRET_KEY", "dev-secret-key-change-me")
def _ensure_puzzle_in_session(difficulty="medium"):
    """
    Ensure a puzzle and its solution are present in the session.
    Returns a tuple (puzzle, solution, givens_mask).
    """
    if "puzzle" not in session or "solution" not in session or "givens" not in session:
        puzzle, solution = generate_puzzle(difficulty=difficulty)
        givens = [[1 if puzzle[r][c] != 0 else 0 for c in range(9)] for r in range(9)]
        session["puzzle"] = puzzle
        session["solution"] = solution
        session["givens"] = givens
    return session["puzzle"], session["solution"], session["givens"]
@app.route("/", methods=["GET"])
def index():
    """
    Render the Sudoku game page. If no active puzzle, generate a new one.
    """
    puzzle, solution, givens = _ensure_puzzle_in_session()
    # Do not expose solution to client; only puzzle and givens are rendered.
    return render_template("index.html", puzzle=puzzle, givens=givens)
@app.route("/api/puzzle", methods=["POST"])
def api_puzzle():
    """
    Return the current puzzle and givens from the session in JSON format.
    """
    puzzle, _, givens = _ensure_puzzle_in_session()
    return jsonify({"puzzle": puzzle, "givens": givens})
@app.route("/api/new", methods=["POST"])
def api_new():
    """
    Generate a new puzzle and store it in session. Accepts optional difficulty.
    """
    data = request.get_json(silent=True) or {}
    difficulty = data.get("difficulty", "medium")
    puzzle, solution = generate_puzzle(difficulty=difficulty)
    givens = [[1 if puzzle[r][c] != 0 else 0 for c in range(9)] for r in range(9)]
    session["puzzle"] = puzzle
    session["solution"] = solution
    session["givens"] = givens
    return jsonify({"puzzle": puzzle, "givens": givens, "difficulty": difficulty})
@app.route("/api/verify", methods=["POST"])
def api_verify():
    """
    Verify the current board against the solution.
    Request JSON:
      {
        "board": [[int x9] x9]
      }
    Response JSON:
      {
        "complete": bool,           # True if no zeros on board
        "solved": bool,             # True if board matches solution exactly
        "incorrect_cells": [{"row": r, "col": c}, ...],  # cells that don't match solution
        "message": str
      }
    """
    if "solution" not in session or "givens" not in session:
        return jsonify({"error": "No active puzzle found."}), 400
    data = request.get_json(silent=True) or {}
    board = data.get("board")
    # Validate board shape
    if not isinstance(board, list) or len(board) != 9 or any(
        not isinstance(row, list) or len(row) != 9 for row in board
    ):
        return jsonify({"error": "Invalid board format."}), 400
    # Normalize inputs to integers in 0..9
    try:
        normalized = []
        for r in range(9):
            row = []
            for c in range(9):
                val = board[r][c]
                if val in (None, "", " "):
                    row.append(0)
                else:
                    v = int(val)
                    if v < 0 or v > 9:
                        return jsonify({"error": "Board values must be 0..9."}), 400
                    row.append(v)
            normalized.append(row)
        board = normalized
    except Exception:
        return jsonify({"error": "Board contains non-numeric values."}), 400
    solution = session["solution"]
    givens = session["givens"]
    # Ensure givens aren't changed
    for r in range(9):
        for c in range(9):
            if givens[r][c] == 1 and board[r][c] != solution[r][c]:
                return jsonify({
                    "complete": False,
                    "solved": False,
                    "incorrect_cells": [{"row": r, "col": c}],
                    "message": "You modified a given cell, which is not allowed."
                }), 200
    incorrect = []
    complete = True
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                complete = False
            elif board[r][c] != solution[r][c]:
                incorrect.append({"row": r, "col": c})
    solved = complete and len(incorrect) == 0
    if solved:
        msg = "Congratulations! You solved the puzzle."
    elif complete:
        msg = "Board is complete but has mistakes. Please review highlighted cells."
    else:
        msg = "Progress saved. Keep going!"
    return jsonify({
        "complete": complete,
        "solved": solved,
        "incorrect_cells": incorrect,
        "message": msg
    })
if __name__ == "__main__":
    # Run development server
    app.run(host="0.0.0.0", port=5000, debug=True)