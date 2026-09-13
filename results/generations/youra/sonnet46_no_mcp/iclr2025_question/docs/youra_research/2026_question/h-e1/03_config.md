# Configuration: H-E1 Semantic Entropy UQ Comparison (EXISTENCE PoC)

**Hypothesis:** H-E1 | **Type:** EXISTENCE | **Tier:** LIGHT

Applied: Single-Config flat module layout for PoC experiments
Applied: Bootstrap CI reproducibility seeding pattern
Applied: Bonferroni correction multi-comparison pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## ExperimentConfig Dataclass

```python
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ExperimentConfig:
    # Dataset
    hf_dataset_id: str = "pminervini/HaluEval"
    dataset_split: str = "qa_samples"
    n_hallucinated: int = 1000
    n_factual: int = 1000
    seed: int = 42

    # LLM Inference
    llm_model_id: str = "meta-llama/Llama-2-7b-chat-hf"
    llm_dtype: str = "float16"
    max_new_tokens: int = 256
    greedy_temperature: float = 0.0
    stochastic_temperature: float = 1.0
    n_stochastic_samples: int = 5

    # NLI Model
    nli_model_id: str = "microsoft/deberta-large-mnli"
    nli_batch_size: int = 16

    # Evaluation
    n_bootstrap: int = 1000
    bonferroni_k: int = 3
    alpha: float = 0.05
    min_auroc_gap: float = 0.05
    min_ci_separation: float = 0.0

    # AUROC direction per method: True = higher score → more hallucinated
    auroc_higher_is_more_hallucinated: Dict[str, bool] = field(default_factory=lambda: {
        "token_entropy_mean": True,
        "semantic_entropy": True,
        "selfcheckgpt_bertscore_n5": True,
    })

    # Paths
    data_dir: str = "data"
    outputs_dir: str = "outputs"
    results_dir: str = "results"
    figures_dir: str = "figures"


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
```

---

## Equivalent YAML Schema

```yaml
# h-e1 experiment config
dataset:
  hf_dataset_id: "pminervini/HaluEval"
  dataset_split: "qa_samples"
  n_hallucinated: 1000
  n_factual: 1000
  seed: 42

llm_inference:
  llm_model_id: "meta-llama/Llama-2-7b-chat-hf"
  llm_dtype: "float16"
  max_new_tokens: 256
  greedy_temperature: 0.0
  stochastic_temperature: 1.0
  n_stochastic_samples: 5

nli_model:
  nli_model_id: "microsoft/deberta-large-mnli"
  nli_batch_size: 16

evaluation:
  n_bootstrap: 1000
  bonferroni_k: 3
  alpha: 0.05
  min_auroc_gap: 0.05
  min_ci_separation: 0.0
  auroc_higher_is_more_hallucinated:
    token_entropy_mean: true
    semantic_entropy: true
    selfcheckgpt_bertscore_n5: true

paths:
  data_dir: "data"
  outputs_dir: "outputs"
  results_dir: "results"
  figures_dir: "figures"
```

---

## Hyperparameter Rationale

| Parameter | Value | Source / Justification |
|-----------|-------|----------------------|
| `n_hallucinated` | 1000 | Stratified balance per HaluEval-QA spec (Li 2023) |
| `n_factual` | 1000 | Stratified balance per HaluEval-QA spec (Li 2023) |
| `seed` | 42 | Convention; ensures reproducible stratified split |
| `llm_model_id` | Llama-2-7b-chat-hf | Kuhn 2023 benchmark model; fits single A100 in float16 |
| `llm_dtype` | float16 | ~14GB VRAM for 7B model; A100 compatible |
| `max_new_tokens` | 256 | Sufficient for QA answers; balances speed vs. coverage |
| `greedy_temperature` | 0.0 | Deterministic decode required for token entropy logit extraction |
| `stochastic_temperature` | 1.0 | Standard sampling temperature for semantic diversity (Kuhn 2023) |
| `n_stochastic_samples` | 5 | Kuhn 2023 default; balances coverage vs. inference cost |
| `nli_model_id` | deberta-large-mnli | Best-in-class NLI for semantic clustering (Kuhn 2023) |
| `nli_batch_size` | 16 | Fits DeBERTa-large on GPU alongside LLM unloaded |
| `n_bootstrap` | 1000 | Standard CI reliability threshold (Efron & Tibshirani 1993) |
| `bonferroni_k` | 3 | Exactly 3 pairwise comparisons: (SE,TE), (SE,SCG), (TE,SCG) |
| `alpha` | 0.05 | Standard significance level; corrected to 0.0167 via Bonferroni |
| `min_auroc_gap` | 0.05 | MUST_WORK gate threshold from H-E1 hypothesis statement |
| `min_ci_separation` | 0.0 | Non-overlapping CIs required; separation > 0 triggers gate pass |

---

## Validation Rules

| Parameter | Rule |
|-----------|------|
| `n_hallucinated`, `n_factual` | > 0; sum ≤ dataset size (~10K) |
| `seed` | Any int; must be fixed before sampling |
| `llm_dtype` | Must be one of: `"float16"`, `"bfloat16"`, `"float32"` |
| `max_new_tokens` | > 0, ≤ model max context |
| `greedy_temperature` | Must be `0.0` (deterministic decode) |
| `stochastic_temperature` | > 0.0 |
| `n_stochastic_samples` | ≥ 2 (minimum for SE clustering); 5 recommended |
| `nli_batch_size` | > 0; GPU memory permitting |
| `n_bootstrap` | ≥ 100; 1000 standard |
| `bonferroni_k` | Must equal number of pairwise comparisons (3 for 3 methods) |
| `alpha` | 0 < alpha < 1; corrected alpha = alpha / bonferroni_k |
| `min_auroc_gap` | ≥ 0.0; MUST_WORK gate threshold |
| `min_ci_separation` | ≥ 0.0; 0.0 means CIs must be non-overlapping |
| `auroc_higher_is_more_hallucinated` | Dict keys must cover all active UQ method names |

---

## A-4: AUROC Evaluation [Complexity: 12, Budget: 1 subtask]

Applied: Bootstrap CI reproducibility seeding pattern

### Configuration (Subset)

```python
# Evaluation-specific fields from ExperimentConfig
n_bootstrap: int = 1000          # bootstrap resamples for 95% CI
bonferroni_k: int = 3            # exactly 3 pairwise tests
alpha: float = 0.05              # family-wise error rate; corrected = 0.05/3 ≈ 0.0167
min_auroc_gap: float = 0.05      # gate threshold: at least 1 pair must exceed
min_ci_separation: float = 0.0   # CIs must be strictly non-overlapping (gap > 0)

# AUROC direction: all three methods use higher = more hallucinated
auroc_higher_is_more_hallucinated: Dict[str, bool] = {
    "token_entropy_mean": True,          # higher entropy → more uncertain → more hallucinated
    "semantic_entropy": True,            # higher SE → more semantically diverse → more hallucinated
    "selfcheckgpt_bertscore_n5": True,   # higher inconsistency → more hallucinated
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A4-1 | AUROC Evaluation Config | Bootstrap seed control via global `seed=42`; Bonferroni k=3 validated against pairwise comparison count; gate thresholds `min_auroc_gap=0.05` and `min_ci_separation=0.0`; AUROC direction dict specifying higher=more hallucinated for all three methods (SE/TE/SCG) |

### Gate Logic (C-A4-1)

```python
# Derived at runtime from ExperimentConfig
alpha_corrected = cfg.alpha / cfg.bonferroni_k  # 0.05 / 3 ≈ 0.0167

# Gate passes if ANY pair satisfies both conditions:
# 1. delta_auroc >= min_auroc_gap (0.05)
# 2. CI lower bound of higher method > CI upper bound of lower method (non-overlapping)
gate_passed = any(
    pair["delta_auroc"] >= cfg.min_auroc_gap
    and pair["ci_lower_winner"] > pair["ci_upper_loser"] + cfg.min_ci_separation
    for pair in pairwise_results
)
```
