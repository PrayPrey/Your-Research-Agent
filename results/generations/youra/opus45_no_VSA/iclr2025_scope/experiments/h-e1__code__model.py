"""H-E1 Linear Probe Model - MiniLM + LogisticRegression"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from typing import Dict, List


class AdapterSelectionProbe:
    """Linear probe on frozen MiniLM embeddings for adapter/task selection."""

    def __init__(
        self,
        encoder_name: str,
        num_classes: int,
        max_iter: int = 2000,
        solver: str = "lbfgs",
        random_state: int = 42,
    ):
        self.encoder = SentenceTransformer(encoder_name)
        self.num_classes = num_classes
        self.classifier = LogisticRegression(
            max_iter=max_iter,
            solver=solver,
            multi_class="multinomial",
            random_state=random_state,
        )

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts with frozen MiniLM -> (N, 384)"""
        return self.encoder.encode(texts, show_progress_bar=True)

    def fit(self, texts: List[str], labels: List[int]) -> None:
        """Train linear probe on embeddings."""
        embeddings = self.encode(texts)
        self.classifier.fit(embeddings, labels)

    def predict(self, texts: List[str]) -> np.ndarray:
        """Predict class labels."""
        embeddings = self.encode(texts)
        return self.classifier.predict(embeddings)

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Predict class probabilities -> (N, num_classes)"""
        embeddings = self.encode(texts)
        return self.classifier.predict_proba(embeddings)

    def evaluate(self, texts: List[str], labels: List[int], k: int = 3) -> Dict[str, float]:
        """Compute top-1 and top-k accuracy."""
        embeddings = self.encode(texts)
        probs = self.classifier.predict_proba(embeddings)
        preds = self.classifier.predict(embeddings)

        top1_acc = accuracy_score(labels, preds)
        topk_acc = top_k_accuracy_score(
            labels, probs, k=min(k, self.num_classes), labels=list(range(self.num_classes))
        )

        return {"top1_accuracy": top1_acc, "top3_accuracy": topk_acc}
