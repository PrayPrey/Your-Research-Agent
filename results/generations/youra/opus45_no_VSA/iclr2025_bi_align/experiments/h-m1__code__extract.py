"""Hidden state extraction from LLMs."""
import torch
from pathlib import Path
from typing import Optional
import numpy as np


def pool_last_token(hidden, attention_mask):
    """Pool last non-pad token. hidden: [B, S, H], mask: [B, S] -> [B, H]."""
    last_idx = attention_mask.sum(dim=1) - 1
    batch_idx = torch.arange(hidden.size(0), device=hidden.device)
    return hidden[batch_idx, last_idx]


def extract_hidden_states(
    model,
    tokenizer,
    texts: list,
    layer_idx: int = -1,
    batch_size: int = 8,
    device: str = "cuda",
    max_length: int = 512,
):
    """Extract pooled hidden states at layer_idx. Returns [N, H]."""
    model.eval()
    all_pooled = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        enc = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            out = model(**enc, output_hidden_states=True)

        h = out.hidden_states[layer_idx]
        pooled = pool_last_token(h, enc["attention_mask"])
        all_pooled.append(pooled.cpu())

    return torch.cat(all_pooled, dim=0)


def compute_bai_scores_simple(texts: list, proxy_keywords: dict = None) -> np.ndarray:
    """Simple BAI scoring via keyword matching (lightweight for PoC).

    For full H-E1 integration, load the actual proxy classifiers.
    Here we use a simplified heuristic based on agency indicators.
    """
    if proxy_keywords is None:
        proxy_keywords = {
            "clarifying_question": ["?", "could you", "can you clarify", "what do you mean"],
            "option_enumeration": ["option 1", "option 2", "alternatively", "you could"],
            "epistemic_hedging": ["might", "perhaps", "possibly", "I think", "not sure"],
            "explicit_deferral": ["up to you", "your choice", "you decide", "depends on"],
        }

    scores = []
    for text in texts:
        text_lower = text.lower()
        proxy_scores = []
        for proxy, keywords in proxy_keywords.items():
            hits = sum(1 for kw in keywords if kw.lower() in text_lower)
            proxy_scores.append(min(1.0, hits / len(keywords)))
        scores.append(np.mean(proxy_scores))

    return np.array(scores)


def binarize_bai(bai_scores: np.ndarray) -> np.ndarray:
    """Median split for balanced binary labels."""
    thresh = np.median(bai_scores)
    if np.std(bai_scores) < 1e-6:
        thresh = 0.5
    return (bai_scores > thresh).astype(int)


def cache_activations(acts: torch.Tensor, labels: np.ndarray, path: str):
    """Save activations and labels to disk."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"activations": acts, "labels": labels}, path)


def load_cached(path: str):
    """Load cached activations and labels."""
    data = torch.load(path)
    return data["activations"], data["labels"]
