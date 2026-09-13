"""
h-e1 Phase 4 v8: Mamba-130m + LoRA on GLUE — dynamo disabled (MambaCache fix)
"""
import os
import sys

# Must be set before any torch import to prevent dynamo from tracing MambaCache
os.environ["TORCHDYNAMO_DISABLE"] = "1"

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

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME = "state-spaces/mamba-130m-hf"
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
TARGET_MODULES = ["in_proj", "out_proj", "x_proj"]
MAX_LENGTH = 64
BATCH_SIZE = 32
EPOCHS = 3
LR = 3e-4
WEIGHT_DECAY = 0.01
WARMUP_RATIO = 0.06
SEED = 42
TRAIN_MAX = 4000
VAL_MAX = 872   # full SST-2 val set; others capped at 872 for consistency
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
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# ── Model ─────────────────────────────────────────────────────────────────────

class MambaClassifier(nn.Module):
    def __init__(self, backbone, num_labels: int, d_model: int = 768):
        super().__init__()
        self.backbone = backbone
        self.classifier = nn.Linear(d_model, num_labels)
        nn.init.normal_(self.classifier.weight, std=0.02)
        nn.init.zeros_(self.classifier.bias)

    def forward(self, input_ids, labels=None):
        out = self.backbone(input_ids, output_hidden_states=True, use_cache=False)
        pooled = out.hidden_states[-1][:, -1, :]
        logits = self.classifier(pooled)
        result = {"logits": logits}
        if labels is not None:
            result["loss"] = F.cross_entropy(logits, labels)
        return result


def make_lora_model(num_labels):
    base = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    cfg = LoraConfig(
        r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES, bias="none", task_type="FEATURE_EXTRACTION",
    )
    backbone = get_peft_model(base, cfg)
    backbone.print_trainable_parameters()
    return MambaClassifier(backbone, num_labels)


def make_zero_shot_model(num_labels):
    base = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    for p in base.parameters():
        p.requires_grad = False
    return MambaClassifier(base, num_labels)

# ── Data ─────────────────────────────────────────────────────────────────────

def subsample(ds, n):
    if len(ds) <= n:
        return ds
    rng = random.Random(SEED)
    return ds.select(sorted(rng.sample(range(len(ds)), n)))


def tok_fn(tokenizer, fields):
    def _tok(batch):
        if len(fields) == 1:
            return tokenizer(batch[fields[0]], max_length=MAX_LENGTH, truncation=True, padding="max_length")
        return tokenizer(batch[fields[0]], batch[fields[1]], max_length=MAX_LENGTH, truncation=True, padding="max_length")
    return _tok


def prepare(task, tokenizer):
    ds = load_dataset("glue", task)
    fields = TASK_TEXT_FIELDS[task]
    train_raw = subsample(ds["train"], TRAIN_MAX)
    val_raw = subsample(ds[TASK_VAL_SPLIT[task]], VAL_MAX)
    col_rm_tr = [c for c in train_raw.column_names if c != "label"]
    col_rm_vl = [c for c in val_raw.column_names if c != "label"]
    tf = tok_fn(tokenizer, fields)
    tr = train_raw.map(tf, batched=True, remove_columns=col_rm_tr)
    vl = val_raw.map(tf, batched=True, remove_columns=col_rm_vl)
    tr.set_format("torch", columns=["input_ids", "label"])
    vl.set_format("torch", columns=["input_ids", "label"])
    print(f"  {task}: train={len(tr)}, val={len(vl)}")
    return DataLoader(tr, batch_size=BATCH_SIZE, shuffle=True), DataLoader(vl, batch_size=BATCH_SIZE)


def eval_model(model, val_loader, task):
    metric = hf_evaluate.load("glue", task)
    model.eval()
    with torch.no_grad():
        for batch in val_loader:
            logits = model(batch["input_ids"].to(DEVICE))["logits"]
            metric.add_batch(predictions=logits.argmax(-1).cpu().tolist(), references=batch["label"].tolist())
    return metric.compute()

# ── Per-task run ──────────────────────────────────────────────────────────────

def run_task(task, tokenizer):
    print(f"\n{'='*60}\nTask: {task}\n{'='*60}")
    set_seed(SEED)
    train_loader, val_loader = prepare(task, tokenizer)

    print("[Zero-shot]", flush=True)
    zs_model = make_zero_shot_model(TASK_LABEL_COUNTS[task]).to(DEVICE)
    zs_metrics = eval_model(zs_model, val_loader, task)
    zs_score = zs_metrics.get(TASK_METRIC_KEY[task], 0.0)
    print(f"  zero-shot {task} = {zs_score:.4f}")
    del zs_model
    if DEVICE == "cuda":
        torch.cuda.empty_cache()

    print("[LoRA train]", flush=True)
    model = make_lora_model(TASK_LABEL_COUNTS[task]).to(DEVICE)
    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, int(total_steps * WARMUP_RATIO), total_steps)
    lora_score = 0.0
    for epoch in range(EPOCHS):
        model.train()
        for step, batch in enumerate(train_loader):
            ids = batch["input_ids"].to(DEVICE)
            lbls = batch["label"].to(DEVICE)
            out = model(ids, labels=lbls)
            out["loss"].backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            if step % 20 == 0:
                print(f"  e{epoch+1} s{step}/{len(train_loader)} loss={out['loss'].item():.4f}", flush=True)
        m = eval_model(model, val_loader, task)
        lora_score = m.get(TASK_METRIC_KEY[task], 0.0)
        print(f"  epoch {epoch+1} val {task} = {lora_score:.4f}", flush=True)

    return zs_score, lora_score, model

# ── Main ─────────────────────────────────────────────────────────────────────

def verify_lora(model, lora_scores, zs_scores):
    backbone = model.backbone
    sd = backbone.state_dict()
    keys = [k for k in sd if "lora_A" in k or "lora_B" in k]
    keys_ok = len(keys) > 0
    nonzero = any(sd[k].abs().sum().item() > 0 for k in keys) if keys else False
    delta = lora_scores.get("sst2", 0) > zs_scores.get("sst2", 0)
    return keys_ok and nonzero, {"lora_keys_present": keys_ok, "lora_weights_nonzero": nonzero, "sst2_delta_positive": delta}


def main():
    set_seed(SEED)
    random.seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    zs_scores, lora_scores, gate_model = {}, {}, None

    for task in TASKS:
        zs, lora, model = run_task(task, tokenizer)
        zs_scores[task] = zs
        lora_scores[task] = lora
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
        "config": {
            "max_length": MAX_LENGTH, "train_max": TRAIN_MAX, "val_max": VAL_MAX,
            "epochs": EPOCHS, "lora_r": LORA_R, "target_modules": TARGET_MODULES,
        },
    }

    for path in [os.path.join(RESULTS_DIR, "results.json"), os.path.join(H_DIR, "experiment_results.json")]:
        with open(path, "w") as f:
            json.dump(results, f, indent=2)

    print("\n" + "="*60 + "\nRESULTS SUMMARY\n" + "="*60)
    for t in TASKS:
        print(f"  {t}: zs={zs_scores[t]:.4f}  lora={lora_scores[t]:.4f}")
    print(f"GLUE avg: zs={glue_avg_zs:.4f}  lora={glue_avg_lora:.4f}")
    print(f"Gate SST-2 > {GATE_THRESHOLD}: {gate_metric:.4f} -> {'PASS' if gate_passed else 'FAIL'}")
    print(f"LoRA activated: {activated}, {indicators}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 5))
        w, x = 0.35, list(range(len(TASKS)))
        ax.bar([i-w/2 for i in x], [zs_scores[t] for t in TASKS], w, label="Zero-shot", color="steelblue", alpha=0.8)
        ax.bar([i+w/2 for i in x], [lora_scores[t] for t in TASKS], w, label=f"LoRA r={LORA_R}", color="coral", alpha=0.8)
        ax.axhline(GATE_THRESHOLD, color="red", ls="--", label=f"Gate ({GATE_THRESHOLD})")
        ax.set_xticks(x)
        ax.set_xticklabels(TASKS)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Score")
        ax.set_title("Mamba-130m LoRA vs Zero-shot (GLUE)")
        ax.legend()
        plt.tight_layout()
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
