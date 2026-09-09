"""Load an XMind workbook from a `.xmind` file (auto-detects JSON or legacy XML)."""

from __future__ import annotations

import json
import zipfile
from typing import IO

from .workbook import Workbook


def _is_json_format(names: list[str]) -> bool:
    return "content.json" in names


def _is_xml_format(names: list[str]) -> bool:
    return "content.xml" in names


def load_workbook(path: str) -> Workbook:
    """Load an `.xmind` file. Supports modern JSON format and legacy XML."""
    with zipfile.ZipFile(path, "r") as z:
        names = z.namelist()
        if _is_json_format(names):
            return _load_json(z)
        if _is_xml_format(names):
            raise UnsupportedFormatError(
                "Detected legacy XMind 2.0 XML format. "
                "Use xmindpy.convert.to_json() to migrate first."
            )
        raise ValueError(f"Unrecognized .xmind archive (members: {names[:5]})")


def load_from_stream(stream: IO[bytes]) -> Workbook:
    import io

    with zipfile.ZipFile(io.BytesIO(stream.read()), "r") as z:
        names = z.namelist()
        if _is_json_format(names):
            return _load_json(z)
        if _is_xml_format(names):
            raise UnsupportedFormatError(
                "Detected legacy XMind 2.0 XML format. "
                "Use xmindpy.convert.to_json() to migrate first."
            )
        raise ValueError(f"Unrecognized .xmind archive (members: {names[:5]})")


def _load_json(z: zipfile.ZipFile) -> Workbook:
    content_bytes = z.read("content.json")
    content = json.loads(content_bytes.decode("utf-8"))
    if not isinstance(content, list):
        raise ValueError(
            f"Invalid content.json: expected array of sheets, got {type(content).__name__}"
        )
    workbook = Workbook.from_content(content)
    if "metadata.json" in z.namelist():
        metadata = json.loads(z.read("metadata.json").decode("utf-8"))
        workbook.metadata = metadata
    return workbook


class UnsupportedFormatError(Exception):
    """Raised when the input file uses a format this library does not parse directly."""