"""Data curation pipeline: MinHash dedup + perplexity filter + domain resampling"""
from typing import List, Dict, Optional
import random
from datasketch import MinHash, MinHashLSH
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import numpy as np
from datasets import load_dataset


class DataCurator:
    """Applies curation transformations to C4 data"""

    def __init__(
        self,
        dedup_ratio: float,
        filter_level: int,
        domain_mix: int,
        seed: int = 42
    ):
        """
        Args:
            dedup_ratio: Target dedup (0.0=none, 0.95=aggressive)
            filter_level: 0=none, 1=median, 2=top25%
            domain_mix: 0=uniform, 1=quality_weighted
        """
        self.dedup_ratio = dedup_ratio
        self.filter_level = filter_level
        self.domain_mix = domain_mix
        self.seed = seed
        random.seed(seed)

        # Load perplexity model if filtering enabled
        if filter_level > 0:
            self.perplexity_model = GPT2LMHeadModel.from_pretrained("gpt2")
            self.perplexity_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            self.perplexity_model.eval()
            if torch.cuda.is_available():
                self.perplexity_model = self.perplexity_model.cuda()

    def deduplicate_minhash(
        self,
        texts: List[str],
        num_perm: int = 128,
        threshold: float = 0.8
    ) -> List[str]:
        """MinHash LSH dedup. Returns: texts * dedup_ratio"""
        if self.dedup_ratio == 0.0:
            return texts

        lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        unique = []

        for i, text in enumerate(texts):
            m = MinHash(num_perm=num_perm)
            for word in text.split():
                m.update(word.encode('utf8'))

            if not lsh.query(m):
                lsh.insert(f"doc_{i}", m)
                unique.append(text)

        # Target dedup ratio
        target_size = int(len(texts) * (1 - self.dedup_ratio))
        if len(unique) > target_size:
            unique = unique[:target_size]

        return unique

    def filter_by_perplexity(
        self,
        texts: List[str],
        threshold: Optional[float] = None
    ) -> List[str]:
        """Filter by GPT-2 perplexity. texts: [N] -> [N*filter_ratio]"""
        if self.filter_level == 0:
            return texts

        # Compute perplexities
        perplexities = []
        for text in texts:
            tokens = self.perplexity_tokenizer.encode(text, return_tensors="pt")
            if torch.cuda.is_available():
                tokens = tokens.cuda()

            with torch.no_grad():
                outputs = self.perplexity_model(tokens, labels=tokens)
                loss = outputs.loss.item()
                perplexity = np.exp(loss)

            perplexities.append(perplexity)

        # Determine threshold
        if threshold is None:
            if self.filter_level == 1:  # median
                threshold = np.median(perplexities)
            elif self.filter_level == 2:  # top25%
                threshold = np.percentile(perplexities, 25)

        # Filter
        filtered = [t for t, p in zip(texts, perplexities) if p < threshold]
        return filtered

    def resample_domains(
        self,
        texts: List[str],
        urls: List[str]
    ) -> List[str]:
        """Resample by domain quality. texts: [N] -> [N] (resampled)"""
        if self.domain_mix == 0:
            return texts

        # Extract domains
        domains = [url.split('/')[2] if '/' in url else url for url in urls]

        # Compute domain quality weights (inverse frequency)
        domain_counts = {}
        for d in domains:
            domain_counts[d] = domain_counts.get(d, 0) + 1

        weights = [1.0 / domain_counts[d] for d in domains]
        weights = np.array(weights) / sum(weights)

        # Weighted resample
        indices = np.random.choice(len(texts), size=len(texts), p=weights)
        return [texts[i] for i in indices]

    def curate_subset(
        self,
        c4_stream,
        target_gb: int = 50
    ) -> List[Dict[str, str]]:
        """Pipeline: stream -> dedup -> filter -> mix. Returns: [{"text": ..., "url": ...}]"""
        # Sample until target size
        texts, urls = [], []
        total_bytes = 0
        target_bytes = target_gb * 1024 * 1024 * 1024

        for sample in c4_stream:
            text = sample["text"]
            url = sample.get("url", "")
            texts.append(text)
            urls.append(url)
            total_bytes += len(text.encode('utf-8'))

            if total_bytes >= target_bytes:
                break

        print(f"Sampled {len(texts)} documents ({total_bytes/(1024**3):.2f} GB)")

        # Apply curation
        if self.dedup_ratio > 0:
            texts_dedup = self.deduplicate_minhash(texts)
            print(f"After dedup: {len(texts_dedup)} docs (ratio: {len(texts_dedup)/len(texts):.2f})")
            texts = texts_dedup

        if self.filter_level > 0:
            texts_filter = self.filter_by_perplexity(texts)
            print(f"After filter: {len(texts_filter)} docs")
            texts = texts_filter

        if self.domain_mix == 1:
            texts = self.resample_domains(texts, urls[:len(texts)])
            print(f"After domain mix: {len(texts)} docs")

        return [{"text": t, "url": u} for t, u in zip(texts, urls[:len(texts)])]


def generate_all_conditions(
    output_dir: str,
    base_config: Dict
) -> List[str]:
    """Generate 9 curated C4 subsets. Returns: List of JSONL file paths (one per condition)"""
    from config import CONFIG
    import os
    import json

    os.makedirs(output_dir, exist_ok=True)
    paths = []

    for cond in CONFIG.curation.conditions:
        print(f"\n{'='*60}")
        print(f"Generating condition: {cond.name}")
        print(f"  dedup={cond.dedup_ratio}, filter={cond.filter_level}, mix={cond.domain_mix}")
        print('='*60)

        curator = DataCurator(
            dedup_ratio=cond.dedup_ratio,
            filter_level=cond.filter_level,
            domain_mix=cond.domain_mix,
            seed=base_config.get("seed", 42)
        )

        c4_stream = load_dataset("allenai/c4", "en", split="train", streaming=True)
        curated = curator.curate_subset(c4_stream, target_gb=50)

        path = f"{output_dir}/condition_{cond.name}.jsonl"
        with open(path, 'w') as f:
            for item in curated:
                f.write(json.dumps(item) + '\n')

        print(f"Saved: {path} ({len(curated)} docs)")
        paths.append(path)

    return paths
