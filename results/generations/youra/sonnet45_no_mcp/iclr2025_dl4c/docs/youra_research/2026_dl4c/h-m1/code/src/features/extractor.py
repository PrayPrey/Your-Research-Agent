"""
Execution Trace Feature Extractor
Extracts pass@k, runtime quartiles, and error distributions
Based on 03_logic.md specifications
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from scipy.special import comb


class ExecutionTraceExtractor:
    """Extract execution trace features from benchmark evaluation results."""

    def __init__(self, benchmark_name: str):
        self.benchmark_name = benchmark_name
        self.feature_schema = {
            'pass@1': float, 'pass@10': float, 'pass@100': float,
            'runtime_q25': float, 'runtime_q50': float, 'runtime_q75': float,
            'error_syntax': float, 'error_runtime': float, 'error_timeout': float
        }

    def extract_passk(self, model_outputs: List[Dict], k_values: List[int] = [1, 10, 100]) -> Dict[str, float]:
        """
        Calculate pass@k metrics using Chen et al. 2021 formula.

        Formula: pass@k = E[1 - (n-c choose k) / (n choose k)]
        where n = total samples, c = correct samples
        """
        passk_scores = {}

        for k in k_values:
            probabilities = []

            for problem in model_outputs:
                n = problem.get('n_samples', 1)
                c = problem.get('n_correct', 0)

                # Edge cases
                if c >= k:
                    prob = 1.0  # Guaranteed to pass
                elif c == 0:
                    prob = 0.0  # Impossible to pass
                elif n < k:
                    prob = 1.0 if c > 0 else 0.0
                else:
                    # Standard formula
                    try:
                        prob = 1.0 - float(comb(n - c, k, exact=True)) / float(comb(n, k, exact=True))
                    except:
                        prob = float(c) / float(n)  # Fallback to simple ratio

                probabilities.append(prob)

            passk_scores[f'pass@{k}'] = np.mean(probabilities) if probabilities else 0.0

        return passk_scores

    def extract_runtime_quartiles(self, passing_solutions: List[Dict]) -> Dict[str, float]:
        """
        Compute runtime distribution quartiles for passing solutions.
        Returns 25th, 50th, 75th percentiles in milliseconds.
        """
        if not passing_solutions:
            return {
                'runtime_q25': None,
                'runtime_q50': None,
                'runtime_q75': None
            }

        runtimes = [sol['runtime_ms'] for sol in passing_solutions if 'runtime_ms' in sol]

        if not runtimes:
            return {
                'runtime_q25': None,
                'runtime_q50': None,
                'runtime_q75': None
            }

        # Cap at 99th percentile to exclude extreme outliers
        p99 = np.percentile(runtimes, 99)
        runtimes_capped = [min(r, p99) for r in runtimes]

        return {
            'runtime_q25': float(np.percentile(runtimes_capped, 25)),
            'runtime_q50': float(np.percentile(runtimes_capped, 50)),
            'runtime_q75': float(np.percentile(runtimes_capped, 75))
        }

    def categorize_errors(self, failed_solutions: List[Dict]) -> Dict[str, float]:
        """
        Categorize error types and compute distribution percentages.
        Categories: syntax, runtime, timeout
        """
        if not failed_solutions:
            return {
                'error_syntax': None,
                'error_runtime': None,
                'error_timeout': None
            }

        counters = {'syntax': 0, 'runtime': 0, 'timeout': 0}

        for failure in failed_solutions:
            error_type = failure.get('error_type', 'runtime')
            if error_type in counters:
                counters[error_type] += 1

        total = sum(counters.values())

        if total == 0:
            return {
                'error_syntax': None,
                'error_runtime': None,
                'error_timeout': None
            }

        return {
            'error_syntax': (counters['syntax'] / total) * 100.0,
            'error_runtime': (counters['runtime'] / total) * 100.0,
            'error_timeout': (counters['timeout'] / total) * 100.0
        }

    def extract_all_features(self, model_name: str, evaluation_results: Dict) -> Dict:
        """
        Extract complete feature vector for one model-benchmark pair.

        Args:
            model_name: Model identifier
            evaluation_results: {
                "outputs": List[Dict],  # model_outputs for pass@k
                "passing": List[Dict],   # passing_solutions for runtime
                "failed": List[Dict]     # failed_solutions for errors
            }
        """
        features = {
            'model': model_name,
            'benchmark': self.benchmark_name
        }

        # Extract pass@k
        if 'outputs' in evaluation_results:
            passk = self.extract_passk(evaluation_results['outputs'])
            features.update(passk)

        # Extract runtime quartiles
        if 'passing' in evaluation_results:
            runtime = self.extract_runtime_quartiles(evaluation_results['passing'])
            features.update(runtime)

        # Extract error distributions
        if 'failed' in evaluation_results:
            errors = self.categorize_errors(evaluation_results['failed'])
            features.update(errors)

        return features
