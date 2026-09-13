from pathlib import Path
from typing import Dict, Set
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import networkx as nx
from collections import defaultdict


class CommunityVisualizer:
    """Generate visualizations for community detection results."""

    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config.figures_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_gate_metrics(self, target: Dict, actual: Dict):
        """Bar chart: target vs actual metrics."""
        fig, ax = plt.subplots(figsize=self.config.figure_size_default)

        metrics = ['Citation Overlap', 'Modularity']
        x = np.arange(len(metrics))
        width = 0.35

        target_values = [target['citation_overlap'], target['modularity']]
        actual_values = [actual['citation_overlap'], actual['modularity']]

        ax.bar(x - width/2, target_values, width, label='Target', color='lightblue')
        ax.bar(x + width/2, actual_values, width, label='Actual', color='orange')

        ax.set_ylabel('Value')
        ax.set_title('Gate Metrics: Target vs Actual')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        save_path = self.output_dir / "gate_metrics.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.figure_dpi)
        plt.close()
        print(f"Saved gate metrics: {save_path}")

    def plot_community_sizes(self, communities: Dict[str, int]):
        """Histogram: community size distribution."""
        community_sizes = defaultdict(int)
        for method, label in communities.items():
            community_sizes[label] += 1

        sizes = list(community_sizes.values())

        fig, ax = plt.subplots(figsize=self.config.figure_size_default)
        ax.hist(sizes, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(sizes), color='red', linestyle='--', label=f'Mean: {np.mean(sizes):.1f}')
        ax.set_xlabel('Community Size (number of methods)')
        ax.set_ylabel('Frequency')
        ax.set_title('Community Size Distribution')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        save_path = self.output_dir / "community_sizes.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.figure_dpi)
        plt.close()
        print(f"Saved community sizes: {save_path}")

    def plot_citation_heatmap(self, communities: Dict[str, int], citation_dict: Dict[str, Set[str]]):
        """Heatmap: pairwise Jaccard similarity."""
        methods = sorted(communities.keys(), key=lambda m: communities[m])

        n = len(methods)
        if n > 200:
            print(f"Warning: {n} methods, sampling 200 for heatmap")
            methods = methods[:200]
            n = 200

        matrix = np.zeros((n, n))
        for i, m1 in enumerate(methods):
            for j, m2 in enumerate(methods):
                if m1 not in citation_dict or m2 not in citation_dict:
                    continue

                c1 = citation_dict[m1]
                c2 = citation_dict[m2]

                if len(c1) == 0 and len(c2) == 0:
                    matrix[i, j] = 0.0
                else:
                    intersection = len(c1 & c2)
                    union = len(c1 | c2)
                    matrix[i, j] = intersection / union if union > 0 else 0.0

        fig, ax = plt.subplots(figsize=self.config.figure_size_heatmap)
        sns.heatmap(matrix, cmap=self.config.colormap, vmin=0, vmax=1, square=True, ax=ax, cbar_kws={'label': 'Jaccard Similarity'})
        ax.set_xlabel('Methods (sorted by community)')
        ax.set_ylabel('Methods (sorted by community)')
        ax.set_title('Citation Overlap Heatmap')

        save_path = self.output_dir / "citation_heatmap.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.figure_dpi)
        plt.close()
        print(f"Saved citation heatmap: {save_path}")

    def plot_network_graph(self, graph: nx.Graph, communities: Dict[str, int]):
        """Force-directed graph with community colors."""
        method_nodes = {n for n, d in graph.nodes(data=True) if d.get('bipartite') == 0}
        subgraph = graph.subgraph(method_nodes).copy()

        if len(subgraph.nodes()) > 100:
            print(f"Warning: {len(subgraph.nodes())} nodes, sampling 100 for visualization")
            sampled = list(subgraph.nodes())[:100]
            subgraph = subgraph.subgraph(sampled).copy()

        fig, ax = plt.subplots(figsize=self.config.figure_size_network)

        pos = nx.spring_layout(subgraph, seed=self.config.random_seed, k=0.3, iterations=50)

        node_colors = [self.config.community_colors[communities.get(node, 0) % len(self.config.community_colors)] for node in subgraph.nodes()]

        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=100, alpha=0.8, ax=ax)
        nx.draw_networkx_edges(subgraph, pos, alpha=0.2, ax=ax)

        ax.set_title('Network Graph (Methods colored by community)')
        ax.axis('off')

        save_path = self.output_dir / "network_graph.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.figure_dpi)
        plt.close()
        print(f"Saved network graph: {save_path}")
