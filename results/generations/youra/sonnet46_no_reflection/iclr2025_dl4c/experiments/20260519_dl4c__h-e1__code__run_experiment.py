import os
import sys
import json
import time

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from train_grpo import train_grpo
from train_dpo import train_dpo
from evaluate import run_full_evaluation
from kl_metric import load_checkpoint_kl_log
from visualize import generate_all_figures


def run_experiment():
    cfg = get_config()

    # Resolve paths relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cfg.output_dir = os.path.join(script_dir, "outputs")
    cfg.figures_dir = os.path.join(script_dir, "../figures")
    cfg.checkpoint_dir = os.path.join(script_dir, "../checkpoints")

    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    print(f"=== Experiment start ===")
    print(f"Config: model={cfg.model_id}, grpo_steps={cfg.grpo_steps}, dpo_steps={cfg.dpo_steps}")

    # Phase 1: GRPO training
    t0 = time.time()
    print("\n[Phase 1] GRPO training...")
    grpo_checkpoint = train_grpo(cfg)
    print(f"GRPO done in {time.time()-t0:.1f}s. Checkpoint: {grpo_checkpoint}")

    # Phase 2: DPO training
    t1 = time.time()
    print("\n[Phase 2] DPO training...")
    dpo_checkpoint = train_dpo(cfg)
    print(f"DPO done in {time.time()-t1:.1f}s. Checkpoint: {dpo_checkpoint}")

    # Phase 3: Evaluation
    t2 = time.time()
    print("\n[Phase 3] Evaluation...")
    eval_output = os.path.join(cfg.output_dir, "eval_results.json")
    results = run_full_evaluation(grpo_checkpoint, dpo_checkpoint, cfg, eval_output)
    print(f"Evaluation done in {time.time()-t2:.1f}s")

    # Phase 4: Figures
    print("\n[Phase 4] Generating figures...")
    grpo_kl_log = load_checkpoint_kl_log(grpo_checkpoint)
    dpo_kl_log = load_checkpoint_kl_log(dpo_checkpoint)
    figure_paths = generate_all_figures(results, grpo_kl_log, dpo_kl_log, cfg.figures_dir)

    # Summary
    ci = results["bootstrap_ci"]
    print("\n=== RESULTS SUMMARY ===")
    print(f"GRPO pass@1: {results['grpo_pass_rate']:.3f}")
    print(f"DPO  pass@1: {results['dpo_pass_rate']:.3f}")
    print(f"Bootstrap 95% CI for differential: [{ci['lower']:.4f}, {ci['upper']:.4f}]")
    print(f"Mean differential: {ci['mean']:.4f}")
    print(f"Gate satisfied: {results['gate_satisfied']}")
    print(f"Total time: {time.time()-t0:.1f}s")

    # Save summary
    summary = {
        "grpo_checkpoint": grpo_checkpoint,
        "dpo_checkpoint": dpo_checkpoint,
        "eval_results_path": eval_output,
        "figure_paths": figure_paths,
        "gate_satisfied": results["gate_satisfied"],
        "bootstrap_ci": ci,
        "grpo_pass_rate": results["grpo_pass_rate"],
        "dpo_pass_rate": results["dpo_pass_rate"],
    }
    summary_path = os.path.join(cfg.output_dir, "experiment_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to {summary_path}")

    return results


if __name__ == "__main__":
    run_experiment()
