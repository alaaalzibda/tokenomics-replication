import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from tokenomics.shingle import analyse_run
from tokenomics.tokenize import get_tokenizer
from tokenomics.trace import CallRecord, Message

TOK = get_tokenizer("heuristic")


def call(i, text, run="r"):
    return CallRecord(
        run_id=run, task_id="t", call_index=i, phase="CodeReview",
        model="m", provider="openai", messages=[Message("user", text)],
        response_text="", input_tokens=0, output_tokens=0,
    )


def words(n, start=0):
    return " ".join(f"w{j}" for j in range(start, start + n))


def test_partition_is_exact():
    calls = [call(0, words(200)), call(1, words(200)), call(2, words(150, 50))]
    r = analyse_run(calls, tokenizer=TOK, window=8)
    assert r.redundant_tokens == r.cacheable_redundant_tokens + r.uncacheable_redundant_tokens


def test_first_call_has_no_redundancy():
    r = analyse_run([call(0, words(300))], tokenizer=TOK, window=8)
    assert r.redundant_tokens == 0
    assert r.prefix_cache_tokens == 0


def test_identical_repeat_is_fully_cacheable():
    text = words(300)
    r = analyse_run([call(0, text), call(1, text)], tokenizer=TOK, window=8)
    assert r.uncacheable_redundant_tokens == 0
    assert r.cacheable_redundant_tokens > 0


def test_repeat_after_changed_prefix_is_uncacheable():
    """The case the study is about: same body, different opening line."""
    body = words(400)
    a = "alpha unique opening line here\n\n" + body
    b = "beta different opening line here\n\n" + body
    r = analyse_run([call(0, a), call(1, b)], tokenizer=TOK, window=8)
    assert r.redundant_tokens > 0
    assert r.uncacheable_redundant_tokens > 0, "body repeats but prefix diverged"


def test_unrelated_calls_have_low_redundancy():
    r = analyse_run([call(0, words(300)), call(1, words(300, 10_000))],
                    tokenizer=TOK, window=16)
    assert r.redundancy < 0.05


def test_empty_run_rejected():
    with pytest.raises(ValueError):
        analyse_run([], tokenizer=TOK)
