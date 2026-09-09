"""Smoke tests: build a workbook, save it, load it back, compare."""

from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

from xmindpy import Workbook, Topic, load_workbook


def _build_workbook() -> Workbook:
    wb = Workbook()
    sheet = wb.create_sheet("外综服平台")
    root = sheet.root_topic

    c1 = Topic("一、项目总览：四川制造+川品云销 内外贸一体化B2B2C平台")
    c1.add(Topic("政策底座：川经信专报〔2025〕218号川品云销方案"))
    c1.add(Topic("核心原则：一企一档一窗，单套企业工作台，内外贸一体化，不拆分两套后台"))
    root.add(c1)

    c4 = Topic("四、企业一体化工作台")
    sub = Topic("④外贸业务子模块（集成丝路易购能力）")
    sub.add(Topic("AI海外客户匹配（海关数据+海外第三方采购数据）"))
    sub.add(Topic("海外云仓库存调度"))
    c4.add(sub)
    root.add(c4)
    return wb


def test_save_and_load_roundtrip() -> None:
    wb = _build_workbook()

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "wb.xmind"
        wb.save(str(out))

        # Archive structure check
        with zipfile.ZipFile(out) as z:
            names = z.namelist()
            assert names[0] == "mimetype", f"mimetype must be first entry, got {names[0]}"
            assert "content.json" in names
            assert "metadata.json" in names
            assert "manifest.json" in names
            assert "Thumbnails/thumbnail.png" in names

            content = json.loads(z.read("content.json"))
            assert isinstance(content, list)
            assert len(content) == 1
            assert content[0]["class"] == "sheet"
            assert content[0]["title"] == "外综服平台"

            metadata = json.loads(z.read("metadata.json"))
            assert metadata["dataStructureVersion"] == "3"
            assert metadata["layoutEngineVersion"] == "5"

            manifest = json.loads(z.read("manifest.json"))
            entries = manifest["file-entries"]
            assert "content.json" in entries
            assert entries["content.json"]["media-type"] == "application/json"

        loaded = load_workbook(str(out))
        assert len(loaded.sheets) == 1
        sheet = loaded.sheets[0]
        assert sheet.title == "外综服平台"
        root = sheet.root_topic
        assert root.title == "外综服平台"
        assert len(root.children) == 2
        # Drill into the nested ④ sub-module
        c4 = root.children[1]
        assert "企业一体化工作台" in c4.title
        foreign = c4.children[0]
        assert foreign.title.startswith("④外贸业务子模块")
        assert any(c.title.startswith("AI海外客户匹配") for c in foreign.children)


def test_minimal_workbook() -> None:
    """Empty-style workbook with one topic should serialize without errors."""
    wb = Workbook()
    sheet = wb.create_sheet("Plan")
    sheet.root_topic.add(Topic("Step 1"))
    sheet.root_topic.add(Topic("Step 2"))

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "minimal.xmind"
        wb.save(str(out))
        loaded = load_workbook(str(out))
        assert loaded.sheets[0].root_topic.children[0].title == "Step 1"


def test_unknown_fields_are_preserved() -> None:
    """Topics and sheets with unrecognized JSON fields round-trip unchanged.

    Forward-compat guarantee: if XMind adds a new feature (callouts,
    summaries, boundaries, image refs, ...) and the user has saved a file
    with it, xmindpy will load and re-save it without losing the data,
    even if we don't model those features yet.
    """
    raw_content = [
        {
            "id": "sheet-1",
            "class": "sheet",
            "title": "Future-proof sheet",
            "futureSheetFlag": {"weird": [1, 2, 3]},
            "rootTopic": {
                "id": "root-1",
                "class": "topic",
                "title": "Root",
                "callouts": {"attached": [{"title": "Important!"}]},
                "summary": [{"range": "root-1/child-a", "label": "Summary"}],
                "image": "xap:resources/future-image.png",
                "children": {
                    "attached": [
                        {"id": "child-a", "class": "topic", "title": "Child"}
                    ]
                },
            },
        }
    ]

    wb = Workbook.from_content(raw_content)
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "future.xmind"
        wb.save(str(out))

        with zipfile.ZipFile(out) as z:
            saved = json.loads(z.read("content.json"))

        sheet = saved[0]
        assert sheet["futureSheetFlag"] == {"weird": [1, 2, 3]}, "sheet-level extras dropped"
        root = sheet["rootTopic"]
        assert "callouts" in root, "topic-level callouts dropped"
        assert root["summary"][0]["label"] == "Summary", "summary dropped"
        assert root["image"] == "xap:resources/future-image.png", "image ref dropped"

        # And round-tripping again stays stable.
        loaded = load_workbook(str(out))
        loaded.save(out)
        with zipfile.ZipFile(out) as z:
            saved2 = json.loads(z.read("content.json"))
        assert saved2[0]["futureSheetFlag"] == {"weird": [1, 2, 3]}
        assert saved2[0]["rootTopic"]["summary"][0]["label"] == "Summary"