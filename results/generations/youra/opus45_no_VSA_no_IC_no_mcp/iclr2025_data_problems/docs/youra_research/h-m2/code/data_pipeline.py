"""Data pipeline: download, deduplicate, tokenize, pack."""
import os
import json
import torch
from typing import List, Optional
from transformers import GPT2TokenizerFast
from config import DeduplicationConfig, ScaledExperimentConfig
from dedup import apply_deduplication, log_dedup_stats, verify_deduplication_applied

def download_redpajama(num_samples: int = 50000, cache_dir: str = "./data/raw") -> List[str]:
    """Download RedPajama-v2 sample documents."""
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"redpajama_{num_samples}.json")

    if os.path.exists(cache_file):
        print(f"Loading cached documents from {cache_file}")
        with open(cache_file, "r") as f:
            return json.load(f)

    print(f"Downloading RedPajama-v2 sample ({num_samples} documents)...")
    try:
        from datasets import load_dataset
        ds = load_dataset(
            "togethercomputer/RedPajama-Data-v2",
            name="sample",
            split="train",
            streaming=True,
            trust_remote_code=True
        )
        documents = []
        for i, item in enumerate(ds):
            if i >= num_samples:
                break
            text = item.get("raw_content", item.get("text", ""))
            if text and len(text) > 100:
                documents.append(text[:5000])  # truncate long docs
        print(f"Downloaded {len(documents)} documents")
    except Exception as e:
        print(f"RedPajama download failed: {e}")
        print("Generating synthetic data for validation...")
        documents = generate_synthetic_corpus(num_samples)

    with open(cache_file, "w") as f:
        json.dump(documents, f)

    return documents

def generate_synthetic_corpus(num_samples: int) -> List[str]:
    """Generate synthetic text corpus for validation."""
    import random
    random.seed(42)

    templates = [
        "The {} {} the {} {}.",
        "In {} times, people {} to {} their {}.",
        "Research shows that {} can {} {}.",
        "The study of {} reveals {} patterns in {}.",
        "Understanding {} requires {} analysis of {}.",
    ]

    nouns = ["algorithm", "data", "model", "system", "network", "function",
             "process", "structure", "method", "approach", "theory", "concept"]
    verbs = ["analyzes", "processes", "transforms", "evaluates", "computes",
             "optimizes", "generates", "validates", "implements", "designs"]
    adjectives = ["complex", "efficient", "robust", "scalable", "innovative",
                  "fundamental", "advanced", "modern", "traditional", "novel"]

    documents = []
    for i in range(num_samples):
        num_sentences = random.randint(5, 20)
        sentences = []
        for _ in range(num_sentences):
            template = random.choice(templates)
            words = []
            for char in template.split("{}"):
                if words:
                    word_type = random.choice([nouns, verbs, adjectives])
                    words.append(random.choice(word_type))
            sentence = template
            for word in words[:-1]:
                sentence = sentence.replace("{}", word, 1)
            sentences.append(sentence)

        doc = " ".join(sentences)
        # Create some duplicates for dedup testing
        if i > 0 and random.random() < 0.1:
            doc = documents[random.randint(0, len(documents)-1)]
        elif i > 0 and random.random() < 0.15:
            base = documents[random.randint(0, len(documents)-1)]
            words = base.split()
            for j in range(len(words) // 10):
                idx = random.randint(0, len(words)-1)
                words[idx] = random.choice(nouns + verbs + adjectives)
            doc = " ".join(words)

        documents.append(doc)

    print(f"Generated {len(documents)} synthetic documents")
    return documents

def build_dataset(documents: List[str], config: DeduplicationConfig) -> List[str]:
    """Apply deduplication and verify."""
    original_count = len(documents)
    deduplicated = apply_deduplication(documents, config)
    deduplicated_count = len(deduplicated)

    verified = verify_deduplication_applied(original_count, deduplicated_count, config)
    stats = log_dedup_stats(config.level, original_count, deduplicated_count)

    if not verified:
        print(f"WARNING: Deduplication verification failed for level {config.level}")

    return deduplicated

def tokenize_and_pack(
    documents: List[str],
    total_tokens: int,
    seq_len: int = 256,
    tokenizer_name: str = "gpt2"
) -> torch.Tensor:
    """Tokenize documents and pack into fixed-length sequences."""
    tokenizer = GPT2TokenizerFast.from_pretrained(tokenizer_name)
    tokenizer.pad_token = tokenizer.eos_token

    all_tokens = []
    for doc in documents:
        tokens = tokenizer.encode(doc, add_special_tokens=False)
        all_tokens.extend(tokens)
        all_tokens.append(tokenizer.eos_token_id)

    # Repeat or truncate to total_tokens
    if len(all_tokens) < total_tokens:
        repeats = (total_tokens // len(all_tokens)) + 1
        all_tokens = (all_tokens * repeats)[:total_tokens]
    else:
        all_tokens = all_tokens[:total_tokens]

    # Pack into sequences
    num_seqs = len(all_tokens) // seq_len
    tokens_tensor = torch.tensor(all_tokens[:num_seqs * seq_len], dtype=torch.long)
    packed = tokens_tensor.view(num_seqs, seq_len)

    print(f"Packed {len(all_tokens)} tokens into {packed.shape[0]} sequences of length {seq_len}")
    return packed

def save_packed_tokens(tokens: torch.Tensor, level: str, out_dir: str = "./data/packed") -> str:
    """Save packed tokens to disk."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{level}.pt")
    torch.save(tokens, path)
    print(f"Saved packed tokens to {path}")
    return path

def load_packed_tokens(level: str, data_dir: str = "./data/packed") -> Optional[torch.Tensor]:
    """Load packed tokens from disk if exists."""
    path = os.path.join(data_dir, f"{level}.pt")
    if os.path.exists(path):
        return torch.load(path)
    return None
