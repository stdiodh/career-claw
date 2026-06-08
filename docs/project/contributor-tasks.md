# Contributor Task Ideas

This document lists contribution ideas before they become GitHub issues.

It is meant to help first-time contributors choose a small, reviewable task.

Do not start large workflow or policy changes without opening an issue first.

## Good first issues

### docs: improve fork setup wording

Scope:

- Clarify one confusing setup step in `docs/getting-started/fork-setup.md`.
- Keep the fork to dry-run to artifact review to Discord delivery flow intact.
- Do not change workflow logic.

Verify:

- README link still works.
- `docs/getting-started/fork-setup.md` remains readable.
- `git diff --check` passes.

### docs: clarify runtime variable examples

Scope:

- Improve one example in `docs/getting-started/runtime-configuration.md`.
- Keep existing defaults unchanged.
- Do not edit workflow YAML.

Verify:

- Invalid examples still show `9:00`, `24:00`, `09:60`, and `morning`.
- Timezone examples remain IANA timezone names.

### test: add stale OSS candidate fixture

Scope:

- Add one fixture for an issue older than the recent window.
- Ensure it is not `safe_to_recommend`.
- Keep `created_at` as the freshness source.

Verify:

- Related candidate or validator tests pass.
- `updated_at` does not make a stale issue safe.

### docs: improve sample output notes

Scope:

- Improve `docs/getting-started/sample-output.md`.
- Use existing example files or placeholder links only.
- Do not add real Discord screenshots or webhook URLs.

Verify:

- No real webhook or secret appears.
- Relative links resolve.

### docs: improve demo asset README

Scope:

- Clarify screenshot redaction rules.
- Keep demo assets limited to GitHub Actions, validation artifacts, generated briefs, and Discord output.
- Do not add placeholder image files.

Verify:

- No missing image link is introduced.
- `python3 scripts/check-doc-format.py` passes.

## Help wanted

### docs: add Java/Kotlin source curation guide

Scope:

- Explain what makes a good source for Java/Kotlin backend developers.
- Include public availability, update cadence, and reliability caveats.
- Avoid unverified claims.

Verify:

- Source suggestion issue template still asks for usefulness and cautions.
- No paywalled or private source is presented as generally available.

### feat: improve validation report readability

Scope:

- Make validation errors easier to understand.
- Preserve existing validation rules.
- Do not downgrade unsafe OSS URL failures to warnings.

Verify:

- stale URL still fails.
- hallucinated issue URL still fails.
- safe fallback still passes.

### test: add contributor-friendly validator fixtures

Scope:

- Add small fixtures that show one validation failure per file.
- Keep fixture names explicit.
- Avoid real secrets and private URLs.

Verify:

- `./scripts/validate.sh` passes.
- Failure fixtures fail for the intended reason.

## Not accepted contributions

- fake usage metrics
- fake stars, forks, downloads, active users, or adoption stories
- auto-claiming external GitHub issues
- auto-commenting on external repositories
- auto-assigning or auto-labeling external issues
- storing secrets in docs or fixtures
- adding scraped private data
- bypassing validation to force Discord delivery
- presenting planned roadmap items as current features

## Before opening a PR

- Read [CONTRIBUTING.md](../../CONTRIBUTING.md).
- Check [Fork Setup Guide](../getting-started/fork-setup.md) if the change affects user setup.
- Check [OSS Candidate Policy](../policies/oss-candidate-policy.md) if the change affects OSS candidates.
- Run the smallest relevant validation command.
- Explain what changed and why in the pull request body.
