import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Tuple, List


class H_E1_DataLoader:
    def __init__(self, h_e1_results_path: Path):
        self.results_path = Path(h_e1_results_path).parent

    def load_correlation_matrix(self) -> Tuple[np.ndarray, List[str]]:
        # [3, 3], list of 3 strings
        with open(self.results_path / "correlation_results.json") as f:
            data = json.load(f)
        corr_matrix = np.array(data["correlation_matrix"])
        benchmark_names = data["benchmarks"]
        return corr_matrix, benchmark_names

    def compute_distance_matrix(self, corr_matrix: np.ndarray) -> np.ndarray:
        # [3, 3], symmetric, elements in [0, 2]
        return 1 - np.abs(corr_matrix)

    def load_benchmark_scores(self) -> pd.DataFrame:
        # [N, 6] with columns [model_name, size_stratum, params_billions, truthfulqa_score, advbench_score, bold_score]
        csv_path = self.results_path.parent / "data" / "benchmark_scores.csv"
        return pd.read_csv(csv_path)
