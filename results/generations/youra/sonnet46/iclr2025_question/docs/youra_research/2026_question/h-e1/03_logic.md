# Logic: H-E1 (EXISTENCE PoC)

**Hypothesis:** DeBERTa-v3-large-mnli P(contradiction) as hallucination signal on HaluEval
**Type:** EXISTENCE PoC
**Generated:** 2026-03-16

Applied: Standard PyTorch inference_mode batch pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## ST-L1: NLIInferenceModel.predict() [A-3, Budget: 1]

### API Signatures

```python
# code/model.py
import numpy as np
from typing import List, Dict
import torch
from sentence_transformers import CrossEncoder

class NLIInferenceModel:
    def __init__(self, config: "ExperimentConfig") -> None:
        """Store config; model not loaded until load() is called."""
        self.config = config
        self.model: CrossEncoder = None
        self._contradiction_idx: int = None

    def load(self) -> None:
        """Load CrossEncoder model and verify label map."""
        ...

    def get_contradiction_index(self) -> int:
        """Return verified index of 'contradiction' class from id2label."""
        ...

    def predict(
        self,
        premises: List[str],
        hypotheses: List[str],
        batch_size: int = 32,
    ) -> np.ndarray:
        """Batch NLI inference with inference_mode and progress logging.
        Returns shape: (N, 3) — [P(contradiction), P(entailment), P(neutral)]
        """
        ...
```

### Pseudo-code

```
def predict(self, premises, hypotheses, batch_size=32):
    N = len(premises)
    logging.info(f"Running NLI inference: {N} examples, batch_size={batch_size}")
    pairs = list(zip(premises, hypotheses))

    with torch.inference_mode():
        scores = self.model.predict(
            pairs,
            batch_size=batch_size,
            apply_softmax=True,
            show_progress_bar=False,
        )   # shape: (N, 3)

    # Log first-batch shape
    logging.info(f"Inference complete. scores.shape={scores.shape}")

    # Progress already logged by CrossEncoder; also log per-1000 manually if needed:
    # for i in range(0, N, batch_size):
    #     if i % 1000 == 0: logging.info(f"Processed {i}/{N}")

    assert scores.shape == (N, 3), f"Unexpected shape: {scores.shape}"
    return scores  # np.ndarray shape: (N, 3)
```

---

## ST-L2: NLIInferenceModel.verify_label_map() [A-3, Budget: 1]

### API Signatures

```python
    def verify_label_map(self) -> Dict[int, str]:
        """Verify id2label, find contradiction index. Returns label map dict."""
        ...
```

### Pseudo-code

```
def verify_label_map(self):
    id2label = self.model.config.id2label  # e.g. {0: 'contradiction', ...}

    contradiction_idx = None
    for idx, label in id2label.items():
        if 'contradiction' in label.lower():
            contradiction_idx = idx
            break

    if contradiction_idx is None:
        logging.warning("'contradiction' not found in id2label; falling back to index 0")
        contradiction_idx = 0

    logging.info(f"Label map: {id2label}, contradiction_idx={contradiction_idx}")
    self._contradiction_idx = contradiction_idx
    return id2label
```

---

## ST-L3: delong_test() [A-4, Budget: 1]

### API Signatures

```python
# code/evaluate.py
import numpy as np
import scipy.stats

def delong_test(
    y_true: np.ndarray,   # shape: (N,) — binary labels {0, 1}
    y_score: np.ndarray,  # shape: (N,) — predicted probabilities
) -> float:
    """fastDeLong test: AUROC vs 0.5 baseline. Returns two-tailed p-value."""
    ...
```

### Pseudo-code (fastDeLong)

```
def delong_test(y_true, y_score):
    pos = y_score[y_true == 1]   # shape: (m,)
    neg = y_score[y_true == 0]   # shape: (n,)
    m, n = len(pos), len(neg)

    # Placement matrix (m, n): pos[i] vs neg[j]
    matrix = (pos[:, None] > neg[None, :]).astype(float)
    matrix += 0.5 * (pos[:, None] == neg[None, :]).astype(float)

    V10 = matrix.mean(axis=1)   # shape: (m,) — structural component for positives
    V01 = matrix.mean(axis=0)   # shape: (n,) — structural component for negatives

    auroc = matrix.mean()

    S10 = np.var(V10, ddof=1) / m
    S01 = np.var(V01, ddof=1) / n
    var_auroc = S10 + S01

    z = (auroc - 0.5) / np.sqrt(var_auroc)
    p_value = 2.0 * scipy.stats.norm.sf(abs(z))  # two-tailed
    return float(p_value)
```

---

## ST-L4: verify_mechanism_activated() [A-4, Budget: 1]

### API Signatures

```python
from sklearn.metrics import roc_auc_score
from typing import Tuple

def verify_mechanism_activated(
    scores: np.ndarray,   # shape: (N, 3)
    labels: np.ndarray,   # shape: (N,) — binary {0, 1}
    task_name: str,
) -> Tuple[bool, dict]:
    """Check 4 NLI mechanism indicators. Returns (all_pass, indicator_dict)."""
    ...
```

### Pseudo-code

```
def verify_mechanism_activated(scores, labels, task_name):
    p_contra = scores[:, 0]  # preliminary check using index 0; caller uses verified idx

    indicators = {
        "shape_correct":  scores.shape[1] == 3,
        "non_uniform":    scores.std(axis=0).mean() > 0.05,
        "above_random":   roc_auc_score(labels, p_contra) > 0.50,
        "label_verified": 0.0 < labels.mean() < 1.0,
    }
    all_pass = all(indicators.values())
    failed = [k for k, v in indicators.items() if not v]
    if failed:
        logging.warning(f"[{task_name}] Mechanism check FAILED: {failed}")
    return all_pass, indicators
```

---

## ST-L5: label_audit() [A-4, Budget: 1]

### API Signatures

```python
def label_audit(
    premises: List[str],
    hypotheses: List[str],
    labels: np.ndarray,    # shape: (N,)
    scores: np.ndarray,    # shape: (N, 3) — full softmax matrix
    seed: int = 42,
    n: int = 200,
) -> dict:
    """Stratified sample n hallucinated examples; compute structural ceiling.
    Returns: {p_contradictory, auroc_max, category_counts, n_sampled}
    """
    ...
```

### Pseudo-code

```
def label_audit(premises, hypotheses, labels, scores, seed=42, n=200):
    rng = np.random.default_rng(seed)
    hall_idx = np.where(labels == 1)[0]           # hallucinated example indices
    sample_n = min(n, len(hall_idx))
    sampled_idx = rng.choice(hall_idx, size=sample_n, replace=False)

    # Use P(contradiction) column (index already verified by caller)
    p_contra_sampled = scores[sampled_idx, 0]     # shape: (sample_n,) — adjust col as needed

    # Auto-classify: Category A = score > 0.4 (NLI detectable contradiction)
    cat_A = (p_contra_sampled > 0.4).sum()
    cat_B = (p_contra_sampled < 0.2).sum()
    cat_C = sample_n - cat_A - cat_B

    p_contradictory = cat_A / sample_n
    auroc_max = p_contradictory + 0.5 * (1 - p_contradictory)

    return {
        "p_contradictory": float(p_contradictory),
        "auroc_max":        float(auroc_max),
        "category_counts":  {"A": int(cat_A), "B": int(cat_B), "C": int(cat_C)},
        "n_sampled":        sample_n,
    }
```

---

## ST-L6: evaluate_task() [A-4, Budget: 1]

### API Signatures

```python
from dataclasses import dataclass

@dataclass
class TaskResult:
    task_name: str
    auroc: float
    delong_pvalue: float
    cohen_d: float
    auroc_max: float          # structural ceiling
    p_contradictory: float
    score_inverted: bool
    n_examples: int
    label_distribution: dict  # {0: int, 1: int}

def evaluate_task(
    task_name: str,
    scores: np.ndarray,       # shape: (N, 3)
    labels: np.ndarray,       # shape: (N,)
    premises: List[str],
    hypotheses: List[str],
    contradiction_idx: int,
    config: "ExperimentConfig",
) -> TaskResult:
    """Full per-task evaluation: AUROC, DeLong, Cohen's d, inversion, label audit."""
    ...
```

### Pseudo-code

```
def evaluate_task(task_name, scores, labels, premises, hypotheses,
                  contradiction_idx, config):
    p_contradiction = scores[:, contradiction_idx]  # shape: (N,)

    verify_mechanism_activated(scores, labels, task_name)

    auroc_raw = roc_auc_score(labels, p_contradiction)

    # Inversion check
    if auroc_raw < 0.5:
        p_final = 1.0 - p_contradiction
        score_inverted = True
        logging.warning(f"[{task_name}] Score inverted (auroc_raw={auroc_raw:.3f})")
    else:
        p_final = p_contradiction
        score_inverted = False

    auroc = roc_auc_score(labels, p_final)
    delong_pvalue = delong_test(labels, p_final)

    # Cohen's d
    hall = p_final[labels == 1]
    non_hall = p_final[labels == 0]
    pooled_std = np.sqrt((hall.var(ddof=1) + non_hall.var(ddof=1)) / 2)
    d = float((hall.mean() - non_hall.mean()) / pooled_std)

    audit = label_audit(premises, hypotheses, labels, scores,
                        seed=config.seed, n=config.label_audit_n)

    return TaskResult(
        task_name=task_name,
        auroc=float(auroc),
        delong_pvalue=float(delong_pvalue),
        cohen_d=d,
        auroc_max=audit["auroc_max"],
        p_contradictory=audit["p_contradictory"],
        score_inverted=score_inverted,
        n_examples=len(labels),
        label_distribution={0: int((labels==0).sum()), 1: int((labels==1).sum())},
    )
```

---

## ST-L7: main() orchestration [A-6, Budget: 1]

### API Signatures

```python
# code/run_experiment.py
import os
import sys
import subprocess
import logging
from typing import Dict, List

def setup_gpu() -> None:
    """Detect lowest-memory GPU; set CUDA_VISIBLE_DEVICES."""
    ...

def main() -> None:
    """End-to-end experiment: load data, infer, evaluate, save, gate check."""
    ...
```

### Pseudo-code

```
def setup_gpu():
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
        capture_output=True, text=True,
    )
    free_mem = [int(x.strip()) for x in result.stdout.strip().split('\n')]
    best_gpu = str(free_mem.index(max(free_mem)))
    os.environ['CUDA_VISIBLE_DEVICES'] = best_gpu
    logging.info(f"Using GPU {best_gpu} ({max(free_mem)} MB free)")


def main():
    logging.basicConfig(level=logging.INFO)

    # 1. GPU
    setup_gpu()

    # 2. Config
    config = get_config()

    # 3. Data
    tasks_data: List[TaskData] = load_all_tasks()   # 3 TaskData objects

    # 4. Model
    model = NLIInferenceModel(config)
    model.load()
    model.verify_label_map()
    contradiction_idx = model.get_contradiction_index()

    # 5. Inference
    scores_dict: Dict[str, np.ndarray] = {}   # task_name -> (N, 3)
    for task in tasks_data:
        scores = model.predict(task.premises, task.hypotheses,
                               batch_size=config.batch_size)
        scores_dict[task.task_name] = scores

    # 6. Evaluate
    results: List[TaskResult] = []
    for task in tasks_data:
        result = evaluate_task(
            task_name=task.task_name,
            scores=scores_dict[task.task_name],
            labels=task.labels,
            premises=task.premises,
            hypotheses=task.hypotheses,
            contradiction_idx=contradiction_idx,
            config=config,
        )
        results.append(result)

    # 7. Gate
    gate_pass, gate_msg = check_gate_condition(results, config)

    # 8. Figures
    os.makedirs(config.figures_dir, exist_ok=True)
    plot_gate_metrics(results, f"{config.figures_dir}/gate_metrics_comparison.png")
    task_arrays = [
        (r, scores_dict[r.task_name],
         next(t.labels for t in tasks_data if t.task_name == r.task_name))
        for r in results
    ]
    plot_roc_curves(task_arrays, f"{config.figures_dir}/roc_curves.png")
    plot_score_distributions(task_arrays, f"{config.figures_dir}/score_distributions.png")
    plot_structural_ceiling(results, f"{config.figures_dir}/structural_ceiling.png")

    # 9. Save
    save_results(results, scores_dict, config)

    # 10. Gate result
    print(f"[H-E1] Gate {'PASS' if gate_pass else 'FAIL'}: {gate_msg}")
    sys.exit(0 if gate_pass else 1)
```

---

## Subtasks Summary [7/7 used]

| ID | Subtask | Source | Description |
|----|---------|--------|-------------|
| L-1 | NLIInferenceModel.predict() | A-3 | Batch inference loop, inference_mode, progress logging, shape assertion |
| L-2 | NLIInferenceModel.verify_label_map() | A-3 | id2label verification, contradiction index with fallback warning |
| L-3 | delong_test() | A-4 | fastDeLong numpy: placement matrix, V10/V01, variance, Z-score vs 0.5 |
| L-4 | verify_mechanism_activated() | A-4 | 4-indicator NLI sanity check, logs failed checks |
| L-5 | label_audit() | A-4 | Stratified sample 200 hallucinated, score-threshold categorization, AUROC_max |
| L-6 | evaluate_task() | A-4 | Full per-task orchestration: inversion check, DeLong, Cohen's d, audit |
| L-7 | main() + setup_gpu() | A-6 | End-to-end wiring, GPU detection, 4 figures, JSON save, gate exit code |

---

## Tensor Shapes Summary

| Variable | Shape | Note |
|----------|-------|------|
| scores (full) | (N, 3) | model.predict output per task |
| p_contradiction | (N,) | scores[:, contradiction_idx] |
| labels | (N,) | binary int {0, 1} |
| pos / neg (DeLong) | (m,) / (n,) | split by label class |
| placement matrix | (m, n) | DeLong inner computation |
| p_contra_sampled | (sample_n,) | label_audit sampled P(contradiction) |
