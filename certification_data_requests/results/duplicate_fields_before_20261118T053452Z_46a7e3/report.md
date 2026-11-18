# Duplicate-field diagnostic — before

| Duplicate field | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|
| content_hash | 200; verified=true | 200; verified=true | 200; verified=true | MISSED |
| Certificate_id | 200; verified=true | 200; verified=true | 200; verified=true | MISSED |
| status | 200; verified=true | 200; verified=true | 200; verified=true | MISSED |

Target: each ambiguous record returns 503, verified: false, certificate_store_unavailable.
Full requests, responses, intentionally corrupted files, logs and image identity are retained.
