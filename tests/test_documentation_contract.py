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
            "주간 최대 19회",
            "백엔드 실무`, `PS`, `OSS 기여 준비`, `백엔드 연결 CS 지식",
            "configs/delivery-schedule.json",
            "Spring Security는 학습 lab에는 남아 있지만",
            "실제 원격 동작 기준은 기본 브랜치에 병합된 commit",
            "한국어 README를 단일 기준으로 관리합니다",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, readme)


if __name__ == "__main__":
    unittest.main()
