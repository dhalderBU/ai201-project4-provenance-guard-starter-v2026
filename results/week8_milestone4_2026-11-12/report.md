# Milestone 4 — verdict and diagnosis review

The original Milestone 2 and 3 evidence is retained unchanged. This review
adds explicit stage diagnoses, grouped mechanisms, and an opposing-verdict
self-review after external Claude access failed. No service change was made.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict | Decision rule |
|---|---|---|---|---|---|---|
| 1. False positive rate | At most 2/5 human pieces labelled AI | 0/5 AI labels | 0/5 AI labels | 0/5 AI labels | MET | Each trial scored all five fixed human-reference samples and returned zero AI labels, which is within the original allowance of two. This is a sample verdict, not a population false-positive rate. |
| 2. AI minus human mean score | Mean gap >= 0.30 (5 AI + 5 human) | 0.5094183499788741 | 0.5094183499788741 | 0.5094183499788741 | MET | Every trial returned a mean AI score of 0.7845462862090351 and a mean human score of 0.27512793623016096; their difference 0.5094183499788741 exceeds the original minimum of 0.30. |
| 3. Correct labels | At least 4/5 correct labels | 4/5 | 4/5 | 4/5 | MET | Each trial had four cases matching both the preassigned expected label and the original score bands, meeting the four-of-five allowance. All three labels appeared. The fifth case exposes the unchanged 0.40 service cutoff versus the written 0.45 cutoff; the numeric target allows one miss and does not make the implementation discrepancy disappear. |
| 4. Appeal process | 5/5 appeals satisfy the recorded process | 5/5 | 5/5 | 5/5 | MET | All five sampled appeals in each trial were accepted, retained under_review status, recorded both audit events, scored the three variants with 60/40 arithmetic, and returned the majority label and applicable warning. This establishes the process for the tested inputs; the live cohort did not produce an unsure majority. Three existing mocked tests separately passed for majority messages, weights, and exact variants. |
| 5. Complete and accurate audit entries | 10/10 requests logged in the required format | 6/10 | 6/10 | 6/10 | MISSED | All ten requests per trial were logged, but four entries per trial violate the explicit requirement to use unknown for invalid creator IDs. Only six of ten conform, below the required 100%; recording the raw value is not enough to meet the whole criterion. |

## Every broken attack

| ID | Stages | Mechanism |
|---|---|---|
| EV01 | signal one, signal two, combining rule | The typo-bearing text receives model 0.1635. MATTR 0.939444 contributes zero AI-oriented vocabulary score, but uniform sentence lengths still give style 0.5. The 70% low model term dominates: combined 0.264450, human. The intended style attack is not, by itself, the demonstrated dominant cause. |
| EV02 | signal two, combining rule | Sentence spread 0.815855 and MATTR 0.894286 exceed the human anchors; low structural punctuation adds nothing. All style contributions are zero. Combining model 0.5943 with style 0 gives 0.416010, unsure. |
| EV03 | signal one, signal two, combining rule | At 105 whitespace words the model uses the 50/50 blend: perplexity score 0.6662 and Binoculars 0.3400 become 0.5031. High MATTR contributes zero vocabulary score; spread supplies style 0.253225. The outer blend yields 0.428137, unsure. |
| EV04 | signal one, signal two, combining rule | The unusual-vocabulary text has model 0.6114. MATTR 0.940541 contributes zero vocabulary score; regular sentence lengths supply style 0.5. The outer blend gives 0.577980, below the 0.60 AI boundary. Unusual vocabulary alone is not proven causal without an unchanged-vocabulary control. |
| EV05 | signal one, signal two, combining rule | The edited text has model 0.3212. Spread 0.625171 and MATTR 0.859394 contribute zero; punctuation supplies the small remaining style score 0.002439. Combined 0.225572 falls in human. |
| EV06 | signal two, combining rule | Sentence spread 1.082600, MATTR 0.848837, and low punctuation make style exactly zero. Model 0.5727 is reduced to combined 0.400890, unsure. Uneven lengths are treated as human-like structure rather than origin evidence. |
| EV09 | signal one, signal two, combining rule | At 110 words, perplexity score 0.7042 and Binoculars 0.5022 blend to model 0.6032. High MATTR and uneven lengths leave style 0.227432. The outer blend gives 0.490470, unsure; the human opening cannot be separated from the AI body by these whole-text measurements. |
| FP02 | signal one, signal two, combining rule | Formal human prose has model 0.7387. Low sentence spread gives its maximum AI-oriented contribution; MATTR 0.769630 adds a vocabulary contribution. Style 0.607937 and the 70/30 blend produce 0.699471, AI. Predictability and regularity are mistaken for authorship. |
| FP03 | signal one, signal two, combining rule | Careful human prose has model 0.8051. Sentence regularity supplies almost all of style 0.424341. The model term contributes 0.563570 and style adds 0.127302, crossing 0.60 at 0.690872 despite the lower style score. |
| FP04 | signal one, signal two, combining rule | Rubric-based human prose has model 0.8329. Sentence regularity contributes style 0.367147 even though vocabulary contributes zero. The weighted terms 0.583030 and 0.110144 produce 0.693174, AI. |
| FP05 | signal one, signal two, combining rule | Technical instructions have model 0.8005, spread 0.262475, and MATTR 0.614000. The normalized spread contribution is 0.964357 and the vocabulary contribution is 1.0, giving style 0.782179. Both signals reinforce the false accusation: combined 0.795004, AI. |
| FP06 | signal one, combining rule | Template-like human correspondence has model 0.8814, contributing 0.616980 after its 70% weight, already above the AI boundary before the nonnegative style term is added. Style 0.317243 raises the final score to 0.712153. The high predictability-based model score is sufficient for this false label. |
| FP07 | signal one, signal two, combining rule | Deliberate human repetition has model 0.8816, whose weighted contribution 0.617120 already exceeds 0.60. MATTR 0.526000 saturates the vocabulary contribution, supplying all of style 0.3. Combined 0.707120 is AI; legitimate repetition is penalized by both signals. |
| PI01 | signal two, combining rule, label mapping | The instruction-bearing text has model 0.4625 and style 0: spread 0.604918 and vocabulary ratio 0.933333 contribute zero AI-oriented style evidence. The ordinary 70/30 calculation produces 0.323750, human. The requested label is reached, but the record does not show instructions overriding scoring. |
| PI02 | signal one, signal two, combining rule, label mapping | The fake-system-message text has model 0.2044 and style 0, producing 0.143080, human through normal scoring. Its requested confidence 0.02 was not returned. This is a label-goal failure under the fixed attack policy, not evidence of a successful authority override. |

## Review artifacts

- [Criterion verdicts](criterion_verdicts.json)
- [Attack measurements and diagnoses](attack_diagnoses.json)
- [Source-provenance checks](provenance_checks.json)
- [Opposing-verdict self-review](opposing_review.md)
- [Prepared Claude prompt](claude_prompt.txt)
- [Unsuccessful external-review attempt](claude_attempt.json)
- [Three focused appeal tests](appeal_branch_tests.txt)
- [Validation and unchanged-file checks](validation.json)

The README, below its Unit 8 marker, contains the grouped patterns, limits,
final decisions, and next-milestone priority.
