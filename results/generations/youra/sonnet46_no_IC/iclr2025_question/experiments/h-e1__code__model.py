"""h-e1 model loading, layout validation, per-layer lens extraction (A-2, A-3)."""
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from constants import MODEL_IDS, EXPECTED_HIDDEN_STATES, HF_TOKEN


class LayoutError(Exception):
    pass


def load_model(model_key: str):
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_IDS[model_key], torch_dtype=torch.float16,
        device_map="auto", token=HF_TOKEN).eval()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_IDS[model_key], token=HF_TOKEN)
    return model, tokenizer


def validate_layout(model) -> None:
    if not hasattr(model, "model") or not hasattr(model.model, "norm"):
        raise LayoutError(f"{type(model).__name__} missing model.model.norm")
    if not hasattr(model, "lm_head"):
        raise LayoutError(f"{type(model).__name__} missing model.lm_head")


@torch.no_grad()
def per_layer_lens_signals(model, hidden_states, answer_slice) -> dict:
    """Single pass over 32 non-embedding layers (A-3.1 + A-3.2 merged).
    Returns {"entropy": (32,), "maxprob": (32,), "adj_kl": (32,), "top1_match": (32,)}.
    adj_kl[0] = NaN. Raises LayoutError if len(hidden_states) != 33."""
    if len(hidden_states) != EXPECTED_HIDDEN_STATES:
        raise LayoutError(
            f"expected {EXPECTED_HIDDEN_STATES} hidden states, got {len(hidden_states)}")

    norm, head = model.model.norm, model.lm_head
    n = EXPECTED_HIDDEN_STATES - 1
    entropy = np.zeros(n)
    maxprob = np.zeros(n)
    adj_kl = np.full(n, np.nan)
    argmax_ids = []
    prev_logp = None
    for l in range(n):
        h_l = hidden_states[l + 1][:, answer_slice, :]        # skip embedding idx 0
        logits = head(norm(h_l)).float()                      # (1, T_ans, V) float32
        logp = logits.log_softmax(-1)
        p = logp.exp()
        entropy[l] = (-(p * logp).sum(-1)).mean().item()
        maxprob[l] = p.max(-1).values.mean().item()
        argmax_ids.append(logp.argmax(-1)[0])                 # (T_ans,)
        if prev_logp is not None:
            adj_kl[l] = (p * (logp - prev_logp)).sum(-1).mean().item()
        prev_logp = logp                                      # single buffer (R7)

    final_argmax = argmax_ids[n - 1]
    top1_match = np.array(
        [(a == final_argmax).float().mean().item() for a in argmax_ids])
    return {"entropy": entropy, "maxprob": maxprob, "adj_kl": adj_kl,
            "top1_match": top1_match}
