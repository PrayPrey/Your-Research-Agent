from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

from config import BATCH_SIZE, GREEDY_SEED, MIN_MODELS, STOCHASTIC_SEEDS, STOCHASTIC_TEMPERATURE, TASKS

logger = logging.getLogger(__name__)


def get_batch_size(params: str) -> int:
    return BATCH_SIZE.get(params, 4)


def _build_model_args(model: dict) -> str:
    hf_id = model["hf_id"]
    requires_4bit = model.get("requires_4bit", False)

    if requires_4bit:
        try:
            import bitsandbytes  # noqa: F401
        except ImportError:
            raise RuntimeError(
                f"Model {model['id']} requires 4-bit quantization but bitsandbytes is not installed. "
                "Run: pip install bitsandbytes"
            )
        return f"pretrained={hf_id},load_in_4bit=True"
    else:
        return f"pretrained={hf_id},dtype=float16"


def run_model_greedy(model: dict, output_dir: Path) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)
    model_args = _build_model_args(model)
    batch = get_batch_size(model["params"])
    tasks_str = ",".join(TASKS)
    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", model_args,
        "--tasks", tasks_str,
        "--num_fewshot", "0",
        "--batch_size", str(batch),
        "--seed", str(GREEDY_SEED),
        "--log_samples",
        "--output_path", str(output_dir),
        "--device", "cuda",
    ]
    logger.info(f"[greedy] {model['id']}: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"[greedy] {model['id']} failed (rc={result.returncode}):\n{result.stderr[-2000:]}")
        return False
    return True


def run_model_stochastic(model: dict, seed: int, output_dir: Path) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)
    model_args = _build_model_args(model)
    batch = get_batch_size(model["params"])
    tasks_str = ",".join(TASKS)
    gen_kwargs = f"temperature={STOCHASTIC_TEMPERATURE},seed={seed}"
    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", model_args,
        "--tasks", tasks_str,
        "--num_fewshot", "0",
        "--batch_size", str(batch),
        "--seed", str(seed),
        "--gen_kwargs", gen_kwargs,
        "--log_samples",
        "--output_path", str(output_dir),
        "--device", "cuda",
    ]
    logger.info(f"[stochastic seed={seed}] {model['id']}: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"[stochastic seed={seed}] {model['id']} failed (rc={result.returncode}):\n{result.stderr[-2000:]}")
        return False
    return True


def run_all_models(models: list[dict], results_dir: Path) -> dict[str, bool]:
    results_dir = Path(results_dir)
    success_map: dict[str, bool] = {}

    for model in models:
        mid = model["id"]
        greedy_dir = results_dir / mid / "greedy"
        try:
            ok = run_model_greedy(model, greedy_dir)
        except Exception as e:
            logger.error(f"[greedy] {mid} exception: {e}")
            ok = False
        success_map[mid] = ok

        for seed in STOCHASTIC_SEEDS:
            stoch_dir = results_dir / mid / f"stochastic_seed{seed}"
            try:
                run_model_stochastic(model, seed, stoch_dir)
            except Exception as e:
                logger.error(f"[stochastic seed={seed}] {mid} exception: {e}")

    n_ok = sum(success_map.values())
    logger.info(f"Greedy evaluation complete: {n_ok}/{len(models)} models succeeded")
    if n_ok < MIN_MODELS:
        sys.exit(f"ABORT: Only {n_ok}/{len(models)} models succeeded. Minimum {MIN_MODELS} required.")

    return success_map
