"""Pluggable tokenizer.

Cross-model raw token counts are meaningless (different vocabularies), so the
study only ever reports *shares*. For a share to be sound, the numerator and
the denominator must come from the same tokenizer. This module guarantees that
by making the choice explicit and recording it on every result.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Protocol


class Tokenizer(Protocol):
    name: str
    def encode(self, text: str) -> list[int]: ...
    def count(self, text: str) -> int: ...


class HeuristicTokenizer:
    """Word/punctuation split, hashed to ids. Only for smoke tests.

    The ids MUST depend on the content: an earlier version returned
    ``range(n)``, which made every text of the same length compare as
    identical and drove the redundancy measure to a meaningless ~100%.
    """
    name = "heuristic:wordpunct"
    _SPLIT = __import__("re").compile(r"\w+|[^\w\s]")

    def encode(self, text: str) -> list[int]:
        return [hash(t) & 0xFFFFFFFF for t in self._SPLIT.findall(text)]

    def count(self, text: str) -> int:
        return len(self.encode(text))


class TiktokenTokenizer:
    def __init__(self, encoding: str = "o200k_base") -> None:
        import tiktoken
        self._enc = tiktoken.get_encoding(encoding)
        self.name = f"tiktoken:{encoding}"

    def encode(self, text: str) -> list[int]:
        return self._enc.encode(text, disallowed_special=())

    def count(self, text: str) -> int:
        return len(self.encode(text))


@lru_cache(maxsize=8)
def get_tokenizer(kind: str = "auto") -> Tokenizer:
    """kind: "auto" | "tiktoken" | "heuristic" | "tiktoken:<encoding>"."""
    if kind.startswith("tiktoken"):
        enc = kind.split(":", 1)[1] if ":" in kind else "o200k_base"
        return TiktokenTokenizer(enc)
    if kind == "heuristic":
        return HeuristicTokenizer()
    if kind == "strict":
        # Never silently degrade: used for anything that will be published.
        return TiktokenTokenizer()
    if kind == "auto":
        try:
            return TiktokenTokenizer()
        except Exception as exc:
            import sys
            print(
                "\n*** TOKENIZER FALLBACK ***\n"
                f"tiktoken unavailable ({type(exc).__name__}: {str(exc)[:90]}).\n"
                "Falling back to a word-split heuristic. Shares remain internally\n"
                "consistent, but DO NOT PUBLISH these numbers. tiktoken downloads\n"
                "its encoding on first use, so this usually means no network.\n"
                "Re-run with --tokenizer strict once it can reach the internet.\n",
                file=sys.stderr,
            )
            return HeuristicTokenizer()
    raise ValueError(f"unknown tokenizer {kind!r}")
