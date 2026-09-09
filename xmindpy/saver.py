"""Save a Workbook as a modern XMind 2020+ JSON-format `.xmind` file."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from typing import IO, Any

from .workbook import Workbook

MIMETYPE = "application/vnd.xmind.workbook"

# 1x1 transparent PNG; some XMind builds require a thumbnail to render preview.
THUMBNAIL_PNG: bytes = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000d49444154789c6300010000000500010d0a2db40000000049454e44"
    "ae426082"
)


def _build_metadata(workbook: Workbook) -> dict[str, Any]:
    md = {
        "modifier": workbook.metadata.get("modifier", ""),
        "dataStructureVersion": "3",
        "creator": workbook.metadata.get("creator") or {"name": "xmindpy"},
        "layoutEngineVersion": "5",
    }
    if workbook.sheets:
        md["activeSheetId"] = workbook.sheets[0].id
    md["created"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    return md


def _build_manifest(file_entries: dict[str, str]) -> str:
    entries = {path: {"media-type": media} for path, media in file_entries.items()}
    return json.dumps({"file-entries": entries}, ensure_ascii=False, indent=2)


def save_workbook(workbook: Workbook, path: str) -> None:
    """Save ``workbook`` to ``path`` in modern XMind JSON format."""
    content_json = json.dumps(workbook.to_content(), ensure_ascii=False, indent=2)
    metadata_json = json.dumps(_build_metadata(workbook), ensure_ascii=False, indent=2)

    # manifest lists every file we actually put in the zip; compute media-types.
    manifest_data = _build_manifest({
        "content.json": "application/json",
        "metadata.json": "application/json",
        "Thumbnails/thumbnail.png": "image/png",
    })

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        # mimetype MUST be the first entry, stored uncompressed
        mimetype_info = zipfile.ZipInfo("mimetype")
        mimetype_info.compress_type = zipfile.ZIP_STORED
        z.writestr(mimetype_info, MIMETYPE)

        z.writestr("content.json", content_json)
        z.writestr("metadata.json", metadata_json)
        z.writestr("manifest.json", manifest_data)
        z.writestr("Thumbnails/thumbnail.png", THUMBNAIL_PNG)


def save_to_stream(workbook: Workbook, stream: IO[bytes]) -> None:
    """Like :func:`save_workbook` but writes to a binary stream."""
    import io

    buf = io.BytesIO()
    save_workbook(workbook, buf)
    stream.write(buf.getvalue())