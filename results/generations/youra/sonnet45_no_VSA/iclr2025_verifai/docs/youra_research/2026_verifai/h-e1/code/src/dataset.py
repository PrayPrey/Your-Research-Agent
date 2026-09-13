"""Dataset manager for FM-bench-verified."""

from typing import List
from dataclasses import dataclass
from pathlib import Path
import random


@dataclass
class Program:
    """Single C program with ground truth ACSL."""
    id: str
    c_code: str
    gold_acsl: str
    properties: List[str]


class DatasetManager:
    """Manage benchmark dataset."""

    def __init__(self, dataset_name: str = "fm-universe/FM-bench-verified"):
        self.dataset_name = dataset_name
        self.dataset = None

    def load_benchmark(self, num_programs: int = 10, seed: int = 42) -> List[Program]:
        """
        Load benchmark programs.

        Args:
            num_programs: Number of programs to select
            seed: Random seed for reproducibility

        Returns:
            List of Program objects
        """
        # Try to load from HuggingFace
        try:
            from datasets import load_dataset
            self.dataset = load_dataset(self.dataset_name, trust_remote_code=True)
            return self._select_programs_from_hf(num_programs, seed)
        except Exception as e:
            print(f"Warning: Could not load HuggingFace dataset: {e}")
            print("Using synthetic fallback programs...")
            return self._create_fallback_programs(num_programs)

    def _select_programs_from_hf(self, num_programs: int, seed: int) -> List[Program]:
        """Select programs from HuggingFace dataset."""
        random.seed(seed)

        # Get train split
        train_data = self.dataset['train']

        # Sample programs
        indices = random.sample(range(len(train_data)), min(num_programs, len(train_data)))

        programs = []
        for idx in indices:
            data = train_data[idx]

            # Extract C code and ACSL
            c_code = self._extract_c_code(data)
            gold_acsl = self._extract_gold_acsl(data)

            programs.append(Program(
                id=f"program_{idx:03d}",
                c_code=c_code,
                gold_acsl=gold_acsl,
                properties=data.get('properties', [])
            ))

        return programs

    def _extract_c_code(self, raw_data: dict) -> str:
        """Extract unannotated C code from dataset."""
        # Try different field names
        for field in ['code', 'c_code', 'source', 'program']:
            if field in raw_data:
                code = raw_data[field]
                # Strip ACSL annotations
                import re
                code = re.sub(r'/\*@.*?\*/', '', code, flags=re.DOTALL)
                return code.strip()

        return raw_data.get('text', '')

    def _extract_gold_acsl(self, raw_data: dict) -> str:
        """Extract gold ACSL specification."""
        for field in ['acsl', 'specification', 'annotated_code']:
            if field in raw_data:
                return raw_data[field]

        return raw_data.get('text', '')

    def _create_fallback_programs(self, num_programs: int) -> List[Program]:
        """Create synthetic programs for testing when dataset unavailable."""

        programs = []

        # Program 1: Simple max
        programs.append(Program(
            id="program_001",
            c_code="""int find_max(int *arr, int n) {
    int max_idx = 0;
    for (int i = 1; i < n; i++) {
        if (arr[i] > arr[max_idx]) max_idx = i;
    }
    return max_idx;
}""",
            gold_acsl="""/*@ requires n > 0;
  @ requires \\valid_read(arr + (0..n-1));
  @ ensures \\result >= 0 && \\result < n;
  @ ensures \\forall integer i; 0 <= i < n ==> arr[i] <= arr[\\result];
  @*/
int find_max(int *arr, int n) {
    int max_idx = 0;
    /*@ loop invariant 1 <= i <= n;
      @ loop invariant 0 <= max_idx < i;
      @ loop invariant \\forall integer j; 0 <= j < i ==> arr[j] <= arr[max_idx];
      @ loop variant n - i;
      @*/
    for (int i = 1; i < n; i++) {
        if (arr[i] > arr[max_idx]) max_idx = i;
    }
    return max_idx;
}""",
            properties=["functional_correctness"]
        ))

        # Program 2: Array sum
        programs.append(Program(
            id="program_002",
            c_code="""int array_sum(int *arr, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}""",
            gold_acsl="""/*@ requires n >= 0;
  @ requires \\valid_read(arr + (0..n-1));
  @ ensures \\result == \\sum(0, n-1, \\lambda integer k; arr[k]);
  @*/
int array_sum(int *arr, int n) {
    int sum = 0;
    /*@ loop invariant 0 <= i <= n;
      @ loop invariant sum == \\sum(0, i-1, \\lambda integer k; arr[k]);
      @ loop variant n - i;
      @*/
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}""",
            properties=["functional_correctness"]
        ))

        # Add more simple programs as needed
        return programs[:num_programs]
