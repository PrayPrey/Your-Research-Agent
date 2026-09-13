from typing import Dict, Set, Any
from collections import defaultdict


class CommunityEvaluator:
    """Evaluate community detection results."""

    def __init__(self, config):
        self.config = config

    def compute_citation_overlap(self, communities: Dict[str, int], citation_dict: Dict[str, Set[str]]) -> float:
        """
        Compute average pairwise Jaccard similarity within communities.

        Args:
            communities: {method_id: community_label}
            citation_dict: {method_id: set(cited_paper_ids)}

        Returns:
            Average citation overlap (0-1)
        """
        community_groups = defaultdict(list)
        for method, label in communities.items():
            community_groups[label].append(method)

        all_overlaps = []
        for label, methods in community_groups.items():
            if len(methods) < 2:
                continue

            overlaps = []
            for i, m1 in enumerate(methods):
                for m2 in methods[i + 1:]:
                    if m1 not in citation_dict or m2 not in citation_dict:
                        continue

                    overlap = self.jaccard_similarity(citation_dict[m1], citation_dict[m2])
                    overlaps.append(overlap)

            if overlaps:
                all_overlaps.extend(overlaps)

        return sum(all_overlaps) / len(all_overlaps) if all_overlaps else 0.0

    def jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """Jaccard similarity between two sets."""
        if len(set1) == 0 and len(set2) == 0:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def compute_community_stats(self, communities: Dict[str, int]) -> Dict[str, Any]:
        """Compute community size statistics."""
        community_sizes = defaultdict(int)
        for method, label in communities.items():
            community_sizes[label] += 1

        sizes = list(community_sizes.values())
        return {
            'num_communities': len(community_sizes),
            'min_size': min(sizes) if sizes else 0,
            'max_size': max(sizes) if sizes else 0,
            'mean_size': sum(sizes) / len(sizes) if sizes else 0.0,
            'sizes': sizes
        }
