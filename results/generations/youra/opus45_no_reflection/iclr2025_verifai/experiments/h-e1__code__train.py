"""H-E1 Data Pipeline: Load datasets, generate buggy code, capture failures"""

import os
import sys
import json
import random
import subprocess
import tempfile
import traceback
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter

from config import CONFIG
from model import generate_signal_variants

def load_datasets() -> List[Dict]:
    """Load HumanEval + MBPP datasets."""
    from datasets import load_dataset

    problems = []

    # HumanEval
    humaneval = load_dataset("openai/openai_humaneval", split="test", trust_remote_code=True)
    for item in humaneval:
        problems.append({
            "id": f"HE_{item['task_id']}",
            "prompt": item["prompt"],
            "test": item["test"],
            "entry_point": item["entry_point"],
            "canonical_solution": item.get("canonical_solution", ""),
            "source": "humaneval"
        })

    # MBPP
    mbpp = load_dataset("mbpp", split="test", trust_remote_code=True)
    for item in mbpp:
        test_code = "\n".join(item["test_list"]) if item.get("test_list") else ""
        problems.append({
            "id": f"MBPP_{item['task_id']}",
            "prompt": item["text"],
            "test": test_code,
            "entry_point": extract_function_name(item.get("code", "")),
            "canonical_solution": item.get("code", ""),
            "source": "mbpp"
        })

    print(f"Loaded {len(problems)} problems (HumanEval: {sum(1 for p in problems if p['source']=='humaneval')}, MBPP: {sum(1 for p in problems if p['source']=='mbpp')})")
    return problems

def extract_function_name(code: str) -> str:
    """Extract first function name from code."""
    match = re.search(r'def\s+(\w+)\s*\(', code)
    return match.group(1) if match else "solution"

def generate_buggy_code(problem: Dict, introduce_bug: bool = True) -> str:
    """Generate buggy code by mutating canonical solution."""
    solution = problem.get("canonical_solution", "")
    if not solution:
        # Fallback: create minimal buggy stub
        entry = problem.get("entry_point", "solution")
        return f"def {entry}(*args, **kwargs):\n    raise NotImplementedError('No solution provided')"

    if not introduce_bug:
        return solution

    # Simple bug injection strategies
    mutations = [
        (r'\breturn\s+(\w+)', r'return \1 + 1'),  # Off-by-one
        (r'==', '!='),  # Flip comparison
        (r'>=', '<'),   # Wrong comparison
        (r'<=', '>'),
        (r'\band\b', 'or'),  # Logic flip
        (r'\bTrue\b', 'False'),
        (r'\[\s*0\s*\]', '[1]'),  # Wrong index
        (r'\[\s*-1\s*\]', '[0]'),
    ]

    buggy = solution
    applied = False
    random.shuffle(mutations)

    for pattern, replacement in mutations:
        if re.search(pattern, buggy):
            buggy = re.sub(pattern, replacement, buggy, count=1)
            applied = True
            break

    if not applied:
        # Fallback: add assertion error
        lines = buggy.strip().split('\n')
        if len(lines) > 1:
            indent = len(lines[1]) - len(lines[1].lstrip())
            buggy = lines[0] + '\n' + ' ' * indent + 'assert False, "Injected bug"\n' + '\n'.join(lines[1:])

    return buggy

def run_pytest_capture(problem: Dict, code: str) -> Tuple[str, str]:
    """Run code with test, capture error and trace output."""
    entry_point = problem.get("entry_point", "solution")
    test_code = problem.get("test", "")

    # Build full test file
    full_code = f'''{code}

# Test code
{test_code}

# Run entry point check
if __name__ == "__main__":
    try:
        {entry_point}
    except Exception as e:
        pass
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(full_code)
        temp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        error_output = result.stderr
        trace_output = result.stderr  # Combined for simplicity

        # If no error, try running pytest-style assertions
        if not error_output and result.returncode == 0:
            # Code passed, no failure to capture
            return "", ""

        return error_output, trace_output

    except subprocess.TimeoutExpired:
        return "TimeoutError: Code execution exceeded 10 seconds", ""
    except Exception as e:
        return str(e), traceback.format_exc()
    finally:
        os.unlink(temp_path)

def classify_error_type(error_output: str) -> str:
    """Classify error into category."""
    if not error_output:
        return "no_error"

    error_lower = error_output.lower()
    if 'syntaxerror' in error_lower:
        return 'syntax'
    elif 'nameerror' in error_lower:
        return 'name'
    elif 'typeerror' in error_lower:
        return 'type'
    elif 'assertionerror' in error_lower:
        return 'assertion'
    elif 'indexerror' in error_lower:
        return 'index'
    elif 'keyerror' in error_lower:
        return 'key'
    elif 'valueerror' in error_lower:
        return 'value'
    elif 'attributeerror' in error_lower:
        return 'attribute'
    elif 'timeouterror' in error_lower:
        return 'timeout'
    else:
        return 'other'

def sample_failures(failures: List[Dict], n: int = 100, seed: int = 42) -> List[Dict]:
    """Stratified sample by error type."""
    random.seed(seed)

    # Group by error type
    by_type = {}
    for f in failures:
        et = f.get("error_type", "other")
        by_type.setdefault(et, []).append(f)

    print(f"Error type distribution: {Counter(f['error_type'] for f in failures)}")

    # Stratified sample
    total = len(failures)
    sampled = []

    for et, items in by_type.items():
        # Proportional allocation
        proportion = len(items) / total
        count = max(1, int(n * proportion))
        sampled.extend(random.sample(items, min(count, len(items))))

    # Fill remaining slots if needed
    while len(sampled) < n and len(sampled) < len(failures):
        remaining = [f for f in failures if f not in sampled]
        if remaining:
            sampled.append(random.choice(remaining))
        else:
            break

    # Trim if over
    if len(sampled) > n:
        sampled = random.sample(sampled, n)

    return sampled

def build_signal_dataset(problems: List[Dict], sample_size: int = 100) -> List[Dict]:
    """Build dataset of failures with 6 signal variants each."""
    print(f"Generating buggy code and capturing failures...")

    failures = []

    for i, problem in enumerate(problems):
        if i % 50 == 0:
            print(f"Processing problem {i+1}/{len(problems)}...")

        # Generate buggy code
        buggy_code = generate_buggy_code(problem, introduce_bug=True)

        # Capture error
        error_output, trace_output = run_pytest_capture(problem, buggy_code)

        if error_output:
            failures.append({
                "id": problem["id"],
                "source": problem["source"],
                "error_output": error_output,
                "trace_output": trace_output,
                "error_type": classify_error_type(error_output),
                "buggy_code": buggy_code
            })

    print(f"Collected {len(failures)} failures from {len(problems)} problems")

    # Sample
    sampled = sample_failures(failures, n=sample_size, seed=CONFIG["random_seed"])
    print(f"Sampled {len(sampled)} failures")

    # Generate signal variants
    signal_dataset = []
    for failure in sampled:
        variants = generate_signal_variants(failure["error_output"], failure["trace_output"])
        for condition, signal_text in variants.items():
            signal_dataset.append({
                "problem_id": failure["id"],
                "source": failure["source"],
                "error_type": failure["error_type"],
                "condition": condition,
                "signal_text": signal_text
            })

    print(f"Generated {len(signal_dataset)} signal instances ({len(sampled)} failures x 6 conditions)")
    return signal_dataset

def main():
    """Main data pipeline."""
    output_dir = Path(__file__).parent / CONFIG["output_dir"]
    output_dir.mkdir(exist_ok=True)

    # Load datasets
    problems = load_datasets()

    # Build signal dataset
    signal_dataset = build_signal_dataset(problems, sample_size=CONFIG["sample_size"])

    # Save
    output_path = output_dir / "signal_dataset.json"
    with open(output_path, 'w') as f:
        json.dump(signal_dataset, f, indent=2)

    print(f"Signal dataset saved to {output_path}")
    print(f"Total signals: {len(signal_dataset)}")

    return signal_dataset

if __name__ == "__main__":
    main()
