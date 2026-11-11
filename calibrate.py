"""
Score every sample in a folder with both the perplexity signal and the
Binoculars signal, side by side.

    python calibrate.py Milestone4_test_sample
    python calibrate.py Milestone4_test_sample --extra "a pasted paragraph" --extra-label human

Each sample's label is guessed from its filename (human / ai / borderline),
so the table shows which signal gets each one right and where the midpoint
should go.
"""

import argparse
import json
import sys
from pathlib import Path

from binoculars_signal import binoculars_score, binoculars_signal, ms, MIDPOINT, STEEPNESS

TEXT_KEYS = ("text", "input", "content", "paragraph", "body", "sample", "prompt")


def extract_text(obj):
    """Find the text in whatever shape the JSON has."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in TEXT_KEYS:
            if k in obj and isinstance(obj[k], str):
                return obj[k]
        for v in obj.values():            # nested one level, e.g. {"sample": {"text": ...}}
            t = extract_text(v)
            if t:
                return t
    if isinstance(obj, list) and obj:
        return extract_text(obj[0])
    return None


def guess_label(name):
    n = name.lower()
    if "human" in n:
        return "human"
    if "borderline" in n:
        return "borderline"
    if "ai" in n:
        return "ai"
    return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--extra", action="append", default=[], help="a pasted paragraph to score too")
    ap.add_argument("--extra-label", action="append", default=[], help="label for each --extra")
    args = ap.parse_args()

    samples = []
    for path in sorted(Path(args.folder).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"skipping {path.name}: not valid JSON ({exc})")
            continue
        text = extract_text(data)
        if not text:
            top = list(data.keys()) if isinstance(data, dict) else type(data).__name__
            print(f"skipping {path.name}: couldn't find the text (top-level keys: {top})")
            continue
        samples.append((path.stem, guess_label(path.stem), text))

    for i, text in enumerate(args.extra):
        label = args.extra_label[i] if i < len(args.extra_label) else "?"
        samples.append((f"extra_{i + 1}", label, text))

    if not samples:
        sys.exit("no samples found")

    print(f"\nmidpoint {MIDPOINT}  steepness {STEEPNESS}\n")
    header = f"{'sample':<36} {'label':<10} {'words':>5} {'ppl':>7} {'B':>7} {'model_sig':>10} {'binoc_sig':>10}"
    print(header)
    print("-" * len(header))

    rows = []
    for name, label, text in samples:
        try:
            r = binoculars_score(text)
            m = ms.model_signal(text)
            b_sig = binoculars_signal(text)
        except ms.TextTooShortError:
            print(f"{name:<36} {label:<10}   (too short)")
            continue
        rows.append((name, label, len(text.split()), r["perplexity"], r["B"], m, b_sig))
        print(f"{name:<36} {label:<10} {len(text.split()):>5} {r['perplexity']:>7.1f} "
              f"{r['B']:>7.3f} {m:>10.3f} {b_sig:>10.3f}")

    # suggest a midpoint from the labeled rows
    ai_b = [r[4] for r in rows if r[1] == "ai"]
    hu_b = [r[4] for r in rows if r[1] == "human"]
    if ai_b and hu_b:
        hi_ai, lo_hu = max(ai_b), min(hu_b)
        print(f"\nB range  ai: {min(ai_b):.3f}–{hi_ai:.3f}   human: {lo_hu:.3f}–{max(hu_b):.3f}")
        if hi_ai < lo_hu:
            print(f"clean separation; suggested BINOCULARS_MIDPOINT = {(hi_ai + lo_hu) / 2:.3f}")
        else:
            print("ai and human B ranges overlap — this pair isn't separating these samples")


if __name__ == "__main__":
    main()