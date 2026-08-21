#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "==> Checking syntax"
bash -n career-feed
python3 -m py_compile scripts/collect_oss_candidates.py

echo "==> Checking JSON"
python3 -m json.tool configs/oss-repositories.json >/dev/null
python3 -m json.tool tests/fixtures/oss-api-responses.json >/dev/null

echo "==> Running tests"
python3 -X dev -W error -m unittest discover -s tests -p 'test_*.py' -v

echo "==> Checking deterministic fixture collection"
temporary="$(mktemp -d)"
trap 'rm -rf "${temporary}"' EXIT
python3 scripts/collect_oss_candidates.py \
  --fixture tests/fixtures/oss-api-responses.json \
  --now 2026-08-20T09:00:00Z \
  --json-output "${temporary}/oss-candidates.json" \
  --markdown-output "${temporary}/oss-candidates.md"
python3 - "${temporary}/oss-candidates.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    artifact = json.load(handle)
assert artifact["complete"] is True
assert artifact["request_count"] <= artifact["request_limit"]
assert len(artifact["shortlist"]) <= 5
assert len(artifact["recommendations"]) <= 3
assert all(0 <= item["score"] <= 100 for item in artifact["recommendations"])
PY
grep -q '^# Daily OSS Contribution$' "${temporary}/oss-candidates.md"

echo "==> Checking active workflows"
test -f .github/workflows/oss-weekly.yml
test -f .github/workflows/pr-checks.yml
test "$(find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | wc -l | tr -d ' ')" = "2"
if rg -n \
  'DISCORD_WEBHOOK|contents: write|GITHUB_TOKEN|github\.token|schedule:|collect_spring_updates|generate_backend_daily|mark_progress|lab/gradlew' \
  .github career-feed scripts/collect_oss_candidates.py; then
  echo "Removed product or write-capable integration remains." >&2
  exit 1
fi

echo "==> Checking diff whitespace"
git diff --check

echo "==> Validation complete"
