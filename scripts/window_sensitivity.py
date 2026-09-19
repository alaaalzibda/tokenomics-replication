"""Print redundancy as a function of the shingle window k, for every trace.

Any claim about redundancy has to survive this table, so it is a script rather
than a number someone typed into the README once.
"""
from __future__ import annotations
import argparse, glob, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tokenomics.shingle import window_sensitivity   # noqa: E402
from tokenomics.tokenize import get_tokenizer       # noqa: E402
from tokenomics.trace import read_trace             # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("--tokenizer", default="auto")
    args = ap.parse_args()

    tok = get_tokenizer(args.tokenizer)
    files = sorted(glob.glob(args.pattern))
    if not files:
        print("no traces matched"); return 2

    ks = (8, 16, 32, 64, 128)
    print(f"tokenizer = {tok.name}\n")
    print(f"{'task':<20}" + "".join(f"{'k='+str(k):>9}" for k in ks) + f"{'spread':>10}")
    spreads = []
    for f in files:
        ws = window_sensitivity(read_trace(f), windows=ks, tokenizer=tok)
        sp = (max(ws.values()) - min(ws.values())) * 100
        spreads.append(sp)
        name = Path(f).name.split("__")[0]
        print(f"{name:<20}" + "".join(f"{ws[k]*100:8.1f}%" for k in ks) + f"{sp:9.1f}pp")
    print(f"\nspread across tasks: min {min(spreads):.1f}pp  max {max(spreads):.1f}pp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
