"""Data loading for H-M2 Hidden State Drift Analysis."""
import random
from typing import List, Dict
import torch
from datasets import load_dataset
from tqdm import tqdm
from config import AnalysisConfig


def get_long_documents(config: AnalysisConfig, tokenizer) -> List[str]:
    """Stream C4 validation, filter for docs with enough chars, take num_samples with seed."""
    random.seed(config.seed)
    dataset = load_dataset(
        config.dataset_name,
        config.dataset_config,
        split=config.dataset_split,
        streaming=True
    )

    long_docs = []
    print(f"Streaming C4 validation, filtering for docs >= {config.min_doc_chars} chars...")

    for example in tqdm(dataset, desc="Filtering long documents"):
        text = example["text"]
        if len(text) >= config.min_doc_chars:
            long_docs.append(text)
            if len(long_docs) >= config.num_samples:
                break

    print(f"Found {len(long_docs)} documents with >= {config.min_doc_chars} chars")
    return long_docs


def build_batches(docs: List[str], tokenizer, length: int, batch_size: int) -> List[Dict]:
    """Tokenize and batch documents at target length."""
    batches = []
    batch_texts = []

    for doc in docs:
        batch_texts.append(doc)
        if len(batch_texts) == batch_size:
            encoded = tokenizer(
                batch_texts,
                padding="max_length",
                truncation=True,
                max_length=length,
                return_tensors="pt"
            )
            batches.append({
                "input_ids": encoded["input_ids"],
                "attention_mask": encoded["attention_mask"]
            })
            batch_texts = []

    if batch_texts:
        encoded = tokenizer(
            batch_texts,
            padding="max_length",
            truncation=True,
            max_length=length,
            return_tensors="pt"
        )
        batches.append({
            "input_ids": encoded["input_ids"],
            "attention_mask": encoded["attention_mask"]
        })

    return batches
