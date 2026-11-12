# Milestone 6 — remaining failures and submission readiness

This milestone finishes the documentation using the completed before and
after runs. It makes no service, test, criterion, or fixture changes and
does not rerun the attacks or evaluation.

## Final result

The one measured improvement raised `AI_THRESHOLD` from 0.60 to 0.80.
Human-reference attacks labelled AI fell from 6/8 to 0/8, but detections
among the five AI evaluation references fell from 5/5 to 1/5 in each trial.
The full attack outcome changed from 41 HELD / 15 BROKE to 47 HELD / 9 BROKE.
Three criteria meet their original targets; criteria 3 and 5 miss in all
three after trials. These are results on the fixed samples used in this
project, not an independent accuracy estimate.

The README's [What's Still Broken](../../README.md#whats-still-broken)
accounts for all nine remaining broken attacks: EV01, EV02, EV03, EV04,
EV05, EV06, EV09, PI01, and PI02. Each row identifies the stage, mechanism,
next investigation or fix, and reason it was deferred. Criteria 3 and 5
have the same treatment. The creator-ID normalization defect is the next
implementation priority; classification changes need independent samples
and matched controls. The one-improvement constraint is why the route fix
was deferred, not a claim that the defect is acceptable.

The README also includes the two-sentence production tradeoff and a
[Unit 8 AI-use disclosure](../../README.md#how-i-used-ai--unit-8). The
disclosure identifies Codex's implementation and analysis work, the sample
provenance limits, and the unsuccessful external Claude review attempt.

## Evidence index

| Requirement | Saved evidence |
|---|---|
| Limiter and audit instrumentation | [Milestone 1 README section](../../README.md#milestone-1--limit-and-audit-log) |
| All 56 attacks before | [Before report](../week8_milestone2_before_2026-11-12/report.md) |
| Five criteria, three before trials | [Before evaluation](../week8_milestone3_before_2026-11-12/report.md) |
| Verdicts and diagnoses | [Milestone 4 report](../week8_milestone4_2026-11-12/report.md) |
| One declared service change | [Plan](../week8_milestone5_2026-11-12/improvement_plan.json), [patch](../week8_milestone5_2026-11-12/change.patch), [source comparison](../week8_milestone5_2026-11-12/source_comparison.json) |
| All 56 attacks after | [After report](../week8_milestone5_attack_after_2026-11-12/report.md) |
| Five criteria, three after trials | [After evaluation](../week8_milestone5_eval_after_2026-11-12/report.md) |
| Side-by-side results and measured tradeoff | [Milestone 5 report](../week8_milestone5_2026-11-12/report.md), [README comparison](../../README.md#the-improvement) |
| Ten real audit entries, including a 429, in each extract | [Before extract](../week8_milestone2_before_2026-11-12/selected_audit_entries.jsonl), [after extract](../week8_milestone5_attack_after_2026-11-12/selected_audit_entries.jsonl); both pasted in the README |
| Focused validation already completed | [45-test output](../week8_milestone5_2026-11-12/final_focused_tests.txt), [Milestone 5 validation](../week8_milestone5_2026-11-12/validation.json) |
| Final documentation and preservation checks | [Milestone 6 validation](validation.json) |

## Publication and submission

The existing Git origin identifies this repository:
[dhalderBU/ai201-project4-provenance-guard-starter-v2026](https://github.com/dhalderBU/ai201-project4-provenance-guard-starter-v2026).
No replacement repository was created. This is the URL to reuse for the
course; a previous course submission receipt was not available to verify.

Local checkpoint: `week8-milestone6-2026-11-12`. Changes are kept local under
the user's existing instruction. Nothing was pushed or submitted to the
course during this milestone, and no submission receipt is claimed. Local
completion does not make these changes available on the remote repository.

The external Claude review also remains unavailable: the attempt produced
no answer, and the saved opposing review is explicitly Codex self-review.
This limitation is disclosed rather than counted as an external review.
