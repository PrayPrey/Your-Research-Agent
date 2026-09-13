"""
Disagreement-Based Uncertainty Quantification
Analyzes response disagreement patterns to estimate uncertainty
"""
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')


class DisagreementAnalyzer:
    """Analyze disagreement patterns across model responses"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize with sentence transformer for embeddings
        Using a smaller, efficient model for semantic similarity
        """
        print(f"Loading sentence transformer: {model_name}")
        self.encoder = SentenceTransformer(model_name)
        print("Sentence transformer loaded")

    def compute_embeddings(self, responses: List[str]) -> np.ndarray:
        """Compute semantic embeddings for responses"""
        try:
            embeddings = self.encoder.encode(responses, show_progress_bar=False)
            return embeddings
        except Exception as e:
            print(f"Error computing embeddings: {e}")
            # Return random embeddings as fallback
            return np.random.randn(len(responses), 384)

    def compute_semantic_dispersion(self, embeddings: np.ndarray) -> float:
        """
        Compute semantic dispersion score
        Higher score indicates more disagreement
        """
        if len(embeddings) < 2:
            return 0.0

        # Compute pairwise cosine similarities
        similarities = cosine_similarity(embeddings)

        # Average similarity across all pairs (excluding diagonal)
        n = len(embeddings)
        avg_similarity = (similarities.sum() - n) / (n * (n - 1))

        # Dispersion is 1 - average similarity
        dispersion = 1.0 - avg_similarity
        return float(dispersion)

    def compute_cluster_diversity(self, embeddings: np.ndarray, n_clusters: int = 3) -> float:
        """
        Compute cluster-based diversity score
        Higher score indicates responses fall into multiple distinct clusters
        """
        if len(embeddings) < 2:
            return 0.0

        try:
            # Use fewer clusters if we have fewer samples
            n_clusters = min(n_clusters, len(embeddings))

            if n_clusters < 2:
                return 0.0

            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)

            # Compute size of largest cluster
            unique, counts = np.unique(labels, return_counts=True)
            max_cluster_size = counts.max()

            # Diversity is 1 - (max_cluster_size / total)
            diversity = 1.0 - (max_cluster_size / len(embeddings))
            return float(diversity)

        except Exception as e:
            print(f"Error in clustering: {e}")
            return 0.0

    def compute_length_variance(self, responses: List[str]) -> float:
        """
        Compute coefficient of variation for response lengths
        Higher score indicates more variance in response lengths
        """
        if len(responses) < 2:
            return 0.0

        lengths = [len(r.split()) for r in responses]
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)

        if mean_length == 0:
            return 0.0

        # Coefficient of variation
        cv = std_length / mean_length
        return float(cv)

    def analyze_responses(self, responses: List[Dict]) -> Dict:
        """
        Analyze a set of responses and compute disagreement metrics
        """
        # Extract response texts
        response_texts = [r['response'] for r in responses if not r.get('error', False)]

        if len(response_texts) < 2:
            return {
                'semantic_dispersion': 0.0,
                'cluster_diversity': 0.0,
                'length_variance': 0.0,
                'n_responses': len(response_texts),
                'embeddings': None,
            }

        # Compute embeddings
        embeddings = self.compute_embeddings(response_texts)

        # Compute metrics
        semantic_dispersion = self.compute_semantic_dispersion(embeddings)
        cluster_diversity = self.compute_cluster_diversity(embeddings)
        length_variance = self.compute_length_variance(response_texts)

        return {
            'semantic_dispersion': semantic_dispersion,
            'cluster_diversity': cluster_diversity,
            'length_variance': length_variance,
            'n_responses': len(response_texts),
            'embeddings': embeddings,
            'centroid': np.mean(embeddings, axis=0) if len(embeddings) > 0 else None,
        }

    def compute_composite_uncertainty(self, metrics: Dict,
                                      weights: Dict = None) -> float:
        """
        Combine disagreement metrics into composite uncertainty score
        """
        if weights is None:
            # Default weights
            weights = {
                'semantic_dispersion': 0.4,
                'cluster_diversity': 0.3,
                'length_variance': 0.3,
            }

        uncertainty = (
                weights['semantic_dispersion'] * metrics['semantic_dispersion'] +
                weights['cluster_diversity'] * metrics['cluster_diversity'] +
                weights['length_variance'] * metrics['length_variance']
        )

        return float(uncertainty)

    def batch_analyze(self, response_dict: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """
        Analyze multiple questions' responses
        Returns dict mapping question to analysis results
        """
        results = {}

        for idx, (question, responses) in enumerate(response_dict.items()):
            if (idx + 1) % 10 == 0:
                print(f"  Analyzed {idx + 1}/{len(response_dict)} questions")

            analysis = self.analyze_responses(responses)
            uncertainty = self.compute_composite_uncertainty(analysis)
            analysis['composite_uncertainty'] = uncertainty

            results[question] = analysis

        print(f"  Analyzed {len(response_dict)} questions total")
        return results
