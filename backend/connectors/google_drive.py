"""Google Drive connector for Nutrivana document ingestion.

Authenticates via OAuth2 using ``credentials.json`` in the backend folder
and persists tokens to ``token_drive.json``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaIoBaseDownload

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = BACKEND_DIR / "credentials.json"
TOKEN_PATH = BACKEND_DIR / "token_drive.json"
TEMP_DIR = BACKEND_DIR / "temp"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

NUTRIVANA_FOLDERS = ("Word Docs", "Retros", "Jira", "OKRs")

# Google Workspace native types → (export MIME, file extension)
GOOGLE_EXPORT_MIME: dict[str, tuple[str, str]] = {
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".docx",
    ),
    "application/vnd.google-apps.spreadsheet": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xlsx",
    ),
}


def get_drive_service() -> Resource:
    """Authenticate with Google Drive and return an API service object."""
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

    return build("drive", "v3", credentials=creds)


def _find_folder_id(service: Resource, folder_name: str) -> str:
    """Return the Drive ID for the first non-trashed folder matching ``folder_name``."""
    escaped_name = folder_name.replace("'", "\\'")
    query = (
        "mimeType='application/vnd.google-apps.folder' "
        f"and name='{escaped_name}' "
        "and trashed=false"
    )
    response = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id,name)", pageSize=1)
        .execute()
    )
    folders = response.get("files", [])
    if not folders:
        raise FileNotFoundError(f"Drive folder not found: {folder_name!r}")

    return folders[0]["id"]


def list_files_in_folder(service: Resource, folder_name: str) -> list[dict[str, Any]]:
    """List files in a Drive folder by name.

    Returns dicts with ``id``, ``name``, ``mimeType``, and ``modifiedTime``.
    """
    folder_id = _find_folder_id(service, folder_name)
    query = f"'{folder_id}' in parents and trashed=false"

    files: list[dict[str, Any]] = []
    page_token: str | None = None

    while True:
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                pageToken=page_token,
                pageSize=100,
            )
            .execute()
        )

        for item in response.get("files", []):
            files.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "mimeType": item["mimeType"],
                    "modifiedTime": item.get("modifiedTime"),
                }
            )

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return files


def download_file(
    service: Resource,
    file_id: str,
    file_name: str,
    dest_folder: str | Path,
) -> str:
    """Download a Drive file to ``dest_folder`` and return the local path.

    Regular files are downloaded as-is. Google Docs and Sheets are exported
    to ``.docx`` and ``.xlsx`` respectively.
    """
    dest_path = Path(dest_folder)
    dest_path.mkdir(parents=True, exist_ok=True)

    meta = (
        service.files()
        .get(fileId=file_id, fields="mimeType,name")
        .execute()
    )
    mime_type = meta.get("mimeType", "")

    if mime_type in GOOGLE_EXPORT_MIME:
        export_mime, extension = GOOGLE_EXPORT_MIME[mime_type]
        stem = Path(file_name).stem
        local_name = file_name if file_name.lower().endswith(extension) else f"{stem}{extension}"
        request = service.files().export_media(
            fileId=file_id, mimeType=export_mime
        )
    else:
        local_name = file_name
        request = service.files().get_media(fileId=file_id)

    local_path = dest_path / local_name

    with open(local_path, "wb") as handle:
        downloader = MediaIoBaseDownload(handle, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    logger.info("Downloaded %s → %s", file_id, local_path)
    return str(local_path)


def list_all_nutrivana_files() -> list[dict[str, Any]]:
    """List every file across the four Nutrivana Drive folders."""
    service = get_drive_service()
    all_files: list[dict[str, Any]] = []

    folders = [
        {"drive_name": "Sprint Meeting Notes", "label": "Meeting Notes"},
        {"drive_name": "Sprint Planning", "label": "Planning"},
        {"drive_name": "Sprint Retrospective", "label": "Retros"},
        {"drive_name": "jira", "label": "Jira"},
        {"drive_name": "Product Strategy", "label": "Product Strategy"},
    ]

    for folder in folders:
        try:
            folder_files = list_files_in_folder(service, folder["drive_name"])
        except FileNotFoundError:
            logger.warning("Skipping missing Drive folder: %s", folder["drive_name"])
            continue

        for item in folder_files:
            all_files.append(
                {
                    "folder_name": folder["label"],
                    "file_id": item["id"],
                    "file_name": item["name"],
                    "mime_type": item["mimeType"],
                    "modified_time": item.get("modifiedTime"),
                }
            )

    return all_files
