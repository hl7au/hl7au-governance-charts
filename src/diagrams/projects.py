"""Projects view — Board and AU-TSC above each work group's projects."""
from __future__ import annotations

from ..options import Options
from ..parse import Model
from ..theme import Theme
from .base import Canvas, wrap

BAND_HEIGHT = 92
BAND_GAP = 22
CARD_HEADER = 74
CARD_PAD = 26
CHIP_HEIGHT = 84          # preferred height; shrinks only if a column is full
CHIP_GAP = 20
MIN_CHIP_GAP = 10
LINE_HEIGHT = 26
ACCELERATOR_HEIGHT = 22   # the extra line a project with an accelerator needs


def _chip_metrics(model: Model, theme: Theme, chip_width: float,
                  area_height: float) -> tuple[float, float]:
    """Chip height and gap — uniform across the whole diagram.

    Chips grow to fit the longest label and, if any project names an
    accelerator, the extra line every chip reserves so they stay a set. They
    give that back if a column would otherwise run past the bottom of its card.
    """
    projects = [p for wg in model.work_groups for p in wg.projects]
    lines = max((len(wrap(p.name, chip_width - 46, theme.fs_chip))
                 for p in projects), default=1)
    extra = ACCELERATOR_HEIGHT if any(p.accelerator for p in projects) else 0
    height = max(CHIP_HEIGHT, lines * LINE_HEIGHT + 34 + extra)
    gap = CHIP_GAP
    count = max((len(wg.projects) for wg in model.work_groups), default=1)

    if count > 1 and count * height + (count - 1) * gap > area_height:
        gap = max(MIN_CHIP_GAP, (area_height - count * height) / (count - 1))
    if count * height + (count - 1) * gap > area_height:
        height = (area_height - (count - 1) * gap) / count
    return height, gap


def render(model: Model, theme: Theme | None = None,
           options: Options | None = None) -> str:
    o = options or Options()
    t = (theme or Theme()).variant(dark=o.dark, transparent=o.transparent)
    c = Canvas(t)
    columns = len(model.work_groups)

    c.title_block(o.title or "HL7 Australia — Work Groups and Projects. Projects and "
                             "implementation guides owned by each Work Group")

    board_y = t.margin
    tsc_y = board_y + BAND_HEIGHT + BAND_GAP
    c.band(board_y, BAND_HEIGHT, model.board, t.board_fill)
    c.band(tsc_y, BAND_HEIGHT, model.tsc_title, t.tsc_fill)

    card_y = tsc_y + BAND_HEIGHT + 70
    card_h = t.height - card_y - t.margin
    c.connectors(tsc_y + BAND_HEIGHT, card_y, columns)

    area_top = card_y + CARD_HEADER + CARD_PAD
    area_h = card_h - CARD_HEADER - 2 * CARD_PAD
    chip_w = t.column_width(columns) - 40
    chip_h, gap = _chip_metrics(model, t, chip_w, area_h)

    for i, wg in enumerate(model.work_groups):
        x, w = c.card(i, columns, card_y, card_h, wg.name, header_height=CARD_HEADER)
        accent = t.accent(i)
        n = len(wg.projects)
        block = n * chip_h + max(0, n - 1) * gap
        top = area_top + (area_h - block) / 2
        chip_x = x + 20
        for j, project in enumerate(wg.projects):
            y = top + j * (chip_h + gap)
            c.rect(chip_x, y, chip_w, chip_h, fill=t.chip_fill, rx=8, stroke=t.chip_border)
            c.rect(chip_x, y, 5, chip_h, fill=accent, rx=2.5)

            lines = wrap(project.name, chip_w - 46, t.fs_chip)
            text_h = len(lines) * LINE_HEIGHT + (ACCELERATOR_HEIGHT if project.accelerator else 0)
            centre = chip_x + chip_w / 2 + 2
            start = y + (chip_h - text_h) / 2 + LINE_HEIGHT * 0.72
            for k, line in enumerate(lines):
                c.text(centre, start + k * LINE_HEIGHT, line,
                       size=t.fs_chip, fill=t.ink, anchor="middle")
            if project.accelerator:
                c.text(centre, start + len(lines) * LINE_HEIGHT - 1,
                       project.accelerator, size=t.fs_accelerator, fill=t.muted,
                       anchor="middle")

    c.footer_date(o.date or model.date)
    return c.render(display_width=o.width)
