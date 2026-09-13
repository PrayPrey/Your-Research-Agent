# Config: H-E1 Conditional Independence of SE_N5 and min_logprob

**Version:** 1.0
**Date:** 2026-08-02
**Hypothesis:** H-E1 (EXISTENCE / MUST_WORK)

Applied: Standard dataclass pattern (green-field project — no base hypothesis to verify)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design, no prior config files to analyze
**Config Files Found**: None — `code/config.py` to be created
**Pattern Used**: dataclass

---

## 1. ExperimentConfig Dataclass

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Dataset
    dataset_id: str = "mandarjoshi/trivia_qa"
    dataset_config: str = "rc.nocontext"
    dataset_split: str = "validation"
    n_prompts: int = 2500
    seed: int = 42

    # Generator (Llama)
    llm_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    n_samples: int = 5
    temperature: float = 0.7
    top_p: float = 0.95
    max_new_tokens: int = 50

    # NLI (for SE clustering)
    nli_id: str = "cross-encoder/nli-deberta-v3-small"
    nli_batch_size: int = 32
    strict_entailment: bool = False  # non-strict: equivalent if no contradiction AND not both neutral

    # LM Judge
    judge_id: str = "Qwen/Qwen2.5-7B-Instruct"
    judge_batch_size: int = 16

    # Statistical thresholds — MUST NOT CHANGE (gate spec)
    pearson_r_threshold: float = 0.7
    partial_r2_threshold: float = 0.02
    circularity_threshold: float = 0.4
    abandon_threshold: float = 0.85

    # Paths
    checkpoint_path: str = "docs/youra_research/h-e1/results/signals.pkl"
    results_path: str = "docs/youra_research/h-e1/results/stats.json"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    code_dir: str = "docs/youra_research/h-e1/code"


# Module-level constants (for direct import in code/config.py)
CONFIG = ExperimentConfig()

DATASET_ID = CONFIG.dataset_id
DATASET_CONFIG = CONFIG.dataset_config
DATASET_SPLIT = CONFIG.dataset_split
N_PROMPTS = CONFIG.n_prompts
SEED = CONFIG.seed

LLM_ID = CONFIG.llm_id
N_SAMPLES = CONFIG.n_samples
TEMPERATURE = CONFIG.temperature
TOP_P = CONFIG.top_p
MAX_NEW_TOKENS = CONFIG.max_new_tokens

NLI_ID = CONFIG.nli_id
NLI_BATCH_SIZE = CONFIG.nli_batch_size
STRICT_ENTAILMENT = CONFIG.strict_entailment

JUDGE_ID = CONFIG.judge_id
JUDGE_BATCH_SIZE = CONFIG.judge_batch_size

PEARSON_R_THRESHOLD = CONFIG.pearson_r_threshold
PARTIAL_R2_THRESHOLD = CONFIG.partial_r2_threshold
CIRCULARITY_THRESHOLD = CONFIG.circularity_threshold
ABANDON_THRESHOLD = CONFIG.abandon_threshold

CHECKPOINT_PATH = CONFIG.checkpoint_path
RESULTS_PATH = CONFIG.results_path
FIGURES_DIR = CONFIG.figures_dir
```

---

## 2. YAML Config Schema

```yaml
# h-e1-config.yaml
# Override defaults by passing --config h-e1-config.yaml to main.py

dataset:
  id: mandarjoshi/trivia_qa
  config: rc.nocontext
  split: validation
  n_prompts: 2500
  seed: 42

generator:
  llm_id: meta-llama/Llama-3.1-8B-Instruct
  n_samples: 5
  temperature: 0.7
  top_p: 0.95
  max_new_tokens: 50

nli:
  nli_id: cross-encoder/nli-deberta-v3-small
  nli_batch_size: 32
  strict_entailment: false

judge:
  judge_id: Qwen/Qwen2.5-7B-Instruct
  judge_batch_size: 16

thresholds:
  pearson_r_threshold: 0.7
  partial_r2_threshold: 0.02
  circularity_threshold: 0.4
  abandon_threshold: 0.85

paths:
  checkpoint_path: docs/youra_research/h-e1/results/signals.pkl
  results_path: docs/youra_research/h-e1/results/stats.json
  figures_dir: docs/youra_research/h-e1/figures
  code_dir: docs/youra_research/h-e1/code
```

---

## 3. E4: LM-Judge Config Subtask [Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E4-1 | Judge prompt + model loading config | Prompt template, model dtype/device config, batch inference config |

### Judge Prompt Template

```python
JUDGE_PROMPT: str = (
    "Is the following answer correct for the question? Answer YES or NO.\n"
    "Question: {question}\nAnswer: {answer}\nCorrect?"
)
```

### Model Loading Config

```python
JUDGE_LOAD_KWARGS = {
    "torch_dtype": "bfloat16",   # matches generator dtype
    "device_map": "auto",
}
```

### Fallback Alias Matching

Primary: parse first token of judge output for "YES" or "NO" (case-insensitive).
Fallback (when judge output is ambiguous): exact string match of `greedy_answer.strip().lower()` against any entry in `aliases_list` (lowercased). Returns 1 on any match, 0 otherwise.

### Batching Config

```python
JUDGE_BATCH_SIZE: int = 16  # reduce to 8 on <24GB VRAM
```

### Assertion

```python
assert JUDGE_ID.split("/")[0] != LLM_ID.split("/")[0], \
    "Judge must differ from generator model family"
# Qwen vs meta-llama: passes
```

---

## 4. Results JSON Schema

File: `docs/youra_research/h-e1/results/stats.json`

```json
{
  "pearson_r": "<float> Pearson correlation between SE_N5 and min_logprob",
  "pearson_p": "<float> Two-sided p-value for Pearson r",
  "spearman_rho": "<float> Spearman rho between SE_N5 and LM-judge correctness (circularity check)",
  "spearman_p": "<float> Two-sided p-value for Spearman rho",
  "partial_r2_se": "<float> McFadden partial R² of SE in full vs reduced LR model",
  "lrt_chi2": "<float> Likelihood ratio test chi² statistic",
  "lrt_p": "<float> LRT p-value (threshold: < 0.05 for significance)",
  "gate_pass": "<bool> True if |pearson_r| < 0.7 AND partial_r2_se >= 0.02",
  "decision": "<str> One of: PASS | EXPLORE_N10 | ABANDON",
  "n_samples": "<int> Number of prompts evaluated (expect 2500)",
  "se_variance": "<float> np.var(se_scores) — must be > 0.01",
  "min_logprob_mean": "<float> np.mean(min_logprob_scores) — must be < 0"
}
```

Decision logic:
- `PASS`: `|pearson_r| < 0.7 AND partial_r2_se >= 0.02`
- `ABANDON`: `|pearson_r| > 0.85`
- `EXPLORE_N10`: all other cases (borderline correlation or low partial R²)

---

## 5. Hyperparameter Rationale Table

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_prompts` | 2500 | Sufficient power for Pearson/LR tests; matches prior TriviaQA eval conventions |
| `n_samples` | 5 | SE_N5: minimal sample count for cluster entropy estimation (jlko/semantic_uncertainty default) |
| `temperature` | 0.7 | Standard stochastic diversity for SE; matches semantic_uncertainty reference runs |
| `top_p` | 0.95 | Nucleus sampling default; pairs with temperature=0.7 |
| `max_new_tokens` | 50 | TriviaQA answers are short; 50 tokens prevents truncation while limiting compute |
| `nli_id` | cross-encoder/nli-deberta-v3-small | Lightweight; runs on CPU; matches jlko/semantic_uncertainty lightweight config |
| `strict_entailment` | False | Non-strict mode: equivalent if no contradiction AND not both neutral (per reference impl) |
| `nli_batch_size` | 32 | Fits cross-encoder in CPU RAM; tune up for GPU |
| `judge_id` | Qwen/Qwen2.5-7B-Instruct | Cross-family judge (Qwen vs Llama); 7B fits on same GPU after offloading Llama |
| `judge_batch_size` | 16 | Balanced throughput for 7B on 24GB VRAM |
| `pearson_r_threshold` | 0.7 | Phase 2B gate spec — non-negotiable |
| `partial_r2_threshold` | 0.02 | Phase 2B gate spec — non-negotiable |
| `circularity_threshold` | 0.4 | Phase 2C spec — guards against SE being a proxy for correctness |
| `abandon_threshold` | 0.85 | Phase 2B gate spec — signals SE is reparameterization of log-prob |
| `seed` | 42 | Single seed (EXISTENCE PoC); fixed for reproducibility |
