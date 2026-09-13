"""Entropy Layer Ranking for h-e2.

Computes mean per-layer attention entropy over calibration set using head-mean pooling.
Head-mean (not head-max) — critical lesson from h-e1.
"""
from __future__ import annotations

import torch
from typing import Tuple, List


def compute_entropy_layer_ranking(
    model,
    tokenizer,
    calib_dataset,
    n_sequences: int = 100,
    max_seq_len: int = 512,
    device: str = "cuda",
) -> List[int]:
    """
    Returns 32 layer indices sorted by mean per-layer attention entropy descending.
    Head-mean pooling (NOT head-max — h-e1 lesson).
    """
    ranking, _ = compute_entropy_layer_ranking_with_scores(
        model, tokenizer, calib_dataset, n_sequences, max_seq_len, device
    )
    return ranking


def compute_entropy_layer_ranking_with_scores(
    model,
    tokenizer,
    calib_dataset,
    n_sequences: int = 100,
    max_seq_len: int = 512,
    device: str = "cuda",
) -> Tuple[List[int], List[float]]:
    """
    Returns:
        ranking: list[int] — layer indices sorted entropy descending
        entropy_scores: list[float] — mean entropy per layer (index=layer_idx)
    """
    model.eval()
    num_layers = model.config.num_hidden_layers  # 32 for Llama-2-7B
    layer_entropy_sums = torch.zeros(num_layers, device=device)
    count = 0

    for i, sample in enumerate(calib_dataset):
        if i >= n_sequences:
            break
        text = sample["text"]
        if not text or not text.strip():
            continue

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_seq_len,
        ).to(device)

        if inputs["input_ids"].shape[1] < 2:
            continue

        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)

        # outputs.attentions: tuple of (1, n_heads, seq_len, seq_len) per layer
        for layer_idx, attn in enumerate(outputs.attentions):
            # attn: (1, n_heads, seq_len, seq_len) — already softmaxed
            attn_mean = attn[0].mean(dim=0)  # head-mean → (seq_len, seq_len)
            eps = 1e-9
            H = -(attn_mean * torch.log(attn_mean + eps)).sum(dim=-1)  # (seq_len,)
            layer_entropy_sums[layer_idx] += H.mean().item()

        count += 1
        if count % 10 == 0:
            print(f"  Calibration progress: {count}/{n_sequences}")

    if count == 0:
        raise ValueError("No valid calibration sequences found")

    layer_entropy_mean = layer_entropy_sums / count  # (num_layers,)
    ranking = torch.argsort(layer_entropy_mean, descending=True).tolist()
    entropy_scores = layer_entropy_mean.tolist()

    print(f"Entropy ranking complete ({count} sequences). Top-4: {ranking[:4]}")
    return ranking, entropy_scores
