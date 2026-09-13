# H-M2 Logic: Annotator Conflation Analysis

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from actual H-M1 code (not spec)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**: `task_classifier.compute_bidir_features`, `task_classifier.USER_BELIEF_MARKERS/CONTEXT_MARKERS/HEDGE_MARKERS`, `outputs/results.json` schema

**Critical finding**: `results.json` per-task records do NOT include a `features` dict. Fields present: `task_id`, `task_type` ("A"/"B"), and per-model confidence keys `confidence_Llama_2_7b_chat`, `confidence_Llama_2_13b_cha`, `confidence_Mistral_7B_Inst` (truncated names, verified from actual file). Per-feature analysis (FR-3) must re-derive features from source task text using H-M1's `compute_bidir_features`, or fall back to using `task_type` as a coarse proxy if source text is unavailable. Aggregate block also has `models_evaluated` list with full model names — use to map short keys to full names.

---

## A-1: Conflation Analysis Pipeline [Complexity: Medium, Budget: 6]

**Applied**: Standard pandas/numpy aggregation, no KB pattern needed (pure analysis).

### API Signatures

```python
# analysis.py
from typing import Dict, List, Optional
import json

# Full model name -> short confidence key used in H-M1 results.json
MODEL_KEY_MAP = {
    "meta-llama/Llama-2-7b-chat-hf": "confidence_Llama_2_7b_chat",
    "meta-llama/Llama-2-13b-chat-hf": "confidence_Llama_2_13b_cha",
    "mistralai/Mistral-7B-Instruct-v0.2": "confidence_Mistral_7B_Inst",
}

def load_h_m1_results(results_path: str) -> Dict:
    """Load H-M1 results.json. Returns {"aggregate": {...}, "per_task": List[Dict]}."""
    ...

def analyze_high_confidence_correlation(
    task_results: List[Dict],
    threshold: float = 0.7,
    model_key: str = "confidence_Llama_2_7b_chat",
) -> Dict:
    """
    Filter tasks with confidence >= threshold on model_key, split by task_type.
    Returns:
      {rate_a: float, rate_b: float, rate_difference: float,
       conflation_score: float, n_high_a: int, n_high_b: int,
       n_total_a: int, n_total_b: int, gate_pass: bool}
    conflation_score = 1 - rate_difference
    gate_pass = (rate_difference < 0.15) or (conflation_score > 0.85)
    """
    ...

def per_feature_analysis(
    task_results: List[Dict],
    threshold: float = 0.7,
    model_key: str = "confidence_Llama_2_7b_chat",
    task_texts: Optional[Dict[str, str]] = None,
) -> Dict:
    """
    Break down high-conf rate by feature marker (USER_MARKERS/CONTEXT_MARKERS/HEDGE_MARKERS).
    If task_texts provided, recompute features via
    h-m1.code.task_classifier.compute_bidir_features(text) per task_id.
    If task_texts is None, returns {} for feature keys with a warning field.
    Returns:
      {"user_belief_reference": {"rate": float, "n": int},
       "context_dependent": {"rate": float, "n": int},
       "hedged_answer": {"rate": float, "n": int}}
    """
    ...

def cross_model_analysis(
    task_results: List[Dict],
    threshold: float = 0.7,
) -> Dict:
    """
    Run analyze_high_confidence_correlation per model in MODEL_KEY_MAP.
    Returns:
      {model_short_name: {rate_a, rate_b, rate_difference, conflation_score}, ...,
       "consistency": {"std_rate_difference": float, "same_gate_pass": bool}}
    """
    ...

def threshold_sensitivity(
    task_results: List[Dict],
    thresholds: List[float] = [0.5, 0.6, 0.7, 0.8, 0.9],
    model_key: str = "confidence_Llama_2_7b_chat",
) -> Dict:
    """Returns {threshold: {rate_a, rate_b, rate_difference, conflation_score}, ...}."""
    ...

def generate_figures(results: Dict, output_dir: str) -> None:
    """
    Writes to output_dir:
      gate_metrics.png       - bar chart rate_a vs rate_b (primary model, threshold=0.7)
      feature_heatmap.png    - per-feature high-conf rates (rows=feature, cols=type A/B)
      cross_model_scatter.png - rate_difference per model
      sensitivity_curve.png  - rate_difference vs threshold line plot
    """
    ...
```

### Tensor Shapes

N/A — this is scalar/dict analysis over `per_task` list (2212 records), no tensors.

### Pseudo-code: analyze_high_confidence_correlation

```
1. high = [t for t in task_results if t[model_key] >= threshold]
2. n_high_a = count(t.task_type == "A" for t in high)
3. n_high_b = count(t.task_type == "B" for t in high)
4. n_total_a, n_total_b = counts by task_type in task_results
5. rate_a = n_high_a / n_total_a; rate_b = n_high_b / n_total_b
6. rate_difference = abs(rate_a - rate_b)
7. conflation_score = 1 - rate_difference
8. gate_pass = rate_difference < 0.15 or conflation_score > 0.85
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_h_m1_results | JSON load + schema validation |
| L-1-2 | analyze_high_confidence_correlation | Core FR-1/FR-2 gate logic |
| L-1-3 | per_feature_analysis | FR-3, requires H-M1 text re-classification path |
| L-1-4 | cross_model_analysis | FR-4, loops MODEL_KEY_MAP |
| L-1-5 | threshold_sensitivity | FR-5, loops thresholds list |
| L-1-6 | generate_figures | FR-6, matplotlib/seaborn, 4 PNGs |

---

## External Dependencies (Base Hypothesis: H-M1)

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-m1/code/task_classifier.py (ACTUAL CODE)
USER_BELIEF_MARKERS = ["you think", "your opinion", "do you believe", "your view", "you feel"]
CONTEXT_MARKERS = ["given that", "considering", "in this situation", "assuming", "if you were"]
HEDGE_MARKERS = ["might", "could", "possibly", "it depends", "perhaps", "maybe"]

def compute_bidir_features(text: str) -> Dict[str, bool]:
    """Returns {"user_belief_reference": bool, "context_dependent": bool, "hedged_answer": bool}."""
    ...

def classify_task_type(text: str, threshold: int = 1) -> str:
    """Returns 'A' or 'B'."""
    ...
```

**Verified from**: `docs/youra_research/h-m1/code/task_classifier.py` (actual implementation).

**results.json schema** (verified from `docs/youra_research/h-m1/code/outputs/results.json`):
```python
{
  "aggregate": {"gate_pass": bool, "n_type_a": int, "n_type_b": int,
                "models_evaluated": List[str], ...},
  "per_task": [
    {"task_id": str, "task_type": "A" | "B",
     "confidence_Llama_2_7b_chat": float,
     "confidence_Llama_2_13b_cha": float,
     "confidence_Mistral_7B_Inst": float}
  ]
}
```
No `features` key per task — H-M2's `per_feature_analysis` must call `compute_bidir_features` on original task text (from H-M1's `data.py` loader) if per-feature breakdown is required; otherwise document as a known gap.
