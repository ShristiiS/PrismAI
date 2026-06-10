"""Ingest Gmail threads into PrismAI via the central email pipeline (no delete)."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from connectors.gmail import get_gmail_service, get_thread, list_threads
from ingestion.pipeline import ingest_email
from ingestion.storage import get_supabase

THREAD_SLEEP_SECONDS = 1


def fetch_chunk_ids(supabase: Any, document_id: str) -> list[str]:
    chunk_ids: list[str] = []
    page_size = 1000
    offset = 0
    while True:
        response = (
            supabase.table("document_chunks")
            .select("id")
            .eq("document_id", document_id)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = response.data or []
        chunk_ids.extend(str(row["id"]) for row in batch)
        if len(batch) < page_size:
            break
        offset += page_size
    return chunk_ids


def count_questions_for_document(supabase: Any, document_id: str) -> int:
    chunk_ids = fetch_chunk_ids(supabase, document_id)
    if not chunk_ids:
        return 0
    total = 0
    for start in range(0, len(chunk_ids), 100):
        batch = chunk_ids[start : start + 100]
        response = (
            supabase.table("chunk_questions")
            .select("id")
            .in_("chunk_id", batch)
            .execute()
        )
        total += len(response.data or [])
    return total


def _ingest_thread(thread: dict[str, Any]) -> dict[str, Any]:
    """Map a hydrated Gmail thread dict to :func:`ingest_email` keyword args."""
    return ingest_email(
        body=thread["body"],
        email_id=thread["thread_id"],
        thread_id=thread["thread_id"],
        subject=thread["subject"],
        sender=thread["sender"],
        recipients=thread["recipients"],
        email_date=thread["date"],
        gmail_labels=thread["labels"],
    )


def main() -> int:
    """Sync up to ``--max`` Gmail threads through :func:`ingest_email`.

    One-sentence summary: authenticates once, lists thread IDs, hydrates
    each thread with :func:`get_thread`, and hands it to the central email
    ingestion pipeline — printing per-thread status and aggregate counts.

    Why it exists for PrismAI:
        PMs rely on Gmail threads (decisions, escalations, customer feedback)
        alongside Drive docs. This script is the batch entry point for loading
        Nutrivana mailbox content into Supabase without deleting existing rows.
        Operators run it after OAuth setup or when backfilling email history.

    Decisions made inside (each one explained):
        1. **``--max`` default 500** — matches ``list_threads`` default cap
           so a full mailbox backfill is one command, while ``--max 50`` supports
           smoke tests without embedding hundreds of threads.
        2. **``ingest_email`` not ``ingest_file``** — Gmail delivers HTML
           bodies, labels, and headers — not downloadable files. The email
           pipeline handles HTML cleanup, header people-seeding, label-only
           dedup, and ``source_type=gmail`` storage semantics.
        3. **``email_id = thread_id``** — one Supabase document per Gmail
           thread; thread ID is the stable ``source_id`` for dedup and updates.
        4. **1-second sleep between threads** — lighter than Drive's 2-second
           delay because Gmail API + embedding batch per thread is already
           slower; 1s avoids rate-limit bursts without making backfills painful.
        5. **No Supabase deletes** — fresh ingest only; ``ingest_email`` dedup
           skips unchanged threads or metadata-only label updates.
        6. **Question count after ingest** — queries ``chunk_questions`` by
           document ID so operators see question-index coverage per thread.

    What the caller does with the return value:
        Shell exit code: ``0`` on success, ``1`` if any thread errored.
        Operators read stdout for per-thread status and the final summary block.

    What breaks if this is wrong or missing:
        Wrong API choice (``ingest_file``) → HTML stored as binary garbage,
        no sender/subject columns, Gmail filters dead. No sleep → Gmail or
        OpenRouter rate limits mid-run. Wrong ``email_id`` → dedup collisions
        across threads. Skipping this script → email never reaches Supabase
        and PM retrieval is Drive-only.
    """
    parser = argparse.ArgumentParser(description="Ingest Gmail threads into PrismAI.")
    parser.add_argument(
        "--max",
        type=int,
        default=500,
        help="Maximum number of thread IDs to fetch and process (default: 500).",
    )
    args = parser.parse_args()
    max_results = args.max

    if max_results < 1:
        print("--max must be at least 1", file=sys.stderr)
        return 1

    # WHY THIS EXISTS IN PRISM AI:
    # Gmail OAuth tokens live in token_gmail.json; one service object is
    # reused for every thread in the run.
    #
    # WHAT THIS BLOCK DOES:
    # Calls get_gmail_service() to authenticate (or refresh) and build
    # the Gmail API v1 client.
    #
    # WHY THIS WAY:
    # Auth once per script invocation — same pattern as ingest_sprint.py
    # and drive_ingestion.py; avoids re-opening the browser per thread.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Expired or missing token → script exits before any thread ingests;
    # operator sees OAuth error with zero rows in Supabase.
    supabase = get_supabase()
    service = get_gmail_service()

    # WHY THIS EXISTS IN PRISM AI:
    # We list thread IDs first (cheap API call) before hydrating full MIME
    # payloads — so --max caps work without fetching bodies we will discard.
    #
    # WHAT THIS BLOCK DOES:
    # Paginates Gmail threads.list up to max_results IDs.
    #
    # WHY THIS WAY:
    # list_threads already handles page tokens; passing max_results from
    # --max lets operators smoke-test with --max 50.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Fetching all threads without cap → unbounded backfill cost; ignoring
    # --max → operator cannot limit a test run.
    thread_ids = list_threads(service, max_results=max_results)

    if not thread_ids:
        print("No Gmail threads found.")
        return 0

    print(f"=== INGEST GMAIL ({len(thread_ids)} thread(s), --max={max_results}) ===\n")

    summary: dict[str, Any] = {
        "threads_processed": 0,
        "total_chunks": 0,
        "total_questions": 0,
        "errors": [],
    }

    # WHY THIS EXISTS IN PRISM AI:
    # Each thread is one ingest unit — hydrate, ingest, report, throttle.
    #
    # WHAT THIS BLOCK DOES:
    # For every thread ID: get_thread → ingest_email → print status →
    # accumulate success counts or record errors.
    #
    # WHY THIS WAY:
    # Sequential processing keeps logs readable and respects API rate limits;
    # exceptions on one thread do not abort the entire batch.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Parallel ingest without throttling → Gmail 429 errors; abort-on-first-
    # error → one bad thread blocks hundreds of valid threads from ingesting.
    for index, thread_id in enumerate(thread_ids):
        subject = thread_id

        try:
            thread = get_thread(service, thread_id)
            subject = thread.get("subject") or thread_id

            sender = thread.get("sender") or ""
            if "nutrivana.prism@gmail.com" not in sender.lower():
                print(f"[SKIP] {subject} — not a Nutrivana team email")
                continue

            result = _ingest_thread(thread)

            status = result.get("status", "unknown")
            chunks_stored = int(result.get("chunks_stored") or 0)
            document_id = result.get("document_id")
            questions_stored = 0
            if document_id:
                questions_stored = count_questions_for_document(supabase, document_id)

            print(
                f"subject={subject} | status={status} | "
                f"chunks={chunks_stored} | questions={questions_stored}"
            )

            if status == "success":
                summary["threads_processed"] += 1
                summary["total_chunks"] += chunks_stored
                summary["total_questions"] += questions_stored
            elif status not in ("skipped", "metadata_updated"):
                reason = result.get("reason", "unknown")
                summary["errors"].append(
                    f"{subject}: status={status}, reason={reason}"
                )

        except Exception as exc:
            message = str(exc)
            print(f"ERROR: {subject}: {message}", file=sys.stderr)
            summary["errors"].append(f"{subject}: {message}")

        # WHY THIS EXISTS IN PRISM AI:
        # Gmail and embedding APIs enforce per-minute quotas; back-to-back
        # thread ingests can trigger 429s or OpenRouter throttling.
        #
        # WHAT THIS BLOCK DOES:
        # Sleeps THREAD_SLEEP_SECONDS (1s) after each thread except the last.
        #
        # WHY THIS WAY:
        # 1 second is shorter than Drive's 2s because each thread already
        # includes parse + LLM metadata + embed + question generation latency.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # No sleep → rate-limit failures mid-batch; sleep after last thread →
        # wasted wait with no benefit (guarded by index check).
        if index < len(thread_ids) - 1:
            time.sleep(THREAD_SLEEP_SECONDS)

    # WHY THIS EXISTS IN PRISM AI:
    # Operators need one glance at totals after a long backfill run.
    #
    # WHAT THIS BLOCK DOES:
    # Prints aggregate threads processed (success only), chunks, questions,
    # and any error list.
    #
    # WHY THIS WAY:
    # Matches ingest_sprint.py / ingest_strategy_docs.py summary format so
    # log parsing stays consistent across connectors.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Missing summary → operator cannot tell if backfill succeeded without
    # querying Supabase row counts manually.
    print("\n=== SUMMARY ===")
    print(f"Total threads processed: {summary['threads_processed']}")
    print(f"Total chunks: {summary['total_chunks']}")
    print(f"Total questions: {summary['total_questions']}")
    if summary["errors"]:
        print(f"Errors ({len(summary['errors'])}):")
        for error in summary["errors"]:
            print(f"  - {error}")
    else:
        print("Errors: none")

    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
