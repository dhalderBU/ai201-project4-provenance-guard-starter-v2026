# Unit 9 — earlier implementation evidence

Archived before the criteria self-check revision. Counts and examples below
refer to their stated implementation stages; current scope and results are in
[README.md](README.md#capstone).

## Capstone

<!-- Unit9 Milestone 1 start -->

**What This Extends**

I am extending **Provenance Guard**, the text-assessment system I built in Units 7 and 8, in the same repository. It already combines model and style signals, handles appeals, records audit events, and issues a certificate after human review. I know its weak points from my earlier tests: formal human writing can receive an AI label, altered AI text can avoid detection, and short text may not provide enough evidence. The capability I am adding addresses a different gap: a customer cannot currently present text with a certificate ID and check whether it matches the version that was certified.

**The Shape**

I am choosing **C — Extend one capability**: verify content against its certificate. When a human reviewer approves a submission, I will calculate a SHA-256 hash of the complete stored text, encoded as UTF-8, and save it with the existing certificate ID in the certificate record and corresponding audit event. I will add one endpoint that accepts presented text and a certificate ID, looks up that specific certificate, and compares the submitted text's hash with its saved hash. A match will confirm that the text matches the certified version held by this application. The first version will compare text exactly, including whitespace and punctuation. Unknown certificates, changed text, and older certificates without a stored hash will not be reported as verified. This feature is planned; the existing certificate flow does not yet perform this comparison.

Out of scope for this unit:

- **Changing the detector:** I am not adding or retraining models, changing scoring weights, or adjusting classification thresholds as part of this extension.
- **Public-key signing and offline verification:** the check will depend on this application's stored certificate records. A matching content hash will not independently prove human authorship or authenticate the issuer outside this system.
- **Cloud or GPU deployment:** I will use **Path B — local with logs**, running the existing CPU Docker image through the commands in [RUNNING.md](RUNNING.md).

Scope check: I am budgeting about **90 minutes of feature implementation**: approximately 25 minutes to attach the hash during certificate issuance, 35 minutes for the lookup-and-compare endpoint, and 30 minutes for invalid inputs and compatibility with existing certificate records. These are planning estimates, not measured build times. The existing submission store, review flow, certificate IDs, and Docker setup will be reused. I will keep the feature to exact text matching through one endpoint if the build starts exceeding that budget. Structured run logging with inputs, outputs, failures, and request duration, plus a measured cost over ten runs, remains required supporting work for the deployment milestone. The acceptance criteria, trials, and results will be documented separately.

<!-- Unit9 Milestone 1 end -->

<!-- Unit9 Milestone 2 start -->

**Built capability**

I implemented the content-verification capability scoped in Milestone 1. In `verification.py::review_content()`, each new approval now hashes the complete original text as UTF-8 using SHA-256. The resulting `content_hash` and `hash_algorithm` are saved inside the credential alongside its existing `Certificate_id`, in both the certificate file and the review audit event. Repeating an approval preserves the original certificate and hash.

I added **`POST /verification/verify`**, handled by `app.py::verify_certified_content()` and `verification.py::verify_content()`. It accepts `certificate_id` and `text`, finds that specific certificate, and compares the presented text's hash with the hash saved at approval. It checks the full text, including whitespace, punctuation, Unicode characters, and text beyond the detector's 400-token input limit. It does not run either model or change the submission's review status.

Matching text returns HTTP 200 with `verified: true`. Changed text returns HTTP 200 with `verified: false` and `status: "content_mismatch"`; a completed check is not automatically a successful match. Invalid input returns 400, an unknown certificate returns 404, a legacy or unusable certificate returns 409, and unavailable certificate storage returns 503. Older certificates remain readable but are not silently assigned a hash or reported as content-verified. Request examples and the response contract are in [RUNNING.md](RUNNING.md).

**Certificate ID update — November 17, 2026**

New certificates use `Certificate_id = content_hash[-8:]`, without a prefix.
Separate approvals of identical text retain separate history records but share
the ID. Verification compares the complete SHA-256 hash and returns the latest
matching approval's `content_id`, UTC `verified_dt_time`, and precise ISO 8601
`latest_certification_at`. Matching only the eight-character suffix cannot verify
different content. An ordinary lookup or retry of an already-completed approval
does not refresh the certification date. Existing UUID-based IDs remain readable;
their records are not rewritten. The full response contract is in [RUNNING.md](RUNNING.md).

**Build and regression checks**

For the November 17 certificate-ID update, the focused suite passed **149 tests**
in both native Python and the CPU Docker image, including 23 content-verification
tests. These cover repeated content, latest-approval ordering, real eight-character
suffix collisions, older UUID certificates, retries, and restart persistence.
An isolated HTTP check using the real CPU models certified the same text twice:
both approvals returned ID `80d6dfa0`, and verification returned the second
approval's timestamp before and after container replacement. Retrying the first
approval preserved its original record. The temporary container and test volume
were removed. These are implementation checks; the five cases per criterion in
each of three formal Capstone runs remain separate, as defined in [criteria.md](criteria.md).
The command under **Operational additions** below runs this focused suite.

The following evidence describes the initial UUID-based implementation, before
the November 17 ID update. Its original response examples are retained as run evidence.

I initially added 13 tests in [test_content_verification.py](test_content_verification.py) covering a known SHA-256 test vector, exact Unicode matching, altered text, certificate-ID binding, changes beyond the model input limit, invalid requests, legacy records, invalid/duplicate certificate records, storage failures, repeat approvals, and lookup after a process restart. The tests also check that verification does not invoke model inference or alter the stored records.

The selected suite passed **104 tests: 13 new tests and 91 existing tests**, both in the native Python 3.12 environment and in the CPU Docker image. The existing tests cover submissions and audit records, appeals, human review, content-status lookup, rate limits, attack pacing, stylometry, and evaluation-runner behavior. This is the focused regression suite, not a claim that every historical test module in the repository was run.

```bash
docker compose exec -T \
  -e AI201_REQUEST_TIMEOUT_ENABLED=0 -e AI201_INFERENCE_PROCESS_ENABLED=0 \
  -e AI201_CIRCUIT_BREAKER_ENABLED=0 -e AI201_OPERATIONAL_METRICS_ENABLED=0 \
  app python -m unittest -b \
  test_content_verification test_verification test_content_api \
  test_appeals test_audit_api test_attack_pacing test_rate_limiting \
  test_stylometry test_eval_runner
```

I also compared `samples/clearly_human.json` using the real CPU models before and after the change. The original submission scores and automatic-appeal results were identical:

| Existing behavior | Before | After |
| --- | --- | --- |
| Submission label | `human` | `human` |
| Model score | `0.4445` | `0.4445` |
| Style score | `0.11507598784194532` | `0.11507598784194532` |
| Combined score | `0.3456727963525836` | `0.3456727963525836` |
| Automatic appeal | `human`, 3 human votes | `human`, 3 human votes |

In an isolated Docker instance, I exercised the full HTTP flow: submit, automatic appeal, request human review, approve, and verify the resulting certificate. These are actual responses from that temporary instance; its test records were removed afterward:

```json
{"certificate_id":"vh_40ab9f36cf684588","content_id":"c_a130bf17f827","hash_algorithm":"sha256","status":"verified","verified":true}
```

Adding one trailing space to the same text produced:

```json
{"certificate_id":"vh_40ab9f36cf684588","content_id":"c_a130bf17f827","hash_algorithm":"sha256","status":"content_mismatch","verified":false}
```

The same HTTP check confirmed that unknown IDs and invalid input return the documented errors, an empty `/submit` still returns 400, and certificate lookup still works after replacing the container while retaining its log volume. After replacement, neither model was loaded when verification succeeded. The main application's existing records were not used for these checks.

This completes the capability build and focused regression checks. Formal acceptance trials and the ten-run cost measurement remain separate work for the later milestones. Request-duration and verification-result instrumentation was added afterward as described below. The existing detector models, scoring settings, and CPU deployment choice are unchanged.

<!-- Unit9 Milestone 2 end -->

**Operational additions**

I added a configurable three-second processing budget and a circuit breaker in
[config.py](config.py). Scoring runs in a persistent CPU process that is killed
on timeout, returning HTTP 504. By default, three consecutive scoring timeouts
pause scoring for 30 seconds; open-circuit requests return 503 with `Retry-After`.
Perplexity, Binoculars, and style analysis share one deadline, as do all variants
of an automatic appeal. Decisions and certificates are written by the HTTP
process after a deadline check. Model loading is outside the request budget;
`/health` reports readiness. The run guide explains the boundary of the budget
and why network and persistence overhead can extend client-observed latency.

The separate [operational log](RUNNING.md#request-timeouts-circuit-breaker-and-operational-metrics)
is `logs/operational_metrics.jsonl`. It captures request arrivals/completions,
HTTP statuses, labels, request duration, CPU measurements, timeout values, circuit
state, and per-model input/output tokens. GPT-2 normally runs twice per submission
and DistilGPT-2 once. Generated output tokens are zero: these models score supplied
text rather than generate text. Incomplete computation is marked explicitly, and
unknown CPU time is not reported as zero.

`GET /metrics?hours=24` returns request counts, average/p50/p95 duration, separate
submission and appeal label counts, status counts including 200/400/429/503/504,
timeouts grouped by the settings used at the time, and model/CPU totals.
`GET /metrics?hours=6&download=1` downloads the same report as JSON. Counts include
health and metrics traffic; the current metrics request is received but not yet
completed. Records persist in Docker's `app-data` volume.

Operational checks are in [test_operations.py](test_operations.py). They exercise
actual child-process cancellation, shared deadlines, concurrent health/metrics
requests, busy rejection, breaker recovery, optional-model fallback, token
accounting, time-window counts, historical settings, and log failures. Run them
alongside the earlier regression suite:

```bash
docker compose exec -T \
  -e AI201_REQUEST_TIMEOUT_ENABLED=0 -e AI201_INFERENCE_PROCESS_ENABLED=0 \
  -e AI201_CIRCUIT_BREAKER_ENABLED=0 -e AI201_OPERATIONAL_METRICS_ENABLED=0 \
  app python -m unittest -b \
  test_operations test_content_verification test_verification test_content_api \
  test_appeals test_audit_api test_attack_pacing test_rate_limiting \
  test_stylometry test_eval_runner
```

Those environment overrides let the earlier tests mock models within their own
process and avoid writing operational records to deployment logs. Operational
tests explicitly enable the new features with temporary storage and isolated
test workers. These implementation checks do not replace formal capstone trials.

The focused suite passed **139 tests** in both native Python and the CPU Docker
image. In an isolated real-model HTTP check, the tracked human sample retained
its `human` label and combined score `0.3456727963525836`, completing in about
0.327 seconds; its automatic appeal retained three human votes. The same check
verified certificate issuance/matching and the report's 400/429 counts. Reducing
the configured budget to 0.01 seconds deliberately produced a 504, followed by
a 503 from an open circuit. Replacing that temporary container retained both
the certificate and operational history, including the distinct 0.01- and
3-second timeout settings. Its test container and record volume were removed
afterward; the application's existing business records were not used for testing.
