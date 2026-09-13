"""Data loading and preprocessing for LongBench."""

from datasets import load_dataset
from config import MAX_TOKENS


def load_task(task_name: str):
    """Load LongBench task dataset."""
    return load_dataset("THUDM/LongBench", task_name, split="test", trust_remote_code=True)


def truncate_sample(sample: dict, tokenizer, max_tokens: int = MAX_TOKENS) -> dict:
    """Middle-truncate context+input to max_tokens."""
    context = sample.get("context", "")
    inp = sample.get("input", "")
    text = context + "\n" + inp

    tokens = tokenizer.encode(text, add_special_tokens=False)
    if len(tokens) <= max_tokens:
        return sample

    half = max_tokens // 2
    tokens = tokens[:half] + tokens[-half:]
    sample["context"] = tokenizer.decode(tokens, skip_special_tokens=True)
    sample["input"] = ""
    return sample


def build_prompt(sample: dict, task_name: str) -> str:
    """Build prompt for generation."""
    context = sample.get("context", "")
    inp = sample.get("input", "")

    if task_name in ["trec", "lsht"]:
        return f"{context}\n\nQuestion: {inp}\nAnswer:"
    elif task_name in ["gov_report", "qmsum", "multi_news", "vcsum"]:
        return f"{context}\n\nSummary:"
    elif task_name in ["passage_retrieval_en", "passage_retrieval_zh"]:
        return f"{context}\n\nWhich passage answers the question? {inp}\nAnswer:"
    elif task_name == "passage_count":
        return f"{context}\n\n{inp}\nAnswer:"
    elif task_name in ["lcc", "repobench-p"]:
        return f"{context}\n\n{inp}"
    else:
        return f"{context}\n\nQuestion: {inp}\nAnswer:"
