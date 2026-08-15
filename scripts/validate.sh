#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "==> Checking Python syntax"
bash -n career-feed
python3 -m py_compile \
  scripts/collect_spring_updates.py \
  scripts/collect_oss_candidates.py \
  scripts/check_oss_delivery_gate.py \
  scripts/generate_backend_daily.py \
  scripts/mark_progress.py \
  scripts/record_oss_shadow.py \
  scripts/send_discord.py \
  scripts/sync_delivery_schedule.py \
  scripts/verify_curriculum.py

echo "==> Checking JSON"
python3 -m json.tool audits/job-market-2026q3.json >/dev/null
python3 -m json.tool configs/backend-practice.json >/dev/null
python3 -m json.tool configs/competency-taxonomy.json >/dev/null
python3 -m json.tool configs/curriculum-matrix.json >/dev/null
python3 -m json.tool configs/delivery-schedule.json >/dev/null
python3 -m json.tool configs/oss-repositories.json >/dev/null
python3 -m json.tool configs/oss-delivery-gate.json >/dev/null
python3 -m json.tool configs/ps-problems.json >/dev/null
python3 -m json.tool configs/spring-updates.json >/dev/null
python3 -m json.tool configs/verification-profile.json >/dev/null
python3 -m json.tool data/curriculum-verification.json >/dev/null
python3 -m json.tool data/progress.json >/dev/null
python3 -m json.tool tests/fixtures/oss-api-responses.json >/dev/null
python3 -m json.tool tests/fixtures/spring-updates.json >/dev/null

echo "==> Running tests"
python3 -X dev -W error -m unittest discover -s tests -p 'test_*.py' -v

echo "==> Checking VERIFIED curriculum contracts"
python3 scripts/verify_curriculum.py >/dev/null
python3 scripts/sync_delivery_schedule.py --check >/dev/null
python3 scripts/check_oss_delivery_gate.py >/dev/null

echo "==> Checking deterministic generation and fixture collection"
temporary="$(mktemp -d)"
trap 'rm -rf "${temporary}"' EXIT
python3 scripts/collect_spring_updates.py \
  --fixture tests/fixtures/spring-updates.json \
  --output "${temporary}/spring-updates.json"
test -s "${temporary}/spring-updates.json"
python3 - "${temporary}/spring-updates.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    update = json.load(handle)
assert set(update) == {"title", "date", "link", "source"}
assert update["source"] in {"Spring Boot", "Spring AI"}
assert update["link"].startswith("https://github.com/spring-projects/")
PY

python3 scripts/generate_backend_daily.py \
  --date 2026-08-15 \
  --spring-updates "${temporary}/spring-updates.json" \
  --output "${temporary}/backend-daily.md"
test -s "${temporary}/backend-daily.md"
grep -q '^# Career Feed - Backend Daily$' "${temporary}/backend-daily.md"
grep -q '^## 오늘의 PS$' "${temporary}/backend-daily.md"
grep -q '^## 공식 Spring 새소식$' "${temporary}/backend-daily.md"
test "$(grep -c '^## ' "${temporary}/backend-daily.md")" = "2"

python3 scripts/collect_oss_candidates.py \
  --fixture tests/fixtures/oss-api-responses.json \
  --now 2026-07-16T00:00:00Z \
  --json-output "${temporary}/oss-candidates.json" \
  --markdown-output "${temporary}/oss-candidates.md"
python3 - "${temporary}/oss-candidates.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    artifact = json.load(handle)
assert artifact["complete"] is True
assert artifact["request_count"] == 25
assert artifact["request_limit"] == 34
assert len(artifact["candidates"]) == 5
assert len(artifact["ready_to_ask"]) == 2
assert len({item["repository"] for item in artifact["ready_to_ask"]}) == 2
PY
grep -q '^# Career Feed - OSS Weekly$' "${temporary}/oss-candidates.md"

echo "==> Running Kotlin/Java/Spring lab"
./lab/gradlew -p lab test --rerun-tasks --no-daemon
if [ "${RUN_POSTGRES_TESTS:-0}" = "1" ]; then
  ./lab/gradlew -p lab postgresTest --rerun-tasks --no-daemon
fi

echo "==> Checking active workflows"
test -f .github/workflows/backend-daily.yml
test -f .github/workflows/mark-progress.yml
test -f .github/workflows/oss-weekly.yml
test -f .github/workflows/pr-checks.yml
test "$(find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | wc -l | tr -d ' ')" = "4"
if rg -n 'openai/codex-action|OPENAI_API_KEY|5,35 \* \* \* \*' \
  .github \
  README.md \
  scripts/collect_spring_updates.py \
  scripts/collect_oss_candidates.py \
  scripts/generate_backend_daily.py \
  scripts/mark_progress.py \
  scripts/send_discord.py; then
  echo "Removed LLM or high-frequency schedule reference remains." >&2
  exit 1
fi
if rg -n 'OSS_GITHUB_APP_TOKEN|create-github-app-token|secrets\.GITHUB_TOKEN|github\.token' \
  scripts/collect_spring_updates.py \
  scripts/collect_oss_candidates.py \
  .github/workflows/oss-weekly.yml; then
  echo "Unsupported OSS credential path remains." >&2
  exit 1
fi

echo "==> Checking diff whitespace"
git diff --check

echo "==> Validation complete"
