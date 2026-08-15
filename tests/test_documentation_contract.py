from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_DOCUMENTS = (
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "SECURITY.md",
    ROOT / "VALIDATION_PLAN.md",
    ROOT / "audits/verification-evidence-2026-07-16.md",
    ROOT / "lab/README.md",
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^]]*]\(([^)]+)\)")


class DocumentationContractTests(unittest.TestCase):
    def test_product_documents_exist_without_legacy_translation_trees(self) -> None:
        for path in PRODUCT_DOCUMENTS:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())
        self.assertFalse((ROOT / "docs/en").exists())
        self.assertFalse((ROOT / "docs/kr").exists())

    def test_local_markdown_links_resolve(self) -> None:
        for document in PRODUCT_DOCUMENTS:
            content = document.read_text(encoding="utf-8")
            for raw_target in MARKDOWN_LINK_RE.findall(content):
                target = raw_target.strip().strip("<>")
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_text = unquote(target.split("#", 1)[0].split("?", 1)[0])
                resolved = (document.parent / path_text).resolve()
                with self.subTest(document=document.relative_to(ROOT), target=target):
                    self.assertTrue(resolved.exists())

    def test_readme_states_the_current_oss_and_document_contract(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in (
            "`오늘의 PS`와 `공식 Spring 새소식` 두 영역",
            "실행당 최대 34회",
            "최대 8개",
            "최종 OSS 후보 최대 2개",
            "./career-feed oss",
            "configs/delivery-schedule.json",
            "Spring Security는 학습 lab에는 남아 있지만",
            "실제 원격 동작 기준은 기본 브랜치에 병합된 commit",
            "한국어 README를 단일 기준으로 관리합니다",
            "일반 AI 동향, 블로그, 뉴스 사이트, 소셜 미디어, 투자 뉴스 수집은 범위 밖",
            "`published_at` 기준 최근 14일",
            "draft와 prerelease는 제외",
            "100개씩 최대 10페이지를 끝까지 확인",
            "더 오래된 항목으로 대체하지 않고 전체를 fail closed",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, readme)


if __name__ == "__main__":
    unittest.main()
