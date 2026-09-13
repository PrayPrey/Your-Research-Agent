"""
Benchmark Sampler: Stratified sampling from Papers with Code API
Task M1-1: Data Collection Infrastructure
Based on: 03_logic.md#M1-1, 03_architecture.md#Module-2
"""

import requests
import pandas as pd
import time
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BenchmarkSample:
    """Structure for a single benchmark sample."""
    benchmark_id: str
    paper_title: str
    domain: str  # CV or NLP
    year: int
    github_url: Optional[str]
    dataset_card_url: Optional[str]
    badge_status: bool
    artifact_count: int


class BenchmarkSampler:
    """Stratified sampling of benchmarks from Papers with Code."""

    def __init__(self, api_base_url: str, rate_limit: float, max_retries: int):
        self.api_base_url = api_base_url
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.session = requests.Session()

    def fetch_classification_benchmarks(
        self,
        task: str = "classification",
        start_year: int = 2019,
        end_year: int = 2024
    ) -> pd.DataFrame:
        """
        Fetch classification benchmarks via Papers with Code API.

        Returns:
            DataFrame with columns: [benchmark_id, paper_title, domain, year,
                                     github_url, dataset_card_url, badge_status, artifact_count]
        """
        url = f"{self.api_base_url}benchmarks/"
        all_benchmarks = []

        page = 1
        while True:
            params = {"task": task, "page": page}

            # Retry logic
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(f"API request failed after {self.max_retries} attempts: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff

            data = response.json()
            results = data.get('results', [])
            if not results:
                break

            all_benchmarks.extend(results)

            # Check pagination
            if not data.get('next'):
                break

            page += 1
            time.sleep(self.rate_limit)  # Rate limiting

        # Filter by year and artifact presence
        filtered = []
        for b in all_benchmarks:
            year = b.get('year', 0)
            if not (start_year <= year <= end_year):
                continue

            # Count artifacts
            artifact_count = sum([
                bool(b.get('github_url')),
                bool(b.get('dataset_card_url')),
                b.get('badge_status', False)
            ])

            if artifact_count >= 2:  # Minimum 2 artifacts
                filtered.append({
                    'benchmark_id': b.get('id', ''),
                    'paper_title': b.get('paper_title', ''),
                    'domain': self._infer_domain(b.get('task', '')),
                    'year': year,
                    'github_url': b.get('github_url'),
                    'dataset_card_url': b.get('dataset_card_url'),
                    'badge_status': b.get('badge_status', False),
                    'artifact_count': artifact_count
                })

        return pd.DataFrame(filtered)

    def _infer_domain(self, task_name: str) -> str:
        """Infer domain (CV or NLP) from task name."""
        nlp_keywords = ['language', 'nlp', 'text', 'translation', 'sentiment']
        task_lower = task_name.lower()

        for keyword in nlp_keywords:
            if keyword in task_lower:
                return 'NLP'
        return 'CV'

    def stratified_sample(
        self,
        benchmarks: pd.DataFrame,
        strata: Dict[str, int]
    ) -> pd.DataFrame:
        """
        Sample n benchmarks per domain using stratified sampling.

        Args:
            benchmarks: Full benchmark DataFrame
            strata: {'CV': 10, 'NLP': 10}

        Returns:
            DataFrame with 20 rows (10 CV + 10 NLP)
        """
        sampled = []

        for domain, count in strata.items():
            domain_benchmarks = benchmarks[benchmarks['domain'] == domain]

            if len(domain_benchmarks) < count:
                raise ValueError(f"Insufficient {domain} benchmarks: {len(domain_benchmarks)} < {count}")

            sample = domain_benchmarks.sample(n=count, random_state=42)
            sampled.append(sample)

        return pd.concat(sampled, ignore_index=True)

    def save_sample(self, sample: pd.DataFrame, output_dir: str) -> None:
        """Export benchmark_sample.csv."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "benchmark_sample.csv")
        sample.to_csv(output_path, index=False)
        print(f"Saved {len(sample)} benchmarks to {output_path}")
