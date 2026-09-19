"""Position-aware redundancy, in token space.

Why this module exists
----------------------
A first cut computed block-level duplication and prefix-cache coverage
separately, then reported "uncacheable = near - cacheable". That is unsound:
the two are measured in different spaces, are not nested, and on a run with a
long shared preamble the subtraction went negative and clamped to zero -- which
would have silently hidden the exact quantity the study is about.

This module measures everything in one space: tokens of the prompt, with
positions. For each call:

  * tokenise the prompt once  -> t[0..n)
  * cache_len  = longest common prefix with any earlier prompt in the run
  * a token at position i is REDUNDANT if the k-token window starting at i was
    already sent in an earlier call of the run
  * a redundant token is CACHEABLE if i < cache_len, UNCACHEABLE otherwise

so redundant = cacheable_redundant + uncacheable_redundant, exactly, by
construction. `uncacheable_redundant` is the headline: content the system pays
full price for on every call and that no prefix cache can reach, because it
does not sit at the front of the prompt.

k (window size) is a real parameter. Too small and ordinary English collides;
too large and a one-token edit hides a whole repeated file. Default 32; the
sensitivity of the result to k belongs in the write-up.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from .tokenize import Tokenizer, get_tokenizer
from .trace import CallRecord

DEFAULT_WINDOW = 32


@dataclass
class RunRedundancy:
    run_id: str
    task_id: str
    model: str
    n_calls: int
    input_tokens: int
    redundant_tokens: int
    cacheable_redundant_tokens: int
    uncacheable_redundant_tokens: int
    prefix_cache_tokens: int
    tokenizer: str
    window: int

    def _s(self, n: int) -> float:
        return n / self.input_tokens if self.input_tokens else 0.0

    @property
    def redundancy(self) -> float:
        """Share of input tokens already sent earlier in the same run."""
        return self._s(self.redundant_tokens)

    @property
    def cacheable(self) -> float:
        """Redundant AND inside the prefix a provider cache would hit."""
        return self._s(self.cacheable_redundant_tokens)

    @property
    def uncacheable(self) -> float:
        """Redundant but outside the cacheable prefix. The headline number."""
        return self._s(self.uncacheable_redundant_tokens)

    @property
    def prefix_coverage(self) -> float:
        """Share of input tokens sitting in a cacheable prefix at all."""
        return self._s(self.prefix_cache_tokens)


def _lcp(a: Sequence[int], b: Sequence[int]) -> int:
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def analyse_run(
    calls: Sequence[CallRecord],
    tokenizer: Tokenizer | None = None,
    window: int = DEFAULT_WINDOW,
) -> RunRedundancy:
    if not calls:
        raise ValueError("analyse_run got no calls")
    tok = tokenizer or get_tokenizer("auto")

    seen_windows: set[tuple[int, ...]] = set()
    prior: list[list[int]] = []

    total = red = cache_red = uncache_red = prefix_tokens = 0

    for call in calls:
        t = tok.encode(call.prompt_text())
        n = len(t)
        total += n

        cache_len = max((_lcp(t, p) for p in prior), default=0)
        prefix_tokens += cache_len

        # Mark tokens covered by a window seen in an earlier call.
        covered = bytearray(n)
        if n >= window:
            for i in range(n - window + 1):
                if tuple(t[i : i + window]) in seen_windows:
                    for j in range(i, i + window):
                        covered[j] = 1

        for i in range(n):
            if covered[i]:
                red += 1
                if i < cache_len:
                    cache_red += 1
                else:
                    uncache_red += 1

        # Only now add this call's windows, so a call never matches itself.
        if n >= window:
            for i in range(n - window + 1):
                seen_windows.add(tuple(t[i : i + window]))
        prior.append(t)

    assert red == cache_red + uncache_red, "redundancy partition must be exact"

    return RunRedundancy(
        run_id=calls[0].run_id,
        task_id=calls[0].task_id,
        model=calls[0].model,
        n_calls=len(calls),
        input_tokens=total,
        redundant_tokens=red,
        cacheable_redundant_tokens=cache_red,
        uncacheable_redundant_tokens=uncache_red,
        prefix_cache_tokens=prefix_tokens,
        tokenizer=tok.name,
        window=window,
    )


def summarise(results: Sequence[RunRedundancy]) -> dict[str, float]:
    if not results:
        return {}
    return {
        "redundancy": mean(r.redundancy for r in results),
        "cacheable": mean(r.cacheable for r in results),
        "uncacheable": mean(r.uncacheable for r in results),
        "prefix_coverage": mean(r.prefix_coverage for r in results),
    }


def window_sensitivity(
    calls: Sequence[CallRecord],
    windows: Sequence[int] = (8, 16, 32, 64, 128),
    tokenizer: Tokenizer | None = None,
) -> dict[int, float]:
    """Redundancy as a function of k. Any claim must survive this table."""
    tok = tokenizer or get_tokenizer("auto")
    return {w: analyse_run(calls, tokenizer=tok, window=w).redundancy for w in windows}
