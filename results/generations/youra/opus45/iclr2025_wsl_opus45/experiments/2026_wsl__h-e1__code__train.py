"""
LoRA Training Pipeline for H-E1

Trains LoRA adapters on multiple tasks with deterministic seeding.
"""

import os
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType

from config import (
    BASE_MODEL_ID,
    LORA_CONFIG,
    TRAIN_CONFIG,
    DATASETS,
    PRIMARY_SEED,
    ADAPTERS_PER_TASK,
    ADAPTER_DIR,
)
from data import load_and_format_dataset, tokenize_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_base_model_sha256(model_id: str) -> str:
    """
    Compute SHA-256 hash of model config for provenance tracking.

    Args:
        model_id: HuggingFace model ID

    Returns:
        Hex digest of model config hash
    """
    from huggingface_hub import hf_hub_download

    try:
        config_path = hf_hub_download(repo_id=model_id, filename="config.json")
        with open(config_path, "rb") as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()[:16]
    except Exception as e:
        logger.warning(f"Could not compute SHA256: {e}")
        return "unknown"


def load_base_model(model_id: str) -> tuple:
    """
    Load Llama-3.2-1B-Instruct with bfloat16.

    Args:
        model_id: HuggingFace model ID

    Returns:
        Tuple of (model, tokenizer)
    """
    logger.info(f"Loading model: {model_id}")

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16 if TRAIN_CONFIG["bf16"] else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )

    if TRAIN_CONFIG["gradient_checkpointing"]:
        model.gradient_checkpointing_enable()

    return model, tokenizer


def build_lora_model(base_model, lora_cfg: dict):
    """
    Wrap base model with PEFT LoRA configuration.

    Args:
        base_model: HuggingFace model
        lora_cfg: LoRA configuration dict

    Returns:
        PeftModel with LoRA adapters
    """
    peft_config = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["lora_alpha"],
        lora_dropout=lora_cfg["lora_dropout"],
        bias=lora_cfg["bias"],
        task_type=TaskType.CAUSAL_LM,
        target_modules=lora_cfg["target_modules"],
    )

    model = get_peft_model(base_model, peft_config)
    model.print_trainable_parameters()

    return model


def set_deterministic(seed: int) -> None:
    """
    Set all random seeds for reproducibility.

    Args:
        seed: Random seed value
    """
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    # Deterministic operations
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Set environment variable for full determinism
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"


def train_single_adapter(
    task_name: str,
    seed: int,
    output_dir: str,
    train_cfg: Optional[dict] = None,
) -> dict:
    """
    Train one LoRA adapter for a specific task and seed.

    Args:
        task_name: Name of the task
        seed: Random seed
        output_dir: Directory to save adapter
        train_cfg: Training configuration (default: TRAIN_CONFIG)

    Returns:
        Metadata dict with training info
    """
    if train_cfg is None:
        train_cfg = TRAIN_CONFIG

    # Set deterministic seed
    set_deterministic(seed)

    # Load base model fresh for each adapter
    model, tokenizer = load_base_model(BASE_MODEL_ID)

    # Build LoRA model
    model = build_lora_model(model, LORA_CONFIG)

    # Load and tokenize dataset
    dataset = load_and_format_dataset(task_name, max_samples=train_cfg["max_samples"])
    tokenized_dataset = tokenize_dataset(dataset, tokenizer, max_length=train_cfg["max_length"])

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=train_cfg["epochs"],
        per_device_train_batch_size=train_cfg["batch_size"],
        learning_rate=train_cfg["lr"],
        warmup_ratio=train_cfg["warmup_ratio"],
        weight_decay=train_cfg["weight_decay"],
        optim=train_cfg["optimizer"],
        lr_scheduler_type=train_cfg["lr_scheduler_type"],
        bf16=train_cfg["bf16"],
        logging_steps=50,
        save_strategy="no",  # Only save at end
        seed=seed,
        data_seed=seed,
        report_to="none",
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # Train
    logger.info(f"Training adapter: {task_name} (seed={seed})")
    train_result = trainer.train()

    # Save adapter
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    # Compute SHA256 for provenance
    sha256 = verify_base_model_sha256(BASE_MODEL_ID)

    # Build metadata
    metadata = {
        "task": task_name,
        "seed": seed,
        "output_dir": output_dir,
        "base_model_sha256": sha256,
        "train_loss": train_result.training_loss,
        "train_steps": train_result.global_step,
        "timestamp": datetime.now().isoformat(),
    }

    # Save metadata
    with open(os.path.join(output_dir, "training_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # Clear GPU memory
    del model, trainer
    torch.cuda.empty_cache()

    return metadata


def run_training_pipeline(hypothesis_folder: str) -> list:
    """
    Train all adapters for the experiment.

    Creates 200 adapters: 8 tasks x 20 seeds + control variations.
    Skips already-saved adapters for resumability.

    Args:
        hypothesis_folder: Base folder for hypothesis outputs

    Returns:
        List of metadata dicts for all trained adapters
    """
    adapter_dir = os.path.join(hypothesis_folder, "adapters")
    os.makedirs(adapter_dir, exist_ok=True)

    all_metadata = []
    tasks = list(DATASETS.keys())

    # Generate seed list: 20 seeds per task
    # Seeds 0-19 for main experiment
    seeds = list(range(ADAPTERS_PER_TASK))

    total_adapters = len(tasks) * len(seeds)
    completed = 0

    logger.info(f"Training {total_adapters} adapters ({len(tasks)} tasks x {len(seeds)} seeds)")

    for task_name in tasks:
        for seed in seeds:
            # Output directory for this adapter
            output_dir = os.path.join(adapter_dir, f"{task_name}_seed{seed}")

            # Check if already trained (resume support)
            metadata_file = os.path.join(output_dir, "training_metadata.json")
            if os.path.exists(metadata_file):
                logger.info(f"Skipping {task_name}_seed{seed} (already exists)")
                with open(metadata_file) as f:
                    all_metadata.append(json.load(f))
                completed += 1
                continue

            # Train adapter
            try:
                metadata = train_single_adapter(task_name, seed, output_dir)
                all_metadata.append(metadata)
                completed += 1
                logger.info(f"Progress: {completed}/{total_adapters}")
            except Exception as e:
                logger.error(f"Failed to train {task_name}_seed{seed}: {e}")
                continue

    # Save combined metadata
    combined_path = os.path.join(adapter_dir, "all_adapters_metadata.json")
    with open(combined_path, "w") as f:
        json.dump(all_metadata, f, indent=2)

    logger.info(f"Training complete: {len(all_metadata)}/{total_adapters} adapters")

    return all_metadata


if __name__ == "__main__":
    from config import HYPOTHESIS_FOLDER

    print(f"Starting training pipeline for: {HYPOTHESIS_FOLDER}")
    metadata = run_training_pipeline(HYPOTHESIS_FOLDER)
    print(f"Trained {len(metadata)} adapters")
