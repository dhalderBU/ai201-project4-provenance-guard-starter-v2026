"""
Fit DETECTOR_MIDPOINT and DETECTOR_STEEPNESS for the perplexity signal.

model_signal() squashes perplexity with

    score = 1 / (1 + (ppl / midpoint) ** steepness)

which is a logistic on ln(ppl) with slope `steepness` and centre ln(midpoint).
A one-feature logistic regression of label on ln(ppl) gives

    P(ai) = 1 / (1 + exp(-(a * ln(ppl) + c)))

so   steepness = -a   and   midpoint = exp(-c / a).

Run it on the SAME calibration split used for Binoculars so the two signals
are fitted to the same data and the same model:

    python fit_perplexity.py calibration_samples/hc3_50_100/calibration
    python fit_perplexity.py calibration_samples/hc3_50_100/calibration --max-fpr 0.2
    python fit_perplexity.py <cal folder> --validate calibration_samples/hc3_50_100/validation

Labels come from filenames (human / ai; borderline is skipped).
"""

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE, Path.cwd()):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import config    # noqa: E402
import detector  # noqa: E402

TEXT_KEYS = ("text", "input", "content", "paragraph", "body", "sample", "prompt")


def extract_text(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in TEXT_KEYS:
            if isinstance(obj.get(k), str):
                return obj[k]
        for v in obj.values():
            t = extract_text(v)
            if t:
                return t
    if isinstance(obj, list) and obj:
        return extract_text(obj[0])
    return None


def label_of(name):
    n = name.lower()
    if "human" in n:
        return 0
    if "borderline" in n:
        return None
    if "ai" in n:
        return 1
    return None


def load(folders):
    out = []
    for folder in folders:
        for path in sorted(Path(folder).glob("*.json")):
            lab = label_of(path.stem)
            if lab is None:
                continue
            try:
                text = extract_text(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                text = None
            if text:
                out.append((path.stem, lab, text))
    return out


def score_with(ppl, midpoint, steepness):
    return 1.0 / (1.0 + (ppl / midpoint) ** steepness)


def report(name, rows, midpoint, steepness, max_fpr):
    """Accuracy / FPR / TPR of the perplexity signal at a 0.5 cut, for given constants."""
    import numpy as np
    s = np.array([score_with(p, midpoint, steepness) for _, _, p in rows])
    y = np.array([lab for _, lab, _ in rows])
    pred = s >= 0.5
    fpr = pred[y == 0].mean() if (y == 0).any() else float("nan")
    tpr = pred[y == 1].mean() if (y == 1).any() else float("nan")
    ok = "ok" if fpr <= max_fpr else f"EXCEEDS {max_fpr}"
    print(f"  {name:<34} midpoint {midpoint:6.1f}  steepness {steepness:4.2f}  "
          f"acc {(pred == y).mean():.3f}  fpr {fpr:.3f} ({ok})  tpr {tpr:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+", help="calibration folder(s) of labeled *.json")
    ap.add_argument("--validate", nargs="*", default=[], help="held-out folder(s) to evaluate on")
    ap.add_argument("--max-fpr", type=float, default=0.4)
    args = ap.parse_args()

    import numpy as np
    from sklearn.linear_model import LogisticRegression

    samples = load(args.folders)
    if not samples:
        sys.exit("no labeled samples found")

    print(f"scoring {len(samples)} samples with {config.DETECTOR_MODEL} ...")
    rows = []
    for name, lab, text in samples:
        try:
            rows.append((name, lab, detector.perplexity(text)))
        except detector.TextTooShortError:
            print(f"  {name}: too short, skipped")
    n_ai = sum(1 for _, lab, _ in rows if lab == 1)
    n_hu = len(rows) - n_ai
    print(f"{n_ai} ai, {n_hu} human")
    if n_ai < 5 or n_hu < 5:
        print("WARNING: fewer than 5 per class — treat the fit as a first guess")

    ppl = np.array([p for _, _, p in rows])
    y = np.array([lab for _, lab, _ in rows])
    x = np.log(ppl)
    print(f"perplexity  ai: median {np.median(ppl[y == 1]):.1f}   human: median {np.median(ppl[y == 0]):.1f}")

    # ---- rule 1: logistic fit on ln(ppl) --------------------------------------
    lr = LogisticRegression(C=100.0, class_weight="balanced").fit(x.reshape(-1, 1), y)
    a, c = float(lr.coef_[0][0]), float(lr.intercept_[0])
    if a >= 0:
        sys.exit("slope has the wrong sign — perplexity is not separating ai from human on this set")
    fit_steep = -a
    fit_mid = math.exp(-c / a)

    # ---- rule 2: FPR-constrained midpoint (steepness held at the fitted value) --
    best = None
    for mid in np.exp(np.linspace(x.min(), x.max(), 300)):
        s = score_with(ppl, mid, fit_steep)
        fpr = (s[y == 0] >= 0.5).mean()
        tpr = (s[y == 1] >= 0.5).mean()
        if fpr <= args.max_fpr and (best is None or tpr > best[1]):
            best = (float(mid), tpr, fpr)

    cur_mid = getattr(config, "DETECTOR_MIDPOINT", 45.0)
    cur_steep = getattr(config, "DETECTOR_STEEPNESS", 1.6)

    print("\n=== on the calibration set ===")
    report("current config", rows, cur_mid, cur_steep, args.max_fpr)
    report("rule 1 (logistic fit)", rows, fit_mid, fit_steep, args.max_fpr)
    if best:
        report(f"rule 2 (FPR <= {args.max_fpr})", rows, best[0], fit_steep, args.max_fpr)

    if args.validate:
        val = []
        for name, lab, text in load(args.validate):
            try:
                val.append((name, lab, detector.perplexity(text)))
            except detector.TextTooShortError:
                pass
        if val:
            print(f"\n=== on the validation set ({len(val)} samples) ===")
            report("current config", val, cur_mid, cur_steep, args.max_fpr)
            report("rule 1 (logistic fit)", val, fit_mid, fit_steep, args.max_fpr)
            if best:
                report(f"rule 2 (FPR <= {args.max_fpr})", val, best[0], fit_steep, args.max_fpr)

    print("\nput in config.py:")
    print(f"DETECTOR_MIDPOINT = {fit_mid:.1f}")
    print(f"DETECTOR_STEEPNESS = {fit_steep:.2f}")
    if best and abs(math.log(best[0]) - math.log(fit_mid)) > 0.1:
        print(f"# or, if rule 2's FPR matters more:  DETECTOR_MIDPOINT = {best[0]:.1f}")


if __name__ == "__main__":
    main()