import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

PASS_AT_1_PATTERN = re.compile(r"humaneval_plus\s+pass@1:\s*([0-9]+\.[0-9]+)", re.IGNORECASE)
PASS_AT_1_FALLBACK = re.compile(r"humaneval\s+pass@1:\s*([0-9]+\.[0-9]+)", re.IGNORECASE)


def verify_checkpoints(cfg) -> Dict[str, List[str]]:
    """Returns {condition: [missing_step, ...]} for non-baseline steps."""
    missing = {}
    for condition in cfg.conditions:
        missing[condition] = []
        for step in cfg.steps:
            ckpt_path = cfg.checkpoint_path(condition, step)
            if not Path(ckpt_path).exists():
                missing[condition].append(step)
    return missing


def run_fallback_training(cfg, missing: Dict[str, List[str]]) -> None:
    """
    Injects H-M2 code into sys.path and runs GRPO with save_strategy='steps'
    for conditions that are missing checkpoints.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import GRPOConfig, GRPOTrainer

    h_m2_code = str(Path(cfg.h_m2_code_dir).resolve())

    # Load h-m2 modules directly by file path to avoid name conflicts with h-m4
    import importlib.util as _ilu

    def _load_mod(name, filepath):
        spec = _ilu.spec_from_file_location(f"h_m2_{name}", filepath)
        mod = _ilu.module_from_spec(spec)
        sys.modules[f"h_m2_{name}"] = mod
        spec.loader.exec_module(mod)
        return mod

    _h_m2_config_mod = _load_mod("config", f"{h_m2_code}/config.py")
    H_M2Config = _h_m2_config_mod.H_M2Config

    # dataset.py imports 'config' by name — patch sys.modules temporarily
    sys.modules["config"] = _h_m2_config_mod
    _h_m2_dataset_mod = _load_mod("dataset", f"{h_m2_code}/dataset.py")
    load_mbpp_subsets = _h_m2_dataset_mod.load_mbpp_subsets
    _h_m2_reward_mod = _load_mod("reward", f"{h_m2_code}/reward.py")
    make_execution_reward = _h_m2_reward_mod.make_execution_reward

    h_m2_cfg = H_M2Config()
    reward_fn = make_execution_reward(timeout=h_m2_cfg.exec_timeout)

    # Load datasets once (variance50, random50, full374)
    variance_50_ds, random_50_ds, _, _ = load_mbpp_subsets(h_m2_cfg)

    # Build full374 dataset
    from datasets import load_dataset as _load_ds
    full374_ds = _load_ds(h_m2_cfg.mbpp_dataset_id, h_m2_cfg.mbpp_subset, split=h_m2_cfg.mbpp_split)

    condition_datasets = {
        "variance50": variance_50_ds,
        "random50": random_50_ds,
        "full374": full374_ds,
    }

    for condition, missing_steps in missing.items():
        if not missing_steps:
            continue

        output_dir = f"{cfg.h_m2_results_dir}/{condition}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        dataset = condition_datasets[condition]

        grpo_cfg = GRPOConfig(
            output_dir=output_dir,
            num_generations=h_m2_cfg.num_generations,
            generation_batch_size=h_m2_cfg.generation_batch_size,
            max_steps=h_m2_cfg.max_steps,
            learning_rate=h_m2_cfg.learning_rate,
            beta=h_m2_cfg.beta,
            logging_steps=h_m2_cfg.logging_steps,
            save_strategy="steps",
            save_steps=10,
            use_vllm=h_m2_cfg.use_vllm,
            seed=h_m2_cfg.seed,
            max_completion_length=h_m2_cfg.max_new_tokens,
            per_device_train_batch_size=1,
            report_to="none",
        )

        model = AutoModelForCausalLM.from_pretrained(
            h_m2_cfg.model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(h_m2_cfg.model_id)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Add prompt column as H-M2 train.py does
        INSTRUCTION_TEMPLATE = (
            "Write a Python function to solve the following problem.\n\n"
            "Problem: {problem}\n\n"
            "Provide only the function implementation, no explanations.\n"
        )
        dataset = dataset.map(lambda ex: {**ex, "prompt": INSTRUCTION_TEMPLATE.format(problem=ex["text"])})

        trainer = GRPOTrainer(
            model=model,
            args=grpo_cfg,
            train_dataset=dataset,
            reward_funcs=[reward_fn],
            processing_class=tokenizer,
        )
        trainer.train()
        print(f"[H-M4 fallback] {condition} training complete. Checkpoints in {output_dir}")


def generate_samples(checkpoint_path: str, condition: str, step: str, cfg) -> str:
    """
    Run evalplus.codegen for one (condition, step) checkpoint.
    Resume-safe: skips if samples.jsonl already exists.
    Returns output_dir path.
    """
    output_dir = cfg.eval_output_dir(condition, step)
    samples_path = Path(output_dir) / "samples.jsonl"

    if samples_path.exists():
        print(f"[H-M4] Skipping generation (resume): {condition}/{step}")
        return output_dir

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "evalplus.codegen",
        "--model", checkpoint_path,
        "--dataset", cfg.dataset,
        "--backend", cfg.backend,
        "--n_samples", str(cfg.n_samples),
        "--temperature", str(cfg.temperature),
        "--root", output_dir,
    ]
    print(f"[H-M4] Generating samples: {condition}/{step} → {output_dir}")
    subprocess.run(cmd, check=True)
    return output_dir


def evaluate_samples(output_dir: str, cfg) -> float:
    """
    Run evalplus.evaluate on generated samples.jsonl.
    Returns humaneval_plus pass@1 as float.
    """
    samples_path = f"{output_dir}/samples.jsonl"
    cmd = [
        sys.executable, "-m", "evalplus.evaluate",
        "--dataset", cfg.dataset,
        "--samples", samples_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return parse_pass_at_1(result.stdout + result.stderr)


def parse_pass_at_1(stdout: str) -> float:
    """Extract humaneval_plus pass@1 from evalplus stdout."""
    m = PASS_AT_1_PATTERN.search(stdout)
    if m:
        return float(m.group(1))
    m = PASS_AT_1_FALLBACK.search(stdout)
    if m:
        return float(m.group(1))
    raise ValueError(f"Could not parse pass@1 from evalplus output.\nOutput:\n{stdout[:1000]}")


def run_all_evaluations(cfg) -> Dict[str, Dict[str, float]]:
    """
    Evaluates all (condition × step) combinations.
    step_0 frozen baseline evaluated ONCE, reused for all conditions.
    Returns: {condition: {step: pass@1_float}}
    """
    results = {cond: {} for cond in cfg.conditions}

    # Evaluate frozen baseline once
    print("[H-M4] Evaluating frozen baseline (step_0)...")
    baseline_dir = generate_samples(
        checkpoint_path=cfg.baseline_model,
        condition="baseline",
        step="step_0",
        cfg=cfg,
    )
    baseline_pass_at_1 = evaluate_samples(baseline_dir, cfg)
    print(f"[H-M4] Baseline pass@1 = {baseline_pass_at_1:.4f}")

    for cond in cfg.conditions:
        results[cond]["step_0"] = baseline_pass_at_1

    # Evaluate fine-tuned checkpoints
    for cond in cfg.conditions:
        for step in cfg.steps:
            ckpt_path = cfg.checkpoint_path(cond, step)
            if not Path(ckpt_path).exists():
                print(f"[H-M4] WARNING: checkpoint missing {cond}/{step}. Skipping.")
                results[cond][step] = None
                continue
            out_dir = generate_samples(ckpt_path, cond, step, cfg)
            results[cond][step] = evaluate_samples(out_dir, cfg)
            print(f"[H-M4] {cond}/{step} pass@1 = {results[cond][step]:.4f}")

    return results
