"""Context redundancy: how much of the input token share is re-sent context?

This is the part of the study that is not a replication.

Salim et al. report that input tokens are 53.9% of all consumption, rising to
80.2% in Documentation and ~60% in Design and Testing. They stop there. The
open question is how much of that input is content the system had *already
sent* in an earlier call of the same run -- i.e. how much of the dominant cost
is re-transmission rather than new information.

We report three distinct numbers, because they answer three different
questions and are routinely conflated:

1. exact_redundancy
   Share of input tokens sitting in a block byte-identical (after whitespace
   normalisation) to a block sent earlier in the run. A floor.

2. near_redundancy
   As above, but a block also counts if it is >= `near_threshold` similar to an
   earlier block. Catches the real agentic pattern: the same file resent with
   three lines changed after a review round. A realistic estimate.

3. cacheable_redundancy
   Share of input tokens covered by the longest common *prefix* with any
   earlier prompt in the run. This is the only one of the three that maps to
   money today: provider prefix caches (OpenAI, Anthropic) bill a cache hit at
   a fraction of the input rate, but they match on prefixes only. Content that
   repeats in the middle of a prompt is redundant and yet uncacheable.

The gap between (2) and (3) is the interesting quantity: it is the redundancy
that current caching cannot reach, and therefore the size of the prize for
context restructuring rather than caching.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Sequence

from .tokenize import Tokenizer, get_tokenizer
from .trace import CallRecord

_WS = re.compile(r"\s+")
_BLOCK_SPLIT = re.compile(r"\n\s*\n")


def normalise(text: str) -> str:
    return _WS.sub(" ", text).strip()


def block_key(text: str) -> str:
    return hashlib.blake2b(normalise(text).encode("utf-8"), digest_size=16).hexdigest()


def split_blocks(text: str, min_chars: int = 40) -> list[str]:
    """Split a message into comparison units on blank lines.

    Blocks shorter than `min_chars` are ignored: matching "OK" or a bare brace
    across calls would inflate redundancy without meaning anything.
    """
    return [b for b in (p.strip() for p in _BLOCK_SPLIT.split(text)) if len(b) >= min_chars]


@dataclass
class RunRedundancy:
    run_id: str
    task_id: str
    model: str
    n_calls: int
    input_tokens: int
    exact_redundant_tokens: int
    near_redundant_tokens: int
    cacheable_tokens: int
    tokenizer: str
    near_threshold: float

    def _share(self, n: int) -> float:
        return n / self.input_tokens if self.input_tokens else 0.0

    @property
    def exact_redundancy(self) -> float:
        return self._share(self.exact_redundant_tokens)

    @property
    def near_redundancy(self) -> float:
        return self._share(self.near_redundant_tokens)

    @property
    def cacheable_redundancy(self) -> float:
        return self._share(self.cacheable_tokens)

    @property
    def uncacheable_redundancy(self) -> float:
        """Redundant but not reachable by a prefix cache. The headline gap."""
        return max(0.0, self.near_redundancy - self.cacheable_redundancy)


def _longest_common_prefix(a: Sequence[int], b: Sequence[int]) -> int:
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def analyse_run(
    calls: Sequence[CallRecord],
    tokenizer: Tokenizer | None = None,
    near_threshold: float = 0.90,
    max_near_candidates: int = 400,
) -> RunRedundancy:
    """Compute the three redundancy measures for one run.

    `calls` must be the ordered calls of a single run.
    """
    tok = tokenizer or get_tokenizer("auto")
    if not calls:
        raise ValueError("analyse_run got no calls")

    seen_exact: set[str] = set()
    seen_norm: list[str] = []          # for near-duplicate comparison
    prior_encodings: list[list[int]] = []

    total_input = 0
    exact_tokens = 0
    near_tokens = 0
    cacheable_tokens = 0

    for call in calls:
        prompt = call.prompt_text()
        encoded = tok.encode(prompt)
        total_input += len(encoded)

        # --- 3. prefix-cacheable: best LCP against any earlier prompt ---
        if prior_encodings:
            cacheable_tokens += max(
                _longest_common_prefix(encoded, p) for p in prior_encodings
            )
        prior_encodings.append(encoded)

        # --- 1 & 2. block-level exact and near duplication ---
        new_keys: list[str] = []
        new_norms: list[str] = []
        for msg in call.messages:
            for block in split_blocks(msg.content):
                n_tok = tok.count(block)
                key = block_key(block)
                norm = normalise(block)

                if key in seen_exact:
                    exact_tokens += n_tok
                    near_tokens += n_tok
                else:
                    # only pay for fuzzy matching when the exact test fails
                    if _is_near_duplicate(
                        norm, seen_norm, near_threshold, max_near_candidates
                    ):
                        near_tokens += n_tok
                    new_keys.append(key)
                    new_norms.append(norm)

        seen_exact.update(new_keys)
        seen_norm.extend(new_norms)

    return RunRedundancy(
        run_id=calls[0].run_id,
        task_id=calls[0].task_id,
        model=calls[0].model,
        n_calls=len(calls),
        input_tokens=total_input,
        exact_redundant_tokens=exact_tokens,
        near_redundant_tokens=near_tokens,
        cacheable_tokens=cacheable_tokens,
        tokenizer=tok.name,
        near_threshold=near_threshold,
    )


def _is_near_duplicate(
    norm: str, pool: list[str], threshold: float, max_candidates: int
) -> bool:
    if not pool:
        return False
    # Most recent blocks first: in an agent run, the near-duplicate of a block
    # is almost always the previous version of the same artefact.
    candidates = pool[-max_candidates:]
    n = len(norm)
    lo, hi = n * threshold, n / threshold if threshold else n
    for other in reversed(candidates):
        if not (lo <= len(other) <= hi):   # cheap length gate before the O(n^2)
            continue
        if SequenceMatcher(None, norm, other, autojunk=False).quick_ratio() < threshold:
            continue
        if SequenceMatcher(None, norm, other, autojunk=False).ratio() >= threshold:
            return True
    return False
