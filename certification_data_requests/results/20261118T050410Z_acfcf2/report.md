# Certified-content integrity — criteria 6–10

Five cases per criterion per run. A case passes only when every check passes.
Three runs: 25 cases per run, 75 case executions. Setup requests are not extra cases.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 6. Correct hash storage | 5/5 certificates have correct full hashes, short IDs and audit copies | 5/5 | 5/5 | 5/5 | **PASSED** |
| 7. Latest matching certification returned | 5/5 text cases return the latest matching approval twice | 5/5 | 5/5 | 5/5 | **PASSED** |
| 8. Altered content fails verification | 5/5 texts reject all four alterations | 5/5 | 5/5 | 5/5 | **PASSED** |
| 9. Unverifiable requests fail closed | 5/5 failure categories return all required responses | 5/5 | 5/5 | 5/5 | **PASSED** |
| 10. Certification survives container replacement | 5/5 certificates retain evidence and verification after replacement | 5/5 | 5/5 | 5/5 | **PASSED** |

## Failed checks

None in the completed cases.

See `results.json` for expected/actual checks, `metadata.json` for source/image identity,
and each run directory for JSON requests, raw responses, recorded curl commands,
business-record snapshots, operational logs and container logs.

Fixture approvals are synthetic test actions; they do not establish human authorship.
