"""Batch evaluation runner: lm-eval harness over 720 checkpoint-condition pairs."""
import json
import logging
import os
import subprocess

import pandas as pd

from config import CONFIG

logger = logging.getLogger(__name__)


def run_lm_eval(
    model_path: str,
    output_path: str,
    tasks: list = None,
    num_fewshot: int = 4,
) -> dict:
    """Run lm-evaluation-harness for one checkpoint.
    Returns: {"mmlu_4shot": float, "hellaswag_0shot": float}
    """
    if tasks is None:
        tasks = CONFIG.eval_tasks
    os.makedirs(output_path, exist_ok=True)
    cmd = [
        "lm-eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_path}",
        "--tasks", ",".join(tasks),
        "--num_fewshot", str(num_fewshot),
        "--batch_size", CONFIG.eval_batch_size,
        "--output_path", output_path,
        "--log_samples",
    ]
    logger.info(f"Evaluating: {model_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"lm-eval failed for {model_path}:\n{result.stderr[:500]}")
    return parse_lm_eval_output(output_path)


def parse_lm_eval_output(output_dir: str) -> dict:
    """Parse lm-eval JSON output; returns metric dict."""
    # lm-eval writes results.json in output_dir
    results_file = os.path.join(output_dir, "results.json")
    if not os.path.exists(results_file):
        # Try nested directory
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f == "results.json":
                    results_file = os.path.join(root, f)
                    break

    if not os.path.exists(results_file):
        raise FileNotFoundError(f"results.json not found in {output_dir}")

    with open(results_file) as f:
        data = json.load(f)

    results = data.get("results", {})

    # MMLU: aggregate over subtasks
    mmlu_scores = []
    for key, val in results.items():
        if "mmlu" in key.lower():
            acc = val.get("acc,none") or val.get("acc") or val.get("acc_norm,none") or 0
            mmlu_scores.append(acc)
    mmlu_4shot = sum(mmlu_scores) / len(mmlu_scores) if mmlu_scores else 0.0

    # HellaSwag
    hellaswag_data = results.get("hellaswag", {})
    hellaswag_0shot = (
        hellaswag_data.get("acc_norm,none")
        or hellaswag_data.get("acc_norm")
        or hellaswag_data.get("acc,none")
        or hellaswag_data.get("acc", 0.0)
    )

    return {"mmlu_4shot": float(mmlu_4shot), "hellaswag_0shot": float(hellaswag_0shot)}


def evaluate_all_checkpoints(
    run_records: list,
    eval_root: str,
) -> list:
    """Evaluate 72 runs × 10 checkpoints = 720 evaluations.
    Returns list of result dicts with all condition columns.
    """
    results = []
    for run in run_records:
        if run.get("status") != "done":
            logger.warning(f"Skipping {run['run_id']} (status={run.get('status')})")
            continue
        for ckpt_path in run.get("hf_checkpoint_paths", []):
            ckpt_name = os.path.basename(ckpt_path)
            eval_dir = os.path.join(eval_root, run["run_id"], ckpt_name)
            done_flag = os.path.join(eval_dir, "_EVAL_DONE")

            if os.path.exists(done_flag):
                # Load cached result
                try:
                    metrics = parse_lm_eval_output(eval_dir)
                    step = _parse_step(ckpt_name)
                    results.append(_make_result_row(run, step, metrics))
                    continue
                except Exception:
                    pass

            try:
                metrics = run_lm_eval(ckpt_path, eval_dir)
                open(done_flag, "w").close()
                step = _parse_step(ckpt_name)
                results.append(_make_result_row(run, step, metrics))
            except RuntimeError as e:
                logger.warning(f"Eval failed for {ckpt_path}: {e}")

    return results


def _parse_step(ckpt_name: str) -> int:
    import re
    m = re.search(r"\d+", ckpt_name)
    return int(m.group()) if m else 0


def _make_result_row(run: dict, step: int, metrics: dict) -> dict:
    # Parse condition string: e.g. "dolma_ppl20_j07"
    variant = run.get("variant", "")
    parts = variant.split("_")
    corpus = parts[0] if parts else "unknown"
    ppl_threshold = 35
    dedup_j = 0.9
    for p in parts:
        if p.startswith("ppl"):
            try:
                ppl_threshold = int(p[3:])
            except ValueError:
                pass
        if p.startswith("j"):
            try:
                dedup_j = int(p[1:]) / 10.0
            except ValueError:
                pass

    return {
        "scale": run.get("scale"),
        "ppl_threshold": ppl_threshold,
        "dedup_j": dedup_j,
        "corpus": corpus,
        "seed": run.get("seed"),
        "checkpoint_step": step,
        "mmlu_4shot": metrics.get("mmlu_4shot", 0.0),
        "hellaswag_0shot": metrics.get("hellaswag_0shot", 0.0),
        "contamination_rate": run.get("contamination_rate", 0.0),
        "run_id": run.get("run_id"),
    }


def save_results(results: list, csv_path: str, parquet_path: str) -> None:
    """Write results to CSV + Parquet."""
    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)
    logger.info(f"Saved {len(df)} results to {csv_path}")
