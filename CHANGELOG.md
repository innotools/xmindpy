# Changelog

All notable changes to xmindpy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-10

### Added

- Initial release.
- `Workbook`, `Sheet`, `Topic` dataclasses with `Workbook.create_sheet` /
  `Workbook.add_sheet` for in-memory building.
- `Workbook.save(path)` and `save_to_stream(stream)` emitting the XMind 2020+
  JSON format (mimetype, content.json, metadata.json, manifest.json,
  Thumbnails/thumbnail.png).
- `load_workbook(path)` and `load_from_stream(stream)` reading any XMind
  workbook (auto-detects JSON or legacy XML format).
- Topic fields: `title`, `id`, `children`, `detached`, `notes`, `labels`,
  `markers`, `style_id`, `hyperlinks`.
- `convert.to_json(src, dst)` and `convert.to_legacy_xml(src, dst)` for
  migrating between legacy XML and modern JSON formats.
- Forward-compat: unknown JSON fields on `Topic` / `Sheet` are preserved on
  round-trip.
- GitHub Actions: pytest matrix (3.10 / 3.11 / 3.12) on push and PR;
  trusted-publishing release to PyPI on `v*` tags.

### Notes

- Forked from [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) by
  Devin (MIT). The XML DOM core was replaced with native Python objects so the
  library emits the JSON-based file format that XMind 2020 / 2022 / 2024 expects.
