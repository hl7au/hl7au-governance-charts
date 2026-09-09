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
    bg: str = "#f4f5f8"
    ink: str = "#0c0c0c"
    muted: str = "#5a6069"
    line: str = "#d6d9df"
    board_fill: str = "#0c0c0c"
    tsc_fill: str = "#c72026"
    tsc_header: str = "#a8171d"
    tsc_ink_muted: str = "#fbe6e7"
    tsc_bullet: str = "#ffffff"
    card_fill: str = "#ffffff"
    card_header: str = "#eff1f5"
    chip_fill: str = "#f7f8fa"
    chip_border: str = "#e2e5ea"

    # One accent per work group, cycled in the order work groups are listed.
    accents: tuple[str, ...] = ("#c72026", "#c72026", "#c72026", "#c72026")

    # Type scale
    fs_date: int = 15
    fs_band: int = 27
    fs_card_title: int = 24
    fs_body: int = 23
    fs_role: int = 16
    fs_chip: int = 21
    fs_accelerator: int = 15

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
    bg="#101114",
    ink="#f0f1f3",
    muted="#9aa1ab",
    line="#2f333a",
    board_fill="#000000",
    tsc_fill="#b81d23",
    tsc_header="#8f1519",
    tsc_ink_muted="#f7d2d4",
    tsc_bullet="#ffffff",
    card_fill="#1a1c20",
    card_header="#23262b",
    chip_fill="#1f2228",
    chip_border="#31353d",
    accents=("#e5424a", "#e5424a", "#e5424a", "#e5424a"),
)
