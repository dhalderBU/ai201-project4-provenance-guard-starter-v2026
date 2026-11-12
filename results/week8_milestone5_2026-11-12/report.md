# Milestone 5 — one threshold change, measured before and after

Only service change: `config.py::AI_THRESHOLD`, 0.60 → 0.80.

The change reduced false AI accusations from 6/8 human-reference attacks to
0/8, but reduced detection of the five AI reference samples from 5/5 to 1/5
in each trial and caused the original label criterion to miss.

| Outcome | Before | After |
|---|---|---|
| Full attack set | 41 HELD / 15 BROKE | 47 HELD / 9 BROKE |
| False AI labels on human-reference attacks | 6/8 | 0/8 |
| Correct human labels in that attack family | 0/8 | 0/8 |
| AI references labelled AI per trial | 5/5 | 1/5 |
| Criteria meeting original targets | 4/5 | 3/5 |

| Criterion | Target | Before 1 | Before 2 | Before 3 | Before verdict | After 1 | After 2 | After 3 | After verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1. False positive rate | At most 2/5 human pieces labelled AI | 0/5 AI | 0/5 AI | 0/5 AI | MET | 0/5 AI | 0/5 AI | 0/5 AI | MET |
| 2. AI minus human mean score | Mean gap >= 0.30 (5 AI + 5 human) | 0.509418 | 0.509418 | 0.509418 | MET | 0.509418 | 0.509418 | 0.509418 | MET |
| 3. Correct labels | At least 4/5 correct labels | 4/5 | 4/5 | 4/5 | MET | 3/5 | 3/5 | 3/5 | MISSED |
| 4. Appeal process | 5/5 appeals satisfy the recorded process | 5/5 | 5/5 | 5/5 | MET | 5/5 | 5/5 | 5/5 | MET |
| 5. Complete and accurate audit entries | 10/10 requests logged in the required format | 6/10 | 6/10 | 6/10 | MISSED | 6/10 | 6/10 | 6/10 | MISSED |

## Interpretation

The seven scored human-reference attacks all now receive unsure; the eighth
is still rejected as too short. Avoiding an AI label is not confirmation of
human authorship. The same one evasion fixture remains AI-labelled, so that
attack family does not expose the recall loss seen on the separate five
AI reference texts. Scores and HTTP statuses match their before counterparts.
Only labels and related messages/votes changed.

Criterion 3 regresses because the demo AI score 0.619604 now maps to unsure;
its original target/oracle stays fixed. The existing 0.40/0.45 boundary
mismatch remains. Criterion 5 still records all requests but only six of ten
entries normalize creator IDs as required. The original targets were not
changed, and no second service fix was made.

The threshold was chosen using known failures, so this is an in-sample
comparison, not proof of generalization. A separate validation cohort is
needed before a broader performance claim.

## Evidence

- [Declared improvement plan](improvement_plan.json)
- [Single service-setting patch](change.patch)
- [Source comparison and separate unit-test fixture maintenance](source_comparison.json)
- [Before attack report](../week8_milestone2_before_2026-11-12/report.md)
- [After attack report: all 56 outcomes and audit excerpt](../week8_milestone5_attack_after_2026-11-12/report.md)
- [Paired attack results](attack_comparison.json)
- [Before three-trial evaluation](../week8_milestone3_before_2026-11-12/report.md)
- [After three-trial evaluation: complete real responses](../week8_milestone5_eval_after_2026-11-12/report.md)
- [Paired criterion results and label changes](criterion_comparison.json)
- [Validation: unchanged scores/statuses, repeated trials, 191 new audit entries](validation.json)
- [Final focused tests: 45 passed](final_focused_tests.txt)

The README contains all 56 attack pairs, all five criterion rows, before and
after health calls, ten after-run attack audit entries, and five real
after-trial JSON examples. Nothing above the Unit 8 marker was changed.
