from __future__ import annotations

import datetime as dt
import html
import json
import os
import urllib.request
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = Path(__file__).resolve().parent.parent / "profile"
CACHE = OUT.parent / "cache"
ASSETS = OUT.parent / "assets"
JOINED = dt.date(2018, 11, 3)  # GitHub account creation, shown as "Uptime"

# --- Edit these -------------------------------------------------------------
TITLE = "anton@erlandsson"
INFO = [
    ("OS", "Ubuntu, Debian, Windows, Omarchy"),
    ("Uptime", None),  # filled from JOINED
    ("Host", "Sweden"),
    ("Kernel", "Full Stack Web Developer"),
    ("IDE", "VSCode, Cursor, T3 Code"),
    None,
    ("Languages.Programming", "TypeScript, Java, C++, Python"),
    ("Languages.Computer", "HTML, CSS, SQL, YAML"),
    ("Languages.Real", "Swedish, English"),
    None,
    # One line per layer: what runs in the browser, the API, where it runs.
    ("Focus.Frontend", "Next.js, Vite, Tailwind CSS"),
    ("Focus.Backend", "Node.js, Express, PostgreSQL"),
    ("Focus.Infra", "Docker, Proxmox, Nginx, CI/CD"),
]
CONTACT = [
    ("Email", "hello@antonerlandsson.net"),
    ("Website", "antonerlandsson.net"),
    ("Discord", "erlandsson"),
]
# Icons are 24x24: Lucide (ISC) for monitor/mail, Simple Icons (CC0) for Discord.
_STROKE = 'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "website": f'<g {_STROKE}><rect width="20" height="14" x="2" y="3" rx="2"/>'
    '<path d="M8 21h8M12 17v4"/></g>',
    "email": f'<g {_STROKE}><rect width="20" height="16" x="2" y="4" rx="2"/>'
    '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></g>',
    "discord": '<path fill="{c}" d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/>',
}
# (file name, label, theme colour) for the buttons under the card.
LINKS = [
    ("email", "Email", "key"),
    ("discord", "Discord", "value"),
    ("website", "Website", "key"),
]

THEMES = {
    "dark": {
        "bg": "#161b22", "fg": "#c9d1d9", "border": "#30363d",
        "key": "#f76e0a", "value": "#a5d6ff", "dots": "#616e7f",
    },
    "light": {
        "bg": "#ffffff", "fg": "#24292f", "border": "#d0d7de",
        "key": "#bc4c00", "value": "#0550ae", "dots": "#8c959f",
    },
}

# --- Layout -----------------------------------------------------------------
ADVANCE = 0.6  # monospace glyph width in em; Consolas is size-adjusted to match
FONT, LINE, COLS = 16, 20, 60  # info panel
ART_WIDTH, ART_WIDTH_MOBILE = 400, 340  # px the art grid is scaled to fit
MARGIN, GUTTER = 20, 24


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def span(text: str, cls: str | None = None) -> str:
    return f'<tspan class="{cls}">{esc(text)}</tspan>' if cls else esc(text)


def key(name: str) -> str:
    """`Languages.Real` colours both halves, keeps the dot plain."""
    return ".".join(span(part, "key") for part in name.split("."))


def kv(name: str, value: str, width: int) -> str:
    """'. Key: ..... value' padded with dots to exactly `width` columns."""
    dots = width - len(f". {name}:  {value}") - 1
    assert dots >= 1, f"{name}: {value!r} does not fit in {width} cols"
    body = span(". ", "dots") + key(name) + ":" + span(f" {'.' * dots} ", "dots")
    return body + span(value, "value")


def rule(label: str, bold: bool = False) -> str:
    return span(label, "title" if bold else None) + " " + "-" * (COLS - len(label) - 1)


def uptime(today: dt.date) -> str:
    months = (today.year - JOINED.year) * 12 + today.month - JOINED.month
    if today.day < JOINED.day:
        months -= 1
    anchor_y, anchor_m = divmod(JOINED.month - 1 + months, 12)
    anchor = dt.date(JOINED.year + anchor_y, anchor_m + 1, JOINED.day)
    days = (today - anchor).days
    y, m = divmod(months, 12)

    def plural(n: int, w: str) -> str:
        return f"{n} {w}" + ("" if n == 1 else "s")

    return f"{plural(y, 'year')}, {plural(m, 'month')}, {plural(days, 'day')}"


def graphql(query: str, **variables) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


def streaks(days: list[tuple[str, int]], today: dt.date) -> tuple[int, int]:
    """(longest, current) runs of days with contributions. Today without any
    yet does not break the current streak, the day is not over."""
    longest = run = 0
    for date, count in sorted(days):
        if date > today.isoformat():
            break
        run = run + 1 if count else 0
        longest = max(longest, run)
    counts = dict(days)
    current, day = 0, today
    if not counts.get(day.isoformat()):
        day -= dt.timedelta(days=1)
    while counts.get(day.isoformat()):
        current += 1
        day -= dt.timedelta(days=1)
    return longest, current


def paged(field: str, node: str, args: str = "") -> tuple[int, list[dict]]:
    """(totalCount, all nodes) of a connection on the viewer, e.g. pullRequests."""
    nodes, after = [], None
    while True:
        page = graphql(
            f"""query($after: String) {{ viewer {{ {field}(first: 100, after: $after {args}) {{
              totalCount pageInfo {{ hasNextPage endCursor }} nodes {{ {node} }} }} }} }}""",
            after=after,
        )["viewer"][field]
        nodes += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return page["totalCount"], nodes
        after = page["pageInfo"]["endCursor"]


def commit_counts(names: list[str], user_id: str) -> dict[str, int]:
    """Your commits on each repo's default branch, 50 repos per query."""
    history = f'history(author: {{id: "{user_id}"}}) {{ totalCount }}'
    counts = {}
    for start in range(0, len(names), 50):
        chunk = names[start : start + 50]
        aliases = " ".join(
            f"r{i}: repository(owner: {json.dumps(n.split('/')[0])}, "
            f"name: {json.dumps(n.split('/')[1])}) {{ defaultBranchRef "
            f"{{ target {{ ... on Commit {{ {history} }} }} }} }}"
            for i, n in enumerate(chunk)
        )
        for alias, repo in graphql(f"{{ {aliases} }}").items():
            branch = (repo or {}).get("defaultBranchRef") or {}
            counts[chunk[int(alias[1:])]] = branch["target"]["history"]["totalCount"] if branch else 0
    return counts


def fetch_stats(today: dt.date) -> dict[str, str]:
    """Stats for the token's owner. Needs a token that can read your org repos."""
    keys = ("repos", "contributed", "commits", "prs", "contributions", "issues")
    if not TOKEN:
        return dict.fromkeys((*keys, "longest", "current"), "--")
    names = lambda nodes: {n["nameWithOwner"] for n in nodes}  # noqa: E731

    # shortcut: first 100 repos per owner/org, page these if one ever has more
    repo_list = "repositories(first: 100) { nodes { nameWithOwner } }"
    me = graphql(
        f"""{{ viewer {{
          login id
          owned: repositories(first: 100, ownerAffiliations: OWNER) {{ nodes {{ nameWithOwner }} }}
          collab: repositories(first: 100, ownerAffiliations: COLLABORATOR) {{ nodes {{ nameWithOwner }} }}
          organizations(first: 100) {{ nodes {{ {repo_list} }} }}
        }} }}"""
    )["viewer"]
    owned = names(me["owned"]["nodes"])
    org_repos = {
        r for org in me["organizations"]["nodes"] for r in names(org["repositories"]["nodes"])
    }

    repo = "repository { nameWithOwner }"
    pr_total, prs = paged("pullRequests", repo)
    issue_total, issues = paged("issues", repo)
    pr_repos = {n["repository"]["nameWithOwner"] for n in prs}
    issue_repos = {n["repository"]["nameWithOwner"] for n in issues}
    _, recent = paged(
        "repositoriesContributedTo",
        "nameWithOwner",
        ", includeUserRepositories: true, "
        "contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]",
    )

    # contributionsCollection spans at most a year, so ask once per year. Its
    # calendar includes private work; its per-repo lists only what the token
    # may see, which still catches commits to public repos you don't belong to.
    per_year = " ".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", '
        f'to: "{y}-12-31T23:59:59Z") {{ contributionCalendar {{ totalContributions '
        "weeks { contributionDays { date contributionCount } } } "
        f"commitContributionsByRepository(maxRepositories: 100) {{ {repo} }} }}"
        for y in range(JOINED.year, today.year + 1)
    )
    years = list(graphql(f"{{ viewer {{ {per_year} }} }}")["viewer"].values())
    year_repos = {
        c["repository"]["nameWithOwner"]
        for y in years
        for c in y["commitContributionsByRepository"]
    }

    candidates = (
        owned | names(me["collab"]["nodes"]) | org_repos
        | pr_repos | issue_repos | names(recent) | year_repos
    )
    commits = commit_counts(sorted(candidates), me["id"])
    committed = {n for n, c in commits.items() if c}

    # Repos: yours, plus org repos you committed or opened a PR in.
    repos = owned | (org_repos & (committed | pr_repos))
    # Contributed: every repo with your commit, PR or issue, whoever owns it.
    contributed = committed | pr_repos | issue_repos | names(recent) | year_repos

    days = [
        (d["date"], d["contributionCount"])
        for y in years
        for week in y["contributionCalendar"]["weeks"]
        for d in week["contributionDays"]
    ]
    longest, current = streaks(days, today)
    stats = {
        "repos": len(repos),
        "contributed": len(contributed),
        "commits": sum(commits.values()),
        "prs": pr_total,
        "contributions": sum(y["contributionCalendar"]["totalContributions"] for y in years),
        "issues": issue_total,
        "longest": longest,
        "current": current,
    }
    return {k: f"{v:,}" for k, v in stats.items()}


LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def write_calendar() -> None:
    """Last year's calendar for tools/build_pacman.py, in its cache format:
    weeks of seven weekday slots (0 = Sunday), None where a day doesn't exist."""
    cal = graphql(
        """{ viewer { contributionsCollection { contributionCalendar {
          totalContributions weeks { contributionDays {
            date weekday contributionCount contributionLevel } } } } } }"""
    )["viewer"]["contributionsCollection"]["contributionCalendar"]
    weeks = []
    for week in cal["weeks"]:
        slots: list[dict | None] = [None] * 7
        for day in week["contributionDays"]:
            slots[day["weekday"]] = {
                "date": day["date"],
                "count": day["contributionCount"],
                "level": LEVELS[day["contributionLevel"]],
            }
        weeks.append(slots)
    CACHE.mkdir(exist_ok=True)
    (CACHE / "calendar.json").write_text(
        json.dumps({"total": cal["totalContributions"], "weeks": weeks}), encoding="utf-8"
    )


def load_art(theme: str) -> list[str]:
    lines = (ASSETS / f"ascii-{theme}.txt").read_text(encoding="utf-8").splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def panel(stats: dict[str, str], today: dt.date) -> list[str | None]:
    rows: list[str | None] = [rule(TITLE, bold=True)]
    for item in INFO:
        if item is None:
            rows.append(None)
        else:
            name, value = item
            rows.append(kv(name, value or uptime(today), COLS))
    rows += [None, rule("- Contact")]
    rows += [kv(k, v, COLS) for k, v in CONTACT]
    rows += [None, rule("- GitHub Stats")]
    left, right = 32, COLS - 32 - 3  # two columns joined by " | "
    for (k1, v1), (k2, v2) in [
        (("Repos", "repos"), ("Contributed", "contributed")),
        (("Commits", "commits"), ("PRs", "prs")),
        (("Contributions", "contributions"), ("Issues", "issues")),
    ]:
        rows.append(kv(k1, stats[v1], left) + " | " + kv(k2, stats[v2], right))
    current, longest = stats["current"], stats["longest"]
    if current.replace(",", "").isdigit() and int(current.replace(",", "")) > 2:
        rows.append(kv("Current.Streak", f"{current} days (Longest: {longest})", COLS))
    else:
        rows.append(kv("Longest.Streak", f"{longest} days", COLS))
    return rows


STYLE = """<style>
@font-face {{ font-family: 'ConsolasFix'; src: local('Consolas'); size-adjust: 109%; }}
text, tspan {{ white-space: pre; }}
.key, .title {{ fill: {key}; }} .title {{ font-weight: bold; }}
.value {{ fill: {value}; }} .dots {{ fill: {dots}; }}
</style>"""
FONTS = 'font-family="ConsolasFix, Consolas, Menlo, \'DejaVu Sans Mono\', monospace"'


def card(theme: str, art: list[str], rows: list[str | None], mobile: bool = False) -> str:
    """Wide: art left, panel right. Mobile: art on top, panel below, so the
    image is narrow and its text stays readable when a phone scales it down."""
    c = THEMES[theme]
    # Last row is a blinking prompt; discrete calcMode snaps like a cursor.
    cursor = (
        span("> ", "key") + '<tspan class="value">\u2588<animate attributeName="opacity" '
        'values="1;0" dur="1.06s" calcMode="discrete" repeatCount="indefinite"/></tspan>'
    )
    rows = [*rows, None, cursor]
    art_w = ART_WIDTH_MOBILE if mobile else ART_WIDTH
    art_font = art_w / (max(map(len, art)) * ADVANCE)
    art_line = art_font * ADVANCE * 2  # glyph cells are 1:2 (width:height)
    panel_w = COLS * FONT * ADVANCE
    panel_h, art_h = len(rows) * LINE, len(art) * art_line

    if mobile:
        width = round(panel_w + 2 * MARGIN)
        height = round(MARGIN + art_h + GUTTER + panel_h + MARGIN)
        art_x, art_top = (width - art_w) / 2, MARGIN
        panel_x, panel_top = MARGIN, MARGIN + art_h + GUTTER
    else:
        height = round(max(panel_h, art_h) + 2 * MARGIN)
        width = round(MARGIN + art_w + GUTTER + panel_w + MARGIN)
        art_x, art_top = MARGIN, (height - art_h) / 2
        panel_x, panel_top = MARGIN + art_w + GUTTER, (height - panel_h) / 2
    # 0.8em puts the first baseline just under the block's top edge.
    art_y, panel_y = art_top + 0.8 * art_font, panel_top + 0.8 * FONT

    art_lines = "\n".join(
        f'<tspan x="{art_x:g}" y="{art_y + i * art_line:.1f}">{esc(line)}</tspan>'
        for i, line in enumerate(art)
    )
    panel_lines = "\n".join(
        f'<tspan x="{panel_x:g}" y="{panel_y + i * LINE:g}">{row if row is not None else span(".", "dots")}</tspan>'
        for i, row in enumerate(rows)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" {FONTS}>
{STYLE.format(**c)}
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{c['bg']}" stroke="{c['border']}"/>
<text fill="{c['fg']}" font-size="{art_font:.2f}">
{art_lines}
</text>
<text fill="{c['fg']}" font-size="{FONT}">
{panel_lines}
</text>
</svg>
"""


def button(theme: str, name: str, label: str, colour: str, w: int = 300) -> str:
    """w=150 for phones: same text size in half the width, so it scales less."""
    c, h, size, icon = THEMES[theme], 50, 15, 22
    accent = c[colour]
    text_w = len(label) * size * ADVANCE
    x = (w - icon - 10 - text_w) / 2  # centre icon + gap + label as one group
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONTS}>
<defs><clipPath id="r"><rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="6"/></clipPath></defs>
<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="6" fill="{c['bg']}" stroke="{c['border']}" stroke-width="1.5"/>
<rect x="2" y="{h - 5}" width="{w - 4}" height="3" fill="{accent}" clip-path="url(#r)"/>
<svg x="{x:.1f}" y="{(h - icon) / 2 - 1.5:.1f}" width="{icon}" height="{icon}" viewBox="0 0 24 24">{ICONS[name].format(c=accent)}</svg>
<text x="{x + icon + 10:.1f}" y="{h / 2 + 3.5:.1f}" font-size="{size}" letter-spacing="0.5" fill="{c['fg']}">{esc(label.upper())}</text>
</svg>
"""


def main() -> None:
    today = dt.date.today()
    stats = fetch_stats(today)
    print(f"uptime: {uptime(today)}\nstats: {stats}")
    if TOKEN:
        write_calendar()
    rows = panel(stats, today)
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        art = load_art(theme)
        for suffix, mobile in (("", False), ("-mobile", True)):
            (OUT / f"card-{theme}{suffix}.svg").write_text(
                card(theme, art, rows, mobile), encoding="utf-8"
            )
            for name, label, colour in LINKS:
                (OUT / f"link-{name}-{theme}{suffix}.svg").write_text(
                    button(theme, name, label, colour, 150 if mobile else 300),
                    encoding="utf-8",
                )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    # Self-check: uptime math across month/year boundaries.
    assert uptime(dt.date(2018, 11, 3)) == "0 years, 0 months, 0 days"
    assert uptime(dt.date(2019, 12, 2)) == "1 year, 0 months, 29 days"
    assert uptime(dt.date(2026, 11, 11)) == "8 years, 0 months, 8 days"
    _days = [("2026-01-01", 1), ("2026-01-02", 3), ("2026-01-03", 0), ("2026-01-04", 2),
             ("2026-01-05", 1), ("2026-01-06", 0)]
    assert streaks(_days, dt.date(2026, 1, 6)) == (2, 2)  # empty today keeps it
    assert streaks(_days, dt.date(2026, 1, 3)) == (2, 2)
    assert streaks(_days[:3], dt.date(2026, 1, 4)) == (2, 0)
    main()
