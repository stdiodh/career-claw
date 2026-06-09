"""Naver provider marker for ko-KR source collection."""

from __future__ import annotations

from .base import SearchProvider


class NaverSearchProvider(SearchProvider):
    name = "naver"
