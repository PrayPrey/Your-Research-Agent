# data.py - h-m3: TruthfulQA MC1 loading for RCI flip detection
from datasets import load_dataset
from config import CONFIG


def load_truthfulqa_mc1():
    """Load TruthfulQA MC1 dataset. Returns list of question dicts."""
    ds = load_dataset(CONFIG["dataset"], CONFIG["dataset_config"], split="validation")
    samples = []
    for row in ds:
        mc1 = row["mc1_targets"]
        correct_idx = mc1["labels"].index(1)
        samples.append({
            "question": row["question"],
            "choices": mc1["choices"],
            "correct_answer": mc1["choices"][correct_idx],
            "correct_idx": correct_idx,
        })
    return samples


def build_prompts(samples):
    """Build prompts for greedy decoding to determine hallucination labels."""
    prompts = []
    for s in samples:
        prompt = f"Question: {s['question']}\nAnswer:"
        prompts.append({
            "prompt": prompt,
            "question": s["question"],
            "correct_answer": s["correct_answer"],
            "choices": s["choices"],
        })
    return prompts
