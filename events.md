# HL7 AU Ballot Announcements

Ballot announcements. Edit this file, run `python build.py`, and the ballot page is
regenerated. Every key date is derived from the voting open date using the offsets in
`Process: HL7 AU Balloting` — you only need to state one date per ballot.

## Voting Entitlements

Shown under Requirements on every ballot.

- Partner Organisation Member — up to 12 nominated voters per balloted item
- Benefactor Organisation Member — up to 9 nominated voters per balloted item
- Gold Organisation Member — up to 6 nominated voters per balloted item
- Silver Organisation Member — up to 3 nominated voters per balloted item
- Individual/Student Member — up to 1 voter per balloted item

## Links

Referenced from every ballot's Requirements.

- confluence signup: https://link.hl7.au/confluence-jira-signup
- join organisation: https://link.hl7.au/join-hl7-au-organisation
- join individual: https://link.hl7.au/join-hl7-au-individual

## Publication URLs

Ballot versions publish at `<base>/<segment>/<version>`, so an item's link is derived
from its version. Match by the start of the item name; an empty segment publishes at the
base. An item can still carry an explicit URL, which wins.

The link only appears once the ballot's `final ballot published` date has passed.

- base: https://hl7.org.au/fhir
- AU Base:
- AU Core: core
- AU eRequesting: ereq
- AU Patient Summary: ps

## Ballots

Newest first is handled automatically — list them in any order. Ballots whose voting has
closed collapse by default.

Ballot items read `Name — Version — Type — Work Group`, plus the published URL as a
further field once the ballot version exists. Version and URL are recognised by shape,
so they can go anywhere in the bullet and may be omitted. Add `withdrawn` to an item
that was announced and then pulled before the ballot ran; it renders struck through and
never links, since no build was published.

Dates are `YYYY-MM-DD`. Only `voting opens` is required; any derived date can be pinned
by stating it explicitly when reality differs from the standard timeline, or set to
`n/a` when the step did not happen at all.

Every date below is transcribed from the ballot's Confluence announcement page.

### Ballot 2027-08

- voting opens: 2027-08-04
- connectathon: 2027-08-24 to 2027-08-26

#### Items

### Ballot 2027-03

- voting opens: 2027-03-03
- connectathon: 2027-03-16 to 2027-03-18

#### Items

### Ballot 2026-08

- voting opens: 2026-08-05
- connectathon: 2026-08-25 to 2026-08-26
- signup: https://confluence.hl7.org/spaces/HA/pages/413052189/Ballot+2026-08

#### Items

- AU Core R3 — 3.0.0-ballot1 — Working Standard — AU Core Work Group
- AU Base R7 — 7.0.0-ballot1 — Working Standard — FHIR Work Group

### Ballot 2026-02

Signup ran extended, from mid-December. The Connectathon was announced as expected within
the period rather than on fixed days.

- voting opens: 2026-02-20
- notice of intent: 2025-12-12
- signup opens: 2025-12-16
- ballot published: 2026-02-16
- connectathon: 2026-03-09 to 2026-03-15

#### Items

- AU Patient Summary R1 — 1.0.0-ballot — Working Standard — AU Core Technical Design Group
- AU Base R6 — 6.1.0 — Working Standard — FHIR Work Group — withdrawn

### Ballot 2025-08

- voting opens: 2025-08-11
- notice of intent: 2025-06-29
- signup opens: 2025-07-06
- signup closes: 2025-08-03
- voting closes: 2025-09-07
- connectathon: 2025-09-01 to 2025-09-02

#### Items

- AU Base — 6.0.0-ballot — Working Standard — FHIR Work Group
- AU Core R2 — 2.0.0-ballot — Working Standard — Sparked AU Core Technical Design Group
- AU eRequesting R1 — 1.0.0-ballot — Working Standard — Sparked AU eRequesting Technical Design Group
- AU Patient Summary R1 — 0.3.0-ballot — Draft for Comment — Sparked AU Core Technical Design Group

### Ballot 2025-03

No balloted items for this cycle.

- voting opens: 2025-03-04
- notice of intent: 2025-01-18
- signup opens: 2025-01-25
- ballot published: 2025-03-03
- voting closes: 2025-04-04
- connectathon: 2025-03-19 to 2025-03-20

#### Items

### Ballot 2024-08

- voting opens: 2024-08-12
- voting closes: 2024-09-08
- connectathon: 2024-08-21

#### Items

- AU Base — 4.2.2-ballot — Working Standard — FHIR Work Group
- AU Core — 1.0.0-ballot — Working Standard — Sparked AU Core Technical Design Group
- AU eRequesting — 0.1.0-ballot — Draft for Comment — Sparked AU eRequesting Technical Design Group

### Ballot 2024-03

Predates the Notice of Intent to Ballot step.

- voting opens: 2024-03-11
- notice of intent: n/a
- signup opens: 2024-02-08
- signup closes: 2024-03-08
- ballot published: 2024-03-09
- voting closes: 2024-03-31

#### Items

- AU Core — 0.3.0-ballot — Draft for Comment — Sparked AU Core Technical Design Group
