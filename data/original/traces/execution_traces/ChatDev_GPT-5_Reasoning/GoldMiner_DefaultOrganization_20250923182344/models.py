'''
Game entities and mechanics: Claw and MineObject,
plus utility functions used across the game.
'''
import math
from typing import List, Optional, Dict
def clamp(v, lo, hi):
    return max(lo, min(hi, v))
def distance(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)
class MineObject:
    def __init__(self, x: float, y: float, r: float, kind: str, value: int, weight: float, color: str):
        self.x = x
        self.y = y
        self.r = r
        self.kind = kind
        self.value = value
        self.weight = max(0.1, float(weight))
        self.color = color
        self.collected = False
    def __repr__(self):
        return f"<MineObject {self.kind} (${self.value}) @({self.x:.1f},{self.y:.1f}) r={self.r}>"
class Claw:
    def __init__(self, anchor_x: float, anchor_y: float, max_depth_y: float):
        # Anchor and geometry
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        # Swing parameters
        self.angle_deg = 0.0
        self.angle_min = -65.0
        self.angle_max = 65.0
        self.swing_speed = 65.0  # degrees per second
        self.swing_dir = 1.0
        # Rope
        self.rope_length = 30.0
        self.rope_min = 30.0
        self.rope_max = max(120.0, max_depth_y - anchor_y - 10.0)
        self.extend_speed = 360.0          # px/s
        self.retract_base_speed = 320.0    # px/s, modified by weight
        # State machine: "swing", "extend", "retract"
        self.state = "swing"
        self.attached: Optional[MineObject] = None
    def reset(self):
        self.angle_deg = 0.0
        self.swing_dir = 1.0
        self.rope_length = self.rope_min
        self.state = "swing"
        self.attached = None
    def start_grab(self):
        if self.state == "swing":
            self.state = "extend"
    def hook_position(self):
        rad = math.radians(self.angle_deg)
        hx = self.anchor_x + math.cos(rad) * self.rope_length
        hy = self.anchor_y + math.sin(rad) * self.rope_length
        return hx, hy
    def _attach(self, obj: MineObject):
        self.attached = obj
    def _release(self):
        self.attached = None
    def update(self, dt: float, objects: List[MineObject], hook_radius: float) -> Optional[Dict]:
        """
        Update claw physics and handle grabbing logic.
        Returns an event dict when an object is collected:
          {"type": "collect", "object": obj}
        """
        event = None
        if self.state == "swing":
            # Update swing angle
            self.angle_deg += self.swing_speed * self.swing_dir * dt
            if self.angle_deg >= self.angle_max:
                self.angle_deg = self.angle_max
                self.swing_dir = -1.0
            elif self.angle_deg <= self.angle_min:
                self.angle_deg = self.angle_min
                self.swing_dir = 1.0
            self.rope_length = self.rope_min
        elif self.state == "extend":
            # Extend rope
            self.rope_length += self.extend_speed * dt
            hx, hy = self.hook_position()
            # Check collision with objects
            hit_obj = None
            for obj in objects:
                if obj.collected:
                    continue
                if distance(hx, hy, obj.x, obj.y) <= (hook_radius + obj.r):
                    hit_obj = obj
                    break
            if hit_obj is not None:
                self._attach(hit_obj)
                self.state = "retract"
            else:
                # If reached max rope length, retract empty
                if self.rope_length >= self.rope_max or hy >= (self.anchor_y + self.rope_max - 10.0):
                    self.state = "retract"
        elif self.state == "retract":
            # Retraction speed depends on weight
            speed = self.retract_base_speed
            if self.attached is not None:
                # Heavier objects reel in slower
                speed = max(60.0, self.retract_base_speed / float(self.attached.weight))
            self.rope_length -= speed * dt
            # Move attached object with hook
            hx, hy = self.hook_position()
            if self.attached is not None:
                self.attached.x = hx
                self.attached.y = hy
            # Completed retraction
            if self.rope_length <= self.rope_min:
                self.rope_length = self.rope_min
                # If we have an attached object, collect it
                if self.attached is not None:
                    self.attached.collected = True
                    event = {"type": "collect", "object": self.attached}
                # Return to swinging
                self._release()
                self.state = "swing"
        return event