# Architecture: H-E1

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-03

Applied: minimal-pipeline (flat scripts, no abstraction layers)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** docs/youra_research/h-e1/
**Findings:** Only 02c_experiment_brief.md and 03_prd.md exist. New implementation from scratch.

Archon KB returned diffusers/image-generation content only (similarity < 0.48). No domain-relevant patterns extracted.

---

## File Structure

```
h-e1/
  code/
    config.py              # all hyperparameters, paths, category labels
    distill_mohawk.py      # MOHAWK 3-stage distillation wrapper (calls goombalab/mohawk)
    distill_lawcat.py      # LAWCAT 2-phase distillation wrapper (calls zeyuliu1037/LAWCAT)
    distill_hybrid4.py     # Hybrid-4 Stage 3 fine-tuning wrapper
    evaluate.py            # LongBench v2 eval + Δ_norm computation
    analyze.py             # statistical analysis + mechanism verification
    visualize.py           # 4 figures → h-e1/figures/
  figures/
  checkpoints/
    mohawk/
    lawcat/
    hybrid4/
  results/                 # JSON per model
```

External repos cloned alongside (not inside code/):
```
repos/
  mohawk/    # git clone https://github.com/goombalab/mohawk
  LAWCAT/    # git clone https://github.com/zeyuliu1037/LAWCAT
  LongBench/ # git clone https://github.com/THUDM/LongBench
```

---

## Modules

### Config (`code/config.py`)

**Dependencies:** none

```python
TEACHER_MODEL = "meta-llama/Llama-3-8B"
C4_DATASET = ("allenai/c4", "en")
LONGBENCH_DATASET = ("THUDM/LongBench", "v2")

MOHAWK_REPO = "repos/mohawk"
LAWCAT_REPO = "repos/LAWCAT"
LONGBENCH_REPO = "repos/LongBench"

MOHAWK_CONFIG = "configs/Llama/8B/"
MOHAWK_STAGE_TOKENS = {"stage1": 26_000_000, "stage2": 52_000_000, "stage3": 920_000_000}
MOHAWK_LR = {"stage1": 1e-3, "stage2": 5e-4, "stage3": 1e-4}
MOHAWK_BATCH = {"stage1": 8, "stage2": 8, "stage3": 32}
MOHAWK_SEQ_LEN = 2048
MOHAWK_SEED = 42

LAWCAT_SEQ_LEN = 1024
LAWCAT_PHASE1_TOKENS = 50_000_000
LAWCAT_PHASE1_LR = 1e-2
LAWCAT_PHASE1_MSE_WEIGHT = 1000
LAWCAT_LORA_R = 16
LAWCAT_LORA_ALPHA = 32
LAWCAT_LORA_LR = 1e-4
LAWCAT_SEED = 0

HYBRID4_KEPT_LAYERS = list(range(14, 18))  # layers 14-17 retain attention
HYBRID4_STAGE3_TOKENS = 200_000_000

CATEGORIES = [
    "single_doc_qa", "multi_doc_qa", "long_in_context_learning",
    "long_dialogue", "code_repo", "long_structured_data"
]
RETRIEVAL_HEAVY = {"multi_doc_qa", "long_structured_data"}
GENERATION_HEAVY = {"long_in_context_learning"}

CHECKPOINT_DIR = "checkpoints"
RESULTS_DIR = "results"
FIGURES_DIR = "figures"

PPL_GATE_MAX_RELATIVE_GAP = 0.05
L2_GATE_MAX_RATIO = 0.15
STAGE1_FROBENIUS_MAX = 0.15
ABORT_ON_GATE_FAIL = True
```

---

### MOHAWK Distillation (`code/distill_mohawk.py`)

**Dependencies:** config, goombalab/mohawk, transformers, torch

```python
def run_mohawk_distillation(
    stage: int,                    # 1, 2, or 3
    teacher_path: str,
    student_checkpoint: str | None,  # None for stage 1
    output_dir: str,
    n_tokens: int,
    lr: float,
    batch_size: int,
    seed: int = MOHAWK_SEED,
) -> str: ...                      # returns checkpoint path

def check_ppl_gate(
    student_checkpoint: str,
    teacher_path: str,
    dataset: tuple[str, str],
    max_relative_gap: float = PPL_GATE_MAX_RELATIVE_GAP,
) -> tuple[bool, float, float]: ...  # (passed, student_ppl, teacher_ppl)

def check_alignment_gate(
    student_checkpoint: str,
    teacher_path: str,
    l2_threshold: float = L2_GATE_MAX_RATIO,
) -> tuple[bool, float]: ...         # (passed, ratio)

def run_full_mohawk_pipeline(output_base: str) -> str: ...  # returns stage3 checkpoint
```

---

### LAWCAT Distillation (`code/distill_lawcat.py`)

**Dependencies:** config, zeyuliu1037/LAWCAT, transformers, peft, torch

```python
def run_lawcat_phase1(
    teacher_path: str,
    output_dir: str,
    n_tokens: int = LAWCAT_PHASE1_TOKENS,
    lr: float = LAWCAT_PHASE1_LR,
    mse_weight: float = LAWCAT_PHASE1_MSE_WEIGHT,
    seed: int = LAWCAT_SEED,
) -> str: ...                    # returns phase1 checkpoint

def run_lawcat_phase2_lora(
    phase1_checkpoint: str,
    output_dir: str,
    n_tokens: int,               # remaining budget after phase1
    lora_r: int = LAWCAT_LORA_R,
    lora_alpha: int = LAWCAT_LORA_ALPHA,
    lr: float = LAWCAT_LORA_LR,
    seed: int = LAWCAT_SEED,
) -> str: ...                    # returns final checkpoint

def run_full_lawcat_pipeline(output_base: str) -> str: ...
```

---

### Hybrid-4 Distillation (`code/distill_hybrid4.py`)

**Dependencies:** config, distill_mohawk, goombalab/mohawk

```python
def build_hybrid4_model(
    mohawk_ssm_checkpoint: str,
    kept_layers: list[int] = HYBRID4_KEPT_LAYERS,  # restore attn for layers 14-17
) -> str: ...                                        # returns hybrid4 init checkpoint

def run_hybrid4_stage3(
    hybrid4_init_checkpoint: str,
    teacher_path: str,
    output_dir: str,
    n_tokens: int = HYBRID4_STAGE3_TOKENS,
) -> str: ...                                        # returns final checkpoint
```

---

### Evaluation (`code/evaluate.py`)

**Dependencies:** config, transformers, datasets (THUDM/LongBench)

```python
def evaluate_model_longbench(
    model_path: str,
    model_name: str,              # "teacher" | "mohawk" | "lawcat" | "hybrid4"
    output_json: str,
) -> dict[str, float]: ...        # {category: accuracy}

def compute_delta_norm(
    teacher_results: dict[str, float],
    student_results: dict[str, float],
) -> dict[str, float]: ...        # {category: delta_norm}

def run_all_evaluations(
    teacher_path: str,
    mohawk_ckpt: str,
    lawcat_ckpt: str,
    hybrid4_ckpt: str,
    results_dir: str,
) -> dict[str, dict[str, float]]: ...  # {model_name: {category: delta_norm}}
```

---

### Analysis (`code/analyze.py`)

**Dependencies:** config, numpy, scipy, statsmodels, evaluate outputs (JSON)

```python
def bootstrap_interaction_ratio(
    delta_norm_ssm: dict[str, float],
    delta_norm_lawcat: dict[str, float],
    longbench_predictions: dict,      # raw per-example predictions for resampling
    n_resamples: int = 10_000,
    seed: int = 42,
) -> tuple[float, float, float]: ... # (ratio, ci_low, ci_high)

def fit_mixed_effects_model(
    all_delta_norms: dict[str, dict[str, float]],  # {strategy: {category: delta_norm}}
) -> tuple[float, float]: ...         # (interaction_p_value, holm_corrected_p)

def verify_mechanism_activated(
    mohawk_checkpoint: str,
    lawcat_checkpoint: str,
    training_logs: dict,
    delta_norms: dict[str, dict[str, float]],
) -> tuple[bool, dict[str, bool]]: ...

def run_analysis(results_dir: str) -> dict: ...  # full analysis summary dict
```

---

### Visualization (`code/visualize.py`)

**Dependencies:** config, matplotlib, seaborn, analyze outputs

```python
def plot_delta_norm_bars(
    delta_norms: dict[str, dict[str, float]],  # {strategy: {category: delta_norm}}
    output_path: str,                           # figures/fig1_bar.png
) -> None: ...

def plot_delta_norm_heatmap(
    delta_norms: dict[str, dict[str, float]],
    output_path: str,                           # figures/fig2_heatmap.png
) -> None: ...

def plot_error_bars(
    delta_norms: dict[str, dict[str, float]],
    ci_data: dict,                              # from bootstrap_interaction_ratio
    output_path: str,                           # figures/fig3_errorbars.png
) -> None: ...

def plot_ratio_across_categories(
    delta_norm_ssm: dict[str, float],
    delta_norm_lawcat: dict[str, float],
    output_path: str,                           # figures/fig4_ratio.png
) -> None: ...

def generate_all_figures(
    delta_norms: dict[str, dict[str, float]],
    analysis_results: dict,
    figures_dir: str,
) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment & Repo Setup | Clone goombalab/mohawk, zeyuliu1037/LAWCAT, THUDM/LongBench; install deps; verify LLaMA-3-8B access; write config.py | 6 | 1+2+1+2 |
| A-2 | MOHAWK-SSM Distillation | Run 3-stage MOHAWK on LLaMA-3-8B (C4, ≤1B tokens, 4×A100); implement gate checks (PPL, L2); save checkpoints | 17 | 4+4+4+5 |
| A-3 | LAWCAT Distillation | Run 2-phase LAWCAT on LLaMA-3-8B (Phase 1 MSE + Phase 2 LoRA, 2×A100); adapt 1B config from 1B paper config | 15 | 4+4+4+3 |
| A-4 | Hybrid-4 + Evaluation | Build Hybrid-4 from MOHAWK-SSM checkpoint; run Stage 3; evaluate all 4 models on LongBench v2; compute Δ_norm | 13 | 3+3+4+3 |
| A-5 | Analysis & Visualization | Bootstrap CI, mixed-effects model, mechanism verification, 4 figures | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3], Medium(9-13): [A-4, A-5], Low(4-8): [A-1]

**Total budget check**: 5 Epics × avg ~3 subtasks = ~15 subtasks. Within LIGHT tier budget.
