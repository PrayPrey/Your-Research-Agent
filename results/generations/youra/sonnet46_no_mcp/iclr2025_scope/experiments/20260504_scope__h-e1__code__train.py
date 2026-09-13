import os
import logging
from transformers import (
    Trainer, TrainingArguments, AutoTokenizer,
    DataCollatorForSeq2Seq,
)
from config import TrainingConfig
from data import LongAlpacaDataset
from model import build_model

logger = logging.getLogger(__name__)


def get_training_args(cfg: TrainingConfig) -> TrainingArguments:
    return TrainingArguments(
        output_dir=cfg.output_dir,
        num_train_epochs=cfg.num_train_epochs,
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        learning_rate=cfg.learning_rate,
        warmup_ratio=cfg.warmup_ratio,
        lr_scheduler_type=cfg.lr_scheduler_type,
        fp16=cfg.fp16,
        bf16=cfg.bf16,
        seed=cfg.seed,
        dataloader_num_workers=cfg.dataloader_num_workers,
        save_strategy=cfg.save_strategy,
        logging_steps=cfg.logging_steps,
        report_to=cfg.report_to,
        run_name=cfg.run_name,
        remove_unused_columns=False,
        gradient_checkpointing=True,
        optim="adamw_torch",
        ddp_find_unused_parameters=False,
    )


def run_training(cfg: TrainingConfig) -> str:
    """Run full training for a single condition. Returns output_dir path."""
    os.makedirs(cfg.output_dir, exist_ok=True)

    logger.info(f"Loading tokenizer: {cfg.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name, use_fast=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info(f"Building model (condition={cfg.condition})")
    model = build_model(cfg)
    model.print_trainable_parameters()

    logger.info("Loading dataset")
    dataset = LongAlpacaDataset(tokenizer, max_seq_length=cfg.max_seq_length)

    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
        pad_to_multiple_of=8,
    )

    training_args = get_training_args(cfg)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=collator,
    )

    logger.info(f"Starting training: {cfg.run_name}")
    trainer.train()

    # Save adapter weights
    adapter_path = os.path.join(cfg.output_dir, "adapter")
    model.save_pretrained(adapter_path)
    tokenizer.save_pretrained(adapter_path)
    logger.info(f"Adapter saved to: {adapter_path}")

    return adapter_path
