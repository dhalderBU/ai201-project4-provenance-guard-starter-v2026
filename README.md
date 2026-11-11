# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> `/ping` checks that the service is running. Use `/submit` to score text and
> `/appeal` to request a review of a saved submission.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does (includes stretch feature)

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->
I estimate how AI-like text looks using perplexity, Binoculars, and style
measurements including MATTR. I treat the result as a heuristic, not proof of
authorship.

1. I accept `text` and an optional `creator_id` at `POST /submit`.
2. I reject invalid JSON, empty text, and insufficient text with HTTP `400`.
3. I calculate perplexity with `detector.model_signal(text)`. At 100 words or
   more, I blend it 50/50 with Binoculars when available; otherwise I use
   perplexity alone.
4. I calculate sentence-length spread, punctuation density, and MATTR with
   `stylometry.style_signal(text)`.
5. I combine 70% model score and 30% style score in `scoring.py::combine_signals`.
6. I select `human`, `unsure`, or `ai` with `scoring.score_to_label` and return
   the corresponding sentence from `scoring.LABEL_TEXT`.
7. I save the text in `logs/submissions.jsonl` and the decision in `logs/audit.jsonl`,
   linked by `content_id`. I offer automatic appeals
   or human verification with supporting text and a reviewer decision.

I link these JSONL files by `content_id`, with one JSON object per line:

| File | What I store |
|---|---|
| `logs/submissions.jsonl` | `timestamp` in UTC (`+00:00`), `content_id`, `creator_id`, `text`, `guess`, `label`, `label_text`, `confidence`, `status` (`"decided"`), `model_score`, `style_score`, `combined_score`, `perplexity_score`, `binoculars_score`, `binoculars_used`, and `word_count`. |
| `logs/audit.jsonl` | Decision scores, labels, status, appeal evidence, and review outcomes. New decisions omit the submitted text. |
| `logs/verified_human_certification_log.jsonl` | Approved certificates with `Certificate_id` and `verified_dt_time` explicitly in UTC. |

I save the same initial decision values in the submission and audit files.
The submission keeps its initial `decided` status; reviews append their outcomes
to the audit log, and `GET /content/<id>` returns the current status.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**

I use `detector.model_signal(text)` to calculate perplexity with a local model,
GPT-2 by default (`config.DETECTOR_MODEL`). Lower perplexity means the text is
easier for that model to predict. I convert it to an AI-oriented score:

```text
perplexity_score = 1 / (1 + (perplexity / 45.0) ** 1.6)
```

I clamp the score to `[0, 1]` and round to four decimals. Higher means more
AI-like; the model scores text rather than identifying its author.

For my stretch feature, I use `binoculars_signal.py::binoculars_signal`, inspired
by Hans et al. (2024),
[*Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text*](https://proceedings.mlr.press/v235/hans24a.html),
published at ICML 2024. I use GPT-2 and DistilGPT-2 with matching tokenizer
vocabularies. My 50/50 blend is a scoring choice in this project.

In `app.py::submit`, I use the blend only when Binoculars succeeds and
`len(text.split()) >= BINOCULARS_MIN_WORDS` (currently `100`):

```python
if binoculars_used:
    model_score = round(0.5 * perplexity_score + 0.5 * binoculars_score, 4)
else:
    model_score = perplexity_score
```

I still calculate and return Binoculars for shorter inputs, but set
`binoculars_used` to `false`. I also use perplexity alone if Binoculars raises
`detector.DetectorUnavailable`. I then combine 70% model and 30% style through
`scoring.py::combine_signals`.

**Why that might differ between human and AI writing:**

I treat predictable phrasing as possible AI-like evidence, but people also
write plainly and repeat familiar expressions. Predictability cannot establish
authorship.

**What it can't see:**

I score only the first 400 tokens (`DETECTOR_MAX_TOKENS`), without editing
history or authorship records. Plain human writing can score high; unusual
vocabulary can lower the score regardless of who wrote it.

### Signal two — the style signal

**What it measures:**

I measure sentence-length spread, structural punctuation density, and
vocabulary diversity using moving-average type-token ratio (MATTR) in
`stylometry.py`. I count lowercase word tokens using `words(text)` and its
`[A-Za-z']+` pattern:

| Method | Raw measurement | Empty-input result |
| --- | --- | --- |
| `sentence_length_spread(text)` | Population standard deviation of sentence token counts divided by their mean | `0.0` |
| `punctuation_density(text)` | Count of `, ; : — – ( )` divided by the total word-token count | `0.0` |
| `moving_average_ttr(text, 50)` via `ttr_measure(text)[0]` | Mean of unique tokens / 50 across overlapping 50-token windows; whole-text TTR at 50 tokens or fewer | `0.0` |

I use `TTR_WINDOW = 50`. `ttr_measure(text)` returns
`(value, ai_anchor, human_anchor)`; the table shows its measurement value.
These empty-input zeros apply to the raw measurements. The combined
`style_signal(text)` requires at least three sentences and 40 word tokens,
otherwise it raises `TextTooShortError`.

**Stretch feature — what MATTR means:**

MATTR means **moving-average type-token ratio**: distinct lowercase words
divided by word occurrences, averaged over sliding windows. I use
`moving_average_ttr(text, 50)` through `ttr_measure(text)` to average windows
1–50, 2–51, and so on. At 50 word tokens or fewer, I use whole-text TTR
with the active MATTR anchors (`0.72`, `0.86`).

I keep `type_token_ratio(text)` available. Setting `TTR_WINDOW = 0` selects
whole-text TTR and its original anchors.

**Why use MATTR (proposed by claude):**

I use MATTR to reduce the length sensitivity of whole-text TTR, which tends
to fall as longer passages repeat words. Equal-sized windows make vocabulary
diversity easier to compare. I follow Covington and McFall (2010),
[*Cutting the Gordian Knot: The Moving-Average Type–Token Ratio (MATTR)*](https://www.tandfonline.com/doi/abs/10.1080/09296171003643098).
I chose the 50-word window and anchors for this project; MATTR measures
vocabulary diversity, not authorship.

Sentence splitting uses whitespace after `.`, `!`, or `?`. Tokenization uses
`[A-Za-z']+`, matching the sample: digits are excluded, straight apostrophes
stay within tokens, and curly apostrophes split tokens. Wordless sentence
fragments remain in the spread distribution, also matching the sample.
Structural punctuation density can exceed `1.0`; it is a raw ratio, not a score.

`style_subscores(text)` converts the measurements into AI-oriented contributions.
For the current MATTR settings, the calculation is:

```python
spread_ai = clamp01((0.60 - spread) / (0.60 - 0.25))
punct_ai = clamp01((density - 0.06) / (0.14 - 0.06))
mattr = moving_average_ttr(text, 50)
mattr_ai = clamp01((0.86 - mattr) / (0.86 - 0.72))

style_score = 0.50 * spread_ai + 0.20 * punct_ai + 0.30 * mattr_ai
```

I call this contribution `mattr_ai` here; the code retains `ttr_ai` and
`STYLE_WEIGHT_TTR`.

`clamp01` limits each contribution to `[0.0, 1.0]`. The style score keeps
full precision. All sample limits, anchors, weights, and label thresholds are
named constants at the top of `stylometry.py`.

| Setting | Constants | Values |
| --- | --- | --- |
| Minimum sample | `MIN_STYLE_SENTENCES`, `MIN_STYLE_WORDS` | `3`, `40` |
| Spread anchors | `SPREAD_AI_ANCHOR`, `SPREAD_HUMAN_ANCHOR` | `0.25`, `0.60` |
| Structural punctuation anchors | `PUNCTUATION_HUMAN_ANCHOR`, `PUNCTUATION_AI_ANCHOR` | `0.06`, `0.14` marks per word |
| MATTR window | `TTR_WINDOW` | `50` word tokens |
| Active MATTR anchors | `MATTR_AI_ANCHOR`, `MATTR_HUMAN_ANCHOR` | `0.72`, `0.86` |
| Whole-text TTR anchors when `TTR_WINDOW = 0` | `TTR_AI_ANCHOR`, `TTR_HUMAN_ANCHOR` | `0.62`, `0.80` |
| Weights | `STYLE_WEIGHT_SPREAD`, `STYLE_WEIGHT_PUNCTUATION`, `STYLE_WEIGHT_TTR` | `0.50`, `0.20`, `0.30` |
| Style decision thresholds | `STYLE_AI_THRESHOLD`, `STYLE_UNCERTAIN_THRESHOLD` | `0.65`, `0.40` |

Both sample minimums must be met. `style_score(text)` and `style_subscores(text)`
return `None` below three sentences or 40 words, exactly as in the supplied
algorithm. `style_signal(text)` preserves its existing float-returning service
signature by raising `TextTooShortError` for insufficient text. The existing
`/submit` handler catches that exception and returns HTTP `400` with a message.

`style_score_to_label(score)` applies these style-only labels:

| Score | Style classification |
| --- | --- |
| `None` | `INSUFFICIENT_DATA` |
| `0.65 <= score <= 1.00` | Likely AI |
| `0.40 <= score < 0.65` | Uncertain |
| `0.00 <= score < 0.40` | Likely Human |

`style_classification(text)` combines scoring and style labeling. The CLI shows
the raw measurements, normalized contributions, combined style score, and label.
The API continues to pass the numeric style signal into its separate
model/style combination; these thresholds do not change that combining rule.

I slide the window across the whole text, without a word-count cutoff. My
anchors need evaluation on labeled samples; they are not authorship boundaries.

**Why that might differ between human and AI writing:**

I treat uniform sentence lengths, frequent structural punctuation, and repeated
vocabulary as possible AI-like patterns. I need samples to test those assumptions.

**What it can't see:**

My style checks cannot identify authorship or understand meaning. Editing
punctuation, sentences, or vocabulary can change the score. MATTR still depends
on window size and topic; short inputs retain whole-text TTR's length sensitivity.
My sentence splitter can misread abbreviations, and my word pattern misses
accented letters and other scripts.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

I combine 70% model score and 30% style score. The model score includes
Binoculars only when the conditions above are met. Both inputs are in `[0, 1]`,
so their weighted average stays in that range. I give the model more influence
when they disagree, which also gives its mistakes more influence.

**Trace of an unsure result — hypothetical scenario:**

I use imaginary scores below to illustrate the flow; this is not a test run.

1. **The writer enters their text.** A writer submits the following passage as their own original work:

   > Every morning I take my dog out before work. Today the mist was still hanging over the park, and we stopped near the gate while a neighbor looked for her keys. I got home a little late, so I ate breakfast standing beside the sink.

2. **The service receives the submission.** The website sends the passage in
   `text`, along with the caller's `creator_id`, to `POST /submit`. The route
   parses the JSON and checks the input. This passage is non-empty and meets
   the style signal's minimum of three sentences and 40 words.

3. **Model score.** I assume `detector.model_signal(text)` returns `0.7`.
   This passage is under 100 words, so I use perplexity alone.

4. **Style score.** I assume `stylometry.style_signal(text)` returns `0.30`;
   this is an illustrative value, not a measurement of the passage.

5. **The service combines the scores and chooses a label.**
   `scoring.combine_signals(0.7, 0.30)` calculates `(0.7 * 0.7) + (0.3 * 0.30) = 0.58`.
   The route passes the combined score to `scoring.score_to_label()`, which
   returns `("unsure", 0.58)` because `0.40 < 0.58 < 0.60`.

6. **The writer sees the assessment.** The service generates a
   `content_id`, logs the decision and scores, and returns JSON containing the
   ID, `guess`, `label`, `label_text`, `confidence`, `combined_score`,
   `model_score`, and `style_score`. The `label_text` field contains:

   > We do not have enough evidence to determine how this text was written. The writer can request a review.
7. **The writer appeals.** The writer submits the returned `content_id` and
   their reasoning to `POST /appeal`. The endpoint records the appeal as
   `under_review` and rechecks the original text and the two versions with a
   boundary sentence removed. For this three-sentence example, both shortened
   versions fall below the style signal's three-sentence minimum and vote
   unsure. The majority is therefore unsure, and the message is:

   > Based on revaluation we do not have enough evidence to determine how this text was written. Your appeal has been recorded.

**The numbers:**

- `WEIGHT_MODEL_SIGNAL = 0.7`
- `WEIGHT_STYLE_SIGNAL = 0.3`
- The weights add up to `1.0`.
- `HUMAN_THRESHOLD = 0.40`
- `AI_THRESHOLD = 0.60`

```text
combined_score = (0.7 * model_score) + (0.3 * style_score)
```

I define the final thresholds in `config.py`: human at `score <= 0.40`, unsure
at `0.40 < score < 0.60`, and AI at `score >= 0.60`. These differ from the
style-only thresholds. I treat the combined score as a heuristic, not a
calibrated probability.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->
It lives in `scoring.py::combine_signals`
**A case where my two signals split, and what my rule does with it:**

I go by total score based on the scoring mechanism. Even if the results slitthe way the scoring is doe the model_score has higher overall weitage compared to stylometry. The model score is also a weighted score 50:50 of the detecotr model and the binocular 2nd model. so the split in decision is ignored instead we take the decision based on the overall computed score.

I recorded this baseline example before Binoculars, MATTR, and the threshold
change. `Milestone4_test_sample/borderline_ai_milestone4.json` returned a model
score of `0.5195` and a style score of `0.6808494097161918`.
The model score lies in the final rule's unsure range, while the style-only
classifier treats the style score as likely AI. This is a measured disagreement
in the strength of the signals.

```text
combined_score = (0.7 * 0.5195) + (0.3 * 0.6808494097161918)
               = 0.5679048229148576
label = unsure
```

The model contributes `0.36365`, and style contributes about `0.204255`.
The combined score stays below the AI threshold of `0.60` and above the human
threshold then set to `0.45`, so the final label is unsure. The audit entry is
`c_df4de07a8019`; its full record appears below.

Disagreement does not always produce unsure. For comparison, hypothetical
scores of model `0.90` and style `0.10` give `0.66`, which receives an AI label.
Reversing them gives `0.34`, which receives a human label. These comparison
values illustrate the model's larger weight; they are not additional test runs.

### Milestone 4 — Input tests and audit evidence

I keep these baseline results unchanged: they used perplexity alone, whole-text
TTR, and a `0.45` human cutoff, before my stretch changes.

My four Milestone 4 entries come from [logs/audit.jsonl](logs/audit.jsonl), lines
164–167, recorded on **November 10, 2026 at 12:58:48 a.m. Pacific Standard
Time** (`2026-11-10T08:58:48+00:00` in the log). The submissions were made with:

```bash
for sample in ./Milestone4_test_sample/*.json; do
  printf '\nTesting %s\n' "$sample"
  curl -i -X POST http://127.0.0.1:5000/submit \
    -H "Content-Type: application/json" \
    --data-binary "@$sample"
  printf '\n'
done
```

The audit records do not store filenames. The mapping below was checked against
the loop's sorted file order, the creator IDs, and a local recalculation of both
signals for each file. All four recalculated signal pairs matched the recorded
values. These checks did not submit new requests or append audit entries.

The separate clearly-human test was already recorded earlier, on **November
10, 2026 at 12:22:26 a.m. Pacific Standard Time**, in audit line 163. It used
`samples/clearly-human.json`. Recalculating both signals for that saved file
matched the earlier entry's creator ID and scores. The table includes that
earlier test alongside the four files from the Milestone 4 batch.

**Recorded results:** Scores in the table are rounded to six decimal places;
the exact logged values are preserved in the JSONL excerpt below. Baseline labels
used `0.7 * model_score + 0.3 * style_score`, with human at `<= 0.45`, AI at
`>= 0.60`, and unsure between those boundaries.

| Test input | File | Model score | Style score | Combined score | Recorded label |
| --- | --- | ---: | ---: | ---: | --- |
| Clearly AI | [clearly-AI_milestone4.json](Milestone4_test_sample/clearly-AI_milestone4.json) | 0.919500 | 0.655224 | 0.840217 | `ai` |
| Clearly human — earlier run | [clearly-human.json](samples/clearly-human.json) | 0.444500 | 0.199291 | 0.370937 | `human` |
| Formal human — designated test category | [clearly-human_milestone4.json](Milestone4_test_sample/clearly-human_milestone4.json) | 0.308100 | 0.455105 | 0.352202 | `human` |
| Lightly-edited AI | [clearly-AI_lightly_editted.json](Milestone4_test_sample/clearly-AI_lightly_editted.json) | 0.832100 | 0.823410 | 0.829493 | `ai` |
| Borderline | [borderline_ai_milestone4.json](Milestone4_test_sample/borderline_ai_milestone4.json) | 0.519500 | 0.680849 | 0.567905 | `unsure` |

**Assignment coverage:** `clearly-human_milestone4.json` is designated as the
formal-human case, and `borderline_ai_milestone4.json` is designated as the
borderline case. Together with the earlier `samples/clearly-human.json` test,
the recorded runs cover all four required categories: clearly AI, clearly
human, formal human, and lightly-edited AI. The borderline input is an
additional test. The clearly-human and formal-human cases use different texts
and different audit entries.

**What the separate signals show:**

1. **Clearly AI:** Both signals support the recorded AI label. The model score
   is `0.9195`, and the style score is about `0.655224`; their weighted result
   is about `0.840217`. The style score is lower than the model score partly
   because structural punctuation contributes zero under the baseline rule.
2. **Formal human:** The final human label matches the supplied test
   category. The model score is `0.3081`, while the style score is higher at
   about `0.455105`, within the style-only uncertain range. Its TTR is `0.68`,
   which becomes a TTR AI sub-score of about `0.666667`; the spread sub-score
   is about `0.510211`, and punctuation contributes zero. Those style rules
   produce some AI-like evidence for this human text, but the model's larger
   weight keeps the final score at about `0.352202`, within the human range.
3. **Lightly-edited AI:** The edited sample receives an AI label: model
   `0.8321`, style about `0.823410`, combined about `0.829493`.
   Its low sentence-length spread (`0.159458`) and low TTR (`0.560694`) both
   map to maximum AI sub-scores of `1.0`. Punctuation contributes a sub-score
   of about `0.117052`. This explains the high style score for the edited
   passage. These measurements describe the edited text; without a paired
   unedited passage, they do not quantify the effect of the edits.
4. **Borderline movie review:** The style signal is more AI-like than the
   model signal. Its TTR (`0.610294`) maps to `ttr_ai = 1.0`, and spread maps
   to `spread_ai = 0.761699`, despite punctuation contributing zero. The final
   score is about `0.567905`, so the result is unsure, consistent with its
   intended borderline role. This checks the uncertainty band; it does not
   establish authorship or replace the separate clearly-human test.
5. **Clearly human, from the earlier run:** The model score is `0.4445`, and
   the style score is about `0.199291`. Both fall in their respective human
   ranges. The weighted calculation is
   `(0.7 * 0.4445) + (0.3 * 0.19929078014184398) = 0.3709372340425532`,
   which receives a human label. Its audit ID is `c_e7713e4b8ef4`.

These are diagnostics of five selected samples, not an accuracy estimate.
The style measurements and sub-scores above were recalculated from the saved
texts; they are not additional fields claimed to be in the original audit log.

**The earlier clearly-human audit entry:**

```jsonl
{"timestamp": "2026-11-10T08:22:26+00:00", "content_id": "c_e7713e4b8ef4", "creator_id": "demo_instructor", "guess": null, "model_score": 0.4445, "style_score": 0.19929078014184398, "combined_score": 0.3709372340425532, "label": "human", "status": "decided", "confidence": 0.3709372340425532}
```

**The four original audit entries, in submission order: borderline, lightly-edited AI, clearly AI, and the designated formal-human sample:**

```jsonl
{"timestamp": "2026-11-10T08:58:48+00:00", "content_id": "c_df4de07a8019", "creator_id": "demo_instructor", "guess": null, "model_score": 0.5195, "style_score": 0.6808494097161918, "combined_score": 0.5679048229148576, "label": "unsure", "status": "decided", "confidence": 0.5679048229148576}
{"timestamp": "2026-11-10T08:58:48+00:00", "content_id": "c_826437d6b820", "creator_id": "deb_demo_instructor", "guess": null, "model_score": 0.8321, "style_score": 0.8234104046242774, "combined_score": 0.8294931213872831, "label": "ai", "status": "decided", "confidence": 0.8294931213872831}
{"timestamp": "2026-11-10T08:58:48+00:00", "content_id": "c_f6d165650e97", "creator_id": "deb_demo_instructor", "guess": null, "model_score": 0.9195, "style_score": 0.6552244389917785, "combined_score": 0.8402173316975334, "label": "ai", "status": "decided", "confidence": 0.8402173316975334}
{"timestamp": "2026-11-10T08:58:48+00:00", "content_id": "c_67cdde910c80", "creator_id": "deb_demo_instructor", "guess": null, "model_score": 0.3081, "style_score": 0.4551054998369862, "combined_score": 0.3522016499510958, "label": "human", "status": "decided", "confidence": 0.3522016499510958}
```

`app.py::submit` already passes `model_score`, `style_score`, and
`combined_score` to `audit.log_decision`, which writes them in each decision
record. These four entries verify that all three scores are logged together.
The recorded classification is in `label`; the legacy `guess` field is `null`
in this run and is reproduced unchanged above.

---

**API endpoint details / shape:**

| Endpoint | Request fields | Response fields |
|---|---|---|
| `POST /submit` | `text`, `creator_id` | `content_id`, `guess`, `label`, `label_text`, `confidence`, `combined_score`, `model_score`, `style_score` |
| `POST /appeal` — automatic | `content_id`, `reasoning`; `review_type="automatic"` or omitted | HTTP `200`: `content_id`, `appeal_id`, `review_type`, `status`, `label`, `label_text`, `message`, `votes`, `evaluations`, `weights` |
| `POST /appeal` — human verification | `content_id`, `reasoning`, `review_type="human_verification"`, `additional_text` | HTTP `202`: `content_id`, `verification_request_id`, `review_type`, `status`, `message` |
| `POST /verification/review` | `content_id`, `status`; optional `reviewer`, `review_notes` | `content_id`, `verification_request_id`, `status`, `credential` |
| `GET /verification/review/<id>` | Content ID in the URL; prior human-verification request | `content_id`, `submission`, `decision`, `verification_request`, `review` (null while pending) |
| `GET /content/<id>` | Content ID in the URL | `content_id`, `status`, `credential`; also `verification_request_id` and `verification_status` after a human-verification request. Unknown IDs return HTTP `404`. |
| `GET /log` | Optional query parameters: `content_id`, `limit` | `count`, `entries`; filtering by `content_id` shows the original decision and subsequent appeal events. |

I return the same classification in `guess` and `label`, with its sentence in
`label_text`. I set `confidence = combined_score`; it measures AI-likeness,
not certainty. I default an omitted `creator_id` to `"unknown"`.

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

I use `scoring.score_to_label` for the label and `scoring.LABEL_TEXT` for the
message. I return and log both. These ranges match `config.py`; for example,
`score_to_label(0.20)` returns `("human", 0.20)`.

| API label | Score range | Exact `label_text` returned to the reader |
|---|---|---|
| `human` | `0.00 ≤ score ≤ 0.40` | `Our checks  suggest this text was written by a person. This assessment can be wrong.` |
| `unsure` | `0.40 < score < 0.60` | We do not have enough evidence to determine how this text was written. The writer can request a review. |
| `ai` | `0.60 ≤ score ≤ 1.00` | Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review. |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

I acknowledge uncertainty and offer an appeal without accusing the writer.
I offer either an automatic recheck or human verification based on supporting
text. Certification requires a reviewer decision.

### Milestone 5 — Verified label responses

I preserve these baseline responses from before Binoculars, MATTR, and the
human-cutoff change from `0.45` to `0.40`.

On **November 10, 2026 at 1:20:16 a.m. Pacific Standard Time**, the three saved
texts below were submitted to the running `POST /submit` service with
`creator_id = "milestone5_label_verification"`. All three requests returned
HTTP `200`. The model and style signals ran on the actual text without mocks.
The responses below were captured from those requests and matched their audit
entries in [logs/audit.jsonl](logs/audit.jsonl), lines 168–170.

I captured these before adding `guess` as an alias for `label`. My API table
above lists the current response fields.

| Submitted text | Returned label | Combined score (rounded) | Audit/content ID |
| --- | --- | ---: | --- |
| [clearly-human.json](samples/clearly-human.json) | `human` | 0.370937 | `c_f3096c136035` |
| [borderline_ai_milestone4.json](Milestone4_test_sample/borderline_ai_milestone4.json) | `unsure` | 0.567905 | `c_fa3392918623` |
| [clearly-AI_milestone4.json](Milestone4_test_sample/clearly-AI_milestone4.json) | `ai` | 0.840217 | `c_4dbfc96d2186` |

**Human response:**

```json
{
  "combined_score": 0.3709372340425532,
  "confidence": 0.3709372340425532,
  "content_id": "c_f3096c136035",
  "label": "human",
  "label_text": "Our checks suggest this text was written by a person. This assessment can be wrong.",
  "model_score": 0.4445,
  "style_score": 0.19929078014184398
}
```

**Unsure response:**

```json
{
  "combined_score": 0.5679048229148576,
  "confidence": 0.5679048229148576,
  "content_id": "c_fa3392918623",
  "label": "unsure",
  "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.",
  "model_score": 0.5195,
  "style_score": 0.6808494097161918
}
```

**AI response:**

```json
{
  "combined_score": 0.8402173316975334,
  "confidence": 0.8402173316975334,
  "content_id": "c_4dbfc96d2186",
  "label": "ai",
  "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
  "model_score": 0.9195,
  "style_score": 0.6552244389917785
}
```

My baseline checks reached all three labels and verified the old `0.45` human
cutoff and `0.60` AI cutoff. I now use `0.40` for human, as shown above.
`test_scoring_api.py` checks configured boundaries and matching response/log labels.

---

## Sample Run

### Appeals: automatic and human verification

I accept an existing `content_id` and non-empty `reasoning` at `POST /appeal`.
I select the process through `review_type`; unsupported values return HTTP `400`:

**Automatic appeal** — I use this by default when `review_type` is omitted:

```json
{
  "content_id": "c_example",
  "review_type": "automatic",
  "reasoning": "Please recheck the original assessment."
}
```

**Human-verification appeal** — I also require non-empty `additional_text`:

```json
{
  "content_id": "c_example",
  "review_type": "human_verification",
  "reasoning": "Please review my writing process.",
  "additional_text": "My earlier draft and an explanation of my revisions..."
}
```

I record the supporting text and UTC request time in `logs/audit.jsonl`, return
HTTP `202` with a `verification_request_id`, and set `under_review`. Human
verification uses a reviewer's decision without rerunning model or style scoring.
I use the original submission's writer ID. I inspect the saved text and evidence through
`GET /verification/review/<id>`, then submit `certified` or `not_certified` to
`POST /verification/review`. I check the current status at `GET /content/<id>`.
I show that flow under [A verified-human path](#a-verified-human-path).

For an automatic appeal, I return HTTP `200` after rechecking three versions:

1. The original text.
2. The text with its first sentence removed.
3. The text with its last sentence removed.

For both review paths, I retrieve the original text by `content_id` from
`logs/submissions.jsonl`. I support older items through text already saved in
their historical audit entries. I append appeal outcomes to `logs/audit.jsonl`.

For automatic appeals, I use perplexity alone as the model input, plus the current MATTR
style signal. I combine them through `scoring.combine_appeal_signals`:

```text
APPEAL_WEIGHT_MODEL_SIGNAL = 0.6
APPEAL_WEIGHT_STYLE_SIGNAL = 0.4
appeal_score = (0.6 * model_score) + (0.4 * style_score)
```

I label each version human at `<= 0.40`, AI at `>= 0.60`, and unsure between.
I take the majority vote, using unsure for a three-way tie. I retain the
original decision, which used the submission's 70/30 weights.

I save the appeal before inference, then append an `appeal_reassessment` with
scores and votes. I keep automatic appeals `under_review` for every result,
including `human`; an automatic recheck does not issue a certificate. The saved
submission and original `decided` audit record retain their initial values.

An unsure majority returns this message from the appeal criterion:

> Based on revaluation we do not have enough evidence to determine how this text was written. Your appeal has been recorded.

An AI majority also explains that the assessment can be wrong and asks the
writer to provide earlier versions for human review, as shown in the actual
response below. Invalid JSON or empty fields return HTTP `400`; a nonexistent
submission ID returns HTTP `404`. A variant too short to score votes unsure,
with unavailable scores left null and an `insufficient_data` status. If the
original text is missing from both files, I still record the automatic appeal;
its evaluations report `original_text_unavailable` and vote unsure. A model-loading
failure similarly votes unsure with `model_unavailable`.

### Actual submission, appeal, and audit check

I captured this baseline run on **November 10, 2026 at 1:31:11 a.m. PST**
(`2026-11-10T09:31:11+00:00`), before Binoculars, MATTR, and the threshold change.
I used real model/style scores and preserved the responses below. Rerunning
these requests with the current code can produce different scores.
These historical responses predate `review_type` and the extra signal fields.
The historical audit response includes `text`; new submissions store it separately.

**Submit the text first:**

```bash
curl -sS -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  --data-binary "@Milestone4_test_sample/clearly-AI_milestone4.json"
```

Response body (HTTP `200 OK`):

```json
{
  "combined_score": 0.8402173316975334,
  "confidence": 0.8402173316975334,
  "content_id": "c_e00cdce4c319",
  "guess": "ai",
  "label": "ai",
  "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
  "model_score": 0.9195,
  "style_score": 0.6552244389917785
}
```

**Appeal the returned content ID:**

```bash
curl -sS -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_e00cdce4c319", "reasoning": "Please review this decision using the original text and the versions with the first and last sentences removed."}'
```

Response body (HTTP `200 OK`):

```json
{
  "appeal_id": "a_84d1f13993bd",
  "content_id": "c_e00cdce4c319",
  "evaluations": [
    {
      "combined_score": 0.8137897755967114,
      "label": "ai",
      "model_score": 0.9195,
      "status": "scored",
      "style_score": 0.6552244389917785,
      "variant": "original"
    },
    {
      "combined_score": 0.8239619782194989,
      "label": "ai",
      "model_score": 0.9212,
      "status": "scored",
      "style_score": 0.6781049455487471,
      "variant": "without_first_sentence"
    },
    {
      "combined_score": 0.8074872684493513,
      "label": "ai",
      "model_score": 0.9121,
      "status": "scored",
      "style_score": 0.6505681711233782,
      "variant": "without_last_sentence"
    }
  ],
  "label": "ai",
  "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
  "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
  "status": "under_review",
  "votes": {
    "ai": 3,
    "human": 0,
    "unsure": 0
  },
  "weights": {
    "model": 0.6,
    "style": 0.4
  }
}
```

**Check the original decision and its new review status:**

```bash
curl -sS "http://127.0.0.1:5000/log?content_id=c_e00cdce4c319"
```

Response body (HTTP `200 OK`):

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": 0.8402173316975334,
      "confidence": 0.8402173316975334,
      "content_id": "c_e00cdce4c319",
      "creator_id": "deb_demo_instructor",
      "guess": "ai",
      "label": "ai",
      "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
      "model_score": 0.9195,
      "status": "decided",
      "style_score": 0.6552244389917785,
      "text": "It is not true that glands in the breast that have produced milk cannot get cancer. Any part of the body, including the breasts, can potentially develop cancer. \nThe breast is made up of various types of cells, including glandular cells, which produce milk, and connective tissue cells. Cancer can develop in either of these types of cells, as well as in other cells in the breast. The most common type of breast cancer is ductal carcinoma, which starts in the cells lining the milk ducts. \nIt is important for all individuals to be aware of the signs and symptoms of breast cancer and to practice regular self-exams and seek medical care if they notice any changes in their breasts. It is also important to get regular mammograms and other screenings, as recommended by a healthcare provider, in order to detect breast cancer early and increase the chances of successful treatment.",
      "timestamp": "2026-11-10T09:31:11+00:00"
    },
    {
      "appeal_id": "a_84d1f13993bd",
      "content_id": "c_e00cdce4c319",
      "creator_id": "deb_demo_instructor",
      "event": "appeal",
      "reasoning": "Please review this decision using the original text and the versions with the first and last sentences removed.",
      "status": "under_review",
      "timestamp": "2026-11-10T09:31:11+00:00"
    },
    {
      "appeal_id": "a_84d1f13993bd",
      "content_id": "c_e00cdce4c319",
      "creator_id": "deb_demo_instructor",
      "evaluations": [
        {
          "combined_score": 0.8137897755967114,
          "label": "ai",
          "model_score": 0.9195,
          "status": "scored",
          "style_score": 0.6552244389917785,
          "variant": "original"
        },
        {
          "combined_score": 0.8239619782194989,
          "label": "ai",
          "model_score": 0.9212,
          "status": "scored",
          "style_score": 0.6781049455487471,
          "variant": "without_first_sentence"
        },
        {
          "combined_score": 0.8074872684493513,
          "label": "ai",
          "model_score": 0.9121,
          "status": "scored",
          "style_score": 0.6505681711233782,
          "variant": "without_last_sentence"
        }
      ],
      "event": "appeal_reassessment",
      "label": "ai",
      "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
      "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
      "status": "under_review",
      "timestamp": "2026-11-10T09:31:11+00:00",
      "votes": {
        "ai": 3,
        "human": 0,
        "unsure": 0
      },
      "weights": {
        "model": 0.6,
        "style": 0.4
      }
    }
  ]
}
```

`GET /log` returned the unchanged original `decided` entry, the appeal and its
reasoning, and the reassessment, all linked to `c_e00cdce4c319`. The latest
event has `status: "under_review"`. Its three evaluations match the appeal
response, and the AI majority is three votes out of three. Each evaluation
records its model score, style score, combined score, and label.

My baseline test run passed 43 tests before the stretch changes.
`test_appeals.py` covers votes, sentence removal, 60/40 weighting, validation,
text retention, and unavailable or insufficient inputs.

<details>
<summary>Earlier Milestone 3 observations</summary>

These earlier observations are retained as history. The short sample initially
returned HTTP `200`; a later repeat returned HTTP `400` after minimum-length
validation was added. They are separate observations from different stages,
not two responses to the same request.

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl --fail-with-body --silent --show-error --include --max-time 60 \
  -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text":"Every morning I take my dog out. The morning mist and fresh air are refreshing.","creator_id":"milestone3_check"}'

     HTTP/1.1 400 BAD REQUEST
     Server: Werkzeug/3.1.8 Python/3.12.6
     Date: Tue, 10 Nov 2026 09:15:39 GMT
     Content-Type: application/json
     Content-Length: 126
     Connection: close

     {
          "error": "bad_request",
          "message": "Text is too short for style analysis. Provide at least 3 sentences and 40 words."
     }
     curl: (22) The requested URL returned error: 400
```

Earlier response body (HTTP `200 OK`):

```json
{
  "confidence": 0.5,
  "content_id": "c_fdcd3c03f3db",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.3704,
  "style_score": null
}
```
**Earlier log check:**

```bash
curl -s "http://127.0.0.1:5000/log?limit=1" | python3 -m json.tool
```

```json
{
    "count": 1,
    "entries": [
        {
            "combined_score": 0.5,
            "confidence": 0.5,
            "content_id": "c_fdcd3c03f3db",
            "creator_id": "milestone3_check",
            "guess": null,
            "label": "unsure",
            "model_score": 0.3704,
            "status": "decided",
            "style_score": 0.5,
            "timestamp": "2026-11-09T09:46:52+00:00"
        }
    ]
}
```

---

**What the log shows after this submission**

```bash
$ curl --fail-with-body --silent --show-error --include --max-time 10 \
  "http://127.0.0.1:5000/log?limit=1"
```

Earlier response body (HTTP `200 OK`):

```json
{
  "count": 1,
  "entries": [
    {
      "combined_score": 0.5,
      "confidence": 0.5,
      "content_id": "c_fdcd3c03f3db",
      "creator_id": "milestone3_check",
      "guess": null,
      "label": "unsure",
      "model_score": 0.3704,
      "status": "decided",
      "style_score": 0.5,
      "timestamp": "2026-11-09T09:46:52+00:00"
    }
  ]
}
```

The submission response and `GET /log` contain the same `content_id`
(`c_fdcd3c03f3db`) and real `model_score` (`0.3704`). The same
entry was also verified in `logs/audit.jsonl`. This confirms that the first
signal's result is now returned to the caller and recorded for that submission.

These older Milestone 3 records captured placeholder confidence and labels,
with `style_score: null` in the response and `0.5` in the log. I show the later
baseline submission and appeal above with both real signals.

</details>

---

## How I Used AI

I keep these earlier AI exchanges as history; my current settings are documented
in **Signals and Scoring**.

**Moment 1 — Implementing and inspecting the style signal**

- *What I asked for:* I wan tot build a AI writing detector what is the rule that I should follow for style if the three components are:
Spread Score Rule : Calculate $\frac{\text{stdev}}{\text{mean}}$ of sentence lengths
Punctuation Density Rule -
Token Ratio / TTR Rule : Calculate $\frac{\text{unique lowercase words}}{\text{total words}}$

What should be the weights or proportion that we a should add the three componenets so that the overall style score is in the range 0-1 which we high scores are AI and low scores are human
- *What came back:* The key thing is that weighting is the last step. Weights only produce a 0–1 score if each component is already a 0–1 “AI-likeness” number pointing the same direction, so the rule has three parts.

1. Normalize each raw feature into 0–1, with high = AI

Each raw metric has a different range and, in some cases, the wrong direction (low spread means AI, not high). Use a clamped linear map between a “human-typical” value and an “AI-typical” value:

```python
def to_ai_score(x, human_val, ai_val):
    s = (x - human_val) / (ai_val - human_val)
    return max(0.0, min(1.0, s))
```

Reasonable starting anchors (tune these on your own labeled samples — they are calibration points, not constants):

Spread (CV = stdev/mean of sentence lengths): AI text is “flat,” human text is bursty. spread_ai = to_ai_score(cv, human_val=0.75, ai_val=0.35) — a CV ≥ 0.75 scores 0, ≤ 0.35 scores 1.
Punctuation density (punctuation marks / total words): count , ; : — ( ) per word. LLM prose tends to run dense with commas, colons and dashes; casual human writing runs lighter. punct_ai = to_ai_score(density, human_val=0.08, ai_val=0.16). This is the noisiest of the three — formal human writing (academic, legal) is also dense — so verify the direction on your data before trusting it.
TTR (unique lowercase words / total words): repetitive vocabulary leans AI. ttr_ai = to_ai_score(ttr, human_val=0.62, ai_val=0.45). One caveat: TTR falls as text gets longer, so compute it on fixed-size windows (e.g. 100–200 words, averaged) or the anchors above won’t hold across different document lengths.

2. Combine with weights that sum to 1

style_score = 0.50 * spread_ai + 0.20 * punct_ai + 0.30 * ttr_ai

Since each component is in [0, 1] and the weights sum to 1, the result is guaranteed to be in [0, 1]. The rationale for the split: sentence-length burstiness is the most consistently reported stylometric separator, lexical diversity is second, and punctuation density is the easiest for both humans and prompted models to shift, so it gets the smallest vote. If you have no data yet, equal thirds (0.33 each) is a defensible baseline.

3. Then let data pick the real weights

Once you have even 50–100 labeled samples per class, fit a logistic regression on the three normalized components. The sigmoid output is already 0–1, and the learned coefficients tell you what the weights actually should be for your corpus — often punctuation drops out almost entirely. That’s also where you’d pick the decision threshold (0.5 is just a default; look at your precision/recall curve).

One honest limit to keep in mind for the write-up: three stylometric features will separate obvious cases but will produce plenty of false positives on polished, formal human writing and false negatives on AI text that’s been prompted to “write casually.” Treat the score as a signal, not a verdict.
- *What I changed:* 
I used this information to create my methods in stylometry.py and scoring.py .

**Moment 2 — i dont have many samples to train. SO give me the standard rule to be followed for short paragraph of 6-10 lines**

- *What I asked for:* i  dont have many samples to train. SO give me the standard rule to be followed for short paragraph of 6-10 lines
- *What came back:* Decision rule.

≥ 0.65 → likely AI
0.40 – 0.65 → uncertain
< 0.40 → likely human

Why these numbers for short text

Spread: with only 6–10 sentences, CV swings a lot, so the human anchor is lowered to 0.60 (vs 0.75 for long text) to avoid flagging a human who happens to write evenly. One very short sentence (“Really.”) will spike the CV, which is fine — that’s a human tell.
Punctuation: count only the “structural” marks. Periods are excluded because every sentence has one; they carry no information.
TTR: in under 200 words most words appear once, so human TTR sits around 0.80–0.90 and even repetitive AI text rarely drops below ~0.60. Using the long-text anchors (0.62/0.45) here would make everything look human.

Sanity check before you ship it: paste in two or three paragraphs you know are human (your own writing, a news paragraph) and two or three you generate with an LLM on a plain prompt. If the humans don’t land under ~0.40 and the AI ones over ~0.65, nudge the single anchor that’s misbehaving by ±0.05 — don’t touch the weights. That’s a five-minute calibration that needs no training set.
- *What I changed:* I applied these rules in my stylometry.py and scoring.py

## Stretch Features

**A third signal**

I added Binoculars score alongside perplexity and style. For inputs of at least
100 words, when Binoculars is available, I use **35% perplexity(0.5 weight of 70%), 35% Binoculars(0.5 weight of 70%), and 30% style**. I average the two model scores first, then apply the 70/30
model/style rule in `scoring.py::combine_signals`. For shorter inputs or
unavailable Binoculars, I use **70% perplexity and 30% style**. . I do this as the paper on binoculars  mentioned it perfromed poorly for short test (i have used the short text threshold as 100 words), so any text above 100 words will use all three signals below that will use only two signals which is performing better for shrter texts.


**A GET /content/<id> endpoint**

I return the item's latest status and credential through `app.py::get_content`.
The credential is `null` until certification; unknown IDs return HTTP `404`.
After a human-verification request, I also return `verification_request_id` and
`verification_status` (`pending`, `certified`, or `not_certified`). A later automatic
appeal sets `status` to `under_review` while retaining any certificate and its
verification status.
For this earlier automatic appeal:

```bash
curl -sS http://127.0.0.1:5000/content/c_e00cdce4c319
```

Response (`200 OK`):

```json
{
  "content_id": "c_e00cdce4c319",
  "status": "under_review",
  "credential": null
}
```

<a id="a-verified-human-path"></a>

**A verified-human path**

I ask for an earlier draft and an explanation through a `human_verification`
appeal. I then load the original submission, decision, evidence, and review outcome:

```bash
curl -sS http://127.0.0.1:5000/verification/review/c_verification_demo
```

I read `submission.text` from the submission file and
`verification_request.additional_text` from the audit log. The `review` field
is `null` while pending and contains the saved decision after review. I return
the latest human-verification request. For new submissions, `submission.status`
and `decision.status` retain `decided`; I use `GET /content/<id>` for current status.
If the original text is unavailable, `submission` is `null`. Unknown IDs return
`404`; a known item with no human-verification request returns `409`.
After reading the evidence, I send the reviewer decision:

```bash
curl -sS -X POST http://127.0.0.1:5000/verification/review \
  -H "Content-Type: application/json" \
  -d '{"content_id":"c_verification_demo","status":"certified"}'
```

I use `"status":"not_certified"` to decline; successful decisions return HTTP
`200`. I can include `reviewer` and `review_notes`; they default to `"unspecified"`
and `""`. I apply the decision to the latest human-verification request and reload
the submission before saving a new decision. Missing original text blocks certification with `409`,
but I can still decline. A creator-ID mismatch also returns `409`.
Duplicate pending requests, new requests for certified items, and conflicting
decisions return `409`. Repeating the same decision for the same request returns
the saved result, including its existing reviewer and notes.

On certification, I generate a short UUID-based `Certificate_id`, check its
uniqueness, and record `verified_dt_time` explicitly in UTC. I append the approved
record to `logs/verified_human_certification_log.jsonl` and the review outcome to
`logs/audit.jsonl`. A declined request has no credential; the writer can submit
new evidence in another appeal. I preserve the original submission and scores;
the certificate applies only to the reviewed item.

I check the result by content ID:

```bash
curl -sS http://127.0.0.1:5000/content/c_verification_demo
```

I captured this HTTP `200` response using **isolated test data and simulated
reviewer approval**. The request, pending response, and both review outcomes are in
[the API demo record](results/verification_api_demo.json). I replace the demo ID
with my own submission ID when using the service.

```json
{
  "content_id": "c_verification_demo",
  "credential": {
    "Certificate_id": "vh_f5aabe004ec64f00",
    "method": "draft_review",
    "type": "verified_human",
    "verified_dt_time": "2026-11-11 08:57:53 UTC"
  },
  "status": "certified",
  "verification_request_id": "vr_bcb353a64c9b4d75",
  "verification_status": "certified"
}
```

Before review, I return `under_review` with `credential: null`. After a decline,
I return `not_certified` with `credential: null`. I treat the certificate as a
record of draft review, separate from the automated authorship label.

---


<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

I limit `POST /submit` to **9 requests per minute and 400 per day** in
`config.py`. I enable limiting by default; `AI201_RATE_LIMITS=0` disables it.

```bash
AI201_RATE_LIMITS=1 .venv/bin/python app.py
```

I return HTTP `429` with a JSON error and `Retry-After` when either limit is
exceeded, and log the rejection before scoring. Other routes do not use this
allowance. My in-memory counters reset on restart and are separate per process.

**Why those numbers and not others:**
I allow room for revisions while limiting bursts and daily automated use.
I will evaluate these settings against normal use and the attack tests.

<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** I use a nonblank `creator_id`, falling back to the
IP address. Changing IDs bypasses a shared allowance; callers sharing an IP
without IDs share one allowance. I count invalid submissions too.

**Rate-limit evidence:** I still need to record this run. The 10th request from
the same caller within one minute exceeds the minute limit and returns HTTP `429`.

<!-- python run_attacks.py --flood 25 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [x] criteria.md has five numbered criteria, each naming a target
       [x] Each has a reason underneath
       [x] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [x] Two signals that measure DIFFERENT things, each with a named blind spot
       [x] Three label variants, all reachable, written out in full
       [x] POST /appeal changes status and writes to the log
       [x] Signals and Scoring names scoring.py::combine_signals
       [x] Sample Run: a submission AND an appeal, as pasted text
       [x] At least four new commits
       [x] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
