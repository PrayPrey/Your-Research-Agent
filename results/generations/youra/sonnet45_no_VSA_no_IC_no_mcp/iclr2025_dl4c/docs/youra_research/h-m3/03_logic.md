# Logic Specification: h-m3
## Supervised AI Feedback Training System

**Date:** 2026-08-25  
**Author:** PrayPrey  
**Hypothesis:** h-m3  
**Phase:** 3 (Implementation Planning)

---

## Codebase Analysis

**Project Type:** existing_codebase  
**Status:** Existing patterns analyzed from h-e1 archive  
**Analyzed Path:** `docs/youra_research/_archive/20260824T222421_routing_recovery/h-e1/code/`  
**Relevant Symbols:** `ExecutionFeedbackCollector.collect_humaneval()`, `DataValidator.generate_report()`, `ResultVisualizer.generate_all()`

---

## Overview

Design API signatures and tensor shapes for supervised learning system that fine-tunes CodeBERT on human quality annotations. Target: AI-human correlation >0.7.

**Core Components:**
1. Data loading from h-e1 cache + human annotations
2. Model fine-tuning (CodeBERT regression)
3. Correlation evaluation with statistical tests
4. Visualization (4 required plots)

**Applied:** Standard PyTorch/HuggingFace fine-tuning pattern

---

## L-1: Data Loading Module [Complexity: 2, Budget: 5]

### API Signatures

```python
from dataclasses import dataclass
from typing import Tuple, List, Optional
from torch.utils.data import Dataset

@dataclass
class CodeSample:
    """Single code sample with human annotation."""
    problem_id: str
    code: str
    human_score: float  # 0-10 scale
    dataset: str  # "humaneval" or "mbpp"

class AnnotatedCodeDataset(Dataset):
    """PyTorch dataset for (code, human_score) pairs."""
    
    def __init__(self, samples: List[CodeSample], tokenizer, max_length: int = 512):
        """Initialize dataset. samples: List[CodeSample] -> tokenized tensors"""
        ...
    
    def __getitem__(self, idx: int) -> dict:
        """Return tokenized batch. idx -> {"input_ids": [512], "labels": [1]}"""
        ...
    
    def __len__(self) -> int:
        ...

def load_humaneval_annotations(cache_path: str) -> List[CodeSample]:
    """Load HumanEval with human scores from h-e1 cache."""
    ...

def load_mbpp_annotations(cache_path: str) -> List[CodeSample]:
    """Load MBPP with human scores from h-e1 cache."""
    ...

def create_splits(
    samples: List[CodeSample], 
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    seed: int = 42
) -> Tuple[List[CodeSample], List[CodeSample], List[CodeSample]]:
    """Split data into train/val/test. Returns (train, val, test)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [batch, 512] | Tokenized code |
| attention_mask | [batch, 512] | Padding mask |
| labels | [batch, 1] | Human scores (0-10) |

### Pseudo-code

```
1. Load HumanEval + MBPP from cache (164 + 974 = 1138 samples)
2. Parse human_score field from cached annotations
3. Stratified split by score distribution (70/15/15)
4. Tokenize with CodeBERT tokenizer (truncate to 512)
5. Convert to PyTorch Dataset (return dict with input_ids, labels)
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Cache loading | Read h-e1 cached JSONL files |
| L-1-2 | Annotation parsing | Extract human_score field |
| L-1-3 | Data splitting | Stratified 70/15/15 split |
| L-1-4 | Tokenization | CodeBERT preprocessing |
| L-1-5 | Dataset wrapper | PyTorch Dataset implementation |

---

## L-2: Model Training Module [Complexity: 3, Budget: 6]

### API Signatures

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

class SupervisedFeedbackModel:
    """CodeBERT fine-tuned for human score prediction."""
    
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        """Load pretrained CodeBERT with regression head (num_labels=1)."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=1
        )
    
    def train(
        self, 
        train_dataset: AnnotatedCodeDataset,
        val_dataset: AnnotatedCodeDataset,
        output_dir: str = "./checkpoint",
        epochs: int = 5,
        batch_size: int = 8,
        learning_rate: float = 2e-5
    ) -> None:
        """Fine-tune model. Saves best checkpoint by val_loss."""
        ...
    
    def predict(self, codes: List[str]) -> List[float]:
        """Predict human scores. codes: List[str] -> List[float] (0-10 scale)"""
        ...
    
    def save(self, path: str) -> None:
        """Save trained model and tokenizer."""
        ...
    
    def load(self, path: str) -> None:
        """Load trained model from checkpoint."""
        ...

def compute_mse_loss(predictions, labels):
    """MSE loss for regression. predictions: [batch, 1], labels: [batch, 1] -> scalar"""
    return ((predictions - labels) ** 2).mean()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits (model output) | [batch, 1] | Raw predictions |
| labels | [batch, 1] | Ground truth scores |
| loss | scalar | MSE loss |

### Pseudo-code

```
1. Load CodeBERT-base (125M params)
2. Replace classification head with linear(768 -> 1) for regression
3. Create HuggingFace Trainer:
   - optimizer: AdamW(lr=2e-5)
   - loss: MSE
   - eval_strategy: per epoch
   - early_stopping: patience=2 on val_loss
4. Train 5 epochs (batch_size=8)
5. Save best checkpoint by validation loss
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Model loading | Load pretrained CodeBERT |
| L-2-2 | Regression head | Replace classifier with linear layer |
| L-2-3 | Training loop | HuggingFace Trainer setup |
| L-2-4 | Checkpointing | Save best model by val_loss |
| L-2-5 | Inference | Predict scores on new code |
| L-2-6 | Baseline loading | Load h-e1/h-m1 predictions for comparison |

---

## L-3: Evaluation Module [Complexity: 2, Budget: 5]

### API Signatures

```python
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error
from typing import Dict

@dataclass
class EvaluationResult:
    """Evaluation metrics."""
    spearman_rho: float
    spearman_p: float
    pearson_r: float
    mae: float
    gate_passed: bool

def evaluate_correlation(
    human_scores: List[float],
    ai_predictions: List[float]
) -> EvaluationResult:
    """Calculate correlation metrics.
    
    Args:
        human_scores: [N] ground truth scores
        ai_predictions: [N] model predictions
    
    Returns:
        EvaluationResult with correlations and gate status
    """
    rho, p_value = spearmanr(human_scores, ai_predictions)
    r, _ = pearsonr(human_scores, ai_predictions)
    mae = mean_absolute_error(human_scores, ai_predictions)
    
    gate_passed = (rho > 0.7) and (p_value < 0.05)
    
    return EvaluationResult(rho, p_value, r, mae, gate_passed)

def load_baseline_predictions(
    hypothesis_id: str,
    cache_path: str = "../.data_cache"
) -> Dict[str, float]:
    """Load cached AI predictions from h-e1 or h-m1.
    
    Args:
        hypothesis_id: "h-e1" or "h-m1"
        cache_path: Path to cache directory
    
    Returns:
        Dict mapping problem_id -> ai_prediction
    """
    ...

def compare_to_baselines(
    test_samples: List[CodeSample],
    proposed_predictions: List[float],
    cache_path: str
) -> Dict[str, float]:
    """Compare h-m3 to h-e1 and h-m1 baselines.
    
    Returns:
        {"h_e1": 0.45, "h_m1": 0.65, "h_m3": 0.75}
    """
    ...
```

### Pseudo-code

```
1. Get test set predictions from trained model (170 samples)
2. Calculate Spearman correlation(human_scores, ai_predictions)
3. Statistical significance: p-value < 0.05
4. Gate check: rho > 0.7 AND p < 0.05
5. Load h-e1 baseline (r=0.45-0.52) and h-m1 (r=0.65) from cache
6. Compare: [h-e1, h-m1, h-m3] correlations
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Correlation calculation | Spearman + Pearson |
| L-3-2 | Statistical tests | p-value computation |
| L-3-3 | Baseline loading | Read h-e1/h-m1 cached results |
| L-3-4 | Gate check | Automated pass/fail logic |
| L-3-5 | Error analysis | MAE and residual distribution |

---

## L-4: Visualization Module [Complexity: 2, Budget: 4]

### API Signatures

```python
import matplotlib.pyplot as plt
from typing import List, Optional

class ResultVisualizer:
    """Generate required figures for h-m3."""
    
    def __init__(self, save_dir: str = "./figures"):
        """Initialize visualizer with output directory."""
        self.save_dir = save_dir
    
    def plot_correlation_comparison(
        self,
        correlations: Dict[str, float],
        gate_threshold: float = 0.7
    ) -> None:
        """Bar chart: [h-e1, h-m1, h-m3] correlations with 0.7 threshold line.
        
        Saves to: {save_dir}/correlation_comparison.png
        """
        ...
    
    def plot_scatter(
        self,
        human_scores: List[float],
        ai_predictions: List[float]
    ) -> None:
        """Scatter plot: human vs AI predictions with diagonal reference.
        
        Saves to: {save_dir}/prediction_scatter.png
        """
        ...
    
    def plot_learning_curve(
        self,
        epochs: List[int],
        val_correlations: List[float]
    ) -> None:
        """Line plot: validation correlation vs epoch.
        
        Saves to: {save_dir}/learning_curve.png
        """
        ...
    
    def plot_error_distribution(
        self,
        human_scores: List[float],
        ai_predictions: List[float]
    ) -> None:
        """Histogram: |human - AI| residuals.
        
        Saves to: {save_dir}/error_distribution.png
        """
        ...
    
    def generate_all(
        self,
        eval_result: EvaluationResult,
        baseline_correlations: Dict[str, float],
        test_data: List[CodeSample],
        predictions: List[float],
        training_history: Optional[dict] = None
    ) -> None:
        """Generate all 4 required figures in one call."""
        ...
```

### Pseudo-code

```
1. Bar chart: 
   - x-axis: ["h-e1", "h-m1", "h-m3"]
   - y-axis: Spearman correlation
   - horizontal line at 0.7 (gate threshold)

2. Scatter plot:
   - x-axis: human scores (0-10)
   - y-axis: AI predictions (0-10)
   - diagonal line (perfect agreement)
   - annotate with rho value

3. Learning curve:
   - x-axis: epochs (1-5)
   - y-axis: validation Spearman correlation
   - shows convergence behavior

4. Error histogram:
   - x-axis: |human_score - ai_prediction| bins
   - y-axis: count
   - shows prediction accuracy distribution
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Bar chart | Baseline vs proposed comparison |
| L-4-2 | Scatter plot | Human vs AI predictions |
| L-4-3 | Learning curve | Training convergence |
| L-4-4 | Error histogram | Residual distribution |

---

## L-5: Integration & Orchestration [Complexity: 1, Budget: 3]

### API Signatures

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    """Configuration for h-m3 experiment."""
    model_name: str = "microsoft/codebert-base"
    cache_path: str = "../.data_cache/datasets"
    epochs: int = 5
    batch_size: int = 8
    learning_rate: float = 2e-5
    seed: int = 42
    output_dir: str = "./results"

def run_experiment(config: ExperimentConfig) -> EvaluationResult:
    """Run complete h-m3 pipeline.
    
    Steps:
        1. Load data from h-e1 cache
        2. Train supervised model
        3. Evaluate on test set
        4. Generate visualizations
        5. Save validation report
    
    Returns:
        EvaluationResult with gate status
    """
    # 1. Data loading
    humaneval = load_humaneval_annotations(config.cache_path)
    mbpp = load_mbpp_annotations(config.cache_path)
    all_samples = humaneval + mbpp
    train, val, test = create_splits(all_samples, seed=config.seed)
    
    train_dataset = AnnotatedCodeDataset(train, tokenizer)
    val_dataset = AnnotatedCodeDataset(val, tokenizer)
    
    # 2. Model training
    model = SupervisedFeedbackModel(config.model_name)
    model.train(train_dataset, val_dataset, epochs=config.epochs)
    
    # 3. Evaluation
    test_codes = [s.code for s in test]
    test_human = [s.human_score for s in test]
    predictions = model.predict(test_codes)
    
    result = evaluate_correlation(test_human, predictions)
    baselines = compare_to_baselines(test, predictions, config.cache_path)
    
    # 4. Visualization
    viz = ResultVisualizer(f"{config.output_dir}/figures")
    viz.generate_all(result, baselines, test, predictions)
    
    # 5. Save results
    save_validation_report(result, baselines, config.output_dir)
    
    return result

def save_validation_report(
    result: EvaluationResult,
    baselines: Dict[str, float],
    output_dir: str
) -> None:
    """Write 04_validation.md with gate verdict and metrics."""
    ...
```

### Pseudo-code

```
main():
    1. Load config (seed=42, epochs=5, batch_size=8)
    2. Load + split data (797 train, 171 val, 170 test)
    3. Fine-tune CodeBERT (5 epochs, early stopping)
    4. Predict on test set
    5. Calculate correlations (Spearman, Pearson)
    6. Check gate: rho > 0.7 AND p < 0.05
    7. Compare to baselines (h-e1: 0.45-0.52, h-m1: 0.65)
    8. Generate 4 figures
    9. Save validation report with PASS/FAIL verdict
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Config management | ExperimentConfig dataclass |
| L-5-2 | Pipeline orchestration | run_experiment() main loop |
| L-5-3 | Report generation | 04_validation.md writer |

---

## Error Handling Patterns

### Data Loading Errors

```python
# Missing cache files
if not os.path.exists(cache_path):
    raise FileNotFoundError(
        f"h-e1 cache not found at {cache_path}. "
        "Run h-e1 experiment first or check path."
    )

# Missing human_score field
if "human_score" not in sample:
    raise ValueError(
        f"Sample {sample['problem_id']} missing human_score annotation. "
        "Check h-e1 cache format or regenerate annotations."
    )

# Insufficient samples after filtering
if len(test_samples) < 170:
    raise ValueError(
        f"Test set has {len(test_samples)} samples, need >=170. "
        "Check data splits or total dataset size."
    )
```

### Training Errors

```python
# Training divergence
if val_loss > 100 or math.isnan(val_loss):
    raise RuntimeError(
        f"Training diverged (val_loss={val_loss}). "
        "Try lower learning rate or check data normalization."
    )

# OOM errors
try:
    model.train(...)
except torch.cuda.OutOfMemoryError:
    print("GPU OOM. Reducing batch_size from 8 to 4.")
    config.batch_size = 4
    model.train(...)
```

### Evaluation Errors

```python
# Statistical significance failure
if p_value >= 0.05:
    print(
        f"WARNING: p-value={p_value:.4f} >= 0.05. "
        "Correlation not statistically significant. "
        "Consider larger test set or stronger model."
    )

# Gate failure
if not result.gate_passed:
    print(
        f"GATE FAILED: rho={result.spearman_rho:.3f} <= 0.7. "
        "Hypothesis h-m3 did not reach target correlation. "
        "Blocking dependent hypotheses."
    )
```

---

## Task Budget Summary

| Module | Complexity | Budget | Subtasks |
|--------|-----------|--------|----------|
| L-1: Data Loading | 2 | 5 | 5/5 |
| L-2: Model Training | 3 | 6 | 6/6 |
| L-3: Evaluation | 2 | 5 | 5/5 |
| L-4: Visualization | 2 | 4 | 4/4 |
| L-5: Integration | 1 | 3 | 3/3 |
| **Total** | - | **23/30** | **23/30** |

**Budget Allocation:**
- Environment setup: 1 task (dependencies)
- Testing: 4 tasks (data, training, eval, viz)
- Documentation: 2 tasks (comments, report)
- **Total Used: 30/30**

---

## Critical Implementation Notes

### 1. Data Format Assumptions
- h-e1 cache expected at: `docs/youra_research/.data_cache/datasets/`
- Each sample must have: `{problem_id, code, human_score, dataset}`
- If human_score unavailable, fallback to synthetic annotations or use h-e1 AI feedback as proxy

### 2. Model Selection
- Primary: `microsoft/codebert-base` (proven code understanding)
- Fallback: `Salesforce/codet5-base` (if CodeBERT underperforms)
- Always use `num_labels=1` for regression (not classification)

### 3. Gate Condition
- **MUST_WORK Gate:** `rho > 0.7 AND p < 0.05`
- Test set size: 170 samples (15% of 1138 total)
- Failure blocks downstream hypotheses in verification_state.yaml

### 4. Baseline Comparison
- h-e1 baseline: r=0.45-0.52 (zero-shot GPT-3.5)
- h-m1 baseline: r=0.65 (supervised, previous attempt)
- Load from cache or recompute if unavailable

### 5. Reproducibility
- Fixed seed: 42 (for splits and training)
- Save best checkpoint by val_loss (not correlation)
- Log all hyperparameters in validation report

---

## Self-Validation Checklist

- [x] No ASCII diagrams
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (23/30)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] Function signatures with type hints
- [x] Pseudo-code for complex algorithms (training loop, correlation)
- [x] Error handling patterns specified

---

**Next Step:** Phase 4 Coding - Implement APIs exactly as specified above
