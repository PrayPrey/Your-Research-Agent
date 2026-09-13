"""Token Entropy computation for H-E1."""
import os
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_llama(model_id: str = "meta-llama/Llama-2-7b-hf", hf_token: str = None):
    """Load Llama-2-7B float16 with device_map=auto."""
    if hf_token is None:
        hf_token = os.environ.get("HF_TOKEN")
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        token=hf_token,
    )
    model.eval()
    return model, tokenizer


def compute_single_te(
    question_text: str,
    model,
    tokenizer,
    max_new_tokens: int = 50,
) -> float:
    """Greedy decode via output_scores; mean per-token Shannon entropy over generated tokens."""
    inputs = tokenizer(question_text, return_tensors="pt")
    input_ids = inputs["input_ids"].to(model.device)
    prompt_len = input_ids.shape[1]

    with torch.no_grad():
        out = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
        )

    if not out.scores:
        return 0.0

    # out.scores: tuple of (1, vocab_size) tensors, one per generated token
    scores = torch.stack(list(out.scores), dim=1)  # (1, gen_len, vocab_size)
    probs = torch.softmax(scores.float(), dim=-1)   # (1, gen_len, vocab_size)
    entropy = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1)  # (1, gen_len)
    return float(entropy.mean().item())


def compute_te_scores(questions: list, model, tokenizer) -> list:
    """Sequential TE computation over all questions. Returns list[float] len N."""
    te_scores = []
    for i, q in enumerate(questions):
        te = compute_single_te(q["question"], model, tokenizer)
        te_scores.append(te)
        if (i + 1) % 10 == 0:
            print(f"  TE: {i+1}/{len(questions)} done")
    return te_scores
