# Sample Output

> Language: [한국어](./sample-output.md) | [English](../../en/getting-started/sample-output.md)

Career Feed가 어떤 결과물을 만드는지 빠르게 확인하는 예시 모음입니다.

이 파일들은 설명용 sample입니다. 실제 운영 결과, 사용자 수, 채택 사례를 주장하지 않습니다.

## Available Examples

| Output | File | Notes |
| --- | --- | --- |
| Daily Backend Brief | [daily-backend-brief.example.md](../examples/daily-backend-brief.example.md) | 일일 백엔드 학습, PS 루틴, OSS 준비, 실무 지식 예시 |
| Korea Dev/AI News Daily | [korea-dev-ai-news-daily.example.md](../examples/korea-dev-ai-news-daily.example.md) | 한국 개발/AI 뉴스 후보와 읽을거리 정리 예시 |
| Backend Career Site Radar | [career-site-radar.example.md](../examples/career-site-radar.example.md) | 주간 커리어 사이트 확인 루틴 예시 |

## What to Check

- 공개 URL 또는 명확한 placeholder만 사용합니다.
- Discord webhook URL, API key, token, credential, private channel name을 포함하지 않습니다.
- OSS 후보 예시는 외부 GitHub 저장소에 자동 댓글, PR, assign, label 변경을 하는 것처럼 표현하지 않습니다.
- safe 후보가 없는 날의 fallback output은 정상 예시로 둘 수 있습니다.

## Adding a Sample

새 sample을 추가할 때는 다음 기준을 지킵니다.

1. redacted 또는 placeholder data만 사용합니다.
2. PR에서 검토 가능한 짧은 크기로 유지합니다.
3. generated output인지 hand-written example인지 명확히 적습니다.
4. 파일이 실제로 존재할 때만 이 문서와 README에서 링크합니다.
5. 문서 검증을 실행합니다.

```bash
python3 scripts/check-doc-format.py
git diff --check
```

## Related Documents

- [Fork Setup Guide](fork-setup.md)
- [Usage Guide](usage.md)
- [Demo Guide](../demo.md)
- [Local Validation](../operations/local-validation.md)
