"""Contriever retrieval pipeline for provenance metadata generation"""

import torch
from transformers import AutoModel, AutoTokenizer
from typing import List, Tuple
import numpy as np

class ContrieverRetriever:
    def __init__(self, model_name: str = "facebook/contriever-msmarco", device: str = "cuda"):
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model.eval()

    def chunk_document(self, document: str, chunk_size: int = 512, overlap: int = 128) -> List[str]:
        """Split document into overlapping passages"""
        tokens = self.tokenizer.encode(document, add_special_tokens=False)
        passages = []
        for start in range(0, len(tokens), chunk_size - overlap):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            passages.append(self.tokenizer.decode(chunk_tokens, skip_special_tokens=True))
        return passages

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :]  # CLS pooling
        return embeddings.cpu().numpy()

    def retrieve(self, query: str, passages: List[str], top_k: int = 5) -> Tuple[List[str], List[float]]:
        """Retrieve top-K passages"""
        query_emb = self.encode([query])
        passage_embs = self.encode(passages)

        # Cosine similarity
        scores = (query_emb @ passage_embs.T).squeeze(0)
        scores = scores.tolist()

        # Min-max normalization
        min_score, max_score = min(scores), max(scores)
        if max_score > min_score:
            scores = [(s - min_score) / (max_score - min_score) for s in scores]
        else:
            scores = [0.0] * len(scores)

        # Top-K
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [passages[i] for i in top_indices], [scores[i] for i in top_indices]
