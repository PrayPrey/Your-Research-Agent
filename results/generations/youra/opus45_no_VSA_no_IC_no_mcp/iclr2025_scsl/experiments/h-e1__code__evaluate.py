import json
import os


def dominance_epoch(epoch_ratios: list) -> int | None:
    for epoch, ratio in epoch_ratios:
        if ratio > 1.0:
            return epoch
    return None


def check_gate(epoch_ratios: list) -> dict:
    dom_epoch = dominance_epoch(epoch_ratios)

    if dom_epoch is not None and dom_epoch < 10:
        ratio_at_dom = next(r for e, r in epoch_ratios if e == dom_epoch)
        return {
            "pass": True,
            "dominance_epoch": dom_epoch,
            "ratio_at_dominance": ratio_at_dom,
            "reason": f"Spurious dominance at epoch {dom_epoch} (< 10), ratio = {ratio_at_dom:.4f}"
        }
    elif dom_epoch is not None:
        ratio_at_dom = next(r for e, r in epoch_ratios if e == dom_epoch)
        return {
            "pass": False,
            "dominance_epoch": dom_epoch,
            "ratio_at_dominance": ratio_at_dom,
            "reason": f"Spurious dominance at epoch {dom_epoch} (>= 10), too late"
        }
    else:
        max_ratio = max(r for _, r in epoch_ratios) if epoch_ratios else 0
        return {
            "pass": False,
            "dominance_epoch": None,
            "ratio_at_dominance": max_ratio,
            "reason": f"No epoch with ratio > 1.0 found; max ratio = {max_ratio:.4f}"
        }


def save_metrics(epoch_ratios: list, gate_result: dict, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "gate_result.json"), "w") as f:
        json.dump(gate_result, f, indent=2)

    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump({
            "epoch_ratios": epoch_ratios,
            "gate_result": gate_result
        }, f, indent=2)

    print(f"Metrics saved to {output_dir}")
