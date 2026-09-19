"""Run the full analysis over one or two traces and print the tables."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tokenomics.aggregate import (  # noqa: E402
    stage_shares, type_shares, stage_type_shares, calls_per_stage,
)
from tokenomics.phases import PAPER_STAGE_SHARE, PAPER_TYPE_SHARE  # noqa: E402
from tokenomics.redundancy import analyse_run  # noqa: E402
from tokenomics.tokenize import get_tokenizer  # noqa: E402
from tokenomics.trace import group_by_run, read_trace  # noqa: E402


def hr(title: str) -> None:
    print(f"\n{title}\n" + "-" * len(title))


def report(path: str, tokenizer: str, basis: str, compare_paper: bool) -> dict:
    records = read_trace(path)
    model = records[0].model
    runs = len({r.run_id for r in records})

    print("=" * 68)
    print(f"{path}")
    print(f"model={model}  runs={runs}  calls={len(records)}  basis={basis}")
    print("=" * 68)

    hr("Stage share of tokens (mean over runs where the stage ran)")
    for s in stage_shares(records, basis=basis):
        line = str(s)
        if compare_paper and s.stage in PAPER_STAGE_SHARE:
            delta = s.mean_share - PAPER_STAGE_SHARE[s.stage]
            line += f"   paper {PAPER_STAGE_SHARE[s.stage]*100:5.1f}%  delta {delta*100:+5.1f}pp"
        print(line)

    hr("Token type split (input/output only - cross-model comparable)")
    ts = type_shares(records, include_reasoning=False)
    for k, v in ts.items():
        print(f"{k:<10} {v*100:5.1f}%")

    hr("Token type split including reasoning (NOT cross-model comparable)")
    tsr = type_shares(records, include_reasoning=True)
    for k, v in tsr.items():
        extra = f"   paper {PAPER_TYPE_SHARE[k]*100:5.1f}%" if compare_paper else ""
        print(f"{k:<10} {v*100:5.1f}%{extra}")

    hr("Per-stage input share")
    for stage, d in sorted(stage_type_shares(records).items(), key=lambda kv: -kv[1]["input"]):
        print(f"{stage:<16} input {d['input']*100:5.1f}%   output {d['output']*100:5.1f}%")

    hr("Calls per stage")
    for stage, n in sorted(calls_per_stage(records).items(), key=lambda kv: -kv[1]):
        print(f"{stage:<16} {n}")

    hr("CONTEXT REDUNDANCY  (the part that is not a replication)")
    tok = get_tokenizer(tokenizer)
    results = [analyse_run(calls, tokenizer=tok) for _, calls in group_by_run(records)]
    print(f"tokenizer = {tok.name}\n")
    print(f"{'run':<24}{'exact':>9}{'near':>9}{'cacheable':>11}{'uncacheable':>13}")
    for r in results:
        print(f"{r.run_id:<24}{r.exact_redundancy*100:8.1f}%{r.near_redundancy*100:8.1f}%"
              f"{r.cacheable_redundancy*100:10.1f}%{r.uncacheable_redundancy*100:12.1f}%")
    summary = {
        "model": model,
        "exact": mean(r.exact_redundancy for r in results),
        "near": mean(r.near_redundancy for r in results),
        "cacheable": mean(r.cacheable_redundancy for r in results),
        "uncacheable": mean(r.uncacheable_redundancy for r in results),
        "input_share": ts["input"],
    }
    print("-" * 66)
    print(f"{'MEAN':<24}{summary['exact']*100:8.1f}%{summary['near']*100:8.1f}%"
          f"{summary['cacheable']*100:10.1f}%{summary['uncacheable']*100:12.1f}%")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("traces", nargs="+")
    ap.add_argument("--tokenizer", default="auto")
    ap.add_argument("--basis", default="billable", choices=["billable", "total"])
    ap.add_argument("--compare-paper", action="store_true")
    args = ap.parse_args()

    summaries = [report(t, args.tokenizer, args.basis, args.compare_paper) for t in args.traces]

    if len(summaries) > 1:
        print("\n" + "=" * 68)
        print("CROSS-MODEL COMPARISON  (input+output basis)")
        print("=" * 68)
        print(f"{'model':<26}{'input%':>9}{'exact':>9}{'near':>9}{'cacheable':>11}")
        for s in summaries:
            print(f"{s['model']:<26}{s['input_share']*100:8.1f}%{s['exact']*100:8.1f}%"
                  f"{s['near']*100:8.1f}%{s['cacheable']*100:10.1f}%")
        print("\nNOTE: different tokenizers -> compare shares only, never raw counts.")


if __name__ == "__main__":
    main()
