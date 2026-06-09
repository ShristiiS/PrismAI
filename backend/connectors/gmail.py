"""Gmail connector for Nutrivana email ingestion.

This module authenticates to Gmail via OAuth2 using ``credentials.json`` in
the backend folder and persists refresh tokens to ``token_gmail.json``. It
lists threads, fetches full conversation payloads (subject, participants,
body text, labels), and exposes a single helper to pull every thread for
downstream ingestion via :func:`ingestion.pipeline.ingest_email`.

Public API
----------
``get_gmail_service()``
    Authenticate (or refresh) and return a Gmail API v1 service object.

``list_threads(service, max_results=500)``
    Return up to ``max_results`` thread IDs from the authenticated mailbox.

``get_thread(service, thread_id)``
    Fetch one thread and return a dict with ``thread_id``, ``subject``,
    ``sender``, ``recipients``, ``date``, ``body``, and ``labels``.

``list_all_nutrivana_threads()``
    List all threads and return fully hydrated thread dicts.

How to use
----------
First run opens a browser for OAuth consent (Gmail read-only scope)::

    from connectors.gmail import list_all_nutrivana_threads

    threads = list_all_nutrivana_threads()
    for thread in threads:
        print(thread["subject"], thread["sender"])
"""

from __future__ import annotations

import base64
import logging
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = BACKEND_DIR / "credentials.json"
TOKEN_PATH = BACKEND_DIR / "token_gmail.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service() -> Resource:
    """Authenticate with Gmail and return an API service object."""
    creds: Credentials | None = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


def _header_value(headers: list[dict[str, str]], name: str) -> str:
    """Return the first header value matching ``name`` (case-insensitive)."""
    target = name.lower()
    for header in headers:
        if header.get("name", "").lower() == target:
            return header.get("value", "")
    return ""


def _parse_address_list(raw: str) -> list[str]:
    """Split a comma-separated To/Cc header into individual addresses."""
    if not raw.strip():
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _decode_body_data(data: str) -> str:
    """Decode a Gmail API base64url-encoded body fragment."""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def _extract_body_from_payload(payload: dict[str, Any]) -> str:
    """Recursively extract plain-text (or HTML fallback) from a MIME payload."""
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if body_data:
        text = _decode_body_data(body_data)
        if mime_type == "text/html":
            # Prefer plain text when available; HTML is a fallback only.
            return text
        return text

    parts = payload.get("parts", [])
    plain_parts: list[str] = []
    html_parts: list[str] = []

    for part in parts:
        part_mime = part.get("mimeType", "")
        if part_mime == "text/plain":
            part_body = part.get("body", {}).get("data")
            if part_body:
                plain_parts.append(_decode_body_data(part_body))
        elif part_mime == "text/html":
            part_body = part.get("body", {}).get("data")
            if part_body:
                html_parts.append(_decode_body_data(part_body))
        elif part.get("parts"):
            nested = _extract_body_from_payload(part)
            if nested:
                plain_parts.append(nested)

    if plain_parts:
        return "\n".join(plain_parts)
    if html_parts:
        return "\n".join(html_parts)
    return ""


def _format_internal_date(internal_date: str | None) -> str:
    """Convert Gmail ``internalDate`` (epoch ms) to an ISO-8601 string."""
    if not internal_date:
        return ""
    try:
        from datetime import datetime, timezone

        timestamp_ms = int(internal_date)
        return (
            datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
            .isoformat()
        )
    except (TypeError, ValueError):
        return ""


def list_threads(service: Resource, max_results: int = 500) -> list[str]:
    """List thread IDs from the authenticated mailbox.

    Paginates through the Gmail threads API until ``max_results`` IDs are
    collected or there are no more pages.
    """
    thread_ids: list[str] = []
    page_token: str | None = None

    while len(thread_ids) < max_results:
        # Step 1: Request one page of thread summaries (IDs only).
        page_size = min(100, max_results - len(thread_ids))
        response = (
            service.users()
            .threads()
            .list(userId="me", maxResults=page_size, pageToken=page_token)
            .execute()
        )

        for thread in response.get("threads", []):
            thread_ids.append(thread["id"])
            if len(thread_ids) >= max_results:
                break

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return thread_ids


def get_thread(service: Resource, thread_id: str) -> dict[str, Any]:
    """Fetch a full thread and return structured metadata plus body text."""
    # Step 2: Retrieve every message in the thread with full MIME payloads.
    response = (
        service.users()
        .threads()
        .get(userId="me", id=thread_id, format="full")
        .execute()
    )

    messages = response.get("messages", [])
    if not messages:
        return {
            "thread_id": thread_id,
            "subject": "",
            "sender": "",
            "recipients": [],
            "date": "",
            "body": "",
            "labels": [],
        }

    # Step 3: Use the first message for thread-level headers (subject, date).
    first_payload = messages[0].get("payload", {})
    first_headers = first_payload.get("headers", [])

    subject = _header_value(first_headers, "Subject")
    sender = _header_value(first_headers, "From")

    to_raw = _header_value(first_headers, "To")
    cc_raw = _header_value(first_headers, "Cc")
    recipients = _parse_address_list(to_raw) + _parse_address_list(cc_raw)

    date_header = _header_value(first_headers, "Date")
    if date_header:
        try:
            date = parsedate_to_datetime(date_header).isoformat()
        except (TypeError, ValueError):
            date = date_header
    else:
        date = _format_internal_date(messages[0].get("internalDate"))

    # Step 4: Collect labels from every message (union, stable order).
    label_set: list[str] = []
    seen_labels: set[str] = set()
    for message in messages:
        for label in message.get("labelIds", []):
            if label not in seen_labels:
                seen_labels.add(label)
                label_set.append(label)

    # Step 5: Concatenate the body text of all messages in chronological order.
    body_parts: list[str] = []
    for message in messages:
        payload = message.get("payload", {})
        message_body = _extract_body_from_payload(payload)
        if message_body.strip():
            msg_headers = payload.get("headers", [])
            msg_from = _header_value(msg_headers, "From")
            msg_date = _header_value(msg_headers, "Date") or _format_internal_date(
                message.get("internalDate")
            )
            body_parts.append(f"From: {msg_from}\nDate: {msg_date}\n\n{message_body}")

    body = "\n\n---\n\n".join(body_parts)

    return {
        "thread_id": thread_id,
        "subject": subject,
        "sender": sender,
        "recipients": recipients,
        "date": date,
        "body": body,
        "labels": label_set,
    }


def list_all_nutrivana_threads() -> list[dict[str, Any]]:
    """List and hydrate every thread in the authenticated Gmail mailbox."""
    # Step 6: Authenticate once, then walk every thread ID.
    service = get_gmail_service()
    thread_ids = list_threads(service)

    threads: list[dict[str, Any]] = []
    for thread_id in thread_ids:
        try:
            thread = get_thread(service, thread_id)
            threads.append(thread)
        except Exception:
            logger.exception("Failed to fetch thread %s", thread_id)

    logger.info("Fetched %d Gmail thread(s)", len(threads))
    return threads
