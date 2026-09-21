"""Run ONE ChatDev task against any OpenAI-compatible endpoint and record it.

ChatDev's own source is never modified. We install the recorder first, which
wraps openai.ChatCompletion.create, then hand control to ChatDev unchanged.

Ollama (free, local):
    ollama serve &
    ollama pull qwen2.5-coder:7b
    python3 scripts/run_task.py --task "Design a basic Gomoku game." \
        --name gomoku --model qwen2.5-coder:7b \
        --base-url http://localhost:11434/v1 --api-key ollama

Anthropic (paid):
    export ANTHROPIC_API_KEY=...
    python3 scripts/run_task.py --task "Design a basic Gomoku game." \
        --name gomoku --model claude-opus-4-1 \
        --base-url https://api.anthropic.com/v1
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, help="the software task prompt")
    ap.add_argument("--name", required=True, help="short project name, no spaces")
    ap.add_argument("--model", required=True, help="real model name sent on the wire")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--api-key", default=None, help="defaults to ANTHROPIC_API_KEY")
    ap.add_argument("--out", default=None)
    ap.add_argument("--chatdev", default=str(ROOT / "vendor" / "ChatDev1x"))
    ap.add_argument("--config", default="Default",
                    help="CompanyConfig folder: Default, or Reordered for the "
                         "cache-friendly prompt ordering (scripts/reorder_prompts.py)")
    args = ap.parse_args()

    key = args.api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        print("No API key. Pass --api-key or set ANTHROPIC_API_KEY.")
        return 2

    chatdev = Path(args.chatdev)
    if not (chatdev / "run.py").exists():
        print(f"ChatDev not found at {chatdev}")
        return 2

    out = Path(args.out or ROOT / "data" / "traces" / f"{args.name}__{args.model.replace('/','_').replace(':','-')}.jsonl")

    # ChatDev validates the key by reading the environment directly
    # (camel/utils.py: openai_api_key_required), so setting it on the client
    # object alone is not enough. Set both.
    os.environ["OPENAI_API_KEY"] = key

    import openai
    openai.api_key = key
    openai.api_base = args.base_url

    from tokenomics.record import install
    install(
        out_path=out,
        model=args.model,
        provider="anthropic" if "anthropic" in args.base_url else "openai-compatible",
        run_id=f"{args.model}:{args.name}",
        task_id=args.name,
        wire_model=args.model,          # ChatDev still thinks it is calling gpt-4
    )

    # Hand over to ChatDev, unmodified. GPT_4 keeps its token bookkeeping valid.
    sys.path.insert(0, str(chatdev))
    os.chdir(chatdev)
    sys.argv = ["run.py", "--task", args.task, "--name", args.name,
                "--model", "GPT_4", "--config", args.config]

    print(f"[runner] endpoint={args.base_url}  wire model={args.model}  config={args.config}")
    print(f"[runner] task={args.task!r}\n")

    import runpy
    try:
        runpy.run_path("run.py", run_name="__main__")
    except SystemExit as e:
        if e.code not in (0, None):
            print(f"[runner] ChatDev exited with {e.code}")
            return int(e.code)
    print(f"\n[runner] trace written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
