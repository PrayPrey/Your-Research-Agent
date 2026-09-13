"""E5-large embedding model and similarity computation for h-e1."""

import torch
from torch import Tensor
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from config import CONFIG


def load_embedder(model_name: str = None) -> SentenceTransformer:
    """Load E5-large-v2 via sentence-transformers."""
    if model_name is None:
        model_name = CONFIG["model_name"]
    return SentenceTransformer(model_name)


def embed_domains(model: SentenceTransformer, texts: list[str], batch_size: int = None) -> Tensor:
    """Embed domain samples with 'passage: ' prefix, L2-normalized."""
    if batch_size is None:
        batch_size = CONFIG["batch_size"]

    prefixed = [CONFIG["passage_prefix"] + t for t in texts]
    embeddings = model.encode(prefixed, batch_size=batch_size, convert_to_tensor=True, show_progress_bar=True)
    return F.normalize(embeddings, p=2, dim=1)


def embed_tasks(model: SentenceTransformer, texts: list[str], batch_size: int = None) -> Tensor:
    """Embed task exemplars with 'query: ' prefix, L2-normalized."""
    if batch_size is None:
        batch_size = CONFIG["batch_size"]

    prefixed = [CONFIG["query_prefix"] + t for t in texts]
    embeddings = model.encode(prefixed, batch_size=batch_size, convert_to_tensor=True, show_progress_bar=True)
    return F.normalize(embeddings, p=2, dim=1)


def random_baseline_embeddings(n: int, dim: int = 1024, seed: int = 42) -> Tensor:
    """Generate random unit vectors as baseline embeddings."""
    torch.manual_seed(seed)
    emb = torch.randn(n, dim)
    return F.normalize(emb, p=2, dim=1)


def compute_domain_scores(domain_emb: Tensor, task_emb: Tensor,
                          domain_labels: list[str]) -> dict[str, float]:
    """Compute per-domain mean similarity scores.

    1. Compute cosine similarity matrix [N_d, N_t] via dot product (pre-normalized)
    2. Mean per sample (across tasks)
    3. Mean per domain
    """
    # [N_d, N_t]
    sim_matrix = domain_emb @ task_emb.T

    # Mean similarity per domain sample
    per_sample_mean = sim_matrix.mean(dim=1)  # [N_d]

    # Group by domain
    domains = CONFIG["domains"]
    domain_scores = {}

    for domain in domains:
        mask = torch.tensor([l == domain for l in domain_labels])
        if mask.sum() > 0:
            domain_scores[domain] = per_sample_mean[mask].mean().item()

    return domain_scores
