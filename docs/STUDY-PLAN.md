# Study plan

**Working title.** Is the 59.4% code-review token share a property of the
framework or of the model? A replication and extension of *Tokenomics*
(Salim, Latendresse, Khatoonabadi and Shihab, arXiv:2601.14470).

## What the original found

ChatDev, GPT-5 reasoning (`gpt-5-2025-08-07`), 30 ProgramDev tasks, n=1 per
task, temperature immutable at 1.0.

| Stage | Share | n of 30 |
|---|---|---|
| Code Review | 59.4% | 30 |
| Code Completion | 26.8% | 6 |
| Documentation | 20.1% | 30 |
| Testing | 10.3% | 12 |
| Coding | 8.6% | 30 |
| Design | 2.4% | 30 |

Token type split: input 53.9%, output 24.4%, reasoning 21.6%.

The authors call the findings *preliminary* and list as limitations: a single
system, a single model, 30 tasks, small n on two stages, and one of several
possible phase mappings.

## RQ1 (replication) — is the distribution model-dependent?

Hold ChatDev, the task corpus and the phase mapping fixed. Change the model.

* **H0**: the stage distribution is a property of the framework's control flow,
  so it is stable across models.
* **H1**: it is model-dependent, so the 59.4% headline does not transfer.

Either outcome is publishable. H0 strengthens their claim beyond what they
could show; H1 bounds it.

### Design decisions that are not negotiable

1. **Report shares, never raw token counts across models.** Different
   tokenizers. Raw totals are not comparable and reviewers will say so.
2. **Cross-model figures use input+output only.** GPT-5 bills a separate
   reasoning field; Claude's extended thinking is accounted differently; a
   non-reasoning model reports zero. Including it compares three different
   things. Their own reasoning split is reproduced separately, GPT-5 only.
3. **Repeat runs.** They ran n=1 at temperature 1.0. With n=1 any cross-model
   gap is indistinguishable from run-to-run noise. Minimum: 5 repeats on a
   10-task subset, report the spread, and state the smallest difference the
   design can actually detect.
4. **Keep the prompts byte-identical.** The only permitted change in the
   ChatDev adapter is the transport. Any prompt edit is a confound; log a diff
   of every change made to the framework.
5. **Reuse their phase mapping unchanged.** An alternative mapping is a
   separate sensitivity analysis, not a silent improvement.

## RQ2 (the contribution) — how much of the input share is re-sent context?

Input is the largest slice (53.9% overall, 80.2% in Documentation). Nobody has
measured how much of it is content the system had already sent.

For each call, in token space, with positions:

* `cache_len` = longest common prefix with any earlier prompt in the run
* a token is **redundant** if the k-token window starting there was already
  sent earlier in the run
* a redundant token is **cacheable** if it lies before `cache_len`, and
  **uncacheable** otherwise

By construction `redundant = cacheable + uncacheable` exactly.

**`uncacheable` is the headline.** Provider prefix caches bill a hit at a
fraction of the input rate, but they match prefixes only. Content that repeats
in the middle of a prompt is paid for at full rate on every single call, and no
caching product on the market reaches it. That share is the size of the prize
for restructuring agent context rather than caching it.

Report `k` sensitivity over {8, 16, 32, 64, 128}. A claim that moves with `k`
is not a claim.

### Why this is worth doing at all

If uncacheable redundancy is small, caching is the whole answer and the field
should stop theorising. If it is large, there is a concrete, quantified target
for context compression and agent protocol design, which is a research agenda
rather than an engineering tweak.

## Threats we inherit and must state

* One framework (ChatDev). Any finding is about ChatDev-shaped systems.
* ProgramDev tasks skew small. Redundancy likely *rises* with project size, so
  our figure is probably a lower bound; say so rather than implying generality.
* The phase mapping is an abstraction, theirs and now ours.
* Our own adapter is a confound if it changes prompts. Hence the diff log.

## Budget

Their reasoning tokens alone ran 17,280–40,000 per task. At 21.6% of the total
that implies roughly 80k–185k tokens per task, so 30 tasks is about 2.5M–5.5M
tokens per model. **Decide the ceiling before writing the runner.** Likely
affordable shape: full 30 tasks on a cheap model, a 10-task subset repeated 5x
on the frontier model.

## Status

* [x] Phase mapping, trace schema, aggregation, redundancy analyser
* [x] Synthetic trace generator so the pipeline is testable at zero cost
* [ ] **Ask Shihab whether his group is already running this**
* [ ] ChatDev fork + provider adapter (OpenAI, Anthropic), prompts byte-identical
* [ ] Pilot: 3 tasks, both models, verify instrumentation against provider billing
* [ ] Full run to budget
* [ ] Write-up, limitations, public repo
