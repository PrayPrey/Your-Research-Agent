import os
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from config import HHIAnalysisConfig, VENUES, YEARS
from data_loader import load_pwc_data
from metrics import extract_venue_year_metrics, validate_hhi_scores

def plot_hhi_heatmap(metrics_df: pd.DataFrame, save_path: str) -> None:
    pivot = metrics_df.pivot(index='venue', columns='year', values='hhi')
    plt.figure(figsize=(10, 4))
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='YlOrRd', vmin=0, vmax=0.5)
    plt.title('HHI Concentration by Venue and Year')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_hhi_timeseries(metrics_df: pd.DataFrame, save_path: str) -> None:
    plt.figure(figsize=(10, 5))
    for venue in metrics_df['venue'].unique():
        subset = metrics_df[metrics_df['venue'] == venue].sort_values('year')
        plt.plot(subset['year'], subset['hhi'], marker='o', label=venue)
    plt.xlabel('Year')
    plt.ylabel('HHI')
    plt.title('HHI Concentration Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_coverage_bar(details: dict, save_path: str) -> None:
    plt.figure(figsize=(6, 4))
    labels = ['Valid', 'Missing']
    values = [details['valid_count'], details['expected_count'] - details['valid_count']]
    colors = ['#2ecc71', '#e74c3c']
    plt.bar(labels, values, color=colors)
    plt.ylabel('Venue-Year Combinations')
    plt.title(f"Coverage: {details['valid_count']}/{details['expected_count']}")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_entropy_vs_hhi(metrics_df: pd.DataFrame, save_path: str) -> None:
    plt.figure(figsize=(8, 6))
    for venue in metrics_df['venue'].unique():
        subset = metrics_df[metrics_df['venue'] == venue]
        plt.scatter(subset['hhi'], subset['entropy'], label=venue, s=60, alpha=0.7)
    plt.xlabel('HHI (Concentration)')
    plt.ylabel('Normalized Entropy (Diversity)')
    plt.title('Entropy vs HHI')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_top_datasets(papers_df: pd.DataFrame, save_path: str, top_n: int = 10) -> None:
    exploded = papers_df.explode('datasets')
    exploded = exploded[exploded['datasets'].notna() & (exploded['datasets'] != '')]
    counts = exploded.groupby(['venue', 'datasets']).size().reset_index(name='count')

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for i, venue in enumerate(VENUES):
        ax = axes[i]
        venue_data = counts[counts['venue'] == venue].nlargest(top_n, 'count')
        ax.barh(venue_data['datasets'], venue_data['count'])
        ax.set_xlabel('Count')
        ax.set_title(f'{venue} Top {top_n} Datasets')
        ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def main():
    config = HHIAnalysisConfig()
    os.makedirs(config.results_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    print("=" * 60)
    print("H-E1: HHI Concentration Analysis")
    print("=" * 60)

    print("\n[1/5] Loading PWC data...")
    papers_df = load_pwc_data()
    print(f"Loaded {len(papers_df)} filtered papers")

    print("\n[2/5] Computing HHI metrics...")
    metrics_df = extract_venue_year_metrics(papers_df, config.venues, list(range(config.year_start, config.year_end + 1)))
    print(f"Computed metrics for {len(metrics_df)} venue-year combinations")
    print(metrics_df.to_string())

    print("\n[3/5] Validating results...")
    success, details = validate_hhi_scores(metrics_df)
    print(f"Gate passed: {success}")
    print(f"Coverage: {details['coverage']*100:.1f}% ({details['valid_count']}/{details['expected_count']})")
    print(f"HHI range: [{details['min_hhi']:.4f}, {details['max_hhi']:.4f}]")
    print(f"HHI variance: {details['variance']:.6f}")

    print("\n[4/5] Saving results...")
    metrics_df.to_csv(config.results_csv, index=False)
    print(f"Saved metrics to {config.results_csv}")

    validation_output = {
        'gate_passed': success,
        'details': details,
        'provenance': {
            'hypothesis_id': 'H-E1',
            'data_source': 'pwc-archive',
            'venues': config.venues,
            'years': list(range(config.year_start, config.year_end + 1))
        }
    }
    with open(config.validation_json, 'w') as f:
        json.dump(validation_output, f, indent=2)
    print(f"Saved validation to {config.validation_json}")

    print("\n[5/5] Generating figures...")
    plot_hhi_heatmap(metrics_df, os.path.join(config.figures_dir, 'hhi_heatmap.png'))
    plot_hhi_timeseries(metrics_df, os.path.join(config.figures_dir, 'hhi_timeseries.png'))
    plot_coverage_bar(details, os.path.join(config.figures_dir, 'coverage_bar.png'))
    plot_entropy_vs_hhi(metrics_df, os.path.join(config.figures_dir, 'entropy_vs_hhi.png'))
    plot_top_datasets(papers_df, os.path.join(config.figures_dir, 'top_datasets.png'))
    print("Figures saved to", config.figures_dir)

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)

    return success, details, metrics_df

if __name__ == "__main__":
    main()
