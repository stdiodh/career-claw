from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_DOCUMENTS = (
    ROOT / "README.md",
    ROOT / "OSS_RECOMMENDATION_GUIDE.md",
    ROOT / "VALIDATION_PLAN.md",
    ROOT / "SECURITY.md",
    ROOT / "AGENTS.md",
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^]]*]\(([^)]+)\)")


class DocumentationContractTests(unittest.TestCase):
    def test_product_documents_exist_and_local_links_resolve(self) -> None:
        for document in PRODUCT_DOCUMENTS:
            with self.subTest(document=document.name):
                self.assertTrue(document.is_file())
            content = document.read_text(encoding="utf-8")
            for raw_target in MARKDOWN_LINK_RE.findall(content):
                target = raw_target.strip().strip("<>")
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_text = unquote(target.split("#", 1)[0].split("?", 1)[0])
                resolved = (document.parent / path_text).resolve()
                with self.subTest(document=document.name, target=target):
                    self.assertTrue(resolved.exists())

    def test_readme_describes_the_implemented_product_only(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in (
            "Spring 생태계 오픈소스 이슈를 추천",
            "spring-projects/spring-security",
            "spring-projects/spring-restdocs",
            "spring-projects/spring-boot",
            "최대 5개",
            "최대 3개",
            "공개 GitHub REST API를 읽기만",
            "예약 실행, Discord 전송과 품질 ledger는 현재 범위에 없습니다",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, readme)
        for removed_product in (
            "Programmers",
            "Spring AI",
            "오늘의 PS",
            "Mark Progress",
            "backend-daily",
        ):
            with self.subTest(removed_product=removed_product):
                self.assertNotIn(removed_product, readme)

    def test_guide_matches_the_scoring_and_read_only_contract(self) -> None:
        guide = (ROOT / "OSS_RECOMMENDATION_GUIDE.md").read_text(encoding="utf-8")
        for marker in (
            "Skill Fit | 30",
            "Contribution Signal | 20",
            "Scope Clarity | 15",
            "Validation | 15",
            "Maintainer Activity | 10",
            "Learning Value | 10",
            "최대 5개만 상세 검증",
            "최대 3개만 추천",
            "외부 comment, assign, branch, fork와 PR 생성은 자동화하지 않는다",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, guide)

    def test_removed_product_paths_are_absent(self) -> None:
        for relative_path in (
            "lab/settings.gradle.kts",
            "data/progress.json",
            "audits/job-market-2026q3.json",
            ".github/workflows/backend-daily.yml",
            ".github/workflows/mark-progress.yml",
            "scripts/generate_backend_daily.py",
            "scripts/mark_progress.py",
            "scripts/send_discord.py",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertFalse((ROOT / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
