'''
Core palindrome detection logic used by the GUI and exporter.
Provides:
- DetectionOptions: configuration for what to detect and how to normalize
- PalindromeMatch: result record with positions compatible with Tk Text
- detect_palindromes: main API to analyze a text string
'''
from dataclasses import dataclass
from typing import List, Iterator, Tuple
import re
@dataclass
class DetectionOptions:
    """Options for controlling what to detect and how to normalize."""
    check_words: bool = True
    check_sentences: bool = True
    check_lines: bool = True
    min_length: int = 3
    ignore_case: bool = True
    ignore_non_alnum: bool = True
@dataclass
class PalindromeMatch:
    """
    A single palindrome detection result.
    line_no is 1-based (Tk Text indexing starts at 1).
    start_pos/end_pos are 0-based column offsets within that line; end_pos is exclusive.
    """
    category: str           # 'word' | 'sentence' | 'line'
    text: str               # Original substring as it appears in the file
    normalized: str         # Normalized text used for palindrome check
    length: int             # Length of normalized text
    line_no: int            # 1-based line number
    start_pos: int          # 0-based column start in the line
    end_pos: int            # 0-based column end (exclusive) in the line
def _normalize(s: str, ignore_case: bool, ignore_non_alnum: bool) -> str:
    """Normalize text according to options (strip non-alnum, optional casefold)."""
    if ignore_non_alnum:
        s = "".join(ch for ch in s if ch.isalnum())
    if ignore_case:
        s = s.casefold()
    return s
def _is_palindrome(s: str) -> bool:
    """Return True if s is a non-empty palindrome."""
    return len(s) > 0 and s == s[::-1]
def _iter_words(line: str) -> Iterator[Tuple[int, int]]:
    """
    Yield (start, end) spans for words within a line.
    Words are contiguous alphanumeric sequences (Unicode-aware); underscores are excluded.
    """
    n = len(line)
    i = 0
    while i < n:
        # Skip non-alphanumeric characters
        while i < n and not line[i].isalnum():
            i += 1
        if i >= n:
            break
        start = i
        # Consume contiguous alphanumeric characters
        while i < n and line[i].isalnum():
            i += 1
        yield start, i
def _iter_sentences(line: str) -> Iterator[Tuple[int, int]]:
    """
    Yield (start, end) spans of sentence-like segments within a single line.
    Sentences end at '.', '!' or '?' (include trailing closing quotes/brackets if present).
    The final fragment without terminal punctuation is also yielded.
    """
    n = len(line)
    start = 0
    i = 0
    while i < n:
        if line[i] in ".!?":
            end = i + 1
            # Include typical trailing quotes/brackets adjacent to sentence end.
            while end < n and line[end] in ')"\']':
                end += 1
            yield start, end
            # Skip whitespace before next sentence
            j = end
            while j < n and line[j].isspace():
                j += 1
            start = j
            i = j
        else:
            i += 1
    if start < n:
        yield start, n
def detect_palindromes(text: str, options: DetectionOptions) -> List[PalindromeMatch]:
    """
    Detect palindromic words, sentences, and lines within the provided text.
    Processing is done per line so the GUI can highlight words/sentences within a single line.
    """
    results: List[PalindromeMatch] = []
    lines = text.splitlines()  # does not keep newline; line numbers remain consistent with Tk Text
    for line_no, line in enumerate(lines, start=1):
        # Entire line
        if options.check_lines:
            norm_line = _normalize(line, options.ignore_case, options.ignore_non_alnum)
            if len(norm_line) >= options.min_length and _is_palindrome(norm_line):
                results.append(PalindromeMatch(
                    category="line",
                    text=line,
                    normalized=norm_line,
                    length=len(norm_line),
                    line_no=line_no,
                    start_pos=0,
                    end_pos=len(line),
                ))
        # Words in line
        if options.check_words:
            for start, end in _iter_words(line):
                segment = line[start:end]
                norm = _normalize(segment, options.ignore_case, options.ignore_non_alnum)
                if len(norm) >= options.min_length and _is_palindrome(norm):
                    results.append(PalindromeMatch(
                        category="word",
                        text=segment,
                        normalized=norm,
                        length=len(norm),
                        line_no=line_no,
                        start_pos=start,
                        end_pos=end,
                    ))
        # Sentences in line
        if options.check_sentences:
            for start, end in _iter_sentences(line):
                segment = line[start:end]
                if not segment.strip():
                    continue
                norm = _normalize(segment, options.ignore_case, options.ignore_non_alnum)
                if len(norm) >= options.min_length and _is_palindrome(norm):
                    results.append(PalindromeMatch(
                        category="sentence",
                        text=segment,
                        normalized=norm,
                        length=len(norm),
                        line_no=line_no,
                        start_pos=start,
                        end_pos=end,
                    ))
    return results