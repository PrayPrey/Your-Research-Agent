"""Run full evaluation: all 154 checkpoints x 3 model sizes in parallel across GPUs."""
from __future__ import annotations
import json
import logging
import os
import sys
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

sys.path.insert(0, str(Path(__file__).parent))
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EVAL_WORKER = """
import sys, os, json, logging
sys.path.insert(0, '{code_dir}')
os.environ['CUDA_VISIBLE_DEVICES'] = '{gpu_id}'
import config
from src.evaluator import evaluate_checkpoint
logging.basicConfig(level=logging.WARNING)
try:
    scores = evaluate_checkpoint('{model_size}', {step}, device='cuda')
    print(json.dumps({{'ok': True, 'model_size': '{model_size}', 'step': {step}, 'scores': scores}}))
except Exception as e:
    print(json.dumps({{'ok': False, 'model_size': '{model_size}', 'step': {step}, 'error': str(e)}}))
"""


def eval_one(args):
    model_size, step, gpu_id, code_dir = args
    cache_path = Path(config.EVAL_CACHE_DIR) / model_size / f"step{step:07d}.json"
    if cache_path.exists():
        return {"ok": True, "model_size": model_size, "step": step, "cached": True}

    script = EVAL_WORKER.format(
        code_dir=code_dir,
        gpu_id=str(gpu_id),
        model_size=model_size,
        step=step,
    )
    result = subprocess.run(
        ["python", "-c", script],
        capture_output=True, text=True, timeout=300,
    )
    last_line = result.stdout.strip().split("\n")[-1] if result.stdout.strip() else ""
    try:
        return json.loads(last_line)
    except json.JSONDecodeError:
        return {"ok": False, "model_size": model_size, "step": step, "error": result.stderr[-200:]}


def main():
    code_dir = str(Path(__file__).parent)
    Path(config.EVAL_CACHE_DIR).mkdir(parents=True, exist_ok=True)

    # Build task list: (model_size, step, gpu_id)
    gpu_ids = [0, 1, 2, 3, 4]
    tasks = []
    for i, ms in enumerate(config.MODEL_SIZES):
        gpu = gpu_ids[i % len(gpu_ids)]
        for step in config.CHECKPOINT_STEPS:
            cache_path = Path(config.EVAL_CACHE_DIR) / ms / f"step{step:07d}.json"
            if not cache_path.exists():
                tasks.append((ms, step, gpu, code_dir))

    logger.info(f"Total evaluations needed: {len(tasks)} (skipping cached)")
    if not tasks:
        logger.info("All evaluations already cached.")
        return

    # Run with limited parallelism (1 worker per GPU model size to avoid OOM)
    n_workers = min(3, len(gpu_ids))  # one per model size
    done = 0
    failed = 0

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = {executor.submit(eval_one, t): t for t in tasks}
        for future in as_completed(futures):
            result = future.result()
            done += 1
            if not result.get("ok"):
                failed += 1
                logger.error(f"FAILED {result.get('model_size')} step {result.get('step')}: {result.get('error', '')[:100]}")
            elif not result.get("cached"):
                logger.info(f"[{result['model_size']}] step {result['step']}: {result.get('scores', {})}")
            if done % 10 == 0:
                logger.info(f"Progress: {done}/{len(tasks)} done, {failed} failed")

    logger.info(f"Evaluation complete: {done - failed} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
