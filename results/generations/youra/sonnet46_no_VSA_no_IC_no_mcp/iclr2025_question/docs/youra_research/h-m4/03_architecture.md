---
hypothesis_id: h-m4
phase: architecture
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Architecture: H-M4 — Verbalized Confidence (VC) Uncertainty Estimation

Applied: single-script-inference-with-cached-baselines pattern (VC-only inference, h-m3 baselines reused)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m3)
**Status**: h-m3 code found and analyzed at h-m3/code/ — 5 files: config.py, scg.py, evaluate.py, visualize.py, run.py
**Analyzed Path**: `docs/youra_research/h-m3/code/`
**Findings**: h-m3 uses sys.path injection to reuse bootstrap_auroc from h-m2/code/evaluate.py and load_h_e2v2_samples from h-e1/code/data.py. h-m4 mirrors same pattern — vc.py replaces scg.py, evaluate.py updated for VC gate logic.

---

## File Organization

```
docs/youra_research/h-m4/code/
  config.py     # fixed config dataclass
  vc.py         # Llama-2-7B-Chat VC inference + mechanism verification
  evaluate.py   # bootstrap AUROC, gate logic (VC < TE, VC < SE)
  visualize.py  # 5 figures -> ../figures/
  run.py        # orchestration: load -> infer -> evaluate -> visualize -> save
docs/youra_research/h-m4/
  figures/      # auroc_comparison.png, confidence_histogram.png,
                #   roc_curves.png, reliability_diagram.png, scatter_vc_em.png
  results.json
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_h_e2v2_samples | `sys.path.insert(0, "../../h-e1/code"); from data import load_h_e2v2_samples` | `h-e1/code/data.py` |
| bootstrap_auroc | `sys.path.insert(0, "../../h-m2/code"); from evaluate import bootstrap_auroc` | `h-m2/code/evaluate.py` |
| h-m3 results | `json.load(open("../../h-m3/results.json"))` → `auroc_te`, `auroc_se`, `em_labels` | `h-m3/results.json` |

**Verified from**: `docs/youra_research/h-m3/code/` (actual implementation)

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class Config:
    model_id: str = "meta-llama/Llama-2-7b-chat-hf"
    max_new_tokens: int = 80
    seed: int = 42
    n_bootstrap: int = 1000
    n_questions: int = 98
    parse_rate_gate: float = 0.80
    auroc_te_baseline: float = 0.4381   # inherited from h-m3
    auroc_se_baseline: float = 0.286    # inherited from h-m3
    hm2_code_dir: str = "../../h-m2/code"
    hm3_results_path: str = "../../h-m3/results.json"
    he1_code_dir: str = "../../h-e1/code"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"
```

---

### VC (`code/vc.py`)

**Dependencies**: Config, transformers, torch, re

```python
import re, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SYSTEM_PROMPT = "You are a helpful and honest assistant."

def load_vc_model(cfg: "Config") -> tuple:
    """Returns (model, tokenizer) for Llama-2-7B-Chat in float16."""
    ...

def build_vc_prompt(question: str) -> str:
    """Llama-2-Chat [INST]...[/INST] format requesting Answer + Confidence."""
    ...

def extract_confidence(response: str) -> tuple[float, bool]:
    """
    Regex extraction of confidence percentage.
    Returns (confidence_0_1, parsed: bool). Fallback: (0.5, False).
    """
    ...

def compute_vc_uncertainty(question: str, model, tokenizer, device: str) -> tuple[float, bool]:
    """
    Single greedy forward pass. Returns (uncertainty=1-confidence, parsed).
    """
    ...

def run_vc_inference(
    questions: list[str],
    model,
    tokenizer,
    device: str,
) -> tuple[list[float], int]:
    """
    Iterates all questions. Returns (vc_uncertainties, fallback_count).
    Logs per-question: 'Parsed confidence: X.XX for question N'.
    """
    ...

def verify_vc_mechanism(
    vc_uncertainties: list[float],
    fallback_count: int,
    n_questions: int,
    auroc_vc: float,
    cfg: "Config",
) -> tuple[bool, dict]:
    """
    Checks: parse_rate_ok (>=0.80), not_all_same (distinct scores>5),
    auroc_computed. Returns (activated, indicators).
    """
    ...
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: Config, numpy, sklearn; imports bootstrap_auroc from h-m2

```python
def load_bootstrap_auroc(hm2_code_dir: str): ...

def load_hm3_baselines(hm3_results_path: str) -> tuple[float, float, dict]:
    """
    Returns (auroc_te, auroc_se, em_labels) from h-m3/results.json.
    Falls back to cfg constants if key missing.
    """
    ...

def compute_vc_auroc(
    vc_uncertainties: list[float],
    em_labels: dict,
    cfg: "Config",
) -> dict:
    """
    Returns dict: auroc_vc, ci_vc, auroc_te, auroc_se,
    gate_vc_lt_te, gate_vc_lt_se, ece.
    """
    ...

def compute_ece(
    confidences: list[float],
    em_labels: dict,
    n_bins: int = 10,
) -> float:
    """Expected Calibration Error."""
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy, sklearn

```python
def plot_auroc_comparison(results: dict, out_path: str) -> None:
    """Bar chart: VC vs TE vs SE AUROC with 95% CI error bars."""
    ...

def plot_confidence_histogram(vc_confidences: list[float], out_path: str) -> None:
    """Histogram of raw 0-100% confidence scores; flags degeneracy."""
    ...

def plot_roc_curves(
    vc_uncertainties: list[float],
    se_scores: dict,
    te_scores: dict,
    em_labels: dict,
    out_path: str,
) -> None:
    """ROC curves for VC, TE, SE overlaid."""
    ...

def plot_reliability_diagram(
    vc_confidences: list[float],
    em_labels: dict,
    out_path: str,
) -> None:
    """ECE reliability diagram: mean confidence vs accuracy per bin."""
    ...

def plot_scatter_vc_em(
    vc_confidences: list[float],
    em_labels: dict,
    out_path: str,
) -> None:
    """Scatter: VC confidence vs EM correctness for 98 questions."""
    ...

def generate_all_figures(
    vc_uncertainties: list[float],
    vc_confidences: list[float],
    se_scores: dict,
    te_scores: dict,
    em_labels: dict,
    results: dict,
    figures_dir: str,
) -> None: ...
```

---

### Run (`code/run.py`)

**Dependencies**: all modules above

```python
import sys, os, json
from config import Config
from vc import load_vc_model, run_vc_inference, verify_vc_mechanism
from evaluate import load_bootstrap_auroc, load_hm3_baselines, compute_vc_auroc
from visualize import generate_all_figures

def load_artifacts(cfg: Config) -> tuple:
    """
    Loads em_labels from h-m3/results.json.
    Optionally loads se_scores, te_scores for ROC visualization.
    Returns (questions: list[str], em_labels: dict, se_scores: dict, te_scores: dict).
    """
    ...

def save_results(results: dict, path: str) -> None: ...

def main() -> None:
    """
    1. load_artifacts -> questions, em_labels, se_scores, te_scores
    2. load_vc_model -> model, tokenizer
    3. run_vc_inference -> vc_uncertainties, fallback_count
    4. compute_vc_auroc -> results dict
    5. verify_vc_mechanism -> activated, indicators
    6. generate_all_figures -> figures/
    7. save_results -> results.json
    8. print gate verdict: VC AUROC < TE AUROC?
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Data Flow

```
h-m3/results.json -> em_labels, te_scores, se_scores
  |
  v
questions (98) from h-e1/code/data.py or h-m3 results
  |
  v
load_vc_model() -> Llama-2-7B-Chat (float16, CUDA)
  |
  v
run_vc_inference(questions) -> vc_uncertainties [98], fallback_count
  |
  v
verify_vc_mechanism() -> activated, indicators
  |
  v
compute_vc_auroc(vc_uncertainties, em_labels) -> results dict
  |
  +-> generate_all_figures() -> figures/*.png (5 figures)
  +-> save_results() -> results.json
  +-> print gate verdict
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| A-1 | Project setup | File structure, config.py, figures/ dir, verify external paths to h-m2/h-m3 | config.py | 5 | 1+1+1+2 |
| A-2 | Artifact loading | load_artifacts(): load em_labels + se/te scores from h-m3/results.json; load 98 questions | run.py | 8 | 2+3+1+2 |
| A-3 | VC model loading | load_vc_model(): AutoModelForCausalLM Llama-2-7B-Chat, float16, device_map=auto | vc.py | 7 | 2+2+1+2 |
| A-4 | VC inference | build_vc_prompt(), extract_confidence(), run_vc_inference(): 98-question loop with logging | vc.py | 12 | 3+2+4+3 |
| A-5 | Mechanism verification | verify_vc_mechanism(): parse_rate, distinct-scores, degenerate detection | vc.py | 8 | 2+2+2+2 |
| A-6 | AUROC evaluation | evaluate.py: load_bootstrap_auroc from h-m2, compute_vc_auroc, compute_ece, gate logic | evaluate.py | 10 | 2+3+3+2 |
| A-7 | Visualization | 5 figures: bar AUROC, confidence histogram, ROC curves, reliability diagram, scatter | visualize.py | 12 | 3+2+4+3 |
| A-8 | Orchestration + results | run.py main(), save_results() to results.json, gate verdict print | run.py | 8 | 2+2+2+2 |
| A-9 | Smoke test | Verify run completes, results.json valid, all 5 figures exist, gate verdict printed | run.py | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-6, A-7], Low(4-8): [A-1, A-2, A-3, A-5, A-8, A-9]
