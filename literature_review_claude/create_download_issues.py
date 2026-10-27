"""Open one GitHub issue per paper in to_download.md (papers without a local PDF).

Each issue gives the DOI / open-access link, the target folder and the exact file name, so the
paper can be downloaded, dropped into place and the issue closed.

Usage:
    python literature_review_claude/create_download_issues.py --dry-run      # preview only
    python literature_review_claude/create_download_issues.py                # needs `gh auth login`

Re-running is safe: papers that already have an issue (open or closed, matched by the
"[Paper Pxxx]" title prefix) are skipped.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
TO_DOWNLOAD = HERE / "to_download.md"
REPO = "vlbthambawita/ECGEN-Eval"
LABEL = "paper-download"


def parse_rows() -> list[dict]:
    cols = ["n", "priority", "id", "title", "author", "year", "venue", "doi", "oa", "why",
            "folder", "save_as"]
    rows = []
    for line in TO_DOWNLOAD.read_text().splitlines():
        if not re.match(r"\| \d+ \|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != len(cols):
            sys.exit(f"Unexpected column count in: {line[:80]}")
        r = dict(zip(cols, cells))
        r["folder"] = r["folder"].strip("`")
        r["save_as"] = r["save_as"].strip("`")
        rows.append(r)
    return rows


def issue_title(r: dict) -> str:
    title = r["title"] if len(r["title"]) <= 110 else r["title"][:107] + "..."
    return f"[Paper {r['id']}] {title}"


def issue_body(r: dict) -> str:
    dest = f"literature_review_claude/papers/{r['folder']}/{r['save_as']}"
    links = [f"- DOI / publisher page: {r['doi']}"]
    if r["oa"]:
        links.append(f"- Open-access copy (try this first): {r['oa']}")
    links.append(
        "- Search: [Google Scholar](https://scholar.google.com/scholar?q="
        + urllib.parse.quote(r["title"]) + ")")
    return f"""**Paper:** {r['title']}
**First author:** {r['author']} · **Year:** {r['year']} · **Venue:** {r['venue']}
**Review ID:** {r['id']} · **Priority:** {r['priority']}

**Why it matters:** {r['why']}

### Where to download
{chr(10).join(links)}

### Where to put it
Save the PDF as:

```
{dest}
```

(PDFs are git-ignored, so the file stays local; it is not committed.)

### To close this issue
1. Download the PDF and save it at the path above.
2. Close this issue.
3. Ask Claude to "add the newly downloaded papers". It extracts the full text, updates
   `papers_index.csv`, `structured_extraction.jsonl` and the note, rebuilds the Paper
   Database, and removes the row from `to_download.md`.
"""


def api(method: str, path: str, data: dict | None = None, ok_codes: tuple[int, ...] = ()):
    """Call the GitHub REST API through the authenticated `gh` CLI."""
    cmd = ["gh", "api", "-X", method, path, "-H", "Accept: application/vnd.github+json"]
    if data is not None:
        cmd += ["--input", "-"]
    res = subprocess.run(cmd, input=json.dumps(data) if data is not None else None,
                         capture_output=True, text=True)
    if res.returncode != 0:
        if any(f"HTTP {c}" in res.stderr for c in ok_codes):
            return None
        sys.exit(f"gh api {method} {path} failed: {res.stderr.strip()}")
    return json.loads(res.stdout) if res.stdout.strip() else None


def existing_ids() -> set[str]:
    ids, page = set(), 1
    while True:
        items = api("GET", f"/repos/{REPO}/issues?state=all&per_page=100&page={page}")
        if not items:
            return ids
        for it in items:
            m = re.match(r"\[Paper (P\d+)\]", it["title"])
            if m:
                ids.add(m.group(1))
        page += 1


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="print the issues instead of creating them")
    ap.add_argument("--limit", type=int, default=0, help="create at most N issues (0 = all)")
    args = ap.parse_args()

    rows = parse_rows()
    if args.dry_run:
        for r in rows[: args.limit or None]:
            print("=" * 80, "\n" + issue_title(r), f"  [labels: {LABEL}, priority: {r['priority'].lower()}]")
            print(issue_body(r))
        print(f"{len(rows)} papers in to_download.md")
        return

    if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        sys.exit("Log in first: gh auth login")

    for name, color in [(LABEL, "0e8a16"), ("priority: high", "d93f0b"),
                        ("priority: medium", "fbca04"), ("priority: low", "c5def5")]:
        # 422 = label already exists
        api("POST", f"/repos/{REPO}/labels", {"name": name, "color": color}, ok_codes=(422,))

    done = existing_ids()
    created = 0
    for r in rows:
        if r["id"] in done:
            print(f"skip {r['id']} (issue exists)")
            continue
        if args.limit and created >= args.limit:
            break
        issue = api("POST", f"/repos/{REPO}/issues", {
            "title": issue_title(r), "body": issue_body(r),
            "labels": [LABEL, f"priority: {r['priority'].lower()}"]})
        created += 1
        print(f"#{issue['number']} {r['id']} {issue['html_url']}")
        time.sleep(1.5)  # stay under GitHub's secondary rate limit for content creation
    print(f"created {created} issues")


if __name__ == "__main__":
    main()
