---
hypothesis_id: h-c1
phase: config
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Config: H-C1 — Cross-Benchmark Four-Way AUROC Ranking (TruthfulQA)

Applied: single-script-dataclass pattern (same lineage as h-m4)
Applied: inherited-and-extended-config pattern (reuses h-m4 fields; extends to 4-method pipeline)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m4)
**Status**: Config fields verified from h-m4/code/config.py actual code
**Config Files Found**: `docs/youra_research/h-m4/code/config.py`
**Pattern Used**: dataclass (same as h-m3, h-m4 chain)

---

## Inherited Configuration (Base Hypothesis)

From `docs/youra_research/h-m4/code/config.py` (actual code, verified):

```python
# H-M4 actual fields (verified from 03_config.md which shows h-m4/code/config.py):
@dataclass
class Config:
    model_id: str = "meta-llama/Llama-2-7b-chat-hf"  # VC-only in H-M4
    max_new_tokens: int = 80
    do_sample: bool = False
    temperature: float = 1.0
    batch_size: int = 1
    seed: int = 42
    precision: str = "float16"
    n_bootstrap: int = 1000
    n_bins_ece: int = 10
    parse_rate_gate: float = 0.80
    auroc_te_baseline: float = 0.4381
    auroc_se_baseline: float = 0.286
    n_questions: int = 98
    dataset_id: str = "mandarjoshi/trivia_qa"
    dataset_config: str = "rc"
    hm2_code_dir: str = "../../h-m2/code"
    hm3_results_path: str = "../../h-m3/results.json"
    he1_code_dir: str = "../../h-e1/code"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"
    figure_dpi: int = 150
    # ... figure size and color fields
```

H-C1 inherits: `seed`, `n_bootstrap`, `hm2_code_dir`, `figures_dir`, `results_path`, `figure_dpi`, color fields
Dropped: `auroc_te_baseline`, `auroc_se_baseline` (H-M4 are comparison refs, not gates), `n_bins_ece`, `he1_code_dir`, `hm3_results_path`, `dataset_id="mandarjoshi/trivia_qa"`, `dataset_config="rc"`, `parse_rate_gate=0.80` (lowered to 0.70)
New in H-C1: `model_id_base`, `model_id_chat`, `nli_model_id`, `K`, `temperature_sample`, `temperature_greedy`, `max_new_tokens_gen`, `max_new_tokens_vc`, `n_questions=200`, `dataset_id="truthful_qa"`, `hm4_code_dir`, `hm4_results_path`, SCG/figure settings

---

## A-7: VC Computation Config [Complexity: 10, Budget: 2 subtasks]

Applied: h-m4-vc-reuse-pattern with parse_rate_gate adjustment for TruthfulQA

### C-7-1: Full Config Dataclass

```python
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class Config:
    # --- Models ---
    model_id_base: str = "meta-llama/Llama-2-7b-hf"           # SE/SCG/TE generation
    model_id_chat: str = "meta-llama/Llama-2-7b-chat-hf"      # VC elicitation
    nli_model_id: str = "cross-encoder/nli-deberta-v3-small"   # SE NLI clustering

    # --- Generation ---
    K: int = 10                        # stochastic samples for SE/SCG
    temperature_sample: float = 0.7    # for K-sample generation
    temperature_greedy: float = 0.0    # for TE logit extraction
    max_new_tokens_gen: int = 50       # for SE/SCG/TE generation
    max_new_tokens_vc: int = 80        # for VC Chat model
    do_sample_vc: bool = False         # VC always greedy

    # --- Data ---
    n_questions: int = 200
    dataset_id: str = "truthful_qa"
    dataset_config: str = "generation"
    seed: int = 42

    # --- Evaluation ---
    n_bootstrap: int = 1000
    parse_rate_gate: float = 0.70   # lowered from H-M4 0.80; TruthfulQA may be harder to parse
    batch_size: int = 8             # for 7B-hf generation; 1 for VC Chat (memory)

    # --- Paths ---
    hm2_code_dir: str = "../../h-m2/code"       # bootstrap_auroc source
    hm4_code_dir: str = "../../h-m4/code"       # VC functions source
    hm4_results_path: str = "../../h-m4/results.json"  # TriviaQA baselines
    figures_dir: str = "../figures"
    results_path: str = "../results.json"

    # --- Figure settings ---
    figure_dpi: int = 150
    fig_size_bar: Tuple[int, int] = (8, 5)         # auroc_comparison.png
    fig_size_cross: Tuple[int, int] = (9, 5)       # cross_benchmark_comparison.png
    fig_size_rank: Tuple[int, int] = (7, 4)        # rank_ordering.png
    fig_size_dist: Tuple[int, int] = (8, 4)        # vc_confidence_distribution.png
    fig_size_violin: Tuple[int, int] = (9, 5)      # bootstrap_distributions.png

    # Color palette
    color_se: str = "#55A868"
    color_scg: str = "#8172B2"
    color_te: str = "#DD8452"
    color_vc: str = "#4C72B0"

    # Output filenames
    fname_bar: str = "auroc_comparison.png"
    fname_cross: str = "cross_benchmark_comparison.png"
    fname_rank: str = "rank_ordering.png"
    fname_dist: str = "vc_confidence_distribution.png"
    fname_violin: str = "bootstrap_distributions.png"
```

### C-7-2: Full YAML Schema

```yaml
# h-c1 experiment config — all tunable parameters
# Usage: loaded by run.py, overrides Config defaults

models:
  base: "meta-llama/Llama-2-7b-hf"
  chat: "meta-llama/Llama-2-7b-chat-hf"
  nli: "cross-encoder/nli-deberta-v3-small"

generation:
  K: 10                      # stochastic samples per question (SE/SCG)
  temperature_sample: 0.7    # for K-sample generation
  temperature_greedy: 0.0    # for TE logit extraction
  max_new_tokens_gen: 50     # short answer generation
  max_new_tokens_vc: 80      # VC Chat model response
  seed: 42
  batch_size: 8              # batched across N questions for 7B-hf

data:
  n_questions: 200
  dataset_id: "truthful_qa"
  dataset_config: "generation"
  filter: "yes_no"           # filter to yes/no questions only

evaluation:
  n_bootstrap: 1000
  seed: 42

thresholds:
  parse_rate_gate: 0.70      # VC parse rate; warn if below (not abort)

paths:
  hm2_code_dir: "../../h-m2/code"
  hm4_code_dir: "../../h-m4/code"
  hm4_results_path: "../../h-m4/results.json"
  figures_dir: "../figures"
  results_path: "../results.json"

figures:
  dpi: 150
  colors:
    se: "#55A868"
    scg: "#8172B2"
    te: "#DD8452"
    vc: "#4C72B0"
  sizes:
    bar: [8, 5]
    cross: [9, 5]
    rank: [7, 4]
    dist: [8, 4]
    violin: [9, 5]
  filenames:
    bar: "auroc_comparison.png"
    cross: "cross_benchmark_comparison.png"
    rank: "rank_ordering.png"
    dist: "vc_confidence_distribution.png"
    violin: "bootstrap_distributions.png"
```

**Validation notes:**
- `parse_rate_gate: 0.70` — reduced from H-M4 (0.80); TruthfulQA adversarial questions may produce more VC parsing failures; treat as warning not abort
- `K: 10` — same as h-e2-v2 and H-M4; ensures controlled comparison
- `batch_size: 8` — for Llama-2-7B-hf (7B in float16 ≈ 14GB; batch_size=8 fits ~40GB GPU); override to 1-4 for smaller GPUs
- `do_sample_vc: False` — VC always greedy (same as H-M4; deterministic)
- `temperature_greedy: 0.0` — for TE; no effect on output but explicit

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Config dataclass | Full Config with 4-method fields; parse_rate_gate=0.70; color palette for 4 methods |
| C-7-2 | YAML schema | Full experiment YAML; all tunable params; validation notes for parse_rate and batch_size |

---

## A-2: Data Loading Config [Complexity: 9, Budget: 1 subtask]

### C-2-1: Dataset Loading Parameters

```python
# TruthfulQA yes/no subset parameters
DATASET_CONFIG = {
    "dataset_id": "truthful_qa",
    "dataset_config": "generation",  # "generation" split has yes/no questions
    "split": "validation",
    "yesno_answers": {"yes", "no"},  # filter criterion for best_answer
    "max_n": 200,
    "seed": 42,
    "tokenizer_max_length": 512,
    "prompt_template": "Q: {question}\nA:",  # for 7B-hf generation
}

# Label normalization
NORMALIZATION = {
    "strip_whitespace": True,
    "lowercase": True,
    "strip_punctuation": False,  # "yes." != "yes" — don't strip; TruthfulQA gold is clean
}
```

**Note:** TruthfulQA generation split has ~817 questions total. Yes/no subset is ~200 questions (best_answer in {"yes", "no"}). Use `max_n=200` cap with seed=42 for reproducibility if actual count differs.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Dataset config | TruthfulQA loading params; yes/no filter spec; label normalization rules |

---

## A-10: Orchestration Config [Complexity: 10, Budget: 1 subtask]

### C-10-1: Run Pipeline Configuration

```python
# Sequential model loading order to avoid OOM
PIPELINE_CONFIG = {
    "model_loading_order": ["base_7b", "nli_deberta", "chat_7b"],
    # 1. Load Llama-2-7B-hf → generate K=10 samples + greedy logits → del model
    # 2. Load DeBERTa NLI → compute SE → del model
    # 3. Compute SCG (bert-score, no GPU model needed if CPU-compatible)
    # 4. Load Llama-2-7B-Chat → compute VC → del model
    # Then: compute AUROC, figures, save results

    "delete_after_use": True,     # del model + torch.cuda.empty_cache() after each stage
    "torch_empty_cache": True,

    # Failsafe: if VC model OOM, load with load_in_8bit=True
    "vc_fallback_8bit": True,
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Pipeline config | Sequential model loading order; delete-after-use pattern; OOM fallback for VC |
