"""Data collection module for retrospective corpus."""

import requests
import time
from pathlib import Path
from typing import List, Dict


def query_papers_with_code(tag: str, max_results: int, api_url: str, timeout: int) -> List[Dict]:
    """Query Papers with Code API for papers with timing data."""
    params = {"tags": tag, "items_per_page": max_results}

    try:
        response = requests.get(api_url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        papers = []
        for paper in data.get("results", [])[:max_results]:
            papers.append({
                "paper_id": paper.get("id", paper.get("title", "unknown")),
                "title": paper.get("title"),
                "pdf_url": paper.get("url_pdf"),
                "venue": "PWC",
                "year": paper.get("published", {}).get("year", 2023),
            })

        print(f"[PWC] Found {len(papers)} papers")
        return papers

    except Exception as e:
        print(f"[PWC] Error: {e}")
        return []


def scrape_conference_papers(venue: str, year: int, keywords: List[str]) -> List[Dict]:
    """Scrape conference papers (stub - returns empty for this EXISTENCE hypothesis)."""
    # EXISTENCE hypothesis - skip web scraping, use PWC API only
    return []


def download_pdf(url: str, save_path: Path, max_retries: int, timeout: int) -> bool:
    """Download PDF with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(response.content)
            return True

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"[Download] Failed after {max_retries} retries: {url}")
                return False

    return False


def collect_all_sources(config: Dict) -> List[Dict]:
    """Execute collection from all sources."""
    papers = []

    # Papers with Code
    pwc_papers = query_papers_with_code(
        tag=config["collection"]["pwc_tag"],
        max_results=config["collection"]["pwc_max_results"],
        api_url=config["collection"]["pwc_api_url"],
        timeout=config["collection"]["timeout_seconds"]
    )
    papers.extend(pwc_papers)

    # Conferences (stub for EXISTENCE hypothesis)
    # for conf in config["collection"]["conferences"]:
    #     for year in conf["years"]:
    #         conf_papers = scrape_conference_papers(conf["venue"], year, config["collection"]["keywords"])
    #         papers.extend(conf_papers)

    print(f"[Collection] Total papers: {len(papers)}")
    return papers
