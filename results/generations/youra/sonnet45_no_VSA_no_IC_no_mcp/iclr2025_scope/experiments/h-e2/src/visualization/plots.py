import matplotlib.pyplot as plt
from typing import Dict
import os

class Visualizer:
    """Generate coverage analysis plots."""

    def plot_coverage_vs_threshold(self, coverage_pct: float, threshold: float, save_path: str):
        """Bar chart: actual coverage vs threshold."""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(['Actual Coverage', 'Threshold'], [coverage_pct, threshold], color=['blue', 'red'])
        ax.set_ylabel('Coverage (%)')
        ax.set_ylim([0, 100])
        ax.axhline(y=threshold, color='r', linestyle='--', label=f'{threshold}% threshold')
        ax.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    def plot_domain_comparison(self, nlp_pct: float, cv_pct: float, save_path: str):
        """Bar chart: NLP vs CV coverage."""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(['NLP', 'CV'], [nlp_pct, cv_pct], color=['green', 'orange'])
        ax.set_ylabel('Coverage (%)')
        ax.set_ylim([0, 100])
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    def plot_source_breakdown(self, breakdown: Dict[str, int], save_path: str):
        """Stacked bar: PwC-only, HF-only, Both, Neither."""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        fig, ax = plt.subplots(figsize=(8, 4))
        categories = ['PwC Only', 'HF Only', 'Both', 'Neither']
        values = [breakdown['pwc_only'], breakdown['hf_only'], breakdown['both'], breakdown['neither']]
        ax.bar(categories, values, color=['purple', 'cyan', 'green', 'red'])
        ax.set_ylabel('Dataset Count')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
