"""Model loading and evaluation for H-E1 benchmark correlation experiment."""

import torch
import numpy as np
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import MODEL_ID, SEED


def load_model(model_id: str = MODEL_ID, device: str = "cuda"):
    """Load model and tokenizer in eval mode."""
    torch.manual_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer


def sequence_logprob(model, tokenizer, prompt: str, continuation: str, device: str = "cuda") -> float:
    """Compute log probability of continuation given prompt."""
    full_text = prompt + continuation
    prompt_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids
    full_ids = tokenizer(full_text, return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)

    prompt_len = prompt_ids.shape[1]

    with torch.no_grad():
        outputs = model(full_ids)
        logits = outputs.logits  # [1, L, V]

    log_probs = torch.log_softmax(logits, dim=-1)

    # Get log probs for continuation tokens (shifted by 1)
    cont_log_probs = []
    for i in range(prompt_len, full_ids.shape[1]):
        token_id = full_ids[0, i].item()
        cont_log_probs.append(log_probs[0, i - 1, token_id].item())

    return sum(cont_log_probs) if cont_log_probs else 0.0


def eval_truthfulqa_mc1(model, tokenizer, dataset, device: str = "cuda") -> np.ndarray:
    """Evaluate TruthfulQA MC1 accuracy. Returns binary array."""
    results = []
    for sample in tqdm(dataset, desc="TruthfulQA MC1"):
        question = sample["question"]
        choices = sample["mc1_targets"]["choices"]
        labels = sample["mc1_targets"]["labels"]

        scores = []
        for choice in choices:
            lp = sequence_logprob(model, tokenizer, question + " ", choice, device)
            scores.append(lp)

        pred_idx = np.argmax(scores)
        correct = 1 if labels[pred_idx] == 1 else 0
        results.append(correct)

    return np.array(results)


def eval_hhh_preference(model, tokenizer, dataset, device: str = "cuda") -> np.ndarray:
    """Evaluate HHH preference accuracy. Returns binary array."""
    results = []
    for sample in tqdm(dataset, desc="HHH Preference"):
        chosen = sample["chosen"]
        rejected = sample["rejected"]

        # Find common prefix (prompt)
        min_len = min(len(chosen), len(rejected))
        prefix_end = 0
        for i in range(min_len):
            if chosen[i] != rejected[i]:
                break
            prefix_end = i + 1

        # Use first part as prompt, rest as continuation
        prompt = chosen[:prefix_end] if prefix_end > 0 else ""
        chosen_cont = chosen[prefix_end:]
        rejected_cont = rejected[prefix_end:]

        lp_chosen = sequence_logprob(model, tokenizer, prompt, chosen_cont, device)
        lp_rejected = sequence_logprob(model, tokenizer, prompt, rejected_cont, device)

        correct = 1 if lp_chosen > lp_rejected else 0
        results.append(correct)

    return np.array(results)


def run_all_evaluations(model, tokenizer, truthfulqa_ds, hhh_helpful_ds, hhh_harmless_ds):
    """Run all benchmark evaluations."""
    scores = {}

    print("Evaluating TruthfulQA...")
    scores["truthfulqa"] = eval_truthfulqa_mc1(model, tokenizer, truthfulqa_ds)
    print(f"  Accuracy: {scores['truthfulqa'].mean():.3f}")

    print("Evaluating HHH-helpful...")
    scores["hhh_helpful"] = eval_hhh_preference(model, tokenizer, hhh_helpful_ds)
    print(f"  Accuracy: {scores['hhh_helpful'].mean():.3f}")

    print("Evaluating HHH-harmless...")
    scores["hhh_harmless"] = eval_hhh_preference(model, tokenizer, hhh_harmless_ds)
    print(f"  Accuracy: {scores['hhh_harmless'].mean():.3f}")

    return scores
