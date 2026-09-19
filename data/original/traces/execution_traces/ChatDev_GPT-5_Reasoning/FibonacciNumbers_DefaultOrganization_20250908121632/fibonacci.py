'''
Fibonacci sequence utilities.
This module provides core logic for generating Fibonacci numbers
and validating user input. The primary function `generate_fibonacci_up_to`
returns all Fibonacci numbers less than or equal to the given limit,
starting from 0, 1 (i.e., 0, 1, 1, 2, 3, 5, ...).
'''
from typing import List, Dict
def parse_limit(text: str) -> int:
    """
    Parse and validate the limit input as a non-negative integer.
    Args:
        text: Input string from the user.
    Returns:
        A non-negative integer representing the upper bound (inclusive).
    Raises:
        ValueError: If the input is empty, not an integer, or negative.
    """
    s = (text or "").strip()
    if not s:
        raise ValueError("Please enter a non-negative integer.")
    try:
        value = int(s, 10)
    except (TypeError, ValueError):
        raise ValueError("Invalid number. Enter a whole number like 0, 10, 12345.")
    if value < 0:
        raise ValueError("The number must be non-negative (>= 0).")
    return value
def generate_fibonacci_up_to(limit: int) -> List[int]:
    """
    Generate Fibonacci numbers up to and including the given limit.
    The sequence starts with 0 and 1: 0, 1, 1, 2, 3, 5, ...
    Args:
        limit: Non-negative integer specifying the inclusive upper bound.
    Returns:
        A list of Fibonacci numbers n where n <= limit.
    Raises:
        ValueError: If limit is negative.
    """
    if limit < 0:
        raise ValueError("Limit must be non-negative.")
    result: List[int] = []
    a, b = 0, 1
    while a <= limit:
        result.append(a)
        a, b = b, a + b
    return result
def format_sequence(seq: List[int], separator: str = ", ") -> str:
    """
    Format a sequence of integers into a string.
    Args:
        seq: List of integers.
        separator: String used to separate numbers.
    Returns:
        A single string with numbers joined by the separator.
    """
    return separator.join(str(x) for x in seq)
def sequence_stats(seq: List[int]) -> Dict[str, int]:
    """
    Compute basic statistics for a sequence of integers.
    Args:
        seq: List of integers.
    Returns:
        A dict with keys: 'count', 'max', 'sum'.
        For an empty list, count is 0, max is 0, sum is 0.
    """
    if not seq:
        return {"count": 0, "max": 0, "sum": 0}
    return {"count": len(seq), "max": max(seq), "sum": sum(seq)}