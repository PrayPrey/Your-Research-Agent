"""Main analysis script for h-c2 low-confidence dispersion."""

import sys
from pathlib import Path

# CRITICAL: Add h-c1 code path FIRST (for src modules)
h1_code = str(Path(__file__).parent.parent.parent / 'h-c1' / 'code')
sys.path.insert(0, h1_code)

import pandas as pd
import numpy as np
import json
from src.data_loader import SurveyDataLoader
from src.validators import check_sample_size

# NOW import local h-c2 modules (after h-c1 src modules loaded)
h2_code = str(Path(__file__).parent)
if h2_code not in sys.path:
    sys.path.insert(0, h2_code)

import src.dispersion_metrics as metrics
import src.visualizer_ext as viz

# Import config LAST to get h-c2 config, not h-c1 config
import importlib.util
config_path = Path(__file__).parent / 'config.py'
spec = importlib.util.spec_from_file_location("h2_config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


def load_low_confidence_data(csv_path: str) -> pd.DataFrame:
    """Load and filter low-confidence responses."""
    loader = SurveyDataLoader(csv_path, confidence_threshold=config.CONFIDENCE_THRESHOLD)
    df = loader.load_raw()
    low_conf = df[df['confidence'] < config.CONFIDENCE_THRESHOLD].copy()
    print(f"Loaded {len(low_conf)} low-confidence responses (confidence <{config.CONFIDENCE_THRESHOLD})")
    return low_conf


def run_analysis(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    End-to-end dispersion analysis.

    Returns:
        results: {benchmark: {mean, std_dev, std_dev_pct, n}}
    """
    results = {}

    for benchmark in config.BENCHMARKS:
        print(f"\nAnalyzing {benchmark}...")
        result = metrics.calculate_std_dev_by_benchmark(
            df, benchmark, min_sample_size=config.MIN_SAMPLE_SIZE
        )
        results[benchmark] = result

        # Print summary
        if result['status'] == 'ok':
            print(f"  n={result['n']}, mean={result['mean']:.2f}, "
                  f"std_dev={result['std_dev']:.2f} ({result['std_dev_pct']*100:.1f}%), "
                  f"gate_pass={result['gate_pass']}")
        else:
            print(f"  {result['status']} (n={result['n']})")

    return results


def export_results(results: dict, gate_status: bool, passing: list, output_dir: Path) -> None:
    """Write dispersion_summary.csv and dispersion_summary.json."""
    # CSV
    csv_data = []
    for benchmark, r in results.items():
        csv_data.append({
            'benchmark': benchmark,
            'n': int(r['n']),
            'mean_year': r['mean'],
            'std_dev': r['std_dev'],
            'std_dev_pct': r['std_dev_pct'],
            'gate_pass': bool(r['gate_pass']),
            'status': r['status']
        })

    df_out = pd.DataFrame(csv_data)
    csv_path = output_dir / 'dispersion_summary.csv'
    df_out.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")

    # JSON - convert numpy types to Python native
    results_serializable = {}
    for k, v in results.items():
        results_serializable[k] = {
            key: (bool(val) if isinstance(val, (bool, np.bool_)) else
                  int(val) if isinstance(val, np.integer) else
                  float(val) if isinstance(val, np.floating) else val)
            for key, val in v.items()
        }

    json_data = {
        'results': results_serializable,
        'gate_satisfied': bool(gate_status),
        'passing_benchmarks': passing,
        'gate_type': config.GATE_TYPE,
        'threshold': float(config.STD_DEV_PCT_THRESHOLD)
    }

    json_path = output_dir / 'dispersion_summary.json'
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"Saved: {json_path}")


def print_summary(results: dict, gate_status: bool, passing: list) -> None:
    """Print final summary."""
    print("\n" + "="*60)
    print("GATE EVALUATION")
    print("="*60)
    print(f"Gate Type: {config.GATE_TYPE}")
    print(f"Threshold: {config.STD_DEV_PCT_THRESHOLD*100:.0f}% std dev")
    print(f"Gate Status: {'PASS' if gate_status else 'FAIL'}")
    if passing:
        print(f"Passing Benchmarks: {', '.join(passing)}")
    else:
        print("No benchmarks passed threshold")
    print("="*60)


def main():
    # Setup paths
    output_dir = Path(config.RESULTS_DIR)
    plots_dir = Path(config.PLOTS_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print("Loading low-confidence survey data...")
    low_conf_df = load_low_confidence_data(config.SURVEY_CSV_PATH)

    # Load full data for stratification plot
    full_df = pd.read_csv(config.SURVEY_CSV_PATH)

    # Run analysis
    results = run_analysis(low_conf_df, output_dir)

    # Evaluate gate
    gate_status, passing = metrics.evaluate_gate(results)

    # Export results
    export_results(results, gate_status, passing, output_dir)

    # Generate plots
    print("\nGenerating visualizations...")
    viz.plot_std_dev_bars(
        results,
        config.STD_DEV_PCT_THRESHOLD,
        str(plots_dir / 'std_dev_bars.png')
    )
    viz.plot_sample_sizes(
        results,
        config.MIN_SAMPLE_SIZE,
        str(plots_dir / 'sample_sizes.png')
    )
    viz.plot_distribution_faceted(
        low_conf_df,
        str(plots_dir / 'distribution_by_benchmark.png')
    )
    viz.plot_confidence_stratification(
        full_df,
        str(plots_dir / 'confidence_stratification.png')
    )

    # Print summary
    print_summary(results, gate_status, passing)

    print("\n✓ Analysis complete!")
    return 0 if gate_status else 1


if __name__ == "__main__":
    sys.exit(main())
