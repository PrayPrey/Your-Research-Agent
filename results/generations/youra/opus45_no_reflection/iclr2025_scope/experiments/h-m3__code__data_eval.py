"""H-M3 Evaluation Data Pipeline - LongBench QA loader with length bucketing"""
import torch
from typing import Dict, List
from datasets import load_dataset
from config import ExperimentConfig

def load_longbench_tasks(config: ExperimentConfig) -> Dict[str, List[dict]]:
    """Load LongBench QA tasks."""
    all_data = {}
    for task in config.longbench_tasks:
        try:
            ds = load_dataset("THUDM/LongBench", task, split="test")
            samples = []
            for item in ds:
                samples.append({
                    "task": task,
                    "context": item.get("context", item.get("input", "")),
                    "question": item.get("question", item.get("input", "")),
                    "answers": item.get("answers", [item.get("answer", "")]),
                    "prompt": _build_prompt(item),
                })
            all_data[task] = samples[:config.samples_per_task]
        except Exception as e:
            raise RuntimeError(
                f"LongBench task '{task}' unavailable: {e}. "
                "Ensure internet access and HuggingFace datasets works. "
                "Run: python -c \"from datasets import load_dataset; load_dataset('THUDM/LongBench', 'narrativeqa', split='test')\""
            )
    return all_data

def _build_prompt(item: dict) -> str:
    """Build QA prompt from LongBench item."""
    context = item.get("context", item.get("input", ""))
    question = item.get("question", "")
    if question:
        return f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    return f"{context}\n\nAnswer:"

def _synthetic_qa_samples(task: str, n: int) -> List[dict]:
    """Generate synthetic QA samples for offline testing."""
    samples = []
    for i in range(n):
        context = f"This is document {i} about {task}. " * 100
        samples.append({
            "task": task,
            "context": context,
            "question": f"What is this document about?",
            "answers": [f"Document {i} about {task}"],
            "prompt": f"Context: {context}\n\nQuestion: What is this document about?\n\nAnswer:",
        })
    return samples

def bucket_by_length(
    samples: List[dict],
    tokenizer,
    target_lengths: List[int],
) -> Dict[int, List[dict]]:
    """Bucket samples by target lengths using middle truncation."""
    buckets = {length: [] for length in target_lengths}

    for sample in samples:
        prompt = sample["prompt"]
        tokens = tokenizer(prompt, return_tensors="pt")["input_ids"][0]
        token_len = len(tokens)

        for target in sorted(target_lengths):
            if token_len <= target * 1.2:
                truncated = _middle_truncate(prompt, tokenizer, target)
                sample_copy = sample.copy()
                sample_copy["prompt"] = truncated
                sample_copy["original_length"] = token_len
                buckets[target].append(sample_copy)
                break
        else:
            truncated = _middle_truncate(prompt, tokenizer, max(target_lengths))
            sample_copy = sample.copy()
            sample_copy["prompt"] = truncated
            sample_copy["original_length"] = token_len
            buckets[max(target_lengths)].append(sample_copy)

    return buckets

def _middle_truncate(text: str, tokenizer, target_length: int) -> str:
    """Truncate from middle to preserve instruction + question ends."""
    tokens = tokenizer(text, return_tensors="pt")["input_ids"][0]
    if len(tokens) <= target_length:
        return text

    keep_start = target_length // 2
    keep_end = target_length - keep_start
    truncated_tokens = torch.cat([tokens[:keep_start], tokens[-keep_end:]])
    return tokenizer.decode(truncated_tokens, skip_special_tokens=True)
