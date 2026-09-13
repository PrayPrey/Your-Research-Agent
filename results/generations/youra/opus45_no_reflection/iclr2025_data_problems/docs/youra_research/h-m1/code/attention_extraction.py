"""Attention extraction for H-M1."""
import torch
from tqdm import tqdm


def extract_attentions(
    model,
    tokenizer,
    texts: list[str],
    max_length: int = 128,
    device: str = "cpu",
) -> list[tuple]:
    """
    Forward pass per sample (batch=1).
    Returns list of per-sample attention tuples: each tuple has 12 tensors of shape [1, H, S, S].
    """
    model = model.to(device)
    model.eval()
    results = []

    for text in tqdm(texts, desc="Extracting attentions"):
        enc = tokenizer(
            text,
            truncation=True,
            max_length=max_length,
            padding=False,
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            out = model(**enc)

        # out.attentions is tuple of 12 tensors, each [1, H, S, S]
        # Move to CPU to avoid GPU memory accumulation
        cpu_attns = tuple(a.cpu() for a in out.attentions)
        results.append(cpu_attns)

    return results
