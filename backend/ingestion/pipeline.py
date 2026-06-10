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

import asyncio
import hashlib  # noqa: F401  (kept per spec; storage.compute_hash is the canonical hasher)
import json
import logging
import re
import os  # noqa: F401  (kept per spec; ``load_dotenv`` populates os.environ)
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

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


def _derive_doc_type(title: str, ext: str) -> str:
    """Infer a stable ``doc_type`` label from the file title and extension.

    One-sentence summary: maps Drive filenames + extensions to the vocabulary
    PrismAI uses in Supabase filters (``jira``, ``retro``, ``prd``, etc.) so
    agents can scope retrieval without parsing paths at query time.

    Why it exists for PrismAI:
        Connectors pass a raw title and extension; chunk rows need a normalized
        ``doc_type`` column for PM filters ("show me all retros", "only Jira
        exports"). Filename heuristics match how Nutrivana names artefacts
        (``Sprint_10_Jira.xlsx``, ``Q2_OKR.docx``) without an LLM on every file.

    Returns:
        A short string tag stored on document/chunk rows (never ``None``).

    What breaks if this is wrong:
        Wrong tag → filter queries return empty sets or mix unrelated formats
        (e.g. treating a PRD as a generic ``document``).
    """
    title_lower = title.lower()

    # WHY THIS EXISTS IN PRISM AI:
    # Excel workbooks are the most heterogeneous format — Jira dumps, OKR
    # rollups, and retros all share ``.xlsx`` but need different retrieval
    # behaviour and UI labels.
    #
    # WHAT THIS BLOCK DOES:
    # Substrings in the lowercase title pick a specialised doc_type; otherwise
    # we fall back to ``spreadsheet``.
    #
    # WHY THIS WAY:
    # Title keywords are how PMs actually name files in Drive; extension alone
    # cannot distinguish Jira from OKR sheets.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # A Jira export labelled ``spreadsheet`` → sprint/ticket filters miss it.
    if ext == ".xlsx":
        if "jira" in title_lower:
            return "jira"
        if "retro" in title_lower:
            return "retro"
        if "okr" in title_lower:
            return "okr"
        if "roadmap" in title_lower:
            return "roadmap"
        return "spreadsheet"

    # WHY THIS EXISTS IN PRISM AI:
    # Word docs carry planning specs, meeting notes, and PRDs — all ``.docx``
    # but different PM question patterns at retrieval time.
    #
    # WHAT THIS BLOCK DOES:
    # Title keyword routing for Word; default ``document`` for generic docs.
    #
    # WHY THIS WAY:
    # ``meeting`` and ``sync`` both catch "Weekly Sync" and "Sprint 8 Meeting".
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # PRDs stored as ``document`` → "show PRDs only" filters exclude real PRDs.
    if ext == ".docx":
        if "planning" in title_lower:
            return "planning"
        if "meeting" in title_lower or "sync" in title_lower:
            return "meeting_notes"
        if "spec" in title_lower or "technical" in title_lower:
            return "technical_spec"
        if "prd" in title_lower:
            return "prd"
        return "document"

    # WHY THIS EXISTS IN PRISM AI:
    # Scanned/exported PDFs are a distinct artefact class (page-based chunking,
    # no Word structure). Single extension → single type keeps routing simple.
    if ext == ".pdf":
        return "pdf"

    # WHY THIS EXISTS IN PRISM AI:
    # Plain text and markdown exports (release notes, ADRs) share one chunker
    # path; one label avoids duplicating logic for ``.txt`` vs ``.md``.
    if ext in (".txt", ".md"):
        return "markdown"

    # WHY THIS EXISTS IN PRISM AI:
    # Decks use slide-based chunking; ``presentation`` signals that to filters
    # and ranking without inspecting chunk metadata.
    if ext == ".pptx":
        return "presentation"

    # WHY THIS EXISTS IN PRISM AI:
    # Unknown extensions still need a non-null doc_type for NOT NULL columns
    # and consistent filter UX.
    return "document"


def _derive_quarter(sprint: Optional[str]) -> Optional[str]:
    """Map a Nutrivana sprint number to a calendar quarter label.

    One-sentence summary: converts sprint ``"1"``–``"13"`` into ``Q1``–``Q4``
    using the fixed sprint calendar baked into the Nutrivana dataset.

    Why it exists for PrismAI:
        Many files lack explicit quarter metadata from Drive. Sprint number is
        the reliable join key PMs already use ("Sprint 8 retro"). Denormalising
        quarter onto chunks lets agents filter ``WHERE quarter = 'Q2'`` without
        joining a sprint calendar table at query time.

    Returns:
        ``"Q1"``, ``"Q2"``, ``"Q3"``, ``"Q4"``, or ``None`` when sprint is
        missing or not in the 1–13 range.

    What breaks if this is wrong:
        Wrong quarter → cross-quarter retrieval (Q1 OKR text answering a Q2
        question). ``None`` when sprint was valid → quarter filter returns
        nothing for otherwise good content.
    """
    # WHY THIS EXISTS IN PRISM AI:
    # Gmail and some Drive paths only discover sprint late; empty string and
    # None must both mean "unknown quarter" not a bogus Q label.
    #
    # WHAT THIS BLOCK DOES:
    # Early exit when sprint is falsy.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Treating ``""`` as sprint 0 → wrong quarter or conversion errors.
    if not sprint:
        return None

    # WHY THIS EXISTS IN PRISM AI:
    # Sprint is stored as TEXT in Supabase; connectors may pass ``"08"`` or
    # non-numeric junk from folder names — we must not crash ingestion.
    #
    # WHAT THIS BLOCK DOES:
    # Parses sprint to integer; returns None on failure.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Uncaught ValueError → entire file ingest fails for one bad folder tag.
    try:
        sprint_num = int(sprint)
    except (ValueError, TypeError):
        return None

    # WHY THIS EXISTS IN PRISM AI:
    # Nutrivana runs 13 sprints across four quarters (3+3+3+4). This mapping
    # is dataset-specific but stable for V1 demos and evals.
    #
    # WHAT THIS BLOCK DOES:
    # Bucket sprint_num into Q1–Q4 by inclusive ranges.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Off-by-one at boundaries (e.g. sprint 3 vs 4) mis-tags an entire quarter
    # of artefacts.
    if 1 <= sprint_num <= 3:
        return "Q1"
    if 4 <= sprint_num <= 6:
        return "Q2"
    if 7 <= sprint_num <= 9:
        return "Q3"
    if 10 <= sprint_num <= 13:
        return "Q4"
    return None


def _derive_quarter_from_sheet(sheet_name: str) -> Optional[str]:
    """Derive quarter from sheet name if it starts with Q1, Q2, Q3 or Q4."""
    if not sheet_name:
        return None
    name = sheet_name.strip().upper()
    if name.startswith("Q1"):
        return "Q1"
    elif name.startswith("Q2"):
        return "Q2"
    elif name.startswith("Q3"):
        return "Q3"
    elif name.startswith("Q4"):
        return "Q4"
    return None


# Nutrivana sprint → approximate start date (ISO). Used when Drive omits
# created_at but the connector knows sprint from folder path or filename.
_SPRINT_START_DATES: Dict[str, str] = {
    "1": "2025-01-01",
    "2": "2025-01-15",
    "3": "2025-01-29",
    "4": "2025-02-12",
    "5": "2025-02-26",
    "6": "2025-03-12",
    "7": "2025-03-26",
    "8": "2025-04-09",
    "9": "2025-04-23",
    "10": "2025-05-07",
    "11": "2025-05-21",
    "12": "2025-06-04",
    "13": "2025-06-18",
}


def _derive_file_date(
    sprint: Optional[str],
    file_created_at: Optional[str],
) -> Optional[str]:
    """Resolve ``file_created_at`` from Drive metadata or sprint calendar.

    One-sentence summary: returns the connector-supplied timestamp when present;
    otherwise looks up a synthetic start date from the Nutrivana sprint map.

    Why it exists for PrismAI:
        Sorting and "what changed this sprint?" UX need a date on every chunk row.
        Drive sometimes omits ``createdTime`` on shared shortcuts; sprint inferred
        from folder path is still trustworthy enough for V1 ordering and filters.

    Returns:
        An ISO date string, or ``None`` when neither Drive nor sprint can
        supply a date.

    What breaks if this is wrong:
        Synthetic dates on wrong sprint → timeline answers cite files as if they
        were written weeks earlier/later than reality.
    """
    # WHY THIS EXISTS IN PRISM AI:
    # Real Drive timestamps are authoritative when the connector has them —
    # never overwrite with synthetic sprint dates.
    #
    # WHAT THIS BLOCK DOES:
    # Passes through non-None ``file_created_at`` unchanged.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Overwriting real dates → provenance and "recently updated" sorts lie.
    if file_created_at is not None:
        return file_created_at

    # WHY THIS EXISTS IN PRISM AI:
    # Without sprint we have no fallback in the Nutrivana calendar table.
    if sprint is None:
        return None

    # WHY THIS EXISTS IN PRISM AI:
    # Sprint keys are strings to match TEXT sprint columns and regex extractors
    # that return ``"8"`` not ``8``.
    #
    # WHAT THIS BLOCK DOES:
    # Looks up sprint in ``_SPRINT_START_DATES``; unknown sprints → None.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Missing key for sprint 8 → chunks store NULL dates despite known sprint.
    return _SPRINT_START_DATES.get(str(sprint))


_EMPTY_CHUNK_METADATA: Dict[str, List[str]] = {
    "people": [],
    "ticket_ids": [],
}

_VALID_TICKET_PATTERN = re.compile(
    r"^(TECH|GOAL|NUTR|CF|AN|BUG|MON|RES|RET|ONBD|PRE|MET|NPS|MKT|FUN|V2|INVEST|"
    r"GOAL-BUG|NUTR-BUG|AN-BUG|CF-BUG|AN-CR|GOAL-SPIKE|NUTR-TASK|NUTR-EPIC|GOAL-EPIC|CF-EPIC)"
    r"-\d+(-COMPLETE)?$"
)


def extract_chunk_metadata(content: str, feature_catalog: list[str], doc_type: str | None = None) -> dict:
    """Extract people, tickets, features, and metrics from one chunk via LLM.

    WHAT THIS FUNCTION DOES FOR PRISM AI:
        After chunking, each ``document_chunks`` row can carry denormalised
        ``people``, ``ticket_ids``, ``features``, and ``metrics`` columns for
        fast filters ("what did Arjun ship?", "chunks mentioning TECH-001",
        "OKR metrics for Bar Graph"). This function calls gpt-4.1-nano on
        OpenRouter to read one chunk plus the canonical feature catalog and
        return those four lists without blocking ingest on failure.

    WHY WE EXTRACT THESE FOUR FIELDS:
        - people: PM questions are often person-centric ("what did Arjun say
          about RLS?"); first-name tags match how the team refers to each other.
        - ticket_ids: Jira-style IDs are the join key between email, docs, and
          sheets; indexed ticket columns power "everything about GOAL-BUG-005".
        - features: Canonical product names from the catalog link chunks across
          formats (PRD, retro, Jira) when wording differs.
        - metrics: Retention, MAU, NPS, etc. let agents answer metric questions
          without regex over arbitrary percentages in body text.

    WHY WE NEED THE FEATURE CATALOG:
        Feature names in docs are inconsistent ("goal snapshots" vs "Goal
        Snapshots", ticket aliases). The catalog is the single source of truth;
        the model must return only canonical strings present in that list (max
        three per chunk) so filters and dashboards stay stable.

    WHAT HAPPENS IF EXTRACTION FAILS:
        Any API, parse, or schema error logs once and returns four empty lists so
        ingest continues; chunks still store content and embeddings, only the
        enrichment columns are blank until re-ingest.
    """
    logger = logging.getLogger(__name__)

    def _fix1_ticket_id_regex(chunk_content: str, merged: Dict[str, List[str]]) -> None:
        """Fix 1 — Ticket ID regex: scan content and add missing ticket IDs."""
        ticket_pattern = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b", re.IGNORECASE)
        excluded_tokens = {
            "WAITLIST", "USDA", "PRD", "MVP", "IST", "EER", "JWT",
            "V1", "V2", "V3", "Q1", "Q2", "Q3", "Q4", "P0", "P1", "P2", "P3",
            "API", "RLS", "DB", "UI", "UX", "RDA", "MAU", "NPS", "FAQ", "OKR", "KR",
        }
        existing = {ticket.upper() for ticket in merged.get("ticket_ids", [])}
        for match in ticket_pattern.finditer(chunk_content):
            ticket_id = match.group(0).upper()
            if ticket_id in excluded_tokens or ticket_id in existing:
                continue
            merged.setdefault("ticket_ids", []).append(ticket_id)
            existing.add(ticket_id)

    word_count = len(content.split())
    if word_count < 20:
        short_result = dict(_EMPTY_CHUNK_METADATA)
        _fix1_ticket_id_regex(content, short_result)
        return short_result

    try:
        # WHY THIS EXISTS IN PRISM AI:
        # Short chunks (headings, "Action Items" alone) waste LLM calls and invite
        # hallucinated tickets/features. The prompt adds three feature-matching
        # methods (ticket alias, topic, when-in-doubt) plus explicit anti-hallucination
        # rules; regex ticket validation is a second guard after parse.
        #
        # WHAT THIS BLOCK DOES:
        # Builds the v2 extractor prompt with catalog, chunk text, METHOD 1–3
        # feature rules, and CRITICAL literal-only extraction guardrails.
        #
        # WHY THIS WAY:
        # Ticket→feature examples in the prompt teach alias matching without a second
        # DB join; topic examples cover chunks that mention features without ticket IDs.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Vague prompt → WAITLIST/USDA tagged as tickets; invented features break
        # ``WHERE features @> …`` filters; missing METHOD 2 → topic-only chunks get [].
        prompt_1 = f"""## TASK
Extract two types of metadata from a product document chunk for PrismAI — a PM assistant tool for Nutrivana, an Indian nutrition tracking app.

## CONTEXT
Chunks come from sprint planning docs, meeting notes, Jira tickets, retrospectives, OKR documents, and internal emails written by the Nutrivana team between January 2025 and June 2025.

## RULES

### 1. people

#### EXTRACT IF
Only extract if the person is actively and directly involved in this specific chunk:
- Assignee of a ticket
- Author of a comment or email
- Decision maker ("Shristi decided...", "Shristi approved...")
- Action item owner (person assigned a task with a due date)
- Person who raised, flagged, or proposed something
- Owner of an outcome or result in review or narrative text — this includes any person whose name appears in a possessive or active pattern: "X's work resulted in...", "X reduced...", "X built...", "X drove..." — extract that person
- Owner listed in an Owner column in OKR initiative rows

#### DO NOT EXTRACT IF
DO NOT extract if:
- The chunk only contains a list of attendees at the top of a document — attendees are passively listed, return []
- The person is only mentioned in passing ("similar to what Kabir said", "a suggestion from Kabir")
- The person is referenced but not actively doing anything in this chunk
- The person only has a role or title next to their name with no described action

Only return names from this exact whitelist: Shristi, Arjun, Priya, Kabir, Ananya, Ravi.
Use first name only. No duplicates.
Return [] if no one from the list is actively involved.

### 2. ticket_ids
Scan every single word in the FULL chunk text for ticket ID patterns.
A ticket ID follows this pattern: one or more uppercase word segments separated by hyphens, ending in one or more digits.
Examples of FORMAT only — there are many more: `TECH-001`, `NUTR-007`, `AN-CR-001`, GOAL-BUG-002, CF-BUG-003, NUTR-TASK-001, GOAL-003, CF-007.

#### EXTRACT IF
Extract ALL codes matching this pattern found ANYWHERE in the text including:
- Primary ticket column
- Comment text body
- Notes columns in tables
- Narrative and decision text
- Any referenced ticket like "the fix from NUTR-026" or "dependency from GOAL-003"
- Short one-line rows where the ticket ID appears as the header field value — always extract it

#### DO NOT EXTRACT IF
DO NOT extract these common words even if they match the pattern:
WAITLIST, USDA, PRD, MVP, IST, EER, JWT, V1, V2, V3, Q1, Q2, Q3, Q4, P0, P1, P2, P3, API, RLS, DB, UI, UX, RDA, MAU, NPS, FAQ, OKR, KR

NEVER invent ticket IDs — sprint numbers like "Sprint 8" are NOT ticket IDs. Dates, version numbers, and section labels are NOT ticket IDs. Section labels appearing in a Ticket ID column such as "Overall delivery rate" are NOT ticket IDs.
Return [] only if truly no ticket ID pattern exists anywhere in the chunk.

## CRITICAL RULES FOR ALL FIELDS
- Extract ONLY what is literally present in the chunk text
- DO NOT infer or invent anything not explicitly in the text
- If the chunk is very short (under 20 words) and contains no meaningful content — return [] for all fields

## CHUNK TEXT
{content}

## FORMAT
Return ONLY a valid JSON object with exactly these two keys: people, ticket_ids.
```json
{{
  "people": [],
  "ticket_ids": []
}}
```
Each value is a list of strings. Empty list if nothing found.
No explanation. No preamble. No markdown fences. Only the JSON object."""

        # WHY THIS EXISTS IN PRISM AI:
        # OpenRouter uses the same env vars as embedder and signal_detector so ops
        # only configure OPENAI_API_KEY and OPENAI_BASE_URL once per worker.
        #
        # WHAT THIS BLOCK DOES:
        # POST chat/completions with gpt-4.1-nano, temperature 0, chunk prompt.
        #
        # WHY THIS WAY:
        # Mirrors classify_excel_sheet_with_llm headers and httpx timeout for
        # consistent routing and failure modes across ingestion LLM calls.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Missing API key → every chunk gets empty metadata; wrong model → drift in
        # extracted ticket IDs and feature names.
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ShristiiS/PrismAI",
            "X-Title": "PrismAI",
        }
        payload_base = {
            "model": "gpt-4.1",
            "max_completion_tokens": 1000,
            "temperature": 0,
        }

        def _parse_llm_keys(response: httpx.Response, keys: tuple[str, ...]) -> Dict[str, List[str]]:
            response.raise_for_status()
            response_data = response.json()
            raw_content = response_data["choices"][0]["message"]["content"]
            if not isinstance(raw_content, str):
                raise ValueError("LLM response content is not a string")

            cleaned_content = raw_content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            elif cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()

            parsed = json.loads(cleaned_content)
            out: Dict[str, List[str]] = {}
            for key in keys:
                value = parsed.get(key, [])
                if not isinstance(value, list):
                    value = []
                out[key] = [str(item) for item in value]
            return out

        response_1 = httpx.post(
            url,
            headers=headers,
            json={**payload_base, "messages": [{"role": "user", "content": prompt_1}]},
            timeout=60.0,
        )
        parsed_1 = _parse_llm_keys(response_1, ("people", "ticket_ids"))
        result: Dict[str, List[str]] = dict(parsed_1)

        # Fix 1 — Ticket ID regex
        _fix1_ticket_id_regex(content, result)

        # Validate ticket_ids — regex filter, case insensitive
        valid_ticket_pattern = re.compile(
            r"^(TECH|GOAL|NUTR|CF|AN|BUG|MON|RES|RET|ONBD|PRE|MET|NPS|MKT|FUN|V2|INVEST|"
            r"GOAL-BUG|NUTR-BUG|AN-BUG|CF-BUG|AN-CR|GOAL-SPIKE|NUTR-TASK|NUTR-EPIC|GOAL-EPIC|CF-EPIC)"
            r"-\d+(-COMPLETE)?$"
        )
        result["ticket_ids"] = [
            t
            for t in result.get("ticket_ids", [])
            if isinstance(t, str) and valid_ticket_pattern.match(t.upper())
        ]

        # Validate people — normalize casing, only keep known 6 team members
        valid_people = {"arjun", "shristi", "priya", "kabir", "ananya", "ravi"}
        result["people"] = [
            p.capitalize() for p in result.get("people", [])
            if isinstance(p, str) and p.lower() in valid_people
        ]
        return result

    except Exception as exc:
        # WHY THIS EXISTS IN PRISM AI:
        # Metadata enrichment must never abort a 3,000-chunk ingest because one
        # OpenRouter call timed out or returned malformed JSON.
        #
        # WHAT THIS BLOCK DOES:
        # Logs the failure and returns four empty lists (ingest continues).
        #
        # WHY THIS WAY:
        # Fail-open on enrichment matches Excel LLM fallback philosophy — content
        # and embeddings are more critical than optional filter columns.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Re-raising here → partial documents in Supabase with no chunks; PMs see
        # missing files until manual re-run.
        logger.error(
            "extract_chunk_metadata failed: %s",
            exc,
            exc_info=True,
        )
        return dict(_EMPTY_CHUNK_METADATA)


async def generate_questions(chunk_text: str) -> list[str]:
    """Generate 0–10 PM search questions that this chunk fully answers."""
    logger = logging.getLogger(__name__)

    system_prompt = f"""## Role

You are building a search index for PrismAI, a Product Manager assistant for a mobile nutrition tracking app called Nutrivana.

## Task

Read the document chunk below carefully.

Generate between **0 and 10** specific questions that a Product Manager would realistically search for where this chunk is the **direct and complete answer**.

Read the content first and decide what questions this chunk can actually and fully answer.

## When to return empty

If the chunk contains no meaningful information a PM would search for — for example it is just a section header or empty — return an empty list.

## Rules

- Read the **ENTIRE** chunk from start to finish before generating any questions. Do not stop after covering a few facts.
- Every distinct fact, number, decision, person, date, and action item that a PM would realistically search for must have at least one question. Cover all of them before stopping.
- Even if the chunk is very short, if it contains any specific searchable fact — a name, a number, a date, a decision — generate at least one question for it.
- Do **not** generate vague or generic questions like `What happened in Sprint 13?` or `What is this about?`
- Every question must be specific enough that **this chunk and only this chunk** answers it.
- For chunks containing tables or lists where each row is a distinct item, generate at least one specific question per row.
- Do **not** summarise multiple rows into one broad question.
- Never assume or infer a sprint number, sprint name, or any specific sprint reference that is **not** explicitly written in the chunk text. If the chunk does not mention a sprint number, refer to it as `this sprint` — do **not** insert a specific sprint number like `Sprint 13` or `Sprint 8`.
- When a chunk contains specific facts, numbers, names, dates, or criteria — your questions must reference those specific details directly. Do **not** ask generic category questions. A question whose answer is a specific fact in the chunk is always better than a broad question that could match many chunks.

## Output format

Return **only** a JSON array of question strings.

- No explanation
- No numbering
- No markdown fences
- Just the JSON array

## Examples

### Correct output

```json
["What were the A/B test results for simplified onboarding?", "Why did the team decide to remove EER onboarding?"]
```

### Empty chunk

```json
[]
```

## Chunk text

{chunk_text}"""

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ShristiiS/PrismAI",
            "X-Title": "PrismAI",
        }
        payload = {
            "model": "gpt-4.1-mini",
            "max_completion_tokens": 32768,
            "temperature": 0,
            "messages": [{"role": "system", "content": system_prompt}],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        raw_content = response.json()["choices"][0]["message"]["content"]
        if not isinstance(raw_content, str):
            raise ValueError("LLM response content is not a string")

        cleaned_content = raw_content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
        cleaned_content = cleaned_content.strip()

        parsed = json.loads(cleaned_content)
        if not isinstance(parsed, list):
            return []
        return [str(item) for item in parsed if isinstance(item, str)]

    except Exception as exc:
        logger.error(
            "generate_questions failed: %s",
            exc,
            exc_info=True,
        )
        return []


async def _store_questions_for_chunk(
    supabase: Any,
    chunk_id: str,
    chunk_content: str,
) -> int:
    """Generate, embed, and persist PM search questions for one chunk row."""
    questions = await generate_questions(chunk_content)
    if not questions:
        return 0

    embeddings = get_embeddings(questions)
    if len(embeddings) != len(questions):
        raise ValueError(
            f"Embedding count {len(embeddings)} != question count {len(questions)}"
        )

    records = [
        {
            "chunk_id": chunk_id,
            "question": question,
            "question_embedding": embedding,
            "question_index": index,
        }
        for index, (question, embedding) in enumerate(zip(questions, embeddings))
    ]
    supabase.table("chunk_questions").insert(records).execute()
    return len(records)


async def _store_questions_for_inserted_chunks_async(
    supabase: Any,
    inserted_chunks: List[Dict[str, Any]],
) -> None:
    for row in inserted_chunks:
        chunk_id = row.get("id")
        chunk_content = row.get("content")
        if not chunk_id or not chunk_content:
            continue
        try:
            stored = await _store_questions_for_chunk(supabase, chunk_id, chunk_content)
            if stored:
                logger.info(
                    "Stored %s questions for chunk_id=%s",
                    stored,
                    chunk_id,
                )
        except Exception as exc:
            logger.error(
                "Question generation or storage failed for chunk_id=%s: %s",
                chunk_id,
                exc,
                exc_info=True,
            )


def store_questions_for_inserted_chunks(
    supabase: Any,
    inserted_chunks: List[Dict[str, Any]],
) -> None:
    """Generate and store PM search questions for newly inserted document chunks."""
    if not inserted_chunks:
        return
    asyncio.run(_store_questions_for_inserted_chunks_async(supabase, inserted_chunks))


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
        7. **Enrich chunk metadata** — load the Supabase feature catalog once,
           then :func:`extract_chunk_metadata` per chunk (people, ticket_ids,
           features, metrics) via LLM before embeddings are generated.
        8. **Embed** — single batch call (embedder handles internal
           batching); errors propagate to the outer try/except.
        9. **Store** —
              * insert_document (create) **or** update_document_after_reingestion
                (update).
              * insert_chunks_with_embeddings.
              * Excel: ``upsert_row_hashes`` per sheet for the next
                row-diff cycle.

    Chunk metadata (``base_metadata``):
        Denormalised fields copied onto every chunk for retrieval and UI:
        * **doc_type** — from title + extension via :func:`_derive_doc_type`;
          enables document-type filters (``jira``, ``retro``, ``prd``, etc.).
        * **document_title** — Drive title for search-result display and
          citations.
        * **quarter** — from sprint via :func:`_derive_quarter`; powers
          cross-sprint trend queries (``WHERE quarter = 'Q2'``).
        * **file_created_at** — Drive timestamp or sprint calendar fallback
          via :func:`_derive_file_date`; supports chronological retrieval.
        * **file_updated_at** — last modified time from the connector.
        * **owner** — file owner for attribution and people-centric filters.

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
        # Chunk rows expose doc_type, quarter, and dates as real columns so
        # agents filter without JSON operators — "Q2 retros only", "newest
        # PRDs first", "jira exports in this sprint".
        #
        # WHAT THIS BLOCK DOES:
        # Enriches base_metadata with derived doc_type/quarter/date fields
        # and display-oriented document_title before chunkers copy metadata
        # onto every chunk.
        #
        # WHY THIS WAY:
        # Helpers centralise Nutrivana sprint calendar rules; ingest_file
        # only wires connector params (title, ext, sprint) into those rules
        # once per file instead of duplicating logic in each chunker branch.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Missing doc_type → type filters return nothing. Wrong quarter →
        # cross-sprint noise in answers. Wrong file_created_at → timeline
        # retrieval ranks old sprint docs as "recent". Missing document_title
        # → citations show file_id instead of a human-readable name.
        quarter = _derive_quarter(sprint)
        base_metadata.update({
            "doc_type": _derive_doc_type(title, ext),
            "document_title": title,
            "quarter": quarter,
            "file_created_at": _derive_file_date(sprint, file_created_at),
            "file_updated_at": file_updated_at,
            "owner": owner,
        })

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
        # Feature canonical names live in Supabase so extract_chunk_metadata can
        # map aliases to one vocabulary — same catalog for every sheet and format.
        #
        # WHAT THIS BLOCK DOES:
        # Loads all feature ``name`` values into ``feature_catalog`` once per file.
        #
        # WHY THIS WAY:
        # One query per ingest avoids N round trips inside the per-chunk LLM loop.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Empty catalog → model invents feature names; filters on features column
        # return nothing or wrong product areas.
        features_result = supabase.table("features").select("name").execute()
        feature_catalog = (
            features_result.data
            if features_result.data
            else []
        )

        # WHY THIS EXISTS IN PRISM AI:
        # people/ticket_ids/features/metrics columns on document_chunks are filled
        # from LLM extraction so agents filter without scanning chunk body text.
        #
        # WHAT THIS BLOCK DOES:
        # Calls extract_chunk_metadata for every chunk (all Excel sheets, Word,
        # PDF, slides, text) and merges results into chunk.metadata.
        #
        # WHY THIS WAY:
        # Runs after chunking, before embed — enrichment failure returns empty
        # lists and never blocks storage; content/vectors unchanged.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Skipping enrichment → ticket/people filters miss this file entirely;
        # running after embed would require a second pass over stored rows.
        for chunk in all_chunks:
            quarter = chunk.metadata.get("quarter")
            if quarter is None:
                quarter = _derive_quarter_from_sheet(chunk.metadata.get("sheet_name"))
            chunk.metadata["quarter"] = quarter
            extracted = extract_chunk_metadata(
                chunk.content, feature_catalog, doc_type=chunk.metadata.get("doc_type")
            )
            people = list(dict.fromkeys(extracted["people"]))
            ticket_ids = list(dict.fromkeys(extracted["ticket_ids"]))
            chunk.metadata["people"] = people
            chunk.metadata["ticket_ids"] = ticket_ids

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

        inserted_chunks = insert_chunks_with_embeddings(
            supabase,
            document_id,
            all_chunks,
            embeddings,
        )
        logger.info("Stored %s chunks for %s", len(inserted_chunks), title)
        store_questions_for_inserted_chunks(supabase, inserted_chunks)

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
            "chunks_stored": len(inserted_chunks),
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
    """Ingest one Gmail message (HTML body, labels, sender/recipients) end-to-end.

    One-sentence summary: hashes ``email_id + body`` for dedup, distinguishes
    full skip vs label-only metadata update vs body-changed re-ingest, parses
    sender/recipient headers into seed ``people``, chunks via
    :func:`chunk_email`, enriches with LLM metadata, embeds, stores, and
    generates per-chunk search questions.

    Why it exists for PrismAI:
        Gmail is the highest-churn connector PMs poll frequently. Most polls
        return zero body changes but plenty of label updates (Inbox → Done,
        custom tags). We special-case label-only updates as a metadata write
        so the connector can poll every few minutes without re-embedding.
        PM questions like "what did Arjun say about GOAL-BUG-005?" depend on
        accurate sender/recipient ``people`` tags, self-contained chunks, and
        question embeddings — all produced here.

    Decisions made inside (each one explained):
        1. **Hash = ``email_id + body``** — ``email_id`` guarantees uniqueness;
           body detects content changes. Hashing body alone would collide on
           identical auto-reply snippets across threads.
        2. **Three-way dedup** — unchanged hash + labels → skip; unchanged hash
           + different labels → metadata-only update (zero embed cost); changed
           hash → delete old chunks and re-ingest.
        3. **Sender display-name parsing** — Gmail ``From`` arrives as
           ``Display Name <email@domain>``. We take the text before ``<``,
           first word only, and whitelist-match against the six Nutrivana team
           first names. PM filters use first names, not full display strings.
        4. **Recipient plus-address parsing** — Nutrivana test mail uses
           ``nutrivana.prism+shristi@gmail.com`` style addresses. The tag
           after ``+`` encodes the intended recipient; regex extraction +
           whitelist match is deterministic and avoids LLM hallucination on
           headers.
        5. **Seed ``people`` before LLM** — header-derived names are merged
           with :func:`extract_chunk_metadata` output so To/From participants
           appear in ``document_chunks.people`` even when the body never
           mentions them by name.
        6. **``sprint=None`` and ``quarter=None`` always** — email threads
           are not sprint-scoped artefacts like Drive filenames. Subject-line
           sprint tokens are unreliable (forwards, cross-sprint replies).
           ``file_created_at`` / ``file_updated_at`` carry the send date for
           chronological filters instead.
        7. **``chunk_email`` paragraph splitting** — long bodies split on
           ``\\n\\n`` (paragraph separator) with a repeated From/Subject/Date
           prefix on every chunk so each retrieved slice is self-contained.
        8. **Question generation after store** — same as file ingest;
           :func:`store_questions_for_inserted_chunks` builds the
           question-index retrieval layer per chunk.

    What the caller does with the return value:
        The Gmail connector (``ingest_gmail.py``) inspects ``status`` to
        increment success/skip/error counts, logs ``subject`` and
        ``chunks_stored`` for operator visibility, and reads
        ``document_id`` when it needs to count stored questions.

    Returns:
        Success: ``{"status": "success", "subject", "document_id",
        "chunks_stored", "action"}``.
        Skip: ``{"status": "skipped", "reason", "subject"}``.
        Metadata-only: ``{"status": "metadata_updated", "subject"}``.
        Error: ``{"status": "error", "subject", "reason"}``.

    What breaks if this is wrong or missing:
        Re-embedding on every label tweak would cost more than the rest of
        ingestion combined. Skipping a real body change leaves PMs reading
        stale escalations. Wrong sender/recipient parsing → "what did Priya
        say?" misses threads she was on. Missing seed people → header-only
        attribution lost. Wrong sprint/quarter on email → cross-sprint filter
        noise. Skipping question generation → PM natural-language queries miss
        the question-index retrieval path.
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

        team_whitelist = {"shristi", "arjun", "priya", "kabir", "ananya", "ravi"}

        def _match_team_name(name: str) -> Optional[str]:
            normalized = name.strip().lower()
            if normalized in team_whitelist:
                return normalized.capitalize()
            return None

        # WHY THIS EXISTS IN PRISM AI:
        # Gmail ``From`` headers arrive as ``Display Name <email@domain>``.
        # PM filters and ``document_chunks.people`` use first names (Arjun,
        # Priya) — not full display strings or raw email addresses.
        #
        # WHAT THIS BLOCK DOES:
        # Strips the angle-bracket email, takes the first word of the display
        # name, and whitelist-matches against the six Nutrivana team members.
        #
        # WHY THIS WAY:
        # Splitting on ``<`` is the RFC-5322 display-name boundary; first
        # word matches how the team refers to each other in standups and Jira.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Parsing the full address or last name → ``people`` filters miss
        # "what did Arjun say"; wrong whitelist pass → external senders
        # pollute people columns.
        display_name = sender.split("<", 1)[0].strip()
        sender_first_name = display_name.split()[0] if display_name else ""
        matched_sender = _match_team_name(sender_first_name)

        # WHY THIS EXISTS IN PRISM AI:
        # Nutrivana test mail uses Gmail plus-addressing
        # (``nutrivana.prism+shristi@gmail.com``) to encode the intended
        # recipient in the To header without separate mailboxes per person.
        #
        # WHAT THIS BLOCK DOES:
        # For each recipient address, regex-extracts the tag between ``+``
        # and ``@``, capitalizes it, and whitelist-matches to a team name.
        #
        # WHY THIS WAY:
        # Plus-tag extraction is deterministic — no LLM needed on headers.
        # Multiple recipients are all collected because group threads can
        # include several team members in To/Cc plus-addresses.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Missing plus-tag parse → recipient never appears in ``people``;
        # "what did Shristi receive?" queries miss threads she was copied on.
        matched_recipients: list[str] = []
        for address in recipients:
            plus_match = re.search(r"\+([^@]+)@", address)
            if not plus_match:
                continue
            matched = _match_team_name(plus_match.group(1))
            if matched:
                matched_recipients.append(matched)

        # WHY THIS EXISTS IN PRISM AI:
        # Header-derived names must survive even when the email body never
        # mentions them. The LLM enrichment pass can add body mentions but
        # should not be the only source for From/To participants.
        #
        # WHAT THIS BLOCK DOES:
        # Builds a deduplicated ``seed_people`` list from matched sender +
        # all matched recipients, merged into chunk ``people`` after the
        # LLM call.
        #
        # WHY THIS WAY:
        # Seeding before :func:`extract_chunk_metadata` guarantees header
        # attribution on every chunk; LLM output extends rather than
        # replaces the list.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Skipping seed → PM asks "show me Priya's emails" and retrieval
        # only finds threads where her name appears in the body text.
        seed_people: list[str] = []
        if matched_sender:
            seed_people.append(matched_sender)
        for name in matched_recipients:
            if name not in seed_people:
                seed_people.append(name)

        email_metadata: Dict[str, Any] = {
            "source_type": "gmail",
            "email_id": email_id,
            "thread_id": thread_id,
            # WHY THIS EXISTS IN PRISM AI:
            # Sender and subject are the two most common email filters PMs use —
            # "what did Arjun say" scopes by sender; "find the GOAL-BUG-005
            # thread" scopes by subject line text.
            #
            # WHAT THIS BLOCK DOES:
            # Copies connector sender/subject into email_metadata so chunkers and
            # insert_chunks_with_embeddings can promote them to real table columns.
            #
            # WHY THIS WAY:
            # Denormalised columns with indexes beat ``metadata->>'sender'`` on
            # every Gmail poll; values must be present at ingest, not only in JSONB.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Missing keys → sender/subject columns stay NULL → email filters return
            # empty sets even when the thread was ingested.
            "sender": sender,
            "recipients": recipients,
            "subject": subject,
            "email_date": email_date,
            "gmail_labels": gmail_labels,
            "has_attachment": has_attachment,
            "attachment_names": attachment_names or [],
            "is_attachment": False,
            # WHY THIS EXISTS IN PRISM AI:
            # Email threads are not sprint-scoped Drive artefacts. Subject-line
            # sprint tokens are unreliable (forwards, cross-sprint replies).
            # PM date filters use ``file_created_at`` (send date) instead.
            #
            # WHAT THIS BLOCK DOES:
            # Sets ``sprint`` and ``quarter`` to ``None`` on every email chunk.
            #
            # WHY THIS WAY:
            # Drive files encode sprint in filenames; Gmail does not. Forcing
            # sprint/quarter from subject/labels mis-tags late replies and
            # breaks cross-quarter retrieval filters.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Inferring sprint from subject → Sprint 8 reply sent in Q3 lands
            # in Q3 filters; PM cross-sprint queries return wrong threads.
            "sprint": None,
            "quarter": None,
            "doc_type": "email",
            "document_title": subject,
            "file_created_at": email_date,
            "file_updated_at": email_date,
            "author": sender,
        }

        # WHY THIS EXISTS IN PRISM AI:
        # Long email threads must become multiple embeddable units without
        # losing who said what. ``chunk_email`` splits on ``\\n\\n``
        # (paragraph separator) and repeats From/Subject/Date on every chunk.
        #
        # WHAT THIS BLOCK DOES:
        # Delegates cleaned body + metadata to :func:`chunk_email`, which
        # short-circuits to one chunk under 500 chars or packs paragraphs
        # up to ``EMAIL_MAX_CHUNK`` for longer threads.
        #
        # WHY THIS WAY:
        # Paragraph boundaries preserve conversational structure better than
        # fixed character splits; the repeated prefix makes each chunk
        # citable without fetching sibling chunks.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Skipping chunk_email → one giant embed mixes three topics and
        # ranks for none; missing prefix repeat → "what did Alex say?"
        # returns body text with no sender attribution.
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

        # WHY THIS EXISTS IN PRISM AI:
        # Email chunks reference the same canonical feature names as Drive files
        # so "everything about Simplified Onboarding" spans Gmail and PRDs.
        #
        # WHAT THIS BLOCK DOES:
        # Loads feature names from Supabase once per message ingest.
        #
        # WHY THIS WAY:
        # Reuses the shared ``features`` table instead of hard-coding catalog in
        # pipeline.py; one query per email before the per-chunk LLM loop.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Stale or empty catalog → mis-tagged features on mail threads PMs search
        # by product name.
        features_result = supabase.table("features").select("name").execute()
        feature_catalog = (
            features_result.data
            if features_result.data
            else []
        )

        # WHY THIS EXISTS IN PRISM AI:
        # Gmail threads mention tickets, people, and metrics inline — promoting
        # LLM extraction onto metadata lets insert_chunks_with_embeddings write
        # real filter columns (same as file ingest).
        #
        # WHAT THIS BLOCK DOES:
        # Enriches every email chunk with people, ticket_ids, features, metrics.
        #
        # WHY THIS WAY:
        # Before embed/store only — failures return empty lists and do not block
        # the message from being searchable by body vector.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Enrich after storage → DB rows lack ticket_ids until re-ingest; PM
        # "find GOAL-BUG-005 email" filters miss new mail.
        for chunk in chunks:
            extracted = extract_chunk_metadata(
                chunk.content, feature_catalog, doc_type=chunk.metadata.get("doc_type")
            )
            # WHY THIS EXISTS IN PRISM AI:
            # ``seed_people`` from headers must union with LLM-extracted body
            # mentions so ``document_chunks.people`` is complete on every chunk.
            #
            # WHAT THIS BLOCK DOES:
            # Merges header-seeded names with LLM ``people`` output using
            # order-preserving deduplication before writing chunk metadata.
            #
            # WHY THIS WAY:
            # ``dict.fromkeys(seed + extracted)`` keeps seed order first, then
            # appends any new names the LLM found in the body text.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Overwriting seed with LLM-only output → header participants
            # disappear when the body never names them explicitly.
            people = list(dict.fromkeys(seed_people + extracted["people"]))
            ticket_ids = list(dict.fromkeys(extracted["ticket_ids"]))
            chunk.metadata["people"] = people
            chunk.metadata["ticket_ids"] = ticket_ids

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

        inserted_chunks = insert_chunks_with_embeddings(
            supabase,
            document_id,
            chunks,
            embeddings,
        )
        logger.info("Stored %s email chunks for %s", len(inserted_chunks), subject)
        # WHY THIS EXISTS IN PRISM AI:
        # Question-based retrieval is the primary PM search path after the
        # metadata-extraction pivot. Each stored chunk needs 0–10 generated
        # questions with embeddings in ``chunk_questions``.
        #
        # WHAT THIS BLOCK DOES:
        # Calls :func:`store_questions_for_inserted_chunks` on the rows
        # returned by :func:`insert_chunks_with_embeddings`.
        #
        # WHY THIS WAY:
        # Questions require chunk UUIDs from Supabase — must run after insert,
        # same pattern as :func:`ingest_file`.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Skipping question generation → natural-language PM queries miss
        # the question-index path and rely on content embedding alone.
        store_questions_for_inserted_chunks(supabase, inserted_chunks)

        return {
            "status": "success",
            "subject": subject,
            "document_id": document_id,
            "chunks_stored": len(inserted_chunks),
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
