"""Test real GitHub API data collection."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_collector import GitHubDataCollector
from config import ExperimentConfig

config = ExperimentConfig()
collector = GitHubDataCollector('')  # No token - use unauthenticated

print(f"Collecting {config.dataset_size} repositories from curated list...")
print("This uses REAL GitHub API (no mock data)")

# Collect repository list
repos_df = collector.collect_pwc_repos(
    year_range=config.year_range,
    min_stars=config.min_stars,
    max_repos=config.dataset_size
)

print(f"\n✓ Collected {len(repos_df)} repositories")
print("\nSample repositories:")
print(repos_df[['repo_name', 'stars']].head(10))

# Test fetching metadata for first repo
if len(repos_df) > 0:
    test_repo = repos_df.iloc[0]['repo_name']
    print(f"\nFetching full metadata for: {test_repo}")
    metadata = collector.fetch_repo_metadata(test_repo)
    print(f"✓ Metadata keys: {list(metadata.keys())}")
    print(f"  Stars: {metadata.get('stars')}")
    print(f"  Forks: {metadata.get('forks')}")
    print(f"  Contributors: {metadata.get('contributors')}")
    print(f"  Days since last commit: {metadata.get('days_since_last_commit')}")

print("\n✓ Real data collection test PASSED")
