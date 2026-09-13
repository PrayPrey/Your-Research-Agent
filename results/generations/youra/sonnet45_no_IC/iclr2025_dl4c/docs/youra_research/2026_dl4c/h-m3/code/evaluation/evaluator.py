"""
Real evaluation pipeline for code generation experiments
Task: A-7 (Evaluation Pipeline)
Computes pass@1, human_preference, and harmonic_mean from real dataset execution
"""
import torch
import json
import subprocess
import tempfile
import os
from typing import List, Dict, Tuple
from tqdm import tqdm
from pathlib import Path


class CodeEvaluator:
    """Evaluator for code generation using real test execution"""

    def __init__(self, device: str = "cuda", execution_timeout: int = 5):
        self.device = device
        self.execution_timeout = execution_timeout

    def execute_code(self, code: str, test_cases: str, timeout: int = None) -> bool:
        """
        Execute generated code against test cases
        Returns True if all tests pass, False otherwise
        """
        if timeout is None:
            timeout = self.execution_timeout

        # Create temporary file for execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write code and test cases
            f.write(code)
            f.write('\n\n')
            f.write(test_cases)
            temp_path = f.name

        try:
            # Execute with timeout
            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                timeout=timeout,
                text=True
            )

            # Check if execution succeeded (no errors, no assertion failures)
            success = (result.returncode == 0)

            return success

        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            return False
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

    def compute_pass_at_1(
        self,
        model,
        tokenizer,
        test_loader,
        max_samples: int = None
    ) -> Tuple[float, List[Dict]]:
        """
        Compute pass@1 metric on test set

        Returns:
            pass_at_1: float - percentage of problems solved correctly
            results: List[Dict] - per-sample results for analysis
        """
        model.eval()

        total_samples = 0
        passed_samples = 0
        results = []

        with torch.no_grad():
            for batch_idx, batch in enumerate(tqdm(test_loader, desc="Evaluating pass@1")):
                if max_samples and total_samples >= max_samples:
                    break

                prompts = batch['prompt']
                test_cases = batch['test_cases']
                task_ids = batch['sample_id']

                # Generate code for each prompt
                inputs = tokenizer(
                    list(prompts),
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                ).to(self.device)

                outputs = model.generate(
                    **inputs,
                    max_new_tokens=256,
                    do_sample=False,  # Greedy decoding for pass@1
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )

                generated_codes = tokenizer.batch_decode(outputs, skip_special_tokens=True)

                # Evaluate each generated code
                for prompt, code, tests, task_id in zip(prompts, generated_codes, test_cases, task_ids):
                    # Extract only the generated part (after prompt)
                    if prompt in code:
                        code_only = code[len(prompt):].strip()
                    else:
                        code_only = code.strip()

                    # Execute and check
                    passed = self.execute_code(code_only, tests)

                    total_samples += 1
                    if passed:
                        passed_samples += 1

                    results.append({
                        'task_id': task_id,
                        'prompt': prompt,
                        'generated_code': code_only,
                        'test_cases': tests,
                        'passed': passed
                    })

        pass_at_1 = passed_samples / max(total_samples, 1)

        return pass_at_1, results

    def compute_human_preference(
        self,
        results: List[Dict],
        annotation_cache_path: str = None
    ) -> float:
        """
        Compute human preference score

        IMPORTANT: HumanEval/MBPP datasets do not contain human annotations.
        This metric uses code quality indicators INDEPENDENT of execution correctness:
        - Code length appropriateness
        - Documentation quality (docstrings, comments)
        - Structural quality (proper functions, returns)
        - Code complexity (lower is better)

        These metrics provide a quality signal that is NOT derived from pass/fail status,
        avoiding tautological measurement where human_preference would just mirror pass@1.

        In production, this should be replaced with real human annotations if available.
        """
        if annotation_cache_path and os.path.exists(annotation_cache_path):
            # Load cached human annotations
            with open(annotation_cache_path, 'r') as f:
                annotations = json.load(f)

            # Match annotations to results
            scores = []
            for result in results:
                task_id = result['task_id']
                if task_id in annotations:
                    scores.append(annotations[task_id]['score'])

            if scores:
                return sum(scores) / len(scores)

        # Fallback: Independent code quality metrics (NOT based on pass/fail)
        # Real human annotations are not available for HumanEval/MBPP.
        # Use code quality proxies that are independent of execution correctness.
        total_score = 0

        for result in results:
            code = result['generated_code']

            # Start with neutral score (NOT based on pass/fail to avoid tautology)
            score = 0.5

            # Code length quality (prefer moderate length)
            code_len = len(code.strip())
            if 50 <= code_len <= 300:
                score += 0.15  # Reasonable length
            elif code_len < 20:
                score -= 0.15  # Too short, likely incomplete
            elif code_len > 500:
                score -= 0.10  # Too long, may be overcomplicated

            # Documentation quality (independent of correctness)
            has_docstring = '"""' in code or "'''" in code
            has_comments = '#' in code
            if has_docstring:
                score += 0.15
            elif has_comments:
                score += 0.10

            # Structural quality (proper Python patterns)
            has_def = 'def ' in code
            has_return = 'return' in code
            if has_def and has_return:
                score += 0.15  # Well-structured function
            elif has_def:
                score += 0.05  # Function definition but no return

            # Code complexity heuristic (simpler is better)
            complexity_keywords = ['if', 'for', 'while', 'try', 'except', 'elif', 'else']
            complexity_count = sum(code.count(kw) for kw in complexity_keywords)
            if complexity_count <= 3:
                score += 0.10  # Simple code
            elif complexity_count > 8:
                score -= 0.10  # Overly complex

            # Anti-patterns (independent of execution)
            if code.strip() == 'pass' or code.strip() == '':
                score -= 0.3  # Empty/stub code
            if code.count('import') > 5:
                score -= 0.05  # Excessive imports

            # Clamp to [0, 1]
            score = max(0.0, min(1.0, score))
            total_score += score

        return total_score / max(len(results), 1)

    def evaluate_model(
        self,
        model,
        tokenizer,
        test_loader,
        annotation_cache_path: str = None,
        max_samples: int = None
    ) -> Dict[str, float]:
        """
        Full evaluation: pass@1, human_preference, harmonic_mean

        Returns:
            metrics: Dict with pass_at_1, human_preference, harmonic_mean
        """
        # Compute pass@1 with per-sample results
        pass_at_1, results = self.compute_pass_at_1(
            model=model,
            tokenizer=tokenizer,
            test_loader=test_loader,
            max_samples=max_samples
        )

        # Compute human preference (heuristic or cached)
        human_preference = self.compute_human_preference(
            results=results,
            annotation_cache_path=annotation_cache_path
        )

        # Compute harmonic mean
        if pass_at_1 + human_preference > 0:
            harmonic_mean = 2 * (pass_at_1 * human_preference) / (pass_at_1 + human_preference)
        else:
            harmonic_mean = 0.0

        return {
            'pass_at_1': pass_at_1,
            'human_preference': human_preference,
            'harmonic_mean': harmonic_mean,
            'total_samples': len(results),
            'passed_samples': sum(1 for r in results if r['passed'])
        }


def evaluate_baseline(
    model_name: str,
    feedback_type: str,
    test_loader,
    device: str,
    checkpoint_path: str = None
) -> Dict[str, float]:
    """
    Evaluate a baseline model (execution_only, ai_only, human_only)

    Args:
        model_name: HuggingFace model identifier
        feedback_type: Type of feedback used during training
        test_loader: Test dataset loader
        device: cuda or cpu
        checkpoint_path: Optional path to trained checkpoint

    Returns:
        metrics: Dict with evaluation results
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Load model
    if checkpoint_path and os.path.exists(checkpoint_path):
        model = AutoModelForCausalLM.from_pretrained(checkpoint_path)
    else:
        model = AutoModelForCausalLM.from_pretrained(model_name)

    model = model.to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Evaluate
    evaluator = CodeEvaluator(device=device)
    metrics = evaluator.evaluate_model(
        model=model,
        tokenizer=tokenizer,
        test_loader=test_loader
    )

    return metrics


if __name__ == "__main__":
    # Test evaluator
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from data.dataset import create_dataloaders

    print("Testing CodeEvaluator...")

    model_name = "Salesforce/codegen-350M-mono"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load model
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model = model.to(device)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Create test loader (small subset)
    _, _, test_loader = create_dataloaders(
        tokenizer=tokenizer,
        batch_size=2,
        cache_dir="../.data_cache/datasets"
    )

    # Evaluate
    evaluator = CodeEvaluator(device=device)
    metrics = evaluator.evaluate_model(
        model=model,
        tokenizer=tokenizer,
        test_loader=test_loader,
        max_samples=10  # Small test
    )

    print(f"\nTest Results:")
    print(f"  Pass@1: {metrics['pass_at_1']:.3f}")
    print(f"  Human Preference: {metrics['human_preference']:.3f}")
    print(f"  Harmonic Mean: {metrics['harmonic_mean']:.3f}")
    print(f"  Samples: {metrics['passed_samples']}/{metrics['total_samples']}")
