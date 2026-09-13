"""H-M3 main evaluation script (simple sequential version for POC)."""
import argparse
import json
from pathlib import Path
import sys

from loader import load_minif2f_problems
from worker import evaluate_single_problem
from random_sampler import TacticSampler


def main():
    parser = argparse.ArgumentParser(description='H-M3: Random Mathlib Tactic Sampler')
    parser.add_argument('--minif2f-path', type=str, required=True)
    parser.add_argument('--config', type=str, default='config/tactic_distribution.yaml')
    parser.add_argument('--budget', type=int, default=15)
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--output-dir', type=str, default='results')
    args = parser.parse_args()

    # Setup
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load
    print(f"Loading problems from {args.minif2f_path}")
    problems = load_minif2f_problems(args.minif2f_path)
    print(f"Loaded {len(problems)} problems")

    # Evaluate sequentially (POC mode)
    sampler = TacticSampler(args.config)
    results = []

    for idx, problem in enumerate(problems):
        print(f"Evaluating [{idx+1}/{len(problems)}] {problem.id}...")
        result = evaluate_single_problem(
            (problem, idx),
            sampler,
            budget=args.budget,
            timeout=args.timeout
        )
        results.append(result)

    # Write JSONL
    jsonl_path = output_dir / 'h_m3_results.jsonl'
    with open(jsonl_path, 'w') as f:
        for result in results:
            json.dump({
                'problem_id': result.problem_id,
                'source': result.source,
                'outcome': result.outcome,
                'time_s': result.time_s,
                'tactics_used': result.tactics_used,
                'tactic_sequence': result.tactic_sequence,
                'seed': result.seed
            }, f)
            f.write('\n')

    solved = sum(1 for r in results if r.outcome == 'solved')
    print(f"\nResults written to {jsonl_path}")
    print(f"Total: {len(results)}, Solved: {solved}")


if __name__ == '__main__':
    main()
