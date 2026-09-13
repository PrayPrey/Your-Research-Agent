"""Data loading for h-e1: WikiText-103 calibration subsets."""
import torch
from datasets import load_dataset
from transformers import AutoTokenizer


def load_wikitext103():
    """Load WikiText-103 validation split texts."""
    ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="validation")
    return ds["text"]


def chunk_and_split(
    texts,
    tokenizer_name="meta-llama/Llama-2-7b-hf",
    seqlen=2048,
    n_subsets=3,
    subset_size=45,
):
    """
    Tokenize WikiText-103 texts, chunk into seqlen windows, split into n_subsets.

    Returns:
        (subset_A, subset_B, subset_C) — each a list of `subset_size` tensors of shape (1, seqlen)
    """
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    full_text = "\n\n".join(t for t in texts if t.strip())

    token_ids = tokenizer.encode(full_text, add_special_tokens=False)
    token_ids = torch.tensor(token_ids, dtype=torch.long)

    n_chunks = len(token_ids) // seqlen
    token_ids = token_ids[: n_chunks * seqlen]
    chunks = token_ids.view(n_chunks, seqlen)
    chunk_list = [chunks[i].unsqueeze(0) for i in range(n_chunks)]

    required = n_subsets * subset_size
    assert len(chunk_list) >= required, (
        f"Need ≥{required} chunks, got {len(chunk_list)}"
    )

    subset_A = chunk_list[0:subset_size]
    subset_B = chunk_list[subset_size:2*subset_size]
    subset_C = chunk_list[2*subset_size:3*subset_size]
    return subset_A, subset_B, subset_C
