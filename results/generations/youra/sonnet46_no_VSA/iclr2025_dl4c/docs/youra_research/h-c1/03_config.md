# Configuration: H-C1 — Scale Attenuation of SFT Source Identity Effect

**Applied: H-E2 hardcoded-dict pattern, extended to 7B with YAML experiment manifest**

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from H-E2 base code (`docs/youra_research/h-e2/code/`)
**Config Files Found**: `h-e2/code/train.py`, `h-e2/code/ds_zero3_config.json`, `h-e2/code/requirements.txt`
**Pattern Used**: hardcoded dict (same as H-E2) + YAML experiment manifest for run management

---

## Inherited Configuration (Base Hypothesis H-E2)

### Verified From Actual H-E2 Code

```python
# From: docs/youra_research/h-e2/code/train.py (ACTUAL CODE)
# All values below verified from implementation

CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS = [42, 123, 777]

FIXED_HPARAMS = {
    "learning_rate": 2e-5,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.05,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "bf16": True,
    "completion_only_loss": True,
    "max_length": 2048,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,  # non-standard: DeepSeek-Coder official recommendation
}

EPOCHS_PER_CONDITION = {
    "humaneval_only": 6,
    "mbpp_only":      3,
    "leetcode_only":  1,
    "equal_mix":      2,
}
```

---

## H-C1 Configuration

### Python Constants (`train.py`)

```python
# ── Model ──────────────────────────────────────────────────────────────────
MODEL_ID = "deepseek-ai/deepseek-coder-7b-base"
DTYPE = "bfloat16"
ATTN_IMPL = "flash_attention_2"
DEVICE_MAP = None  # ZeRO-3 handles device placement; do not set device_map with DeepSpeed

# ── Experiment ─────────────────────────────────────────────────────────────
CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS = [42, 123, 777]

# ── Hyperparameters (identical to H-E2 for controlled comparison) ──────────
FIXED_HPARAMS = {
    "learning_rate": 2e-5,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.05,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "bf16": True,
    "completion_only_loss": True,
    "max_length": 2048,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,  # non-standard: DeepSeek-Coder official recommendation
}

EPOCHS_PER_CONDITION = {
    "humaneval_only": 6,
    "mbpp_only":      3,
    "leetcode_only":  1,
    "equal_mix":      2,
}

# ── Data ───────────────────────────────────────────────────────────────────
DEDUP_THRESHOLD = 0.95
TARGET_PROBLEMS = 164
H_E2_DATASETS_DIR = "docs/youra_research/h-e2/data/sft_sources"  # reuse prepared splits

# ── Evaluation ─────────────────────────────────────────────────────────────
EVALPLUS_VERSION = "0.3.1"
BENCHMARKS = ["humaneval", "mbpp"]
EVALPLUS_BACKEND = "hf"
EVALPLUS_GREEDY = True  # temperature=0, do_sample=False

# ── Paths ──────────────────────────────────────────────────────────────────
OUTPUT_DIR = "docs/youra_research/h-c1/checkpoints"
RESULTS_FILE = "docs/youra_research/h-c1/results/results.csv"
FIGURES_DIR = "docs/youra_research/h-c1/figures"
REPORT_PATH = "docs/youra_research/h-c1/results/statistical_report.txt"

# ── LoRA fallback (activate if OOM on full fine-tune) ──────────────────────
LORA_CONFIG = {
    "r": 16,
    "lora_alpha": 32,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "CAUSAL_LM",
}
LORA_ENABLED = False  # ponytail: set True only if full fine-tune OOM on 4x H100 80GB

# ── Run matrix ─────────────────────────────────────────────────────────────
ALL_RUNS = [
    {"condition": c, "seed": s}
    for c in CONDITIONS
    for s in SEEDS
]  # 12 total

# ── Analysis thresholds (same as H-E2) ────────────────────────────────────
N_COMPARISONS = 12
ALPHA = 0.05
MIN_CONTRAST_PP = 2.0
FAIL_THRESHOLD_PP = 1.5
```

---

## YAML Experiment Manifest (`experiments/h-c1/config.yaml`)

```yaml
model:
  name: deepseek-ai/deepseek-coder-7b-base
  dtype: bfloat16
  attn_implementation: flash_attention_2
  device_map: null  # DeepSpeed manages placement

training:
  learning_rate: 2.0e-5
  lr_scheduler_type: cosine
  num_train_epochs: null  # set per-condition via EPOCHS_PER_CONDITION
  per_device_train_batch_size: 4
  gradient_accumulation_steps: 4
  warmup_ratio: 0.05
  weight_decay: 0.01
  bf16: true
  save_strategy: "no"   # save only final checkpoint per run
  completion_only_loss: true
  max_seq_length: 2048

data:
  conditions:
    - humaneval_only
    - mbpp_only
    - leetcode_only
    - equal_mix
  seeds:
    - 42
    - 123
    - 777
  dedup_threshold: 0.95
  token_budget_equalize: true   # same as H-E2: TARGET_PROBLEMS=164
  h_e2_datasets_dir: docs/youra_research/h-e2/data/sft_sources

evaluation:
  evalplus_version: "0.3.1"
  datasets:
    - humaneval
    - mbpp
  decoding:
    do_sample: false
    temperature: 1.0   # irrelevant when do_sample=false; kept for explicitness
    max_new_tokens: 512
  backend: hf

paths:
  output_dir: docs/youra_research/h-c1/checkpoints
  results_file: docs/youra_research/h-c1/results/results.csv
  figures_dir: docs/youra_research/h-c1/figures

lora_fallback:
  enabled: false
  r: 16
  lora_alpha: 32
  lora_dropout: 0.05
  bias: none
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj
    - up_proj
    - down_proj
```

---

## DeepSpeed ZeRO-3 Config (`experiments/h-c1/ds_zero3_config.json`)

Same as H-E2 with `sub_group_size` kept for 7B sharding across 4 GPUs.

```json
{
  "bf16": {
    "enabled": true
  },
  "zero_optimization": {
    "stage": 3,
    "overlap_comm": true,
    "contiguous_gradients": true,
    "sub_group_size": 1e9,
    "reduce_bucket_size": 5e8,
    "stage3_prefetch_bucket_size": 5e8,
    "stage3_param_persistence_threshold": 1e6,
    "allgather_bucket_size": 2e8,
    "stage3_max_live_parameters": 1e9,
    "stage3_max_reuse_distance": 1e9,
    "stage3_gather_16bit_weights_on_model_save": true
  },
  "gradient_accumulation_steps": "auto",
  "gradient_clipping": 1.0,
  "steps_per_print": 10,
  "train_batch_size": "auto",
  "train_micro_batch_size_per_gpu": "auto",
  "wall_clock_breakdown": false
}
```

---

## Environment Variables

```bash
# HuggingFace cache — set before launching any script
export HF_HOME=/scratch/hf_cache
export HF_DATASETS_CACHE=/scratch/hf_cache/datasets
export TOKENIZERS_PARALLELISM=false

# DeepSpeed / multi-GPU
export MASTER_ADDR=localhost
export MASTER_PORT=29500
```

---

## Requirements (`experiments/h-c1/requirements.txt`)

```
torch>=2.1.0
transformers>=4.40.0
trl>=0.8.6
accelerate>=0.28.0
deepspeed>=0.14.0
datasets>=2.18.0
evalplus==0.3.1
scipy>=1.12.0
pingouin>=0.5.4
statsmodels>=0.14.0
matplotlib>=3.8.0
pandas>=2.0.0
numpy>=1.26.0
peft>=0.10.0
flash-attn>=2.5.0
```

Notes:
- `evalplus==0.3.1` pinned (exact version required for reproducibility with H-E2)
- `peft` required for LoRA fallback path even when `LORA_ENABLED=False` (import guard)
- `flash-attn` build requires CUDA 11.8+ and matching torch version; install separately if needed: `pip install flash-attn --no-build-isolation`

---

## Validation Checks

```python
# Paste into train.py __main__ guard or a standalone validate_config.py

def validate_config():
    # 1. All conditions present
    assert set(CONDITIONS) == {"humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"}, \
        f"Missing conditions: {set(CONDITIONS)}"

    # 2. Seeds match spec
    assert SEEDS == [42, 123, 777], f"Seeds mismatch: {SEEDS}"

    # 3. Model loads in bf16 (smoke test — loads config only, no weights)
    from transformers import AutoConfig
    cfg = AutoConfig.from_pretrained(MODEL_ID)
    assert cfg.model_type in ("llama", "deepseek"), \
        f"Unexpected model_type: {cfg.model_type}"
    print(f"Config OK: {MODEL_ID}, {len(ALL_RUNS)} runs, seeds={SEEDS}")

if __name__ == "__main__":
    validate_config()
```

---

## Key Delta from H-E2

| Parameter | H-E2 | H-C1 |
|-----------|-------|-------|
| `MODEL_ID` | `deepseek-coder-1.3b-base` | `deepseek-coder-7b-base` |
| All hparams | (baseline) | **identical** |
| Hardware | single GPU / 2-GPU | 4× H100 80GB + ZeRO-3 |
| `DEVICE_MAP` | auto | null (DeepSpeed) |
