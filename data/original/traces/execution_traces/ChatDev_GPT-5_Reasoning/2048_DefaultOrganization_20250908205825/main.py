'''
Flask web app for a 2048 game with server-side Python game logic and client-side keyboard controls.
'''
from flask import Flask, render_template, request, session, jsonify
import os
from game import Game2048
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-2048')
def get_game_from_session() -> Game2048:
    """
    Load the current game from the session or create a new one if missing.
    """
    state = session.get('game_state')
    if state:
        try:
            return Game2048.from_state(state)
        except Exception:
            # If session data is corrupted, start a new game
            return new_game()
    else:
        return new_game()
def save_game_to_session(game: Game2048) -> None:
    """
    Persist the game state to the session.
    """
    session['game_state'] = game.to_state()
def new_game() -> Game2048:
    """
    Create and store a fresh game in the session.
    """
    game = Game2048()
    save_game_to_session(game)
    return game
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/init', methods=['POST'])
def init_game():
    game = new_game()
    return jsonify({
        'ok': True,
        'state': {
            'board': game.board,
            'score': game.score,
            'max_tile': game.max_tile,
            'size': game.size,
            'game_over': not game.can_move(),
        }
    })
@app.route('/state', methods=['GET'])
def state():
    game = get_game_from_session()
    return jsonify({
        'ok': True,
        'state': {
            'board': game.board,
            'score': game.score,
            'max_tile': game.max_tile,
            'size': game.size,
            'game_over': not game.can_move(),
        }
    })
@app.route('/move', methods=['POST'])
def move():
    payload = request.get_json(silent=True) or {}
    direction = payload.get('dir')
    if direction not in ('up', 'down', 'left', 'right'):
        return jsonify({'ok': False, 'error': 'Invalid direction'}), 400
    game = get_game_from_session()
    if not game.can_move():
        # Already game over; return current state unchanged.
        save_game_to_session(game)
        return jsonify({
            'ok': True,
            'changed': False,
            'state': {
                'board': game.board,
                'score': game.score,
                'max_tile': game.max_tile,
                'size': game.size,
                'game_over': True,
            }
        })
    changed, gained = game.move(direction)
    if changed:
        game.add_random_tile()
    # Save regardless to persist score and state
    save_game_to_session(game)
    return jsonify({
        'ok': True,
        'changed': changed,
        'gained': gained,
        'state': {
            'board': game.board,
            'score': game.score,
            'max_tile': game.max_tile,
            'size': game.size,
            'game_over': not game.can_move(),
        }
    })
if __name__ == '__main__':
    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)