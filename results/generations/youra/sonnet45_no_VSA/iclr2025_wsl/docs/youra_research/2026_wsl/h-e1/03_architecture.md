# Architecture Design: H-E1 Statistical Features Sufficiency

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-07-11  
**Applied Pattern:** sklearn pipeline + state_dict parsing  

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing code to analyze - clean implementation

---

## Design Philosophy

EXISTENCE architecture - minimal structure to test "does it work?"
- Single-file modules (no complex abstractions)
- Sequential pipeline (no parallelization needed)
- CPU-only processing (no GPU infrastructure)
- Direct CSV storage (no database layer)

---

## Module Structure

### 1. DataLoader (`src/data_loader.py`)

**Dependencies:** timm, torch, pandas

```python
class TIMMDataLoader:
    def __init__(self, model_families: dict, random_seed: int = 42): ...
    def download_models(self) -> list[tuple[str, str, dict]]: ...
    def create_splits(self, data: list, test_size: float = 0.3) -> tuple[pd.DataFrame, pd.DataFrame]: ...
    def save_features(self, train_df: pd.DataFrame, val_df: pd.DataFrame, output_dir: str): ...
```

**Interface:**
- `download_models()` → [(model_name, family, state_dict), ...]
- `create_splits()` → (train_df, val_df) with stratification
- `save_features()` → CSV files to disk

---

### 2. FeatureExtractor (`src/feature_extractor.py`)

**Dependencies:** torch, re, numpy

```python
class StatisticalFeatureExtractor:
    def extract_features(self, state_dict: dict) -> dict: ...
    def _count_normalization_layers(self, state_dict: dict) -> dict: ...
    def _compute_param_mass_ratio(self, state_dict: dict) -> float: ...
    def _is_conv_weight(self, tensor: torch.Tensor) -> bool: ...
    def _is_linear_weight(self, tensor: torch.Tensor) -> bool: ...
    def _exclude_head_keys(self, key: str) -> bool: ...
```

**Interface:**
- `extract_features(state_dict)` → {bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio}

---

### 3. AssumptionValidator (`src/assumption_validator.py`)

**Dependencies:** pandas, numpy

```python
class AssumptionValidator:
    def __init__(self, train_df: pd.DataFrame): ...
    def validate_a1_naming_alignment(self, sample_size: int = 10) -> dict: ...
    def validate_a2_normalization_convention(self) -> dict: ...
    def validate_a3_scale_invariance(self, family_models: list[str]) -> dict: ...
    def save_validation_results(self, output_path: str): ...
```

**Interface:**
- `validate_a1_naming_alignment()` → {passed: bool, alignment_rate: float}
- `validate_a2_normalization_convention()` → {passed: bool, cnn_ln_rate: float, trans_bn_rate: float}
- `validate_a3_scale_invariance()` → {passed: bool, cv: float}

---

### 4. ClassifierTrainer (`src/classifier_trainer.py`)

**Dependencies:** sklearn, pandas, joblib

```python
class LogisticClassifierTrainer:
    def __init__(self, random_state: int = 42): ...
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> tuple: ...
    def save_artifacts(self, classifier, scaler, output_dir: str): ...
    def load_artifacts(self, model_dir: str) -> tuple: ...
```

**Interface:**
- `train(X_train, y_train)` → (classifier, scaler)
- `save_artifacts()` → classifier.pkl, scaler.pkl
- `load_artifacts()` → (classifier, scaler)

---

### 5. Evaluator (`src/evaluator.py`)

**Dependencies:** sklearn, pandas, matplotlib

```python
class ValidationEvaluator:
    def __init__(self, classifier, scaler): ...
    def evaluate(self, X_val: pd.DataFrame, y_val: pd.Series) -> dict: ...
    def generate_confusion_matrix(self, y_true, y_pred, output_path: str): ...
    def generate_feature_importance(self, feature_names: list, output_path: str): ...
    def generate_r_distribution(self, val_df: pd.DataFrame, output_path: str): ...
    def get_misclassified_models(self, val_df: pd.DataFrame, y_pred) -> pd.DataFrame: ...
```

**Interface:**
- `evaluate()` → {macro_accuracy, per_class_accuracy, confusion_matrix}
- `generate_confusion_matrix()` → PNG plot
- `generate_feature_importance()` → PNG plot
- `generate_r_distribution()` → PNG plot

---

### 6. ReportGenerator (`src/report_generator.py`)

**Dependencies:** pandas

```python
class ResultsReporter:
    def __init__(self, results: dict, assumptions: dict): ...
    def generate_markdown_report(self, output_path: str): ...
    def _format_confusion_matrix_table(self, conf_matrix) -> str: ...
    def _format_feature_importance_table(self, importance) -> str: ...
    def _format_failure_cases(self, misclassified_df) -> str: ...
```

**Interface:**
- `generate_markdown_report()` → results/h_e1_results.md

---

### 7. Pipeline Orchestrator (`main.py`)

**Dependencies:** All above modules

```python
class ExperimentPipeline:
    def __init__(self, config: dict): ...
    def run_data_preparation(self): ...
    def run_assumption_validation(self): ...
    def run_training(self): ...
    def run_evaluation(self): ...
    def run_reporting(self): ...
    def execute_full_pipeline(self): ...
```

**Interface:**
- `execute_full_pipeline()` → End-to-end execution

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── data_loader.py           # Module 1
│   │   ├── feature_extractor.py     # Module 2
│   │   ├── assumption_validator.py  # Module 3
│   │   ├── classifier_trainer.py    # Module 4
│   │   ├── evaluator.py             # Module 5
│   │   └── report_generator.py      # Module 6
│   ├── main.py                      # Module 7 - Orchestrator
│   ├── config.py                    # Model selection + hyperparameters
│   └── requirements.txt
├── data/
│   ├── model_list.json              # 60 model names + families
│   ├── train_features.csv           # 42 models
│   ├── val_features.csv             # 18 models
│   └── assumption_validation.json   # A1/A2/A3 results
├── models/
│   ├── classifier.pkl
│   └── scaler.pkl
├── results/
│   ├── confusion_matrix.png
│   ├── feature_importance.png
│   ├── r_distribution.png
│   └── h_e1_results.md
└── logs/
    └── experiment_log.txt
```

---

## Configuration (`code/config.py`)

```python
MODEL_FAMILIES = {
    'CNN': [
        'resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152',
        'mobilenetv3_large_100', 'efficientnet_b0', 'efficientnet_b4',
        'densenet121', 'densenet201', 'vgg16', 'vgg19',
        'convnext_tiny', 'convnext_base',
        'resnext50_32x4d', 'wide_resnet50_2',
        'regnetx_032', 'regnety_032',
        'seresnet50', 'senet154',
        'inception_v3', 'inception_v4',
        'dpn68', 'dpn131'
    ],
    'Transformer': [
        'vit_tiny_patch16_224', 'vit_small_patch16_224', 
        'vit_base_patch16_224', 'vit_large_patch16_224',
        'deit_tiny_patch16_224', 'deit_small_patch16_224',
        'deit_base_patch16_224', 'deit_base_distilled_patch16_224',
        'swin_tiny_patch4_window7_224', 'swin_small_patch4_window7_224',
        'swin_base_patch4_window7_224', 'beit_base_patch16_224',
        'twins_pcpvt_base', 'twins_svt_base', 'cait_s24_224',
        'coat_lite_medium', 'levit_256', 'levit_384',
        'poolformer_m36', 'poolformer_m48',
        'xcit_small_12_p16_224', 'crossvit_base_240'
    ],
    'Hybrid': [
        'resnetv2_50x1_bit_distilled', 'convit_base',
        'pit_b_224', 'pit_s_224', 'cait_xxs24_224',
        'mixer_b16_224', 'mixer_l16_224',
        'convnext_base_in22k', 'twins_pcpvt_small',
        'visformer_small', 'tnt_s_patch16_224', 'maxvit_tiny_tf_224'
    ]
}

FEATURE_NAMES = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

NORM_PATTERNS = {
    'bn': r'bn|batch_norm|batchnorm',
    'ln': r'ln|layer_norm|layernorm',
    'gn': r'gn|group_norm|groupnorm'
}

HEAD_KEYWORDS = ['head', 'fc', 'classifier']

CLASSIFIER_CONFIG = {
    'multi_class': 'multinomial',
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 42,
    'class_weight': 'balanced'
}

SPLIT_CONFIG = {
    'test_size': 0.3,
    'random_state': 42
}

THRESHOLDS = {
    'macro_accuracy': 0.80,
    'per_class_accuracy': 0.75,
    'scale_invariance_cv': 0.15,
    'a1_alignment_rate': 0.90,
    'a2_violation_rate': 0.15
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Setup Project | Create directory structure, install dependencies, initialize config | 4 | 1+1+1+1 (dir+deps+config+verify) |
| E1-2 | Implement Data Pipeline | DataLoader + FeatureExtractor (download, extract, split, save) | 12 | 3+3+3+3 (download+extract+split+save) |
| E1-3 | Implement Validation | AssumptionValidator (A1/A2/A3 tests) | 8 | 2+3+3 (A1+A2+A3) |
| E1-4 | Implement Training | ClassifierTrainer (fit LogisticRegression, save artifacts) | 6 | 2+2+2 (scaler+fit+save) |
| E1-5 | Implement Evaluation | Evaluator (metrics, plots, failure analysis) | 10 | 2+3+3+2 (metrics+confusion+importance+distribution) |
| E1-6 | Implement Reporting | ReportGenerator (markdown generation) | 5 | 2+2+1 (format+write+verify) |
| E1-7 | Pipeline Integration | Orchestrator main.py (end-to-end execution) | 7 | 2+2+2+1 (wire+log+error+test) |

**Total Complexity:** 52 (LIGHT tier for EXISTENCE)

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E1-2, E1-5], Low(4-8): [E1-1, E1-3, E1-4, E1-6, E1-7]

**Task Dependencies:**
- E1-1 → E1-2 (setup before data loading)
- E1-2 → E1-3 (data required for validation)
- E1-2 → E1-4 (data required for training)
- E1-4 → E1-5 (trained model required for evaluation)
- E1-3, E1-5 → E1-6 (validation + evaluation results required for report)
- E1-1 through E1-6 → E1-7 (all modules required for orchestration)

---

## Complexity Breakdown Details

### E1-2: Implement Data Pipeline (12)
- Module_Size: 3 (2 classes, 8 methods total)
- Dependencies: 3 (timm API, torch state_dict, pandas)
- Algorithm: 3 (regex matching, stratification, parameter counting)
- Integration: 3 (TIMM download, CSV save, error handling)

### E1-5: Implement Evaluation (10)
- Module_Size: 2 (1 class, 6 methods)
- Dependencies: 3 (sklearn metrics, matplotlib, pandas)
- Algorithm: 3 (confusion matrix, coefficient analysis, histogram)
- Integration: 2 (plot generation, file I/O)

---

## Integration Points

### Data Flow
1. `main.py` → `DataLoader.download_models()` → model checkpoints
2. `FeatureExtractor.extract_features()` → feature vectors
3. `DataLoader.create_splits()` → train/val CSVs
4. `ClassifierTrainer.train()` → trained artifacts
5. `Evaluator.evaluate()` → metrics + plots
6. `ReportGenerator.generate_markdown_report()` → results document

### File Dependencies
- `data/train_features.csv` → read by `ClassifierTrainer`
- `models/classifier.pkl` → read by `Evaluator`
- `data/assumption_validation.json` → read by `ReportGenerator`
- `results/*.png` → referenced by `ReportGenerator`

---

## Error Handling Strategy

### Data Loading
- Checkpoint download timeout (30 min) → retry once, then skip model
- Missing model → log warning, substitute with similar architecture
- State dict parse error → log error, skip model

### Feature Extraction
- Empty state dict → raise ValueError
- Zero total parameters → set param_mass_ratio = 0.0
- No normalization layers → set no_norm_flag = 1

### Training
- Non-convergence (max_iter exceeded) → log warning, proceed with partial fit
- Singular matrix error → check feature variance, remove constant features

### Evaluation
- Division by zero in CV → handle with np.inf flag
- Plot generation failure → log error, continue without plot

---

## Logging Strategy

**Log File:** `logs/experiment_log.txt`

**Format:**
```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [Module] Message
```

**Levels:**
- INFO: Pipeline progress (started/completed phases)
- WARNING: Non-critical issues (model substitution, plot failure)
- ERROR: Critical failures (data loading error, training failure)
- METRIC: Key metrics (accuracy, CV, violation rates)

**Critical Checkpoints:**
- Data download progress (every 10 models)
- Assumption validation results (A1/A2/A3 pass/fail)
- Training completion (convergence status)
- Validation accuracy (primary metric)
- Decision gate (PASS/FAIL verdict)

---

## Success Validation

### Unit Tests (Not Implemented for PoC)
- Feature extraction: verify ResNet-50 has BN, ViT-Base has LN
- Parameter counting: validate conv vs linear tensor shapes
- Stratification: verify train/val class distribution

### Integration Validation
- End-to-end smoke test: run pipeline on 5-model subset
- Verify CSV format: 42 rows × 7 columns (train), 18 rows × 7 columns (val)
- Verify artifact existence: classifier.pkl, scaler.pkl, 3 PNG plots

### Output Validation
- `h_e1_results.md` contains all required sections
- Confusion matrix is 3×3 with labels [CNN, Transformer, Hybrid]
- Feature importance table has 5 rows

---

## Resource Estimates

### Time Budget (Total: 3-4 hours)
- E1-1 Setup: 30 min
- E1-2 Data Pipeline: 2-3 hours (checkpoint download dominates)
- E1-3 Validation: 5 min
- E1-4 Training: 1 min
- E1-5 Evaluation: 5 min
- E1-6 Reporting: 10 min
- E1-7 Integration: 10 min (already wired during development)

### Memory Budget
- Peak RAM: ~4 GB (loading largest model checkpoint)
- Per-model average: ~200 MB (state dict only, no activations)
- Feature dataset: <1 MB (60 models × 5 features)

### Storage Budget
- Checkpoints: 15 GB (~/.cache/torch/hub/checkpoints/)
- Workspace: 5 GB (code, data, results, logs)
- Total: 20 GB

---

## EXISTENCE Compliance Check

- [x] 4-8 Epic tasks (7 tasks defined)
- [x] Minimal file structure (7 modules, no nested packages)
- [x] No ablation modules (single baseline classifier)
- [x] Basic evaluation only (metrics + plots, no diagnostic suites)
- [x] Fixed configuration (no hyperparameter search)
- [x] CPU-only (no GPU infrastructure)
- [x] Direct storage (CSV files, no databases)

---

## Next Phase Handoff

**For Phase 4 (Coder):**
- Module interfaces defined (7 classes with method signatures)
- File paths specified (absolute from h-e1/code/)
- Dependencies listed (timm, torch, sklearn, pandas, matplotlib)
- Epic tasks with complexity scores (7 tasks, 52 total complexity)
- Configuration centralized (config.py with all constants)

**No Implementation Details Provided:**
- Regex pattern specifics (Coder discretion)
- Matplotlib plot styling (basic defaults acceptable)
- Error message formatting (standard Python exceptions)
- Logging verbosity (INFO level minimum)

**Critical Implementation Note:**
- `FeatureExtractor._count_normalization_layers()` MUST use case-insensitive regex (re.IGNORECASE)
- `FeatureExtractor._exclude_head_keys()` MUST check for 'head', 'fc', 'classifier' substrings
- `DataLoader.create_splits()` MUST use stratify=df['family'] parameter

---

**End of Architecture Document**
