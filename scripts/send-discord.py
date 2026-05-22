#!/usr/bin/env python3
"""Send a Markdown report to Discord via webhook."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


MAX_CHUNK_LENGTH = 1800
MAX_RATE_LIMIT_RETRIES = 5
REQUEST_TIMEOUT_SECONDS = 30
WEBHOOK_USERNAME = "Career Feed"
USER_AGENT = "career-feed-discord-sender"
CHUNK_HEADER_PREFIX = "Career Feed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a Markdown file to a Discord webhook."
    )
    parser.add_argument("markdown_file", help="Path to the Markdown report file.")
    return parser.parse_args()


def get_webhook_url() -> str:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL environment variable is required.")

    return webhook_url


def read_markdown(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Markdown file does not exist: {path}")
    if not path.is_file():
        raise RuntimeError(f"Markdown path is not a file: {path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise RuntimeError(f"Markdown report is empty: {path}")

    return content


def is_section_heading(line: str) -> bool:
    return bool(re.match(r"^##\s+\S", line))


def is_fence_marker(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def split_by_section_headings(content: str) -> list[str]:
    sections: list[str] = []
    current: list[str] = []
    in_code_fence = False

    for line in content.splitlines():
        if is_fence_marker(line):
            in_code_fence = not in_code_fence

        if is_section_heading(line) and current and not in_code_fence:
            sections.append("\n".join(current).strip())
            current = [line]
            continue

        current.append(line)

    if current:
        sections.append("\n".join(current).strip())

    return [section for section in sections if section]


def hard_wrap_text(text: str, limit: int) -> list[str]:
    return [text[index : index + limit] for index in range(0, len(text), limit)]


def merge_segments(segments: list[str], limit: int, separator: str) -> list[str]:
    chunks: list[str] = []
    current = ""

    for segment in segments:
        if not segment:
            continue
        if len(segment) > limit:
            raise ValueError("Segment is longer than the chunk limit.")

        candidate = segment if not current else f"{current}{separator}{segment}"
        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            chunks.append(current)
        current = segment

    if current:
        chunks.append(current)

    return chunks


def split_by_lines(text: str, limit: int) -> list[str]:
    line_segments: list[str] = []

    for line in text.splitlines():
        if len(line) <= limit:
            line_segments.append(line)
            continue

        line_segments.extend(hard_wrap_text(line, limit))

    return merge_segments(line_segments, limit, "\n")


def chunk_markdown(content: str, limit: int = MAX_CHUNK_LENGTH) -> list[str]:
    if limit <= 0:
        raise ValueError("Chunk limit must be greater than zero.")

    sections = split_by_section_headings(content)
    section_segments: list[str] = []

    for section in sections:
        if len(section) <= limit:
            section_segments.append(section)
            continue

        section_segments.extend(split_by_lines(section, limit))

    chunks = merge_segments(section_segments, limit, "\n\n")
    if any(len(chunk) > limit for chunk in chunks):
        raise RuntimeError("Failed to split Markdown into safe Discord chunks.")

    return chunks


def format_chunk_header(chunk_index: int, total_chunks: int) -> str:
    if total_chunks == 1:
        return CHUNK_HEADER_PREFIX

    return f"{CHUNK_HEADER_PREFIX} ({chunk_index}/{total_chunks})"


def add_chunk_headers(chunks: list[str]) -> list[str]:
    total_chunks = len(chunks)
    formatted_chunks: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        header = format_chunk_header(index, total_chunks)
        available_length = MAX_CHUNK_LENGTH - len(header) - 2
        if available_length <= 0:
            raise RuntimeError("Chunk header leaves no room for Discord content.")

        if len(chunk) <= available_length:
            formatted_chunks.append(f"{header}\n\n{chunk}")
            continue

        for split_chunk in chunk_markdown(chunk, available_length):
            formatted_chunks.append(split_chunk)

    if len(formatted_chunks) != total_chunks:
        return add_chunk_headers(formatted_chunks)

    return formatted_chunks


def build_payload(content: str) -> bytes:
    payload = {
        "content": content,
        "username": WEBHOOK_USERNAME,
        "allowed_mentions": {"parse": []},
    }
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def parse_retry_after(body: str, headers: Any) -> float:
    try:
        parsed = json.loads(body) if body else {}
        retry_after = parsed.get("retry_after")
        if isinstance(retry_after, (int, float)):
            return max(float(retry_after), 0.0)
        if isinstance(retry_after, str):
            return max(float(retry_after), 0.0)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    retry_after_header = headers.get("Retry-After") if headers else None
    if retry_after_header:
        try:
            return max(float(retry_after_header), 0.0)
        except ValueError:
            pass

    return 1.0


def summarize_response_body(body: str) -> str:
    cleaned = " ".join(body.split())
    if not cleaned:
        return "No response body."

    return cleaned[:500]


def post_discord_chunk(
    webhook_url: str, content: str, chunk_index: int, total_chunks: int
) -> None:
    payload = build_payload(content)
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    attempts = 0
    while True:
        try:
            with urllib.request.urlopen(
                request, timeout=REQUEST_TIMEOUT_SECONDS
            ) as response:
                if 200 <= response.status < 300:
                    return

                body = response.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    "Discord webhook returned non-success status "
                    f"{response.status} for chunk {chunk_index}/{total_chunks}: "
                    f"{summarize_response_body(body)}"
                )
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 429 and attempts < MAX_RATE_LIMIT_RETRIES:
                attempts += 1
                retry_after = parse_retry_after(body, exc.headers)
                print(
                    "Discord rate limit received. "
                    f"Retrying chunk {chunk_index}/{total_chunks} "
                    f"after {retry_after:.2f} seconds "
                    f"(attempt {attempts}/{MAX_RATE_LIMIT_RETRIES}).",
                    file=sys.stderr,
                )
                time.sleep(retry_after)
                continue

            raise RuntimeError(
                f"Discord webhook returned HTTP {exc.code} for chunk "
                f"{chunk_index}/{total_chunks}: {summarize_response_body(body)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Network error while sending chunk {chunk_index}/{total_chunks}: "
                f"{exc.reason}"
            ) from exc


def send_to_discord(webhook_url: str, chunks: list[str]) -> int:
    message_chunks = add_chunk_headers(chunks)
    total_chunks = len(message_chunks)
    if total_chunks == 0:
        raise RuntimeError("No Discord message chunks were generated.")

    for index, chunk in enumerate(message_chunks, start=1):
        post_discord_chunk(webhook_url, chunk, index, total_chunks)

    return total_chunks


def main() -> int:
    args = parse_args()

    try:
        content = read_markdown(Path(args.markdown_file))
        webhook_url = get_webhook_url()
        chunks = chunk_markdown(content)
        sent_count = send_to_discord(webhook_url, chunks)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"Failed to send Discord message: {exc}", file=sys.stderr)
        return 1

    print(f"Successfully sent {sent_count} Discord chunk(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
