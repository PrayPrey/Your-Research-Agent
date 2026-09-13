import numpy as np
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN

import hc1_config as config


class AgencyPatternClusterer:
    """Cluster disagreement responses and identify agency-preserving patterns."""

    def __init__(self, min_cluster_size=None):
        if min_cluster_size is None:
            min_cluster_size = config.MIN_CLUSTER_SIZE

        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        self.umap_model = UMAP(
            n_neighbors=config.UMAP_N_NEIGHBORS,
            n_components=config.UMAP_N_COMPONENTS,
            metric=config.UMAP_METRIC,
            random_state=config.RANDOM_STATE,
        )
        self.hdbscan_model = HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric=config.HDBSCAN_METRIC,
            cluster_selection_method=config.HDBSCAN_SELECTION_METHOD,
            prediction_data=True,
        )
        self.topic_model = BERTopic(
            embedding_model=self.embedding_model,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan_model,
            top_n_words=config.TOP_N_WORDS,
            calculate_probabilities=True,
        )
        self._embeddings = None

    def fit_transform(self, texts):
        """Cluster texts and return (topics, probs)."""
        print(f"Generating embeddings for {len(texts)} texts...")
        self._embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        print("Fitting BERTopic...")
        topics, probs = self.topic_model.fit_transform(texts, embeddings=self._embeddings)

        n_topics = len(set(topics)) - (1 if -1 in topics else 0)
        print(f"Discovered {n_topics} topics (excluding noise)")

        return topics, probs

    def get_topic_info(self):
        """Get interpretable topic descriptions."""
        return self.topic_model.get_topic_info()

    def get_topic_keywords(self, topic_id):
        """Get top keywords for a topic as list of (word, score) tuples."""
        topic = self.topic_model.get_topic(topic_id)
        if topic is None or topic == False:
            return []
        return topic

    def get_representative_docs(self, topic_id, n=5):
        """Get representative documents for a topic."""
        docs = self.topic_model.get_representative_docs(topic_id)
        if docs is None:
            return []
        return docs[:n]

    @property
    def topic_embeddings_(self):
        """Get topic embeddings (centroids)."""
        return self.topic_model.topic_embeddings_

    @property
    def embeddings(self):
        """Get document embeddings."""
        return self._embeddings
