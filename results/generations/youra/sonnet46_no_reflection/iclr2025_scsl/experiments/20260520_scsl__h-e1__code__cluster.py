"""K-means clustering probe with AMI and purity metrics."""
import numpy as np
from typing import Tuple, Dict
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score


def run_kmeans(embeddings: np.ndarray, k: int = 2,
               n_init: int = 10, seed: int = 42) -> np.ndarray:
    kmeans = KMeans(n_clusters=k, n_init=n_init, random_state=seed)
    return kmeans.fit_predict(embeddings).astype(np.int32)


def worst_cluster_purity(group_ids: np.ndarray, cluster_assignments: np.ndarray,
                          k: int) -> float:
    purities = []
    for c in range(k):
        mask = cluster_assignments == c
        if mask.sum() == 0:
            continue
        counts = np.bincount(group_ids[mask])
        purities.append(counts.max() / mask.sum())
    return float(min(purities))


def run_kmeans_probe(embeddings: np.ndarray, group_ids: np.ndarray,
                     k: int = 2, n_init: int = 10, seed: int = 42
                     ) -> Tuple[float, float, np.ndarray]:
    cluster_assignments = run_kmeans(embeddings, k, n_init, seed)
    ami = float(adjusted_mutual_info_score(group_ids, cluster_assignments))
    wp = worst_cluster_purity(group_ids, cluster_assignments, k)
    return ami, wp, cluster_assignments


def compute_random_baseline(group_ids: np.ndarray, k: int = 2,
                             seed: int = 0) -> Tuple[float, float]:
    rng = np.random.RandomState(seed)
    random_assignments = rng.randint(0, k, size=len(group_ids)).astype(np.int32)
    ami_random = float(adjusted_mutual_info_score(group_ids, random_assignments))
    purity_random = worst_cluster_purity(group_ids, random_assignments, k)
    return ami_random, purity_random


def verify_mechanism_activated(embeddings: np.ndarray, cluster_assignments: np.ndarray,
                                group_ids: np.ndarray, k: int = 2
                                ) -> Tuple[bool, Dict[str, bool]]:
    ami_actual = float(adjusted_mutual_info_score(group_ids, cluster_assignments))
    rng = np.random.RandomState(0)
    ami_random = float(adjusted_mutual_info_score(
        group_ids, rng.randint(0, k, size=len(group_ids))))
    indicators = {
        'embedding_shape_correct': bool(embeddings.shape[1] == 2048),
        'clusters_non_trivial': bool(all((cluster_assignments == c).sum() > 10 for c in range(k))),
        'ami_above_chance': bool(ami_actual > ami_random + 0.1),
        'ami_passes_threshold': bool(ami_actual >= 0.5),
    }
    return all(indicators.values()), indicators


def probe(embeddings_path: str, group_ids_path: str, k: int = 2) -> Dict:
    embeddings = np.load(embeddings_path)
    group_ids = np.load(group_ids_path)
    ami, wp, assignments = run_kmeans_probe(embeddings, group_ids, k)
    ami_random, purity_random = compute_random_baseline(group_ids, k)
    mechanism_ok, _ = verify_mechanism_activated(embeddings, assignments, group_ids, k)
    return {
        'ami': ami,
        'worst_purity': wp,
        'ami_random': ami_random,
        'purity_random': purity_random,
        'mechanism_ok': bool(mechanism_ok),
    }


def main():
    import argparse, json
    parser = argparse.ArgumentParser()
    parser.add_argument('--embeddings', required=True)
    parser.add_argument('--group_ids', required=True)
    parser.add_argument('--k', type=int, default=2)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    result = probe(args.embeddings, args.group_ids, args.k)
    print(json.dumps(result, indent=2))
    if args.output:
        import yaml
        with open(args.output, 'w') as f:
            yaml.dump(result, f)


if __name__ == '__main__':
    main()
