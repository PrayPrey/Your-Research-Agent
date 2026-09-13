"""Dependency graph construction for dataset usage relationships."""
import networkx as nx
import json
import gzip
from pathlib import Path
from typing import List, Dict, Any, Set
from .config import GRAPH_CONSTRUCTION_CONFIG

class DependencyGraphBuilder:
    def __init__(self, hf_token=None, gh_token=None):
        self.hf_token = hf_token
        self.gh_token = gh_token
        self.graph = nx.DiGraph()
        self.config = GRAPH_CONSTRUCTION_CONFIG

    def build_graph(self, hf_metadata: List[Dict], github_deps: List[Dict], pwc_citations: List[Dict]) -> nx.DiGraph:
        """Build dependency graph from multi-source data."""
        self._add_dataset_nodes(hf_metadata)
        self._add_usage_edges(github_deps, source="github")
        self._add_usage_edges(pwc_citations, source="pwc")
        self._handle_cycles()
        return self.graph

    def _add_dataset_nodes(self, metadata: List[Dict]):
        for dataset in metadata:
            self.graph.add_node(
                dataset['id'],
                schema=dataset.get('schema', {}),
                deprecated=dataset.get('deprecated', False),
                successor_id=dataset.get('successor'),
                download_count=dataset.get('downloads', 0)
            )

    def _add_usage_edges(self, deps: List[Dict], source: str):
        confidence = self.config['edge_confidence'].get(
            source if source in self.config['edge_confidence'] else 'code_mention',
            0.5
        )
        for dep in deps:
            if dep['source'] in self.graph and dep['target'] in self.graph:
                self.graph.add_edge(
                    dep['source'],
                    dep['target'],
                    entity_type=dep.get('entity_type', 'script'),
                    confidence=confidence,
                    source=source
                )

    def _handle_cycles(self) -> List[Set[str]]:
        sccs = list(nx.strongly_connected_components(self.graph))
        cycles = [scc for scc in sccs if len(scc) > 1]
        if cycles:
            print(f"Warning: {len(cycles)} cycles detected in graph")
        return cycles

    def save(self, path: str):
        data = nx.node_link_data(self.graph)
        if self.config['performance']['serialize_compression'] == 'gzip':
            with gzip.open(path, 'wt') as f:
                json.dump(data, f)
        else:
            Path(path).write_text(json.dumps(data))

    def load(self, path: str) -> nx.DiGraph:
        if path.endswith('.gz'):
            with gzip.open(path, 'rt') as f:
                data = json.load(f)
        else:
            data = json.loads(Path(path).read_text())
        self.graph = nx.node_link_graph(data)
        return self.graph
