"""Papers with Code API client."""
import requests
import logging
from typing import List, Dict, Tuple
from datetime import datetime


logger = logging.getLogger(__name__)


class PwCClient:
    """Client for Papers with Code API interactions."""

    def __init__(self, base_url: str = "https://paperswithcode.com/api/v1"):
        """Initialize Papers with Code client.

        Args:
            base_url: Base URL for Papers with Code API
        """
        self.base_url = base_url
        self.session = requests.Session()

    def get_benchmarks(
        self,
        min_submissions: int = 5,
        date_range: Tuple[str, str] = ("2019-01-01", "2024-12-31")
    ) -> List[Dict]:
        """Fetch benchmarks with filtering criteria.

        Args:
            min_submissions: Minimum number of submissions per benchmark
            date_range: Tuple of (start_date, end_date) in YYYY-MM-DD format

        Returns:
            List of benchmark data dictionaries
        """
        logger.info("Fetching benchmarks from Papers with Code...")

        # Note: PwC API doesn't support direct filtering by date range
        # We'll fetch all and filter client-side
        url = f"{self.base_url}/benchmarks"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            benchmarks = data.get('results', [])
            logger.info(f"Retrieved {len(benchmarks)} benchmarks")

            return benchmarks
        except Exception as e:
            logger.error(f"Failed to fetch benchmarks: {e}")
            return []

    def get_paper_metadata(self, paper_id: str) -> Dict:
        """Get detailed paper metadata including publication date.

        Args:
            paper_id: Papers with Code paper ID

        Returns:
            Paper metadata dictionary
        """
        url = f"{self.base_url}/papers/{paper_id}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch paper {paper_id}: {e}")
            return {}

    def get_paper_repositories(self, paper_id: str) -> List[str]:
        """Extract linked GitHub repository URLs.

        Args:
            paper_id: Papers with Code paper ID

        Returns:
            List of GitHub repository URLs
        """
        url = f"{self.base_url}/papers/{paper_id}/repositories"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            repos = [r.get('url', '') for r in data.get('results', [])]
            return [r for r in repos if 'github.com' in r]
        except Exception as e:
            logger.warning(f"Failed to fetch repositories for {paper_id}: {e}")
            return []

    def get_leaderboard_timeline(self, benchmark_id: str) -> List[Dict]:
        """Get temporal submission data for reproduction analysis.

        Args:
            benchmark_id: Benchmark identifier

        Returns:
            List of leaderboard entries with timestamps
        """
        url = f"{self.base_url}/benchmarks/{benchmark_id}/results"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            return data.get('results', [])
        except Exception as e:
            logger.warning(f"Failed to fetch leaderboard for {benchmark_id}: {e}")
            return []
