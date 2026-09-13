# Config: H-M1

**Type:** MECHANISM (full analysis, not PoC) — sparsity thresholds are the gate, no hyperparameter tuning needed.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (matches architecture doc; no base hypothesis code to reuse)
**Config Files Found**: None
**Pattern Used**: dataclass

**Applied**: Standard PyTorch/HuggingFace experiment-config defaults (no matching KB pattern found via Archon search).

---

## A-1/A-2: Data + Model Config

```python
@dataclass
class ExperimentConfig:
    # Data
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    split: str = "validation"       # 872 samples
    max_length: int = 128
    batch_size: int = 1             # per-sample attention extraction

    # Models
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"
    num_layers: int = 12
    num_heads: int = 12

    # Sparsity
    zero_threshold: float = 1e-6    # near-zero attention weight cutoff
    causal_threshold: float = 0.99  # >99% upper-triangle zeros => is_causal

    # Gate thresholds (from PRD Sec 9)
    bert_gate_max: float = 0.10     # BERT upper_triangle_sparsity must be <
    gpt2_gate_min: float = 0.99     # GPT-2 upper_triangle_sparsity must be >

    # Repro
    seed: int = 42
    device: str = "cuda"            # falls back to "cpu" if unavailable

    # Output paths
    output_dir: str = "code"
    results_path: str = "code/results.json"
    report_path: str = "code/report.md"
    figures_dir: str = "figures"
```

### Subtasks [2/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Config dataclass | Define `ExperimentConfig` above in `config.py` |
| C-2 | Path setup | Ensure `figures/` and `code/` dirs exist on run start |

---

## A-7/A-8: Gate + Visualization Config

```python
GATE_CONFIG = {
    "bert_max_sparsity": 0.10,
    "gpt2_min_sparsity": 0.99,
}

FIGURE_FILES = {
    "gate_comparison": "figures/gate_comparison.png",
    "attention_heatmaps": "figures/attention_heatmaps.png",
    "layerwise_sparsity": "figures/layerwise_sparsity.png",
    "entropy_histogram": "figures/entropy_histogram.png",
}
```

### Subtasks [2/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3 | Gate dict | `GATE_CONFIG` used by `verify.py` to pass/fail |
| C-4 | Figure paths dict | `FIGURE_FILES` used by `visualize.py` output targets |

---

## Total Subtasks: 4/4 used
