# H-M3 Configuration: Representation Separation Analysis

**Type**: MECHANISM | No training — inference + analysis only

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (base hypothesis H-M1 present)
**Status**: Verified from actual code — `docs/youra_research/h-m1/code/config.py`
**Config Files Found**: `h-m1/code/config.py` (dataclass `M1Config`, instance `CONFIG`)
**Pattern Used**: Python dataclass with module-level `CONFIG` instance, relative output paths (`outputs/`, `../figures`)

H-M3 config reuses H-M1's `models` list and `batch_size`/`seed` fields verbatim for consistency (verified field names, not assumed).

---

## Main Configuration (Python Dataclass)

```python
"""Configuration for H-M3 representation separation analysis."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class M3Config:
    # Inherited from H-M1 (models must match for hidden-state consistency)
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.2",
    ])
    primary_model_index: int = 0
    batch_size: int = 8
    device_map: str = "auto"
    dtype: str = "float16"
    seed: int = 42

    # Extraction
    hidden_layer: int = -1       # last layer
    token_position: int = -1     # last token

    # Analysis
    cv_folds: int = 5
    tsne_perplexity: int = 30
    tsne_components: int = 2

    # Gates (from PRD success criteria)
    separation_score_pass: float = 0.1
    probe_accuracy_pass: float = 0.6
    separation_score_fail: float = 0.3
    probe_accuracy_fail: float = 0.8

    # Task counts (from H-M1 classifications)
    total_tasks: int = 2212
    type_a_count: int = 1977
    type_b_count: int = 235

    # Paths
    hm1_results_path: str = "../../h-m1/code/outputs/results.json"
    hm1_task_types_path: str = "../../h-m1/code/outputs/task_types.json"
    output_dir: str = "outputs"
    results_path: str = "outputs/results.json"
    figures_dir: str = "../figures"


CONFIG = M3Config()
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-1 | Extraction | Load models, extract last-layer/last-token hidden states for all 2212 tasks |
| C-M3-2 | Analysis | Compute separation_score (intra/inter cosine similarity) + LinearSVC 5-fold probe |
| C-M3-3 | Reporting | Gate check against thresholds, t-SNE plot, export results.json |

---

## Environment Requirements

- Python 3.9+
- torch >= 2.0
- transformers >= 4.30
- scikit-learn
- scipy
- matplotlib, seaborn
- umap-learn (optional, t-SNE via sklearn is default)
