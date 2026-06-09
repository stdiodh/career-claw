"""GitHub provider marker for OSS candidate discovery."""

from __future__ import annotations

from .base import SearchProvider


class GitHubSearchProvider(SearchProvider):
    name = "github"
