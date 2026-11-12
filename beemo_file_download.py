"""
Pull 10 "in-between" samples (human-edited AI text and LLM-edited AI text)
from the Beemo dataset, restricted to 5-10 sentences, and save to CSV.

Usage:
    pip install datasets pandas
    python beemo_file_download.py
"""

import csv
import json
import random
import re

from datasets import load_dataset

random.seed(42)

MIN_SENT, MAX_SENT = 5, 10
CATEGORIES = ("Generation", "Rewrite", "Summarize")   # QA rows are too short
OUT_FILE = "beemo_inbetween_10.csv"


def n_sent(text: str) -> int:
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


def in_range(text) -> bool:
    return isinstance(text, str) and MIN_SENT <= n_sent(text) <= MAX_SENT


def iter_edits(val):
    """Yield (prompt_label, text) from an edits column, whatever its stored shape."""
    if val is None:
        return
    if isinstance(val, str):                       # JSON-encoded string?
        try:
            val = json.loads(val)
        except json.JSONDecodeError:
            yield "P?", val                        # a single plain string
            return
    if isinstance(val, dict):                      # {"P1": "...", "P2": "...", "P3": "..."}
        for k, v in val.items():
            yield k, v
    elif isinstance(val, list):
        for i, item in enumerate(val, 1):
            if isinstance(item, dict):             # [{"P1": "..."}, {"P2": "..."}, ...]
                for k, v in item.items():
                    yield k, v
            elif isinstance(item, str):            # ["...", "...", "..."]
                yield f"P{i}", item


def main():
    ds = load_dataset("toloka/beemo", split="train")
    print(f"Loaded {len(ds)} rows")
    print("Shape of gpt-4o_edits in row 0:", type(ds[0]["gpt-4o_edits"]).__name__)

    candidates = []
    for row in ds:
        if row["category"] not in CATEGORIES:
            continue

        # human-edited AI text
        if in_range(row["human_edits"]):
            candidates.append({
                "id": row["id"],
                "category": row["category"],
                "source_model": row["model"],
                "edit_type": "human_edited",
                "text": row["human_edits"],
            })

        # LLM-edited AI text
        for col, editor in (("gpt-4o_edits", "gpt4o"), ("llama-3.1-70b_edits", "llama70b")):
            for p, txt in iter_edits(row[col]):
                if in_range(txt):
                    candidates.append({
                        "id": row["id"],
                        "category": row["category"],
                        "source_model": row["model"],
                        "edit_type": f"{editor}_{p}",
                        "text": txt,
                    })

    human_ed = [c for c in candidates if c["edit_type"] == "human_edited"]
    llm_ed = [c for c in candidates if c["edit_type"] != "human_edited"]
    print(f"Candidates: {len(human_ed)} human-edited, {len(llm_ed)} LLM-edited")

    random.shuffle(human_ed)
    random.shuffle(llm_ed)

    # 5 human-edited + 5 LLM-edited, each from a different prompt
    sample, seen_ids = [], set()
    for pool, k in ((human_ed, 5), (llm_ed, 5)):
        taken = 0
        for c in pool:
            if taken >= k:
                break
            if c["id"] in seen_ids:
                continue
            seen_ids.add(c["id"])
            sample.append(c)
            taken += 1

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "category", "source_model", "edit_type", "text"])
        w.writeheader()
        w.writerows(sample)

    print(f"\nWrote {len(sample)} samples to {OUT_FILE}\n")
    for s in sample:
        print(f"[{s['edit_type']} | {s['category']} | from {s['source_model']} | {n_sent(s['text'])} sentences]")
        print(s["text"])
        print("-" * 80)


if __name__ == "__main__":
    main()