"""Training loops for H-E1 experiment."""
import torch
from torch.utils.data import DataLoader
from transformers import Trainer, TrainingArguments, DataCollatorForSeq2Seq
from peft import PeftModel
from tqdm import tqdm

from config import Config
from model import RLCodeTrainer


def prepare_ce_dataset(data: list[dict], tokenizer, max_length: int = 512):
    """Prepare dataset for CE training."""
    encodings = {"input_ids": [], "attention_mask": [], "labels": []}

    for item in data:
        prompt = item["prompt"]
        # For CE, use canonical solution as target
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


def train_rl(model: PeftModel, tokenizer, data: list[dict], cfg: Config) -> PeftModel:
    """RL fine-tuning with execution feedback."""
    trainer = RLCodeTrainer(model, tokenizer, cfg)

    for epoch in range(cfg.rl_epochs):
        print(f"\n=== RL Epoch {epoch + 1}/{cfg.rl_epochs} ===")
        total_reward = 0.0

        for item in tqdm(data, desc=f"RL Epoch {epoch + 1}"):
            prompt = item["prompt"]
            # Use base_input as simple test cases
            tests = item.get("base_input", [])
            if not tests:
                continue

            # Format tests as assertions
            entry_point = item.get("entry_point", "solution")
            test_strs = [f"assert {entry_point}(*{t[0]}) == {t[1]}" for t in tests if len(t) >= 2]

            if test_strs:
                reward = trainer.rl_step(prompt, test_strs)
                total_reward += reward

        avg_reward = total_reward / max(1, len(data))
        print(f"RL Epoch {epoch + 1} avg reward: {avg_reward:.3f}")

    return model


def run_all_conditions(data: list[dict], cfg: Config) -> dict[str, PeftModel]:
    """Train and return models for all 4 conditions."""
    from model import load_base_model, wrap_lora
    import copy

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # CE model: CE training only
    print("\n" + "="*50)
    print("Training CE model (Cross-Entropy only)")
    print("="*50)
    base_model, tokenizer = load_base_model(cfg)
    ce_model = wrap_lora(base_model, cfg)
    ce_model = ce_model.to(device)
    ce_model = train_ce(ce_model, tokenizer, data, cfg)
    ce_model.save_pretrained(cfg.checkpoint_dir / "ce_final")

    # RL model: CE warmup + RL training
    print("\n" + "="*50)
    print("Training RL model (CE warmup + RL)")
    print("="*50)
    base_model2, _ = load_base_model(cfg)
    rl_model = wrap_lora(base_model2, cfg)
    rl_model = rl_model.to(device)
    # CE warmup
    rl_model = train_ce(rl_model, tokenizer, data, cfg)
    # RL phase
    rl_model = train_rl(rl_model, tokenizer, data, cfg)
    rl_model.save_pretrained(cfg.checkpoint_dir / "rl_final")

    return {"CE": ce_model, "RL": rl_model, "tokenizer": tokenizer}
