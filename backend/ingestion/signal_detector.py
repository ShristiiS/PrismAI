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

import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import fitz  # PyMuPDF
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
        2. Treat the first non-empty row as headers. For each column,
           collect non-None values from data rows as strings. If any column
           has between 2 and 8 unique values, the total count of values is
           more than 1.5x the unique count, and values appear in >= 50% of
           data rows -> group_by_column, high (the column's header name is
           returned in ``group_by_column``).
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

        for col_idx, header in enumerate(headers):
            if header is None or str(header).strip() == "":
                continue

            column_values: list[str] = []
            for row in data_rows:
                if col_idx >= len(row):
                    continue
                value = row[col_idx]
                if value is None:
                    continue
                column_values.append(str(value))

            total_values = len(column_values)
            if total_values == 0:
                continue
            unique_count = len(set(column_values))
            presence_ratio = total_values / num_data_rows if num_data_rows else 0

            if (
                2 <= unique_count <= 8
                and total_values > 1.5 * unique_count
                and presence_ratio >= 0.5
            ):
                return DetectionResult(
                    strategy=Strategy.group_by_column,
                    confidence="high",
                    group_by_column=str(header),
                    notes=(
                        f"Column '{header}' has {unique_count} unique values across "
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
