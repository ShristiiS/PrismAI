"""Deterministic verification of all document_chunks rows in Supabase."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from ingestion.storage import get_supabase

VALID_DOC_TYPES = [
    "jira",
    "meeting_notes",
    "planning",
    "retro",
    "okr",
    "roadmap",
    "technical_spec",
    "email",
]

VALID_FOLDERS = ["Jira", "Meeting Notes", "Planning", "Retros", "Product Strategy"]

FOLDER_DOCTYPE_MAP = {
    "Jira": ["jira"],
    "Meeting Notes": ["meeting_notes"],
    "Planning": ["planning"],
    "Retros": ["retro"],
    "Product Strategy": ["okr", "roadmap", "technical_spec"],
}

SPRINT_REQUIRED = ["jira", "retro", "meeting_notes", "planning"]
SPRINT_MUST_BE_NULL = ["okr", "roadmap", "technical_spec"]

QUARTER_MAP = {
    "1": "Q1",
    "2": "Q1",
    "3": "Q1",
    "4": "Q2",
    "5": "Q2",
    "6": "Q2",
    "7": "Q3",
    "8": "Q3",
    "9": "Q3",
    "10": "Q4",
    "11": "Q4",
    "12": "Q4",
    "13": "Q4",
}

SHEET_NAME_REQUIRED = ["jira", "retro", "okr", "roadmap"]
SHEET_NAME_MUST_BE_EMPTY = ["meeting_notes", "planning", "technical_spec", "email"]

SECTION_HEADING_REQUIRED = ["meeting_notes", "planning", "technical_spec"]
SECTION_HEADING_MUST_BE_EMPTY = ["jira", "retro", "okr", "roadmap", "email"]

PEOPLE_WHITELIST = ["Shristi", "Arjun", "Priya", "Kabir", "Ananya", "Ravi"]

EXCLUDED_TICKET_WORDS = [
    "V1",
    "V2",
    "V3",
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "P0",
    "P1",
    "P2",
    "P3",
    "API",
    "RLS",
    "DB",
    "UI",
    "UX",
    "JWT",
    "IST",
    "EER",
    "RDA",
    "PRD",
    "MVP",
    "MAU",
    "NPS",
    "FAQ",
    "OKR",
    "KR",
    "USDA",
    "WAITLIST",
]

SUMMARY_CATEGORIES = [
    "sprint",
    "quarter",
    "doc_type",
    "folder",
    "source_type",
    "sheet_name",
    "section_heading",
    "sender",
    "subject",
    "chunk_index",
    "document_title",
    "author",
    "file_created_at",
    "file_updated_at",
    "people",
    "features",
    "ticket_ids",
    "metrics",
    "chunk_type",
]

CHUNK_FIELDS = (
    "document_id,chunk_index,document_title,sprint,quarter,doc_type,folder,"
    "source_type,sheet_name,section_heading,sender,subject,author,"
    "file_created_at,file_updated_at,people,ticket_ids,features,metrics,chunk_type"
)


def _title(row: dict[str, Any]) -> str:
    return str(row.get("document_title") or "unknown")


def _idx(row: dict[str, Any]) -> Any:
    return row.get("chunk_index")


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _normalize_sprint(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _as_list(value: Any) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    return None


def _fetch_all_chunks(supabase: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page_size = 1000
    offset = 0

    while True:
        response = (
            supabase.table("document_chunks")
            .select(CHUNK_FIELDS)
            .order("document_title")
            .order("chunk_index")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = response.data or []
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size

    return rows


def _fetch_feature_catalog(supabase: Any) -> set[str]:
    response = supabase.table("features").select("name").execute()
    data = response.data or []
    return {str(row["name"]) for row in data if row.get("name")}


def main() -> None:
    supabase = get_supabase()
    chunks = _fetch_all_chunks(supabase)
    feature_catalog = _fetch_feature_catalog(supabase)

    counts: dict[str, int] = defaultdict(int)

    def report(category: str, row: dict[str, Any], message: str) -> None:
        if category.startswith("people"):
            summary_key = "people"
        elif category.startswith("features"):
            summary_key = "features"
        else:
            summary_key = category

        print(f"[{category}] {_title(row)} | chunk_index={_idx(row)} | {message}")
        counts[summary_key] += 1

    for row in chunks:
        title = _title(row)
        doc_type = row.get("doc_type")
        chunk_index = row.get("chunk_index")
        folder = row.get("folder")
        source_type = row.get("source_type")
        sprint = _normalize_sprint(row.get("sprint"))
        quarter = row.get("quarter")
        sheet_name = row.get("sheet_name")
        section_heading = row.get("section_heading")
        sender = row.get("sender")
        subject = row.get("subject")
        author = row.get("author")
        chunk_type = row.get("chunk_type")

        # document_title
        if _is_empty(row.get("document_title")):
            report("document_title", row, "document_title is null or empty")

        # doc_type
        if doc_type is None:
            report("doc_type", row, "doc_type is null")
        elif doc_type not in VALID_DOC_TYPES:
            report("doc_type", row, f"invalid doc_type: {doc_type}")

        # sprint
        if doc_type in SPRINT_REQUIRED:
            if sprint is None:
                report(
                    "sprint",
                    row,
                    f"sprint=None but doc_type={doc_type} requires sprint",
                )
            elif not sprint.isdigit() or not (1 <= int(sprint) <= 13):
                report("sprint", row, f"invalid sprint value: {sprint}")
        if doc_type in SPRINT_MUST_BE_NULL and sprint is not None:
            report(
                "sprint",
                row,
                f"sprint={sprint} but doc_type={doc_type} requires sprint=null",
            )

        # quarter
        if sprint is not None:
            expected_quarter = QUARTER_MAP.get(sprint)
            if expected_quarter is None:
                report("quarter", row, f"sprint={sprint} has no QUARTER_MAP entry")
            elif quarter != expected_quarter:
                report(
                    "quarter",
                    row,
                    f"sprint={sprint} but quarter={quarter}, should be {expected_quarter}",
                )
        elif doc_type not in ("okr", "roadmap"):
            if quarter is not None:
                report(
                    "quarter",
                    row,
                    f"sprint is null but quarter={quarter}, should be null "
                    f"(doc_type={doc_type})",
                )
        if quarter is not None and quarter not in ("Q1", "Q2", "Q3", "Q4"):
            report("quarter", row, f"invalid quarter value: {quarter}")

        # folder
        if doc_type == "email":
            if folder is not None and folder not in VALID_FOLDERS:
                report("folder", row, f"email chunk has invalid folder: {folder}")
        else:
            if folder is None or (isinstance(folder, str) and folder.strip() == ""):
                report("folder", row, f"folder is null/empty but doc_type={doc_type}")
            elif folder not in VALID_FOLDERS:
                report("folder", row, f"invalid folder: {folder}")
            else:
                allowed = FOLDER_DOCTYPE_MAP.get(folder, [])
                if doc_type not in allowed:
                    report(
                        "folder",
                        row,
                        f"doc_type={doc_type} does not match folder={folder} "
                        f"(expected one of {allowed})",
                    )

        # source_type
        if source_type is None:
            report("source_type", row, "source_type is null")
        elif source_type not in ("google_drive", "gmail"):
            report("source_type", row, f"invalid source_type: {source_type}")
        elif doc_type == "email" and source_type != "gmail":
            report(
                "source_type",
                row,
                f"email chunk has source_type={source_type}, must be gmail",
            )
        elif doc_type != "email" and source_type != "google_drive":
            report(
                "source_type",
                row,
                f"non-email chunk has source_type={source_type}, must be google_drive",
            )

        # sheet_name
        if doc_type in SHEET_NAME_REQUIRED:
            if _is_empty(sheet_name):
                report(
                    "sheet_name",
                    row,
                    f"sheet_name empty but doc_type={doc_type} requires sheet_name",
                )
        if doc_type in SHEET_NAME_MUST_BE_EMPTY and not _is_empty(sheet_name):
            report(
                "sheet_name",
                row,
                f"sheet_name={sheet_name!r} populated for doc_type={doc_type}",
            )

        # section_heading
        if doc_type in SECTION_HEADING_REQUIRED:
            if chunk_index is not None and chunk_index > 0 and _is_empty(section_heading):
                report(
                    "section_heading",
                    row,
                    f"section_heading empty but doc_type={doc_type} requires it "
                    f"for chunk_index > 0",
                )
        if doc_type in SECTION_HEADING_MUST_BE_EMPTY and not _is_empty(section_heading):
            report(
                "section_heading",
                row,
                f"section_heading={section_heading!r} populated for doc_type={doc_type}",
            )

        # sender
        if doc_type == "email":
            if _is_empty(sender):
                report("sender", row, "email chunk missing sender")
            elif "@" not in str(sender):
                report("sender", row, f"sender missing @: {sender}")
            elif not str(sender).strip().endswith("nutrivana.in"):
                report("sender", row, f"sender does not end with nutrivana.in: {sender}")
        elif sender is not None and str(sender).strip() != "":
            report("sender", row, f"non-email chunk has sender={sender}")

        # subject
        if doc_type == "email":
            if _is_empty(subject):
                report("subject", row, "email chunk missing subject")
        elif subject is not None and str(subject).strip() != "":
            report("subject", row, f"non-email chunk has subject={subject}")

        # author
        if doc_type == "email":
            if author is None or (isinstance(author, str) and author.strip() == ""):
                report("author", row, "author is null or empty")
            elif sender is not None and str(author) != str(sender):
                report(
                    "author",
                    row,
                    f"author={author!r} does not match sender={sender!r}",
                )

        # file_created_at / file_updated_at
        if row.get("file_created_at") is None:
            report("file_created_at", row, "file_created_at is null")
        if row.get("file_updated_at") is None:
            report("file_updated_at", row, "file_updated_at is null")

        # chunk_type
        if chunk_type is None:
            report("chunk_type", row, "chunk_type is null")
        elif chunk_type not in ("standard", "table"):
            report("chunk_type", row, f"unexpected chunk_type: {chunk_type}")

        # people
        people = _as_list(row.get("people"))
        if people is None:
            report("people_null", row, "people is null instead of []")
        else:
            seen_people: set[str] = set()
            for person in people:
                name = str(person).strip()
                if name == "":
                    report("people", row, "empty string in people array")
                    continue
                if " " in name:
                    report("people", row, f"full name not allowed: {name}")
                if name != name.strip() or (name and name[0].islower()):
                    report("people", row, f"lowercase name: {name}")
                if name not in PEOPLE_WHITELIST:
                    report("people", row, f"unknown person: {name}")
                if name in seen_people:
                    report("people_duplicate", row, f"duplicate person: {name}")
                seen_people.add(name)

        # features
        features = _as_list(row.get("features"))
        if features is None:
            report("features", row, "features is null instead of []")
        else:
            seen_features: set[str] = set()
            for feature in features:
                fname = str(feature).strip()
                if fname == "":
                    report("features", row, "empty string in features array")
                    continue
                if fname not in feature_catalog:
                    report("features_unknown", row, f"unknown feature: {fname}")
                if fname in seen_features:
                    report("features", row, f"duplicate feature: {fname}")
                seen_features.add(fname)

        # ticket_ids
        ticket_ids = _as_list(row.get("ticket_ids"))
        if ticket_ids is None:
            report("ticket_ids", row, "ticket_ids is null instead of []")
        else:
            seen_tickets: set[str] = set()
            for ticket in ticket_ids:
                tid = str(ticket).strip()
                if tid == "":
                    report("ticket_ids", row, "empty string in ticket_ids array")
                    continue
                if tid.upper() in {w.upper() for w in EXCLUDED_TICKET_WORDS}:
                    report("ticket_ids", row, f"excluded word in ticket_ids: {tid}")
                if tid in seen_tickets:
                    report("ticket_ids", row, f"duplicate ticket_id: {tid}")
                seen_tickets.add(tid)

        # metrics
        metrics = _as_list(row.get("metrics"))
        if metrics is None:
            report("metrics", row, "metrics is null instead of []")
        else:
            seen_metrics: set[str] = set()
            for metric in metrics:
                mval = str(metric).strip()
                if mval == "":
                    report("metrics", row, "empty string in metrics array")
                    continue
                if mval in seen_metrics:
                    report("metrics", row, f"duplicate metric: {mval}")
                seen_metrics.add(mval)

    # chunk_index sequencing per (document_title, sheet_name)
    by_doc_sheet: dict[tuple[str, Any], list[dict[str, Any]]] = defaultdict(list)
    for row in chunks:
        by_doc_sheet[(_title(row), row.get("sheet_name"))].append(row)

    for (title, sheet_name), doc_chunks in by_doc_sheet.items():
        indices: list[int] = []
        for row in doc_chunks:
            idx = row.get("chunk_index")
            if idx is None:
                report(
                    "chunk_index",
                    {
                        "document_title": title,
                        "sheet_name": sheet_name,
                        "chunk_index": None,
                    },
                    "chunk_index is null",
                )
                continue
            if not isinstance(idx, int):
                try:
                    idx = int(idx)
                except (TypeError, ValueError):
                    report(
                        "chunk_index",
                        row,
                        f"chunk_index is not an integer: {idx}",
                    )
                    continue
            if idx < 0:
                report("chunk_index", row, f"negative chunk_index: {idx}")
            indices.append(idx)

        if not indices:
            continue

        index_counts = Counter(indices)
        for dup_idx, count in index_counts.items():
            if count > 1:
                report(
                    "chunk_index",
                    {
                        "document_title": title,
                        "sheet_name": sheet_name,
                        "chunk_index": dup_idx,
                    },
                    f"duplicate chunk_index: {dup_idx}",
                )

        sorted_unique = sorted(index_counts.keys())
        if sorted_unique and sorted_unique[0] != 0:
            report(
                "chunk_index",
                {
                    "document_title": title,
                    "sheet_name": sheet_name,
                    "chunk_index": sorted_unique[0],
                },
                f"chunk_index does not start at 0 (starts at {sorted_unique[0]})",
            )

        for i in range(1, len(sorted_unique)):
            prev_idx = sorted_unique[i - 1]
            curr_idx = sorted_unique[i]
            if curr_idx - prev_idx > 1:
                report(
                    "chunk_index",
                    {
                        "document_title": title,
                        "sheet_name": sheet_name,
                        "chunk_index": curr_idx,
                    },
                    f"gap in chunk_index sequence after {prev_idx} (next is {curr_idx})",
                )

    print("\n=== SUMMARY ===")
    total = 0
    for category in SUMMARY_CATEGORIES:
        count = counts.get(category, 0)
        print(f"{category} issues: {count}")
        total += count
    print(f"TOTAL ISSUES: {total}")


if __name__ == "__main__":
    main()
