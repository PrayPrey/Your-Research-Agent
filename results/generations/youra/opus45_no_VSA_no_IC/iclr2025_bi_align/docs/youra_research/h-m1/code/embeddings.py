"""Embedding computation with sentence-transformers."""

import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from config import CONFIG


def get_model(device: str = None) -> SentenceTransformer:
    """Load embedding model."""
    model = SentenceTransformer(CONFIG["embedding_model"], device=device)
    return model


def compute_embeddings(texts: list[str], model: SentenceTransformer) -> np.ndarray:
    """Encode texts to embeddings. Returns [N, 384] array."""
    embeddings = model.encode(
        texts,
        batch_size=CONFIG["batch_size"],
        show_progress_bar=True,
        convert_to_numpy=True,
    )
    return embeddings


def compute_pairwise_similarity(emb_a: np.ndarray, emb_b: np.ndarray) -> np.ndarray:
    """Row-wise cosine similarity. Returns [N] array in [-1, 1]."""
    norm_a = np.linalg.norm(emb_a, axis=1, keepdims=True)
    norm_b = np.linalg.norm(emb_b, axis=1, keepdims=True)
    emb_a_normed = emb_a / (norm_a + 1e-8)
    emb_b_normed = emb_b / (norm_b + 1e-8)
    similarity = np.sum(emb_a_normed * emb_b_normed, axis=1)
    return similarity


def save_embeddings(path, emb_a: np.ndarray, emb_b: np.ndarray, battle_ids: np.ndarray):
    """Save embeddings to npz."""
    np.savez(path, emb_a=emb_a, emb_b=emb_b, battle_id=battle_ids)
    print(f"Saved embeddings to {path}")


def load_embeddings(path) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """Load cached embeddings if exists."""
    if not path.exists():
        return None
    data = np.load(path)
    return data["emb_a"], data["emb_b"], data["battle_id"]
