"""Parse `governance.md` into the model the diagrams draw from.

The markdown is deliberately plain: headings for structure, bullets for content.
Prose between headings is ignored, so the source file can carry its own
instructions without confusing the parser.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

# "Name — Role", "Name -- Role" and "Name - Role" all split the same way.
ROLE_SPLIT = re.compile(r"\s+(?:—|–|--|-)\s+")
BULLET = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


@dataclass
class Member:
    name: str
    role: str | None = None


@dataclass
class WorkGroup:
    name: str
    cochairs: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)


@dataclass
class Model:
    title: str = "HL7 Australia"
    meta: dict[str, str] = field(default_factory=dict)
    tsc: list[Member] = field(default_factory=list)
    work_groups: list[WorkGroup] = field(default_factory=list)

    @property
    def date(self) -> str:
        return self.meta.get("date", "")

    @property
    def board(self) -> str:
        return self.meta.get("board", "HL7 Australia Board")

    @property
    def tsc_title(self) -> str:
        return self.meta.get("tsc-title", "AU Technical Steering Committee (AU-TSC)")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def parse(markdown: str) -> Model:
    model = Model()
    section = None          # 'meta' | 'tsc' | 'workgroups'
    subsection = None       # 'cochairs' | 'projects'
    current_wg: WorkGroup | None = None

    for raw in markdown.splitlines():
        heading = HEADING.match(raw)
        if heading:
            level, text = len(heading.group(1)), heading.group(2)
            if level == 1:
                model.title = text
            elif level == 2:
                key = _slug(text)
                section = {"meta": "meta", "autsc": "tsc", "tsc": "tsc",
                           "workgroups": "workgroups"}.get(key)
                current_wg, subsection = None, None
            elif level == 3 and section == "workgroups":
                current_wg = WorkGroup(name=text)
                model.work_groups.append(current_wg)
                subsection = None
            elif level == 4 and current_wg is not None:
                key = _slug(text)
                subsection = {"cochairs": "cochairs", "chairs": "cochairs",
                              "projects": "projects"}.get(key)
            continue

        bullet = BULLET.match(raw)
        if not bullet:
            continue
        item = bullet.group(1)

        if section == "meta":
            if ":" in item:
                key, value = item.split(":", 1)
                model.meta[key.strip().lower()] = value.strip()
        elif section == "tsc":
            parts = ROLE_SPLIT.split(item, maxsplit=1)
            model.tsc.append(Member(parts[0].strip(),
                                    parts[1].strip() if len(parts) > 1 else None))
        elif section == "workgroups" and current_wg is not None:
            if subsection == "cochairs":
                current_wg.cochairs.append(item)
            elif subsection == "projects":
                current_wg.projects.append(item)

    return model


def select(model: Model, slugs: Sequence[str]) -> Model:
    """Filtered, re-ordered copy. Unknown slugs are ignored; empty means all."""
    if not slugs:
        return model
    from .options import slug as _slug

    index = {_slug(wg.name): wg for wg in model.work_groups}
    chosen = [index[s] for s in slugs if s in index]
    if not chosen:
        return model
    return Model(title=model.title, meta=model.meta, tsc=model.tsc, work_groups=chosen)


def parse_file(path: str | Path) -> Model:
    return parse(Path(path).read_text(encoding="utf-8"))
