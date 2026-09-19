"""Record every ChatDev LLM call without editing a line of ChatDev.

Why a monkey patch and not a fork
---------------------------------
The single biggest threat to this study is that our own instrumentation
changes the prompts, so that a model-to-model difference is really a
difference between our two adapters. ChatDev 1.x funnels every call through
one place -- ``openai.ChatCompletion.create`` in ``camel/model_backend.py`` --
so we wrap that function, copy what passes through, and hand the arguments on
untouched. ChatDev's source tree stays byte-identical to the upstream fork,
which is a claim we can demonstrate with ``git status`` rather than assert.

Usage (before ChatDev's run.py does any work):

    from tokenomics.record import install
    install(out_path="data/traces/run.jsonl", model="claude-opus-5",
            provider="anthropic")

The phase name is recovered from the call stack: ChatDev carries ``phase_name``
on the Phase object that drives each call. If it cannot be found the call is
recorded as ``Unknown`` rather than guessed, and the analysis will refuse it.
"""

from __future__ import annotations

import atexit
import inspect
import json
import threading
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .trace import SCHEMA_VERSION, CallRecord, Message

_lock = threading.Lock()
_state: dict[str, Any] = {"fh": None, "n": 0, "unknown": 0}


def _current_phase() -> str:
    """Walk the stack for ChatDev's phase name.

    Checked in order of reliability: an explicit ``phase_name`` attribute on a
    bound ``self``, then a local variable of the same name, then the class name
    of a Phase subclass.
    """
    for frame_info in inspect.stack()[2:]:
        loc = frame_info.frame.f_locals
        obj = loc.get("self")
        if obj is not None:
            name = getattr(obj, "phase_name", None)
            if isinstance(name, str) and name:
                return name
        name = loc.get("phase_name")
        if isinstance(name, str) and name:
            return name
        if obj is not None:
            cls = type(obj).__name__
            if cls not in ("ModelBackend", "OpenAIModel", "ChatAgent", "RolePlaying"):
                base_names = {b.__name__ for b in type(obj).__mro__}
                if "Phase" in base_names:
                    return cls
    return "Unknown"


def install(
    out_path: str | Path,
    model: str,
    provider: str,
    run_id: str | None = None,
    task_id: str = "unknown",
    wire_model: str | None = None,
) -> None:
    """Record every call; optionally rewrite the model name on the wire.

    `wire_model` exists so that ChatDev's source tree never has to be edited.
    ChatDev 1.x keeps a hardcoded ``num_max_token_map`` of GPT-3.5/GPT-4 names
    inside ``OpenAIModel.run`` and raises KeyError on anything else. Rather
    than patch that table -- and then have to argue that the patch changed
    nothing -- we let ChatDev believe it is calling ``gpt-4`` and substitute
    the real model name in the outgoing request. The message list is passed
    through untouched, so prompts are byte-identical by construction.

    THREAT, to be stated in the write-up: ChatDev sizes ``max_tokens`` from
    gpt-4's 8192-token window. If the target model has a different context
    window, the cap differs from what a native integration would set. This
    affects how much a model is *allowed* to emit, not what it is asked.
    """
    import openai  # imported here so the patch applies to the same module object

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fh = out_path.open("w", encoding="utf-8")
    fh.write(json.dumps({"_schema": SCHEMA_VERSION}) + "\n")
    _state["fh"] = fh

    run = run_id or f"{model}:{task_id}"
    original = openai.ChatCompletion.create

    def patched(*args: Any, **kwargs: Any) -> Any:
        if wire_model:
            kwargs = {**kwargs, "model": wire_model}  # name only; messages untouched
        response = original(*args, **kwargs)
        try:
            _write(run, task_id, model, provider, kwargs, response)
        except Exception as exc:                       # never break a paid run
            print(f"[tokenomics] record failed: {exc!r}")
        return response

    patched._tokenomics_original = original  # type: ignore[attr-defined]
    openai.ChatCompletion.create = patched
    atexit.register(_close)
    note = f" wire={wire_model}" if wire_model else ""
    print(f"[tokenomics] recording -> {out_path}  (model={model}{note})")


def _write(run, task_id, model, provider, kwargs, response) -> None:
    usage = response.get("usage", {}) or {}
    details = usage.get("completion_tokens_details", {}) or {}
    choices = response.get("choices", [{}]) or [{}]
    text = (choices[0].get("message", {}) or {}).get("content", "") or ""

    phase = _current_phase()
    with _lock:
        if phase == "Unknown":
            _state["unknown"] += 1
        rec = CallRecord(
            run_id=run,
            task_id=task_id,
            call_index=_state["n"],
            phase=phase,
            model=model,
            provider=provider,
            messages=[
                Message(role=m.get("role", "user"), content=m.get("content", "") or "")
                for m in kwargs.get("messages", [])
            ],
            response_text=text,
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
            reasoning_tokens=int(details.get("reasoning_tokens", 0)),
            cached_input_tokens=int(
                (usage.get("prompt_tokens_details", {}) or {}).get("cached_tokens", 0)
            ),
            token_basis="provider",
            meta={"wire_model": kwargs.get("model")},
        )
        _state["fh"].write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
        _state["fh"].flush()
        _state["n"] += 1


def _close() -> None:
    fh = _state.get("fh")
    if fh and not fh.closed:
        fh.close()
        msg = f"[tokenomics] wrote {_state['n']} call records"
        if _state["unknown"]:
            msg += f"  ({_state['unknown']} with phase=Unknown -- investigate before analysing)"
        print(msg)
