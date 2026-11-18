# Running Provenance Guard

Run commands from the repository root. The shell examples use Bash or Zsh.
Commands beginning with `docker compose` are entered on the Docker host;
`exec` runs the remaining command inside the container. API examples use
`PROVENANCE_URL`, selected for your run mode below.
This guide describes the current source code and Docker configuration; it does
not describe the original starter stubs or a different model configuration.

Choose one service instance to use for a session:

| Run path | API address from the host | Records |
| --- | --- | --- |
| Docker Compose | `http://127.0.0.1:5001` | Repository `logs/` directory, mounted at `/app/logs` |
| Local IDE / native Python on macOS/Linux | `http://127.0.0.1:5000` | Repository `logs/` directory |

Both run paths use the same `logs/` directory for submission histories,
certificates, audit entries, and operational metrics. Run one instance at a time
against that directory.
For a diagram of the implemented workflows, see [PROGRAM_FLOW.md](PROGRAM_FLOW.md).

Start with [Docker deployment](#docker-deployment) or
[local Python/IDE setup](#native-python-setup-and-startup), then use the
[shared API instructions](#check-the-api-and-submit-text).

## Prerequisites

- Docker path: Docker Desktop or Docker Engine with the Compose plugin running.
  The current built image is Linux ARM64, tested on Apple Silicon.
- Native path: Python 3.12 is the tested version here. The project's environment
  checker accepts Python 3.11–3.13. Use macOS, Linux, or a Linux environment such
  as WSL; `verification.py` imports the Unix-only
  [`fcntl` module](https://docs.python.org/3/library/fcntl.html), so native Windows
  Python cannot import the current application.
- Internet access for installing dependencies and downloading uncached models.
  No hosted inference API key is required.
- Enough disk space and memory for Python, PyTorch, both models, and inference.
  The environment checker uses a 9 GB free-disk threshold and a 4 GB RAM
  recommendation; these are setup checks, not measured peak usage guarantees.

The Docker dependency lock pins exact package versions and download hashes.
The native `requirements.txt` mostly specifies version ranges, so installing it
on another date may select different versions. Neither path currently pins the
Hugging Face model revisions in application code.

---

<a id="run-the-existing-application-with-docker"></a>

## Docker deployment

This packages the current source code without changing the detector or review
workflow. Docker runs the application on CPU. The current `config.py` defaults
are `gpt2` and `distilgpt2`, with a 100-word Binoculars gate and a 50/50 model
blend in `app.py`. Automatic `human` assessments and approved manual reviews
share `logs/certification_log.jsonl`; exact certified text bypasses scoring.

Start Docker Desktop. Run the following commands from the repository root.

### Docker: build the image

```bash
docker build -t provenance-guard:local .
```

The image includes Python 3.12, the application, all root-level Python and
Markdown files, supporting documentation, small evaluation/attack fixtures,
Gunicorn, and CPU PyTorch. Calibration and dataset-download dependencies are
also installed, so the packaged helpers can be invoked explicitly.
`requirements-docker.lock` pins the resolved Python dependencies and their
download hashes. The base Python image is pinned by digest. The build uses
your machine's architecture; the current image and dependency resolution have
been checked on Linux ARM64 through Docker Desktop on Apple Silicon. An AMD64
build has not been validated. An existing ARM64 image needs a compatible runtime
or emulation when transferred to a different CPU architecture.

### Docker: prepare the log directory

```bash
mkdir -p logs
```

On Linux, the host `logs/` directory and any existing log files must be writable
by container UID/GID `10001`. Configure that access before starting containers;
ownership set inside the image does not change a bind-mounted host directory.
The current Docker Desktop setup on macOS was checked for read/write access.

### Docker: prepare the models

```bash
docker compose run --rm --no-deps app python -c "import binoculars_signal; print(binoculars_signal.warm_up())"
```

This downloads and checks the models without scoring text or writing audit
results. It can be run before starting the service, after building the image.
The first download needs internet and disk space. Model files are stored in the
persistent `model-cache` volume (`HF_HOME=/models`) and reused on subsequent
runs. Model weights are not baked into this image. At startup, the service loads
them into its inference process, outside the request budget. Wait for `/health`
to report `inference_ready: true` before sending scoring requests. Models follow the revisions
selected by the existing application's loaders; they are not revision-pinned.

### Docker: start the service

```bash
docker compose up --build -d
```

This single command also builds the image if needed. The API is available at
`http://127.0.0.1:5001`; the service listens on port 5000 inside the container.
Gunicorn runs as a non-root user with one HTTP worker and four threads, debug
mode off, and a 300-second worker watchdog. The application has its own
**three-second request budget**, described below. One HTTP worker shares the
in-memory rate limits and circuit breaker; restarting resets those counters.
`gunicorn_conf.py` starts a separate persistent CPU process for scoring. This
lets the application stop overdue computation while health and metrics requests
continue to respond.

### Docker: check readiness and submit a sample

```bash
curl http://127.0.0.1:5001/health
curl -X POST http://127.0.0.1:5001/ping \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello from Docker"}'
docker compose ps
docker compose logs --tail=50 app
```

`/health` checks that the service responds; container health does not prove model
readiness. `inference_ready: false` is normal while models load. Before readiness,
scoring returns HTTP 503 with `error: "model_not_ready"` and `Retry-After`.
`binoculars_loaded` and `binoculars_startup_error` separately describe the optional
performer. If that model fails to load but the detector is ready, the existing
perplexity-only fallback remains available. Fix its cache/configuration and
restart the service to retry the optional model's initialization.
Use the existing `/submit`, `/appeal`, and review endpoints at this port.
From the repository checkout on the host, score this tracked sample after model
preparation. This command reads the host copy of the sample; the three tracked
sample JSON files are also included under `/app/samples` in the image:

```bash
curl -X POST http://127.0.0.1:5001/submit \
  -H 'Content-Type: application/json' \
  --data-binary @samples/clearly_human.json
```

### Docker: persistent records, stopping, and backups

Compose mounts `./logs` beside `compose.yaml` at `/app/logs`, including submissions,
audit entries, issued certificates, and operational metrics. Docker reads and
updates the same files as an IDE or native Python run. Compose creates a missing
host `logs/` directory. Log writers also create missing parent directories and
open files in append mode, creating each file on its first write while preserving
existing records. In every deployment,
application code resolves log paths relative to the directory containing
`config.py`, independently of the process working directory. The `app-results`
volume stores helper outputs under
`/app/results`; `model-cache` stores downloaded models and Hugging Face dataset
caches under `/models`. The image excludes existing logs, generated results,
large downloaded datasets, `.env`, and the host's virtual environment. Copying
the image to another machine does not copy the host logs or these volumes.

```bash
docker compose down
docker compose up -d
```

These commands preserve the host `logs/` directory and both named volumes.
`docker compose down --volumes` deletes helper outputs and model caches from
those volumes; the host `logs/` directory remains.
While the service is running, copy its records into an unused directory when
you need a run record for the assignment. For a consistent backup, stop incoming
submissions and reviews while copying the files:

```bash
mkdir -p results
mkdir results/docker-session && \
  docker compose cp app:/app/logs/. results/docker-session/

mkdir results/docker-helper-output && \
  docker compose cp app:/app/results/. results/docker-helper-output/
```

Use a new output directory for each session and commit capstone criteria before
collecting capstone evaluation results. These launch instructions are separate
from the capstone's acceptance trials.

### Docker: ports and source updates

If port 5001 is occupied, use `PROVENANCE_PORT=5002 docker compose up -d` and
change the URLs accordingly. Keep that setting in the host shell or the Compose
`.env` file for later invocations. After code edits, use `docker compose up --build -d`;
the application code is copied into the image, not mounted from your checkout.

### Docker: deployment on another machine

Copy a source checkout containing the current application changes, Dockerfile,
Compose file, and dependency lock to the deployment machine. Run the Docker
build, model preparation, and startup commands there. Its `./logs` directory is
relative to its own `compose.yaml`; logs stay on that machine. Existing logs and
model-cache volumes are not transferred with an image or Git checkout unless
you copy them separately.

The published API port binds to loopback by default. To access a remote Docker
deployment from your laptop while retaining that binding, open an SSH tunnel
(replace `user@server` with your deployment host):

```bash
ssh -N -L 5001:127.0.0.1:5001 user@server
```

Then use `http://127.0.0.1:5001` on the laptop. Choose another local tunnel port
if that port is occupied. ARM64 was tested; other architectures need their own
compatible build and validation.

### Docker: dependency-lock maintenance

After an intentional dependency update, regenerate the lock with `uv`. Update
the explicit version selections in `requirements-docker.in` too when they would
otherwise conflict with the new requirements. This optional maintenance command
requires `uv`; it is not needed to build or run the existing locked image:

```bash
uv pip compile requirements-docker.in --python-version 3.12 \
  --python-platform aarch64-unknown-linux-gnu --torch-backend cpu \
  --index-strategy unsafe-best-match \
  --generate-hashes --emit-index-url --output-file requirements-docker.lock
```

---

## Native Python setup and startup

### Local Python: create the environment

Create a virtual environment with a supported interpreter, then install the
application dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python test.py
```

Use `python3.11` or `python3.13` only if that is the supported interpreter you
intend to use. The environment check imports the packages and checks `/ping`
through Flask's test client; it is not a full test of scoring, appeals, or the
acceptance criteria. Its model-cache check only inspects the usual home cache,
so a custom `HF_HOME` can make its download warning inaccurate.

### Local Python: prepare the models

Prepare both configured models without scoring text or writing audit records:

```bash
.venv/bin/python -c "import binoculars_signal; print(binoculars_signal.warm_up())"
```

The native cache normally lives under `~/.cache/huggingface`. `HF_HOME` can set
another cache location. Model downloading and cached/offline operation are
provided by [Transformers](https://huggingface.co/docs/transformers/v4.57.1/installation).
The Docker cache is separate from this native cache.

### Local Python: start Flask

Start the service in one terminal:

```bash
AI201_DEBUG=0 .venv/bin/python app.py
```

This runs Flask's development server on `127.0.0.1:5000`. Setting debug to zero
avoids the development reloader during recorded sessions. If you instead run
`.venv/bin/python app.py` without that setting, debug mode defaults to enabled
on loopback. Stop the server with Ctrl+C. If the intended service is already
running, use it rather than starting another process on the same port.

### Local IDE: launch configuration

Select this project's `.venv/bin/python` interpreter, set the script to `app.py`,
and use the project root as the working directory. Set `HOST=127.0.0.1`,
`PORT=5000`, and `AI201_DEBUG=0` in the IDE's run configuration. Wait for
`GET /health` to report `inference_ready: true`. Stop the IDE's server before
switching to another launch method that uses the same log directory.

Native Python does not automatically load `.env`; set environment variables in
the shell or IDE. The application resolves `logs/` relative to `config.py`, so
an IDE's working directory does not move the logs.

### Local Python: start Gunicorn

For a native Gunicorn run instead of Flask's development server:

```bash
.venv/bin/gunicorn --config gunicorn_conf.py --bind 127.0.0.1:5000 --workers 1 --threads 4 \
  --timeout 300 --access-logfile - --error-logfile - app:app
```

Gunicorn's command-line `--bind` determines its listening address. The `HOST`
and `PORT` values in `config.py` control `python app.py`; they do not override
Gunicorn's explicit binding. The Docker command is fixed to container port 5000.

<a id="gpu-inference"></a>

## Current model, device, and scoring settings

| Setting | Current value or behavior |
| --- | --- |
| Detector and Binoculars observer | `gpt2` by default |
| Binoculars performer | `distilgpt2` |
| Device | CPU: the current loaders do not move models or tensors to CUDA/MPS |
| Model text limit | First 400 tokens |
| Binoculars inclusion threshold | At least 100 whitespace-separated words |
| Model blend at/above threshold | 50% perplexity and 50% Binoculars, rounded to four decimals |
| Below threshold or unavailable Binoculars | Perplexity supplies the model score |
| Final submission blend | 70% model and 30% style |
| Final labels | `human` at/below 0.45; `unsure` between 0.45 and 0.60; `ai` at/above 0.60 |
| Style minimum | Three sentences and 40 word tokens |
| MATTR | 50-word window; AI anchor 0.68, human anchor 0.82 |
| Automatic appeal blend | 60% perplexity and 40% style for each text variant |

Binoculars is computed even below its inclusion threshold. Setting
`BINOCULARS_PERFORMER = None` in `config.py` selects single-model Binoculars;
it does not disable the calculation. The current Binoculars curve uses midpoint
`0.85` and steepness `20.0`.

`AI201_DEVICE`, `AI201_BINOCULARS`, and `AI201_BINOCULARS_PERFORMER` are not read
by the current code. Setting them will not enable GPU inference, disable
Binoculars, or change the performer. `/health` does not return
`inference_device` or `binoculars_enabled`.

These application environment variables are implemented:

| Variable | Default | Effect |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Binding for `python app.py`; debug is disabled when this is not loopback. |
| `PORT` | `5000` | Port for `python app.py`. |
| `AI201_DEBUG` | `1` | Enables debug only on loopback; use `0` for recorded runs. |
| `AI201_DETECTOR_MODEL` | `gpt2` | Selects the detector/observer model. Changing it can require recalibration and a compatible performer. |
| `AI201_REQUEST_TIMEOUT_ENABLED` | `1` | Enforce the shared request processing budget; `0` disables it. |
| `AI201_REQUEST_TIMEOUT_SECONDS` | `3` | Positive finite processing-time limit in seconds. |
| `AI201_CIRCUIT_BREAKER_ENABLED` | `1` | Pause scoring after repeated timeouts; `0` disables the breaker. |
| `AI201_CIRCUIT_BREAKER_FAILURE_THRESHOLD` | `3` | Scoring timeouts without an intervening successful scoring request needed to open the circuit. |
| `AI201_CIRCUIT_BREAKER_RECOVERY_SECONDS` | `30` | Positive cooldown before allowing one recovery probe. |
| `AI201_OPERATIONAL_METRICS_ENABLED` | `1` | Write request receipts and completions to the operational JSONL file. |
| `AI201_INFERENCE_PROCESS_ENABLED` | `1` | Keep enabled for deployment. `0` is only for in-process mock-based tests, with timeouts disabled. |

`HF_HOME` is a Hugging Face library setting. It changes the model-cache location,
not the scoring rule. Restart native Python after source or environment changes.

### Docker: environment settings and rebuilding

`PROVENANCE_PORT` selects the host-side published port; it does not change scoring.
Compose forwards the timeout, circuit-breaker, and operational-logging variables
listed above. It does not forward arbitrary host variables; add explicit service
environment entries if needed.
Compose reads its `.env` file for interpolation of those declared variables.
After source changes, rebuild and recreate with `docker compose up --build -d`.

### Docker: model-cache sizes

| Model | `model.safetensors` size |
| --- | ---: |
| `gpt2` | 548,105,171 bytes (about 548 MB) |
| `distilgpt2` | 352,824,413 bytes (about 353 MB) |

These are measured weight-file sizes, not peak RAM or total installation size.
Tokenizers, dependencies, cache metadata, and inference tensors add overhead.
The application runs models locally; the course's local-with-logs Path B is
appropriate. A hosted deployment would need its own resource and persistence
assessment. No particular free-host plan is assumed here.

## Check the API and submit text

In a second terminal, select the instance you started:

### Docker: select the API address

```bash
PROVENANCE_URL=http://127.0.0.1:5001
```

### Local Python/IDE: select the API address

```bash
PROVENANCE_URL=http://127.0.0.1:5000
```

Use the actual host port if you changed it. Run the following shared commands
in the same terminal where you set `PROVENANCE_URL`.

### Shared API: health and ping

```bash
curl -sS "$PROVENANCE_URL/health"
curl -sS -X POST "$PROVENANCE_URL/ping" \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello"}'
```

`/health` returns `inference_ready`, `detector_loaded`, `binoculars_loaded`, model
names, startup errors, timeout settings, circuit state, `rate_limiting`,
`log_entries`, and `ok`. HTTP 200 and `ok: true` mean the HTTP service responded;
check `inference_ready` separately before scoring. These fields are specific to
`/health`, not the normal `/submit` response. The loading flags describe the
serving process. Running the preparation command
in another process fills the disk cache but does not set these flags to true.

### Shared API: submissions and automatic certification

From the host repository, submit the tracked example file:

```bash
curl -sS -X POST "$PROVENANCE_URL/submit" \
  -H 'Content-Type: application/json' \
  --data-binary @samples/clearly_human.json
```

A newly scored request returns HTTP 200 with a real `content_id`, label,
reader-facing message, and scores. The sample filename is not a guarantee of
the returned classification. Empty or insufficient text returns HTTP 400;
`/submit` is implemented and does not return the old starter's HTTP 501.
Save the returned `content_id` for subsequent requests to the same instance.

A newly scored `human` result also returns `certification_status="certified"`,
`certificate_id`, and `credential`. It appends an `automated_assessment`
certificate to `logs/certification_log.jsonl`. Automatic appeals that conclude
`human` use the same store and bind their certificate to the complete original
text. Scores of `ai` or `unsure` do not create certificates. Manual approvals
append `draft_review` certificates to the same file; an automatic certificate
does not prevent a later request for manual review.

`config.CERTIFICATION_LOG` is the single storage setting. New records have
`schema_version=1` and a unique `certification_event_id`, suitable as a future
NoSQL document key. The short `Certificate_id` identifies the content and can
repeat; it is not a unique document key. `credential.method` identifies the
certification process, and automatic records retain the assessment source and
scores or appeal votes. New credentials use `type="content_certification"`.

Before scoring, `/submit` hashes the complete UTF-8 text and searches the saved
certificates. An exact match with a valid approval returns HTTP 200 with
`status="already_certified"`, `already_certified=true`, `verified=true`, and
`message="This content is already certified."`. The response includes the
existing `content_id`, `certificate_id`, full `credential`, and
`latest_certification_at`. No certificate ID is required in the request.
The latest matching approval is selected by its timestamp, even when separate
approvals share the same text or use historical UUID certificate IDs.

This lookup skips model scoring and preserves the submission, audit, certificate,
and approval date. It remains subject to rate limits and the request deadline,
and is recorded in the operational log. Matching content does not attribute the
original author's work to the person resubmitting it. Changed whitespace,
punctuation, or Unicode produces a different full hash and follows normal scoring;
matching only the eight-character certificate suffix is insufficient. Legacy
records without a saved hash also follow normal scoring. A corrupt/unreadable
certificate store returns 503 `certificate_store_unavailable`; an invalid or
conflicting matching approval returns 409 `certificate_unverifiable`.

### Shared API: routes and appeals

| Route | Required input or purpose |
| --- | --- |
| `POST /ping` | Optional JSON message; echoes it and identifies the service. |
| `GET /health` | Service and model-loading status. |
| `GET /metrics` | Operational report; optional `hours` and `download=1` query parameters. |
| `POST /submit` | JSON `text`; optional `creator_id`. |
| `POST /appeal` | Existing `content_id` and non-empty `reasoning`; defaults to automatic reassessment. |
| `POST /appeal` with `review_type="human_verification"` | Also requires non-empty `additional_text`; returns HTTP 202 and a review request ID. |
| `GET /verification/review/<content_id>` | Retrieve original text, review evidence, and saved outcome. |
| `POST /verification/review` | `content_id` and `status` (`certified` or `not_certified`); optional `reviewer` and `review_notes`. |
| `POST /verification/verify` | `certificate_id` and the exact `text` to compare with that certificate's saved hash. |
| `GET /content/<content_id>` | Retrieve current content/review status and any issued certificate. |
| `GET /log` | Audit entries; optional `limit` and `content_id` query parameters. |

For example, replace `c_REPLACE_WITH_RETURNED_ID` with the ID returned above:

```bash
curl -sS -X POST "$PROVENANCE_URL/appeal" \
  -H 'Content-Type: application/json' \
  -d '{"content_id":"c_REPLACE_WITH_RETURNED_ID","reasoning":"Please recheck this assessment."}'
```

Automatic reassessment returns HTTP 200 and keeps the appeal `under_review`.
It uses three text variants and a majority vote. A `human` majority creates an
`automated_assessment` certificate while the appeal remains `under_review`.
The human-review path is implemented in `verification.py`. The current reviewer
endpoint is unauthenticated. See [PROGRAM_FLOW.md](PROGRAM_FLOW.md) for the full
sequence and the limits of a certificate backed by this application's records.

### Shared API: request and approve a manual review

Replace the placeholder content ID with the one returned by `/submit`, and
provide the actual supporting draft and reviewer details:

```bash
curl -sS -X POST "$PROVENANCE_URL/appeal" \
  -H 'Content-Type: application/json' \
  -d '{"content_id":"c_REPLACE_WITH_RETURNED_ID","review_type":"human_verification","reasoning":"Please review my drafts.","additional_text":"REPLACE_WITH_SUPPORTING_DRAFT"}'

curl -sS "$PROVENANCE_URL/verification/review/c_REPLACE_WITH_RETURNED_ID"

curl -sS -X POST "$PROVENANCE_URL/verification/review" \
  -H 'Content-Type: application/json' \
  -d '{"content_id":"c_REPLACE_WITH_RETURNED_ID","status":"certified","reviewer":"REPLACE_WITH_REVIEWER_NAME","review_notes":"REPLACE_WITH_REVIEW_FINDINGS"}'
```

Use `status="not_certified"` for a declined review. The review request must exist
before a decision can be recorded. An automatic certificate still allows a
manual review; an already approved manual review does not allow another request.

### Shared API: verify text against a certificate

After automatic certification or a manual approval, copy `credential.Certificate_id`
from the response or `GET /content/<content_id>`. The verification request
uses the lowercase field `certificate_id`. Replace both example values below
with that ID and the exact certified text:

```bash
curl -sS -X POST "$PROVENANCE_URL/verification/verify" \
  -H 'Content-Type: application/json' \
  -d '{"certificate_id":"REPLACE_WITH_ISSUED_ID","text":"The exact previously certified text."}'
```

For text containing line breaks or quotes, put the correctly JSON-escaped
payload in a file and pass `--data-binary @verify-request.json` instead.

| HTTP status | Response | Meaning |
| --- | --- | --- |
| 200 | `verified: true`, `status: "verified"` | The full hash matches; returns the latest matching certification's content ID and timestamps. |
| 200 | `verified: false`, `status: "content_mismatch"` | The check completed, but this text does not match this certificate. |
| 400 | `verified: false`, `error: "bad_request"` | Invalid JSON, missing/invalid fields, empty text, or invalid UTF-8 text. |
| 404 | `verified: false`, `error: "certificate_not_found"` | No record exists for that ID, including when the certificate file is missing or empty. |
| 409 | `verified: false`, `error: "certificate_unverifiable"` | Missing/unusable hash or timestamp metadata, an inconsistent short ID, or conflicting copies of one approval activity. |
| 503 | `verified: false`, `error: "certificate_store_unavailable"` | The certificate file is unreadable, malformed, or contains duplicate JSON field names. |
| 504 | `error: "request_timeout"` | The shared processing deadline expires; this operational error does not include `verified`. |

The shared operational receipt logger can also return 503
`operational_log_unavailable` before the route runs. That error also has no
`verified` field. These responses describe `/verification/verify`; unmatched
text sent to `/submit` proceeds through scoring instead of returning a mismatch.

Duplicate field names are rejected at every object level, including inside a
credential. The parser does not choose between conflicting values or rewrite the
file. Any such record makes certificate verification unavailable until the store
is repaired. Separate approval records may still share the same certificate ID.

Always inspect `verified`, not just HTTP 200. Every new certificate stores
`credential.hash_algorithm="sha256"` and `credential.content_hash` in the shared
certification file. Manual approvals also copy the credential into their review
audit event; automatic appeals include it in their reassessment event. Initial
submission decisions are linked to automatic certificates by `content_id`.
The hash covers the full UTF-8
text, including whitespace, punctuation, and text beyond the model's 400-token
limit. No trimming or Unicode normalization is applied. The lookup does not
run models, change content status, or rewrite old certificates. Existing
certificates without a hash remain readable but cannot pass this content check.

For new approvals, **`Certificate_id = content_hash[-8:]`**: exactly eight lowercase
hexadecimal characters, with no `vh_` prefix. For example, SHA-256 of the text
`abc` ends in `f20015ad`. Identical text approved under separate submissions gets
the same certificate ID, with a separate certification-history record for each
approval. Submission and verification-request IDs remain separate identities.

The eight-character suffix is a lookup key; it is not globally unique. Verification
compares the complete 64-character SHA-256 hash. If different full hashes share
the short ID, only records matching the presented full hash can verify. Among
those records, the latest approval is selected by its timezone-aware `timestamp`,
with file order breaking exact timestamp ties. New approval timestamps preserve
microseconds, so separate approvals within the same second can be ordered.

Successful verification now returns:

| Field | Meaning |
| --- | --- |
| `certificate_id` | The supplied certificate ID. |
| `content_id` | Submission associated with the latest matching approval. |
| `verified_dt_time` | That approval's original human-readable date/time, in UTC. |
| `latest_certification_at` | The same approval's precise timestamp in ISO 8601 UTC, including stored fractional seconds. |
| `certification_method` | `automated_assessment` or `draft_review` for the matching record; `null` on a text mismatch. |

“Latest activity” means **latest successful certification**, not the current
lookup time. Repeating approval of the same already-reviewed submission returns
its original record and does not refresh its date. Resubmitting identical text
returns the existing certificate. A later qualifying automatic appeal or manual
review adds a new certification activity. `GET /content/<id>`
continues to show that particular submission's own approval, rather than another
submission's more recent certification.

For `content_mismatch`, both timestamp fields are `null`; if the short ID spans
multiple full hashes and none matches, `content_id` is also `null`. Older
UUID-based IDs remain usable by their stored ID when their full hashes and dates
are valid. Historical `type="verified_human"` review credentials remain readable.
On first access, the old `verified_human_certification_log.jsonl` file is renamed
to `certification_log.jsonl` without changing its records. If both files already
exist, the service fails closed instead of overwriting either; merge them before
continuing. Historical submission labels are not retroactively certified.

A match establishes equality with the stored certified version. It does not
independently prove authorship or provide public-key issuer authentication.
Verification requests appear in Gunicorn access logs and in the operational
JSONL file, including their HTTP status, duration, `result_status`, and `verified`
result. They do not add business audit events or model-token usage.

## Request timeouts, circuit breaker, and operational metrics

The flags and defaults live near the top of [config.py](config.py). The default
deadline is **3 seconds for the whole Flask request**, shared across perplexity,
Binoculars, and style analysis; an automatic appeal's three variants share the
same budget. Model loading happens before readiness. The isolated process owns
only computation. The HTTP process writes decisions and certificates after a
deadline check, so abandoned scoring cannot later save a decision.

| Situation | HTTP response | Behavior |
| --- | --- | --- |
| Processing deadline expires | 504, `request_timeout` | Stop overdue scoring and reload its models; other handlers return at their next deadline check. |
| Circuit is open | 503, `circuit_open` | Reject scoring immediately with `Retry-After`; other routes remain available. |
| Another request owns the computation process | 503, `inference_busy` | Return immediately with `Retry-After` rather than queue scoring work. |
| Models are loading or primary initialization failed | 503, `model_not_ready` | Inspect `/health` and console logs before retrying. |

Three scoring timeouts without an intervening successful scoring request open
the circuit for a 30-second cooldown by default.
After the cooldown, one scoring request probes recovery. Success closes the
circuit and clears the timeout counter; an unsuccessful probe opens it again.
Successful scoring resets the closed circuit's counter. Rate-limit and validation
failures are counted in metrics but do not trip the circuit. Circuit state and
rate limits are in memory; their operational records survive restarts.
Existing-certificate matches in `/submit` skip inference and do not enter the
scoring circuit. `/health`, `/metrics`, and `/verification/verify` also remain
available while scoring is paused, subject to their own request deadlines.

### Docker: change the processing budget

For example, change the deadline and recreate the Docker service:

```bash
AI201_REQUEST_TIMEOUT_SECONDS=5 docker compose up -d
```

Supply the setting again on later Compose invocations, or put it in the local
`.env` file. Set `AI201_REQUEST_TIMEOUT_ENABLED=0` to disable the deadline, or
`AI201_CIRCUIT_BREAKER_ENABLED=0` to disable only the circuit breaker. Keep process
isolation enabled. If changing Python source defaults, rebuild the image too.

### Local Python/IDE: change the processing budget

Stop the existing native process, then set the same setting when starting it:

```bash
AI201_REQUEST_TIMEOUT_SECONDS=5 AI201_DEBUG=0 .venv/bin/python app.py
```

For an IDE, put these values in its run configuration and restart. These flags
are read at startup. A Compose `.env` file is not loaded by native `app.py`.

### Shared timing limits

The budget starts in Flask's first request hook. It does not include network
transfer or waiting in the web server before Flask begins. Scoring is forcibly
stopped at expiry; other handlers check the deadline cooperatively, including
before successful persistence. OS scheduling, process shutdown, and file I/O can
add response overhead. A write that has already committed keeps its actual
success response and records `deadline_exceeded` if late. This is a server
processing budget, not a guarantee that every client receives bytes within
exactly three seconds. A timed-out automatic appeal may retain its initial
acceptance event, but cannot append a later reassessment from abandoned work.

### Shared metrics queries

Use the `PROVENANCE_URL` selected for Docker or local Python above:

```bash
curl -sS "$PROVENANCE_URL/metrics?hours=24"
curl -sS "$PROVENANCE_URL/metrics?hours=6&download=1" \
  -o operational-metrics.json
```

`hours` defaults to 24 and accepts positive fractional values through 720 hours.
Invalid values return 400. `download=1` adds an attachment filename; the response
is `application/json` in both cases. The report includes:

- Requests received, completed, and lacking a completion record; counts by route.
- Average, minimum, maximum, median, and p95 processing duration in seconds.
- `classification_counts` for successful `POST /submit`: `human`, `ai`, `unsure`.
  Automatic-appeal labels have a separate count to avoid counting them as new submissions.
  An `already_certified` response still counts as a request and HTTP 200, but
  contributes no new classification because it did not run scoring.
- HTTP status counts, including 200, 400, 429, 503, and 504; timeouts and circuit rejections.
- Historical timeout settings with the number of requests and timeouts under each
  setting, plus the current timeout and circuit state.
- Per-model token/forward-pass totals and measured CPU seconds.

The window uses each request's UTC arrival time. All routes count, including
health checks and metrics queries. The current metrics query contributes its
receipt, but its completion has not happened yet. Averages and status counts use
completed requests only. Receipts without completions can indicate in-flight work
or an interrupted process. Receipt/completion pairs are deduplicated by request
ID; malformed records are skipped and counted. Historical records are available
only while logging is enabled and the log file is retained.

### Shared operational-log measurements

`logs/operational_metrics.jsonl` is the separate performance/operations log.
Each request has `request_received` and `request_completed` events sharing a
`request_id`, also returned in `X-Request-ID`. Completion records contain HTTP
status, processing duration, label/result, timeout value and flag, breaker state,
CPU measurements, and per-forward-pass model measurements. The log omits full
request text; original submissions remain in the existing submission store.

`duration_seconds` measures elapsed wall time through response construction,
before writing the completion record and sending the response. `cpu_time_seconds`
adds the HTTP handler thread's CPU time to CPU time measured inside the isolated
scoring process. It excludes model startup, idle time, and network transfer. CPU
seconds can exceed wall seconds because PyTorch uses multiple CPU threads. If a
process is killed before reporting its CPU total, the request total is `null`
and `cpu_measurement_complete` is false; completed forward-pass measurements are
still retained. The report's measured CPU total excludes unknown request totals.

`models` is keyed by the configured model name. For a newly scored submission
with both default models available, GPT-2 runs twice (perplexity and Binoculars
observer), while DistilGPT-2 runs once. An existing-certificate match runs no
models. Optional-model failure and single-model configuration change these counts.
`input_tokens` counts the actual tokens passed to each started forward pass after
the 400-token limit, including repeated use of the same text. Interrupted calls
are included there; `completed_input_tokens` counts only completed calls.
`scored_tokens` counts prediction positions used by completed scoring passes.
**`output_tokens` is zero for both models:** these calls score text and do not
generate a response. Automatic appeals run GPT-2 on each scorable variant and do
not use DistilGPT-2. These are local compute measurements, not hosted API billing.

The operational file and its parent folder are created on the first request.
If the initial receipt cannot be written, the API returns 503 before doing
business work. A completion-write failure is reported to the console and adds
`X-Operational-Metrics: unavailable`; it does not undo an already committed result.
The current implementation scans the JSONL file for each report and does not
rotate it automatically. Retain or back up the host `logs/` directory as
needed; a sufficiently large log can exhaust the metrics request's time budget.

## Logs, helper scripts, and documentation

| Location | Contents |
| --- | --- |
| `logs/submissions.jsonl` | Complete submitted text and initial decisions. |
| `logs/audit.jsonl` | Decisions, submission rejections, appeals, and review events. |
| `logs/certification_log.jsonl` | Automatic `human` assessments and approved manual reviews, distinguished by `credential.method`. |
| `logs/operational_metrics.jsonl` | Request receipts/completions, latency, HTTP statuses, timeouts, classifications, and per-model token/CPU measurements. |
| `results/` | Reports and captured responses created by evaluation scripts. |

Native Python and Docker write to the same repository `logs/` directory. Docker
sees it at `/app/logs` through the Compose bind mount. Each file appears when its
first record is written; the certificate file is created by the first automatic
`human` result or approved manual review.
Console logs and JSONL records are separate.

### Docker: storage mounts and packaged files

| Container path | Persistent storage | Purpose |
| --- | --- | --- |
| `/app/logs` | Host `./logs` bind mount | Audit, submission, certificate, and operational JSONL files, plus the review lock. |
| `/app/results` | `app-results` volume | Evaluation reports and other helper outputs. |
| `/models` | `model-cache` volume | Hugging Face models and dataset caches. |
| Standard output/error | Docker logging | Gunicorn access/error logs, viewed with `docker compose logs app`. |

Logs are directly visible in the host repository's `logs/` folder. Results and
model caches remain in Docker-managed volumes; use the copy commands above to
export helper outputs. The host `logs/` directory must be writable by the
container's application user (UID/GID 10001 on Linux). The image creates the
other directories writable by that user. `config.py` resolves log/result paths
relative to the application directory (`/app` in Docker), independently of the
working directory used to invoke a helper. When running the image without
Compose, mount the deployment's logs directory at `/app/logs` to retain that
same host-visible layout.

The image includes every root-level `*.py` and `*.md`, including `criteria.md`,
the test modules, runners, and calibration/download tools. It also includes
Markdown documentation under `.github/`, `samples/`, and `eval_samples/`, the
three tracked sample JSON files, `eval_samples/samples.json`, and the two attack
CSVs under `attack_set 3/`. Other local datasets and generated reports are not
embedded; supply their paths explicitly or mount an input folder when needed.

### Docker: inspect and run helper tools

With the service running, inspect the packaged tools without sending scoring
requests:

```bash
docker compose exec app python run_eval.py --help
docker compose exec app python run_attacks.py --set 'attack_set 3' --show
docker compose exec app python calibrate.py --help
docker compose exec app sh
```

The historical Unit 8 evaluation can use the service's internal port. Read the
[current compatibility limitation](#five-criteria-three-trials-unit-8) before
using its results. This command creates submissions and audit entries and writes
reports to the `app-results` volume:

```bash
docker compose exec app python run_eval.py \
  --url http://127.0.0.1:5000 --label before
```

Inside this container, use port **5000**; port **5001** is the host mapping.
Use `exec` to call the existing API from the running container. A separate
`docker compose run --rm app ...` container would reach the service at
`http://app:5000`, not its own `127.0.0.1`.

### Docker: download and prepare calibration data

Download/preparation scripts should write beneath `/app/results` so their
outputs are writable and survive container replacement. For example:

```bash
docker compose exec app python download_hc3_samples.py \
  --output-dir /app/results/hc3
docker compose exec app python prepare_calibration_samples.py \
  --source-dir /app/results/hc3 --output-dir /app/results/calibration
docker compose exec -w /app/results app python /app/beemo_file_download.py
```

The Beemo script writes a fixed filename in its working directory, hence the
`-w /app/results` option. Download commands need internet access and disk space;
they are not run automatically at startup. `test.py` is included, but its native
virtual-environment check fails in this image, which installs Python packages
directly. Use `docker compose exec app python -m pip check` for container dependency
consistency. Use the isolated Docker regression command below for mock-based tests;
those tests need different inference settings from the running service.

### Local Python/IDE: helper tools

Native helper commands after environment setup include:

| Command | Purpose |
| --- | --- |
| `.venv/bin/python test.py` | Environment/import checks and a Flask test-client ping. |
| `.venv/bin/python detector.py` | Score a built-in sample with the detector; downloads its model if needed. |
| `.venv/bin/python binoculars_signal.py` | Score a built-in sample with both configured models. |
| `.venv/bin/python stylometry.py "YOUR TEXT"` | Print style measurements for supplied text. |
| `.venv/bin/python run_eval.py --help` | Show evaluation options without sending requests. |
| `.venv/bin/python run_attacks.py --help` | Show attack-runner options. |
| `.venv/bin/python run_paced_attacks.py --help` | Show options for paced attack runs. |

Calibration fitting uses `scikit-learn`, and `beemo_file_download.py` uses
`datasets`. Docker installs both through `requirements-docker.in` and the lock.
They remain optional extras outside the image and are not listed in the native
`requirements.txt`. The scripts also need their specified input datasets.
Their availability is not implied by passing the basic environment check.

## Current certification and operational regression checks

These tests use temporary records and mocked scoring where appropriate. They
cover automatic/manual certificates, full-hash matching, legacy-file migration,
time limits, circuit recovery, and metrics. Real worker-process timeout tests
enable their required settings internally. Disabling inference isolation in
these commands is only for tests; keep it enabled in the deployed application.

### Local Python: regression checks

```bash
AI201_INFERENCE_PROCESS_ENABLED=0 AI201_REQUEST_TIMEOUT_ENABLED=0 \
  .venv/bin/python -B -m unittest \
  test_automatic_certification test_submit_certification \
  test_content_verification test_verification test_operations
```

### Docker: isolated regression checks

After building the current image, run tests in a disposable container with no
host log mount and no model downloads:

```bash
docker run --rm --network none \
  -e AI201_INFERENCE_PROCESS_ENABLED=0 -e AI201_REQUEST_TIMEOUT_ENABLED=0 \
  --entrypoint python provenance-guard:local -B -m unittest \
  test_automatic_certification test_submit_certification \
  test_content_verification test_verification test_operations
```

Full unittest discovery also includes older GPU/model-blend tests that reference
settings no longer implemented, such as `BINOCULARS_ENABLED`, and fail with the
current configuration. The commands above cover 98 certification and operations
tests; they do not include those historical tests.

## Rate limits and attack runs

These commands create submissions, audit entries, and result files. Use the
intended instance and preserve the required order of criteria and results
commits before collecting assignment evidence.

`POST /submit` permits nine requests per minute and 400 per day independently
for each IP address and each valid creator ID. Exceeding either allowance
returns HTTP 429. Keep `RATE_LIMITING_ENABLED = True` for Unit 8 runs.
`AI201_RATE_LIMITS` is not an implemented override. Changing creators does not
reset the shared IP allowance. A process restart resets the in-memory counts.

### Local Python: run attacks against the selected API

With `PROVENANCE_URL` set as above, a burst check is:

```bash
.venv/bin/python run_attacks.py --flood 15 --url "$PROVENANCE_URL"
```

It writes `results/flood_<timestamp>.md`. If the model is ready and all requests
land within one allowance window, successful requests should be followed by
429s. Slow inference can spread requests across windows, so the absence of a
429 alone does not prove the limiter is disabled. Check `/health`, elapsed
time, and existing quota usage. Warm model inference and allow the previous
minute window to expire before a controlled burst.

The repository includes `attack_set 3/attacks.csv` and
`attack_set 3/attacks_malformed_requests.csv`. To inspect one without sending it:

```bash
.venv/bin/python run_attacks.py --set "attack_set 3" --id EV03 --show
```

To run the complete set with pacing:

```bash
.venv/bin/python run_paced_attacks.py --set "attack_set 3" \
  --output results/attack_set3_next_run --url "$PROVENANCE_URL" --health-wait 10
```

Choose an unused output directory each time. The runner preserves input bodies,
paces normal submissions in batches of nine per 61-second window, and begins
flood rows in a fresh window. It records responses, timing, health checks,
source/input hashes, and an audit excerpt. Review attack outcomes against their
targets; HTTP success by itself does not mean an attack was resisted. Its initial
ten-second wait does not guarantee that a previously used IP allowance is fresh.

### Docker: run attacks inside the application container

Use the internal service port and an unused output directory in the results
volume. Run one attack workload at a time:

```bash
docker compose exec app python run_attacks.py \
  --set 'attack_set 3' --id EV03 --show
docker compose exec app python run_attacks.py \
  --flood 15 --url http://127.0.0.1:5000
docker compose exec app python run_paced_attacks.py \
  --set 'attack_set 3' --output /app/results/attack_set3_next_run \
  --url http://127.0.0.1:5000 --health-wait 10
```

Current submissions may return `already_certified` without scores. The attack
runners still record these responses, but their older label/score-based verdict
heuristics need manual review for this response shape.

## Five criteria, three trials (Unit 8)

This is a historical scoring evaluator. It assumes every successful `/submit`
returns fresh scores. Automatic certificates now cause repeated exact text to
return `already_certified` without scores, including repeats within its three
trials. The runner can execute, but may report incomplete scoring or failed
criteria for that reason. An empty store only avoids matches initially; it does
not solve repeats later in the run. Use the current regression checks and the
certification-integrity runner for the new behavior. Do not treat this legacy
report as an unchanged acceptance test for automatic certification.

### Local Python: historical evaluation command

With the intended service running and the host environment activated:

```bash
.venv/bin/python run_eval.py --label before --url "$PROVENANCE_URL"
```

`scenarios.py` defines the fixed cases in `eval_samples/samples.json`, and
`run_eval.py` implements their checks. The runner sends 105 submissions across
five criteria and three trials each, plus appeal requests. It checks health,
waits ten seconds, and paces submissions at nine per 61-second window. Pacing
alone takes roughly eleven minutes; inference and appeals can add more time.
Avoid other submissions to that instance during a measured run. HTTP 429 is
recorded as a failed request rather than silently retried.

Each run creates a new `results/run_<timestamp>_before/` directory with a report,
metrics, raw responses, source/input snapshots, health records, and audit
entries. An explicit `--output results/unused_directory` selects another unused
directory. After a documented improvement, use `--label after` with the same
fixtures and targets. Do not change the service or fixtures between trials.

The label checks use a human cutoff of 0.45 and an AI cutoff of 0.60, matching
the current service defaults. These are the existing Unit 7/8 criteria.
Editing `criteria.md` alone does not change the executable scenarios or checks;
the runner snapshots that file but does not convert Markdown into tests.
The capstone criteria use the separate runner below.

### Docker: historical evaluation command

```bash
docker compose exec app python run_eval.py \
  --url http://127.0.0.1:5000 --label before
```

This has the same repeated-certification limitation described above.

When targeting Docker from host scripts, rebuild the image after code changes
so the source files snapshotted by the runner match the service being measured.
The runner checks host files for changes; it does not independently verify the
container's source revision. The source of each fixed sample is documented in
[eval_samples/README.md](eval_samples/README.md).

## Capstone integrity criteria and cost measurement

### Docker: certification-integrity criteria

From the project root, run all five integrity criteria, five cases each across
three trials, in isolated CPU Docker containers:

```bash
bash certification_data_requests/commands.sh --validate-only
bash certification_data_requests/commands.sh
```

The wrapper needs host `python3`, Docker, and curl. `--validate-only` checks the
fixture pack without containers or API requests. The full command is a separate,
long-running evaluation; it does not require the host virtual environment.
The runner builds the test image, reuses cached models and saves actual requests,
responses, logs and a Markdown results table in a new directory. It uses separate
test volumes; the running application's records are not its test store.
See [the request pack](certification_data_requests/README.md) and
[copyable commands](certification_data_requests/COMMANDS.md) for prerequisites,
manual curl examples and supplemental regressions.

### Docker: historical cost-measurement limitation

The [Milestone 7 measurement command](certification_data_requests/COMMANDS.md#milestone-7-measured-compute-cost)
predates automatic certificate lookup on `/submit`. Its warm-up certifies a
fixed text, then its assessment loop resubmits that same text. The current API
correctly skips inference, so `measure_cost.py` stops at its check that both
models ran. Do not use that command unchanged to measure fresh-scoring cost.
It needs a workload update with independently scored, uncertified inputs before
new ten-run assessment averages are meaningful. Existing saved measurements
describe the earlier code version. For current request measurements, inspect
`/metrics` and `logs/operational_metrics.jsonl`.

## When something goes wrong

| Symptom | Check or action |
| --- | --- |
| Cannot connect to the Docker daemon | Start Docker Desktop or the Docker Engine and confirm `docker info` works. |
| Docker cannot write logs on Linux | Check host `./logs` permissions for UID/GID 10001, including existing files. The bind mount keeps host permissions. |
| Cannot connect to the API | Check the selected instance: host port 5001 for Docker, 5000 for default native Python. Use `/health` or `/ping`. |
| Address/port already in use | Identify the existing service and use it, or choose another port. For Docker, set `PROVENANCE_PORT`; for native Python, set `PORT`. |
| HTTP 400 from `/submit` | Check JSON content type, non-empty text, model token minimum, and the style minimum of three sentences and 40 words. |
| HTTP 404 for content or appeal | The ID is unknown to this service's records. Confirm it came from the same instance. |
| HTTP 409 during human review | Check whether review is already pending/completed, whether a decision conflicts, or whether the original text is unavailable. Read the JSON error code/message. |
| Certificate log not visible locally | Open `logs/certification_log.jsonl`. It appears after an automatic `human` result or manual approval. Docker writes into this same host directory. |
| `/submit` returns no scores with `already_certified` | This is the expected exact-hash lookup response; inspect its saved credential and timestamp. |
| HTTP 429 | An IP or creator allowance was exceeded; inspect the rate-limit headers and audit entry. |
| `DetectorUnavailable` / HTTP 500 | Inspect the download/cache, connectivity, available memory, and console error; run model preparation in the same environment. |
| HTTP 503 `model_not_ready` | Wait for `/health` to report `inference_ready`; inspect its startup error and the model cache if loading fails. |
| HTTP 503 `certificate_store_unavailable` | Check JSONL validity and read/write permissions. If both old and new certificate filenames exist, reconcile their records before continuing. |
| HTTP 503 `circuit_open` or `inference_busy` | Respect `Retry-After`. Check `/metrics` for timeouts, concurrency, and current breaker state. |
| HTTP 504 `request_timeout` | The request exceeded its configured processing budget. Check the operational record, CPU contention, and input length; adjust the budget explicitly if needed. |
| Later requests are slow | Inspect `/metrics` and individual operational records for wall time, model calls, and CPU time. Model reload after a timeout takes place before scoring readiness. |
| GPU environment variables have no effect | The current code does not implement device selection; inference is on CPU. |
| `ModuleNotFoundError: fcntl` on Windows Python | Use a Linux container or WSL; the verification module requires Unix file locking. |
| Script or Markdown file missing inside Docker | Rebuild and recreate with `docker compose up --build -d`; the current image includes root-level Python/Markdown files and the documented fixture folders. |
| Helper cannot write its output | Use `/app/results` for `--output`/`--output-dir`; for Beemo use `docker compose exec -w /app/results app python /app/beemo_file_download.py`. |
| HTTP 501 or a hardcoded placeholder response | You are likely running an older checkout or image; the current `/submit` and `/appeal` are implemented. |
| Expected label does not appear in your samples | Inspect actual scores and thresholds. The configured ranges have no gaps; a sample set may not reach every label. |

## Assignment records and validation scope

Keep the same repository for the extension. Commit the Docker build files,
dependency lock, and updated run instructions before expecting a clean checkout
to reproduce this Docker setup. The local Docker files must be included in the
submitted repository; an image on one computer is not a source submission.

For the capstone, commit your own five criteria before new evaluation results,
preserve earlier evidence, and record the build/test/improvement history. The
assignment requires at least eight new commits and its nine README sections
under a `## Capstone` heading. `logs/` and `results/` are intentionally eligible
for version control. Logs are already visible on the host; helper outputs in
Docker volumes must be copied out before they can be committed. Do not commit
downloaded models or the virtual environment.

This guide was rechecked on **2026-11-18** against the current source, the existing
Python 3.12 environment, and the running ARM64 Docker service. Both native Flask
and native Gunicorn were started with isolated temporary log directories; model
readiness, ping, scoring, automatic certification, repeat lookup, verification,
and metrics download were exercised. Native and Docker dependency checks,
documented helper argument parsing, fixture validation, and Compose configuration
were checked. Docker health, certificate lookup, verification, and metrics download
were checked against the running service. All 98 tests in the regression commands
above passed in each environment.

The full timed attack/acceptance runs, fresh model downloads, and dependency-lock
regeneration were not repeated during this audit. Historical Milestone 7 evidence built
a fresh GitHub clone of `e790d0a` on ARM64 and checked nine API requests, including
assessment, review, verification, rejection and metrics. Existing dependency build
layers were reused; an earlier isolated clone check started with empty log and
model-cache volumes and loaded both models. [Saved checkout evidence](certification_data_requests/validation/clean_checkout.json).
A fresh native dependency installation, AMD64 execution and Windows execution
remain unvalidated.
