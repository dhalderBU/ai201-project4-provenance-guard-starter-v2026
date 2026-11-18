# Unit 9 submission check

Checked November 17, 2026 (Pacific time). Unit 9 implementation, criteria and
measured evidence were published in commit `e790d0a`, followed by the checkout
validation and final write-up commit. The Unit 8 baseline is `4f2984b`.

Repository URL: [Provenance Guard](https://github.com/dhalderBU/ai201-project4-provenance-guard-starter-v2026).

| Requirement | Status and evidence |
|---|---|
| Same project repository | Met: existing Units 7–8 repository and remote retained. |
| Five numbered criteria with targets and reasons | Present: [criteria 6–10](criteria.md#capstone-additional-5-criteria), five cases each; all five cover the extension, including deliberate failures. |
| Preserve criterion revisions | Available earlier wording and reasons are in `criteria.md`; the original criterion 6 uniqueness sentence was not retained. Frozen trial inputs preserve the definitions actually tested. |
| Run path and environment | Present: [RUNNING.md](RUNNING.md), CPU Docker start command, dependency lock, model setup, persistent logs and API examples. |
| Validate a fresh clone | Met on ARM64: a fresh GitHub clone of `e790d0a` built and passed nine API checks in a recreated container. [Evidence](certification_data_requests/validation/clean_checkout.json). Dependency build layers and isolated volumes were reused; an earlier local clone loaded both models into a new cache. |
| Nine bold labels under `## Capstone` | Present in [README.md](README.md#capstone), with milestone comment markers. Earlier AI-use sections remain in place. |
| Ten structured records and one failure | Present under **Instrumentation**: ten real assessments and one HTTP 400 rejection, with timestamp, input reference, output and duration. Full inputs/responses and operational JSONL are retained. |
| Measured cost and 100-person arithmetic | Present under **What It Costs**: means of ten assessments and ten verifications; workload and exclusions stated. |
| Five criteria across three trials, before and after | Present: two complete five-row tables, each covering 75 case executions; all criteria MET. |
| Diagnose, improve one thing, rerun | Present: duplicate JSON fields were accepted; strict parsing changed supplemental rejection from 0/9 to 9/9. Original scores stayed 75/75. |
| Remaining limitations and next step | Present: tighten criterion 9 to 16 checks, disclose store-wide failure on corruption, prioritize reviewer authentication. |
| Two specific AI-use moments | Present, including disclosure that Codex drafted/revised criteria and implemented/tested the improvement. |
| Criteria written unaided | Not met: AI helped draft and revise the criteria at the user's request. This is disclosed rather than described as unaided work. |
| At least eight new Unit 9 commits | Not met: two completion commits publish this work; the required eight incremental commits were not made. |
| Named criteria commit before any results | Not met: criteria and results were first committed together after testing in `e790d0a`. Later commits cannot establish the required historical order. |
| Publish source and evidence | Met: intended Unit 9 source/docs, the five selected evidence directories and checkout validation are committed and pushed to `origin/main`. Older untracked experiments were left out. |
| Submit repository URL to the course | Outstanding: the course submission destination was not supplied. No course submission has been made. |

The request pack's `.gitignore` includes only the five evidence directories
linked by the final README: acceptance before/after, duplicate-field diagnostics
before/after, and cost measurements. Exploratory runs remain local. Downloaded
models, caches and virtual environments remain excluded.

Submit the repository URL through the course's submission page when its location
is available. Commit-history and unaided-authorship gaps need an honest explanation;
they cannot be repaired by relabeling existing work. The working tree still contains
older untracked experiments that are separate from this Unit 9 publication.
