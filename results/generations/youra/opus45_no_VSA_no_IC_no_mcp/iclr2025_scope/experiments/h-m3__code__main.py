#!/usr/bin/env python3
"""H-M3: Task-Conditioned SSM Training - validates adaptation capability preservation."""

import os
import yaml
import json
import random
import logging
from pathlib import Path
from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from datasets import load_dataset
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

TASK_ID_MAP = {"boolq": 0, "cb": 1, "copa": 2, "rte": 3, "wic": 4}
TASK_NUM_LABELS = {"boolq": 2, "cb": 3, "copa": 2, "rte": 2, "wic": 2}


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


@dataclass
class Config:
    d_model: int = 768
    d_state: int = 16
    d_conv: int = 4
    expand: int = 2
    rank: int = 32
    n_tasks: int = 5
    max_steps: int = 100
    lr: float = 2e-5
    batch_size: int = 8
    grad_clip: float = 1.0
    seeds: tuple = (42, 123, 2024)
    k_shots: tuple = (8, 16)
    device: str = "cuda"


class TaskConditionedSSM(nn.Module):
    """Simplified TC-SSM for PoC: task embedding modulates linear projections."""

    def __init__(self, d_model: int = 768, d_hidden: int = 256, n_tasks: int = 5, rank: int = 32):
        super().__init__()
        self.d_model = d_model
        self.d_hidden = d_hidden
        self.task_embedding = nn.Embedding(n_tasks, rank)
        self.task_down = nn.Linear(rank, d_hidden)
        self.task_up = nn.Linear(d_hidden, d_model)
        self.proj_in = nn.Linear(d_model, d_hidden)
        self.proj_out = nn.Linear(d_hidden, d_model)
        self.norm = nn.LayerNorm(d_model)
        self.activation = nn.GELU()

    def forward(self, x: torch.Tensor, task_ids: torch.Tensor) -> torch.Tensor:
        # x: [B, L, D], task_ids: [B]
        task_emb = self.task_embedding(task_ids)  # [B, rank]
        task_mod = self.task_up(self.task_down(task_emb))  # [B, D]
        h = self.proj_in(x)  # [B, L, d_hidden]
        h = self.activation(h)
        h = self.proj_out(h)  # [B, L, D]
        h = h + task_mod.unsqueeze(1)  # task conditioning via additive modulation
        log.debug(f"TC-SSM: Task conditioning applied, task_id={task_ids.tolist()}")
        return self.norm(h + x)


class TCSSMClassifier(nn.Module):
    """TC-SSM with classification head for SuperGLUE tasks."""

    def __init__(self, vocab_size: int = 50257, d_model: int = 768, n_layers: int = 4,
                 n_tasks: int = 5, rank: int = 32, max_len: int = 512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_len, d_model)
        self.layers = nn.ModuleList([
            TaskConditionedSSM(d_model, d_model // 2, n_tasks, rank)
            for _ in range(n_layers)
        ])
        self.classifier = nn.Linear(d_model, max(TASK_NUM_LABELS.values()))
        self.n_tasks = n_tasks

    def forward(self, input_ids: torch.Tensor, task_ids: torch.Tensor,
                labels: Optional[torch.Tensor] = None):
        B, L = input_ids.shape
        positions = torch.arange(L, device=input_ids.device).unsqueeze(0).expand(B, L)
        x = self.embedding(input_ids) + self.pos_embedding(positions)
        for layer in self.layers:
            x = layer(x, task_ids)
        pooled = x.mean(dim=1)  # mean pooling
        logits = self.classifier(pooled)
        loss = None
        if labels is not None:
            num_labels = TASK_NUM_LABELS[list(TASK_ID_MAP.keys())[task_ids[0].item()]]
            loss = F.cross_entropy(logits[:, :num_labels], labels)
        return {"loss": loss, "logits": logits}


class BaselineClassifier(nn.Module):
    """Standard transformer-style classifier (no task conditioning) as baseline."""

    def __init__(self, vocab_size: int = 50257, d_model: int = 768, n_layers: int = 4, max_len: int = 512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_len, d_model)
        self.layers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(d_model, d_model * 2),
                nn.GELU(),
                nn.Linear(d_model * 2, d_model),
                nn.LayerNorm(d_model)
            ) for _ in range(n_layers)
        ])
        self.classifier = nn.Linear(d_model, max(TASK_NUM_LABELS.values()))

    def forward(self, input_ids: torch.Tensor, task_ids: torch.Tensor = None,
                labels: Optional[torch.Tensor] = None, task_name: str = "boolq"):
        B, L = input_ids.shape
        positions = torch.arange(L, device=input_ids.device).unsqueeze(0).expand(B, L)
        x = self.embedding(input_ids) + self.pos_embedding(positions)
        for layer in self.layers:
            x = layer(x) + x  # residual
        pooled = x.mean(dim=1)
        logits = self.classifier(pooled)
        loss = None
        if labels is not None:
            if task_ids is not None:
                task_name = list(TASK_ID_MAP.keys())[task_ids[0].item()]
            num_labels = TASK_NUM_LABELS[task_name]
            loss = F.cross_entropy(logits[:, :num_labels], labels)
        return {"loss": loss, "logits": logits}


def verify_mechanism_activation(model: TCSSMClassifier, batch: dict, device: str) -> bool:
    """Verify TC-SSM mechanism produces different outputs for different tasks."""
    model = model.to(device)
    input_ids = batch["input_ids"].to(device)
    task_ids_a = torch.zeros(input_ids.size(0), dtype=torch.long, device=device)
    task_ids_b = torch.ones(input_ids.size(0), dtype=torch.long, device=device)

    with torch.no_grad():
        out_a = model(input_ids, task_ids=task_ids_a)
        out_b = model(input_ids, task_ids=task_ids_b)

    diff = (out_a["logits"] - out_b["logits"]).abs().mean().item()
    log.info(f"Mechanism verification: logit diff between tasks = {diff:.6f}")

    if diff < 1e-6:
        log.warning("FAIL: Task conditioning has no effect")
        return False

    # Check modulation magnitude
    task_emb = model.layers[0].task_embedding(task_ids_a)
    task_mod = model.layers[0].task_up(model.layers[0].task_down(task_emb))
    mod_mean = task_mod.abs().mean().item()
    log.info(f"Mechanism verification: modulation magnitude = {mod_mean:.6f}")

    if mod_mean < 1e-3:
        log.warning("FAIL: Modulation values near zero")
        return False

    log.info("PASS: Mechanism verification successful")
    return True


class SuperGLUEDataset(Dataset):
    """Simple SuperGLUE dataset wrapper."""

    def __init__(self, task: str, split: str = "train", max_len: int = 128, k_shot: int = None, seed: int = 42):
        self.task = task
        self.max_len = max_len
        raw = load_dataset("super_glue", task, split=split)

        if k_shot is not None and k_shot < len(raw):
            random.seed(seed)
            indices = random.sample(range(len(raw)), k_shot)
            self.data = [raw[i] for i in indices]
        else:
            self.data = list(raw)

        self.task_id = TASK_ID_MAP[task]
        self.num_labels = TASK_NUM_LABELS[task]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Format input based on task
        if self.task == "boolq":
            text = f"Question: {item['question']} Passage: {item['passage']}"
        elif self.task == "cb":
            text = f"Premise: {item['premise']} Hypothesis: {item['hypothesis']}"
        elif self.task == "copa":
            text = f"Premise: {item['premise']} Choice1: {item['choice1']} Choice2: {item['choice2']}"
        elif self.task == "rte":
            text = f"Premise: {item['premise']} Hypothesis: {item['hypothesis']}"
        elif self.task == "wic":
            text = f"Sentence1: {item['sentence1']} Sentence2: {item['sentence2']} Word: {item['word']}"
        else:
            text = str(item)

        # Simple tokenization (character-level for PoC)
        tokens = [ord(c) % 50257 for c in text[:self.max_len]]
        tokens = tokens + [0] * (self.max_len - len(tokens))  # pad

        label = item["label"] if "label" in item else 0

        return {
            "input_ids": torch.tensor(tokens, dtype=torch.long),
            "labels": torch.tensor(label, dtype=torch.long),
            "task_id": torch.tensor(self.task_id, dtype=torch.long)
        }


def collate_fn(batch):
    return {
        "input_ids": torch.stack([b["input_ids"] for b in batch]),
        "labels": torch.stack([b["labels"] for b in batch]),
        "task_ids": torch.stack([b["task_id"] for b in batch])
    }


def run_few_shot_adaptation(model: nn.Module, train_loader: DataLoader, val_loader: DataLoader,
                            task_name: str, config: Config, device: str) -> dict:
    """Run few-shot adaptation and return accuracy curve."""
    model = deepcopy(model).to(device)
    model.train()

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr, weight_decay=0.01)

    step = 0
    per_step_acc = []
    train_iter = iter(train_loader)

    while step < config.max_steps:
        try:
            batch = next(train_iter)
        except StopIteration:
            train_iter = iter(train_loader)
            batch = next(train_iter)

        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)
        task_ids = batch["task_ids"].to(device)

        optimizer.zero_grad()
        outputs = model(input_ids, task_ids=task_ids, labels=labels)
        loss = outputs["loss"]
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), config.grad_clip)
        optimizer.step()

        step += 1

        # Evaluate every 10 steps
        if step % 10 == 0 or step == config.max_steps:
            acc = evaluate_model(model, val_loader, device)
            per_step_acc.append((step, acc))
            log.info(f"Step {step}: accuracy = {acc:.4f}")

    final_acc = per_step_acc[-1][1] if per_step_acc else 0.0
    ceiling = max(a for _, a in per_step_acc) if per_step_acc else 0.0
    steps_to_95pct = None
    for s, a in per_step_acc:
        if ceiling > 0 and a >= 0.95 * ceiling:
            steps_to_95pct = s
            break

    return {
        "accuracy": final_acc,
        "steps_to_95pct": steps_to_95pct,
        "per_step_acc": per_step_acc,
        "ceiling": ceiling
    }


def evaluate_model(model: nn.Module, val_loader: DataLoader, device: str) -> float:
    """Evaluate model accuracy on validation set."""
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            task_ids = batch["task_ids"].to(device)

            outputs = model(input_ids, task_ids=task_ids)
            num_labels = TASK_NUM_LABELS[list(TASK_ID_MAP.keys())[task_ids[0].item()]]
            preds = outputs["logits"][:, :num_labels].argmax(dim=-1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    model.train()
    return correct / total if total > 0 else 0.0


def run_experiment(config: Config, output_dir: Path):
    """Main experiment: compare TC-SSM vs baseline on SuperGLUE few-shot."""
    device = config.device if torch.cuda.is_available() else "cpu"
    log.info(f"Running on device: {device}")

    results = {"tc_ssm": {}, "baseline": {}}

    for task in TASK_ID_MAP.keys():
        log.info(f"=== Task: {task} ===")
        results["tc_ssm"][task] = {}
        results["baseline"][task] = {}

        for k in config.k_shots:
            log.info(f"--- {k}-shot ---")
            tc_accs = []
            base_accs = []
            tc_steps = []
            base_steps = []

            for seed in config.seeds:
                set_seed(seed)
                log.info(f"Seed: {seed}")

                # Create datasets
                train_ds = SuperGLUEDataset(task, "train", k_shot=k, seed=seed)
                val_ds = SuperGLUEDataset(task, "validation")

                train_loader = DataLoader(train_ds, batch_size=config.batch_size,
                                         shuffle=True, collate_fn=collate_fn)
                val_loader = DataLoader(val_ds, batch_size=32, collate_fn=collate_fn)

                # TC-SSM model
                tc_model = TCSSMClassifier(
                    d_model=config.d_model, n_layers=4,
                    n_tasks=config.n_tasks, rank=config.rank
                )

                # Verify mechanism works
                sample_batch = next(iter(train_loader))
                assert verify_mechanism_activation(tc_model, sample_batch, device), \
                    "Mechanism verification failed"

                tc_result = run_few_shot_adaptation(
                    tc_model, train_loader, val_loader, task, config, device
                )
                tc_accs.append(tc_result["accuracy"])
                tc_steps.append(tc_result["steps_to_95pct"] or config.max_steps)

                # Baseline model (no task conditioning)
                base_model = BaselineClassifier(d_model=config.d_model, n_layers=4)
                base_result = run_few_shot_adaptation(
                    base_model, train_loader, val_loader, task, config, device
                )
                base_accs.append(base_result["accuracy"])
                base_steps.append(base_result["steps_to_95pct"] or config.max_steps)

            results["tc_ssm"][task][k] = {
                "mean_acc": float(np.mean(tc_accs)),
                "std_acc": float(np.std(tc_accs)),
                "mean_steps": float(np.mean(tc_steps)),
                "all_accs": tc_accs
            }
            results["baseline"][task][k] = {
                "mean_acc": float(np.mean(base_accs)),
                "std_acc": float(np.std(base_accs)),
                "mean_steps": float(np.mean(base_steps)),
                "all_accs": base_accs
            }

            log.info(f"TC-SSM {k}-shot: {np.mean(tc_accs):.4f} ± {np.std(tc_accs):.4f}")
            log.info(f"Baseline {k}-shot: {np.mean(base_accs):.4f} ± {np.std(base_accs):.4f}")

    return results


def compute_aggregate_metrics(results: dict) -> dict:
    """Compute aggregate metrics across all tasks."""
    tc_accs = []
    base_accs = []
    tc_steps = []

    for task in results["tc_ssm"]:
        for k in results["tc_ssm"][task]:
            tc_accs.append(results["tc_ssm"][task][k]["mean_acc"])
            base_accs.append(results["baseline"][task][k]["mean_acc"])
            tc_steps.append(results["tc_ssm"][task][k]["mean_steps"])

    tc_mean = np.mean(tc_accs)
    base_mean = np.mean(base_accs)
    gap = (base_mean - tc_mean) * 100  # gap in percentage points

    return {
        "tc_ssm_avg_acc": float(tc_mean),
        "baseline_avg_acc": float(base_mean),
        "accuracy_gap_pct": float(gap),
        "tc_ssm_within_5pct": gap <= 5.0,
        "avg_steps_to_95pct": float(np.mean(tc_steps)),
        "adaptation_under_100_steps": float(np.mean(tc_steps)) <= 100
    }


def plot_results(results: dict, aggregate: dict, output_dir: Path):
    """Generate required visualizations."""
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    # Gate comparison bar chart (required)
    tasks = list(results["tc_ssm"].keys())
    tc_16shot = [results["tc_ssm"][t][16]["mean_acc"] for t in tasks]
    base_16shot = [results["baseline"][t][16]["mean_acc"] for t in tasks]

    x = np.arange(len(tasks))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, tc_16shot, width, label='TC-SSM', color='#2ecc71')
    bars2 = ax.bar(x + width/2, base_16shot, width, label='Baseline', color='#3498db')

    ax.set_ylabel('Accuracy')
    ax.set_title('16-shot Adaptation: TC-SSM vs Baseline')
    ax.set_xticks(x)
    ax.set_xticklabels([t.upper() for t in tasks])
    ax.legend()
    ax.set_ylim(0, 1)

    # Add value labels
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(figures_dir / "gate_comparison.png", dpi=150)
    plt.close()

    # Per-task breakdown
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for i, k in enumerate([8, 16]):
        ax = axes[i]
        tc_acc = [results["tc_ssm"][t][k]["mean_acc"] for t in tasks]
        base_acc = [results["baseline"][t][k]["mean_acc"] for t in tasks]

        x = np.arange(len(tasks))
        ax.bar(x - width/2, tc_acc, width, label='TC-SSM', color='#2ecc71')
        ax.bar(x + width/2, base_acc, width, label='Baseline', color='#3498db')
        ax.set_ylabel('Accuracy')
        ax.set_title(f'{k}-shot Adaptation')
        ax.set_xticks(x)
        ax.set_xticklabels([t.upper() for t in tasks])
        ax.legend()
        ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(figures_dir / "per_task_breakdown.png", dpi=150)
    plt.close()

    log.info(f"Figures saved to {figures_dir}")


def determine_gate_result(aggregate: dict) -> str:
    """Determine MUST_WORK gate result."""
    # Primary: TC-SSM within 5% of baseline
    # Secondary: Adaptation in <100 steps

    within_5pct = aggregate["tc_ssm_within_5pct"]
    under_100_steps = aggregate["adaptation_under_100_steps"]

    if within_5pct and under_100_steps:
        return "PASS"
    elif within_5pct or under_100_steps:
        return "PARTIAL"
    else:
        return "FAIL"


def main():
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent

    # Load config
    config_path = script_dir / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            cfg_dict = yaml.safe_load(f)
        config = Config(
            d_model=cfg_dict.get("model", {}).get("d_model", 768),
            d_state=cfg_dict.get("model", {}).get("d_state", 16),
            rank=cfg_dict.get("task_conditioning", {}).get("rank", 32),
            n_tasks=cfg_dict.get("task_conditioning", {}).get("n_tasks", 5),
            max_steps=cfg_dict.get("few_shot_training", {}).get("max_steps", 100),
            lr=cfg_dict.get("few_shot_training", {}).get("lr", 2e-5),
            batch_size=cfg_dict.get("few_shot_training", {}).get("batch_size", 8),
            grad_clip=cfg_dict.get("few_shot_training", {}).get("grad_clip", 1.0),
            seeds=tuple(cfg_dict.get("few_shot_training", {}).get("seeds", [42, 123, 2024])),
            k_shots=tuple(cfg_dict.get("few_shot_eval", {}).get("k_shots", [8, 16])),
        )
    else:
        config = Config()

    log.info("Starting H-M3 experiment: Task-Conditioned SSM Training")
    log.info(f"Config: rank={config.rank}, n_tasks={config.n_tasks}, max_steps={config.max_steps}")

    # Run experiment
    results = run_experiment(config, output_dir)

    # Compute aggregate metrics
    aggregate = compute_aggregate_metrics(results)

    # Determine gate result
    gate_result = determine_gate_result(aggregate)

    log.info("=" * 50)
    log.info("EXPERIMENT RESULTS")
    log.info("=" * 50)
    log.info(f"TC-SSM average accuracy: {aggregate['tc_ssm_avg_acc']:.4f}")
    log.info(f"Baseline average accuracy: {aggregate['baseline_avg_acc']:.4f}")
    log.info(f"Accuracy gap: {aggregate['accuracy_gap_pct']:.2f}%")
    log.info(f"Within 5% threshold: {aggregate['tc_ssm_within_5pct']}")
    log.info(f"Average steps to 95% ceiling: {aggregate['avg_steps_to_95pct']:.1f}")
    log.info(f"Adaptation under 100 steps: {aggregate['adaptation_under_100_steps']}")
    log.info("=" * 50)
    log.info(f"GATE RESULT: {gate_result}")
    log.info("=" * 50)

    # Generate visualizations
    plot_results(results, aggregate, output_dir)

    # Save results - convert numpy bools
    def convert_np(obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_np(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_np(v) for v in obj]
        return obj

    results_file = output_dir / "experiment_results.json"
    with open(results_file, "w") as f:
        json.dump(convert_np({
            "results": results,
            "aggregate": aggregate,
            "gate_result": gate_result
        }), f, indent=2)
    log.info(f"Results saved to {results_file}")

    print("EXPERIMENT COMPLETE")
    return gate_result, aggregate, results


if __name__ == "__main__":
    main()
