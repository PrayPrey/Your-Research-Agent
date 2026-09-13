# Architecture Document: H-C1 Edge Case Robustness Validation

**Hypothesis ID:** h-c1  
**Type:** CONDITION (SHOULD_WORK gate)  
**Date:** 2026-07-11  
**Version:** 1.0

---

## Knowledge Base Applied

Applied: Robustness evaluation with failure analysis patterns for ML systems.

---

## Codebase Analysis (Serena)

**Project Type:** Existing codebase (h-m3 and h-e1 dependencies)  
**Status:** Reusing h-m3 checkpoint extraction and feature extraction (100% reuse)  
**Analyzed Path:** h-m3/code (actual implementation verified)  
**Findings:** CheckpointOnlyExtractor and StatisticalFeatureExtractor interfaces match specification. No h-e1 classifier found (must be created or loaded at runtime).

---

## Architecture Overview

H-C1 validates edge case robustness by:
1. Curating 20 edge case models across 4 architecture families
2. Reusing h-m3 feature extraction (100% code reuse)
3. Loading h-e1 trained classifier (assumed to exist or trained on-the-fly)
4. Computing accuracy metrics with per-family breakdown
5. Generating failure mode analysis with feature distributions

**Core Dependencies:**
- h-m3: CheckpointOnlyExtractor, StatisticalFeatureExtractor
- h-e1: Trained Logistic Regression classifier (sklearn)

---

## Module Structure

### 1. EdgeCaseModelCurator (`src/edge_case_curator.py`)

**Dependencies:** None (TIMM API only)

```python
class EdgeCaseModelCurator:
    def __init__(self, edge_case_families: dict): ...
    def validate_timm_availability(self) -> dict: ...
    def get_edge_case_models(self) -> list[str]: ...
    def assign_family_labels(self, model_names: list[str]) -> dict[str, str]: ...
```

### 2. ClassifierLoader (`src/classifier_loader.py`)

**Dependencies:** None (sklearn only)

```python
class ClassifierLoader:
    def __init__(self, classifier_path: str = None): ...
    def load_or_train(self, fallback_features_df: pd.DataFrame = None, fallback_labels: pd.Series = None) -> object: ...
    def save_classifier(self, classifier: object, path: str): ...
```

### 3. EdgeCaseEvaluator (`src/edge_case_evaluator.py`)

**Dependencies:** ClassifierLoader

```python
class EdgeCaseEvaluator:
    def __init__(self, classifier: object): ...
    def predict(self, features_df: pd.DataFrame) -> pd.Series: ...
    def compute_accuracy_metrics(self, y_true: pd.Series, y_pred: pd.Series, family_labels: dict) -> dict: ...
    def compute_degradation(self, edge_accuracy: float, baseline_accuracy: float) -> float: ...
```

### 4. FailureModeAnalyzer (`src/failure_analyzer.py`)

**Dependencies:** None

```python
class FailureModeAnalyzer:
    def __init__(self, features_df: pd.DataFrame, predictions: pd.Series, ground_truth: pd.Series): ...
    def generate_confusion_matrix(self, family_labels: dict) -> dict: ...
    def analyze_per_family_failures(self, family_labels: dict) -> dict: ...
    def compute_feature_distributions(self, edge_features: pd.DataFrame, baseline_features: pd.DataFrame) -> dict: ...
    def save_failure_report(self, output_path: str): ...
```

### 5. GateDecisionMaker (`src/gate_decision.py`)

**Dependencies:** None

```python
class GateDecisionMaker:
    def __init__(self, thresholds: dict): ...
    def evaluate_gate(self, accuracy_metrics: dict) -> dict: ...
    def generate_recommendation(self, gate_result: dict) -> str: ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CheckpointOnlyExtractor | `sys.path.append('../h-m3/code/src'); from checkpoint_only_extractor import CheckpointOnlyExtractor` | `h-m3/code/src/checkpoint_only_extractor.py` |
| StatisticalFeatureExtractor | `sys.path.append('../h-m3/code/src'); from feature_extractor import StatisticalFeatureExtractor` | `h-m3/code/src/feature_extractor.py` |

**Verified from**: h-m3/code/src (actual implementation)

**Note:** h-e1 classifier assumed to be at `../h-e1/code/results/logistic_classifier.pkl` (fallback: train on-the-fly).

---

## Data Flow

```
Edge Case Models (20) → CheckpointOnlyExtractor (h-m3)
                      ↓
                5D Feature Vectors → Classifier (h-e1)
                      ↓
                Predictions → EdgeCaseEvaluator
                      ↓
                Accuracy Metrics → GateDecisionMaker
                      ↓
                PASS/DOCUMENT Decision

Misclassified Models → FailureModeAnalyzer
                      ↓
                Failure Report (confusion matrix, feature distributions)
```

---

## Configuration Design

### Edge Case Families (`config_h_c1.py`)

```python
EDGE_CASE_FAMILIES = {
    'NormFree': ['nfnet_f0', 'nfnet_f1', 'dm_nfnet_f0', 'nfnet_f2', 'nfnet_f3'],
    'SENet': ['seresnet50', 'senet154', 'legacy_seresnet50', 'seresnet101', 'seresnet152'],
    'RegNet': ['regnetx_032', 'regnety_032', 'regnetx_160', 'regnety_160', 'regnetx_320'],
    'ViT-Extreme': ['vit_giant_patch14_224', 'vit_huge_patch14_224', 'vit_large_patch32_224', 
                    'deit_huge_patch14_224', 'beit_large_patch16_224']
}

GATE_THRESHOLDS = {
    'overall_accuracy_min': 0.70,
    'per_family_pass_count_min': 3,
    'degradation_max': 0.15,
    'baseline_accuracy': 0.85
}

CLASSIFIER_CONFIG = {
    'path': '../h-e1/code/results/logistic_classifier.pkl',
    'fallback_train': True,
    'features': ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']
}

OUTPUT_PATHS = {
    'edge_features_csv': 'results/edge_case_features.csv',
    'predictions_csv': 'results/edge_case_predictions.csv',
    'accuracy_json': 'results/accuracy_by_family.json',
    'confusion_matrix_png': 'results/confusion_matrix.png',
    'feature_distributions_png': 'results/feature_distributions.png',
    'failure_analysis_md': 'results/failure_analysis.md',
    'validation_report_md': 'results/04_validation.md'
}
```

---

## Error Handling Strategy

### Model Availability Failures

```python
# EdgeCaseModelCurator
def validate_timm_availability(self):
    available = []
    missing = []
    for family, models in self.edge_case_families.items():
        for model in models:
            if model in timm.list_models():
                available.append(model)
            else:
                missing.append((family, model))
    
    if len(available) < 12:  # Minimum 3 per family
        raise ValueError(f"Insufficient edge cases: {len(available)}/20")
    
    return {'available': available, 'missing': missing}
```

### Classifier Missing Fallback

```python
# ClassifierLoader
def load_or_train(self, fallback_features_df, fallback_labels):
    try:
        classifier = joblib.load(self.classifier_path)
        logger.info(f"Loaded classifier from {self.classifier_path}")
    except FileNotFoundError:
        logger.warning("Classifier not found, training fallback...")
        classifier = LogisticRegression(random_state=42, max_iter=1000)
        classifier.fit(fallback_features_df, fallback_labels)
        logger.info("Fallback classifier trained")
    
    return classifier
```

### Feature Extraction Failures

```python
# Delegated to h-m3 CheckpointOnlyExtractor
# Handles download retries, skips failed models, logs errors
# Returns failed_models list for reporting
```

---

## Integration Points

### With h-m3 (Feature Extraction)

```python
# main_h_c1.py
sys.path.append('../h-m3/code/src')
from checkpoint_only_extractor import CheckpointOnlyExtractor

extractor = CheckpointOnlyExtractor(cache_dir='../.cache/checkpoints')
edge_results = extractor.extract_batch(edge_case_models)
features_df = edge_results['features']
failed_models = edge_results['failed_models']
```

### With h-e1 (Classifier)

```python
# main_h_c1.py
from src.classifier_loader import ClassifierLoader

loader = ClassifierLoader(classifier_path='../h-e1/code/results/logistic_classifier.pkl')
classifier = loader.load_or_train(
    fallback_features_df=baseline_features,  # From h-m3 standard models
    fallback_labels=baseline_labels
)
```

---

## Output Artifacts

### 1. Edge Case Features (`results/edge_case_features.csv`)

| model_name | bn_count | ln_count | gn_count | no_norm_flag | param_mass_ratio | family_label |
|------------|----------|----------|----------|--------------|------------------|--------------|
| nfnet_f0   | 0        | 0        | 0        | 1            | 0.95             | NormFree     |
| seresnet50 | 45       | 0        | 0        | 0            | 0.92             | SENet        |
| ...        | ...      | ...      | ...      | ...          | ...              | ...          |

### 2. Predictions (`results/edge_case_predictions.csv`)

| model_name | predicted_family | ground_truth | correct |
|------------|------------------|--------------|---------|
| nfnet_f0   | CNN              | NormFree     | False   |
| seresnet50 | CNN              | SENet        | True    |
| ...        | ...              | ...          | ...     |

### 3. Accuracy Breakdown (`results/accuracy_by_family.json`)

```json
{
  "NormFree": {"accuracy": 0.60, "count": 5, "correct": 3},
  "SENet": {"accuracy": 0.80, "count": 5, "correct": 4},
  "RegNet": {"accuracy": 0.75, "count": 5, "correct": 4},
  "ViT-Extreme": {"accuracy": 0.70, "count": 5, "correct": 4},
  "overall_edge": {"accuracy": 0.71, "count": 20, "correct": 15},
  "overall_baseline": {"accuracy": 0.85, "count": 15, "correct": 13},
  "degradation": 0.14,
  "gate_decision": "PASS"
}
```

### 4. Failure Analysis Report (`results/failure_analysis.md`)

```markdown
# Failure Mode Analysis

## Confusion Matrix
(Per-family predicted vs ground truth heatmap)

## Per-Family Failures

### NormFree (2/5 failures)
- nfnet_f0: Predicted CNN (R=0.95, no_norm_flag=1)
- nfnet_f1: Predicted CNN (R=0.96, no_norm_flag=1)

**Pattern:** All NormFree misclassified as CNN despite no_norm_flag=1
**Hypothesis:** Logistic regression coefficient for no_norm_flag is near-zero
**Proposed Fix:** Retrain classifier with balanced edge case representation

## Feature Distributions
(Box plots: edge vs baseline per feature)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C1-1 | Edge Case Curation | Validate TIMM availability for 20 edge case models, assign family labels | 8 | 2+2+2+2 (validate+curate+label+config) |
| C1-2 | Classifier Setup | Load h-e1 classifier or train fallback on standard models | 10 | 3+3+2+2 (load+fallback+test+save) |
| C1-3 | Feature Extraction | Extract 5D features from edge cases using h-m3 extractor | 6 | 2+2+1+1 (import+extract+validate+save) |
| C1-4 | Evaluation Pipeline | Predict families, compute accuracy metrics, per-family breakdown | 12 | 3+3+3+3 (predict+overall+per-family+degradation) |
| C1-5 | Failure Analysis | Generate confusion matrix, feature distributions, failure patterns | 14 | 4+4+3+3 (confusion+distributions+patterns+report) |
| C1-6 | Gate Decision | Evaluate thresholds, generate recommendation, validation report | 8 | 2+2+2+2 (evaluate+recommend+report+summary) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [C1-5], Medium(9-13): [C1-2, C1-4], Low(4-8): [C1-1, C1-3, C1-6]

**Total Complexity:** 58 (typical CONDITION hypothesis)

---

## File Structure

```
docs/youra_research/h-c1/code/
├── config_h_c1.py                      # Edge case families, thresholds, paths
├── main_h_c1.py                        # Orchestrator: curate → extract → predict → analyze
├── src/
│   ├── edge_case_curator.py            # TIMM availability validation, family labels
│   ├── classifier_loader.py            # Load h-e1 classifier or train fallback
│   ├── edge_case_evaluator.py          # Prediction, accuracy metrics, degradation
│   ├── failure_analyzer.py             # Confusion matrix, feature distributions
│   └── gate_decision.py                # Gate evaluation, recommendations
├── results/
│   ├── edge_case_features.csv          # Extracted features (20 models)
│   ├── edge_case_predictions.csv       # Predictions with ground truth
│   ├── accuracy_by_family.json         # Per-family accuracy breakdown
│   ├── confusion_matrix.png            # Confusion matrix visualization
│   ├── feature_distributions.png       # Edge vs baseline distributions
│   ├── failure_analysis.md             # Detailed failure patterns
│   └── 04_validation.md                # Gate decision report
└── requirements.txt                    # Dependencies (reuse h-m3)
```

---

## Validation Protocol

### Step 1: Availability Check
- Validate TIMM availability for all 20 edge case models
- Minimum viable: 12 models (3 per family)
- Fallback: Substitute similar edge cases if missing

### Step 2: Feature Extraction
- Extract 5D features using h-m3 CheckpointOnlyExtractor
- Validate no_norm_flag=1 for NormFree models
- Expected runtime: ~2 minutes (20 models × 1.05s median)

### Step 3: Classification
- Load h-e1 classifier or train fallback
- Predict family labels for all edge cases
- Expected runtime: <1 second

### Step 4: Accuracy Evaluation
- Overall accuracy with 95% Wilson confidence intervals
- Per-family accuracy breakdown
- Degradation = baseline_acc - edge_acc

### Step 5: Failure Analysis
- Confusion matrix per family
- Feature distribution comparison (edge vs baseline)
- Systematic error pattern identification

### Step 6: Gate Decision
- **P1:** Overall accuracy ≥70% → PASS/DOCUMENT
- **P2:** ≥3/4 families pass 70% → PASS/DOCUMENT
- Generate recommendation based on failure patterns

---

## Risk Mitigation

### Risk 1: Edge Case Model Unavailability
**Mitigation:** Pre-validate with `timm.list_models()`, fallback to similar variants  
**Contingency:** Minimum 3 models per family (12 total), document substitutions

### Risk 2: h-e1 Classifier Missing
**Mitigation:** Fallback training on standard models from h-m3  
**Contingency:** Verify fallback accuracy matches h-e1 baseline (>80%)

### Risk 3: Insufficient Statistical Power
**Mitigation:** Report 95% confidence intervals, expand to 30 models if CI >±10%  
**Contingency:** Increase each family from 5 → 7-8 models

### Risk 4: TIMM Naming Ambiguity
**Mitigation:** Manual ground truth labeling, validate assumptions (e.g., no_norm_flag=1 for NormFree)  
**Contingency:** Cross-reference TIMM model cards, inspect checkpoint keys

---

## Performance Targets

| Metric | Target | Justification |
|--------|--------|---------------|
| Total Runtime | <5 minutes | 2 min extraction + 1 sec inference + 2 min analysis |
| Memory Usage | <4 GB | Checkpoint-only (no model instantiation) |
| GPU Requirement | None | CPU-only (h-m3 validated) |
| Code Reuse | 80% | h-m3 extractor (100%), sklearn (100%), new analysis (~150 lines) |

---

## Success Criteria

### Primary (SHOULD_WORK Gate)

**P1:** Overall edge case accuracy ≥70%  
- Computation: `accuracy_score(y_true_edge, y_pred_edge)`
- Decision: PASS if ≥70%, DOCUMENT if <70%

**P2:** At least 3/4 families pass 70% threshold  
- Computation: Count families with accuracy ≥70%
- Decision: PASS if ≥3 families, DOCUMENT if <3

### Secondary (Characterization)

**S1:** Failure mode documentation identifies systematic patterns  
**S2:** `no_norm_flag` shows non-zero importance for edge cases  
**S3:** Parameter-mass ratio R remains discriminative (Cohen's d >0.5)

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Step:** Launch coder-agent (Phase 4 Step 08)
