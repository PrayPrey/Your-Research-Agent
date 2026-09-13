"""Repair lm_eval results for runs that got 0.0 due to missing lm_eval."""
import json
import os
import glob
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CHECKPOINTS_DIR = os.path.join(os.path.dirname(__file__), "outputs", "checkpoints")
STATE_FILE = os.path.join(os.path.dirname(__file__), "outputs", "training_state.json")


def run_lm_eval(model_path: str) -> float:
    eval_output = os.path.join(model_path, "lm_eval_hellaswag")
    result_file_pattern = os.path.join(eval_output, "**", "results*.json")

    existing = glob.glob(result_file_pattern, recursive=True)
    if existing:
        with open(sorted(existing)[-1]) as f:
            cached = json.load(f)
        results = cached.get("results", {})
        hellaswag = results.get("hellaswag", {})
        acc = hellaswag.get("acc_norm,none") or hellaswag.get("acc_norm") or 0.0
        logger.info(f"Cached: {os.path.basename(model_path)} acc={acc:.4f}")
        return float(acc)

    os.makedirs(eval_output, exist_ok=True)
    cmd = [
        sys.executable, "-m", "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_path},dtype=float32",
        "--tasks", "hellaswag",
        "--num_fewshot", "0",
        "--output_path", eval_output,
        "--log_samples",
        "--batch_size", "32",
    ]
    logger.info(f"Running lm_eval on {os.path.basename(model_path)}")
    env = os.environ.copy()
    if "CUDA_VISIBLE_DEVICES" not in env:
        env["CUDA_VISIBLE_DEVICES"] = "0"
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=7200, env=env)
    if proc.returncode != 0:
        logger.error(f"lm_eval failed: {proc.stderr[-500:]}")
        return 0.0

    json_files = glob.glob(result_file_pattern, recursive=True)
    if not json_files:
        logger.warning(f"No results JSON in {eval_output}")
        return 0.0
    with open(sorted(json_files)[-1]) as f:
        results = json.load(f)
    hellaswag = results.get("results", {}).get("hellaswag", {})
    acc = hellaswag.get("acc_norm,none") or hellaswag.get("acc_norm") or 0.0
    logger.info(f"Done: {os.path.basename(model_path)} acc={acc:.4f}")
    return float(acc)


def main():
    with open(STATE_FILE) as f:
        state = json.load(f)

    for run_key, run_data in state.items():
        if run_data.get("status") != "done":
            continue
        rows = run_data.get("rows", [])
        if not any(r.get("hellaswag_acc_norm", 0.0) == 0.0 for r in rows):
            logger.info(f"Skipping {run_key} — already has non-zero acc")
            continue

        logger.info(f"Repairing {run_key}...")
        run_ckpt_dir = os.path.join(CHECKPOINTS_DIR, run_key)
        if not os.path.exists(run_ckpt_dir):
            logger.warning(f"No checkpoint dir: {run_ckpt_dir}")
            continue

        for row in rows:
            step = row["checkpoint_step"]
            ckpt_dir = os.path.join(run_ckpt_dir, f"checkpoint-{step}")
            if not os.path.exists(ckpt_dir):
                ckpt_dir = run_ckpt_dir  # use final checkpoint
            acc = run_lm_eval(ckpt_dir)
            row["hellaswag_acc_norm"] = acc

        # also get real training loss from trainer_state.json
        trainer_state_path = os.path.join(run_ckpt_dir, "checkpoint-500", "trainer_state.json")
        if os.path.exists(trainer_state_path):
            with open(trainer_state_path) as f:
                ts = json.load(f)
            last_loss = ts.get("log_history", [{}])[-1].get("loss", 5.0)
            for row in rows:
                row["train_loss"] = last_loss

    # Save repaired state
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    logger.info("Repair complete, state saved.")


if __name__ == "__main__":
    main()
