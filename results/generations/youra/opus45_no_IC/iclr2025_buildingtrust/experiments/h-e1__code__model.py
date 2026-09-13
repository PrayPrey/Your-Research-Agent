"""Model loading and inference for Llama-2-7B on TruthfulQA."""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import MODEL_ID, DTYPE, DEVICE_MAP


def load_model_and_tokenizer(model_id=MODEL_ID):
    """Load Llama-2-7B model and tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=DTYPE,
        device_map=DEVICE_MAP,
    )
    model.eval()
    return model, tokenizer


def score_choices(model, tokenizer, question, choices, device):
    """Compute log-probability for each answer choice."""
    scores = []
    for choice in choices:
        prompt = f"Q: {question}\nA: {choice}"
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits

        answer_tokens = tokenizer(choice, return_tensors="pt", add_special_tokens=False).input_ids[0]
        answer_len = len(answer_tokens)

        if answer_len > 0:
            log_probs = F.log_softmax(logits[0, -answer_len-1:-1], dim=-1)
            answer_tokens = answer_tokens.to(device)
            score = log_probs[range(answer_len), answer_tokens].sum().item()
        else:
            score = float("-inf")

        scores.append(score)
    return scores


def predict(question, choices, correct_idx, model, tokenizer, device, cluster_id):
    """Predict answer and return confidence + correctness."""
    scores = score_choices(model, tokenizer, question, choices, device)
    probs = F.softmax(torch.tensor(scores), dim=-1)
    confidence, pred_idx = probs.max(dim=-1)
    correct = (pred_idx.item() == correct_idx)

    return {
        "confidence": confidence.item(),
        "correct": correct,
        "cluster_id": cluster_id,
        "predicted_idx": pred_idx.item(),
        "correct_idx": correct_idx,
    }
