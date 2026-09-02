"""Request -> SVG. Shared by the dev server, the Lambda handler and the site build.

Keeping routing here means a query parameter behaves identically however the
image is served, and there is one place to change caching or headers.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence
from urllib.parse import parse_qs, urlparse

from .diagrams import DIAGRAMS
from .options import Options
from .parse import Model, parse_file, select
from .theme import Theme

SVG_TYPE = "image/svg+xml; charset=utf-8"
HTML_TYPE = "text/html; charset=utf-8"

# Browsers cache briefly; the CDN holds it longer and is invalidated on publish.
CACHE_CONTROL = "public, max-age=300, s-maxage=86400"


@dataclass
class Response:
    status: int
    content_type: str
    body: str
    etag: str | None = None

    def headers(self, cache_control: str | None = None) -> dict[str, str]:
        """`cache_control` overrides the default — the dev server passes
        `no-store` so an edit to governance.md shows on the next refresh."""
        h = {
            "Content-Type": self.content_type,
            "Cache-Control": (cache_control or CACHE_CONTROL)
            if self.status == 200 else "no-store",
            # Diagrams are public reference material; allow cross-origin embedding.
            "Access-Control-Allow-Origin": "*",
        }
        if self.etag:
            h["ETag"] = self.etag
        return h


class Renderer:
    """Holds the parsed model. Reloads when governance.md changes on disk."""

    def __init__(self, source: str | Path):
        self.source = Path(source)
        self._mtime: float | None = None
        self._model: Model | None = None

    @property
    def model(self) -> Model:
        mtime = self.source.stat().st_mtime
        if self._model is None or mtime != self._mtime:
            self._model, self._mtime = parse_file(self.source), mtime
        return self._model

    def svg(self, diagram: str, options: Options) -> str:
        _, render = DIAGRAMS[diagram]
        return render(select(self.model, options.groups), Theme(), options)

    def handle(self, path: str, query: Mapping[str, Sequence[str] | str] | str = "",
               *, if_none_match: str | None = None) -> Response:
        name = _diagram_name(path)
        params = parse_qs(query) if isinstance(query, str) else query

        if name is None:
            if path.rstrip("/") in ("", "/index.html"):
                return Response(200, HTML_TYPE, index_html())
            if path.rstrip("/") == "/health":
                return Response(200, "text/plain; charset=utf-8", "ok")
            return Response(404, "text/plain; charset=utf-8",
                            "Not found. Try /cochairs.svg or /projects.svg\n")

        options = Options.from_query(params)
        body = self.svg(name, options)
        etag = '"%s"' % hashlib.sha256(body.encode("utf-8")).hexdigest()[:32]
        if if_none_match and if_none_match.strip() == etag:
            return Response(304, SVG_TYPE, "", etag)
        return Response(200, SVG_TYPE, body, etag)


def _diagram_name(path: str) -> str | None:
    """`/charts/projects.svg` -> `projects`. Anything else -> None."""
    stem = urlparse(path).path.rstrip("/").rsplit("/", 1)[-1]
    if stem.endswith(".svg"):
        stem = stem[:-4]
    return stem if stem in DIAGRAMS else None


def index_html(base: str = "") -> str:
    """A small page documenting the endpoints, with live previews."""
    examples = [
        ("Co-chairs", f"{base}/cochairs.svg", "the default"),
        ("Projects", f"{base}/projects.svg", "the default"),
        ("Dark", f"{base}/cochairs.svg?dark=1", "for a dark page"),
        ("No header", f"{base}/projects.svg?header=0",
         "drops the title block when the page already has a heading"),
        ("Selected groups", f"{base}/projects.svg?groups=fhir,aucore",
         "filters and re-orders the columns"),
    ]
    rows = "\n".join(
        f'<figure><figcaption><b>{label}</b> — {note}<br>'
        f'<code>&lt;img src="{url}"&gt;</code></figcaption>'
        f'<img src="{url}" alt="{label}" loading="lazy"></figure>'
        for label, url, note in examples)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HL7 AU governance charts</title>
<style>
 :root {{ color-scheme: light dark; }}
 body {{ font: 16px/1.55 "Segoe UI", system-ui, sans-serif; margin: 0 auto; padding: 2rem 1.25rem;
        max-width: 68rem; }}
 h1 {{ font-size: 1.6rem; margin: 0 0 .25rem; }}
 p.lede {{ margin: 0 0 2rem; opacity: .75; }}
 figure {{ margin: 0 0 2.5rem; }}
 figcaption {{ margin-bottom: .5rem; font-size: .9rem; }}
 code {{ background: rgba(127,127,127,.16); padding: .15em .4em; border-radius: 4px;
         font-size: .85em; }}
 img {{ width: 100%; height: auto; border-radius: 10px; }}
 table {{ border-collapse: collapse; margin-bottom: 2.5rem; font-size: .92rem; }}
 th, td {{ text-align: left; padding: .35rem .9rem .35rem 0; vertical-align: top; }}
 th {{ font-weight: 600; }}
</style></head><body>
<h1>HL7 AU governance charts</h1>
<p class="lede">SVG endpoints for embedding in a page. Generated from
<code>governance.md</code>.</p>
<table>
<tr><th>Parameter</th><th>Values</th><th>Effect</th></tr>
<tr><td><code>groups</code></td><td><code>fhir,aucore,auerequesting,terminology</code></td>
    <td>Which work groups appear, and in what order</td></tr>
<tr><td><code>dark</code></td><td><code>1</code> / <code>0</code></td><td>Dark palette</td></tr>
<tr><td><code>header</code></td><td><code>1</code> / <code>0</code></td>
    <td>Show or drop the title and subtitle</td></tr>
<tr><td><code>w</code></td><td><code>320</code>–<code>4000</code></td>
    <td>Rendered width; the drawing scales, it does not reflow</td></tr>
<tr><td><code>transparent</code></td><td><code>1</code> / <code>0</code></td>
    <td>Omit the background rectangle</td></tr>
<tr><td><code>date</code>, <code>title</code></td><td>any text</td>
    <td>Override the subtitle date and the title</td></tr>
</table>
{rows}
</body></html>
"""
