#!/usr/bin/env python3
"""
Preference Entropy Analyzer - H-E1 EXISTENCE PoC

Tests whether Shannon entropy can be reliably computed from pairwise preference
datasets. Analyzes Anthropic-HH to measure preference diversity across prompts.

MUST_WORK gate: ≥95% success rate, variance > 0, all values in [0, ln(2)] nats.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from datasets import load_dataset
from scipy.stats import entropy
from pathlib import Path
from datetime import datetime


class PreferenceEntropyAnalyzer:
    """Computes preference entropy from Anthropic-HH pairwise comparisons."""

    def __init__(self, dataset_name="Anthropic/hh-rlhf", sample_size=100, seed=1):
        self.dataset_name = dataset_name
        self.sample_size = sample_size
        self.seed = seed
        self.dataset = None
        self.results = []

        np.random.seed(self.seed)

    def load_dataset(self):
        """Load Anthropic-HH dataset via HuggingFace."""
        print(f"Loading dataset: {self.dataset_name}")
        self.dataset = load_dataset(self.dataset_name)
        train_size = len(self.dataset['train'])
        test_size = len(self.dataset.get('test', []))
        print(f"Dataset loaded: train={train_size}, test={test_size}")
        return self.dataset

    def sample_prompts(self):
        """Sample n prompts from dataset with fixed seed."""
        train_data = self.dataset['train']

        # Group examples by prompt context (first 200 chars of chosen text)
        prompt_groups = defaultdict(list)
        for idx, example in enumerate(train_data):
            prompt_key = example['chosen'][:200]
            prompt_groups[prompt_key].append(example)

        # Sample prompts with enough comparisons (>=5)
        valid_prompts = {k: v for k, v in prompt_groups.items() if len(v) >= 5}
        prompt_keys = list(valid_prompts.keys())

        if len(prompt_keys) < self.sample_size:
            print(f"Warning: Only {len(prompt_keys)} prompts with >=5 comparisons")
            sampled_keys = prompt_keys
        else:
            sampled_indices = np.random.choice(len(prompt_keys),
                                               size=self.sample_size,
                                               replace=False)
            sampled_keys = [prompt_keys[i] for i in sampled_indices]

        sampled_prompts = {k: valid_prompts[k] for k in sampled_keys}
        print(f"Sampled {len(sampled_prompts)} prompts (seed={self.seed})")
        return sampled_prompts

    def aggregate_preferences(self, prompt_examples):
        """Aggregate chosen/rejected counts from pairwise comparisons."""
        # For binary pairwise comparisons: chosen vs rejected
        # Count frequency of each option being chosen
        chosen_count = len(prompt_examples)  # Each example has a chosen response
        rejected_count = len(prompt_examples)  # And a rejected response

        # Binary distribution: [chosen preference, rejected preference]
        # In pairwise format, we treat each pair as one vote for chosen
        return np.array([chosen_count, rejected_count], dtype=float)

    def compute_entropy(self, preference_counts):
        """Compute Shannon entropy from preference distribution.

        Returns entropy in nats (natural log base), or None if insufficient data.
        """
        if preference_counts.sum() < 5:
            return None

        # scipy.stats.entropy handles normalization automatically
        H = entropy(preference_counts, base=np.e)
        return H

    def analyze_dataset(self):
        """Main analysis: compute entropy for sampled prompts."""
        self.load_dataset()
        sampled_prompts = self.sample_prompts()

        self.results = []
        for prompt_id, examples in sampled_prompts.items():
            preference_counts = self.aggregate_preferences(examples)
            H = self.compute_entropy(preference_counts)

            if H is not None:
                self.results.append({
                    'prompt_id': prompt_id[:50],  # Truncate for readability
                    'entropy': float(H),
                    'num_comparisons': int(preference_counts.sum() / 2)
                })

        print(f"Computed entropy for {len(self.results)} prompts")
        return self.results

    def compute_metrics(self, results):
        """Calculate evaluation metrics."""
        entropy_values = [r['entropy'] for r in results]

        # Primary metrics
        success_count = len(results)
        success_rate = (success_count / self.sample_size) * 100

        # Entropy statistics
        entropy_mean = float(np.mean(entropy_values)) if entropy_values else 0.0
        entropy_std = float(np.std(entropy_values)) if entropy_values else 0.0
        entropy_min = float(np.min(entropy_values)) if entropy_values else 0.0
        entropy_max = float(np.max(entropy_values)) if entropy_values else 0.0

        # Validation checks
        max_binary_entropy = np.log(2)  # ln(2) ≈ 0.693 nats
        all_in_range = all(0 <= e <= max_binary_entropy for e in entropy_values)
        variance_positive = entropy_std > 0

        metrics = {
            'success_rate': success_rate,
            'success_count': success_count,
            'sample_size': self.sample_size,
            'entropy_mean': entropy_mean,
            'entropy_std': entropy_std,
            'entropy_min': entropy_min,
            'entropy_max': entropy_max,
            'entropy_range': [entropy_min, entropy_max],
            'all_in_valid_range': all_in_range,
            'variance_positive': variance_positive,
            'max_binary_entropy': float(max_binary_entropy),
            'gate_passed': success_rate >= 95 and variance_positive and all_in_range
        }

        print("\nMetrics:")
        print(f"  Success rate: {success_rate:.1f}% ({success_count}/{self.sample_size})")
        print(f"  Mean entropy: {entropy_mean:.4f} nats")
        print(f"  Std entropy: {entropy_std:.4f} nats")
        print(f"  Range: [{entropy_min:.4f}, {entropy_max:.4f}] nats")
        print(f"  Valid range: {all_in_range}")
        print(f"  Variance > 0: {variance_positive}")
        print(f"  MUST_WORK gate: {'PASS' if metrics['gate_passed'] else 'FAIL'}")

        return metrics

    def generate_figures(self, results, metrics, output_dir="../figures"):
        """Generate visualization figures."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        entropy_values = [r['entropy'] for r in results]

        # Figure 1: Gate metrics comparison (MANDATORY)
        fig, ax = plt.subplots(figsize=(8, 6))
        categories = ['Success Rate\n(≥95%)', 'Variance\n(>0)', 'Valid Range\n([0, ln(2)])']
        targets = [95.0, 0.01, 1.0]  # Target values
        actuals = [
            metrics['success_rate'],
            metrics['entropy_std'],
            1.0 if metrics['all_in_valid_range'] else 0.0
        ]

        x = np.arange(len(categories))
        width = 0.35
        ax.bar(x - width/2, targets, width, label='Target', alpha=0.7, color='green')
        ax.bar(x + width/2, actuals, width, label='Actual', alpha=0.7, color='blue')
        ax.set_ylabel('Value')
        ax.set_title('Gate Metrics: Target vs Actual')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/gate_metrics.png", dpi=150)
        plt.close()

        # Figure 2: Entropy distribution histogram
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(entropy_values, bins=20, edgecolor='black', alpha=0.7)
        ax.set_xlabel('Entropy (nats)')
        ax.set_ylabel('Frequency (count of prompts)')
        ax.set_title('Distribution of Preference Entropy')
        ax.axvline(metrics['entropy_mean'], color='red', linestyle='--',
                   label=f"Mean: {metrics['entropy_mean']:.4f}")
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/entropy_histogram.png", dpi=150)
        plt.close()

        # Figure 3: Entropy vs prompt index scatter
        fig, ax = plt.subplots(figsize=(8, 6))
        indices = range(len(entropy_values))
        ax.scatter(indices, entropy_values, alpha=0.6, s=30)
        ax.set_xlabel('Prompt Index')
        ax.set_ylabel('Entropy (nats)')
        ax.set_title('Entropy vs Prompt Index')
        ax.axhline(metrics['entropy_mean'], color='red', linestyle='--',
                   label=f"Mean: {metrics['entropy_mean']:.4f}")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/entropy_scatter.png", dpi=150)
        plt.close()

        # Figure 4: Success rate pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        success_count = metrics['success_count']
        failed_count = self.sample_size - success_count
        sizes = [success_count, failed_count]
        labels = [f"Computed ({success_count})", f"Failed ({failed_count})"]
        colors = ['green', 'red']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('Entropy Computation Success Rate')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/success_rate_pie.png", dpi=150)
        plt.close()

        print(f"\nGenerated 4 figures in {output_dir}/")

    def save_results(self, results, metrics, output_path="../h-e1_results.json"):
        """Save analysis results to JSON."""
        output_data = {
            'experiment': 'H-E1 Preference Entropy Analysis',
            'hypothesis': 'Base models produce outputs with preference entropy H_base ≥ 1.8 nats',
            'dataset': self.dataset_name,
            'sample_size': self.sample_size,
            'seed': self.seed,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'metrics': metrics,
            'results': results
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Results saved to {output_path}")


def main():
    """Run preference entropy analysis."""
    print("=" * 60)
    print("H-E1: Preference Entropy Measurement (EXISTENCE PoC)")
    print("=" * 60)

    analyzer = PreferenceEntropyAnalyzer(
        dataset_name="Anthropic/hh-rlhf",
        sample_size=100,
        seed=1
    )

    results = analyzer.analyze_dataset()
    metrics = analyzer.compute_metrics(results)
    analyzer.generate_figures(results, metrics)
    analyzer.save_results(results, metrics, output_path="../h-e1_results.json")

    print("\n" + "=" * 60)
    print("Analysis complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
