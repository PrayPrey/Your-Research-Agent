import json
import time
import pickle
from pathlib import Path
from typing import Dict, List, Set, Tuple
import requests
import networkx as nx
from networkx.algorithms import bipartite


class APIDataLoader:
    """Load benchmark-method data from Papers with Code and Semantic Scholar APIs."""

    def __init__(self, config):
        self.config = config
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_benchmark_methods(self, benchmark_names: List[str]) -> Dict[str, List[str]]:
        """
        Fetch papers using specific benchmarks from Papers with Code API.

        Args:
            benchmark_names: List of benchmark names to query

        Returns:
            {benchmark_name: [paper_ids]}
        """
        cache_path = self.cache_dir / "benchmark_methods.json"
        if cache_path.exists() and self.config.use_cache:
            with open(cache_path) as f:
                return json.load(f)

        benchmark_methods = {}
        for benchmark in benchmark_names:
            try:
                url = f"{self.config.pwc_api_base}/benchmarks/{benchmark}/results/"
                response = requests.get(url, timeout=self.config.api_timeout)
                response.raise_for_status()
                data = response.json()

                paper_ids = [
                    result['paper']['id']
                    for result in data.get('results', [])
                    if self.config.publication_year_min <= int(result['paper'].get('year', 0)) <= self.config.publication_year_max
                ]
                benchmark_methods[benchmark] = paper_ids
                time.sleep(self.config.s2_rate_limit_delay)

            except Exception as e:
                print(f"Warning: Failed to fetch {benchmark}: {e}")
                benchmark_methods[benchmark] = []

        with open(cache_path, 'w') as f:
            json.dump(benchmark_methods, f, indent=2)

        return benchmark_methods

    def fetch_citations(self, paper_ids: List[str]) -> Dict[str, Set[str]]:
        """
        Fetch citation data from Semantic Scholar API.

        Args:
            paper_ids: List of paper IDs

        Returns:
            {paper_id: set(cited_paper_ids)}
        """
        cache_path = self.cache_dir / "citation_dict.json"
        if cache_path.exists() and self.config.use_cache:
            with open(cache_path) as f:
                data = json.load(f)
                return {k: set(v) for k, v in data.items()}

        citation_dict = {}
        for paper_id in paper_ids:
            try:
                url = f"{self.config.s2_api_base}/paper/{paper_id}"
                response = requests.get(url, timeout=self.config.api_timeout)
                response.raise_for_status()
                data = response.json()

                citations = set(ref['paperId'] for ref in data.get('citations', []) if ref.get('paperId'))
                citation_dict[paper_id] = citations
                time.sleep(self.config.s2_rate_limit_delay)

            except Exception as e:
                print(f"Warning: Failed to fetch citations for {paper_id}: {e}")
                citation_dict[paper_id] = set()

        with open(cache_path, 'w') as f:
            json.dump({k: list(v) for k, v in citation_dict.items()}, f, indent=2)

        return citation_dict

    def build_bipartite_graph(self, benchmark_methods: Dict[str, List[str]]) -> nx.Graph:
        """
        Construct bipartite graph (benchmarks ↔ methods).

        Args:
            benchmark_methods: {benchmark_name: [paper_ids]}

        Returns:
            NetworkX bipartite graph
        """
        G = nx.Graph()

        all_benchmarks = list(benchmark_methods.keys())
        all_methods = list(set(paper for papers in benchmark_methods.values() for paper in papers))

        G.add_nodes_from(all_methods, bipartite=0)
        G.add_nodes_from(all_benchmarks, bipartite=1)

        for benchmark, methods in benchmark_methods.items():
            for method in methods:
                G.add_edge(method, benchmark)

        low_degree_nodes = [n for n in G.nodes() if G.degree(n) < self.config.min_degree]
        G.remove_nodes_from(low_degree_nodes)
        print(f"Removed {len(low_degree_nodes)} low-degree nodes (min_degree={self.config.min_degree})")

        isolated_nodes = list(nx.isolates(G))
        G.remove_nodes_from(isolated_nodes)
        print(f"Removed {len(isolated_nodes)} isolated nodes")

        return G

    def save_cache(self, graph: nx.Graph, citations: Dict[str, Set[str]]):
        """Save processed graph and citations to disk."""
        graph_path = self.cache_dir / "bipartite_graph.gpickle"
        with open(graph_path, 'wb') as f:
            pickle.dump(graph, f)

        citation_path = self.cache_dir / "citation_dict.json"
        with open(citation_path, 'w') as f:
            json.dump({k: list(v) for k, v in citations.items()}, f, indent=2)

    def load_cache(self) -> Tuple[nx.Graph, Dict[str, Set[str]]]:
        """Load cached graph and citations."""
        graph_path = self.cache_dir / "bipartite_graph.gpickle"
        citation_path = self.cache_dir / "citation_dict.json"

        if not (graph_path.exists() and citation_path.exists()):
            raise FileNotFoundError("Cache not found")

        with open(graph_path, 'rb') as f:
            graph = pickle.load(f)

        with open(citation_path) as f:
            data = json.load(f)
            citations = {k: set(v) for k, v in data.items()}

        return graph, citations
