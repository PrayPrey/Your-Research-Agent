# Architecture: h-m2 - Transfer Stability Correlates with Objective-Independence

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-24
**Author:** Phase 3 Architecture Agent

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Reusing h-e1 curation + h-m1 sweep infrastructure
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-m1/code/`
**Findings**: Reuse DeduplicationFilter, PerplexityFilter (h-e1), ThresholdSweepController (h-m1). Add multi-variant pipeline controller + dependent filter implementations.

**Applied Patterns**: Archon KB - 5-variant comparative experiment pattern, objective-independent vs dependent filter categorization

---

## System Overview

**Pipeline:** C4 Thresholds → 5 Dolly Variants → 5 Fine-Tuned Models → Dual Evaluation → Statistical Analysis → Gate Check

**Execution Model:** Sequential 5-condition pipeline (single GPU, fixed hyperparameters)

**Components:**
- C4ThresholdExtractor (NEW): Parse C4 docs for threshold defaults
- VariantPipelineController (NEW): Orchestrate 5 dataset generation paths
- ObjectiveIndependentFilters (REUSED h-e1): Dedup + perplexity
- ObjectiveDependentFilters (NEW): Domain mixing or instruction quality fallback
- GridSearchTuner (REUSED h-m1): Threshold optimization
- TrainingOrchestrator (REUSED h-e1): LLaMA-2-7B fine-tuning
- EvaluationRunner (REUSED h-e1): lm-evaluation-harness wrapper
- StatisticalAnalyzer (NEW): Bootstrap CIs, Welch's t-test, Cohen's d

**Data Flow:**
```
C4 docs → Extract thresholds → [Baseline, Transferred-Indep, Tuned-Indep, Transferred-Dep, Tuned-Dep]
                                                    ↓
                              5 parallel training runs → MMLU + HellaSwag → Delta computation → Gate
```

---

## Module Interfaces

### C4ThresholdExtractor (`code/extract_c4_thresholds.py`)

**Dependencies:** requests, yaml

```python
class C4ThresholdExtractor:
    def __init__(self, c4_docs_url: str = "https://huggingface.co/datasets/c4"): ...
    
    def extract_deduplication_params(self) -> dict:
        """Parse n-gram size, similarity threshold. Fallback: {ngram: 13, threshold: 0.8}"""
        ...
    
    def extract_perplexity_params(self) -> dict:
        """Parse cutoff, reference LM. Fallback: {cutoff: 1000, model: 'kenlm'}"""
        ...
    
    def extract_domain_ratios(self) -> dict | None:
        """Parse web/news/forums proportions. Return None if unavailable."""
        ...
    
    def save_config(self, output_path: str = "c4_thresholds.yaml"): ...
```

### VariantPipelineController (`code/prepare_dolly_variants.py`)

**Dependencies:** ObjectiveIndependentFilters, ObjectiveDependentFilters, GridSearchTuner

```python
class VariantPipelineController:
    def __init__(self, dolly_data: list[dict], c4_config: dict): ...
    
    def create_baseline(self) -> list[dict]:
        """No filtering. Return raw train split."""
        ...
    
    def create_transferred_indep(self, c4_thresholds: dict) -> list[dict]:
        """Apply C4 dedup + perplexity to Dolly."""
        ...
    
    def create_tuned_indep(self, val_data: list[dict]) -> tuple[list[dict], dict]:
        """Grid search dedup=[0.7,0.8,0.9,0.95], ppl=[500,1000,1500,2000]."""
        ...
    
    def create_transferred_dep(self, c4_config: dict) -> list[dict]:
        """Apply C4 domain ratios OR content filters (fallback)."""
        ...
    
    def create_tuned_dep(self, val_data: list[dict]) -> tuple[list[dict], dict]:
        """Optimize instruction quality filters on validation set."""
        ...
    
    def run_all(self) -> dict:
        """Generate all 5 variants, return {condition: data_path}."""
        ...
```

### ObjectiveIndependentFilters (`code/filters/independent.py`)

**Dependencies:** h-e1 DeduplicationFilter, PerplexityFilter

```python
from h_e1.code.curation import DeduplicationFilter, PerplexityFilter

class ObjectiveIndependentFilters:
    def __init__(self, dedup_threshold: float, ppl_cutoff: float): ...
    
    def apply(self, dataset: list[dict]) -> tuple[list[dict], dict]:
        """Chain dedup → perplexity, return (filtered, stats)."""
        ...
```

### ObjectiveDependentFilters (`code/filters/dependent.py`)

**Dependencies:** numpy

```python
class DomainMixingFilter:
    def __init__(self, target_ratios: dict):
        """target_ratios: {category: proportion}"""
        ...
    
    def apply(self, dataset: list[dict], category_field: str = "category") -> list[dict]:
        """Resample dataset to match target domain ratios."""
        ...

class InstructionQualityFilter:
    def __init__(self, diversity_cutoff: float = 0.5, min_length: int = 10): ...
    
    def compute_prompt_diversity(self, instruction: str) -> float:
        """N-gram diversity score (unique/total trigrams)."""
        ...
    
    def apply(self, dataset: list[dict]) -> tuple[list[dict], dict]:
        """Filter by diversity + length heuristics."""
        ...
```

### GridSearchTuner (`code/tuning/grid_search.py`)

**Dependencies:** h-m1 ThresholdSweepController

```python
from h_m1.code.threshold_sweep import ThresholdSweepController

class GridSearchTuner:
    def __init__(self, train_data: list[dict], val_data: list[dict]): ...
    
    def tune_independent(
        self,
        dedup_range: list[float],
        ppl_range: list[float]
    ) -> tuple[float, float, dict]:
        """Return (best_dedup, best_ppl, all_results)."""
        ...
    
    def tune_dependent(self, filter_type: str) -> tuple[dict, dict]:
        """Optimize domain ratios OR instruction quality params."""
        ...
```

### TrainingOrchestrator (`code/train_llama.py`)

**Dependencies:** h-e1 train.py, transformers

```python
from h_e1.code.train import prepare_instruction_dataset

def train_single_model(
    train_data: list[dict],
    val_data: list[dict],
    output_dir: str,
    model_name: str = "meta-llama/Llama-2-7b-hf",
    epochs: int = 3,
    batch_size: int = 8,
    lr: float = 2e-5,
    seed: int = 42
) -> dict:
    """Fixed hyperparameters per FR-6. Return train_stats."""
    ...

def train_all_variants(variant_data: dict) -> dict:
    """Train 5 models sequentially. Return {condition: checkpoint_path}."""
    ...
```

### EvaluationRunner (`code/evaluate_models.py`)

**Dependencies:** lm_eval, pandas

```python
class EvaluationRunner:
    def __init__(self, lm_eval_path: str = "lm-evaluation-harness"): ...
    
    def run_mmlu(self, model_path: str) -> dict:
        """Run 57 MMLU tasks (14,042 samples). Return {task: accuracy}."""
        ...
    
    def run_hellaswag(self, model_path: str) -> float:
        """Run HellaSwag validation (10,042 samples). Return accuracy."""
        ...
    
    def evaluate_all(self, checkpoints: dict) -> pd.DataFrame:
        """Evaluate 5 models on both benchmarks. Return results/scores.csv."""
        ...
```

### DeltaComputer (`code/compute_deltas.py`)

**Dependencies:** pandas, numpy

```python
class DeltaComputer:
    def __init__(self, scores_df: pd.DataFrame): ...
    
    def compute_transfer_delta(
        self,
        transferred_condition: str,
        tuned_condition: str,
        benchmark: str
    ) -> float:
        """delta = |acc_transferred - acc_tuned| / acc_tuned * 100%"""
        ...
    
    def compute_category_deltas(self) -> dict:
        """Return {independent: delta, dependent: delta} averaged across benchmarks."""
        ...
    
    def save_results(self, output_path: str = "results/transfer_deltas.csv"): ...
```

### StatisticalAnalyzer (`code/statistical_analysis.py`)

**Dependencies:** scipy, numpy

```python
class StatisticalAnalyzer:
    def __init__(self, scores_df: pd.DataFrame, n_bootstrap: int = 10000): ...
    
    def bootstrap_ci(self, condition: str, benchmark: str, alpha: float = 0.05) -> tuple[float, float]:
        """Compute 95% CI via bootstrap resampling."""
        ...
    
    def welch_ttest(self, independent_deltas: list[float], dependent_deltas: list[float]) -> dict:
        """Return {statistic, pvalue}."""
        ...
    
    def cohens_d(self, independent_deltas: list[float], dependent_deltas: list[float]) -> float:
        """Effect size for category separation."""
        ...
    
    def run_full_analysis(self) -> dict:
        """Bootstrap CIs + t-test + Cohen's d. Save to results/statistical_analysis.yaml."""
        ...
```

### GateChecker (`code/gate_check.py`)

**Dependencies:** yaml

```python
class GateChecker:
    def __init__(self, deltas: dict, stats: dict): ...
    
    def check_primary_criteria(self) -> dict:
        """independent_delta <= 1.0% AND dependent_delta > 5.0%"""
        ...
    
    def check_secondary_criteria(self) -> dict:
        """Non-overlapping CIs, curation benefit >= 2%"""
        ...
    
    def generate_report(self, output_path: str = "results/gate_check.yaml") -> str:
        """Return PASS/FAIL with justification."""
        ...
```

---

## External Dependencies (Base Hypotheses)

### Module Reuse Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DeduplicationFilter | `from h_e1.code.curation import DeduplicationFilter` | `docs/youra_research/h-e1/code/curation.py` |
| PerplexityFilter | `from h_e1.code.curation import PerplexityFilter` | `docs/youra_research/h-e1/code/curation.py` |
| prepare_instruction_dataset | `from h_e1.code.train import prepare_instruction_dataset` | `docs/youra_research/h-e1/code/train.py` |
| ThresholdSweepController | `from h_m1.code.threshold_sweep import ThresholdSweepController` | `docs/youra_research/h-m1/code/threshold_sweep.py` |

**Note**: Import paths assume Python packages or sys.path includes `docs/youra_research/`.

---

## File Organization

```
h-m2/code/
├── extract_c4_thresholds.py       # C4ThresholdExtractor
├── prepare_dolly_variants.py      # VariantPipelineController
├── filters/
│   ├── independent.py             # ObjectiveIndependentFilters wrapper
│   └── dependent.py               # DomainMixingFilter, InstructionQualityFilter
├── tuning/
│   └── grid_search.py             # GridSearchTuner
├── train_llama.py                 # TrainingOrchestrator
├── evaluate_models.py             # EvaluationRunner
├── compute_deltas.py              # DeltaComputer
├── statistical_analysis.py        # StatisticalAnalyzer
├── gate_check.py                  # GateChecker
└── run_experiment.py              # Main pipeline script

h-m2/data/
├── c4_thresholds.yaml             # Extracted C4 config
├── dolly_splits/                  # train.jsonl (13,513), val.jsonl (1,502)
├── dolly_variants/                # 5 condition folders
│   ├── baseline/
│   ├── transferred_indep/
│   ├── tuned_indep/
│   ├── transferred_dep/
│   └── tuned_dep/
└── tuning_logs/                   # independent.yaml, dependent.yaml

h-m2/models/                       # 5 × 13GB checkpoints
├── baseline/
├── transferred_indep/
├── tuned_indep/
├── transferred_dep/
└── tuned_dep/

h-m2/results/
├── mmlu_scores.csv                # 5 models × 57 tasks
├── hellaswag_scores.csv           # 5 models × 1 score
├── transfer_deltas.csv            # Independent vs dependent deltas
├── statistical_analysis.yaml      # CIs, p-values, Cohen's d
└── gate_check.yaml                # PASS/FAIL decision
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | C4 extraction → Dolly splits → 5 variant generation → tuning | 17 | 2+2+4+5+4 (Module:2, Dedup:2, Tuning:4, DepFilters:5, Integration:4) |
| A-2 | Training Pipeline | Environment setup → 5 parallel fine-tuning runs → checkpointing | 12 | 3+6+3 (Setup:3, Training:6, Monitoring:3) |
| A-3 | Evaluation Pipeline | lm-eval setup → MMLU/HellaSwag → delta computation → stats | 15 | 3+5+4+3 (LMEval:3, Benchmarks:5, Deltas:4, Stats:3) |
| A-4 | Validation | Gate check → failure analysis → report generation | 8 | 2+3+3 (Criteria:2, Analysis:3, Report:3) |

**Distribution**: High(14-17): [A-1, A-3], Medium(9-13): [A-2], Low(4-8): [A-4]

**Total Complexity**: 52 (target range for MECHANISM gate)

---

## Epic Task Breakdown

### A-1: Data Pipeline (Complexity: 17)

**Objective:** Generate 5 Dolly variants with documented filtering steps

**Dependencies:** C4 docs, Dolly-15k HF dataset, h-e1 filters, h-m1 sweep

**Subtasks:**
1. **C4 threshold extraction** (2): Parse docs, implement fallback defaults, save YAML
2. **Dolly preprocessing** (2): Load dataset, 90/10 split, verify format
3. **Baseline + transferred variants** (4): No-op baseline, apply C4 dedup/perplexity, apply C4 domain filters
4. **Tuned variant generation** (5): Grid search independent (16 configs), optimize dependent filters, log results
5. **Pipeline integration** (4): VariantPipelineController, parallel execution, stats logging

**Deliverables:**
- `c4_thresholds.yaml`
- `dolly_splits/train.jsonl`, `dolly_splits/val.jsonl`
- `dolly_variants/{baseline,transferred_indep,tuned_indep,transferred_dep,tuned_dep}/train.jsonl`
- `tuning_logs/independent.yaml`, `tuning_logs/dependent.yaml`

**Validation:**
- All 5 variants exist with ≥10k training samples
- Tuning logs show grid search exploration
- Independent filters reduce samples by <30%
- Dependent filters maintain category balance

---

### A-2: Training Pipeline (Complexity: 12)

**Objective:** Fine-tune 5 LLaMA-2-7B models with identical hyperparameters

**Dependencies:** A-1 complete, HuggingFace Transformers, A100 GPU access

**Subtasks:**
1. **Environment setup** (3): Install dependencies, load base model, configure training args
2. **5 fine-tuning runs** (6): Sequential training (3 epochs each), validation logging, checkpoint saving
3. **Monitoring** (3): Track loss curves, verify convergence, log GPU usage

**Deliverables:**
- `train_config.yaml` (epochs=3, lr=2e-5, batch=8, grad_accum=8)
- `models/{condition}/pytorch_model.bin` (5 × ~13GB)
- `models/{condition}/training_log.json` (loss, val perplexity per epoch)

**Validation:**
- All 5 models complete 3 epochs without OOM errors
- Validation perplexity decreases for all conditions
- Checkpoints loadable by HuggingFace Transformers
- Total GPU time <25 hours

---

### A-3: Evaluation Pipeline (Complexity: 15)

**Objective:** Benchmark all models → compute deltas → statistical analysis

**Dependencies:** A-2 complete, lm-evaluation-harness, scipy

**Subtasks:**
1. **lm-eval setup** (3): Install harness, configure MMLU + HellaSwag tasks, test single model
2. **Benchmark execution** (5): Run MMLU (14k samples × 5 models), run HellaSwag (10k samples × 5 models), aggregate scores
3. **Delta computation** (4): Implement transfer delta formula, compute independent vs dependent deltas, average across benchmarks
4. **Statistical analysis** (3): Bootstrap 95% CIs (10k resamples), Welch's t-test, Cohen's d

**Deliverables:**
- `results/mmlu_scores.csv` (columns: condition, task, accuracy)
- `results/hellaswag_scores.csv` (columns: condition, accuracy)
- `results/transfer_deltas.csv` (columns: category, delta_mmlu, delta_hellaswag, delta_avg)
- `results/statistical_analysis.yaml` (CIs, p-value, Cohen's d)

**Validation:**
- MMLU: all conditions show accuracy in [0.2, 0.7] range (sanity check)
- HellaSwag: all conditions show accuracy in [0.3, 0.8] range
- Deltas computed correctly: |(transferred - tuned) / tuned| × 100%
- CIs non-overlapping → p < 0.05

---

### A-4: Validation (Complexity: 8)

**Objective:** Check SHOULD_WORK gate criteria → generate report

**Dependencies:** A-3 complete

**Subtasks:**
1. **Gate criteria check** (2): Independent delta ≤1%, dependent delta >5%, CI separation
2. **Failure mode analysis** (3): Check for reversal, overlap, insufficient separation
3. **Report generation** (3): Document hypothesis support, plot delta comparison, summarize findings

**Deliverables:**
- `results/gate_check.yaml` (status: PASS/FAIL, criteria met: bool, justification: str)
- `h-m2/04_validation.md` (hypothesis statement, results summary, gate decision, failure analysis if applicable)

**Validation:**
- Gate check automated (no manual threshold adjustments)
- Report includes all required plots (delta bar chart, CI intervals)
- PASS conditions: all primary + secondary criteria met
- FAIL conditions: documented with root cause analysis

---

## PoC Constraints & Mock Fallbacks

**GPU unavailability:**
- Substitute LLaMA-2-7B → GPT-2 355M (reduces checkpoint size to 5 × 1.5GB)
- Reduce Dolly samples: use 5k training samples (still statistically valid for delta detection)

**C4 thresholds undocumented:**
- Use literature defaults: dedup threshold=0.8 (13-gram), perplexity=1000 (KenLM 5-gram)
- Focus on categorical comparison (independent vs dependent), not absolute transfer

**Dolly lacks multi-source variant:**
- Fallback to InstructionQualityFilter as objective-dependent technique
- Justify in 04_validation.md: task-specific filter still requires stage alignment

**Excessive sample removal:**
- Monitor filtered counts in VariantPipelineController
- Relax thresholds if filtered samples <10k (ensure statistical power)

---

## Acceptance Criteria

**PoC complete when:**
1. All 5 dataset variants generated with logged filter statistics
2. All 5 fine-tuning runs complete without errors
3. MMLU + HellaSwag scores available for all models
4. Transfer deltas computed with bootstrap CIs
5. Gate check executed → results/gate_check.yaml exists
6. 04_validation.md report generated

**Gate passes (SHOULD_WORK) when:**
- Objective-independent delta ≤ 1.0% (MMLU AND HellaSwag)
- Objective-dependent delta > 5.0% (MMLU AND HellaSwag)
- 95% CIs non-overlapping between categories
- Welch's t-test: p < 0.05

**Gate fails (triggers taxonomy refinement) when:**
- Deltas overlap (no categorical separation)
- Independent delta > 5% (hygiene not universal)
- Dependent delta < 1% (strategy unexpectedly robust)
- Both categories show <1% or >5% (distinction invalid)

---

## Implementation Notes

**Reproducibility:**
- Fixed seeds: data splits (42), training (42), bootstrap (123)
- Versioned dependencies: transformers==4.30.0, lm-eval==0.4.0
- Log all hyperparameters in train_config.yaml

**Storage optimization:**
- Delete intermediate checkpoints (keep final epoch only)
- Compress tuning logs (YAML format)
- Use float16 for model inference (halve memory usage)

**Execution order:**
1. Extract C4 thresholds (1 hour)
2. Generate 5 variants (2 hours including tuning)
3. Train 5 models sequentially (15-20 GPU hours)
4. Evaluate benchmarks (5 hours)
5. Statistical analysis + gate check (30 minutes)

**Total timeline:** 2 days (with GPU access)

---

**Document Status:** Phase 3 Complete
**Next Phase:** Phase 4 - Coding & Validation
**Estimated LoC:** ~1200 (400 new + 800 reused from h-e1/h-m1)
