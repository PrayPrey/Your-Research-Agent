"""Baseline and proposed classifiers for instruction prefix classification."""
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer
from config import SEED, MODEL_NAME, LOGREG_PARAMS


class BaselineClassifier:
    """Random stratified classifier as baseline."""

    def __init__(self, seed: int = SEED):
        self.clf = DummyClassifier(strategy="stratified", random_state=seed)

    def fit(self, X_texts: list, y_labels: list) -> "BaselineClassifier":
        self.clf.fit(X_texts, y_labels)
        return self

    def predict(self, X_texts: list) -> np.ndarray:
        return self.clf.predict(X_texts)


class InstructionPrefixClassifier:
    """MiniLM encoder + LogisticRegression for linear probe."""

    def __init__(self, model_name: str = MODEL_NAME):
        self.encoder = SentenceTransformer(model_name)
        self.clf = LogisticRegression(**LOGREG_PARAMS)
        self._embeddings_cache = None

    def encode(self, texts: list) -> np.ndarray:
        """Encode texts to 384-dim embeddings."""
        return self.encoder.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    def fit(self, X_texts: list, y_labels: list) -> "InstructionPrefixClassifier":
        emb = self.encode(X_texts)
        self._embeddings_cache = emb
        self.clf.fit(emb, y_labels)
        return self

    def predict(self, X_texts: list) -> np.ndarray:
        emb = self.encode(X_texts)
        return self.clf.predict(emb)

    def get_train_embeddings(self) -> np.ndarray:
        """Return cached training embeddings for visualization."""
        return self._embeddings_cache
