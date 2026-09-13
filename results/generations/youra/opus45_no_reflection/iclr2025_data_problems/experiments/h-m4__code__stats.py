"""Statistical analysis for H-M4: paired t-tests and prediction evaluation."""
import numpy as np
from scipy.stats import ttest_rel
from typing import Dict, List, Tuple

def paired_ttest_across_seeds(auc_bert: List[float], auc_gpt2: List[float]) -> Tuple[float, float]:
    """Paired t-test: BERT vs GPT-2 AUCs across seeds. Returns (t_stat, p_value)."""
    if len(auc_bert) < 2 or len(auc_gpt2) < 2:
        return 0.0, 1.0
    t_stat, p_value = ttest_rel(auc_bert, auc_gpt2)
    return float(t_stat), float(p_value)

def aggregate_seed_results(per_seed_results: List[Dict]) -> Dict:
    """Aggregate results across seeds: mean +/- std per (method, arch, budget)."""
    aggregated = {}

    if not per_seed_results:
        return aggregated

    methods = list(per_seed_results[0].keys())
    for method in methods:
        aggregated[method] = {}
        archs = list(per_seed_results[0][method].keys())
        for arch in archs:
            aggregated[method][arch] = {}
            budgets = list(per_seed_results[0][method][arch].keys())
            for budget in budgets:
                aucs = []
                times = []
                for seed_result in per_seed_results:
                    if method in seed_result and arch in seed_result[method]:
                        if budget in seed_result[method][arch]:
                            aucs.append(seed_result[method][arch][budget]["auc"])
                            times.append(seed_result[method][arch][budget]["time"])

                if aucs:
                    aggregated[method][arch][budget] = {
                        "auc_mean": float(np.mean(aucs)),
                        "auc_std": float(np.std(aucs)),
                        "time_mean": float(np.mean(times)),
                        "time_std": float(np.std(times)),
                        "n_seeds": len(aucs),
                    }
    return aggregated

def evaluate_predictions(agg_results: Dict, per_seed_results: List[Dict],
                         alpha: float = 0.05, trak_threshold: float = 0.05) -> Dict:
    """Evaluate P1/P2/P3 predictions with t-tests.

    P1: EK-FAC GPT-2 > BERT at matched compute (expect significant positive diff)
    P2: TracIn BERT > GPT-2 at matched compute (expect significant negative diff)
    P3: TRAK |BERT - GPT-2| < 5% at all budgets
    """
    predictions = {"P1": {}, "P2": {}, "P3": {}}

    methods_map = {"ekfac": "P1", "tracin": "P2", "trak": "P3"}

    for method in ["ekfac", "tracin", "trak"]:
        pred_key = methods_map[method]
        if method not in agg_results:
            continue

        budgets = list(agg_results[method].get("bert", {}).keys())
        for budget in budgets:
            bert_aucs = []
            gpt2_aucs = []
            for seed_result in per_seed_results:
                if method in seed_result:
                    if "bert" in seed_result[method] and budget in seed_result[method]["bert"]:
                        bert_aucs.append(seed_result[method]["bert"][budget]["auc"])
                    if "gpt2" in seed_result[method] and budget in seed_result[method]["gpt2"]:
                        gpt2_aucs.append(seed_result[method]["gpt2"][budget]["auc"])

            if len(bert_aucs) >= 2 and len(gpt2_aucs) >= 2:
                t_stat, p_val = paired_ttest_across_seeds(bert_aucs, gpt2_aucs)
                mean_diff = np.mean(gpt2_aucs) - np.mean(bert_aucs)
                abs_diff = abs(mean_diff)
                pct_diff = abs_diff / max(np.mean(bert_aucs), 0.001) * 100

                if pred_key == "P1":
                    confirmed = mean_diff > 0 and p_val < alpha
                elif pred_key == "P2":
                    confirmed = mean_diff < 0 and p_val < alpha
                else:  # P3
                    confirmed = abs_diff < trak_threshold

                predictions[pred_key][budget] = {
                    "bert_mean": float(np.mean(bert_aucs)),
                    "gpt2_mean": float(np.mean(gpt2_aucs)),
                    "diff": float(mean_diff),
                    "pct_diff": float(pct_diff),
                    "t_stat": float(t_stat),
                    "p_value": float(p_val),
                    "confirmed": bool(confirmed),
                }

    any_confirmed = any(
        any(b.get("confirmed", False) for b in pred.values())
        for pred in predictions.values()
    )
    return {"predictions": predictions, "any_confirmed": any_confirmed}
