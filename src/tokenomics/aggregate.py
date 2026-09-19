"""Per-stage and per-type aggregation, reproducing the paper's tables.

Two deliberate choices, both of which change the numbers:

1. The paper averages a stage's share over the tasks in which that stage
   actually ran, not over all 30. Code Completion ran in 6 tasks and Testing in
   12, which is why 59.4 + 26.8 + 20.1 + 10.3 + 8.6 + 2.4 does not sum to 100.
   We reproduce that convention in `stage_shares(...)` and expose the honest
   all-task version in `stage_shares(..., over_all_runs=True)` alongside it.

2. Every cross-model figure is computed on input+output only, because
   reasoning tokens are not comparable between GPT-5 and Claude. Use
   `basis="billable"` for anything that appears in a model-vs-model claim and
   `basis="total"` only when reproducing the paper's own GPT-5 numbers.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Literal, Sequence

from .phases import STAGES, stage_for
from .trace import CallRecord, group_by_run

Basis = Literal["total", "billable"]


def _tokens(call: CallRecord, basis: Basis) -> int:
    return call.total_tokens if basis == "total" else call.billable_tokens


@dataclass
class StageShare:
    stage: str
    mean_share: float
    sd_share: float
    n_runs: int       # runs in which the stage ran at all
    total_runs: int

    def __str__(self) -> str:
        return (
            f"{self.stage:<16} {self.mean_share*100:5.1f}%  "
            f"(sd {self.sd_share*100:4.1f}, n={self.n_runs}/{self.total_runs})"
        )


def stage_shares(
    records: Sequence[CallRecord],
    basis: Basis = "billable",
    over_all_runs: bool = False,
) -> list[StageShare]:
    """Share of a run's tokens spent in each stage, averaged across runs."""
    per_run: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    run_totals: dict[str, int] = defaultdict(int)

    for run_id, calls in group_by_run(records):
        for c in calls:
            n = _tokens(c, basis)
            per_run[run_id][stage_for(c.phase)] += n
            run_totals[run_id] += n

    total_runs = len(per_run)
    out: list[StageShare] = []
    for stage in STAGES:
        shares = []
        for run_id, stages in per_run.items():
            if run_totals[run_id] == 0:
                continue
            if stage in stages:
                shares.append(stages[stage] / run_totals[run_id])
            elif over_all_runs:
                shares.append(0.0)
        n_present = sum(1 for s in per_run.values() if stage in s)
        out.append(
            StageShare(
                stage=stage,
                mean_share=mean(shares) if shares else 0.0,
                sd_share=pstdev(shares) if len(shares) > 1 else 0.0,
                n_runs=n_present,
                total_runs=total_runs,
            )
        )
    out.sort(key=lambda s: s.mean_share, reverse=True)
    return out


def type_shares(records: Sequence[CallRecord], include_reasoning: bool = False) -> dict[str, float]:
    """Input / output (/ reasoning) share of consumption, averaged per run.

    include_reasoning=True reproduces the paper's GPT-5 split and must NOT be
    used for a cross-model comparison.
    """
    keys = ("input", "output", "reasoning") if include_reasoning else ("input", "output")
    per_run: list[dict[str, float]] = []

    for _, calls in group_by_run(records):
        # completion_tokens includes reasoning_tokens, so the denominator is
        # input + completion, and visible output is completion - reasoning.
        sums = {
            "input": sum(c.input_tokens for c in calls),
            "output": sum((c.visible_output_tokens if include_reasoning
                           else c.output_tokens) for c in calls),
            "reasoning": sum(c.reasoning_tokens for c in calls),
        }
        denom = sum(c.billable_tokens for c in calls)
        if denom:
            per_run.append({k: sums[k] / denom for k in keys})

    return {k: (mean(r[k] for r in per_run) if per_run else 0.0) for k in keys}


def stage_type_shares(
    records: Sequence[CallRecord], include_reasoning: bool = False
) -> dict[str, dict[str, float]]:
    keys = ("input", "output", "reasoning") if include_reasoning else ("input", "output")
    acc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for c in records:
        s = stage_for(c.phase)
        acc[s]["input"] += c.input_tokens
        acc[s]["output"] += (c.visible_output_tokens if include_reasoning
                             else c.output_tokens)
        acc[s]["reasoning"] += c.reasoning_tokens
        acc[s]["_denom"] += c.billable_tokens

    out: dict[str, dict[str, float]] = {}
    for stage, sums in acc.items():
        denom = sums["_denom"]
        if denom:
            out[stage] = {k: sums[k] / denom for k in keys}
    return out


def calls_per_stage(records: Sequence[CallRecord]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for c in records:
        counts[stage_for(c.phase)] += 1
    return dict(counts)
