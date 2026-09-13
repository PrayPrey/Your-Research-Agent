"""GPT-NeoX training launcher for 72 runs."""
import json
import logging
import os
import pathlib
import re
import subprocess

import yaml

from config import CONFIG

logger = logging.getLogger(__name__)

_STATE_FILE = os.path.join(
    os.path.dirname(CONFIG.results_csv), "training_state.json"
)

SCALE_OVERRIDES = {
    70: {
        "num_layers": 6, "hidden_size": 512, "num_attention_heads": 8,
        "lr": 1e-3, "min_lr": 1e-4,
    },
    160: {
        "num_layers": 12, "hidden_size": 768, "num_attention_heads": 12,
        "lr": 6e-4, "min_lr": 6e-5,
    },
}


def build_neox_config(
    scale: int,
    binary_prefix: str,
    seed: int,
    checkpoint_dir: str,
    base_config_path: str,
) -> str:
    """Merge per-run overrides into base Pythia YAML; returns written config path."""
    if os.path.exists(base_config_path):
        with open(base_config_path) as f:
            cfg = yaml.safe_load(f) or {}
    else:
        cfg = {}

    cfg.update({
        "data_path": binary_prefix,
        "seed": seed,
        "save": checkpoint_dir,
        "load": checkpoint_dir,
        "seq_length": 2048,
        "max_position_embeddings": 2048,
        "rotary_pct": 0.25,
        "pos_emb": "rotary",
        "train_iters": CONFIG.train_steps,
        "save_interval": 2500,
        "eval_interval": 2500,
        "checkpoint_factor": 2500,
        "weight_decay": 0.1,
        "gradient_clipping": 1.0,
        "warmup_num_steps": int(CONFIG.train_steps * 0.01),
        "lr_decay_style": "cosine",
        "optimizer": {
            "type": "Adam",
            "params": {"betas": [0.9, 0.95], "eps": 1e-8},
        },
        "fp16": {"enabled": True},
        "zero_optimization": {"stage": 1},
        "global_batch_size": 1024,
    })
    cfg.update(SCALE_OVERRIDES[scale])

    os.makedirs(checkpoint_dir, exist_ok=True)
    out_path = os.path.join(checkpoint_dir, "neox_config.yml")
    with open(out_path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)
    return out_path


def launch_neox_run(neox_config_path: str, neox_repo: str) -> int:
    """Run NeoX training subprocess; returns exit code."""
    deepy = os.path.join(neox_repo, "deepy.py")
    cmd = ["python", deepy, "train.py", neox_config_path]
    logger.info(f"Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=neox_repo)
    return result.returncode


def list_checkpoints(checkpoint_dir: str) -> list:
    """Return sorted list of HF checkpoint paths (auto-converts NeoX → HF)."""
    raw_steps = sorted(
        pathlib.Path(checkpoint_dir).glob("global_step*"),
        key=lambda p: int(re.search(r"\d+", p.name).group())
    )
    hf_paths = []
    for step_dir in raw_steps:
        hf_out = str(step_dir) + "_hf"
        if not pathlib.Path(hf_out, "config.json").exists():
            try:
                convert_checkpoint_to_hf(str(step_dir), hf_out, CONFIG.neox_repo)
            except RuntimeError as e:
                logger.warning(f"HF conversion skipped for {step_dir}: {e}")
                continue
        hf_paths.append(hf_out)
    return hf_paths


def convert_checkpoint_to_hf(
    neox_checkpoint: str,
    output_dir: str,
    neox_repo: str,
) -> str:
    """Call tools/convert_to_hf.py via subprocess."""
    script = os.path.join(neox_repo, "tools", "convert_to_hf.py")
    neox_config = os.path.join(os.path.dirname(neox_checkpoint), "neox_config.yml")
    cmd = [
        "python", script,
        "--input_dir", neox_checkpoint,
        "--output_dir", output_dir,
        "--config_file", neox_config,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"HF conversion failed for {neox_checkpoint}:\n{result.stderr}"
        )
    return output_dir


def _load_training_state() -> dict:
    if not os.path.exists(_STATE_FILE):
        return {}
    with open(_STATE_FILE) as f:
        return json.load(f)


def _save_training_state(state: dict) -> None:
    """Atomic write."""
    os.makedirs(os.path.dirname(_STATE_FILE), exist_ok=True)
    tmp = _STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, _STATE_FILE)


def _upsert(records: list, record: dict) -> None:
    for i, r in enumerate(records):
        if r["run_id"] == record["run_id"]:
            records[i] = record
            return
    records.append(record)


def run_all_training(variant_metadata: list) -> list:
    """Launch 12 variants × 2 scales × 3 seeds = 72 runs.
    Resume: skips runs with status='done'.
    Returns list of run_record dicts.
    """
    state = _load_training_state()
    # Reset crashed runs
    for rec in state.values():
        if rec.get("status") == "running":
            rec["status"] = "pending"

    records = list(state.values())

    for variant in variant_metadata:
        for scale in CONFIG.scales:
            for seed in CONFIG.seeds:
                run_id = f"{variant['condition']}_{scale}m_s{seed}"
                ckpt_dir = os.path.join(CONFIG.checkpoint_root, run_id)

                if state.get(run_id, {}).get("status") == "done":
                    logger.info(f"Skipping {run_id} (done)")
                    continue

                binary_prefix = variant.get("binary_prefix")
                if binary_prefix is None:
                    logger.warning(f"No binary_prefix for {variant['condition']} — skipping")
                    continue

                base_config_map = {
                    70: os.path.join(CONFIG.neox_repo, "configs", "pythia", "70M.yml"),
                    160: os.path.join(CONFIG.neox_repo, "configs", "pythia", "160M.yml"),
                }
                base_cfg = base_config_map[scale]
                neox_cfg = build_neox_config(scale, binary_prefix, seed, ckpt_dir, base_cfg)

                record = {
                    "run_id": run_id,
                    "variant": variant["condition"],
                    "scale": scale,
                    "seed": seed,
                    "checkpoint_dir": ckpt_dir,
                    "status": "running",
                    "hf_checkpoint_paths": [],
                    "error_msg": None,
                }
                state[run_id] = record
                _save_training_state(state)

                exit_code = launch_neox_run(neox_cfg, CONFIG.neox_repo)

                if exit_code == 0:
                    hf_paths = list_checkpoints(ckpt_dir)
                    record["hf_checkpoint_paths"] = hf_paths
                    record["status"] = "done"
                else:
                    record["status"] = "error"
                    record["error_msg"] = f"exit_code={exit_code}"

                state[run_id] = record
                _save_training_state(state)
                _upsert(records, record)

    return records
