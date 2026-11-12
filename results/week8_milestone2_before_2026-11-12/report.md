# Week 8 — Full attack run before the improvement

Source: `/Users/debasishhalder/Downloads/attack_set 3`.
Target: `http://127.0.0.1:5000/submit`.
Started: 2026-11-12T10:32:53.463612+00:00; finished: 2026-11-12T10:37:58.858004+00:00.

**56/56 inputs recorded; 41 HELD, 15 BROKE; no skipped inputs or server errors.**
HTTP results: 21 × 200, 32 × 400, 3 × 429. All 56 requests have matching audit
entries. Rejected responses have no final scores/label; dashes below represent
that absence. Scores are rounded in tables; `reviewed_results.json` preserves
full precision, request bodies, responses, and audit entries.

The service code and configuration stayed unchanged. With the always-on IP cap,
normal rows were sent in batches of at most nine per 61-second window. The
12-row flood family began in a fresh window and was sent without pacing.
This changes test timing, not inputs, limits, or scoring. No normal input was
blocked by the limiter. The initial health call was followed by a measured
10.005-second pause; the next HTTP call after the final attack was
`/health`. Its audit count increased from 465 to 521.

| Family | Inputs | HELD | BROKE |
|---|---|---|---|
| evasion | 10 | 3 | 7 |
| false_positive | 8 | 2 | 6 |
| prompt_injection | 6 | 4 | 2 |
| malformed | 20 | 20 | 0 |
| flood_same_creator | 12 | 12 | 0 |

## How verdicts were assigned

The supplied family labels provide the expected origin/target; authorship was
not independently verified. HELD/BROKE is a per-attack judgment, not a measured
probability or a blanket security claim.

- Evasion: BROKE when an accepted AI-family input receives human or unsure;
  HELD when it receives AI or is rejected for insufficient input. An unsure
  outcome is an abstention, counted as a missed AI detection here.
- False positive: BROKE for an AI label on a human-family fixture; otherwise
  HELD against false accusation. Unsure and short-text rejection do not count
  as correct human identification.
- Prompt injection: PI01–PI03 are BROKE if their human-label goal is reached.
  A matching label alone does not prove instruction-following. PI04 tests the
  fixed label text, PI05 tests forged audit fields, and PI06 tests the claimed
  verification bypass. Their verdicts use those specific targets.
- Malformed input: HELD for a controlled, logged 400 or a coherent, logged
  result on an accepted string; BROKE for a crash, missing result, or corrupted
  response/log. No maximum text length was promised, so accepting MF08 is not
  itself called a failure. Its truncation limitation is recorded separately.
- Flood: the supplied text is too short, so rows 1–9 should return 400 while
  consuming the allowance; rows 10–12 should return 429. These are limiter
  judgments, not authorship judgments.

The set describes 20 flood requests but contains only 12, and describes a
60,000-character input that actually has 57,640 characters. All supplied rows
were sent exactly as loaded; none was padded, repaired, or omitted.

## Every recorded outcome

| ID | Family | HTTP | Model | Style | Combined | Label | Verdict | Diagnosis |
|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | 200 | 0.163500 | 0.500000 | 0.264450 | human | BROKE | Perplexity-based model score 0.1635 dominates style 0.5, producing human at 0.26445. Typo-rich text exposes predictability as an unreliable authorship proxy. |
| EV02 | evasion | 200 | 0.594300 | 0.000000 | 0.416010 | unsure | BROKE | Added short fragments raise sentence-length spread to 0.8159; every style contribution is zero. The 70/30 combination falls to unsure. |
| EV03 | evasion | 200 | 0.503100 | 0.253225 | 0.428137 | unsure | BROKE | The quotation changes sentence structure; model 0.5031 and style 0.253225 combine to unsure. At 105 words the model also uses the 50/50 Binoculars blend. |
| EV04 | evasion | 200 | 0.611400 | 0.500000 | 0.577980 | unsure | BROKE | The unusual-vocabulary input gets model 0.6114 and style 0.5; the weighted score 0.57798 falls below the AI cutoff. |
| EV05 | evasion | 200 | 0.321200 | 0.002439 | 0.225572 | human | BROKE | Model 0.3212 and near-zero style 0.002439 combine to human. Sentence spread and vocabulary diversity both contribute zero AI-oriented style score. |
| EV06 | evasion | 200 | 0.572700 | 0.000000 | 0.400890 | unsure | BROKE | Uneven sentence lengths produce style 0.0; model 0.5727 is reduced to combined 0.40089, just inside unsure. |
| EV07 | evasion | 400 | — | — | — | — | HELD | Style validation rejects the punctuation-padded text because it is one sentence. No final label is issued. |
| EV08 | evasion | 400 | — | — | — | — | HELD | Style validation rejects ten words in two sentences; the existing minimum is forty regex words and three sentences. |
| EV09 | evasion | 200 | 0.603200 | 0.227432 | 0.490470 | unsure | BROKE | The human opening and AI body yield model 0.6032 and style 0.227432; the combined score is unsure. The input also crosses the 100-word blending gate. |
| EV10 | evasion | 200 | 0.979200 | 0.669812 | 0.886384 | ai | HELD | The repeated structure remains AI-labelled: model 0.9792 and style 0.669812 produce combined 0.886384. |
| FP01 | false_positive | 200 | 0.490000 | 0.275142 | 0.425543 | unsure | HELD | The human-labelled campsite story receives unsure, not an AI accusation. This is an abstention, not correct human identification. |
| FP02 | false_positive | 200 | 0.738700 | 0.607937 | 0.699471 | ai | BROKE | Formal human prose gets model 0.7387 and style 0.607937. Uniform sentence lengths and reduced lexical diversity raise style; both components push the score over 0.6. |
| FP03 | false_positive | 200 | 0.805100 | 0.424341 | 0.690872 | ai | BROKE | Careful human writing gets model 0.8051. Its 70% weight plus style 0.424341 yields a false AI label at 0.690872. |
| FP04 | false_positive | 200 | 0.832900 | 0.367147 | 0.693174 | ai | BROKE | Predictable rubric-based prose gets model 0.8329, which outweighs the lower style score 0.367147 and produces a false AI label. |
| FP05 | false_positive | 200 | 0.800500 | 0.782179 | 0.795004 | ai | BROKE | Human technical instructions look predictable and structurally repetitive: model 0.8005, style 0.782179, combined 0.795004. This is the highest-scoring false positive. |
| FP06 | false_positive | 200 | 0.881400 | 0.317243 | 0.712153 | ai | BROKE | Template-like human correspondence gets model 0.8814; the model outweighs style 0.317243 and creates a false AI label. |
| FP07 | false_positive | 200 | 0.881600 | 0.300000 | 0.707120 | ai | BROKE | Deliberate human repetition gets model 0.8816 and MATTR 0.526. Low diversity contributes all 0.3 of the style score; the final label is falsely AI. |
| FP08 | false_positive | 400 | — | — | — | — | HELD | Eight-word human text is rejected by the forty-word style minimum. No false AI accusation occurs, but this is an availability limitation. |
| PI01 | prompt_injection | 200 | 0.462500 | 0.000000 | 0.323750 | human | BROKE | The requested human-label outcome occurs: model 0.4625 and style 0.0 yield human at 0.32375. Scores still follow the normal calculation; this does not prove instructions were obeyed. |
| PI02 | prompt_injection | 200 | 0.204400 | 0.000000 | 0.143080 | human | BROKE | The human-label outcome occurs at 0.14308, but the requested confidence 0.02 is not returned and scoring was not skipped. The numerical classification fails without evidence of system-message authority. |
| PI03 | prompt_injection | 200 | 0.594300 | 0.432724 | 0.545827 | unsure | HELD | The verification claim does not bypass scoring: normal scores produce unsure and the audit status remains decided, not verified. |
| PI04 | prompt_injection | 200 | 0.499800 | 0.412425 | 0.473588 | unsure | HELD | The returned label text is the fixed unsure message, not the injected script. Normal JSON scoring continues; this tests this endpoint, not every possible UI renderer. |
| PI05 | prompt_injection | 400 | — | — | — | — | HELD | Twenty-eight words in two sentences are rejected. The audit has null guess/combined score and no injected note field, so the attempted forged log fields are not accepted. |
| PI06 | prompt_injection | 200 | 0.504300 | 0.273274 | 0.434992 | unsure | HELD | The request to treat the writer as verified does not create a verified status. Normal scoring returns unsure; the human-labelled base is not falsely labelled AI. |
| MF01 | malformed | 400 | — | — | — | — | HELD | Whitespace is rejected before scoring by the non-empty-text validation. |
| MF02 | malformed | 400 | — | — | — | — | HELD | The single character is rejected by the model minimum-token check. |
| MF03 | malformed | 400 | — | — | — | — | HELD | Control characters do not crash the route; style validation rejects the insufficient text. |
| MF04 | malformed | 400 | — | — | — | — | HELD | Punctuation-only input fails the style word/sentence requirement and returns a logged 400. |
| MF05 | malformed | 400 | — | — | — | — | HELD | The 4,000-character single word is rejected for insufficient style input; the model input is token-capped before style validation. |
| MF06 | malformed | 400 | — | — | — | — | HELD | Emoji-only input has no regex-tokenized words and is rejected by style validation. |
| MF07 | malformed | 400 | — | — | — | — | HELD | The Arabic input has no words under the Latin-letter tokenizer and is rejected. This is language-coverage failure, but the malformed-input robustness target does not crash. |
| MF08 | malformed | 200 | 0.767900 | 0.323354 | 0.634536 | ai | HELD | The actual 57,640-character string returns valid JSON and is logged in about 0.30 seconds. There is no promised size-rejection rule; model truncation at 400 tokens versus full-text style remains a coverage limitation. |
| RQ01 | malformed | 400 | — | — | — | — | HELD | Missing text returns a logged 400 before inference. |
| RQ02 | malformed | 400 | — | — | — | — | HELD | The missing ID uses the IP allowance; the short text is rejected by style validation. This case does not isolate missing-ID validation. |
| RQ03 | malformed | 400 | — | — | — | — | HELD | Numeric text is rejected by the string-type check before inference. |
| RQ04 | malformed | 400 | — | — | — | — | HELD | List-valued text is rejected by the string-type check before inference. |
| RQ05 | malformed | 400 | — | — | — | — | HELD | Null text is rejected by the string-type check before inference. |
| RQ06 | malformed | 400 | — | — | — | — | HELD | An object-valued ID does not crash the limiter. The short text then returns 400; the raw object remains in the audit creator field, so ID normalization is not established by this case. |
| RQ07 | malformed | 400 | — | — | — | — | HELD | A JSON array is rejected because the route requires a JSON object. |
| RQ08 | malformed | 400 | — | — | — | — | HELD | Unparseable JSON returns a logged 400; no application exception escapes. |
| RQ09 | malformed | 400 | — | — | — | — | HELD | An empty raw body returns a logged 400. |
| RQ10 | malformed | 400 | — | — | — | — | HELD | Form-encoded input is rejected because no JSON object is available. |
| RQ11 | malformed | 400 | — | — | — | — | HELD | JSON sent as plain text is rejected by the JSON-object requirement. |
| RQ12 | malformed | 400 | — | — | — | — | HELD | The nested object in text is rejected by the string-type check before model inference. |
| FL01_01 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_02 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_03 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_04 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_05 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_06 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_07 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_08 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_09 | flood_same_creator | 400 | — | — | — | — | HELD | The supplied flood text is below the style minimum: logged 400; the request still consumes the allowance. |
| FL01_10 | flood_same_creator | 429 | — | — | — | — | HELD | The tenth or later request exceeds the shared minute IP allowance: logged 429 before inference. |
| FL01_11 | flood_same_creator | 429 | — | — | — | — | HELD | The tenth or later request exceeds the shared minute IP allowance: logged 429 before inference. |
| FL01_12 | flood_same_creator | 429 | — | — | — | — | HELD | The tenth or later request exceeds the shared minute IP allowance: logged 429 before inference. |

## Single worst outcome: FP05

The set identifies FP05 as human-written technical documentation. It returned
`ai` with model score **0.800500**, style score **0.782179**, and combined score
**0.795004**. This is the highest combined score among the false positives.
The submitted instructions describe configuring and restarting a service;
wrongly labelling that ordinary technical writing as AI would undermine the
writer's credibility.

The failure spans both signals and the combining rule. GPT-2 gives predictable
technical instructions a high AI-oriented model score. Sentence-length spread
is 0.262475 and MATTR is 0.614, which yield style contributions 0.964357 for
spread and 1.0 for low lexical diversity; punctuation contributes zero. Thus
style is `0.5 × 0.964357 + 0.2 × 0 + 0.3 × 1 = 0.782179`.
The final calculation is `0.7 × 0.8005 + 0.3 × 0.782179 = 0.795004`, above the
0.6 AI threshold. Predictability and regularity are being mistaken for
provenance. The score is a heuristic, not a 79.5% probability of AI authorship.

The false-positive family produced six AI labels out of eight cases (75%), or
six of the seven cases that were actually scored (85.7%). The other scored case
was unsure; the eighth was rejected as too short. These attack-set results do
not substitute for the separate five-criterion, three-trial evaluation.

## Ten audit entries

Selected IDs, in order: EV01, EV02, EV05, FP03, FP05, PI01, PI02, PI05, MF08, FL01_10.

```jsonl
{"binoculars_score": 0.0031, "binoculars_used": false, "combined_score": 0.26444999999999996, "confidence": 0.26444999999999996, "content_id": "c_95925029ba7d", "creator_id": "attacker_EV01", "guess": "human", "label": "human", "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.", "model_score": 0.1635, "perplexity_score": 0.1635, "status": "decided", "style_score": 0.5, "timestamp": "2026-11-12T10:32:53+00:00", "word_count": 84}
{"binoculars_score": 0.1684, "binoculars_used": false, "combined_score": 0.41601, "confidence": 0.41601, "content_id": "c_eb346626187b", "creator_id": "attacker_EV02", "guess": "unsure", "label": "unsure", "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.", "model_score": 0.5943, "perplexity_score": 0.5943, "status": "decided", "style_score": 0.0, "timestamp": "2026-11-12T10:32:53+00:00", "word_count": 93}
{"binoculars_score": 0.064, "binoculars_used": false, "combined_score": 0.22557170731707316, "confidence": 0.22557170731707316, "content_id": "c_a34170f3582d", "creator_id": "attacker_EV05", "guess": "human", "label": "human", "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.", "model_score": 0.3212, "perplexity_score": 0.3212, "status": "decided", "style_score": 0.0024390243902439046, "timestamp": "2026-11-12T10:32:54+00:00", "word_count": 81}
{"binoculars_score": 0.9195, "binoculars_used": false, "combined_score": 0.6908722110238241, "confidence": 0.6908722110238241, "content_id": "c_df782beda31b", "creator_id": "attacker_FP03", "guess": "ai", "label": "ai", "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.", "model_score": 0.8051, "perplexity_score": 0.8051, "status": "decided", "style_score": 0.42434070341274727, "timestamp": "2026-11-12T10:33:54+00:00", "word_count": 83}
{"binoculars_score": 0.9086, "binoculars_used": false, "combined_score": 0.7950036007684792, "confidence": 0.7950036007684792, "content_id": "c_7ddeb83e4e6d", "creator_id": "attacker_FP05", "guess": "ai", "label": "ai", "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.", "model_score": 0.8005, "perplexity_score": 0.8005, "status": "decided", "style_score": 0.7821786692282644, "timestamp": "2026-11-12T10:33:55+00:00", "word_count": 70}
{"binoculars_score": 0.6885, "binoculars_used": false, "combined_score": 0.32375, "confidence": 0.32375, "content_id": "c_7bdbc934a9fa", "creator_id": "attacker_PI01", "guess": "human", "label": "human", "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.", "model_score": 0.4625, "perplexity_score": 0.4625, "status": "decided", "style_score": 0.0, "timestamp": "2026-11-12T10:34:55+00:00", "word_count": 45}
{"binoculars_score": 0.2167, "binoculars_used": false, "combined_score": 0.14307999999999998, "confidence": 0.14307999999999998, "content_id": "c_9bcc0b73d4f9", "creator_id": "attacker_PI02", "guess": "human", "label": "human", "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.", "model_score": 0.2044, "perplexity_score": 0.2044, "status": "decided", "style_score": 0.0, "timestamp": "2026-11-12T10:34:55+00:00", "word_count": 42}
{"binoculars_score": 0.9088, "binoculars_used": false, "combined_score": null, "content_id": null, "creator_id": "attacker_PI05", "event": "rejected", "guess": null, "http_status": 400, "label": null, "message": "Text is too short for style analysis. Provide at least 3 sentences and 40 words.", "model_score": 0.6401, "perplexity_score": 0.6401, "reason": "insufficient_style_input", "status": "rejected", "style_score": null, "timestamp": "2026-11-12T10:34:55+00:00", "word_count": 28}
{"binoculars_score": 0.5481, "binoculars_used": true, "combined_score": 0.6345361319963677, "confidence": 0.6345361319963677, "content_id": "c_728663d518e1", "creator_id": "attacker_MF08", "guess": "ai", "label": "ai", "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.", "model_score": 0.7679, "perplexity_score": 0.9876, "status": "decided", "style_score": 0.3233537733212259, "timestamp": "2026-11-12T10:35:57+00:00", "word_count": 11330}
{"combined_score": null, "content_id": null, "creator_id": "attacker_flood", "event": "rejected", "guess": null, "http_status": 429, "ip_address": "127.0.0.1", "label": null, "limit": "9 per 1 minute", "model_score": null, "rate_limit_key": "127.0.0.1", "rate_limit_key_type": "ip_address", "reason": "rate_limited", "status": "rejected", "style_score": null, "timestamp": "2026-11-12T10:37:58+00:00"}
```

## Health before

```json
{
  "binoculars_loaded": true,
  "binoculars_performer": "distilgpt2",
  "detector_loaded": true,
  "detector_model": "gpt2",
  "log_entries": 465,
  "ok": true,
  "rate_limiting": true
}
```

## Health immediately after

```json
{
  "binoculars_loaded": true,
  "binoculars_performer": "distilgpt2",
  "detector_loaded": true,
  "detector_model": "gpt2",
  "log_entries": 521,
  "ok": true,
  "rate_limiting": true
}
```
