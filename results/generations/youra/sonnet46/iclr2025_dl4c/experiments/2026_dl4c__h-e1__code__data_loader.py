"""APPS dataset loader for h-e1 prescreening pipeline."""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class APPSDataLoader:
    """Loads and filters APPS introductory problems from HuggingFace."""

    def __init__(self, dataset_id: str = "codeparrot/apps", split: str = "train"):
        self.dataset_id = dataset_id
        self.split = split
        self._dataset = None

    def _ensure_loaded(self) -> None:
        if self._dataset is None:
            from datasets import load_dataset
            logger.info(f"Loading dataset {self.dataset_id} split={self.split}")
            self._dataset = load_dataset(self.dataset_id, split=self.split, trust_remote_code=True)

    def parse_test_cases(self, raw_tests: str) -> list[dict]:
        """Parse raw test cases JSON string into list of {input, output} dicts.

        The APPS dataset stores test cases as a JSON string with keys
        'inputs' and 'outputs' (lists).

        Returns:
            list of dicts with 'input' (str) and 'output' (str) keys.
        """
        if not raw_tests:
            return []
        try:
            import sys
            if hasattr(sys, 'set_int_max_str_digits'):
                sys.set_int_max_str_digits(0)  # Unlimited
            data = json.loads(raw_tests)
            inputs = data.get("inputs", [])
            outputs = data.get("outputs", [])
            test_cases = []
            for inp, out in zip(inputs, outputs):
                test_cases.append({
                    "input": str(inp) if inp is not None else "",
                    "output": str(out) if out is not None else "",
                })
            return test_cases
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            logger.debug(f"Failed to parse test cases: {e}")
            return []

    def load_and_filter(self, min_test_cases: int = 3) -> list[dict]:
        """Load APPS dataset, filter difficulty=introductory and T>=min_test_cases.

        Returns:
            list of problem dicts with keys:
                problem_id (int), prompt (str), test_cases (list[dict]), T (int)
        """
        self._ensure_loaded()
        problems = []
        skipped_difficulty = 0
        skipped_tests = 0
        skipped_parse = 0

        for idx, example in enumerate(self._dataset):
            # Filter by difficulty
            difficulty = example.get("difficulty", "")
            if difficulty != "introductory":
                skipped_difficulty += 1
                continue

            # Parse test cases
            raw_tests = example.get("input_output", "") or ""
            test_cases = self.parse_test_cases(raw_tests)

            if not test_cases:
                skipped_parse += 1
                continue

            # Filter by minimum test case count
            if len(test_cases) < min_test_cases:
                skipped_tests += 1
                continue

            prompt = example.get("question", "") or ""
            problems.append({
                "problem_id": idx,
                "prompt": prompt,
                "test_cases": test_cases,
                "T": len(test_cases),
            })

        logger.info(
            f"Loaded {len(problems)} introductory problems with T>={min_test_cases}. "
            f"Skipped: difficulty={skipped_difficulty}, parse_fail={skipped_parse}, "
            f"insufficient_tests={skipped_tests}"
        )
        return problems


def load_apps_introductory(min_test_cases: int = 3) -> list[dict]:
    """Convenience function: load APPS introductory problems with T>=min_test_cases.

    Returns:
        list of problem dicts.
    """
    loader = APPSDataLoader()
    return loader.load_and_filter(min_test_cases=min_test_cases)
