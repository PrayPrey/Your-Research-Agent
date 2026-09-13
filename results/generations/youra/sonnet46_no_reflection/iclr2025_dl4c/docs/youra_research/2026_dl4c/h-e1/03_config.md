# Configuration: H-E1 — Execution-RL vs DPO Structural Efficiency (EXISTENCE PoC)

**Version:** 1.0
**Date:** 2026-05-19
**Hypothesis Type:** EXISTENCE

Applied: Standard dataclass config pattern (single fixed config, no grid search)
Applied: TRL GRPOConfig/DPOConfig defaults for LLM fine-tuning

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — new config design, no existing codebase
**Config Files Found:** None — new config
**Pattern Used:** dataclass

---

## Full ExperimentConfig

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    seed: int = 42
    dtype: str = "bfloat16"

    # Training — GRPO
    grpo_lr: float = 1e-6
    grpo_batch_size: int = 4
    grpo_grad_accum: int = 4
    grpo_num_generations: int = 8
    grpo_beta: float = 0.04
    grpo_steps: int = 1000
    grpo_save_steps: int = 100

    # Training — DPO
    dpo_lr: float = 5e-7
    dpo_batch_size: int = 2
    dpo_grad_accum: int = 8
    dpo_beta: float = 0.1
    dpo_steps: int = 1000
    dpo_save_steps: int = 100

    # Data
    training_dataset: str = "sahil2801/CodeAlpaca-20k"
    kl_prompt_count: int = 100
    dpo_min_pairs: int = 1000

    # Evaluation
    kl_tolerance: float = 0.05
    bootstrap_samples: int = 10000
    bootstrap_ci: float = 0.95
    gate_magnitude: float = 0.20

    # Paths
    output_dir: str = "h-e1/outputs"
    figures_dir: str = "h-e1/figures"
    checkpoint_dir: str = "h-e1/checkpoints"
```

---

## Hyperparameter Justification Table

| Field | Default | Source | Valid Range | Sensitivity |
|-------|---------|--------|-------------|-------------|
| `model_id` | deepseek-coder-7b-instruct-v1.5 | Phase 2B spec | — | Fixed |
| `seed` | 42 | Convention | any int | Low |
| `dtype` | bfloat16 | A100/H100 optimal | float16/bfloat16 | Low |
| `grpo_lr` | 1e-6 | DeepSeekMath paper, conservative RL LR | 1e-7 – 5e-6 | High |
| `grpo_batch_size` | 4 | Single-GPU memory constraint (7B model) | 1–8 | Medium |
| `grpo_grad_accum` | 4 | Effective batch = 16; RL stability | 1–16 | Medium |
| `grpo_num_generations` | 8 | TRL GRPO default; variance-reward tradeoff | 4–16 | High |
| `grpo_beta` | 0.04 | DeepSeekMath GRPO setting | 0.01–0.1 | High |
| `grpo_steps` | 1000 | EXISTENCE PoC: enough to observe KL effect | 500–2000 | Medium |
| `grpo_save_steps` | 100 | 10 checkpoints for KL matching | — | Low |
| `dpo_lr` | 5e-7 | TRL DPO docs; lower than SFT LR | 1e-7 – 2e-6 | High |
| `dpo_batch_size` | 2 | Paired samples; 7B memory constraint | 1–4 | Medium |
| `dpo_grad_accum` | 8 | Effective batch = 16; matches GRPO effective | 1–16 | Medium |
| `dpo_beta` | 0.1 | Original DPO paper (Rafailov et al. 2023) | 0.05–0.5 | High |
| `dpo_steps` | 1000 | Matched to grpo_steps for fair comparison | 500–2000 | Medium |
| `dpo_save_steps` | 100 | KL checkpoint matching | — | Low |
| `training_dataset` | CodeAlpaca-20k | Phase 2B spec; code domain | — | Fixed |
| `kl_prompt_count` | 100 | Sufficient for stable KL estimate | 50–500 | Medium |
| `dpo_min_pairs` | 1000 | Minimum for DPO convergence | 500–5000 | Medium |
| `kl_tolerance` | 0.05 | 5% KL window for checkpoint matching; tight but achievable | 0.01–0.1 | Critical |
| `bootstrap_samples` | 10000 | Standard bootstrap CI stability | 1000–100000 | Low |
| `bootstrap_ci` | 0.95 | Standard 95% CI | 0.9–0.99 | Low |
| `gate_magnitude` | 0.20 | Phase 2B spec; 20% relative improvement threshold | — | Fixed |
| `output_dir` | h-e1/outputs | Phase 2B spec | — | Fixed |
| `figures_dir` | h-e1/figures | Phase 2B spec | — | Fixed |
| `checkpoint_dir` | h-e1/checkpoints | Phase 2B spec | — | Fixed |

---

## YAML Schema

```yaml
experiment:
  model:
    model_id: "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    seed: 42
    dtype: "bfloat16"

  training:
    grpo:
      lr: 1.0e-6
      batch_size: 4
      grad_accum: 4
      num_generations: 8
      beta: 0.04
      steps: 1000
      save_steps: 100

    dpo:
      lr: 5.0e-7
      batch_size: 2
      grad_accum: 8
      beta: 0.1
      steps: 1000
      save_steps: 100

  data:
    training_dataset: "sahil2801/CodeAlpaca-20k"
    kl_prompt_count: 100
    dpo_min_pairs: 1000

  evaluation:
    kl_tolerance: 0.05
    bootstrap_samples: 10000
    bootstrap_ci: 0.95
    gate_magnitude: 0.20

  paths:
    output_dir: "h-e1/outputs"
    figures_dir: "h-e1/figures"
    checkpoint_dir: "h-e1/checkpoints"
```

---

## TRL GRPOConfig Mapping

```python
from trl import GRPOConfig

def make_grpo_config(cfg: ExperimentConfig) -> GRPOConfig:
    return GRPOConfig(
        output_dir=cfg.checkpoint_dir + "/grpo",
        learning_rate=cfg.grpo_lr,
        per_device_train_batch_size=cfg.grpo_batch_size,
        gradient_accumulation_steps=cfg.grpo_grad_accum,
        num_generations=cfg.grpo_num_generations,
        beta=cfg.grpo_beta,
        max_steps=cfg.grpo_steps,
        save_steps=cfg.grpo_save_steps,
        seed=cfg.seed,
        bf16=(cfg.dtype == "bfloat16"),
        fp16=(cfg.dtype == "float16"),
        dataloader_num_workers=0,
        remove_unused_columns=False,
        log_completions=True,
    )
```

---

## TRL DPOConfig Mapping

```python
from trl import DPOConfig

def make_dpo_config(cfg: ExperimentConfig) -> DPOConfig:
    return DPOConfig(
        output_dir=cfg.checkpoint_dir + "/dpo",
        learning_rate=cfg.dpo_lr,
        per_device_train_batch_size=cfg.dpo_batch_size,
        gradient_accumulation_steps=cfg.dpo_grad_accum,
        beta=cfg.dpo_beta,
        max_steps=cfg.dpo_steps,
        save_steps=cfg.dpo_save_steps,
        seed=cfg.seed,
        bf16=(cfg.dtype == "bfloat16"),
        fp16=(cfg.dtype == "float16"),
        dataloader_num_workers=0,
        remove_unused_columns=False,
    )
```

---

## Hyperparameter Sensitivity Analysis

For EXISTENCE PoC, the priority order for correctness:

1. **`kl_tolerance` (0.05)** — Critical. Controls fairness of KL-matched checkpoint comparison. Too tight (< 0.01) → no valid pairs found. Too loose (> 0.1) → unfair comparison. 0.05 is the primary gate.

2. **`grpo_beta` / `dpo_beta`** — High. Controls KL penalty strength. Mismatched betas produce incomparable regularization regimes. grpo_beta=0.04 (DeepSeekMath) and dpo_beta=0.1 (original DPO paper) are domain-standard.

3. **`grpo_num_generations` (8)** — High. Fewer generations increase reward variance; more increase memory. 8 is standard TRL default for 7B models.

4. **`grpo_lr` / `dpo_lr`** — High. Both set conservatively below typical SFT rates to avoid catastrophic forgetting during short PoC run.

5. **`grpo_steps` / `dpo_steps` (1000)** — Medium. Sufficient for KL curves to diverge meaningfully. Not enough for full convergence (intentional for PoC).

6. **`kl_prompt_count` (100)** — Medium. More prompts = more stable KL estimate but slower evaluation. 100 is sufficient for PoC signal detection.

---

## Environment Setup

```bash
# GPU selection (always use single GPU with lowest memory usage)
nvidia-smi
export CUDA_VISIBLE_DEVICES=0   # set to empty GPU id

# Python environment
export HF_HOME=/tmp/hf_cache
export TOKENIZERS_PARALLELISM=false
export WANDB_DISABLED=true       # disable for PoC unless logging needed

# Run experiment
cd h-e1/code
python run_experiment.py
```

---

## requirements.txt

```
torch==2.3.0
transformers==4.44.0
trl==0.9.6
datasets==2.20.0
accelerate==0.31.0
peft==0.11.1
bitsandbytes==0.43.1
evalplus==0.3.1
scipy==1.13.1
numpy==1.26.4
matplotlib==3.9.0
seaborn==0.13.2
pandas==2.2.2
tqdm==4.66.4
```

---

## Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig dataclass | Write `h-e1/code/config.py` with the dataclass above |
| C-1-2 | TRL config factories | Add `make_grpo_config` and `make_dpo_config` helper functions to `config.py` |
