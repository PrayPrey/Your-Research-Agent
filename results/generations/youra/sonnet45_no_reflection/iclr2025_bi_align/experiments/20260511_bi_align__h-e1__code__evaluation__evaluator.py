"""Evaluators for MMLU and HumanEval benchmarks."""

import pandas as pd
import re
from typing import Dict, List


class MMLUEvaluator:
    """MMLU evaluation with few-shot prompting."""

    def __init__(self, model_client, data_loader):
        self.model_client = model_client
        self.data_loader = data_loader

    def evaluate(self, lambda_value: float) -> pd.DataFrame:
        """Run MMLU evaluation for given compliance level."""
        from models.api_client import PolicyLayer

        system_prompt = PolicyLayer.get_system_prompt(lambda_value)
        results = []

        print(f"\nEvaluating MMLU (λ={lambda_value})...")

        for subject_idx, subject in enumerate(self.data_loader.subjects):
            if subject_idx % 10 == 0:
                print(f"Progress: {subject_idx}/{len(self.data_loader.subjects)} subjects")

            # Get few-shot examples
            few_shot_examples = self.data_loader.get_few_shot_examples(subject)

            # Get test questions for this subject
            test_items = [item for item in self.data_loader.dataset["test"] if item["subject"] == subject]

            for item in test_items:
                # Build few-shot prompt
                prompt = self._build_few_shot_prompt(few_shot_examples, item)

                # Get model response
                response = self.model_client.generate(prompt, system_prompt)

                # Parse answer
                predicted = self._parse_answer(response)
                correct = (predicted == item["answer"])

                results.append({
                    "lambda": lambda_value,
                    "subject": subject,
                    "question_id": item.get("question", "")[:50],  # Use first 50 chars as ID
                    "predicted": predicted,
                    "ground_truth": item["answer"],
                    "correct": correct
                })

        return pd.DataFrame(results)

    def _build_few_shot_prompt(self, examples: List[Dict], test_item: Dict) -> str:
        """Build few-shot prompt."""
        prompt = ""

        # Add few-shot examples
        for ex in examples:
            prompt += self.data_loader.format_question(ex)
            prompt += f" {ex['answer']}\n\n"

        # Add test question
        prompt += self.data_loader.format_question(test_item)

        return prompt

    def _parse_answer(self, response: str) -> str:
        """Extract A/B/C/D from response."""
        # Look for single letter answer
        match = re.search(r'\b([A-D])\b', response)
        if match:
            return match.group(1)

        # Fallback: return first character if it's A-D
        if response and response[0] in "ABCD":
            return response[0]

        return "INVALID"

    def compute_accuracy(self, results: pd.DataFrame) -> float:
        """Compute accuracy."""
        return results["correct"].mean()


class HumanEvalEvaluator:
    """HumanEval evaluation with pass@k metric."""

    def __init__(self, model_client, data_loader):
        self.model_client = model_client
        self.data_loader = data_loader

    def evaluate(self, lambda_value: float) -> pd.DataFrame:
        """Run HumanEval evaluation for given compliance level."""
        from models.api_client import PolicyLayer

        system_prompt = PolicyLayer.get_system_prompt(lambda_value)
        results = []

        print(f"\nEvaluating HumanEval (λ={lambda_value})...")

        for i, task_id in enumerate(self.data_loader.problems):
            if i % 20 == 0:
                print(f"Progress: {i}/{len(self.data_loader.problems)} problems")

            # Get problem prompt
            prompt = self.data_loader.format_problem(task_id)

            # Generate completion
            completion = self.model_client.generate(
                prompt, system_prompt, max_tokens=512
            )

            # Execute tests
            passed = self._execute_tests(task_id, completion)

            results.append({
                "lambda": lambda_value,
                "task_id": task_id,
                "completion": completion,
                "passed": passed
            })

        return pd.DataFrame(results)

    def _execute_tests(self, task_id: str, completion: str) -> bool:
        """Execute unit tests for completion."""
        from human_eval.execution import check_correctness
        import warnings

        # Suppress warnings from execution
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            try:
                result = check_correctness(
                    task_id,
                    completion,
                    timeout=3.0
                )
                return result["passed"]
            except Exception:
                return False

    def compute_pass_at_k(self, results: pd.DataFrame, k: int = 1) -> float:
        """Compute pass@k metric."""
        # For k=1 with single sample, pass@1 = mean(passed)
        return results["passed"].mean()
