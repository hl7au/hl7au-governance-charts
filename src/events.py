"""Parse `events.md` into ballots with their derived key dates.

The HL7 AU balloting process fixes every key date relative to the day voting
opens, so that is the only date a ballot has to state. See
`Process: HL7 AU Balloting` on Confluence — the offsets below encode it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

BULLET = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
# "n/a" on a key date means the step did not happen, as against simply unknown.
NOT_APPLICABLE = {"n/a", "na", "none", "not applicable", "-"}
SPLIT = re.compile(r"\s+(?:—|–|--|-)\s+")

# Days relative to the day voting opens.
OFFSETS: dict[str, int] = {
    "notice_of_intent": -42,   # NIB due: 7 days before enrolment opens
    "signup_opens": -35,       # ballot enrolment opens
    "signup_closes": -7,       # enrolment closes
    "published": -7,           # approved content published: 1 week before ballot open
    "voting_closes": 28,       # 4 week voting period
}

# Everything a ballot bullet may set, in the spellings a human would write.
FIELDS: dict[str, str] = {
    "votingopens": "voting_opens",
    "ballotvoting": "voting_opens",
    "votingcloses": "voting_closes",
    "noticeofintent": "notice_of_intent",
    "noticeofintenttoballot": "notice_of_intent",
    "nib": "notice_of_intent",
    "signupopens": "signup_opens",
    "ballotsignup": "signup_opens",
    "signupcloses": "signup_closes",
    "published": "published",
    "finalballotpublished": "published",
    "ballotpublished": "published",
    "connectathon": "connectathon",
    "signup": "signup_link",
    "signuplink": "signup_link",
}

LABELS: dict[str, str] = {
    "notice_of_intent": "Notice of Intent to Ballot",
    "signup_opens": "Ballot signup opens",
    "signup_closes": "Ballot signup closes",
    "published": "Final ballot published",
    "voting_opens": "Voting opens",
    "voting_closes": "Voting closes",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _parse_date(text: str) -> date | None:
    m = ISO.search(text)
    return date(int(m[1]), int(m[2]), int(m[3])) if m else None


def _parse_range(text: str) -> tuple[date, date] | None:
    found = [date(int(a), int(b), int(c)) for a, b, c in ISO.findall(text)]
    if not found:
        return None
    return found[0], found[-1]


# A version looks like 3.0.0-ballot1 / 7.0.0 — recognised wherever it appears in
# the bullet, so the three descriptive fields keep their order.
VERSION = re.compile(r"^\d+\.\d+(\.\d+)?([.\-+][\w.\-]+)?$")


@dataclass
class BallotItem:
    name: str
    kind: str | None = None       # e.g. "Working Standard"
    committee: str | None = None
    version: str | None = None    # e.g. "3.0.0-ballot1"
    url: str | None = None        # published ballot version, once it exists
    withdrawn: bool = False       # announced, then pulled before the ballot ran


@dataclass
class Ballot:
    name: str
    voting_opens: date | None = None
    pinned: dict[str, date] = field(default_factory=dict)
    omitted: set[str] = field(default_factory=set)   # steps that did not apply
    connectathon: tuple[date, date] | None = None
    signup_link: str | None = None
    items: list[BallotItem] = field(default_factory=list)

    def date_for(self, key: str) -> date | None:
        """A pinned date if one was stated, otherwise the derived one."""
        if key in self.omitted:
            return None
        if key in self.pinned:
            return self.pinned[key]
        if key == "voting_opens":
            return self.voting_opens
        if self.voting_opens is None or key not in OFFSETS:
            return None
        return self.voting_opens + timedelta(days=OFFSETS[key])

    def is_derived(self, key: str) -> bool:
        return key not in self.pinned and key != "voting_opens"

    def status(self, today: date) -> str:
        opens, closes = self.date_for("voting_opens"), self.date_for("voting_closes")
        if opens is None:
            return "upcoming"
        if today < opens:
            return "upcoming"
        if closes is not None and today > closes:
            return "closed"
        return "open"


@dataclass
class Events:
    title: str = "HL7 AU Ballot Announcements"
    entitlements: list[str] = field(default_factory=list)
    links: dict[str, str] = field(default_factory=dict)
    publication_base: str = ""
    # Item-name prefix -> path segment, e.g. "AU Core" -> "core".
    publication_paths: dict[str, str] = field(default_factory=dict)
    ballots: list[Ballot] = field(default_factory=list)

    def published_url(self, item: "BallotItem") -> str | None:
        """Where a version publishes: `<base>/<segment>/<version>`.

        An explicit URL on the item wins. Longest name prefix wins, so
        "AU Core" is not shadowed by a shorter entry.
        """
        if item.withdrawn:
            return None
        if item.url:
            return item.url
        if not (self.publication_base and item.version):
            return None
        match = max((k for k in self.publication_paths
                     if item.name.lower().startswith(k.lower())),
                    key=len, default=None)
        if match is None:
            return None
        segment = self.publication_paths[match]
        parts = [self.publication_base.rstrip("/")]
        if segment:
            parts.append(segment.strip("/"))
        parts.append(item.version)
        return "/".join(parts)

    def ordered(self) -> list[Ballot]:
        """Newest first. Ballots without a date sort last, keeping file order."""
        dated = [b for b in self.ballots if b.voting_opens]
        undated = [b for b in self.ballots if not b.voting_opens]
        return sorted(dated, key=lambda b: b.voting_opens, reverse=True) + undated


def parse(markdown: str) -> Events:
    events = Events()
    section: str | None = None
    in_items = False
    ballot: Ballot | None = None

    for raw in markdown.splitlines():
        heading = HEADING.match(raw)
        if heading:
            level, text = len(heading.group(1)), heading.group(2)
            if level == 1:
                events.title = text
            elif level == 2:
                section = {"votingentitlements": "entitlements",
                           "entitlements": "entitlements",
                           "links": "links",
                           "publicationurls": "publications",
                           "publications": "publications",
                           "ballots": "ballots"}.get(_slug(text))
                ballot, in_items = None, False
            elif level == 3 and section == "ballots":
                ballot = Ballot(name=text)
                events.ballots.append(ballot)
                in_items = False
            elif level == 4 and ballot is not None:
                in_items = _slug(text) in {"items", "ballotcontent", "content"}
            continue

        bullet = BULLET.match(raw)
        if not bullet:
            continue
        item = bullet.group(1)

        if section == "entitlements":
            events.entitlements.append(item)
        elif section == "links":
            if ":" in item:
                key, value = item.split(":", 1)
                events.links[_slug(key)] = value.strip()
        elif section == "publications":
            if ":" in item:
                key, value = item.split(":", 1)
                key, value = key.strip(), value.strip()
                if key.lower() == "base":
                    events.publication_base = value
                else:
                    events.publication_paths[key] = value
        elif ballot is not None and in_items:
            parts = [p.strip() for p in SPLIT.split(item) if p.strip()]
            withdrawn = any(p.lower().startswith("withdrawn") for p in parts)
            parts = [p for p in parts if not p.lower().startswith("withdrawn")]
            version = next((p for p in parts if VERSION.match(p)), None)
            url = next((p for p in parts if p.startswith(("http://", "https://"))), None)
            rest = [p for p in parts if p not in (version, url)]
            ballot.items.append(BallotItem(
                rest[0] if rest else item,
                rest[1] if len(rest) > 1 else None,
                rest[2] if len(rest) > 2 else None,
                version, url, withdrawn))
        elif ballot is not None and ":" in item:
            key, value = item.split(":", 1)
            field_name = FIELDS.get(_slug(key))
            value = value.strip()
            if field_name == "signup_link":
                ballot.signup_link = value
            elif field_name == "connectathon":
                ballot.connectathon = _parse_range(value)
            elif field_name == "voting_opens":
                ballot.voting_opens = _parse_date(value)
            elif field_name:
                if value.strip().lower() in NOT_APPLICABLE:
                    ballot.omitted.add(field_name)
                else:
                    pinned = _parse_date(value)
                    if pinned:
                        ballot.pinned[field_name] = pinned

    return events


def parse_file(path: str | Path) -> Events:
    return parse(Path(path).read_text(encoding="utf-8"))


def format_date(value: date | None) -> str:
    return value.strftime("%d %b %Y") if value else "TBC"


def format_range(start: date | None, end: date | None) -> str:
    """A period, with the repeated parts dropped: `01 Jul – 29 Jul 2026`,
    `25 – 26 Aug 2026`, `05 Aug – 02 Sep 2026`."""
    if start is None or end is None:
        return format_date(start or end)
    if start == end:
        return format_date(start)
    if start.year == end.year and start.month == end.month:
        return f"{start.strftime('%d')} – {format_date(end)}"
    if start.year == end.year:
        return f"{start.strftime('%d %b')} – {format_date(end)}"
    return f"{format_date(start)} – {format_date(end)}"
