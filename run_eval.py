"""Run the 20 test questions through the assistant and write eval/results.csv for scoring.

Run:  python -m eval.run_eval

Columns written: retrieval_hit (automatic), refused (automatic), then `score` and `notes`
which YOU fill in by hand (correct / partially correct / wrong), then run:
    python -m eval.run_eval --summary
"""
import argparse
import csv
from pathlib import Path

from app import config

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results.csv"


def run():
    from app import rag

    rows = []
    with open(HERE / "questions.csv", newline="", encoding="utf-8") as f:
        for q in csv.DictReader(f):
            text, hits = rag.answer(q["question"])
            sources = sorted({h["source"] for h in hits})
            in_scope = q["in_scope"] == "yes"
            rows.append(
                {
                    **q,
                    "answer": text.replace("\n", " "),
                    "retrieved_sources": "; ".join(sources),
                    # did the right document appear in the top-k chunks?
                    "retrieval_hit": (q["expected_source"] in sources) if in_scope else "n/a",
                    # did the model use the refusal sentence?
                    "refused": config.REFUSAL.lower()[:35] in text.lower(),
                    "score": "",   # fill in: correct / partially correct / wrong
                    "notes": "",
                }
            )
    with open(RESULTS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    hits = [r for r in rows if r["retrieval_hit"] is True]
    in_scope = [r for r in rows if r["in_scope"] == "yes"]
    print(f"Wrote {RESULTS}. Retrieval hit rate: {len(hits)}/{len(in_scope)}")
    print("Now open results.csv, fill the `score` column by hand, then run with --summary.")


def summary():
    with open(RESULTS, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    scored = [r for r in rows if r["score"].strip()]
    if len(scored) < len(rows):
        print(f"Warning: only {len(scored)}/{len(rows)} rows scored.")
    def n(label, subset):
        return sum(1 for r in subset if r["score"].strip().lower() == label)
    ins = [r for r in rows if r["in_scope"] == "yes"]
    out = [r for r in rows if r["in_scope"] == "no"]
    print(f"In scope ({len(ins)}): {n('correct', ins)} correct, {n('partially correct', ins)} partially correct, {n('wrong', ins)} wrong")
    print(f"Out of scope ({len(out)}): {n('correct', out)} correctly refused, {n('wrong', out)} wrong")
    total = n("correct", rows)
    print(f"\nRESUME LINE: {total}/{len(rows)} correct, {n('correct', out)}/{len(out)} out-of-scope questions correctly refused")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    summary() if args.summary else run()
