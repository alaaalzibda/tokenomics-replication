"""Generate a synthetic ChatDev-shaped trace.

Purpose: let the whole analysis pipeline be exercised, reviewed and unit-tested
before a single paid API call is made. These numbers are NOT results and must
never appear in the write-up. The generator deliberately mimics the one
structural feature that matters for the redundancy analysis: on each review
round the agent re-sends the entire current source file with a few lines
changed, on top of a fixed system preamble.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tokenomics.trace import CallRecord, Message, write_trace  # noqa: E402

PREAMBLE = (
    "You are a senior software engineer working inside a virtual software company.\n"
    "Follow the company's architecture rules at all times. Be concise and precise.\n"
    "Never invent APIs. Always return complete, runnable files.\n"
) * 4

def source_file(version: int, lines: int = 90) -> str:
    body = []
    for i in range(lines):
        if version and i % 29 == version % 29:
            body.append(f"    value_{i} = compute_{i}(x) + {version}  # revised r{version}")
        else:
            body.append(f"    value_{i} = compute_{i}(x)")
    return "def main(x):\n" + "\n".join(body) + "\n    return value_0\n"


PHASE_PLAN = [
    ("DemandAnalysis", 1), ("LanguageChoose", 1),
    ("Coding", 1),
    ("CodeReviewComment", 4), ("CodeReviewModification", 4),
    ("Test", 2), ("TestModification", 1),
    ("EnvironmentDoc", 1), ("Manual", 1),
]


def build_run(run_id: str, task_id: str, model: str, provider: str, rng: random.Random):
    records, idx, version = [], 0, 0
    for phase, repeats in PHASE_PLAN:
        for _ in range(repeats):
            if phase == "CodeReviewModification":
                version += 1
            src = source_file(version)
            msgs = [Message("system", PREAMBLE)]
            if phase not in ("DemandAnalysis", "LanguageChoose"):
                msgs.append(Message("user", f"Current implementation:\n\n{src}"))
            msgs.append(Message("user", f"[{phase}] Task: {task_id}. Proceed."))
            prompt_chars = sum(len(m.content) for m in msgs)
            inp = prompt_chars // 4
            out = rng.randint(200, 1400)
            reasoning = rng.randint(300, 2600) if provider == "openai" else 0
            records.append(CallRecord(
                run_id=run_id, task_id=task_id, call_index=idx, phase=phase,
                model=model, provider=provider, messages=msgs,
                response_text="<synthetic>", input_tokens=inp, output_tokens=out,
                reasoning_tokens=reasoning, token_basis="heuristic",
                meta={"synthetic": True},
            ))
            idx += 1
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/traces/sample_synthetic.jsonl")
    ap.add_argument("--tasks", type=int, default=6)
    ap.add_argument("--model", default="gpt-5-2025-08-07")
    ap.add_argument("--provider", default="openai", choices=["openai", "anthropic"])
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    all_records = []
    for t in range(args.tasks):
        task = f"ProgramDev/task_{t:02d}"
        all_records += build_run(f"{args.model}:{t:02d}", task, args.model, args.provider, rng)

    n = write_trace(args.out, all_records)
    print(f"wrote {n} synthetic call records -> {args.out}")


if __name__ == "__main__":
    main()
