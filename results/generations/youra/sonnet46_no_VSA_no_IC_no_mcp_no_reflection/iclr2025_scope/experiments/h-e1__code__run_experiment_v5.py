"""
h-e1 Phase 4 v5: Mamba-130m + Projection-only LoRA on GLUE
Key fixes vs v4:
- Dataset mapped ONCE per task (shared between zero-shot and LoRA eval)
- HF dataset cache enabled (avoids re-tokenizing)
- Train subsample via select() before map (faster)
- Tasks run sequentially, model freed after each
- Explicit CUDA cache clear between tasks
"""
import os
import sys
import json
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
from transformers.optimization import get_linear_schedule_with_warmup
from torch.optim import AdamW
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
import evaluate as hf_evaluate

# ── Config ───────────────────────────────────────────────────────────────────
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
TRAIN_MAX_SAMPLES = 10000  # cap training at 10k per task (well above minimum, fast)
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
TASK_METRIC_KEY = {"sst2": "accuracy", "mnli": "accuracy", "qnli": "accuracy", "qqp": "f1"}

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
H_DIR = os.path.dirname(CODE_DIR)
RESULTS_DIR = os.path.join(H_DIR, "results")
FIGURES_DIR = os.path.join(H_DIR, "figures")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")
if DEVICE == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}, VRAM: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")

# ── Model ─────────────────────────────────────────────────────────────────────

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

# ── Data (tokenize once per task, share between zero-shot and LoRA) ───────────

def prepare_task_data(task, tokenizer):
    """Returns (train_loader, val_loader) with train subsampled to TRAIN_MAX_SAMPLES."""
    ds = load_dataset("glue", task)
    fields = TASK_TEXT_FIELDS[task]

    def tok(batch):
        if len(fields) == 1:
            return tokenizer(batch[fields[0]], max_length=MAX_LENGTH, truncation=True, padding="max_length")
        return tokenizer(batch[fields[0]], batch[fields[1]], max_length=MAX_LENGTH, truncation=True, padding="max_length")

    # Subsample train BEFORE tokenizing to avoid mapping huge datasets
    train_raw = ds["train"]
    n_train = len(train_raw)
    if n_train > TRAIN_MAX_SAMPLES:
        rng = random.Random(SEED)
        idxs = sorted(rng.sample(range(n_train), TRAIN_MAX_SAMPLES))
        train_raw = train_raw.select(idxs)

    val_raw = ds[TASK_VAL_SPLIT[task]]

    col_rm = [c for c in train_raw.column_names if c != "label"]
    train_tok = train_raw.map(tok, batched=True, remove_columns=col_rm)
    train_tok.set_format("torch", columns=["input_ids", "label"])

    col_rm_val = [c for c in val_raw.column_names if c != "label"]
    val_tok = val_raw.map(tok, batched=True, remove_columns=col_rm_val)
    val_tok.set_format("torch", columns=["input_ids", "label"])

    print(f"  {task}: train={len(train_tok)}, val={len(val_tok)}")
    train_loader = DataLoader(train_tok, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_tok, batch_size=BATCH_SIZE)
    return train_loader, val_loader

# ── Eval ──────────────────────────────────────────────────────────────────────

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
    return metrics.get(TASK_METRIC_KEY[task], 0.0)

# ── Training ─────────────────────────────────────────────────────────────────

def run_task(task, tokenizer):
    """Run zero-shot eval + LoRA fine-tune for one GLUE task. Returns (zs_score, lora_score, model)."""
    print(f"\n{'='*60}\nTask: {task}\n{'='*60}")
    set_seed(SEED)
    train_loader, val_loader = prepare_task_data(task, tokenizer)

    # Zero-shot
    print(f"[Zero-shot] {task}...")
    zs_model = build_zero_shot_model(TASK_LABEL_COUNTS[task]).to(DEVICE)
    zs_metrics = eval_model(zs_model, val_loader, task)
    zs_score = get_scalar(task, zs_metrics)
    print(f"  zero-shot {task} = {zs_score:.4f}")
    del zs_model
    if DEVICE == "cuda":
        torch.cuda.empty_cache()

    # LoRA fine-tune
    print(f"[LoRA] {task}...")
    model = build_lora_model(TASK_LABEL_COUNTS[task]).to(DEVICE)
    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    total_steps = len(train_loader) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    for epoch in range(EPOCHS):
        model.train()
        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(DEVICE)
            labels = batch["label"].to(DEVICE)
            out = model(input_ids, labels=labels)
            out["loss"].backward()
            optimizer.step(); scheduler.step(); optimizer.zero_grad()
            if step % 100 == 0:
                print(f"  epoch {epoch+1}/{EPOCHS} step {step}/{len(train_loader)} loss={out['loss'].item():.4f}")
        lora_metrics = eval_model(model, val_loader, task)
        lora_score = get_scalar(task, lora_metrics)
        print(f"  epoch {epoch+1} val {task} = {lora_score:.4f}")

    return zs_score, lora_score, model

# ── LoRA verification ─────────────────────────────────────────────────────────

def verify_lora(model, lora_scores, zs_scores):
    sd = model.backbone.state_dict()
    lora_keys = [k for k in sd if "lora_A" in k or "lora_B" in k]
    keys_present = len(lora_keys) > 0
    weights_nonzero = any(sd[k].abs().sum().item() > 0 for k in lora_keys) if lora_keys else False
    delta_positive = lora_scores.get("sst2", 0) > zs_scores.get("sst2", 0)
    indicators = {
        "lora_keys_present": keys_present,
        "lora_weights_nonzero": weights_nonzero,
        "sst2_delta_positive": delta_positive,
    }
    return keys_present and weights_nonzero, indicators

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    set_seed(SEED)
    random.seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    zs_scores = {}
    lora_scores = {}
    gate_model = None

    for task in TASKS:
        zs_score, lora_score, model = run_task(task, tokenizer)
        zs_scores[task] = zs_score
        lora_scores[task] = lora_score
        if task == GATE_TASK:
            gate_model = model
        else:
            del model
            if DEVICE == "cuda":
                torch.cuda.empty_cache()

    gate_metric = lora_scores[GATE_TASK]
    gate_passed = gate_metric > GATE_THRESHOLD
    glue_avg_zs = sum(zs_scores.values()) / len(zs_scores)
    glue_avg_lora = sum(lora_scores.values()) / len(lora_scores)

    activated, indicators = verify_lora(gate_model, lora_scores, zs_scores)

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
        "train_max_samples_per_task": TRAIN_MAX_SAMPLES,
        "lora_config": {"r": LORA_R, "alpha": LORA_ALPHA, "target_modules": TARGET_MODULES},
    }

    # Save
    for out_path in [
        os.path.join(RESULTS_DIR, "results.json"),
        os.path.join(H_DIR, "experiment_results.json"),
    ]:
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Zero-shot: {zs_scores}")
    print(f"LoRA:      {lora_scores}")
    print(f"GLUE avg zero-shot: {glue_avg_zs:.4f}")
    print(f"GLUE avg LoRA:      {glue_avg_lora:.4f}")
    print(f"Gate (SST-2 > {GATE_THRESHOLD}): {gate_metric:.4f} → {'PASS' if gate_passed else 'FAIL'}")
    print(f"LoRA activated: {activated}, indicators: {indicators}")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 5))
        w = 0.35
        x = list(range(len(TASKS)))
        ax.bar([i - w/2 for i in x], [zs_scores[t] for t in TASKS], w, label="Zero-shot", color="steelblue", alpha=0.8)
        ax.bar([i + w/2 for i in x], [lora_scores[t] for t in TASKS], w, label=f"LoRA r={LORA_R}", color="coral", alpha=0.8)
        ax.axhline(GATE_THRESHOLD, color="red", linestyle="--", label=f"Gate threshold ({GATE_THRESHOLD})")
        ax.set_xticks(x); ax.set_xticklabels(TASKS)
        ax.set_ylim(0, 1.05); ax.set_ylabel("Score"); ax.set_title("Mamba-130m LoRA vs Zero-shot (GLUE)")
        ax.legend(); plt.tight_layout()
        fig_path = os.path.join(FIGURES_DIR, "glue_comparison.png")
        plt.savefig(fig_path, dpi=150)
        print(f"Figure: {fig_path}")
    except Exception as e:
        print(f"Figure skipped: {e}")

    return gate_passed


if __name__ == "__main__":
    ok = main()
    print("EXPERIMENT COMPLETE")
    sys.exit(0 if ok else 1)
