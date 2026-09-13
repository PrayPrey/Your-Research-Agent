"""Training script for h-m2: Fine-tune GPT-2 on dataset variants."""

import json
import yaml
import torch
from pathlib import Path
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

def load_variant(condition: str) -> list:
    """Load dataset variant."""
    path = Path(f"data/dolly_variants/{condition}/train.jsonl")
    samples = []
    with open(path) as f:
        for line in f:
            samples.append(json.loads(line))
    return samples

def format_instruction(sample):
    """Format Dolly sample as instruction-response."""
    return f"Instruction: {sample['instruction']}\nResponse: {sample['response']}"

def train_model(condition: str):
    """Train model on single condition."""
    print(f"\nTraining {condition}...")

    # Load config
    with open("config/train_config.yaml") as f:
        config = yaml.safe_load(f)

    # Load data
    samples = load_variant(condition)
    texts = [format_instruction(s) for s in samples]
    dataset = Dataset.from_dict({"text": texts})

    print(f"Training samples: {len(dataset)}")

    # Load model and tokenizer
    model_name = config["model"]["name"]
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    model = GPT2LMHeadModel.from_pretrained(model_name)

    # Tokenize
    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=config["model"]["max_seq_length"],
            padding="max_length"
        )

    tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])

    # Training args
    training_config = config["training"]
    output_dir = f"models/{condition}"
    args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=training_config["epochs"],
        per_device_train_batch_size=training_config["batch_size"],
        gradient_accumulation_steps=training_config["gradient_accumulation_steps"],
        learning_rate=training_config["learning_rate"],
        warmup_steps=training_config["warmup_steps"],
        lr_scheduler_type=training_config["lr_scheduler"],
        logging_steps=training_config["logging_steps"],
        save_strategy=training_config["save_strategy"],
        save_total_limit=training_config["save_total_limit"],
        seed=training_config["seed"],
        fp16=training_config["fp16"]
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )

    # Train
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    print(f"Saved checkpoint to {output_dir}")
    return output_dir

def main():
    conditions = ["baseline", "transferred_indep", "tuned_indep", "transferred_dep", "tuned_dep"]

    checkpoints = {}
    for condition in conditions:
        checkpoint = train_model(condition)
        checkpoints[condition] = checkpoint

    # Save checkpoint paths
    with open("results/checkpoints.yaml", "w") as f:
        yaml.dump(checkpoints, f)

    print("\nAll models trained.")

if __name__ == "__main__":
    main()
