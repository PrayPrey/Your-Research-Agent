"""Data loading utilities for DynaMix experiment.

Loads real text data from HuggingFace datasets for 5 domains:
- web: Common Crawl / C4
- code: The Stack / code_search_net
- science: Scientific papers (pubmed abstracts)
- wiki: Wikipedia
- instructions: Alpaca / FLAN style instructions
"""

import os
import logging
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import GPT2TokenizerFast
from datasets import load_dataset
from config import DOMAINS, SEQ_LEN, TOKENS_PER_DOMAIN, DATA_CACHE_DIR

logger = logging.getLogger(__name__)


def get_tokenizer():
    """Load GPT-2 tokenizer."""
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def tokenize_texts(texts, tokenizer, max_tokens=None):
    """Tokenize a list of texts and return concatenated token IDs."""
    all_ids = []
    for text in texts:
        ids = tokenizer.encode(text, add_special_tokens=False)
        all_ids.extend(ids)
        all_ids.append(tokenizer.eos_token_id)
        if max_tokens and len(all_ids) >= max_tokens:
            break
    if max_tokens:
        all_ids = all_ids[:max_tokens]
    return all_ids


def load_domain_data(domain, tokenizer, max_tokens=TOKENS_PER_DOMAIN, split="train"):
    """Load data for a specific domain."""
    os.makedirs(DATA_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(DATA_CACHE_DIR, f"{domain}_{split}_{max_tokens}.pt")

    if os.path.exists(cache_path):
        logger.info(f"Loading cached {domain} data from {cache_path}")
        return torch.load(cache_path)

    logger.info(f"Loading {domain} data from HuggingFace...")

    texts = []
    try:
        if domain == "web":
            # C4 dataset (Common Crawl)
            ds = load_dataset("allenai/c4", "en", split=split, streaming=True)
            count = 0
            for sample in ds:
                texts.append(sample["text"])
                count += 1
                if count >= 2000:
                    break

        elif domain == "code":
            # CodeSearchNet Python
            ds = load_dataset("code_search_net", "python", split=split, streaming=True)
            count = 0
            for sample in ds:
                if sample.get("func_code_string"):
                    texts.append(sample["func_code_string"])
                count += 1
                if count >= 2000:
                    break

        elif domain == "science":
            # Scientific papers (arXiv abstracts)
            ds = load_dataset("scientific_papers", "arxiv", split=split, streaming=True)
            count = 0
            for sample in ds:
                if sample.get("abstract"):
                    texts.append(sample["abstract"])
                count += 1
                if count >= 2000:
                    break

        elif domain == "wiki":
            # Wikipedia
            ds = load_dataset("wikimedia/wikipedia", "20231101.en", split=split, streaming=True)
            count = 0
            for sample in ds:
                texts.append(sample["text"])
                count += 1
                if count >= 2000:
                    break

        elif domain == "instructions":
            # FLAN/Alpaca style
            ds = load_dataset("tatsu-lab/alpaca", split=split, streaming=True)
            count = 0
            for sample in ds:
                text = f"Instruction: {sample.get('instruction', '')} Input: {sample.get('input', '')} Output: {sample.get('output', '')}"
                texts.append(text)
                count += 1
                if count >= 2000:
                    break
    except Exception as e:
        logger.warning(f"Failed to load {domain} from primary source: {e}. Using fallback.")
        texts = _load_fallback(domain, tokenizer, max_tokens)
        token_ids = tokenize_texts(texts, tokenizer, max_tokens)
        data = torch.tensor(token_ids, dtype=torch.long)
        torch.save(data, cache_path)
        return data

    if len(texts) < 50:
        logger.warning(f"Only got {len(texts)} texts for {domain}, using fallback")
        texts = _load_fallback(domain, tokenizer, max_tokens)

    token_ids = tokenize_texts(texts, tokenizer, max_tokens)
    data = torch.tensor(token_ids, dtype=torch.long)
    torch.save(data, cache_path)
    logger.info(f"Loaded {len(data)} tokens for {domain}")
    return data


def _load_fallback(domain, tokenizer, max_tokens):
    """Fallback data loading using widely available datasets."""
    logger.info(f"Using fallback dataset for {domain}")

    if domain in ["web", "wiki"]:
        # Use wikitext as fallback
        ds = load_dataset("wikitext", "wikitext-103-raw-v1", split="train", streaming=True)
        texts = []
        for sample in ds:
            if sample["text"].strip():
                texts.append(sample["text"])
            if len(texts) >= 2000:
                break
        return texts

    elif domain == "code":
        # Use github code fallback
        try:
            ds = load_dataset("bigcode/the-stack-smol", data_dir="data/python", split="train", streaming=True)
            texts = []
            for sample in ds:
                texts.append(sample.get("content", ""))
                if len(texts) >= 1000:
                    break
            if texts:
                return texts
        except:
            pass
        # Last resort: use wikitext
        ds = load_dataset("wikitext", "wikitext-103-raw-v1", split="train", streaming=True)
        texts = []
        for sample in ds:
            if sample["text"].strip():
                texts.append("# Python code\n" + sample["text"])
            if len(texts) >= 1000:
                break
        return texts

    elif domain == "science":
        try:
            ds = load_dataset("scientific_papers", "arxiv", split="train", streaming=True)
            texts = []
            for sample in ds:
                if sample.get("abstract"):
                    texts.append(sample["abstract"])
                if len(texts) >= 1000:
                    break
            if texts:
                return texts
        except:
            pass
        ds = load_dataset("wikitext", "wikitext-103-raw-v1", split="train", streaming=True)
        texts = []
        for sample in ds:
            if sample["text"].strip():
                texts.append(sample["text"])
            if len(texts) >= 1000:
                break
        return texts

    elif domain == "instructions":
        try:
            ds = load_dataset("databricks/databricks-dolly-15k", split="train", streaming=True)
            texts = []
            for sample in ds:
                text = f"Instruction: {sample.get('instruction', '')} Response: {sample.get('response', '')}"
                texts.append(text)
                if len(texts) >= 1000:
                    break
            if texts:
                return texts
        except:
            pass
        ds = load_dataset("wikitext", "wikitext-103-raw-v1", split="train", streaming=True)
        texts = []
        for sample in ds:
            if sample["text"].strip():
                texts.append(sample["text"])
            if len(texts) >= 1000:
                break
        return texts

    return ["Fallback text " * 100] * 100


class DomainDataset(Dataset):
    """Dataset that samples from multiple domains with given mixture weights."""

    def __init__(self, domain_data, seq_len=SEQ_LEN):
        """
        domain_data: dict {domain_name: token_tensor}
        seq_len: sequence length for each sample
        """
        self.domain_data = domain_data
        self.seq_len = seq_len
        self.domains = list(domain_data.keys())

        # Precompute number of sequences per domain
        self.num_seqs = {}
        for domain, data in domain_data.items():
            n = len(data) // seq_len
            self.num_seqs[domain] = max(1, n)

    def get_batch(self, domain, batch_size, device="cpu"):
        """Get a random batch from a specific domain."""
        data = self.domain_data[domain]
        n_seqs = len(data) // self.seq_len
        if n_seqs < 1:
            # Pad if too short
            data = data.repeat(self.seq_len // len(data) + 2)
            n_seqs = len(data) // self.seq_len

        indices = torch.randint(0, n_seqs, (batch_size,))
        x = torch.stack([data[i * self.seq_len: (i + 1) * self.seq_len] for i in indices])
        return x.to(device)

    def get_mixed_batch(self, mixture_weights, batch_size, device="cpu"):
        """Get a mixed batch according to mixture weights."""
        weights = np.array(mixture_weights)
        weights = weights / weights.sum()

        # Sample domain counts
        counts = np.random.multinomial(batch_size, weights)

        batches = []
        domain_indices = []
        for i, (domain, count) in enumerate(zip(self.domains, counts)):
            if count > 0:
                batch = self.get_batch(domain, count, device)
                batches.append(batch)
                domain_indices.extend([i] * count)

        x = torch.cat(batches, dim=0)
        # Shuffle
        perm = torch.randperm(x.size(0))
        return x[perm]

    def __len__(self):
        return sum(self.num_seqs.values())

    def __getitem__(self, idx):
        # Not used directly, use get_batch instead
        return None


def load_all_domains(tokenizer, max_tokens=TOKENS_PER_DOMAIN):
    """Load data for all domains."""
    domain_data = {}
    for domain in DOMAINS:
        data = load_domain_data(domain, tokenizer, max_tokens)
        domain_data[domain] = data
        logger.info(f"Domain {domain}: {len(data)} tokens")
    return domain_data


def get_eval_data(domain_data, seq_len=SEQ_LEN, n_batches=20, device="cpu"):
    """Get evaluation data for each domain."""
    eval_data = {}
    for domain, data in domain_data.items():
        n_seqs = len(data) // seq_len
        if n_seqs < n_batches:
            n_seqs = n_batches
        # Use last 20% of data for evaluation (avoid overlap with train)
        eval_start = int(len(data) * 0.8)
        eval_tokens = data[eval_start:]
        if len(eval_tokens) < seq_len * n_batches:
            eval_tokens = data  # Use all if not enough

        n = min(n_batches, len(eval_tokens) // seq_len)
        seqs = [eval_tokens[i * seq_len: (i + 1) * seq_len] for i in range(n)]
        if seqs:
            eval_data[domain] = torch.stack(seqs).to(device)
    return eval_data
