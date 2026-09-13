"""Evaluation: test execution and pass@1 computation."""

import subprocess
import tempfile
import os
from typing import List, Dict
import matplotlib.pyplot as plt
import config


def extract_code_block(text: str) -> str:
    """Extract code from markdown code blocks or raw text."""
    if "```python" in text:
        parts = text.split("```python")
        if len(parts) > 1:
            code = parts[1].split("```")[0]
            return code.strip()
    if "```" in text:
        parts = text.split("```")
        if len(parts) > 1:
            return parts[1].strip()
    return text.strip()


def run_tests(code: str, test: str, entry_point: str, timeout: int = config.TIMEOUT_SEC) -> bool:
    """Execute code with test cases. Returns True if all tests pass."""
    code = extract_code_block(code)

    full_code = f"{code}\n\n{test}"

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(full_code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
    finally:
        os.unlink(temp_path)


def compute_pass_at_1(results: List[Dict]) -> float:
    """Compute pass@1 from results list."""
    if not results:
        return 0.0
    passed = sum(1 for r in results if r.get("passed", False))
    return passed / len(results)


def plot_comparison(pass_rates: Dict[str, float], out_path: str) -> None:
    """Bar chart comparing pass@1 across conditions."""
    plt.figure(figsize=(8, 6))
    conditions = list(pass_rates.keys())
    values = [pass_rates[c] for c in conditions]
    colors = ['#4CAF50' if 'ai' in c.lower() else '#2196F3' if 'zero' in c.lower() else '#FF9800'
              for c in conditions]

    plt.bar(conditions, values, color=colors)
    plt.ylabel('pass@1')
    plt.title('pass@1 Comparison: AI Critic vs Random Baseline')
    plt.ylim(0, 1)

    for i, v in enumerate(values):
        plt.text(i, v + 0.02, f'{v:.3f}', ha='center')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_iteration_curve(curves: Dict[str, List[float]], out_path: str) -> None:
    """Plot pass@1 improvement across refinement iterations."""
    plt.figure(figsize=(8, 6))

    for label, values in curves.items():
        x = list(range(len(values)))
        plt.plot(x, values, marker='o', label=label)

    plt.xlabel('Iteration (k)')
    plt.ylabel('pass@1')
    plt.title('pass@1 vs Refinement Iterations')
    plt.legend()
    plt.ylim(0, 1)
    plt.xticks(range(config.K_ITERS + 1))
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
