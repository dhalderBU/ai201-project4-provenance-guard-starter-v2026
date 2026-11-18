# seed_submit
curl -sS -i -X POST -H 'Content-Type: application/json' --data-binary @certification_data_requests/results/duplicate_fields_after_20261118T053732Z_533cee/run_1/requests/001_seed_submit.json http://127.0.0.1:51153/submit
# seed_request_review
curl -sS -i -X POST -H 'Content-Type: application/json' --data-binary @certification_data_requests/results/duplicate_fields_after_20261118T053732Z_533cee/run_1/requests/002_seed_request_review.json http://127.0.0.1:51153/appeal
# seed_approve
curl -sS -i -X POST -H 'Content-Type: application/json' --data-binary @certification_data_requests/results/duplicate_fields_after_20261118T053732Z_533cee/run_1/requests/003_seed_approve.json http://127.0.0.1:51153/verification/review
# duplicate_content_hash
curl -sS -i -X POST -H 'Content-Type: application/json' --data-binary @certification_data_requests/results/duplicate_fields_after_20261118T053732Z_533cee/run_1/requests/004_duplicate_content_hash.json http://127.0.0.1:51153/verification/verify
# duplicate_Certificate_id
curl -sS -i -X POST -H 'Content-Type: application/json' --data-binary @certification_data_requests/results/duplicate_fields_after_20261118T053732Z_533cee/run_1/requests/005_duplicate_Certificate_id.json http://127.0.0.1:51153/verification/verify
# duplicate_status
curl -sS -i -X POST -H 'Content-Type: application/json' --data-binary @certification_data_requests/results/duplicate_fields_after_20261118T053732Z_533cee/run_1/requests/006_duplicate_status.json http://127.0.0.1:51153/verification/verify
