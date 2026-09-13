"""Transitive impact analysis for deprecated datasets."""
import networkx as nx
from typing import Set, Dict, Any
from collections import defaultdict
from .config import IMPACT_ANALYSIS_CONFIG

class ImpactAnalyzer:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.config = IMPACT_ANALYSIS_CONFIG

    def compute_impact(self, dataset_id: str) -> Dict[str, Any]:
        """Compute transitive impact radius."""
        affected = self._compute_transitive_closure(dataset_id)

        summary = {
            'total': len(affected),
            'by_type': self._group_by_type(dataset_id, affected),
            'by_depth': self._depth_distribution(dataset_id, affected)
        }

        return {'affected': affected, 'summary': summary}

    def _compute_transitive_closure(self, dataset_id: str) -> Set[str]:
        if dataset_id not in self.graph:
            return set()
        try:
            affected = nx.descendants(self.graph, dataset_id)
            max_affected = self.config['closure']['max_affected_entities']
            if len(affected) > max_affected:
                print(f"Warning: {len(affected)} affected entities exceeds limit {max_affected}")
                affected = set(list(affected)[:max_affected])
            return affected
        except Exception as e:
            print(f"Error computing descendants for {dataset_id}: {e}")
            return set()

    def _group_by_type(self, root: str, entities: Set[str]) -> Dict[str, int]:
        counts = defaultdict(int)
        for entity in entities:
            if root in self.graph and entity in self.graph[root]:
                entity_type = self.graph[root][entity].get('entity_type', 'unknown')
                counts[entity_type] += 1
            else:
                # Traverse to find edge
                try:
                    path = nx.shortest_path(self.graph, root, entity)
                    if len(path) >= 2:
                        entity_type = self.graph[path[-2]][path[-1]].get('entity_type', 'unknown')
                        counts[entity_type] += 1
                except nx.NetworkXNoPath:
                    counts['unknown'] += 1
        return dict(counts)

    def _depth_distribution(self, root: str, entities: Set[str]) -> Dict[int, int]:
        depths = defaultdict(int)
        for entity in entities:
            try:
                depth = nx.shortest_path_length(self.graph, root, entity)
                bin_depth = min(depth, max(self.config['grouping']['depth_bins']))
                depths[bin_depth] += 1
            except nx.NetworkXNoPath:
                pass
        return dict(depths)
