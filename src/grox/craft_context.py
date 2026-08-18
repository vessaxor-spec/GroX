from __future__ import annotations

import hashlib
import re
from typing import Any


_WORD_RE = re.compile(r"[a-z0-9_-]+")
_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_MANDATORY_HEADINGS = ("Purpose", "Safety Boundaries", "GroX Operational Binding")
_FALLBACK_HEADINGS = ("Responsibilities", "Domain Context", "Identity")


def _words(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _frontmatter_value(card: str, key: str) -> str | None:
    if not card.startswith("---\n"):
        return None
    end = card.find("\n---\n", 4)
    if end < 0:
        return None
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", card[4:end], re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip('"\'') or None


def _sections(card: str) -> list[tuple[str, str]]:
    matches = list(_SECTION_RE.finditer(card))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(card)
        heading = match.group(1).strip()
        text = card[start:end].strip()
        if heading and text:
            sections.append((heading, text))
    return sections


def select_craft_context(
    card: str,
    objective: str,
    *,
    max_sections: int = 6,
    max_chars: int = 4500,
) -> dict[str, Any]:
    """Select bounded Mission-relevant specialist craft without granting authority.

    Selection is deterministic and lexical. Mandatory safety/operational sections
    are retained when present, then Mission-relevant sections are chosen by token
    overlap. If the objective has no useful overlap, stable craft fundamentals are
    used as bounded fallbacks. Complete craft cards are never injected by default.
    """
    max_sections = max(1, int(max_sections))
    max_chars = max(256, int(max_chars))
    sections = _sections(card)
    section_map = {heading: text for heading, text in sections}
    objective_words = _words(objective)

    selected_headings: list[str] = [
        heading for heading in _MANDATORY_HEADINGS if heading in section_map
    ]

    scored: list[tuple[int, int, str]] = []
    for position, (heading, text) in enumerate(sections):
        if heading in selected_headings:
            continue
        heading_overlap = len(objective_words & _words(heading))
        body_overlap = len(objective_words & _words(text))
        score = heading_overlap * 8 + body_overlap
        if score > 0:
            scored.append((-score, position, heading))
    scored.sort()

    for _, _, heading in scored:
        if heading not in selected_headings:
            selected_headings.append(heading)
        if len(selected_headings) >= max_sections:
            break

    if len(selected_headings) < max_sections:
        for heading in _FALLBACK_HEADINGS:
            if heading in section_map and heading not in selected_headings:
                selected_headings.append(heading)
            if len(selected_headings) >= max_sections:
                break

    selected_set = set(selected_headings[:max_sections])
    ordered = [(heading, text) for heading, text in sections if heading in selected_set]

    context: list[dict[str, Any]] = []
    used_chars = 0
    clipped = False
    for heading, text in ordered:
        remaining = max_chars - used_chars
        if remaining <= 0:
            clipped = True
            break
        chosen = text
        if len(chosen) > remaining:
            chosen = chosen[:remaining].rstrip()
            clipped = True
        if not chosen:
            continue
        context.append({"heading": heading, "content": chosen})
        used_chars += len(chosen)
        if used_chars >= max_chars:
            break

    full_sha = hashlib.sha256(card.encode("utf-8")).hexdigest()
    returned_headings = [item["heading"] for item in context]
    return {
        "schema": "grox-selective-craft-context-v1",
        "craft_sha256": full_sha,
        "source_revision": _frontmatter_value(card, "source_revision"),
        "freshness_policy": _frontmatter_value(card, "freshness_policy"),
        "selected_headings": returned_headings,
        "selected_sections": context,
        "selected_chars": used_chars,
        "card_chars": len(card),
        "max_sections": max_sections,
        "max_chars": max_chars,
        "full_card_injected": False,
        "truncated": clipped or len(returned_headings) < len(sections) or used_chars < len(card),
    }
