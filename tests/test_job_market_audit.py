from __future__ import annotations

import json
import unittest
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "audits/job-market-2026q3.json"
TAXONOMY_PATH = ROOT / "configs/competency-taxonomy.json"


class JobMarketAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        cls.taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))

    def test_sample_contract_is_satisfied(self) -> None:
        postings = self.audit["postings"]
        method = self.audit["method"]
        companies = Counter(posting["company"] for posting in postings)
        groups = Counter(
            posting.get("industry_group", posting["industry"]) for posting in postings
        )

        self.assertEqual(self.audit["status"], "COMPLETE")
        self.assertEqual(len(postings), method["sample_size"])
        self.assertGreaterEqual(len(companies), method["minimum_companies"])
        self.assertLessEqual(max(companies.values()), method["maximum_per_company"])
        self.assertLessEqual(
            max(groups.values()) * 100 / len(postings),
            method["maximum_industry_share_percent"],
        )
        self.assertEqual(
            len(postings),
            len({(posting["company"], posting["role"]) for posting in postings}),
        )
        self.assertEqual(len(postings), len({posting["source_url"] for posting in postings}))

    def test_every_posting_is_inside_the_frozen_window(self) -> None:
        checked_at = date.fromisoformat(self.audit["checked_at"])
        window_start = date.fromisoformat(self.audit["window_start"])
        valid_until = date.fromisoformat(self.audit["valid_until"])
        self.assertLessEqual((valid_until - checked_at).days, 92)
        self.assertGreaterEqual(valid_until, checked_at)
        for posting in self.audit["postings"]:
            posted_at = date.fromisoformat(posting["date_posted"])
            self.assertGreaterEqual(posted_at, window_start, posting["source_url"])
            self.assertLessEqual(posted_at, checked_at, posting["source_url"])
            self.assertTrue(posting["source_url"].startswith("https://"))
            self.assertTrue(posting["experience"].strip())
            self.assertEqual(posting["scope_rule"], "INTERNSHIP_ENTRY_OR_MAX_3Y")
            self.assertIs(posting["scope_verified"], True)
            self.assertEqual(len(posting["keyword_ids"]), len(set(posting["keyword_ids"])))

    def test_declared_frequencies_are_reproducible(self) -> None:
        frequencies = Counter(
            keyword
            for posting in self.audit["postings"]
            for keyword in posting["keyword_ids"]
        )
        self.assertEqual(dict(frequencies), self.audit["frequency"])

        known = set(self.taxonomy["market_keywords"])
        self.assertFalse(set(frequencies) - known)
        threshold = self.audit["method"]["market_demand_threshold"]
        self.assertEqual(
            set(self.audit["market_supported_ids"]),
            {keyword for keyword, count in frequencies.items() if count >= threshold},
        )


if __name__ == "__main__":
    unittest.main()
