'''
Puzzle model and daily generator. Selects one category from each difficulty
(yellow, green, blue, purple) deterministically based on today's date,
shuffles the 16 words, and exposes structures for gameplay checks.
'''
from dataclasses import dataclass
from typing import Dict, List, Optional
import random
from datetime import date as dt_date
from category_bank import get_category_bank, CategoryDefinition
from utils import days_since_epoch
@dataclass
class Category:
    name: str
    words: List[str]
    difficulty: str  # 'yellow', 'green', 'blue', 'purple'
    color: str       # computed hex color
@dataclass
class Puzzle:
    words: List[str]
    word_to_category: Dict[str, int]  # word -> category index (0..3)
    categories: List[Category]        # 4 categories in display order (Y, G, B, P)
def get_color_for_difficulty(difficulty: str) -> str:
    mapping = {
        "yellow": "#f7da21",
        "green": "#66bb6a",
        "blue": "#42a5f5",
        "purple": "#8e24aa",
    }
    return mapping.get(difficulty.lower(), "#cccccc")
def generate_daily_puzzle(date: Optional[dt_date] = None) -> Puzzle:
    """
    Generate a daily puzzle deterministically:
    - Pick exactly one category from each difficulty: yellow, green, blue, purple.
    - Ensure all 16 words are unique.
    - Shuffle words with the same seeded RNG so the layout is daily-fixed.
    """
    if date is None:
        date = dt_date.today()
    seed = days_since_epoch(date)
    rng = random.Random(seed)
    bank = get_category_bank()
    # Split bank by difficulty
    diff_groups: Dict[str, List[CategoryDefinition]] = {"yellow": [], "green": [], "blue": [], "purple": []}
    for cat in bank:
        key = cat.difficulty.lower()
        if key in diff_groups:
            diff_groups[key].append(cat)
    # Safety checks
    for k in ("yellow", "green", "blue", "purple"):
        if not diff_groups[k]:
            raise ValueError(f"No categories available for difficulty: {k}")
    attempts = 0
    max_attempts = 1000
    while attempts < max_attempts:
        attempts += 1
        chosen_defs = [
            rng.choice(diff_groups["yellow"]),
            rng.choice(diff_groups["green"]),
            rng.choice(diff_groups["blue"]),
            rng.choice(diff_groups["purple"]),
        ]
        # Ensure uniqueness of words across chosen categories
        words: List[str] = []
        ok = True
        seen = set()
        for cd in chosen_defs:
            for w in cd.words:
                if w in seen:
                    ok = False
                    break
                seen.add(w)
                words.append(w)
            if not ok:
                break
        if not ok:
            continue
        # Construct categories in fixed order [yellow, green, blue, purple]
        categories: List[Category] = []
        for cd in chosen_defs:
            categories.append(Category(
                name=cd.name,
                words=list(cd.words),
                difficulty=cd.difficulty,
                color=get_color_for_difficulty(cd.difficulty)
            ))
        # Shuffle words deterministically
        rng.shuffle(words)
        # Build map word -> category index
        word_to_category: Dict[str, int] = {}
        for idx, cat in enumerate(categories):
            for w in cat.words:
                word_to_category[w] = idx
        return Puzzle(words=words, word_to_category=word_to_category, categories=categories)
    raise RuntimeError("Failed to generate a valid daily puzzle after many attempts.")