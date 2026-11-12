# Full attack run — after the single threshold change

AI_THRESHOLD changed from 0.60 to 0.80. All 56 original inputs were sent.
47 HELD / 9 BROKE; 21 HTTP 200, 32 HTTP 400, and 3 HTTP 429.
Scores and request/status pairs exactly match the before run.
Verdicts use the unchanged [policy](../week8_milestone5_2026-11-12/verdict_policy.md).

| ID | Family | HTTP | Model | Style | Combined | Label | Verdict | Diagnosis |
|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | 200 | 0.163500 | 0.500000 | 0.264450 | human | BROKE | Signal one/two scores and their 70/30 combination are unchanged; 0.264450 still maps to human. Missed AI detection under the fixed policy. |
| EV02 | evasion | 200 | 0.594300 | 0.000000 | 0.416010 | unsure | BROKE | Signal one/two scores and their 70/30 combination are unchanged; 0.416010 still maps to unsure. Missed AI detection under the fixed policy. |
| EV03 | evasion | 200 | 0.503100 | 0.253225 | 0.428137 | unsure | BROKE | Signal one/two scores and their 70/30 combination are unchanged; 0.428137 still maps to unsure. Missed AI detection under the fixed policy. |
| EV04 | evasion | 200 | 0.611400 | 0.500000 | 0.577980 | unsure | BROKE | Signal one/two scores and their 70/30 combination are unchanged; 0.577980 still maps to unsure. Missed AI detection under the fixed policy. |
| EV05 | evasion | 200 | 0.321200 | 0.002439 | 0.225572 | human | BROKE | Signal one/two scores and their 70/30 combination are unchanged; 0.225572 still maps to human. Missed AI detection under the fixed policy. |
| EV06 | evasion | 200 | 0.572700 | 0.000000 | 0.400890 | unsure | BROKE | Signal one/two scores and their 70/30 combination are unchanged; 0.400890 still maps to unsure. Missed AI detection under the fixed policy. |
| EV07 | evasion | 400 | — | — | — | — | HELD | Style validation rejects the punctuation-padded text because it is one sentence. No final label is issued. |
| EV08 | evasion | 400 | — | — | — | — | HELD | Style validation rejects ten words in two sentences; the existing minimum is forty regex words and three sentences. |
| EV09 | evasion | 200 | 0.603200 | 0.227432 | 0.490470 | unsure | BROKE | Signal one/two scores and their 70/30 combination are unchanged; 0.490470 still maps to unsure. Missed AI detection under the fixed policy. |
| EV10 | evasion | 200 | 0.979200 | 0.669812 | 0.886384 | ai | HELD | Signal one/two scores and their 70/30 combination are unchanged; 0.886384 still maps to ai. Remains above the 0.80 AI threshold. |
| FP01 | false_positive | 200 | 0.490000 | 0.275142 | 0.425543 | unsure | HELD | The human-labelled campsite story receives unsure, not an AI accusation. This is an abstention, not correct human identification. |
| FP02 | false_positive | 200 | 0.738700 | 0.607937 | 0.699471 | unsure | HELD | Label changed from ai to unsure at unchanged score 0.699471. The 0.80 threshold avoids an AI accusation by abstaining; it does not establish human authorship. |
| FP03 | false_positive | 200 | 0.805100 | 0.424341 | 0.690872 | unsure | HELD | Label changed from ai to unsure at unchanged score 0.690872. The 0.80 threshold avoids an AI accusation by abstaining; it does not establish human authorship. |
| FP04 | false_positive | 200 | 0.832900 | 0.367147 | 0.693174 | unsure | HELD | Label changed from ai to unsure at unchanged score 0.693174. The 0.80 threshold avoids an AI accusation by abstaining; it does not establish human authorship. |
| FP05 | false_positive | 200 | 0.800500 | 0.782179 | 0.795004 | unsure | HELD | Label changed from ai to unsure at unchanged score 0.795004. The 0.80 threshold avoids an AI accusation by abstaining; it does not establish human authorship. |
| FP06 | false_positive | 200 | 0.881400 | 0.317243 | 0.712153 | unsure | HELD | Label changed from ai to unsure at unchanged score 0.712153. The 0.80 threshold avoids an AI accusation by abstaining; it does not establish human authorship. |
| FP07 | false_positive | 200 | 0.881600 | 0.300000 | 0.707120 | unsure | HELD | Label changed from ai to unsure at unchanged score 0.707120. The 0.80 threshold avoids an AI accusation by abstaining; it does not establish human authorship. |
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
| MF08 | malformed | 200 | 0.767900 | 0.323354 | 0.634536 | unsure | HELD | The accepted long text remains coherent and logged. Its unchanged score 0.634536 now maps to unsure under the 0.80 threshold. The 400-model-token/full-text-style coverage mismatch remains. |
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

## Health before; wait ten seconds

```json
{
  "binoculars_loaded": false,
  "binoculars_performer": "distilgpt2",
  "detector_loaded": false,
  "detector_model": "gpt2",
  "log_entries": 656,
  "ok": true,
  "rate_limiting": true
}
```

## Health immediately after the flood

```json
{
  "binoculars_loaded": true,
  "binoculars_performer": "distilgpt2",
  "detector_loaded": true,
  "detector_model": "gpt2",
  "log_entries": 712,
  "ok": true,
  "rate_limiting": true
}
```

## Ten audit entries

Selected IDs: EV01, EV02, EV05, FP03, FP05, PI01, PI02, PI05, MF08, FL01_10.

```jsonl
{"binoculars_score": 0.0031, "binoculars_used": false, "combined_score": 0.26444999999999996, "confidence": 0.26444999999999996, "content_id": "c_ca7079b9eb68", "creator_id": "attacker_EV01", "guess": "human", "label": "human", "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.", "model_score": 0.1635, "perplexity_score": 0.1635, "status": "decided", "style_score": 0.5, "timestamp": "2026-11-12T11:24:36+00:00", "word_count": 84}
{"binoculars_score": 0.1684, "binoculars_used": false, "combined_score": 0.41601, "confidence": 0.41601, "content_id": "c_1b67d8a97e0a", "creator_id": "attacker_EV02", "guess": "unsure", "label": "unsure", "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.", "model_score": 0.5943, "perplexity_score": 0.5943, "status": "decided", "style_score": 0.0, "timestamp": "2026-11-12T11:24:36+00:00", "word_count": 93}
{"binoculars_score": 0.064, "binoculars_used": false, "combined_score": 0.22557170731707316, "confidence": 0.22557170731707316, "content_id": "c_627e064fdaa5", "creator_id": "attacker_EV05", "guess": "human", "label": "human", "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.", "model_score": 0.3212, "perplexity_score": 0.3212, "status": "decided", "style_score": 0.0024390243902439046, "timestamp": "2026-11-12T11:24:36+00:00", "word_count": 81}
{"binoculars_score": 0.9195, "binoculars_used": false, "combined_score": 0.6908722110238241, "confidence": 0.6908722110238241, "content_id": "c_ab6d26e7e97f", "creator_id": "attacker_FP03", "guess": "unsure", "label": "unsure", "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.", "model_score": 0.8051, "perplexity_score": 0.8051, "status": "decided", "style_score": 0.42434070341274727, "timestamp": "2026-11-12T11:25:33+00:00", "word_count": 83}
{"binoculars_score": 0.9086, "binoculars_used": false, "combined_score": 0.7950036007684792, "confidence": 0.7950036007684792, "content_id": "c_70d11bf1cfb0", "creator_id": "attacker_FP05", "guess": "unsure", "label": "unsure", "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.", "model_score": 0.8005, "perplexity_score": 0.8005, "status": "decided", "style_score": 0.7821786692282644, "timestamp": "2026-11-12T11:25:33+00:00", "word_count": 70}
{"binoculars_score": 0.6885, "binoculars_used": false, "combined_score": 0.32375, "confidence": 0.32375, "content_id": "c_0fd99305374c", "creator_id": "attacker_PI01", "guess": "human", "label": "human", "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.", "model_score": 0.4625, "perplexity_score": 0.4625, "status": "decided", "style_score": 0.0, "timestamp": "2026-11-12T11:26:34+00:00", "word_count": 45}
{"binoculars_score": 0.2167, "binoculars_used": false, "combined_score": 0.14307999999999998, "confidence": 0.14307999999999998, "content_id": "c_f3631242348f", "creator_id": "attacker_PI02", "guess": "human", "label": "human", "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.", "model_score": 0.2044, "perplexity_score": 0.2044, "status": "decided", "style_score": 0.0, "timestamp": "2026-11-12T11:26:34+00:00", "word_count": 42}
{"binoculars_score": 0.9088, "binoculars_used": false, "combined_score": null, "content_id": null, "creator_id": "attacker_PI05", "event": "rejected", "guess": null, "http_status": 400, "label": null, "message": "Text is too short for style analysis. Provide at least 3 sentences and 40 words.", "model_score": 0.6401, "perplexity_score": 0.6401, "reason": "insufficient_style_input", "status": "rejected", "style_score": null, "timestamp": "2026-11-12T11:26:34+00:00", "word_count": 28}
{"binoculars_score": 0.5481, "binoculars_used": true, "combined_score": 0.6345361319963677, "confidence": 0.6345361319963677, "content_id": "c_9029772a112a", "creator_id": "attacker_MF08", "guess": "unsure", "label": "unsure", "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.", "model_score": 0.7679, "perplexity_score": 0.9876, "status": "decided", "style_score": 0.3233537733212259, "timestamp": "2026-11-12T11:27:36+00:00", "word_count": 11330}
{"combined_score": null, "content_id": null, "creator_id": "attacker_flood", "event": "rejected", "guess": null, "http_status": 429, "ip_address": "127.0.0.1", "label": null, "limit": "9 per 1 minute", "model_score": null, "rate_limit_key": "127.0.0.1", "rate_limit_key_type": "ip_address", "reason": "rate_limited", "status": "rejected", "style_score": null, "timestamp": "2026-11-12T11:29:37+00:00"}
```
