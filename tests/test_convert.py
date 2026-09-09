"""Legacy XML → modern JSON conversion test.

Builds a tiny legacy-format `.xmind` in-memory and verifies xmindpy can convert
it into a file that the modern XMind app can open.
"""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from xmindpy import load_workbook
from xmindpy.convert import to_json


def _build_legacy_xmind_xml() -> str:
    """Return the contents of a minimal but valid XMind 2.0 content.xml."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0">
  <sheet id="sheet-1">
    <title>Legacy Sheet</title>
    <topic id="root-1">
      <title>Central Topic</title>
      <children>
        <topics type="attached">
          <topic id="a">
            <title>Branch A</title>
            <children>
              <topics type="attached">
                <topic id="a1"><title>Leaf A1</title></topic>
              </topics>
            </children>
          </topic>
          <topic id="b"><title>Branch B</title></topic>
        </topics>
      </children>
    </topic>
  </sheet>
</xmap-content>
"""


def _make_legacy_xmind(path: Path) -> None:
    """Write a tiny but real XMind 2.0 archive (legacy XML format)."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        z.writestr(info, "application/vnd.xmind.workbook")
        z.writestr("content.xml", _build_legacy_xmind_xml())
        z.writestr("meta.xml", "<?xml version=\"1.0\"?><xmap-meta/>")
        z.writestr("META-INF/manifest.xml", "<?xml version=\"1.0\"?><manifest/>")
        z.writestr("styles.xml", "<?xml version=\"1.0\"?><xmap-styles/>")


def test_convert_xml_to_json() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "legacy.xmind"
        dst = Path(tmpdir) / "modern.xmind"
        _make_legacy_xmind(src)

        wb = to_json(str(src), str(dst))

        # Old file shouldn't be loadable by the new loader directly.
        try:
            load_workbook(str(src))
        except Exception as exc:
            assert "legacy" in str(exc).lower() or "xml" in str(exc).lower(), exc
        else:
            raise AssertionError("expected load_workbook to reject legacy XML format")

        # The converted file must load.
        loaded = load_workbook(str(dst))
        assert loaded.sheets[0].title == "Legacy Sheet"
        root = loaded.sheets[0].root_topic
        assert root.title == "Central Topic"
        assert [c.title for c in root.children] == ["Branch A", "Branch B"]
        assert root.children[0].children[0].title == "Leaf A1"