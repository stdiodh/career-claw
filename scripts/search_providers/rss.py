"""RSS provider marker.

The current RSS collection implementation remains in collect-kr-feeds.py during
the v0.2 compatibility window. This module exposes the provider name for the
locale-aware provider registry.
"""

from __future__ import annotations

from .base import SearchProvider


class RssSearchProvider(SearchProvider):
    name = "rss"
