"""Co-chairs view — AU-TSC membership above the work groups and their co-chairs."""
from __future__ import annotations

from ..options import Options
from ..parse import Model
from ..theme import Theme
from .base import Canvas, centred_block, fit_size

TSC_COLUMNS = 4
TSC_HEADER = 62
TSC_ROW = 50
CARD_HEADER = 74


def render(model: Model, theme: Theme | None = None,
           options: Options | None = None) -> str:
    o = options or Options()
    t = (theme or Theme()).variant(dark=o.dark, transparent=o.transparent)
    c = Canvas(t)
    columns = len(model.work_groups)

    title = o.title or model.title
    subtitle = (f"AU Technical Steering Committee and Work Group co-chairs · "
                f"{o.date or model.date}").rstrip(" ·")
    c.title_block(f"{title}. {subtitle}")
    if o.header:
        c.header(title, subtitle)

    # ---- AU-TSC band, members in a grid -----------------------------
    rows = -(-len(model.tsc) // TSC_COLUMNS)
    tsc_y = 122 if o.header else t.margin
    tsc_h = TSC_HEADER + 26 + rows * TSC_ROW + 18
    c.rect(t.margin, tsc_y, t.content_width, tsc_h, fill=t.tsc_fill, rx=12)
    c.top_rounded(t.margin, tsc_y, t.content_width, TSC_HEADER, fill=t.tsc_header)
    c.text(t.margin + 30, tsc_y + 41, model.tsc_title, size=26, fill="#ffffff", weight="700")

    inner_x = t.margin + 30
    inner_w = (t.content_width - 60) / TSC_COLUMNS
    for i, member in enumerate(model.tsc):
        x = inner_x + (i % TSC_COLUMNS) * inner_w
        y = tsc_y + TSC_HEADER + 48 + (i // TSC_COLUMNS) * TSC_ROW
        c.add(f'<circle cx="{x+5:.1f}" cy="{y-8:.1f}" r="4.5" fill="{t.tsc_bullet}"/>')
        c.text(x + 22, y, member.name, size=t.fs_body, fill="#ffffff")
        if member.role:
            c.text(x + 22, y + 22, member.role, size=t.fs_role, fill=t.tsc_ink_muted)

    # ---- work group cards -------------------------------------------
    card_y = tsc_y + tsc_h + 70
    card_h = t.height - card_y - t.margin
    c.connectors(tsc_y + tsc_h, card_y, columns)

    area_top = card_y + CARD_HEADER + 20
    area_h = card_h - CARD_HEADER - 46
    pitch = area_h / max(len(wg.cochairs) for wg in model.work_groups)

    for i, wg in enumerate(model.work_groups):
        x, w = c.card(i, columns, card_y, card_h, wg.name, header_height=CARD_HEADER)
        top = centred_block(area_top, area_h, len(wg.cochairs), pitch)
        for j, name in enumerate(wg.cochairs):
            size = fit_size(name, w - 36, t.fs_body, min_size=15)
            c.text(x + w / 2, top + pitch * (j + 0.5) + 8, name,
                   size=size, fill=t.ink, anchor="middle")

    return c.render(display_width=o.width)
