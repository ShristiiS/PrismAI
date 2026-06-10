"""Shared Supabase client factory for PrismAI retrieval and API layers.

The ingestion pipeline uses :func:`ingestion.storage.get_supabase` directly.
Retrieval and future agent code import from here so query-time modules do not
depend on ingestion package internals.
"""

from ingestion.storage import get_supabase

__all__ = ["get_supabase"]
