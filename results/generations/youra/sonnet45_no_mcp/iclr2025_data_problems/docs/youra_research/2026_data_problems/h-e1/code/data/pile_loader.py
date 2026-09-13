"""
Real Dataset Loader for Multi-Domain Text Data
Uses publicly available datasets as proxies for Pile domains.
Falls back to real accessible datasets when The Pile is unavailable.
"""

import torch
from torch.utils.data import Dataset
from datasets import load_dataset
from transformers import GPT2Tokenizer
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Mapping of domain names to publicly accessible dataset alternatives
# These are real datasets that approximate the Pile's domain categories
# Using datasets without loading scripts (Parquet/Arrow format)
DOMAIN_DATASET_MAPPING = {
    "Pile-CC": {
        "dataset": "allenai/c4",
        "subset": "en",
        "split": "train",
        "text_field": "text"
    },
    "StackExchange": {
        "dataset": "HuggingFaceH4/stack-exchange-preferences",
        "subset": None,
        "split": "train",
        "text_field": "question"
    },
    "Wikipedia": {
        "dataset": "wikimedia/wikipedia",
        "subset": "20231101.en",
        "split": "train",
        "text_field": "text"
    },
    "ArXiv": {
        "dataset": "togethercomputer/RedPajama-Data-1T-Sample",
        "subset": None,
        "split": "train",
        "text_field": "text"
    },
    "Github": {
        "dataset": "bigcode/the-stack-smol",
        "subset": "data/python",
        "split": "train",
        "text_field": "content"
    },
    "PubMed": {
        "dataset": "pubmed",
        "subset": None,
        "split": "train",
        "text_field": "MedlineCitation"
    }
}


class RealDataset(Dataset):
    """
    PyTorch Dataset wrapper for real multi-domain datasets.
    Uses publicly available datasets that match Pile domain characteristics.
    """

    def __init__(
        self,
        domain: str,
        tokenizer: GPT2Tokenizer,
        max_length: int = 2048,
        max_samples: Optional[int] = None,
        streaming: bool = True
    ):
        """
        Args:
            domain: Domain name from DOMAIN_DATASET_MAPPING keys
            tokenizer: GPT-2 tokenizer
            max_length: Maximum sequence length
            max_samples: Maximum number of samples to load (for testing/smoke test)
            streaming: If True, use streaming mode (recommended for large datasets)
        """
        self.domain = domain
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.max_samples = max_samples
        self.streaming = streaming

        if domain not in DOMAIN_DATASET_MAPPING:
            raise ValueError(f"Unknown domain: {domain}. Must be one of {list(DOMAIN_DATASET_MAPPING.keys())}")

        dataset_config = DOMAIN_DATASET_MAPPING[domain]
        dataset_name = dataset_config["dataset"]
        subset = dataset_config["subset"]
        split = dataset_config["split"]
        self.text_field = dataset_config["text_field"]

        logger.info(f"Loading real dataset for domain: {domain}")
        logger.info(f"  Dataset: {dataset_name}, Subset: {subset}, Streaming: {streaming}")

        try:
            # Load dataset from Hugging Face
            if subset:
                self.dataset = load_dataset(
                    dataset_name,
                    subset,
                    split=split,
                    streaming=streaming
                )
            else:
                self.dataset = load_dataset(
                    dataset_name,
                    split=split,
                    streaming=streaming
                )

            # Materialize samples if needed
            if not streaming and max_samples:
                self.samples = []
                for i, sample in enumerate(self.dataset):
                    if i >= max_samples:
                        break
                    self.samples.append(sample)
                logger.info(f"✅ Loaded {len(self.samples)} samples from {domain}")
            elif not streaming:
                self.samples = list(self.dataset)
                logger.info(f"✅ Loaded {len(self.samples)} samples from {domain}")
            else:
                # Streaming mode - create iterator
                self.samples = None
                self.dataset_iter = iter(self.dataset)
                self.cache = []
                logger.info(f"✅ Streaming mode enabled for {domain}")

        except Exception as e:
            logger.error(f"Failed to load dataset for {domain}: {e}")
            raise

    def __len__(self):
        if self.samples is not None:
            return len(self.samples)
        elif self.max_samples:
            return self.max_samples
        else:
            return 100000  # Default size for streaming

    def __getitem__(self, idx):
        """Get tokenized sample."""
        # Get raw text
        if self.samples is not None:
            # Non-streaming mode
            sample = self.samples[idx]
        else:
            # Streaming mode with cache
            while idx >= len(self.cache):
                try:
                    self.cache.append(next(self.dataset_iter))
                except StopIteration:
                    # Reset iterator if we run out
                    self.dataset_iter = iter(self.dataset)
                    self.cache.append(next(self.dataset_iter))
            sample = self.cache[idx % len(self.cache)]

        # Extract text from appropriate field
        raw_text = sample.get(self.text_field, "")

        # Handle cases where text might be empty or None
        if not raw_text:
            raw_text = " "

        # Tokenize
        encoded = self.tokenizer(
            raw_text,
            max_length=self.max_length + 1,  # +1 for shifting
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

        # Extract input_ids and create labels
        input_ids = encoded["input_ids"].squeeze(0)

        # Shift for autoregressive training
        return {
            "input_ids": input_ids[:-1],
            "labels": input_ids[1:]
        }


def load_pile_domains(
    domains: List[str],
    max_samples_per_domain: Optional[int] = None,
    streaming: bool = True,
    tokenizer: Optional[GPT2Tokenizer] = None
) -> Dict[str, Dataset]:
    """
    Load multiple real datasets matching Pile domain categories.

    Args:
        domains: List of domain names to load
        max_samples_per_domain: Max samples per domain (for testing)
        streaming: Use streaming mode
        tokenizer: GPT-2 tokenizer (creates one if None)

    Returns:
        Dict mapping domain name to RealDataset
    """
    if tokenizer is None:
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        tokenizer.pad_token = tokenizer.eos_token

    domain_datasets = {}
    failed_domains = []

    for domain in domains:
        try:
            dataset = RealDataset(
                domain=domain,
                tokenizer=tokenizer,
                max_length=2048,
                max_samples=max_samples_per_domain,
                streaming=streaming
            )
            domain_datasets[domain] = dataset
            logger.info(f"✅ Successfully loaded domain: {domain}")
        except Exception as e:
            logger.error(f"❌ Failed to load domain {domain}: {e}")
            failed_domains.append(domain)
            continue

    if not domain_datasets:
        raise RuntimeError(f"Failed to load any domains. Attempted: {domains}, Failed: {failed_domains}")

    if failed_domains:
        logger.warning(f"Successfully loaded {len(domain_datasets)}/{len(domains)} domains")
        logger.warning(f"Failed domains: {failed_domains}")

    return domain_datasets
