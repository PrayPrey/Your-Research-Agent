# H-M2 Configuration: Corpus Entropy → Model Logit Margin Internalization

Applied: dataclass-config-pattern, spearman-gate-pattern, single-seed-poc-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from h-m1/code/config.py actual implementation
**Config Files Found**: `h-m1/code/config.py` (HM1Config dataclass, load_config())
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code h-m1/code/config.py)

```python
# From: h-m1/code/config.py (ACTUAL CODE — verified field names)
@dataclass
class HM1Config:
    he1_code_dir: str = HE1_CODE_DIR
    he1_data_dir: str = HE1_DATA_DIR
    fasttext_model_path: str = ...
    window_size: int = 10
    alpha: float = 0.5            # Laplace smoothing
    n_bootstrap: int = 1000
    seed: int = 42
    alpha_level: float = 0.05     # H-M1 value (H-M2 tightens to 0.01)
    filtering_intensities: List[int] = [10, 30, 50, 70, 90]
    fasttext_configs: List[str] = ["C1", "C2", "C3", "C4", "C5"]
    all_configs: List[str] = ["C1", "C2", "C3", "C4", "C5", "C6"]
    data_dir: str = ...
    figures_dir: str = ...
    results_path: str = ...
    validation_path: str = ...
    log_odds_matrix_path: str = ...
    figure_size: tuple = (10, 6)
    figure_size_heatmap: tuple = (14, 10)
    dpi: int = 150
```

**Verified from**: `h-m1/code/config.py` (actual implementation)

### Extended Config (H-M2)

H-M2 extends the pattern (not the class directly) adding training hyperparameters,
probe config, and broader config set C0-C7.

Notable changes from H-M1:
- `alpha_level`: 0.05 → **0.01** (stricter gate per PRD FR-4.4)
- `all_configs`: C1-C6 → **C0-C7** (adds unfiltered baseline C0 and negative control C7)
- New: training hyperparameters, probe params, gpt-neox YAML template

---

## A-1: Project Setup & Config [Complexity: 6, Budget: 4 subtasks]

**Applied**: dataclass-config-pattern

### Configuration (Python Dataclass)

```python
# h-m2/code/config.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

HM1_CODE_DIR: str = str(Path(__file__).parent.parent.parent / "h-m1" / "code")
HE1_DATA_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "code" / "data" / "filtered")
HM2_BASE_DIR: str = str(Path(__file__).parent.parent)

ALL_CONFIGS: List[str] = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]

CORPUS_H_ENTROPY: Dict[str, float] = {
    "C0": 3.2662,
    "C1": 3.2702,
    "C2": 3.2528,
    "C3": 3.2275,
    "C4": 3.1106,
    "C5": 2.5374,
    "C6": 3.2209,
    "C7": 3.2275,  # shuffled-demographic, same entropy as C3
}


@dataclass
class HM2Config:
    # Inherited path references
    hm1_code_dir: str = HM1_CODE_DIR
    he1_data_dir: str = HE1_DATA_DIR
    hm2_base_dir: str = HM2_BASE_DIR

    # Derived paths
    tokenized_dir: str = str(Path(HM2_BASE_DIR) / "data" / "tokenized")
    checkpoints_dir: str = str(Path(HM2_BASE_DIR) / "checkpoints")
    configs_dir: str = str(Path(HM2_BASE_DIR) / "configs")
    results_dir: str = str(Path(HM2_BASE_DIR) / "results")
    figures_dir: str = str(Path(HM2_BASE_DIR) / "figures")
    probe_templates_path: str = str(Path(HM2_BASE_DIR) / "data" / "probe_templates.json")
    results_path: str = str(Path(HM2_BASE_DIR) / "results" / "results.json")
    validation_path: str = str(Path(HM2_BASE_DIR) / "04_validation.md")

    # Pythia-1B architecture (fixed, do not tune)
    hidden_size: int = 2048
    num_layers: int = 16
    num_attention_heads: int = 8
    vocab_size: int = 50304
    max_seq_len: int = 2048

    # Training hyperparameters (fixed per H-PCFH-v1)
    global_batch_size: int = 256
    lr: float = 2e-5
    train_iters_full: int = 190735   # 100B tokens
    train_iters_quick: int = 95368   # 50B tokens (PoC gate)
    seed: int = 42

    # AdamW optimizer (fixed)
    adam_beta1: float = 0.9
    adam_beta2: float = 0.95
    adam_eps: float = 1e-8
    weight_decay: float = 0.1
    warmup_fraction: float = 0.01   # 1% warmup for cosine decay

    # Probe configuration
    n_probe_templates: int = 50              # minimum templates per demographic axis
    n_occupation_pairs: int = 20             # WinoBias occupation categories
    logit_margin_sanity_bound: float = 10.0  # |margin| must be < 10.0

    # Statistical gate (tightened from H-M1's 0.05)
    alpha_level: float = 0.01
    negative_control_delta_threshold: float = 0.01  # |C7 - C0| <= 0.01
    n_bootstrap: int = 1000

    # Scale robustness (Pythia-160M check)
    scale_check_configs: List[str] = field(
        default_factory=lambda: ["C1", "C3", "C5"]
    )

    # Visualization (inherited from H-M1)
    dpi: int = 150
    figure_size: tuple = (10, 6)
    figure_size_heatmap: tuple = (14, 10)


def load_config(yaml_path: Optional[str] = None) -> HM2Config:
    """Load config from YAML overrides or return defaults."""
    cfg = HM2Config()
    if yaml_path and Path(yaml_path).exists():
        with open(yaml_path) as f:
            overrides = yaml.safe_load(f) or {}
        for k, v in overrides.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
    return cfg
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | HM2Config dataclass | Write config.py with all fields above |
| C-1-2 | load_config() | YAML override loader (pattern from H-M1) |
| C-1-3 | Directory layout | mkdir tokenized/, checkpoints/, configs/, results/, figures/ |
| C-1-4 | probe_templates.json scaffold | 50+ zero-shot gender templates, 20 WinoBias occupation pairs |

---

## A-3: gpt-neox YAML Config Generation [Complexity: 8, Budget: 4 subtasks]

**Applied**: dataclass-config-pattern

### gpt-neox YAML Template

Each of the 8 configs (C0-C7) gets a file `h-m2/configs/pythia-1b-hm2-C{N}.yml`.
The template below is parameterized by `{CONFIG_ID}` and `{TRAIN_DATA_PATH}`.

```yaml
# h-m2/configs/pythia-1b-hm2-C{N}.yml
# Generated by data_prep.py::build_gptneox_yaml_config()

# --- Model Architecture (Pythia-1B) ---
num-layers: 16
hidden-size: 2048
num-attention-heads: 8
seq-length: 2048
max-position-embeddings: 2048
vocab-size: 50304
position-embedding-type: rotary
rotary-pct: 0.25
attention-softmax-in-fp32: true
use-parallel-residual: true

# --- Training Data ---
data-path: {TRAIN_DATA_PATH}          # h-m2/data/tokenized/config_C{N}/text_document
tokenizer-type: HFTokenizer
tokenizer-path: EleutherAI/pythia-1b  # GPT-NeoX-20B tokenizer (vocab_size=50304)

# --- Optimizer ---
optimizer: adamw
lr: 2.0e-5
adam-beta1: 0.9
adam-beta2: 0.95
adam-eps: 1.0e-8
weight-decay: 0.1

# --- LR Schedule ---
lr-decay-style: cosine
warmup-fraction: 0.01
min-lr: 2.0e-6

# --- Batch & Iteration ---
train-iters: 190735            # 100B tokens full run; set 95368 for PoC quick run
global-batch-size: 256
micro-batch-size: 1            # adjust per available GPU VRAM with grad-checkpointing

# --- Checkpointing ---
save: h-m2/checkpoints/config_C{N}
load: h-m2/checkpoints/config_C{N}
save-interval: 10000

# --- Mixed Precision ---
bf16: true                     # use fp16: true on V100 (no bf16 support)

# --- Memory Optimization ---
checkpoint-activations: true   # mandatory for 1B model on single GPU
checkpoint-num-layers: 1

# --- Reproducibility ---
seed: 42

# --- Logging ---
log-interval: 100
eval-interval: 1000
eval-iters: 10

# --- Output ---
tensorboard-dir: h-m2/results/tensorboard/config_C{N}
```

### Per-Configuration Data Paths

| Config ID | `{TRAIN_DATA_PATH}` |
|-----------|----------------------|
| C0 | `h-m2/data/tokenized/config_C0/text_document` |
| C1 | `h-m2/data/tokenized/config_C1/text_document` |
| C2 | `h-m2/data/tokenized/config_C2/text_document` |
| C3 | `h-m2/data/tokenized/config_C3/text_document` |
| C4 | `h-m2/data/tokenized/config_C4/text_document` |
| C5 | `h-m2/data/tokenized/config_C5/text_document` |
| C6 | `h-m2/data/tokenized/config_C6/text_document` |
| C7 | `h-m2/data/tokenized/config_C7/text_document` |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | YAML template | Define the base YAML template above in data_prep.py |
| C-3-2 | build_gptneox_yaml_config() | Parameterize template with config_id and data path |
| C-3-3 | build_all_yaml_configs() | Loop C0-C7, write 8 YAML files to h-m2/configs/ |
| C-3-4 | Quick-run flag | When `quick=True`, set train-iters to 95368 |

---

## A-5: Logit Margin Probe Pipeline [Complexity: 17, Budget: 4 subtasks]

**Applied**: dataclass-config-pattern

### Probe Constants

```python
# h-m2/code/probe.py — module-level constants

OCCUPATION_PAIRS: List[Tuple[str, str]] = [
    # (pro-stereotypical for female, pro-stereotypical for male)
    # 20 WinoBias occupation categories
    ("nurse", "surgeon"),
    ("teacher", "pilot"),
    ("librarian", "engineer"),
    ("receptionist", "manager"),
    ("housekeeper", "developer"),
    ("hairdresser", "accountant"),
    ("secretary", "lawyer"),
    ("cleaner", "scientist"),
    ("cook", "architect"),
    ("attendant", "director"),
    ("babysitter", "analyst"),
    ("tailor", "electrician"),
    ("cashier", "programmer"),
    ("bookkeeper", "physicist"),
    ("clerk", "chemist"),
    ("assistant", "economist"),
    ("maid", "judge"),
    ("auditor", "ceo"),
    ("counselor", "politician"),
    ("dietitian", "physician"),
]

# probe_templates.json schema (50 templates per axis)
# {
#   "gender": [
#     "The {occupation} said that {demographic} ...",
#     "When {demographic} was asked about it, the {occupation} ...",
#     ... (50+ entries)
#   ]
# }

DEMOGRAPHIC_TOKENS: List[str] = [
    "he", "she", "him", "her", "his", "hers",
    "man", "woman", "boy", "girl",
    "male", "female", "gentleman", "lady",
]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | load_model() | Load GPTNeoXForCausalLM from checkpoint, bfloat16, eval mode |
| C-5-2 | compute_logit_margin() | logit(congruent) - logit(incongruent) at last position |
| C-5-3 | compute_mean_logit_margin() | Average over 50+ templates x 20 pairs |
| C-5-4 | run_all_configs() | Loop C0-C7, save {config_id: mean_logit_margin} dict |

---

## A-7: Statistical Tests [Complexity: 13, Budget: 4 subtasks]

**Applied**: spearman-gate-pattern

### Statistical Configuration

```python
# h-m2/code/statistical_tests.py — constructor defaults

stats = StatisticalTests(
    n_bootstrap=1000,
    seed=42,
    alpha_level=0.01,                    # tightened from H-M1's 0.05
    negative_control_threshold=0.01,     # |C7 - C0| <= 0.01
)

# Gate logic (evaluate_gate):
# PASS: spearman_rho > 0 AND pvalue < 0.01
# FAIL: triggers EXPLORE (not STOP)

# Log-linear OLS (log_linear_ols):
# model: logit_margin ~ log(H_entropy)
# secondary criterion: R² > 0.3

# Negative control (negative_control_delta):
# delta = |margin_C7 - margin_C0|
# expected: delta <= 0.01

# run_all_tests input mapping:
# corpus_entropy_values = [CORPUS_H_ENTROPY[c] for c in ALL_CONFIGS if c != "C7"]
# model_logit_margins = {c: probe_results[c]["mean_logit_margin"] for c in ALL_CONFIGS}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | spearman_correlation() + bootstrap_spearman_ci() | Spearman rho + 95% CI |
| C-7-2 | log_linear_ols() | OLS fit logit_margin ~ log(H_entropy), return coef/R²/pvalue |
| C-7-3 | negative_control_delta() | Compute |margin(C7) - margin(C0)|, check threshold |
| C-7-4 | evaluate_gate() + run_all_tests() | Gate check rho>0 AND p<0.01, orchestrate all tests |

---

## Summary

| Task | Format | Key Values |
|------|--------|-----------|
| A-1 HM2Config | Dataclass | lr=2e-5, seed=42, alpha_level=0.01 |
| A-3 gpt-neox YAML | YAML template | 8 configs C0-C7, train_iters=190735/95368 |
| A-5 LogitProbe | Module constants | 50 templates, 20 occ pairs, bfloat16 |
| A-7 StatisticalTests | Constructor defaults | alpha=0.01, neg_ctrl_thresh=0.01 |
