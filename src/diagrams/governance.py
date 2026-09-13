"""Governance view — the Board, the AU-TSC beneath it, and the work groups.

Structure only: the Board names its members, the levels below are named but not
populated. It answers "who governs what", where the co-chairs view answers
"who is on what".
"""
from __future__ import annotations

from ..options import Options
from ..parse import Model
from ..theme import Theme
from .base import Canvas, fit_size

BOARD_COLUMNS = 4
BOARD_HEADER = 66
BOARD_ROW = 62
BOARD_PAD = 34
BAND_HEIGHT = 100
CARD_HEIGHT = 250
CARD_HEADER = 4          # the accent rule; the name sits in the card body
GAP = 92


def render(model: Model, theme: Theme | None = None,
           options: Options | None = None) -> str:
    o = options or Options()
    t = (theme or Theme()).variant(dark=o.dark, transparent=o.transparent)
    c = Canvas(t)
    columns = len(model.work_groups)
    members = model.board_members

    c.title_block(o.title or f"{model.board}, AU Technical Steering Committee "
                             f"and Work Groups")

    rows = -(-len(members) // BOARD_COLUMNS) if members else 0
    board_h = BOARD_HEADER + (BOARD_PAD + rows * BOARD_ROW if rows else 0)

    # Three levels and two connector gaps; centre the stack so the leftover
    # space sits above and below rather than pooling at the bottom.
    stack = board_h + GAP + BAND_HEIGHT + GAP + CARD_HEIGHT
    top = max(t.margin, (t.height - stack) / 2)

    # ---- Board: black header, members below on the card ------------------
    board_y = top
    c.rect(t.margin, board_y, t.content_width, board_h, fill=t.card_fill, rx=12,
           stroke=t.line, stroke_width=1.5)
    c.top_rounded(t.margin, board_y, t.content_width, BOARD_HEADER,
                  fill=t.board_fill)
    c.text(t.width / 2, board_y + 43, model.board, size=t.fs_band,
           fill="#ffffff", anchor="middle", weight="700")

    inner_x = t.margin + 40
    inner_w = (t.content_width - 80) / BOARD_COLUMNS
    for i, member in enumerate(members):
        x = inner_x + (i % BOARD_COLUMNS) * inner_w
        y = board_y + BOARD_HEADER + 52 + (i // BOARD_COLUMNS) * BOARD_ROW
        c.add(f'<circle cx="{x+5:.1f}" cy="{y-8:.1f}" r="4.5" fill="{t.accent(0)}"/>')
        size = fit_size(member.name, inner_w - 46, t.fs_body, min_size=16)
        c.text(x + 22, y, member.name, size=size, fill=t.ink)
        if member.role:
            c.text(x + 22, y + 23, member.role, size=t.fs_role, fill=t.muted)

    # ---- AU-TSC: the band only, no membership ----------------------------
    tsc_y = board_y + board_h + GAP
    c.line(f"M{t.width/2:.1f} {board_y + board_h} V{tsc_y}")
    c.band(tsc_y, BAND_HEIGHT, model.tsc_title, t.tsc_fill)

    # ---- Work groups: named, not populated -------------------------------
    card_y = tsc_y + BAND_HEIGHT + GAP
    c.connectors(tsc_y + BAND_HEIGHT, card_y, columns)
    for i, wg in enumerate(model.work_groups):
        x, w = t.column_x(i, columns), t.column_width(columns)
        c.rect(x, card_y, w, CARD_HEIGHT, fill=t.card_fill, rx=12,
               stroke=t.line, stroke_width=1.5)
        c.rect(x, card_y, w, CARD_HEADER, fill=t.accent(i), rx=2)
        size = fit_size(wg.name, w - 44, 26, min_size=16, bold=True)
        c.text(x + w / 2, card_y + CARD_HEIGHT / 2 + size * 0.35, wg.name,
               size=size, fill=t.ink, anchor="middle", weight="700")

    c.footer_date(o.date or model.date)
    return c.render(display_width=o.width)
