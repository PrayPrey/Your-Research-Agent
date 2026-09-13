# System Architecture: H-M1 Gradient Flow Feature Validation

**Hypothesis:** H-M1  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Architecture Agent (Phase 3)

---

## 1. Architecture Overview

### 1.1 System Purpose
Validate gradient accumulation mechanism by extracting layer-wise progression features from pretrained CNNs and comparing classification performance against H-E1 baseline.

### 1.2 Design Philosophy
- **Minimal Infrastructure (LIGHT tier):** Reuse H-E1 proven components, replace only feature extractor
- **Controlled Experiment:** Identical pipeline to H-E1 except feature extraction
- **Mechanism Isolation:** Gradient-flow features only (no global statistics)

### 1.3 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    H-M1 Experiment Pipeline                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Model Loader] → [Gradient Flow Feature Extractor]         │
│       ↓                       ↓                              │
│  20 Pretrained Models → 6 Features per Model                │
│                               ↓                              │
│                    [StandardScaler Normalization]            │
│                               ↓                              │
│                    [Logistic Regression Classifier]          │
│                               ↓                              │
│              [Evaluation: Accuracy, Confusion Matrix]        │
│                               ↓                              │
│                    [Visualization & Metrics Export]          │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Reused from H-E1: Model Loader, Classifier, Evaluation, Output
New for H-M1: Gradient Flow Feature Extractor
```

---

## 2. Codebase Analysis (Serena)

**Analysis Source:** H-E1 base hypothesis codebase review

### 2.1 H-E1 Code Structure (Base Hypothesis)

```
h-e1/code/
├── main.py                    # Entry point, orchestrates pipeline
├── model_loader.py            # Load 20 torchvision models
├── feature_extractor.py       # GlobalStatisticsExtractor (4 features)
├── classifier.py              # LogisticRegression + StandardScaler
├── evaluate.py                # Metrics computation
├── visualize.py               # Figure generation
└── outputs/
    ├── metrics.json           # Test accuracy, confusion matrix
    └── figures/               # PNG visualizations
```

**Key Findings from H-E1:**
- Model loader handles auto-download gracefully
- Feature extraction takes <5 seconds for 20 models
- Classifier converges in <1 second (16 training samples)
- StandardScaler configuration: `StandardScaler()` (default params)
- LogisticRegression configuration: `LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000)`

### 2.2 Reuse Strategy

**Import from H-E1:**
```python
# Reuse H-E1 modules directly (minimal/no modification)
from h_e1.code.model_loader import load_pretrained_models, SHALLOW_MODELS, DEEP_MODELS
from h_e1.code.classifier import train_classifier, make_predictions
from h_e1.code.evaluate import compute_metrics, save_metrics
from h_e1.code.visualize import plot_confusion_matrix
```

**Replace for H-M1:**
```python
# New gradient-flow feature extractor
from feature_extractor import GradientFlowFeatureExtractor
```

### 2.3 External Dependencies (Verified from H-E1)

**Import Paths (Actual Code):**
- `torch.nn.modules.conv.Conv2d` for conv layer detection
- `torch.nn.modules.linear.Linear` for fc layer detection
- `torch.linalg.norm(tensor, ord='fro')` for Frobenius norm
- `sklearn.linear_model.LogisticRegression`
- `sklearn.preprocessing.StandardScaler`
- `sklearn.metrics.accuracy_score, confusion_matrix, classification_report`

**Applied:** H-E1 import pattern reuse (verified working implementation)

---

## 3. Module Design

### 3.1 Module Hierarchy

```
h_m1/
├── main.py                           # Experiment orchestrator
├── feature_extractor.py              # GradientFlowFeatureExtractor (NEW)
├── random_init_test.py               # Random model initialization test (NEW)
├── visualize_comparison.py           # H-E1 vs H-M1 comparison plots (NEW)
├── model_loader.py -> h_e1/          # Symlink to H-E1 (reuse)
├── classifier.py -> h_e1/            # Symlink to H-E1 (reuse)
├── evaluate.py -> h_e1/              # Symlink to H-E1 (reuse)
└── outputs/
    ├── metrics.json
    └── figures/
```

**Design Rationale:**
- Symlinks to H-E1 modules enforce code reuse (no divergence)
- New modules isolate H-M1-specific logic (feature extraction, random test, comparison viz)
- Same output structure as H-E1 for consistency

### 3.2 Data Flow

```
Step 1: Load Models
  Input: torchvision.models API
  Output: 20 pretrained model objects
  Module: model_loader.py (H-E1)

Step 2: Extract Gradient-Flow Features
  Input: Model objects
  Output: (20, 6) numpy array
  Module: feature_extractor.py (NEW)
  
  For each model:
    - Iterate through parameters
    - Extract layer-wise Frobenius norms + positions
    - Compute 6 gradient-flow features

Step 3: Normalize Features
  Input: (20, 6) feature array
  Output: (20, 6) normalized array
  Module: classifier.py (H-E1)
  Method: StandardScaler.fit_transform()

Step 4: Train-Test Split
  Input: 20 models (10 shallow, 10 deep)
  Output: 16 train, 4 test (stratified)
  Module: classifier.py (H-E1)
  Config: random_state=42

Step 5: Train Classifier
  Input: (16, 6) train features + labels
  Output: Trained LogisticRegression
  Module: classifier.py (H-E1)

Step 6: Evaluate
  Input: (4, 6) test features + labels
  Output: Accuracy, confusion matrix, classification report
  Module: evaluate.py (H-E1)

Step 7: Random Model Test (Optional)
  Input: Random initialized models (same architectures)
  Output: Test accuracy on random models
  Module: random_init_test.py (NEW)

Step 8: Visualize
  Input: Metrics, feature importance
  Output: PNG figures
  Module: visualize_comparison.py (NEW)
```

---

## 4. File Organization

### 4.1 Directory Structure

```
h-m1/
├── code/
│   ├── main.py                        # Entry point
│   ├── feature_extractor.py           # Gradient flow extractor (NEW)
│   ├── random_init_test.py            # Random init validation (NEW)
│   ├── visualize_comparison.py        # H-E1 vs H-M1 plots (NEW)
│   ├── model_loader.py -> ../../h-e1/code/model_loader.py
│   ├── classifier.py -> ../../h-e1/code/classifier.py
│   ├── evaluate.py -> ../../h-e1/code/evaluate.py
│   └── outputs/
│       ├── metrics.json               # Test accuracy, confusion matrix
│       └── figures/
│           ├── accuracy_comparison.png        # H-E1 vs H-M1 vs Random
│           ├── feature_importance.png         # Coefficient magnitudes
│           ├── confusion_matrix.png
│           ├── layer_progression.png          # Shallow vs deep norm progression
│           └── feature_distributions.png      # Box plots per feature
├── 03_prd.md
├── 03_architecture.md (this file)
├── 03_logic.md
├── 03_config.md
└── 03_tasks.yaml
```

### 4.2 Configuration Files

**Config Schema:** Hardcoded in main.py (LIGHT tier, no YAML config)

```python
# main.py configuration
CONFIG = {
    "random_seed": 42,
    "train_test_split": 0.8,
    "classifier": {
        "type": "LogisticRegression",
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 1000
    },
    "feature_scaler": "StandardScaler",
    "output_dir": "outputs",
    "run_random_test": True  # Enable random initialization test
}
```

---

## 5. Proposed Tasks (Epic Level)

### Epic E-1: Environment Setup
**ID:** E-1  
**Priority:** 100  
**Complexity:** 4/20  
**Breakdown:** Module=1, Dependencies=1, Algorithm=0, Integration=2  
**Description:** Install dependencies and verify H-E1 codebase access.

**Acceptance Criteria:**
- Python packages installed (torch, torchvision, sklearn, numpy, matplotlib)
- H-E1 code directory readable
- Symlinks created successfully

**Reference Files:**
- 03_prd.md#section-7-dependencies

---

### Epic E-2: Gradient Flow Feature Extractor
**ID:** E-2  
**Priority:** 95  
**Complexity:** 16/20  
**Breakdown:** Module=4, Dependencies=2, Algorithm=8, Integration=2  
**Description:** Implement `GradientFlowFeatureExtractor` class to compute 6 gradient-flow features.

**Acceptance Criteria:**
- Extract layer-wise Frobenius norms with position tracking
- Compute norm progression slope via `np.polyfit(positions, norms, deg=1)`
- Calculate norm variance, input/output norms, depth-weighted norm, layer count
- Output: (6,) numpy array per model
- Process 20 models in <5 seconds

**Reference Files:**
- 03_prd.md#fr-1-gradient-flow-feature-extractor
- 03_logic.md#api-gradientflowfeatureextractor
- 02c_experiment_brief.md#core-mechanism-implementation

**Subtasks:** See 03_logic.md for API details

---

### Epic E-3: Main Experiment Pipeline
**ID:** E-3  
**Priority:** 90  
**Complexity:** 12/20  
**Breakdown:** Module=3, Dependencies=3, Algorithm=2, Integration=4  
**Description:** Orchestrate full experiment: load models → extract features → train → evaluate → visualize.

**Acceptance Criteria:**
- Reuse H-E1 model loader (20 models)
- Call GradientFlowFeatureExtractor for all models
- Train LogisticRegression classifier (16 train, 4 test)
- Compute test accuracy, confusion matrix
- Save metrics to metrics.json
- Total runtime <60 seconds

**Reference Files:**
- 03_prd.md#fr-2-model-loader
- 03_prd.md#fr-3-binary-classifier
- 03_prd.md#fr-4-evaluation-pipeline
- 03_logic.md#main-pipeline

---

### Epic E-4: Random Initialization Test
**ID:** E-4  
**Priority:** 85  
**Complexity:** 14/20  
**Breakdown:** Module=3, Dependencies=2, Algorithm=6, Integration=3  
**Description:** Initialize same 20 architectures with random weights, extract gradient-flow features, train classifier to verify training-induced patterns.

**Acceptance Criteria:**
- Create random initialized models (same architectures as pretrained)
- Extract gradient-flow features from random models
- Train classifier on random model features
- Expected: <55% accuracy (fail to classify)
- Compare random vs pretrained accuracy

**Reference Files:**
- 03_prd.md#fr-5-random-initialization-test
- 03_logic.md#random-initialization-test

---

### Epic E-5: Visualization and Comparison
**ID:** E-5  
**Priority:** 80  
**Complexity:** 10/20  
**Breakdown:** Module=2, Dependencies=1, Algorithm=3, Integration=4  
**Description:** Generate comparison visualizations (H-E1 vs H-M1 vs Random baseline).

**Acceptance Criteria:**
- **Mandatory:** Test accuracy bar chart (H-E1=100%, H-M1=?, Random=50%)
- **Optional:** Layer-wise norm progression plot (shallow vs deep)
- **Optional:** Feature importance comparison (H-E1's 4 features vs H-M1's 6 features)
- **Optional:** Confusion matrix, feature distribution box plots
- Save all figures to `outputs/figures/`

**Reference Files:**
- 03_prd.md#fr-6-visualization-generation
- 03_logic.md#visualization-module
- 03_config.md#visualization-settings

---

### Epic E-6: Failsafe - Pipeline Continuation Checkpoint
**ID:** E-6  
**Priority:** 1  
**Complexity:** 2/20  
**Breakdown:** Module=1, Dependencies=0, Algorithm=0, Integration=1  
**Description:** Verify all outputs exist and experiment completed successfully before Phase 4.5.

**Acceptance Criteria:**
- Check metrics.json exists
- Verify mandatory figure (accuracy_comparison.png) exists
- Log completion status

**Reference Files:**
- 03_prd.md#acceptance-criteria-summary

---

## 6. Integration Points

### 6.1 H-E1 Integration

**Dependency Type:** Code Reuse (Base Hypothesis)

**Integration Method:**
- Symlink H-E1 modules into H-M1 code directory
- Import H-E1 functions directly
- Use identical configuration (classifier, scaler, random seed)

**Verified Import Paths (from H-E1 actual code):**
```python
# From h-e1/code/model_loader.py
SHALLOW_MODELS = ["resnet18", "resnet34", ...]  # 10 models
DEEP_MODELS = ["resnet50", "resnet101", ...]    # 10 models

def load_pretrained_models() -> Dict[str, torch.nn.Module]:
    """Returns {model_name: model_object} for all 20 models"""
    pass

# From h-e1/code/classifier.py
def train_classifier(features: np.ndarray, labels: np.ndarray, config: dict):
    """Returns (trained_model, scaler)"""
    pass
```

**Applied:** Reuse H-E1 codebase with minimal wrapper (symlinks + imports)

### 6.2 External Libraries

**PyTorch Integration:**
- Model loading: `torchvision.models.{model_name}(pretrained=True)`
- Layer iteration: `model.named_parameters()` or `model.modules()`
- Norm computation: `torch.linalg.norm(param.data, ord='fro')`

**Scikit-learn Integration:**
- Classifier: `LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000)`
- Scaler: `StandardScaler().fit_transform(features)`
- Metrics: `accuracy_score(y_true, y_pred)`

---

## 7. Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **DL Framework** | PyTorch | ≥2.0.0 | H-E1 compatibility, torchvision models |
| **Model Zoo** | torchvision | ≥0.15.0 | Pretrained CNN weights |
| **Classifier** | scikit-learn | ≥1.3.0 | LogisticRegression, StandardScaler |
| **Numerics** | NumPy | ≥1.24.0 | Feature array operations |
| **Visualization** | Matplotlib | ≥3.7.0 | Figure generation |
| **Language** | Python | ≥3.9 | H-E1 compatibility |

---

## 8. Complexity Analysis

### 8.1 Task Breakdown Summary

| Epic ID | Title | Complexity | Type |
|---------|-------|------------|------|
| E-1 | Environment Setup | 4/20 (Low) | setup |
| E-2 | Gradient Flow Feature Extractor | 16/20 (High) | implementation |
| E-3 | Main Experiment Pipeline | 12/20 (Medium) | implementation |
| E-4 | Random Initialization Test | 14/20 (High) | validation |
| E-5 | Visualization and Comparison | 10/20 (Medium) | analysis |
| E-6 | Failsafe Checkpoint | 2/20 (Low) | validation |
| **Total** | **6 Epic Tasks** | **58/120** | **FULL Tier** |

**Budget Compliance:**
- Epic Range: 6 tasks (within FULL tier 6-12 range ✓)
- Infrastructure: Standard (LIGHT reuse + H-M1 extensions)
- Total Complexity: 58 (moderate for FULL tier)

### 8.2 Critical Path

```
E-1 (Setup) → E-2 (Feature Extractor) → E-3 (Main Pipeline) → E-4 (Random Test) → E-5 (Visualization) → E-6 (Failsafe)
```

**Estimated Duration:** 1-2 hours (implementation) + <1 minute (runtime)

---

## 9. Risk Analysis

| Risk | Mitigation |
|------|------------|
| H-E1 symlinks break | Copy files instead of symlink if filesystem doesn't support |
| Random models classify well | Document as architectural mechanism dominance (expected finding) |
| Gradient features perform poorly | Primary gate is >50% (not 100%), partial contribution acceptable |
| Feature extraction too slow | Optimize by caching norms, use batch processing |

---

## 10. Architecture Validation

**Checklist:**
- ✅ Reuses H-E1 proven components (model loader, classifier, evaluation)
- ✅ Isolates H-M1-specific logic (gradient-flow feature extractor)
- ✅ Within FULL tier budget (6 Epic tasks, 6-12 range)
- ✅ Modular design (easy to swap feature extractors)
- ✅ Controlled experiment (identical pipeline except features)
- ✅ Clear integration points with H-E1
- ✅ External dependencies verified from H-E1 codebase

**Applied:** Architecture pattern from research experiment best practices (Archon KB: controlled hypothesis testing)

---

*Architecture Document v1.0 | Generated by Phase 3 Architecture Agent | Hypothesis: H-M1*
