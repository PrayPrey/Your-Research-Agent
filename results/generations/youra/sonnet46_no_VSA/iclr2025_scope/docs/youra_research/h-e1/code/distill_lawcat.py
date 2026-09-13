"""LAWCAT 2-phase distillation wrapper for LLaMA-3-8B → linear attention student."""
import os
import sys
import json
import subprocess
import shutil
import tempfile
from pathlib import Path

import torch
import yaml

CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
LAWCAT_REPO = str(HYPOTHESIS_DIR / "repos" / "LAWCAT")

from config import (
    TEACHER_MODEL, CHECKPOINTS_DIR, HF_CACHE,
    LAWCAT_SEQ_LEN, LAWCAT_PHASE1_TOKENS, LAWCAT_PHASE2_TOKENS,
    LAWCAT_PHASE1_LR, LAWCAT_PHASE1_MSE_WEIGHT,
    LAWCAT_LORA_R, LAWCAT_LORA_ALPHA, LAWCAT_LORA_LR, LAWCAT_SEED,
)


def _tokens_to_steps(n_tokens: int, seq_len: int = LAWCAT_SEQ_LEN, batch_size: int = 8) -> int:
    """Convert token budget to training steps."""
    tokens_per_step = seq_len * batch_size
    return max(1, n_tokens // tokens_per_step)


def _write_lawcat_model_config(output_path: str, phase1_checkpoint: str | None = None) -> str:
    """Write model config YAML adapted for LLaMA-3-8B."""
    config = {
        "name": "llama",
        "model": {
            "pretrained_model_name_or_path": phase1_checkpoint if phase1_checkpoint else TEACHER_MODEL,
            "cache_dir": str(Path(HF_CACHE) / "hub"),
            "return_dict": True,
            "load_in_8bit": False,
            "load_in_4bit": False,
            "device_map": "auto",
            "low_cpu_mem_usage": True,
            "torch_dtype": "bfloat16",
        },
        "attention": {
            "attention_type": "lawcat_llama_window_sw_gla",
            "state_chunk_len": 12000,
            "window_size": 0,
            "sink_size": 0,
            "use_short_conv": True,
            "wo_conv_v": True,
            "la_init": "idt",
            "conv_init_coeff": 0.001,
            "norm_la_kv": True,
            "qk_activation": "identity",
            "repeat_bf_conv": True,
            "map_la_kv": 2,
            "use_output_gate": False,
            "affine_attention_factors": False,
            "feature_map": "softmax_dim",
            "feature_map_kwargs": {"eps": 1e-12, "fullspace": True},
            "layer_idx": None,
            "learned_kernel": "untied_head_einsum",
            "learned_kernel_kwargs": {
                "feature_dim": 64,
                "skip_connection": False,
                "bias": False,
                "zero_init": False,
            },
            "tie_qk_kernels": True,
            "train_qk": False,
        },
    }
    with open(output_path, "w") as f:
        yaml.dump(config, f)
    return output_path


def _write_lawcat_distill_config(
    output_path: str,
    n_tokens: int,
    lr: float,
    mse_weight: float,
    seq_len: int,
    checkpoint_dir: str,
    seed: int,
) -> str:
    """Write distillation experiment config using alpaca_clean dataset."""
    max_steps = _tokens_to_steps(n_tokens, seq_len, batch_size=8)

    config = {
        "dataset": {
            "name": "alpaca_clean",
            "dataset_config": {
                "name": "default",
                "path": "yahma/alpaca-cleaned",
                "chunk_size": seq_len,
                "concat_data": True,
                "cache_dir": str(Path(HF_CACHE) / "datasets"),
            },
            "pretrained_model_config": {
                "pretrained_model_name_or_path": "",
                "cache_dir": str(Path(HF_CACHE) / "hub"),
            },
            "preprocess_config": None,
        },
        "dataloader": {
            "batch_size": 1,
            "num_workers": 4,
            "drop_last": False,
            "pin_memory": True,
        },
        "optimizer": {
            "optim": "adamw_torch",
            "lr": lr,
            "weight_decay": 0.0,
        },
        "lr_scheduler": {
            "lr_scheduler_type": "cosine",
            "num_warmup_steps": 100,
        },
        "trainer": {
            "name": "distill_attention_xent_mse",
            "reverse_kl": False,
            "mse_factor": mse_weight,
            "xent_factor": 0.0,
            "reg_factor": 0.0,
            "train_gumbel_gate": False,
            "bf16": True,
            "train_split": "train",
            "val_split": "validation",
            "num_train_epochs": 100,
            "gradient_accumulation_steps": 8,
            "seed": seed,
            "batch_size": 1,
            "load_best_model_at_end": False,
            "greater_is_better": False,
            "metric_for_best_model": "distill/eval/loss",
            "logging_steps": 100,
            "evaluation_strategy": "steps",
            "max_steps": max_steps,
            "eval_steps": max(100, max_steps // 10),
            "max_eval_batches": 50,
            "output_dir": checkpoint_dir,
            "save_steps": max(500, max_steps // 5),
        },
    }
    with open(output_path, "w") as f:
        yaml.dump(config, f)
    return output_path


def _write_lawcat_finetune_config(
    output_path: str,
    n_tokens: int,
    seq_len: int,
    lora_r: int,
    lora_alpha: int,
    lr: float,
    checkpoint_dir: str,
    seed: int,
) -> str:
    """Write LoRA fine-tune config using alpaca_clean dataset."""
    max_steps = _tokens_to_steps(n_tokens, seq_len, batch_size=8)

    config = {
        "dataset": {
            "name": "alpaca_clean",
            "dataset_config": {
                "name": "default",
                "path": "yahma/alpaca-cleaned",
                "chunk_size": seq_len,
                "concat_data": True,
                "cache_dir": str(Path(HF_CACHE) / "datasets"),
            },
            "pretrained_model_config": {
                "pretrained_model_name_or_path": "",
                "cache_dir": str(Path(HF_CACHE) / "hub"),
            },
            "preprocess_config": None,
        },
        "dataloader": {
            "batch_size": 1,
            "num_workers": 4,
            "drop_last": False,
            "pin_memory": True,
        },
        "optimizer": {
            "optim": "adamw_torch",
            "lr": lr,
            "weight_decay": 0.0,
        },
        "lr_scheduler": {
            "lr_scheduler_type": "cosine",
            "num_warmup_steps": 100,
        },
        "trainer": {
            "name": "default_lm",
            "bf16": True,
            "train_split": "train",
            "val_split": "validation",
            "num_train_epochs": 100,
            "gradient_accumulation_steps": 8,
            "seed": seed,
            "batch_size": 1,
            "load_best_model_at_end": False,
            "metric_for_best_model": "eval/loss",
            "logging_steps": 100,
            "evaluation_strategy": "steps",
            "max_steps": max_steps,
            "eval_steps": max(100, max_steps // 10),
            "max_eval_batches": 50,
            "output_dir": checkpoint_dir,
            "save_steps": max(500, max_steps // 5),
        },
        "finetune": {
            "method": "lora",
            "kwargs": {
                "r": lora_r,
                "lora_alpha": lora_alpha,
                "lora_dropout": 0.0,
                "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
            },
        },
    }
    with open(output_path, "w") as f:
        yaml.dump(config, f)
    return output_path


def run_lawcat_phase1(
    teacher_path: str = TEACHER_MODEL,
    output_dir: str | None = None,
    n_tokens: int = LAWCAT_PHASE1_TOKENS,
    lr: float = LAWCAT_PHASE1_LR,
    mse_weight: float = LAWCAT_PHASE1_MSE_WEIGHT,
    seed: int = LAWCAT_SEED,
) -> str:
    """Run LAWCAT Phase 1: MSE alignment on C4. Returns checkpoint path."""
    if output_dir is None:
        output_dir = str(CHECKPOINTS_DIR / "lawcat" / "phase1")
    os.makedirs(output_dir, exist_ok=True)

    cfg_dir = Path(output_dir) / "configs"
    cfg_dir.mkdir(exist_ok=True)

    model_cfg = _write_lawcat_model_config(str(cfg_dir / "model_8b.yaml"))
    distill_cfg = _write_lawcat_distill_config(
        str(cfg_dir / "distill_c4_phase1.yaml"),
        n_tokens=n_tokens, lr=lr, mse_weight=mse_weight,
        seq_len=LAWCAT_SEQ_LEN, checkpoint_dir=output_dir, seed=seed,
    )

    env = os.environ.copy()
    env["HF_HOME"] = HF_CACHE
    env["PYTHONPATH"] = str(HYPOTHESIS_DIR / "repos" / "LAWCAT" / "src")
    env["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"
    env["TOKENIZERS_PARALLELISM"] = "false"

    cmd = [
        sys.executable, "distill_llama.py",
        "--model_config", os.path.basename(model_cfg).replace(".yaml", ""),
        "--distill_config", os.path.basename(distill_cfg).replace(".yaml", ""),
        "--lk_zero_init",
        "--seed", str(seed),
    ]

    # LAWCAT expects configs in ./configs/model/ and ./configs/experiment/
    # We write them there temporarily
    lawcat_model_dir = Path(LAWCAT_REPO) / "configs" / "model"
    lawcat_exp_dir = Path(LAWCAT_REPO) / "configs" / "experiment"
    lawcat_model_dir.mkdir(exist_ok=True)
    lawcat_exp_dir.mkdir(exist_ok=True)

    shutil.copy(model_cfg, lawcat_model_dir / "model_8b.yaml")
    shutil.copy(distill_cfg, lawcat_exp_dir / "distill_c4_phase1.yaml")

    print(f"[LAWCAT Phase 1] Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=LAWCAT_REPO, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"LAWCAT Phase 1 failed with code {result.returncode}")

    # Find checkpoint
    ckpts = sorted(Path(output_dir).glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1]))
    if ckpts:
        return str(ckpts[-1])
    if (Path(output_dir) / "config.json").exists():
        return output_dir
    raise RuntimeError(f"No checkpoint found in {output_dir}")


def run_lawcat_phase2_lora(
    phase1_checkpoint: str,
    output_dir: str | None = None,
    n_tokens: int = LAWCAT_PHASE2_TOKENS,
    lora_r: int = LAWCAT_LORA_R,
    lora_alpha: int = LAWCAT_LORA_ALPHA,
    lr: float = LAWCAT_LORA_LR,
    seed: int = LAWCAT_SEED,
) -> str:
    """Run LAWCAT Phase 2: LoRA fine-tuning. Returns merged checkpoint path."""
    if output_dir is None:
        output_dir = str(CHECKPOINTS_DIR / "lawcat" / "phase2")
    os.makedirs(output_dir, exist_ok=True)

    cfg_dir = Path(output_dir) / "configs"
    cfg_dir.mkdir(exist_ok=True)

    model_cfg = _write_lawcat_model_config(
        str(cfg_dir / "model_8b_phase2.yaml"),
        phase1_checkpoint=phase1_checkpoint,
    )
    finetune_cfg = _write_lawcat_finetune_config(
        str(cfg_dir / "finetune_lora_c4.yaml"),
        n_tokens=n_tokens, seq_len=LAWCAT_SEQ_LEN,
        lora_r=lora_r, lora_alpha=lora_alpha, lr=lr,
        checkpoint_dir=output_dir, seed=seed,
    )

    lawcat_model_dir = Path(LAWCAT_REPO) / "configs" / "model"
    lawcat_exp_dir = Path(LAWCAT_REPO) / "configs" / "experiment"
    shutil.copy(model_cfg, lawcat_model_dir / "model_8b_phase2.yaml")
    shutil.copy(finetune_cfg, lawcat_exp_dir / "finetune_lora_c4.yaml")

    env = os.environ.copy()
    env["HF_HOME"] = HF_CACHE
    env["PYTHONPATH"] = str(HYPOTHESIS_DIR / "repos" / "LAWCAT" / "src")
    env["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"
    env["TOKENIZERS_PARALLELISM"] = "false"

    cmd = [
        sys.executable, "distill_llama.py",
        "--model_config", "model_8b_phase2",
        "--finetune_config", "finetune_lora_c4",
        "--load_distill_checkpoint", phase1_checkpoint,
        "--seed", str(seed),
    ]

    print(f"[LAWCAT Phase 2] Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=LAWCAT_REPO, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"LAWCAT Phase 2 failed with code {result.returncode}")

    ckpts = sorted(Path(output_dir).glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1]))
    if ckpts:
        return str(ckpts[-1])
    if (Path(output_dir) / "config.json").exists():
        return output_dir
    raise RuntimeError(f"No checkpoint found in {output_dir}")


def run_full_lawcat_pipeline(output_base: str | None = None) -> str:
    """Run LAWCAT Phase 1 + Phase 2. Returns final checkpoint path."""
    if output_base is None:
        output_base = str(CHECKPOINTS_DIR / "lawcat")

    print("=" * 60)
    print("LAWCAT Phase 1: MSE Alignment")
    p1_ckpt = run_lawcat_phase1(output_dir=os.path.join(output_base, "phase1"))
    print(f"Phase 1 complete: {p1_ckpt}")

    print("=" * 60)
    print("LAWCAT Phase 2: LoRA Fine-tuning")
    p2_ckpt = run_lawcat_phase2_lora(
        phase1_checkpoint=p1_ckpt,
        output_dir=os.path.join(output_base, "phase2"),
    )
    print(f"Phase 2 complete: {p2_ckpt}")

    return p2_ckpt


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--phase", type=int, choices=[1, 2, 0], default=0,
                   help="0=full pipeline")
    p.add_argument("--phase1-checkpoint", type=str, default=None)
    p.add_argument("--output-dir", type=str, default=str(CHECKPOINTS_DIR / "lawcat"))
    args = p.parse_args()

    if args.phase == 0:
        final_ckpt = run_full_lawcat_pipeline(args.output_dir)
        print(f"LAWCAT pipeline complete: {final_ckpt}")
    elif args.phase == 1:
        ckpt = run_lawcat_phase1(output_dir=os.path.join(args.output_dir, "phase1"))
        print(f"Phase 1 complete: {ckpt}")
    elif args.phase == 2:
        if not args.phase1_checkpoint:
            raise ValueError("--phase1-checkpoint required for phase 2")
        ckpt = run_lawcat_phase2_lora(
            phase1_checkpoint=args.phase1_checkpoint,
            output_dir=os.path.join(args.output_dir, "phase2"),
        )
        print(f"Phase 2 complete: {ckpt}")
