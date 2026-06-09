# Security Policy

> Language: [한국어](./SECURITY.md) | [English](../en/SECURITY.md)

## Supported versions

`v0.2.x` is the current release line.

Security guidance applies to the current default branch and the latest v0.2.x release while the project is in early public development.

## Supported scope

Career Feed의 현재 운영 범위는 GitHub Actions, OpenAI API, Discord Webhook 기반 자동 브리핑 workflow입니다.

보안 정책은 이 범위 안의 문서, workflow 설정, script, secret 사용 방식, Discord 전송 정책을 중심으로 다룹니다.

Daily Backend Brief, Dev News Daily, Backend Career Site Radar, PS 진행 표시 workflow가 주요 대상입니다.

## Not in scope

현재 다음 항목은 운영 범위 밖입니다.

- 상시 실행 서버
- 데이터베이스
- 웹 대시보드
- Discord Gateway Bot
- Slash Command
- 사용자 계정 시스템
- 채용 매칭 서비스

이 범위 밖 시스템에 대한 취약점 보고는 현재 보안 범위에 해당하지 않을 수 있습니다.

## Sensitive information

다음 값은 공개 issue, PR, commit, log, 문서 예시에 포함하지 마세요.

- OpenAI API key
- Discord Webhook URL
- GitHub token
- Naver API credentials
- Brave Search API key
- OpenAI organization ID
- 개인 이메일
- 기타 credentials

Secret은 GitHub Secrets 또는 로컬 환경변수로만 다룹니다.

실제 값을 README, docs, issue template, test fixture에 넣지 마세요.

## Reporting a vulnerability or secret exposure

민감 정보가 노출되었거나 취약점을 발견했다면 공개 issue에 secret 값을 붙여 넣지 마세요.

GitHub private vulnerability reporting이 활성화되어 있다면 그 기능을 사용해 주세요.

private reporting이 보이지 않으면 repository profile 또는 maintainer가 공개한 기존 연락 경로를 사용해 먼저 알려 주세요.

제보에는 다음 정보를 포함하면 도움이 됩니다.

- 영향을 받는 파일이나 workflow
- 노출 또는 취약점의 유형
- 재현 가능한 최소 설명
- secret 값 자체를 제외한 관련 정황

노출된 credential은 즉시 폐기하고 새 값으로 교체해야 합니다.

## Secret handling

`.env` 파일에 실제 값을 넣어 commit하지 마세요.

API key를 screenshot에 포함하지 마세요.

Discord Webhook URL을 issue, PR, docs, log, release note에 붙여 넣지 마세요.

민감값은 GitHub Actions Secrets에 넣습니다.

GitHub Actions Variables는 timezone, target time, feature flag처럼 비민감 설정에만 사용합니다.

## Discord webhook safety

Discord Webhook URL은 secret입니다.

노출되었다면 Discord에서 webhook을 폐기하고 새 URL을 발급하세요.

첫 설정에서는 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false`와 `dry_run=true`로 전송을 막고 artifact부터 확인하세요.

v0.2.x 동안 `ko-KR` daily workflow는 legacy webhook fallback 이름을 지원합니다. 이 값도 GitHub Secrets에만 저장하고, breaking release 계획 없이 fallback behavior를 제거하지 않습니다.

## GitHub Actions logs

raw secret 값을 출력하지 마세요.

민감값은 GitHub Actions Secrets masking에 맡기고, 스크립트에서 직접 echo하지 않습니다.

로그나 screenshot을 공유하기 전에 webhook URL, token, private repository URL, Discord channel detail이 없는지 확인하세요.

## Automation boundaries

자동화 범위는 좁게 유지합니다.

OpenAI API는 maintainer가 검토 가능한 브리핑 초안, 검증 리포트, 학습 주제 우선순위화, OSS 후보 정리에 사용합니다.

외부 저장소에 자동 댓글을 작성하거나, 자동 PR을 만들거나, issue를 자동 assign하거나, label을 자동 변경하지 않습니다.

무검토 배포를 목표로 하지 않습니다.

## Maintainer response

보고된 문제는 영향 범위를 확인한 뒤 대응합니다.

Secret 노출이 의심되면 우선 credential 폐기와 교체를 진행합니다.

문서나 workflow 정책이 문제라면 작은 수정으로 복구합니다.

필요하면 README, CONTRIBUTING, issue template, workflow 설명을 업데이트합니다.

## Safe handling checklist

- Secret 값을 공개 issue에 붙여 넣지 않습니다.
- API key, token, webhook URL을 commit하지 않습니다.
- Discord Webhook URL을 스크린샷이나 로그에 노출하지 않습니다.
- 노출된 Discord Webhook은 Discord에서 폐기하고 새 URL로 교체합니다.
- GitHub Actions log에 민감 정보가 출력되지 않도록 합니다.
- 외부 저장소 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 추가하지 않습니다.
- OpenAI API output은 maintainer가 검토 가능한 초안으로만 사용합니다.
- 검증 명령을 실행할 때 로컬 환경변수 출력에 주의합니다.
