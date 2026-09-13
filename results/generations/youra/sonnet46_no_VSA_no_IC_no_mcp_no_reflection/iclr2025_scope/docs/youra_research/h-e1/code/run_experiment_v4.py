"""
h-e1 Phase 4 RE-RUN: Mamba-130m + Projection-only LoRA on GLUE
- Training: 10% subsample of train (faster, still statistically meaningful)
- Evaluation: FULL validation split (standard GLUE practice)
- Gate: SST-2 accuracy > 70%
"""
import os
import sys
import json
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Subset
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
from transformers.optimization import get_linear_schedule_with_warmup
from torch.optim import AdamW
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
import evaluate as hf_evaluate

# ── Config ──────────────────────────────────────────────────────────────────
MODEL_NAME = "state-spaces/mamba-130m-hf"
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
TARGET_MODULES = ["in_proj", "out_proj", "x_proj"]
MAX_LENGTH = 128
BATCH_SIZE = 32
EPOCHS = 3
LR = 3e-4
WEIGHT_DECAY = 0.01
WARMUP_RATIO = 0.06
SEED = 42
TRAIN_SUBSAMPLE = 0.10  # 10% of train set — fast but meaningful
GATE_TASK = "sst2"
GATE_THRESHOLD = 0.70
TASKS = ["sst2", "mnli", "qnli", "qqp"]

TASK_LABEL_COUNTS = {"sst2": 2, "mnli": 3, "qnli": 2, "qqp": 2}
TASK_TEXT_FIELDS = {
    "sst2": ("sentence",),
    "mnli": ("premise", "hypothesis"),
    "qnli": ("question", "sentence"),
    "qqp": ("question1", "question2"),
}
TASK_VAL_SPLIT = {"sst2": "validation", "mnli": "validation_matched", "qnli": "validation", "qqp": "validation"}
TASK_METRIC = {"sst2": "accuracy", "mnli": "accuracy", "qnli": "accuracy", "qqp": "f1"}

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

# ── Model ────────────────────────────────────────────────────────────────────

class MambaClassifier(nn.Module):
    def __init__(self, backbone, num_labels: int, d_model: int = 768):
        super().__init__()
        self.backbone = backbone
        self.classifier = nn.Linear(d_model, num_labels)
        nn.init.normal_(self.classifier.weight, std=0.02)
        nn.init.zeros_(self.classifier.bias)

    def forward(self, input_ids, labels=None):
        out = self.backbone(input_ids, output_hidden_states=True)
        pooled = out.hidden_states[-1][:, -1, :]
        logits = self.classifier(pooled)
        result = {"logits": logits}
        if labels is not None:
            result["loss"] = F.cross_entropy(logits, labels)
        return result


def build_lora_model(num_labels):
    assert "conv1d" not in TARGET_MODULES
    base = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    cfg = LoraConfig(
        r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES, bias="none", task_type="FEATURE_EXTRACTION",
    )
    peft_model = get_peft_model(base, cfg)
    peft_model.print_trainable_parameters()
    return MambaClassifier(peft_model, num_labels)


def build_zero_shot_model(num_labels):
    base = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    for p in base.parameters():
        p.requires_grad = False
    return MambaClassifier(base, num_labels)

# ── Data ─────────────────────────────────────────────────────────────────────

def get_loaders(task, tokenizer, subsample_train=True):
    ds = load_dataset("glue", task)
    fields = TASK_TEXT_FIELDS[task]

    def tok(batch):
        if len(fields) == 1:
            return tokenizer(batch[fields[0]], max_length=MAX_LENGTH, truncation=True, padding="max_length")
        return tokenizer(batch[fields[0]], batch[fields[1]], max_length=MAX_LENGTH, truncation=True, padding="max_length")

    col_rm = [c for c in ds["train"].column_names if c != "label"]
    ds = ds.map(tok, batched=True, remove_columns=col_rm)
    ds.set_format("torch", columns=["input_ids", "label"])

    train_ds = ds["train"]
    if subsample_train:
        n = max(500, int(len(train_ds) * TRAIN_SUBSAMPLE))
        idxs = random.sample(range(len(train_ds)), n)
        train_ds = Subset(train_ds, idxs)

    val_ds = ds[TASK_VAL_SPLIT[task]]
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    print(f"  {task}: train={len(train_ds)}, val={len(val_ds)}")
    return train_loader, val_loader


def eval_model(model, val_loader, task):
    metric = hf_evaluate.load("glue", task)
    model.eval()
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(DEVICE)
            logits = model(input_ids)["logits"]
            preds = logits.argmax(dim=-1).cpu().tolist()
            metric.add_batch(predictions=preds, references=batch["label"].tolist())
    return metric.compute()


def get_scalar(task, metrics):
    key = TASK_METRIC[task]
    return metrics.get(key, 0.0)

# ── Training ──────────────────────────────────────────────────────────────────

def train_task(task, tokenizer):
    print(f"\n{'='*60}\n[LoRA] {task}...\n{'='*60}")
    set_seed(SEED)
    model = build_lora_model(TASK_LABEL_COUNTS[task]).to(DEVICE)
    train_loader, val_loader = get_loaders(task, tokenizer, subsample_train=True)
    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    total_steps = len(train_loader) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)
    loss_hist = []
    final_metrics = {}
    for epoch in range(EPOCHS):
        model.train()
        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(DEVICE)
            labels = batch["label"].to(DEVICE)
            out = model(input_ids, labels=labels)
            out["loss"].backward()
            optimizer.step(); scheduler.step(); optimizer.zero_grad()
            loss_hist.append(out["loss"].item())
            if step % 50 == 0:
                print(f"  epoch {epoch+1} step {step}/{len(train_loader)} loss={out['loss'].item():.4f}")
        final_metrics = eval_model(model, val_loader, task)
        score = get_scalar(task, final_metrics)
        print(f"  epoch {epoch+1} val {task}={score:.4f}")
    return model, final_metrics, loss_hist


def eval_zero_shot(task, tokenizer):
    print(f"\n[Zero-shot] {task}...")
    model = build_zero_shot_model(TASK_LABEL_COUNTS[task]).to(DEVICE)
    _, val_loader = get_loaders(task, tokenizer, subsample_train=False)
    metrics = eval_model(model, val_loader, task)
    score = get_scalar(task, metrics)
    print(f"  {task} zero-shot: {score:.4f}")
    return score

# ── Verify LoRA ───────────────────────────────────────────────────────────────

def verify_lora(model, lora_scores, zs_scores):
    sd = model.backbone.state_dict()
    lora_keys = [k for k in sd if "lora_A" in k or "lora_B" in k]
    keys_present = len(lora_keys) > 0
    weights_nonzero = any(sd[k].abs().sum().item() > 0 for k in lora_keys) if lora_keys else False
    delta_positive = lora_scores.get("sst2", 0) > zs_scores.get("sst2", 0)
    indicators = {"lora_keys_present": keys_present, "lora_weights_nonzero": weights_nonzero, "sst2_delta_positive": delta_positive}
    return keys_present and weights_nonzero, indicators

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    set_seed(SEED)
    random.seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Phase 1: Zero-shot
    print("\n" + "="*60)
    print("PHASE 1: Zero-shot evaluation")
    print("="*60)
    zs_scores = {}
    for task in TASKS:
        zs_scores[task] = eval_zero_shot(task, tokenizer)

    # Phase 2: LoRA fine-tuning
    print("\n" + "="*60)
    print("PHASE 2: LoRA fine-tuning")
    print("="*60)
    lora_scores = {}
    lora_models = {}
    loss_hists = {}
    for task in TASKS:
        model, metrics, hist = train_task(task, tokenizer)
        lora_scores[task] = get_scalar(task, metrics)
        lora_models[task] = model
        loss_hists[task] = hist

    # Gate
    gate_metric = lora_scores[GATE_TASK]
    gate_passed = gate_metric > GATE_THRESHOLD
    glue_avg_zs = sum(zs_scores.values()) / len(zs_scores)
    glue_avg_lora = sum(lora_scores.values()) / len(lora_scores)

    activated, indicators = verify_lora(lora_models[GATE_TASK], lora_scores, zs_scores)

    results = {
        "zero_shot": zs_scores,
        "lora": lora_scores,
        "glue_avg_zero_shot": glue_avg_zs,
        "glue_avg_lora": glue_avg_lora,
        "gate_passed": gate_passed,
        "gate_metric": gate_metric,
        "gate_threshold": GATE_THRESHOLD,
        "lora_activated": activated,
        "mechanism_indicators": indicators,
        "train_subsample_ratio": TRAIN_SUBSAMPLE,
        "lora_config": {"r": LORA_R, "alpha": LORA_ALPHA, "target_modules": TARGET_MODULES},
    }

    # Save results
    out_path = os.path.join(RESULTS_DIR, "results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    # Also save to experiment_results.json (pipeline standard location)
    exp_out = os.path.join(os.path.dirname(__file__), "..", "experiment_results.json")
    with open(exp_out, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Zero-shot: {zs_scores}")
    print(f"LoRA:      {lora_scores}")
    print(f"GLUE avg zero-shot: {glue_avg_zs:.4f}")
    print(f"GLUE avg LoRA:      {glue_avg_lora:.4f}")
    print(f"Gate (SST-2 > {GATE_THRESHOLD}): {gate_metric:.4f} → {'PASS ✅' if gate_passed else 'FAIL ❌'}")
    print(f"LoRA activated: {activated}, indicators: {indicators}")
    print(f"Results: {out_path}")

    # Minimal visualization
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 5))
        x = range(len(TASKS))
        w = 0.35
        zs_vals = [zs_scores[t] for t in TASKS]
        lora_vals = [lora_scores[t] for t in TASKS]
        bars1 = ax.bar([i - w/2 for i in x], zs_vals, w, label="Zero-shot", color="steelblue", alpha=0.8)
        bars2 = ax.bar([i + w/2 for i in x], lora_vals, w, label="LoRA (r=8)", color="coral", alpha=0.8)
        ax.axhline(GATE_THRESHOLD, color="red", linestyle="--", label=f"Gate ({GATE_THRESHOLD})")
        ax.set_xticks(list(x)); ax.set_xticklabels(TASKS)
        ax.set_ylim(0, 1.05); ax.set_ylabel("Score"); ax.set_title("Mamba-130m LoRA vs Zero-shot on GLUE")
        ax.legend(); plt.tight_layout()
        fig_path = os.path.join(FIGURES_DIR, "glue_comparison.png")
        plt.savefig(fig_path, dpi=150)
        print(f"Figure saved: {fig_path}")
    except Exception as e:
        print(f"Figure generation failed (non-fatal): {e}")

    return gate_passed


if __name__ == "__main__":
    ok = main()
    print("EXPERIMENT COMPLETE")
    sys.exit(0 if ok else 1)
