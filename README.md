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

If you only read one section, read
[What a development team can do with this](#what-a-development-team-can-do-with-this).
It is the practical answer: which part of an agent's bill is avoidable, and
what to change to avoid it.

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

## Validation: the pipeline reproduces the original exactly

The authors released their 30 ChatDev/GPT-5 execution traces
([Zenodo record 17430187](https://zenodo.org/records/17430187)). Those logs
carry, per LLM call, the phase that was running and the provider-reported token
counts — everything the stage aggregation needs.

So before reporting anything of our own, we ran **our** phase mapping and
**our** aggregation over **their** raw traces and compared against their
published table.

```
python3 scripts/verify_against_original.py \
  data/original/traces/execution_traces/ChatDev_GPT-5_Reasoning
```

| Stage | Ours | Paper | Δ | n |
|---|---|---|---|---|
| Design | 2.4% | 2.4% | 0.0 | 30/30 |
| Coding | 8.6% | 8.6% | 0.0 | 30/30 |
| Code Completion | 26.8% | 26.8% | 0.0 | **6/30** |
| Code Review | **59.4%** | **59.4%** | 0.0 | 30/30 |
| Testing | 10.3% | 10.3% | 0.0 | **12/30** |
| Documentation | 20.1% | 20.1% | 0.0 | 30/30 |

| Token type | Ours | Paper | Δ |
|---|---|---|---|
| input | 54.4% | 53.9% | +0.5 |
| output | 24.9% | 24.4% | +0.5 |
| reasoning | 20.6% | 21.6% | −1.0 |

Every stage share reproduces to within 0.05 percentage points, and both
small-sample stage counts — Code Completion in 6 of 30 tasks, Testing in 12 —
match exactly. The instrument is validated against data we did not produce.

### The bug this caught

The first run of this validation returned input 45.1% / output 37.8% /
reasoning 17.1% against their 53.9 / 24.4 / 21.6. The cause was ours:

**Providers report `completion_tokens` inclusive of `reasoning_tokens`.** Our
`CallRecord.total_tokens` was returning `input + output + reasoning`, counting
reasoning twice. Correcting the denominator to `input + completion`, and taking
visible output as `completion − reasoning`, brought all three within a point.

The bug was invisible in our own runs, because a local model reports zero
reasoning tokens — it would have surfaced only on a frontier-model run, after
the expensive part. It is fixed in `trace.py` and `aggregate.py`, and
`total_tokens` now carries the reasoning behind the convention.

### What the traces also settle

* The logs are **ChatDev 1.x** — the config paths in every trace point at
  `ChatDev/CompanyConfig/Default/ChatChainConfig.json`, the 1.x layout.
* The runs are dated **8–24 September 2025**, close to four months before the 2.0
  rewrite removed 1.x from the repository.
* **The replication package does not pin a ChatDev version or commit either.**
  Neither the paper nor the Zenodo README names one, so the exact framework
  version remains unrecoverable from the published artifacts.
* Their traces record token counts but **not the verbatim prompt arrays**, so
  the redundancy measure below cannot be run over them without reconstructing
  prompts. That is not attempted here.

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

The measure is stable in two independent ways. Across window sizes `k` = 8 to
128 it falls monotonically by between **4.8 and 9.4 percentage points**
depending on the task, with no threshold effect — the ranking of tasks and the
size of the effect are unchanged by the choice of `k`.
And re-running the whole analysis under a word-split heuristic instead of
`tiktoken` shifted every pooled figure by less than 1 percentage point
(redundant 80.6 vs 79.7, cacheable 45.0 vs 45.1, uncacheable 35.6 vs 34.7),
so the result does not depend on the choice of tokenizer.

Input tokens were **75.6%** of consumption (sd 4.1), against 53.9% in the
original. Part of that gap is structural: our model emits no reasoning tokens,
so the same input is divided by a smaller denominator.

### Where the stranded tokens actually are

The original paper reports token spend by stage. Running the redundancy measure
with the same stage attribution puts the two tables side by side:

```bash
python3 scripts/redundancy_by_stage.py "data/traces/*__qwen2.5-coder-7b.jsonl" --tokenizer strict
```

| Stage | Share of all input | Redundant | **Uncacheable** |
|---|---|---|---|
| **Documentation** | 22.6% | 82.8% | **73.4%** |
| Code Review | 38.6% | 85.8% | 32.0% |
| Testing | 27.5% | 92.3% | 22.5% |
| Coding | 2.8% | 29.0% | 20.2% |
| Design | 4.1% | 19.3% | 13.2% |
| Code Completion | 4.5% | 72.5% | 7.4% |
| **all** | 100% | 82.0% | 36.5% |

**Stranding is not uniform. It ranges from 7.4% to 73.4% depending on the
stage**, and that changes the advice. A team should not apply one fix
everywhere: Code Completion is almost entirely cacheable and needs nothing,
while Documentation wastes nearly three quarters of its input on repetition no
cache can reach.

This also sharpens a result in the original. The paper reports Documentation as
the most input-dominated stage, at 80.2% input. Our measurement suggests *why*
that input is expensive: most of it is not new material but re-sent context
positioned where the discount cannot apply.

Testing is the mirror image — the highest raw redundancy of any stage at 92.3%,
yet only 22.5% stranded, so caching already absorbs most of it.

A caveat on mechanism: these are the positions of repeated tokens, which we
measure directly. *Why* a given stage strands more than another — prompt
template ordering, how late in the run the stage fires, how much prior content
exists to repeat against — is a hypothesis this data does not settle.

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

* One run per task on our side. No variance estimate within a task.
* 10 of 30 tasks.

## What a development team can do with this

The paper answers *where* tokens go. This section answers the question a team
actually has to act on: **which part of that bill is avoidable, and what do I
change to avoid it?**

### The problem, stated plainly

A language model has no memory. Every call is independent: text in, text out,
nothing retained. Anything that looks like memory — an agent that knows what
was decided three steps ago, a chat that follows a long conversation — is the
surrounding application **re-sending that text on every single call**.

For an agentic system this compounds. In ChatDev's review loop the system
prompt, the coding standards and the entire current source file go out again on
every round, even when three lines changed. That is why input dominates
consumption: 53.9% of tokens in the original study, 75.6% in our runs.

Teams know their agent is expensive. What they do not know is **how much of
that cost is new information and how much is re-transmission** — and, crucially,
which part of the re-transmission they can actually do something about.

### Why the total is not actionable, but the split is

"Our agent repeats 80% of its input" is an interesting fact and a useless one.
It does not tell you whether to change a setting or change your code.

Provider prefix caching (OpenAI, Anthropic and others) charges a large discount
for the opening stretch of a prompt that matches one processed recently. The
critical property is that it matches **from token zero and stops at the first
difference**. It is a bookmark, not a search: the provider has stored the work
for "a prompt beginning with exactly these tokens", and because a transformer's
computation at position *n* depends on every position before it, that stored
work is valid only if the entire preceding run is identical.

So repeated text falls into two categories with completely different economics:

| | What it is | Who fixes it | How |
|---|---|---|---|
| **Cacheable** | Repeated text sitting **before** the first difference from the previous prompt | The provider | Enable prefix caching. No code change |
| **Uncacheable** | Repeated text sitting **after** the first difference | You | Change how the prompt is assembled |

The second category is invisible in every dashboard we are aware of. It is
billed at the full input rate, on every call, forever, and no caching product
on the market can reach it.

### Worked example

One call sends 1,000 input tokens. Our measurements across ten tasks give:

```
 203 tokens   genuinely new                           unavoidable
 450 tokens   repeated, before the first difference   cache reaches it
 347 tokens   repeated, after the first difference    cache cannot reach it
```

(Our shares are 20.3 / 45.1 / 34.7 percent; rounded to whole tokens they would
sum to 1,001, so one token is shaved off the cacheable bucket here to keep the
example exact.)

797 of those 1,000 tokens are text the system already sent. Not 797 different
things — the same standards and the same source file, again.

Let `d` be your provider's cache-hit rate as a fraction of the standard input
rate (commonly around 0.1, but check your own pricing page — it varies by
provider and has changed over time). Per 1,000 input tokens, in units of the
standard input price:

* **No caching:** 1000 × 1 = **1000**
* **Caching on, prompts as they are:** 550 × 1 + 450 × d = **595** at d = 0.1
* **Caching on, prompts reordered so repetition sits in the prefix:**
  203 × 1 + 797 × d = **283** at d = 0.1

That is a **40% reduction** from enabling caching alone, and a **72% reduction**
once the prompt order stops stranding repetition — on input tokens, which were
75.6% of all consumption in these runs.

The first step is a configuration change. The second is a change to the order
in which you concatenate strings. Neither alters a single word of what the
model is asked.

### What "reorder the prompt" actually means

Most agent frameworks build a prompt by gluing sections together, and the order
is usually whatever was convenient when the code was written. A typical
arrangement puts the volatile part first:

```
[Task: Gomoku. Phase: CodeReview, round 3 of 6]   <-- changes every call
You are a Code Reviewer. Follow the architecture rules...
...500 lines of standards...
Current implementation:
...90 lines of source...
```

Every call changes line 1, so the cache matches almost nothing and you pay full
rate for 590 lines that were byte-identical to last time.

Inverting it costs nothing:

```
You are a Code Reviewer. Follow the architecture rules...
...500 lines of standards...                       <-- never changes
Current implementation:
...90 lines of source...                           <-- changes rarely
[Task: Gomoku. Phase: CodeReview, round 3 of 6]    <-- changes every call
```

Same information, same question, same answer. But now the cache matches 590
lines before reaching anything that moved.

**The design rule: order sections from most stable to least stable.** System
role and rules first, then long-lived project context, then the current
artefact, and the per-call instruction last.

**What silently destroys a prefix.** Anything variable near the top, even when
it carries no meaning for the task:

* timestamps or dates injected into a system prompt
* request, session or trace IDs
* turn or round counters ("round 3 of 6")
* the task or project name, when it is prepended rather than appended
* a randomised greeting or persona line
* a typo — one character is enough; the match ends there and everything below
  it is billed in full

None of these change what is being asked. All of them can cost you the discount
on everything that follows.

### A third lever: stop re-sending what did not change

Reordering makes repetition cheap. Not repeating is cheaper still.

ChatDev re-sends the complete source file on every review round even when the
previous round changed three lines. Sending a unified diff, or only the changed
region with a few lines of surrounding context, attacks the volume rather than
the unit price. This is more invasive than reordering — the agent's prompts
have to be written to expect diffs — but it is the only lever that reduces the
token count itself.

Ordering to apply them in, cheapest first:

1. **Enable prefix caching.** Configuration. Minutes.
2. **Reorder prompt assembly, stable to volatile.** A small, local code change,
   and a lint rule to keep it that way.
3. **Send diffs instead of whole artefacts.** A real redesign of the agent's
   prompts, worth doing only once 1 and 2 are exhausted.

### How to get your own three numbers

The harness records every call a framework makes and reports the split. It
wraps the provider client rather than modifying the framework, so it can be
attached to an existing agent without touching it:

```bash
python3 scripts/summarise.py "data/traces/*__<your-model>.jsonl" --tokenizer strict
python3 scripts/window_sensitivity.py "data/traces/*__<your-model>.jsonl"
```

Read the result as a diagnosis:

* **High redundancy, high cacheable share** — you are leaving money on the
  table for no reason. Turn caching on.
* **High redundancy, high uncacheable share** — caching will disappoint you.
  Your prompt order is the problem. This is the case our ten tasks fall into,
  with roughly a third of all input stranded.
* **Low redundancy** — repetition is not your cost driver. Look at output and
  reasoning tokens instead, and at how many calls the framework makes at all.

### Beyond cost

Three consequences follow from the same measurement, and only the first is
about money:

* **Latency.** A cache hit skips the prefill for that prefix, so the discount
  usually comes with a faster first token. Time-to-first-token on agentic
  workloads is dominated by prefill on long prompts.
* **Context window.** Re-sent context occupies the window. An agent that spends
  80% of its input on repetition hits its context limit roughly five times
  sooner than one that does not, which forces truncation or summarisation and
  degrades quality for reasons that have nothing to do with the model.
* **Energy.** Tokens processed are computation performed. Repetition that the
  cache does not absorb is compute spent re-deriving something already derived.
  We measure tokens, not joules, and we are careful not to claim otherwise —
  but the direction is not in question.

### What this section does not claim

* The reordering figures above are an **upper bound** computed from where
  repeated tokens sit, not a measured saving from an implemented change. The
  obvious next experiment is to implement the reordering in ChatDev and measure
  whether the predicted shift from uncacheable to cacheable actually occurs.
* Ten tasks, one framework, one model, one run each.
* ProgramDev tasks are small. Redundancy plausibly rises with project size, so
  these figures are more likely a floor than a ceiling.
* Cache-hit pricing and eligibility rules differ by provider and change over
  time. The arithmetic above is parameterised by `d` for that reason.

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
* **Run-to-run variance.** The paper does not state runs per task; their 30
  traces for 30 projects imply one each. With one run, no cross-model
  difference can be distinguished from noise; use `--repeat` and report the
  spread.
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
