"""
Models for EmbedPrint data attribution.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, AutoModelForCausalLM, AutoConfig
from typing import Dict, Tuple, Optional
import numpy as np


class ProjectionHead(nn.Module):
    """Projection head to map embeddings to signature space."""

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SignatureBank(nn.Module):
    """Learnable signature vectors for clusters."""

    def __init__(self, num_clusters: int, signature_dim: int):
        super().__init__()
        self.num_clusters = num_clusters
        self.signature_dim = signature_dim

        # Initialize with orthogonal vectors
        self.signatures = nn.Parameter(torch.zeros(num_clusters, signature_dim))
        self._initialize_orthogonal()

    def _initialize_orthogonal(self):
        """Initialize signatures with orthogonal random projections."""
        # Use QR decomposition for orthogonal initialization
        max_dim = max(self.num_clusters, self.signature_dim)
        random_matrix = torch.randn(max_dim, max_dim)
        q, _ = torch.linalg.qr(random_matrix)
        init_signatures = q[: self.num_clusters, : self.signature_dim]
        self.signatures.data.copy_(init_signatures)

    def forward(self, cluster_ids: torch.Tensor) -> torch.Tensor:
        """Get signatures for given cluster IDs."""
        return self.signatures[cluster_ids]

    def get_all_signatures(self) -> torch.Tensor:
        """Get all signature vectors."""
        return self.signatures


class EmbedPrintModel(nn.Module):
    """
    EmbedPrint: Data attribution via embedding fingerprints.
    """

    def __init__(
        self,
        model_name: str,
        num_clusters: int,
        signature_dim: int = 64,
        projection_dim: int = 256,
        hidden_dim: int = 768,
    ):
        super().__init__()

        # Load pretrained language model
        self.config = AutoConfig.from_pretrained(model_name)
        self.lm = AutoModelForCausalLM.from_pretrained(model_name)

        # Get actual hidden dimension from model config
        if hasattr(self.config, "n_embd"):
            hidden_dim = self.config.n_embd
        elif hasattr(self.config, "hidden_size"):
            hidden_dim = self.config.hidden_size

        self.hidden_dim = hidden_dim
        self.num_clusters = num_clusters
        self.signature_dim = signature_dim

        # Projection head for fingerprint space
        self.projection = ProjectionHead(hidden_dim, projection_dim, signature_dim)

        # Learnable cluster signatures
        self.signature_bank = SignatureBank(num_clusters, signature_dim)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        cluster_ids: Optional[torch.Tensor] = None,
        return_attribution: bool = False,
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass with optional fingerprint loss computation.

        Args:
            input_ids: Token IDs [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, seq_len]
            cluster_ids: Ground truth cluster IDs [batch_size] (for training)
            return_attribution: Whether to return attribution scores

        Returns:
            Dictionary with loss, logits, and optionally attribution scores
        """
        # Language model forward pass
        outputs = self.lm(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
        )

        # Get last hidden state
        last_hidden = outputs.hidden_states[-1]  # [batch_size, seq_len, hidden_dim]

        # Pool to get sequence representation (mean pooling over non-padding tokens)
        mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
        sum_hidden = torch.sum(last_hidden * mask_expanded, dim=1)
        sum_mask = mask_expanded.sum(dim=1).clamp(min=1e-9)
        pooled = sum_hidden / sum_mask  # [batch_size, hidden_dim]

        # Project to signature space
        projected = self.projection(pooled)  # [batch_size, signature_dim]
        projected = F.normalize(projected, p=2, dim=-1)

        result = {
            "logits": outputs.logits,
            "hidden_states": pooled,
            "projected": projected,
        }

        # Compute LM loss
        # Shift for autoregressive loss
        shift_logits = outputs.logits[..., :-1, :].contiguous()
        shift_labels = input_ids[..., 1:].contiguous()
        lm_loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            ignore_index=-100,
        )
        result["lm_loss"] = lm_loss

        if cluster_ids is not None:
            # Compute fingerprint contrastive loss
            fp_loss = self._compute_fingerprint_loss(projected, cluster_ids)
            result["fp_loss"] = fp_loss

        if return_attribution:
            # Compute attribution scores
            all_signatures = self.signature_bank.get_all_signatures()  # [num_clusters, signature_dim]
            all_signatures = F.normalize(all_signatures, p=2, dim=-1)
            # Similarity to all clusters
            attribution_scores = torch.matmul(projected, all_signatures.T)  # [batch_size, num_clusters]
            result["attribution_scores"] = attribution_scores

        return result

    def _compute_fingerprint_loss(
        self, projected: torch.Tensor, cluster_ids: torch.Tensor, temperature: float = 0.07
    ) -> torch.Tensor:
        """
        Compute contrastive fingerprint loss.

        Args:
            projected: Projected embeddings [batch_size, signature_dim]
            cluster_ids: Cluster assignments [batch_size]
            temperature: Temperature for softmax

        Returns:
            Contrastive loss scalar
        """
        batch_size = projected.size(0)

        # Get all signatures
        all_signatures = self.signature_bank.get_all_signatures()  # [num_clusters, signature_dim]
        all_signatures = F.normalize(all_signatures, p=2, dim=-1)

        # Compute similarities to all clusters
        similarities = torch.matmul(projected, all_signatures.T) / temperature  # [batch_size, num_clusters]

        # Cross-entropy loss with cluster_ids as targets
        loss = F.cross_entropy(similarities, cluster_ids)

        return loss

    def get_attribution(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Get attribution scores for inputs."""
        with torch.no_grad():
            result = self.forward(input_ids, attention_mask, return_attribution=True)
        return result["attribution_scores"]


class BaselineEmbeddingModel(nn.Module):
    """Simple embedding-based attribution baseline."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__()
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self.train_embeddings = None
        self.train_cluster_ids = None

    def fit(self, texts: list, cluster_ids: np.ndarray):
        """Store training data embeddings."""
        self.train_embeddings = self.model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
        self.train_embeddings = F.normalize(self.train_embeddings, p=2, dim=-1)
        self.train_cluster_ids = torch.tensor(cluster_ids, dtype=torch.long)

    def get_attribution(self, texts: list, top_k: int = 10) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get top-k most similar training samples for attribution."""
        query_embeddings = self.model.encode(texts, convert_to_tensor=True)
        query_embeddings = F.normalize(query_embeddings, p=2, dim=-1)

        # Compute similarities
        similarities = torch.matmul(query_embeddings, self.train_embeddings.T)

        # Get top-k
        top_scores, top_indices = torch.topk(similarities, k=top_k, dim=-1)

        return top_indices, top_scores
