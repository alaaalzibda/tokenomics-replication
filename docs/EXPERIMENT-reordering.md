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

*(to be filled in after the run — including if it fails)*
