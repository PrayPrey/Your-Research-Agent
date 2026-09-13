"""MC1 evaluation for TruthfulQA benchmark."""
import torch
from typing import List


def compute_sequence_logprob(model, tokenizer, text: str, prompt_len: int, device: str) -> float:
    """Compute log-prob of answer tokens (after prompt_len)."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits

    # Shift for next-token prediction
    shift_logits = logits[:, :-1, :].contiguous()
    shift_labels = input_ids[:, 1:].contiguous()

    log_probs = torch.log_softmax(shift_logits, dim=-1)
    token_log_probs = log_probs.gather(-1, shift_labels.unsqueeze(-1)).squeeze(-1)

    # Sum only answer tokens (after prompt_len)
    answer_start = max(0, prompt_len - 1)
    answer_log_prob = token_log_probs[0, answer_start:].sum().item()
    return answer_log_prob


def evaluate_mc1(model, tokenizer, sample: dict, device: str) -> int:
    """Evaluate single MC1 sample. Returns 1 if correct, 0 otherwise."""
    question = sample["question"]
    choices = sample["mc1_targets"]["choices"]
    labels = sample["mc1_targets"]["labels"]

    # Find correct answer index
    correct_idx = labels.index(1)

    # Compute log-prob for each choice
    prompt = f"Q: {question}\nA:"
    prompt_len = len(tokenizer.encode(prompt))

    logprobs = []
    for choice in choices:
        text = f"Q: {question}\nA: {choice}"
        logprob = compute_sequence_logprob(model, tokenizer, text, prompt_len, device)
        logprobs.append(logprob)

    # Select highest log-prob
    predicted_idx = max(range(len(logprobs)), key=lambda i: logprobs[i])
    return 1 if predicted_idx == correct_idx else 0


def evaluate_mc1_batch(model, tokenizer, dataset, device: str, max_samples: int = None) -> dict:
    """Evaluate entire TruthfulQA MC1 dataset."""
    scores = []
    n = min(max_samples, len(dataset)) if max_samples else len(dataset)

    for i in range(n):
        score = evaluate_mc1(model, tokenizer, dataset[i], device)
        scores.append(score)

    accuracy = sum(scores) / len(scores) if scores else 0.0
    stderr = (accuracy * (1 - accuracy) / len(scores)) ** 0.5 if len(scores) > 1 else 0.0

    return {"scores": scores, "accuracy": accuracy, "stderr": stderr, "n": len(scores)}
