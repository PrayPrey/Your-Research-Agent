"""
Training Orchestrator for h-e1
Fine-tune LLaMA-2-7B on curated instruction datasets
"""
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from typing import List, Dict
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_instruction_dataset(
    samples: List[Dict],
    tokenizer,
    max_length: int = 512
) -> Dataset:
    """
    Prepare instruction dataset with proper formatting.

    Args:
        samples: [{"instruction": str, "input": str, "output": str}]
        tokenizer: HuggingFace tokenizer
        max_length: Max sequence length

    Returns:
        HuggingFace Dataset with tokenized samples
    """

    def format_instruction(sample):
        instruction = sample.get('instruction', '')
        input_text = sample.get('input', '')
        output = sample.get('output', '')

        # Alpaca template per 02c spec
        if input_text:
            prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
        else:
            prompt = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"

        return prompt

    # Format and tokenize
    formatted_texts = [format_instruction(s) for s in samples]
    tokenized = tokenizer(
        formatted_texts,
        truncation=True,
        max_length=max_length,
        padding=False,
        return_tensors=None
    )

    # Create labels (same as input_ids for causal LM)
    tokenized['labels'] = tokenized['input_ids'].copy()

    return Dataset.from_dict(tokenized)


def train_model(
    model_name: str,
    train_samples: List[Dict],
    val_samples: List[Dict],
    output_dir: str,
    num_epochs: int = 3,
    learning_rate: float = 2e-5,
    batch_size: int = 4,
    seed: int = 42
) -> Dict:
    """
    Fine-tune LLaMA-2-7B per 03_logic.md L-4 spec.

    Returns:
        {"model_path": str, "metrics": dict}
    """
    logger.info(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Set padding token (LLaMA doesn't have one by default)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    logger.info(f"Preparing datasets (train={len(train_samples)}, val={len(val_samples)})...")
    train_dataset = prepare_instruction_dataset(train_samples, tokenizer)
    val_dataset = prepare_instruction_dataset(val_samples, tokenizer)

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Causal LM (not masked LM)
    )

    # Training arguments per 03_config.md
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        seed=seed,
        fp16=True,
        dataloader_num_workers=4,
        remove_unused_columns=False
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )

    logger.info("Starting training...")
    train_result = trainer.train()

    logger.info(f"Saving model to {output_dir}")
    trainer.save_model(output_dir)

    # Metrics
    metrics = {
        "train_loss": train_result.metrics.get("train_loss"),
        "eval_loss": trainer.evaluate().get("eval_loss"),
        "train_runtime": train_result.metrics.get("train_runtime"),
        "train_samples_per_second": train_result.metrics.get("train_samples_per_second")
    }

    return {"model_path": output_dir, "metrics": metrics}


if __name__ == "__main__":
    # PoC test (smoke test only - not full training)
    from curation import curate_dataset

    print("=== PoC: Loading curated dataset ===")
    cache_dir = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_data_problems/docs/youra_research/.data_cache/datasets/alpaca"
    curated, stats = curate_dataset(cache_dir=cache_dir)

    # Split train/val (90/10)
    split_idx = int(len(curated) * 0.9)
    train_samples = curated[:split_idx]
    val_samples = curated[split_idx:]

    print(f"Train: {len(train_samples)}, Val: {len(val_samples)}")
    print("\n=== PoC: Smoke test (1 epoch, 10 samples) ===")

    # Tiny smoke test
    result = train_model(
        model_name="meta-llama/Llama-2-7b-hf",
        train_samples=train_samples[:10],
        val_samples=val_samples[:5],
        output_dir="./outputs/smoke_test",
        num_epochs=1,
        batch_size=2,
        seed=42
    )

    print(f"Smoke test complete: {result['metrics']}")
