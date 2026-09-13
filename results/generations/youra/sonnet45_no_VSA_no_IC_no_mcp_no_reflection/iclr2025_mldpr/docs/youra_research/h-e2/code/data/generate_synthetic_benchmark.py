#!/usr/bin/env python3
"""
Generate synthetic benchmark leaderboard data for hypothesis validation.
Simulates ImageNet leaderboard progression (2018-2024) with velocity decay pattern.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def generate_imagenet_leaderboard():
    """
    Generate synthetic ImageNet leaderboard matching historical patterns.

    Pattern:
    - 2018-2020: Fast improvement (~2-3% per year)
    - 2020-2022: Moderate improvement (~1% per year)
    - 2022-2024: Saturation (<0.5% per year, velocity < 0.1/month)
    """
    np.random.seed(42)

    # Time range
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2024, 12, 31)
    num_submissions = 500  # ~2 submissions/week

    dates = pd.date_range(start_date, end_date, periods=num_submissions)

    # Score progression
    scores = []
    base_score = 76.0  # Starting accuracy (2018)

    for i, date in enumerate(dates):
        year_progress = (date - start_date).days / 365.25

        # Velocity decay pattern
        if year_progress < 2:  # 2018-2020: Fast phase
            trend_score = base_score + 2.5 * year_progress
            noise_std = 0.3
        elif year_progress < 4:  # 2020-2022: Moderate phase
            trend_score = base_score + 5.0 + 1.0 * (year_progress - 2)
            noise_std = 0.2
        else:  # 2022-2024: Saturation phase (< 0.1/month = <1.2/year)
            trend_score = base_score + 7.0 + 0.4 * (year_progress - 4)
            noise_std = 0.15

        # Add noise
        score = trend_score + np.random.normal(0, noise_std)
        score = min(score, 88.0)  # Hard cap (realistic for ImageNet)
        scores.append(score)

    df = pd.DataFrame({
        'date': dates,
        'score': scores,
        'model': [f'Model_{i:03d}' for i in range(num_submissions)],
        'paper': [f'Paper_{i:03d}' for i in range(num_submissions)]
    })

    return df

def generate_glue_leaderboard():
    """Generate synthetic GLUE leaderboard (similar pattern)."""
    np.random.seed(43)

    start_date = datetime(2018, 1, 1)
    end_date = datetime(2024, 12, 31)
    num_submissions = 300

    dates = pd.date_range(start_date, end_date, periods=num_submissions)

    scores = []
    base_score = 80.0

    for i, date in enumerate(dates):
        year_progress = (date - start_date).days / 365.25

        if year_progress < 2:
            trend_score = base_score + 3.0 * year_progress
            noise_std = 0.4
        elif year_progress < 4:
            trend_score = base_score + 6.0 + 1.2 * (year_progress - 2)
            noise_std = 0.3
        else:
            trend_score = base_score + 8.4 + 0.3 * (year_progress - 4)
            noise_std = 0.2

        score = trend_score + np.random.normal(0, noise_std)
        score = min(score, 92.0)
        scores.append(score)

    df = pd.DataFrame({
        'date': dates,
        'score': scores,
        'model': [f'Model_{i:03d}' for i in range(num_submissions)],
        'paper': [f'Paper_{i:03d}' for i in range(num_submissions)]
    })

    return df

def generate_squad_leaderboard():
    """Generate synthetic SQuAD leaderboard (similar pattern)."""
    np.random.seed(44)

    start_date = datetime(2018, 1, 1)
    end_date = datetime(2024, 12, 31)
    num_submissions = 400

    dates = pd.date_range(start_date, end_date, periods=num_submissions)

    scores = []
    base_score = 82.0

    for i, date in enumerate(dates):
        year_progress = (date - start_date).days / 365.25

        if year_progress < 2:
            trend_score = base_score + 2.8 * year_progress
            noise_std = 0.35
        elif year_progress < 4:
            trend_score = base_score + 5.6 + 1.1 * (year_progress - 2)
            noise_std = 0.25
        else:
            trend_score = base_score + 7.8 + 0.35 * (year_progress - 4)
            noise_std = 0.18

        score = trend_score + np.random.normal(0, noise_std)
        score = min(score, 94.0)
        scores.append(score)

    df = pd.DataFrame({
        'date': dates,
        'score': scores,
        'model': [f'Model_{i:03d}' for i in range(num_submissions)],
        'paper': [f'Paper_{i:03d}' for i in range(num_submissions)]
    })

    return df

if __name__ == '__main__':
    data_dir = Path(__file__).parent

    # Generate datasets
    benchmarks = {
        'imagenet': generate_imagenet_leaderboard(),
        'glue': generate_glue_leaderboard(),
        'squad': generate_squad_leaderboard()
    }

    for name, df in benchmarks.items():
        output_path = data_dir / f'{name}_leaderboard.csv'
        df.to_csv(output_path, index=False)
        print(f"Generated {len(df)} entries for {name} -> {output_path}")
