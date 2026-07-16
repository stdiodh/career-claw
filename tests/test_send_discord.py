from __future__ import annotations

import json
import os
import unittest
import urllib.error
from unittest import mock

from scripts import send_discord


class DiscordSenderTests(unittest.TestCase):
    def test_chunks_stay_below_discord_limit(self) -> None:
        markdown = "# Backend Daily\n\n## One\n\n" + ("가" * 3000)
        chunks = send_discord.split_markdown_for_discord(markdown)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(
            all(len(chunk) <= send_discord.DISCORD_CONTENT_LIMIT for chunk in chunks)
        )

    def test_payload_disables_mentions(self) -> None:
        payload = json.loads(send_discord.build_payload("@everyone test"))

        self.assertEqual(payload["allowed_mentions"], {"parse": []})
        self.assertEqual(payload["content"], "@everyone test")

    def test_single_chunk_does_not_repeat_title(self) -> None:
        markdown = "# Backend Daily\n\n오늘의 과제"

        self.assertEqual(send_discord.split_markdown_for_discord(markdown), [markdown])

    def test_webhook_requires_discord_https_url_without_leaking_value(self) -> None:
        secret = "http://example.com/api/webhooks/123/private-token"
        with mock.patch.dict(os.environ, {"DISCORD_WEBHOOK_URL": secret}):
            with self.assertRaises(RuntimeError) as context:
                send_discord.get_webhook_url()

        self.assertNotIn("private-token", str(context.exception))

    def test_non_object_retry_body_uses_header_fallback(self) -> None:
        self.assertEqual(send_discord.parse_retry_after("[]", {"Retry-After": "2"}), 2.0)

    def test_zero_retries_makes_one_request(self) -> None:
        error = urllib.error.URLError("offline")
        webhook_url = "https://" + "discord.com" + "/api/webhooks/123/token"
        with mock.patch("urllib.request.urlopen", side_effect=error) as urlopen:
            with self.assertRaises(RuntimeError):
                send_discord.post_discord_chunk(
                    webhook_url,
                    "test",
                    1,
                    1,
                    max_retries=0,
                )

        self.assertEqual(urlopen.call_count, 1)


if __name__ == "__main__":
    unittest.main()
