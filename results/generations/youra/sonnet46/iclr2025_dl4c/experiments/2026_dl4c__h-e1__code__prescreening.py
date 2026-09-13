"""Main orchestration for h-e1 prescreening inference pipeline."""
import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone

import pandas as pd
import torch
from tqdm import tqdm

from config import PrescreeningConfig, validate_config, load_config_from_yaml
from data_loader import load_apps_introductory
from evaluate import compute_gate_metrics, check_gate
from execution_sandbox import run_against_test_cases
from reward_fn import compute_r_ratio, compute_r_binary, compute_s_term
from visualization import generate_all_figures

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """Configure root logger with console and optional file handler."""
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO),
                        format=fmt, datefmt=datefmt, handlers=handlers)


def load_model(
    sft_checkpoint_path: str,
    base_model_id: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
    dtype: torch.dtype = torch.bfloat16,
):
    """Load SFT checkpoint or fallback to base model.

    Returns:
        (model, tokenizer) tuple.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if os.path.isdir(sft_checkpoint_path) and len(os.listdir(sft_checkpoint_path)) > 0:
        model_path = sft_checkpoint_path
        logger.info(f"Loading SFT checkpoint from {model_path}")
        sft_used = True
    else:
        model_path = base_model_id
        logger.warning(
            f"SFT checkpoint not found at {sft_checkpoint_path}. "
            f"Falling back to {base_model_id}"
        )
        sft_used = False

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=dtype,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="right")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model.eval()
    return model, tokenizer


def generate_rollouts(
    model,
    tokenizer,
    problems: list[dict],
    k: int = 8,
    temperature: float = 0.8,
    max_new_tokens: int = 1024,
    batch_size: int = 4,
    seed: int = 42,
) -> dict:
    """Generate k rollouts per problem using batched inference.

    Args:
        model: loaded HuggingFace model.
        tokenizer: loaded tokenizer.
        problems: list of problem dicts with 'problem_id' and 'prompt' keys.
        k: number of rollouts per problem.
        temperature: sampling temperature.
        max_new_tokens: max tokens to generate per rollout.
        batch_size: number of problems per batch (each expanded to B*k prompts).
        seed: random seed for reproducibility.

    Returns:
        dict: {problem_id: [rollout_0, ..., rollout_{k-1}]}
    """
    torch.manual_seed(seed)
    results = {}

    for batch_start in tqdm(range(0, len(problems), batch_size), desc="Generating rollouts"):
        batch = problems[batch_start: batch_start + batch_size]

        # Apply chat template to each problem, replicated k times
        prompts = []
        for p in batch:
            chat = [{"role": "user", "content": p["prompt"]}]
            try:
                formatted = tokenizer.apply_chat_template(
                    chat, tokenize=False, add_generation_prompt=True
                )
            except Exception:
                formatted = p["prompt"]
            for _ in range(k):
                prompts.append(formatted)

        # Tokenize all B*k prompts
        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048,
        ).to(model.device)

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                pad_token_id=tokenizer.eos_token_id,
            )

        # Slice only newly generated tokens
        new_ids = output_ids[:, inputs["input_ids"].shape[1]:]
        decoded = tokenizer.batch_decode(new_ids, skip_special_tokens=True)

        # Reshape to [B, k] and store
        for i, prob in enumerate(batch):
            results[prob["problem_id"]] = decoded[i * k: (i + 1) * k]

    return results


def run_prescreening(
    problems: list[dict],
    rollouts: dict,
    s_term_range: tuple = (0.3, 0.55),
    execution_timeout: float = 5.0,
) -> tuple[list[dict], list[dict]]:
    """Evaluate rollouts and filter by S_term range.

    Args:
        problems: list of problem dicts.
        rollouts: dict mapping problem_id to list of rollout strings.
        s_term_range: (min, max) S_term filter.
        execution_timeout: seconds per test case.

    Returns:
        (prescreened_problems, per_problem_results) tuple.
    """
    s_min, s_max = s_term_range
    per_problem_results = []

    for prob in tqdm(problems, desc="Evaluating rollouts"):
        pid = prob["problem_id"]
        codes = rollouts.get(pid, [])
        if not codes:
            continue

        tests_passed_vec = [
            run_against_test_cases(code, prob["test_cases"], timeout=execution_timeout)
            for code in codes
        ]
        T = prob["T"]
        r_ratio_vec = [compute_r_ratio(tp, T) for tp in tests_passed_vec]
        r_binary_vec = [compute_r_binary(tp, T) for tp in tests_passed_vec]
        s_term = compute_s_term(codes, prob["test_cases"], timeout=execution_timeout)

        per_problem_results.append({
            "problem_id": pid,
            "s_term": s_term,
            "T": T,
            "r_ratio_vec": r_ratio_vec,
            "r_binary_vec": r_binary_vec,
            "tests_passed_vec": tests_passed_vec,
        })

    prescreened = [r for r in per_problem_results if s_min <= r["s_term"] <= s_max]
    return prescreened, per_problem_results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="h-e1 Prescreening Inference — EXISTENCE validation"
    )
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--batch_size", type=int, default=4,
                        help="Inference batch size (default: 4)")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to YAML config file to override defaults")
    parser.add_argument("--resume", action="store_true", default=False,
                        help="Resume from processed_problem_ids.json if it exists")
    parser.add_argument("--save_rollouts", action="store_true", default=False,
                        help="Save all rollouts to rollouts.json")
    parser.add_argument("--n_problems", type=int, default=None,
                        help="Limit number of problems to process (for faster smoke tests)")
    return parser


def main(seed: int = 42, batch_size: int = 4, config_path: str = None,
         resume: bool = False, save_rollouts: bool = False, n_problems: int = None) -> None:
    """Orchestrate the full h-e1 prescreening pipeline."""
    cfg = PrescreeningConfig(seed=seed, batch_size=batch_size)
    if config_path:
        cfg = load_config_from_yaml(config_path, cfg)
    cfg.save_rollouts = save_rollouts
    validate_config(cfg)

    setup_logging(log_level=cfg.log_level, log_file=cfg.log_file)
    torch.manual_seed(cfg.seed)

    # Set up output directories
    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    per_problem_csv = os.path.join(cfg.output_dir, "per_problem_results.csv")
    processed_ids: set = set()
    existing_results: list = []

    # Resume logic
    if resume and os.path.exists(per_problem_csv):
        existing_df = pd.read_csv(per_problem_csv)
        processed_ids = set(existing_df["problem_id"].tolist())
        existing_results = existing_df.to_dict("records")
        logger.info(f"Resume: skipping {len(processed_ids)} already-processed problems")

    # Data loading
    problems_all = load_apps_introductory(min_test_cases=cfg.min_test_cases)
    if n_problems is not None and n_problems > 0:
        problems_all = problems_all[:n_problems]
        logger.info(f"Limited to {n_problems} problems (--n_problems flag)")
    if len(problems_all) < cfg.min_prescreened_problems:
        raise RuntimeError(
            f"FAIL EARLY: T>={cfg.min_test_cases} filter yielded only "
            f"{len(problems_all)} problems (need >={cfg.min_prescreened_problems})"
        )

    remaining = [p for p in problems_all if p["problem_id"] not in processed_ids]
    logger.info(f"Problems to process: {len(remaining)} / {len(problems_all)}")

    # Model loading
    sft_path = os.path.join(os.path.dirname(__file__), "sft_checkpoint")
    dtype_map = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}
    dtype = dtype_map.get(cfg.dtype, torch.bfloat16)
    sft_used = os.path.isdir(sft_path) and len(os.listdir(sft_path)) > 0
    model_used = sft_path if sft_used else cfg.base_model_id

    model, tokenizer = load_model(
        sft_checkpoint_path=sft_path,
        base_model_id=cfg.base_model_id,
        dtype=dtype,
    )

    # Inference
    rollouts = generate_rollouts(
        model, tokenizer, remaining,
        k=cfg.k_rollouts,
        temperature=cfg.temperature,
        max_new_tokens=cfg.max_new_tokens,
        batch_size=cfg.batch_size,
        seed=cfg.seed,
    )

    # Per-problem evaluation
    new_results = []
    for prob in tqdm(remaining, desc="Evaluating rollouts"):
        pid = prob["problem_id"]
        codes = rollouts.get(pid, [])
        tests_passed_vec = [
            run_against_test_cases(code, prob["test_cases"], timeout=cfg.execution_timeout)
            for code in codes
        ]
        T = prob["T"]
        r_ratio_vec = [compute_r_ratio(tp, T) for tp in tests_passed_vec]
        r_binary_vec = [compute_r_binary(tp, T) for tp in tests_passed_vec]
        s_term = compute_s_term(codes, prob["test_cases"], timeout=cfg.execution_timeout)

        new_results.append({
            "problem_id": pid,
            "s_term": s_term,
            "T": T,
            "r_ratio_vec": json.dumps(r_ratio_vec),
            "r_binary_vec": json.dumps(r_binary_vec),
            "tests_passed_vec": json.dumps(tests_passed_vec),
        })

        if len(new_results) % cfg.log_every_n_problems == 0:
            logger.info(f"Processed {len(new_results)} problems ...")

    # Save rollouts optionally
    if cfg.save_rollouts:
        rollouts_path = os.path.join(cfg.output_dir, "rollouts.json")
        with open(rollouts_path, "w") as f:
            json.dump({str(k): v for k, v in rollouts.items()}, f)
        logger.info(f"Saved rollouts to {rollouts_path}")

    # Persist incremental results
    all_results = existing_results + new_results
    pd.DataFrame(all_results).to_csv(per_problem_csv, index=False)

    # S_term prescreening filter
    def parse_s_term(r):
        return float(r["s_term"]) if not isinstance(r["s_term"], str) else float(r["s_term"])

    prescreened = [r for r in all_results if cfg.s_term_min <= parse_s_term(r) <= cfg.s_term_max]
    logger.info(f"Prescreened: {len(prescreened)} / {len(all_results)} problems "
                f"(S_term in [{cfg.s_term_min}, {cfg.s_term_max}])")
    if len(prescreened) < cfg.min_prescreened_problems:
        raise RuntimeError(
            f"FAIL EARLY: prescreened subset has only {len(prescreened)} problems "
            f"(need >={cfg.min_prescreened_problems})"
        )

    # Gate metrics
    metrics = compute_gate_metrics(
        prescreened,
        threshold_pass_ge1=cfg.gate_fraction_k_pass_threshold,
        threshold_pct_above=cfg.gate_pct_groups_threshold,
        variance_ratio_threshold=cfg.variance_ratio_threshold,
    )
    gate_pass, gate_msg = check_gate(metrics)
    logger.info(f"Gate result: {gate_msg}")

    # Enrich metrics with metadata
    metrics.update({
        "gate_message": gate_msg,
        "n_problems_total": len(problems_all),
        "n_problems_after_t_filter": len(problems_all),
        "n_problems_prescreened": len(prescreened),
        "n_groups_eligible_variance": metrics.get("n_non_degenerate_groups", 0),
        "run_seed": cfg.seed,
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "sft_checkpoint_used": sft_used,
        "model_used": model_used,
    })

    # Persist gate metrics
    gate_path = os.path.join(cfg.output_dir, "gate_metrics.json")
    with open(gate_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Saved gate metrics to {gate_path}")

    # Visualization
    generate_all_figures(
        metrics=metrics,
        per_problem_results=prescreened,
        figures_dir=cfg.figures_dir,
    )

    logger.info("Prescreening complete.")
    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()
    main(
        seed=args.seed,
        batch_size=args.batch_size,
        config_path=args.config,
        resume=args.resume,
        save_rollouts=args.save_rollouts,
        n_problems=args.n_problems,
    )
