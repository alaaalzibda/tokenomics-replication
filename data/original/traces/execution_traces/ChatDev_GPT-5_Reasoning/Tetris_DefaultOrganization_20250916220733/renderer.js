'''
"Renderer handles drawing the board, active piece, ghost piece, and next preview to canvases."
'''
const __DOC__ = `
Renderer draws:
- Board cells
- Ghost piece (translucent)
- Active piece
- Grid lines (subtle) and border effects
- Next piece preview
`;
import { COLORS, SHAPES } from './shapes.js';
export class Renderer {
  constructor(boardCtx, nextCtx, options) {
    this.boardCtx = boardCtx;
    this.nextCtx = nextCtx;
    this.cols = options.cols;
    this.rows = options.rows;
    this.cellSize = options.cellSize;
  }
  clearBoard() {
    const ctx = this.boardCtx;
    const w = this.cols * this.cellSize;
    const h = this.rows * this.cellSize;
    ctx.clearRect(0, 0, w, h);
    // background
    ctx.fillStyle = '#10131b';
    ctx.fillRect(0, 0, w, h);
  }
  drawGrid() {
    const ctx = this.boardCtx;
    const cs = this.cellSize;
    const w = this.cols * cs;
    const h = this.rows * cs;
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x <= w; x += cs) {
      ctx.moveTo(x + 0.5, 0);
      ctx.lineTo(x + 0.5, h);
    }
    for (let y = 0; y <= h; y += cs) {
      ctx.moveTo(0, y + 0.5);
      ctx.lineTo(w, y + 0.5);
    }
    ctx.stroke();
  }
  drawCell(ctx, x, y, color, alpha = 1) {
    const cs = this.cellSize;
    const px = x * cs;
    const py = y * cs;
    ctx.globalAlpha = alpha;
    // main cell
    ctx.fillStyle = color;
    ctx.fillRect(px + 1, py + 1, cs - 2, cs - 2);
    // highlight and shade for some depth
    const lighter = shadeColor(color, 0.25);
    const darker = shadeColor(color, -0.25);
    ctx.fillStyle = lighter;
    ctx.fillRect(px + 2, py + 2, cs - 4, (cs - 4) * 0.25);
    ctx.fillStyle = darker;
    ctx.fillRect(px + 2, py + cs - 4 - (cs - 4) * 0.25, cs - 4, (cs - 4) * 0.25);
    ctx.globalAlpha = 1;
  }
  drawBoardGrid(boardGrid) {
    const ctx = this.boardCtx;
    for (let r = 0; r < boardGrid.length; r++) {
      for (let c = 0; c < boardGrid[r].length; c++) {
        const cell = boardGrid[r][c];
        if (cell) {
          const color = COLORS[cell] || '#888';
          this.drawCell(ctx, c, r, color, 1);
        }
      }
    }
  }
  drawPiece(piece) {
    const ctx = this.boardCtx;
    const m = piece.matrix;
    const color = COLORS[piece.type] || '#aaa';
    for (let r = 0; r < m.length; r++) {
      for (let c = 0; c < m[r].length; c++) {
        if (!m[r][c]) continue;
        const x = piece.x + c;
        const y = piece.y + r;
        if (y >= 0) {
          this.drawCell(ctx, x, y, color, 1);
        }
      }
    }
  }
  drawGhost(piece, ghostY) {
    const ctx = this.boardCtx;
    const m = piece.matrix;
    const color = COLORS[piece.type] || '#aaa';
    for (let r = 0; r < m.length; r++) {
      for (let c = 0; c < m[r].length; c++) {
        if (!m[r][c]) continue;
        const x = piece.x + c;
        const y = ghostY + r;
        if (y >= 0) {
          this.drawCell(ctx, x, y, color, 0.18);
        }
      }
    }
  }
  drawNext(nextType) {
    const ctx = this.nextCtx;
    const size = this.nextCtx.canvas.width / (window.devicePixelRatio || 1);
    ctx.clearRect(0, 0, size, size);
    ctx.fillStyle = '#10131b';
    ctx.fillRect(0, 0, size, size);
    if (!nextType) return;
    const matrix = SHAPES[nextType][0];
    const color = COLORS[nextType] || '#aaa';
    // compute bounds of occupied cells to center
    let minX = 99, minY = 99, maxX = -1, maxY = -1;
    for (let r = 0; r < matrix.length; r++) {
      for (let c = 0; c < matrix[r].length; c++) {
        if (matrix[r][c]) {
          minX = Math.min(minX, c);
          maxX = Math.max(maxX, c);
          minY = Math.min(minY, r);
          maxY = Math.max(maxY, r);
        }
      }
    }
    const wCells = maxX - minX + 1;
    const hCells = maxY - minY + 1;
    const cellSize = Math.floor(Math.min((size - 16) / wCells, (size - 16) / hCells));
    const offsetX = Math.floor((size - wCells * cellSize) / 2);
    const offsetY = Math.floor((size - hCells * cellSize) / 2);
    // draw cells
    for (let r = 0; r < matrix.length; r++) {
      for (let c = 0; c < matrix[r].length; c++) {
        if (!matrix[r][c]) continue;
        const px = offsetX + (c - minX) * cellSize;
        const py = offsetY + (r - minY) * cellSize;
        // draw similar style to board cells
        ctx.fillStyle = color;
        ctx.globalAlpha = 1;
        ctx.fillRect(px + 1, py + 1, cellSize - 2, cellSize - 2);
        const lighter = shadeColor(color, 0.25);
        const darker = shadeColor(color, -0.25);
        ctx.fillStyle = lighter;
        ctx.fillRect(px + 2, py + 2, cellSize - 4, (cellSize - 4) * 0.25);
        ctx.fillStyle = darker;
        ctx.fillRect(px + 2, py + cellSize - 4 - (cellSize - 4) * 0.25, cellSize - 4, (cellSize - 4) * 0.25);
      }
    }
  }
  render(board, activePiece, ghostY, nextType) {
    this.clearBoard();
    this.drawGrid();
    this.drawBoardGrid(board.grid);
    if (activePiece) {
      if (ghostY !== null && ghostY !== undefined) {
        this.drawGhost(activePiece, ghostY);
      }
      this.drawPiece(activePiece);
    }
    this.drawNext(nextType);
  }
}
function shadeColor(hex, percent) {
  // hex to RGB
  const c = hex.replace('#', '');
  const num = parseInt(c, 16);
  const r = (num >> 16) & 255;
  const g = (num >> 8) & 255;
  const b = num & 255;
  const t = percent >= 0 ? 255 : 0;
  const p = Math.abs(percent);
  const R = Math.round((t - r) * p) + r;
  const G = Math.round((t - g) * p) + g;
  const B = Math.round((t - b) * p) + b;
  return '#' + ((1 << 24) + (R << 16) + (G << 8) + B).toString(16).slice(1);
}