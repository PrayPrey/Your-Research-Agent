import numpy as np


def verify_contamination_mechanism(cont_acc: float, clean_acc: float) -> dict:
    mechanism_active = cont_acc > clean_acc
    effect_size = cont_acc - clean_acc

    print(f"[MECHANISM CHECK] Contaminated: {cont_acc:.4f}, Clean: {clean_acc:.4f}")
    print(f"[MECHANISM CHECK] Effect: {effect_size:.4f}, Active: {mechanism_active}")

    return {
        "mechanism_active": bool(mechanism_active),
        "contaminated_accuracy": float(cont_acc),
        "clean_accuracy": float(clean_acc),
        "effect_size": float(effect_size),
    }


def verify_monotonic_trend(effect_sizes_by_level: dict) -> bool:
    levels = sorted([l for l in effect_sizes_by_level.keys() if l > 0])
    if len(levels) < 2:
        return True

    prev = effect_sizes_by_level[levels[0]]
    for level in levels[1:]:
        curr = effect_sizes_by_level[level]
        if curr < prev:
            return False
        prev = curr
    return True


def aggregate_across_seeds(results_per_seed: list) -> dict:
    effect_sizes = [r["effect_size"] for r in results_per_seed]
    return {
        "mean_effect_size": float(np.mean(effect_sizes)),
        "std_effect_size": float(np.std(effect_sizes)),
        "min_effect_size": float(np.min(effect_sizes)),
        "max_effect_size": float(np.max(effect_sizes)),
    }
