#!/usr/bin/env bash
# Run from CodePathWeek7, the parent of certification_data_requests.
# API requests are executed with curl by the Python runner.
set -euo pipefail
python3 certification_data_requests/run_tests.py "$@"
