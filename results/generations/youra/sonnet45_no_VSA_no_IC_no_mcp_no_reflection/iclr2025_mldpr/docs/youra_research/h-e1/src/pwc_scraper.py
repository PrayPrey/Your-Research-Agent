"""Papers With Code leaderboard scraper with async HTTP."""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import aiohttp
from pydantic import BaseModel, Field


class Submission(BaseModel):
    benchmark: str
    model_name: str
    score: float
    submission_date: str
    paper_title: str = ""
    paper_url: str = ""


class PWCLeaderboardScraper:
    BASE_URL = "https://paperswithcode.com/api/v1"
    RATE_LIMIT_DELAY = 0.6  # 100 req/min
    MAX_RETRIES = 3

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def _fetch_with_retry(self, url: str) -> Dict[str, Any]:
        for attempt in range(self.MAX_RETRIES):
            try:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                async with self.session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def fetch_benchmark_sota(self, benchmark_slug: str) -> List[Submission]:
        """Fetch SOTA results for a benchmark."""
        print(f"Fetching {benchmark_slug} leaderboard...")

        # Fetch benchmark details to get ID
        benchmarks_url = f"{self.BASE_URL}/benchmarks/"
        benchmarks_data = await self._fetch_with_retry(benchmarks_url)

        benchmark_id = None
        for b in benchmarks_data.get("results", []):
            if benchmark_slug.lower() in b.get("name", "").lower() or \
               benchmark_slug.lower() in b.get("slug", "").lower():
                benchmark_id = b.get("id")
                break

        if not benchmark_id:
            print(f"Benchmark '{benchmark_slug}' not found")
            return []

        # Fetch SOTA results
        sota_url = f"{self.BASE_URL}/sota/"
        params = {"benchmark": benchmark_id}

        submissions = []
        page = 1
        while True:
            paginated_url = f"{sota_url}?benchmark={benchmark_id}&page={page}"
            data = await self._fetch_with_retry(paginated_url)

            results = data.get("results", [])
            if not results:
                break

            for result in results:
                # Extract timestamp from paper metadata
                paper = result.get("paper", {})
                paper_title = paper.get("title", "")
                paper_url = paper.get("url", "")

                # Use paper published date as proxy for submission date
                published = paper.get("published")
                if not published:
                    # Try to extract from arxiv_id or github_url
                    arxiv_id = paper.get("arxiv_id", "")
                    if arxiv_id and len(arxiv_id) >= 4:
                        # ArXiv ID format: YYMM.NNNNN
                        year_month = arxiv_id[:4]
                        try:
                            year = 2000 + int(year_month[:2]) if int(year_month[:2]) < 50 else 1900 + int(year_month[:2])
                            month = int(year_month[2:4])
                            published = f"{year:04d}-{month:02d}-01"
                        except:
                            published = None

                if published:
                    submission = Submission(
                        benchmark=benchmark_slug,
                        model_name=result.get("model_name", "unknown"),
                        score=float(result.get("metrics", {}).get("accuracy", 0.0)),
                        submission_date=published,
                        paper_title=paper_title,
                        paper_url=paper_url
                    )
                    submissions.append(submission)

            # Check if more pages
            if not data.get("next"):
                break
            page += 1

        print(f"Fetched {len(submissions)} submissions for {benchmark_slug}")
        return submissions

    def save_jsonl(self, submissions: List[Submission], filename: str):
        """Save submissions to JSONL file."""
        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            for sub in submissions:
                f.write(sub.model_dump_json() + "\n")
        print(f"Saved to {output_path}")


async def main():
    benchmarks = {
        "imagenet": "imagenet",
        "glue": "glue",
        "squad": "squad"
    }

    output_dir = Path("../data/pwc_leaderboards")

    async with PWCLeaderboardScraper(output_dir) as scraper:
        for bench_name, bench_slug in benchmarks.items():
            submissions = await scraper.fetch_benchmark_sota(bench_slug)
            scraper.save_jsonl(submissions, f"{bench_name}_raw.jsonl")


if __name__ == "__main__":
    asyncio.run(main())
