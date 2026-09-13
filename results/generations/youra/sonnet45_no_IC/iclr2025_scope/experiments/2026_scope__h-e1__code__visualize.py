#!/usr/bin/env python3
"""
H-E1: Generate Visualization Figures
Creates 4 required plots for benchmark collection validation.
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter

sns.set_style("whitegrid")

def load_benchmarks():
    """Load benchmarks from JSONL file."""
    benchmarks = []
    with open('output/benchmarks_collection.jsonl', 'r') as f:
        for line in f:
            benchmarks.append(json.loads(line))
    return benchmarks

def plot_domain_distribution(benchmarks, output_dir):
    """Bar chart: Benchmark count by domain."""
    domains = [b['domain'] for b in benchmarks]
    domain_counts = Counter(domains)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(domain_counts.keys(), domain_counts.values(), color='steelblue', edgecolor='black')

    # Highlight domains with ≥10 benchmarks
    for i, (domain, count) in enumerate(domain_counts.items()):
        if count >= 10:
            bars[i].set_color('green')

    plt.axhline(y=10, color='red', linestyle='--', label='Minimum threshold (10)')
    plt.xlabel('Domain', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Benchmarks', fontsize=12, fontweight='bold')
    plt.title('Benchmark Count by Domain', fontsize=14, fontweight='bold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / 'domain_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated domain_distribution.png")

def plot_source_breakdown(benchmarks, output_dir):
    """Pie chart: Benchmark sources breakdown."""
    sources = [b['source_paper'] for b in benchmarks]
    source_counts = Counter(sources)

    plt.figure(figsize=(10, 8))
    colors = sns.color_palette("Set2", len(source_counts))
    plt.pie(source_counts.values(), labels=source_counts.keys(), autopct='%1.1f%%',
            colors=colors, startangle=90, textprops={'fontsize': 11})
    plt.title('Benchmark Sources Breakdown', fontsize=14, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_dir / 'source_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated source_breakdown.png")

def plot_method_family_distribution(benchmarks, output_dir):
    """Stacked bar chart: Method family distribution by domain."""
    from collections import defaultdict

    # Collect family counts per domain
    domain_families = defaultdict(lambda: Counter())

    for b in benchmarks:
        domain = b['domain']
        for method_data in b['method_rankings'].values():
            family = method_data['family']
            domain_families[domain][family] += 1

    # Prepare data for stacked bar chart
    domains = sorted(domain_families.keys())
    families = ['Linear', 'Polynomial', 'RNN', 'Augmentation']

    data = {family: [] for family in families}
    for domain in domains:
        for family in families:
            data[family].append(domain_families[domain][family])

    # Plot stacked bars
    plt.figure(figsize=(12, 6))
    bottom = [0] * len(domains)

    colors = {'Linear': 'skyblue', 'Polynomial': 'orange', 'RNN': 'green', 'Augmentation': 'purple'}

    for family in families:
        plt.bar(domains, data[family], bottom=bottom, label=family, color=colors[family], edgecolor='black')
        bottom = [b + d for b, d in zip(bottom, data[family])]

    plt.xlabel('Domain', fontsize=12, fontweight='bold')
    plt.ylabel('Method Count', fontsize=12, fontweight='bold')
    plt.title('Method Family Distribution by Domain', fontsize=14, fontweight='bold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / 'method_families.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated method_families.png")

def plot_completeness_heatmap(benchmarks, output_dir):
    """Heatmap: Data completeness by source."""
    from collections import defaultdict
    import numpy as np

    # Required fields
    fields = ['sample_size', 'dimensionality', 'num_classes', 'method_rankings']

    # Collect completeness data
    source_completeness = defaultdict(lambda: {field: 0 for field in fields})
    source_totals = Counter()

    for b in benchmarks:
        source = b['source_paper']
        source_totals[source] += 1

        for field in fields:
            value = b.get(field)
            if value is not None and (not isinstance(value, dict) or len(value) > 0):
                source_completeness[source][field] += 1

    # Calculate percentages
    sources = sorted(source_completeness.keys())
    data = []

    for source in sources:
        row = []
        for field in fields:
            count = source_completeness[source][field]
            total = source_totals[source]
            percentage = (count / total * 100) if total > 0 else 0
            row.append(percentage)
        data.append(row)

    data = np.array(data)

    # Plot heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(data, annot=True, fmt='.0f', cmap='RdYlGn', cbar_kws={'label': 'Completeness (%)'},
                xticklabels=fields, yticklabels=sources, vmin=0, vmax=100)
    plt.title('Data Completeness by Source', fontsize=14, fontweight='bold')
    plt.xlabel('Field', fontsize=12, fontweight='bold')
    plt.ylabel('Source', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'completeness_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated completeness_heatmap.png")

def main():
    """Generate all visualization figures."""
    print("="*60)
    print("Generating Visualizations")
    print("="*60)

    # Load data
    benchmarks = load_benchmarks()
    print(f"Loaded {len(benchmarks)} benchmarks\n")

    # Create figures directory
    output_dir = Path("../figures")
    output_dir.mkdir(exist_ok=True)

    # Generate plots
    plot_domain_distribution(benchmarks, output_dir)
    plot_source_breakdown(benchmarks, output_dir)
    plot_method_family_distribution(benchmarks, output_dir)
    plot_completeness_heatmap(benchmarks, output_dir)

    print(f"\n✓ All figures saved to {output_dir}")
    print("="*60)

if __name__ == '__main__':
    main()
