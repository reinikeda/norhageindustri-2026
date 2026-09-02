"""Turn product specification text into table rows when possible."""

from __future__ import annotations

import re

ITEM_SPLIT = re.compile(r"(?:(?<=^)|(?<=\s))[-•]\s+")
PAIR_SPLIT = re.compile(r"\s+[–—]\s+|:\s+")


def specification_rows(product):
    stored = [
        (spec.label, spec.value)
        for spec in product.specifications.all()
        if spec.label and spec.value
    ]
    if stored:
        return stored
    rows, _notes = parse_specification_text(product.technical_text)
    return rows


def specification_notes(product):
    if product.specifications.exists():
        return product.technical_text
    _rows, notes = parse_specification_text(product.technical_text)
    return notes


def parse_specification_text(text):
    """Return (rows, leftover_notes) from admin text or imported bullets."""
    if not text or not str(text).strip():
        return [], ""
    text = str(text).strip()
    table_rows = _parse_markdown_table(text)
    if table_rows:
        return table_rows, ""

    chunks = [part.strip() for part in ITEM_SPLIT.split(text) if part.strip()]
    if len(chunks) == 1 and "\n" in text:
        chunks = [line.strip().lstrip("-• ").strip() for line in text.splitlines() if line.strip()]

    rows = []
    notes = []
    for chunk in chunks:
        pair = PAIR_SPLIT.split(chunk, maxsplit=1)
        if len(pair) == 2 and 1 <= len(pair[0]) <= 80 and pair[1].strip():
            rows.append((pair[0].strip(), pair[1].strip()))
        else:
            notes.append(chunk)
    return rows, " ".join(notes)


def _parse_markdown_table(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 3 or not lines[0].startswith("|"):
        return []
    separator = lines[1].replace(" ", "")
    if not re.match(r"^\|?:?-{3,}:?(\|:?-{3,}:?)*\|?$", separator):
        return []
    rows = []
    for line in lines[2:]:
        if "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 2 and cells[0] and cells[1]:
            rows.append((cells[0], cells[1]))
    return rows
