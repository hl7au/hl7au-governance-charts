# HL7 AU governance charts

Renders the HL7 Australia governance diagrams as 16:9 SVGs from one markdown file, as
files, from a local server, or from CloudFront for embedding in web pages.
`governance.md` is the only file anyone should need to edit to change what they say.

```
governance.md           the content — TSC members, work groups, co-chairs, projects
build.py                CLI: files into out/, or a publishable tree with --site
serve.py                local dev server (stdlib http.server)
lambda_function.py      AWS Lambda entry point for the /render/* endpoint
src/parse.py            markdown -> Model; select() filters and re-orders work groups
src/options.py          query string -> Options; the one definition of every parameter
src/service.py          routing, caching headers, ETag, the index page
src/theme.py            palette (light and dark), type scale, canvas geometry
src/diagrams/base.py    SVG primitives: canvas, bands, cards, connectors, text fitting
src/diagrams/*.py       one module per diagram
out/, site/             generated (gitignored — regenerate, don't edit)
```

`python build.py` after any change. No dependencies; standard library only, which is
also why the Lambda needs no layer.

## Conventions

- **Never hand-edit generated SVG.** Fix the markdown, the theme, or a diagram module.
- **No colour or font size literals in `src/diagrams/`.** They live in `Theme`. A new
  colour is a new field on `Theme` *and* an entry in `DARK`, or dark mode silently keeps
  the light value.
- **The diagrams carry no title or byline.** They are embedded in pages that already
  have a heading. The only text outside the boxes is a small date stamp bottom right,
  drawn by `Canvas.footer_date` into the margin the cards already leave clear. `title`
  survives as the SVG's accessible name only — it is not drawn.
- **A parameter is defined once, in `src/options.py`.** Both the static build and the
  HTTP endpoints construct `Options`, so they cannot drift. Adding one means: a field,
  parsing in `from_query`, use in the diagrams, a row in the README table and in
  `index_html()`.
- **Layout scales with content.** Column count comes from the number of work groups;
  card titles shrink then wrap; project chips shrink before they overflow a card. Keep
  that property — test 3, 5 and 6 work groups before calling a layout change done.
- **`Name — Value` is the one markdown idiom for an optional qualifier.** TSC members use
  it for a role, projects for a FHIR Accelerator. Both parse through `ROLE_SPLIT` and
  render as a smaller muted line under the name. Reuse it rather than inventing brackets
  or a second separator.
- **Adding a diagram:** a module in `src/diagrams/` exposing
  `render(model, theme, options) -> str`, registered in `src/diagrams/__init__.py`.
  It picks up `--only`, `--site`, the routes and every parameter for free.

## Serving

Charts are published into an **existing** CloudFront distribution that this repo does not
own, under the `charts/` prefix of its S3 origin. There is deliberately no Terraform: two
states describing one distribution would fight. `src/service.py` is shared by the dev
server, the Lambda and the site build, so a route behaves the same in all three.
`docs/deploy.md` has the detail.

Two invariants in the workflow protect a bucket and a distribution we share with other
content: the S3 sync's source and destination are both `charts/`, so `--delete` cannot
reach anything else; and the invalidation is `/charts/*`, never `/*`. Keep both.

Publishing has to update **both** origins: the Lambda bundles `governance.md`, so a
content change that only syncs S3 leaves `/render/*` stale. The workflow does both.

## Text fitting

Width is estimated from character counts (`CHAR_WIDTH`, `CHAR_WIDTH_BOLD` in
`src/diagrams/base.py`), calibrated for Segoe UI / Arial — what Windows and PowerPoint
actually use. If you QA by rasterising with cairosvg or rsvg, those substitute DejaVu Sans,
which is noticeably wider: mild apparent tightness in a PNG preview is expected and is not
a real overflow. Judge fit in a browser.

## Background

`docs/session-history.md` records where the content came from, which options were
considered and rejected, and the layout traps already hit. Read it before reworking
the layout or the data sources.

## Provenance

Content originates from the HL7 AU Confluence spaces (work group space home pages) and the
draw.io source of *Process: Work Groups and Projects* in the HA space. When those change,
update `governance.md` — the diagrams are not live views.
