#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/setup-fork.sh [--minimal] [--with-discord] [--enable-schedule] [--repo OWNER/REPO]

Options:
  --minimal          Set the OPENAI_API_KEY repository Secret using an interactive gh prompt.
  --with-discord    Set DISCORD_WEBHOOK_CAREER_FEED and enable Discord delivery.
  --enable-schedule Set CAREER_FEED_SCHEDULE_ENABLED=true for recurring scheduled generation.
  --repo OWNER/REPO Target repository. If omitted, gh tries to infer it from the current directory.
  -h, --help        Show this help.

Examples:
  scripts/setup-fork.sh --minimal
  scripts/setup-fork.sh --minimal --repo your-name/career-feed
  scripts/setup-fork.sh --minimal --with-discord --repo your-name/career-feed
USAGE
}

die() {
  echo "setup-fork: $*" >&2
  exit 1
}

info() {
  echo "setup-fork: $*"
}

require_gh() {
  if ! command -v gh >/dev/null 2>&1; then
    die "GitHub CLI is not installed. Install gh, then run: gh auth login"
  fi

  if ! gh auth status >/dev/null 2>&1; then
    die "GitHub CLI is not authenticated. Run: gh auth login"
  fi
}

validate_repo_name() {
  local value="$1"
  if [[ ! "${value}" =~ ^[^[:space:]/]+/[^[:space:]/]+$ ]]; then
    die "Repository must use OWNER/REPO format: ${value}"
  fi
}

resolve_repo() {
  local requested_repo="$1"
  local inferred_repo=""

  if [[ -n "${requested_repo}" ]]; then
    validate_repo_name "${requested_repo}"
    echo "${requested_repo}"
    return
  fi

  if inferred_repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null)" && [[ -n "${inferred_repo}" ]]; then
    validate_repo_name "${inferred_repo}"
    echo "${inferred_repo}"
    return
  fi

  die "Missing repository. Run from a cloned GitHub repository or pass --repo OWNER/REPO."
}

confirm_continue() {
  local prompt="$1"
  local reply=""
  read -r -p "${prompt} Press Enter to continue or Ctrl-C to abort. " reply
}

set_secret_interactively() {
  local repo="$1"
  local secret_name="$2"

  info "Setting ${secret_name} for ${repo}."
  info "Enter the value in the gh prompt. It will not be echoed by this script."
  gh secret set "${secret_name}" --repo "${repo}"
}

set_variable() {
  local repo="$1"
  local variable_name="$2"
  local variable_value="$3"

  info "Setting ${variable_name}=${variable_value} for ${repo}."
  gh variable set "${variable_name}" --repo "${repo}" --body "${variable_value}"
}

minimal=false
with_discord=false
enable_schedule=false
repo=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --minimal)
      minimal=true
      ;;
    --with-discord)
      with_discord=true
      ;;
    --enable-schedule)
      enable_schedule=true
      ;;
    --repo)
      shift
      if [[ $# -eq 0 || "$1" == --* ]]; then
        die "--repo requires OWNER/REPO."
      fi
      repo="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
  shift
done

if [[ "${minimal}" != true && "${with_discord}" != true && "${enable_schedule}" != true ]]; then
  usage >&2
  die "Choose at least one action: --minimal, --with-discord, or --enable-schedule."
fi

require_gh
repo="$(resolve_repo "${repo}")"

if ! gh repo view "${repo}" --json nameWithOwner --jq .nameWithOwner >/dev/null 2>&1; then
  die "Cannot access repository ${repo}. Check the OWNER/REPO value and gh permissions."
fi

info "Target repository: ${repo}"

if [[ "${minimal}" == true ]]; then
  set_secret_interactively "${repo}" "OPENAI_API_KEY"
  info "Minimal setup complete. No optional Variables were created."
fi

if [[ "${with_discord}" == true ]]; then
  cat <<'WARNING'
setup-fork: Warning: Discord delivery is still blocked while dry_run=true.
setup-fork: Setting CAREER_FEED_DISCORD_DELIVERY_ENABLED=true only allows live delivery after a workflow is run with dry_run=false and validation passes.
WARNING
  confirm_continue "Configure generic Discord delivery now?"
  set_secret_interactively "${repo}" "DISCORD_WEBHOOK_CAREER_FEED"
  set_variable "${repo}" "CAREER_FEED_DISCORD_DELIVERY_ENABLED" "true"
fi

if [[ "${enable_schedule}" == true ]]; then
  cat <<'WARNING'
setup-fork: Warning: scheduled generation may consume OpenAI API credits when the configured time window matches.
setup-fork: Manual workflow_dispatch runs work without enabling scheduled generation.
WARNING
  set_variable "${repo}" "CAREER_FEED_SCHEDULE_ENABLED" "true"
fi

info "Done."
