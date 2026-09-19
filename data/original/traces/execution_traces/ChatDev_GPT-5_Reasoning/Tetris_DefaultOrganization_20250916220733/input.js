'''
"Input handling: binds keyboard events to game actions (move, rotate, drops). Pause/Resume is handled centrally in main.js to keep UI and loop state in sync."
'''
const __DOC__ = `
Input class attaches keydown/keyup handlers:
- ArrowLeft/ArrowRight: move
- ArrowDown: soft drop
- ArrowUp / KeyX: rotate CW
- KeyZ: rotate CCW
- Space: hard drop
(Pause/Resume via 'P' is handled in main.js to keep UI and loop state in sync.)
Lock delay is managed uniformly in Game.update() when the piece is on the ground.
`;
export class Input {
  constructor(game) {
    this.game = game;
    this.held = new Set();
    this.keyDownHandler = this.onKeyDown.bind(this);
    this.keyUpHandler = this.onKeyUp.bind(this);
    document.addEventListener('keydown', this.keyDownHandler);
    document.addEventListener('keyup', this.keyUpHandler);
  }
  detach() {
    document.removeEventListener('keydown', this.keyDownHandler);
    document.removeEventListener('keyup', this.keyUpHandler);
  }
  onKeyDown(e) {
    if (e.repeat && (e.code === 'ArrowLeft' || e.code === 'ArrowRight')) {
      // Allow OS-level repeat for left/right
    }
    if (this.held.has(e.code) && e.code !== 'ArrowDown') {
      return;
    }
    this.held.add(e.code);
    switch (e.code) {
      case 'ArrowLeft':
        e.preventDefault();
        this.game.inputMove(-1);
        break;
      case 'ArrowRight':
        e.preventDefault();
        this.game.inputMove(1);
        break;
      case 'ArrowDown':
        e.preventDefault();
        this.game.inputSoftDrop();
        break;
      case 'ArrowUp':
      case 'KeyX':
        e.preventDefault();
        this.game.inputRotate(1);
        break;
      case 'KeyZ':
        e.preventDefault();
        this.game.inputRotate(-1);
        break;
      case 'Space':
        e.preventDefault();
        this.game.inputHardDrop();
        break;
      default:
        break;
    }
  }
  onKeyUp(e) {
    this.held.delete(e.code);
  }
}