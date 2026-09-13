"""
Baseline Methods for Comparison

This module implements baseline methods for code generation:
1. Base Model: No alignment, just generation
2. Binary Execution RL: Pass/fail reward only
3. Random Preference: Random preference pairs
4. Self-Repair: Simple self-repair without ExePlay
"""
import torch
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from dataclasses import dataclass

from execution_feedback import (
    execute_code_with_tests,
    compute_execution_quality_score,
    extract_code_from_response,
    ExecutionResult
)


@dataclass
class BaselineResult:
    """Result from a baseline method"""
    method_name: str
    pass_rate: float
    avg_eqs: float
    total_solutions: int
    passed_solutions: int
    solutions_per_task: Dict[str, List[Tuple[str, float, bool]]]


class BaseModelBaseline:
    """
    Baseline 1: Base Model without any alignment.
    Just generates code using the base LLM.
    """

    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def generate_and_evaluate(
        self,
        tasks: List[Dict[str, Any]],
        num_samples: int = 4,
        temperature: float = 0.7,
        max_length: int = 256
    ) -> BaselineResult:
        """Generate solutions and evaluate."""
        all_solutions = {}
        total = 0
        passed = 0
        eqs_scores = []

        for task in tasks:
            task_id = str(task.get('id', ''))
            all_solutions[task_id] = []

            prompt = self._create_prompt(task)
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            for _ in range(num_samples):
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_length,
                        temperature=temperature,
                        do_sample=True,
                        top_p=0.95,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )

                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                code = generated_text[len(prompt):].strip()
                code = extract_code_from_response(code)

                if 'prompt' in task and task['prompt'].strip().startswith('def '):
                    if not code.strip().startswith('def '):
                        code = task['prompt'] + '\n' + code

                # Execute and score
                test_cases = task.get('test_cases', [])
                exec_result = execute_code_with_tests(code, test_cases)
                eqs = compute_execution_quality_score(exec_result)

                total += 1
                if exec_result.passed:
                    passed += 1
                eqs_scores.append(eqs)

                all_solutions[task_id].append((code, eqs, exec_result.passed))

        return BaselineResult(
            method_name="Base Model",
            pass_rate=passed / total if total > 0 else 0,
            avg_eqs=np.mean(eqs_scores) if eqs_scores else 0,
            total_solutions=total,
            passed_solutions=passed,
            solutions_per_task=all_solutions
        )

    def _create_prompt(self, task: Dict[str, Any]) -> str:
        problem = task.get('problem', '')
        prompt = task.get('prompt', '')
        if prompt:
            return f"# Problem: {problem}\n\n# Complete the following function:\n{prompt}\n"
        else:
            return f"# Problem: {problem}\n\n# Write a Python function to solve this problem:\n"


class BinaryExecutionBaseline:
    """
    Baseline 2: Binary Execution Feedback.
    Only uses pass/fail signals, no fine-grained EQS.
    """

    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def generate_and_evaluate(
        self,
        tasks: List[Dict[str, Any]],
        num_samples: int = 4,
        temperature: float = 0.7,
        max_length: int = 256
    ) -> BaselineResult:
        """Generate solutions using binary feedback only."""
        all_solutions = {}
        total = 0
        passed = 0
        eqs_scores = []

        for task in tasks:
            task_id = str(task.get('id', ''))
            all_solutions[task_id] = []

            prompt = self._create_prompt(task)
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            for _ in range(num_samples):
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_length,
                        temperature=temperature,
                        do_sample=True,
                        top_p=0.95,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )

                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                code = generated_text[len(prompt):].strip()
                code = extract_code_from_response(code)

                if 'prompt' in task and task['prompt'].strip().startswith('def '):
                    if not code.strip().startswith('def '):
                        code = task['prompt'] + '\n' + code

                # Execute with binary feedback only
                test_cases = task.get('test_cases', [])
                exec_result = execute_code_with_tests(code, test_cases)

                # Binary score: 1.0 if passed, 0.0 otherwise
                binary_score = 1.0 if exec_result.passed else 0.0

                total += 1
                if exec_result.passed:
                    passed += 1
                eqs_scores.append(binary_score)

                all_solutions[task_id].append((code, binary_score, exec_result.passed))

        return BaselineResult(
            method_name="Binary Execution",
            pass_rate=passed / total if total > 0 else 0,
            avg_eqs=np.mean(eqs_scores) if eqs_scores else 0,
            total_solutions=total,
            passed_solutions=passed,
            solutions_per_task=all_solutions
        )

    def _create_prompt(self, task: Dict[str, Any]) -> str:
        problem = task.get('problem', '')
        prompt = task.get('prompt', '')
        if prompt:
            return f"# Problem: {problem}\n\n# Complete the following function:\n{prompt}\n"
        else:
            return f"# Problem: {problem}\n\n# Write a Python function to solve this problem:\n"


class SelfRepairBaseline:
    """
    Baseline 3: Self-Repair.
    Attempts to repair failed solutions using error feedback.
    """

    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def generate_and_evaluate(
        self,
        tasks: List[Dict[str, Any]],
        num_samples: int = 4,
        max_repairs: int = 2,
        temperature: float = 0.7,
        max_length: int = 256
    ) -> BaselineResult:
        """Generate solutions with self-repair attempts."""
        all_solutions = {}
        total = 0
        passed = 0
        eqs_scores = []

        for task in tasks:
            task_id = str(task.get('id', ''))
            all_solutions[task_id] = []

            prompt = self._create_prompt(task)
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            for _ in range(num_samples):
                # Initial generation
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_length,
                        temperature=temperature,
                        do_sample=True,
                        top_p=0.95,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )

                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                code = generated_text[len(prompt):].strip()
                code = extract_code_from_response(code)

                if 'prompt' in task and task['prompt'].strip().startswith('def '):
                    if not code.strip().startswith('def '):
                        code = task['prompt'] + '\n' + code

                # Execute
                test_cases = task.get('test_cases', [])
                exec_result = execute_code_with_tests(code, test_cases)

                # Attempt repairs if failed
                repair_count = 0
                while not exec_result.passed and repair_count < max_repairs:
                    # Create repair prompt
                    repair_prompt = self._create_repair_prompt(task, code, exec_result)
                    repair_inputs = self.tokenizer(
                        repair_prompt, return_tensors="pt", truncation=True, max_length=512
                    )
                    repair_inputs = {k: v.to(self.device) for k, v in repair_inputs.items()}

                    with torch.no_grad():
                        repair_outputs = self.model.generate(
                            **repair_inputs,
                            max_new_tokens=max_length,
                            temperature=0.5,  # Lower temperature for repairs
                            do_sample=True,
                            top_p=0.9,
                            pad_token_id=self.tokenizer.pad_token_id,
                            eos_token_id=self.tokenizer.eos_token_id,
                        )

                    repair_text = self.tokenizer.decode(repair_outputs[0], skip_special_tokens=True)
                    repaired_code = repair_text[len(repair_prompt):].strip()
                    repaired_code = extract_code_from_response(repaired_code)

                    if 'prompt' in task and task['prompt'].strip().startswith('def '):
                        if not repaired_code.strip().startswith('def '):
                            repaired_code = task['prompt'] + '\n' + repaired_code

                    # Execute repaired code
                    exec_result = execute_code_with_tests(repaired_code, test_cases)
                    code = repaired_code
                    repair_count += 1

                eqs = compute_execution_quality_score(exec_result)

                total += 1
                if exec_result.passed:
                    passed += 1
                eqs_scores.append(eqs)

                all_solutions[task_id].append((code, eqs, exec_result.passed))

        return BaselineResult(
            method_name="Self-Repair",
            pass_rate=passed / total if total > 0 else 0,
            avg_eqs=np.mean(eqs_scores) if eqs_scores else 0,
            total_solutions=total,
            passed_solutions=passed,
            solutions_per_task=all_solutions
        )

    def _create_prompt(self, task: Dict[str, Any]) -> str:
        problem = task.get('problem', '')
        prompt = task.get('prompt', '')
        if prompt:
            return f"# Problem: {problem}\n\n# Complete the following function:\n{prompt}\n"
        else:
            return f"# Problem: {problem}\n\n# Write a Python function to solve this problem:\n"

    def _create_repair_prompt(
        self,
        task: Dict[str, Any],
        code: str,
        exec_result: ExecutionResult
    ) -> str:
        error_info = ""
        if exec_result.error_messages:
            error_info = "\n".join(exec_result.error_messages[:2])

        return f"""# Problem: {task.get('problem', '')}

# The following code has errors:
{code}

# Errors:
{error_info}

# Please fix the code to make it work correctly:
"""


def run_all_baselines(
    model,
    tokenizer,
    tasks: List[Dict[str, Any]],
    num_samples: int = 4,
    device: str = "cuda"
) -> Dict[str, BaselineResult]:
    """
    Run all baseline methods and return results.

    Args:
        model: The language model
        tokenizer: The tokenizer
        tasks: List of task dictionaries
        num_samples: Number of samples per task
        device: Device to use

    Returns:
        Dictionary mapping method names to results
    """
    results = {}

    print("\n" + "="*50)
    print("Running Base Model Baseline...")
    print("="*50)
    base_baseline = BaseModelBaseline(model, tokenizer, device)
    results["Base Model"] = base_baseline.generate_and_evaluate(tasks, num_samples)
    print(f"Base Model - Pass Rate: {results['Base Model'].pass_rate:.4f}, Avg EQS: {results['Base Model'].avg_eqs:.4f}")

    print("\n" + "="*50)
    print("Running Binary Execution Baseline...")
    print("="*50)
    binary_baseline = BinaryExecutionBaseline(model, tokenizer, device)
    results["Binary Execution"] = binary_baseline.generate_and_evaluate(tasks, num_samples)
    print(f"Binary Execution - Pass Rate: {results['Binary Execution'].pass_rate:.4f}, Avg Score: {results['Binary Execution'].avg_eqs:.4f}")

    print("\n" + "="*50)
    print("Running Self-Repair Baseline...")
    print("="*50)
    repair_baseline = SelfRepairBaseline(model, tokenizer, device)
    results["Self-Repair"] = repair_baseline.generate_and_evaluate(tasks, num_samples)
    print(f"Self-Repair - Pass Rate: {results['Self-Repair'].pass_rate:.4f}, Avg EQS: {results['Self-Repair'].avg_eqs:.4f}")

    return results
