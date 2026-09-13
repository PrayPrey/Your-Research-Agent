import json
from datasets import load_dataset, Dataset
from config import GRPOConfig


def load_apps(min_test_cases: int = 5) -> Dataset:
    """Load APPS train split, filter to problems with >= min_test_cases."""
    ds = load_dataset("codeparrot/apps", split="train", trust_remote_code=True)

    def has_enough_tests(example):
        try:
            io = example.get("input_output", "") or ""
            data = json.loads(io)
            return len(data.get("inputs", [])) >= min_test_cases
        except Exception:
            return False

    return ds.filter(has_enough_tests, num_proc=8)


def format_prompt(problem_description: str, tokenizer, max_tokens: int = 1024) -> str:
    """Truncate description to max_tokens tokens, return formatted prompt string."""
    token_ids = tokenizer.encode(problem_description, add_special_tokens=False)
    if len(token_ids) > max_tokens:
        problem_description = tokenizer.decode(token_ids[:max_tokens], skip_special_tokens=True)
    return f"{problem_description}\n\nWrite a Python solution:"


def get_test_cases(example: dict) -> list:
    """Parse example['input_output'] JSON -> list of {'input': str, 'output': str}."""
    try:
        io = example.get("input_output", "") or ""
        data = json.loads(io)
        inputs = data.get("inputs", [])
        outputs = data.get("outputs", [])
        return [
            {"input": str(inp), "output": str(out)}
            for inp, out in zip(inputs, outputs)
        ]
    except Exception:
        return []


def build_dataset(cfg: GRPOConfig, tokenizer) -> Dataset:
    """Load, filter, format APPS. Returns dataset with 'prompt' and 'test_cases' columns."""
    raw = load_apps(cfg.min_test_cases)

    def process(example):
        prompt = format_prompt(
            example.get("question", example.get("problem_statement", "")),
            tokenizer,
            cfg.max_prompt_tokens,
        )
        test_cases = get_test_cases(example)
        # Serialize test_cases as JSON string for dataloader compatibility
        return {"prompt": prompt, "test_cases": json.dumps(test_cases)}

    processed = raw.map(process, num_proc=8, remove_columns=raw.column_names)
    # Remove entries with empty prompts or no test cases
    processed = processed.filter(
        lambda x: x["prompt"] and len(json.loads(x["test_cases"])) >= cfg.min_test_cases
    )
    return processed
