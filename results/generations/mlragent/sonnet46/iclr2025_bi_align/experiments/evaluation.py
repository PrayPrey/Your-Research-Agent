"""
Evaluation metrics for CAVE and baselines.

Metrics:
- Representational Fidelity: AUC-ROC on held-out preference prediction
- Feedback Efficiency: queries to reach target fidelity
- Value Diversity Preservation: Jensen-Shannon divergence between group distributions
- Drift Detection: precision/recall of flagged drift events
"""

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from scipy.spatial.distance import jensenshannon
from scipy.special import softmax
from config import NUM_DEMOGRAPHIC_GROUPS, NUM_VALUE_DIMS, DEVICE


def compute_preference_auc(model, data_batch, device=DEVICE):
    """Compute AUC-ROC for preference prediction on a batch."""
    model.eval()
    with torch.no_grad():
        user_ids = torch.tensor(data_batch['user_ids'], dtype=torch.long, device=device)
        action_a = torch.tensor(data_batch['action_a'], dtype=torch.long, device=device)
        action_b = torch.tensor(data_batch['action_b'], dtype=torch.long, device=device)
        contexts = torch.tensor(data_batch['contexts'], dtype=torch.float32, device=device)
        prefs = data_batch['preferences']

        if hasattr(model, 'forward') and hasattr(model, 'compute_kl_divergence'):
            # CAVE model
            logits, _ = model(user_ids, action_a, action_b, contexts)
        elif hasattr(model, 'forward') and callable(getattr(model, 'forward')):
            out = model(user_ids, action_a, action_b, contexts)
            if isinstance(out, tuple):
                logits = out[0]
            else:
                logits = out
        else:
            logits = model(user_ids, action_a, action_b, contexts)

        probs = torch.sigmoid(logits).cpu().numpy()
        try:
            auc = roc_auc_score(prefs, probs)
        except Exception:
            auc = 0.5
    return auc


def compute_value_diversity(model_user_values, user_groups, n_groups=NUM_DEMOGRAPHIC_GROUPS):
    """
    Jensen-Shannon divergence between group-level value distributions.
    Larger JS divergence = better diversity preservation.
    """
    group_values = []
    for g in range(n_groups):
        mask = user_groups == g
        if mask.sum() == 0:
            continue
        vals = model_user_values[mask]  # (n_g, value_dim)
        group_values.append(vals)

    if len(group_values) < 2:
        return 0.0

    # Compute pairwise JS divergences using value histograms
    js_divs = []
    for i in range(len(group_values)):
        for j in range(i + 1, len(group_values)):
            # Use mean value vectors to construct distributions
            v_i = group_values[i].mean(0)  # (value_dim,)
            v_j = group_values[j].mean(0)

            # Convert to probability distributions via softmax
            p_i = softmax(v_i)
            p_j = softmax(v_j)

            js = jensenshannon(p_i, p_j)
            js_divs.append(js)

    return float(np.mean(js_divs))


def evaluate_drift_detection(detected_drift_users, true_drift_users, all_users):
    """
    Evaluate drift detection: precision/recall/F1 against ground truth.
    """
    detected_set = set(detected_drift_users)
    true_set = set(true_drift_users)

    tp = len(detected_set & true_set)
    fp = len(detected_set - true_set)
    fn = len(true_set - detected_set)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp,
        'fp': fp,
        'fn': fn,
    }


def compute_feedback_efficiency(auc_over_queries, target_auc=0.7):
    """
    Number of queries to reach target AUC.
    Returns -1 if target never reached.
    """
    for n_queries, auc in enumerate(auc_over_queries):
        if auc >= target_auc:
            return n_queries
    return -1


def compute_metrics_over_time(model, env, data, user_groups, device=DEVICE):
    """Compute all metrics at each training epoch."""
    metrics = {}
    model_vals = model.user_mu.detach().cpu().numpy() if hasattr(model, 'user_mu') else None

    if model_vals is not None:
        metrics['value_diversity'] = compute_value_diversity(model_vals, user_groups)
    else:
        metrics['value_diversity'] = 0.0

    return metrics
