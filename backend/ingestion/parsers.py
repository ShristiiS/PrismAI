"""Structured parsers for PrismAI ingestion.

Reads raw files and converts them into labelled structural elements.
This module never chunks — chunking is always a separate downstream step.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List

import fitz  # PyMuPDF
import openpyxl
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from pptx import Presentation


@dataclass
class ParsedElement:
    """One structural unit extracted from a source document."""

    element_type: str  # heading | paragraph | table | bold_title | blank | slide
    content: str
    level: int  # heading level 1–3, or 0 for non-headings
    metadata: Dict[str, Any] = field(default_factory=dict)


def _strip_xml_tag(tag: str) -> str:
    """Return XML local tag name without namespace prefix."""
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _heading_level_from_style(style_name: str) -> int:
    """Parse heading level from a Word paragraph style name."""
    m = re.search(r"(\d+)", style_name)
    if m:
        return max(1, min(3, int(m.group(1))))
    return 1


def parse_docx(file_path: str) -> List[ParsedElement]:
    """Parse a Word document into structural elements in document order.

    Uses the XML body iterator ``doc.element.body`` so tables stay interleaved
    with paragraphs. Raises :exc:`ValueError` if parsing fails.
    """

    try:
        doc = Document(file_path)
        out: List[ParsedElement] = []

        for element in doc.element.body:
            tag = _strip_xml_tag(element.tag)

            if tag == "p":
                para = Paragraph(element, doc._body)
                style_name = para.style.name if para.style is not None else ""
                text = para.text or ""

                if style_name.startswith("Heading"):
                    lvl = _heading_level_from_style(style_name)
                    out.append(
                        ParsedElement(
                            element_type="heading",
                            content=text.strip(),
                            level=lvl,
                            metadata={},
                        )
                    )
                elif not text.strip():
                    out.append(
                        ParsedElement(
                            element_type="blank",
                            content="",
                            level=0,
                            metadata={},
                        )
                    )
                else:
                    text_runs = [r for r in para.runs if (r.text or "")]
                    all_bold = bool(text_runs) and all(r.bold for r in text_runs)
                    if all_bold and len(text) <= 80:
                        out.append(
                            ParsedElement(
                                element_type="bold_title",
                                content=text.strip(),
                                level=0,
                                metadata={},
                            )
                        )
                    else:
                        out.append(
                            ParsedElement(
                                element_type="paragraph",
                                content=text,
                                level=0,
                                metadata={},
                            )
                        )

            elif tag == "tbl":
                table = Table(element, doc._body)
                row_texts: List[str] = []
                max_cols = 0
                for row in table.rows:
                    cells = row.cells
                    max_cols = max(max_cols, len(cells))
                    unique_vals: List[str] = []
                    prev_val: str | None = None
                    for cell in cells:
                        val = (cell.text or "").strip()
                        if val == prev_val:
                            continue
                        unique_vals.append(val)
                        prev_val = val
                    row_texts.append(" | ".join(unique_vals))

                table_body = "\n".join(row_texts)
                out.append(
                    ParsedElement(
                        element_type="table",
                        content=table_body,
                        level=0,
                        metadata={
                            "row_count": len(table.rows),
                            "col_count": max_cols,
                        },
                    )
                )

        return out

    except Exception as exc:
        raise ValueError(f"Failed to parse DOCX {file_path!r}: {exc}") from exc


def parse_excel(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Parse all sheets of an Excel workbook into headers and row dicts.

    Returns ``{ sheet_name: { \"headers\": [...], \"rows\": [{col: val}] } }``.
    Uses read-only streaming mode. Workbook is closed before return.
    """

    workbook = openpyxl.load_workbook(
        file_path, read_only=True, data_only=True
    )
    try:
        result: Dict[str, Dict[str, Any]] = {}

        for sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
            raw_rows: List[tuple[Any, ...]] = []

            for row in ws.iter_rows(values_only=True):
                if row is None:
                    continue
                if not any(cell is not None for cell in row):
                    continue
                raw_rows.append(tuple(row))

            if not raw_rows:
                result[sheet_name] = {"headers": [], "rows": []}
                continue

            header_row = raw_rows[0]
            headers: List[str] = []
            for idx, cell in enumerate(header_row):
                if cell is None or str(cell).strip() == "":
                    headers.append(f"Column{idx}")
                else:
                    headers.append(str(cell))

            data_rows: List[Dict[str, str]] = []
            for data_tuple in raw_rows[1:]:
                row_dict: Dict[str, str] = {}
                for col_idx, header in enumerate(headers):
                    val = (
                        data_tuple[col_idx]
                        if col_idx < len(data_tuple)
                        else None
                    )
                    row_dict[header] = "" if val is None else str(val)

                if not any(v.strip() for v in row_dict.values()):
                    continue
                data_rows.append(row_dict)

            result[sheet_name] = {"headers": headers, "rows": data_rows}

        return result

    finally:
        workbook.close()


def parse_pptx(file_path: str) -> List[ParsedElement]:
    """Parse a PowerPoint deck into one ``slide`` element per slide in order."""

    prs = Presentation(file_path)
    elements: List[ParsedElement] = []

    for slide_idx, slide in enumerate(prs.slides):
        parts: List[str] = []

        title_shape = slide.shapes.title
        if title_shape is not None and title_shape.has_text_frame:
            t = title_shape.text_frame.text.strip()
            if t:
                parts.append(t)

        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            if title_shape is not None and shape is title_shape:
                continue
            paras = [
                p.text.strip()
                for p in shape.text_frame.paragraphs
                if p.text and p.text.strip()
            ]
            if paras:
                parts.append("\n".join(paras))

        if slide.has_notes_slide:
            ns = slide.notes_slide
            if ns.notes_text_frame is not None:
                ntxt = ns.notes_text_frame.text.strip()
                if ntxt:
                    parts.append(ntxt)

        content = "\n".join(parts)
        elements.append(
            ParsedElement(
                element_type="slide",
                content=content,
                level=0,
                metadata={"slide_number": slide_idx + 1},
            )
        )

    return elements


def _span_is_bold(span: Dict[str, Any]) -> bool:
    """Detect bold from font name or PyMuPDF span flags (bit 4)."""
    font = span.get("font") or ""
    if isinstance(font, str) and ("Bold" in font or "bold" in font):
        return True
    flags = span.get("flags")
    if isinstance(flags, int) and (flags & 16):
        return True
    return False


def parse_pdf(file_path: str) -> List[ParsedElement]:
    """Parse a PDF into headings and paragraphs using font metrics."""

    elements: List[ParsedElement] = []

    with fitz.open(file_path) as pdf:
        font_sizes_first_pass: List[float] = []
        page_limit = min(5, pdf.page_count)
        for pi in range(page_limit):
            page = pdf[pi]
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        sz = span.get("size")
                        if isinstance(sz, (int, float)):
                            font_sizes_first_pass.append(float(sz))

        if font_sizes_first_pass:
            body_size = float(statistics.median(font_sizes_first_pass))
        else:
            body_size = 11.0

        num_pages = pdf.page_count
        for pi in range(num_pages):
            page = pdf[pi]
            page_num = pi + 1
            page_text = page.get_text()
            text_len = len(page_text.strip())

            if text_len < 50:
                elements.append(
                    ParsedElement(
                        element_type="paragraph",
                        content=f"[Page {page_num} — scanned, needs OCR]",
                        level=0,
                        metadata={"page": page_num},
                    )
                )
                elements.append(
                    ParsedElement(
                        element_type="blank",
                        content="",
                        level=0,
                        metadata={"page_break_after": page_num},
                    )
                )
                continue

            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text") or ""
                        if not text.strip():
                            continue
                        sz_raw = span.get("size")
                        if not isinstance(sz_raw, (int, float)):
                            continue
                        sz = float(sz_raw)
                        bold = _span_is_bold(span)
                        is_heading = sz >= 1.3 * body_size or (
                            bold
                            and len(text) < 100
                            and abs(sz - body_size) <= 0.10 * body_size
                        )

                        if is_heading:
                            lvl = 1 if sz >= 1.5 * body_size else 2
                            elements.append(
                                ParsedElement(
                                    element_type="heading",
                                    content=text,
                                    level=max(1, min(3, lvl)),
                                    metadata={"page": page_num},
                                )
                            )
                        else:
                            elements.append(
                                ParsedElement(
                                    element_type="paragraph",
                                    content=text,
                                    level=0,
                                    metadata={"page": page_num},
                                )
                            )

            elements.append(
                ParsedElement(
                    element_type="blank",
                    content="",
                    level=0,
                    metadata={"page_break_after": page_num},
                )
            )

    return elements


def parse_text_file(file_path: str) -> List[ParsedElement]:
    """Parse a plain-text or Markdown file line-by-line."""

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    out: List[ParsedElement] = []
    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            out.append(
                ParsedElement(element_type="blank", content="", level=0)
            )
            continue

        if line.startswith("#"):
            level = 0
            for ch in line:
                if ch == "#":
                    level += 1
                else:
                    break
            level = max(1, min(3, level))
            inner = line[level:].strip()
            out.append(
                ParsedElement(
                    element_type="heading",
                    content=inner,
                    level=level,
                )
            )
        else:
            out.append(
                ParsedElement(
                    element_type="paragraph",
                    content=line,
                    level=0,
                )
            )

    return out


def parse_email_body(raw_body: str, is_html: bool = False) -> str:
    """Normalize email body to plain text by stripping HTML and reply chains."""

    text = raw_body.replace("\r\n", "\n")

    if is_html:
        text = re.sub(
            r"<style[^>]*>.*?</style>",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        text = re.sub(
            r"<script[^>]*>.*?</script>",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&#\d+;", "", text)
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")

    lines = text.split("\n")

    def should_cut_from_line_index(i: int) -> bool:
        line = lines[i]
        if re.match(r"^On .+ wrote:\s*$", line):
            return True
        if re.match(r"^---\s*Original Message\s*---\s*$", line, re.I):
            return True
        if line.startswith(">"):
            return True
        if re.match(r"^_{5,}", line):
            return True
        if line.startswith("From:") and i + 1 < len(lines):
            if lines[i + 1].lstrip().startswith("Sent:"):
                return True
        return False

    cut_idx: int | None = None
    for i in range(len(lines)):
        if should_cut_from_line_index(i):
            cut_idx = i
            break

    if cut_idx is not None:
        lines = lines[:cut_idx]

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()

