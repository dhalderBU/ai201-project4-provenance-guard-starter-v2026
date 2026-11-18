# Certified-content integrity request pack

Start with [COMMANDS.md](COMMANDS.md) for commands to copy from the project root.
The complete test command is:

```bash
bash certification_data_requests/commands.sh
```

This pack implements criteria **6–10** in [criteria.md](../criteria.md).
It uses **5 cases per criterion per run**, repeated for **3 runs**: 25 cases per
run, 75 case executions. Multiple requests inside a case do not increase its
case count. Every check in a case must pass.

| Folder | Five cases | Required checks within each run |
|---|---|---|
| `criterion_06` | One per text | Full UTF-8 SHA-256, final-eight-character ID, identical certificate/audit hash metadata |
| `criterion_07` | One per text | Ten lookups return the latest matching approval's identity and timestamps |
| `criterion_08` | One per text | Four changes per text: word, punctuation, trailing space, letter case; all twenty fail verification |
| `criterion_09` | Wrong pairing, unknown ID, legacy record, invalid input, corrupt storage | Respectively 5, 2, 2, 3 and 1 requests; all thirteen fail with the specified response |
| `criterion_10` | One per text | Container replacement preserves each certificate, its approval audit record and verification behavior |

Each folder contains `criterion.json`, five `case_XX.json` descriptions, and its
verification request bodies in `requests/` where applicable. Criterion 6's submit
requests reference the shared `fixtures/` directory. The two shared human-review
templates are resolved using the real `content_id` returned by `/submit`.

The five fixtures are synthetic prose used only to exercise integrity behavior:
ordinary ASCII, non-ASCII text, LF line breaks, surrounding spaces, and a long
text. These tests make no claim about who authored them. Each contains at least
40 words and three sentences. The runner validates full hashes independently on
the host and uses the image's GPT-2 tokenizer without truncation to prove that
the long fixture's word change begins after token 400 and leaves the first 400
tokens unchanged.

The application runs its real CPU models with its default timeout, scoring,
rate-limit and circuit-breaker settings. Each criterion/run gets fresh records.
Setup submission failures count as failures, and failed HTTP requests are not
retried. Criterion 7 waits for the IP rate-limit window before its tenth setup
submission. Each of its five cases includes both approvals and both lookups.

Criterion 9 appends two legacy records without hash metadata, then appends the
malformed line only after the other failure categories have completed. Both
operations target the runner's dedicated test certificate store. Criterion 10
removes and recreates its test container with the same log volume; it does not
merely restart a process. The runner compares each complete certificate and
approval audit record with its saved original and requires exactly five certificates.
Operational logs are retained as evidence but can grow during requests.

Read-only lookup, approval retries and suffix collisions have
[separate regression checks](COMMANDS.md#additional-regression-checks).
Earlier reports keep their original definitions; rerun after revising criteria.

Results go to a new timestamped directory under `results/`:

- `report.md`: the requested Markdown table, with **PASSED**, **MISSED**, or **INCOMPLETE**.
- `results.json`: each case's expected/actual values and pass/fail checks.
- `metadata.json`: immutable image ID, source hashes, tokenizer boundary evidence and execution settings.
- `inputs/`: frozen copies of the request pack and relevant source files.
- `run_1/criterion_06/`, etc.: resolved request JSON, raw response bodies, response JSONL,
  recorded curl commands, container identities, business-file snapshots and final logs.

The runner writes partial results after each criterion, so an interrupted run
cannot be reported as a complete pass. Existing results are never overwritten.
Generated evidence is excluded from Git by this folder's `.gitignore`; add a
selected report explicitly if you want to commit it.
