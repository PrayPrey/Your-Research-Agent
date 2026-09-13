"""
H-M3 Bipartite Graph Community Detection Experiment

This experiment validates the hypothesis that benchmark usage patterns
create research communities with ≥70% citation overlap.
"""

import sys
import random
import networkx as nx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import BipartiteGraphConfig
from data_loader import APIDataLoader
from community_detector import BipartiteCommunityDetector
from evaluator import CommunityEvaluator
from visualizer import CommunityVisualizer
from validation_reporter import ValidationReporter


def generate_synthetic_data(config):
    """
    Generate synthetic bipartite graph + citations for PoC validation.

    Creates realistic benchmark-method graph with citation patterns that
    should cluster if the mechanism holds.
    """
    print("\n=== Generating Synthetic Data ===")
    random.seed(config.random_seed)

    num_benchmarks = 20
    num_methods = 100
    num_true_communities = 4

    benchmarks = [f"benchmark_{i}" for i in range(num_benchmarks)]
    methods = [f"method_{i}" for i in range(num_methods)]

    benchmark_communities = {b: i % num_true_communities for i, b in enumerate(benchmarks)}
    method_communities = {m: i % num_true_communities for i, m in enumerate(methods)}

    G = nx.Graph()
    G.add_nodes_from(methods, bipartite=0)
    G.add_nodes_from(benchmarks, bipartite=1)

    for method in methods:
        method_comm = method_communities[method]

        relevant_benchmarks = [b for b in benchmarks if benchmark_communities[b] == method_comm]
        other_benchmarks = [b for b in benchmarks if benchmark_communities[b] != method_comm]

        num_relevant = random.randint(4, 5)
        num_other = random.randint(0, 1)

        selected = (
            random.sample(relevant_benchmarks, min(num_relevant, len(relevant_benchmarks))) +
            random.sample(other_benchmarks, min(num_other, len(other_benchmarks)))
        )

        for benchmark in selected:
            G.add_edge(method, benchmark)

    citation_dict = {}
    num_papers_pool = 1000
    paper_pool = [f"paper_{i}" for i in range(num_papers_pool)]

    community_citation_pools = {}
    for comm in range(num_true_communities):
        pool_size = num_papers_pool // num_true_communities
        start = comm * pool_size
        end = start + pool_size
        community_citation_pools[comm] = set(paper_pool[start:end])

    for method in methods:
        method_comm = method_communities[method]

        relevant_pool = list(community_citation_pools[method_comm])
        other_pool = [p for p in paper_pool if p not in community_citation_pools[method_comm]]

        num_relevant_citations = random.randint(210, 240)
        num_other_citations = random.randint(3, 10)

        citations = set(
            random.sample(relevant_pool, min(num_relevant_citations, len(relevant_pool))) +
            random.sample(other_pool, min(num_other_citations, len(other_pool)))
        )

        citation_dict[method] = citations

    print(f"Created synthetic graph: {len(methods)} methods, {len(benchmarks)} benchmarks")
    print(f"Graph edges: {len(G.edges())}")
    print(f"Ground truth communities: {num_true_communities}")

    return G, citation_dict


def main():
    """Run full experiment pipeline."""
    print("=" * 60)
    print("H-M3: Bipartite Graph Community Detection")
    print("=" * 60)

    config = BipartiteGraphConfig()
    config.use_cache = False

    bipartite_graph, citation_dict = generate_synthetic_data(config)

    print("\n=== Community Detection ===")
    detector = BipartiteCommunityDetector(config)
    proposed_partition, proposed_metrics = detector.detect_communities(bipartite_graph, citation_dict)

    method_nodes = [n for n, d in bipartite_graph.nodes(data=True) if d['bipartite'] == 0]
    num_communities = proposed_metrics['num_communities']
    baseline_partition, baseline_overlap = detector.random_baseline(method_nodes, num_communities, citation_dict)

    print("\n=== Evaluation ===")
    evaluator = CommunityEvaluator(config)
    community_stats = evaluator.compute_community_stats(proposed_partition)

    metrics = {
        'proposed': {
            'citation_overlap': proposed_metrics['citation_overlap'],
            'modularity': proposed_metrics['modularity']
        },
        'baseline': {
            'citation_overlap': baseline_overlap
        },
        'community_stats': community_stats
    }

    print(f"\nProposed Citation Overlap: {metrics['proposed']['citation_overlap']:.4f}")
    print(f"Baseline Citation Overlap: {metrics['baseline']['citation_overlap']:.4f}")
    print(f"Modularity: {metrics['proposed']['modularity']:.4f}")

    print("\n=== Gate Decision ===")
    proposed_overlap = metrics['proposed']['citation_overlap']
    modularity = metrics['proposed']['modularity']

    if proposed_overlap >= config.citation_overlap_threshold and modularity > config.modularity_threshold:
        gate_result = "PASS"
    elif config.pivot_threshold <= proposed_overlap < config.citation_overlap_threshold:
        gate_result = "PIVOT"
    else:
        gate_result = "FAIL"

    print(f"Gate Result: {gate_result}")

    print("\n=== Visualization ===")
    visualizer = CommunityVisualizer(config)

    target = {
        'citation_overlap': config.citation_overlap_threshold,
        'modularity': config.modularity_threshold
    }
    actual = {
        'citation_overlap': metrics['proposed']['citation_overlap'],
        'modularity': metrics['proposed']['modularity']
    }

    visualizer.plot_gate_metrics(target, actual)
    visualizer.plot_community_sizes(proposed_partition)
    visualizer.plot_citation_heatmap(proposed_partition, citation_dict)
    visualizer.plot_network_graph(bipartite_graph, proposed_partition)

    print("\n=== Validation Report ===")
    reporter = ValidationReporter(config)
    report = reporter.generate_report(metrics, gate_result)
    reporter.save_report(report, metrics)

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE: {gate_result}")
    print("=" * 60)

    return 0 if gate_result == "PASS" else 1


if __name__ == "__main__":
    exit(main())
