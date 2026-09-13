#!/usr/bin/env python
"""Test script to verify GitHub API data collection works."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_collector import GitHubDataCollector
from config import ExperimentConfig
import pandas as pd

def main():
    print("Testing GitHub API Data Collection")
    print("=" * 70)

    config = ExperimentConfig()
    collector = GitHubDataCollector(config.github_api_token)

    print(f"\n1. Testing collect_pwc_repos() with {min(10, config.dataset_size)} repos...")
    pwc_repos = collector.collect_pwc_repos(
        year_range=config.year_range,
        min_stars=config.min_stars,
        max_repos=10  # Just test with 10 repos
    )

    print(f"\nCollected {len(pwc_repos)} repositories:")
    print(pwc_repos[['repo_name', 'stars']].head())

    if len(pwc_repos) > 0:
        print(f"\n2. Testing fetch_repo_metadata() for first repo...")
        first_repo = pwc_repos.iloc[0]['repo_name']
        metadata = collector.fetch_repo_metadata(first_repo)
        print(f"\nMetadata for {first_repo}:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        print("\n✅ Data collection test PASSED")
        print(f"Ready to collect full dataset of {config.dataset_size} repos")
    else:
        print("\n❌ Data collection test FAILED - no repos collected")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
