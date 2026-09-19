"""Run the ProgramDev corpus, one ChatDev process per task.

Each task runs in its OWN subprocess. ChatDev keeps global state and the
recorder patches a module-level function, so running several tasks inside one
interpreter would let one task's context leak into the next and quietly
corrupt the redundancy measure -- the very thing this study reports.

Resumable: a task whose trace already exists is skipped, so you can stop this
at any point and start it again.

    python3 scripts/run_all.py --model qwen2.5-coder:7b \
        --base-url http://localhost:11434/v1 --api-key ollama --limit 10
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", name) or "task"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--dataset", default=str(ROOT / "data" / "programdev_dataset.json"))
    ap.add_argument("--limit", type=int, default=0, help="0 = all 30")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=1800, help="seconds per task")
    ap.add_argument("--repeat", type=int, default=1, help="runs per task, for variance")
    args = ap.parse_args()

    tasks = json.loads(Path(args.dataset).read_text())
    tasks = tasks[args.start:]
    if args.limit:
        tasks = tasks[: args.limit]

    tag = args.model.replace("/", "_").replace(":", "-")
    trace_dir = ROOT / "data" / "traces"
    trace_dir.mkdir(parents=True, exist_ok=True)

    total = len(tasks) * args.repeat
    done = skipped = failed = 0
    t0 = time.time()

    for rep in range(args.repeat):
        for i, t in enumerate(tasks):
            name = slug(t["project_name"])
            run_name = name if args.repeat == 1 else f"{name}_r{rep}"
            out = trace_dir / f"{run_name}__{tag}.jsonl"

            if out.exists() and out.stat().st_size > 200:
                skipped += 1
                print(f"[{done+skipped+failed}/{total}] skip {run_name} (already have a trace)")
                continue

            cmd = [
                sys.executable, str(ROOT / "scripts" / "run_task.py"),
                "--task", t["description"], "--name", run_name,
                "--model", args.model, "--base-url", args.base_url,
                "--out", str(out),
            ]
            if args.api_key:
                cmd += ["--api-key", args.api_key]

            print(f"\n[{done+skipped+failed+1}/{total}] {run_name}: {t['description'][:70]}")
            started = time.time()
            try:
                r = subprocess.run(cmd, timeout=args.timeout,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                if r.returncode == 0 and out.exists():
                    n = sum(1 for _ in out.open()) - 1
                    done += 1
                    print(f"      ok  {n} calls  {time.time()-started:.0f}s")
                else:
                    failed += 1
                    tail = (r.stderr or b"").decode(errors="replace").strip().splitlines()[-2:]
                    print(f"      FAILED rc={r.returncode}  {' | '.join(tail)[:180]}")
                    out.unlink(missing_ok=True)   # never leave a partial trace behind
            except subprocess.TimeoutExpired:
                failed += 1
                print(f"      TIMEOUT after {args.timeout}s")
                out.unlink(missing_ok=True)

    mins = (time.time() - t0) / 60
    print(f"\ndone={done} skipped={skipped} failed={failed}  elapsed={mins:.1f} min")
    print(f"\nanalyse with:\n  python3 scripts/analyze.py data/traces/*__{tag}.jsonl --tokenizer strict --compare-paper")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
