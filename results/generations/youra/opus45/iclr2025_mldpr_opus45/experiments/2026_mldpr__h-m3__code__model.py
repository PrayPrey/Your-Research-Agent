"""Model implementations for h-m3 Archetype Recovery experiment.

Implements ArchetypeRecoveryMatcher (proposed) and RandomBaselineMatcher (baseline)
for mapping cluster centroids to theoretical archetypes via shape descriptor alignment.
"""

import numpy as np
from scipy.spatial.distance import cosine
from typing import Dict, List, Tuple, Set

from config import ExperimentConfig, ARCHETYPE_PROFILES, DESCRIPTOR_ORDER


class ArchetypeRecoveryMatcher:
    """
    Map empirical cluster centroids to theoretical archetypes
    using shape descriptor alignment (>70% threshold).
    """

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.archetypes = ARCHETYPE_PROFILES
        self.threshold = config.alignment_threshold
        self.descriptor_order = DESCRIPTOR_ORDER

    def normalize_profile(self, profile: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize descriptor values to 0-1 range for comparison.

        Uses min-max normalization based on observed ranges from h-m2.
        """
        norm_ranges = self.config.get_norm_ranges()
        normalized = {}

        for key, value in profile.items():
            if key in norm_ranges:
                min_v, max_v = norm_ranges[key]
                if max_v - min_v > 1e-10:
                    normalized[key] = (value - min_v) / (max_v - min_v)
                else:
                    normalized[key] = 0.5
                # Clip to [0, 1]
                normalized[key] = np.clip(normalized[key], 0.0, 1.0)
            else:
                normalized[key] = value

        return normalized

    def compute_alignment(
        self, cluster_profile: Dict[str, float], archetype_name: str
    ) -> float:
        """
        Compute alignment score (0-1) between cluster and archetype.

        Uses cosine similarity: 1 - cosine_distance
        """
        archetype = self.archetypes[archetype_name]

        # Normalize cluster profile
        norm_profile = self.normalize_profile(cluster_profile)

        # Build vectors in consistent order
        cluster_vec = np.array([norm_profile.get(k, 0.5) for k in self.descriptor_order])
        archetype_vec = np.array([archetype.get(k, 0.5) for k in self.descriptor_order])

        # Cosine similarity (1 - cosine distance)
        # Handle edge case where vectors are zero
        if np.linalg.norm(cluster_vec) < 1e-10 or np.linalg.norm(archetype_vec) < 1e-10:
            return 0.0

        alignment = 1.0 - cosine(cluster_vec, archetype_vec)

        return float(alignment)

    def build_alignment_matrix(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> np.ndarray:
        """
        Build full alignment matrix: (k clusters, n archetypes).

        Returns:
            alignment_matrix: (k, n_archetypes) = (4, 5) by default
        """
        archetype_names = list(self.archetypes.keys())
        k = len(cluster_profiles)
        n_archetypes = len(archetype_names)

        alignment_matrix = np.zeros((k, n_archetypes), dtype=np.float64)

        for i, (cluster_id, profile) in enumerate(sorted(cluster_profiles.items())):
            for j, arch_name in enumerate(archetype_names):
                alignment_matrix[i, j] = self.compute_alignment(profile, arch_name)

        return alignment_matrix

    def match_clusters(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> Tuple[Dict[int, Tuple[str, float]], int]:
        """
        Assign each cluster to best-matching archetype if alignment > threshold.

        Returns:
            (assignments, n_recovered)
            assignments: {cluster_id: (archetype_name, alignment_score)}
            n_recovered: count of distinct archetypes matched above threshold
        """
        assignments: Dict[int, Tuple[str, float]] = {}
        recovered: Set[str] = set()

        for cluster_id, profile in cluster_profiles.items():
            best_arch = None
            best_score = 0.0

            for arch_name in self.archetypes:
                score = self.compute_alignment(profile, arch_name)
                if score > best_score:
                    best_arch = arch_name
                    best_score = score

            if best_score >= self.threshold:
                assignments[cluster_id] = (best_arch, best_score)
                recovered.add(best_arch)

        return assignments, len(recovered)


class RandomBaselineMatcher:
    """
    Random archetype assignment baseline.

    Randomly assigns each cluster to one of 5 archetypes (seed=42).
    Expected alignment: ~20% by chance.
    """

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.archetypes = ARCHETYPE_PROFILES
        self.random_state = config.random_state

    def match_clusters(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> Tuple[Dict[int, Tuple[str, float]], int]:
        """
        Random assignment without replacement.

        Returns:
            (assignments, n_recovered)
        """
        np.random.seed(self.random_state)

        archetype_names = list(self.archetypes.keys())
        cluster_ids = sorted(cluster_profiles.keys())
        k = len(cluster_ids)

        # Random assignment (sample without replacement if k <= n_archetypes)
        if k <= len(archetype_names):
            random_archetypes = np.random.choice(
                archetype_names, size=k, replace=False
            )
        else:
            random_archetypes = np.random.choice(
                archetype_names, size=k, replace=True
            )

        assignments: Dict[int, Tuple[str, float]] = {}
        recovered: Set[str] = set()

        for i, cluster_id in enumerate(cluster_ids):
            arch_name = random_archetypes[i]
            # Random score between 0.1 and 0.5 (simulating chance alignment)
            score = 0.1 + np.random.random() * 0.4
            assignments[cluster_id] = (arch_name, score)
            recovered.add(arch_name)

        return assignments, len(recovered)
