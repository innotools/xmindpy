# xmindpy

[English](README.md) | [简体中文](README.zh-CN.md)

Modern Python SDK for creating, reading, and editing **XMind 2020+** mind map files (JSON format).

This is a clean rewrite of [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) — the original library only supports the legacy XMind 2.0 XML format and **cannot produce files that XMind 2020/2022/2024 can open**. This fork replaces the XML DOM core with native Python objects and emits the JSON-based file format that modern XMind expects.

## Install

```bash
pip install xmindpy
```

## Quick start

```python
from xmindpy import Workbook, Topic

wb = Workbook()
sheet = wb.create_sheet("Project Plan")
root = Topic("Project Plan")
root.add(Topic("Research"))
root.add(Topic("Design"))
root.add(Topic("Build"))
sheet.root_topic = root

wb.save("plan.xmind")
```

Open `plan.xmind` in XMind 2020 or later — it just works.

## Loading

```python
from xmindpy import load_workbook

wb = load_workbook("plan.xmind")
for sheet in wb.sheets:
    print(sheet.title)
    print(sheet.root_topic.title)
```

## Convert legacy `.xmind` files (XML format)

```python
from xmindpy import convert
convert.to_json("legacy.xmind", "modern.xmind")
```

## API

| Class | Purpose |
|-------|---------|
| `Workbook` | Container for one or more sheets |
| `Sheet` | One mind map (tab) in the workbook |
| `Topic` | A node in the mind map; has children, notes, labels, markers |
| `load_workbook(path)` | Load an `.xmind` file (auto-detects JSON or legacy XML format) |
| `convert.to_json(src, dst)` | Migrate a legacy XML-format `.xmind` to modern JSON format |

## File format

The generated `.xmind` is a ZIP with:

| File | Purpose |
|------|---------|
| `mimetype` | Always `application/vnd.xmind.workbook` |
| `content.json` | Top-level array of sheets |
| `metadata.json` | `dataStructureVersion: "3"`, `layoutEngineVersion: "5"` |
| `manifest.json` | File-entry registry (`file-entries` object, `media-type` kebab-case) |
| `Thumbnails/thumbnail.png` | 1×1 transparent PNG (required by some parsers) |

This matches the format documented at the [XMind Wiki](https://github.com/xmindltd/xmind/wiki/XMindFileFormat).

## License

MIT — see [LICENSE](LICENSE).

Forked from [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) by Devin (MIT).