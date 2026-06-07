# 데모 에셋

## 목적

이 디렉터리는 demo 문서에서 사용하는 redacted screenshot과 GIF 파일을 보관합니다.

asset은 Career Feed가 GitHub Actions, validation artifacts, generated briefs, Discord Webhook delivery로 운영되는 방식을 보여주기 위한 자료입니다.

웹 대시보드, hosted service, Discord Gateway Bot, Slash Command product, 채용 추천 플랫폼처럼 보이게 만들면 안 됩니다.

현재 asset은 mock redacted screenshot 4장입니다.

실제 GitHub, Discord, webhook, token, account data를 포함하지 않습니다.

## 허용 에셋

허용되는 asset은 redacted GitHub Actions screenshot, redacted Actions summary screenshot, redacted validation report screenshot, redacted generated briefing screenshot, redacted Discord briefing screenshot입니다.

운영 흐름을 정확히 표현한다면 mock data 기반 screenshot도 사용할 수 있습니다.

작고 검토 가능한 short GIF demo도 사용할 수 있습니다.

실제 production screenshot은 민감 정보가 제거된 뒤에만 사용할 수 있습니다.

placeholder image file은 허용하지 않습니다.

링크를 만들기 위해 빈 이미지 파일을 추가하지 않습니다.

## 권장 형식

정적 screenshot은 PNG 또는 WebP를 우선합니다.

Markdown에서 짧은 움직임을 보여줘야 할 때만 GIF를 사용합니다.

mp4 파일은 repository에 직접 커밋하지 않습니다.

긴 영상은 GitHub Release asset, PR attachment, project page, external video link를 사용합니다.

raw screen recording file은 이 디렉터리에 보관하지 않습니다.

## 크기 기준

정적 screenshot은 가능한 한 작게 유지합니다.

PNG 또는 WebP는 가능하면 파일당 1MB 이하를 목표로 합니다.

GIF demo는 짧게 유지합니다.

GIF를 repository에 넣는다면 가능하면 10MB 이하를 목표로 합니다.

GIF가 너무 크면 README에는 정적 screenshot을 사용하고 영상은 외부 링크나 Release asset으로 분리합니다.

commit 전에 screenshot을 필요한 안전 영역으로 crop합니다.

## Redaction 요구사항

Discord webhook URL을 노출하지 않습니다.

OpenAI API key를 노출하지 않습니다.

Naver credential을 노출하지 않습니다.

Discord server name, channel name, username, avatar, user id, private invite detail을 노출하지 않습니다.

개인 DM, private email, account name, private repository URL을 노출하지 않습니다.

브라우저 URL에 token이나 query parameter가 보이면 안 됩니다.

secret-like 문자열이 보이는 Actions log는 캡처하지 않습니다.

solid redaction block 또는 crop을 사용합니다.

텍스트가 복구될 수 있는 blur에만 의존하지 않습니다.

## 파일 이름

파일명은 소문자와 설명형 이름을 사용합니다.

권장 파일명은 다음과 같습니다.

- `github-actions-dispatch-redacted.png`
- `actions-summary-redacted.png`
- `validation-report-redacted.png`
- `discord-brief-redacted.png`
- `career-feed-demo.gif`

파일은 `docs/assets/demo/` 바로 아래에 둡니다.

미래 문서 변경이 필요하기 전까지 nested folder는 만들지 않습니다.

## 리뷰 체크리스트

- 파일이 `docs/assets/demo/`에 존재한다.
- 문서 링크가 실제 존재하는 파일만 가리킨다.
- asset이 redacted 또는 mock data를 사용한다.
- webhook, token, API key, credential, private URL, personal identifier가 보이지 않는다.
- Discord server, channel, user, avatar detail이 가려져 있다.
- 파일 크기가 repository review에 무리가 없다.
- screenshot이 현재 workflow 이름, input, artifact, message shape을 반영한다.
- reviewer가 private context 없이 asset 의미를 이해할 수 있다.

## 에셋 업데이트

workflow 이름, workflow input, artifact 이름, validation report, Discord message format이 바뀌면 asset을 업데이트합니다.

오래된 asset은 여러 버전으로 남기지 말고 삭제하거나 교체합니다.

이미지를 추가하거나 교체한 뒤에는 다음 명령을 실행합니다.

```bash
find docs/assets/demo -maxdepth 1 -type f -print
du -h docs/assets/demo/*
```

PR에는 image 또는 GIF asset 추가 여부를 적습니다.

image 또는 GIF asset을 추가했다면 redaction을 사람이 직접 확인했다는 점을 적습니다.
