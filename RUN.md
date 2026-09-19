# How to run a task

Everything below runs on your Mac. ChatDev's source is never edited.

## Free, local, with Ollama

```bash
# once
ollama serve &
ollama pull qwen2.5-coder:7b

# then, from the project root
source .venv/bin/activate
python3 scripts/run_task.py \
  --task "Design a basic Gomoku game." \
  --name gomoku \
  --model qwen2.5-coder:7b \
  --base-url http://localhost:11434/v1 \
  --api-key ollama
```

## Paid, Anthropic

```bash
source .venv/bin/activate
export ANTHROPIC_API_KEY=...
python3 scripts/run_task.py \
  --task "Design a basic Gomoku game." \
  --name gomoku \
  --model claude-opus-4-1 \
  --base-url https://api.anthropic.com/v1
```

## Then analyse

```bash
python3 scripts/analyze.py data/traces/gomoku__*.jsonl --compare-paper
```

## What to check on the first run

* the recorder prints `recording -> ...` before ChatDev starts
* at the end it prints how many call records were written
* if it reports any `phase=Unknown`, tell me before trusting the numbers
* compare its `input_tokens` total against the provider's own usage page
