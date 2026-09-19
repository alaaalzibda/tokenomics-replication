'''
Word lists and word-selection helpers:
- ANSWER_LIST: curated list of 5-letter English words used for the daily answer.
- GUESSES_LIST/VALID_GUESSES: allowed guess dictionary; membership is enforced during validation.
- Validation ensures only 5-letter A–Z words are included to prevent runtime crashes.
- get_daily_word(date=None): deterministically picks a word based on date (UTC).
- get_random_word(): returns a random answer word.
- is_valid_guess(word): fast O(1) dictionary membership check for guesses.
'''
import random
from datetime import date as Date, datetime, timezone
from typing import List, Set
# A modest curated list of 5-letter English words for daily answers.
# You can extend this list as desired.
ANSWER_LIST = [
    "apple", "brave", "crane", "delta", "eagle", "flame", "grape", "honey", "ivory", "joker",
    "kneel", "lemon", "mango", "noble", "ocean", "piano", "queen", "roast", "sunny", "tiger",
    "ultra", "vigor", "whale", "xenon", "yacht", "zesty", "adore", "bloom", "cider", "dolly",
    "ember", "fancy", "glove", "hazel", "irony", "jelly", "kitty", "lunar", "mirth", "nylon",
    "optic", "pride", "quilt", "rally", "salsa", "tease", "unite", "vivid", "waltz", "xylem",
    "yodel", "zebra", "angel", "bison", "chess", "dwell", "elite", "forgo", "gamma", "hippo",
    "inert", "jaunt", "karma", "linen", "metal", "nicer", "omega", "parer", "quake", "riper",
    "solar", "table", "unfed", "voter", "woven", "xerox", "yearn", "zonal", "aloft", "blaze",
    "canny", "drape", "expel", "femur", "gaily", "hoist", "ingot", "jolly", "knack", "lodge",
    "moult", "naiad", "ounce", "pleat", "radii", "sleet", "theta", "udder", "vaunt", "worry",
    "wreak", "wrung", "yeast", "zippy"
]
def _validate_answers(lst: List[str]) -> List[str]:
    """
    Validate and normalize the answer/guess lists:
    - Only keep 5-letter alphabetic words.
    - Lowercase all words.
    Raise ValueError if any invalid entries are found to prevent regressions.
    """
    invalid = [w for w in lst if not (isinstance(w, str) and len(w) == 5 and w.isalpha())]
    if invalid:
        raise ValueError(
            "Word lists must contain only 5-letter alphabetic words. Invalid entries: "
            + ", ".join(map(str, invalid))
        )
    return [w.lower() for w in lst]
VALID_ANSWERS: List[str] = _validate_answers(ANSWER_LIST)
assert len(VALID_ANSWERS) > 0, "VALID_ANSWERS must not be empty."
# Allowed guesses dictionary. Start with answers plus a modest set of common words.
GUESSES_LIST = list(set(ANSWER_LIST + [
    # Common 5-letter English words
    "about", "other", "which", "their", "there", "would", "could", "these", "those", "where",
    "after", "again", "below", "every", "first", "great", "house", "large", "never", "place",
    "small", "sound", "still", "thing", "think", "three", "world", "young", "right", "light",
    "point", "water", "story", "money", "heart", "music", "human", "laugh", "rough", "tough",
    "sugar", "spice", "sweet", "salty", "bread", "cheer", "grill", "grind", "spoon", "knife",
    "spike", "pride", "glory", "sleet", "storm", "cloud", "winds", "sunny", "rainy", "snowy",
    "zesty", "amber", "beach", "cabin", "drift", "flint", "gleam", "hover", "ivies", "jokes",
    "knees", "leapt", "mirth", "novel", "oasis", "punch", "quart", "rhyme", "sugar", "tulip",
    "udder", "vocal", "whirl", "xenon", "youth", "zebra"
]))
VALID_GUESSES: Set[str] = set(_validate_answers(GUESSES_LIST))
def is_valid_guess(word: str) -> bool:
    """Return True if the provided 5-letter word is in the allowed guess dictionary."""
    if not isinstance(word, str):
        return False
    return word.lower() in VALID_GUESSES
def _utc_today() -> Date:
    return datetime.now(timezone.utc).date()
def get_daily_word(date: Date = None) -> str:
    """
    Deterministically return the daily word for the given UTC date.
    If date is None, use today's UTC date.
    Uses a fixed base date to compute an index into the validated answer list.
    """
    base = Date(2021, 6, 19)  # Wordle-origin-like base date
    if date is None:
        date = _utc_today()
    answers = VALID_ANSWERS
    if date < base:
        # If before base, wrap forward using absolute day difference
        idx = abs((base - date).days) % len(answers)
        return answers[idx]
    offset = (date - base).days
    idx = offset % len(answers)
    return answers[idx]
def get_random_word() -> str:
    """Return a random word from the validated answer list."""
    return random.choice(VALID_ANSWERS)