# Copy-and-paste commands

Run these from **CodePathWeek7**, the parent of `certification_data_requests`.
Docker must be running. The host needs `python3` and `curl`; no additional host
Python packages or `jq` are needed.

## Run all five criteria, three times, and generate the table

Copy this entire command:

```bash
bash certification_data_requests/commands.sh
```

The command builds a separate test image, then executes the JSON requests with
**curl**. It creates a fresh container and log volume for each criterion/run,
performs the required store checks and container replacement, writes the Markdown
table, and removes its temporary containers and volumes. It prints the exact
`report.md` path at the end. It does not submit test data to your application on
port 5001 or replace that application's container.

Allow several minutes. Criterion 7 requires a pause in each run because ten setup
submissions exceed the application's nine-per-minute limit. A first model download
can take longer. Existing Compose model-cache volumes are reused read-only.

The table has this structure; the runner fills it with measured results:

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 6. Correct hash storage | 5/5 certificate cases | NOT RUN | NOT RUN | NOT RUN | **INCOMPLETE** |
| 7. Latest matching certification returned | 5/5 latest-approval cases | NOT RUN | NOT RUN | NOT RUN | **INCOMPLETE** |
| 8. Altered content fails verification | 5/5 alteration cases | NOT RUN | NOT RUN | NOT RUN | **INCOMPLETE** |
| 9. Unverifiable requests fail closed | 5/5 failure-category cases | NOT RUN | NOT RUN | NOT RUN | **INCOMPLETE** |
| 10. Certification survives container replacement | 5/5 persistence cases | NOT RUN | NOT RUN | NOT RUN | **INCOMPLETE** |

Every run must score **5/5** for a criterion to receive **PASSED**. A completed
run with a failed check produces **MISSED**. Unexecuted runs remain **NOT RUN**.
The command exits with status 1 if any criterion misses; the report and evidence
are still saved. Earlier reports are never overwritten.

Useful optional commands:

```bash
# Validate the JSON, hashes and case counts without starting Docker or sending requests.
python3 certification_data_requests/run_tests.py --validate-only

# Use an image you already built instead of building the dedicated test image.
bash certification_data_requests/commands.sh --skip-build --image provenance-guard:local
```

If your cache is not attached to a running Compose app, add
`--model-cache YOUR_DOCKER_MODEL_CACHE_VOLUME`. For slow initial downloads, add
`--readiness-timeout 600`. This changes startup waiting only, not the application's
request timeout.

## Copy individual curl requests

The following is an optional manual walkthrough against your application on
port 5001. It creates one test submission and its certification in that
application's records. The automated command above uses isolated records instead.
These individual commands do **not** generate the full criteria table.

Copy this setup block once. It saves temporary response files and resolves the
new `content_id` into the review templates:

```bash
BASE_URL=http://127.0.0.1:5001
CERT_MANUAL_DIR=$(mktemp -d)
export CERT_MANUAL_DIR

curl -sS -X POST "$BASE_URL/submit" \
  -H 'Content-Type: application/json' \
  --data-binary @certification_data_requests/fixtures/ordinary.submit.json \
  -o "$CERT_MANUAL_DIR/submission.json"

python3 - <<'PY'
import json, os
from pathlib import Path
folder = Path(os.environ['CERT_MANUAL_DIR'])
content_id = json.loads((folder / 'submission.json').read_text())['content_id']
for name in ('request_human_review', 'approve_review'):
    body = json.loads(Path(f'certification_data_requests/{name}.template.json').read_text())
    body['content_id'] = content_id
    (folder / f'{name}.json').write_text(json.dumps(body))
print('Submitted content:', content_id)
PY

curl -sS -i -X POST "$BASE_URL/appeal" \
  -H 'Content-Type: application/json' \
  --data-binary "@$CERT_MANUAL_DIR/request_human_review.json"

curl -sS -i -X POST "$BASE_URL/verification/review" \
  -H 'Content-Type: application/json' \
  --data-binary "@$CERT_MANUAL_DIR/approve_review.json"
```

Copy any of these curl statements next:

```bash
# Criterion 7 lookup: expect 200, verified: true and the latest matching approval.
curl -sS -i -X POST "$BASE_URL/verification/verify" \
  -H 'Content-Type: application/json' \
  --data-binary @certification_data_requests/criterion_07/requests/case_01_unchanged.json

# Criterion 8: same text with a trailing space — expect 200 and verified: false.
curl -sS -i -X POST "$BASE_URL/verification/verify" \
  -H 'Content-Type: application/json' \
  --data-binary @certification_data_requests/criterion_08/requests/case_01_space.json

# Criterion 9: absent certificate ID — expect 404 and certificate_not_found.
curl -sS -i -X POST "$BASE_URL/verification/verify" \
  -H 'Content-Type: application/json' \
  --data-binary @certification_data_requests/criterion_09/requests/unknown_01.json

# Criterion 9: missing ID — expect 400 and bad_request.
curl -sS -i -X POST "$BASE_URL/verification/verify" \
  -H 'Content-Type: application/json' \
  --data-binary @certification_data_requests/criterion_09/requests/missing_id.json

# Additional regression check: repeating an approval preserves its credential/date.
curl -sS -i -X POST "$BASE_URL/verification/review" \
  -H 'Content-Type: application/json' \
  --data-binary "@$CERT_MANUAL_DIR/approve_review.json"
```

Use `--data-binary @file` so whitespace and Unicode reach the API as stored in
the JSON. Every request file is ready JSON; the two files named `.template.json`
require the actual submission's `content_id`, as shown above. Verification request
IDs are precomputed from the fixed text's full SHA-256 hash.

Criterion 6 additionally reads the certificate and audit files. Criterion 7's full
case needs a second approval and two lookups. Criterion 9's legacy/corruption tests
and criterion 10's container-replacement test are performed by the automated
command, in its isolated volume. Do not append the malformed fixture to your
application's real certificate log.

Each completed run directory also contains `curl_commands.sh`, which records the
exact resolved requests used. Those commands reference temporary ports and content
IDs; their containers are removed after testing. They are evidence to inspect,
not a standalone replay script. Use `commands.sh` to recreate a complete test run.

## Additional regression checks

These six existing tests cover read-only lookup, stable IDs for repeated content,
approval retries and real eight-character SHA-256 suffix collisions. They are
separate from the 75 acceptance case executions. From the project root:

```bash
AI201_REQUEST_TIMEOUT_ENABLED=0 AI201_INFERENCE_PROCESS_ENABLED=0 \
AI201_CIRCUIT_BREAKER_ENABLED=0 AI201_OPERATIONAL_METRICS_ENABLED=0 \
.venv/bin/python -m unittest -v \
  test_content_verification.ContentVerificationTests.test_exact_unicode_match_is_verified_without_changing_records \
  test_content_verification.ContentVerificationTests.test_same_content_reuses_id_and_lookup_returns_latest_certification_by_time \
  test_content_verification.ContentVerificationTests.test_retry_of_older_approval_does_not_refresh_or_replace_latest_activity \
  test_content_verification.ContentVerificationTests.test_real_suffix_collision_does_not_verify_uncertified_content \
  test_content_verification.ContentVerificationTests.test_collision_lookup_selects_latest_matching_full_hash_not_other_content \
  test_verification.VerificationTests.test_repeating_decision_preserves_certificate_and_conflicting_decision_is_rejected
```

These test-only overrides support mocked inference and temporary records; they do
not change the deployed application. See [RUNNING.md](../RUNNING.md) to create the
Python environment if `.venv` is not available.
