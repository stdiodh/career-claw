"""Shared types for locale-aware search providers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    source: str
    summary: str = ""
    published_at: str = ""


class SearchProvider:
    name = "base"

    def search_news(self, query: str, locale: str) -> list[SearchResult]:
        raise NotImplementedError

    def search_web(self, query: str, locale: str) -> list[SearchResult]:
        raise NotImplementedError
