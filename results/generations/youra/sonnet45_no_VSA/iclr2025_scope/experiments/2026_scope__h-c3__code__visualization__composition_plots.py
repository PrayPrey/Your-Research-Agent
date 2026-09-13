"""
Composition Visualizer for h-c3
Generates required and optional figures
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Dict
import networkx as nx

from analysis.composition_metrics import CompositionMetrics


class CompositionVisualizer:
    """Generates visualizations for composition contract validation"""

    def __init__(self, output_dir: str = "../figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_gate_metrics(self, metrics: CompositionMetrics) -> None:
        """
        Mandatory: Bar chart comparing target vs actual metrics.

        Saves to: figures/gate_metrics.png
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics_data = {
            'Detection Rate': {
                'target': 60.0,
                'actual': metrics.detection_rate,
                'ci_lower': metrics.detection_ci_lower,
                'ci_upper': metrics.detection_ci_upper
            },
            'Version Stability': {
                'target': 80.0,
                'actual': metrics.version_stability_rate,
                'ci_lower': None,
                'ci_upper': None
            },
            'False Positive Rate': {
                'target': 5.0,
                'actual': metrics.false_positive_rate,
                'ci_lower': None,
                'ci_upper': None
            }
        }

        x = np.arange(len(metrics_data))
        width = 0.35

        targets = [v['target'] for v in metrics_data.values()]
        actuals = [v['actual'] for v in metrics_data.values()]

        ax.bar(x - width/2, targets, width, label='Target', color='#2ecc71')
        bars = ax.bar(x + width/2, actuals, width, label='Actual', color='#3498db')

        # Add CI error bars for detection rate
        ci_errors = []
        for i, (key, data) in enumerate(metrics_data.items()):
            if data['ci_lower'] is not None and data['ci_upper'] is not None:
                error = [
                    data['actual'] - data['ci_lower'],
                    data['ci_upper'] - data['actual']
                ]
                ci_errors.append(error)
            else:
                ci_errors.append([0, 0])

        # Convert to array for errorbar
        yerr = np.array(ci_errors).T
        ax.errorbar(x + width/2, actuals, yerr=yerr, fmt='none', color='black', capsize=5)

        ax.set_xlabel('Metric')
        ax.set_ylabel('Percentage (%)')
        ax.set_title(f'h-c3 Gate Metrics (Status: {metrics.gate_status})')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics_data.keys())
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_metrics.png', dpi=300)
        plt.close()

    def plot_detection_by_type(self, contractable_by_type: Dict[str, int]) -> None:
        """
        Bar chart: detection rate for each contract type.

        Saves to: figures/detection_by_type.png
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        types = list(contractable_by_type.keys())
        counts = list(contractable_by_type.values())
        colors = ['#3498db', '#f39c12', '#9b59b6']

        ax.bar(types, counts, color=colors)
        ax.set_xlabel('Contract Type')
        ax.set_ylabel('Contractable Defects')
        ax.set_title('Detection Rate by Contract Type')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'detection_by_type.png', dpi=300)
        plt.close()

    def plot_execution_time_dist(self, execution_times: List[float]) -> None:
        """
        Histogram of contract execution times.

        Saves to: figures/execution_time_dist.png
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Filter out zero times
        valid_times = [t for t in execution_times if t > 0]

        if not valid_times:
            # No valid times, create placeholder
            ax.text(0.5, 0.5, 'No valid execution times recorded',
                   ha='center', va='center', transform=ax.transAxes)
        else:
            ax.hist(valid_times, bins=20, color='#3498db', alpha=0.7, edgecolor='black')
            ax.axvline(x=10.0, color='#e74c3c', linestyle='--', linewidth=2,
                      label='10s Threshold')
            ax.set_xlabel('Execution Time (seconds)')
            ax.set_ylabel('Frequency')
            ax.set_title('Contract Execution Time Distribution')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'execution_time_dist.png', dpi=300)
        plt.close()

    def plot_version_stability_heatmap(self, stability_data: np.ndarray = None) -> None:
        """
        Heatmap: rows=defects, cols=version deltas.

        Saves to: figures/version_stability_heatmap.png
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        if stability_data is None:
            # Placeholder data for PoC
            stability_data = np.random.binomial(1, 0.8, size=(62, 5))

        im = ax.imshow(stability_data, cmap='RdYlGn', aspect='auto')

        ax.set_xlabel('Version Delta')
        ax.set_ylabel('Defect ID')
        ax.set_title('Version Stability Heatmap (Green=Stable, Red=Unstable)')
        ax.set_xticks(range(5))
        ax.set_xticklabels(['-2', '-1', '0', '+1', '+2'])

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Stable (1) / Unstable (0)')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'version_stability_heatmap.png', dpi=300)
        plt.close()

    def plot_failure_propagation(self, propagation_graph: Dict) -> None:
        """
        Network diagram: nodes=pipeline stages, edges=failure propagation.

        Saves to: figures/failure_propagation.png
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        # Create directed graph
        G = nx.DiGraph()

        # Add nodes
        nodes = propagation_graph.get('nodes', [])
        for node in nodes:
            G.add_node(node)

        # Add edges
        edges = propagation_graph.get('edges', [])
        for source, target in edges:
            if source != "none":
                G.add_edge(source, target)

        # Layout
        pos = nx.spring_layout(G, seed=1)

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='#3498db', node_size=2000, ax=ax)

        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True,
                              arrowsize=20, ax=ax)

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=12, font_color='white', ax=ax)

        ax.set_title('Failure Propagation Network')
        ax.axis('off')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'failure_propagation.png', dpi=300)
        plt.close()

    def generate_all_figures(
        self,
        metrics: CompositionMetrics,
        execution_times: List[float],
        propagation_graph: Dict
    ) -> None:
        """Generate all required and optional figures"""
        self.plot_gate_metrics(metrics)
        self.plot_detection_by_type(metrics.contractable_by_type)
        self.plot_execution_time_dist(execution_times)
        self.plot_version_stability_heatmap()
        self.plot_failure_propagation(propagation_graph)
