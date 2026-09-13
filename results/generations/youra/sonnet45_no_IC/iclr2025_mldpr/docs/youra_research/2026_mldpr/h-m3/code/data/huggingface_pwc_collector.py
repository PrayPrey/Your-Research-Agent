"""
HuggingFace Papers with Code Data Collector

Since the Papers with Code API is unavailable (returns 302 redirect),
this module attempts to collect real benchmark data from alternative sources:

1. HuggingFace Datasets - papers_with_code dataset
2. Direct web scraping from paperswithcode.com (last resort)
3. Cached data from previous successful collections

CRITICAL: This collects REAL data, not synthetic/mock data.
"""

import requests
import pandas as pd
import json
import logging
import time
from typing import List, Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HuggingFacePWCCollector:
    """Collects real benchmark data from HuggingFace/Papers with Code sources."""

    def __init__(self, year_start: int = 2019, year_end: int = 2024):
        self.year_start = year_start
        self.year_end = year_end
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Research/Academic)'
        })

    def try_huggingface_datasets(self) -> Optional[pd.DataFrame]:
        """
        Try to load Papers with Code data from HuggingFace Datasets.

        HuggingFace hosts archived benchmark data that may be suitable.
        """
        try:
            from datasets import load_dataset

            logger.info("Attempting to load Papers with Code data from HuggingFace...")

            # Try various potential dataset names
            potential_datasets = [
                "paperswithcode/benchmarks",
                "paperswithcode/evaluation-results",
                "bigscience/evaluation-results"
            ]

            for dataset_name in potential_datasets:
                try:
                    logger.info(f"Trying dataset: {dataset_name}")
                    dataset = load_dataset(dataset_name, split='train')

                    # Convert to pandas DataFrame
                    df = dataset.to_pandas()
                    logger.info(f"✓ Loaded {len(df)} records from {dataset_name}")

                    return df

                except Exception as e:
                    logger.debug(f"Failed to load {dataset_name}: {e}")
                    continue

            logger.warning("No Papers with Code datasets found on HuggingFace")
            return None

        except ImportError:
            logger.warning("HuggingFace datasets library not installed")
            return None
        except Exception as e:
            logger.warning(f"HuggingFace datasets method failed: {e}")
            return None

    def scrape_benchmark_page(self, benchmark_url: str) -> Optional[Dict]:
        """
        Scrape benchmark data directly from paperswithcode.com website.

        This is a last resort when APIs are unavailable.
        """
        try:
            response = self.session.get(benchmark_url, timeout=30)
            response.raise_for_status()

            # Basic HTML parsing (would need beautifulsoup for production)
            html = response.text

            # Extract benchmark metadata
            # This is a simplified version - production would use BeautifulSoup
            benchmark_data = {
                'url': benchmark_url,
                'html_length': len(html)
            }

            logger.info(f"Scraped {benchmark_url}")
            return benchmark_data

        except Exception as e:
            logger.warning(f"Failed to scrape {benchmark_url}: {e}")
            return None

    def load_cached_pwc_data(self, cache_dir: Path = Path("./cache")) -> Optional[pd.DataFrame]:
        """
        Load previously cached Papers with Code data.

        This should contain REAL benchmark results from a previous successful collection.
        """
        cache_file = cache_dir / "pwc_benchmarks_cache.csv"

        if cache_file.exists():
            logger.info(f"Loading cached Papers with Code data from {cache_file}")
            df = pd.read_csv(cache_file)

            # Validate cache has required columns
            required_cols = ["benchmark_id", "benchmark_name", "performance_values", "artifact_count"]
            if all(col in df.columns for col in required_cols):
                logger.info(f"✓ Loaded {len(df)} benchmarks from cache")
                return df
            else:
                logger.warning(f"Cache file missing required columns: {required_cols}")
                return None
        else:
            logger.info("No cache file found")
            return None

    def collect_from_h_m1_with_real_results(self, h_m1_metadata_path: str) -> pd.DataFrame:
        """
        Use H-M1 benchmark metadata + fetch real performance results.

        H-M1 has REAL benchmark names. We fetch real performance data for each.

        This is NOT mock data - it uses real benchmark identifiers and attempts
        to get real results from alternative sources.
        """
        logger.info(f"Loading H-M1 benchmark metadata from {h_m1_metadata_path}")

        # Load real benchmark names from H-M1
        if h_m1_metadata_path.endswith('.json'):
            with open(h_m1_metadata_path, 'r') as f:
                benchmarks = json.load(f)
        else:
            benchmarks_df = pd.read_csv(h_m1_metadata_path)
            benchmarks = benchmarks_df.to_dict('records')

        logger.info(f"Loaded {len(benchmarks)} real benchmark records from H-M1")

        # For each benchmark, try to fetch real performance results
        collected_data = []

        for benchmark in benchmarks[:100]:  # Limit to target count
            benchmark_id = benchmark.get('benchmark_id', '')
            benchmark_name = benchmark.get('name', '')

            logger.info(f"Processing benchmark: {benchmark_name}")

            # Try multiple sources for real results
            results = self._fetch_real_results_for_benchmark(benchmark_id, benchmark_name)

            if results and len(results) >= 5:
                collected_data.append({
                    'benchmark_id': benchmark_id,
                    'benchmark_name': benchmark_name,
                    'num_results': len(results),
                    'performance_values': results,
                    'source': 'real_collection',
                    'year': benchmark.get('publication_year', 2020)
                })

            time.sleep(0.5)  # Rate limiting

        if collected_data:
            df = pd.DataFrame(collected_data)
            logger.info(f"✓ Collected real results for {len(df)} benchmarks")
            return df
        else:
            raise RuntimeError("Could not collect any real benchmark results")

    def _fetch_real_results_for_benchmark(self, benchmark_id: str,
                                         benchmark_name: str) -> Optional[List[float]]:
        """
        Fetch real performance results for a specific benchmark.

        Tries multiple sources in order of preference.
        """
        # Try 1: Direct API endpoint (may work for specific benchmarks)
        try:
            url = f"https://paperswithcode.com/api/v1/benchmarks/{benchmark_id}/results"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])

                performance_values = []
                for result in results:
                    # Extract accuracy/F1 metrics
                    metrics = result.get('metrics', {})
                    if 'accuracy' in metrics:
                        performance_values.append(float(metrics['accuracy']))
                    elif 'f1' in metrics:
                        performance_values.append(float(metrics['f1']))

                if performance_values:
                    logger.info(f"  ✓ Fetched {len(performance_values)} real results from API")
                    return performance_values
        except:
            pass

        # Try 2: Web scraping (if API fails)
        # This would be implemented with BeautifulSoup in production

        # Try 3: Known benchmark databases
        # ImageNet, CIFAR, etc. have published results in papers

        logger.debug(f"  Could not fetch real results for {benchmark_name}")
        return None

    def collect_dataset(self, target_count: int = 100,
                       high_artifact_threshold: int = 2) -> pd.DataFrame:
        """
        Main collection method - tries all available real data sources.

        Priority order:
        1. Cached data (from previous successful collection)
        2. HuggingFace Datasets
        3. H-M1 metadata + fetch real results
        4. Direct web scraping

        NEVER falls back to synthetic/mock data.
        """
        logger.info("="*60)
        logger.info("REAL DATA COLLECTION - No Mock/Synthetic Fallback")
        logger.info("="*60)

        # Try 1: Cached data
        df = self.load_cached_pwc_data()
        if df is not None and len(df) >= target_count // 2:
            logger.info("✓ Using cached real data")
            return df[:target_count]

        # Try 2: HuggingFace Datasets
        df = self.try_huggingface_datasets()
        if df is not None and len(df) >= target_count // 2:
            logger.info("✓ Using HuggingFace Papers with Code data")
            return df[:target_count]

        # Try 3: H-M1 benchmarks + fetch real results
        h_m1_path = "../../h-m1/code/data/processed/benchmarks_filtered.csv"
        if Path(h_m1_path).exists():
            try:
                df = self.collect_from_h_m1_with_real_results(h_m1_path)
                if len(df) >= target_count // 2:
                    logger.info("✓ Collected real results for H-M1 benchmarks")
                    return df[:target_count]
            except Exception as e:
                logger.warning(f"H-M1 + real results collection failed: {e}")

        # All methods failed
        raise RuntimeError(
            "CRITICAL: Could not collect real benchmark data from any source.\n"
            "Attempted sources:\n"
            "  1. Cached data (not found)\n"
            "  2. HuggingFace Datasets (not available)\n"
            "  3. H-M1 + real results (failed)\n"
            "  4. Papers with Code API (unavailable)\n"
            "\n"
            "Manual data collection required. See README for instructions."
        )


if __name__ == "__main__":
    collector = HuggingFacePWCCollector()

    try:
        df = collector.collect_dataset(target_count=100)
        print(f"✓ Collected {len(df)} benchmarks")
        print(df.head())
    except RuntimeError as e:
        print(f"❌ Collection failed: {e}")
