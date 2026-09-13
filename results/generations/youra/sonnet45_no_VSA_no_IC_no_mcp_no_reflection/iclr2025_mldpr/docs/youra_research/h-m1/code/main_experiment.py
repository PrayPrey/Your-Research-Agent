from pathlib import Path
import json
from data_loader import PWCDataLoader
from convergence_detector import ConvergenceDetector
from statistical_validator import StatisticalValidator
from visualizer import ConvergenceVisualizer

BENCHMARKS = ["imagenet", "glue", "squad"]
BENCHMARK_THRESHOLDS = {
    "imagenet": 0.012,
    "glue": 0.008,
    "squad": 0.010
}

def run_convergence_experiment(data_dir: Path, output_dir: Path) -> dict:
    loader = PWCDataLoader(data_dir)
    validator = StatisticalValidator()
    visualizer = ConvergenceVisualizer(output_dir / 'figures')

    results = {}
    converged_count = 0

    for benchmark in BENCHMARKS:
        print(f"\nProcessing {benchmark}...")
        df = loader.load_benchmark(benchmark)
        df = loader.prepare_monthly_aggregation(df)

        threshold = BENCHMARK_THRESHOLDS[benchmark]
        detector = ConvergenceDetector(window_months=6, threshold=threshold, top_k=5)

        rolling_std = detector.compute_rolling_std(df, benchmark)
        convergence_date, final_std = detector.detect_first_convergence(rolling_std)

        if convergence_date:
            validation = validator.validate_convergence(df, convergence_date, benchmark)
            if validation['significant']:
                converged_count += 1
        else:
            validation = {'significant': False, 'pvalue': None}

        visualizer.plot_timeline(benchmark, rolling_std, rolling_std, threshold, convergence_date)

        results[benchmark] = {
            'convergence_date': convergence_date,
            'final_std': final_std,
            'threshold': threshold,
            'validation': validation
        }

        print(f"  Threshold: {threshold*100:.2f}%")
        print(f"  Convergence: {convergence_date or 'Not detected'}")
        if convergence_date:
            print(f"  Final std: {final_std:.6f} ({final_std*100:.3f}%)")
            print(f"  p-value: {validation.get('pvalue', 'N/A')}")

    visualizer.plot_gate_metrics(target_benchmarks=2, actual_benchmarks=converged_count)

    gate_pass = converged_count >= 2
    output = {
        'results': results,
        'converged_count': converged_count,
        'gate_pass': gate_pass
    }

    with open(output_dir / 'results' / 'convergence_results.json', 'w') as f:
        json.dump(output, indent=2, fp=f)

    print(f"\n{'='*50}")
    print(f"Gate verdict: {'PASS' if gate_pass else 'FAIL'}")
    print(f"Benchmarks converged: {converged_count}/3 (target: 2)")
    print(f"{'='*50}")

    return output

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    results = run_convergence_experiment(
        data_dir=base_dir / "data" / "pwc_leaderboards",
        output_dir=base_dir
    )
