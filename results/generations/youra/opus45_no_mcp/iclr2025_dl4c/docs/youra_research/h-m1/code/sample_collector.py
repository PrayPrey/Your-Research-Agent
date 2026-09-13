"""Generate failing samples with tracebacks for H-M1 analysis."""
import sys
import json
import random
import torch
from typing import List, Dict, Optional
from tqdm import tqdm

sys.path.insert(0, '../h-e1/code')
from config import U_LINE_ERRORS


def classify_error(traceback_str: str) -> str:
    """Classify error as U_line or U_ignore."""
    if not traceback_str:
        return "pass"
    for err in U_LINE_ERRORS:
        if err in traceback_str:
            return "U_line"
    return "U_ignore"


def parse_traceback_line(traceback_str: str) -> Optional[int]:
    """Extract failing source line number from traceback."""
    import re
    if not traceback_str:
        return None
    matches = re.findall(r'File ".*?", line (\d+)', traceback_str)
    if matches:
        return int(matches[-1])
    return None


def execute_code_safely(code: str, test_input: str = "", timeout_s: int = 5):
    """Execute code and return (result, traceback)."""
    import subprocess

    try:
        result = subprocess.run(
            ["python", "-c", code],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        if result.returncode != 0:
            return "ERROR", result.stderr
        return "PASS", None
    except subprocess.TimeoutExpired:
        return "ERROR", "TimeoutError: Execution exceeded time limit"
    except Exception as e:
        return "ERROR", str(e)


def generate_failing_samples(
    model,
    tokenizer,
    dataset,
    n_samples: int = 500,
    max_attempts: int = 2000,
    seed: int = 42,
) -> List[Dict]:
    """Generate code samples that fail with parseable tracebacks."""
    random.seed(seed)
    torch.manual_seed(seed)

    samples = []
    attempts = 0
    dataset_indices = list(range(len(dataset)))
    random.shuffle(dataset_indices)

    pbar = tqdm(total=n_samples, desc="Collecting failing samples")

    for idx in dataset_indices:
        if len(samples) >= n_samples or attempts >= max_attempts:
            break

        attempts += 1
        item = dataset[idx]
        prompt = item.get("question", item.get("problem", ""))
        if not prompt:
            continue

        inputs = tokenizer(
            prompt,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=256,
                do_sample=True,
                temperature=0.8,
                pad_token_id=tokenizer.pad_token_id,
            )

        code = tokenizer.decode(outputs[0], skip_special_tokens=True)

        if not code.strip() or len(code.split('\n')) < 3:
            continue

        test_io = item.get("input_output", "{}")
        if isinstance(test_io, str):
            try:
                test_io = json.loads(test_io)
            except:
                test_io = {}

        test_input = ""
        if isinstance(test_io, dict) and "inputs" in test_io:
            inputs_list = test_io["inputs"]
            if inputs_list:
                test_input = inputs_list[0] if isinstance(inputs_list[0], str) else ""

        result, traceback = execute_code_safely(code, test_input)

        if result in ["ERROR", "FAIL"] and traceback:
            error_line = parse_traceback_line(traceback)
            if error_line is not None:
                error_type = classify_error(traceback)
                samples.append({
                    "code": code,
                    "traceback": traceback,
                    "error_type": error_type,
                    "error_line": error_line,
                    "problem_id": idx,
                })
                pbar.update(1)

    pbar.close()
    print(f"Collected {len(samples)} failing samples from {attempts} attempts")

    u_line_count = sum(1 for s in samples if s["error_type"] == "U_line")
    u_ignore_count = sum(1 for s in samples if s["error_type"] == "U_ignore")
    print(f"Distribution: U_line={u_line_count}, U_ignore={u_ignore_count}")

    return samples


def generate_synthetic_samples(
    n_samples: int = 500,
    seed: int = 42,
) -> List[Dict]:
    """Generate synthetic failing samples for testing without model."""
    random.seed(seed)

    templates = [
        ("def foo():\n    x = 1\n    y = undefined_var\n    return x + y",
         'File "<string>", line 3\n    NameError: name \'undefined_var\' is not defined',
         "U_line", 3),
        ("def bar():\n    lst = [1,2,3]\n    return lst[10]\n",
         'File "<string>", line 3\n    IndexError: list index out of range',
         "U_line", 3),
        ("def baz():\n    d = {}\n    return d['missing']\n",
         'File "<string>", line 3\n    KeyError: \'missing\'',
         "U_line", 3),
        ("def qux():\n    x = 1\n    return x + 'string'\n",
         'File "<string>", line 3\n    TypeError: unsupported operand type(s)',
         "U_line", 3),
        ("def rec():\n    return rec()\n",
         'File "<string>", line 2\n    RecursionError: maximum recursion depth exceeded',
         "U_ignore", 2),
        ("import time\ndef slow():\n    time.sleep(100)\n",
         'TimeoutError: Execution exceeded time limit',
         "U_ignore", 3),
    ]

    samples = []
    for i in range(n_samples):
        template = random.choice(templates)
        code, traceback, error_type, error_line = template
        code_with_variation = code + f"\n# sample {i}"
        samples.append({
            "code": code_with_variation,
            "traceback": traceback,
            "error_type": error_type,
            "error_line": error_line,
            "problem_id": i,
        })

    return samples
