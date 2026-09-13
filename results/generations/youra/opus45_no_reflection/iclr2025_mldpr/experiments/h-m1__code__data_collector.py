"""Semantic Scholar API wrapper with caching and rate limiting."""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable

from semanticscholar import SemanticScholar


class DataCollector:
    def __init__(self, cache_dir: str = "cache/", rate_limit_sleep: float = 1.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit_sleep = rate_limit_sleep
        self.sch = SemanticScholar()
        self.max_retries = 3

    def _cache_key(self, key: str) -> Path:
        h = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{h}.json"

    def _cached_get(self, key: str, fetch_fn: Callable[[], Any]) -> Any:
        cache_path = self._cache_key(key)
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)
        result = self._rate_limited_call(fetch_fn)
        with open(cache_path, "w") as f:
            json.dump(result, f)
        return result

    def _rate_limited_call(self, fn: Callable[[], Any]) -> Any:
        backoff = 1.0
        for attempt in range(self.max_retries):
            try:
                result = fn()
                time.sleep(self.rate_limit_sleep)
                return result
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise
        return fn()

    def fetch_foundation_papers(self, paper_ids: list[str]) -> list[dict]:
        def fetch():
            papers = []
            for pid in paper_ids:
                try:
                    p = self.sch.get_paper(pid, fields=["paperId", "title", "citationCount", "year", "venue"])
                    if p:
                        papers.append({
                            "paperId": p.paperId,
                            "title": p.title,
                            "citationCount": p.citationCount or 0,
                            "year": p.year,
                            "venue": p.venue,
                        })
                    time.sleep(self.rate_limit_sleep)
                except Exception as e:
                    print(f"Warning: Could not fetch {pid}: {e}")
            return papers
        key = f"foundation:{','.join(paper_ids)}"
        return self._cached_get(key, fetch)

    def fetch_comparison_set(self, years: list[int], venues: list[str], min_per_year: int = 1000) -> list[dict]:
        all_papers = []
        seen_ids = set()
        for year in years:
            year_papers = self._bulk_search_year(year, venues, min_per_year)
            for p in year_papers:
                if p["paperId"] not in seen_ids:
                    seen_ids.add(p["paperId"])
                    all_papers.append(p)
        return all_papers

    def _bulk_search_year(self, year: int, venues: list[str], target: int) -> list[dict]:
        def fetch():
            papers = []
            try:
                results = self.sch.search_paper(
                    query="machine learning",
                    year=str(year),
                    fields_of_study=["Computer Science"],
                    limit=target,
                    fields=["paperId", "title", "citationCount", "year", "venue"],
                )
                for p in results:
                    if p.citationCount is not None:
                        papers.append({
                            "paperId": p.paperId,
                            "title": p.title,
                            "citationCount": p.citationCount,
                            "year": p.year,
                            "venue": p.venue,
                        })
                    if len(papers) >= target:
                        break
            except Exception as e:
                print(f"Warning: Search for year {year} failed: {e}")
            return papers
        key = f"comparison:{year}:{','.join(venues)}:{target}"
        return self._cached_get(key, fetch)
