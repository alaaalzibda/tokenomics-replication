'''
Main entry for the Gold Miner web game using PyScript (Python in the browser).
Updates in this fix:
- Headless-safe import guard: avoid importing PyScript/JS modules when not available.
- Only start the game automatically when running under PyScript; otherwise exit gracefully.
- Provide a no-op create_proxy fallback so the module can be imported/executed in non-browser tests.
Why:
The test runner executes main.py in a standard Python environment (no 'js' module),
causing "ModuleNotFoundError: No module named 'js'". With these guards, the script
can be imported/run in headless mode without crashing, while still working normally
in the browser via PyScript.
'''
import math
import random
# Try to import browser/pyodide APIs; fall back to headless-safe stubs
try:
    from js import document, window  # type: ignore
    from pyodide.ffi import create_proxy  # type: ignore
    PYSCRIPT = True
except Exception:
    document = None
    window = None
    PYSCRIPT = False
    def create_proxy(fn):
        # In headless mode, just return the function itself
        return fn
from models import Claw, MineObject, distance
from level import LevelManager
class Game:
    def __init__(self):
        if not PYSCRIPT:
            raise RuntimeError("Game UI requires a browser/PyScript runtime.")
        # Canvas and drawing context
        self.canvas = document.getElementById("game-canvas")
        self.ctx = self.canvas.getContext("2d")
        # UI elements
        self.overlay = document.getElementById("overlay")
        self.overlay_text = document.getElementById("overlay-text")
        self.btn_next = document.getElementById("btn-next")
        self.btn_retry = document.getElementById("btn-retry")
        self.width = self.canvas.width
        self.height = self.canvas.height
        # World params
        self.ground_y = self.height - 40
        self.hook_radius = 10
        # Game state
        self.level_manager = LevelManager()
        self.level_index = 1
        self.score = 0
        self.goal = 0
        self.time_left = 60.0
        self.objects = []
        self.claw = Claw(self.width / 2, 60, self.ground_y - 20)
        self.running = False
        self.level_active = True
        # Internal timing
        self._last_ts = None
        self._frame_cb = None
        self._raf_id = None  # Track the active RAF id to avoid duplicate loops
        self._transitioning = False  # Debounce Next/Retry
        # Event handlers (store proxies to avoid GC)
        self._keydown_proxy = create_proxy(self.on_keydown)
        self._click_proxy = create_proxy(self.on_click)
        self._next_proxy = create_proxy(self.on_next)
        self._retry_proxy = create_proxy(self.on_retry)
        document.addEventListener("keydown", self._keydown_proxy)
        self.canvas.addEventListener("mousedown", self._click_proxy)
        self.btn_next.addEventListener("click", self._next_proxy)
        self.btn_retry.addEventListener("click", self._retry_proxy)
        # Initial setup
        self.start_level(self.level_index)
    def start(self):
        # Idempotent: only start a new loop if none is running
        if self._raf_id is not None:
            return
        self.running = True
        self.level_active = True
        self._frame_cb = create_proxy(self._loop)
        self._raf_id = window.requestAnimationFrame(self._frame_cb)
    def start_level(self, index: int):
        cfg = self.level_manager.get_config(index, self.width, self.height, self.ground_y)
        self.level_index = index
        self.time_left = cfg["time_limit"]
        self.goal = cfg["goal_score"]
        self.objects = cfg["objects"]
        self.score = 0
        self.claw.reset()
        self.hide_overlay()
        self.running = True
        self.level_active = True
        self._last_ts = None
    def end_level(self, win: bool):
        # Stop game loop and cancel any scheduled frame
        self.running = False
        self.level_active = False
        if self._raf_id is not None:
            try:
                window.cancelAnimationFrame(self._raf_id)
            except Exception:
                pass
            self._raf_id = None
        self._frame_cb = None
        # Re-enable buttons for the next interaction
        try:
            self.btn_next.disabled = False
            self.btn_retry.disabled = False
        except Exception:
            pass
        self._transitioning = False
        # Overlay UI
        if win:
            self.overlay_text.innerText = f"Level {self.level_index} Completed!\nScore: {self.score} / Goal: {self.goal}"
            self.btn_next.style.display = "inline-block"
            self.btn_retry.style.display = "none"
        else:
            self.overlay_text.innerText = f"Time Up! Try Again.\nScore: {self.score} / Goal: {self.goal}"
            self.btn_next.style.display = "none"
            self.btn_retry.style.display = "inline-block"
        self.overlay.style.display = "flex"
    def hide_overlay(self):
        self.overlay.style.display = "none"
    def on_next(self, evt=None):
        # Debounce and prevent rapid multi-clicks
        if self._transitioning:
            return
        self._transitioning = True
        try:
            if evt is not None:
                evt.preventDefault()
        except Exception:
            pass
        try:
            self.btn_next.disabled = True
            self.btn_retry.disabled = True
        except Exception:
            pass
        # Increment difficulty
        self.level_index += 1
        self.start_level(self.level_index)
        self.start()
    def on_retry(self, evt=None):
        # Debounce and prevent rapid multi-clicks
        if self._transitioning:
            return
        self._transitioning = True
        try:
            if evt is not None:
                evt.preventDefault()
        except Exception:
            pass
        try:
            self.btn_next.disabled = True
            self.btn_retry.disabled = True
        except Exception:
            pass
        # Retry same level
        self.start_level(self.level_index)
        self.start()
    def on_keydown(self, evt):
        key = getattr(evt, "code", "")
        if key == "Space" or getattr(evt, "key", "") == " " or key == "Enter":
            # Prevent page scroll/accidental behaviors
            try:
                evt.preventDefault()
            except Exception:
                pass
            self.claw.start_grab()
    def on_click(self, evt):
        self.claw.start_grab()
    def _loop(self, ts):
        if self._last_ts is None:
            dt = 0.016
        else:
            dt = max(0.0, (ts - self._last_ts) / 1000.0)
        self._last_ts = ts
        if self.running:
            self.update(dt)
            self.draw()
            if self.running:
                self._raf_id = window.requestAnimationFrame(self._frame_cb)
            else:
                self._raf_id = None
    def update(self, dt: float):
        # Update timer
        if self.level_active:
            self.time_left = max(0.0, self.time_left - dt)
        # Update claw and handle interactions
        event = self.claw.update(dt, self.objects, self.hook_radius)
        # If an object has just been collected, adjust score
        if event and event["type"] == "collect":
            obj = event["object"]
            if obj.kind == "bomb":
                # Penalty for bomb
                self.score += obj.value  # negative
                self.time_left = max(0.0, self.time_left - 3.0)
            else:
                self.score += obj.value
        # Level transitions
        if self.time_left <= 0.0 and self.level_active:
            # Time's up
            won = self.score >= self.goal
            self.end_level(won)
        elif (self.score >= self.goal) and self.level_active:
            # Reached goal early
            self.end_level(True)
    def draw(self):
        ctx = self.ctx
        w, h = self.width, self.height
        # Clear
        ctx.clearRect(0, 0, w, h)
        # Background
        ctx.fillStyle = "#0d1b2a"
        ctx.fillRect(0, 0, w, h)
        # Ground
        ctx.fillStyle = "#2b2d42"
        ctx.fillRect(0, self.ground_y, w, h - self.ground_y)
        # Draw objects
        for obj in self.objects:
            if obj.collected:
                continue
            ctx.beginPath()
            ctx.arc(obj.x, obj.y, obj.r, 0, math.pi * 2)
            ctx.fillStyle = obj.color
            ctx.fill()
            ctx.lineWidth = 2
            ctx.strokeStyle = "#00000080"
            ctx.stroke()
            # Draw value label
            ctx.fillStyle = "#ffffff"
            ctx.font = "12px monospace"
            val = f"{obj.value:+d}" if obj.kind == "bomb" else f"{obj.value}"
            ctx.fillText(f"{obj.kind} ${val}", obj.x - obj.r, obj.y - obj.r - 4)
            # Draw position
            ctx.fillText(f"({int(obj.x)}, {int(obj.y)})", obj.x - obj.r, obj.y + obj.r + 12)
        # Draw claw rope and hook
        hook_x, hook_y = self.claw.hook_position()
        # Rope
        ctx.beginPath()
        ctx.moveTo(self.claw.anchor_x, self.claw.anchor_y)
        ctx.lineTo(hook_x, hook_y)
        ctx.lineWidth = 3
        ctx.strokeStyle = "#e0e1dd"
        ctx.stroke()
        # Hook
        ctx.beginPath()
        ctx.arc(hook_x, hook_y, self.hook_radius, 0, math.pi * 2)
        ctx.fillStyle = "#adb5bd"
        ctx.fill()
        ctx.lineWidth = 2
        ctx.strokeStyle = "#00000080"
        ctx.stroke()
        # Claw anchor
        ctx.beginPath()
        ctx.arc(self.claw.anchor_x, self.claw.anchor_y, 8, 0, math.pi * 2)
        ctx.fillStyle = "#e0fbfc"
        ctx.fill()
        # Status text
        ctx.fillStyle = "#ffffff"
        ctx.font = "16px monospace"
        ctx.fillText(f"Level: {self.level_index}", 12, 22)
        ctx.fillText(f"Score: {self.score}", 12, 42)
        ctx.fillText(f"Goal: {self.goal}", 12, 62)
        ctx.fillText(f"Time: {self.time_left:0.1f}s", 12, 82)
        # Display claw position
        ctx.fillText(f"Claw: ({int(hook_x)}, {int(hook_y)})", 12, 102)
        # Instructions
        ctx.fillStyle = "#ffffffaa"
        ctx.font = "14px monospace"
        ctx.fillText("Press Space or Click to grab!", w - 260, 24)
        # Boundaries
        ctx.strokeStyle = "#ffffff20"
        ctx.lineWidth = 1
        ctx.strokeRect(0, 0, w, h)
        # Top area separator
        ctx.strokeStyle = "#ffffff30"
        ctx.beginPath()
        ctx.moveTo(0, self.claw.anchor_y + 10)
        ctx.lineTo(w, self.claw.anchor_y + 10)
        ctx.stroke()
def main():
    if not PYSCRIPT:
        # Headless run: avoid raising when executed in non-browser tests
        print("Gold Miner requires PyScript (browser). Headless mode: skipping UI.")
        return
    game = Game()
    game.start()
# Auto-start only when running under PyScript in the browser
if PYSCRIPT:
    main()
else:
    # If invoked directly in a standard Python environment, do a tiny smoke test.
    if __name__ == "__main__":
        lm = LevelManager()
        cfg = lm.get_config(1, 900, 600, 560)
        print(f"Headless smoke test OK. Spawned objects: {len(cfg['objects'])}")