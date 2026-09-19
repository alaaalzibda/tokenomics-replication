"""Validate our pipeline against the authors' own published traces.

The authors released the 30 ChatDev/GPT-5 execution traces on Zenodo
(record 17430187). Those logs carry, per LLM call, the phase that was running
and the provider-reported token counts. That is everything our stage
aggregation needs.

So this is a ground-truth test of our instrument: parse their traces with OUR
phase mapping and OUR aggregation, and see whether we land on the numbers they
published. If we do, the pipeline is validated against data we did not produce.
If we do not, we have a bug -- and we would rather find it here than in a
write-up.

It also converts the traces into our own schema, so the redundancy analyser can
later run over them (token counts only; these logs do not contain the verbatim
prompt arrays, so redundancy over them would need prompt reconstruction and is
NOT attempted here).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from statistics import mean, pstdev

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tokenomics.phases import (  # noqa: E402
    PAPER_STAGE_SHARE, PAPER_TYPE_SHARE, STAGES, UnknownPhase, stage_for,
)

# ChatDev marks the running phase two ways. The parameter table printed at the
# start of every chat is the reliable one; "execute SimplePhase:[X]" appears
# only for phases nested inside a ComposedPhase. A first version of this parser
# used only the latter and silently lost Design, Coding and Documentation --
# which is why the validation below is worth running at all.
RE_PHASE_TABLE = re.compile(r"\|\s*\*\*phase_name\*\*\s*\|\s*(\w+)\s*\|")
RE_PHASE_EXEC = re.compile(r"execute SimplePhase:\[(\w+)\]")
RE_USAGE = re.compile(r"\*\*\[OpenAI_Usage_Info Receive\]\*\*")
RE_NUM = re.compile(r"^(prompt_tokens|completion_tokens|total_tokens|reasoning_tokens):\s*(\d+)")


def parse_log(path: Path) -> list[dict]:
    """One dict per LLM call: phase + token counts, in order."""
    calls: list[dict] = []
    phase = None
    pending: dict | None = None

    for line in path.read_text(errors="replace").splitlines():
        m = RE_PHASE_TABLE.search(line) or RE_PHASE_EXEC.search(line)
        if m:
            phase = m.group(1)
            continue
        if RE_USAGE.search(line):
            pending = {"phase": phase or "Unknown"}
            continue
        if pending is not None:
            m = RE_NUM.match(line.strip())
            if m:
                pending[m.group(1)] = int(m.group(2))
                if len(pending) >= 5:          # phase + 4 counts
                    calls.append(pending)
                    pending = None
            elif line.strip() and not line.startswith("cost"):
                if len(pending) > 1:
                    calls.append(pending)
                pending = None
    return calls


def stage_totals(calls: list[dict], basis: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for c in calls:
        try:
            s = stage_for(c["phase"])
        except UnknownPhase:
            s = "UNMAPPED:" + c["phase"]
        # completion_tokens includes reasoning_tokens; never add it again.
        n = c.get("prompt_tokens", 0) + c.get("completion_tokens", 0)
        out[s] = out.get(s, 0) + n
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("traces_dir")
    ap.add_argument("--basis", default="total", choices=["total", "billable"],
                    help="total = input+output+reasoning, as the paper counts it")
    args = ap.parse_args()

    logs = sorted(Path(args.traces_dir).rglob("*.log"))
    if not logs:
        print("no .log files found"); return 2

    per_task, unmapped, all_calls = [], set(), []
    for lg in logs:
        calls = parse_log(lg)
        if not calls:
            continue
        all_calls += calls
        tot = stage_totals(calls, args.basis)
        for k in tot:
            if k.startswith("UNMAPPED:"):
                unmapped.add(k.split(":", 1)[1])
        denom = sum(tot.values())
        if denom:
            per_task.append({k: v / denom for k, v in tot.items()})

    print("=" * 76)
    print(f"VALIDATION against the authors' own traces")
    print(f"traces={len(per_task)}  calls={len(all_calls)}  basis={args.basis}")
    print("=" * 76)

    if unmapped:
        print(f"\n!! phases with no mapping: {sorted(unmapped)}\n")

    print(f"\n{'stage':<17}{'ours':>8}{'sd':>7}{'n':>7}   paper    delta")
    print("-" * 60)
    for stage in STAGES:
        vals = [t[stage] for t in per_task if stage in t and t[stage] > 0]
        p = PAPER_STAGE_SHARE.get(stage, 0)
        if vals:
            m = mean(vals)
            flag = "  <-- CHECK" if abs(m - p) > 0.03 else ""
            print(f"{stage:<17}{m*100:7.1f}%{pstdev(vals)*100:6.1f}"
                  f"{len(vals):>4}/{len(per_task):<2} {p*100:6.1f}%  {(m-p)*100:+6.1f}pp{flag}")
        else:
            print(f"{stage:<17}{'--':>8}{'':>7}{0:>4}/{len(per_task):<2} {p*100:6.1f}%")

    print(f"\n{'type':<17}{'ours':>8}{'':>7}{'':>7}   paper    delta")
    print("-" * 60)
    tot = {k: sum(c.get(k, 0) for c in all_calls)
           for k in ("prompt_tokens", "completion_tokens", "reasoning_tokens")}
    denom = sum(tot.values())
    denom = tot["prompt_tokens"] + tot["completion_tokens"]
    visible_out = tot["completion_tokens"] - tot["reasoning_tokens"]
    for label, val in (("input", tot["prompt_tokens"]), ("output", visible_out),
                       ("reasoning", tot["reasoning_tokens"])):
        m = val / denom if denom else 0
        p = PAPER_TYPE_SHARE[label]
        flag = "  <-- CHECK" if abs(m - p) > 0.03 else ""
        print(f"{label:<17}{m*100:7.1f}%{'':>7}{'':>7} {p*100:6.1f}%  {(m-p)*100:+6.1f}pp{flag}")

    r = [c.get("reasoning_tokens", 0) for c in all_calls]
    print(f"\nreasoning tokens per task: min {min(sum(1 for _ in [0]) and 0, 0) or ''}"
          f"{min(r)}  max {max(r)}  (paper reports 17,280-40,000 per TASK)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
