# Logic Specification: H-M4

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (SSI is a novel metric, no prior code)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: SSI Computation & Evaluation Pipeline [Complexity: MEDIUM, Budget: full]

**Applied**: Standard PyTorch/numpy inverse-variance metric + sklearn/scipy eval (KB unavailable, using roadmap spec)

### API Signatures

```python
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import pearsonr

def compute_ssi(confidence_scores: np.ndarray, epsilon: float = 1e-8) -> float:
    """SSI = 1/(var+eps) for one item. confidence_scores: [K] -> scalar"""
    ...

def compute_ssi_batch(confidence_matrix: np.ndarray, epsilon: float = 1e-8) -> np.ndarray:
    """confidence_matrix: [N, K] -> ssi: [N]"""
    ...

def extract_confidence_matrix(
    model,
    tokenizer,
    items: list[dict],          # MMLU items with paraphrases
    paraphrases: dict[str, list[str]],  # item_id -> K paraphrase strings
    device: str = "cuda",
    batch_size: int = 16,
) -> np.ndarray:
    """Run inference, extract softmax prob of correct option. -> [N, K]"""
    ...

def evaluate_ssi_discrimination(
    ssi_clean: np.ndarray,          # [N] SSI at 0% contamination
    ssi_contaminated: np.ndarray,   # [N] SSI at 50% contamination
    contamination_levels: np.ndarray,  # [5] e.g. [0,5,10,20,50]
    mean_ssi_per_level: np.ndarray,    # [5]
) -> dict:
    """Returns {auc, pearson_r, p_value, cohens_d, primary_pass, secondary_pass}"""
    ...

def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Pooled-variance effect size between two 1D arrays."""
    ...

def generate_visualizations(
    results: dict,
    ssi_by_level: dict[int, np.ndarray],  # {contamination_pct: ssi_array}
    out_dir: str,
) -> list[str]:
    """Saves 4 figures to out_dir, returns saved file paths."""
    ...
```

### Tensor / Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| confidence_matrix | [N=14042, K=20] | per model checkpoint |
| ssi_values | [N] | one per item |
| ssi_by_level | dict of 5 x [N] | keyed by contamination % |
| y_true / y_scores (AUC) | [2N] | clean(0) vs contaminated(1) labels/scores |
| contamination_levels, mean_ssi_per_level | [5], [5] | for pearsonr |

### Pseudo-code: Main Experiment Loop

```
levels = [0, 5, 10, 20, 50]
confidence_by_level = {}   # level -> [N, K]
ssi_by_level = {}          # level -> [N]

for level in levels:
    model, tokenizer = load_checkpoint(f"mistral-7b-mmlu-{level}pct")
    conf_matrix = extract_confidence_matrix(model, tokenizer, mmlu_items, paraphrases)
    confidence_by_level[level] = conf_matrix
    ssi_by_level[level] = compute_ssi_batch(conf_matrix)
    free_gpu(model)

mean_ssi_per_level = np.array([ssi_by_level[l].mean() for l in levels])

results = evaluate_ssi_discrimination(
    ssi_clean=ssi_by_level[0],
    ssi_contaminated=ssi_by_level[50],
    contamination_levels=np.array(levels),
    mean_ssi_per_level=mean_ssi_per_level,
)
results["cohens_d"] = cohens_d(ssi_by_level[50], ssi_by_level[0])
results["gate"] = "PASS" if results["primary_pass"] and results["secondary_pass"] \
                  else "PARTIAL" if results["primary_pass"] else "FAIL"

generate_visualizations(results, ssi_by_level, out_dir="figures/")
save_json(results, "results.json")
```

### Error Handling

| Case | Handling |
|------|----------|
| variance == 0 (identical confidences) | epsilon=1e-8 in denominator prevents div-by-zero |
| Missing/NaN confidence score | drop item from that level's matrix row, log warning, exclude from N |
| Checkpoint file not found | raise `FileNotFoundError` with checkpoint path, abort level, skip to next |
| K mismatch across items (ragged paraphrase counts) | pad/truncate to K=20 or raise `ValueError` if <K available |
| GPU OOM during batch inference | catch `torch.cuda.OutOfMemoryError`, halve `batch_size`, retry once, else raise |
| pearsonr on constant array | catch `ValueError`, set r=nan, p=nan, log warning |
| Empty ssi_clean/ssi_contaminated | raise `ValueError` before AUC call |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | SSI core fns | `compute_ssi`, `compute_ssi_batch` |
| L-1-2 | Confidence extraction | Load checkpoints, run paraphrase inference -> confidence matrix |
| L-1-3 | Evaluation | AUC, pearsonr, Cohen's d, gate logic |
| L-1-4 | Visualization | 4 required figures saved to `figures/` |
