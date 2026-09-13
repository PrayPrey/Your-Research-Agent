"""Data loading for H-M1: SST-2 validation set."""
from datasets import load_dataset


def load_sst2_validation() -> list[str]:
    """Load SST-2 validation texts (872 samples)."""
    ds = load_dataset("glue", "sst2", split="validation")
    return [ex["sentence"] for ex in ds]


def tokenize_batch(tokenizer, texts: list[str], max_length: int = 128) -> dict:
    """Tokenize a batch of texts."""
    return tokenizer(
        texts,
        truncation=True,
        max_length=max_length,
        padding=True,
        return_tensors="pt",
    )
