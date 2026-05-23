"""Supabase persistence layer for the PrismAI ingestion pipeline.

This module is the **only** place that reads from or writes to Supabase for
ingestion. Nothing else in the project touches the database directly — parsers,
chunkers, and embedders stay pure; pipeline.py orchestrates and calls these
functions with a client from :func:`get_supabase`.

Why this isolation exists:
    When a PM uploads a sprint retro or an Excel backlog changes row-by-row,
    we need predictable dedup, re-ingest, and partial updates. Centralising all
    SQL/PostgREST calls here prevents scattered queries that drift out of sync,
    leak credentials, or embed half-updated chunks alongside stale vectors.
"""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

if TYPE_CHECKING:
    # Chunk lives in chunkers; importing that graph here would pull parsers/PyMuPDF.
    # Runtime only needs duck-typed objects with chunk_index, content, metadata.
    from ingestion.chunkers import Chunk


# WHY THIS EXISTS IN PRISM AI:
# pipeline.py imports storage before the worker hits Supabase. Loading
# backend/.env here ensures SUPABASE_URL / SUPABASE_KEY / OPENAI_* are
# visible without exporting them manually in every shell session.
#
# WHAT THIS BLOCK DOES:
# Loads environment variables from .env when the module is imported.
#
# WHY THIS WAY:
# ``load_dotenv()`` is idempotent for already-set vars — safe in prod
# where secrets come from the platform env.
#
# WHAT BREAKS IF THIS IS WRONG:
# First Supabase call would 401 because keys never loaded from disk.
load_dotenv()


# WHY THIS EXISTS IN PRISM AI:
# Batch ingestion logs document IDs, chunk deletes, and upserts — the
# operator needs structured logs that respect LOG_LEVEL instead of raw
# prints scattered through pipeline.py.
#
# WHAT THIS BLOCK DOES:
# Creates the storage module logger.
#
# WHY THIS WAY:
# ``logging.getLogger(__name__)`` ties log lines to ``ingestion.storage``
# for filtering in Datadog or CloudWatch later.
#
# WHAT BREAKS IF THIS IS WRONG:
# Using ``print`` only → production log aggregation misses DB failures.
logger = logging.getLogger(__name__)


# WHY THIS EXISTS IN PRISM AI:
# Creating a new HTTPS client per request burns TCP handshakes and can
# exhaust connection pools during a 5,000-chunk ingest. One shared client
# matches Supabase's intended usage pattern.
#
# WHAT THIS BLOCK DOES:
# Holds the lazily-created singleton client instance.
#
# WHY THIS WAY:
# ``None`` means "not yet built"; :func:`get_supabase` fills this once.
#
# WHAT BREAKS IF THIS IS WRONG:
# Recreating ``create_client`` on every pipeline step → slower ingest and
# occasional rate-limit spikes from connection churn.
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Return a shared Supabase client, creating it on first use.

    One-sentence summary: reads ``SUPABASE_URL`` and ``SUPABASE_KEY`` from the
    environment and returns a singleton ``Client``.

    Why it exists for PrismAI:
        Every ingestion step — dedup lookup, document insert, chunk delete,
        embedding insert — needs the same authenticated client. A factory keeps
        credential reads and ``create_client`` in one place so pipeline.py never
        duplicates connection logic.

    Decisions made inside:
        1. **Singleton via module-level ``_supabase_client``** — avoids paying
           connection setup cost hundreds of times per batch job.
        2. **Validate env vars at call time, not import time** — lets tests
           import ``storage`` without a live ``.env``, while still failing fast
           before the first real DB operation.
        3. **``ValueError`` with an explicit message** — operators immediately
           see which variable is missing instead of a cryptic ``None`` URL in
           httpx.

    Returns:
        A configured :class:`supabase.Client` reused for all subsequent calls.

    What breaks if this is wrong:
        A fresh client per call → intermittent auth errors and slow ingest.
        Skipping validation → ``create_client(None, …)`` raises deep inside
        httpx and masks the root cause.

    Raises:
        ValueError: If ``SUPABASE_URL`` or ``SUPABASE_KEY`` is missing or empty.
    """

    global _supabase_client

    # WHY THIS EXISTS IN PRISM AI:
    # First call pays the ``create_client`` cost; every later call reuses
    # the same TCP pool — critical when inserting 100-row chunk batches.
    #
    # WHAT THIS BLOCK DOES:
    # Return existing client if already constructed.
    #
    # WHY THIS WAY:
    # Double-checked locking isn't needed — Python's GIL makes assignment
    # of the client reference atomic for our single-threaded FastAPI worker.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Always constructing → connection leaks or handshake storms under load.
    if _supabase_client is not None:
        return _supabase_client

    # WHY THIS EXISTS IN PRISM AI:
    # Secrets must never be hardcoded — they rotate per environment and per
    # developer machine.
    #
    # WHAT THIS BLOCK DOES:
    # Read URL and anon/service key from the environment.
    #
    # WHY THIS WAY:
    # ``os.getenv`` returns ``None`` for unset vars — we normalize emptiness
    # with ``not url`` so ``VAR=""`` also fails loudly.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Silent ``None`` URLs cause obscure connection errors minutes into ingest.
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url:
        raise ValueError(
            "SUPABASE_URL environment variable is not set or is empty. "
            "Add it to backend/.env before calling get_supabase()."
        )
    if not key:
        raise ValueError(
            "SUPABASE_KEY environment variable is not set or is empty. "
            "Add it to backend/.env before calling get_supabase()."
        )

    # WHY THIS EXISTS IN PRISM AI:
    # ``create_client`` wires auth headers and the PostgREST base URL — this
    # is the official Supabase Python entrypoint.
    #
    # WHAT THIS BLOCK DOES:
    # Instantiate and cache the client.
    #
    # WHY THIS WAY:
    # Assignment to the module global happens once; subsequent imports see the
    # cached instance.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Forgetting to assign → every call creates a new client anyway.
    _supabase_client = create_client(url, key)
    logger.info("Supabase client initialised (singleton).")
    return _supabase_client


def compute_hash(content: bytes | str) -> str:
    """Compute a SHA-256 hex digest for raw bytes or UTF-8 text.

    One-sentence summary: normalises input to bytes, hashes once, returns the
    64-character lowercase hex string.

    Why it exists for PrismAI:
        Dedup and change-detection drive whether we skip ingest, re-embed
        everything, or patch Excel rows. Drive files are hashed from raw bytes;
        Gmail messages from ``email_id + body``; spreadsheet rows from joined
        cell values — all paths converge on this single function so two pipelines
        never disagree on what "same content" means.

    Decisions made inside:
        1. **Strings encoded as UTF-8** — matches how Chunk ``content`` and
           email bodies are stored as text in Python.
        2. **SHA-256** — fast, collision-resistant enough for document-level
           dedup; stable across machines (unlike pickle hashes).

    Returns:
        Lowercase hex digest string. Callers store this in ``documents.content_hash``
        or compare against ``row_hashes.row_hash``.

    What breaks if this is wrong:
        Wrong encoding → same logical file hashes differently → duplicate
        documents or missed re-ingests. Wrong algorithm → dedup logic diverges
        from mobile/web clients if they ever compute hashes independently.

    Raises:
        UnicodeEncodeError: If a string contains characters not representable in
            UTF-8 (extremely rare for PM-facing text).
    """

    # WHY THIS EXISTS IN PRISM AI:
    # ``hashlib.sha256`` consumes bytes; Drive ingestion hands us ``bytes`` while
    # Gmail concatenation produces ``str``. Branching once here keeps every caller
    # simple.
    #
    # WHAT THIS BLOCK DOES:
    # Convert strings to UTF-8 bytes; leave bytes untouched.
    #
    # WHY THIS WAY:
    # UTF-8 is the project's canonical on-disk and on-wire encoding for text.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Passing a ``str`` directly to ``sha256`` raises ``TypeError`` and stops
    # the whole batch ingest at file one.
    data = content.encode("utf-8") if isinstance(content, str) else content

    # WHY THIS EXISTS IN PRISM AI:
    # Hex digest is what we store in Postgres ``text`` columns — readable in SQL
    # editors and safe in JSON logs without binary blobs.
    #
    # WHAT THIS BLOCK DOES:
    # Compute SHA-256 and return ``hexdigest()``.
    #
    # WHY THIS WAY:
    # One-shot ``hashlib.sha256(data).hexdigest()`` avoids incremental ``update``
    # boilerplate for single blobs.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Returning ``digest()`` (raw bytes) would corrupt JSON inserts and break
    # string comparisons in Python.
    return hashlib.sha256(data).hexdigest()


def get_document_by_source_id(
    supabase: Client,
    source_id: str,
) -> Optional[Dict[str, Any]]:
    """Fetch ``id`` and ``content_hash`` for a document by its external ``source_id``.

    One-sentence summary: runs a minimal ``SELECT`` on ``documents`` keyed by
    ``source_id`` and returns the first row or ``None``.

    Why it exists for PrismAI:
        Drive file IDs and Gmail message IDs are stable external keys. Pipeline
        asks "have we seen this ``source_id`` before?" before uploading chunks —
        we only need the UUID primary key and the last hash to decide skip vs
        re-ingest vs insert.

    Decisions made inside:
        1. **Select only ``id`` and ``content_hash``** — smaller payload than
           ``SELECT *``; avoids leaking huge ``metadata`` blobs into Python when
           all we need is dedup state.
        2. **``.maybe_single()``** — PostgREST returns a single dict or ``None``
           when zero rows; avoids catching exceptions on miss.

    Returns:
        ``{"id": "<uuid>", "content_hash": "<sha256>"}`` or ``None`` if no row.

    What breaks if this is wrong:
        Selecting ``*`` → slower ingest and accidental coupling to columns we
        rename later. Using ``.single()`` instead of ``maybe_single()`` → 406
        errors when no row exists, crashing "first upload" flows.

    Raises:
        PostgREST errors if the table or columns don't exist — surfaces schema drift.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # We deliberately fetch two columns only — network + JSON decode stays tiny
    # on hot-path dedup queries during 10k-file bulk uploads.
    #
    # WHAT THIS BLOCK DOES:
    # Query ``documents`` filtered by ``source_id``, limit semantics via
    # ``maybe_single``.
    #
    # WHY THIS WAY:
    # ``maybe_single()`` maps cleanly to Optional[dict] without try/except.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Wrong column names → PostgREST 400 and ingest stops for every file.
    try:
        response = (
            supabase.table("documents")
            .select("id, content_hash")
            .eq("source_id", source_id)
            .maybe_single()
            .execute()
        )
    except Exception:
        return None

    if response is None:
        return None

    data = getattr(response, "data", None)
    if data is None:
        return None
    if isinstance(data, list):
        if not data:
            return None
        row = data[0]
    else:
        row = data

    if not isinstance(row, dict):
        return None

    doc_id = row.get("id")
    content_hash = row.get("content_hash")
    if doc_id is None or content_hash is None:
        return None

    return {"id": doc_id, "content_hash": content_hash}


def document_exists_by_content_hash(
    supabase: Client,
    content_hash: str,
) -> bool:
    """Return True if any ``documents`` row already stores this ``content_hash``.

    One-sentence summary: existence check used to catch duplicate uploads under
    different ``source_id`` values (same bytes, new Drive file).

    Why it exists for PrismAI:
        PMs re-export ``Sprint3_Retro.docx`` as ``Sprint3_Retro_copy.docx`` with a
        new Drive ID but identical bytes. ``source_id`` dedup misses that;
        ``content_hash`` catches it so we don't double-bill embeddings or answer
        with two identical chunks.

    Decisions made inside:
        1. **``limit(1)``** — we only need existence, not a full duplicate list.
        2. **Select minimal column ``id``** — satisfies PostgREST while keeping
           payload tiny.

    Returns:
        ``True`` if at least one matching row exists, else ``False``.

    What breaks if this is wrong:
        Always returning ``False`` → duplicate docs flood pgvector and PM search
        returns the same paragraph twice. Always ``True`` → every new upload looks
        like a duplicate and nothing ever ingests.

    Raises:
        PostgREST errors on schema mismatch.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Existence probe — selecting ``id`` alone proves a row is there without
    # transferring titles or metadata JSON.
    #
    # WHAT THIS BLOCK DOES:
    # Query ``documents`` where ``content_hash`` matches, cap at one row.
    #
    # WHY THIS WAY:
    # ``limit(1)`` stops the server scanning more than necessary on large tables.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # No limit → Postgres may plan a sequential scan returning many IDs we throw
    # away — slower bulk dedup.
    response = (
        supabase.table("documents")
        .select("id")
        .eq("content_hash", content_hash)
        .limit(1)
        .execute()
    )

    # WHY THIS EXISTS IN PRISM AI:
    # ``execute().data`` is a list of rows — non-empty means duplicate content.
    #
    # WHAT THIS BLOCK DOES:
    # Return boolean based on whether ``data`` has length.
    #
    # WHY THIS WAY:
    # Explicit ``bool(...)`` makes the return type obvious to type checkers.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Checking ``data is not None`` alone → ``[]`` is truthy-fails incorrectly... 
    # actually ``[]`` is falsy in ``bool([])`` → False. Good.
    # Checking wrong attribute → always False.
    return bool(response.data)


def insert_document(supabase: Client, doc_data: Dict[str, Any]) -> str:
    """Insert one row into ``documents`` and return the new primary-key UUID.

    One-sentence summary: thin wrapper around ``INSERT`` that extracts ``id``
    from the PostgREST representation response.

    Why it exists for PrismAI:
        After pipeline validates a file, it writes the document envelope (title,
        folder, sprint, owner, hashes, timestamps) **before** chunks exist. That
        UUID becomes ``document_id`` on every ``document_chunks`` row — the spine
        of RAG citations ("this answer came from doc X").

    Decisions made inside:
        1. **Caller supplies full ``doc_data`` dict** — keeps ``storage.py``
           schema-agnostic; when Supabase adds a nullable column, pipeline passes
           it without editing every INSERT builder here.
        2. **Return ``id`` from ``response.data[0]``** — representation mode
           guarantees the inserted row echoes generated defaults (UUID, timestamps).

    Returns:
        The new document's UUID as a string.

    What breaks if this is wrong:
        Wrong table name → every ingest 404s. Mis-parsing response → pipeline
        attaches chunks to ``None`` and FK inserts explode.

    Raises:
        PostgREST errors on constraint violations (duplicate ``source_id``, etc.).
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Single-row insert — PostgREST accepts a dict or list of dicts; dict is
    # clearer for one document envelope.
    #
    # WHAT THIS BLOCK DOES:
    # Insert ``doc_data`` into ``documents``.
    #
    # WHY THIS WAY:
    # Default ``returning='representation'`` from supabase-py returns the row.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Omitting required NOT NULL columns → 400 and the PM sees "upload failed".
    response = supabase.table("documents").insert(doc_data).execute()

    # WHY THIS EXISTS IN PRISM AI:
    # We need the UUID for subsequent chunk inserts — extracting here avoids every
    # caller duplicating ``response.data[0]["id"]``.
    #
    # WHAT THIS BLOCK DOES:
    # Pull ``id`` from the first returned row.
    #
    # WHY THIS WAY:
    # Index ``[0]`` fails loudly if insert broke silently — better than returning
    # ``None``.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # If ``data`` is empty due to RLS blocking return, we raise here — surfacing
    # misconfigured policies immediately.
    if not response.data:
        raise RuntimeError(
            "insert_document: Supabase returned no row data — check RLS policies "
            "and INSERT privileges on the documents table."
        )
    row = response.data[0]
    new_id = row["id"]
    logger.info("Inserted document id=%s source_id=%s", new_id, doc_data.get("source_id"))
    return str(new_id)


def update_document_after_reingestion(
    supabase: Client,
    document_id: str,
    new_hash: str,
) -> None:
    """Update ``content_hash`` and ``ingested_at`` after a successful re-ingest.

    One-sentence summary: marks the document row as freshly embedded without
    deleting the stable ``id`` foreign-key anchor.

    Why it exists for PrismAI:
        When a PRD changes, we delete old chunks, insert new vectors, but keep
        the same ``documents.id`` so bookmarks, Slack links, and audit trails stay
        valid. Updating hash + timestamp tells operators "this version is live".

    Decisions made inside:
        1. **ISO 8601 UTC via ``datetime.now(timezone.utc).isoformat()``** —
           Postgres ``timestamptz`` parses this cleanly; timezone-aware avoids
           daylight-saving ambiguity in logs.
        2. **Only two columns touched** — leaves title/folder alone unless
           pipeline separately updates them.

    Returns:
        ``None``.

    What breaks if this is wrong:
        Forgetting ``ingested_at`` → stale freshness indicators in admin UI.
        Wrong ``document_id`` → silent zero-row update if RLS hides rows — caller
        should verify rows affected in strict mode later if needed.

    Raises:
        PostgREST errors on invalid UUID or RLS denial.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # ``ingested_at`` answers "when did PrismAI last embed this?" for support
    # tickets ("I uploaded Friday but still see Monday's answer").
    #
    # WHAT THIS BLOCK DOES:
    # Build the PATCH payload with new hash and current UTC timestamp string.
    #
    # WHY THIS WAY:
    # ISO format string matches how most Supabase JS/Python examples store timestamps.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Naive ``datetime.utcnow()`` → missing ``Z`` offset in some clients' parsers.
    payload = {
        "content_hash": new_hash,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }

    # WHY THIS EXISTS IN PRISM AI:
    # Scoped update by primary key — never blanket-updates the whole table.
    #
    # WHAT THIS BLOCK DOES:
    # ``UPDATE documents SET ... WHERE id = document_id``.
    #
    # WHY THIS WAY:
    # ``.eq("id", document_id)`` is the canonical Supabase filter pattern.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Wrong filter column → wrong document rows get new hashes — catastrophic for
    # retrieval attribution.
    supabase.table("documents").update(payload).eq("id", document_id).execute()
    logger.info(
        "Updated document after re-ingestion id=%s new_hash_prefix=%s...",
        document_id,
        new_hash[:12],
    )


def update_document_metadata_only(
    supabase: Client,
    document_id: str,
    new_metadata: Dict[str, Any],
) -> None:
    """Replace only ``documents.metadata`` (e.g. Gmail labels) without re-embedding.

    One-sentence summary: PATCH one JSON column so label churn doesn't trigger
    chunk deletes or embedding spend.

    Why it exists for PrismAI:
        Gmail threads gain labels ("Blocked", "FYI") without body changes.
        Re-embedding those would burn tokens and churn vectors identically.
        This path updates Supabase metadata for filters/UI while leaving vectors
        untouched — zero embedding cost.

    Decisions made inside:
        1. **JSON dict passed through** — Supabase stores JSONB; Python dict maps
           cleanly via PostgREST JSON encoding.
        2. **Does not touch ``content_hash`` or ``ingested_at``** — preserves the
           semantic "last embedded" truth.

    Returns:
        ``None``.

    What breaks if this is wrong:
        Accidentally calling this after a body edit → chunks reflect old text while
        metadata claims new labels — PM sees contradictory filters.

    Raises:
        PostgREST errors on invalid JSON or RLS.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Narrowest possible write surface — reduces accidental column wipes during
    # refactors.
    #
    # WHAT THIS BLOCK DOES:
    # ``UPDATE documents SET metadata = :new_metadata WHERE id = :id``.
    #
    # WHY THIS WAY:
    # Single-key payload ensures PostgREST can't misinterpret fields.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Passing ``new_metadata`` at top level mixed with other keys → unintentionally
    # clears columns omitted from JSON merge semantics depending on API version.
    supabase.table("documents").update({"metadata": new_metadata}).eq(
        "id", document_id
    ).execute()
    logger.info("Updated document metadata only id=%s", document_id)


def delete_chunks_for_document(supabase: Client, document_id: str) -> None:
    """Delete all ``document_chunks`` rows for a document; keep the ``documents`` row.

    One-sentence summary: wipes vectors before re-inserting fresh embeddings after
    a content change.

    Why it exists for PrismAI:
        Re-ingesting an updated PRD must remove stale chunk rows first — otherwise
        similarity search returns both v1 and v2 paragraphs and the PM gets self-
        contradictory answers ("velocity was 40" vs "velocity was 52").

    Decisions made inside:
        1. **Count-before-delete for logging** — operators see how much storage was
           reclaimed; Supabase delete responses don't always echo counts clearly.
        2. **Delete filtered by ``document_id`` only** — scoped blast radius.

    Returns:
        ``None``.

    What breaks if this is wrong:
        Skipping delete → duplicate chunks accumulate OR stale vectors remain.
        Over-broad delete → wipes another team's doc if ``document_id`` wrong.

    Raises:
        PostgREST errors on missing table or RLS denial.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Operators grep logs for "Deleted N chunks" during incident response — we need
    # N without fetching every primary key into Python RAM.
    #
    # WHAT THIS BLOCK DOES:
    # Run a ``COUNT``-exact select scoped to ``document_id``.
    #
    # WHY THIS WAY:
    # Supabase-py attaches ``.count`` to the response when ``count='exact'`` is passed.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # If count unavailable, we log "unknown" rather than crashing the delete path.
    count_resp = (
        supabase.table("document_chunks")
        .select("id", count="exact")
        .eq("document_id", document_id)
        .execute()
    )
    n_before = getattr(count_resp, "count", None)

    # WHY THIS EXISTS IN PRISM AI:
    # Actual removal of vectors + metadata rows from ``document_chunks``.
    #
    # WHAT THIS BLOCK DOES:
    # ``DELETE FROM document_chunks WHERE document_id = :id``.
    #
    # WHY THIS WAY:
    # Filtered delete is idempotent — second call deletes zero rows harmlessly.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Missing filter → catastrophic table truncation if chain bug ever dropped filter.
    supabase.table("document_chunks").delete().eq("document_id", document_id).execute()

    logger.info(
        "Deleted chunks for document_id=%s (count_before=%s)",
        document_id,
        n_before if n_before is not None else "unknown",
    )


def delete_document_and_chunks(supabase: Client, document_id: str) -> None:
    """Delete a document row (chunks cascade) and explicitly purge ``row_hashes``.

    One-sentence summary: full removal when a source file is permanently gone from
    Drive/Gmail and PrismAI should forget it entirely.

    Why it exists for PrismAI:
        GDPR-style deletes and "wrong repo uploaded" clean-ups require removing the
        document spine AND vectors. Chunks cascade from ``documents`` FK; ``row_hashes``
        does **not** cascade (per your schema note) — leaving orphans would confuse
        Excel delta logic on the next ingest of an unrelated doc.

    Decisions made inside:
        1. **Delete ``row_hashes`` first** — avoids FK issues if ``row_hashes``
           references ``documents``.
        2. **Then delete ``documents``** — relying on FK cascade to wipe chunks.
        3. **Explicit chunk cascade assumption** — if cascade isn't configured in
           Supabase, chunks become orphans — schema must match.

    Returns:
        ``None``.

    What breaks if this is wrong:
        Deleting ``documents`` before ``row_hashes`` → FK violation aborts txn.
        Forgetting ``row_hashes`` → stale Excel hash rows point at deleted docs.

    Raises:
        PostgREST / FK errors if schema constraints disagree with call order.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # ``row_hashes`` is not covered by ON DELETE CASCADE from ``documents`` in your
    # Supabase setup — explicit delete prevents orphaned hash rows that would make
    # delta-sync think rows still exist for a ghost document_id.
    #
    # WHAT THIS BLOCK DOES:
    # ``DELETE FROM row_hashes WHERE document_id = :id``.
    #
    # WHY THIS WAY:
    # Filtered delete scoped to the UUID — never blanket truncate.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Skipping this → next Excel ingest sees phantom hashes under recycled IDs if
    # UUIDs were ever reused (they shouldn't be, but orphans still clutter storage).
    rh = (
        supabase.table("row_hashes")
        .delete()
        .eq("document_id", document_id)
        .execute()
    )
    logger.info(
        "Deleted row_hashes for document_id=%s (response rows=%s)",
        document_id,
        len(rh.data) if rh.data else 0,
    )

    # WHY THIS EXISTS IN PRISM AI:
    # Removing the ``documents`` row triggers FK cascade on ``document_chunks`` per
    # your DB configuration — one delete wipes all vectors tied to this PRD/email.
    #
    # WHAT THIS BLOCK DOES:
    # ``DELETE FROM documents WHERE id = :id``.
    #
    # WHY THIS WAY:
    # Primary-key delete is the smallest logical operation for "remove this corpus".
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # If cascade is NOT configured, chunks remain referencing a missing document —
    # retrieval joins break and PM answers cite ghost documents.
    doc_del = supabase.table("documents").delete().eq("id", document_id).execute()
    logger.info(
        "Deleted document id=%s and cascaded chunks (documents_response_rows=%s)",
        document_id,
        len(doc_del.data) if doc_del.data else 0,
    )


def insert_chunks_with_embeddings(
    supabase: Client,
    document_id: str,
    chunks: List[Chunk],
    embeddings: List[List[float]],
) -> int:
    """Insert paired Chunk rows and embedding vectors into ``document_chunks``.

    One-sentence summary: validates parallel lists, builds denormalised projection
    columns from each chunk's metadata JSON, and inserts in batches of 100.

    Why it exists for PrismAI:
        After embedder returns vectors, pipeline must persist (content, embedding,
        filters for sprint/folder/sheet/page) in one transactionally-safe sequence.
        Batching keeps ingest under PostgREST payload limits and reduces round trips
        during a 3,000-chunk PDF.

    Decisions made inside:
        1. **``len(chunks) == len(embeddings)`` enforced** — impossible to silently zip
           misaligned lists (the worst class of RAG bugs — wrong vector for paragraph).
        2. **Batch size 100** — matches embedder batching and stays below common
           gateway body limits (~few MB JSON).
        3. **Denormalised columns extracted from ``chunk.metadata``** — speeds filters
           (`WHERE sprint = '24'`) without JSON operators in hot queries; full
           ``metadata`` JSON preserved for forward compatibility.
        4. **``chunk_type`` defaults to ``"standard"``** — UI and ranking can treat
           tables/slides differently later.
        5. **``token_count`` via whitespace split word count** — proxy for billing /
           diagnostics until tiktoken is wired.
        6. **Embedding stored as Python list** — PostgREST/pgvector accepts float arrays.
        7. **``sender`` and ``subject`` columns for Gmail chunks** — promoted from
           metadata so email agents can filter without JSON operators: "show me all
           emails from Arjun" uses ``WHERE sender = …``, "find emails about
           GOAL-BUG-005" uses ``WHERE subject ILIKE …`` on an indexed column.

    Returns:
        Integer count of rows inserted (sum across batches).

    What breaks if this is wrong:
        Misaligned zip → answers cite wrong sections. Oversized batches → HTTP 413
        or gateway timeouts mid-ingest. Omitting ``document_id`` FK → insert fails.

    Raises:
        ValueError: If chunk and embedding list lengths differ.
        PostgREST errors on dimension mismatch (embedding length ≠ column dim), FK
            violations, or RLS denial.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # This guard catches the #1 silent data corruption bug in batched RAG — off-by-one
    # embedding arrays from retry logic bugs.
    #
    # WHAT THIS BLOCK DOES:
    # Raise ``ValueError`` if lengths differ.
    #
    # WHY THIS WAY:
    # Fail fast before touching Supabase — partial inserts would be harder to roll back.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Without guard, first batch might succeed while second crashes — DB ends up with
    # half a document embedded.
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"insert_chunks_with_embeddings: len(chunks)={len(chunks)} != "
            f"len(embeddings)={len(embeddings)} — refusing to insert misaligned data."
        )

    # WHY THIS EXISTS IN PRISM AI:
    # Building all records first keeps the batch loop simple — we slice Python lists,
    # not re-walk Chunk objects per batch slice boundary math twice.
    #
    # WHAT THIS BLOCK DOES:
    # Zip chunks with embeddings and construct one dict per row for PostgREST.
    #
    # WHY THIS WAY:
    # Local ``meta`` variable avoids mutating the dataclass's metadata dict.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Wrong field names vs Supabase columns → 400 errors on every insert.
    records: List[Dict[str, Any]] = []
    for chunk, embedding in zip(chunks, embeddings):
        meta = chunk.metadata or {}
        record: Dict[str, Any] = {
            "document_id": document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "embedding": embedding,
            "chunk_type": meta.get("element_type", meta.get("chunk_type", "standard")),
            "token_count": len(chunk.content.split()),
            "source_type": meta.get("source_type"),
            "folder": meta.get("folder"),
            "sprint": meta.get("sprint"),
            "section_heading": meta.get("section_heading"),
            "sheet_name": meta.get("sheet_name"),
            "page_number": meta.get("page_number"),
            "doc_type": meta.get("doc_type"),
            "document_title": meta.get("file_name") or meta.get("document_title"),
            "quarter": meta.get("quarter"),
            "file_created_at": meta.get("file_created_at"),
            "file_updated_at": meta.get("file_updated_at"),
            "author": meta.get("owner") or meta.get("sender"),
            "people": meta.get("people", []),
            "ticket_ids": meta.get("ticket_ids", []),
            "features": meta.get("features", []),
            "metrics": meta.get("metrics", []),
            # WHY THIS EXISTS IN PRISM AI:
            # Gmail is filtered constantly by who sent the thread and what the
            # subject line mentions — these are hot paths, not occasional reads.
            #
            # WHAT THIS BLOCK DOES:
            # Copies sender and subject from chunk metadata onto real table columns.
            #
            # WHY THIS WAY:
            # Indexed columns beat ``metadata->>'sender'`` JSONB extraction on every
            # poll ("emails from Arjun", "subject contains GOAL-BUG-005").
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Values only in JSONB → slow scans, missed indexes, email filters time
            # out or return stale results under load.
            "sender": meta.get("sender"),
            "subject": meta.get("subject"),
            "metadata": meta,
        }
        records.append(record)

    # WHY THIS EXISTS IN PRISM AI:
    # PostgREST has practical payload limits; 100-row batches mirror ``embedder.py``
    # so operational logs align ("embedded 100, inserted 100").
    #
    # WHAT THIS BLOCK DOES:
    # Slice ``records`` into windows of 100 and ``INSERT`` each.
    #
    # WHY THIS WAY:
    # Simple ``for i in range(0, len, 100)`` — no itertools dependency.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Single giant insert → timeout or 413; partial failure loses granularity on retry.
    total_inserted = 0
    batch_size = 100
    for start in range(0, len(records), batch_size):
        batch = records[start : start + batch_size]
        resp = supabase.table("document_chunks").insert(batch).execute()
        inserted = len(resp.data) if resp.data else len(batch)
        total_inserted += inserted
        logger.info(
            "Inserted document_chunks batch document_id=%s rows=%s (start_index=%s)",
            document_id,
            inserted,
            start,
        )

    logger.info(
        "Finished insert_chunks_with_embeddings document_id=%s total_rows=%s",
        document_id,
        total_inserted,
    )
    return total_inserted


def get_row_hashes_for_document(
    supabase: Client,
    document_id: str,
) -> Dict[str, str]:
    """Return a map ``"{sheet_name}:{row_index}" -> row_hash`` for Excel delta sync.

    One-sentence summary: loads all ``row_hashes`` rows for a document into an in-
    memory dict keyed by sheet + row position.

    Why it exists for PrismAI:
        Large Excel backlogs change one row at a time (owner tweak, status flip).
        Re-embedding the whole sheet wastes money. Pipeline compares live row hashes
        against this dict to find dirty indices only.

    Decisions made inside:
        1. **Composite string key ``f"{sheet_name}:{row_index}"``** — unique across
           sheets without nested dict default-dict boilerplate in callers.
        2. **Values are hex hashes** — direct string compare with ``compute_hash`` output.

    Returns:
        Dict mapping composite keys to hash strings; empty dict if no rows.

    What breaks if this is wrong:
        Wrong key format → pipeline misses dirty rows OR deletes wrong chunks.
        Returning full ORM objects → slower Excel sync on 100k-row sheets.

    Raises:
        PostgREST errors if ``row_hashes`` table missing.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # We need three columns to build the composite key and compare hashes — nothing else.
    #
    # WHAT THIS BLOCK DOES:
    # Select ``sheet_name``, ``row_index``, ``row_hash`` filtered by ``document_id``.
    #
    # WHY THIS WAY:
    # No ``SELECT *`` — avoids pulling created_at noise into Python on wide rows.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Wrong column names → KeyError building dict keys below.
    response = (
        supabase.table("row_hashes")
        .select("sheet_name, row_index, row_hash")
        .eq("document_id", document_id)
        .execute()
    )

    # WHY THIS EXISTS IN PRISM AI:
    # Callers do ``stored[k] == computed`` — O(1) dict probe per row during Excel scan.
    #
    # WHAT THIS BLOCK DOES:
    # Fold result rows into ``out``.
    #
    # WHY THIS WAY:
    # ``str(row_index)`` normalises if PostgREST returns int — key stays stable.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Using bare ``row_index`` as dict key without sheet → collisions across sheets.
    out: Dict[str, str] = {}
    for row in response.data or []:
        key = f"{row['sheet_name']}:{row['row_index']}"
        out[key] = row["row_hash"]
    logger.info(
        "Loaded %s row_hashes entries for document_id=%s",
        len(out),
        document_id,
    )
    return out


def upsert_row_hashes(
    supabase: Client,
    document_id: str,
    sheet_name: str,
    row_hashes_dict: Dict[int, str],
) -> None:
    """Upsert per-row content hashes for Excel delta detection.

    One-sentence summary: writes ``(document_id, sheet_name, row_index, row_hash)``
    rows with ``ON CONFLICT DO UPDATE`` on the composite unique key.

    Why it exists for PrismAI:
        After processing one sheet, pipeline stores fingerprints for every logical
        row. Next sync recomputes hashes — unchanged rows skip chunk deletes;
        changed rows trigger targeted ``delete_chunks_for_rows``.

    Decisions made inside:
        1. **Supabase ``upsert(..., on_conflict='document_id,sheet_name,row_index')``** —
           matches your UNIQUE constraint; avoids race duplicate inserts from parallel workers.
        2. **Batch entire sheet dict in one HTTP call** — sheets rarely exceed a few thousand
           rows; single upsert keeps txn atomic from PrismAI's perspective.

    Returns:
        ``None``.

    What breaks if this is wrong:
        Wrong ``on_conflict`` columns → Postgres rejects upsert or creates duplicates.
        Missing upsert → second ingest fails on unique violations.

    Raises:
        PostgREST errors on constraint name mismatch or RLS denial.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Empty sheet edge case — nothing to write, avoid empty upsert quirks.
    #
    # WHAT THIS BLOCK DOES:
    # Early return if no row hashes computed.
    #
    # WHY THIS WAY:
    # Saves an HTTP round-trip.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # None — harmless skip.
    if not row_hashes_dict:
        logger.info(
            "upsert_row_hashes skipped empty dict document_id=%s sheet=%s",
            document_id,
            sheet_name,
        )
        return

    # WHY THIS EXISTS IN PRISM AI:
    # PostgREST upsert expects a list of homogeneous dicts matching table columns.
    #
    # WHAT THIS BLOCK DOES:
    # Materialise ``row_hashes_dict`` into ORM-shaped rows.
    #
    # WHY THIS WAY:
    # List comprehension keeps order deterministic (sorted by row_index for easier
    # log diffing — optional but nice); we sort keys for stable batch content.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Wrong keys → column mismatch errors on upsert.
    rows_to_upsert = [
        {
            "document_id": document_id,
            "sheet_name": sheet_name,
            "row_index": row_index,
            "row_hash": row_hash,
        }
        for row_index, row_hash in sorted(row_hashes_dict.items())
    ]

    # WHY THIS EXISTS IN PRISM AI:
    # ``ON CONFLICT (document_id, sheet_name, row_index) DO UPDATE`` semantics —
    # critical for idempotent nightly sync jobs that may retry halfway.
    #
    # WHAT THIS BLOCK DOES:
    # ``UPSERT`` all rows for this sheet in one API call.
    #
    # WHY THIS WAY:
    # ``on_conflict`` string lists columns exactly as defined in unique constraint order
    # (must match Postgres constraint column order — verify in Supabase dashboard).
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Column order typo → upsert falls back to insert-only and raises duplicate key errors.
    supabase.table("row_hashes").upsert(
        rows_to_upsert,
        on_conflict="document_id,sheet_name,row_index",
    ).execute()
    logger.info(
        "Upserted %s row_hashes rows document_id=%s sheet=%s",
        len(rows_to_upsert),
        document_id,
        sheet_name,
    )


def delete_chunks_for_rows(
    supabase: Client,
    document_id: str,
    row_indices: List[int],
) -> None:
    """Delete ``document_chunks`` rows whose JSON metadata ``row_index`` matches.

    One-sentence summary: targeted chunk wipe for Excel rows that changed — leaves
    untouched rows' vectors in place.

    Why it exists for PrismAI:
        Owner updates on row 14 shouldn't force re-embedding rows 1–13. Pipeline
        computes dirty indices, calls this, then inserts fresh chunks only for those rows.

    Decisions made inside:
        1. **Filter ``metadata->>row_index`` via ``IN`` list** — PostgREST exposes JSON
           path columns in filters; values compared as **strings** because ``->>`` returns text.
        2. **Early return on empty ``row_indices``** — avoids generating ``IN ()`` SQL edge cases.
        3. **Always scoped by ``document_id``** — prevents cross-document deletes.

    Returns:
        ``None``.

    What breaks if this is wrong:
        Broad delete → wipes sprint velocity chunks unrelated to the edited row.
        Wrong JSON path → zero rows deleted → stale answers persist for changed Excel cells.

    Raises:
        PostgREST errors if filter syntax rejected by API version (fallback would be per-row delete).
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Empty dirty set after diff means nothing to delete — skip HTTP call.
    #
    # WHAT THIS BLOCK DOES:
    # Return immediately if ``row_indices`` is empty.
    #
    # WHY THIS WAY:
    # Defensive against pipeline calling with ``[]`` after filter optimisation.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Low risk — worst case wasted round-trip if check omitted.
    if not row_indices:
        logger.info(
            "delete_chunks_for_rows skipped empty row_indices document_id=%s",
            document_id,
        )
        return

    # WHY THIS EXISTS IN PRISM AI:
    # JSON ``metadata`` stores ``row_index`` as emitted by chunkers (integer in Python dict,
    # serialised to JSON number). PostgREST ``->>`` yields TEXT — we must ``IN`` compare
    # against string forms ``\"14\"`` not mixed int/string or some paths fail to match.
    #
    # WHAT THIS BLOCK DOES:
    # Build ``str_indices`` for ``.in_()`` filter.
    #
    # WHY THIS WAY:
    # Explicit ``str(i)`` keeps behaviour aligned with ``metadata->>row_index`` text extraction.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Passing ints when DB stores text → zero deletes → PM sees stale Excel answers forever.
    str_indices = [str(i) for i in row_indices]

    # WHY THIS EXISTS IN PRISM AI:
    # The actual targeted delete — ``document_id`` AND row_index IN dirty set.
    #
    # WHAT THIS BLOCK DOES:
    # Chain ``eq`` + ``in_`` on ``document_chunks``.
    #
    # WHY THIS WAY:
    # Single query deletes all dirty-row chunks at once — faster than N sequential deletes.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # If ``metadata->>row_index`` filter unsupported by hosted PostgREST config, switch to
    # RPC — but this matches standard Supabase JSON filtering docs.
    (
        supabase.table("document_chunks")
        .delete()
        .eq("document_id", document_id)
        .in_("metadata->>row_index", str_indices)
        .execute()
    )
    logger.info(
        "Deleted chunks for document_id=%s row_indices=%s",
        document_id,
        row_indices,
    )


def log_ingestion_result(results: List[Dict[str, Any]]) -> None:
    """Print a human-readable summary of a batch ingestion run to stdout.

    One-sentence summary: aggregates per-file result dicts into counts and lists
    failures for terminal operators.

    Why it exists for PrismAI:
        After processing a Drive folder with 200 files, PMs and developers need an at-a-glance
        digest — how many net-new ingests vs skips vs errors vs total chunks — without reading
        JSON logs.

    Decisions made inside:
        1. **Uses ``print`` not ``logger.info`` for the framed summary** — matches your spec's
           console UX; structured logs already happened during writes.
        2. **``re_ingested`` flag splits successes** — distinguishes fresh ingest from content refresh.
        3. **Failed files aggregate ``reason`** — speeds triage ("403 on file X").

    Returns:
        ``None``.

    What breaks if this is wrong:
        Silent summary → operators assume green builds when half the corpus failed.

    Raises:
        None intentionally — summary code must never throw on malformed result dicts; we ``.get`` defensively.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Four buckets drive operator behaviour — net ingest vs re-ingest vs skip vs hard error.
    #
    # WHAT THIS BLOCK DOES:
    # Initialise counters and failure collector.
    #
    # WHY THIS WAY:
    # Single pass over ``results`` keeps O(n) time for large batches.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Wrong initialisation → negative counts impossible but logic bugs could double-count.
    ingested = 0
    re_ingested = 0
    skipped = 0
    errors = 0
    total_chunks = 0
    failed_files: List[str] = []

    # WHY THIS EXISTS IN PRISM AI:
    # Each pipeline worker appends a uniform dict — but defensive ``.get`` prevents KeyError
    # if someone logs partial dicts during development.
    #
    # WHAT THIS BLOCK DOES:
    # Classify each result row into buckets and sum chunk counts.
    #
    # WHY THIS WAY:
    # Branch on ``status`` first — cheapest discriminator.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Misclassification → wrong headline numbers → PM trust erosion ("said 0 errors but DB empty").
    for item in results:
        status = item.get("status", "")
        title = item.get("title", "<unknown>")
        if status == "success":
            if item.get("re_ingested"):
                re_ingested += 1
            else:
                ingested += 1
            chunks = item.get("chunks")
            if isinstance(chunks, int):
                total_chunks += chunks
        elif status == "skipped":
            skipped += 1
        elif status == "error":
            errors += 1
            reason = item.get("reason", "unknown error")
            failed_files.append(f"{title}: {reason}")
        else:
            # WHY THIS EXISTS IN PRISM AI:
            # Forward-compatible — new statuses shouldn't crash the summary printer.
            #
            # WHAT THIS BLOCK DOES:
            # Treat unknown status as error bucket conservatively.
            #
            # WHY THIS WAY:
            # Safer to over-flag than hide failures.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Typo status strings inflate error count — still preferable to silent drop.
            errors += 1
            failed_files.append(f"{title}: unknown status {status!r}")

    # WHY THIS EXISTS IN PRISM AI:
    # Framed output matches the product spec ASCII mock — easy screenshot for Slack status.
    #
    # WHAT THIS BLOCK DOES:
    # ``print`` summary lines.
    #
    # WHY THIS WAY:
    # Pure stdout — CI/CD logs capture without log-level filters hiding it.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Using logger-only would bury summary under DEBUG in some deployments.
    sep = "────────────────────────────────────────────────────"
    print(sep)
    print("  Ingestion complete")
    print(f"  ✓ Ingested:     {ingested}")
    print(f"  ↺ Re-ingested:  {re_ingested}")
    print(f"  → Skipped:      {skipped} (unchanged)")
    print(f"  ✗ Errors:       {errors}")
    print()
    if failed_files:
        print("  Failed files:")
        for line in failed_files:
            print(f"    • {line}")
        print()
    print(f"  Total chunks stored: {total_chunks}")
    print(sep)
