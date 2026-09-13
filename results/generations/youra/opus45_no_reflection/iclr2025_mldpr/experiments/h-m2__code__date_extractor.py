"""Date extraction from benchmark metadata."""
import re
from datetime import datetime
from data_loader import fetch_semantic_scholar_date, RateLimiter, SemanticScholarConfig
import requests


def parse_paper_date(date_str: str) -> int | None:
    """Parse date string to year."""
    if not date_str:
        return None

    for fmt in ["%Y-%m-%d", "%Y-%m", "%Y"]:
        try:
            return datetime.strptime(date_str[:len(fmt.replace("%", "").replace("-", "")) + fmt.count("-")], fmt).year
        except (ValueError, TypeError):
            continue

    match = re.search(r"(19|20)\d{2}", str(date_str))
    if match:
        return int(match.group())
    return None


def extract_benchmark_date(benchmark_metadata: dict) -> int | None:
    """Extract creation year from PWC benchmark metadata."""
    introduced = benchmark_metadata.get("introduced_date")
    if introduced:
        year = parse_paper_date(introduced)
        if year:
            return year

    paper = benchmark_metadata.get("introduced_by") or benchmark_metadata.get("paper")
    if paper:
        if isinstance(paper, dict):
            date = paper.get("date") or paper.get("published")
            if date:
                return parse_paper_date(date)
        elif isinstance(paper, str):
            return parse_paper_date(paper)

    date_field = benchmark_metadata.get("date") or benchmark_metadata.get("created_date")
    if date_field:
        return parse_paper_date(date_field)

    return None


def resolve_missing_dates(benchmarks: list[dict], max_lookups: int = 200) -> list[dict]:
    """Resolve missing dates via Semantic Scholar API."""
    limiter = RateLimiter(100)
    config = SemanticScholarConfig()
    session = requests.Session()
    lookups = 0

    for b in benchmarks:
        if b.get("year") is not None:
            continue

        paper = b.get("_raw", {}).get("introduced_by") or b.get("_raw", {}).get("paper")
        title = None
        if isinstance(paper, dict):
            title = paper.get("title")

        if title and lookups < max_lookups:
            limiter.wait()
            date = fetch_semantic_scholar_date(title, session, config)
            if date:
                b["year"] = parse_paper_date(date)
            lookups += 1

    print(f"Semantic Scholar lookups: {lookups}")
    return benchmarks
