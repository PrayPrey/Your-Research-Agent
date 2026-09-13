# Logic Design: H-M3 Viability Classification

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis ID:** H-M3
**Type:** MECHANISM (Rule-based classifier)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Overview

Rule-based binary classifier for hypothesis viability prediction using Gate 1 micro-pilot overhead (10 samples). No neural network training - uses validated scaling factor k from h-m1 prerequisite.

**Applied**: Standard classification pattern with statistical testing (scipy.stats)

---

## A-1: Gate1ViabilityClassifier [Complexity: 2, Budget: 10]

**Applied**: Rule-based threshold classifier

### API Signatures

```python
class Gate1ViabilityClassifier:
    """Binary classifier for hypothesis viability using Gate 1 overhead."""
    
    def __init__(self, scaling_factor_k: float, threshold: float = 0.10):
        """
        Initialize classifier.
        
        Args:
            scaling_factor_k: Validated from h-m1 (r >= 0.7)
            threshold: Viability threshold (default 10%)
        """
        self.k = scaling_factor_k
        self.threshold = threshold
    
    def predict(self, O_10: float) -> tuple[str, float]:
        """
        Predict viability for single hypothesis.
        
        Args:
            O_10: 10-sample overhead (0.0-1.0)
        
        Returns:
            (prediction, O_pred) where:
            - prediction: "viable" | "non-viable"
            - O_pred: float (predicted full-scale overhead)
        
        Raises:
            ValueError: If O_10 not in [0.0, 1.0]
        """
        ...
    
    def predict_batch(self, O_10_array: np.ndarray) -> tuple[list[str], np.ndarray]:
        """
        Predict viability for batch.
        
        Args:
            O_10_array: (N,) array of 10-sample overheads
        
        Returns:
            (predictions, O_preds) where:
            - predictions: list[str] length N
            - O_preds: (N,) array of predicted overheads
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Range | Note |
|----------|-------|-------|------|
| O_10 | scalar | [0.0, 1.0] | Input: 10-sample overhead |
| O_10_array | (N,) | [0.0, 1.0] | Batch input (N=30 for corpus) |
| O_pred | scalar | [0.0, inf) | Predicted full-scale overhead |
| O_preds | (N,) | [0.0, inf) | Batch predictions |
| prediction | str | {"viable", "non-viable"} | String label |
| predictions | list[str] | {"viable", "non-viable"} | Batch labels |

### Pseudo-code

```
predict(O_10):
    1. Validate: 0 <= O_10 <= 1
    2. O_pred = O_10 * k
    3. prediction = "non-viable" if O_pred > threshold else "viable"
    4. Return (prediction, O_pred)

predict_batch(O_10_array):
    1. predictions = []
    2. O_preds = []
    3. For each O_10 in O_10_array:
        a. pred, O_pred = predict(O_10)
        b. Append to lists
    4. Return (predictions, np.array(O_preds))
```

### Edge Cases

- **O_10 = 0**: Valid input, O_pred = 0, predict "viable"
- **k = 1**: No scaling, O_pred = O_10
- **O_pred = threshold**: Classify as "viable" (<=threshold)
- **O_10 > 1.0 or O_10 < 0.0**: Raise ValueError

### Subtasks [5/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | __init__ | Store k and threshold |
| L-1-2 | predict | Single prediction with validation |
| L-1-3 | predict_batch | Batch wrapper over predict |
| L-1-4 | Input validation | Check O_10 range [0.0, 1.0] |
| L-1-5 | Edge case handling | O_10=0, k=1, threshold boundary |

---

## A-2: Evaluation Functions [Complexity: 1, Budget: 8]

**Applied**: sklearn metrics + scipy.stats binomial test

### API Signatures

```python
def compute_accuracy(predictions: list[str], actuals: list[str]) -> float:
    """
    Compute classification accuracy.
    
    Args:
        predictions: List of "viable" | "non-viable"
        actuals: List of ground truth labels
    
    Returns:
        Accuracy in [0.0, 1.0]
    
    Raises:
        ValueError: If len(predictions) != len(actuals)
    """
    ...

def compute_confusion_matrix(
    predictions: list[str], 
    actuals: list[str]
) -> dict[str, int]:
    """
    Compute confusion matrix components.
    
    Args:
        predictions: List of predicted labels
        actuals: List of ground truth labels
    
    Returns:
        {"TP": int, "TN": int, "FP": int, "FN": int} where:
        - TP: Correctly predicted non-viable
        - TN: Correctly predicted viable
        - FP: Incorrectly predicted non-viable
        - FN: Incorrectly predicted viable
    """
    ...

def binomial_test_vs_null(
    n_correct: int, 
    n_total: int, 
    null_p: float = 0.5,
    alpha: float = 0.05
) -> tuple[float, bool]:
    """
    Test if accuracy exceeds null hypothesis.
    
    Args:
        n_correct: Number of correct predictions
        n_total: Total predictions
        null_p: Null hypothesis probability (default 0.5)
        alpha: Significance level (default 0.05)
    
    Returns:
        (p_value, reject_null) where:
        - p_value: float (one-tailed test)
        - reject_null: bool (True if p < alpha)
    """
    ...
```

### Pseudo-code

```
compute_accuracy(predictions, actuals):
    1. Validate len(predictions) == len(actuals)
    2. correct = sum(p == a for p, a in zip(predictions, actuals))
    3. Return correct / len(predictions)

compute_confusion_matrix(predictions, actuals):
    1. TP = count where p="non-viable" and a="non-viable"
    2. TN = count where p="viable" and a="viable"
    3. FP = count where p="non-viable" and a="viable"
    4. FN = count where p="viable" and a="non-viable"
    5. Return {"TP": TP, "TN": TN, "FP": FP, "FN": FN}

binomial_test_vs_null(n_correct, n_total, null_p, alpha):
    1. p_value = scipy.stats.binom_test(n_correct, n_total, p=null_p, alternative='greater')
    2. reject_null = p_value < alpha
    3. Return (p_value, reject_null)
```

### Subtasks [3/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | compute_accuracy | Accuracy from sklearn.metrics.accuracy_score |
| L-2-2 | compute_confusion_matrix | Manual count or sklearn.metrics.confusion_matrix |
| L-2-3 | binomial_test_vs_null | scipy.stats.binom_test wrapper |

---

## A-3: Baseline Functions [Complexity: 1, Budget: 3]

**Applied**: numpy.random for null hypothesis baseline

### API Signatures

```python
def random_baseline(n_samples: int, seed: int = 42) -> np.ndarray:
    """
    Random guessing baseline (50% probability).
    
    Args:
        n_samples: Number of predictions (30 for corpus)
        seed: Random seed for reproducibility
    
    Returns:
        (n_samples,) array of "viable" | "non-viable"
    """
    ...
```

### Pseudo-code

```
random_baseline(n_samples, seed):
    1. np.random.seed(seed)
    2. Return np.random.choice(["viable", "non-viable"], size=n_samples)
```

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | random_baseline | Numpy random choice with seed=42 |

---

## A-4: Data Loading Functions [Complexity: 1, Budget: 4]

**Applied**: pandas.read_csv with validation

### API Signatures

```python
def load_corpus(filepath: str) -> pd.DataFrame:
    """
    Load retrospective corpus from h-m1.
    
    Args:
        filepath: Path to CSV (e.g., "../h-m1/data/retrospective_corpus_30.csv")
    
    Returns:
        DataFrame with columns:
        - O_10: float (0.0-1.0)
        - O_full: float (0.0-1.0)
        - hypothesis_type: str
        - threshold: float (default 0.10)
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns missing or invalid types
    """
    ...

def compute_ground_truth_labels(
    O_full_array: np.ndarray, 
    threshold: float = 0.10
) -> list[str]:
    """
    Compute ground truth viability labels.
    
    Args:
        O_full_array: (N,) array of full-scale overheads
        threshold: Viability threshold
    
    Returns:
        List of "viable" | "non-viable" labels
    """
    ...
```

### Pseudo-code

```
load_corpus(filepath):
    1. df = pd.read_csv(filepath)
    2. Validate columns: ["O_10", "O_full", "hypothesis_type", "threshold"]
    3. Validate types: O_10 numeric, O_full numeric
    4. Validate ranges: 0 <= O_10 <= 1, 0 <= O_full <= 1
    5. Return df

compute_ground_truth_labels(O_full_array, threshold):
    1. labels = ["non-viable" if o > threshold else "viable" for o in O_full_array]
    2. Return labels
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | load_corpus | Read CSV with validation |
| L-4-2 | compute_ground_truth_labels | Threshold comparison for labels |

---

## A-5: Scaling Factor Loader [Complexity: 1, Budget: 3]

**Applied**: JSON or direct computation from corpus

### API Signatures

```python
def load_scaling_factor(
    source: str = "compute",
    filepath: str | None = None,
    O_10_values: np.ndarray | None = None,
    O_full_values: np.ndarray | None = None
) -> float:
    """
    Load or compute scaling factor k from h-m1.
    
    Args:
        source: "compute" | "file"
        filepath: Path to JSON if source="file"
        O_10_values: (N,) array for computation if source="compute"
        O_full_values: (N,) array for computation if source="compute"
    
    Returns:
        k: Scaling factor (validated r >= 0.7 from h-m1)
    
    Raises:
        ValueError: If r < 0.7 (validation failure)
    """
    ...
```

### Pseudo-code

```
load_scaling_factor(source, filepath, O_10_values, O_full_values):
    If source == "file":
        1. Load JSON from filepath
        2. k = data["scaling_factor_k"]
    Else if source == "compute":
        1. slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(O_10_values, O_full_values)
        2. If r_value < 0.7: Raise ValueError("Prerequisite h-m1 validation failed")
        3. k = slope
    Return k
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | load_from_file | JSON loader (if h-m1 saved k) |
| L-5-2 | compute_from_corpus | scipy.stats.linregress with validation |

---

## Summary: Task Allocation

| Task ID | Component | Complexity | Budget Used | Status |
|---------|-----------|------------|-------------|--------|
| A-1 | Gate1ViabilityClassifier | 2 | 5/10 | Complete |
| A-2 | Evaluation Functions | 1 | 3/8 | Complete |
| A-3 | Baseline Functions | 1 | 1/3 | Complete |
| A-4 | Data Loading Functions | 1 | 2/4 | Complete |
| A-5 | Scaling Factor Loader | 1 | 2/3 | Complete |
| **Total** | **5 components** | **6** | **13/28** | **Within budget** |

---

## Error Handling Summary

### Input Validation
- **O_10 range**: Raise ValueError if not in [0.0, 1.0]
- **Missing columns**: Raise ValueError if CSV lacks O_10, O_full
- **Scaling factor r**: Raise ValueError if r < 0.7 (prerequisite failure)
- **Length mismatch**: Raise ValueError if len(predictions) != len(actuals)

### Edge Cases
- **O_10 = 0**: Valid, predicts "viable"
- **k = 1**: Valid, no scaling
- **O_pred = threshold**: Classify as "viable" (<=threshold convention)
- **Empty arrays**: Handle with appropriate error messages

---

## Dependencies

### External Libraries
- **numpy**: Array operations, random baseline
- **pandas**: CSV loading, DataFrame operations
- **scipy.stats**: linregress (scaling factor), binom_test (statistical testing)
- **sklearn.metrics**: accuracy_score, confusion_matrix (optional, can implement manually)

### Prerequisite Data
- **h-m1 corpus**: retrospective_corpus_30.csv with O_10, O_full measurements
- **Scaling factor k**: Validated r >= 0.7 from h-m1 (either load from file or compute)

---

## Phase 4 Integration Notes

### Expected Call Sequence
1. `load_corpus("../h-m1/data/retrospective_corpus_30.csv")` → df
2. `load_scaling_factor(source="compute", O_10_values=df["O_10"], O_full_values=df["O_full"])` → k
3. `classifier = Gate1ViabilityClassifier(scaling_factor_k=k, threshold=0.10)`
4. `predictions, O_preds = classifier.predict_batch(df["O_10"].values)`
5. `actuals = compute_ground_truth_labels(df["O_full"].values, threshold=0.10)`
6. `accuracy = compute_accuracy(predictions, actuals)`
7. `cm = compute_confusion_matrix(predictions, actuals)`
8. `p_value, reject_null = binomial_test_vs_null(n_correct=int(accuracy * 30), n_total=30)`

### Output Files
- **No model checkpoints** (rule-based classifier)
- **Results JSON**: Save accuracy, confusion matrix, p_value
- **Figures**: accuracy_comparison.png, confusion_matrix.png, error_analysis.png

---

*Next Phase: Phase 4 - Coding*
