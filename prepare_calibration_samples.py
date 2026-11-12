"""Export original HC3 answers as JSON samples for the calibration scripts.

    .venv/bin/python prepare_calibration_samples.py

Defaults: 50–100 whitespace-separated words, 150 examples per class in each
of two splits. The full downloaded HC3 all.jsonl must already exist locally.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import random

import stylometry


def normalize(text):
    return " ".join(text.split())


def length_band(count):
    return "50-59" if count < 60 else "60-79" if count < 80 else "80-100"


def select_samples(source_dir, per_class, seed):
    """Keep whole prompts in one split and match source/length across labels."""
    pools = {"ai": [], "human": []}
    seen_text = {}
    ambiguous = set()
    with (source_dir / "all.jsonl").open(encoding="utf-8") as source:
        for source_row, line in enumerate(source):
            original = json.loads(line)
            for label, field in (("human", "human_answers"), ("ai", "chatgpt_answers")):
                for answer_index, text in enumerate(original[field]):
                    count = len(text.split())
                    if not 50 <= count <= 100:
                        continue
                    sentence_count = len(stylometry.sentences(text))
                    if (len(stylometry.words(text)) < stylometry.MIN_STYLE_WORDS
                            or sentence_count < stylometry.MIN_STYLE_SENTENCES):
                        continue
                    key = normalize(text)
                    if key in seen_text:
                        if seen_text[key] != label:
                            ambiguous.add(key)
                        continue
                    seen_text[key] = label
                    pools[label].append(dict(text=text, label=label, word_count=count,
                                             source=original["source"], source_row=source_row,
                                             answer_index=answer_index, sentence_count=sentence_count))
    common_sources = {r["source"] for r in pools["ai"]} & {r["source"] for r in pools["human"]}
    pools = {label: [r for r in rows if r["source"] in common_sources and normalize(r["text"]) not in ambiguous]
             for label, rows in pools.items()}
    groups = sorted({r["source_row"] for rows in pools.values() for r in rows})
    rng = random.Random(seed)
    rng.shuffle(groups)
    calibration_groups = set(groups[:len(groups) // 2])
    # Include shorter answers deliberately; sampling at natural prevalence
    # would make almost the entire evaluation set 80–100 words long.
    band_targets = {"50-59": per_class // 15, "60-79": 2 * per_class // 5}
    band_targets["80-100"] = per_class - sum(band_targets.values())
    selected = []
    for split in ("calibration", "validation"):
        def in_split(row):
            return (row["source_row"] in calibration_groups) == (split == "calibration")
        ai_rows = [r for r in pools["ai"] if in_split(r)]
        human_rows = [r for r in pools["human"] if in_split(r)]
        rng.shuffle(ai_rows)
        rng.shuffle(human_rows)
        ai_groups_used, human_groups_used = set(), set()
        band_counts = Counter()
        count = 0
        for ai in ai_rows:
            if ai["source_row"] in ai_groups_used:
                continue
            band = length_band(ai["word_count"])
            if band_counts[band] >= band_targets[band]:
                continue
            matches = [h for h in human_rows
                       if h["source"] == ai["source"]
                       and length_band(h["word_count"]) == length_band(ai["word_count"])
                       and h["source_row"] not in human_groups_used]
            if not matches:
                continue
            human = min(matches, key=lambda h: abs(h["word_count"] - ai["word_count"]))
            selected.extend(dict(row, split=split) for row in (ai, human))
            ai_groups_used.add(ai["source_row"])
            human_groups_used.add(human["source_row"])
            band_counts[band] += 1
            count += 1
            if count == per_class:
                break
        if count < per_class:
            raise ValueError(f"Only {count} matched examples per class available in {split} ({dict(band_counts)}); reduce --per-class.")
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path("Hugging_face_dataset"))
    parser.add_argument("--output-dir", type=Path, default=Path("calibration_samples/hc3_50_100"))
    parser.add_argument("--per-class", type=int, default=150)
    parser.add_argument("--seed", type=int, default=20261111)
    args = parser.parse_args()
    if args.per_class < 1:
        parser.error("--per-class must be positive")
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error("Output directory is not empty; choose a new --output-dir to preserve existing samples.")
    selected = select_samples(args.source_dir, args.per_class, args.seed)
    source_metadata = json.loads((args.source_dir / "metadata.json").read_text())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for row in selected:
        filename = f"{row['label']}_{row['source_row']:08d}_{row['answer_index']:02d}.json"
        relative = Path(row["split"]) / filename
        path = args.output_dir / relative
        path.parent.mkdir(exist_ok=True)
        sample = dict(row, creator_id=f"hc3_{row['label']}_{row['source_row']}_{row['answer_index']}",
                      dataset=source_metadata["dataset"], dataset_revision=source_metadata["revision"])
        path.write_text(json.dumps(sample, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest.append(dict(file=str(relative), **{k:v for k,v in sample.items() if k != "text"}))
    metadata = {
        "dataset": source_metadata["dataset"], "dataset_page": source_metadata["dataset_page"],
        "dataset_revision": source_metadata["revision"], "license": source_metadata.get("license"),
        "source_file": str(args.source_dir / "all.jsonl"),
        "seed": args.seed, "min_words": 50, "max_words": 100,
        "word_count_method": "len(text.split())", "text_truncated": False,
        "minimum_style_words": stylometry.MIN_STYLE_WORDS,
        "minimum_sentences": stylometry.MIN_STYLE_SENTENCES,
        "selection": "Matched class counts by source and length band, with nearest word count; source questions do not cross splits.",
        "samples": manifest,
    }
    (args.output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    lines = ["# HC3 calibration samples: 50–100 words", "",
             f"Source: [{source_metadata['dataset']}]({source_metadata['dataset_page']})",
             f"at revision `{source_metadata['revision']}`. Seed: `{args.seed}`.", "",
             "Each file contains one original, unmodified answer. Length is `len(text.split())`, matching the app's Binoculars gate.",
             "Samples come from the full `all.jsonl`, including answers outside the earlier 5–10 sentence export. Each meets the style signal's minimum of 40 tokenized words and three sentences.", "",
             "| Split | Human | AI | Total |", "|---|---:|---:|---:|"]
    for split in ("calibration", "validation"):
        counts = Counter(r["label"] for r in selected if r["split"] == split)
        lines.append(f"| {split} | {counts['human']} | {counts['ai']} | {sum(counts.values())} |")
    lines.extend(["", "| Words | Human per split | AI per split |", "|---|---:|---:|"])
    for band in ("50-59", "60-79", "80-100"):
        count = sum(r["split"] == "calibration" and r["label"] == "human" and length_band(r["word_count"]) == band for r in selected)
        lines.append(f"| {band} | {count} | {count} |")
    lines.extend(["", "Class counts match by source and length band. Exact duplicate texts are removed; answers from a source question stay in one split.",
                  "Use calibration to choose parameters, then validation to measure them. Do not combine the folders when fitting.",
                  "The 50–59 word group remains small. Results apply to these HC3 answers, not texts below 50 words, one- or two-sentence inputs, or newer generators.", "",
                  "Run from the repository root:", "", "```bash",
                  f"AI201_DEVICE=mps .venv/bin/python calibrate.py {args.output_dir}/calibration --fit --max-fpr 0.2",
                  f"AI201_DEVICE=mps .venv/bin/python calibrate_combined.py {args.output_dir}/calibration --max-fpr 0.2 --min-words 100",
                  f"AI201_DEVICE=mps .venv/bin/python calibrate.py {args.output_dir}/validation",
                  "```", "",
                  "The 20% false-positive ceiling is a stricter trial target than the project's existing 40% acceptance ceiling.",
                  "The scripts only report values; they do not update config.py. `--min-words` splits the report and does not change the app's Binoculars gate.",
                  "Do not use a sweep fitted on validation data as your next settings. Evaluate fixed settings and report false positives, AI recall, and unsure counts.", "",
                  "License and attribution: the local source metadata records CC-BY-SA-4.0. The HC3 dataset card notes that stricter upstream source licenses still apply.",
                  "Citation: Guo et al. (2023), *How Close is ChatGPT to Human Experts? Comparison Corpus, Evaluation, and Detection*, arXiv:2301.07597.", ""])
    (args.output_dir / "README.md").write_text("\n".join(lines))
    print(f"Created {len(selected)} sample files in {args.output_dir}")
    print(f"Each split: {args.per_class} human + {args.per_class} AI")
    print("Length bands:", dict(Counter((r['split'], length_band(r['word_count'])) for r in selected)))


if __name__ == "__main__":
    main()
