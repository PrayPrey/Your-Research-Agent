"""k-center greedy subset selection."""
import numpy as np
import time
from scipy.spatial.distance import cdist
import yaml


def load_config(config_path: str = "config/experiment_config.yaml") -> dict:
    """Load experiment config."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def k_center_greedy(
    embeddings: np.ndarray,
    k: int,
    seed: int = 42,
    metric: str = "cosine"
) -> tuple[np.ndarray, float]:
    """
    Select k diverse samples maximizing min distance (farthest-point sampling).
    embeddings: [N, D] -> selected indices: [k]
    Returns: (indices, selection_time)
    """
    np.random.seed(seed)
    n = len(embeddings)

    assert k <= n, f"k={k} > n={n}"

    print(f"Running k-center greedy: k={k}, n={n}, metric={metric}")
    start = time.time()

    # Random initialization
    selected = [np.random.randint(n)]

    # Compute distances from first point
    distances = cdist([embeddings[selected[0]]], embeddings, metric=metric)[0]

    # Greedy selection (iterative farthest point)
    for i in range(k - 1):
        farthest_idx = np.argmax(distances)
        selected.append(farthest_idx)

        # Update distances
        new_distances = cdist([embeddings[farthest_idx]], embeddings, metric=metric)[0]
        distances = np.minimum(distances, new_distances)

        if (i + 1) % 500 == 0:
            print(f"  Selected {i + 1}/{k} samples")

    selection_time = time.time() - start
    print(f"✓ Selected {k} samples in {selection_time:.2f}s")

    return np.array(selected), selection_time


def compute_diversity(embeddings: np.ndarray, indices: np.ndarray) -> float:
    """Compute average pairwise cosine distance in selected subset."""
    subset = embeddings[indices]
    distances = cdist(subset, subset, metric='cosine')
    # Exclude diagonal (self-distances = 0)
    mask = ~np.eye(len(indices), dtype=bool)
    avg_distance = distances[mask].mean()
    return avg_distance


def select_all_subsets(config: dict) -> dict:
    """
    Run k-center greedy for 3 stages × 3 sizes = 9 configurations.
    Returns: {stage_kSize: {"indices_path": str, "time": float, "diversity": float}}
    """
    results = {}

    for stage in ["early", "mid", "late"]:
        embeddings_path = f"{config['paths']['embeddings_dir']}{stage}_embeddings.npy"
        embeddings = np.load(embeddings_path)
        print(f"\nLoaded {stage} embeddings: {embeddings.shape}")

        for k in config["dataset"]["subset_sizes"]:
            indices, selection_time = k_center_greedy(
                embeddings=embeddings,
                k=k,
                seed=config["subset_selection"]["seed"],
                metric=config["subset_selection"]["distance_metric"]
            )

            diversity = compute_diversity(embeddings, indices)

            output_path = f"{config['paths']['subsets_dir']}{stage}_k{k}_indices.npy"
            np.save(output_path, indices)
            print(f"✓ Saved indices to {output_path} (diversity={diversity:.4f})")

            results[f"{stage}_k{k}"] = {
                "indices_path": output_path,
                "time": selection_time,
                "diversity": diversity
            }

    return results


if __name__ == "__main__":
    config = load_config()
    results = select_all_subsets(config)

    print("\n=== Subset Selection Summary ===")
    for condition, info in results.items():
        print(f"{condition:15s}: time={info['time']:.2f}s, diversity={info['diversity']:.4f}")

    print(f"\n✓ All subsets selected")
