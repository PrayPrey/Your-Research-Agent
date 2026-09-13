"""Training pipeline for GPT-2 with information density tracking"""
from transformers import GPT2LMHeadModel, GPT2Tokenizer, AdamW, get_cosine_schedule_with_warmup
from metrics.density_analyzer import InformationDensityAnalyzer
from torch.utils.data import Dataset, DataLoader
import torch
import json
import csv
from pathlib import Path
from typing import Dict
from config import CONFIG


class C4Dataset(Dataset):
    """Load curated C4 subset from JSONL"""

    def __init__(self, jsonl_path: str, tokenizer, max_length: int = 1024):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.texts = []

        with open(jsonl_path, 'r') as f:
            for line in f:
                item = json.loads(line)
                self.texts.append(item["text"])

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        tokens = self.tokenizer.encode(
            text,
            max_length=self.max_length,
            truncation=True,
            return_tensors="pt"
        )[0]

        return {
            "input_ids": tokens,
            "labels": tokens.clone()
        }


def collate_fn(batch):
    """Pad batch"""
    input_ids = [item["input_ids"] for item in batch]
    labels = [item["labels"] for item in batch]

    # Pad to max length in batch
    max_len = max(len(ids) for ids in input_ids)
    input_ids_padded = torch.stack([
        torch.cat([ids, torch.zeros(max_len - len(ids), dtype=torch.long)])
        for ids in input_ids
    ])
    labels_padded = torch.stack([
        torch.cat([lbls, torch.full((max_len - len(lbls),), -100, dtype=torch.long)])
        for lbls in labels
    ])

    return {
        "input_ids": input_ids_padded,
        "labels": labels_padded
    }


class GPT2TrainerWithMetrics:
    """Train GPT-2 + density analyzer."""

    def __init__(
        self,
        model_name: str = "gpt2",
        analyzer: InformationDensityAnalyzer = None
    ):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        if torch.cuda.is_available():
            self.model = self.model.cuda()

        self.analyzer = analyzer if analyzer else InformationDensityAnalyzer(
            self.model,
            vocab_size=CONFIG.density_metrics.vocab_size
        )

    def train_condition(
        self,
        dataset_path: str,
        output_dir: str,
        total_steps: int = 50000
    ) -> Dict[str, float]:
        """Train single condition. Returns: final metrics"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Load dataset
        dataset = C4Dataset(dataset_path, self.tokenizer)
        dataloader = DataLoader(
            dataset,
            batch_size=CONFIG.training.micro_batch_size,
            shuffle=True,
            collate_fn=collate_fn
        )

        # Optimizer
        optimizer = AdamW(
            self.model.parameters(),
            lr=CONFIG.training.learning_rate,
            betas=(CONFIG.training.adam_beta1, CONFIG.training.adam_beta2),
            eps=CONFIG.training.adam_eps,
            weight_decay=CONFIG.training.weight_decay
        )

        # LR scheduler
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=CONFIG.training.warmup_steps,
            num_training_steps=total_steps
        )

        # Metrics log
        metrics_csv = Path(output_dir) / "metrics.csv"
        with open(metrics_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["step", "loss", "entropy", "fisher_trace", "lr"])

        # Training loop
        step = 0
        self.model.train()
        while step < total_steps:
            for batch in dataloader:
                if step >= total_steps:
                    break

                input_ids = batch["input_ids"]
                labels = batch["labels"]
                if torch.cuda.is_available():
                    input_ids = input_ids.cuda()
                    labels = labels.cuda()

                # Forward + metrics
                optimizer.zero_grad()
                loss, entropy, fisher_trace = self.analyzer(input_ids, labels)

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    CONFIG.training.grad_clip
                )

                # Optimizer step
                optimizer.step()
                scheduler.step()

                # Log
                if step % CONFIG.training.log_interval == 0:
                    lr = scheduler.get_last_lr()[0]
                    with open(metrics_csv, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([step, loss.item(), entropy, fisher_trace, lr])

                    print(f"Step {step}/{total_steps} | Loss: {loss.item():.4f} | Entropy: {entropy:.4f} | Fisher: {fisher_trace:.2e}")

                # Checkpoint
                if step % CONFIG.training.checkpoint_interval == 0 and step > 0:
                    ckpt_path = Path(output_dir) / f"checkpoint_{step}.pt"
                    torch.save(self.model.state_dict(), ckpt_path)

                step += 1

        # Final metrics
        final_metrics = {
            "final_loss": loss.item(),
            "final_entropy": entropy,
            "final_fisher_trace": fisher_trace
        }

        return final_metrics


def train_all_conditions(
    condition_paths: List[str],
    base_config: Dict
) -> str:
    """Train 9 conditions sequentially. Returns: metrics CSV path"""
    import pandas as pd

    all_metrics = []

    for cond_path in condition_paths:
        cond_name = Path(cond_path).stem.replace("condition_", "")
        print(f"\n{'='*60}")
        print(f"Training condition: {cond_name}")
        print('='*60)

        output_dir = f"results/checkpoints/{cond_name}"
        trainer = GPT2TrainerWithMetrics()

        final = trainer.train_condition(
            dataset_path=cond_path,
            output_dir=output_dir,
            total_steps=CONFIG.training.total_steps
        )

        all_metrics.append({
            "condition": cond_name,
            **final
        })

    # Save aggregate
    df = pd.DataFrame(all_metrics)
    out_path = "results/all_conditions_metrics.csv"
    df.to_csv(out_path, index=False)

    return out_path
