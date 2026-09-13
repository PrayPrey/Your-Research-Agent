"""
Visualizer for h-m2 temporal lead time validation.
Timeline, distribution, and citation curve plots.
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List
from config import FIGURES_DIR, DPI, FIGSIZE, LEAD_TIME_THRESHOLD


class TemporalVisualizer:
    """Generate visualizations for temporal lead time analysis."""

    def __init__(self, output_dir: Path = FIGURES_DIR):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_timeline(self, lead_times: List[dict]) -> None:
        """
        Plot saturation dates vs adoption dates timeline.

        Args:
            lead_times: List of lead time results with dates
        """
        fig, ax = plt.subplots(figsize=FIGSIZE)

        benchmarks = []
        sat_dates = []
        adopt_dates = []
        shifts = []

        for lt in lead_times:
            benchmarks.append(lt['benchmark'])
            sat_dates.append(pd.to_datetime(lt['saturation_date']))
            adopt_dates.append(pd.to_datetime(lt['adoption_date']))
            shifts.append(lt['shift'])

        # Plot timeline arrows
        y_positions = range(len(benchmarks))

        for i, (benchmark, sat, adopt, shift) in enumerate(zip(benchmarks, sat_dates, adopt_dates, shifts)):
            # Saturation point
            ax.scatter(sat, i, color='blue', s=100, marker='o', label='Saturation' if i == 0 else '')

            # Adoption point
            ax.scatter(adopt, i, color='red', s=100, marker='s', label='Adoption' if i == 0 else '')

            # Arrow showing lead time
            ax.annotate('', xy=(adopt, i), xytext=(sat, i),
                       arrowprops=dict(arrowstyle='->', color='gray', lw=2))

            # Labels
            ax.text(sat, i, f"  {benchmark}", va='center', ha='right', fontsize=9)
            ax.text(adopt, i, f"  {shift}", va='center', ha='left', fontsize=9)

        ax.set_yticks(y_positions)
        ax.set_yticklabels(['' for _ in y_positions])
        ax.set_xlabel('Date')
        ax.set_title('Temporal Lead Times: Saturation → Paradigm Shift Adoption')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        output_file = self.output_dir / "timeline.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=DPI)
        plt.close()

        print(f"Saved timeline plot to {output_file}")

    def plot_lead_time_distribution(self, lead_times: List[dict]) -> None:
        """
        Plot histogram of lead times with threshold line.

        Args:
            lead_times: List of lead time results
        """
        fig, ax = plt.subplots(figsize=(8, 5))

        lead_values = [lt['lead_time_months'] for lt in lead_times]

        # Histogram
        ax.hist(lead_values, bins=10, color='steelblue', alpha=0.7, edgecolor='black')

        # Threshold line
        ax.axvline(LEAD_TIME_THRESHOLD, color='red', linestyle='--',
                  linewidth=2, label=f'{LEAD_TIME_THRESHOLD}mo threshold')

        ax.set_xlabel('Lead Time (months)')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Lead Times')
        ax.legend()
        ax.grid(True, alpha=0.3)

        output_file = self.output_dir / "lead_time_histogram.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=DPI)
        plt.close()

        print(f"Saved histogram to {output_file}")

    def plot_citation_curves(self, citation_data: Dict[str, pd.DataFrame]) -> None:
        """
        Plot monthly citation time series for paradigm shift papers.

        Args:
            citation_data: Dict of {paper_id: citation_timeseries_df}
        """
        fig, ax = plt.subplots(figsize=FIGSIZE)

        for paper_id, df in citation_data.items():
            dates = pd.to_datetime(df['date'])
            citations = df['citations']
            ax.plot(dates, citations, marker='o', label=paper_id.upper(), linewidth=2)

        ax.set_xlabel('Date')
        ax.set_ylabel('Citations/Month')
        ax.set_title('Citation Curves for Paradigm Shift Papers')
        ax.legend()
        ax.grid(True, alpha=0.3)

        output_file = self.output_dir / "citation_curves.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=DPI)
        plt.close()

        print(f"Saved citation curves to {output_file}")


if __name__ == "__main__":
    # Load lead times
    results_dir = Path(__file__).parent.parent / "results"
    with open(results_dir / "lead_times.json") as f:
        lead_time_results = json.load(f)

    lead_times = lead_time_results['pairs']

    # Load citation data
    data_dir = Path(__file__).parent.parent / "data" / "citations"
    citation_data = {}

    for paper_id in ['gpt3', 'vit', 'llama']:
        cache_file = data_dir / f"{paper_id}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
            citation_data[paper_id] = pd.DataFrame(data)

    # Generate visualizations
    visualizer = TemporalVisualizer()
    visualizer.plot_timeline(lead_times)
    visualizer.plot_lead_time_distribution(lead_times)
    visualizer.plot_citation_curves(citation_data)

    print("\nAll visualizations generated")
