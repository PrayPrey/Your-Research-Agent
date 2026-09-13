"""IFR (Influence Fragility Ratio) computation"""
import numpy as np
from scipy.stats import spearmanr
from sklearn.neighbors import NearestNeighbors


class IFRComputer:
    def __init__(self, embeddings: np.ndarray, trak_scores: np.ndarray, k: int = 50):
        self.embeddings = embeddings
        self.trak_scores = trak_scores
        self.k = k
        self.nn = NearestNeighbors(n_neighbors=k + 1, metric='cosine')
        self.nn.fit(embeddings)

    def compute_redundancy(self) -> np.ndarray:
        distances, _ = self.nn.kneighbors(self.embeddings)
        redundancy = 1 - distances[:, 1:].mean(axis=1)
        return redundancy

    def compute_ifr(self, redundancy: np.ndarray, epsilon: float = 0.01) -> np.ndarray:
        replaceability = np.maximum(1 - redundancy, epsilon)
        ifr = np.abs(self.trak_scores) / replaceability
        return ifr

    def compute_correlation(self, ifr: np.ndarray, redundancy: np.ndarray) -> tuple:
        rho, pvalue = spearmanr(ifr, redundancy)
        return rho, pvalue


def extract_embeddings(model, tokenizer, texts: list, batch_size: int = 32, max_length: int = 512) -> np.ndarray:
    import torch
    model.eval()
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
            last_hidden = outputs.hidden_states[-1]
            attention_mask = inputs["attention_mask"].unsqueeze(-1)
            pooled = (last_hidden * attention_mask).sum(1) / attention_mask.sum(1)
            embeddings.append(pooled.cpu().numpy())

    return np.concatenate(embeddings, axis=0)
