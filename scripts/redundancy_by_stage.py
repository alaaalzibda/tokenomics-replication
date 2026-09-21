"""Redundancy broken down by SDLC stage.

The original paper reports where tokens are SPENT, by stage. This reports how
much of each stage's input is text the run had already sent -- so the two
tables line up and can be read together.

A token is redundant if the k-token window starting at it was already sent
earlier in the run; cacheable if it also lies within the longest common prefix
with an earlier prompt, uncacheable otherwise. Each call is attributed to the
stage that was running when it was made.
"""
from __future__ import annotations

import argparse, glob, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tokenomics.phases import stage_for, STAGES          # noqa: E402
from tokenomics.shingle import DEFAULT_WINDOW, _lcp      # noqa: E402
from tokenomics.tokenize import get_tokenizer            # noqa: E402
from tokenomics.trace import read_trace                  # noqa: E402


def per_stage(calls, tok, window=DEFAULT_WINDOW):
    seen: set[tuple[int, ...]] = set()
    prior: list[list[int]] = []
    acc = defaultdict(lambda: [0, 0, 0])   # stage -> [input, redundant, uncacheable]

    for call in calls:
        t = tok.encode(call.prompt_text())
        n = len(t)
        stage = stage_for(call.phase)
        cache_len = max((_lcp(t, p) for p in prior), default=0)

        covered = bytearray(n)
        if n >= window:
            for i in range(n - window + 1):
                if tuple(t[i:i + window]) in seen:
                    for j in range(i, i + window):
                        covered[j] = 1

        red = sum(covered)
        unc = sum(1 for i in range(n) if covered[i] and i >= cache_len)
        acc[stage][0] += n
        acc[stage][1] += red
        acc[stage][2] += unc

        if n >= window:
            for i in range(n - window + 1):
                seen.add(tuple(t[i:i + window]))
        prior.append(t)
    return acc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("--tokenizer", default="auto")
    args = ap.parse_args()

    tok = get_tokenizer(args.tokenizer)
    total = defaultdict(lambda: [0, 0, 0])
    files = sorted(glob.glob(args.pattern))
    for f in files:
        for stage, v in per_stage(read_trace(f), tok).items():
            for i in range(3):
                total[stage][i] += v[i]

    print(f"tokenizer = {tok.name}   tasks = {len(files)}\n")
    print(f"{'stage':<17}{'input tok':>11}{'redundant':>11}{'UNCACHEABLE':>13}")
    print("-" * 52)
    rows = [(s, *total[s]) for s in STAGES if s in total]
    rows.sort(key=lambda r: -(r[3] / r[1] if r[1] else 0))
    for stage, inp, red, unc in rows:
        print(f"{stage:<17}{inp:>11,}{red/inp*100:10.1f}%{unc/inp*100:12.1f}%")
    gi = sum(r[1] for r in rows); gr = sum(r[2] for r in rows); gu = sum(r[3] for r in rows)
    print("-" * 52)
    print(f"{'ALL':<17}{gi:>11,}{gr/gi*100:10.1f}%{gu/gi*100:12.1f}%")
    print(f"\nShare of all input tokens, by stage:")
    for stage, inp, red, unc in sorted(rows, key=lambda r: -r[1]):
        print(f"  {stage:<17}{inp/gi*100:5.1f}%  of which {unc/inp*100:.0f}% is stranded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
