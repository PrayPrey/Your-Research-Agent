"""Sample collection with ground truth annotation for H-M3."""
import sys
import os
import random
from dataclasses import dataclass
from typing import List, Optional
import importlib.util

H_M1_CODE = os.path.join(os.path.dirname(__file__), '../../h-m1/code')
H_M2_CODE = os.path.join(os.path.dirname(__file__), '../../h-m2/code')
sys.path.insert(0, H_M1_CODE)
sys.path.insert(0, H_M2_CODE)

from sample_collector import classify_error, parse_traceback_line, execute_code_safely
from ground_truth import find_bug_line_ast

_spec = importlib.util.spec_from_file_location("h_m2_config", os.path.join(H_M2_CODE, "config.py"))
_h_m2_cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_h_m2_cfg)
U_LINE_ERRORS = _h_m2_cfg.U_LINE_ERRORS
U_IGNORE_ERRORS = _h_m2_cfg.U_IGNORE_ERRORS
SEED = _h_m2_cfg.SEED


@dataclass
class NoiseSample:
    code: str
    traceback: str
    error_type: str
    traceback_line: int
    ground_truth_line: int


def _get_error_type_specific(traceback_str: str) -> str:
    """Extract exception class name from traceback."""
    all_errors = U_LINE_ERRORS | U_IGNORE_ERRORS
    for err in all_errors:
        if err in traceback_str:
            return err
    return "UnknownError"


def collect_synthetic_samples(n_per_category: int = 500, seed: int = SEED) -> List[NoiseSample]:
    """Generate synthetic samples with known ground truth."""
    random.seed(seed)

    u_line_templates = [
        ("def foo():\n    x = 1\n    y = undefined_var\n    return x + y",
         'File "<string>", line 3\n    NameError: name \'undefined_var\' is not defined', 3, 3),
        ("def bar():\n    lst = [1,2,3]\n    return lst[10]\n",
         'File "<string>", line 3\n    IndexError: list index out of range', 3, 3),
        ("def baz():\n    d = {}\n    return d['missing']\n",
         'File "<string>", line 3\n    KeyError: \'missing\'', 3, 3),
        ("def qux():\n    x = 1\n    return x + 'string'\n",
         'File "<string>", line 3\n    TypeError: unsupported operand type(s)', 3, 3),
        ("def divide():\n    a = 5\n    return a / 0\n",
         'File "<string>", line 3\n    ZeroDivisionError: division by zero', 3, 3),
    ]

    u_ignore_templates = [
        ("def rec():\n    return rec()\nrec()",
         'File "<string>", line 2\n    RecursionError: maximum recursion depth exceeded', 2, 1),
        ("def check(x):\n    assert x > 100\ncheck(5)",
         'File "<string>", line 2\n    AssertionError', 2, 3),
        ("def process():\n    raise RuntimeError('fail')\nprocess()",
         'File "<string>", line 2\n    RuntimeError: fail', 2, 2),
        ("import time\ndef slow():\n    while True:\n        pass\nslow()",
         'TimeoutError: Execution exceeded time limit', 3, 3),
    ]

    samples = []

    for i in range(n_per_category):
        t = u_line_templates[i % len(u_line_templates)]
        code, tb, tb_line, gt_line = t
        code_var = code + f"\n# u_line sample {i}"
        samples.append(NoiseSample(
            code=code_var,
            traceback=tb,
            error_type="U_line",
            traceback_line=tb_line,
            ground_truth_line=gt_line
        ))

    for i in range(n_per_category):
        t = u_ignore_templates[i % len(u_ignore_templates)]
        code, tb, tb_line, gt_line = t
        code_var = code + f"\n# u_ignore sample {i}"
        samples.append(NoiseSample(
            code=code_var,
            traceback=tb,
            error_type="U_ignore",
            traceback_line=tb_line,
            ground_truth_line=gt_line
        ))

    random.shuffle(samples)
    return samples


def collect_stratified_samples(
    model,
    tokenizer,
    dataset,
    n_per_category: int = 500,
    seed: int = SEED,
) -> List[NoiseSample]:
    """Collect real samples from APPS with ground truth annotation."""
    import json
    import torch
    from tqdm import tqdm

    random.seed(seed)
    torch.manual_seed(seed)

    buckets = {"U_line": [], "U_ignore": []}
    indices = list(range(len(dataset)))
    random.shuffle(indices)

    pbar = tqdm(total=n_per_category * 2, desc="Collecting stratified samples")

    for idx in indices:
        if len(buckets["U_line"]) >= n_per_category and len(buckets["U_ignore"]) >= n_per_category:
            break

        item = dataset[idx]
        prompt = item.get("question", item.get("problem", ""))
        if not prompt:
            continue

        inputs = tokenizer(prompt, max_length=512, truncation=True, return_tensors="pt")

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
        if result not in ["ERROR", "FAIL"] or not traceback:
            continue

        error_type_specific = _get_error_type_specific(traceback)
        category = "U_line" if error_type_specific in U_LINE_ERRORS else "U_ignore"

        if len(buckets[category]) >= n_per_category:
            continue

        tb_line = parse_traceback_line(traceback)
        gt_line = find_bug_line_ast(code, error_type_specific, traceback)

        if tb_line is None or gt_line is None:
            continue

        buckets[category].append(NoiseSample(
            code=code,
            traceback=traceback,
            error_type=category,
            traceback_line=tb_line,
            ground_truth_line=gt_line
        ))
        pbar.update(1)

    pbar.close()
    print(f"Collected U_line={len(buckets['U_line'])}, U_ignore={len(buckets['U_ignore'])}")

    return buckets["U_line"] + buckets["U_ignore"]
