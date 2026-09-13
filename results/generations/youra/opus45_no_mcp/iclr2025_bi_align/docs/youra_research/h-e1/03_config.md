# Config: H-E1 (Calibration Inversion Clusters Exist Systematically)

**Type:** EXISTENCE (PoC) | **Tier:** LIGHT | **Date:** 2026-08-19

Applied: Single fixed hardcoded dict pattern (EXISTENCE — no hyperparameter sweep, no variants)
Applied: K-means + silhouette gate-check pattern (scikit-learn standard)

MCP: Archon unavailable — used standard config patterns.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - new config design
**Config Files Found**: None
**Pattern Used**: dataclass (matches architecture's `config.py` module)

---

## A-4: Clustering + silhouette gate [Complexity: 9, Budget: 9]

**Applied**: scikit-learn KMeans + silhouette_score standard pattern; single fixed threshold per EXISTENCE rules (no grid search).

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # Datasets
    datasets: list[str] = field(default_factory=lambda: ["truthfulqa", "ethics", "hhh"])

    # Models
    models: list[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-chat-hf",   # primary — drives gate check
        "meta-llama/Llama-2-13b-chat-hf",  # cross-model agreement
        "mistralai/Mistral-7B-Instruct-v0.2",  # cross-model agreement
    ])
    primary_model_index: int = 0

    # Calibration
    inversion_threshold: float = 0.1  # flags task as "calibration inverted"

    # Clustering
    k_range: list[int] = field(default_factory=lambda: [2, 3, 4, 5])
    default_k: int = 3
    silhouette_gate: float = 0.3  # PRIMARY success gate (FR-5.1)

    # Inference
    batch_size: int = 8  # NFR-2: keeps VRAM < 24GB
    device: str = "cuda"

    # Reproducibility
    seed: int = 42

    # Output
    output_dir: str = "h-e1"
    results_path: str = "h-e1/results.json"
    figures_dir: str = "h-e1/figures"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | `evaluate_k_range` | Fit KMeans for each k in `k_range`, compute silhouette_score per k |
| C-4-2 | `select_best_k` | Pick k with max silhouette score from `evaluate_k_range` output |
| C-4-3 | `cluster_and_evaluate` | Fit final KMeans(k, seed), return labels, centers, silhouette_score, `gate_passed = silhouette_score > silhouette_gate` |
| C-4-4 | Cross-model label alignment | Run clustering per model using shared `k_range`/`seed`, feed labels into agreement heatmap (FR-5.5) |
