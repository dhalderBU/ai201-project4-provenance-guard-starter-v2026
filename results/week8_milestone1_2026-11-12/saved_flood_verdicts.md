# Review of saved flood results

This review uses existing evidence only. No requests were rerun.

Scope: the completed 15-request flood and its one changed-creator follow-up.
These are rate-limiter verdicts, not authorship-classification verdicts.
The full 56-input supplied attack set has no saved results in the repository
and remains unassessed.

HELD means requests 1–9 were accepted, requests 10–15 were rejected, and the
changed-creator probe was still rejected by the shared IP allowance.

**Counts: 16 HELD, 0 BROKE.**

| Request | Expected HTTP | Actual HTTP | Model | Style | Combined | Label | Verdict | Diagnosis |
|---|---|---|---|---|---|---|---|---|
| FLOOD-01 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-02 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-03 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-04 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-05 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-06 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-07 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-08 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-09 | 200 | 200 | 0.255900 | 0.239048 | 0.250845 | human | HELD | Within the first nine requests; accepted and scored. |
| FLOOD-10 | 429 | 429 | — | — | — | — | HELD | Minute IP allowance exhausted; rejected before inference. |
| FLOOD-11 | 429 | 429 | — | — | — | — | HELD | Minute IP allowance exhausted; rejected before inference. |
| FLOOD-12 | 429 | 429 | — | — | — | — | HELD | Minute IP allowance exhausted; rejected before inference. |
| FLOOD-13 | 429 | 429 | — | — | — | — | HELD | Minute IP allowance exhausted; rejected before inference. |
| FLOOD-14 | 429 | 429 | — | — | — | — | HELD | Minute IP allowance exhausted; rejected before inference. |
| FLOOD-15 | 429 | 429 | — | — | — | — | HELD | Minute IP allowance exhausted; rejected before inference. |
| NEW-ID-01 | 429 | 429 | — | — | — | — | HELD | A new creator ID still shares the exhausted IP allowance. |

HTTP status codes come from the saved attack runner output and follow-up
response. Signal scores and labels come from matched audit entries. Rejections
have no scores because the limiter runs before inference. The associated JSON
keeps full-precision scores and content IDs.
