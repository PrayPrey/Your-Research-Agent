"""
Papers with Code API Data Collection Module (M3-1)
Fetches benchmark metadata and performance results from PwC API.
"""

import requests
import pandas as pd
import time
from typing import List, Dict, Optional
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PapersWithCodeCollector:
    """Collects benchmark data from Papers with Code API."""

    BASE_URL = "https://paperswithcode.com/api/v1"

    def __init__(self, year_start: int = 2019, year_end: int = 2024):
        self.year_start = year_start
        self.year_end = year_end
        self.session = requests.Session()

    def fetch_benchmarks(self, task: str = "image-classification",
                        min_results: int = 5) -> List[Dict]:
        """Fetch benchmarks for given task with minimum result count."""
        url = f"{self.BASE_URL}/benchmarks"
        params = {"task": task}

        logger.info(f"Fetching benchmarks for task: {task}")
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        benchmarks = response.json().get("results", [])
        logger.info(f"Found {len(benchmarks)} total benchmarks")

        # Filter by year and result count
        filtered = []
        for bm in benchmarks:
            # Check if benchmark has sufficient results
            if self._count_results(bm) >= min_results:
                filtered.append(bm)

        logger.info(f"After filtering: {len(filtered)} benchmarks with >={min_results} results")
        return filtered

    def _count_results(self, benchmark: Dict) -> int:
        """Count number of results for a benchmark."""
        # Papers with Code API returns result count in benchmark metadata
        return benchmark.get("num_papers", 0)

    def fetch_benchmark_results(self, benchmark_id: str) -> List[Dict]:
        """Fetch all performance results for a benchmark."""
        url = f"{self.BASE_URL}/benchmarks/{benchmark_id}/results"

        logger.info(f"Fetching results for benchmark: {benchmark_id}")
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        results = response.json().get("results", [])
        logger.info(f"Found {len(results)} results")
        return results

    def extract_artifact_metadata(self, paper_info: Dict) -> Dict:
        """Extract artifact metadata (GitHub, dataset card, badge)."""
        artifacts = {
            "has_github": 0,
            "has_dataset_card": 0,
            "has_badge": 0
        }

        # Check for GitHub repository link
        if paper_info.get("url_github"):
            artifacts["has_github"] = 1

        # Check for dataset card (often in supplementary materials)
        if paper_info.get("dataset_links"):
            artifacts["has_dataset_card"] = 1

        # Check for reproducibility badge
        if paper_info.get("badge") or "reproducible" in str(paper_info.get("tags", [])).lower():
            artifacts["has_badge"] = 1

        return artifacts

    def standardize_metric(self, result: Dict) -> Optional[float]:
        """Standardize performance metric (accuracy or F1)."""
        metrics = result.get("metrics", {})

        # Try accuracy first
        if "accuracy" in metrics:
            return float(metrics["accuracy"])

        # Try F1 score
        if "f1" in metrics:
            return float(metrics["f1"])

        # Try top-1 accuracy (common for image classification)
        if "top1_acc" in metrics:
            return float(metrics["top1_acc"])

        return None

    def collect_dataset(self, target_count: int = 100,
                       high_artifact_threshold: int = 2) -> pd.DataFrame:
        """Collect full dataset with balanced artifact groups."""
        benchmarks = self.fetch_benchmarks()

        dataset = []
        for bm in benchmarks:
            benchmark_id = bm.get("id")
            benchmark_name = bm.get("name")

            # Fetch results for this benchmark
            try:
                results = self.fetch_benchmark_results(benchmark_id)

                performance_values = []
                artifacts_list = []

                for result in results:
                    # Extract performance metric
                    metric = self.standardize_metric(result)
                    if metric is not None:
                        performance_values.append(metric)

                    # Extract artifact metadata
                    paper_info = result.get("paper", {})
                    artifacts = self.extract_artifact_metadata(paper_info)
                    artifacts_list.append(artifacts)

                if len(performance_values) >= 5:  # Minimum result count
                    # Aggregate artifact info (take most common or max)
                    artifact_count = max([sum(a.values()) for a in artifacts_list]) if artifacts_list else 0

                    dataset.append({
                        "benchmark_id": benchmark_id,
                        "benchmark_name": benchmark_name,
                        "num_results": len(performance_values),
                        "performance_values": performance_values,
                        "artifact_count": artifact_count,
                        "artifact_group": "high" if artifact_count >= high_artifact_threshold else "low"
                    })

                time.sleep(0.5)  # Rate limiting

                if len(dataset) >= target_count:
                    break

            except Exception as e:
                logger.warning(f"Failed to fetch results for {benchmark_id}: {e}")
                continue

        df = pd.DataFrame(dataset)
        logger.info(f"Collected {len(df)} benchmarks")
        logger.info(f"High artifact: {(df['artifact_group'] == 'high').sum()}")
        logger.info(f"Low artifact: {(df['artifact_group'] == 'low').sum()}")

        return df


if __name__ == "__main__":
    collector = PapersWithCodeCollector()
    df = collector.collect_dataset(target_count=100)

    # Save to file
    output_path = "../outputs/benchmark_data.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✓ Data saved to: {output_path}")
