"""
Calibrate the COMBINED score: the model/style weight and the AI cutoff.

Runs every labeled sample through the same signals /submit uses (perplexity,
Binoculars, stylometry), then sweeps WEIGHT_MODEL_SIGNAL and the AI cutoff
together and reports which combinations keep the human false-positive rate
under the ceiling while catching the most AI.

    python calibrate_combined.py Milestone4_test_sample samples
    python calibrate_combined.py Milestone4_test_sample samples --max-fpr 0.4 --min-words 80

Labels come from filenames (human / ai; borderline rows are shown but not fitted).
Requires no running server: it imports detector, binoculars_signal and
stylometry directly.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE, Path.cwd()):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import config                                   # noqa: E402
import detector                                 # noqa: E402
import binoculars_signal                        # noqa: E402
import stylometry                               # noqa: E402

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


def guess_label(name):
    n = name.lower()
    if "human" in n:
        return "human"
    if "borderline" in n:
        return "borderline"
    if "ai" in n:
        return "ai"
    return "?"


def load_samples(folders):
    out = []
    for folder in folders:
        for path in sorted(Path(folder).glob("*.json")):
            try:
                text = extract_text(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                text = None
            if text:
                out.append((f"{Path(folder).name}/{path.stem}", guess_label(path.stem), text))
            else:
                print(f"skipping {path}: no text found")
    return out


def score_all(samples):
    """One row per sample: the three raw signals plus the model term /submit builds."""
    rows = []
    for name, label, text in samples:
        try:
            ppl = detector.model_signal(text)
            sty = stylometry.style_signal(text)
        except (detector.TextTooShortError, stylometry.TextTooShortError):
            print(f"{name}: too short, skipped")
            continue
        try:
            bino = binoculars_signal.binoculars_signal(text)
        except detector.DetectorUnavailable:
            bino = None
        # same rule as /submit: Binoculars only counts at or above BINOCULARS_MIN_WORDS,
        # and the blend is whatever scoring.combine_model_signals does (config weights).
        min_words = getattr(config, "BINOCULARS_MIN_WORDS", 100)
        use_bino = bino is not None and len(text.split()) >= min_words
        if use_bino:
            try:
                import scoring
                model = scoring.combine_model_signals(ppl, bino)
            except (ImportError, AttributeError):
                wp = getattr(config, "MODEL_WEIGHT_PERPLEXITY", 0.5)
                wb = getattr(config, "MODEL_WEIGHT_BINOCULARS", 0.5)
                model = wp * ppl + wb * bino
        else:
            model = ppl
        rows.append({"name": name, "label": label, "words": len(text.split()),
                     "ppl_sig": ppl, "bino_sig": bino, "model": model, "style": sty})
    return rows


def combined(row, w_model):
    return w_model * row["model"] + (1.0 - w_model) * row["style"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--max-fpr", type=float, default=0.4, help="max share of human samples labeled ai")
    ap.add_argument("--min-words", type=int, default=0,
                    help="also report the sweep restricted to samples with at least this many words")
    args = ap.parse_args()

    w_now = getattr(config, "WEIGHT_MODEL_SIGNAL", 0.7)
    ai_cut_now = None
    for attr in ("AI_THRESHOLD", "AI_CUTOFF", "THRESHOLD_AI", "LABEL_AI_THRESHOLD"):
        if hasattr(config, attr):
            ai_cut_now = getattr(config, attr)
            break

    rows = score_all(load_samples(args.folders))
    if not rows:
        sys.exit("no scorable samples")

    # ---- table ------------------------------------------------------------------
    print(f"\ncurrent config: WEIGHT_MODEL_SIGNAL={w_now}  ai cutoff={ai_cut_now}\n")
    hdr = f"{'sample':<40} {'label':<10} {'words':>5} {'ppl_sig':>8} {'bino_sig':>9} {'model':>7} {'style':>7} {'combined':>9}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        b = "   n/a" if r["bino_sig"] is None else f"{r['bino_sig']:9.3f}"
        print(f"{r['name']:<40} {r['label']:<10} {r['words']:>5} {r['ppl_sig']:>8.3f} {b} "
              f"{r['model']:>7.3f} {r['style']:>7.3f} {combined(r, w_now):>9.3f}")

    # ---- sweep ------------------------------------------------------------------
    def sweep(subset, title):
        ai = [r for r in subset if r["label"] == "ai"]
        hu = [r for r in subset if r["label"] == "human"]
        print(f"\n=== {title}: {len(ai)} ai, {len(hu)} human, ceiling FPR <= {args.max_fpr} ===")
        if not ai or not hu:
            print("need at least one of each label")
            return
        if len(ai) < 5 or len(hu) < 5:
            print("WARNING: fewer than 5 per class — treat as a first guess only")

        # Grid: for each model weight, "ai caught / human flagged" at a set of fixed
        # AI cutoffs, including the one in config. w_model = 0.0 is the style signal
        # alone and 1.0 is the model term alone, so each signal's own worth is visible.
        cuts = sorted({0.4, 0.5, 0.6, 0.7, 0.8} | ({ai_cut_now} if ai_cut_now else set()))
        weights = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        if w_now not in weights:
            weights = sorted(weights + [w_now])

        def cell(w, cut):
            tpr = sum(combined(r, w) >= cut for r in ai) / len(ai)
            fpr = sum(combined(r, w) >= cut for r in hu) / len(hu)
            return tpr, fpr

        print("cells are: ai caught / human flagged   (* = exceeds the FPR ceiling)")
        print(f"{'w_model':>8} " + " ".join(f"{'cut ' + format(c, '.2f'):>13}" for c in cuts) + "   note")
        for w in weights:
            parts = []
            for c in cuts:
                tpr, fpr = cell(w, c)
                flag = "*" if fpr > args.max_fpr else " "
                parts.append(f"{tpr:5.0%} /{fpr:5.0%}{flag}")
            note = ""
            if w == 0.0:
                note = "style only"
            elif w == 1.0:
                note = "model only"
            if abs(w - w_now) < 1e-9:
                note = (note + "  " if note else "") + "<- current weight"
            print(f"{w:>8.2f} " + " ".join(f"{p:>13}" for p in parts) + f"   {note}")

        # The cutoff that catches the most AI under the ceiling, for the current weight,
        # with the FULL feasible range so a floor/ceiling hit is obvious.
        feas = []
        for cut in [c / 100 for c in range(20, 96)]:
            tpr, fpr = cell(w_now, cut)
            if fpr <= args.max_fpr:
                feas.append((tpr, -fpr, cut))
        if feas:
            best_tpr = max(f[0] for f in feas)
            band = [f[2] for f in feas if f[0] == best_tpr]
            lo, hi = min(band), max(band)
            if ai_cut_now:
                tpr_now, fpr_now = cell(w_now, ai_cut_now)
                print(f"\nat the current weight {w_now} and cutoff {ai_cut_now}: "
                      f"catches {tpr_now:.0%} of ai, flags {fpr_now:.0%} of human")
            print(f"highest ai-caught under the ceiling at weight {w_now}: {best_tpr:.0%}, "
                  f"reached by any cutoff in {lo:.2f}–{hi:.2f}"
                  + ("  (hits the sweep floor: the ceiling is loose, not binding)" if lo <= 0.21 else ""))
        print("the human cutoff (clearly_human) is a separate choice; set it below the lowest ai combined score you see")

    sweep(rows, "all samples")
    if args.min_words:
        sweep([r for r in rows if r["words"] >= args.min_words], f"samples with >= {args.min_words} words")
        sweep([r for r in rows if r["words"] < args.min_words], f"samples with < {args.min_words} words")


if __name__ == "__main__":
    main()