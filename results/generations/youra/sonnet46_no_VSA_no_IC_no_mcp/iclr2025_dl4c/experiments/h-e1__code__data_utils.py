"""data_utils.py — E-1: Data Pipeline for H-E1"""
import json
from datasets import load_dataset


def load_apps_train(tokenizer, max_length: int = 1024) -> dict:
    """Load APPS train split; return {'sft': Dataset, 'rlef': Dataset}."""
    ds = load_dataset("codeparrot/apps", split="train")

    # Filter: keep only problems with >= 1 test case
    def has_tests(ex):
        try:
            io = json.loads(ex["input_output"]) if ex["input_output"] else {}
            inputs = io.get("inputs", [])
            return len(inputs) > 0
        except Exception:
            return False

    ds = ds.filter(has_tests)

    sft_ds = ds.map(lambda ex: format_sft_sample(ex, tokenizer, max_length), remove_columns=ds.column_names)
    rlef_ds = ds.map(format_rlef_sample, remove_columns=ds.column_names)

    return {"sft": sft_ds, "rlef": rlef_ds}


def format_sft_sample(problem: dict, tokenizer, max_length: int = 1024) -> dict:
    """Format problem for SFT: (prompt, target) → tokenized."""
    prompt = f"# Problem\n{problem['question']}\n\n# Solution\n"
    try:
        solutions = json.loads(problem["solutions"]) if problem["solutions"] else []
        solution = solutions[0] if solutions else ""
    except Exception:
        solution = ""

    full_text = prompt + solution
    enc = tokenizer(full_text, max_length=max_length, truncation=True, padding=False)
    prompt_enc = tokenizer(prompt, max_length=max_length, truncation=True, padding=False)
    prompt_len = len(prompt_enc["input_ids"])

    labels = [-100] * prompt_len + enc["input_ids"][prompt_len:]
    return {
        "input_ids": enc["input_ids"],
        "attention_mask": enc["attention_mask"],
        "labels": labels,
    }


def format_rlef_sample(problem: dict) -> dict:
    """Format problem for RLEF: prompt + test_cases for reward function."""
    prompt = f"# Problem\n{problem['question']}\n\n# Solution\n"

    try:
        io = json.loads(problem["input_output"]) if problem["input_output"] else {}
        inputs = io.get("inputs", [])
        outputs = io.get("outputs", [])
        test_cases = list(zip(inputs, outputs))
    except Exception:
        test_cases = []

    difficulty = problem.get("difficulty", "interview")

    return {
        "prompt": prompt,
        "test_cases": json.dumps(test_cases),
        "difficulty": difficulty,
    }
