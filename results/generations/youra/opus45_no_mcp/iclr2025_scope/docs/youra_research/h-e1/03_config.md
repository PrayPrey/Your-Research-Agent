# Config: H-E1

**Type:** EXISTENCE (PoC) — single fixed config, no sweeps, 1 seed.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no MCP tools available, no base_hypothesis_folder)
**Config Files Found**: None
**Pattern Used**: Hardcoded dict

**Applied**: Baseline-vs-Proposed fixed-config pattern (from architecture.md)

---

## A-1: Setup & Data Loading [Complexity: 8, Budget: 2 subtasks]

**Applied**: HF datasets auto-download pattern

### Configuration (Hardcoded dict)
```python
BENCHMARKS = {
    "gsm8k": dict(hf_id="openai/gsm8k", subset="main", split="test", metric="exact_match", density=0.1),
    "nq": dict(hf_id="google-research-datasets/natural_questions", subset=None, split="validation", metric="f1", density=0.9),
    "mmlu": dict(hf_id="cais/mmlu", subset="all", split="test", metric="accuracy", density=0.5),
    "hotpotqa": dict(hf_id="hotpot_qa", subset="fullwiki", split="validation", metric="f1", density=0.7),
}
```
Source: PRD FR-3 (test sizes/densities/metrics fixed, no variation).

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Data loading & formatting | Download 4 HF datasets, tokenize/format for causal LM per `BENCHMARKS` config |

---

## A-2: Baseline Model + LoRA [Complexity: 7, Budget: 1 subtask]

**Applied**: PEFT LoRA standard config

### Configuration (Hardcoded dict)
```python
LORA_CONFIG_TRANSFORMER = dict(
    r=16, lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.0,
)

TRAIN_CONFIG = dict(
    lr=2e-4, weight_decay=0.01, betas=(0.9, 0.999),
    warmup_steps=100, batch_size=4, grad_accum=4,
    epochs=3, seed=42,
)

MODEL_ID_BASELINE = "meta-llama/Llama-2-7b-hf"
```
Source: PRD FR-1 (fixed LoRA rank/alpha/targets, 3 epochs). `TRAIN_CONFIG` shared by both models (NFR-1).

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Baseline model load + verify | Load Llama-2-7B, apply `LORA_CONFIG_TRANSFORMER`, verify forward pass |

---

## Full Config Reference (Shared, from architecture.md)

Used as-is by A-3..A-7 (out of this task's allocation, listed for continuity only):

```python
LORA_CONFIG_MAMBA = dict(
    r=16, lora_alpha=32,
    target_modules=["in_proj", "out_proj"],
    lora_dropout=0.0,
)

GATE_THRESHOLDS = dict(
    gsm8k_delta_min=-0.05,
    nq_delta_max=-0.15,
    spearman_min=0.5,
)
```

## Notes
- Mixed precision (fp16/bf16) per NFR-3 — no explicit config field, set via `accelerate`/`Trainer` default flag at train call site.
- No hyperparameter grid — EXISTENCE hypothesis uses single fixed run per model per benchmark, seed=42 only.
