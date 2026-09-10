# xmindpy

用于创建、读取和编辑 **XMind 2020+** 思维导图文件（JSON 格式）的现代 Python SDK。

本项目是对 [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) 的干净重写 —— 原版库仅支持旧的 XMind 2.0 XML 格式，**无法生成 XMind 2020/2022/2024 能打开的文件**。本 fork 用原生 Python 对象替换了 XML DOM 核心，并输出现代 XMind 所期望的 JSON 格式文件。

[English](README.md) | [简体中文](README.zh-CN.md)

## 安装

```bash
pip install xmindpy
```

## 快速开始

```python
from xmindpy import Workbook, Topic

wb = Workbook()
sheet = wb.create_sheet("项目计划")
root = Topic("项目计划")
root.add(Topic("调研"))
root.add(Topic("设计"))
root.add(Topic("开发"))
sheet.root_topic = root

wb.save("plan.xmind")
```

在 XMind 2020 或更高版本中打开 `plan.xmind` 即可正常使用。

## 加载

```python
from xmindpy import load_workbook

wb = load_workbook("plan.xmind")
for sheet in wb.sheets:
    print(sheet.title)
    print(sheet.root_topic.title)
```

## 转换旧版 `.xmind` 文件（XML 格式）

```python
from xmindpy import convert
convert.to_json("legacy.xmind", "modern.xmind")
```

## API

| 类 | 用途 |
|-------|---------|
| `Workbook` | 工作簿容器，包含一个或多个 sheet |
| `Sheet` | 工作簿中的一个思维导图（tab） |
| `Topic` | 思维导图节点，包含子节点、备注、标签、标记 |
| `load_workbook(path)` | 加载 `.xmind` 文件（自动识别 JSON 或旧版 XML 格式） |
| `convert.to_json(src, dst)` | 将旧版 XML 格式 `.xmind` 迁移为现代 JSON 格式 |

## 文件格式

生成的 `.xmind` 是一个 ZIP 包，包含：

| 文件 | 用途 |
|------|---------|
| `mimetype` | 始终为 `application/vnd.xmind.workbook` |
| `content.json` | 顶层 sheet 数组 |
| `metadata.json` | `dataStructureVersion: "3"`，`layoutEngineVersion: "5"` |
| `manifest.json` | 文件条目注册表（`file-entries` 对象，`media-type` kebab-case） |
| `Thumbnails/thumbnail.png` | 1×1 透明 PNG（部分解析器要求） |

与 [XMind Wiki](https://github.com/xmindltd/xmind/wiki/XMindFileFormat) 文档中描述的格式一致。

## 协议

MIT —— 详见 [LICENSE](LICENSE)。

Forked from [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) by Devin (MIT).
