# HL7 AU governance charts

Two 16:9 diagrams and a ballot announcements page, generated from markdown:

- **Co-chairs** — AU Technical Steering Committee membership above each work group and its co-chairs.
- **Projects** — the HL7 Australia Board and AU-TSC above each work group's projects and implementation guides.
- **Ballots** — an announcements page, newest first. The running ballot and the next one
  are expanded and colour-coded (OPEN, CLOSED, NEXT, TENTATIVE); the rest collapse.

They can be built as files, served locally, or published behind CloudFront and embedded
with a plain `<img>`.

```html
<img src="https://apps.hl7.org.au/charts/projects.svg" alt="HL7 AU work groups and projects">
<img src="https://apps.hl7.org.au/render/cochairs.svg?groups=fhir,aucore&dark=1" alt="...">
```

## Use

```bash
python build.py                    # SVGs into out/
python build.py --only projects    # just one diagram
python build.py --site site        # publishable tree: fixed-URL charts + index page
python serve.py                    # http://127.0.0.1:8000 — the same routes, live
```

Python 3.10+. No dependencies.

## URL parameters

| Parameter | Values | Effect |
|---|---|---|
| `groups` | `fhir,aucore,auerequesting,terminology` | Which work groups appear, and in what order |
| `dark` | `1` / `0` | Dark palette |
| `w` | `320`-`4000` | Rendered width; the drawing scales, it does not reflow |
| `transparent` | `1` / `0` | Omit the background rectangle |
| `date` | any text | Replaces the date stamp in the bottom right |
| `title` | any text | Accessible name for the image (not drawn) |

The diagrams carry no title or byline — the embedding page supplies those. The only
text outside the boxes is a small date stamp in the bottom right.

## Editing the content

The diagrams come from [`governance.md`](governance.md), the ballot page from
[`events.md`](events.md).

### governance.md

```markdown
## AU-TSC

- Tim Blake — Chair
- Brett Esler — Deputy Chair

## Work Groups

### FHIR Work Group

#### Co-chairs

- Brett Esler

#### Projects

- AU Base FHIR IG
- AU Core FHIR IG — Sparked
```

A project may name the FHIR Accelerator running it after an em dash; it renders as a
subtitle inside the project box. Accelerators are project-level only — work groups
don't have one.

Work groups render left to right in the order they appear. Add one and the columns
re-space themselves; titles and labels shrink or wrap to fit.

### events.md

Every ballot key date is derived from the voting open date using the offsets in
*Process: HL7 AU Balloting*, so a ballot normally states one date:

```markdown
### Ballot 2026-08

- voting opens: 2026-08-05
- connectathon: 2026-08-25 to 2026-08-26
- signup: https://confluence.hl7.org/...

#### Items

- AU Core R3 — 3.0.0-ballot1 — Working Standard — AU Core Work Group
- AU Base R7 — 7.0.0-ballot1 — Working Standard — FHIR Work Group — https://build.fhir.org/ig/…
```

Items read `Name — Version — Type — Work Group`. Version and URL are matched by shape
rather than position, so they can go anywhere in the bullet and either may be left out.

The link is normally derived rather than typed. `## Publication URLs` maps the start of
an item name to its path segment, and the version completes it:

```markdown
- base: https://hl7.org.au/fhir
- AU Base:
- AU Core: core
- AU eRequesting: ereq
- AU Patient Summary: ps
```

So `AU Core R3` at `3.0.0-ballot1` links to `https://hl7.org.au/fhir/core/3.0.0-ballot1`,
and AU Base, having no segment, publishes at the base. The link appears only once the
ballot's `final ballot published` date has passed — before then the build does not exist.
An explicit URL on the item overrides all of this and is shown immediately.

| Derived | Offset from voting open |
|---|---|
| Notice of Intent to Ballot | −42 days |
| Ballot signup opens | −35 days |
| Ballot signup closes | −7 days |
| Final ballot published | −7 days |
| Voting closes | +28 days |

Shared URLs live under `## Links` (`- confluence signup: https://…`) and entitlements
under `## Voting Entitlements`, so neither is repeated per ballot.

Any of them can be pinned by stating it as its own bullet (`- signup closes: 2026-07-31`)
when a ballot departs from the standard timeline.

## Hosting

Published to `https://apps.hl7.org.au/charts/` via the existing HL7 AU CloudFront
distribution (`s3://hl7auprojects/site/charts/` — note the origin path). The parameterised `/render/*` endpoint is an optional second
phase. See [`docs/deploy.md`](docs/deploy.md).

## Making a deck

The SVGs go straight into PowerPoint (Insert > Pictures > This Device) at full slide size.
To rasterise first:

```bash
pip install cairosvg
python -c "import cairosvg; cairosvg.svg2png(url='out/hl7au-cochairs.svg', \
  write_to='out/hl7au-cochairs.png', output_width=3840, output_height=2160)"
```
