"""Build a cache-friendly variant of ChatDev's phase prompts.

THE INTERVENTION
----------------
Every ChatDev phase prompt is assembled volatile-first:

    Task: "{task}"          <- changes per task
    Codes: "{codes}"        <- changes every review round
    <long static instruction, rules, worked examples>

Because a provider prefix cache matches from token zero and stops at the first
difference, the static block at the end is re-billed at full rate on every
call, however many times it has been sent before. In `Manual` that block is
~1,400 characters of example README; in `Coding` ~940; in `CodeReviewComment`
~800.

This script emits the same prompts with the two halves swapped: static
instruction first, volatile content last. No wording is added or removed.

WHAT IS TREATED AS STABLE
-------------------------
`{assistant_role}` is fixed within a phase, so it does not break a prefix and
counts as stable. Everything else -- task, codes, ideas, modality, language,
requirements, test reports, error summaries -- is volatile.

THE ONE UNAVOIDABLE EDIT
------------------------
Several instructions say "listed above" or "the above regulations", referring
to content that is now below them. Leaving those in place would make the
prompt incoherent and would confound a quality comparison, so directional words
are flipped. These are the only text changes, and every one is logged.
"""
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VOLATILE = {
    "task", "codes", "ideas", "modality", "language", "requirements",
    "test_reports", "error_summary", "comments", "images", "gui",
    "unimplemented_file",
}
PH = re.compile(r"\{(\w+)\}")

# directional fixes, applied only to the block being moved to the front
DIRECTION = [
    (re.compile(r"\blisted above\b", re.I), "listed below"),
    (re.compile(r"\bthe above regulations\b", re.I), "the regulations above"),
    (re.compile(r"\babove\b(?! regulations)", re.I), "below"),
    (re.compile(r"\bAccording to the codes and file format listed below\b", re.I),
     "According to the codes and file format listed below"),
]


def is_volatile(line: str) -> bool:
    return any(p in VOLATILE for p in PH.findall(line))


def reorder(lines: list[str], log: list[str], phase: str) -> list[str]:
    idx = [i for i, l in enumerate(lines) if is_volatile(l)]
    if not idx:
        return lines
    last = max(idx)
    head, tail = lines[: last + 1], lines[last + 1:]
    if not tail:
        return lines

    fixed = []
    for line in tail:
        original = line
        for pat, rep in DIRECTION:
            line = pat.sub(rep, line)
        if line != original:
            log.append(f"  [{phase}] {original.strip()[:70]!r} -> {line.strip()[:70]!r}")
        fixed.append(line)

    return fixed + head


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT / "vendor/ChatDev1x/CompanyConfig/Default/PhaseConfig.json"))
    ap.add_argument("--out", default=str(ROOT / "vendor/ChatDev1x/CompanyConfig/Reordered"))
    args = ap.parse_args()

    src = Path(args.src)
    cfg = json.loads(src.read_text())
    log: list[str] = []
    moved = 0

    for phase, body in cfg.items():
        prompt = body.get("phase_prompt")
        if not prompt:
            continue
        new = reorder(prompt, log, phase)
        if new != prompt:
            moved += 1
            body["phase_prompt"] = new

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "PhaseConfig.json").write_text(json.dumps(cfg, indent=4, ensure_ascii=False))

    # the other two configs are copied unchanged so the folder is a drop-in
    for name in ("ChatChainConfig.json", "RoleConfig.json"):
        s = src.parent / name
        if s.exists():
            (outdir / name).write_text(s.read_text())

    # verify nothing was lost: the multiset of lines must be identical
    orig = json.loads(src.read_text())
    for phase, body in cfg.items():
        a = sorted(orig[phase].get("phase_prompt", []))
        b = sorted(l for l in body.get("phase_prompt", []))
        if len(a) != len(b):
            print(f"!! {phase}: line count changed {len(a)} -> {len(b)}")
            return 1

    print(f"reordered {moved} phases -> {outdir}/PhaseConfig.json")
    print(f"directional edits: {len(log)}")
    for l in log:
        print(l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
