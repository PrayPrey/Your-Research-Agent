"""Fallback training module — used only when H-E1 checkpoints are missing."""
import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

FALLBACK_TRAIN_CONFIG = {
    # H-E1 ExperimentConfig field names (verified from h-e1/code/config.py)
    "model_id": "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
    "seed": 1,
    "dtype": "bfloat16",
    "grpo_lr": 1e-6,
    "grpo_batch_size": 1,
    "grpo_grad_accum": 16,
    "grpo_num_generations": 4,
    "grpo_beta": 0.04,
    "grpo_steps": 200,       # reduced for fallback
    "grpo_save_steps": 100,
    "dpo_lr": 5e-7,
    "dpo_batch_size": 1,
    "dpo_grad_accum": 16,
    "dpo_beta": 0.1,
    "dpo_steps": 200,
    "dpo_save_steps": 100,
    "training_dataset": "sahil2801/CodeAlpaca-20k",
    "kl_prompt_count": 100,
    "dpo_min_pairs": 200,
    "kl_tolerance": 0.05,
    "bootstrap_samples": 1000,
    "bootstrap_ci": 0.95,
    "gate_magnitude": 0.20,
    "output_dir": "outputs",
    "figures_dir": "../figures",
    "checkpoint_dir": "../checkpoints/fallback",
}


def _get_h_e1_code_path() -> str:
    code_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(code_dir, "../../h-e1/code"))


def _build_fallback_cfg(checkpoint_subdir: str = "fallback"):
    h_e1_path = _get_h_e1_code_path()
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)
    from config import ExperimentConfig
    cfg = ExperimentConfig()
    for k, v in FALLBACK_TRAIN_CONFIG.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    cfg.checkpoint_dir = f"../checkpoints/fallback/{checkpoint_subdir}"
    return cfg


def train_grpo_binary(cfg_path: Optional[str] = None) -> str:
    """Re-trains GRPO with binary reward using H-E1 train_grpo.py.

    Returns checkpoint directory path.
    """
    logger.warning("Fallback: training GRPO-binary from scratch (H-E1 checkpoints missing)")
    h_e1_path = _get_h_e1_code_path()
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)

    cfg = _build_fallback_cfg("grpo_binary")
    output_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg.checkpoint_dir)
    )
    os.makedirs(output_dir, exist_ok=True)

    try:
        import train_grpo as tg
        tg.train(cfg, reward_type="binary", output_dir=output_dir)
    except Exception as e:
        logger.error(f"Fallback GRPO-binary training failed: {e}")
        raise

    logger.info(f"GRPO-binary fallback checkpoint: {output_dir}")
    return output_dir


def train_grpo_errortype(cfg_path: Optional[str] = None) -> str:
    """Re-trains GRPO with error-type reward.

    Returns checkpoint directory path.
    """
    logger.warning("Fallback: training GRPO-errortype from scratch")
    h_e1_path = _get_h_e1_code_path()
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)

    cfg = _build_fallback_cfg("grpo_errortype")
    output_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg.checkpoint_dir)
    )
    os.makedirs(output_dir, exist_ok=True)

    try:
        import train_grpo as tg
        tg.train(cfg, reward_type="error_type", output_dir=output_dir)
    except Exception as e:
        logger.error(f"Fallback GRPO-errortype training failed: {e}")
        raise

    return output_dir


def train_dpo(cfg_path: Optional[str] = None) -> str:
    """Re-trains DPO using H-E1 train_dpo.py.

    Returns checkpoint directory path.
    """
    logger.warning("Fallback: training DPO from scratch")
    h_e1_path = _get_h_e1_code_path()
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)

    cfg = _build_fallback_cfg("dpo")
    output_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg.checkpoint_dir)
    )
    os.makedirs(output_dir, exist_ok=True)

    try:
        import train_dpo as td
        td.train(cfg, output_dir=output_dir)
    except Exception as e:
        logger.error(f"Fallback DPO training failed: {e}")
        raise

    return output_dir


def main() -> None:
    """Fallback entry point — called if H-E1 checkpoints missing."""
    import argparse
    parser = argparse.ArgumentParser(description="H-M1 Fallback Training")
    parser.add_argument("--condition", choices=["grpo_binary", "grpo_errortype", "dpo", "all"],
                        default="all")
    args = parser.parse_args()

    if args.condition in ("grpo_binary", "all"):
        train_grpo_binary()
    if args.condition in ("grpo_errortype", "all"):
        train_grpo_errortype()
    if args.condition in ("dpo", "all"):
        train_dpo()


if __name__ == "__main__":
    main()
