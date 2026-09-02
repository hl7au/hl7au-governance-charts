"""Visual language shared by every diagram.

Change a value here and every generated SVG follows. Nothing in `diagrams/`
hard-codes a colour or a font size.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Theme:
    # Canvas — 16:9 so an SVG drops onto a widescreen slide edge to edge.
    width: int = 1920
    height: int = 1080
    margin: int = 46
    col_gap: int = 22

    font: str = "Segoe UI, Helvetica Neue, Arial, sans-serif"

    # Palette
    bg: str = "#f7f9fb"
    ink: str = "#12202e"
    muted: str = "#5b6b7c"
    line: str = "#bfcbd8"
    board_fill: str = "#08203a"
    tsc_fill: str = "#0f3557"
    tsc_header: str = "#0b2942"
    tsc_ink_muted: str = "#8fb3cf"
    tsc_bullet: str = "#5fa8d3"
    card_fill: str = "#ffffff"
    card_header: str = "#e8eef4"
    chip_fill: str = "#f4f8fb"
    chip_border: str = "#dbe4ec"

    # One accent per work group, cycled in the order work groups are listed.
    accents: tuple[str, ...] = ("#1f6f8b", "#2d7a5f", "#8a5a2b", "#6b4c93")

    # Type scale
    fs_title: int = 34
    fs_subtitle: int = 19
    fs_band: int = 27
    fs_card_title: int = 24
    fs_body: int = 23
    fs_role: int = 16
    fs_chip: int = 21

    # Set by `variant()`; when true the background rectangle is omitted.
    transparent: bool = False

    def variant(self, *, dark: bool = False, transparent: bool = False) -> "Theme":
        """A palette swap. Geometry and type scale are untouched."""
        theme = replace(self, **(DARK if dark else {}))
        return replace(theme, transparent=transparent)

    def accent(self, index: int) -> str:
        return self.accents[index % len(self.accents)]

    @property
    def content_width(self) -> int:
        return self.width - 2 * self.margin

    def column_width(self, columns: int) -> float:
        return (self.content_width - self.col_gap * (columns - 1)) / columns

    def column_x(self, index: int, columns: int) -> float:
        return self.margin + index * (self.column_width(columns) + self.col_gap)


# Dark palette — same hues, re-weighted so the cards sit above the page
# rather than glowing on it. Accents lift because they carry less area here.
DARK = dict(
    bg="#0d1520",
    ink="#e8eff6",
    muted="#8fa3b6",
    line="#2b3c4e",
    board_fill="#182b3f",
    tsc_fill="#22456a",
    tsc_header="#1a3552",
    tsc_ink_muted="#9dbdd6",
    tsc_bullet="#6fb6e0",
    card_fill="#16212e",
    card_header="#1e2c3b",
    chip_fill="#1b2836",
    chip_border="#2c3d4f",
    accents=("#4ea3c4", "#5cbc92", "#cf9558", "#a98ed6"),
)
