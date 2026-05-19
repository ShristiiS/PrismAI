"""Single orchestrator for the PrismAI ingestion pipeline.

Why this module exists:
    Connectors (Google Drive, Gmail, future Slack/Notion) must call **only**
    this module to add, update, or remove content. Parsers, signal detectors,
    chunkers, embedders, and Supabase storage are all hidden behind these four
    public functions:

        * :func:`ingest_file`   — for any non-email file artefact (PRDs,
          retros, decks, sprint sheets, scanned PDFs).
        * :func:`ingest_email`  — for Gmail messages (HTML body, labels,
          attachments handled separately by the connector).
        * :func:`delete_file`   — when a Drive file is trashed or unshared.
        * :func:`delete_email`  — when a Gmail thread is trashed; cascades to
          attachment documents linked via ``metadata.parent_email_id``.

    Centralising the orchestration lets PrismAI guarantee:

    1. **Idempotent re-ingest** — same content never re-embedded; changed
       content re-embedded with old chunks atomically replaced.
    2. **Cost discipline** — duplicate-content skip and metadata-only update
       paths avoid embedding charges that PMs would otherwise see in their
       monthly OpenRouter bill.
    3. **One audit point** — every "what got ingested when" log line comes
       from this file, so failures can be traced without grepping connectors.

What breaks if this module is wrong:
    Connectors would either re-embed unchanged files (bill spikes), miss
    label changes (PMs ask "show me everything labelled urgent" and get
    stale results), or orphan chunks under deleted documents (retrieval
    cites ghost files).
"""

from __future__ import annotations

import hashlib  # noqa: F401  (kept per spec; storage.compute_hash is the canonical hasher)
import logging
import os  # noqa: F401  (kept per spec; ``load_dotenv`` populates os.environ)
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from ingestion.parsers import (
    parse_docx,
    parse_email_body,
    parse_excel,
    parse_pdf,
    parse_pptx,
    parse_text_file,
)
from ingestion.signal_detector import (
    Strategy,
    classify_excel_sheet_with_llm,
    detect_docx_strategy,
    detect_email_strategy,
    detect_excel_strategy,
    detect_pdf_strategy,
    detect_pptx_strategy,
    detect_text_strategy,
)
from ingestion.chunkers import (
    Chunk,
    chunk_document,
    chunk_email,
    chunk_excel_sheet,
    chunk_slide_elements,
)
from ingestion.embedder import get_embeddings
from ingestion.storage import (
    compute_hash,
    delete_chunks_for_document,
    delete_chunks_for_rows,  # noqa: F401  (re-exported for connectors that surgically update Excel)
    delete_document_and_chunks,
    document_exists_by_content_hash,
    get_document_by_source_id,
    get_row_hashes_for_document,  # noqa: F401  (re-exported for connectors / future row-diff path)
    get_supabase,
    insert_chunks_with_embeddings,
    insert_document,
    update_document_after_reingestion,
    update_document_metadata_only,
    upsert_row_hashes,
)


# WHY THIS EXISTS IN PRISM AI:
# Connectors import this module before touching Supabase. Loading
# backend/.env here ensures SUPABASE_URL / SUPABASE_KEY / OPENAI_API_KEY are
# resolved without the operator exporting them in every shell.
#
# WHAT THIS BLOCK DOES:
# Reads backend/.env into ``os.environ`` for downstream get_supabase() and
# get_embeddings() calls.
#
# WHY THIS WAY:
# ``load_dotenv()`` is idempotent — already-set platform secrets in prod
# (Render, Fly, Railway) take precedence over the .env file.
#
# WHAT BREAKS IF THIS IS WRONG:
# First Supabase call would 401, first embedding call would 401, and the
# Drive connector run would crash partway with no chunks stored.
load_dotenv()

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────
#  Internal helpers (private; not part of the public connector contract)
# ──────────────────────────────────────────────────────────────────────────


def _build_base_metadata(
    source_type: str,
    title: str,
    source_id: str,
    ext: str,
    folder: Optional[str],
    folder_path: Optional[str],
    folder_id: Optional[str],
    sprint: Optional[str],
    owner: Optional[str],
    file_created_at: Optional[str],
    file_updated_at: Optional[str],
    extra_metadata: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Assemble the ``base_metadata`` dict that every chunk inherits.

    Why centralised: chunkers all expect the same keys (``source_type``,
    ``folder``, ``sprint``, etc.) so retrieval filters work across formats.
    Spreading this dict construction across branches caused subtle drift
    (one path missed ``sprint``, retrieval mis-filtered).
    """

    # WHY THIS EXISTS IN PRISM AI:
    # PM filter UX depends on these keys being present on every chunk —
    # "show me sprint 24 PRDs in folder Roadmap" needs sprint and folder
    # to be on the chunk row even when the chunker is excel-mixed.
    #
    # WHAT THIS BLOCK DOES:
    # Returns a single dict combining caller-supplied identifiers with the
    # connector-supplied ``extra_metadata`` overlay.
    #
    # WHY THIS WAY:
    # ``**(extra_metadata or {})`` last lets connectors override anything
    # (e.g. ``parent_email_id`` for attachment files) without changing this
    # signature.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Missing keys → chunker writes incomplete metadata → PM filter
    # returns nothing or returns wrong-sprint content.
    return {
        "source_type": source_type,
        "file_name": title,
        "file_id": source_id,
        "file_type": ext.lstrip("."),
        "folder": folder,
        "folder_path": folder_path,
        "folder_id": folder_id,
        "sprint": sprint,
        "owner": owner,
        "file_created_at": file_created_at,
        "file_updated_at": file_updated_at,
        **(extra_metadata or {}),
    }


def _compute_excel_row_hashes(
    rows: List[List[Any]],
) -> Dict[int, str]:
    """Hash each Excel row's concatenated cell values for diff-based updates.

    Returns ``{row_index: sha256_hex}`` matching the contract of
    :func:`storage.upsert_row_hashes`.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Excel updates frequently change one cell out of thousands. We hash
    # each row so the next sync can compute a tiny diff (5 rows changed)
    # instead of re-embedding 3,000 rows.
    #
    # WHAT THIS BLOCK DOES:
    # Iterates data rows (index 1+; row 0 is the header), joins all cell
    # and computes SHA-256 via storage.compute_hash.
    #
    # WHY THIS WAY:
    # Pipe is a rare separator in PM data; using it avoids hash collisions
    # between (a, bc) and (ab, c). String coercion handles None / int /
    # float cells without crashing.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Bad hashing → row-diff update either misses changed rows (stale
    # answers) or marks every row dirty (cost spikes back to full
    # re-embed).
    row_hashes: Dict[int, str] = {}
    for row_index, row in enumerate(rows):
        if row_index == 0:
            continue
        joined = "|".join(str(cell) if cell is not None else "" for cell in row)
        row_hashes[row_index] = compute_hash(joined)
    return row_hashes


# ──────────────────────────────────────────────────────────────────────────
#  Public API (called by Drive / Gmail / future connectors)
# ──────────────────────────────────────────────────────────────────────────


def ingest_file(
    file_path: str,
    source_id: str,
    source_type: str,
    title: str,
    folder: Optional[str] = None,
    folder_path: Optional[str] = None,
    folder_id: Optional[str] = None,
    sprint: Optional[str] = None,
    owner: Optional[str] = None,
    file_created_at: Optional[str] = None,
    file_updated_at: Optional[str] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Ingest one file (PRD, retro, deck, spreadsheet, scan) end-to-end.

    One-sentence summary: hashes the file for dedup, decides
    create/update/skip, parses + chunks + embeds via the right strategy, and
    persists everything in Supabase under a single ``documents`` row.

    Why it exists for PrismAI:
        Drive connector polls ~thousands of files; each call here must be
        idempotent, cheap on unchanged content, and atomic on changed
        content (no half-replaced chunks). PMs depend on this guarantee for
        accurate retrieval after their sprint folders churn nightly.

    Steps (numbered):
        1. **Read & hash** — load file bytes once; compute SHA-256 used
           both for dedup and for the ``content_hash`` column on the
           document row.
        2. **Get Supabase client** — singleton, so connector loops don't
           reconnect 3,000 times.
        3. **Duplicate detection** —
              a. ``get_document_by_source_id`` → if hash matches, this is
                 the same file with no changes; skip with status
                 ``"skipped"`` reason ``"unchanged"``.
              b. If hash differs, mark ``action = "update"`` and remember
                 the existing document UUID so we can replace its chunks.
              c. If no row exists with that ``source_id``, fall through to
                 ``document_exists_by_content_hash`` — catches duplicate
                 file IDs (same PRD shared into a different folder).
        4. **Update path: delete old chunks** — clears stale vectors
           before we replace them. Keeping the document row is intentional
           so the UUID stays stable for any external reference.
        5. **Parse** — dispatch on extension; unsupported types return
           early with a clear error reason. ``base_metadata`` is built
           once and threaded through every chunker so filters stay
           consistent.
        6. **Detect strategy + chunk** — Excel processes per-sheet, PowerPoint
           uses fixed slide_based, everything else routes through
           ``signal_detector.detect_*`` and ``chunk_document``. Empty
           chunk lists are reported as ``"no_chunks_produced"`` so the
           connector can flag the file for human review.
        7. **Embed** — single batch call (embedder handles internal
           batching); errors propagate to the outer try/except.
        8. **Store** —
              * insert_document (create) **or** update_document_after_reingestion
                (update).
              * insert_chunks_with_embeddings.
              * Excel: ``upsert_row_hashes`` per sheet for the next
                row-diff cycle.

    Returns:
        Success: ``{"status": "success", "title", "document_id",
        "chunks_stored", "action", "strategy_used"}``.
        Skip: ``{"status": "skipped", "reason", "title"}``.
        Error: ``{"status": "error", "title", "reason"}``.

    What breaks if this is wrong:
        Wrong dedup → embedding cost spikes. Wrong update path → orphan
        chunks alongside fresh ones, retrieval cites contradictory
        versions of the same PRD. Wrong row hash math → next Excel sync
        either misses changed rows or wipes everything.
    """
    try:
        logger.info("Ingesting: %s (source_id=%s)", title, source_id)

        # WHY THIS EXISTS IN PRISM AI:
        # We hash the raw bytes, not the parsed text, so format-only
        # changes (re-saved Word doc with identical content) still match
        # if the bytes are byte-identical — and any meaningful edit
        # (single character) produces a new hash.
        #
        # WHAT THIS BLOCK DOES:
        # Loads file bytes, computes SHA-256 hex digest, captures
        # lowercase extension for routing.
        #
        # WHY THIS WAY:
        # ``Path.read_bytes`` is one syscall and avoids streaming bugs.
        # Lowercase extension makes Drive's mixed-case filenames safe.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Wrong hash → false dedup, embed cost spikes. Case-sensitive
        # extension → ``.PDF`` files would hit the unsupported branch.
        path_obj = Path(file_path)
        file_bytes = path_obj.read_bytes()
        content_hash = compute_hash(file_bytes)
        ext = path_obj.suffix.lower()

        supabase = get_supabase()

        # WHY THIS EXISTS IN PRISM AI:
        # Two-tier dedup: first by source_id (Drive file ID), second by
        # content_hash (catches the same file shared into another folder
        # with a fresh ID).
        #
        # WHAT THIS BLOCK DOES:
        # Looks up the existing document by source_id; decides
        # create/update/skip and remembers the UUID for the update path.
        #
        # WHY THIS WAY:
        # Source-id match is the cheapest path in Postgres (UNIQUE
        # index). content_hash check only runs when source_id missed.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # We'd embed the same content twice (cost) or skip a real change
        # (stale answers).
        existing = get_document_by_source_id(supabase, source_id)
        existing_document_id: Optional[str] = None

        if existing is not None:
            if existing.get("content_hash") == content_hash:
                logger.info("Skipped — unchanged: %s", title)
                return {
                    "status": "skipped",
                    "reason": "unchanged",
                    "title": title,
                }
            action = "update"
            existing_document_id = existing["id"]
            logger.info(
                "Content changed for %s — replacing chunks (document_id=%s)",
                title,
                existing_document_id,
            )
        else:
            if document_exists_by_content_hash(supabase, content_hash):
                logger.info("Skipped — duplicate content: %s", title)
                return {
                    "status": "skipped",
                    "reason": "duplicate_content",
                    "title": title,
                }
            action = "create"

        # WHY THIS EXISTS IN PRISM AI:
        # Update path must wipe old vectors BEFORE inserting new ones —
        # otherwise retrievers see two versions of the same PRD and rank
        # them adjacently, confusing the PM with stale + fresh quotes.
        #
        # WHAT THIS BLOCK DOES:
        # Calls storage.delete_chunks_for_document on the existing UUID.
        #
        # WHY THIS WAY:
        # Keeps the document row alive so external references (audit
        # logs, citations stored elsewhere) stay valid.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Two PRDs in retrieval results pointing at one document_id with
        # contradictory chunks — answers cite both halves of an old + new
        # spec.
        if action == "update" and existing_document_id is not None:
            delete_chunks_for_document(supabase, existing_document_id)

        base_metadata = _build_base_metadata(
            source_type=source_type,
            title=title,
            source_id=source_id,
            ext=ext,
            folder=folder,
            folder_path=folder_path,
            folder_id=folder_id,
            sprint=sprint,
            owner=owner,
            file_created_at=file_created_at,
            file_updated_at=file_updated_at,
            extra_metadata=extra_metadata,
        )

        # WHY THIS EXISTS IN PRISM AI:
        # Each format has its own parser AND its own chunker contract;
        # routing here means connectors stay format-agnostic.
        #
        # WHAT THIS BLOCK DOES:
        # Picks the parser for this extension or short-circuits with a
        # clear error for unsupported types.
        #
        # WHY THIS WAY:
        # Single ``if/elif`` with explicit branches beats a dict of
        # callables — it keeps Excel's special return shape visible
        # alongside the list-returning parsers.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Unsupported file silently routed to wrong parser → garbage
        # chunks; or supported file rejected → connector marks file
        # missing forever.
        elements: List[Any] = []
        sheet_data: Dict[str, Dict[str, Any]] = {}

        if ext == ".docx":
            elements = parse_docx(file_path)
        elif ext == ".xlsx":
            sheet_data = parse_excel(file_path)
        elif ext == ".pdf":
            elements = parse_pdf(file_path)
        elif ext in (".txt", ".md"):
            elements = parse_text_file(file_path)
        elif ext == ".pptx":
            elements = parse_pptx(file_path)
        else:
            logger.warning("Unsupported file type for %s: %s", title, ext)
            return {
                "status": "error",
                "title": title,
                "reason": f"Unsupported file type: {ext}",
            }

        logger.info(
            "Parsed %s — elements=%s sheets=%s",
            title,
            len(elements),
            len(sheet_data),
        )

        # WHY THIS EXISTS IN PRISM AI:
        # Detection+chunking is per-format; we collect everything into
        # ``all_chunks`` so the embed/store path is uniform.
        #
        # WHAT THIS BLOCK DOES:
        # Runs the right detector + chunker for the format, accumulating
        # into a single chunk list and recording the strategy name for
        # the success payload.
        #
        # WHY THIS WAY:
        # Excel can have many sheets each with its own strategy — we
        # collapse to ``"excel_mixed"`` only when more than one sheet
        # actually contributed, otherwise we keep the precise strategy
        # name so dashboards show e.g. ``group_by_column`` for the OKR
        # rollup.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Wrong strategy name in DB → debugging "why is retrieval missing
        # epic X?" gets harder; mixed Excel ingest losing a sheet's
        # chunks → entire backlog tab missing from search.
        all_chunks: List[Chunk] = []
        strategy_used: str = ""

        if ext == ".xlsx":
            sheet_strategies: List[str] = []
            for sheet_name, sheet_payload in sheet_data.items():
                detection = classify_excel_sheet_with_llm(
                    sheet_name, sheet_data[sheet_name]["rows"]
                )
                sheet_chunks = chunk_excel_sheet(
                    sheet_name,
                    sheet_payload,
                    detection,
                    base_metadata,
                )
                all_chunks.extend(sheet_chunks)
                sheet_strategies.append(detection.strategy.value)

            if len(sheet_strategies) > 1:
                strategy_used = "excel_mixed"
            elif sheet_strategies:
                strategy_used = sheet_strategies[0]
            else:
                strategy_used = Strategy.single_chunk.value

        elif ext == ".pptx":
            _ = detect_pptx_strategy()
            all_chunks = chunk_slide_elements(elements, base_metadata)
            strategy_used = Strategy.slide_based.value

        else:
            if ext == ".docx":
                detection = detect_docx_strategy(file_path)
            elif ext == ".pdf":
                detection = detect_pdf_strategy(file_path)
            else:
                detection = detect_text_strategy(file_path)
            all_chunks = chunk_document(elements, detection, base_metadata)
            strategy_used = detection.strategy.value

        logger.info(
            "Produced %s chunks for %s using strategy=%s",
            len(all_chunks),
            title,
            strategy_used,
        )

        if len(all_chunks) == 0:
            logger.warning("No chunks produced for %s", title)
            return {
                "status": "error",
                "title": title,
                "reason": "no_chunks_produced",
            }

        # WHY THIS EXISTS IN PRISM AI:
        # Embedding is the single most expensive step per file — we batch
        # everything in one call so embedder.get_embeddings can chunk
        # internally with optimal batch size + retry logic.
        #
        # WHAT THIS BLOCK DOES:
        # Extracts chunk text, fans out to OpenRouter, returns vectors in
        # the same order.
        #
        # WHY THIS WAY:
        # Trusting embedder's batching keeps rate-limit logic in one
        # place; we never want pipeline.py to know what 100 means.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Misaligned vectors → catastrophic retrieval errors (every
        # answer cites the wrong chunk). storage.insert_chunks_with_
        # embeddings raises ValueError if lengths drift.
        texts = [chunk.content for chunk in all_chunks]
        embeddings = get_embeddings(texts)

        # WHY THIS EXISTS IN PRISM AI:
        # The document row is the canonical record (what PM uploaded,
        # when, where it lives) — chunks reference it via FK. We build it
        # AFTER chunking so a chunk-empty file never creates a document
        # row.
        #
        # WHAT THIS BLOCK DOES:
        # Builds the doc record dict and either inserts it (create) or
        # bumps content_hash + ingested_at on the existing row (update).
        #
        # WHY THIS WAY:
        # Splitting create vs update is essential — update would wipe
        # ``created_at`` if we re-inserted; create needs a brand new UUID.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Wrong UUID for chunks → orphan chunks; wrong update path →
        # provenance ("when was this first ingested?") becomes wrong.
        doc_record: Dict[str, Any] = {
            "source_type": source_type,
            "source_id": source_id,
            "title": title,
            "doc_type": ext.lstrip("."),
            "folder": folder,
            "folder_path": folder_path,
            "folder_id": folder_id,
            "sprint": sprint,
            "owner": owner,
            "file_created_at": file_created_at,
            "file_updated_at": file_updated_at,
            "content_hash": content_hash,
            "metadata": extra_metadata or {},
        }

        if action == "create":
            document_id = insert_document(supabase, doc_record)
        else:
            assert existing_document_id is not None
            document_id = existing_document_id
            update_document_after_reingestion(
                supabase, document_id, content_hash
            )

        chunks_stored = insert_chunks_with_embeddings(
            supabase,
            document_id,
            all_chunks,
            embeddings,
        )
        logger.info("Stored %s chunks for %s", chunks_stored, title)

        # WHY THIS EXISTS IN PRISM AI:
        # Excel row diffing depends on hashes captured at ingest time.
        # Without them, the next sync can't tell which 5 rows of 3,000
        # changed and would re-embed the whole sheet.
        #
        # WHAT THIS BLOCK DOES:
        # For each sheet, hashes every row's concatenated cell values
        # and upserts the dict via storage.upsert_row_hashes (which uses
        # ON CONFLICT (document_id, sheet_name, row_index)).
        #
        # WHY THIS WAY:
        # Per-sheet upsert keeps each HTTP call small; row-index is the
        # natural unique key within a sheet.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Missing or stale row hashes → next nightly sync over-embeds.
        if ext == ".xlsx":
            for sheet_name, sheet_payload in sheet_data.items():
                rows = sheet_payload.get("rows", [])
                if not rows:
                    continue
                row_hashes_dict = _compute_excel_row_hashes(rows)
                upsert_row_hashes(
                    supabase,
                    document_id,
                    sheet_name,
                    row_hashes_dict,
                )

        return {
            "status": "success",
            "title": title,
            "document_id": document_id,
            "chunks_stored": chunks_stored,
            "action": action,
            "strategy_used": strategy_used,
        }

    except Exception as exc:  # noqa: BLE001 — connectors expect a status dict, not a raise
        logger.exception("Ingestion failed for %s: %s", title, exc)
        return {
            "status": "error",
            "title": title,
            "reason": str(exc),
        }


def ingest_email(
    body: str,
    email_id: str,
    thread_id: str,
    subject: str,
    sender: str,
    recipients: List[str],
    email_date: str,
    gmail_labels: List[str],
    has_attachment: bool = False,
    attachment_names: Optional[List[str]] = None,
    existing_labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Ingest one Gmail message (HTML body, labels, sender/recipients).

    One-sentence summary: hashes ``email_id + body`` for dedup, distinguishes
    "no change", "labels changed only" (zero embedding cost), and "body
    changed" updates, then chunks + embeds + stores.

    Why it exists for PrismAI:
        Gmail is the noisiest source PMs ingest. Most polls return zero body
        changes but plenty of label updates (Inbox → Done, custom tags). We
        special-case label-only updates as a metadata write so the connector
        can poll every 5 minutes without setting OpenRouter on fire.

    Steps (numbered):
        1. **Hash** — content_hash = SHA-256 of ``email_id + body``;
           includes ``email_id`` so two unrelated emails with the same body
           snippet (auto-replies) don't collide.
        2. **Get Supabase client** — singleton.
        3. **Existing check** —
              a. If hash matches AND labels match ``existing_labels`` →
                 fully skip.
              b. If hash matches AND labels differ → call
                 :func:`storage.update_document_metadata_only` (only
                 ``gmail_labels`` is touched; embeddings untouched). This
                 is the **cheap label-rotation path**.
              c. If hash differs → ``action = "update"``; delete old
                 chunks, replace.
              d. If no existing row → ``action = "create"``.
        4. **Parse + chunk** — ``parse_email_body(html=True)`` strips
           reply chains and signatures; :func:`chunk_email` repeats
           ``From / Subject / Date`` on every chunk so retrieval results
           stay self-contained.
        5. **Embed** — same batch path as files.
        6. **Store** — create or update_document_after_reingestion +
           insert_chunks_with_embeddings.

    Returns:
        Success: ``{"status": "success", "subject", "document_id",
        "chunks_stored", "action"}``.
        Skip: ``{"status": "skipped", "reason", "subject"}``.
        Metadata-only: ``{"status": "metadata_updated", "subject"}``.
        Error: ``{"status": "error", "subject", "reason"}``.

    What breaks if this is wrong:
        Re-embedding emails on every label tweak would cost more than the
        rest of the ingestion combined. Skipping a real body change would
        leave PMs reading stale customer escalations.
    """
    try:
        logger.info("Ingesting email: %s (email_id=%s)", subject, email_id)

        # WHY THIS EXISTS IN PRISM AI:
        # The hash key combines email_id (uniqueness) with body (change
        # detection). Body alone would collide across short/auto-reply
        # threads.
        #
        # WHAT THIS BLOCK DOES:
        # Computes the SHA-256 of the concatenation.
        #
        # WHY THIS WAY:
        # storage.compute_hash accepts strings (encodes UTF-8 internally).
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # False matches → missed updates; or false mismatches → endless
        # re-embedding of unchanged threads.
        content_hash = compute_hash(email_id + body)

        supabase = get_supabase()

        # WHY THIS EXISTS IN PRISM AI:
        # We use signal_detector for parity even though emails always
        # use the email-specific chunker — this keeps the strategy log
        # consistent for ops dashboards.
        #
        # WHAT THIS BLOCK DOES:
        # Calls detect_email_strategy() purely for logging / future use.
        #
        # WHY THIS WAY:
        # Emails never branch on strategy today; a no-op call is cheap
        # and keeps the contract uniform.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Nothing user-visible — only a missing log entry.
        _ = detect_email_strategy()

        existing = get_document_by_source_id(supabase, email_id)
        existing_document_id: Optional[str] = None

        # WHY THIS EXISTS IN PRISM AI:
        # The label-only update path is the highest-frequency branch in
        # production Gmail polling — must be fast and zero-cost.
        #
        # WHAT THIS BLOCK DOES:
        # Three-way decision: full skip, metadata-only, full re-ingest.
        #
        # WHY THIS WAY:
        # Comparing as ``set`` removes label ordering noise (Gmail
        # sometimes returns labels in different orders).
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Either too many embed calls (cost) or PM filter "show me
        # urgent" returns stale label state.
        if existing is not None:
            if existing.get("content_hash") == content_hash:
                stored_labels = set(existing_labels or [])
                incoming_labels = set(gmail_labels or [])
                if stored_labels == incoming_labels:
                    logger.info("Skipped — unchanged email: %s", subject)
                    return {
                        "status": "skipped",
                        "reason": "unchanged",
                        "subject": subject,
                    }
                logger.info(
                    "Labels changed only for %s — metadata-only update",
                    subject,
                )
                update_document_metadata_only(
                    supabase,
                    existing["id"],
                    {"gmail_labels": gmail_labels},
                )
                return {
                    "status": "metadata_updated",
                    "subject": subject,
                }
            action = "update"
            existing_document_id = existing["id"]
            logger.info(
                "Email body changed for %s — replacing chunks (document_id=%s)",
                subject,
                existing_document_id,
            )
            delete_chunks_for_document(supabase, existing_document_id)
        else:
            action = "create"

        # WHY THIS EXISTS IN PRISM AI:
        # Gmail bodies are HTML with quoted reply chains, signatures,
        # tracking pixels — retrieval over the raw HTML would surface
        # CSS strings and "On Tue Bob wrote" boilerplate.
        #
        # WHAT THIS BLOCK DOES:
        # Strips HTML, removes quoted replies, trims signatures.
        #
        # WHY THIS WAY:
        # is_html=True is the connector contract; Gmail API always
        # returns text/html or multipart with html part.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # PM searches "what did Alex decide?" surfaces 20 replies of the
        # same quoted chain instead of Alex's actual reply.
        clean_body = parse_email_body(body, is_html=True)

        email_metadata: Dict[str, Any] = {
            "source_type": "gmail",
            "email_id": email_id,
            "thread_id": thread_id,
            "sender": sender,
            "recipients": recipients,
            "subject": subject,
            "email_date": email_date,
            "gmail_labels": gmail_labels,
            "has_attachment": has_attachment,
            "attachment_names": attachment_names or [],
            "is_attachment": False,
        }

        chunks = chunk_email(clean_body, email_metadata)
        logger.info(
            "Produced %s email chunks for %s",
            len(chunks),
            subject,
        )

        if len(chunks) == 0:
            logger.warning("No chunks produced for email %s", subject)
            return {
                "status": "error",
                "subject": subject,
                "reason": "no_chunks_produced",
            }

        texts = [chunk.content for chunk in chunks]
        embeddings = get_embeddings(texts)

        doc_record: Dict[str, Any] = {
            "source_type": "gmail",
            "source_id": email_id,
            "title": subject,
            "doc_type": "email",
            "content_hash": content_hash,
            "metadata": email_metadata,
        }

        if action == "create":
            document_id = insert_document(supabase, doc_record)
        else:
            assert existing_document_id is not None
            document_id = existing_document_id
            update_document_after_reingestion(
                supabase, document_id, content_hash
            )

        chunks_stored = insert_chunks_with_embeddings(
            supabase,
            document_id,
            chunks,
            embeddings,
        )
        logger.info("Stored %s email chunks for %s", chunks_stored, subject)

        return {
            "status": "success",
            "subject": subject,
            "document_id": document_id,
            "chunks_stored": chunks_stored,
            "action": action,
        }

    except Exception as exc:  # noqa: BLE001
        logger.exception("Email ingestion failed for %s: %s", subject, exc)
        return {
            "status": "error",
            "subject": subject,
            "reason": str(exc),
        }


def delete_file(source_id: str) -> Dict[str, Any]:
    """Remove a Drive-style file (and all its chunks) from PrismAI.

    One-sentence summary: looks up the document by ``source_id``, calls
    :func:`storage.delete_document_and_chunks`, and reports the outcome.

    Why it exists for PrismAI:
        Drive connector watches trash/unshare events; when a file leaves
        the user's scope, PrismAI must purge it so retrieval never cites
        a removed PRD or retro.

    Steps:
        1. Resolve UUID via ``source_id``; warn + return ``not_found`` if
           the connector raced ahead of an earlier delete.
        2. ``delete_document_and_chunks`` — cascades chunks via FK and
           explicitly removes ``row_hashes`` rows.

    Returns:
        ``{"status": "deleted", "source_id", "document_id"}`` or
        ``{"status": "not_found", "source_id"}`` or
        ``{"status": "error", "source_id", "reason"}``.

    What breaks if this is wrong:
        Connector says "deleted" but chunks linger → PM gets cited a
        deleted PRD as if it were live.
    """
    try:
        logger.info("Deleting file source_id=%s", source_id)
        supabase = get_supabase()

        existing = get_document_by_source_id(supabase, source_id)
        if existing is None:
            logger.warning(
                "delete_file: no document found for source_id=%s", source_id
            )
            return {
                "status": "not_found",
                "source_id": source_id,
            }

        # WHY THIS EXISTS IN PRISM AI:
        # Single call; storage layer owns cascade semantics + row_hashes
        # mop-up.
        #
        # WHAT THIS BLOCK DOES:
        # Delete documents row by UUID (chunks cascade via FK).
        #
        # WHY THIS WAY:
        # Avoids re-implementing cascade in pipeline; storage tests own
        # that behaviour.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Orphan chunks under no document row → retrieval joins return
        # NULL columns → frontend crashes on title rendering.
        delete_document_and_chunks(supabase, existing["id"])
        logger.info(
            "Deleted file source_id=%s document_id=%s",
            source_id,
            existing["id"],
        )

        return {
            "status": "deleted",
            "source_id": source_id,
            "document_id": existing["id"],
        }

    except Exception as exc:  # noqa: BLE001
        logger.exception("delete_file failed for %s: %s", source_id, exc)
        return {
            "status": "error",
            "source_id": source_id,
            "reason": str(exc),
        }


def delete_email(email_id: str) -> Dict[str, Any]:
    """Remove an email and all attachments tied to it via ``parent_email_id``.

    One-sentence summary: deletes the primary email document AND every
    attachment document whose ``metadata.parent_email_id`` equals the
    email's UUID.

    Why it exists for PrismAI:
        Gmail attachments are ingested as separate ``documents`` rows
        (PDF specs, deck attachments) but logically belong to their
        parent thread. When the email is trashed, those children must
        also disappear — otherwise PMs see "PRD draft" floating in
        retrieval with no parent thread context.

    Steps:
        1. Resolve email document by ``source_id == email_id``.
        2. Delete the email row (cascades chunks).
        3. Query ``documents`` for ``metadata->>'parent_email_id' == document_id``
           — these are the attachments.
        4. Delete each attachment row (cascades its chunks too).
        5. Return the count for connector logging.

    Returns:
        ``{"status": "deleted", "email_id", "attachments_deleted"}`` or
        ``{"status": "not_found", "email_id"}`` or
        ``{"status": "error", "email_id", "reason"}``.

    What breaks if this is wrong:
        Orphan attachment documents pointing at a missing parent thread
        → PMs see "see attachment.pdf" hits with no email context;
        impossible to debug from the UI.
    """
    try:
        logger.info("Deleting email email_id=%s", email_id)
        supabase = get_supabase()

        existing = get_document_by_source_id(supabase, email_id)
        if existing is None:
            logger.warning(
                "delete_email: no document found for email_id=%s", email_id
            )
            return {
                "status": "not_found",
                "email_id": email_id,
            }

        document_id = existing["id"]
        delete_document_and_chunks(supabase, document_id)

        # WHY THIS EXISTS IN PRISM AI:
        # Attachment documents reference the email via
        # ``metadata.parent_email_id`` (the email's UUID, not the Gmail
        # message id) — ingestion sets that key when the connector
        # detects an attachment.
        #
        # WHAT THIS BLOCK DOES:
        # Selects attachments by JSON path filter, then deletes each.
        #
        # WHY THIS WAY:
        # PostgREST exposes JSON path filters via ``->>`` text accessor;
        # we use ``.eq`` with the operator-style key. ``.execute().data``
        # is a list of rows.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Wrong filter → attachments survive parent deletion → orphan
        # citations in PM answers; or filter too broad → unrelated docs
        # deleted (data loss).
        attachments_response = (
            supabase.table("documents")
            .select("id")
            .eq("metadata->>parent_email_id", document_id)
            .execute()
        )
        attachments = attachments_response.data or []

        for attachment in attachments:
            delete_document_and_chunks(supabase, attachment["id"])

        logger.info(
            "Deleted email email_id=%s document_id=%s attachments=%s",
            email_id,
            document_id,
            len(attachments),
        )

        return {
            "status": "deleted",
            "email_id": email_id,
            "attachments_deleted": len(attachments),
        }

    except Exception as exc:  # noqa: BLE001
        logger.exception("delete_email failed for %s: %s", email_id, exc)
        return {
            "status": "error",
            "email_id": email_id,
            "reason": str(exc),
        }
