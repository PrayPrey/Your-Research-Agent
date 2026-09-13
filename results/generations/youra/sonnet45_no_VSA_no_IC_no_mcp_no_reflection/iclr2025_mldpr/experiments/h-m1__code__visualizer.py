import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from typing import Optional

class ConvergenceVisualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_timeline(
        self,
        benchmark: str,
        dates: pd.Series,
        std_values: pd.Series,
        threshold: float,
        convergence_date: Optional[str] = None
    ) -> None:
        plt.figure(figsize=(10, 6))
        plt.plot(dates.index.astype(str), std_values.values, marker='o', label='Rolling Std')
        plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold ({threshold*100}%)')

        if convergence_date:
            plt.axvline(x=convergence_date, color='g', linestyle=':', label='Convergence')
            plt.axvspan(convergence_date, dates.index[-1].strftime('%Y-%m'), alpha=0.2, color='g')

        plt.xlabel('Month')
        plt.ylabel('Rolling Std (6-month window)')
        plt.title(f'{benchmark.upper()} Score Convergence Detection')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / f'convergence_timeline_{benchmark}.png')
        plt.close()

    def plot_gate_metrics(self, target_benchmarks: int, actual_benchmarks: int) -> None:
        categories = ['Target', 'Actual']
        values = [target_benchmarks, actual_benchmarks]
        colors = ['blue', 'green' if actual_benchmarks >= target_benchmarks else 'red']

        plt.figure(figsize=(6, 6))
        plt.bar(categories, values, color=colors)
        plt.ylabel('Benchmarks Converged')
        plt.title('Gate Metrics: Convergence Detection')
        plt.ylim(0, 3)
        for i, v in enumerate(values):
            plt.text(i, v + 0.1, str(v), ha='center', fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_metrics.png')
        plt.close()
