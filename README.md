# Tokenomics replication and extension

Testing whether the token distribution reported in *Tokenomics: Quantifying
Where Tokens Are Used in Agentic Software Engineering*
(Salim, Latendresse, Khatoonabadi and Shihab, arXiv:2601.14470) is a property
of the agent framework or of the underlying model, and measuring how much of
the dominant input-token share is re-sent context.

See `docs/STUDY-PLAN.md` for the design, the hypotheses and the threats.

## Two questions

1. **RQ1** Hold ChatDev and the task corpus fixed, change the model. Does the
   59.4% code-review share move?
2. **RQ2** Of the input tokens, which are 53.9% of all consumption, how many
   were already sent earlier in the same run -- and how much of that is beyond
   the reach of a prefix cache?

## Layout

```
src/tokenomics/
  phases.py      ChatDev phase -> SDLC stage mapping, plus the published figures
  trace.py       one record per LLM call; everything downstream reads this
  tokenize.py    pluggable tokenizer; shares are only valid within one tokenizer
  shingle.py     position-aware redundancy: redundant = cacheable + uncacheable
  aggregate.py   per-stage and per-type shares, reproducing the paper's tables
  redundancy.py  block-level duplication, kept as a secondary diagnostic
scripts/
  make_synthetic_trace.py   fake ChatDev-shaped traces, zero API cost
  analyze.py                run the analysis, print the tables
```

## Run it now, without spending anything

```bash
python3 scripts/make_synthetic_trace.py --out data/traces/sample_synthetic.jsonl --tasks 6
python3 scripts/analyze.py data/traces/sample_synthetic.jsonl --compare-paper
```

**The synthetic numbers are not results.** They exercise the pipeline. The
generator was written to reproduce one structural feature that matters for RQ2:
a fixed system preamble followed by the whole current source file, re-sent on
every review round with a few lines changed.

## Honest status

Nothing has been run against a real model. No finding here is a finding about
the world yet.
