from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
import numpy as np
from typing import List, Dict


class ClusteringPipeline:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', n_clusters: int = 4,
                 random_state: int = 42, max_iter: int = 300, n_init: int = 10):
        """Initialize SentenceBERT + k-means pipeline."""
        self.model = SentenceTransformer(model_name)
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.max_iter = max_iter
        self.n_init = n_init
        self.kmeans = None

    def embed(self, descriptions: List[str], normalize_l2: bool = True) -> np.ndarray:
        """Encode descriptions. descriptions: 20 → [20, 384]"""
        embeddings = self.model.encode(descriptions, show_progress_bar=False)

        # L2 normalization for better cosine similarity
        if normalize_l2:
            embeddings = normalize(embeddings, norm='l2')

        # Validate dimensions
        if embeddings.shape[1] != 384:
            raise ValueError(f"Expected embedding dim 384, got {embeddings.shape[1]}")

        return embeddings

    def cluster(self, embeddings: np.ndarray) -> np.ndarray:
        """K-means clustering. [20, 384] → [20,] cluster labels"""
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            max_iter=self.max_iter,
            n_init=self.n_init
        )
        labels = self.kmeans.fit_predict(embeddings)

        # Check no singleton clusters
        unique, counts = np.unique(labels, return_counts=True)
        singletons = unique[counts < 2]
        if len(singletons) > 0:
            print(f"WARNING: Singleton clusters found: {singletons}")

        return labels

    def run(self, descriptions: List[str], normalize_l2: bool = True) -> Dict:
        """End-to-end pipeline. Returns: {embeddings, labels, centroids}"""
        embeddings = self.embed(descriptions, normalize_l2)
        labels = self.cluster(embeddings)

        return {
            'embeddings': embeddings,
            'labels': labels,
            'centroids': self.kmeans.cluster_centers_
        }
