"""Native Python object model for an XMind workbook."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


def _new_id() -> str:
    return str(uuid.uuid4())


# Fields we know how to round-trip; everything else lands in ``_extras``.
_KNOWN_TOPIC_KEYS = frozenset({
    "id", "class", "title", "styleId", "labels", "markers", "notes",
    "hyperlinks", "children", "detached",
})


@dataclass
class Topic:
    """A node in the mind map.

    Children are stored on ``self.children`` as a list of ``Topic`` instances.
    Detached floating topics go on ``self.detached`` (rare; mirrors XMind's
    "free" topic positioning).

    Unrecognized JSON fields (e.g. ``callout``, ``summary``, ``boundary``,
    image references) loaded from a file are preserved in ``self._extras``
    and re-emitted on save, so the library is forward-compatible with
    XMind features we don't model explicitly.
    """

    title: str
    id: str = field(default_factory=_new_id)
    children: list[Topic] = field(default_factory=list)
    detached: list[Topic] = field(default_factory=list)
    notes: str | None = None
    labels: list[str] = field(default_factory=list)
    markers: list[str] = field(default_factory=list)
    style_id: str | None = None
    hyperlinks: list[str] = field(default_factory=list)
    _extras: dict[str, Any] = field(default_factory=dict)

    def add(self, topic: Topic) -> Topic:
        self.children.append(topic)
        return topic

    def add_detached(self, topic: Topic) -> Topic:
        self.detached.append(topic)
        return topic

    # --- serialization helpers --------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "class": "topic",
            "title": self.title,
        }
        if self.style_id:
            data["styleId"] = self.style_id
        if self.labels:
            data["labels"] = list(self.labels)
        if self.markers:
            data["markers"] = [{"markerId": m} for m in self.markers]
        if self.notes:
            data["notes"] = {"plain": {"content": self.notes}}
        if self.hyperlinks:
            data["hyperlinks"] = [
                {"href": h, "description": h} for h in self.hyperlinks
            ]
        if self.children:
            data["children"] = {"attached": [c.to_dict() for c in self.children]}
        if self.detached:
            data["detached"] = [t.to_dict() for t in self.detached]
        # Preserve any unrecognized fields as-is (callouts, summaries, etc.)
        data.update(self._extras)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Topic:
        topic = cls(
            title=data.get("title", ""),
            id=data.get("id") or _new_id(),
        )
        if "styleId" in data:
            topic.style_id = data["styleId"]
        if "labels" in data:
            topic.labels = list(data["labels"])
        if "markers" in data:
            topic.markers = [m["markerId"] for m in data["markers"] if "markerId" in m]
        if "notes" in data:
            plain = data["notes"].get("plain", {})
            topic.notes = plain.get("content")
        if "hyperlinks" in data:
            topic.hyperlinks = [h.get("href", "") for h in data["hyperlinks"]]
        children = data.get("children", {}).get("attached", [])
        topic.children = [cls.from_dict(c) for c in children]
        detached = data.get("detached", [])
        topic.detached = [cls.from_dict(t) for t in detached]
        # Save any unknown keys so re-save doesn't drop them.
        topic._extras = {k: v for k, v in data.items() if k not in _KNOWN_TOPIC_KEYS}
        return topic


# Same pattern for Sheet: keep unknown fields round-trippable.
_KNOWN_SHEET_KEYS = frozenset({
    "id", "class", "title", "rootTopic", "relationships",
})


@dataclass
class Sheet:
    """One tab / mind map in the workbook.

    Unrecognized JSON fields are preserved in ``self._extras`` so the library
    is forward-compatible with XMind features we don't model explicitly.
    """

    title: str
    root_topic: Topic
    id: str = field(default_factory=_new_id)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    _extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "class": "sheet",
            "title": self.title,
            "rootTopic": self.root_topic.to_dict(),
            "relationships": list(self.relationships),
        }
        data.update(self._extras)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sheet:
        root = Topic.from_dict(data["rootTopic"])
        sheet = cls(
            title=data.get("title", "Sheet"),
            root_topic=root,
            id=data.get("id") or _new_id(),
            relationships=list(data.get("relationships", [])),
        )
        sheet._extras = {k: v for k, v in data.items() if k not in _KNOWN_SHEET_KEYS}
        return sheet


@dataclass
class Workbook:
    """Container of one or more sheets."""

    sheets: list[Sheet] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def create_sheet(self, title: str = "Sheet") -> Sheet:
        sheet = Sheet(
            title=title,
            root_topic=Topic(title=title),
        )
        self.sheets.append(sheet)
        return sheet

    def to_content(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.sheets]

    def save(self, path: str) -> None:
        """Save to a file in modern XMind JSON format."""
        from .saver import save_workbook
        save_workbook(self, path)

    @classmethod
    def from_content(cls, content: list[dict[str, Any]]) -> Workbook:
        wb = cls()
        for sheet_data in content:
            wb.sheets.append(Sheet.from_dict(sheet_data))
        return wb