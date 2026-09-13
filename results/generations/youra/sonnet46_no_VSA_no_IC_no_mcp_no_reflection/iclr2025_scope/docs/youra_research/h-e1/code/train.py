import argparse
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, set_seed
from transformers.optimization import get_linear_schedule_with_warmup
from torch.optim import AdamW
from datasets import load_dataset

from config import ExperimentConfig
from model import MambaForSequenceClassification, build_lora_model, build_zero_shot_model
from glue_evaluate import compute_glue_metric, get_scalar

TASK_LABEL_COUNTS = {"sst2": 2, "mnli": 3, "qnli": 2, "qqp": 2}
TASK_TEXT_FIELDS = {
    "sst2": ("sentence",),
    "mnli": ("premise", "hypothesis"),
    "qnli": ("question", "sentence"),
    "qqp": ("question1", "question2"),
}


def get_dataloaders(task: str, tokenizer, cfg: ExperimentConfig):
    ds = load_dataset("glue", task)
    fields = TASK_TEXT_FIELDS[task]

    def tokenize(batch):
        if len(fields) == 1:
            return tokenizer(batch[fields[0]], max_length=cfg.max_length,
                             truncation=True, padding="max_length")
        else:
            return tokenizer(batch[fields[0]], batch[fields[1]], max_length=cfg.max_length,
                             truncation=True, padding="max_length")

    col_remove = [c for c in ds["train"].column_names if c != "label"]
    ds = ds.map(tokenize, batched=True, remove_columns=col_remove)
    ds.set_format("torch", columns=["input_ids", "label"])
    val_split = "validation_matched" if task == "mnli" else "validation"
    train_loader = DataLoader(ds["train"], batch_size=cfg.batch_size, shuffle=True)
    val_loader = DataLoader(ds[val_split], batch_size=cfg.batch_size)
    return train_loader, val_loader


def eval_model(model: MambaForSequenceClassification, val_loader: DataLoader, task: str, device: str) -> dict:
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(device)
            logits = model(input_ids)["logits"]
            preds = logits.argmax(dim=-1).cpu().tolist()
            all_preds.extend(preds)
            all_labels.extend(batch["label"].tolist())
    return compute_glue_metric(task, all_preds, all_labels)


def train_one_task(task: str, cfg: ExperimentConfig):
    set_seed(cfg.seed)
    device = cfg.device
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    model = build_lora_model(cfg, TASK_LABEL_COUNTS[task]).to(device)
    train_loader, val_loader = get_dataloaders(task, tokenizer, cfg)
    optimizer = AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    total_steps = len(train_loader) * cfg.epochs
    warmup_steps = int(total_steps * cfg.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)
    loss_history = []
    val_metrics = {}
    for epoch in range(cfg.epochs):
        model.train()
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["label"].to(device)
            out = model(input_ids, labels=labels)
            out["loss"].backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            loss_history.append(out["loss"].item())
        val_metrics = eval_model(model, val_loader, task, device)
        score = get_scalar(task, val_metrics)
        print(f"  epoch {epoch+1}/{cfg.epochs} val {task}={score:.4f}")
    return model, val_metrics, loss_history


def eval_zero_shot(task: str, cfg: ExperimentConfig) -> dict:
    device = cfg.device
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    model = build_zero_shot_model(cfg, TASK_LABEL_COUNTS[task]).to(device)
    _, val_loader = get_dataloaders(task, tokenizer, cfg)
    return eval_model(model, val_loader, task, device)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, choices=list(TASK_LABEL_COUNTS))
    args = parser.parse_args()
    cfg = ExperimentConfig()
    model, metrics, _ = train_one_task(args.task, cfg)
    print(metrics)
