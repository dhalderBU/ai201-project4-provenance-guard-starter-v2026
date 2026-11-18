# Duplicate-field diagnostic — after

| Duplicate field | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|
| content_hash | 503; verified=false | 503; verified=false | 503; verified=false | MET |
| Certificate_id | 503; verified=false | 503; verified=false | 503; verified=false | MET |
| status | 503; verified=false | 503; verified=false | 503; verified=false | MET |

Target: each ambiguous record returns 503, verified: false, certificate_store_unavailable.
Full requests, responses, intentionally corrupted files, logs and image identity are retained.
