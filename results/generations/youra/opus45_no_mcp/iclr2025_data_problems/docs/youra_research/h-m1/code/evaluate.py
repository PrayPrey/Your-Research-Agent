import torch
import numpy as np
from datasets import Dataset
from data import format_mmlu_prompt
from tqdm import tqdm


def evaluate_full_test_set(model, tokenizer, test_set: Dataset, answer_token_ids: list, batch_size: int = 16) -> list:
    model.eval()
    results = []

    for idx in tqdm(range(len(test_set)), desc="Evaluating"):
        item = test_set[idx]
        prompt = format_mmlu_prompt(item)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0, -1, :]

        answer_logits = logits[answer_token_ids]
        pred_idx = answer_logits.argmax().item()
        correct = pred_idx == item["answer"]

        results.append({
            "id": idx,
            "correct": correct,
            "pred": chr(ord('A') + pred_idx),
            "answer": chr(ord('A') + item["answer"]),
        })

    return results


def compute_item_accuracy(eval_results: list, contaminated_ids: set) -> dict:
    contaminated_correct = []
    clean_correct = []

    for r in eval_results:
        if r["id"] in contaminated_ids:
            contaminated_correct.append(r["correct"])
        else:
            clean_correct.append(r["correct"])

    cont_acc = np.mean(contaminated_correct) if contaminated_correct else 0.0
    clean_acc = np.mean(clean_correct) if clean_correct else np.mean([r["correct"] for r in eval_results])
    effect_size = cont_acc - clean_acc

    return {
        "contaminated_accuracy": float(cont_acc),
        "clean_accuracy": float(clean_acc),
        "effect_size": float(effect_size),
        "n_contaminated": len(contaminated_correct),
        "n_clean": len(clean_correct),
    }
