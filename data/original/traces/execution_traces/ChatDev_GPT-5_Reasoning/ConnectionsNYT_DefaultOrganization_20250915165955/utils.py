'''
Utility helpers for date handling and deterministic RNG seeding for daily puzzles.
'''
from datetime import date
import random
def today_date_str() -> str:
    """Return current local date as YYYY-MM-DD string."""
    return date.today().isoformat()
def days_since_epoch(d: date) -> int:
    """Deterministic integer seed from a date: days since Unix epoch."""
    epoch = date(1970, 1, 1)
    delta = d - epoch
    return delta.days
def get_seeded_random(d: date) -> random.Random:
    """Get a random.Random instance seeded by the provided date."""
    return random.Random(days_since_epoch(d))