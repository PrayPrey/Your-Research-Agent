"""Data loading and preprocessing for APPS + CodeContests datasets."""

import datasets as hf_datasets
from transformers import PreTrainedTokenizer


# APPS uses string difficulty labels
APPS_EASY_LABELS = {"introductory", "interview"}
APPS_HARD_LABELS = {"competition"}

# CodeContests difficulty: 0=UNKNOWN, 1-7=easy-ish, 8+=hard
# source: 1=CODECHEF, 2=CODEFORCES, 3=HACKEREARTH, 5=ATCODER, 6=AIZU
CC_EASY_MAX_DIFFICULTY = 7
CC_HARD_MIN_DIFFICULTY = 8


def load_apps(split: str = "train") -> hf_datasets.Dataset:
    """Load APPS from codeparrot/apps (cached locally)."""
    return hf_datasets.load_dataset("codeparrot/apps", split=split)


def load_code_contests(split: str = "train") -> hf_datasets.Dataset:
    """Load CodeContests from deepmind/code_contests (cached locally)."""
    return hf_datasets.load_dataset("deepmind/code_contests", split=split)


def filter_apps_easy(ds: hf_datasets.Dataset) -> hf_datasets.Dataset:
    """Keep APPS problems with introductory or interview difficulty."""
    return ds.filter(lambda x: x["difficulty"] in APPS_EASY_LABELS)


def filter_apps_hard(ds: hf_datasets.Dataset) -> hf_datasets.Dataset:
    """Keep APPS problems with competition difficulty."""
    return ds.filter(lambda x: x["difficulty"] in APPS_HARD_LABELS)


def filter_cc_easy(ds: hf_datasets.Dataset) -> hf_datasets.Dataset:
    """Keep CodeContests problems with difficulty <= 7 (easier problems)."""
    return ds.filter(lambda x: 1 <= x["difficulty"] <= CC_EASY_MAX_DIFFICULTY)


def filter_cc_hard(ds: hf_datasets.Dataset) -> hf_datasets.Dataset:
    """Keep CodeContests problems with difficulty >= 8 (harder problems)."""
    return ds.filter(lambda x: x["difficulty"] >= CC_HARD_MIN_DIFFICULTY)


def filter_has_tests(ds: hf_datasets.Dataset) -> hf_datasets.Dataset:
    """Remove problems with no unit test cases."""
    def has_tests(example):
        # APPS: input_output field contains test cases
        if "input_output" in example:
            io = example["input_output"]
            if io and isinstance(io, str) and len(io) > 10:
                return True
        # CodeContests: public_tests or private_tests
        if "public_tests" in example:
            pt = example["public_tests"]
            if pt and isinstance(pt, dict):
                inputs = pt.get("input", [])
                if isinstance(inputs, list) and len(inputs) > 0:
                    return True
        return False
    return ds.filter(has_tests)


def _build_apps_prompt(example: dict) -> str:
    """Build prompt string from APPS example."""
    question = example.get("question", "")
    starter = example.get("starter_code", "")
    if starter:
        return f"{question}\n\n{starter}"
    return question


def _build_cc_prompt(example: dict) -> str:
    """Build prompt string from CodeContests example."""
    return example.get("description", "")


def _safe_str(val, max_len: int = 2000) -> str:
    """Convert value to string safely, truncating if too long."""
    if isinstance(val, str):
        return val[:max_len]
    if isinstance(val, (int, float)):
        # Avoid Python 3.10 integer string conversion limit for huge numbers
        try:
            s = repr(val)
            return s[:max_len]
        except Exception:
            return ""
    try:
        return str(val)[:max_len]
    except Exception:
        return ""


def _serialize_test_cases(example: dict) -> str:
    """Serialize test cases to a JSON string for uniform schema across datasets."""
    import json
    test_cases = []

    # APPS format: input_output is JSON string
    io_str = example.get("input_output", "")
    if io_str and isinstance(io_str, str) and len(io_str) > 2:
        try:
            io_data = json.loads(io_str)
            inputs = io_data.get("inputs", [])
            outputs = io_data.get("outputs", [])
            for inp, out in zip(inputs[:3], outputs[:3]):
                test_cases.append({"input": _safe_str(inp), "output": _safe_str(out)})
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    # CodeContests format: public_tests dict
    if not test_cases:
        pt = example.get("public_tests", {})
        if isinstance(pt, dict):
            inputs = pt.get("input", [])
            outputs = pt.get("output", [])
            for inp, out in zip(inputs[:3], outputs[:3]):
                test_cases.append({"input": _safe_str(inp), "output": _safe_str(out)})

    return json.dumps(test_cases)


def tokenize_prompt(
    example: dict,
    tokenizer: PreTrainedTokenizer,
    max_length: int = 512,
) -> dict:
    """Tokenize problem description. Returns normalized dict with uniform schema."""
    # Determine prompt text based on dataset source
    if "question" in example:
        text = _build_apps_prompt(example)
    else:
        text = _build_cc_prompt(example)

    encoding = tokenizer(
        text,
        max_length=max_length,
        truncation=True,
        padding="max_length",
        return_tensors=None,
    )
    # Return ONLY uniform fields — no dataset-specific nested structs
    # test_cases_json is a JSON string for reward function use
    return {
        "input_ids": encoding["input_ids"],
        "attention_mask": encoding["attention_mask"],
        "prompt": text,
        "test_cases_json": _serialize_test_cases(example),
    }


UNIFORM_COLUMNS = ["input_ids", "attention_mask", "prompt", "test_cases_json"]


def _tokenize_and_normalize(ds: hf_datasets.Dataset, tokenizer: PreTrainedTokenizer) -> hf_datasets.Dataset:
    """Map tokenize_prompt over dataset and keep ONLY uniform columns."""
    ds = ds.map(lambda ex: tokenize_prompt(ex, tokenizer), batched=False)
    # Drop all original columns, keep only the 4 uniform output fields
    cols_to_remove = [c for c in ds.column_names if c not in UNIFORM_COLUMNS]
    if cols_to_remove:
        ds = ds.remove_columns(cols_to_remove)
    return ds


def _load_and_filter_apps(tokenizer: PreTrainedTokenizer, easy: bool) -> hf_datasets.Dataset:
    """Helper: load APPS, filter by difficulty, filter has_tests, tokenize."""
    ds = load_apps()
    if easy:
        ds = filter_apps_easy(ds)
    else:
        ds = filter_apps_hard(ds)
    ds = filter_has_tests(ds)
    return _tokenize_and_normalize(ds, tokenizer)


def _load_and_filter_cc(tokenizer: PreTrainedTokenizer, easy: bool) -> hf_datasets.Dataset:
    """Helper: load CodeContests, filter by difficulty, filter has_tests, tokenize."""
    ds = load_code_contests()
    if easy:
        ds = filter_cc_easy(ds)
    else:
        ds = filter_cc_hard(ds)
    ds = filter_has_tests(ds)
    return _tokenize_and_normalize(ds, tokenizer)


def build_easy_pool(tokenizer: PreTrainedTokenizer) -> hf_datasets.Dataset:
    """APPS introductory+interview + CC difficulty<=7, filtered and tokenized."""
    apps_easy = _load_and_filter_apps(tokenizer, easy=True)
    cc_easy = _load_and_filter_cc(tokenizer, easy=True)
    return hf_datasets.concatenate_datasets([apps_easy, cc_easy])


def build_hard_pool(tokenizer: PreTrainedTokenizer) -> hf_datasets.Dataset:
    """APPS competition + CC difficulty>=8, filtered and tokenized."""
    apps_hard = _load_and_filter_apps(tokenizer, easy=False)
    cc_hard = _load_and_filter_cc(tokenizer, easy=False)
    return hf_datasets.concatenate_datasets([apps_hard, cc_hard])


def build_full_pool(tokenizer: PreTrainedTokenizer) -> hf_datasets.Dataset:
    """All APPS + CC problems (has_tests filtered), tokenized (uniform baseline)."""
    apps = load_apps()
    apps = filter_has_tests(apps)
    apps = _tokenize_and_normalize(apps, tokenizer)

    cc = load_code_contests()
    cc = filter_has_tests(cc)
    cc = _tokenize_and_normalize(cc, tokenizer)

    return hf_datasets.concatenate_datasets([apps, cc])
