#!/usr/bin/env bash
# Run the criteria 6–10 tests from this project's root.
# Usage: bash commands.sh [--validate-only | other runner options]
# Flow: locate this checkout, enter it, then forward options to the test runner.
set -euo pipefail

criteria_project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$criteria_project_dir"
exec bash certification_data_requests/commands.sh "$@"
