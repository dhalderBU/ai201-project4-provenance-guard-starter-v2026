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

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->
Provenance Guard estimates how AI-like a passage looks using two signals. The
score is a heuristic assessment, not proof of who wrote the text.

1. `POST /submit` receives a JSON object containing `text` and an optional
   `creator_id`.
2. The route validates the request. Invalid JSON, empty text, or text too short
   for either signal returns HTTP `400`.
3. `detector.model_signal(text)` uses a local language model to measure text
   predictability and returns a model score between 0 and 1.
4. `stylometry.style_signal(text)` measures sentence-length spread, punctuation
   density, and vocabulary diversity, returning a style score between 0 and 1.
5. `scoring.py::combine_signals` combines the scores using
   `WEIGHT_MODEL_SIGNAL = 0.7` and `WEIGHT_STYLE_SIGNAL = 0.3` from `config.py`.
6. `scoring.score_to_label` applies the configured boundaries to choose
   `human`, `unsure`, or `ai`. `scoring.LABEL_TEXT` supplies the reader-facing
   sentence.
7. The service generates a `content_id`, saves the original text and decision
   in the audit log, and returns the label and scores. The writer can use that
   ID to appeal; the appeal and its recheck results are appended as
   `under_review` events.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**

`detector.model_signal(text)` runs GPT-2 locally by default, using the model
selected by `DETECTOR_MODEL` in `config.py`. It calculates perplexity from the
model's prediction loss: lower perplexity means the text is easier for that
model to predict. The code then converts perplexity to a score between 0 and 1:

```text
model_score = 1 / (1 + (perplexity / 45.0) ** 1.6)
```

The returned score is rounded to four decimal places. Higher values are
treated as stronger AI-like evidence. The model scores the supplied text;
it does not generate an answer about the writer's identity.

**Why that might differ between human and AI writing:**

The working hypothesis is that generated text may use predictable phrasing.
Human writing can contain unusual choices, but people also write plainly and
repeat familiar expressions. Predictability alone cannot establish authorship.

**What it can't see:**

With the current GPT-2 tokenizer, `DETECTOR_MAX_TOKENS = 400` keeps the first
400 tokens and truncates the rest. The model score therefore does not evaluate
the full passage when the input exceeds that limit. It does not use editing
history or authorship records. Plain human writing can receive a high score,
and unfamiliar vocabulary can lower the score regardless of who wrote it.

### Signal two — the style signal

**What it measures:**

The three individual measurement functions implement the supplied sample code:

| Method | Raw measurement | Empty-input result |
| --- | --- | --- |
| `sentence_length_spread(text)` | Population standard deviation of sentence word counts divided by their mean | `0.0` |
| `punctuation_density(text)` | Count of `, ; : — – ( )` divided by the number of words | `0.0` |
| `type_token_ratio(text)` | Unique lowercase word tokens divided by all word tokens | `0.0` |

Sentence splitting uses whitespace after `.`, `!`, or `?`. Tokenization uses
`[A-Za-z']+`, matching the sample: digits are excluded, straight apostrophes
stay within tokens, and curly apostrophes split tokens. Wordless sentence
fragments remain in the spread distribution, also matching the sample.
Structural punctuation density can exceed `1.0`; it is a raw ratio, not a score.

`style_subscores(text)` converts the measurements into AI-oriented contributions:

```python
spread_ai = clamp01((0.60 - spread) / (0.60 - 0.25))
punct_ai = clamp01((density - 0.06) / (0.14 - 0.06))
ttr_ai = clamp01((0.80 - ttr) / (0.80 - 0.62))

style_score = 0.50 * spread_ai + 0.20 * punct_ai + 0.30 * ttr_ai
```

`clamp01` limits each contribution to `[0.0, 1.0]`. The style score keeps
full precision. All sample limits, anchors, weights, and label thresholds are
named constants at the top of `stylometry.py`.

| Setting | Constants | Values |
| --- | --- | --- |
| Minimum sample | `MIN_STYLE_SENTENCES`, `MIN_STYLE_WORDS` | `3`, `40` |
| Spread anchors | `SPREAD_AI_ANCHOR`, `SPREAD_HUMAN_ANCHOR` | `0.25`, `0.60` |
| Structural punctuation anchors | `PUNCTUATION_HUMAN_ANCHOR`, `PUNCTUATION_AI_ANCHOR` | `0.06`, `0.14` marks per word |
| TTR anchors | `TTR_AI_ANCHOR`, `TTR_HUMAN_ANCHOR` | `0.62`, `0.80` |
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

This implementation replaces the earlier short/long branches with the supplied
sample algorithm. It uses the whole input and has no upper word-count cutoff.
The TTR anchors were proposed for prose under 200 words, so scores on longer
inputs need separate evaluation. All anchors are hypotheses to test, not
established authorship boundaries or calibrated probabilities.

**Why that might differ between human and AI writing:**

The style rule treats uniform sentence lengths, frequent structural
punctuation, and repeated vocabulary as AI-like patterns. These are hypotheses
to evaluate on samples, not reliable signatures of authorship by themselves.

**What it can't see:**

It cannot understand meaning or identify who wrote the text. Paraphrasing,
changing punctuation, or splitting sentences can change the score without
changing authorship. TTR depends on input length. The simple sentence splitter
can misread abbreviations, and the ASCII word pattern does not reliably handle
text containing other scripts or accented letters. Those limitations can
distort the measurements in either direction.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

I use a weighted average: the model score contributes 70% and the style score
contributes 30%. Both inputs range from 0 to 1, with higher values indicating
more AI-like text. The weights are nonnegative and add up to 1, so the combined
score stays between the two input scores and within the same 0–1 range.

When the signals disagree, the model score has more influence. There is no
separate disagreement override: the weighted result can receive a human,
unsure, or AI label, depending on the thresholds in `config.py`. Giving the
model more weight also means its mistakes can outweigh the style signal.

**Trace of an unsure result — hypothetical scenario:**

The sample below illustrates the flow using imaginary scores. The assessment
sentence matches the implemented label text; this scenario is not a test run.

1. **The writer enters their text.** A writer submits the following passage as their own original work:

   > Every morning I take my dog out before work. Today the mist was still hanging over the park, and we stopped near the gate while a neighbor looked for her keys. I got home a little late, so I ate breakfast standing beside the sink.

2. **The service receives the submission.** The website sends the passage in
   `text`, along with the caller's `creator_id`, to `POST /submit`. The route
   parses the JSON and checks the input. This passage is non-empty and meets
   the style signal's minimum of three sentences and 40 words.

3. **The model signal scores the text.** The route passes the passage to `detector.model_signal(text)`. For this hypothetical calculation, assume a model score of `0.7`.

4. **The style signal scores the text.** The route passes the same passage to `stylometry.style_signal(text)`. Assume a style score of `0.30`; this is an illustrative value, not a measured result for the passage.

5. **The service combines the scores and chooses a label.**
   `scoring.combine_signals(0.7, 0.30)` calculates `(0.7 * 0.7) + (0.3 * 0.30) = 0.58`.
   The route passes the combined score to `scoring.score_to_label()`, which
   returns `("unsure", 0.58)` because `0.45 < 0.58 < 0.60`.

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
- `HUMAN_THRESHOLD = 0.45`
- `AI_THRESHOLD = 0.60`

```text
combined_score = (0.7 * model_score) + (0.3 * style_score)
```

The weights and final label thresholds are defined in `config.py`.
`scoring.score_to_label` assigns human for scores at or below `0.45`, unsure
for scores above `0.45` and below `0.60`, and AI for scores at or above `0.60`.
These final label thresholds are separate from the style-only thresholds in
`stylometry.py`. The combined score is a heuristic, not a calibrated probability
of AI authorship.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

The actual run of `Milestone4_test_sample/borderline_ai_milestone4.json`
recorded a model score of `0.5195` and a style score of `0.6808494097161918`.
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
threshold of `0.45`, so the final label is unsure. The audit entry is
`c_df4de07a8019`; its full record appears below.

Disagreement does not always produce unsure. For comparison, hypothetical
scores of model `0.90` and style `0.10` give `0.66`, which receives an AI label.
Reversing them gives `0.34`, which receives a human label. These comparison
values illustrate the model's larger weight; they are not additional test runs.

### Milestone 4 — Input tests and audit evidence

The four entries from the latest batch come from [logs/audit.jsonl](logs/audit.jsonl), lines
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
earlier test alongside the four files from the latest batch.

**Recorded results:** Scores in the table are rounded to six decimal places;
the exact logged values are preserved in the JSONL excerpt below. Final labels
use `0.7 * model_score + 0.3 * style_score`, with human at `<= 0.45`, AI at
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
   because structural punctuation contributes zero under the current rule.
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
| `POST /appeal` | `content_id`, `reasoning` | `content_id`, `appeal_id`, `status`, `label`, `label_text`, `message`, `votes`, `evaluations`, `weights` |
| `GET /log` | Optional query parameters: `content_id`, `limit` | `count`, `entries`; filtering by `content_id` shows the original decision and subsequent appeal events. |

For submissions, `guess` and `label` contain the same short classification.
`label_text` contains the full sentence, and `confidence` equals
`combined_score`. The numeric confidence is an AI-oriented score, not certainty
in whichever label was selected. `creator_id` is optional and defaults to
`"unknown"` in the decision record when omitted.

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

`scoring.score_to_label(score)` returns `(label, confidence)`, where `label` is
`"human"`, `"unsure"`, or `"ai"`, and `confidence` is the combined score as a
float. Higher confidence values mean more AI-like, not greater certainty in
the selected label. For example, `score_to_label(0.20)` returns `("human", 0.20)`.

The exact reader-facing messages are defined in `scoring.LABEL_TEXT`.
`app.py::submit` calls `scoring.score_to_label`, selects the corresponding
sentence, and returns it as `label_text` alongside the short `label` and numeric
`confidence`. The same sentence is recorded in the audit log. The ranges below
follow the thresholds in `config.py` and the conditions in `score_to_label`.

| API label | Score range | Exact `label_text` returned to the reader |
|---|---|---|
| `human` | `0.00 ≤ score ≤ 0.45` | Our checks suggest this text was written by a person. This assessment can be wrong. |
| `unsure` | `0.45 < score < 0.60` | We do not have enough evidence to determine how this text was written. The writer can request a review. |
| `ai` | `0.60 ≤ score ≤ 1.00` | Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review. |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

The unsure message describes a limit of the automated checks without accusing
the writer. It acknowledges that the checks cannot determine authorship and
points to human review instead of presenting a numeric score as proof.

### Milestone 5 — Verified label responses

On **November 10, 2026 at 1:20:16 a.m. Pacific Standard Time**, the three saved
texts below were submitted to the running `POST /submit` service with
`creator_id = "milestone5_label_verification"`. All three requests returned
HTTP `200`. The model and style signals ran on the actual text without mocks.
The responses below were captured from those requests and matched their audit
entries in [logs/audit.jsonl](logs/audit.jsonl), lines 168–170.

These captured responses predate the addition of `guess` as an alias for
`label`. They are preserved exactly; the later submission in **Sample Run**
shows the current response fields.

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

All three labels are reachable. Boundary checks also verified that `0.45`
returns human, `0.60` returns AI, and scores strictly between them return unsure.
`scoring.label_ranges()` displays the inclusive and exclusive boundaries
explicitly. The automated checks in `test_scoring_api.py` cover the boundaries
and verify that each response and audit record receive the matching label text.

---

## Sample Run

### Appeal behavior from criteria.md

`app.py::appeal` implements criterion 4 in [criteria.md](criteria.md). It accepts
an existing `content_id` and non-empty `reasoning`, records the appeal as
`under_review`, and reassesses three versions of the saved submission:

1. The original text.
2. The text with its first sentence removed.
3. The text with its last sentence removed.

`scoring.combine_appeal_signals` uses the appeal constants in `config.py`:

```text
APPEAL_WEIGHT_MODEL_SIGNAL = 0.6
APPEAL_WEIGHT_STYLE_SIGNAL = 0.4
appeal_score = (0.6 * model_score) + (0.4 * style_score)
```

Each version uses the current label boundaries: human at `<= 0.45`, AI at
`>= 0.60`, and unsure between them. Two or more votes select the majority
label. A three-way tie returns unsure. The original submission still uses
70% model and 30% style; an appeal does not overwrite that earlier decision.

The original text is retained in new decision records so rechecks use what was
actually submitted. The service records the appeal before inference, then
appends an `appeal_reassessment` event with all three sets of scores and the
vote counts. Both events remain `under_review`, including when the automated
majority is AI or human. The latest event for a content ID shows its current
review status; the original `decided` entry remains unchanged.

An unsure majority returns this message from the appeal criterion:

> Based on revaluation we do not have enough evidence to determine how this text was written. Your appeal has been recorded.

An AI majority also explains that the assessment can be wrong and asks the
writer to provide earlier versions for human review, as shown in the actual
response below. Invalid JSON or empty fields return HTTP `400`; a nonexistent
submission ID returns HTTP `404`. A variant too short to score votes unsure,
with null scores and an `insufficient_data` status. Historical decisions that
have no saved text are still accepted for review: their evaluations report
`original_text_unavailable` and return unsure without invented scores.

### Actual submission, appeal, and audit check

This live run completed on **November 10, 2026 at 1:31:11 a.m. Pacific Standard
Time** (`2026-11-10T09:31:11+00:00`). It used the saved AI sample, real GPT-2 and
stylometry scores, and the real audit log. The curl commands below reproduce
the requests; the JSON bodies were captured from the running service.

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

The automated tests in `test_appeals.py` also cover human and unsure majorities,
a three-way tie, exact sentence removal, 60/40 weighting, validation errors,
text retention, short variants, model unavailability, and preservation of the
original decision. The complete test run passed 43 tests.

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
with `style_score: null` in the response and `0.5` in the log. The current
submission and appeal workflow is demonstrated above with both real signals.

</details>

---

## How I Used AI

**Moment 1 — Implementing and inspecting the style signal**

- *What I asked for:* I wan tot build a AI writing detector what is the rule that I should follow for style if the three components are:
Spread Score Rule : Calculate $\frac{\text{stdev}}{\text{mean}}$ of sentence lengths
Punctuation Density Rule -
Token Ratio / TTR Rule : Calculate $\frac{\text{unique lowercase words}}{\text{total words}}$

What should be the weights or proportion that we a should add the three componenets so that the overall style score is in the range 0-1 which we high scores are AI and low scores are human
- *What came back:* The key thing is that weighting is the last step. Weights only produce a 0–1 score if each component is already a 0–1 “AI-likeness” number pointing the same direction, so the rule has three parts.

1. Normalize each raw feature into 0–1, with high = AI

Each raw metric has a different range and, in some cases, the wrong direction (low spread means AI, not high). Use a clamped linear map between a “human-typical” value and an “AI-typical” value:

def to_ai_score(x, human_val, ai_val):
    s = (x - human_val) / (ai_val - human_val)
    return max(0.0, min(1.0, s))

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

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 submissions per minute and 50 per day, configured in `config.py`.
Both limits apply to `POST /submit` when the service starts with rate limiting enabled:

```bash
AI201_RATE_LIMITS=1 .venv/bin/python app.py
```

Rate limiting is disabled by default. Requests that exceed either limit return
HTTP `429` with a JSON error, the exceeded limit, and a `Retry-After` header.
Each rejection is recorded in the audit log before any model scoring runs.
Other routes do not consume the submission allowance. In-memory counters reset
when the service restarts and are not shared between server processes.

**Why those numbers and not others:**
Five submissions per minute allow a few quick revisions, while 50 per day
limits sustained automated submissions from the same caller. These are initial
limits to evaluate against normal use and the attack tests.

<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** A nonblank string `creator_id`, falling back to the
request's IP address when that ID is absent or invalid. Creator IDs are supplied
by callers, so changing IDs creates separate allowances; callers without IDs
who share an IP share an allowance. Invalid submissions also count toward the limits.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

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