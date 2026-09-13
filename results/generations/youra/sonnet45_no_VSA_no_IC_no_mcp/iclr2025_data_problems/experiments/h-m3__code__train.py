"""Fine-tune Llama-2-7B on subsets."""
import torch
import time
import yaml
import numpy as np
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    set_seed
)
from typing import Dict


def load_config(config_path: str = "config/experiment_config.yaml") -> dict:
    """Load experiment config."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def tokenize_dataset(
    dataset: Dataset,
    tokenizer,
    max_length: int = 512,
    text_column: str = "text"
) -> Dataset:
    """Tokenize text samples."""
    def tokenize_fn(examples):
        return tokenizer(
            examples[text_column],
            max_length=max_length,
            truncation=True,
            padding="max_length"
        )

    tokenized = dataset.map(
        tokenize_fn,
        batched=True,
        remove_columns=dataset.column_names
    )
    return tokenized


def train_llama(
    train_dataset: Dataset,
    output_dir: str,
    config: dict
) -> dict:
    """
    Fine-tune Llama-2-7B on subset.
    Returns: {train_loss: float, train_time: float}
    """
    set_seed(config["training"]["seed"])

    print(f"\n=== Training: {output_dir} ===")
    print(f"Dataset size: {len(train_dataset)}")

    # Load model and tokenizer
    print(f"Loading model: {config['base_model']['model_id']}")
    model = AutoModelForCausalLM.from_pretrained(
        config["base_model"]["model_id"],
        cache_dir=config["base_model"]["cache_dir"],
        torch_dtype=torch.bfloat16 if config["training"]["bf16"] else torch.float32
    )
    tokenizer = AutoTokenizer.from_pretrained(config["base_model"]["model_id"])
    tokenizer.pad_token = tokenizer.eos_token

    # Tokenize dataset
    print("Tokenizing dataset...")
    tokenized = tokenize_dataset(
        dataset=train_dataset,
        tokenizer=tokenizer,
        max_length=config["base_model"]["max_seq_length"]
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=config["training"]["num_train_epochs"],
        per_device_train_batch_size=config["training"]["per_device_train_batch_size"],
        gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
        learning_rate=config["training"]["learning_rate"],
        warmup_steps=config["training"]["warmup_steps"],
        lr_scheduler_type=config["training"]["lr_scheduler_type"],
        weight_decay=config["training"]["weight_decay"],
        max_grad_norm=config["training"]["max_grad_norm"],
        bf16=config["training"]["bf16"],
        fp16=config["training"]["fp16"],
        logging_steps=config["training"]["logging_steps"],
        save_strategy=config["training"]["save_strategy"],
        save_total_limit=config["training"]["save_total_limit"],
        seed=config["training"]["seed"]
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )

    # Train
    print("Training...")
    start = time.time()
    train_result = trainer.train()
    train_time = time.time() - start

    # Save model
    trainer.save_model(output_dir)
    print(f"✓ Saved model to {output_dir}")

    return {
        "train_loss": train_result.training_loss,
        "train_time": train_time
    }


def train_all_conditions(config: dict) -> dict:
    """
    Train 10 models (9 subsets + baseline).
    Returns: {condition: {"checkpoint": str, "loss": float, "time": float}}
    """
    from load_data import load_and_format_dolly

    # Load full dataset
    dataset, texts = load_and_format_dolly(config["dataset"]["cache_dir"])

    # Prepare text column
    dataset = dataset.add_column("text", texts)

    results = {}

    # Baseline (full dataset)
    print("\n" + "=" * 60)
    print("TRAINING BASELINE (full dataset)")
    print("=" * 60)
    output_dir = f"{config['paths']['models_dir']}baseline"
    train_result = train_llama(dataset, output_dir, config)
    results["baseline"] = {
        "checkpoint": output_dir,
        "loss": train_result["train_loss"],
        "time": train_result["train_time"]
    }

    # Subset conditions
    for stage in ["early", "mid", "late"]:
        for k in config["dataset"]["subset_sizes"]:
            condition = f"{stage}_k{k}"
            print("\n" + "=" * 60)
            print(f"TRAINING {condition}")
            print("=" * 60)

            # Load subset indices
            indices_path = f"{config['paths']['subsets_dir']}{condition}_indices.npy"
            indices = np.load(indices_path)

            # Select subset
            subset_dataset = dataset.select(indices.tolist())

            # Train
            output_dir = f"{config['paths']['models_dir']}{condition}"
            train_result = train_llama(subset_dataset, output_dir, config)
            results[condition] = {
                "checkpoint": output_dir,
                "loss": train_result["train_loss"],
                "time": train_result["train_time"]
            }

    return results


if __name__ == "__main__":
    config = load_config()
    results = train_all_conditions(config)

    print("\n=== Training Summary ===")
    for condition, info in results.items():
        print(f"{condition:15s}: loss={info['loss']:.4f}, time={info['time']:.0f}s")

    print(f"\n✓ All models trained")
