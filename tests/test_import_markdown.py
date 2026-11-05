from scripts.import_markdown_postings import parse_posting, strip_personal

SAMPLE = """# Data Analyst — Acme Corp

- **Posting link:** https://jobs.example.com/123
- **Date posted:** 2026-09-01
- **Salary:** $70,000

## Summary
Acme is hiring a Data Analyst to build dashboards.

## Key Requirements
- Python and SQL
- 3+ years of analytics (Samir: 5+)

## Benefits
- Health and dental

## Fit caveats
Strong match, mention Docker work.

### Sub-note
Still part of the personal section.

## Key Responsibilities
- Maintain reports in Power BI
"""


def test_parses_metadata():
    p = parse_posting(SAMPLE)
    assert p["title"] == "Data Analyst"
    assert p["company"] == "Acme Corp"
    assert p["posted_date"] == "2026-09-01"
    assert p["source_url"] == "https://jobs.example.com/123"


def test_keeps_posting_sections_drops_personal_ones():
    text = parse_posting(SAMPLE)["text"]
    assert "Python and SQL" in text
    assert "Power BI" in text
    assert "Health and dental" in text  # "Benefits" must not match "fit"
    assert "Docker" not in text
    assert "Sub-note" not in text
    assert "Salary" not in text  # metadata bullets aren't posting text


def test_strips_inline_personal_notes():
    assert strip_personal("- 3+ years (Samir: 5+)") == "- 3+ years"
    assert (
        strip_personal("Remote. Applied via LinkedIn with a tailored CV.") == "Remote."
    )
    assert strip_personal("- Python (required)") == "- Python (required)"


def test_missing_date_and_company():
    p = parse_posting("# Developer\n- **Date posted:** —\n## Summary\nBuild APIs.")
    assert p["company"] is None
    assert p["posted_date"] is None


def test_rejects_files_without_title_or_body():
    assert parse_posting("no heading here") is None
    assert parse_posting("# Title only\n- **Date posted:** 2026-01-01") is None
