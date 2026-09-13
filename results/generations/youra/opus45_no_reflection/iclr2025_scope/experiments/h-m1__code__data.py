"""Data loading and preprocessing for H-M1."""
import random
from typing import List
from datasets import load_dataset
from tqdm import tqdm
from config import AnalysisConfig

def get_long_documents(config: AnalysisConfig, tokenizer) -> List[str]:
    """Stream C4 validation, filter for docs >= min_doc_tokens, take num_samples with seed."""
    random.seed(config.seed)
    dataset = load_dataset(config.dataset_name, config.dataset_config,
                          split=config.dataset_split, streaming=True)

    long_docs = []
    print(f"Streaming C4 validation, filtering for docs >= {config.min_doc_tokens} tokens...")

    for example in tqdm(dataset, desc="Filtering long documents"):
        text = example["text"]
        tokens = tokenizer(text, truncation=False, add_special_tokens=False)["input_ids"]
        if len(tokens) >= config.min_doc_tokens:
            long_docs.append(text)
            if len(long_docs) >= config.num_samples:
                break

    print(f"Found {len(long_docs)} documents with >= {config.min_doc_tokens} tokens")
    return long_docs

def truncate_to_length(text: str, tokenizer, length: int) -> dict:
    """Tokenize and truncate to exact length, return dict with input_ids/attention_mask."""
    tokens = tokenizer(text, truncation=False, return_tensors="pt", padding=False)
    if tokens["input_ids"].shape[1] > length:
        tokens["input_ids"] = tokens["input_ids"][:, :length]
        tokens["attention_mask"] = tokens["attention_mask"][:, :length]
    return tokens
