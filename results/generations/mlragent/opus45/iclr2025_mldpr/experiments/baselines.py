"""
Baseline methods for comparison with DDHS.
Implements various alternative approaches to dataset health scoring.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_predict
import warnings

from data_generator import DatasetMetadata


class DownloadsOnlyBaseline:
    """
    Simple baseline that uses only download counts to rank datasets.
    Common heuristic in practice - popular datasets are assumed to be good.
    """

    def __init__(self, normalize: bool = True):
        self.normalize = normalize
        self.max_downloads = 1

    def fit(self, datasets: List[DatasetMetadata]):
        """Fit the normalizer based on max downloads"""
        self.max_downloads = max(1, max(d.total_downloads for d in datasets))

    def compute(self, dataset: DatasetMetadata) -> float:
        """Compute score based on downloads"""
        score = dataset.total_downloads / self.max_downloads
        return float(np.clip(score, 0, 1))

    def evaluate_repository(
        self,
        datasets: List[DatasetMetadata]
    ) -> Tuple[List[float], List[Dict]]:
        """Evaluate all datasets"""
        self.fit(datasets)

        scores = []
        all_scores = []

        for ds in datasets:
            score = self.compute(ds)
            scores.append(score)
            all_scores.append({
                'downloads_score': score,
                'DDHS': score  # For compatibility
            })

        return scores, all_scores


class StaticWeightBaseline:
    """
    Static weighted scoring using fixed equal weights for all dimensions.
    Does not adapt weights based on data or learn from deprecation patterns.
    """

    def __init__(self):
        # Equal weights for all features
        self.weights = {
            'downloads': 0.2,
            'citations': 0.2,
            'doc_completeness': 0.2,
            'responsiveness': 0.2,
            'ethics': 0.2
        }
        self.scalers = {}

    def _extract_features(self, dataset: DatasetMetadata) -> Dict[str, float]:
        """Extract raw features from dataset"""
        resolution_rate = dataset.num_resolved_issues / max(1, dataset.num_issues)

        return {
            'downloads': dataset.total_downloads,
            'citations': dataset.citation_count,
            'doc_completeness': dataset.doc_fields_filled / dataset.doc_fields_total,
            'responsiveness': resolution_rate,
            'ethics': 1.0 / (1.0 + dataset.ethical_flags)
        }

    def fit(self, datasets: List[DatasetMetadata]):
        """Fit scalers for normalization"""
        feature_arrays = {k: [] for k in self.weights.keys()}

        for ds in datasets:
            features = self._extract_features(ds)
            for k, v in features.items():
                feature_arrays[k].append(v)

        for k in self.weights.keys():
            arr = np.array(feature_arrays[k]).reshape(-1, 1)
            scaler = StandardScaler()
            scaler.fit(arr)
            self.scalers[k] = scaler

    def compute(self, dataset: DatasetMetadata) -> float:
        """Compute static weighted score"""
        features = self._extract_features(dataset)

        score = 0.0
        for k, weight in self.weights.items():
            val = features[k]
            # Normalize using fitted scaler
            if k in self.scalers:
                val = self.scalers[k].transform([[val]])[0, 0]
                # Convert to [0, 1] range using sigmoid-like transform
                val = 1 / (1 + np.exp(-val))
            score += weight * val

        return float(np.clip(score, 0, 1))

    def evaluate_repository(
        self,
        datasets: List[DatasetMetadata]
    ) -> Tuple[List[float], List[Dict]]:
        """Evaluate all datasets"""
        self.fit(datasets)

        scores = []
        all_scores = []

        for ds in datasets:
            score = self.compute(ds)
            features = self._extract_features(ds)
            scores.append(score)
            all_scores.append({
                **{f'{k}_raw': v for k, v in features.items()},
                'DDHS': score
            })

        return scores, all_scores


class DataShapleyBaseline:
    """
    Simplified Data Shapley-inspired baseline.
    Estimates value of each dataset based on its contribution to
    a proxy downstream task (predicting dataset quality).

    This is a simplified version that uses feature permutation importance
    rather than full Shapley value computation due to computational constraints.
    """

    def __init__(
        self,
        n_iterations: int = 50,
        sample_size: int = 20,
        seed: int = 42
    ):
        self.n_iterations = n_iterations
        self.sample_size = sample_size
        self.rng = np.random.default_rng(seed)
        self.feature_importances = None

    def _extract_feature_vector(self, dataset: DatasetMetadata) -> np.ndarray:
        """Extract numeric feature vector from dataset"""
        age_months = (np.datetime64('2024-01-01') -
                     np.datetime64(dataset.creation_date.isoformat()[:10])).astype('timedelta64[D]').astype(int) // 30

        features = [
            np.log1p(dataset.total_downloads),
            np.log1p(dataset.citation_count),
            dataset.doc_fields_filled / dataset.doc_fields_total,
            dataset.num_resolved_issues / max(1, dataset.num_issues),
            1.0 / (1.0 + dataset.avg_response_time_days),
            float(dataset.maintainer_active),
            float(dataset.has_datasheet),
            float(dataset.has_data_card),
            1.0 / (1.0 + dataset.ethical_flags),
            1.0 / (1.0 + age_months / 12)  # Freshness
        ]

        return np.array(features)

    def fit(self, datasets: List[DatasetMetadata]):
        """
        Fit the model by computing feature importances using a
        simplified Shapley-inspired approach.
        """
        X = np.array([self._extract_feature_vector(ds) for ds in datasets])
        y = np.array([float(not ds.is_deprecated) for ds in datasets])

        # Standardize features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Use logistic regression to get base model
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model = LogisticRegression(max_iter=1000, random_state=42)
            self.model.fit(X_scaled, y)

        # Compute feature importances using permutation
        n_features = X_scaled.shape[1]
        self.feature_importances = np.abs(self.model.coef_[0])

        # Normalize importances
        self.feature_importances = self.feature_importances / np.sum(self.feature_importances)

    def compute(self, dataset: DatasetMetadata) -> float:
        """Compute Shapley-inspired score"""
        features = self._extract_feature_vector(dataset)
        features_scaled = self.scaler.transform(features.reshape(1, -1))[0]

        # Weighted combination based on feature importances
        score = np.sum(features_scaled * self.feature_importances)

        # Normalize to [0, 1]
        score = 1 / (1 + np.exp(-score))

        return float(np.clip(score, 0, 1))

    def evaluate_repository(
        self,
        datasets: List[DatasetMetadata]
    ) -> Tuple[List[float], List[Dict]]:
        """Evaluate all datasets"""
        self.fit(datasets)

        scores = []
        all_scores = []

        for ds in datasets:
            score = self.compute(ds)
            scores.append(score)
            all_scores.append({
                'shapley_score': score,
                'DDHS': score
            })

        return scores, all_scores


class RecencyOnlyBaseline:
    """
    Baseline that only considers dataset recency/freshness.
    Newer datasets get higher scores.
    """

    def __init__(self, decay_rate: float = 0.05):
        self.decay_rate = decay_rate
        self.reference_date = np.datetime64('2024-01-01')

    def compute(self, dataset: DatasetMetadata) -> float:
        """Compute score based on recency"""
        creation = np.datetime64(dataset.creation_date.isoformat()[:10])
        last_update = np.datetime64(dataset.last_updated.isoformat()[:10])

        age_months = (self.reference_date - creation).astype('timedelta64[D]').astype(int) // 30
        update_months = (self.reference_date - last_update).astype('timedelta64[D]').astype(int) // 30

        # Combine age and update recency
        age_score = np.exp(-self.decay_rate * age_months)
        update_score = np.exp(-self.decay_rate * update_months)

        score = 0.5 * age_score + 0.5 * update_score

        return float(np.clip(score, 0, 1))

    def evaluate_repository(
        self,
        datasets: List[DatasetMetadata]
    ) -> Tuple[List[float], List[Dict]]:
        """Evaluate all datasets"""
        scores = []
        all_scores = []

        for ds in datasets:
            score = self.compute(ds)
            scores.append(score)
            all_scores.append({
                'recency_score': score,
                'DDHS': score
            })

        return scores, all_scores


class DocumentationOnlyBaseline:
    """
    Baseline that only considers documentation completeness.
    """

    def compute(self, dataset: DatasetMetadata) -> float:
        """Compute score based on documentation"""
        doc_score = dataset.doc_fields_filled / dataset.doc_fields_total

        # Bonus for having modern documentation
        if dataset.has_datasheet:
            doc_score += 0.15
        if dataset.has_data_card:
            doc_score += 0.1

        # README length bonus
        readme_bonus = min(0.1, dataset.readme_length / 5000)
        doc_score += readme_bonus

        return float(np.clip(doc_score, 0, 1))

    def evaluate_repository(
        self,
        datasets: List[DatasetMetadata]
    ) -> Tuple[List[float], List[Dict]]:
        """Evaluate all datasets"""
        scores = []
        all_scores = []

        for ds in datasets:
            score = self.compute(ds)
            scores.append(score)
            all_scores.append({
                'doc_score': score,
                'DDHS': score
            })

        return scores, all_scores


def get_all_baselines() -> Dict[str, object]:
    """Get all baseline methods"""
    return {
        'Downloads-Only': DownloadsOnlyBaseline(),
        'Static-Weighted': StaticWeightBaseline(),
        'Data-Shapley': DataShapleyBaseline(),
        'Recency-Only': RecencyOnlyBaseline(),
        'Documentation-Only': DocumentationOnlyBaseline()
    }


if __name__ == "__main__":
    # Test baselines
    from data_generator import SyntheticDataGenerator

    generator = SyntheticDataGenerator(seed=42)
    datasets = generator.generate_repository(num_datasets=50)

    baselines = get_all_baselines()

    print("Testing Baseline Methods:")
    print("=" * 80)

    for name, baseline in baselines.items():
        scores, _ = baseline.evaluate_repository(datasets)
        print(f"\n{name}:")
        print(f"  Mean score: {np.mean(scores):.3f}")
        print(f"  Std score: {np.std(scores):.3f}")
        print(f"  Min: {np.min(scores):.3f}, Max: {np.max(scores):.3f}")
