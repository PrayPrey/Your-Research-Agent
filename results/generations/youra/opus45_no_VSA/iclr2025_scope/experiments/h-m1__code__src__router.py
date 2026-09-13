"""IPCR Router: Instruction-Prefix-Conditioned Routing via linear probe."""
import torch
import torch.nn as nn
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer

class IPCRRouter:
    """Routes instructions to task-specific LoRA adapters using frozen MiniLM + linear probe."""

    def __init__(
        self,
        encoder_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        adapter_names: Optional[List[str]] = None,
        embedding_dim: int = 384,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.device = device
        self.encoder = SentenceTransformer(encoder_name, device=device)
        self.encoder.eval()
        for param in self.encoder.parameters():
            param.requires_grad = False

        self.adapter_names = adapter_names or []
        self.num_adapters = len(self.adapter_names)
        self.embedding_dim = embedding_dim
        self.probe: Optional[nn.Linear] = None

    def set_adapter_names(self, names: List[str]) -> None:
        """Set adapter names and reinitialize probe if needed."""
        self.adapter_names = names
        self.num_adapters = len(names)
        if self.probe is not None and self.probe.out_features != self.num_adapters:
            self.probe = None

    def fit(self, embeddings: np.ndarray, labels: np.ndarray, epochs: int = 100, lr: float = 0.01) -> float:
        """Train linear probe on embeddings -> adapter labels."""
        self.probe = nn.Linear(self.embedding_dim, self.num_adapters).to(self.device)
        X = torch.tensor(embeddings, dtype=torch.float32, device=self.device)
        y = torch.tensor(labels, dtype=torch.long, device=self.device)

        optimizer = torch.optim.Adam(self.probe.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()

        self.probe.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            logits = self.probe(X)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

        self.probe.eval()
        with torch.no_grad():
            preds = self.probe(X).argmax(dim=1)
            accuracy = (preds == y).float().mean().item()
        return accuracy

    def fit_from_instructions(
        self, instructions: List[str], adapter_labels: List[int], epochs: int = 100
    ) -> float:
        """Train probe from raw instructions."""
        embeddings = self.encoder.encode(instructions, convert_to_numpy=True)
        labels = np.array(adapter_labels)
        return self.fit(embeddings, labels, epochs)

    @torch.no_grad()
    def route(self, instruction: str) -> str:
        """Route single instruction to best adapter."""
        if self.probe is None:
            raise RuntimeError("Probe not trained. Call fit() first.")
        embedding = self.encoder.encode([instruction], convert_to_numpy=False)
        if isinstance(embedding, np.ndarray):
            embedding = torch.tensor(embedding, device=self.device)
        logits = self.probe(embedding.to(self.device))
        idx = logits.argmax(dim=1).item()
        return self.adapter_names[idx]

    @torch.no_grad()
    def route_batch(self, instructions: List[str]) -> List[str]:
        """Route batch of instructions."""
        if self.probe is None:
            raise RuntimeError("Probe not trained. Call fit() first.")
        embeddings = self.encoder.encode(instructions, convert_to_numpy=False)
        if isinstance(embeddings, np.ndarray):
            embeddings = torch.tensor(embeddings, device=self.device)
        logits = self.probe(embeddings.to(self.device))
        indices = logits.argmax(dim=1).tolist()
        return [self.adapter_names[i] for i in indices]

    @torch.no_grad()
    def route_topk(self, instruction: str, k: int = 3) -> List[str]:
        """Return top-k adapter predictions."""
        if self.probe is None:
            raise RuntimeError("Probe not trained. Call fit() first.")
        embedding = self.encoder.encode([instruction], convert_to_numpy=False)
        if isinstance(embedding, np.ndarray):
            embedding = torch.tensor(embedding, device=self.device)
        logits = self.probe(embedding.to(self.device))
        topk_indices = logits.topk(k, dim=1).indices[0].tolist()
        return [self.adapter_names[i] for i in topk_indices]

    @torch.no_grad()
    def get_confidence(self, instruction: str) -> float:
        """Return confidence (softmax probability) of top prediction."""
        if self.probe is None:
            raise RuntimeError("Probe not trained. Call fit() first.")
        embedding = self.encoder.encode([instruction], convert_to_numpy=False)
        if isinstance(embedding, np.ndarray):
            embedding = torch.tensor(embedding, device=self.device)
        logits = self.probe(embedding.to(self.device))
        probs = torch.softmax(logits, dim=1)
        return probs.max().item()

    def save(self, path: str) -> None:
        """Save probe weights."""
        if self.probe is None:
            raise RuntimeError("No probe to save.")
        state = {
            "probe_state_dict": self.probe.state_dict(),
            "adapter_names": self.adapter_names,
            "embedding_dim": self.embedding_dim,
        }
        torch.save(state, path)

    def load(self, path: str) -> None:
        """Load probe weights."""
        state = torch.load(path, map_location=self.device)
        self.adapter_names = state["adapter_names"]
        self.num_adapters = len(self.adapter_names)
        self.embedding_dim = state["embedding_dim"]
        self.probe = nn.Linear(self.embedding_dim, self.num_adapters).to(self.device)
        self.probe.load_state_dict(state["probe_state_dict"])
        self.probe.eval()
