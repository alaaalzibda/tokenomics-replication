'''
Entity classes for the roguelike game: Player and Monster.
'''
from dataclasses import dataclass
@dataclass
class Player:
    x: int
    y: int
    hp: int
    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy
@dataclass
class Monster:
    x: int
    y: int
    hp: int