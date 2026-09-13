"""Feedback collection: execution, AI, and human simulation."""
from typing import List
import subprocess
import tempfile
import os
import numpy as np

def execute_code(code: str, tests: List[str], timeout: int = 5) -> int:
    """Execute code against tests. Returns 1 if pass, 0 if fail."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code + "\n\n")
            for test in tests:
                f.write(test + "\n")
            temp_path = f.name

        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            timeout=timeout,
            text=True
        )

        os.unlink(temp_path)

        if result.returncode == 0:
            return 1
        else:
            return 0

    except subprocess.TimeoutExpired:
        if 'temp_path' in locals():
            os.unlink(temp_path)
        return 0
    except Exception:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        return 0

def ai_score(prompt: str, code: str) -> float:
    """Score code using heuristic (length-based placeholder for PoC)."""
    # PoC: simple heuristic instead of actual API call
    # Real implementation would use OpenAI API
    if len(code.strip()) == 0:
        return 0.0
    elif len(code.strip()) < 50:
        return 0.3
    elif len(code.strip()) < 150:
        return 0.6
    else:
        return 0.8

def simulate_human_ratings(
    code: str,
    execution_result: int,
    num_raters: int = 3,
    noise_level: float = 0.2,
    seed: int = None
) -> List[float]:
    """Simulate human ratings with noise."""
    if seed is not None:
        np.random.seed(seed)

    base_score = float(execution_result)
    ratings = []

    for _ in range(num_raters):
        noise = np.random.uniform(-noise_level, noise_level)
        rating = base_score + noise
        rating = np.clip(rating, 0.0, 1.0)
        ratings.append(rating)

    return ratings

def collect_execution_feedback(problems, generated_codes: List[str]) -> List[int]:
    """Collect execution feedback for all samples."""
    results = []
    for problem, code in zip(problems, generated_codes):
        result = execute_code(code, problem.tests)
        results.append(result)
    return results

def collect_ai_feedback(problems, generated_codes: List[str]) -> List[float]:
    """Collect AI scores for all samples."""
    scores = []
    for problem, code in zip(problems, generated_codes):
        score = ai_score(problem.prompt, code)
        scores.append(score)
    return scores

def collect_human_feedback(
    problems,
    generated_codes: List[str],
    execution_results: List[int],
    seed: int = 42
) -> List[float]:
    """Collect simulated human ratings (mean across raters)."""
    ratings = []
    for code, exec_result in zip(generated_codes, execution_results):
        rater_scores = simulate_human_ratings(code, exec_result, seed=seed)
        ratings.append(np.mean(rater_scores))
    return ratings

def compute_inter_rater_reliability(all_ratings: np.ndarray) -> float:
    """Compute Cohen's kappa (simplified for PoC)."""
    # PoC: return fixed value for demo
    # Real implementation would compute kappa across all samples
    return 0.7
