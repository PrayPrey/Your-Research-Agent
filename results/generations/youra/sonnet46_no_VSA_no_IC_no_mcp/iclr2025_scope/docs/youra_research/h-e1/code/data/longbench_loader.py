import ast
import json
import random
import torch
from pathlib import Path


LLAMA2_CHAT_TEMPLATE = (
    "[INST] <<SYS>>\nYou are a helpful assistant. Answer the question based on the given context.\n<</SYS>>\n\n"
    "Context:\n{context}\n\nQuestion: {question} [/INST]"
)

# Known JSONL paths in HF cache for LongBench tasks
_LONGBENCH_JSONL_ROOTS = [
    Path("/home/PrayPrey/.cache/huggingface/datasets/downloads/extracted/3b20a458b136aef6a5236d876080249e2cd5415f09fba81b02cd847c4ad31247/data"),
    Path("/home/PrayPrey/.cache/huggingface/datasets/downloads/extracted/bd9c4e6dc4f4a8394489444a0f9b0ee37c1f28f7664b0f20a09d2eceb554b56f/data"),
]


def _parse_answers(answers_raw):
    if isinstance(answers_raw, list):
        return answers_raw
    if isinstance(answers_raw, str):
        try:
            val = ast.literal_eval(answers_raw)
            if isinstance(val, list):
                return val
            return [str(val)]
        except Exception:
            return [answers_raw]
    return [str(answers_raw)]


def _load_from_jsonl(task_name: str, n: int, seed: int) -> list:
    """Fall back to locally cached JSONL files."""
    for root in _LONGBENCH_JSONL_ROOTS:
        fpath = root / f"{task_name}.jsonl"
        if fpath.exists():
            with open(fpath) as f:
                data = [json.loads(l) for l in f if l.strip()]
            rng = random.Random(seed)
            rng.shuffle(data)
            return data[:n]
    raise FileNotFoundError(f"No JSONL found for task '{task_name}' in known cache paths")


def _format_prompt(context: str, question: str) -> str:
    return LLAMA2_CHAT_TEMPLATE.format(context=context, question=question)


def load_task(
    task_name: str,
    tokenizer,
    n: int = 100,
    seed: int = 42,
    max_tokens: int = 4096,
) -> list:
    # Try HuggingFace datasets first, fall back to JSONL cache
    try:
        from datasets import load_dataset
        ds = load_dataset("THUDM/LongBench", task_name, split="test")
        ds = ds.shuffle(seed=seed)
        ds = ds.select(range(min(n, len(ds))))
        raw = [{"context": ex.get("context", ""), "input": ex.get("input", ""), "answers": ex.get("answers", [])}
               for ex in ds]
    except Exception:
        raw_data = _load_from_jsonl(task_name, n, seed)
        raw = [{"context": ex.get("context", ""), "input": ex.get("input", ""), "answers": ex.get("answers", [])}
               for ex in raw_data]

    examples = []
    for ex in raw:
        prompt = _format_prompt(ex["context"], ex["input"])
        ids = tokenizer.encode(prompt, add_special_tokens=True)
        # Left-truncate to max_tokens
        if len(ids) > max_tokens:
            ids = ids[-max_tokens:]
        input_ids = torch.tensor([ids], dtype=torch.long)

        answers = _parse_answers(ex["answers"])
        examples.append({
            "input_ids": input_ids,
            "answers": answers,
            "task": task_name,
        })
    return examples
