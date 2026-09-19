"""Pool every trace for a model and report mean +/- sd across tasks.

analyze.py reports one trace at a time, which is right for inspecting a single
run and wrong for saying anything general. This pools them.
"""
from __future__ import annotations

import argparse, glob, sys
from pathlib import Path
from statistics import mean, pstdev

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tokenomics.aggregate import stage_shares, type_shares          # noqa: E402
from tokenomics.phases import PAPER_STAGE_SHARE, STAGES             # noqa: E402
from tokenomics.shingle import analyse_run                          # noqa: E402
from tokenomics.tokenize import get_tokenizer                       # noqa: E402
from tokenomics.trace import read_trace                             # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("--tokenizer", default="auto")
    args = ap.parse_args()

    files = sorted(glob.glob(args.pattern))
    if not files:
        print("no traces matched"); return 2

    tok = get_tokenizer(args.tokenizer)
    all_records, per_task, red = [], [], []

    for f in files:
        recs = read_trace(f)
        if not recs:
            continue
        all_records += recs
        per_task.append((Path(f).name.split("__")[0], recs))
        red.append(analyse_run(recs, tokenizer=tok))

    model = all_records[0].model
    print("=" * 74)
    print(f"POOLED  model={model}  tasks={len(per_task)}  calls={len(all_records)}")
    print(f"tokenizer={tok.name}")
    print("=" * 74)

    print("\nStage share of tokens, mean over tasks where the stage ran")
    print("-" * 74)
    print(f"{'stage':<17}{'mean':>8}{'sd':>7}{'min':>7}{'max':>7}   {'n':>5}   paper")
    for stage in STAGES:
        vals = []
        for _, recs in per_task:
            s = {x.stage: x.mean_share for x in stage_shares(recs, basis='billable')}
            if s.get(stage, 0) > 0:
                vals.append(s[stage])
        p = PAPER_STAGE_SHARE.get(stage, 0) * 100
        if vals:
            print(f"{stage:<17}{mean(vals)*100:7.1f}%{pstdev(vals)*100:6.1f}"
                  f"{min(vals)*100:6.1f}{max(vals)*100:7.1f}   {len(vals):>2}/{len(per_task):<2}  {p:5.1f}%")
        else:
            print(f"{stage:<17}{'--':>8}{'':>7}{'':>7}{'':>7}    0/{len(per_task):<2}  {p:5.1f}%")

    print("\nToken type split (input+output, cross-model comparable)")
    print("-" * 74)
    ins = []
    for _, recs in per_task:
        ins.append(type_shares(recs)["input"])
    print(f"input       {mean(ins)*100:5.1f}%  (sd {pstdev(ins)*100:.1f}, "
          f"range {min(ins)*100:.1f}-{max(ins)*100:.1f})    paper 53.9%")

    print("\nCONTEXT REDUNDANCY across tasks")
    print("-" * 74)
    print(f"{'task':<22}{'redundant':>11}{'cacheable':>11}{'UNCACHEABLE':>13}")
    for (name, _), r in zip(per_task, red):
        print(f"{name:<22}{r.redundancy*100:10.1f}%{r.cacheable*100:10.1f}%{r.uncacheable*100:12.1f}%")
    for label, f in (("MEAN", mean), ("SD", pstdev)):
        print(f"{label:<22}{f([r.redundancy for r in red])*100:10.1f}%"
              f"{f([r.cacheable for r in red])*100:10.1f}%"
              f"{f([r.uncacheable for r in red])*100:12.1f}%")
    print(f"{'MIN':<22}{min(r.redundancy for r in red)*100:10.1f}%"
          f"{min(r.cacheable for r in red)*100:10.1f}%"
          f"{min(r.uncacheable for r in red)*100:12.1f}%")
    print(f"{'MAX':<22}{max(r.redundancy for r in red)*100:10.1f}%"
          f"{max(r.cacheable for r in red)*100:10.1f}%"
          f"{max(r.uncacheable for r in red)*100:12.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
