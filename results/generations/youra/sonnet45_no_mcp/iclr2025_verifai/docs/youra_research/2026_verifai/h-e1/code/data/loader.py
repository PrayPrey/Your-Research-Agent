"""
Data Loader for LeanDojo Benchmark
Implements TheoremSampler for h-e1 experiment
"""

from typing import List
import numpy as np


class TheoremSampler:
    """Sample theorems from LeanDojo Benchmark."""

    def __init__(self, repo_url: str, commit_hash: str, sample_size: int = 100, seed: int = 42):
        """
        Initialize sampler with dataset parameters.

        Args:
            repo_url: GitHub URL for Lean mathlib repository
            commit_hash: Specific commit hash for reproducibility
            sample_size: Number of theorems to sample
            seed: Random seed for reproducibility
        """
        self.repo_url = repo_url
        self.commit_hash = commit_hash
        self.sample_size = sample_size
        self.seed = seed
        np.random.seed(seed)

    def load_benchmark(self) -> List:
        """
        Load LeanDojo Benchmark dataset.

        Returns:
            List of Theorem objects from LeanDojo
        """
        try:
            from lean_dojo import LeanGitRepo, Benchmark

            print(f"Loading LeanDojo Benchmark from {self.repo_url}...")
            print(f"Commit: {self.commit_hash}")

            # Load the benchmark
            benchmark = Benchmark(LeanGitRepo(self.repo_url, self.commit_hash))

            # Get test theorems
            test_theorems = [thm for thm in benchmark if thm.split == "test"]

            print(f"Loaded {len(test_theorems)} test theorems from benchmark")
            return test_theorems

        except ImportError:
            print("ERROR: LeanDojo not installed. Install with: pip install lean-dojo")
            raise
        except Exception as e:
            print(f"ERROR loading benchmark: {e}")
            raise

    def sample_theorems(self, benchmark: List) -> List:
        """
        Random sample from benchmark.

        Args:
            benchmark: List of Theorem objects

        Returns:
            Random sample of theorems (length = sample_size)
        """
        if len(benchmark) < self.sample_size:
            print(f"WARNING: Benchmark has only {len(benchmark)} theorems, less than requested {self.sample_size}")
            return benchmark

        # Random sampling with fixed seed
        np.random.seed(self.seed)
        indices = np.random.choice(len(benchmark), size=self.sample_size, replace=False)
        sampled = [benchmark[i] for i in indices]

        print(f"Sampled {len(sampled)} theorems (seed={self.seed})")
        return sampled
