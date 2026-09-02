# HL7 AU governance charts

Two 16:9 diagrams, generated from a single markdown file:

- **Co-chairs** — AU Technical Steering Committee membership above each work group and its co-chairs.
- **Projects** — the HL7 Australia Board and AU-TSC above each work group's projects and implementation guides.

They can be built as files, served locally, or published behind CloudFront and embedded
with a plain `<img>`.

```html
<img src="https://charts.example/charts/projects.svg" alt="HL7 AU work groups and projects">
<img src="https://charts.example/render/cochairs.svg?groups=fhir,aucore&dark=1" alt="...">
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
| `header` | `1` / `0` | Show or drop the title and subtitle |
| `w` | `320`-`4000` | Rendered width; the drawing scales, it does not reflow |
| `transparent` | `1` / `0` | Omit the background rectangle |
| `date`, `title` | any text | Override the subtitle date and the title |

`header=0` is the one to reach for when embedding under a heading the page already has.

## Editing the content

Everything the diagrams say comes from [`governance.md`](governance.md):

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
```

Work groups render left to right in the order they appear. Add one and the columns
re-space themselves; titles and labels shrink or wrap to fit.

## Hosting

S3 for the fixed URLs, Lambda for the parameterised ones, one CloudFront distribution in
front of both. Terraform is in [`infra/`](infra/); see [`docs/hosting.md`](docs/hosting.md).

## Making a deck

The SVGs go straight into PowerPoint (Insert > Pictures > This Device) at full slide size.
To rasterise first:

```bash
pip install cairosvg
python -c "import cairosvg; cairosvg.svg2png(url='out/hl7au-cochairs.svg', \
  write_to='out/hl7au-cochairs.png', output_width=3840, output_height=2160)"
```
