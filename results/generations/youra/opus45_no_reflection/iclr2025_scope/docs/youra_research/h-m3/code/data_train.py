"""H-M3 Training Data Pipeline - C4 streaming loader per length bucket"""
import torch
from typing import Iterator, Dict
from datasets import load_dataset
from config import ExperimentConfig

def get_c4_stream(config: ExperimentConfig, tokenizer, length: int) -> Iterator[Dict[str, torch.Tensor]]:
    """Stream tokenized batches from C4 at target length."""
    try:
        dataset = load_dataset(
            config.train_dataset,
            config.train_dataset_config,
            split="train",
            streaming=True,
        )
    except Exception as e:
        raise RuntimeError(
            f"C4 dataset unavailable: {e}. "
            "Ensure internet access and HuggingFace datasets works. "
            "Run: python -c \"from datasets import load_dataset; ds = load_dataset('allenai/c4', 'en', split='train', streaming=True); print(next(iter(ds)))\""
        )

    buffer = []
    for example in dataset:
        text = example.get("text", "")
        if len(text) < 100:
            continue

        tokens = tokenizer(
            text,
            truncation=True,
            max_length=length,
            padding="max_length",
            return_tensors="pt",
        )
        buffer.append(tokens["input_ids"].squeeze(0))

        if len(buffer) >= config.batch_size:
            batch = torch.stack(buffer[:config.batch_size])
            buffer = buffer[config.batch_size:]
            yield {"input_ids": batch.cuda()}

def _synthetic_text_stream():
    """Fallback synthetic data for offline testing."""
    import random
    words = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "and", "cat"]
    while True:
        text = " ".join(random.choices(words, k=500))
        yield {"text": text}
