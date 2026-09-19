"""Ten-second check: can ChatDev's 2023 OpenAI client talk to Anthropic?

ChatDev 1.x pins openai==0.27.8, which predates the modern SDK. Anthropic
publishes an OpenAI-compatible endpoint, but compatibility with a client this
old is not guaranteed. This script answers that before any real work.

    export ANTHROPIC_API_KEY=sk-ant-...
    python3 scripts/check_endpoint.py
"""
from __future__ import annotations

import os
import sys

BASE = "https://api.anthropic.com/v1"
MODEL = os.environ.get("TOKENOMICS_MODEL", "claude-opus-4-1")


def main() -> int:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("ANTHROPIC_API_KEY is not set. Nothing was called, nothing was charged.")
        return 2

    try:
        import openai
    except ImportError:
        print("openai package not installed in this interpreter.")
        return 2

    version = getattr(openai, "__version__", "unknown")
    print(f"openai client version: {version}")
    print(f"endpoint: {BASE}\nmodel:    {MODEL}\n")

    if not hasattr(openai, "ChatCompletion"):
        print("FAIL: this is the modern SDK; ChatDev needs openai==0.27.8.")
        return 1

    openai.api_key = key
    openai.api_base = BASE

    try:
        r = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=16,
        )
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}")
        print("\nIf this is an auth or header error, the legacy client cannot")
        print("speak to Anthropic and we need a shim or a different route.")
        return 1

    usage = r.get("usage", {})
    print("SUCCESS")
    print("  reply :", r["choices"][0]["message"]["content"].strip())
    print("  usage :", dict(usage))
    missing = [k for k in ("prompt_tokens", "completion_tokens") if k not in usage]
    if missing:
        print(f"  WARNING: usage is missing {missing} -- the recorder needs these.")
        return 1
    print("\nGood: prompt_tokens and completion_tokens are reported, so the")
    print("recorder can capture real counts. Cost of this check: a few tokens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
