"""H-M3 main evaluation script."""
import argparse
import json
import multiprocessing as mp
from pathlib import Path
from typing import List
import sys

from loader import load_minif2f_problems, Problem
from worker import evaluate_single_problem, ProverResult, save_checkpoint
from random_sampler import TacticSampler


def worker_fn(args):
    """Parallel worker function."""
    problems_chunk, worker_id, config_path, budget, timeout, checkpoint_dir = args

    sampler = TacticSampler(config_path)
    results = []

    for problem_data in problems_chunk:
        result = evaluate_single_problem(
            problem_data,
            sampler,
            budget=budget,
            timeout=timeout
        )
        results.append(result)

        if len(results) % 10 == 0:
            print(f"[Worker {worker_id}] Completed {len(results)}/{len(problems_chunk)}")
            save_checkpoint(worker_id, results, checkpoint_dir)

    save_checkpoint(worker_id, results, checkpoint_dir)
    return results


def main():
    parser = argparse.ArgumentParser(description='H-M3: Random Mathlib Tactic Sampler')
    parser.add_argument('--minif2f-path', type=str, required=True, help='Path to miniF2F/Test.lean')
    parser.add_argument('--config', type=str, default='config/tactic_distribution.yaml')
    parser.add_argument('--budget', type=int, default=15)
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--output-dir', type=str, default='results')
    parser.add_argument('--checkpoint-dir', type=str, default='checkpoints')
    args = parser.parse_args()

    # Setup
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Load problems
    print(f"Loading problems from {args.minif2f_path}")
    problems = load_minif2f_problems(args.minif2f_path)
    print(f"Loaded {len(problems)} problems")

    # Index problems for deterministic seeding
    indexed_problems = list(enumerate(problems))

    # Split work
    chunk_size = len(indexed_problems) // args.workers
    chunks = [
        indexed_problems[i*chunk_size:(i+1)*chunk_size]
        for i in range(args.workers)
    ]
    if len(indexed_problems) % args.workers != 0:
        chunks[-1].extend(indexed_problems[args.workers*chunk_size:])

    # Prepare worker args
    worker_args = [
        (chunk, i, args.config, args.budget, args.timeout, str(checkpoint_dir))
        for i, chunk in enumerate(chunks)
    ]

    # Run parallel evaluation
    print(f"\nStarting evaluation with {args.workers} workers")
    print(f"Budget: {args.budget} tactics, Timeout: {args.timeout}s per problem\n")

    with mp.Pool(args.workers) as pool:
        results_chunks = pool.map(worker_fn, worker_args)

    # Flatten results
    all_results: List[ProverResult] = []
    for chunk in results_chunks:
        all_results.extend(chunk)

    # Write JSONL
    jsonl_path = output_dir / 'h_m3_results.jsonl'
    with open(jsonl_path, 'w') as f:
        for result in all_results:
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

    print(f"\nResults written to {jsonl_path}")
    print(f"Total problems: {len(all_results)}")
    print(f"Solved: {sum(1 for r in all_results if r.outcome == 'solved')}")


if __name__ == '__main__':
    main()
