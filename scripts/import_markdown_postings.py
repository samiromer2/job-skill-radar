"""Load a folder of Markdown job postings into Job Skill Radar.

Each file looks like:

    # Software Developer — Acme
    - **Posting link:** https://...
    - **Date posted:** 2026-09-01
    ## Summary
    ...

Only the posting's own sections are imported. Sections holding personal notes
(fit, tailoring, application notes, ...) are dropped, so they're never counted
as demand or stored in the database.

Usage:
    python -m scripts.import_markdown_postings <folder> --dry-run
    python -m scripts.import_markdown_postings <folder> --api http://localhost:8000
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

PERSONAL_HEADING = re.compile(
    r"\bfit\b|tailor|\bnotes?\b|samir|apply|application|highlight|\bgaps?\b"
    r"|\bats\b|\bcv\b|decision|truth|screening questions|contact",
    re.IGNORECASE,
)
# Personal notes written inside the posting's own sections
PERSONAL_TEXT = re.compile(
    r"\bsamir\b|\bcv\b|\bapplied (via|on|through|with)\b|\bmy (cv|resume|experience)\b",
    re.IGNORECASE,
)
PARENS = re.compile(r"\s*\([^()]*\)")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
ISO_DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
BATCH_SIZE = 200


def field(text: str, name: str) -> str | None:
    m = re.search(rf"\*\*{name}:\*\*\s*(.+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def strip_personal(line: str) -> str:
    """Drop a note in brackets, else the whole sentence that holds it."""
    if not PERSONAL_TEXT.search(line):
        return line
    line = PARENS.sub(
        lambda m: "" if PERSONAL_TEXT.search(m.group()) else m.group(), line
    )
    sentences = [s for s in SENTENCE_END.split(line) if not PERSONAL_TEXT.search(s)]
    line = " ".join(sentences)
    return "" if line.strip() in ("", "-", "*") else line


def posting_sections(text: str) -> str:
    """Keep the body sections, minus the metadata bullets and personal notes."""
    kept, skip_level, in_body = [], None, False
    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            level = len(m.group(1))
            if level == 1:
                continue
            in_body = True
            if skip_level is not None and level > skip_level:
                continue
            skip_level = level if PERSONAL_HEADING.search(m.group(2)) else None
        if in_body and skip_level is None and (line := strip_personal(line)):
            kept.append(line)
    return "\n".join(kept).strip()


def parse_posting(text: str) -> dict | None:
    lines = text.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        return None
    title, _, company = lines[0][2:].partition(" — ")
    body = posting_sections(text)
    if not body:
        return None
    date = ISO_DATE.search(field(text, "Date posted") or "")
    link = field(text, "Posting link") or ""
    return {
        "title": title.strip()[:200],
        "company": company.strip()[:200] or None,
        "text": body,
        "posted_date": date.group(1) if date else None,
        "source_url": link[:500] if link.startswith("http") else None,
    }


def load_folder(folder: Path) -> tuple[list[dict], int]:
    postings, unreadable = [], 0
    for path in sorted(folder.rglob("Job Description*.md")):
        posting = parse_posting(path.read_text(encoding="utf-8", errors="replace"))
        if posting:
            postings.append(posting)
        else:
            unreadable += 1
    return postings, unreadable


def post_batches(postings: list[dict], api: str) -> dict:
    totals = {"received": 0, "imported": 0, "skipped_duplicates": 0}
    for i in range(0, len(postings), BATCH_SIZE):
        req = urllib.request.Request(
            f"{api.rstrip('/')}/postings/import",
            data=json.dumps(postings[i : i + BATCH_SIZE]).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            for key, value in json.load(resp).items():
                totals[key] += value
    return totals


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--dry-run", action="store_true", help="parse only")
    args = parser.parse_args()

    if not args.folder.is_dir():
        sys.exit(f"Not a folder: {args.folder}")
    postings, unreadable = load_folder(args.folder)
    dated = sum(1 for p in postings if p["posted_date"])
    print(f"parsed {len(postings)} postings ({dated} with a posted date)")
    print(f"skipped {unreadable} files with no title heading or no body")
    if not args.dry_run:
        print(post_batches(postings, args.api))


if __name__ == "__main__":
    main()
