---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
date: "2026-08-25"
author: Anonymous
---

# Architecture: H-E1 — ECE Measurement Pipeline

Applied: Guo-2017-ECE-equal-width-binning
Applied: lm-evaluation-harness-MC-logit-extraction

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No existing modules or patterns to reuse.

---

## File Structure

```
docs/youra_research/h-e1/code/
├── config.py
├── run_experiment.py
├── requirements.txt
├── data/
│   ├── loader.py
│   └── formatter.py
├── models/
│   └── loader.py
├── evaluation/
│   ├── logit_extractor.py
│   ├── ece.py
│   └── validator.py
├── results/
│   └── storage.py
└── visualization/
    └── plots.py
```

---

## Module Interfaces

### Config (`config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    seed: int = 1
    batch_size: int = 8
    n_bins_primary: int = 15
    n_bins_secondary: int = 10
    min_examples_per_cell: int = 200
    subsample_clean: int = 500
    prevalidation_n: int = 10
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.1",
    ])
    use_4bit_threshold_gb: float = 40.0
```

---

### DataLoader (`data/loader.py`)

**Dependencies**: config.py

```python
from datasets import Dataset
from typing import Dict

def load_all_datasets(seed: int = 1) -> Dict[str, Dataset]:
    """Load all 9 HF splits. Returns dict keyed by split name.
    Keys: advglue_qqp, advglue_sst2, advglue_mnli,
          anli_r1, anli_r2, anli_r3,
          glue_qqp, glue_sst2, mnli
    GLUE/MultiNLI subsampled to 500 examples using seed."""
    ...

def save_manifest(datasets: Dict[str, Dataset], out_path: str) -> None: ...
```

---

### Formatter (`data/formatter.py`)

**Dependencies**: None

```python
CHAT_MODELS = {
    "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama/Llama-2-13b-chat-hf",
    "mistralai/Mistral-7B-Instruct-v0.1",
}

def format_mc_prompt(example: dict, task: str, model_id: str) -> tuple[str, list[str]]:
    """Returns (context_str, answer_choices_list).
    Applies chat template for chat/instruct models; raw format for base."""
    ...
```

---

### ModelLoader (`models/loader.py`)

**Dependencies**: config.py

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model(model_id: str, use_4bit: bool = False) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """bfloat16; 4-bit BitsAndBytes if use_4bit. device_map='auto'."""
    ...

def unload_model(model: AutoModelForCausalLM) -> None:
    """del model + torch.cuda.empty_cache()"""
    ...

def get_checkpoint_hash(model_id: str) -> str: ...

def check_vram_gb() -> float: ...
```

---

### LogitExtractor (`evaluation/logit_extractor.py`)

**Dependencies**: models/loader.py, data/formatter.py

```python
import numpy as np
from typing import NamedTuple

class CellResult(NamedTuple):
    confidences: np.ndarray   # max softmax prob per example
    pred_labels: np.ndarray
    true_labels: np.ndarray
    prob_sums: np.ndarray     # softmax sum per example (should be ~1.0)

def extract_cell(
    model, tokenizer, dataset, task: str, model_id: str,
    batch_size: int = 8,
) -> CellResult:
    """Extract logits for all examples in one (model, task, split) cell."""
    ...

def extract_answer_token_ids(tokenizer, choices: list[str]) -> list[int]:
    """Single-token extraction; first-token fallback with warning for multi-token."""
    ...
```

---

### ECE (`evaluation/ece.py`)

**Dependencies**: None

```python
import numpy as np

def compute_ece(confidences: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float:
    """Guo 2017 equal-width ECE: sum_b |B_b|/n * |acc(B_b) - conf(B_b)|"""
    ...

def compute_both(confidences: np.ndarray, correct: np.ndarray) -> tuple[float, float]:
    """Returns (ece_15, ece_10)."""
    ...
```

---

### Validator (`evaluation/validator.py`)

**Dependencies**: evaluation/ece.py

```python
from typing import NamedTuple
import numpy as np
from evaluation.logit_extractor import CellResult

class ValidationResult(NamedTuple):
    passed: bool
    indicators: dict  # keys: coverage_met, non_degenerate, non_uniform, ece_plausible, probs_sum_to_one

def verify_logit_extraction(cell_result: CellResult, ece_15: float) -> ValidationResult:
    """FR-4.3: all 5 indicator checks."""
    ...

def prevalidate_cell(model, tokenizer, dataset, task: str, model_id: str, n: int = 10) -> ValidationResult:
    """Run on n examples before full cell evaluation (Risk R1 mitigation)."""
    ...

def check_clean_sanity(ece_clean_by_model: dict) -> tuple[bool, dict]:
    """FR-4.4: passes if >=2/4 models have clean ECE in [0.05, 0.15]."""
    ...
```

---

### Storage (`results/storage.py`)

**Dependencies**: None

```python
import pandas as pd
from typing import Any

def append_cell_row(path: str, row: dict) -> None:
    """Append one row to ece_results.csv.
    Columns: model, task, split, n_examples, ece_15, ece_10, accuracy, mean_confidence, cell_passed"""
    ...

def write_cell_jsonl(path: str, records: list[dict]) -> None:
    """Per-example JSONL: {confidence, pred_label, true_label, correct}"""
    ...

def write_gate_result(path: str, passed_cells: int, failed_cells: list, clean_sanity: bool) -> None: ...

def write_json(path: str, data: Any) -> None: ...
```

---

### Plots (`visualization/plots.py`)

**Dependencies**: results/storage.py

```python
import pandas as pd

def fig1_ece_comparison(df: pd.DataFrame, out_path: str) -> None:
    """2x2 subplot: grouped bars clean vs adversarial ECE per model x task."""
    ...

def fig2_reliability_diagrams(example_jsonl_paths: list[str], out_path: str) -> None:
    """12-panel reliability diagrams (4 models x 3 tasks), clean+adv overlaid."""
    ...

def fig3_coverage_heatmap(df: pd.DataFrame, out_path: str) -> None:
    """4x6 grid: example count per (model, split) cell."""
    ...

def fig4_confidence_boxplots(example_jsonl_paths: list[str], out_path: str) -> None:
    """Max-softmax confidence distribution boxplots per cell."""
    ...

def fig5_ece_sensitivity(df: pd.DataFrame, out_path: str) -> None:
    """Scatter: ECE_10 vs ECE_15 across all 24 cells."""
    ...
```

---

### Orchestrator (`run_experiment.py`)

**Dependencies**: All modules

```python
from config import ExperimentConfig

def main(config: ExperimentConfig) -> None:
    """
    Sequential loop — for each model_id:
      1. check_vram_gb() → decide use_4bit
      2. load_model()
      3. for each (task, split):
         a. prevalidate_cell() → skip cell + log if fails
         b. extract_cell()
         c. verify_logit_extraction() + compute_both()
         d. append_cell_row() + write_cell_jsonl()
      4. unload_model()
    check_clean_sanity() → write_gate_result()
    generate all 5 figures
    """
    ...

if __name__ == "__main__":
    main(ExperimentConfig())
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | loader.py + formatter.py: load 9 HF splits, subsample with seed, format MC prompts per model type | 10 | 3+2+2+3 |
| A-2 | Model Management | models/loader.py: load/unload 4 LLMs, VRAM check, 4-bit fallback, checkpoint hash recording | 11 | 2+2+4+3 |
| A-3 | Logit Extraction | logit_extractor.py: answer-token logit extraction, softmax, CellResult, token-ID resolution | 14 | 3+3+4+4 |
| A-4 | ECE + Validation | ece.py + validator.py: Guo 2017 ECE (15+10 bin), verify_logit_extraction, prevalidate, clean sanity | 13 | 3+2+5+3 |
| A-5 | Orchestration + Storage | run_experiment.py + storage.py: sequential pipeline, graceful cell failure, all results output | 12 | 2+3+3+4 |
| A-6 | Visualization | plots.py: all 5 required figures | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-1, A-2, A-4, A-5, A-6], Low(4-8): []
