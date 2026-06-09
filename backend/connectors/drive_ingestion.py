"""Google Drive ingestion orchestrator for PrismAI.

This module is the production entry point for syncing Nutrivana documents
from Google Drive into the PrismAI ingestion pipeline. It lists files
across all configured Nutrivana Drive folders, downloads each file to a
local temp directory, extracts sprint metadata from filenames, and hands
each file to :func:`ingestion.pipeline.ingest_file` for parsing, chunking,
embedding, and Supabase storage.

Public API
----------
``run_drive_ingestion()``
    Runs the full Drive → pipeline sync and returns a summary dict with
    per-file results (status, chunks stored, title) and aggregate counts.

``extract_sprint_from_filename(filename)``
    Parses a sprint number from a Drive filename (e.g. ``sprint6_planning.docx``
    → ``"6"``). Returns ``None`` when no sprint token is found.

How to run
----------
From the ``backend`` directory::

    python -m connectors.drive_ingestion

Or import and call programmatically::

    from connectors.drive_ingestion import run_drive_ingestion

    summary = run_drive_ingestion()
    print(summary)
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any

from connectors.google_drive import (
    TEMP_DIR,
    download_file,
    get_drive_service,
    list_all_nutrivana_files,
)
from ingestion.pipeline import delete_file, ingest_file
from ingestion.storage import get_supabase

logger = logging.getLogger(__name__)

# Matches sprint6, Sprint_10, sprint-3, "Sprint 12", etc. in Drive filenames.
SPRINT_PATTERN = re.compile(r"sprint[_\s-]*(\d+)", re.IGNORECASE)

# Pause between files to stay under Google Drive and embedding API rate limits.
INGESTION_DELAY_SECONDS = 2


def extract_sprint_from_filename(filename: str) -> str | None:
    """Return the sprint number string from a filename, or ``None`` if absent."""
    match = SPRINT_PATTERN.search(filename)
    if not match:
        return None
    return match.group(1)


def run_drive_ingestion() -> dict[str, Any]:
    """Sync every Nutrivana Drive file through the ingestion pipeline.

    Returns a summary with total/success/skipped/error counts and a
    ``results`` list containing one entry per file processed.
    """
    # Step 1: Authenticate once and enumerate all files across Nutrivana folders.
    service = get_drive_service()
    drive_files = list_all_nutrivana_files()

    summary: dict[str, Any] = {
        "total": len(drive_files),
        "success": 0,
        "skipped": 0,
        "error": 0,
        "results": [],
    }

    logger.info("Starting Drive ingestion for %d file(s)", len(drive_files))

    for index, drive_file in enumerate(drive_files, start=1):
        file_id = drive_file["file_id"]
        file_name = drive_file["file_name"]
        folder_label = drive_file["folder_name"]
        local_path: str | None = None

        logger.info(
            "Processing %d/%d: %s [%s]",
            index,
            len(drive_files),
            file_name,
            folder_label,
        )

        try:
            # Step 2: Derive sprint from the filename before download.
            sprint = extract_sprint_from_filename(file_name)

            # Step 3: Download to the shared temp folder (exports Google Docs/Sheets).
            local_path = download_file(service, file_id, file_name, TEMP_DIR)

            # Step 4: Hand off to the central ingestion pipeline.
            modified_time = drive_file.get("modified_time")
            result = ingest_file(
                file_path=local_path,
                source_id=file_id,
                source_type="google_drive",
                title=file_name,
                folder=folder_label,
                sprint=sprint,
                file_created_at=modified_time,
                file_updated_at=modified_time,
            )

            status = result.get("status", "unknown")
            chunks_stored = result.get("chunks_stored", 0)
            title = result.get("title", file_name)

            # Step 5: Report outcome for operator visibility.
            print(
                f"[{folder_label}] {title} — "
                f"status={status}, chunks_stored={chunks_stored}"
            )

            if status == "success":
                summary["success"] += 1
            elif status == "skipped":
                summary["skipped"] += 1
            else:
                summary["error"] += 1

            summary["results"].append(
                {
                    "file_id": file_id,
                    "file_name": file_name,
                    "folder": folder_label,
                    "sprint": sprint,
                    "status": status,
                    "chunks_stored": chunks_stored,
                    "title": title,
                    "reason": result.get("reason"),
                }
            )

        except Exception as exc:
            logger.exception("Failed to ingest %s (%s)", file_name, file_id)
            summary["error"] += 1
            print(f"[{folder_label}] {file_name} — status=error, chunks_stored=0")
            summary["results"].append(
                {
                    "file_id": file_id,
                    "file_name": file_name,
                    "folder": folder_label,
                    "sprint": extract_sprint_from_filename(file_name),
                    "status": "error",
                    "chunks_stored": 0,
                    "title": file_name,
                    "reason": str(exc),
                }
            )

        finally:
            # Step 6: Always remove the temp copy so disk usage stays bounded.
            if local_path is not None:
                temp_file = Path(local_path)
                if temp_file.exists():
                    temp_file.unlink()

        # Step 7: Throttle between files to avoid Drive / embedding rate limits.
        if index < len(drive_files):
            time.sleep(INGESTION_DELAY_SECONDS)

    # DELETED detection: purge Supabase rows for files removed from Drive.
    current_drive_ids = {drive_file["file_id"] for drive_file in drive_files}
    supabase = get_supabase()
    drive_documents: list[dict[str, Any]] = []
    page_size = 1000
    offset = 0
    while True:
        response = (
            supabase.table("documents")
            .select("source_id, title")
            .eq("source_type", "google_drive")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = response.data or []
        drive_documents.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size

    deleted_count = 0
    for doc in drive_documents:
        source_id = doc.get("source_id")
        if not source_id or source_id in current_drive_ids:
            continue
        title = doc.get("title", "(unknown)")
        delete_file(source_id)
        print(f"DELETED: {title} ({source_id})")
        deleted_count += 1

    summary["deleted"] = deleted_count

    logger.info(
        "Drive ingestion complete — total=%d success=%d skipped=%d error=%d",
        summary["total"],
        summary["success"],
        summary["skipped"],
        summary["error"],
    )

    return summary


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )
    run_drive_ingestion()
