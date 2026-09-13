"""
H-E1 EXISTENCE PoC Experiment Runner
Cross-encoder NLI-based hallucination detection on HaluEval.

Usage:
    conda run -n youra-h-e1 python run_experiment.py
"""
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# Setup paths: allow running from code/ directory or from h-e1/ root
# ─────────────────────────────────────────────────────────────────────────────
CODE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(CODE_DIR))

from config import ExperimentConfig, get_config
from data import TaskData, load_all_tasks
from evaluate import (
    TaskResult, evaluate_task, check_gate_condition,
    plot_gate_metrics, plot_roc_curves,
    plot_score_distributions, plot_structural_ceiling,
)
from model import NLIInferenceModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("run_experiment")


def setup_gpu() -> None:
    """Select GPU with lowest memory usage and set CUDA_VISIBLE_DEVICES."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True,
        )
        rows = [line.strip().split(", ") for line in result.stdout.strip().splitlines()]
        gpu_id = min(rows, key=lambda r: int(r[1]))[0]
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id
        logger.info(f"[GPU] Selected GPU {gpu_id} (lowest memory used)")
    except Exception as e:
        logger.warning(f"[GPU] nvidia-smi failed ({e}); using default GPU 0")
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")


def save_results(
    results: List[TaskResult],
    scores_dict: Dict[str, np.ndarray],
    config: ExperimentConfig,
    results_dir: Path,
) -> None:
    """
    Save experiment results to JSON files.

    Files:
        h-e1_results.json: full (N,3) score matrices per task
        h-e1_summary.json: per-task metrics summary
    """
    results_dir.mkdir(parents=True, exist_ok=True)

    # Full scores (for H-M series reuse)
    scores_data = {
        task_name: scores.tolist()
        for task_name, scores in scores_dict.items()
    }
    results_path = results_dir / config.scores_filename
    with open(results_path, "w") as f:
        json.dump(scores_data, f)
    logger.info(f"Saved full scores: {results_path}")

    # Summary metrics
    summary = {
        "hypothesis_id": "h-e1",
        "timestamp": datetime.now().isoformat(),
        "gate_type": "MUST_WORK",
        "auroc_threshold": config.auroc_threshold,
        "delong_alpha": config.delong_alpha,
        "tasks_required_to_pass": config.tasks_required_to_pass,
        "per_task_results": [
            {
                "task_name": r.task_name,
                "auroc": r.auroc,
                "delong_pvalue": r.delong_pvalue,
                "cohen_d": r.cohen_d,
                "auroc_max": r.auroc_max,
                "p_contradictory": r.p_contradictory,
                "score_inverted": r.score_inverted,
                "n_examples": r.n_examples,
                "label_distribution": r.label_distribution,
                "mechanism_passed": r.mechanism_passed,
                "mechanism_indicators": r.mechanism_indicators,
                "gate_pass": (
                    r.auroc > config.auroc_threshold and
                    r.delong_pvalue < config.delong_alpha
                ),
            }
            for r in results
        ],
    }
    summary_path = results_dir / config.summary_filename
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Saved summary: {summary_path}")


def main() -> None:
    """
    End-to-end H-E1 experiment:
    1. GPU setup
    2. Config
    3. Data loading
    4. Model loading + label map verification
    5. Batch NLI inference per task
    6. Evaluation per task
    7. Gate condition check
    8. Figure generation (4 plots)
    9. Result saving
    10. Gate result output + exit code
    """
    print("=" * 70)
    print("H-E1 EXISTENCE PoC: NLI-based Hallucination Detection")
    print("Model: cross-encoder/nli-deberta-v3-large")
    print("Dataset: pminervini/HaluEval (dialogue + qa + summarization)")
    print("=" * 70)

    # 1. GPU setup (MUST run before model load)
    setup_gpu()

    # 2. Config
    config = get_config()
    logger.info(f"Config: batch_size={config.batch_size}, tasks={config.tasks}")

    # 3. Data loading
    logger.info("Loading HaluEval datasets...")
    tasks_data: List[TaskData] = load_all_tasks(config)

    # 4. Model
    model = NLIInferenceModel(config)
    model.load()
    model.verify_label_map()
    contradiction_idx = model.get_contradiction_index()
    logger.info(f"Contradiction class index: {contradiction_idx}")

    # 5. Inference per task
    scores_dict: Dict[str, np.ndarray] = {}
    for task in tasks_data:
        logger.info(f"Running inference on {task.task_name} ({task.n_examples} pairs)...")
        scores = model.predict(
            task.premises, task.hypotheses,
            batch_size=config.batch_size,
        )
        scores_dict[task.task_name] = scores
        logger.info(f"  {task.task_name}: scores shape={scores.shape}")

    # 6. Evaluation per task
    results: List[TaskResult] = []
    for task in tasks_data:
        result = evaluate_task(
            task_name=task.task_name,
            scores=scores_dict[task.task_name],
            labels=task.labels,
            premises=task.premises,
            hypotheses=task.hypotheses,
            contradiction_idx=contradiction_idx,
            config=config,
        )
        results.append(result)

    # 7. Gate condition
    gate_pass, gate_msg = check_gate_condition(results, config)

    # 8. Figures
    base_dir = CODE_DIR.parent  # h-e1/ directory
    figures_dir = base_dir / config.figures_dir
    figures_dir.mkdir(parents=True, exist_ok=True)

    task_arrays = [
        (r, scores_dict[r.task_name], next(t.labels for t in tasks_data if t.task_name == r.task_name))
        for r in results
    ]

    plot_gate_metrics(results, str(figures_dir / "gate_metrics_comparison.png"))
    plot_roc_curves(task_arrays, str(figures_dir / "roc_curves.png"), contradiction_idx=contradiction_idx)
    plot_score_distributions(task_arrays, str(figures_dir / "score_distributions.png"), contradiction_idx=contradiction_idx)
    plot_structural_ceiling(results, str(figures_dir / "structural_ceiling.png"))

    # 9. Save results
    results_dir = base_dir / config.results_dir
    save_results(results, scores_dict, config, results_dir)

    # Also copy summary to h-e1_summary.json in the code/outputs directory
    outputs_dir = CODE_DIR / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(results_dir / config.summary_filename, outputs_dir / config.summary_filename)

    # 10. Gate result
    print("\n" + "=" * 70)
    print(f"[H-E1] Gate Result: {'PASS ✓' if gate_pass else 'FAIL ✗'}")
    print(gate_msg)
    print("=" * 70)

    # Print per-task summary
    print("\nPer-task summary:")
    for r in results:
        status = "✓ PASS" if (r.auroc > config.auroc_threshold and r.delong_pvalue < config.delong_alpha) else "✗ FAIL"
        print(f"  {r.task_name:16s} AUROC={r.auroc:.4f}  p={r.delong_pvalue:.4e}  Cohen_d={r.cohen_d:.3f}  [{status}]")

    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
