# Tokenomics: replication and a context-redundancy extension

Testing whether the token distribution reported in *Tokenomics: Quantifying
Where Tokens Are Used in Agentic Software Engineering* (Salim, Latendresse,
Khatoonabadi and Shihab, arXiv:2601.14470, 20 January 2026) is a property of
the agent framework or of the underlying model — and measuring how much of the
dominant input-token share is context the system had already sent.

## Two questions

**RQ1 (replication).** Hold ChatDev and the task corpus fixed, change the
model. Does the 59.4% code-review share move? Either answer is a result: if it
holds, review-dominance is architectural and their claim generalises further
than they showed; if it moves, the headline number is model-specific.

**RQ2 (extension).** Input tokens are the largest slice of consumption (53.9%
overall in the original, rising to 80.2% in Documentation). How much of that
is re-transmission, and how much of *that* is beyond the reach of a prefix
cache?

## Exactly what was run

Reproducibility depends on these being stated, so they are stated.

| | |
|---|---|
| Framework | ChatDev 1.x |
| Source | `github.com/Kunlun-Zhu/ChatDev` (fork) |
| Commit | `a69bda1f26a9ea930cc8b5645ed6b5244393d9a5`, 2023-08-28 |
| Phase chain | DemandAnalysis → LanguageChoose → Coding → CodeCompleteAll → CodeReview → Test → EnvironmentDoc → Manual |
| Task corpus | ProgramDev, all 30 tasks |
| Corpus source | `multi-agent-systems-failure-taxonomy/MAST`, `traces/programdev/programdev_dataset.json` |
| Client | `openai==0.27.8`, pointed at an OpenAI-compatible endpoint |
| ChatDev source changes | **none** — see below |

### Why a fork, and the gap it leaves

The original paper ran ChatDev 1.x. **That version is no longer obtainable from
the official repository.** `OpenBMB/ChatDev`'s history now begins on 7 January
2026 with `f0db945 initial commit of chatdev 2.0`; every earlier commit is
gone, the tags run v2.0.0–v2.2.0 only, and none of the paper's phase names
(`DemandAnalysis`, `CodeComplete`, `CodeReview`, `EnvironmentDoc`, `Manual`)
appear in any commit or tag of the surviving history.

The paper was submitted on 20 January 2026, two weeks after that rewrite, using
the 1.x phase names. We therefore reconstructed 1.x from a community fork,
pinned above by commit hash.

**This is a genuine limitation and it is not ours to fix.** The fork dates from
August 2023; the original authors ran something from late 2025. Where ChatDev
1.x changed between those dates, our framework is not byte-identical to theirs.
The paper does not state a commit, so the exact version cannot be recovered
from the publication alone.

### Instrumentation: no ChatDev source was modified

ChatDev 1.x funnels every LLM call through a single site,
`openai.ChatCompletion.create` in `camel/model_backend.py`. `record.py` wraps
that function, copies what passes through and forwards the arguments untouched.
`vendor/ChatDev1x/` is therefore identical to the fork above, which is a claim
that can be checked rather than trusted.

Two consequences worth stating:

* The model name is substituted **on the wire**, so ChatDev continues to believe
  it is calling `gpt-4` and its own bookkeeping stays valid. Prompts are
  byte-identical by construction.
* Because ChatDev sizes `max_tokens` from gpt-4's 8192-token window, that cap
  may differ from what a native integration would set for another model. This
  affects how much a model is *allowed* to emit, not what it is asked.

## What is measured

### Stage shares

`aggregate.py` reproduces the paper's tables, including its convention of
averaging a stage only over the runs in which that stage ran — which is why
their six stage shares do not sum to 100.

All cross-model figures use **input + output only**. Reasoning tokens are not
comparable across providers: GPT-5 bills a separate reasoning field, extended
thinking is accounted differently elsewhere, and a model without hidden
reasoning reports zero.

Raw token counts are never compared across models, because the tokenizers
differ. Only shares are.

### Context redundancy

For each call, in token space, with positions:

* `cache_len` — longest common prefix with any earlier prompt in the run
* a token is **redundant** if the k-token window starting there was already
  sent earlier in the run
* a redundant token is **cacheable** if it lies before `cache_len`, and
  **uncacheable** otherwise

so `redundant = cacheable + uncacheable` exactly, by construction, and a test
asserts it.

**`uncacheable` is the headline.** Provider prefix caches bill a hit at a
fraction of the input rate, but they match prefixes only. Content that repeats
in the middle of a prompt is paid for at full rate on every call, and no
caching product reaches it. That share is the size of the prize for
restructuring agent context rather than caching it.

`k` sensitivity is reported over {8, 16, 32, 64, 128}. A claim that moves with
`k` is not a claim.

## Results

**10 of the 30 ProgramDev tasks, 162 LLM calls, `qwen2.5-coder:7b` via Ollama,
one run per task.** Every task completed; none failed.

### RQ2 — context redundancy (the new measurement)

| Task | Redundant | Cacheable | **Uncacheable** |
|---|---|---|---|
| 2048 | 84.6% | 49.1% | 35.5% |
| BudgetTracker | 75.5% | 44.1% | 31.4% |
| Checkers | 82.1% | 39.6% | 42.5% |
| Chess | 83.2% | 41.1% | 42.1% |
| DetectPalindromes | 82.9% | 47.3% | 35.6% |
| FibonacciNumbers | 67.9% | 44.2% | 23.7% |
| Sudoku | 75.5% | 29.6% | 45.9% |
| TheCrossword | 83.2% | 45.6% | 37.5% |
| TicTacToe | 82.5% | 55.1% | 27.4% |
| Gomoku | 79.8% | 54.8% | 25.1% |
| **mean** | **79.7%** | **45.1%** | **34.7%** |
| sd | 5.0 | 7.1 | 7.3 |
| range | 67.9–84.6 | 29.6–55.1 | 23.7–45.9 |

Tokenizer: `tiktoken` `o200k_base`.

**Four fifths of all input tokens had already been sent earlier in the same
run.** Across ten tasks spanning a Fibonacci generator to a chess game, that
share never fell below 67.9%.

**Of that, only about half sits in a prefix a provider cache could hit.** A
mean of **34.7% of input tokens are redundant and uncacheable** — re-sent
content positioned where no prefix cache reaches it, paid at full rate on every
call. On no task did that fall below 23.7%.

The measure is stable in two independent ways. It moves by roughly 3–6
percentage points across window sizes `k` = 8 to 128, with no threshold effect.
And re-running the whole analysis under a word-split heuristic instead of
`tiktoken` shifted every pooled figure by less than 1 percentage point
(redundant 80.6 vs 79.7, cacheable 45.0 vs 45.1, uncacheable 35.6 vs 34.7),
so the result does not depend on the choice of tokenizer.

Input tokens were **75.6%** of consumption (sd 4.1), against 53.9% in the
original. Part of that gap is structural: our model emits no reasoning tokens,
so the same input is divided by a smaller denominator.

### RQ1 — stage distribution

| Stage | Ours (mean) | sd | n | Original |
|---|---|---|---|---|
| Code Review | 42.6% | 8.5 | 10/10 | 59.4% |
| Testing | 34.5% | 4.4 | 6/10 | 10.3% |
| Documentation | 22.0% | 5.6 | 10/10 | 20.1% |
| Code Completion | 21.1% | 6.1 | 2/10 | 26.8% |
| Coding | 6.9% | 2.0 | 10/10 | 8.6% |
| Design | 3.6% | 1.4 | 10/10 | 2.4% |

**Code Review is the largest single stage here too**, which is the original's
central qualitative claim and it survives. But at 42.6% rather than 59.4%, with
Testing far larger than reported.

**This is not a controlled test of their 59.4%, and should not be read as one.**
Three things differ at once — the model, the ChatDev version, and the number of
tasks — so no difference can be attributed to any one of them. A clean test of
model dependence requires running the same framework and corpus on a second
model, changing nothing else. That has not been done.

What can be said: Coding (6.9% vs 8.6%), Design (3.6% vs 2.4%) and
Documentation (22.0% vs 20.1%) land close to the published figures, while Code
Review and Testing do not. Code Completion is rare in both — it triggered in
2 of our 10 tasks and 6 of their 30.

### Caveats on these specific numbers

* One run per task. No variance estimate within a task.
* 10 of 30 tasks.

## Running it

See `RUN.md`. A single task:

```bash
python3 scripts/run_task.py --task "..." --name gomoku \
  --model qwen2.5-coder:7b --base-url http://localhost:11434/v1 --api-key ollama
```

The whole corpus, resumable:

```bash
python3 scripts/run_all.py --model qwen2.5-coder:7b \
  --base-url http://localhost:11434/v1 --api-key ollama
```

Analysis (use `--tokenizer strict` for anything reported; `auto` warns loudly
if it falls back):

```bash
python3 scripts/analyze.py "data/traces/*__qwen2.5-coder-7b.jsonl" \
  --tokenizer strict --compare-paper
```

## Threats to validity

* **Framework version.** As above: 1.x reconstructed from a 2023 fork; the
  authors' exact version is unrecoverable from the paper.
* **One framework.** Any finding is about ChatDev-shaped systems.
* **Task size.** ProgramDev tasks are small. Redundancy plausibly rises with
  project size, so these figures are likely a lower bound.
* **Phase mapping.** Theirs, reused unchanged. An alternative mapping is a
  separate sensitivity analysis, not a silent improvement.
* **Run-to-run variance.** The original ran n=1 per task at temperature 1.0.
  With n=1 no cross-model difference can be distinguished from noise; use
  `--repeat` and report the spread.
* **max_tokens.** See instrumentation note above.

## Layout

```
src/tokenomics/
  phases.py      ChatDev phase → SDLC stage mapping, plus the published figures
  trace.py       one record per LLM call; everything downstream reads this
  tokenize.py    pluggable tokenizer; refuses to degrade silently in strict mode
  shingle.py     position-aware redundancy: redundant = cacheable + uncacheable
  aggregate.py   per-stage and per-type shares
  record.py      the zero-edit call recorder
scripts/
  run_task.py    one task
  run_all.py     the corpus, resumable, one subprocess per task
  analyze.py     the tables
  check_endpoint.py          provider compatibility smoke test
  make_synthetic_trace.py    fake traces for testing at zero cost
```

## Status

10 of 30 ProgramDev tasks run and analysed. Remaining: the other 20 tasks, a\nsecond model for a controlled RQ1 test, repeat runs for variance, and a\nregeneration of all figures under a real tokenizer.
