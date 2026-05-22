#!/usr/bin/env python3
"""Create a sample Markdown report for local validation."""

from __future__ import annotations

from pathlib import Path


REPORT_PATH = Path("reports/sample-daily-news.md")


SAMPLE_REPORT = """Career Feed
Sample Date
AI/Backend Daily Brief

한 줄 총평: 이 파일은 실제 뉴스가 아니라 Discord 전송 형식을 확인하기 위한 테스트 리포트입니다.

## 1. Sample AI Platform Update
- 무슨 일: 테스트용 AI 플랫폼 업데이트 항목입니다.
- 왜 중요: Discord 메시지에서 제목과 목록이 어떻게 보이는지 확인할 수 있습니다.
- 개발자 액션: 실제 운영 전 Webhook 전송 형식을 점검합니다.
- 출처/발행시각: 테스트 데이터
- 신뢰도: 높음

## 2. Sample Backend Release
- 무슨 일: 테스트용 백엔드 릴리스 항목입니다.
- 왜 중요: 여러 항목이 포함된 Markdown chunk 처리를 확인할 수 있습니다.
- 개발자 액션: `scripts/send-discord.py`로 수동 전송 테스트를 실행합니다.
- 출처/발행시각: 테스트 데이터
- 신뢰도: 높음

## 오늘 바로 확인할 것
- Markdown이 Discord에서 읽기 쉽게 표시되는지 확인합니다.
- Webhook username이 Career Feed로 표시되는지 확인합니다.

## 제외한 후보
- 실제 뉴스 후보: 샘플 리포트이므로 포함하지 않았습니다.
"""


def main() -> int:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(SAMPLE_REPORT, encoding="utf-8")
    print(f"Created sample report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
