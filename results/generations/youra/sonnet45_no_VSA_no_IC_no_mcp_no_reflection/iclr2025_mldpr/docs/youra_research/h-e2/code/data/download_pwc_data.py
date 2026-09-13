#!/usr/bin/env python3
"""
Download Papers With Code leaderboard data via public API.
Saves to CSV for experiment use.
"""

import requests
import pandas as pd
import json
from pathlib import Path

def fetch_benchmark_results(benchmark_id, metric_name):
    """Fetch leaderboard results from Papers With Code API."""
    url = f"https://paperswithcode.com/api/v1/benchmarks/{benchmark_id}/results"

    results = []
    page = 1

    while True:
        response = requests.get(url, params={'page': page})

        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            break

        data = response.json()

        if 'results' not in data or not data['results']:
            break

        for item in data['results']:
            try:
                date_str = item.get('published', item.get('created_at', ''))
                if not date_str:
                    continue

                metrics = item.get('metrics', {})
                score = None

                # Try to find the metric score
                for metric in metrics:
                    if metric.get('name', '').lower() == metric_name.lower():
                        score = metric.get('value')
                        break

                if score is not None:
                    results.append({
                        'date': pd.to_datetime(date_str),
                        'score': float(score),
                        'model': item.get('model_name', 'unknown'),
                        'paper': item.get('paper_name', '')
                    })
            except Exception as e:
                print(f"Skipping entry: {e}")
                continue

        # Check for next page
        if not data.get('next'):
            break
        page += 1

    return pd.DataFrame(results)

def download_pwc_leaderboard():
    """Download leaderboard data for ImageNet, GLUE, SQuAD."""
    benchmarks = [
        ('imagenet', 'Top 1 Accuracy'),
        ('glue', 'Average'),
        ('squad', 'EM')
    ]

    data_dir = Path(__file__).parent

    for benchmark_id, metric_name in benchmarks:
        print(f"Fetching {benchmark_id}...")

        df = fetch_benchmark_results(benchmark_id, metric_name)

        if df.empty:
            print(f"  No data for {benchmark_id}")
            continue

        # Filter 2018-2024
        df = df[(df['date'] >= '2018-01-01') & (df['date'] <= '2024-12-31')]

        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)

        # Save to CSV
        output_path = data_dir / f'{benchmark_id}_leaderboard.csv'
        df.to_csv(output_path, index=False)

        print(f"  Saved {len(df)} entries to {output_path}")

if __name__ == '__main__':
    download_pwc_leaderboard()
