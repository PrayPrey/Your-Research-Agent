"""QA evaluation (F1 scoring)."""
import re
import string
from collections import Counter
import torch
from datasets import Dataset
from transformers import PreTrainedTokenizer


def normalize_answer(s: str) -> str:
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = " ".join(s.split())
    return s


def compute_f1(pred: str, gold: str) -> float:
    pred_tokens = normalize_answer(pred).split()
    gold_tokens = normalize_answer(gold).split()
    if not gold_tokens:
        return 1.0 if not pred_tokens else 0.0
    if not pred_tokens:
        return 0.0
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_common = sum(common.values())
    if num_common == 0:
        return 0.0
    precision = num_common / len(pred_tokens)
    recall = num_common / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def evaluate_qa(model, tokenizer: PreTrainedTokenizer, val_data: Dataset, batch_size: int = 8) -> float:
    """Compute average F1 on validation set using generative QA approach."""
    model.eval()
    device = next(model.parameters()).device

    f1_scores = []
    for i in range(0, len(val_data), batch_size):
        batch = val_data.select(range(i, min(i + batch_size, len(val_data))))

        for j, example in enumerate(batch):
            question = example["question"]
            context = example["context"]
            answers = example["answers"]["text"]

            prompt = f"Context: {context[:1000]}\nQuestion: {question}\nAnswer:"
            inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id,
                )

            pred = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            pred = pred.split("\n")[0].strip()

            if not answers:
                f1 = 1.0 if not pred else 0.0
            else:
                f1 = max(compute_f1(pred, ans) for ans in answers)
            f1_scores.append(f1)

    return sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
