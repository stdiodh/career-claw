#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "==> Checking Python syntax"
python3 -m py_compile \
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
python3 -m json.tool configs/verification-profile.json >/dev/null
python3 -m json.tool data/curriculum-verification.json >/dev/null
python3 -m json.tool data/progress.json >/dev/null

echo "==> Running tests"
python3 -X dev -W error -m unittest discover -s tests -p 'test_*.py' -v

echo "==> Checking VERIFIED curriculum contracts"
python3 scripts/verify_curriculum.py >/dev/null
python3 scripts/sync_delivery_schedule.py --check >/dev/null
python3 scripts/check_oss_delivery_gate.py >/dev/null

echo "==> Checking deterministic generation and fixture collection"
temporary="$(mktemp -d)"
trap 'rm -rf "${temporary}"' EXIT
python3 scripts/generate_backend_daily.py \
  --date 2026-07-16 \
  --output "${temporary}/backend-daily.md"
test -s "${temporary}/backend-daily.md"
grep -q '^# Career Feed - Backend Daily$' "${temporary}/backend-daily.md"
grep -q '^## 오늘의 백엔드 실무$' "${temporary}/backend-daily.md"
grep -q '^## 오늘의 PS$' "${temporary}/backend-daily.md"
grep -q '^## 오늘의 OSS 기여 준비$' "${temporary}/backend-daily.md"
grep -q '^## 오늘의 백엔드 연결 CS 지식$' "${temporary}/backend-daily.md"
grep -q '검증 profile: `jvm-spring-2026q3-v1`' "${temporary}/backend-daily.md"

python3 scripts/collect_oss_candidates.py \
  --fixture tests/fixtures/oss-api-responses.json \
  --now 2026-07-16T00:00:00Z \
  --json-output "${temporary}/oss-candidates.json" \
  --markdown-output "${temporary}/oss-candidates.md"
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["request_count"])' "${temporary}/oss-candidates.json")" = "19"
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
  scripts/collect_oss_candidates.py \
  scripts/generate_backend_daily.py \
  scripts/mark_progress.py \
  scripts/send_discord.py; then
  echo "Removed LLM or high-frequency schedule reference remains." >&2
  exit 1
fi
if rg -n 'OSS_GITHUB_APP_TOKEN|create-github-app-token|secrets\.GITHUB_TOKEN|github\.token' \
  scripts/collect_oss_candidates.py \
  .github/workflows/oss-weekly.yml; then
  echo "Unsupported OSS credential path remains." >&2
  exit 1
fi

echo "==> Checking diff whitespace"
git diff --check

echo "==> Validation complete"
