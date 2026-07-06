#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Render structured release notes content into the project's fixed-width .txt
format (80-char "=" dividers, aligned label/value fields, hanging-indent
wrapped text and lists) — the same visual style as docs/release-notes-*.txt.

This script owns formatting mechanics only (wrapping, column alignment,
divider placement). It has no opinion about section names, field labels, or
content — that's the caller's (the LLM's) judgment call, since the internal
and customer-facing templates use different headings and framing.

Input JSON shape (read from --input, default stdin):

{
  "title": "RELEASE NOTES",
  "header_fields": [["Product", "..."], ["Version", "..."], ["Release Date", "2026-06-10"]],
  "intro": "Optional 1-2 sentence summary paragraph, printed after the header.",
  "sections": [
    {
      "heading": "NEW FEATURES",
      "empty_text": "None.",
      "entries": [
        {
          "title": "Feature title",
          "fields": [
            {"label": "Description", "text": "What it does and why it matters."},
            {"label": "Details", "items": ["Detail one.", "Detail two."]}
          ]
        }
      ]
    },
    {
      "heading": "NEED HELP?",
      "body": "Freeform paragraph instead of entries, e.g. a support contact blurb."
    }
  ]
}

Rules:
- A section with `entries` renders each entry's title followed by its fields.
- A `text` field is an inline label: value pair, wrapped with a hanging indent;
  multiple text fields within one entry are column-aligned to each other.
- An `items` field renders as a bare "Label:" line followed by an indented
  list ("-" bullets, or "1." numbered if `"numbered": true`).
- A section with no `entries` and no `body` renders `empty_text` (default "None.").
- A section with `body` and no `entries` renders the body as a wrapped paragraph.

Usage:
    python3 render_release_notes.py -i content.json -o docs/release-notes-v1.0.0.txt
    cat content.json | python3 render_release_notes.py > docs/release-notes-v1.0.0.txt
"""

import argparse
import json
import sys
import textwrap

WIDTH = 80


def render_field_block(indent: int, label_width: int, label: str, text: str, width: int = WIDTH) -> list[str]:
    prefix = " " * indent + f"{(label + ':').ljust(label_width + 1)} "
    cont_indent = " " * len(prefix)
    wrapped = textwrap.wrap(text, width=max(width - len(prefix), 20)) or [""]
    lines = [prefix + wrapped[0]]
    lines.extend(cont_indent + w for w in wrapped[1:])
    return lines


def render_items_block(indent: int, label: str, items: list[str], numbered: bool, width: int = WIDTH) -> list[str]:
    lines = [" " * indent + f"{label}:"]
    item_indent = indent + 2
    markers = [f"{i + 1}." for i in range(len(items))] if numbered else ["-" for _ in items]
    marker_width = max((len(m) for m in markers), default=1)
    for marker, item in zip(markers, items):
        prefix = " " * item_indent + marker.ljust(marker_width) + " "
        cont_indent = " " * len(prefix)
        wrapped = textwrap.wrap(item, width=max(width - len(prefix), 20)) or [""]
        lines.append(prefix + wrapped[0])
        lines.extend(cont_indent + w for w in wrapped[1:])
    return lines


def render_entry(entry: dict, width: int = WIDTH) -> list[str]:
    lines = [entry["title"]]
    fields = entry.get("fields", [])
    text_fields = [f for f in fields if "text" in f]
    label_width = max((len(f["label"]) for f in text_fields), default=0)
    for field in fields:
        if "items" in field:
            lines.extend(render_items_block(2, field["label"], field["items"], field.get("numbered", False), width))
        else:
            lines.extend(render_field_block(2, label_width, field["label"], field.get("text", ""), width))
    return lines


def render_section(section: dict, width: int = WIDTH) -> list[str]:
    divider = "=" * width
    lines = [divider, section["heading"], divider, ""]
    entries = section.get("entries")
    if entries:
        for entry in entries:
            lines.extend(render_entry(entry, width))
            lines.append("")
    elif section.get("body"):
        lines.extend(textwrap.wrap(section["body"], width=width) or [""])
        lines.append("")
    else:
        lines.append(section.get("empty_text", "None."))
        lines.append("")
    return lines


def render_header(data: dict, width: int = WIDTH) -> list[str]:
    divider = "=" * width
    lines = [divider, data.get("title", "RELEASE NOTES"), divider, ""]
    header_fields = data.get("header_fields", [])
    label_width = max((len(label) + 1 for label, _ in header_fields), default=0)
    for label, value in header_fields:
        prefix = f"{(label + ':').ljust(label_width + 1)} "
        wrapped = textwrap.wrap(value, width=max(width - len(prefix), 20)) or [""]
        lines.append(prefix + wrapped[0])
        lines.extend(" " * len(prefix) + w for w in wrapped[1:])
    lines.append("")
    if data.get("intro"):
        lines.extend(textwrap.wrap(data["intro"], width=width))
        lines.append("")
    return lines


def render(data: dict, width: int = WIDTH) -> str:
    validate(data)
    lines = render_header(data, width)
    for section in data.get("sections", []):
        lines.extend(render_section(section, width))
    divider = "=" * width
    lines.extend([divider, "END OF RELEASE NOTES", divider])
    return "\n".join(lines) + "\n"


def validate(data: dict) -> None:
    if not isinstance(data.get("sections"), list) or not data["sections"]:
        raise ValueError("Input must include a non-empty 'sections' list")
    for section in data["sections"]:
        if "heading" not in section:
            raise ValueError(f"Section missing 'heading': {section}")
        for entry in section.get("entries", []):
            if "title" not in entry:
                raise ValueError(f"Entry missing 'title' in section '{section['heading']}': {entry}")
            for field in entry.get("fields", []):
                if "label" not in field:
                    raise ValueError(f"Field missing 'label' in entry '{entry['title']}': {field}")
                if "text" not in field and "items" not in field:
                    raise ValueError(f"Field '{field['label']}' needs 'text' or 'items': {field}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input", default="-", help="Path to input JSON, or '-' for stdin (default: stdin)")
    parser.add_argument("-o", "--output", default="-", help="Path to write rendered text, or '-' for stdout (default: stdout)")
    args = parser.parse_args()

    try:
        raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
        data = json.loads(raw)
        rendered = render(data)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output == "-":
        sys.stdout.write(rendered)
    else:
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(rendered)
        print(f"Wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
