import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm


class FormalityScorer:
    def __init__(self, model_name: str = "s-nlp/deberta-large-formality-ranker", device: str = "cuda"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
        self.model.eval()

    def score_batch(self, texts: list[str], batch_size: int = 64) -> list[float]:
        scores = []
        for i in tqdm(range(0, len(texts), batch_size), desc="Scoring formality"):
            batch = texts[i:i + batch_size]
            batch = [t[:512] if len(t) > 512 else t for t in batch]
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=-1)
                if probs.shape[1] == 2:
                    batch_scores = probs[:, 1].cpu().numpy()
                else:
                    batch_scores = probs[:, 0].cpu().numpy()
            scores.extend(batch_scores.tolist())
        return scores

    def load_cache(self, cache_path: str) -> dict | None:
        if os.path.exists(cache_path):
            import json
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None

    def save_cache(self, scores: dict, cache_path: str) -> None:
        import json
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w') as f:
            json.dump(scores, f)
