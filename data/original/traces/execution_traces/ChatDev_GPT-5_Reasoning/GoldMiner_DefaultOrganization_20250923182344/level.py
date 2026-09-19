'''
Level manager: provides increasing difficulty with tighter time limits
and more obstacles, plus object spawning utilities.
'''
import random
from typing import Dict, List
from models import MineObject, distance
class LevelManager:
    def __init__(self):
        # You can tweak these to shape the difficulty curve
        self.base_time = 60
        self.min_time = 25
        self.base_goal = 400
        self.goal_step = 220
    def get_config(self, level_idx: int, width: int, height: int, ground_y: int) -> Dict:
        # Tighter time limits and higher goals as levels progress
        time_limit = max(self.min_time, self.base_time - (level_idx - 1) * 5)
        goal = self.base_goal + (level_idx - 1) * self.goal_step
        # Spawn objects with increasing count and obstacles
        objects = self.spawn_objects(level_idx, width, height, ground_y)
        return {
            "time_limit": time_limit,
            "goal_score": goal,
            "objects": objects,
        }
    def spawn_objects(self, level_idx: int, width: int, height: int, ground_y: int) -> List[MineObject]:
        # Ground area to place objects: below a top margin and above ground
        left, right = 40, width - 40
        top = ground_y - (height * 0.65)  # lay objects in lower ~2/3
        bottom = ground_y - 10
        # Counts increase with level index
        gold_small = 3 + level_idx
        gold_large = 1 + (level_idx // 2)
        rocks = 2 + level_idx
        diamonds = max(1, level_idx // 2)
        bombs = max(0, (level_idx - 1) // 2)
        candidates = []
        # Helper to place without excessive overlap
        def place_object(r, tries=100):
            for _ in range(tries):
                x = random.uniform(left + r, right - r)
                y = random.uniform(top + r, bottom - r)
                if y < top + r or y > bottom - r:
                    continue
                ok = True
                for c in candidates:
                    if distance(x, y, c.x, c.y) <= (r + c.r + 6):
                        ok = False
                        break
                if ok:
                    return x, y
            # Fallback: allow overlap slightly if too crowded
            return random.uniform(left + r, right - r), random.uniform(top + r, bottom - r)
        # Gold small
        for _ in range(gold_small):
            r = random.randint(14, 20)
            x, y = place_object(r)
            value = random.randint(80, 140)
            weight = random.uniform(0.8, 1.3)
            candidates.append(MineObject(x, y, r, "gold", value, weight, "#f4d35e"))
        # Gold large
        for _ in range(gold_large):
            r = random.randint(24, 30)
            x, y = place_object(r)
            value = random.randint(250, 380)
            weight = random.uniform(1.6, 2.4)
            candidates.append(MineObject(x, y, r, "gold", value, weight, "#e9c46a"))
        # Rocks (obstacles, low value, heavy)
        for _ in range(rocks):
            r = random.randint(16, 24)
            x, y = place_object(r)
            value = random.randint(10, 40)
            weight = random.uniform(2.0, 3.0)
            candidates.append(MineObject(x, y, r, "rock", value, weight, "#6c757d"))
        # Diamonds (high value, light)
        for _ in range(diamonds):
            r = random.randint(10, 14)
            x, y = place_object(r)
            value = random.randint(400, 650)
            weight = random.uniform(0.6, 1.0)
            candidates.append(MineObject(x, y, r, "diamond", value, weight, "#00d4ff"))
        # Bombs (negative value, moderate weight) - obstacles
        for _ in range(bombs):
            r = random.randint(12, 16)
            x, y = place_object(r)
            value = -random.randint(150, 250)
            weight = random.uniform(1.0, 1.6)
            candidates.append(MineObject(x, y, r, "bomb", value, weight, "#e63946"))
        return candidates