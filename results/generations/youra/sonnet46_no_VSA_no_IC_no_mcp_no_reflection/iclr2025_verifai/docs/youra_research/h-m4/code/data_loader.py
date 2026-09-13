"""H-M4 data loader: HumanEval + MBPP → 538 unified problems."""
import json
import os
from pathlib import Path


def load_humaneval() -> list[dict]:
    from datasets import load_dataset
    ds = load_dataset("openai/openai_humaneval", split="test")
    problems = []
    for row in ds:
        problems.append({
            "task_id": row["task_id"],
            "prompt": row["prompt"],
            "tests": row["test"],
            "entry_point": row.get("entry_point", ""),
            "source": "humaneval",
        })
    return problems


def load_mbpp() -> list[dict]:
    from datasets import load_dataset
    ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="test")
    problems = []
    for row in ds:
        task_id = f"mbpp/{row['task_id']}"
        test_list = row.get("test_list", [])
        raw_setup = row.get("test_setup_code", row.get("test_imports", ""))
        if isinstance(raw_setup, list):
            test_setup = "\n".join(raw_setup)
        else:
            test_setup = raw_setup or ""
        tests_str = ""
        if test_setup:
            tests_str += str(test_setup) + "\n"
        tests_str += "\n".join(test_list)
        # 'prompt' field name in sanitized split
        prompt_text = row.get("prompt") or row.get("text", "")
        problems.append({
            "task_id": task_id,
            "prompt": prompt_text,
            "tests": tests_str,
            "source": "mbpp",
        })
    return problems


def load_combined() -> list[dict]:
    he = load_humaneval()
    mb = load_mbpp()
    combined = he + mb
    print(f"Loaded {len(he)} HumanEval + {len(mb)} MBPP = {len(combined)} problems")
    return combined


def load_baseline_pass(path: str | None = None) -> dict[str, bool]:
    if path and Path(path).exists():
        with open(path) as f:
            return json.load(f)
    # No cached baseline — return empty dict; runner will treat all as False baseline
    print("No baseline pass@1 cache found. Using empty baseline (all False).")
    return {}
