"""Structural signal detector for chunking strategy selection.

Reads a file's structure (not its content) and decides which chunking
strategy is most appropriate. Detection is purely structural — no business
logic, no content assumptions, no domain-specific rules.

Public API:
    - Strategy            (enum of available chunking strategies)
    - DetectionResult     (dataclass returned by every detector)
    - detect_docx_strategy(file_path)
    - detect_excel_strategy(file_path, sheet_name)
    - detect_pdf_strategy(file_path)
    - detect_email_strategy()
"""

from __future__ import annotations

import json
import logging
import os
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import fitz  # PyMuPDF
import httpx
import openpyxl
from docx import Document


class Strategy(str, Enum):
    """Chunking strategies the detector can recommend."""

    heading_based = "heading_based"
    bold_title_based = "bold_title_based"
    blank_line_based = "blank_line_based"
    recursive_fallback = "recursive_fallback"
    row_based = "row_based"
    group_by_column = "group_by_column"
    single_chunk = "single_chunk"
    paragraph_based = "paragraph_based"
    slide_based = "slide_based"


@dataclass
class DetectionResult:
    """Outcome of a structural signal scan.

    Attributes:
        strategy: The recommended chunking strategy.
        confidence: One of "high", "medium", or "low".
        group_by_column: Header name to group by; only set when
            ``strategy`` is :attr:`Strategy.group_by_column`, otherwise None.
        notes: Plain-English explanation of why this strategy was chosen.
            Useful for debugging and for surfacing detection errors.
    """

    strategy: Strategy
    confidence: str
    group_by_column: Optional[str] = None
    notes: str = ""


def detect_docx_strategy(file_path: str) -> DetectionResult:
    """Pick a chunking strategy for a Word document based on its structure.

    Signals are checked in order; the first one that fires wins:
        1. Heading paragraphs (>= 2 with style name starting "Heading")
           -> heading_based, high.
        2. Fully-bold short paragraphs (>= 2 paragraphs whose runs with text
           are all bold and whose total text is <= 80 chars)
           -> bold_title_based, medium.
        3. Blank paragraphs make up > 15% of all paragraphs and there are
           >= 3 of them -> blank_line_based, medium.
        4. Otherwise -> recursive_fallback, low.

    Any exception is swallowed and reported as recursive_fallback / low,
    with the error message captured in ``notes``.
    """

    try:
        doc = Document(file_path)
        paragraphs = doc.paragraphs
        total_paragraphs = len(paragraphs)

        heading_count = sum(
            1
            for p in paragraphs
            if p.style is not None
            and p.style.name is not None
            and p.style.name.startswith("Heading")
        )
        if heading_count >= 2:
            return DetectionResult(
                strategy=Strategy.heading_based,
                confidence="high",
                notes=(
                    f"Found {heading_count} paragraphs with a 'Heading' style; "
                    "document is structured by headings."
                ),
            )

        bold_title_count = 0
        for p in paragraphs:
            text = p.text or ""
            if not text.strip() or len(text) > 80:
                continue
            text_runs = [r for r in p.runs if (r.text or "")]
            if not text_runs:
                continue
            if all(r.bold for r in text_runs):
                bold_title_count += 1
        if bold_title_count >= 2:
            return DetectionResult(
                strategy=Strategy.bold_title_based,
                confidence="medium",
                notes=(
                    f"Found {bold_title_count} fully-bold short paragraphs "
                    "(<=80 chars) acting as titles."
                ),
            )

        blank_count = sum(1 for p in paragraphs if not (p.text or "").strip())
        if total_paragraphs > 0:
            blank_ratio = blank_count / total_paragraphs
            if blank_ratio > 0.15 and blank_count >= 3:
                return DetectionResult(
                    strategy=Strategy.blank_line_based,
                    confidence="medium",
                    notes=(
                        f"{blank_count} blank paragraphs out of {total_paragraphs} "
                        f"({blank_ratio:.0%}); sections are separated by blank lines."
                    ),
                )

        return DetectionResult(
            strategy=Strategy.recursive_fallback,
            confidence="low",
            notes=(
                "No structural signals fired (no headings, no fully-bold titles, "
                "no blank-line separation); falling back to recursive splitter."
            ),
        )

    except Exception as exc:
        return DetectionResult(
            strategy=Strategy.recursive_fallback,
            confidence="low",
            notes=f"Failed to inspect DOCX structure: {exc!r}",
        )


def detect_excel_strategy(file_path: str, sheet_name: str) -> DetectionResult:
    """Pick a chunking strategy for a single Excel sheet based on its shape.

    Runs per sheet, not per workbook. Signals checked in order:
        1. After dropping fully empty rows, if <= 5 rows remain (header
           included) -> single_chunk, high.
        2. Treat the first non-empty row as headers. Collect non-None values
           from the first column across data rows as strings. If that column
           has between 2 and 8 unique values, the total count of values is
           more than 1.5x the unique count, and values appear in >= 50% of
           data rows -> group_by_column, high (the first column's header name
           is returned in ``group_by_column``).
        3. Otherwise -> row_based, high.

    Any exception is swallowed and reported as row_based / low, with the
    error message captured in ``notes``.
    """

    try:
        workbook = openpyxl.load_workbook(
            file_path, data_only=True, read_only=True
        )
        sheet = workbook[sheet_name]

        all_rows = [tuple(row) for row in sheet.iter_rows(values_only=True)]
        non_empty_rows = [
            row
            for row in all_rows
            if any(cell is not None and str(cell).strip() != "" for cell in row)
        ]

        if len(non_empty_rows) <= 5:
            return DetectionResult(
                strategy=Strategy.single_chunk,
                confidence="high",
                notes=(
                    f"Sheet '{sheet_name}' has only {len(non_empty_rows)} non-empty "
                    "rows (header included); fits in a single chunk."
                ),
            )

        headers = non_empty_rows[0]
        data_rows = non_empty_rows[1:]
        num_data_rows = len(data_rows)

        first_header = headers[0] if headers else None

        column_values: list[str] = []
        for row in data_rows:
            if not row:
                continue
            value = row[0]
            if value is None:
                continue
            column_values.append(str(value))

        total_values = len(column_values)
        unique_count = len(set(column_values)) if total_values else 0
        presence_ratio = total_values / num_data_rows if num_data_rows else 0

        if (
            first_header is not None
            and str(first_header).strip() != ""
            and 2 <= unique_count <= 8
            and total_values > 1.5 * unique_count
            and presence_ratio >= 0.5
        ):
            return DetectionResult(
                strategy=Strategy.group_by_column,
                confidence="high",
                group_by_column=str(first_header),
                notes=(
                    f"Column '{first_header}' has {unique_count} unique values across "
                    f"{total_values} data rows ({presence_ratio:.0%} populated); "
                    "rows can be grouped by this column."
                ),
            )

        return DetectionResult(
            strategy=Strategy.row_based,
            confidence="high",
            notes=(
                f"Sheet '{sheet_name}' has {num_data_rows} data rows with no clear "
                "grouping column; chunking row-by-row."
            ),
        )

    except Exception as exc:
        return DetectionResult(
            strategy=Strategy.row_based,
            confidence="low",
            notes=f"Failed to inspect Excel structure for sheet '{sheet_name}': {exc!r}",
        )


def detect_pdf_strategy(file_path: str) -> DetectionResult:
    """Pick a chunking strategy for a PDF based on extractable text and fonts.

    Inspects only the first 5 pages. Signals in order:
        1. Total extractable text across the first 5 pages is < 100 chars
           -> recursive_fallback, low (notes flag that OCR is needed).
        2. Across all spans on the first 5 pages, the maximum font size is
           >= 1.3x the median, and there are >= 3 distinct font sizes
           -> heading_based, medium.
        3. Otherwise -> recursive_fallback, medium.

    Any exception is swallowed and reported as recursive_fallback / low,
    with the error message captured in ``notes``.
    """

    try:
        with fitz.open(file_path) as pdf:
            page_limit = min(5, pdf.page_count)
            pages = [pdf[i] for i in range(page_limit)]

            combined_text = "".join(page.get_text() for page in pages)
            if len(combined_text) < 100:
                return DetectionResult(
                    strategy=Strategy.recursive_fallback,
                    confidence="low",
                    notes=(
                        f"Only {len(combined_text)} extractable characters across the "
                        f"first {page_limit} page(s); OCR is needed."
                    ),
                )

            font_sizes: list[float] = []
            for page in pages:
                page_dict = page.get_text("dict")
                for block in page_dict.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            size = span.get("size")
                            if isinstance(size, (int, float)):
                                font_sizes.append(float(size))

            if font_sizes:
                median_size = statistics.median(font_sizes)
                max_size = max(font_sizes)
                distinct_sizes = len({round(s, 2) for s in font_sizes})
                if (
                    median_size > 0
                    and max_size >= 1.3 * median_size
                    and distinct_sizes >= 3
                ):
                    return DetectionResult(
                        strategy=Strategy.heading_based,
                        confidence="medium",
                        notes=(
                            f"Font hierarchy detected: max={max_size:.1f}, "
                            f"median={median_size:.1f}, {distinct_sizes} distinct sizes."
                        ),
                    )

            return DetectionResult(
                strategy=Strategy.recursive_fallback,
                confidence="medium",
                notes=(
                    "Text is extractable but no clear font-size hierarchy found; "
                    "using recursive fallback."
                ),
            )

    except Exception as exc:
        return DetectionResult(
            strategy=Strategy.recursive_fallback,
            confidence="low",
            notes=f"Failed to inspect PDF structure: {exc!r}",
        )


def detect_email_strategy() -> DetectionResult:
    """Return the fixed strategy for emails.

    Email structure is consistent across providers, so this detector
    performs no I/O and always returns paragraph_based with high confidence.
    """

    return DetectionResult(
        strategy=Strategy.paragraph_based,
        confidence="high",
        notes="Email structure is consistent — always paragraph based",
    )


def detect_pptx_strategy() -> DetectionResult:
    """Return the fixed strategy for PowerPoint files.

    PowerPoint decks are always chunked one slide at a time, so this
    detector performs no I/O and always returns slide_based with high
    confidence.
    """

    return DetectionResult(
        strategy=Strategy.slide_based,
        confidence="high",
        notes=(
            "PowerPoint files are always chunked one slide at a time "
            "— no detection needed."
        ),
    )


def detect_text_strategy(file_path: str) -> DetectionResult:
    """Pick a chunking strategy for a plain-text or Markdown file.

    Signals are checked in order; the first one that fires wins:
        1. >= 2 lines start with one or more '#' characters (Markdown
           headings) -> heading_based, high.
        2. Blank lines make up > 15% of all lines and there are >= 3
           blank lines -> blank_line_based, medium.
        3. Otherwise -> recursive_fallback, low.

    Any exception is swallowed and reported as recursive_fallback / low,
    with the error message captured in ``notes``.
    """

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        heading_count = sum(
            1 for line in lines if line.lstrip().startswith("#")
        )
        if heading_count >= 2:
            return DetectionResult(
                strategy=Strategy.heading_based,
                confidence="high",
                notes=(
                    f"Found {heading_count} Markdown heading lines "
                    "(starting with '#'); file is structured by headings."
                ),
            )

        blank_count = sum(1 for line in lines if not line.strip())
        if total_lines > 0:
            blank_ratio = blank_count / total_lines
            if blank_ratio > 0.15 and blank_count >= 3:
                return DetectionResult(
                    strategy=Strategy.blank_line_based,
                    confidence="medium",
                    notes=(
                        f"{blank_count} blank lines out of {total_lines} "
                        f"({blank_ratio:.0%}); sections are separated by blank lines."
                    ),
                )

        return DetectionResult(
            strategy=Strategy.recursive_fallback,
            confidence="low",
            notes=(
                f"Only {heading_count} heading line(s) and {blank_count} blank "
                f"line(s) out of {total_lines} total; no clear structural signal."
            ),
        )

    except Exception as exc:
        return DetectionResult(
            strategy=Strategy.recursive_fallback,
            confidence="low",
            notes=f"Failed to inspect text file structure: {exc!r}",
        )


def classify_excel_sheet_with_llm(sheet_name: str, rows: list) -> DetectionResult:
    """Classify an Excel sheet's chunking strategy with an LLM over raw grid rows.

    One-sentence summary: formats every non-skipped row from ``parse_excel`` as
    pipe-separated text, asks OpenRouter which of ``row_based``, ``group_by_column``,
    or ``single_chunk`` keeps related PM context together, and returns a
    ``DetectionResult`` the Excel chunker can consume.

    Why it exists for PrismAI:
        Structural heuristics miss OKR rollups, epic blocks with blank group cells,
        and narrative retros where the header row is content. PMs lose answers when
        related rows land in different chunks. The classifier reads the full sheet
        (including row 0) before choosing a strategy or per-row groups.

    Decisions made inside:
        1. **Pipe-delimited row text** — mirrors how PMs scan spreadsheets and keeps
           token use predictable for wide exports.
        2. **Fixed prompt and model** — ``openai/gpt-5.4-nano`` at temperature 0 so
           classification is repeatable across ingest runs.
        3. **``row_groups`` in ``notes``** — ``DetectionResult`` has no extra field;
           JSON in ``notes`` lets ``group_by_column`` chunking read assignments without
           a schema change.
        4. **``row_based`` / low on failure** — ingest must not stop when the API or
           JSON parse fails; row chunks are the safe default.

    Returns:
        ``DetectionResult`` with ``confidence`` ``high`` on success, or ``row_based`` /
        ``low`` when anything in the LLM path fails.

    What breaks if this is wrong:
        Wrong strategy → PM questions return partial OKR or epic context. Crashes on
        API errors → bulk Drive ingest halts on one bad sheet.
    """

    logger = logging.getLogger(__name__)

    try:
        # WHY THIS EXISTS IN PRISM AI:
        # The model only sees text; we must mirror the sheet row order without
        # assuming which row is a header.
        #
        # WHAT THIS BLOCK DOES:
        # Build ``Row N: cell | cell`` lines with ``None`` cells as empty strings.
        #
        # WHY THIS WAY:
        # Pipe separators match the prompt examples and stay readable in wide sheets.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Dropping row indices or coercing types wrong → groups no longer align with
        # chunker row numbers.
        formatted_rows: list[str] = []
        for row_index, row in enumerate(rows):
            cells = ["" if cell is None else str(cell) for cell in row]
            formatted_rows.append(f"Row {row_index}: {' | '.join(cells)}")
        all_rows_as_text = "\n".join(formatted_rows)
        total_rows = len(rows)

        # WHY THIS EXISTS IN PRISM AI:
        # The prompt encodes PM chunking rules and JSON shape; wording is fixed so
        # evals and regressions stay comparable.
        #
        # WHAT THIS BLOCK DOES:
        # Insert sheet name, row count, and formatted grid into the classifier prompt.
        #
        # WHY THIS WAY:
        # Only the trailing placeholders vary per sheet; the task text stays verbatim.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Editing rules or examples → strategy drift and broken ``row_groups`` keys.
        prompt = (
            "TASK: Analyze an Excel sheet and determine the best chunking strategy "
            "for a RAG system. Assign every DATA row to its correct group if rows "
            "belong together.\n\n"
            "CONTEXT: You are helping a RAG system used by Product Managers. The "
            "system needs to chunk Excel sheets intelligently so that related "
            "information stays together in the same chunk. A chunk is what gets "
            "stored and retrieved when a PM asks a question. If related rows are "
            "split into different chunks the PM gets incomplete answers.\n\n"
            "STRATEGY DEFINITIONS:\n\n"
            "row_based:\n"
            "Use when EACH ROW is a self-contained, independently meaningful record "
            "that a user might search for on its own.\n"
            "Key test: Would a user ever want to find THIS specific row without "
            "needing the other rows? If yes → row_based.\n"
            "CRITICAL: Row length does NOT matter. Even if rows have very long "
            "description, acceptance criteria, or notes columns — if each row is a "
            "separate ticket, item, or record — use row_based. Do NOT use "
            "single_chunk just because rows are long.\n\n"
            "group_by_column:\n"
            "Use when rows belong together in groups under a shared parent value. "
            "Splitting groups loses meaning.\n"
            "Key test: Do multiple rows share the same ID or category and only make "
            "sense when read together? If yes → group_by_column.\n"
            "A parent group column has a value on the FIRST row of a group and empty "
            "cells on subsequent rows of the same group. Sometimes the parent value "
            "repeats on every row instead of being empty — that is still "
            "group_by_column as long as multiple rows share the same value.\n\n"
            "single_chunk:\n"
            "Use when the sheet as a WHOLE tells one continuous story and individual "
            "rows are NOT independently meaningful.\n"
            "Key test: Does this sheet only make sense when read together as a whole? "
            "If yes → single_chunk.\n"
            "CRITICAL: Only use single_chunk when rows are narrative sections or "
            "tightly coupled context. Do NOT use single_chunk for sheets where each "
            "row is a separate ticket, task, bug, initiative, or data record — even "
            "if those rows have long text columns.\n\n"
            "RULES:\n"
            "- Read ALL rows carefully before deciding anything\n"
            "- Row 0 is almost always a header row — identify it and EXCLUDE it "
            "from row_groups\n"
            "- Understand how data rows relate to each other\n"
            "- Understand how data rows relate to columns\n"
            "- Choose exactly one strategy\n"
            "- If group_by_column:\n"
            "  - Identify which column contains the PARENT GROUP values\n"
            "  - Assign EVERY data row to its correct PARENT GROUP value\n"
            "  - If a data row has an empty cell in the group column, it belongs to "
            "the same group as the last non-empty value above it\n"
            "  - NEVER assign a row to its own unique detail value\n\n"
            "EXAMPLES:\n\n"
            "Example 1 — row_based (short rows):\n"
            "Row 0: Ticket ID | Title | Type | Status | Priority\n"
            "Row 1: TECH-001 | Database schema design | Task | In Progress | P0\n"
            "Row 2: TECH-003 | Authentication system | Task | Done | P0\n"
            "Row 3: NUTR-001 | Food diary design | Task | Done | P1\n"
            "Each row is a completely independent ticket. A PM might search for "
            "TECH-001 specifically without needing TECH-003.\n"
            "Strategy: row_based. row_groups: {}\n\n"
            "Example 2 — row_based (long rows with descriptions):\n"
            "Row 0: Ticket ID | Title | Type | Status | Priority | Assignee | "
            "Sprint | Story Points | Description | Acceptance Criteria\n"
            "Row 1: TECH-001 | Database schema design | Task | In Progress | P0 | "
            "Arjun Mehta | Sprint 1 | 8 | We need to design a robust database "
            "schema that manages user profiles, food logs, and nutrient data... | "
            "• Schema includes separate tables for users and food logs...\n"
            "Row 2: TECH-003 | Authentication system | Task | Done | P0 | "
            "Arjun Mehta | Sprint 1 | 5 | We need to implement a JWT authentication "
            "system that manages user sessions effectively... | "
            "• JWT access token should have 1-hour expiry...\n"
            "Row 3: NUTR-TASK-003 | Date-stamped diary design | Task | Done | P0 | "
            "Arjun Mehta | Sprint 1 | 5 | We need to design a data model for the "
            "food diary that handles date-stamped entries... | "
            "• Food diary maintains a separate log for each calendar date...\n"
            "Even though each row has very long Description and Acceptance Criteria "
            "columns, each row is still a completely independent ticket. Row length "
            "does NOT change the strategy. A PM searching for TECH-001 wants only "
            "that ticket, not all tickets together.\n"
            "Strategy: row_based. row_groups: {}\n\n"
            "Example 3 — group_by_column (OKR sheet with empty parent cells):\n"
            "Row 0: Objective | Key Result | Status | Owner\n"
            "Row 1: Ship MVP | Demo completed | Done | Shristi\n"
            "Row 2:  | Tech spec done | Done | Arjun\n"
            "Row 3:  | Waitlist 150 users | Done | Ananya\n"
            "Row 4: User research | 5 interviews completed | Missed | Ananya\n"
            "Row 5:  | Survey done | Done | Ananya\n"
            "Column 0 (Objective) is the parent group column. Rows 2 and 3 have "
            "empty Objective — they belong to the same group as Row 1 which is "
            "Ship MVP. Rows 4 and 5 belong to User research. Separating key results "
            "from their objective loses meaning — a PM asking about Ship MVP needs "
            "all three key results together.\n"
            "Strategy: group_by_column. group_by_column_index: 0\n"
            'row_groups: {"1": "Ship MVP", "2": "Ship MVP", "3": "Ship MVP", '
            '"4": "User research", "5": "User research"}\n\n'
            "Example 4 — group_by_column (comments grouped by ticket ID):\n"
            "Row 0: Ticket ID | Comment Number | Author | Date | Comment Text\n"
            "Row 1: TECH-001 | 1 | Arjun Mehta | 2025-01-02 | I created the schema...\n"
            "Row 2: TECH-001 | 2 | Shristi | 2025-01-03 | Thanks for sharing...\n"
            "Row 3: TECH-001 | 3 | Arjun Mehta | 2025-01-04 | Great point...\n"
            "Row 4: TECH-003 | 1 | Arjun Mehta | 2025-01-05 | I created this ticket...\n"
            "Row 5: TECH-003 | 2 | Shristi | 2025-01-06 | I noticed a conflict...\n"
            "Column 0 (Ticket ID) is the parent group column. All rows with "
            "TECH-001 belong together — they form one conversation thread. All rows "
            "with TECH-003 belong together. Separating comments for the same ticket "
            "loses the conversation context. A PM asking about TECH-001 needs all "
            "its comments together.\n"
            "Strategy: group_by_column. group_by_column_index: 0\n"
            'row_groups: {"1": "TECH-001", "2": "TECH-001", "3": "TECH-001", '
            '"4": "TECH-003", "5": "TECH-003"}\n\n'
            "Example 5 — single_chunk (retrospective narrative):\n"
            "Row 0: Retrospective Narrative\n"
            "Row 1: Sprint summary | Sprint 1 was a foundational sprint...\n"
            "Row 2: What went well | 1. Arjun spike-first approach worked...\n"
            "Row 3: What did not go well | 1. Priya mid-sprint start...\n"
            "Row 4: Key learnings | 1. Architecture decisions need...\n"
            "Row 5: 3 things to carry forward | 1. Earlier PM involvement...\n"
            "Rows form one continuous narrative — sprint summary, what went well, "
            "what did not go well, learnings, carry forward. No row is independently "
            "meaningful without the others. A PM asking about this sprint retrospective "
            "needs all sections together. Splitting would break the story.\n"
            "Strategy: single_chunk. row_groups: {}\n\n"
            "Example 6 — single_chunk (sprint metrics summary):\n"
            "Row 0: Sprint Metrics Summary\n"
            "Row 1: Velocity | 42 story points\n"
            "Row 2: Completion rate | 87 percent\n"
            "Row 3: Bugs raised | 3\n"
            "Row 4: Bugs resolved | 3\n"
            "Row 5: Day 7 retention | 34 percent\n"
            "Row 6: NPS score | 42\n"
            "Rows form a summary of sprint metrics — no single row makes sense alone. "
            "A PM asking about sprint performance needs all metrics together. "
            "Splitting velocity from retention from NPS gives incomplete answers.\n"
            "Strategy: single_chunk. row_groups: {}\n\n"
            "FORMAT: Reply in JSON only. No text outside the JSON:\n"
            "{\n"
            '  "strategy": "row_based" or "group_by_column" or "single_chunk",\n'
            '  "group_by_column_index": null or integer (0-based column index),\n'
            '  "row_groups": {"1": "group value", "2": "group value"},\n'
            '  "reasoning": "one sentence explaining why"\n'
            "}\n\n"
            "IMPORTANT:\n"
            "- row_groups keys are strings of row indices\n"
            '- row_groups should NEVER contain row index "0" — that is always the '
            "header\n"
            "- For row_based and single_chunk — row_groups must be empty {}\n"
            "- For group_by_column — every data row index must have a group value "
            "that is the PARENT GROUP value, not the row's own unique value\n\n"
            f"Sheet name: {sheet_name}\n"
            f"Total rows: {total_rows}\n\n"
            "Complete sheet data:\n"
            f"{all_rows_as_text}"
        )

        # WHY THIS EXISTS IN PRISM AI:
        # OpenRouter credentials and base URL live in env so workers stay deployable
        # without hard-coded secrets.
        #
        # WHAT THIS BLOCK DOES:
        # Read ``OPENAI_API_KEY`` and ``OPENAI_BASE_URL`` for the chat request.
        #
        # WHY THIS WAY:
        # ``os.getenv`` matches the embedder and keeps one config surface for LLM calls.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Missing env → 401 or malformed URL and every sheet falls back to row_based.
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        url = f"{base_url.rstrip('/')}/chat/completions"

        # WHY THIS EXISTS IN PRISM AI:
        # Provider attribution and auth headers are required for OpenRouter routing.
        #
        # WHAT THIS BLOCK DOES:
        # Build Authorization, Content-Type, HTTP-Referer, and X-Title headers.
        #
        # WHY THIS WAY:
        # Same header set as embeddings so ops dashboards group PrismAI traffic.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Wrong bearer token → 401; missing Content-Type → rejected JSON bodies.
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ShristiiS/PrismAI",
            "X-Title": "PrismAI",
        }

        # WHY THIS EXISTS IN PRISM AI:
        # One user turn carries the full sheet; temperature 0 keeps strategy stable.
        #
        # WHAT THIS BLOCK DOES:
        # POST chat completions with model ``openai/gpt-5.4-nano`` and max_tokens 4000.
        #
        # WHY THIS WAY:
        # ``httpx.post`` with a 60s timeout matches embedder networking choices.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Truncated output → invalid JSON; long timeouts → stuck ingest workers.
        payload = {
            "model": "gpt-5.4-nano",
            "max_completion_tokens": 4000,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()

        # WHY THIS EXISTS IN PRISM AI:
        # Models often wrap JSON in markdown fences despite the format instruction.
        #
        # WHAT THIS BLOCK DOES:
        # Pull assistant text, strip ```json fences, and ``json.loads`` the payload.
        #
        # WHY THIS WAY:
        # Fence stripping before parse avoids brittle failures on cosmetic wrapping.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Parsing raw fenced text → JSONDecodeError and row_based fallback every time.
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("LLM response content is not a string")

        cleaned_content = content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
        cleaned_content = cleaned_content.strip()

        parsed = json.loads(cleaned_content)
        strategy_value = parsed.get("strategy")
        group_by_column_index = parsed.get("group_by_column_index")
        row_groups = parsed.get("row_groups", {})
        reasoning = parsed.get("reasoning", "")

        # WHY THIS EXISTS IN PRISM AI:
        # Downstream chunkers branch on ``Strategy`` enum values, not raw strings.
        #
        # WHAT THIS BLOCK DOES:
        # Map the model's strategy string to ``DetectionResult`` fields per strategy.
        #
        # WHY THIS WAY:
        # ``group_by_column`` stores row assignments in ``notes``; other strategies
        # keep human-readable reasoning there.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Missing ``group_by_column`` name or row_groups JSON → epic rows split apart.
        if strategy_value == "group_by_column":
            column_name: Optional[str] = None
            if group_by_column_index is not None and rows:
                first_row = rows[0]
                if (
                    isinstance(group_by_column_index, int)
                    and 0 <= group_by_column_index < len(first_row)
                ):
                    header_cell = first_row[group_by_column_index]
                    if header_cell is not None:
                        column_name = str(header_cell)

            return DetectionResult(
                strategy=Strategy.group_by_column,
                confidence="high",
                group_by_column=column_name,
                notes=json.dumps(row_groups),
            )

        if strategy_value == "single_chunk":
            return DetectionResult(
                strategy=Strategy.single_chunk,
                confidence="high",
                notes=reasoning,
            )

        return DetectionResult(
            strategy=Strategy.row_based,
            confidence="high",
            notes=reasoning,
        )

    except Exception as exc:
        logger.error(
            "LLM Excel classification failed for sheet %s: %s",
            sheet_name,
            exc,
            exc_info=True,
        )
        return DetectionResult(
            strategy=Strategy.row_based,
            confidence="low",
            notes=f"LLM classification failed: {exc}",
        )
