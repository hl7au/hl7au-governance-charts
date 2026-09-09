"""HTML views. Anything that needs to collapse, link or reflow lives here rather
than in `diagrams/` — an SVG cannot do those.

The palette comes from `Theme`, so the pages and the diagrams stay one visual
system: the light values become CSS custom properties and the `DARK` overrides
are re-declared under `prefers-color-scheme: dark`.
"""
from __future__ import annotations

from datetime import date

from .events import Events, format_date, format_range
from .theme import DARK, Theme

# Signup and voting read as periods rather than four separate dates, matching how
# the announcement is written.
def _key_dates(b) -> list[tuple[str, str, date | None, date | None]]:
    """Label, formatted value, and the period it covers. A single date is a
    one-day period, so it counts as active only on the day itself."""
    nib = b.date_for("notice_of_intent")
    published = b.date_for("published")
    rows = [
        ("Notice of Intent to Ballot", format_date(nib), nib, nib),
        ("Ballot signup",
         format_range(b.date_for("signup_opens"), b.date_for("signup_closes")),
         b.date_for("signup_opens"), b.date_for("signup_closes")),
        ("Final ballot published", format_date(published), published, published),
        ("Ballot voting",
         format_range(b.date_for("voting_opens"), b.date_for("voting_closes")),
         b.date_for("voting_opens"), b.date_for("voting_closes")),
    ]
    if b.connectathon:
        start, end = b.connectathon
        rows.append(("HL7 AU Connectathon", format_range(start, end), start, end))
    keys = ["notice_of_intent", "signup_opens", "published", "voting_opens"]
    return [r for r, k in zip(rows, keys + ["connectathon"])
            if k not in b.omitted]


def row_state(start: date | None, end: date | None, today: date) -> str:
    """`pending` before it, `active` during it, `done` after."""
    if start is None:
        return "pending"
    if today < start:
        return "pending"
    if end is not None and today > end:
        return "done"
    return "active"

# The label reads off the header tone, so "the ballot that just finished" and an
# older one both read CLOSED while keeping different colours.
TONE_LABEL = {"open": "Open", "completed": "Closed", "past": "Closed",
              "next": "Next", "future": "Tentative"}


def esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _css(t: Theme) -> str:
    light = {
        "bg": t.bg, "ink": t.ink, "muted": t.muted, "line": t.line,
        "card": t.card_fill, "head": t.card_header, "chip": t.chip_fill,
        "chipline": t.chip_border, "band": t.tsc_fill, "accent": t.accent(0),
        # Header tones: the current/last ballot and the next one are called out,
        # everything else recedes.
        "h-open": "#e6f2ec", "c-open": "#256b52",
        "h-completed": "#e6eef5", "c-completed": "#1f6f8b",
        "h-next": "#fbeedd", "c-next": "#a0651f",
        "h-past": "#eceff2", "c-past": t.muted,
        "h-future": t.card_fill, "c-future": t.muted,
        # Key-date rows: not yet, happening now, done.
        "r-pending": "#eef0f3", "r-active": "#e4f1e9", "r-done": "#e7eff6",
    }
    dark = {
        "bg": DARK["bg"], "ink": DARK["ink"], "muted": DARK["muted"],
        "line": DARK["line"], "card": DARK["card_fill"], "head": DARK["card_header"],
        "chip": DARK["chip_fill"], "chipline": DARK["chip_border"],
        "band": DARK["tsc_fill"], "accent": DARK["accents"][0],
        "h-open": "#17322b", "c-open": "#6fc9a3",
        "h-completed": "#172a3b", "c-completed": "#6fb6e0",
        "h-next": "#33270f", "c-next": "#e0a55f",
        "h-past": DARK["card_header"], "c-past": DARK["muted"],
        "h-future": DARK["card_fill"], "c-future": DARK["muted"],
        "r-pending": "#1b2634", "r-active": "#17322b", "r-done": "#172a3b",
    }
    var = lambda d: "\n".join(f"    --{k}: {v};" for k, v in d.items())
    return f""":root {{
    color-scheme: light dark;
{var(light)}
}}
@media (prefers-color-scheme: dark) {{
  :root {{
{var(dark)}
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0 auto; padding: 2.5rem 1.25rem 3rem; max-width: 62rem;
  font: 16px/1.55 "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  background: var(--bg); color: var(--ink);
}}
h1 {{ font-size: 1.75rem; margin: 0 0 .35rem; }}
p.lede {{ margin: 0 0 2rem; color: var(--muted); }}
details {{
  background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  margin-bottom: 1rem; overflow: hidden;
}}
details[open] {{ box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
summary {{
  cursor: pointer; list-style: none; padding: 1rem 1.25rem;
  display: flex; flex-wrap: wrap; align-items: center; gap: .75rem;
  background: var(--head); border-bottom: 1px solid transparent;
}}
summary.t-future {{ box-shadow: inset 0 -1px 0 var(--line); }}
details[open] summary {{ border-bottom-color: var(--line); }}
summary::-webkit-details-marker {{ display: none; }}
summary::after {{ content: "▸"; margin-left: auto; color: var(--muted); }}
details[open] summary::after {{ content: "▾"; }}
.name {{ font-weight: 700; font-size: 1.1rem; }}
.window {{ color: var(--muted); font-size: .9rem; }}
.pill {{
  font-size: .74rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  padding: .2rem .55rem; border-radius: 999px; border: 1px solid currentColor;
}}
summary.t-open {{ background: var(--h-open); }}
summary.t-completed {{ background: var(--h-completed); }}
summary.t-next {{ background: var(--h-next); }}
summary.t-past {{ background: var(--h-past); }}
summary.t-future {{ background: var(--h-future); }}
summary.t-open .pill {{ color: var(--c-open); }}
summary.t-completed .pill {{ color: var(--c-completed); }}
summary.t-next .pill {{ color: var(--c-next); }}
summary.t-past .pill, summary.t-future .pill {{ color: var(--muted); }}
.body {{ padding: 1.25rem; }}
h3 {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .06em;
      color: var(--muted); margin: 1.5rem 0 .6rem; }}
h3:first-child {{ margin-top: 0; }}
dl.dates {{ display: grid; grid-template-columns: max-content 1fr; gap: 2px 0; margin: 0; }}
dl.dates dt {{ color: var(--muted); padding: .3rem 1.25rem .3rem .6rem;
               border-radius: 6px 0 0 6px; }}
dl.dates dd {{ margin: 0; font-variant-numeric: tabular-nums; padding: .3rem .6rem;
               border-radius: 0 6px 6px 0; }}
.r-pending {{ background: var(--r-pending); }}
.r-active {{ background: var(--r-active); }}
.r-done {{ background: var(--r-done); }}
dd.r-active {{ font-weight: 600; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ text-align: left; padding: .5rem .75rem; border-bottom: 1px solid var(--line); }}
th {{ font-size: .78rem; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }}
tbody tr:last-child td {{ border-bottom: none; }}
td.kind {{ white-space: nowrap; color: var(--muted); }}
td.version {{ white-space: nowrap; font-variant-numeric: tabular-nums;
              font-size: .92em; color: var(--muted); }}
tr.withdrawn td {{ color: var(--muted); }}
td .note {{ font-size: .78em; text-transform: uppercase; letter-spacing: .05em;
            margin-left: .5rem; color: var(--muted); }}
ul.plain {{ margin: 0; padding-left: 1.1rem; }}
ul.plain li {{ margin-bottom: .25rem; }}
a {{ color: var(--accent); }}
.cta {{ display: inline-block; margin-top: .75rem; padding: .5rem .9rem;
        border-radius: 8px; background: var(--band); color: #fff;
        text-decoration: none; font-weight: 600; }}
.cta.disabled {{ background: var(--chip); color: var(--muted);
                 border: 1px solid var(--chipline); cursor: not-allowed;
                 pointer-events: none; }}
footer {{ margin-top: 2.5rem; text-align: right; color: var(--muted); font-size: .8rem; }}
@media (max-width: 34rem) {{
  dl.dates {{ grid-template-columns: 1fr; gap: 0; }}
  dl.dates dt {{ border-radius: 6px 6px 0 0; padding-bottom: 0; }}
  dl.dates dd {{ border-radius: 0 0 6px 6px; margin-bottom: .4rem; }}
}}"""


def _no_items(status: str) -> str:
    """A cycle still to come has yet to announce its content; one that has run
    balloted nothing. Same empty table, different fact."""
    return ("Ballot items to be confirmed." if status == "upcoming"
            else "No ballot items for this cycle.")


def _item_row(i, url: str | None) -> str:
    """One row of the ballot content table.

    A withdrawn item is struck through and never linked: it was announced and
    then pulled, so no build was ever published behind it.
    """
    if i.withdrawn:
        name = "<s>" + esc(i.name) + '</s><span class="note">withdrawn</span>'
        version = "<s>" + esc(i.version) + "</s>" if i.version else ""
        attr = ' class="withdrawn"'
    else:
        name = ('<a href="%s">%s</a>' % (esc(url), esc(i.name))) if url else esc(i.name)
        version = esc(i.version or "")
        attr = ""
    return (f'      <tr{attr}><td class="kind">{esc(i.kind or "")}</td>'
            f'<td>{name}</td><td class="version">{version}</td>'
            f'<td>{esc(i.committee or "")}</td></tr>')


def _ballot_html(b, events: Events, today: date, tone: str, expanded: bool) -> str:
    entitlements, links = events.entitlements, events.links
    status = b.status(today)
    opens, closes = b.date_for("voting_opens"), b.date_for("voting_closes")
    published = b.date_for("published")
    window = format_range(opens, closes) if opens else "dates to be confirmed"

    # The published build only exists once the ballot content has been published,
    # so the derived link waits for that date. An explicit URL is trusted as given.
    is_published = published is not None and today >= published
    rows = "\n".join(
        _item_row(i, events.published_url(i) if (i.url or is_published) else None)
        for i in b.items)
    # The section always appears: its absence would read as an oversight rather
    # than as a cycle that genuinely balloted nothing.
    table = f"""<table><thead><tr><th>Type</th><th>Name</th><th>Version</th>
      <th>Committee</th></tr></thead>
      <tbody>
{rows}
      </tbody></table>""" if b.items else f"<p>{_no_items(status)}</p>"
    content = f"""    <h3>Ballot content</h3>
    {table}"""

    dates = "\n".join(
        f'      <dt class="r-{state}" data-start="{start.isoformat() if start else ""}"'
        f' data-end="{end.isoformat() if end else ""}">{esc(label)}</dt>'
        f'<dd class="r-{state}">{esc(value)}</dd>'
        for label, value, start, end in _key_dates(b)
        for state in [row_state(start, end, today)])

    tiers = "\n".join(f"      <li>{esc(e)}</li>" for e in entitlements)
    account = links.get("confluencesignup")
    signup_account = (f'<a href="{esc(account)}">create an account</a>'
                      if account else "create one if you do not have one")

    org, individual = links.get("joinorganisation"), links.get("joinindividual")
    join = ""
    if org or individual:
        options = [f'<a href="{esc(url)}">{label}</a>'
                   for url, label in ((org, "as an organisation"),
                                      (individual, "as an individual")) if url]
        join = ("    <p>Not yet a member? Join HL7 Australia "
                + " or ".join(options) + ".</p>\n")
    requirements = f"""    <div class="voter-info">
    <h3>Requirements</h3>
    <p>To be eligible to vote you must be a current HL7 Australia member:</p>
    <ul class="plain">
{tiers}
    </ul>
{join}    <p>Organisation member voters can be a different group of individuals for each
       balloted item. You must also be signed in as an HL7.org Confluence/Jira
       user &mdash; {signup_account}.</p>""" \
        if entitlements else ""

    signup = ""
    if b.signup_link and status != "closed":
        # Live until the ballot itself is over; the script re-checks on load so a
        # stale build cannot leave a finished ballot's button clickable.
        if status == "closed":
            button = ('<span class="cta disabled" aria-disabled="true" '
                      f'data-href="{esc(b.signup_link)}">Sign up to ballot</span>')
            note = "Sign-up closed"
        else:
            button = f'<a class="cta" href="{esc(b.signup_link)}">Sign up to ballot</a>'
            note = f'Sign-up closes {format_date(b.date_for("signup_closes"))}'
        signup = (f'    <p>{button}<br><span class="window">{esc(note)}</span></p>')

    # Once voting has closed there is nothing a reader can do about eligibility
    # or sign-up, so the whole voter-facing block goes rather than sitting there
    # inviting action that is no longer possible.
    if status == "closed":
        requirements, signup = "", ""
    elif requirements:
        signup += "\n    </div>"
    

    return f"""  <details{' open' if expanded else ''}
           data-opens="{opens.isoformat() if opens else ''}"
           data-closes="{closes.isoformat() if closes else ''}">
    <summary class="t-{tone}">
      <span class="name">{esc(b.name)}</span>
      <span class="pill">{TONE_LABEL[tone]}</span>
      <span class="window">{esc(window)}</span>
    </summary>
    <div class="body">
    <h3>Key dates</h3>
    <dl class="dates">
{dates}
    </dl>
{content}
{requirements}
{signup}
    </div>
  </details>"""


def presentation(events: Events, today: date) -> dict[int, tuple[str, bool]]:
    """Header tone and default expansion for each ballot.

    Two ballots are called out: the one running (or, failing that, the one that
    just finished) and the next one coming up. Older ballots grey out; ballots
    beyond the next one sit on the card background so they read as pencilled in.

    While a ballot is actually open it is the only one expanded — the next one
    is still coloured, but a reader who can vote today should not have to scroll
    past a future cycle to find the one they can act on.
    """
    order = events.ordered()                       # newest first
    upcoming = [b for b in order if b.status(today) == "upcoming"]
    started = [b for b in order if b.status(today) != "upcoming"]

    result = {id(b): ("future" if b.status(today) == "upcoming" else "past", False)
              for b in order}
    running = bool(started) and started[0].status(today) == "open"
    if started:
        current = started[0]                       # latest that has started
        result[id(current)] = ("open" if running else "completed", True)
    if upcoming:
        # Soonest still to come: coloured always, expanded only when nothing is
        # currently open.
        result[id(upcoming[-1])] = ("next", not running)
    return result


# Recomputes status client-side so a page built weeks ago still reads correctly,
# and re-applies the same open/closed rule the build used.
SCRIPT = """
(function () {
  var LABEL = { open: 'Open', completed: 'Closed', past: 'Closed',
                next: 'Next', future: 'Tentative' };
  var today = new Date().toISOString().slice(0, 10);
  var all = [].slice.call(document.querySelectorAll('details[data-opens]'));
  var states = all.map(function (d) {
    var opens = d.dataset.opens, closes = d.dataset.closes;
    if (!opens) return null;
    // A ballot is finished once its closing day is over, i.e. from midnight after it.
    return today < opens ? 'upcoming' : (closes && today > closes ? 'closed' : 'open');
  });

  // Documents are newest first. Call out the ballot that is running (or the one
  // that just finished) and the next one due; everything else recedes.
  var tone = states.map(function (s) { return s === 'upcoming' ? 'future' : 'past'; });
  var expand = {};
  var current = states.indexOf('open');
  if (current === -1) current = states.indexOf('closed');
  if (current !== -1) {
    tone[current] = states[current] === 'open' ? 'open' : 'completed';
    expand[current] = true;
  }
  var running = states.indexOf('open') !== -1;
  for (var i = states.length - 1; i >= 0; i--) {
    if (states[i] === 'upcoming') { tone[i] = 'next'; expand[i] = !running; break; }
  }

  all.forEach(function (d, i) {
    var status = states[i];
    if (!status) return;
    var summary = d.querySelector('summary');
    summary.className = 't-' + tone[i];
    var pill = d.querySelector('.pill');
    pill.className = 'pill';
    pill.textContent = LABEL[tone[i]];
    d.open = !!expand[i];

    d.querySelectorAll('dt[data-start]').forEach(function (dt) {
      var start = dt.dataset.start, end = dt.dataset.end;
      var state = !start || today < start ? 'pending'
                : (end && today > end ? 'done' : 'active');
      if (!start) state = 'pending';
      dt.className = 'r-' + state;
      if (dt.nextElementSibling) dt.nextElementSibling.className = 'r-' + state;
    });

    if (status === 'closed') {
      var info = d.querySelector('.voter-info');
      if (info) info.remove();
      var cta = d.querySelector('.cta');
      if (cta && cta.parentNode) cta.parentNode.remove();
    }
  });
})();
"""


def render_ballots(events: Events, theme: Theme | None = None,
                   today: date | None = None) -> str:
    t = theme or Theme()
    today = today or date.today()
    shown = presentation(events, today)
    ballots = "\n".join(_ballot_html(b, events, today, *shown[id(b)])
                        for b in events.ordered())
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(events.title)}</title>
<style>
{_css(t)}
</style></head><body>
<h1>{esc(events.title)}</h1>
<p class="lede">The current ballot and the next one are shown expanded. Select any other
to see its detail.</p>
{ballots}
<footer>Generated {esc(format_date(today))}</footer>
<script>{SCRIPT}</script>
</body></html>
"""


PAGES = {"ballots": ("ballots.html", render_ballots)}
