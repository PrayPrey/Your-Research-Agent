"""
Lead time analyzer for h-m2 temporal lead time validation.
Temporal offset computation between saturation and adoption dates.
"""
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List
from config import H1_RESULTS_PATH, BENCHMARK_SHIFT_PAIRS, LEAD_TIME_THRESHOLD


class LeadTimeAnalyzer:
    """Compute temporal lead times between saturation and adoption dates."""

    def __init__(self):
        pass

    def load_saturation_dates(self, h1_results_path: Path = H1_RESULTS_PATH) -> Dict[str, str]:
        """
        Load saturation dates from h-m1 convergence results.

        Args:
            h1_results_path: Path to h-m1 convergence_results.json

        Returns:
            Dict mapping benchmark name to convergence date (YYYY-MM)
        """
        with open(h1_results_path) as f:
            h1_results = json.load(f)

        saturation_dates = {}
        for benchmark, result in h1_results['results'].items():
            saturation_dates[benchmark] = result['convergence_date']

        return saturation_dates

    def compute_lead_times(
        self,
        saturation_dates: Dict[str, str],
        adoption_dates: Dict[str, str],
        pairs: List[tuple] = BENCHMARK_SHIFT_PAIRS
    ) -> List[dict]:
        """
        Compute lead times for (benchmark, shift) pairs.

        Args:
            saturation_dates: Dict of {benchmark: saturation_date}
            adoption_dates: Dict of {shift: adoption_date}
            pairs: List of (benchmark, shift) tuples to analyze

        Returns:
            List of dicts with lead time results
        """
        lead_times = []

        for benchmark, shift in pairs:
            if benchmark not in saturation_dates:
                print(f"Warning: No saturation date for {benchmark}")
                continue
            if shift not in adoption_dates:
                print(f"Warning: No adoption date for {shift}")
                continue

            sat_date = pd.to_datetime(saturation_dates[benchmark])
            adopt_date = pd.to_datetime(adoption_dates[shift])

            # Compute lead time in months
            lead_months = (adopt_date - sat_date) / pd.Timedelta(days=30.44)  # Average month length

            lead_times.append({
                'benchmark': benchmark,
                'shift': shift,
                'saturation_date': saturation_dates[benchmark],
                'adoption_date': adoption_dates[shift],
                'lead_time_months': round(float(lead_months), 2),
                'precedes': lead_months > LEAD_TIME_THRESHOLD
            })

            print(f"{benchmark} -> {shift}: {lead_months:.1f} months lead time")

        return lead_times

    def compute_metrics(self, lead_times: List[dict]) -> Dict[str, float]:
        """
        Compute aggregate metrics from lead times.

        Args:
            lead_times: List of lead time results

        Returns:
            Dict with precede_fraction, mean_lead, median_lead, etc.
        """
        if not lead_times:
            return {}

        precede_count = sum(lt['precedes'] for lt in lead_times)
        lead_values = [lt['lead_time_months'] for lt in lead_times]

        metrics = {
            'precede_fraction': precede_count / len(lead_times),
            'mean_lead_time': float(pd.Series(lead_values).mean()),
            'median_lead_time': float(pd.Series(lead_values).median()),
            'min_lead_time': min(lead_values),
            'max_lead_time': max(lead_values),
            'n_pairs': len(lead_times)
        }

        return metrics


if __name__ == "__main__":
    analyzer = LeadTimeAnalyzer()

    # Load saturation dates from h-m1
    saturation_dates = analyzer.load_saturation_dates()
    print("Saturation dates:", saturation_dates)

    # Load adoption dates
    data_dir = Path(__file__).parent.parent / "data"
    with open(data_dir / "shift_adoption_dates.json") as f:
        adoption_dates = json.load(f)
    print("Adoption dates:", adoption_dates)

    # Compute lead times
    lead_times = analyzer.compute_lead_times(saturation_dates, adoption_dates)

    # Compute metrics
    metrics = analyzer.compute_metrics(lead_times)
    print(f"\nMetrics:")
    print(f"  Precede fraction: {metrics['precede_fraction']:.1%}")
    print(f"  Mean lead time: {metrics['mean_lead_time']:.1f} months")
    print(f"  Median lead time: {metrics['median_lead_time']:.1f} months")

    # Save results
    results = {
        'pairs': lead_times,
        'metrics': metrics
    }

    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "lead_times.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved results to {output_file}")
