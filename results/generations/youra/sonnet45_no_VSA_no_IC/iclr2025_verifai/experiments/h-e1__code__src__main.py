"""Main orchestrator for lean-auto baseline evaluation."""
import sys
import argparse
from pathlib import Path

from loader import load_minif2f_problems
from worker import run_parallel_evaluation
from aggregate import compute_metrics, validate_quality_gates, save_summary, merge_results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-file', required=True, help='Path to miniF2F Test.lean')
    parser.add_argument('--output-dir', default='./data/results', help='Output directory')
    parser.add_argument('--checkpoint-dir', default='./data/checkpoints', help='Checkpoint directory')
    parser.add_argument('--n-workers', type=int, default=8, help='Number of workers')
    parser.add_argument('--pilot', action='store_true', help='Pilot run (N=20)')

    args = parser.parse_args()

    print(f"Loading problems from {args.test_file}...")
    problems = load_minif2f_problems(args.test_file)
    print(f"Loaded {len(problems)} problems")

    if args.pilot:
        problems = problems[:20]
        print(f"Pilot mode: evaluating first {len(problems)} problems")

    print(f"Starting evaluation with {args.n_workers} workers...")
    results = run_parallel_evaluation(
        problems,
        n_workers=args.n_workers,
        checkpoint_dir=args.checkpoint_dir
    )

    print(f"Completed {len(results)} evaluations")

    print("Computing metrics...")
    stats = compute_metrics(results)

    print(f"\nResults:")
    print(f"  Success rate: {stats.success_rate:.3f} [{stats.ci_95_low:.3f}, {stats.ci_95_high:.3f}]")
    print(f"  Solved: {stats.solved_count}, Timeout: {stats.timeout_count}, Error: {stats.error_count}")
    print(f"  Tactic count: mean={stats.mean_tactics:.1f}, std={stats.std_tactics:.1f}, CV={stats.cv_tactics:.2f}")

    validation = validate_quality_gates(results, stats)
    print(f"\nValidation gates:")
    for gate, passed in validation['gates'].items():
        status = 'PASS' if passed else 'FAIL'
        print(f"  {gate}: {status}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = merge_results(results)
    df.to_csv(output_dir / 'results.csv', index=False)
    print(f"\nSaved results to {output_dir / 'results.csv'}")

    save_summary(stats, validation, str(output_dir / 'summary.json'))
    print(f"Saved summary to {output_dir / 'summary.json'}")

    return 0 if validation['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
