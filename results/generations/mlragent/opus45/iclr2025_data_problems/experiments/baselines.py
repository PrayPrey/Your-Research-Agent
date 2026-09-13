"""
Baseline methods for data attribution comparison.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Tuple, Dict, Optional
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TracInAttributor:
    """
    TracIn: Gradient dot-product attribution across checkpoints.
    Simplified implementation for efficiency.
    """

    def __init__(self, model, device: str = "cuda"):
        self.model = model
        self.device = device
        self.gradients_cache = {}
        self.checkpoints = []

    def save_checkpoint(self, epoch: int):
        """Save model checkpoint for TracIn computation."""
        checkpoint = {k: v.clone().detach() for k, v in self.model.named_parameters() if v.requires_grad}
        self.checkpoints.append({"epoch": epoch, "params": checkpoint})
        logger.info(f"Saved checkpoint at epoch {epoch}")

    def compute_sample_gradient(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        sample_idx: int,
    ) -> Dict[str, torch.Tensor]:
        """Compute gradient for a single sample."""
        self.model.zero_grad()

        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Compute loss for this sample
        shift_logits = outputs.logits[..., :-1, :].contiguous()
        shift_labels = input_ids[..., 1:].contiguous()
        loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            ignore_index=-100,
        )

        loss.backward()

        # Store gradients
        gradients = {}
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                gradients[name] = param.grad.clone().detach()

        return gradients

    def compute_attribution(
        self,
        query_ids: torch.Tensor,
        query_mask: torch.Tensor,
        train_loader,
        num_samples: int = 100,
    ) -> np.ndarray:
        """
        Compute TracIn attribution scores.

        Args:
            query_ids: Query input IDs
            query_mask: Query attention mask
            train_loader: DataLoader with training samples
            num_samples: Number of training samples to consider

        Returns:
            Attribution scores for each training sample
        """
        # Compute query gradient
        query_grad = self.compute_sample_gradient(query_ids, query_mask, -1)

        # Compute dot products with training gradients
        attribution_scores = []
        sample_count = 0

        for batch in tqdm(train_loader, desc="Computing TracIn"):
            if sample_count >= num_samples:
                break

            for i in range(batch["input_ids"].size(0)):
                if sample_count >= num_samples:
                    break

                train_ids = batch["input_ids"][i : i + 1].to(self.device)
                train_mask = batch["attention_mask"][i : i + 1].to(self.device)

                train_grad = self.compute_sample_gradient(train_ids, train_mask, sample_count)

                # Compute dot product
                dot_product = 0.0
                for name in query_grad:
                    if name in train_grad:
                        dot_product += torch.sum(query_grad[name] * train_grad[name]).item()

                attribution_scores.append(dot_product)
                sample_count += 1

        return np.array(attribution_scores)


class InfluenceFunctionAttributor:
    """
    Simplified Influence Function attribution.
    Uses first-order approximation for efficiency.
    """

    def __init__(self, model, device: str = "cuda"):
        self.model = model
        self.device = device

    def compute_hvp(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        vector: Dict[str, torch.Tensor],
        damping: float = 0.01,
    ) -> Dict[str, torch.Tensor]:
        """Compute Hessian-vector product approximation."""
        self.model.zero_grad()

        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        shift_logits = outputs.logits[..., :-1, :].contiguous()
        shift_labels = input_ids[..., 1:].contiguous()
        loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            ignore_index=-100,
        )

        # First order gradient
        grads = torch.autograd.grad(loss, [p for p in self.model.parameters() if p.requires_grad], create_graph=True)

        # HVP approximation via finite differences
        hvp = {}
        for (name, param), grad in zip(
            [(n, p) for n, p in self.model.named_parameters() if p.requires_grad], grads
        ):
            if name in vector:
                hvp[name] = grad + damping * vector[name]

        return hvp

    def compute_attribution(
        self,
        query_ids: torch.Tensor,
        query_mask: torch.Tensor,
        train_loader,
        num_samples: int = 100,
        recursion_depth: int = 5,
    ) -> np.ndarray:
        """
        Compute influence function attribution scores.
        """
        # Compute query gradient
        self.model.zero_grad()
        outputs = self.model(input_ids=query_ids, attention_mask=query_mask)
        shift_logits = outputs.logits[..., :-1, :].contiguous()
        shift_labels = query_ids[..., 1:].contiguous()
        query_loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            ignore_index=-100,
        )
        query_loss.backward()

        query_grad = {}
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                query_grad[name] = param.grad.clone().detach()

        # Simplified: Use gradient dot product (first-order approximation)
        attribution_scores = []
        sample_count = 0

        for batch in tqdm(train_loader, desc="Computing Influence"):
            if sample_count >= num_samples:
                break

            for i in range(batch["input_ids"].size(0)):
                if sample_count >= num_samples:
                    break

                train_ids = batch["input_ids"][i : i + 1].to(self.device)
                train_mask = batch["attention_mask"][i : i + 1].to(self.device)

                self.model.zero_grad()
                outputs = self.model(input_ids=train_ids, attention_mask=train_mask)
                shift_logits = outputs.logits[..., :-1, :].contiguous()
                shift_labels = train_ids[..., 1:].contiguous()
                train_loss = F.cross_entropy(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1),
                    ignore_index=-100,
                )
                train_loss.backward()

                # Compute negative gradient dot product
                score = 0.0
                for name, param in self.model.named_parameters():
                    if param.grad is not None and name in query_grad:
                        score -= torch.sum(query_grad[name] * param.grad).item()

                attribution_scores.append(score)
                sample_count += 1

        return np.array(attribution_scores)


class TRAKAttributor:
    """
    TRAK: Data attribution via random projections.
    Simplified implementation.
    """

    def __init__(self, model, projection_dim: int = 512, device: str = "cuda"):
        self.model = model
        self.device = device
        self.projection_dim = projection_dim
        self.projection_matrix = None
        self.train_projections = None

    def _get_gradient_vector(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Get flattened gradient vector for a sample."""
        self.model.zero_grad()

        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        shift_logits = outputs.logits[..., :-1, :].contiguous()
        shift_labels = input_ids[..., 1:].contiguous()
        loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            ignore_index=-100,
        )
        loss.backward()

        # Flatten all gradients
        grad_vector = []
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                grad_vector.append(param.grad.view(-1))

        return torch.cat(grad_vector)

    def fit(self, train_loader, num_samples: int = 100):
        """Compute projected gradients for training samples."""
        # First pass to determine gradient dimension
        sample_batch = next(iter(train_loader))
        sample_ids = sample_batch["input_ids"][0:1].to(self.device)
        sample_mask = sample_batch["attention_mask"][0:1].to(self.device)

        with torch.enable_grad():
            grad_vector = self._get_gradient_vector(sample_ids, sample_mask)
        grad_dim = grad_vector.size(0)

        # Initialize random projection matrix
        self.projection_matrix = torch.randn(grad_dim, self.projection_dim, device=self.device)
        self.projection_matrix = self.projection_matrix / np.sqrt(self.projection_dim)

        # Compute projected gradients for training samples
        projections = []
        sample_count = 0

        for batch in tqdm(train_loader, desc="Computing TRAK projections"):
            if sample_count >= num_samples:
                break

            for i in range(batch["input_ids"].size(0)):
                if sample_count >= num_samples:
                    break

                train_ids = batch["input_ids"][i : i + 1].to(self.device)
                train_mask = batch["attention_mask"][i : i + 1].to(self.device)

                with torch.enable_grad():
                    grad_vector = self._get_gradient_vector(train_ids, train_mask)

                projected = torch.matmul(grad_vector, self.projection_matrix)
                projections.append(projected.detach())
                sample_count += 1

        self.train_projections = torch.stack(projections)
        logger.info(f"TRAK: Stored {len(projections)} training projections")

    def compute_attribution(
        self,
        query_ids: torch.Tensor,
        query_mask: torch.Tensor,
    ) -> np.ndarray:
        """Compute TRAK attribution scores."""
        if self.train_projections is None:
            raise ValueError("Must call fit() first")

        with torch.enable_grad():
            query_grad = self._get_gradient_vector(query_ids, query_mask)

        query_projected = torch.matmul(query_grad, self.projection_matrix)

        # Compute similarities
        similarities = torch.matmul(self.train_projections, query_projected)

        return similarities.cpu().numpy()


class EmbeddingSimilarityAttributor:
    """Simple embedding-based attribution using pretrained embeddings."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "cuda"):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, device=device)
        self.device = device
        self.train_embeddings = None
        self.train_cluster_ids = None

    def fit(self, texts: List[str], cluster_ids: np.ndarray):
        """Store training data embeddings."""
        self.train_embeddings = self.model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
        self.train_embeddings = F.normalize(self.train_embeddings, p=2, dim=-1)
        self.train_cluster_ids = torch.tensor(cluster_ids, dtype=torch.long, device=self.device)

    def compute_attribution(self, texts: List[str], top_k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Get attribution scores based on embedding similarity."""
        query_embeddings = self.model.encode(texts, convert_to_tensor=True)
        query_embeddings = F.normalize(query_embeddings, p=2, dim=-1)

        # Compute similarities
        similarities = torch.matmul(query_embeddings, self.train_embeddings.T)

        return similarities.cpu().numpy()

    def get_cluster_attribution(self, texts: List[str], num_clusters: int) -> np.ndarray:
        """Get cluster-level attribution scores."""
        similarities = self.compute_attribution(texts)

        # Aggregate by cluster
        cluster_scores = np.zeros((len(texts), num_clusters))
        for i in range(num_clusters):
            mask = self.train_cluster_ids.cpu().numpy() == i
            if mask.sum() > 0:
                cluster_scores[:, i] = similarities[:, mask].mean(axis=1)

        return cluster_scores
