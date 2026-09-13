"""Perplexity evaluation for h-e2.

Stride-chunked NLL perplexity — HuggingFace standard pattern.
stride=512 matches SWA window_size for fair comparison.
"""
from __future__ import annotations

import torch
from tqdm import tqdm


def load_wikitext103_test_text() -> str:
    """Load WikiText-103 test split and join with double newlines."""
    from datasets import load_dataset
    print("Loading WikiText-103 test split...")
    dataset = load_dataset("wikitext", "wikitext-103-v1", trust_remote_code=True)
    test_text = "\n\n".join(dataset["test"]["text"])
    print(f"Loaded test split: {len(test_text)} chars")
    return test_text


def compute_perplexity(
    model,
    tokenizer,
    text: str,
    max_length: int = 4096,
    stride: int = 512,
) -> float:
    """
    Stride-chunked NLL perplexity (HuggingFace standard pattern).
    Discards trailing incomplete chunk.
    Uses torch.no_grad() throughout.
    Returns perplexity as float.
    """
    encodings = tokenizer(text, return_tensors="pt")
    input_ids = encodings.input_ids.to(model.device)
    seq_len = input_ids.shape[1]
    print(f"  Total tokens: {seq_len}")

    nlls = []
    prev_end_loc = 0
    chunk_count = 0

    for begin_loc in tqdm(range(0, seq_len, stride), desc="  PPL eval"):
        end_loc = min(begin_loc + max_length, seq_len)
        trg_len = end_loc - prev_end_loc  # tokens newly entering the target window

        if trg_len <= 0:
            prev_end_loc = end_loc
            if end_loc == seq_len:
                break
            continue

        input_chunk = input_ids[:, begin_loc:end_loc]
        target_ids = input_chunk.clone()
        target_ids[:, :-trg_len] = -100  # mask context (non-new) tokens

        with torch.no_grad():
            outputs = model(input_chunk, labels=target_ids)
            # outputs.loss = mean NLL over non-masked positions

        nlls.append(outputs.loss.float() * trg_len)
        prev_end_loc = end_loc
        chunk_count += 1

        if end_loc == seq_len:
            break

    total_nll = torch.stack(nlls).sum()
    ppl = torch.exp(total_nll / seq_len)
    print(f"  Evaluated {chunk_count} chunks, PPL={ppl.item():.4f}")
    return ppl.item()
