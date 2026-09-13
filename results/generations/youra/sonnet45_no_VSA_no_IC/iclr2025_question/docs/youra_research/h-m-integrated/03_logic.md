# Logic Specification: h-m-integrated

**Date:** 2026-08-20
**Hypothesis:** MECHANISM
**Budget:** 7 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-e1 actual implementation
**Analyzed Path:** docs/youra_research/h-e1/code/
**Relevant Symbols:** TruthfulQALoader, TemperatureScaling, ConformalPrediction, MCDropout, compute_auroc, compute_spearman

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are reused from h-e1. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1/code/data/loader.py
class TruthfulQALoader:
    def __init__(self, seed: int = 42): ...
    
    def load_and_split(
        self,
        cal_ratio: float = 0.4,
        cache_dir: str = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """Returns: (calibration_data, test_data)"""
        ...
    
    def label_correctness(
        self,
        question: str,
        answer: str,
        correct_answers: List[str]
    ) -> int:
        """Returns: 0 if correct, 1 if incorrect"""
        ...


# From: docs/youra_research/h-e1/code/uq/methods.py
class TemperatureScaling:
    def __init__(self): ...
    
    def calibrate(
        self,
        logits: List[torch.Tensor],
        labels: List[int],
        max_iter: int = 50
    ) -> float:
        """Returns: optimal temperature"""
        ...
    
    def compute_uncertainty(self, logits: torch.Tensor, T: float = None) -> float:
        """Returns: 1 - max_prob"""
        ...


class ConformalPrediction:
    def __init__(self, alpha: float = 0.1): ...
    
    def calibrate(
        self,
        logits: List[torch.Tensor],
        labels: List[int]
    ) -> float:
        """Returns: (1-alpha) quantile threshold"""
        ...
    
    def compute_uncertainty(self, logits: torch.Tensor) -> float:
        """Returns: 1 - max_prob"""
        ...


class MCDropout:
    def __init__(self, k: int = 5, dropout_rate: float = 0.1): ...
    
    def compute_uncertainty(
        self,
        questions: List[str],
        model,
        tokenizer
    ) -> List[float]:
        """Returns: List of entropy scores"""
        ...


# From: docs/youra_research/h-e1/code/eval/metrics.py
def compute_auroc(y_true: List[int], uncertainties: List[float]) -> float:
    """Returns: AUROC score (0.5 to 1.0)"""
    ...

def compute_spearman(uncertainties: List[float], incorrectness: List[int]) -> float:
    """Returns: Spearman rho correlation coefficient"""
    ...
```

**Verified from:** docs/youra_research/h-e1/code/ (actual implementation)

---

## A-1: Data Pipeline [Complexity: 8, Budget: 2]

**Applied:** Standard Python data loading patterns

### API Signatures

```python
class DataManager:
    """Manages h-e1 artifacts and HaluEval dataset."""
    
    def __init__(self, h_e1_cache_dir: str, seed: int = 42):
        """Initialize data manager."""
        self.h_e1_cache_dir = h_e1_cache_dir
        self.seed = seed
    
    def load_h_e1_artifacts(self) -> Dict[str, Any]:
        """
        Load h-e1 generated artifacts.
        
        Returns:
            {
                "questions": List[str],  # 817 questions
                "answers": List[str],  # Generated answers
                "labels": List[int],  # 0/1 correctness
                "uq_scores": {  # 6 methods
                    "temp_scaling": List[float],
                    "conformal": List[float],
                    "mc_k1": List[float],
                    "mc_k3": List[float],
                    "mc_k5": List[float],
                    "mc_k10": List[float]
                },
                "calibration_params": {
                    "temperature": float,
                    "conformal_threshold": float
                }
            }
        """
        ...
    
    def load_halueval(
        self,
        split: str = "qa",
        cache_dir: str = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Load HaluEval QA split, return 80/20 calib/test.
        
        Returns:
            (calib_data, test_data): Each item = {question, answer, label}
        """
        ...
    
    def verify_splits(self, h_e1_data: Dict) -> bool:
        """Verify 40/60 split consistency with h-e1."""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Load h-e1 artifacts | Read JSON/pickle from cache |
| L-1-2 | Load HaluEval | Download + 80/20 split |

---

## A-2: Mechanism Validator [Complexity: 12, Budget: 3]

**Applied:** Scikit-learn metric patterns, NumPy vectorization

### API Signatures

```python
class UQMechanismValidator:
    """Validates UQ mechanism via multiple metrics."""
    
    def __init__(
        self,
        uq_scores: Dict[str, List[float]],
        predictions: List[str],
        labels: List[int]
    ):
        """
        Args:
            uq_scores: {method_name: [scores]}  # N=817
            predictions: Generated answers
            labels: Binary correctness (0/1)
        """
        self.uq_scores = uq_scores
        self.labels = labels
    
    def compute_spearman(self, method_name: str) -> Tuple[float, float]:
        """
        Spearman correlation.
        
        Returns:
            (rho, p_value)
        """
        ...
    
    def compute_auroc(self, method_name: str) -> float:
        """AUROC treating uncertainty as positive class score."""
        ...
    
    def compute_ause(self, method_name: str, n_bins: int = 10) -> float:
        """
        Area Under Sparsification Error.
        
        Algorithm:
            1. Sort by uncertainty descending
            2. For k in [0, 10%, 20%, ..., 100%]:
                - Remove top k% uncertain samples
                - Compute error on remaining
            3. Integrate error curve (trapezoidal)
        
        Returns:
            AUSE score (lower is better)
        """
        ...
    
    def validate_all_methods(self) -> Dict[str, Dict[str, float]]:
        """
        Run all metrics on all methods.
        
        Returns:
            {
                "temp_scaling": {
                    "spearman_rho": float,
                    "spearman_p": float,
                    "auroc": float,
                    "ause": float,
                    "pass_gate": bool
                },
                ...
            }
        """
        ...
    
    def check_gate(self, results: Dict) -> Tuple[bool, str]:
        """
        Gate logic: ≥4 of 5 non-degenerate methods pass.
        
        Pass condition per method: rho > 0.2 OR auroc > 0.55
        
        Returns:
            (passed, reason_str)
        """
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Spearman + AUROC | Reuse h-e1 functions |
| L-2-2 | AUSE metric | Sparsification curve integration |
| L-2-3 | Gate check logic | Non-degenerate filter + dual metric |

---

## A-3: Cross-Dataset Calibration [Complexity: 11, Budget: 2]

**Applied:** Quantile-based conformal calibration (standard pattern)

### API Signatures

```python
class CrossDatasetCalibrator:
    """Tests conformal calibration transfer across datasets."""
    
    def __init__(
        self,
        source_data: List[Dict],  # HaluEval calib set
        target_data: List[Dict],  # TruthfulQA test set
        alpha: float = 0.1
    ):
        """
        Args:
            source_data: [{question, answer, label}, ...]
            target_data: Same format
            alpha: Miscoverage rate (0.1 → 90% coverage)
        """
        self.source_data = source_data
        self.target_data = target_data
        self.alpha = alpha
    
    def calibrate_on_source(
        self,
        method: str = "conformal"
    ) -> float:
        """
        Fit conformal threshold on HaluEval.
        
        Returns:
            threshold: (1-alpha) quantile of uncertainty scores
        """
        ...
    
    def test_transfer_to_target(self, threshold: float) -> Dict[str, float]:
        """
        Apply threshold to TruthfulQA.
        
        Returns:
            {
                "coverage_source": float,  # HaluEval test coverage
                "coverage_target": float,  # TruthfulQA coverage
                "auroc_source": float,
                "auroc_target": float,
                "transfer_success": bool  # |coverage_target - 0.90| <= 0.10
            }
        """
        ...
    
    def compute_coverage_gap(self, coverage: float) -> float:
        """Returns: |coverage - (1-alpha)|"""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Source calibration | Quantile threshold on HaluEval |
| L-3-2 | Transfer test | Coverage on TruthfulQA |

---

## A-4: HaluEval Inference [Complexity: 14, Budget: 0]

**Note:** NOT allocated logic subtasks (inference runtime, not design).

**Implementation Note:** Reuse h-e1 inference pipeline (LlamaWrapper) with HaluEval questions. Generate answers + uncertainty scores for 6 methods on ~10k samples.

---

## A-5: Visualization Suite [Complexity: 13, Budget: 0]

**Note:** NOT allocated logic subtasks (matplotlib plotting, standard pattern).

**Implementation Note:** 5 matplotlib plots:
1. `plot_gate_metrics_scatter(results, save_path)` - Spearman vs AUROC
2. `plot_spearman_comparison(results, save_path)` - Bar chart
3. `plot_ause_vs_auroc(results, save_path)` - Scatter
4. `plot_sparsification_curves(validator, save_path)` - 6 subplots
5. `plot_cross_dataset_calibration(calibrator, save_path)` - 2-panel

---

## A-6: Report Generation [Complexity: 9, Budget: 0]

**Note:** NOT allocated logic subtasks (markdown templating, standard pattern).

**Implementation Note:** Generate 04_validation.md with:
- Results table (method, Spearman, AUROC, AUSE, PASS/FAIL)
- Cross-dataset transfer table
- Figure links
- Gate decision (PASSED/FAILED)

---

## Total Subtask Usage: 7/7
