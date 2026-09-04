"""SVG primitives shared by the diagrams.

Everything is plain string building — no dependencies, so `python build.py`
works on a bare interpreter.
"""
from __future__ import annotations

from ..theme import Theme


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# Average glyph width as a fraction of font size, calibrated for the
# Segoe UI / Arial stack. Bold runs a little wider.
CHAR_WIDTH = 0.55
CHAR_WIDTH_BOLD = 0.60


def text_width(text: str, font_size: float, bold: bool = False) -> float:
    return len(text) * font_size * (CHAR_WIDTH_BOLD if bold else CHAR_WIDTH)


def fit_size(text: str, max_width: float, base_size: float,
             min_size: float = 15, bold: bool = False) -> float:
    """Largest size at or below `base_size` that keeps `text` inside `max_width`."""
    size = base_size
    while size > min_size and text_width(text, size, bold) > max_width:
        size -= 0.5
    return size


def wrap(text: str, max_width: float, font_size: float) -> list[str]:
    """Greedy wrap using an average glyph width. Good enough for short labels."""
    char_width = font_size * CHAR_WIDTH
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if len(candidate) * char_width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """Accumulates SVG elements and renders the document."""

    def __init__(self, theme: Theme):
        self.t = theme
        self._parts: list[str] = []

    def add(self, markup: str) -> None:
        self._parts.append(markup)

    # -- primitives ----------------------------------------------------
    def text(self, x: float, y: float, content: str, *, size: float,
             fill: str, anchor: str = "start", weight: str = "normal") -> None:
        w = f' font-weight="{weight}"' if weight != "normal" else ""
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}"{a} font-size="{size}"{w} '
                 f'fill="{fill}">{esc(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, stroke_width: float = 1) -> None:
        s = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ""
        r = f' rx="{rx}"' if rx else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{r} '
                 f'fill="{fill}"{s}/>')

    def top_rounded(self, x: float, y: float, w: float, h: float, *, fill: str,
                    radius: float = 12) -> None:
        """A band with only its top corners rounded — used for card headers."""
        self.add(f'<path d="M{x+radius:.1f} {y:.1f} h{w-2*radius:.1f} '
                 f'a{radius},{radius} 0 0 1 {radius},{radius} v{h-radius:.1f} '
                 f'h{-w:.1f} v{-(h-radius):.1f} '
                 f'a{radius},{radius} 0 0 1 {radius},{-radius} z" fill="{fill}"/>')

    def line(self, path: str) -> None:
        self.add(f'<path d="{path}" stroke="{self.t.line}" stroke-width="3" fill="none"/>')

    # -- composites ----------------------------------------------------
    def footer_date(self, date: str) -> None:
        """Small date stamp, bottom right, inside the canvas.

        It sits in the bottom margin the cards already leave clear, so it costs
        the diagram no drawing space.
        """
        if not date:
            return
        t = self.t
        self.text(t.width - t.margin, t.height - 24, date,
                  size=t.fs_date, fill=t.muted, anchor="end")

    def band(self, y: float, height: float, label: str, fill: str) -> None:
        """A full-width bar with a centred label — the Board and TSC rows."""
        t = self.t
        self.rect(t.margin, y, t.content_width, height, fill=fill, rx=12)
        self.text(t.width / 2, y + height / 2 + 10, label, size=t.fs_band,
                  fill="#ffffff", anchor="middle", weight="700")

    def connectors(self, from_y: float, to_y: float, columns: int) -> None:
        """Centre stem, horizontal bus, and a drop into each column."""
        t = self.t
        bus_y = from_y + (to_y - from_y) * 0.55
        centres = [t.column_x(i, columns) + t.column_width(columns) / 2
                   for i in range(columns)]
        self.line(f"M{t.width/2:.1f} {from_y:.1f} V{bus_y:.1f}")
        self.line(f"M{centres[0]:.1f} {bus_y:.1f} H{centres[-1]:.1f}")
        for cx in centres:
            self.line(f"M{cx:.1f} {bus_y:.1f} V{to_y:.1f}")

    def card(self, index: int, columns: int, y: float, height: float,
             title: str, *, header_height: float = 74) -> tuple[float, float]:
        """Draw a work group card and return its (x, width)."""
        t = self.t
        x, w = t.column_x(index, columns), t.column_width(columns)
        self.rect(x, y, w, height, fill=t.card_fill, rx=12, stroke=t.line, stroke_width=1.5)
        self.top_rounded(x, y, w, header_height, fill=t.card_header)
        self.rect(x, y + header_height, w, 4, fill=t.accent(index))

        # Narrow columns: shrink the title, then wrap it, rather than let it
        # bleed past the card edge.
        avail = w - 28
        size = fit_size(title, avail, t.fs_card_title, min_size=15, bold=True)
        lines = [title] if text_width(title, size, bold=True) <= avail \
            else wrap(title, avail, size)
        leading = size * 1.15
        first = y + header_height / 2 + size * 0.35 - (len(lines) - 1) * leading / 2
        for k, line in enumerate(lines):
            self.text(x + w / 2, first + k * leading, line,
                      size=size, fill=t.ink, anchor="middle", weight="700")
        return x, w

    def render(self, *, display_width: int | None = None) -> str:
        """Serialise. `display_width` only changes the width/height attributes —
        the viewBox stays 1920x1080, so the drawing scales rather than reflows."""
        t = self.t
        w = display_width or t.width
        h = round(w * t.height / t.width)
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {t.width} {t.height}" '
                f'width="{w}" height="{h}" role="img" font-family="{t.font}">')
        body = "" if t.transparent else \
            f'<rect width="{t.width}" height="{t.height}" fill="{t.bg}"/>'
        return "\n".join([head + body, *self._parts, "</svg>"])

    def title_block(self, label: str) -> None:
        """Accessible name for the whole image — screen readers and alt text."""
        self.add(f"<title>{esc(label)}</title>")


def centred_block(area_top: float, area_height: float, count: int,
                  pitch: float) -> float:
    """Top edge of `count` items of `pitch` height, centred in the area.

    Keeps a card with two entries from looking like a card that lost its content.
    """
    return area_top + (area_height - count * pitch) / 2
