import random
from typing import Dict, Set, Tuple
import networkx as nx
from networkx.algorithms import bipartite
import community as community_louvain


class BipartiteCommunityDetector:
    """Detect communities from benchmark-method bipartite graph."""

    def __init__(self, config):
        self.config = config
        random.seed(config.random_seed)

    def project_to_unipartite(self, bipartite_graph: nx.Graph) -> nx.Graph:
        """
        Project bipartite graph to unipartite (methods-only).

        Args:
            bipartite_graph: Bipartite graph with 'bipartite' attribute

        Returns:
            Weighted projection on method nodes
        """
        method_nodes = {n for n, d in bipartite_graph.nodes(data=True) if d['bipartite'] == 0}
        projected = bipartite.weighted_projected_graph(bipartite_graph, method_nodes)
        print(f"Projected to {len(projected.nodes())} method nodes, {len(projected.edges())} edges")
        return projected

    def detect_communities(
        self,
        bipartite_graph: nx.Graph,
        citation_dict: Dict[str, Set[str]]
    ) -> Tuple[Dict[str, int], Dict[str, float]]:
        """
        Detect communities via Louvain algorithm.

        Args:
            bipartite_graph: Bipartite graph
            citation_dict: {method_id: set(cited_paper_ids)}

        Returns:
            communities: {method_id: community_label}
            metrics: {modularity, citation_overlap}
        """
        projected_graph = self.project_to_unipartite(bipartite_graph)

        partition = community_louvain.best_partition(
            projected_graph,
            resolution=self.config.resolution,
            random_state=self.config.random_seed
        )

        partition = self._filter_small_communities(partition, projected_graph)

        modularity = community_louvain.modularity(partition, projected_graph)
        print(f"Louvain modularity: {modularity:.4f}")

        citation_overlap = self._compute_citation_overlap(partition, citation_dict)
        print(f"Citation overlap: {citation_overlap:.4f}")

        metrics = {
            'modularity': modularity,
            'citation_overlap': citation_overlap,
            'num_communities': len(set(partition.values()))
        }

        return partition, metrics

    def _filter_small_communities(self, partition: Dict[str, int], graph: nx.Graph) -> Dict[str, int]:
        """Remove communities with < min_community_size nodes."""
        community_sizes = {}
        for node, label in partition.items():
            community_sizes[label] = community_sizes.get(label, 0) + 1

        small_communities = {label for label, size in community_sizes.items() if size < self.config.min_community_size}

        if not small_communities:
            return partition

        filtered = {}
        for node, label in partition.items():
            if label not in small_communities:
                filtered[node] = label

        print(f"Filtered {len(small_communities)} small communities, kept {len(set(filtered.values()))} communities")
        return filtered

    def random_baseline(
        self,
        method_ids: list,
        num_communities: int,
        citation_dict: Dict[str, Set[str]]
    ) -> Tuple[Dict[str, int], float]:
        """
        Random partition baseline.

        Args:
            method_ids: List of method IDs
            num_communities: Number of communities to create
            citation_dict: Citation data

        Returns:
            partition: {method_id: random_label}
            citation_overlap: Random baseline overlap
        """
        random.seed(self.config.random_seed)
        partition = {mid: random.randint(0, num_communities - 1) for mid in method_ids}

        overlap = self._compute_citation_overlap(partition, citation_dict)
        print(f"Random baseline citation overlap: {overlap:.4f}")

        return partition, overlap

    def _compute_citation_overlap(self, partition: Dict[str, int], citation_dict: Dict[str, Set[str]]) -> float:
        """
        Compute average pairwise Jaccard similarity within communities.

        Args:
            partition: {method_id: community_label}
            citation_dict: {method_id: set(cited_paper_ids)}

        Returns:
            Average citation overlap across communities
        """
        from collections import defaultdict

        community_groups = defaultdict(list)
        for method, label in partition.items():
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

                    c1 = citation_dict[m1]
                    c2 = citation_dict[m2]

                    if len(c1) == 0 and len(c2) == 0:
                        overlap = 0.0
                    else:
                        intersection = len(c1 & c2)
                        union = len(c1 | c2)
                        overlap = intersection / union if union > 0 else 0.0

                    overlaps.append(overlap)

            if overlaps:
                all_overlaps.extend(overlaps)

        return sum(all_overlaps) / len(all_overlaps) if all_overlaps else 0.0
