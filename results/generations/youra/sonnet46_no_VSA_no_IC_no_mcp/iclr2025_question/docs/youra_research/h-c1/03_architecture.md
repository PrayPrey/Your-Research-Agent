---
hypothesis_id: h-c1
phase: architecture
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Architecture: H-C1 — Cross-Benchmark Four-Way AUROC Ranking (TruthfulQA)

Applied: single-script-four-method-inference pattern (SE+SCG+TE+VC full pipeline, TruthfulQA dataset)
Applied: sequential-model-loading pattern (7B-hf first, then 7B-Chat; avoids dual-model OOM)
Applied: h-m4-code-reuse pattern (VC module reused verbatim; SE/SCG/TE from h-e2-v2 lineage)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m4 and h-e2-v2 lineage)
**Status**: Base code analyzed from h-m4/code/ and h-e2-v2 codebase descriptions
**Analyzed Paths**:
- `docs/youra_research/h-m4/code/`: config.py, vc.py, evaluate.py, visualize.py, run.py (5 files)
- h-e2-v2 codebase: generate_samples.py → compute_uncertainties.py → evaluate_auroc.py (SE/SCG/TE pipeline)
**Findings**:
- h-m4 code handles VC elicitation; h-m4/vc.py is fully reusable (same model, same prompt, same regex)
- h-m4/evaluate.py provides bootstrap_auroc reuse pattern via sys.path injection from h-m2
- h-e2-v2 handles SE (DeBERTa NLI clustering) + SCG (BERTScore) + TE (greedy logits)
- H-C1 merges both pipelines into a unified four-method runner on TruthfulQA
- Key difference from H-M4: must generate K=10 samples (for SE/SCG/TE); H-M4 was VC-only

---

## File Organization

```
docs/youra_research/h-c1/code/
  config.py       # Config dataclass — TruthfulQA N=200, all 4 methods
  data.py         # load_truthfulqa_yesno(), compute_em_label()
  generate.py     # generate_samples(): K=10 stochastic + greedy for 7B-hf
  uncertainty.py  # compute_te(), compute_se(), compute_scg(), import VC from h-m4
  evaluate.py     # bootstrap_auroc (4 methods), gate logic, cross-benchmark dict
  visualize.py    # 5 figures -> ../figures/
  run.py          # orchestration: data -> generate -> uncertainty -> evaluate -> viz -> save
docs/youra_research/h-c1/
  figures/        # auroc_comparison.png, cross_benchmark_comparison.png,
                  #   rank_ordering.png, vc_confidence_distribution.png,
                  #   bootstrap_distributions.png
  results.json
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| extract_confidence | `sys.path.insert(0, "../../h-m4/code"); from vc import extract_confidence, build_vc_prompt` | `h-m4/code/vc.py` |
| bootstrap_auroc | `sys.path.insert(0, "../../h-m2/code"); from evaluate import bootstrap_auroc` | `h-m2/code/evaluate.py` |
| H-M4 baselines | `json.load(open("../../h-m4/results.json"))` → `auroc_te`, `auroc_se`, `auroc_vc` | `h-m4/results.json` |

**Verified from**: `docs/youra_research/h-m4/code/` (actual implementation structure)
**Note**: h-m4/vc.py `extract_confidence()` and `build_vc_prompt()` reused verbatim (same model, same task format).

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Generation
    model_id_base: str = "meta-llama/Llama-2-7b-hf"
    model_id_chat: str = "meta-llama/Llama-2-7b-chat-hf"
    nli_model_id: str = "cross-encoder/nli-deberta-v3-small"
    K: int = 10
    temperature_sample: float = 0.7
    temperature_greedy: float = 0.0
    max_new_tokens_gen: int = 50
    max_new_tokens_vc: int = 80
    seed: int = 42

    # Dataset
    n_questions: int = 200
    dataset_id: str = "truthful_qa"
    dataset_config: str = "generation"

    # Evaluation
    n_bootstrap: int = 1000
    parse_rate_gate: float = 0.70
    batch_size: int = 8

    # Paths
    hm2_code_dir: str = "../../h-m2/code"
    hm4_code_dir: str = "../../h-m4/code"
    hm4_results_path: str = "../../h-m4/results.json"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"

    # Figure settings
    figure_dpi: int = 150
    color_se: str = "#55A868"
    color_scg: str = "#8172B2"
    color_te: str = "#DD8452"
    color_vc: str = "#4C72B0"
```

---

### Data (`code/data.py`)

**Dependencies**: datasets, random

```python
def load_truthfulqa_yesno(seed=42, max_n=200) -> tuple[list[str], list[str]]:
    """Returns (questions, gold_answers) for TruthfulQA yes/no subset."""
    ...

def compute_em_labels(generated_answers: list[str], gold_answers: list[str]) -> list[int]:
    """Binary EM: 1 if normalized generated == normalized gold."""
    ...
```

---

### Generate (`code/generate.py`)

**Dependencies**: transformers, torch, Config

```python
def load_base_model(cfg: Config) -> tuple:
    """Load Llama-2-7B-hf in float16, device_map=auto. Returns (model, tokenizer)."""
    ...

def generate_k_samples(
    questions: list[str],
    model,
    tokenizer,
    K: int,
    temperature: float,
    seed: int,
) -> list[list[str]]:
    """Returns [N x K] stochastic samples for SE/SCG computation."""
    ...

def generate_greedy_with_logits(
    questions: list[str],
    model,
    tokenizer,
) -> tuple[list[str], list[list[float]]]:
    """Returns (greedy_answers, per_token_logprobs) for TE computation."""
    ...
```

---

### Uncertainty (`code/uncertainty.py`)

**Dependencies**: transformers, bert_score, numpy, Config; imports from h-m4

```python
def compute_te(per_token_logprobs: list[list[float]]) -> list[float]:
    """Mean per-token Shannon entropy from greedy logprobs. Returns [N] TE scores."""
    ...

def compute_se(
    samples: list[list[str]],
    nli_model_id: str,
) -> list[float]:
    """DeBERTa NLI clustering + cluster entropy. Returns [N] SE scores (higher=more uncertain)."""
    ...

def compute_scg(samples: list[list[str]]) -> list[float]:
    """BERTScore pairwise consistency. Returns [N] SCG scores = 1 - mean_pairwise_score."""
    ...

def compute_vc(
    questions: list[str],
    cfg: Config,
) -> tuple[list[float], int]:
    """
    Loads Llama-2-7B-Chat, reuses h-m4 build_vc_prompt + extract_confidence.
    Returns (vc_uncertainty_scores [N], fallback_count).
    """
    ...
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: sklearn, numpy, Config; imports bootstrap_auroc from h-m2

```python
def load_bootstrap_auroc(hm2_code_dir: str): ...

def load_hm4_baselines(hm4_results_path: str) -> dict:
    """Returns dict: auroc_se, auroc_te, auroc_vc, n from H-M4."""
    ...

def compute_all_aurocs(
    se_scores: list[float],
    scg_scores: list[float],
    te_scores: list[float],
    vc_scores: list[float],
    em_labels: list[int],
    cfg: Config,
) -> dict:
    """
    Bootstrap AUROC for all 4 methods.
    Returns dict with: auroc_*, ci_*, gate_primary, gate_secondary,
    gate_tertiary, gate_passed, ranking.
    """
    ...

def evaluate_gate(auroc_se: float, auroc_scg: float, auroc_te: float, auroc_vc: float) -> dict:
    """
    Gate evaluation:
    - primary: SE > TE
    - secondary: VC < TE
    - tertiary: SE >= SCG > TE > VC
    Returns dict of gate results.
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
def plot_auroc_comparison(results: dict, out_path: str) -> None:
    """Bar chart: SE, SCG, TE, VC AUROC on TruthfulQA with 95% CI error bars."""
    ...

def plot_cross_benchmark(results_hc1: dict, hm4_baselines: dict, out_path: str) -> None:
    """Grouped bar: TriviaQA (H-M4) vs TruthfulQA (H-C1) for SE, TE, VC (+ SCG if available)."""
    ...

def plot_rank_ordering(results: dict, out_path: str) -> None:
    """Point plot: method ranking with CI overlap bands. Sorted by AUROC descending."""
    ...

def plot_vc_confidence_distribution(vc_confidences_hc1: list, hm4_baselines: dict, out_path: str) -> None:
    """Overlay histograms: VC confidence distribution TruthfulQA vs TriviaQA."""
    ...

def plot_bootstrap_distributions(bootstrap_samples: dict, out_path: str) -> None:
    """Violin plot of 1000 bootstrap AUROC samples per method."""
    ...

def generate_all_figures(results: dict, hm4_baselines: dict, bootstrap_samples: dict, figures_dir: str) -> None:
    """Generate all 5 figures."""
    ...
```

---

### Run (`code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """
    1. load_truthfulqa_yesno() -> questions, gold_answers
    2. load_base_model() -> model_7b, tokenizer
    3. generate_k_samples(questions) -> samples [N x K]
    4. generate_greedy_with_logits(questions) -> greedy_answers, logprobs
    5. compute_em_labels(greedy_answers, gold_answers) -> em_labels [N]
    6. compute_te(logprobs) -> te_scores [N]
    7. compute_se(samples) -> se_scores [N]
    8. compute_scg(samples) -> scg_scores [N]
    9. del model_7b (free VRAM before loading Chat model)
    10. compute_vc(questions, cfg) -> vc_scores [N], fallback_count
    11. compute_all_aurocs(se, scg, te, vc, em_labels) -> results dict
    12. load_hm4_baselines() -> hm4_baselines
    13. generate_all_figures(results, hm4_baselines, bootstrap_samples, figures_dir)
    14. save results.json
    15. print gate verdict
    """
    ...
```

---

## Data Flow

```
TruthfulQA HuggingFace (auto-download)
  |
  v
load_truthfulqa_yesno() -> questions [200], gold_answers [200]
  |
  v
load_base_model() -> Llama-2-7B-hf (float16, CUDA)
  |
  +-> generate_k_samples() -> samples [200 x 10]
  +-> generate_greedy_with_logits() -> greedy_answers [200], logprobs [200 x T]
  |
  v
compute_em_labels(greedy_answers, gold_answers) -> em_labels [200]
  |
  +-> compute_te(logprobs) -> te_scores [200]
  +-> compute_se(samples) -> se_scores [200]
  +-> compute_scg(samples) -> scg_scores [200]
  |
del model_7b   # free VRAM
  |
  v
compute_vc(questions, cfg) -> vc_scores [200], fallback_count
  |
  v
compute_all_aurocs(se, scg, te, vc, em_labels) -> results dict
  |
  +-> generate_all_figures() -> figures/*.png (5 figures)
  +-> save_results() -> results.json
  +-> print gate verdict
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| A-1 | Project setup | File structure, config.py, figures/ dir, verify external paths to h-m2/h-m4 | config.py | 5 | 1+1+1+2 |
| A-2 | Data loading | data.py: load_truthfulqa_yesno(), compute_em_labels(); HF datasets integration; yes/no filtering | data.py | 9 | 2+3+2+2 |
| A-3 | Llama-2-7B generation | generate.py: load_base_model(), generate_k_samples() [K=10, temp=0.7], generate_greedy_with_logits() | generate.py | 14 | 3+4+4+3 |
| A-4 | TE computation | uncertainty.py: compute_te() from greedy logprobs; mean per-token Shannon entropy | uncertainty.py | 8 | 2+2+2+2 |
| A-5 | SE computation | uncertainty.py: compute_se() with DeBERTa NLI clustering; cluster entropy; NLI model loading | uncertainty.py | 14 | 3+3+4+4 |
| A-6 | SCG computation | uncertainty.py: compute_scg() via BERTScore pairwise; bert-score library integration | uncertainty.py | 10 | 2+3+3+2 |
| A-7 | VC computation | uncertainty.py: compute_vc() reusing h-m4 build_vc_prompt + extract_confidence; Chat model loading | uncertainty.py | 10 | 2+3+3+2 |
| A-8 | AUROC evaluation | evaluate.py: compute_all_aurocs() (4 methods), evaluate_gate(), load_hm4_baselines() | evaluate.py | 12 | 2+3+4+3 |
| A-9 | Visualization | visualize.py: 5 figures (AUROC bar, cross-benchmark, rank ordering, VC dist, bootstrap violin) | visualize.py | 14 | 3+3+4+4 |
| A-10 | Orchestration + results | run.py main(): sequential pipeline, sequential model loading (7B then Chat), results.json | run.py | 10 | 2+3+3+2 |
| A-11 | Smoke test | Verify run completes, results.json valid, all 5 figures exist, gate verdict printed, N>=200 | run.py | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-5, A-9], Medium(9-13): [A-2, A-6, A-7, A-8, A-10], Low(4-8): [A-1, A-4, A-11]
