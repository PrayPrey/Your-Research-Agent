from typing import List, Dict, Tuple
import numpy as np
from sklearn.metrics import roc_auc_score, mean_squared_error, r2_score
from scipy import stats

from config import ExperimentResult


def compute_auc(preds: np.ndarray, labels: np.ndarray) -> float:
    probs = 1 / (1 + np.exp(-np.clip(preds, -500, 500)))
    return roc_auc_score(labels, probs)


def compute_rmse_r2(preds: np.ndarray, targets: np.ndarray) -> Tuple[float, float]:
    rmse = np.sqrt(mean_squared_error(targets, preds))
    r2 = r2_score(targets, preds)
    return rmse, r2


def run_interaction_anova(results: List[ExperimentResult]) -> Dict:
    from collections import defaultdict

    task_arch_values = defaultdict(list)
    for r in results:
        task_arch_values[(r.task, r.architecture)].append(r.metric_value)

    all_values = []
    for v in task_arch_values.values():
        all_values.extend(v)
    mean_val = np.mean(all_values)
    std_val = np.std(all_values) if np.std(all_values) > 1e-8 else 1.0

    normalized = {}
    for key, values in task_arch_values.items():
        normalized[key] = [(v - mean_val) / std_val for v in values]

    tasks = list(set(r.task for r in results))
    archs = list(set(r.architecture for r in results))

    groups = []
    for task in tasks:
        for arch in archs:
            key = (task, arch)
            if key in normalized:
                groups.append(normalized[key])

    if len(groups) >= 2:
        f_stat, p_value = stats.f_oneway(*groups)
    else:
        f_stat, p_value = 0.0, 1.0

    return {
        "f_stat": float(f_stat),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05)
    }


def aggregate_results(results: List[ExperimentResult]) -> Dict:
    from collections import defaultdict

    grouped = defaultdict(list)
    for r in results:
        grouped[(r.task, r.architecture)].append(r.metric_value)

    stats_dict = {}
    for (task, arch), values in grouped.items():
        stats_dict[f"{task}_{arch}"] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "values": values
        }

    return stats_dict


def check_success_criteria(stats: Dict, anova_result: Dict) -> Dict[str, bool]:
    backdoor_dws = stats.get("backdoor_dws", {}).get("mean", 0)
    backdoor_nft = stats.get("backdoor_nft", {}).get("mean", 0)
    backdoor_mlp = stats.get("backdoor_mlp", {}).get("mean", 0)

    accuracy_dws = stats.get("accuracy_dws", {}).get("mean", float("inf"))
    accuracy_nft = stats.get("accuracy_nft", {}).get("mean", float("inf"))
    accuracy_mlp = stats.get("accuracy_mlp", {}).get("mean", float("inf"))

    dws_beats_nft_backdoor = backdoor_dws > backdoor_nft
    nft_beats_dws_accuracy = accuracy_nft < accuracy_dws

    dws_beats_mlp_either = (backdoor_dws > backdoor_mlp) or (accuracy_dws < accuracy_mlp)
    nft_beats_mlp_either = (backdoor_nft > backdoor_mlp) or (accuracy_nft < accuracy_mlp)
    equivariant_beats_mlp = dws_beats_mlp_either or nft_beats_mlp_either

    return {
        "dws_beats_nft_backdoor": dws_beats_nft_backdoor,
        "nft_beats_dws_accuracy": nft_beats_dws_accuracy,
        "equivariant_beats_mlp": equivariant_beats_mlp,
        "interaction_significant": anova_result.get("significant", False)
    }
