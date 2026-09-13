# Architecture: H-E1 Semantic Entropy UQ Comparison (EXISTENCE PoC)

**Hypothesis:** H-E1 | **Type:** EXISTENCE | **Tier:** LIGHT

Applied: Inference-Pipeline-Then-Evaluate pattern (Kuhn 2023 semantic_uncertainty)
Applied: Checkpoint-Resume pattern for long-running GPU inference
Applied: Single-Config flat module layout for PoC experiments

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior hypothesis codebase. All modules built fresh per EXISTENCE PoC rules.

---

## File Structure

```
h-e1/code/
├── config.py            # Single fixed experiment config
├── data.py              # Dataset loading & preprocessing
├── inference.py         # LLM greedy + stochastic inference
├── uq_signals.py        # Token entropy, semantic entropy, SelfCheckGPT
├── evaluate.py          # AUROC + bootstrap CI + statistical testing
├── visualize.py         # Bar chart + ROC curves
├── run_experiment.py    # Orchestration entrypoint
├── requirements.txt
data/
└── halueval_qa_2k.json  # Persisted stratified sample
outputs/
├── greedy_responses.jsonl
├── greedy_logits/
│   └── example_{id}.pt
├── stochastic_samples.jsonl
└── uq_scores/
    ├── token_entropy_mean.json
    ├── semantic_entropy.json
    └── selfcheckgpt_bertscore_n5.json
results/
├── h_e1_results.json
└── h_e1_gate_check.json
figures/
├── auroc_bar_chart.png
└── roc_curves_overlay.png
```

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Dataset
    hf_dataset_id: str = "pminervini/HaluEval"
    dataset_split: str = "qa_samples"
    n_hallucinated: int = 1000
    n_factual: int = 1000
    seed: int = 42

    # LLM
    llm_model_id: str = "meta-llama/Llama-2-7b-chat-hf"
    llm_dtype: str = "float16"
    max_new_tokens: int = 256
    greedy_temperature: float = 0.0
    stochastic_temperature: float = 1.0
    n_stochastic_samples: int = 5

    # NLI
    nli_model_id: str = "microsoft/deberta-large-mnli"
    nli_batch_size: int = 16

    # Evaluation
    n_bootstrap: int = 1000
    bonferroni_k: int = 3
    alpha: float = 0.05
    min_auroc_gap: float = 0.05

    # Paths
    data_dir: str = "data"
    outputs_dir: str = "outputs"
    results_dir: str = "results"
    figures_dir: str = "figures"

def get_config() -> ExperimentConfig: ...
```

---

### DataModule (`code/data.py`)

**Dependencies**: Config

```python
from typing import List, Dict, Any
from config import ExperimentConfig

def load_halueval_qa(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load and stratified-sample 2K HaluEval-QA examples.
    Returns list of dicts: {question, answer, hallucination_label}.
    Saves to data/halueval_qa_2k.json for reproducibility."""
    ...

def save_dataset(examples: List[Dict[str, Any]], path: str) -> None: ...

def load_dataset_from_disk(path: str) -> List[Dict[str, Any]]: ...
```

---

### InferencePipeline (`code/inference.py`)

**Dependencies**: Config, DataModule

```python
from typing import List, Dict, Any, Optional
import torch
from config import ExperimentConfig

def load_llm(cfg: ExperimentConfig) -> tuple:
    """Returns (model, tokenizer) loaded in cfg.llm_dtype on CUDA."""
    ...

def run_greedy_inference(
    examples: List[Dict[str, Any]],
    model,
    tokenizer,
    cfg: ExperimentConfig,
    resume: bool = True,
) -> None:
    """Per-example: saves greedy response text + logit tensor.
    Outputs: outputs/greedy_responses.jsonl, outputs/greedy_logits/example_{id}.pt
    Supports checkpoint resume (skips already-saved examples)."""
    ...

def run_stochastic_inference(
    examples: List[Dict[str, Any]],
    model,
    tokenizer,
    cfg: ExperimentConfig,
    resume: bool = True,
) -> None:
    """Per-example: saves N=5 stochastic sample strings.
    Output: outputs/stochastic_samples.jsonl"""
    ...

def load_greedy_outputs(outputs_dir: str) -> Dict[int, Dict[str, Any]]: ...

def load_stochastic_outputs(outputs_dir: str) -> Dict[int, List[str]]: ...
```

---

### UQSignals (`code/uq_signals.py`)

**Dependencies**: Config, InferencePipeline (output files)

```python
from typing import List, Dict
import torch
from config import ExperimentConfig

def compute_token_entropy_mean(logits: torch.Tensor) -> float:
    """Mean Shannon entropy over generated token distribution.
    logits: (seq_len, vocab_size)"""
    ...

def compute_all_token_entropy(
    outputs_dir: str, cfg: ExperimentConfig
) -> Dict[int, float]:
    """Loads greedy logits, computes token_entropy_mean per example.
    Saves to outputs/uq_scores/token_entropy_mean.json"""
    ...

def load_nli_pipeline(cfg: ExperimentConfig):
    """Returns HuggingFace pipeline for deberta-large-mnli."""
    ...

def cluster_by_nli(
    samples: List[str], nli_pipeline, batch_size: int = 16
) -> Dict[int, int]:
    """Bidirectional NLI entailment clustering (Kuhn 2023).
    Returns {sample_idx: cluster_id}."""
    ...

def compute_semantic_entropy(samples: List[str], nli_pipeline, batch_size: int = 16) -> float:
    """Shannon entropy over NLI-cluster frequency distribution."""
    ...

def compute_all_semantic_entropy(
    outputs_dir: str, cfg: ExperimentConfig
) -> Dict[int, float]:
    """Loads stochastic samples, computes semantic_entropy per example.
    Saves to outputs/uq_scores/semantic_entropy.json"""
    ...

def compute_selfcheckgpt_bertscore(
    greedy_response: str, stochastic_samples: List[str]
) -> float:
    """Runs SelfCheckBERTScore(rescale_with_baseline=True).
    Returns mean per-sentence inconsistency score."""
    ...

def compute_all_selfcheckgpt(
    outputs_dir: str, cfg: ExperimentConfig
) -> Dict[int, float]:
    """Loads greedy + stochastic outputs, computes selfcheckgpt_bertscore_n5.
    Saves to outputs/uq_scores/selfcheckgpt_bertscore_n5.json"""
    ...
```

---

### Evaluator (`code/evaluate.py`)

**Dependencies**: Config

```python
from typing import Dict, Tuple, List
import numpy as np
from config import ExperimentConfig

def compute_auroc(
    labels: np.ndarray, scores: np.ndarray
) -> float: ...

def bootstrap_auroc_ci(
    labels: np.ndarray, scores: np.ndarray, n_resamples: int = 1000, seed: int = 42
) -> Tuple[float, float]:
    """Returns (ci_lower, ci_upper) at 95% level."""
    ...

def pairwise_auroc_differences(
    auroc_map: Dict[str, float],
    ci_map: Dict[str, Tuple[float, float]],
) -> List[Dict]:
    """Returns all 3 pairs with delta_auroc and CI overlap flag."""
    ...

def check_must_work_gate(
    pairwise_results: List[Dict], cfg: ExperimentConfig
) -> Dict:
    """Returns gate_passed bool + which pairs triggered the gate."""
    ...

def save_results(
    auroc_map: Dict[str, float],
    ci_map: Dict[str, Tuple[float, float]],
    pairwise_results: List[Dict],
    gate_result: Dict,
    results_dir: str,
) -> None: ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: Config

```python
from typing import Dict, Tuple, List
import numpy as np
from config import ExperimentConfig

def plot_auroc_bar_chart(
    auroc_map: Dict[str, float],
    ci_map: Dict[str, Tuple[float, float]],
    save_path: str,
) -> None:
    """Bar chart with 95% CI error bars, color-coded by method."""
    ...

def plot_roc_curves_overlay(
    labels: np.ndarray,
    scores_map: Dict[str, np.ndarray],
    auroc_map: Dict[str, float],
    save_path: str,
) -> None:
    """ROC curves for all 3 methods on single plot with AUC annotations."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: Config, DataModule, InferencePipeline, UQSignals, Evaluator, Visualizer

```python
from config import get_config

def main() -> None:
    """End-to-end orchestration:
    1. Load/sample dataset
    2. Greedy inference (resume-safe)
    3. Stochastic inference (resume-safe)
    4. Compute UQ signals (token entropy, semantic entropy, selfcheckgpt)
    5. AUROC + bootstrap CI evaluation
    6. Statistical testing + MUST_WORK gate
    7. Save results JSON
    8. Generate figures
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Setup | Load HaluEval-QA, stratified 2K sample, save to disk | 6 | 2+1+1+2 |
| A-2 | LLM Inference | Greedy + stochastic (N=5) passes with checkpoint-resume, logit saving | 14 | 3+3+4+4 |
| A-3 | UQ Signal Computation | token_entropy_mean + semantic_entropy (NLI clustering) + selfcheckgpt_bertscore | 17 | 4+4+5+4 |
| A-4 | AUROC Evaluation | AUROC per method, 1K bootstrap CIs, pairwise testing, Bonferroni, gate check | 12 | 3+2+4+3 |
| A-5 | Results + Visualization | JSON persistence, bar chart, ROC overlay, figures/ output | 7 | 2+1+2+2 |
| A-6 | Orchestration & Tests | run_experiment.py entrypoint, per-module test methods (3+ each) | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3], Medium(9-13): [A-4], Low(4-8): [A-1, A-5, A-6]

---

## Module Dependency Order

- `config.py` (no deps)
- `data.py` → config
- `inference.py` → config, data
- `uq_signals.py` → config (reads output files from inference)
- `evaluate.py` → config
- `visualize.py` → config
- `run_experiment.py` → all modules

---

## External Package APIs (Key Constraints)

| Package | Class/Function | Notes |
|---------|---------------|-------|
| `selfcheckgpt` | `SelfCheckBERTScore(rescale_with_baseline=True).predict(sentences, sampled_passages)` | pip install selfcheckgpt |
| `transformers` | `pipeline("text-classification", model="microsoft/deberta-large-mnli")` | NLI for SE clustering |
| `sklearn.metrics` | `roc_auc_score(y_true, y_score)` | AUROC per method |
| `datasets` | `load_dataset("pminervini/HaluEval", "qa_samples")` | HaluEval-QA |
