"""Brave provider marker for en-US source collection."""

from __future__ import annotations

from .base import SearchProvider


class BraveSearchProvider(SearchProvider):
    name = "brave"
