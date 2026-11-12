#!/usr/bin/env python3
"""Download HC3 and export human/AI answers containing 5–10 sentences.

Run from the project directory:
    python download_hc3_samples.py
    python download_hc3_samples.py --min-sentences 5 --max-sentences 10

Files are saved under ./Hugging_face_dataset by default. The source all.jsonl
is the same data used by Hello-SimpleAI/HC3's "all" configuration. Downloading
it directly needs only requests, which is already in requirements.txt.
Rerunning replaces these generated files. No text is sent to the local API.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import requests


DATASET_ID = "Hello-SimpleAI/HC3"
DATASET_PAGE = f"https://huggingface.co/datasets/{DATASET_ID}"
DATASET_REVISION = "4d0ff18143b5a7e1b1e79beb540c04549d1e59d3"
SOURCE_BASE_URL = f"{DATASET_PAGE}/resolve/{DATASET_REVISION}"
DEFAULT_OUTPUT_DIR = Path("Hugging_face_dataset")
MIN_SENTENCES = 5
MAX_SENTENCES = 10


def n_sent(text: str) -> int:
    """Count sentences using the exact splitter from the supplied example."""
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


def download_file(url: str, destination: Path) -> None:
    """Download to a temporary file, then replace the destination on success."""
    temporary = destination.with_name(destination.name + ".part")
    print(f"Downloading {destination.name}...", flush=True)
    try:
        with requests.get(url, stream=True, timeout=(15, 60)) as response:
            response.raise_for_status()
            with temporary.open("wb") as output:
                downloaded = 0
                next_progress = 10 * 1024 * 1024
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    output.write(chunk)
                    downloaded += len(chunk)
                    if downloaded >= next_progress:
                        print(f"  {downloaded / (1024 * 1024):.0f} MiB downloaded", flush=True)
                        next_progress += 10 * 1024 * 1024
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def export_samples(
    source: Path, output_dir: Path, min_sentences: int, max_sentences: int
) -> dict[str, int]:
    """Write each matching answer as a labeled JSONL record, preserving its text."""
    counts = {"human": 0, "ai": 0}
    human_path = output_dir / "human.jsonl"
    ai_path = output_dir / "ai.jsonl"
    human_part = output_dir / "human.jsonl.part"
    ai_part = output_dir / "ai.jsonl.part"
    try:
        with source.open(encoding="utf-8") as rows, human_part.open(
            "w", encoding="utf-8"
        ) as human_file, ai_part.open("w", encoding="utf-8") as ai_file:
            for row_index, line in enumerate(rows):
                row = json.loads(line)
                for field, label, output in (
                    ("human_answers", "human", human_file),
                    ("chatgpt_answers", "ai", ai_file),
                ):
                    for answer_index, answer in enumerate(row[field]):
                        sentence_count = n_sent(answer)
                        if min_sentences <= sentence_count <= max_sentences:
                            record = {
                                "text": answer,
                                "label": label,
                                "sentence_count": sentence_count,
                                "source": row.get("source"),
                                "source_row": row_index,
                                "answer_index": answer_index,
                            }
                            output.write(json.dumps(record, ensure_ascii=False) + "\n")
                            counts[label] += 1
        human_part.replace(human_path)
        ai_part.replace(ai_path)
    finally:
        human_part.unlink(missing_ok=True)
        ai_part.unlink(missing_ok=True)
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--min-sentences", type=int, default=MIN_SENTENCES)
    parser.add_argument("--max-sentences", type=int, default=MAX_SENTENCES)
    args = parser.parse_args(argv)
    if args.min_sentences < 1 or args.max_sentences < args.min_sentences:
        parser.error("Sentence limits must satisfy 1 <= min-sentences <= max-sentences.")

    output_dir = args.output_dir.resolve()
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        download_file(f"{SOURCE_BASE_URL}/all.jsonl", output_dir / "all.jsonl")
        download_file(f"{SOURCE_BASE_URL}/README.md", output_dir / "README.md")
        print(f"Selecting answers with {args.min_sentences}–{args.max_sentences} sentences...", flush=True)
        counts = export_samples(
            output_dir / "all.jsonl", output_dir, args.min_sentences, args.max_sentences
        )
        metadata = {
            "dataset": DATASET_ID,
            "dataset_page": DATASET_PAGE,
            "revision": DATASET_REVISION,
            "source_url": f"{SOURCE_BASE_URL}/all.jsonl",
            "license": "cc-by-sa-4.0",
            "min_sentences": args.min_sentences,
            "max_sentences": args.max_sentences,
            "counts": counts,
        }
        (output_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
    except (requests.RequestException, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"HC3 download/export failed: {exc}", file=sys.stderr)
        return 1

    print(f"Human samples: {counts['human']}")
    print(f"AI samples:    {counts['ai']}")
    print(f"Saved source data, samples, and metadata to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
