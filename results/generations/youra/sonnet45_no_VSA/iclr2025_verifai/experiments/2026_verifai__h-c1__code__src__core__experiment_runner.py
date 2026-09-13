"""Experiment orchestrator for h-c1."""

import random
from typing import List, Dict, Tuple
from pathlib import Path
import json


class ExperimentRunner:
    """Orchestrates two-stage experiment: calibration + evaluation."""

    def __init__(self, baselines: Dict):
        self.baseline1 = baselines['iterative_feedback']
        self.baseline2 = baselines['self_consistency']
        self.baseline3 = baselines['hybrid']

    def calibrate_budgets(self, num_validation_programs: int = 15) -> Tuple[Dict, int]:
        """Stage 1: Calibrate on validation set to determine N."""
        from core.compute_budget import ComputeBudgetTracker, ComputeBudget

        total_tokens = 0
        total_time = 0
        total_iterations = 0

        print(f"Stage 1: Calibrating budgets on {num_validation_programs} validation programs...")

        for i in range(num_validation_programs):
            program_id = f"val_prog_{i:03d}"
            budget_tracker = ComputeBudgetTracker()

            # Run baseline 1 to get average budget
            result = self.baseline1.run(program_id, budget_tracker)

            total_tokens += result.compute_budget['total_tokens']
            total_time += result.compute_budget['verifier_time_seconds']
            total_iterations += result.iterations_or_samples

        avg_budget = {
            'total_tokens': total_tokens / num_validation_programs,
            'verifier_time_seconds': total_time / num_validation_programs,
            'iterations': total_iterations / num_validation_programs
        }

        # Compute N for self-consistency
        # Assuming single-shot uses ~3300 tokens and ~15s
        single_shot_tokens = 3300
        single_shot_time = 15.0

        N_from_tokens = int((avg_budget['total_tokens'] * 0.95) / single_shot_tokens)
        N_from_time = int((avg_budget['verifier_time_seconds'] * 0.95) / single_shot_time)
        N = max(3, min(N_from_tokens, N_from_time))

        print(f"Calibration complete:")
        print(f"  - Avg tokens: {avg_budget['total_tokens']:.0f}")
        print(f"  - Avg time: {avg_budget['verifier_time_seconds']:.1f}s")
        print(f"  - Avg iterations: {avg_budget['iterations']:.1f}")
        print(f"  - Computed N for SelfConsistency: {N}")

        return avg_budget, N

    def run_test_set_evaluation(
        self,
        avg_budget: Dict,
        N: int,
        num_test_programs: int = 50,
        checkpoint_freq: int = 10
    ) -> Dict:
        """Stage 2: Evaluate all baselines on test set."""
        from core.compute_budget import ComputeBudgetTracker, ComputeBudget

        target_budget = ComputeBudget(
            total_tokens=int(avg_budget['total_tokens']),
            verifier_time_seconds=avg_budget['verifier_time_seconds'],
            iterations=int(avg_budget['iterations'])
        )

        program_results = []

        print(f"\nStage 2: Evaluating on {num_test_programs} test programs...")

        for i in range(num_test_programs):
            program_id = f"test_prog_{i:03d}"

            # Run all 3 baselines with separate budget trackers
            tracker1 = ComputeBudgetTracker(target_budget=target_budget)
            result1 = self.baseline1.run(program_id, tracker1)

            tracker2 = ComputeBudgetTracker(target_budget=target_budget)
            result2 = self.baseline2.run(program_id, N, tracker2)

            tracker3 = ComputeBudgetTracker(target_budget=target_budget)
            result3 = self.baseline3.run(program_id, tracker3)

            program_result = {
                'program_id': program_id,
                'baseline1': {
                    'discharge_rate': result1.discharge_rate * 100,  # Convert to percentage
                    'compute_budget': result1.compute_budget
                },
                'baseline2': {
                    'discharge_rate': result2.discharge_rate * 100,
                    'compute_budget': result2.compute_budget
                },
                'baseline3': {
                    'discharge_rate': result3.discharge_rate * 100,
                    'compute_budget': result3.compute_budget
                }
            }

            program_results.append(program_result)

            if (i + 1) % checkpoint_freq == 0:
                print(f"  Completed {i + 1}/{num_test_programs} programs")

        print(f"Test set evaluation complete.")

        return {
            'program_results': program_results,
            'calibration_budget': avg_budget,
            'N_samples': N
        }
