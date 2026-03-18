#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
INFRA_DIR="${REPO_ROOT}/infra"
OPENCLAW_DIR="${INFRA_DIR}/openclaw"
COMPOSE_FILE="${INFRA_DIR}/compose.yaml"
ENV_FILE="${REPO_ROOT}/.env"

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "compose file not found: ${COMPOSE_FILE}" >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "env file not found: ${ENV_FILE}" >&2
  echo "copy .env.example to .env and populate real values before deploying" >&2
  exit 1
fi

mkdir -p "${OPENCLAW_DIR}/workspace"

cd "${INFRA_DIR}"

docker compose --env-file ../.env -f compose.yaml pull
docker compose --env-file ../.env -f compose.yaml up -d --remove-orphans
