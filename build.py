#!/usr/bin/env python3
"""Regenerate the diagrams from governance.md.

    python build.py                  # SVGs into out/
    python build.py --only projects  # just one diagram
    python build.py --site site      # publishable tree: fixed-URL charts + index page

The `--site` tree is what gets synced to S3. Every file it writes is reachable at
a stable URL, so a page can embed one with a plain <img src>.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.diagrams import DIAGRAMS
from src.options import Options
from src.parse import parse_file
from src.service import index_html
from src.theme import Theme

ROOT = Path(__file__).parent

# Fixed URLs published to S3. Anything else is a job for the /render endpoint.
SITE_VARIANTS: dict[str, Options] = {
    "": Options(),
    "-dark": Options(dark=True),
    "-bare": Options(header=False),
    "-bare-dark": Options(header=False, dark=True),
}


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=ROOT / "governance.md", type=Path)
    ap.add_argument("--out", default=ROOT / "out", type=Path)
    ap.add_argument("--site", type=Path,
                    help="also write a publishable tree (charts/ + index.html) here")
    ap.add_argument("--only", choices=sorted(DIAGRAMS), action="append")
    args = ap.parse_args()

    model = parse_file(args.source)
    if not model.work_groups:
        raise SystemExit(f"No work groups found in {args.source} — check the headings.")

    theme = Theme()
    names = args.only or sorted(DIAGRAMS)

    for key in names:
        filename, render = DIAGRAMS[key]
        print(f"{key:10s} -> {write(args.out / filename, render(model, theme))}")

    if args.site:
        for key in names:
            _, render = DIAGRAMS[key]
            for suffix, options in SITE_VARIANTS.items():
                write(args.site / "charts" / f"{key}{suffix}.svg",
                      render(model, theme, options))
        write(args.site / "index.html", index_html())
        count = len(names) * len(SITE_VARIANTS) + 1
        print(f"site       -> {args.site} ({count} files)")

    print(f"\n{len(model.work_groups)} work groups · {len(model.tsc)} TSC members · "
          f"{sum(len(wg.projects) for wg in model.work_groups)} projects")


if __name__ == "__main__":
    main()
