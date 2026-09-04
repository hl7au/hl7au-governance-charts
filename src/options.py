"""Render options — the query string, parsed and validated.

One object drives both the static build and the HTTP endpoints, so a URL
parameter and a build flag can never mean different things.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Mapping, Sequence

MAX_WIDTH = 4000
MIN_WIDTH = 320


def slug(text: str) -> str:
    """'AU Core Work Group' -> 'aucore'. Also strips a trailing 'workgroup'."""
    s = re.sub(r"[^a-z0-9]+", "", text.lower())
    return re.sub(r"workgroup$", "", s) or s


@dataclass(frozen=True)
class Options:
    groups: tuple[str, ...] = ()      # slugs, in the order given; empty = all, as listed
    date: str | None = None           # overrides Meta date in the subtitle
    title: str | None = None          # accessible name for the image
    dark: bool = False
    width: int | None = None          # rendered width in px; viewBox is unchanged
    transparent: bool = False

    @classmethod
    def from_query(cls, params: Mapping[str, Sequence[str] | str]) -> "Options":
        def one(key: str) -> str | None:
            v = params.get(key)
            if v is None:
                return None
            return (v[0] if isinstance(v, (list, tuple)) else v) or None

        def flag(key: str, default: bool) -> bool:
            v = one(key)
            if v is None:
                return default
            return v.strip().lower() in {"1", "true", "yes", "on"}

        groups = one("groups")
        width = one("w") or one("width")
        parsed_width = None
        if width:
            try:
                parsed_width = max(MIN_WIDTH, min(MAX_WIDTH, int(float(width))))
            except ValueError:
                parsed_width = None

        return cls(
            groups=tuple(slug(g) for g in groups.split(",") if g.strip()) if groups else (),
            date=one("date"),
            title=one("title"),
            dark=flag("dark", False) or (one("theme") or "").lower() == "dark",
            width=parsed_width,
            transparent=flag("transparent", False)
            or (one("bg") or "").lower() == "transparent",
        )

    def cache_key(self) -> str:
        """Stable string for ETag / cache filenames."""
        return "|".join([
            ",".join(self.groups), self.date or "", self.title or "",
            str(self.dark), str(self.width or ""),
            str(self.transparent),
        ])
