# Experiment: does prompt reordering move stranded tokens into the cache?

**Registered before the run.** Written and committed before any reordered
trace existed, so the prediction cannot be fitted to the result.

## Claim under test

ChatDev assembles every phase prompt volatile-first: task and codes at the top,
the long static instruction underneath. A provider prefix cache matches from
token zero and stops at the first difference, so that static block is billed at
full rate on every call no matter how many times it has been sent.

`scripts/reorder_prompts.py` emits the same prompts with the halves swapped:
static instruction first, volatile content last. No wording is added or
removed; the only edits are four directional words ("above" -> "below"), all
logged by the script, needed so the instructions still make sense.

## Prediction

Against the baseline arm (10 ProgramDev tasks, `qwen2.5-coder:7b`, Default
config):

1. **Total redundancy stays roughly flat.** The same text is sent either way,
   so the share of input that is repeated should not move much. Baseline 82.0%.
2. **The cacheable / uncacheable split shifts toward cacheable.** This is the
   whole point. Baseline uncacheable 36.5% of input; it should fall.
3. **The drop is largest where the static tail is largest.** Ranked by how much
   static text currently sits after the last volatile placeholder:
   `Manual` (~1,383 chars), `Coding` (~940), `CodeReviewComment` (~795).
   So the largest improvement should appear in **Documentation** (73.4%
   uncacheable at baseline), then **Code Review** (32.0%), then **Coding**
   (20.2%).
4. **Code Completion barely moves.** It is already only 7.4% uncacheable;
   there is little to recover.

**What would falsify this:** uncacheable staying flat or rising, or the
improvement appearing in stages with small static tails rather than large ones.

## Known confounds, stated in advance

* **Behaviour may change.** Reordering is not semantically neutral even though
  the content is identical; the model may review more or fewer rounds, which
  changes absolute token counts. Comparisons must therefore be on **shares**,
  not totals.
* **Single run per task, one model, one framework.** A difference of a few
  points is inside the noise this design can resolve.
* **The four directional edits** are a real, if small, change to the text.
* **No quality measurement.** Whether the reordered prompts produce equally
  good software is not tested here, and a cost win that degrades output is not
  a win. This is the obvious next experiment.

## What the script actually does, on six lines

A line counts as volatile if it contains a placeholder from a fixed list
(`task`, `codes`, `ideas`, `modality`, `language`, `requirements`, the
test-report names). `{assistant_role}` is the one exception, treated as stable
because it is fixed within a phase.

The script then finds the LAST volatile line, cuts there, and swaps the halves:

```
1  Task: {task}                          volatile
2  Language: {language}                  volatile
3  Codes: {codes}                        volatile   <- last volatile line
4  You are a reviewer.                   stable
5  Follow the coding standards below.    stable
6  Report bugs one per line.             stable
```

`head` = lines 1-3, `tail` = lines 4-6, and the output is `tail + head`:

```
1  You are a reviewer.
2  Follow the coding standards below.
3  Report bugs one per line.
4  Task: {task}
5  Language: {language}
6  Codes: {codes}
```

The failure is visible in that output. `{task}` and `{language}` render to the
same values on every call of the run, so they were the most widely shared text
in the prompt, and the swap moved them to the bottom where no prefix cache
reaches them. The exception already made for `{assistant_role}` is exactly the
right reasoning; it was simply not applied to the placeholders that are stable
across the whole run rather than within one phase.

## Method

```bash
# baseline already exists: data/traces/*__qwen2.5-coder-7b.jsonl
python3 scripts/reorder_prompts.py

python3 scripts/run_all.py --model qwen2.5-coder:7b \
  --base-url http://localhost:11434/v1 --api-key ollama \
  --config Reordered --tag reordered --limit 10

python3 scripts/redundancy_by_stage.py "data/traces/*__qwen2.5-coder-7b.jsonl" --tokenizer strict
python3 scripts/redundancy_by_stage.py "data/traces/*__qwen2.5-coder-7b-reordered.jsonl" --tokenizer strict
```

## Result

Run: 22 September 2026, Reordered config, `qwen2.5-coder:7b`, 10 ProgramDev
tasks, 73.2 minutes, 10/10 completed, none failed. Both arms measured with
`--tokenizer strict` (`tiktoken` `o200k_base`).

**The prediction failed. Reordering did not convert stranded tokens into
cacheable ones; pooled stranding rose.**

| | baseline | reordered |
|---|---|---|
| input tokens measured | 216,126 | 205,465 |
| redundant | 81.1% | 81.9% |
| **stranded (no prefix cache reaches it)** | **35.8%** | **40.7%** |

Against the four registered predictions:

1. **Total redundancy stays roughly flat.** Held: 81.1% -> 81.9%.
2. **The split shifts toward cacheable.** *Falsified.* Stranded input rose
   4.9 points.
3. **The largest drop appears where the static tail is largest.** *Falsified.*
   Documentation, the stage with the longest static tail, got worse.
4. **Code Completion barely moves.** *Falsified.* It moved most of all, and in
   the wrong direction.

Per stage:

| Stage | stranded, baseline | stranded, reordered | change |
|---|---|---|---|
| Code Completion | 8.8% | 32.8% | **+24.0** |
| Testing | 21.5% | 33.3% | **+11.8** |
| Documentation | 71.3% | 74.7% | +3.4 |
| Coding | 20.2% | 21.6% | +1.4 |
| Design | 13.5% | 14.6% | +1.1 |
| Code Review | 31.9% | 28.6% | **-3.3** |

Code Review is the only stage that moved as predicted.

### Is it just the stage mix?

No. The two arms did behave differently — 13.6 LLM calls per task against 16.2,
and Testing fell from 27.5% of all input to 8.5% while Code Completion rose from
4.5% to 11.0% — so the pooled figure is partly a mix effect. Applying the
**baseline** stage weights to the **reordered** per-stage rates still gives
**39.7%** against the baseline's 35.8%. The direction does not come from the mix.

### Is it inside the noise?

At task level, yes. Per task the change in stranded input is **+2.2 points,
sd 9.8, improved on 4 of 10 tasks** (paired t = 0.72). What can be said is
narrower than "reordering makes it worse": across ten tasks there is **no sign
of the predicted improvement** in any view of the data, and the pooled and
mix-adjusted figures both move the wrong way.

Per-task means, for the record: redundant 79.7% -> 77.4%, cacheable
45.0% -> 40.5%, stranded 34.7% -> 36.9%.

### Why it failed

The premise — that ChatDev assembles prompts volatile-first — is true of each
phase template read on its own, and false of the run as a whole.

Four of the thirteen Default phase prompts open with the same sentence, and
what follows it is `{task}`, `{modality}`, `{language}`, `{ideas}` — placeholders
whose **rendered values are constant for an entire run**. Across the 13 phases
there are only **8 distinct opening lines**. So a call in one phase already
shared a long prefix with calls in *other* phases, and that shared opening was
doing most of the caching work.

Reordering put each phase's own static instruction at the front. Those
instructions differ per phase, so the same 13 phases now have **11 distinct
opening lines**. Cross-phase prefix sharing was traded for within-phase sharing.

For a stage with many calls of its own that trade is roughly neutral — Code
Review, the largest stage, improved slightly. For a stage with few calls it is
a bad trade, because almost all of its prefix matching came from other phases.
Code Completion fires in 2 of 10 tasks and was the worst hit, 8.8% -> 32.8%.

### What this changes in the guidance

"Order sections from most stable to least stable" survives, but **"stable" has
to mean how often the rendered value changes in a real run, not whether the
line contains a template placeholder.** `{task}` is a placeholder and never
changes within a run. A hard-coded instruction that differs per phase is
literal text that changes at every phase switch. Sorting on the syntax instead
of the behaviour is what produced this result.

The practical form: measure, reorder, measure again. A reorder that looks
obviously right can move the number the wrong way, and the only way to know is
the second measurement.

### What this does not test

Whether a *correct* reordering — one that puts genuinely run-constant text
first, across phases as well as within them — recovers the stranded share. That
is the next experiment, and it needs the prompt templates rebuilt around a
shared run-constant header rather than the halves swapped.
