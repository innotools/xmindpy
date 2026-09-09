"""Convert legacy XMind 2.0 XML-format `.xmind` files to the modern JSON format."""

from __future__ import annotations

import json
import zipfile
from xml.etree import ElementTree as ET

from .workbook import Workbook, Sheet, Topic
from .saver import save_workbook

XML_NS = "{urn:xmind:xmap:xmlns:content:2.0}"


def to_json(src_path: str, dst_path: str) -> Workbook:
    """Read ``src_path`` (legacy XML) and save it as ``dst_path`` (modern JSON).

    Returns the migrated :class:`Workbook` so the caller can inspect it.
    """
    workbook = _read_legacy_xml(src_path)
    save_workbook(workbook, dst_path)
    return workbook


def _read_legacy_xml(path: str) -> Workbook:
    """Best-effort XML→JSON parser for the XMind 2.0 schema.

    Supports title, nested ``topic`` children, and ``notes/plain``. Other fields
    (markers, labels, relationships, hyperlinks) are best-effort: when present
    in the XML they are preserved; otherwise they are dropped.
    """
    with zipfile.ZipFile(path, "r") as z:
        with z.open("content.xml") as f:
            tree = ET.parse(f)
    root = tree.getroot()

    workbook = Workbook()
    for sheet_el in root.findall(f"{XML_NS}sheet"):
        title_el = sheet_el.find(f"{XML_NS}title")
        title = title_el.text if title_el is not None else "Sheet"
        topic_el = sheet_el.find(f"{XML_NS}topic")
        root_topic = _topic_from_xml(topic_el) if topic_el is not None else Topic(title=title)
        sheet = Sheet(title=title, root_topic=root_topic)
        workbook.sheets.append(sheet)
    return workbook


def _topic_from_xml(topic_el: ET.Element) -> Topic:
    title_el = topic_el.find(f"{XML_NS}title")
    title = title_el.text if title_el is not None else ""

    topic = Topic(title=title or "", id=topic_el.get("id", ""))

    children_el = topic_el.find(f"{XML_NS}children")
    if children_el is not None:
        topics_el = children_el.find(f"{XML_NS}topics")
        if topics_el is not None:
            for child_el in topics_el.findall(f"{XML_NS}topic"):
                topic.children.append(_topic_from_xml(child_el))

    notes_el = topic_el.find(f"{XML_NS}notes")
    if notes_el is not None:
        plain_el = notes_el.find(f"{XML_NS}plain")
        if plain_el is not None and plain_el.text:
            topic.notes = plain_el.text

    markers_el = topic_el.find(f"{XML_NS}marker-refs")
    if markers_el is not None:
        for marker_el in markers_el.findall(f"{XML_NS}marker-ref"):
            mid = marker_el.get("marker-id")
            if mid:
                topic.markers.append(mid)

    labels_el = topic_el.find(f"{XML_NS}labels")
    if labels_el is not None:
        for label_el in labels_el.findall(f"{XML_NS}label"):
            if label_el.text:
                topic.labels.append(label_el.text)

    return topic


def to_legacy_xml(src_path: str, dst_path: str) -> None:
    """Inverse of :func:`to_json`: write the workbook back as legacy XML.

    Useful if you still need to open the file with very old XMind builds (<2018)
    that predate the JSON format.
    """
    raise NotImplementedError(
        "Round-tripping back to legacy XML is not implemented. "
        "Modern XMind (>= 2018) supports the JSON format produced by save_workbook()."
    )