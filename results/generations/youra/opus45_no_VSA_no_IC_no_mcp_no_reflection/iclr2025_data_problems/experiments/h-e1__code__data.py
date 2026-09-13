"""Data loading and caching for h-e1 experiment."""

import os
import json
import random
from datasets import load_dataset
from config import CONFIG


def load_pile_subset(domains: list[str], n_samples: int, seed: int) -> tuple[list[str], list[str]]:
    """Load domain samples from multiple HF datasets to simulate Pile domains.

    Uses readily available datasets mapped to domain categories.
    """
    random.seed(seed)

    # Map domains to available HF datasets
    domain_datasets = {
        'wikipedia': ('wikipedia', '20220301.en', 'train'),
        'arxiv': ('scientific_papers', 'arxiv', 'train'),
        'pubmed': ('scientific_papers', 'pubmed', 'train'),
        'github': ('codeparrot/github-code', 'Python', 'train'),
        'stackexchange': ('HuggingFaceH4/stack-exchange-preferences', None, 'train'),
        'books3': ('bookcorpus', None, 'train'),
        'pile-cc': ('c4', 'en', 'train'),
        'openwebtext2': ('openwebtext', None, 'train'),
    }

    texts = []
    labels = []

    for domain in domains:
        print(f"Loading {domain}...")
        try:
            ds_name, ds_config, split = domain_datasets.get(domain, (None, None, None))
            if ds_name is None:
                continue

            # Load with streaming for large datasets
            if ds_name in ['c4', 'openwebtext', 'wikipedia', 'codeparrot/github-code']:
                ds = load_dataset(ds_name, ds_config, split=split, streaming=True, trust_remote_code=True)
                count = 0
                for example in ds:
                    if count >= n_samples:
                        break
                    text = example.get('text', example.get('content', ''))
                    if len(text.split()) < 10:
                        continue
                    words = text.split()[:CONFIG["max_tokens"] * 2]
                    texts.append(' '.join(words))
                    labels.append(domain)
                    count += 1
            else:
                ds = load_dataset(ds_name, ds_config, split=split, trust_remote_code=True)
                indices = random.sample(range(len(ds)), min(n_samples, len(ds)))
                for idx in indices:
                    example = ds[idx]
                    text = example.get('text', example.get('article', example.get('question', '')))
                    if len(str(text).split()) < 10:
                        continue
                    words = str(text).split()[:CONFIG["max_tokens"] * 2]
                    texts.append(' '.join(words))
                    labels.append(domain)

        except Exception as e:
            print(f"Failed to load {domain}: {e}")
            continue

    print(f"Total loaded: {len(texts)} samples")
    return texts, labels


def load_pile_subset_synthetic(domains: list[str], n_samples: int, seed: int) -> tuple[list[str], list[str]]:
    """Fallback: create synthetic domain-distinguishable texts for PoC validation.

    Each domain gets characteristic vocabulary to test if embeddings can differentiate.
    """
    random.seed(seed)

    domain_vocab = {
        'arxiv': ['theorem', 'proof', 'lemma', 'equation', 'hypothesis', 'analysis', 'mathematical', 'derivation', 'convergence', 'optimization'],
        'pubmed': ['patient', 'treatment', 'clinical', 'diagnosis', 'symptoms', 'therapy', 'medical', 'disease', 'healthcare', 'pharmaceutical'],
        'wikipedia': ['history', 'country', 'population', 'government', 'culture', 'established', 'notable', 'century', 'region', 'organization'],
        'github': ['function', 'return', 'import', 'class', 'def', 'variable', 'loop', 'array', 'object', 'method'],
        'stackexchange': ['question', 'answer', 'solution', 'error', 'problem', 'help', 'code', 'working', 'trying', 'issue'],
        'books3': ['chapter', 'story', 'character', 'novel', 'narrative', 'dialogue', 'scene', 'author', 'plot', 'fiction'],
        'pile-cc': ['website', 'online', 'content', 'article', 'information', 'page', 'site', 'user', 'service', 'platform'],
        'openwebtext2': ['news', 'report', 'today', 'said', 'according', 'statement', 'official', 'announced', 'source', 'update'],
    }

    common_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'with', 'on', 'that', 'this', 'be', 'are', 'as', 'by', 'from', 'or', 'an', 'have']

    texts = []
    labels = []

    for domain in domains:
        vocab = domain_vocab.get(domain, common_words)
        for _ in range(n_samples):
            # Generate text with domain-specific vocabulary
            words = []
            for _ in range(100):
                if random.random() < 0.3:
                    words.append(random.choice(vocab))
                else:
                    words.append(random.choice(common_words))
            texts.append(' '.join(words))
            labels.append(domain)

    return texts, labels


def load_mmlu_validation() -> list[str]:
    """Load MMLU validation set as task exemplars."""
    ds = load_dataset(CONFIG["mmlu_source"], "all", split="validation")

    texts = []
    for example in ds:
        question = example['question']
        choices = example['choices']
        text = question + " " + " ".join(f"({chr(65+i)}) {c}" for i, c in enumerate(choices))
        texts.append(text)

    return texts


def cache_processed(domain_texts: list[str], domain_labels: list[str],
                    task_texts: list[str], path: str) -> None:
    """Cache processed data to JSON files."""
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "domain_texts.json"), "w") as f:
        json.dump(domain_texts, f)
    with open(os.path.join(path, "domain_labels.json"), "w") as f:
        json.dump(domain_labels, f)
    with open(os.path.join(path, "task_texts.json"), "w") as f:
        json.dump(task_texts, f)


def load_cached(path: str) -> tuple[list[str], list[str], list[str]] | None:
    """Load cached data if available."""
    domain_texts_path = os.path.join(path, "domain_texts.json")
    domain_labels_path = os.path.join(path, "domain_labels.json")
    task_texts_path = os.path.join(path, "task_texts.json")

    if not all(os.path.exists(p) for p in [domain_texts_path, domain_labels_path, task_texts_path]):
        return None

    with open(domain_texts_path) as f:
        domain_texts = json.load(f)
    with open(domain_labels_path) as f:
        domain_labels = json.load(f)
    with open(task_texts_path) as f:
        task_texts = json.load(f)

    return domain_texts, domain_labels, task_texts
