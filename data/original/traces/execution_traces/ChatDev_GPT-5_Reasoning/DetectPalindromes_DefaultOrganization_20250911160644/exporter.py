'''
Export utilities for writing results to CSV.
'''
import csv
from typing import Iterable
from palindrome_detector import PalindromeMatch
def export_results_to_csv(path: str, results: Iterable[PalindromeMatch]) -> None:
    """
    Write results to a CSV file with headers.
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Content", "Normalized", "Length", "Line", "StartCol", "EndCol"])
        for r in results:
            writer.writerow([r.category, r.text, r.normalized, r.length, r.line_no, r.start_pos, r.end_pos])