from typing import Dict, List
import numpy as np
from sklearn.metrics import roc_auc_score


def macro_auc_ovr(y_true: np.ndarray, probs: np.ndarray) -> float:
    """One-vs-rest macro AUC for multiclass."""
    try:
        return roc_auc_score(y_true, probs, multi_class='ovr', average='macro')
    except ValueError:
        return 0.5  # fallback if not all classes present


def gap_closure(dws_aucs: Dict[float, float], nft_aucs: Dict[float, float]) -> Dict[float, float]:
    """DWS - NFT per fraction."""
    return {f: dws_aucs[f] - nft_aucs[f] for f in dws_aucs}


def aggregate_stats(results: Dict) -> Dict:
    """Aggregate per-seed results into mean/std."""
    stats = {}
    for fraction, model_results in results.items():
        stats[fraction] = {}
        for model_type, runs in model_results.items():
            aucs = [r['auc'] for r in runs]
            times = [r['train_time'] for r in runs]
            stats[fraction][model_type] = {
                'auc_mean': np.mean(aucs),
                'auc_std': np.std(aucs),
                'time_mean': np.mean(times),
            }
    return stats


def check_success_criteria(stats: Dict, cfg) -> Dict[str, bool]:
    """Check PRD success criteria."""
    dws_gt_nft_at_25pct = stats[0.25]['dws']['auc_mean'] > stats[0.25]['nft']['auc_mean']

    gap_25 = stats[0.25]['dws']['auc_mean'] - stats[0.25]['nft']['auc_mean']
    gap_100 = stats[1.0]['dws']['auc_mean'] - stats[1.0]['nft']['auc_mean']
    gap_narrows_at_100pct = abs(gap_100) < abs(gap_25)

    both_gt_mlp = all(
        stats[f][m]['auc_mean'] > stats[f]['mlp']['auc_mean']
        for f in cfg.fractions for m in ('dws', 'nft')
    )

    return {
        'dws_gt_nft_at_25pct': dws_gt_nft_at_25pct,
        'gap_narrows_at_100pct': gap_narrows_at_100pct,
        'both_gt_mlp': both_gt_mlp,
    }
