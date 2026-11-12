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

# Make the project modules importable no matter which directory this is run from:
# look next to this script first, then in the current directory.
HERE = Path(__file__).resolve().parent
for p in (HERE, Path.cwd()):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from binoculars_signal import binoculars_score, binoculars_signal, ms, MIDPOINT, STEEPNESS  # noqa: E402

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
    ap.add_argument("folders", nargs="+", help="one or more folders of *.json samples")
    ap.add_argument("--extra", action="append", default=[], help="a pasted paragraph to score too")
    ap.add_argument("--extra-label", action="append", default=[], help="label for each --extra")
    ap.add_argument("--fit", action="store_true",
                    help="fit BINOCULARS_MIDPOINT / STEEPNESS from the labeled rows")
    ap.add_argument("--max-fpr", type=float, default=0.4,
                    help="false-positive ceiling for the threshold rule (default 0.4)")
    args = ap.parse_args()

    samples = []
    for folder in args.folders:
        for path in sorted(Path(folder).glob("*.json")):
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
            samples.append((f"{Path(folder).name}/{path.stem}", guess_label(path.stem), text))

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

    if args.fit:
        fit(ai_b, hu_b, args.max_fpr)


def fit(ai_b, hu_b, max_fpr):
    """
    Two rules for turning labeled B values into config numbers.

    Rule 1 — logistic fit. The 0–1 signal is 1 / (1 + exp(STEEPNESS * (B - MIDPOINT))).
    A one-feature logistic regression of label on B gives P(ai) = 1 / (1 + exp(-(a*B + c))),
    which is the same curve with STEEPNESS = -a and MIDPOINT = -c / a. Least wrong on
    the data as a whole.

    Rule 2 — FPR-constrained threshold on B. Sweep candidate midpoints; keep those where
    at most max_fpr of the human samples fall on the AI side; of those, pick the one that
    catches the most AI samples. This is your project's own criterion applied directly.
    """
    import numpy as np

    n_ai, n_hu = len(ai_b), len(hu_b)
    print(f"\n=== fit on {n_ai} ai + {n_hu} human samples (max FPR {max_fpr}) ===")
    if n_ai < 5 or n_hu < 5:
        print("WARNING: fewer than 5 per class — these numbers will not generalize. "
              "Treat them as a first guess and keep collecting samples.")

    B = np.array(ai_b + hu_b, dtype=float)
    y = np.array([1] * n_ai + [0] * n_hu)

    # --- Rule 1: logistic fit ---------------------------------------------------
    try:
        from sklearn.linear_model import LogisticRegression
        # weak regularization so the fit follows the data; balanced so class sizes don't skew it
        lr = LogisticRegression(C=100.0, class_weight="balanced").fit(B.reshape(-1, 1), y)
        a, c = float(lr.coef_[0][0]), float(lr.intercept_[0])
        if a < 0:
            print(f"rule 1 (logistic fit):  BINOCULARS_MIDPOINT = {-c / a:.3f}   "
                  f"BINOCULARS_STEEPNESS = {-a:.1f}")
        else:
            print("rule 1 (logistic fit):  slope has the wrong sign — B is not separating ai from human")
    except ImportError:
        print("rule 1 skipped: scikit-learn not installed")

    # --- Rule 2: FPR-constrained threshold --------------------------------------
    best_t, best_tpr, best_fpr = None, -1.0, None
    for t in np.linspace(B.min(), B.max(), 200):
        flagged_ai = (B[y == 1] < t).mean()      # ai samples correctly on the AI side (B below t)
        flagged_hu = (B[y == 0] < t).mean()      # human samples wrongly on the AI side
        if flagged_hu <= max_fpr and flagged_ai > best_tpr:
            best_t, best_tpr, best_fpr = float(t), float(flagged_ai), float(flagged_hu)
    if best_t is None:
        print("rule 2: no threshold satisfies the FPR ceiling")
    else:
        print(f"rule 2 (FPR <= {max_fpr}):  BINOCULARS_MIDPOINT = {best_t:.3f}   "
              f"(catches {best_tpr:.0%} of ai, flags {best_fpr:.0%} of human)")
        print("   steepness is not set by this rule; keep rule 1's, or ~20 for a GPT-2 pair")


if __name__ == "__main__":
    main()