"""Quality metrics computation (Q(D) components)."""
from typing import List, Dict
from collections import Counter
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import json
import math
import re

class QualityMetricsComputer:
    def __init__(self, model_name: str = "gpt2", device: str = "cuda"):
        """Load GPT-2 for perplexity."""
        self.model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model.eval()
        self.device = device

    def compute_dedup_ratio(self, texts: List[str], ngram_size: int = 13) -> float:
        """Returns: 1 - (unique_ngrams / total_ngrams)."""
        ngrams = []
        for text in texts:
            tokens = text.split()
            ngrams.extend([tuple(tokens[i:i+ngram_size]) for i in range(len(tokens)-ngram_size+1)])

        total_ngrams = len(ngrams)
        unique_ngrams = len(set(ngrams))

        return 1 - (unique_ngrams / total_ngrams) if total_ngrams > 0 else 0.0

    def compute_domain_diversity(self, urls: List[str]) -> float:
        """HHI-based diversity. Returns: 1 - HHI."""
        from urllib.parse import urlparse

        domains = [urlparse(url).netloc for url in urls if url]
        domain_counts = Counter(domains)
        total = sum(domain_counts.values())

        if total == 0:
            return 0.0

        shares = [count / total for count in domain_counts.values()]
        hhi = sum(share ** 2 for share in shares)

        return 1 - hhi

    def compute_perplexity(self, texts: List[str], batch_size: int = 128) -> float:
        """Batched GPT-2 perplexity. Returns: mean perplexity."""
        perplexities = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            for text in batch:
                inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
                with torch.no_grad():
                    outputs = self.model(**inputs, labels=inputs["input_ids"])
                    perplexity = torch.exp(outputs.loss).item()
                perplexities.append(perplexity)

        return sum(perplexities) / len(perplexities) if perplexities else 0.0

    def compute_token_efficiency(self, texts: List[str]) -> float:
        """Returns: semantic_tokens / total_tokens."""
        from nltk.corpus import stopwords

        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            import nltk
            nltk.download('stopwords')
            stop_words = set(stopwords.words('english'))

        total_tokens = 0
        semantic_tokens = 0

        for text in texts:
            clean_text = re.sub(r'[^\w\s]', '', text.lower())
            tokens = clean_text.split()

            total_tokens += len(tokens)
            semantic_tokens += sum(1 for token in tokens if token not in stop_words)

        return semantic_tokens / total_tokens if total_tokens > 0 else 0.0

    def compute_all(self, subset_path: str) -> Dict[str, float]:
        """Compute all 4 metrics. Returns: {'dedup': ..., 'diversity': ..., ...}"""
        texts = []
        urls = []

        with open(subset_path, 'r') as f:
            for line in f:
                sample = json.loads(line)
                texts.append(sample["text"])
                urls.append(sample.get("url", ""))

        return {
            "dedup": self.compute_dedup_ratio(texts),
            "diversity": self.compute_domain_diversity(urls),
            "perplexity": self.compute_perplexity(texts),
            "efficiency": self.compute_token_efficiency(texts)
        }
