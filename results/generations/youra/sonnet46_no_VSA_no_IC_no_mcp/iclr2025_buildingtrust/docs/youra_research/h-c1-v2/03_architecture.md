# Architecture: h-c1-v2
# RLHF Calibration Moderation — Task-Type-Conditional ΔΔECE Analysis

Applied: cache-reuse incremental extension pattern (h-c1 → h-c1-v2)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-c1/code/`
**Findings**: h-c1 has HC1Config (dataclass extending h-e1 ExperimentConfig), CellECE/ModerationResult NamedTuples, compute_ece (15-bin numpy), compare_rlhf_moderation, 4 plot functions. h-c1 extends h-e1 via sys.path injection. All interfaces verified from actual code.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| compute_ece | `from h_c1.evaluation.ece import compute_ece` | `h-c1/code/evaluation/ece.py` |
| CellECE | `from h_c1.comparison.delta_ece import CellECE` | `h-c1/code/comparison/delta_ece.py` |
| ModerationResult | `from h_c1.comparison.delta_ece import ModerationResult` | `h-c1/code/comparison/delta_ece.py` |
| compare_rlhf_moderation | `from h_c1.comparison.delta_ece import compare_rlhf_moderation` | `h-c1/code/comparison/delta_ece.py` |
| compute_moderation_rate | `from h_c1.comparison.delta_ece import compute_moderation_rate` | `h-c1/code/comparison/delta_ece.py` |
| write_json | `from h_c1.results.storage import write_json` | `h-c1/code/results/storage.py` |
| load_model / unload_model | `from h_c1.models.loader import load_model, unload_model` | `h-c1/code/models/loader.py` |

**Verified from**: `docs/youra_research/h-c1/code/` (actual implementation)

---

## File Organization

```
docs/youra_research/h-c1-v2/code/
  config.py              # HC1V2Config (extends HC1Config)
  data/
    loader.py            # load_hc1v2_datasets: loads h-c1 cache + 13B new runs
    cache_loader.py      # load_h_c1_cache: reads h-c1 result JSON files
  comparison/
    conditional_ece.py   # benchmark-type-stratified ΔΔECE + 13B pair
  visualization/
    plots.py             # 5 required figures (bar, reliability, hist, heatmap, scatter)
  run_experiment.py      # main() orchestrator
```

---

## Modules

### HC1V2Config (`config.py`)

**Dependencies**: HC1Config (h-c1)

```python
import sys, os
_HC1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-c1/code"))
if _HC1_CODE not in sys.path:
    sys.path.insert(0, _HC1_CODE)

from config import HC1Config
from dataclasses import dataclass, field
from typing import Dict, Tuple, List

@dataclass
class HC1V2Config(HC1Config):
    # Models: base 7B (cache-only), chat 7B (cache-only), chat 13B (new inference)
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
    ])

    # Eval cells split by benchmark type
    anli_cells: List[str] = field(default_factory=lambda: [
        "NLI-ANLI-R1", "NLI-ANLI-R2", "NLI-ANLI-R3"
    ])
    advglue_cells: List[str] = field(default_factory=lambda: ["NLI-AdvGLUE"])

    # Pairs: (base_model_id, chat_model_id)
    model_pairs: List[Tuple[str, str]] = field(default_factory=lambda: [
        ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-7b-chat-hf"),
        ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-13b-chat-hf"),
    ])

    # H-C1 cache path (pre-computed 7B results)
    h_c1_results_file: str = "docs/youra_research/h-c1/results/hc1_results.json"
    h_m1_label_mask_path: str = "docs/youra_research/h-m1/results/label_preservation_mask.npy"

    # Gate
    moderation_rate_threshold: float = 0.60
    ddece_threshold: float = 0.01

    # Paths
    results_dir: str = "docs/youra_research/h-c1-v2/results"
    figures_dir: str = "docs/youra_research/h-c1-v2/figures"
    results_file: str = "docs/youra_research/h-c1-v2/results/hc1v2_results.json"
    validation_report: str = "docs/youra_research/h-c1-v2/04_validation.md"
    errors_log: str = "docs/youra_research/h-c1-v2/results/errors.log"
    new_inference_output: str = "docs/youra_research/h-c1-v2/results/13b_chat"
```

---

### CacheLoader (`data/cache_loader.py`)

**Dependencies**: HC1V2Config

```python
import json, numpy as np
from typing import Dict
# CellECE imported from h-c1 path (sys.path set by config.py)
from comparison.delta_ece import CellECE

def load_h_c1_cache(results_file: str) -> Dict[str, Dict[str, CellECE]]:
    """
    Load pre-computed h-c1 CellECE objects from hc1_results.json.
    Returns: {model_id: {cell_id: CellECE}}
    Raises: FileNotFoundError if cache missing, ValueError if schema invalid.
    """
    ...

def load_label_preservation_mask(mask_path: str) -> np.ndarray:
    """Load h-m1 label-preservation mask. Returns bool array shape (N,)."""
    ...

def validate_cache_schema(data: dict) -> bool:
    """Verify cache contains 'cells' with logits, labels, split_id fields."""
    ...
```

---

### DatasetLoader (`data/loader.py`)

**Dependencies**: HC1V2Config, CacheLoader

```python
from datasets import load_dataset, Dataset
from typing import Dict

def load_hc1v2_datasets(seed: int = 1,
                         subsample_clean: int = 1000,
                         subsample_adv: int = 1000) -> Dict[str, Dataset]:
    """
    Loads HuggingFace datasets needed for 13B-chat new inference.
    7B results come from cache — this only loads raw splits for 13B.
    Returns: {split_key: Dataset}
      Keys: 'multi_nli', 'anli_r1', 'anli_r2', 'anli_r3',
            'advglue_mnli', 'mnli', 'glue_mnli'
    """
    ...
```

---

### ConditionalECE (`comparison/conditional_ece.py`)

**Dependencies**: HC1V2Config, CellECE, ModerationResult (h-c1), compute_ece (h-c1)

```python
import numpy as np
from typing import Dict, List, Tuple
from comparison.delta_ece import CellECE, ModerationResult, compare_rlhf_moderation, compute_moderation_rate

def build_cell_ece_from_cache(cache: Dict[str, Dict[str, CellECE]],
                               model_id: str, cell_id: str) -> CellECE:
    """Extract CellECE for a (model_id, cell_id) from h-c1 cache."""
    ...

def compute_moderation_by_benchmark_type(
        base_results: Dict[str, CellECE],
        chat_results: Dict[str, CellECE],
        anli_cells: List[str],
        advglue_cells: List[str],
        ddece_threshold: float = 0.01,
) -> Tuple[List[ModerationResult], List[ModerationResult], float, float]:
    """
    Separate moderation analysis by benchmark type.
    Returns: (anli_results, advglue_results, anli_moderation_rate, advglue_moderation_rate)
    """
    ...

def compute_cross_size_moderation(
        base_7b_results: Dict[str, CellECE],
        chat_13b_results: Dict[str, CellECE],
        anli_cells: List[str],
        ddece_threshold: float = 0.01,
) -> Tuple[List[ModerationResult], float]:
    """
    7B-base vs 13B-chat moderation on ANLI cells (cross-size validation).
    Returns: (moderation_results, moderation_rate)
    """
    ...

def evaluate_gate(anli_moderation_rate: float,
                  threshold: float = 0.60) -> bool:
    """Primary gate: ANLI moderation_rate >= threshold."""
    ...

def summarize_results(
        pair_7b: Tuple[List[ModerationResult], List[ModerationResult], float, float],
        pair_13b: Tuple[List[ModerationResult], float],
) -> dict:
    """Assemble full results summary dict for JSON serialization."""
    ...
```

---

### Plots (`visualization/plots.py`)

**Dependencies**: matplotlib, seaborn, numpy, ModerationResult, CellECE

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict

def fig1_ddece_bar(anli_results: List, advglue_results: List,
                   pair_label: str, out_path: str) -> None:
    """ΔΔECE per cell, color-coded green/red/gray. One call per model pair."""
    ...

def fig2_reliability_diagrams(base_results: Dict, chat_results: Dict,
                               cells: List[str], out_path: str) -> None:
    """Side-by-side reliability diagrams for specified cells (15-bin)."""
    ...

def fig3_confidence_histogram(base_results: Dict, chat_results: Dict,
                               adv_cell: str, out_path: str) -> None:
    """base vs chat confidence distribution on adversarial misclassifications."""
    ...

def fig4_moderation_heatmap(all_cell_results: Dict[str, Dict[str, "CellECE"]],
                             row_models: List[str],
                             col_cells: List[str],
                             out_path: str) -> None:
    """ΔECE heatmap: rows=models, cols=cells. Red=high, green=low/negative."""
    ...

def fig5_ddece_vs_difficulty(anli_results: List,
                              pair_label: str, out_path: str) -> None:
    """Scatter: x=ANLI round difficulty (1/2/3), y=ΔΔECE."""
    ...
```

---

### Orchestrator (`run_experiment.py`)

**Dependencies**: HC1V2Config, CacheLoader, DatasetLoader, ConditionalECE, Plots, load_model/unload_model (h-c1)

```python
import os, sys, json, traceback
from datetime import datetime

def main(config: "HC1V2Config" = None) -> bool:
    """
    Step 1: Load h-c1 cache (7B base + 7B chat, all cells)
    Step 2: Run 13B-chat new inference on ANLI R1/R2/R3 + AdvGLUE
    Step 3: Compute ΔΔECE per benchmark type (7B pair)
    Step 4: Compute ΔΔECE cross-size (13B pair, ANLI only)
    Step 5: Evaluate primary gate (ANLI moderation_rate >= 0.60)
    Step 6: Save results JSON + validation report
    Step 7: Generate 5 figures
    Returns: gate_passed bool
    """
    ...

if __name__ == "__main__":
    from config import HC1V2Config
    sys.exit(0 if main(HC1V2Config()) else 1)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | HC1V2Config, directory structure, sys.path wiring to h-c1 | 6 | 2+1+1+2 |
| A-2 | Cache Loader | load_h_c1_cache from hc1_results.json; schema validation; label mask load | 9 | 2+2+3+2 |
| A-3 | Dataset Loader | HuggingFace loads for 13B inference (ANLI R1/R2/R3, AdvGLUE, MultiNLI, GLUE MNLI) | 7 | 2+2+1+2 |
| A-4 | 13B-chat Inference | lm-eval-harness run for 13B-chat; logit extraction to CellECE format | 14 | 3+3+4+4 |
| A-5 | Conditional ΔΔECE | compute_moderation_by_benchmark_type; ANLI vs AdvGLUE separation; gate eval | 12 | 3+3+3+3 |
| A-6 | Cross-size Validation | compute_cross_size_moderation for 7B-base vs 13B-chat on ANLI | 9 | 2+3+2+2 |
| A-7 | Visualization | 5 figures: bar, reliability, histogram, heatmap, scatter | 13 | 3+2+4+4 |
| A-8 | Orchestrator | run_experiment.py main(); result JSON; validation report | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-5, A-7, A-8, A-2, A-6], Low(4-8): [A-1, A-3]

---

## Data Flow

- h-c1 cache → CacheLoader → `{model_id: {cell_id: CellECE}}` (7B base + 7B chat, all 4 cells)
- HuggingFace → DatasetLoader → raw datasets → 13B-chat inference → CellECE (4 cells)
- All CellECE → ConditionalECE → ModerationResult per benchmark type → gate evaluation
- ModerationResult + CellECE → Plots → 5 PNG figures
