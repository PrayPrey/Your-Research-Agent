"""Error classification using syntax/mypy checks."""
import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List


def classify_errors(generated_code: str) -> str:
    """Run mypy and classify error. Returns: 'syntax' | 'type' | 'semantic' | 'none'"""
    try:
        ast.parse(generated_code)
    except SyntaxError:
        return 'syntax'

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(generated_code)
        path = f.name

    try:
        result = subprocess.run(
            ['mypy', path, '--no-error-summary', '--no-color-output'],
            capture_output=True,
            text=True,
            timeout=5
        )
        Path(path).unlink(missing_ok=True)

        if 'error:' not in result.stdout:
            return 'none'

        if any(kw in result.stdout for kw in ['Incompatible', 'not defined', 'has no attribute']):
            return 'type'
        return 'semantic'
    except:
        Path(path).unlink(missing_ok=True)
        return 'none'


def compute_error_distribution(samples: List[str]) -> Dict[str, float]:
    """Classify N samples, return percentages."""
    counts = {'syntax': 0, 'type': 0, 'semantic': 0, 'none': 0}
    for code in samples:
        err_type = classify_errors(code)
        counts[err_type] += 1

    total = len(samples)
    return {
        'syntax_pct': 100 * counts['syntax'] / total,
        'type_pct': 100 * counts['type'] / total,
        'semantic_pct': 100 * counts['semantic'] / total
    }
