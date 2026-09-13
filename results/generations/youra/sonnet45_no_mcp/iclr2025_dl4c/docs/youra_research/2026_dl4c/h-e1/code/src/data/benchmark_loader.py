"""
Benchmark Data Loader for HumanEval, MBPP, and APPS
Based on 03_architecture.md and 03_logic.md specifications
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datasets import load_dataset
import os


class BenchmarkLoader(ABC):
    """Abstract base class for benchmark dataset loaders."""

    def __init__(self, benchmark_name: str, cache_dir: Optional[str] = None):
        self.benchmark_name = benchmark_name
        self.cache_dir = cache_dir or f"data/{benchmark_name}"
        self.dataset = None

    @abstractmethod
    def load_dataset(self) -> Dict:
        """Load the benchmark dataset."""
        pass

    @abstractmethod
    def get_test_cases(self, problem_id: str) -> List:
        """Get test cases for a specific problem."""
        pass

    @abstractmethod
    def get_problem_count(self) -> int:
        """Get total number of problems in benchmark."""
        pass


class HumanEvalLoader(BenchmarkLoader):
    """Loader for HumanEval benchmark (164 problems)."""

    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__("HumanEval", cache_dir)

    def load_dataset(self) -> Dict:
        """Load HumanEval dataset from HuggingFace."""
        self.dataset = load_dataset("openai_humaneval", cache_dir=self.cache_dir)
        return self.dataset

    def get_test_cases(self, problem_id: str) -> List:
        """Get test cases for a HumanEval problem."""
        if self.dataset is None:
            self.load_dataset()

        # HumanEval uses task_id as identifier
        for problem in self.dataset['test']:
            if problem['task_id'] == problem_id:
                return [problem['test']]
        return []

    def get_problem_count(self) -> int:
        """Get total number of HumanEval problems."""
        if self.dataset is None:
            self.load_dataset()
        return len(self.dataset['test'])


class MBPPLoader(BenchmarkLoader):
    """Loader for MBPP benchmark (~1000 problems)."""

    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__("MBPP", cache_dir)

    def load_dataset(self) -> Dict:
        """Load MBPP dataset from HuggingFace."""
        self.dataset = load_dataset("mbpp", cache_dir=self.cache_dir)
        return self.dataset

    def get_test_cases(self, problem_id: str) -> List:
        """Get test cases for an MBPP problem."""
        if self.dataset is None:
            self.load_dataset()

        # MBPP has multiple splits
        for split in ['train', 'test', 'validation']:
            if split in self.dataset:
                for problem in self.dataset[split]:
                    if str(problem['task_id']) == str(problem_id):
                        return problem.get('test_list', [])
        return []

    def get_problem_count(self) -> int:
        """Get total number of MBPP problems."""
        if self.dataset is None:
            self.load_dataset()
        return sum(len(self.dataset[split]) for split in self.dataset.keys())


class APPSLoader(BenchmarkLoader):
    """Loader for APPS benchmark (10000 problems)."""

    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__("APPS", cache_dir)

    def load_dataset(self) -> Dict:
        """Load APPS dataset from HuggingFace."""
        try:
            self.dataset = load_dataset("codeparrot/apps", cache_dir=self.cache_dir)
            return self.dataset
        except Exception as e:
            print(f"Warning: APPS dataset not available: {e}")
            print("Will use published results for APPS benchmark")
            return None

    def get_test_cases(self, problem_id: str) -> List:
        """Get test cases for an APPS problem."""
        if self.dataset is None:
            return []

        # APPS has hidden test cases
        for split in self.dataset.keys():
            for problem in self.dataset[split]:
                if str(problem.get('problem_id', '')) == str(problem_id):
                    return problem.get('test_cases', [])
        return []

    def get_problem_count(self) -> int:
        """Get total number of APPS problems."""
        if self.dataset is None:
            return 0
        return sum(len(self.dataset[split]) for split in self.dataset.keys())


def create_loader(benchmark_name: str, cache_dir: Optional[str] = None) -> BenchmarkLoader:
    """Factory function to create appropriate benchmark loader."""
    loaders = {
        "HumanEval": HumanEvalLoader,
        "MBPP": MBPPLoader,
        "APPS": APPSLoader
    }

    loader_class = loaders.get(benchmark_name)
    if loader_class is None:
        raise ValueError(f"Unknown benchmark: {benchmark_name}")

    return loader_class(cache_dir)
