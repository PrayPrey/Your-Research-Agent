from typing import List
import pandas as pd
from .loader import instrumented_load_dataset
from .telemetry import TelemetryLogger

class BenchmarkHarness:
    def __init__(
        self,
        datasets: List[str],
        runs_per_dataset: int = 10,
        telemetry: TelemetryLogger = None
    ):
        self.datasets = datasets
        self.runs_per_dataset = runs_per_dataset
        self.telemetry = telemetry or TelemetryLogger()

    def run_benchmarks(self) -> pd.DataFrame:
        results = []
        for item in self.datasets:
            if isinstance(item, tuple):
                dataset, config = item
            else:
                dataset, config = item, None

            for run in range(self.runs_per_dataset):
                try:
                    _, metadata = instrumented_load_dataset(
                        dataset,
                        self.telemetry,
                        config=config,
                        split="train"
                    )
                    results.append({
                        'dataset': dataset,
                        'run': run,
                        'baseline_ms': metadata['baseline_ms'],
                        'instrumented_ms': metadata['telemetry_ms'],
                        'overhead_pct': metadata['overhead_pct'],
                        'telemetry_success': metadata['telemetry_success']
                    })
                except Exception as e:
                    print(f"Failed {dataset} run {run}: {e}")

        return pd.DataFrame(results)

    def aggregate_results(self, df: pd.DataFrame):
        return df.groupby('dataset')['overhead_pct'].agg(['mean', 'std', 'min', 'max']).to_dict()

    def save_results(self, df: pd.DataFrame, path: str):
        df.to_csv(path, index=False)
