# Session history — where this project came from

Written at the end of the Claude (Cowork) session that produced the project, so a
Claude Code session in this directory can pick up with the same context. Everything
here is background and rationale; the working instructions are in `CLAUDE.md`.

## What was asked for, in order

1. Visit each HL7 AU Confluence space, find the work group co-chairs, and draw an SVG
   with a work group per box and a wide AU-TSC box spanning them all.
2. Remove Confluence space names and references from the diagram.
3. Remove the V2 Work Group — it does not exist.
4. Re-lay out for a PowerPoint slide with little whitespace.
5. Add a projects view in the same style, and put both diagrams in a PPTX, one per slide.
6. Turn it into a project that regenerates both diagrams from simple markdown.

## Where the content came from

Read anonymously through the public Confluence REST API (`/rest/api/...`) on
`confluence.hl7.org`. No authentication was needed for reads.

| Content | Source |
|---|---|
| Work group co-chairs | Each work group space's home page (`HAFWG`, `HAAUCOREWG`, `HAAUEREQWG`, `HATXWG`) |
| AU-TSC membership | `HATSC` space home page |
| Projects per work group | The draw.io attachment `HL7 AU Projects` on page `265490273`, *Process: Work Groups and Projects* (space `HA`) |

The projects came from the draw.io **source**, not the rendered image: the mxfile was
fetched, its diagram XML read, and ownership inferred from node geometry (each project's
x/y falls inside a work group container). That is why AU Base, the FHIR Test Data Project,
both Inferno testing framework projects and AU Provider Directory sit under the FHIR Work
Group rather than under AU Core, which is easy to get wrong by eye.

These are point-in-time snapshots. `governance.md` is now the source of truth and does not
track Confluence.

## Content decisions

- **V2 Work Group excluded.** Its space still exists and lists "Co-chairs: TBA", last
  edited December 2023, but Brett confirmed the work group does not exist.
- **AFCC and AFCP excluded as columns.** They have their own Confluence spaces but are a
  committee and a process, not work groups. The AFCC chair appears as a TSC member.
- **AU Provider Directory is a project, not a work group** — it lives inside the FHIR WG
  space and appears as one of its projects.
- **Confluence space keys removed** from the diagrams at Brett's request; no space names,
  keys or source footnotes appear in the output.
- **Work group boxes list names only.** Term end dates and affiliations are published on
  the source pages and were deliberately left out. The TSC box keeps role labels, because
  that is how `HATSC` publishes the list and the names alone would say little.

## Design decisions

- **1920×1080, 16:9.** The first version was 1440×576, which left a band of dead space on
  a widescreen slide. Everything is sized to fill a slide edge to edge with narrow margins.
- **Type sized for projection**, not for reading at desk distance.
- **Name and chip blocks are vertically centred** in their card, not top-aligned. Top
  alignment lines rows up across columns but leaves a card with three entries looking
  half-empty next to one with seven. Centring was the better trade here — if you change it,
  change it in both diagrams so the two slides stay consistent.
- **One accent colour per work group**, cycled in list order, appearing as the rule under
  the card header and the bar on each project chip. It is the only colour that varies.
- **Connectors** are a centre stem, a horizontal bus, and a drop per column — drawn from
  column centres, so they follow any column count.
- **TSC roles moved to a second line** under each name when the layout went to 1920 wide;
  it keeps four columns comfortable.

## Deliverables produced in that session

`HL7-AU-Governance.pptx` — two slides, one full-bleed image each, built with `pptxgenjs`
on a custom 13.333×7.5in layout, from PNGs rasterised at 3840×2160 (cairosvg). The deck
build is **not** in this repo: the project was scoped to SVG output. If you want it back,
the recipe is: rasterise each SVG at 2×, then one `addImage({x:0,y:0,w:13.333,h:7.5})`
per slide, and validate with the pptx skill's `validate.py`.

## Gotchas already hit

- **cairosvg and rsvg substitute DejaVu Sans**, which is meaningfully wider than Segoe UI
  or Arial. A PNG preview will look tighter than the real thing. Width estimates in
  `base.py` are calibrated for Segoe UI / Arial on purpose — do not widen them to make a
  cairosvg preview look right.
- **Layout must survive a different work group count.** Five columns is where card titles
  first collide with card edges and where a five-project column first overruns its card;
  both are handled (shrink-then-wrap titles, chips that give back height and gap). Test 3,
  5 and 6 before calling a layout change done.
- The Confluence page for projects is a static draw.io file. If a project moves between
  work groups there, nothing here notices — update `governance.md`.

## Serving phase

Added after the project moved to `C:\repos`, when the ask became "a dynamic image
generator I can access via HTML".

- **Both fixed and parameterised URLs**, which a pure-S3 site cannot do alone. Hence two
  origins behind one distribution: S3 for `/charts/*`, Lambda for `/render/*`. One
  renderer, one `Options` type, so the two cannot disagree.
- **Content stays in `governance.md`** rather than being read live from Confluence. That
  keeps changes reviewable and the render path free of an external dependency. The cost is
  that a Confluence change needs a commit here.
- **The Lambda bundles `governance.md`**, so a publish that only syncs S3 leaves
  `/render/*` serving stale content. The workflow updates both; do not split them.
- **Function URL auth is `AWS_IAM`**, signed by CloudFront via origin access control. It
  is tempting to set `NONE` while debugging — that exposes an unmetered renderer.
- **Dark palette added.** Board and TSC bands had to move *lighter* than the page in dark
  mode, the reverse of the light palette, or the Board band read as a hole in the page.
- `terraform validate` was never run — the sandbox that wrote it had no network for the
  Terraform binary. The HCL parses, but validate it before the first apply.

## Deployment gotchas hit for real

- **CloudFront origin path.** The `hl7austaging` distribution's S3 origin has origin path
  `/site`, so `/charts/x.svg` is fetched from `s3://hl7auprojects/site/charts/x.svg`.
  Publishing to `charts/` at the bucket root uploads fine and serves 404s.
- **`secrets` is not a valid context in a step `if:`.** It fails the whole workflow file
  at parse time, so nothing runs at all. Surface it as a job-level `env` and test that.
- **The OIDC subject claim carries numeric org and repo IDs** —
  `repo:hl7au@19850944/hl7au-governance-charts@1355314038:ref:refs/heads/main`, not the
  documented `repo:owner/name:ref:...`. See `setup-github.md`; CloudTrail is how to see
  the real value rather than guessing.

## Not done yet

- `git init` and a first commit — deliberately left to Brett.
- No tests. The obvious ones: parse a fixture markdown and assert the model; render at
  3/5/6 work groups and assert no element extends past its card or the canvas.
- PNG and PPTX outputs were considered and dropped from scope; see above for the recipe.
