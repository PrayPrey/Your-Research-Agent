"""
Evaluation metrics and analysis for Neural-Symbolic Repair
"""
import numpy as np
from typing import Dict, List, Tuple
import json

class ExperimentResult:
    """Store results for a single problem"""
    def __init__(self, problem_id: int, method: str):
        self.problem_id = problem_id
        self.method = method
        self.success = False
        self.num_iterations = 0
        self.test_pass_rate = 0.0
        self.converged = False
        self.initial_code = ""
        self.final_code = ""
        self.iteration_history = []

    def to_dict(self):
        return {
            "problem_id": self.problem_id,
            "method": self.method,
            "success": self.success,
            "num_iterations": self.num_iterations,
            "test_pass_rate": self.test_pass_rate,
            "converged": self.converged,
            "iteration_history": self.iteration_history
        }

class Evaluator:
    """Evaluate experiment results and compute metrics"""

    def __init__(self):
        self.results = []

    def add_result(self, result: ExperimentResult):
        """Add an experiment result"""
        self.results.append(result)

    def compute_metrics(self, method: str = None) -> Dict:
        """Compute evaluation metrics"""
        # Filter results by method if specified
        filtered_results = self.results
        if method:
            filtered_results = [r for r in self.results if r.method == method]

        if not filtered_results:
            return {}

        # Repair Success Rate (RSR)
        successful = [r for r in filtered_results if r.success]
        rsr = len(successful) / len(filtered_results) if filtered_results else 0

        # Average Repair Iterations (ARI)
        if successful:
            ari = np.mean([r.num_iterations for r in successful])
        else:
            ari = 0

        # Test Pass Rate
        test_pass_rates = [r.test_pass_rate for r in filtered_results]
        avg_test_pass_rate = np.mean(test_pass_rates) if test_pass_rates else 0

        # Convergence Rate
        converged = [r for r in filtered_results if r.converged or r.success]
        convergence_rate = len(converged) / len(filtered_results) if filtered_results else 0

        return {
            "method": method,
            "repair_success_rate": rsr,
            "average_repair_iterations": ari,
            "avg_test_pass_rate": avg_test_pass_rate,
            "convergence_rate": convergence_rate,
            "total_problems": len(filtered_results),
            "successful_repairs": len(successful)
        }

    def compute_all_metrics(self) -> Dict[str, Dict]:
        """Compute metrics for all methods"""
        methods = set(r.method for r in self.results)
        return {method: self.compute_metrics(method) for method in methods}

    def compare_methods(self, method1: str, method2: str) -> Dict:
        """Compare two methods statistically"""
        results1 = [r for r in self.results if r.method == method1]
        results2 = [r for r in self.results if r.method == method2]

        if not results1 or not results2:
            return {}

        # Match problems
        problem_ids = set(r.problem_id for r in results1) & set(r.problem_id for r in results2)

        success_diff = 0
        iteration_diff = []

        for pid in problem_ids:
            r1 = next(r for r in results1 if r.problem_id == pid)
            r2 = next(r for r in results2 if r.problem_id == pid)

            if r1.success and not r2.success:
                success_diff += 1
            elif r2.success and not r1.success:
                success_diff -= 1

            if r1.success and r2.success:
                iteration_diff.append(r1.num_iterations - r2.num_iterations)

        return {
            "method1": method1,
            "method2": method2,
            "success_advantage": success_diff,
            "avg_iteration_difference": np.mean(iteration_diff) if iteration_diff else 0,
            "compared_problems": len(problem_ids)
        }

    def get_iteration_statistics(self, method: str) -> Dict:
        """Get detailed iteration statistics for a method"""
        filtered_results = [r for r in self.results if r.method == method]

        if not filtered_results:
            return {}

        iterations = [r.num_iterations for r in filtered_results]

        return {
            "method": method,
            "mean_iterations": np.mean(iterations),
            "median_iterations": np.median(iterations),
            "min_iterations": np.min(iterations),
            "max_iterations": np.max(iterations),
            "std_iterations": np.std(iterations)
        }

    def save_results(self, filename: str):
        """Save all results to JSON"""
        with open(filename, 'w') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)

    def load_results(self, filename: str):
        """Load results from JSON"""
        with open(filename, 'r') as f:
            data = json.load(f)

        for item in data:
            result = ExperimentResult(item['problem_id'], item['method'])
            result.success = item['success']
            result.num_iterations = item['num_iterations']
            result.test_pass_rate = item['test_pass_rate']
            result.converged = item['converged']
            result.iteration_history = item.get('iteration_history', [])
            self.results.append(result)

    def get_learning_curve_data(self, method: str) -> Tuple[List[int], List[float]]:
        """Get data for learning curves (iteration vs success rate)"""
        filtered_results = [r for r in self.results if r.method == method]

        if not filtered_results:
            return [], []

        # Group by iteration number
        max_iter = max(r.num_iterations for r in filtered_results)
        iterations = list(range(1, max_iter + 2))
        success_rates = []

        for i in iterations:
            # Count problems that succeeded by iteration i
            succeeded = sum(1 for r in filtered_results
                          if r.success and r.num_iterations <= i)
            success_rates.append(succeeded / len(filtered_results))

        return iterations, success_rates
