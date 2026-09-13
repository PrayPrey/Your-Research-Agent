"""H-M2 Training Orchestration: gpt-neox subprocess launcher for Pythia-1B."""
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from config import HM2Config, ALL_CONFIGS, load_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def find_gptneox_launcher() -> Optional[str]:
    """Find the gpt-neox deepy.py launcher."""
    candidates = [
        Path(__file__).parent.parent.parent / "gpt-neox" / "deepy.py",
        Path("/workspace/gpt-neox/deepy.py"),
        Path(os.environ.get("GPTNEOX_DIR", "")) / "deepy.py",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def train_single_config(
    config_id: str,
    yaml_path: str,
    cfg: HM2Config,
    gpu_id: int = 1,
    dry_run: bool = False,
) -> Dict:
    """Launch gpt-neox training for a single corpus config.

    Returns dict with status and log path.
    """
    checkpoint_dir = Path(cfg.checkpoints_dir) / f"config_{config_id}"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    log_path = str(Path(cfg.results_dir) / f"train_{config_id}.log")
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)

    launcher = find_gptneox_launcher()
    if launcher is None:
        logger.warning(f"gpt-neox launcher not found. Using HuggingFace Trainer fallback for {config_id}.")
        return _hf_train(config_id, checkpoint_dir, cfg)

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    cmd = [
        sys.executable, launcher,
        "train.py",
        "--conf", yaml_path,
    ]

    logger.info(f"[train] Launching {config_id}: {' '.join(cmd)}")

    if dry_run:
        logger.info(f"[train] DRY RUN — not executing: {cmd}")
        return {"status": "dry_run", "config_id": config_id, "log": log_path}

    with open(log_path, "w") as log_f:
        proc = subprocess.run(
            cmd,
            env=env,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            text=True,
        )

    if proc.returncode == 0:
        logger.info(f"[train] {config_id} completed successfully")
        return {"status": "success", "config_id": config_id, "log": log_path}
    else:
        logger.error(f"[train] {config_id} FAILED (rc={proc.returncode})")
        return {"status": "failed", "config_id": config_id, "log": log_path,
                "returncode": proc.returncode}


def _hf_train(config_id: str, checkpoint_dir: Path, cfg: HM2Config) -> Dict:
    """HuggingFace Trainer fallback: train real Pythia-1B on DCLM-POOL JSONL corpus.

    Used when gpt-neox deepy.py is not installed. Trains on the real corpus data
    using HuggingFace Trainer with the Pythia-1B architecture and specified
    hyperparameters from the experiment spec.
    """
    import math
    import torch
    from transformers import (
        AutoTokenizer,
        GPTNeoXConfig,
        GPTNeoXForCausalLM,
        Trainer,
        TrainingArguments,
        DataCollatorForLanguageModeling,
    )
    from datasets import Dataset
    from data_prep import load_corpus

    corpus_path = str(Path(cfg.he1_data_dir) / f"{config_id}.jsonl")
    if not Path(corpus_path).exists():
        logger.error(f"[train] Corpus not found: {corpus_path}")
        return {"status": "failed", "config_id": config_id, "reason": "corpus_not_found"}

    logger.info(f"[train] HF Trainer fallback for {config_id} — loading corpus from {corpus_path}")

    # Load real Pythia-1B architecture
    model_cfg = GPTNeoXConfig(
        hidden_size=cfg.hidden_size,
        num_hidden_layers=cfg.num_layers,
        num_attention_heads=cfg.num_attention_heads,
        intermediate_size=cfg.hidden_size * 4,
        vocab_size=cfg.vocab_size,
        max_position_embeddings=cfg.max_seq_len,
        use_parallel_residual=True,
        rotary_pct=0.25,
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    logger.info(f"[train] Initializing Pythia-1B ({cfg.hidden_size}h, {cfg.num_layers}L) on {device}")
    model = GPTNeoXForCausalLM(model_cfg)
    if dtype == torch.bfloat16:
        model = model.to(dtype)
    model = model.to(device)

    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m", use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load real corpus texts
    logger.info(f"[train] Loading corpus: {corpus_path}")
    texts = load_corpus(corpus_path)
    logger.info(f"[train] Loaded {len(texts)} documents from {corpus_path}")

    # Tokenize and chunk into fixed-length sequences
    seq_length = min(cfg.max_seq_len, 512)  # cap at 512 for memory
    logger.info(f"[train] Tokenizing and chunking to seq_length={seq_length}")

    all_input_ids = []
    for text in texts:
        ids = tokenizer.encode(text, add_special_tokens=True, truncation=False)
        for i in range(0, len(ids) - seq_length + 1, seq_length):
            all_input_ids.append(ids[i:i + seq_length])

    if not all_input_ids:
        logger.error(f"[train] No sequences produced from corpus {corpus_path}")
        return {"status": "failed", "config_id": config_id, "reason": "no_sequences"}

    logger.info(f"[train] {len(all_input_ids)} training sequences of length {seq_length}")

    dataset = Dataset.from_dict({"input_ids": all_input_ids})

    # Determine number of training steps based on token budget
    # Each step processes global_batch_size sequences × seq_length tokens
    tokens_per_step = cfg.global_batch_size * seq_length
    total_tokens = len(all_input_ids) * seq_length
    # Run up to train_iters_quick steps, limited by available data
    max_steps = min(cfg.train_iters_quick, len(all_input_ids) // cfg.global_batch_size)
    max_steps = max(max_steps, 1)
    warmup_steps = max(1, int(max_steps * cfg.warmup_fraction))

    logger.info(f"[train] Training for {max_steps} steps (token_budget={total_tokens:,}, warmup={warmup_steps})")

    save_path = checkpoint_dir / "hf_model"
    training_args = TrainingArguments(
        output_dir=str(save_path),
        max_steps=max_steps,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=cfg.global_batch_size,
        learning_rate=cfg.lr,
        adam_beta1=cfg.adam_beta1,
        adam_beta2=cfg.adam_beta2,
        adam_epsilon=cfg.adam_eps,
        weight_decay=cfg.weight_decay,
        lr_scheduler_type="cosine",
        warmup_steps=warmup_steps,
        bf16=(device == "cuda" and dtype == torch.bfloat16),
        fp16=False,
        gradient_checkpointing=True,
        logging_steps=max(1, max_steps // 20),
        save_steps=max_steps,  # save only at end
        save_total_limit=1,
        seed=cfg.seed,
        dataloader_num_workers=0,
        report_to="none",
        use_cpu=(device == "cpu"),
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )

    logger.info(f"[train] Starting HF Trainer training for {config_id}")
    trainer.train()

    model.save_pretrained(str(save_path))
    logger.info(f"[train] HF checkpoint saved: {save_path}")
    return {"status": "success", "config_id": config_id, "checkpoint": str(save_path)}


def train_all_configs(
    cfg: HM2Config,
    configs: Optional[List[str]] = None,
    gpu_id: int = 1,
    sequential: bool = True,
    dry_run: bool = False,
) -> Dict[str, Dict]:
    """Train all (or specified) corpus configs sequentially.

    Args:
        cfg: HM2Config
        configs: List of config IDs to train (default: ALL_CONFIGS)
        gpu_id: GPU to use
        sequential: If True, train sequentially (required for single GPU)
        dry_run: If True, print commands without executing

    Returns:
        Dict mapping config_id -> result dict
    """
    if configs is None:
        configs = ALL_CONFIGS

    results = {}
    configs_dir = Path(cfg.configs_dir)

    for config_id in configs:
        yaml_path = str(configs_dir / f"pythia-1b-hm2-{config_id}.yml")
        if not Path(yaml_path).exists():
            logger.warning(f"[train] YAML config not found: {yaml_path} — skipping")
            results[config_id] = {"status": "skipped", "reason": "yaml_not_found"}
            continue

        result = train_single_config(
            config_id=config_id,
            yaml_path=yaml_path,
            cfg=cfg,
            gpu_id=gpu_id,
            dry_run=dry_run,
        )
        results[config_id] = result

        if result["status"] == "failed":
            logger.error(f"[train] Stopping pipeline due to failure in {config_id}")
            break

    return results


def find_checkpoint(config_id: str, cfg: HM2Config) -> Optional[str]:
    """Find the latest HuggingFace-format checkpoint for a config."""
    checkpoint_dir = Path(cfg.checkpoints_dir) / f"config_{config_id}"

    # Look for HF-format checkpoint (from mock or converted)
    hf_path = checkpoint_dir / "hf_model"
    if hf_path.exists():
        return str(hf_path)

    # Look for gpt-neox checkpoint that can be loaded
    if checkpoint_dir.exists():
        return str(checkpoint_dir)

    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--configs", nargs="+", default=None, help="Config IDs to train")
    parser.add_argument("--gpu", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    results = train_all_configs(
        cfg=cfg,
        configs=args.configs,
        gpu_id=args.gpu,
        dry_run=args.dry_run,
    )
    print(json.dumps(results, indent=2))
