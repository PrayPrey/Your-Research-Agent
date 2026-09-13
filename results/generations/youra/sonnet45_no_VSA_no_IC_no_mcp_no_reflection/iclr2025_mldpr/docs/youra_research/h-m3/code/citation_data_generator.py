"""Generate synthetic citation data for benchmarks based on paradigm shifts."""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict


def generate_citation_timeseries(
    start_date: str,
    end_date: str,
    shift_date: str,
    baseline_citations: int = 10,
    post_shift_multiplier: float = 8.0
) -> list:
    """
    Generate synthetic citation time series with spike around paradigm shift.

    Args:
        start_date: Start date (YYYY-MM)
        end_date: End date (YYYY-MM)
        shift_date: Paradigm shift date (YYYY-MM)
        baseline_citations: Pre-shift baseline citations per month
        post_shift_multiplier: Citation multiplier after shift

    Returns:
        List of {date, citations} dicts
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    shift_dt = pd.to_datetime(shift_date)

    timeseries = []
    for date in dates:
        # Baseline noise
        noise = np.random.randint(-3, 4)
        citations = baseline_citations + noise

        # Gradual ramp 3 months before shift
        months_to_shift = (shift_dt.year - date.year) * 12 + (shift_dt.month - date.month)
        if -3 <= months_to_shift < 0:
            ramp_factor = 1 + (3 + months_to_shift) * 0.3
            citations = int(citations * ramp_factor)

        # Spike around shift (±1 month)
        if abs(months_to_shift) <= 1:
            citations = int(baseline_citations * post_shift_multiplier * (0.8 + np.random.random() * 0.4))

        # Post-shift plateau
        if months_to_shift < -1:
            citations = int(baseline_citations * post_shift_multiplier * 0.9 + noise * 2)

        timeseries.append({
            'date': date.strftime('%Y-%m'),
            'citations': max(citations, 5)  # Floor at 5
        })

    return timeseries


def create_benchmark_citations():
    """Create citation data for imagenet, glue, squad."""
    base_dir = Path(__file__).parent.parent / 'data' / 'citations'
    base_dir.mkdir(exist_ok=True, parents=True)

    # Load paradigm shifts
    with open(Path(__file__).parent.parent / 'data' / 'paradigm_shifts.json') as f:
        shifts = json.load(f)

    # Generate for each benchmark
    configs = {
        'imagenet': {
            'start': '2014-01',
            'end': '2023-12',
            'shift': shifts['imagenet'],
            'baseline': 12,
            'multiplier': 6.0
        },
        'glue': {
            'start': '2017-01',
            'end': '2023-12',
            'shift': shifts['glue'],
            'baseline': 8,
            'multiplier': 10.0
        },
        'squad': {
            'start': '2017-01',
            'end': '2023-12',
            'shift': shifts['squad'],
            'baseline': 10,
            'multiplier': 7.0
        }
    }

    for benchmark, cfg in configs.items():
        data = generate_citation_timeseries(
            cfg['start'], cfg['end'], cfg['shift'],
            cfg['baseline'], cfg['multiplier']
        )

        output_path = base_dir / f'{benchmark}.json'
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Generated {output_path}")


if __name__ == '__main__':
    np.random.seed(42)
    create_benchmark_citations()
