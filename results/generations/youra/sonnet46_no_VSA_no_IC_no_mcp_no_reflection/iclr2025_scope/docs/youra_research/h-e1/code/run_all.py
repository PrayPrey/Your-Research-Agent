import os
import json
import sys

from config import ExperimentConfig
from train import train_one_task, eval_zero_shot, TASK_LABEL_COUNTS
from glue_evaluate import compute_glue_avg, get_scalar, plot_results
from model import verify_lora_activated

GATE_THRESHOLD = 0.70
GATE_TASK = "sst2"


def run_experiment(cfg: ExperimentConfig) -> dict:
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    zero_shot_raw = {}
    lora_raw = {}
    lora_models = {}
    loss_histories = {}

    for task in cfg.tasks:
        print(f"\n=== Zero-shot eval: {task} ===")
        zs = eval_zero_shot(task, cfg)
        zero_shot_raw[task] = get_scalar(task, zs)
        print(f"  zero-shot {task}={zero_shot_raw[task]:.4f}")

    for task in cfg.tasks:
        print(f"\n=== LoRA training: {task} ===")
        model, metrics, loss_hist = train_one_task(task, cfg)
        lora_raw[task] = get_scalar(task, metrics)
        lora_models[task] = model
        loss_histories[task] = loss_hist
        print(f"  lora {task}={lora_raw[task]:.4f}")

    gate_metric = lora_raw[GATE_TASK]
    gate_passed = gate_metric > GATE_THRESHOLD

    activated, indicators = verify_lora_activated(
        lora_models[GATE_TASK], lora_raw, zero_shot_raw
    )

    results = {
        "zero_shot": zero_shot_raw,
        "lora": lora_raw,
        "glue_avg_zero_shot": compute_glue_avg(zero_shot_raw),
        "glue_avg_lora": compute_glue_avg(lora_raw),
        "gate_passed": gate_passed,
        "gate_metric": gate_metric,
        "gate_threshold": GATE_THRESHOLD,
        "lora_activated": activated,
        "mechanism_indicators": indicators,
        "loss_history": loss_histories,
    }

    out_path = os.path.join(cfg.results_dir, "results.json")
    # loss_history has lists — strip before JSON dump
    json_results = {k: v for k, v in results.items() if k != "loss_history"}
    with open(out_path, "w") as f:
        json.dump(json_results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print(f"Gate: SST-2 accuracy = {gate_metric:.4f} (threshold {GATE_THRESHOLD}) → {'PASS' if gate_passed else 'FAIL'}")

    # plots
    plot_results({**json_results, "loss_history": loss_histories}, cfg)
    return results


if __name__ == "__main__":
    cfg = ExperimentConfig()
    results = run_experiment(cfg)
    sys.exit(0 if results["gate_passed"] else 1)
