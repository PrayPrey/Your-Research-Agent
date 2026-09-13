"""Training loops for H-C1 experiment with diversity control."""
import torch
from torch.utils.data import DataLoader
from transformers import Trainer, TrainingArguments, DataCollatorForSeq2Seq
from peft import PeftModel
from tqdm import tqdm

from config import Config
from model import RLCodeTrainer
from diversity_controller import FeedbackDiversityController


def prepare_ce_dataset(data: list[dict], tokenizer, max_length: int = 512):
    """Prepare dataset for CE training."""
    encodings = {"input_ids": [], "attention_mask": [], "labels": []}

    for item in data:
        prompt = item["prompt"]
        target = item.get("canonical_solution", "")
        if not target:
            continue

        inputs = tokenizer(prompt, truncation=True, max_length=max_length, padding="max_length")
        targets = tokenizer(target, truncation=True, max_length=max_length, padding="max_length")

        encodings["input_ids"].append(inputs["input_ids"])
        encodings["attention_mask"].append(inputs["attention_mask"])
        encodings["labels"].append(targets["input_ids"])

    return encodings


class CEDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __len__(self):
        return len(self.encodings["input_ids"])

    def __getitem__(self, idx):
        return {
            "input_ids": torch.tensor(self.encodings["input_ids"][idx]),
            "attention_mask": torch.tensor(self.encodings["attention_mask"][idx]),
            "labels": torch.tensor(self.encodings["labels"][idx]),
        }


def train_ce(model: PeftModel, tokenizer, data: list[dict], cfg: Config) -> PeftModel:
    """Cross-entropy fine-tuning."""
    encodings = prepare_ce_dataset(data, tokenizer)
    dataset = CEDataset(encodings)

    training_args = TrainingArguments(
        output_dir=str(cfg.checkpoint_dir / "ce"),
        num_train_epochs=cfg.ce_epochs,
        per_device_train_batch_size=cfg.batch_size,
        learning_rate=cfg.lr,
        weight_decay=cfg.weight_decay,
        warmup_steps=cfg.warmup_steps,
        fp16=True,
        logging_steps=10,
        save_strategy="epoch",
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
    )

    trainer.train()
    return model


def train_rl_with_diversity(
    model: PeftModel,
    tokenizer,
    data: list[dict],
    cfg: Config,
    controller: FeedbackDiversityController,
) -> tuple[PeftModel, float]:
    """RL fine-tuning with diversity-controlled batches.

    Returns model and average measured entropy.
    """
    trainer = RLCodeTrainer(model, tokenizer, cfg, controller)
    target_entropy = cfg.diversity_high_threshold if controller.mode == "high" else cfg.diversity_low_threshold

    entropy_measurements = []

    for epoch in range(cfg.rl_epochs):
        print(f"\n=== RL Epoch {epoch + 1}/{cfg.rl_epochs} (mode={controller.mode}) ===")

        # Generate samples with error types
        print("Generating samples for diversity filtering...")
        samples = trainer.generate_samples_with_errors(data, max_samples=min(50, len(data)))

        if not samples:
            print("No samples generated, skipping epoch")
            continue

        # Filter batch according to diversity mode
        filtered = controller.filter_batch(samples, batch_size=len(samples))
        H = controller.compute_entropy(filtered)
        entropy_measurements.append(H)
        controller.log_entropy(filtered, target_entropy)

        # RL update on filtered batch
        avg_reward = trainer.rl_step_batch(filtered)
        print(f"RL Epoch {epoch + 1} avg reward: {avg_reward:.3f}, H={H:.3f} bits")

    avg_H = sum(entropy_measurements) / max(1, len(entropy_measurements))
    return model, avg_H
