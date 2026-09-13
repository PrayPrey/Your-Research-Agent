#!/usr/bin/env python3
"""H-M1 end-to-end orchestrator: binary vs ratio reward policy target shift."""
import argparse
import json
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
sys.path.append(os.path.join(_THIS_DIR, "../../h-e1/code"))
from config import HM1Config, load_hm1_config, save_hm1_config
from train import run_condition
from eval_humaneval import batch_evaluate_humaneval
from eval_mbpp import evaluate_mbpp
from eval_apps_allpass import evaluate_apps_allpass, stratify_apps_val
from analyze import bootstrap_ci, verify_h_m1_mechanism, compile_results
from visualize import save_all_figures, VisualizerConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-M1: Ratio vs Binary Reward Mechanism")
    parser.add_argument("--condition", choices=["binary", "ratio", "both"], default="both")
    parser.add_argument("--resume_from_step", type=int, default=None)
    parser.add_argument("--skip_eval", action="store_true")
    parser.add_argument("--skip_train", action="store_true")
    parser.add_argument("--config_path", default=None)
    parser.add_argument("--output_dir", default=None)
    return parser.parse_args()


def find_checkpoints(cfg: HM1Config, condition: str, from_step: int = None) -> dict:
    """Scan checkpoint dir for saved checkpoints."""
    checkpoint_dir = os.path.join(cfg.output_dir, "checkpoints", condition)
    found = {}
    for step in cfg.checkpoint_steps:
        if from_step is not None and step < from_step:
            continue
        path = os.path.join(checkpoint_dir, f"checkpoint-{step}")
        if os.path.exists(path):
            found[step] = path
    return found


def get_conditions(condition_arg: str) -> list:
    if condition_arg == "both":
        return ["binary", "ratio"]
    return [condition_arg]


def main() -> None:
    args = parse_args()

    cfg = load_hm1_config(args.config_path)
    if args.output_dir:
        cfg.output_dir = args.output_dir

    os.makedirs(cfg.output_dir, exist_ok=True)
    save_hm1_config(cfg, os.path.join(cfg.output_dir, "experiment_config.yaml"))

    print(f"H-M1 Experiment: conditions={args.condition}, steps={cfg.train_steps}")
    print(f"Output: {cfg.output_dir}")

    conditions = get_conditions(args.condition)
    checkpoint_paths_by_condition = {}

    # Step 1-3: Training
    if not args.skip_train:
        for condition in conditions:
            if args.resume_from_step:
                found = find_checkpoints(cfg, condition, from_step=args.resume_from_step)
                if found:
                    print(f"[{condition}] Resuming from step {args.resume_from_step}, found: {sorted(found.keys())}")
                    checkpoint_paths_by_condition[condition] = found
                    continue
            result = run_condition(condition, cfg, cfg.model_name)
            checkpoint_paths_by_condition[condition] = result.checkpoint_paths
    else:
        for condition in conditions:
            checkpoint_paths_by_condition[condition] = find_checkpoints(cfg, condition)

    print("\nCheckpoints found:")
    for cond, paths in checkpoint_paths_by_condition.items():
        print(f"  {cond}: steps {sorted(paths.keys())}")

    if args.skip_eval:
        print("Skipping evaluation (--skip_eval)")
        return

    # Step 4: HumanEval evaluation at all checkpoint steps
    humaneval_curves = {}
    humaneval_per_problem = {}
    problems = None

    for condition in conditions:
        ckpts = checkpoint_paths_by_condition.get(condition, {})
        if not ckpts:
            print(f"⚠ No checkpoints for {condition}, skipping HumanEval")
            continue
        print(f"\n[{condition}] Evaluating HumanEval at steps: {sorted(ckpts.keys())}")
        scores = batch_evaluate_humaneval(ckpts, cfg.model_name, problems)
        humaneval_curves[condition] = scores

    # Step 5: MBPP and APPS all-pass at step 1000
    mbpp_results = {}
    apps_allpass = {}
    per_problem_rates = {}

    # Load APPS val once (stratified)
    print("\nLoading APPS validation split...")
    from datasets import load_dataset
    apps_full = load_dataset("codeparrot/apps", split="validation")
    apps_val_dataset = stratify_apps_val(list(apps_full), n=cfg.apps_val_size)
    print(f"APPS-val stratified sample: {len(apps_val_dataset)} problems")

    for condition in conditions:
        ckpts = checkpoint_paths_by_condition.get(condition, {})
        ckpt_1000 = ckpts.get(1000)
        if ckpt_1000 is None:
            # Try last available step
            if ckpts:
                last_step = max(ckpts.keys())
                ckpt_1000 = ckpts[last_step]
                print(f"⚠ Step 1000 not found for {condition}, using step {last_step}")
            else:
                print(f"⚠ No checkpoints for {condition}, skipping step-1000 eval")
                continue

        print(f"\n[{condition}] MBPP evaluation...")
        mbpp_results[condition] = evaluate_mbpp(ckpt_1000, cfg.model_name)

        print(f"\n[{condition}] APPS all-pass evaluation ({cfg.apps_val_size} problems)...")
        apps_result = evaluate_apps_allpass(ckpt_1000, cfg.model_name, apps_val_dataset, cfg.sandbox_timeout)
        apps_allpass[condition] = apps_result.allpass_fraction
        per_problem_rates[condition] = apps_result.per_problem_rates

    # Step 6: Statistical analysis
    print("\nRunning bootstrap CI...")
    ratio_per_problem = per_problem_rates.get("ratio", [])
    binary_per_problem = per_problem_rates.get("binary", [])

    if ratio_per_problem and binary_per_problem:
        ci = bootstrap_ci(ratio_per_problem, binary_per_problem, n_bootstrap=cfg.bootstrap_n)
    else:
        from analyze import BootstrapResult
        ci = BootstrapResult(mean_diff=0.0, ci_lower=0.0, ci_upper=0.0, excludes_zero=False)
        print("⚠ Missing per-problem rates for bootstrap CI")

    ratio_he = humaneval_curves.get("ratio", {}).get(1000, 0.0)
    binary_he = humaneval_curves.get("binary", {}).get(1000, 0.0)
    ratio_apps = apps_allpass.get("ratio", 0.0)
    binary_apps = apps_allpass.get("binary", 0.0)

    mechanism = verify_h_m1_mechanism(
        ratio_humaneval_pass1=ratio_he,
        binary_humaneval_pass1=binary_he,
        ratio_apps_allpass=ratio_apps,
        binary_apps_allpass=binary_apps,
        bootstrap_ci_lower=ci.ci_lower,
    )

    print(f"\n{'='*60}")
    print(f"MECHANISM VERIFICATION: {mechanism.result}")
    print(f"  HumanEval gap: {mechanism.p1_humaneval_gap:+.4f} (threshold: 0.03)")
    print(f"  CI lower: {ci.ci_lower:+.4f} (>0: {ci.excludes_zero})")
    print(f"  P1 (HumanEval gap): {mechanism.p1_satisfied}")
    print(f"  P2 (policy shift): {mechanism.p2_policy_shift}")
    print(f"  GATE SATISFIED: {mechanism.gate_satisfied}")
    print(f"{'='*60}\n")

    # Compile and save results
    all_results = compile_results(
        humaneval_curves=humaneval_curves,
        mbpp_results=mbpp_results,
        apps_allpass=apps_allpass,
        per_problem_rates=per_problem_rates,
        mechanism_result=mechanism,
        bootstrap_result=ci,
    )

    os.makedirs(os.path.join(cfg.output_dir, "results"), exist_ok=True)
    results_json_path = os.path.join(cfg.output_dir, "results", "h_m1_results.json")
    with open(results_json_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Results saved to: {results_json_path}")

    # Also save to h-m1 folder for pipeline
    hm1_folder = os.path.join(os.path.dirname(__file__), "..")
    pipeline_results_path = os.path.join(hm1_folder, "experiment_results.json")
    with open(pipeline_results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Pipeline results saved to: {pipeline_results_path}")

    # Step 7: Figures
    print("\nGenerating figures...")
    figures_dir = os.path.join(hm1_folder, "figures")
    viz_cfg = VisualizerConfig(output_dir=figures_dir)
    save_all_figures(all_results, figures_dir, viz_cfg)

    print("\nH-M1 experiment complete.")
    print(f"Gate result: {mechanism.result}")


if __name__ == "__main__":
    main()
