"""Trace schema: one record per LLM call.

Everything downstream reads this and only this, so a new provider or a new
agent framework only has to emit these records.

Why the fields are what they are
--------------------------------
`input_tokens` / `output_tokens` are reported by every provider and are
comparable in *share* terms across models. `reasoning_tokens` is NOT
comparable: GPT-5 bills a separate reasoning field, Claude's extended thinking
is accounted differently, and a model without hidden reasoning reports zero.
We therefore carry it, but every cross-model figure must be computed on
input/output only. `token_basis` records which tokenizer produced the counts so
that a reader can never mistake two models' raw totals for like-for-like.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

SCHEMA_VERSION = 1


@dataclass
class Message:
    """One message in a prompt. `content` is kept verbatim: the redundancy
    analysis needs the exact bytes that were sent."""
    role: str
    content: str


@dataclass
class CallRecord:
    run_id: str            # one agent run over one task
    task_id: str           # e.g. "ProgramDev/chess"
    call_index: int        # 0-based, ordered within the run
    phase: str             # ChatDev internal phase name
    model: str             # e.g. "gpt-5-2025-08-07", "claude-opus-5"
    provider: str          # "openai" | "anthropic"
    messages: list[Message]
    response_text: str
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int = 0
    cached_input_tokens: int = 0   # provider-reported cache hits, if any
    token_basis: str = "provider"  # "provider" | "tiktoken:<enc>" | "heuristic"
    wall_ms: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Input + output.

        NOT input + output + reasoning. Providers report ``completion_tokens``
        INCLUSIVE of reasoning tokens, so adding reasoning again double-counts
        it. This was verified against the authors' own published traces: under
        the double-counting convention we got input 45.1 / output 37.8 /
        reasoning 17.1, against their published 53.9 / 24.4 / 21.6; under this
        one we get 54.4 / 25.0 / 20.6, all within about a point.
        """
        return self.input_tokens + self.output_tokens

    @property
    def visible_output_tokens(self) -> int:
        """Output the user actually sees: completion minus hidden reasoning."""
        return max(0, self.output_tokens - self.reasoning_tokens)

    @property
    def billable_tokens(self) -> int:
        """Input + output. The cross-model comparable quantity."""
        return self.input_tokens + self.output_tokens

    def prompt_text(self) -> str:
        return "\n".join(m.content for m in self.messages)


def write_trace(path: str | Path, records: Iterable[CallRecord]) -> int:
    """Write records as JSONL. Returns the number written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"_schema": SCHEMA_VERSION}) + "\n")
        for r in records:
            fh.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
            n += 1
    return n


def read_trace(path: str | Path) -> list[CallRecord]:
    records: list[CallRecord] = []
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "_schema" in obj:
                if obj["_schema"] != SCHEMA_VERSION:
                    raise ValueError(
                        f"trace schema v{obj['_schema']}, expected v{SCHEMA_VERSION}"
                    )
                continue
            obj["messages"] = [Message(**m) for m in obj["messages"]]
            records.append(CallRecord(**obj))
    records.sort(key=lambda r: (r.run_id, r.call_index))
    return records


def group_by_run(records: Sequence[CallRecord]) -> Iterator[tuple[str, list[CallRecord]]]:
    current: list[CallRecord] = []
    key: str | None = None
    for r in records:
        if r.run_id != key:
            if current:
                yield key, current  # type: ignore[misc]
            key, current = r.run_id, []
        current.append(r)
    if current:
        yield key, current  # type: ignore[misc]
