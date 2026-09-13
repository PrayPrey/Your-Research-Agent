"""data_loader.py — A-1: Load H-E1/H-M1/H-M2 inputs and build analysis vectors."""
import json
import os
from pathlib import Path
from typing import Optional
import numpy as np

BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]

# Literature-based contamination estimates (Lee et al. 2022, GPT-4 TR)
# midpoints of reported ranges; used when H-M1 full results unavailable
LITERATURE_CONTAMINATION = {
    "mmlu": 0.055,         # 3-8% → midpoint 5.5%
    "hellaswag": 0.200,    # 15-25% → midpoint 20%
    "arc_challenge": 0.085, # 5-12% → midpoint 8.5%
    "winogrande": 0.025,   # 1-4% → midpoint 2.5%
}


def load_accuracy_differentials(h_e1_folder: str) -> dict[str, dict[str, float]]:
    """Load per-benchmark accuracy differentials from H-E1 results_matrix.json.
    Returns {model_size: {benchmark: dedup_acc - pile_acc}}
    """
    matrix_path = Path(h_e1_folder) / "results_matrix.json"
    if not matrix_path.exists():
        raise FileNotFoundError(f"H-E1 results_matrix.json not found: {matrix_path}")

    with open(matrix_path) as f:
        matrix = json.load(f)

    differentials = {}
    for model_size in MODEL_SIZES:
        if model_size not in matrix:
            raise ValueError(f"Model size '{model_size}' missing from results_matrix.json")
        pile = matrix[model_size]["pile"]
        dedup = matrix[model_size]["dedup"]
        differentials[model_size] = {
            b: dedup[b] - pile[b] for b in BENCHMARKS
        }
    return differentials


def load_contamination_estimates(h_m1_folder: str) -> dict[str, float]:
    """Load per-benchmark 13-gram contamination estimates from H-M1.
    Falls back to literature values if H-M1 full results not yet available.
    Returns {benchmark: overlap_rate}
    """
    # Try real H-M1 results first
    for fname in ["contamination_estimates.json", "overlap_estimates.json", "results/contamination.json"]:
        path = Path(h_m1_folder) / fname
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            # Validate structure
            if all(b in data for b in BENCHMARKS):
                print(f"Loaded H-M1 contamination estimates from {path}")
                return {b: float(data[b]) for b in BENCHMARKS}

    # Fall back to literature-based estimates
    print("H-M1 full results not available; using literature-based contamination estimates "
          "(Lee et al. 2022, GPT-4 TR). Estimates: "
          + str({b: f"{v:.3f}" for b, v in LITERATURE_CONTAMINATION.items()}))
    return dict(LITERATURE_CONTAMINATION)


def load_mink_differentials(h_m2_folder: str) -> Optional[dict[str, float]]:
    """Load per-benchmark min-k% differentials from H-M2 (secondary estimator).
    Returns None if H-M2 results not available or not significant.
    """
    exp_path = Path(h_m2_folder) / "experiment_results.json"
    if not exp_path.exists():
        return None

    with open(exp_path) as f:
        data = json.load(f)

    # Extract per-benchmark mean differential from stats array
    stats = data.get("stats", [])
    if not stats:
        return None

    # Compute per-benchmark mean differential across model sizes
    bench_diffs: dict[str, list[float]] = {b: [] for b in BENCHMARKS}
    for entry in stats:
        bench = entry.get("benchmark")
        diff = entry.get("differential")
        if bench in bench_diffs and diff is not None:
            bench_diffs[bench].append(diff)

    result = {}
    for b in BENCHMARKS:
        vals = bench_diffs[b]
        if vals:
            result[b] = float(np.mean(vals))

    if len(result) < 4:
        return None

    print(f"Loaded H-M2 min-k% differentials: {result}")
    return result


def build_analysis_vectors(
    acc_diff: dict[str, dict[str, float]],
    cont_est: dict[str, float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build flattened 16-obs vectors plus diff_matrix.
    Returns: (cont_repeated (16,), diff_flat (16,), diff_matrix (4,4))
    """
    cont_vec = np.array([cont_est[b] for b in BENCHMARKS])  # (4,)
    diff_matrix = np.array([
        [acc_diff[m][b] for b in BENCHMARKS]
        for m in MODEL_SIZES
    ])  # (4 sizes, 4 benchmarks)

    cont_repeated = np.tile(cont_vec, len(MODEL_SIZES))  # (16,)
    diff_flat = diff_matrix.flatten()  # (16,)
    return cont_repeated, diff_flat, diff_matrix


def validate_inputs(
    acc_diff: dict[str, dict[str, float]],
    cont_est: dict[str, float],
) -> None:
    """Validate that all required keys exist and no NaN values."""
    for m in MODEL_SIZES:
        if m not in acc_diff:
            raise ValueError(f"Missing model_size '{m}' in acc_diff")
        for b in BENCHMARKS:
            if b not in acc_diff[m]:
                raise ValueError(f"Missing benchmark '{b}' for model '{m}' in acc_diff")
            v = acc_diff[m][b]
            if np.isnan(v):
                raise ValueError(f"NaN in acc_diff[{m}][{b}]")
    for b in BENCHMARKS:
        if b not in cont_est:
            raise ValueError(f"Missing benchmark '{b}' in cont_est")
        if np.isnan(cont_est[b]):
            raise ValueError(f"NaN in cont_est[{b}]")


if __name__ == "__main__":
    base = Path(__file__).parent.parent
    h_e1 = str(base / "../h-e1")
    h_m1 = str(base / "../h-m1")
    h_m2 = str(base / "../h-m2")

    acc_diff = load_accuracy_differentials(h_e1)
    cont_est = load_contamination_estimates(h_m1)
    validate_inputs(acc_diff, cont_est)

    cont_rep, diff_flat, diff_matrix = build_analysis_vectors(acc_diff, cont_est)
    print(f"cont_repeated shape: {cont_rep.shape}")
    print(f"diff_flat shape: {diff_flat.shape}")
    print(f"diff_matrix shape: {diff_matrix.shape}")
    print("Data loader OK")
