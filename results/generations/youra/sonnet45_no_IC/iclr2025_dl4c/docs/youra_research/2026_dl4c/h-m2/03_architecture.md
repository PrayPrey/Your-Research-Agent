# System Architecture: h-m2
# Phase 2 AI Feedback Peak Validation

**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Date**: 2026-07-12  
**Applied Patterns**: PyTorch Checkpoint Loading, RL Weight Scheduling, Dynamic PPO Configuration

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: patterns found from base code  
**Analyzed Path**: `docs/youra_research/h-m1/code/`  
**Findings**: h-m1 implementation validated (MUST_WORK gate passed). Tri-modal aggregator, Phase 1 PPO trainer, checkpoint logger, and evaluation pipeline operational. Will extend with Phase 2 weight scheduling and quality tracking.

---

## Architecture Overview

**Mission**: Validate Phase 2 AI feedback weight peak hypothesis by extending h-m1 framework to Phase 2 (30-70% progress) with AI-heavy weight scheduling and quality improvement tracking.

**Core Strategy**: Extend h-m1 architecture with Phase 2 components - load 30% checkpoint, continue training with AI peak scheduling, track quality improvement without correctness regression.

**Components**:
1. Data Pipeline (100% reuse from h-m1)
2. Phase2TriModalAggregator (new - AI peak scheduling)
3. Phase2PPOTrainer (extend h-m1 trainer)
4. Phase2Metrics (new - quality tracking, gate validation)
5. Visualization (extend h-m1 visualizer)

---

## Module Structure

### 1. Data Pipeline (`data/dataset.py`)

**Dependencies**: h-m1 implementation (100% reuse)

```python
class CodeGenerationDataset:
    def __init__(self, cache_dir: str = "./.data_cache/datasets"): ...
    def load_datasets(self): ...
    def create_splits(self, train_ratio: float = 0.8, val_ratio: float = 0.1): ...
    def get_dataloader(self, split: str, batch_size: int = 8): ...
```

---

### 2. Phase2TriModalAggregator (`models/phase2_tri_modal_aggregator.py`)

**Dependencies**: h-m1 TriModalAggregator

```python
class Phase2TriModalAggregator(nn.Module):
    def __init__(self, config: dict, phase2_checkpoints: list = [0.30, 0.40, 0.50, 0.60, 0.70]): ...
    def compute_dynamic_weights(self, training_progress: float) -> dict: ...
    def forward(self, exec_r: Tensor, ai_r: Tensor, human_r: Tensor, progress: float) -> Tensor: ...
    def log_phase2_checkpoint(self, progress: float, weights: dict): ...
    def find_ai_weight_peak(self) -> float: ...
```

---

### 3. Phase2PPOTrainer (`train/phase2_ppo_trainer.py`)

**Dependencies**: h-m1 Phase1PPOTrainer, Phase2TriModalAggregator

```python
class Phase2PPOTrainer:
    def __init__(self, checkpoint_path: str, aggregator, feedback_collector, config: dict): ...
    def load_h_m1_checkpoint(self, checkpoint_path: str): ...
    def compute_training_progress(self, current_episode: int, total_episodes: int) -> float: ...
    def train_step(self, batch: dict, current_episode: int) -> dict: ...
    def evaluate_checkpoint(self, dataloader: DataLoader) -> dict: ...
    def train(self, dataloader: DataLoader, total_episodes: int = 10000) -> dict: ...
    def save_checkpoint(self, path: str, progress: float, metrics: dict): ...
```

---

### 4. Feedback Collectors (`models/feedback_collectors.py`)

**Dependencies**: h-m1 implementation (100% reuse)

```python
class FeedbackCollector:
    def __init__(self): ...
    def collect_execution_feedback(self, code: str, test_cases: list) -> float: ...
    def collect_ai_feedback(self, code: str, prompt: str) -> float: ...
    def collect_human_feedback(self, code: str, sample_id: str) -> float: ...
    def collect_all(self, code: str, context: dict) -> dict: ...
```

---

### 5. Phase2Metrics (`evaluation/phase2_metrics.py`)

**Dependencies**: scipy, numpy, h-m1 CheckpointLogger

```python
class Phase2Analyzer:
    def __init__(self, checkpoint_data: dict): ...
    def find_ai_weight_peak(self) -> Tuple[float, dict]: ...
    def compute_quality_improvement_rate(self) -> float: ...
    def compute_correctness_maintenance(self) -> dict: ...
    def validate_gate_criteria(self) -> dict: ...
    def generate_report(self) -> str: ...
```

---

### 6. Quality Evaluator (`evaluation/quality_evaluator.py`)

**Dependencies**: h-m1 human annotation cache

```python
class QualityEvaluator:
    def __init__(self, human_annotation_cache: str): ...
    def load_cached_annotations(self) -> dict: ...
    def evaluate_quality(self, model, dataloader: DataLoader) -> float: ...
    def compute_preference_score(self, generated_code: str, sample_id: str) -> float: ...
```

---

### 7. CodeEvaluator (`evaluation/evaluator.py`)

**Dependencies**: h-m1 implementation (100% reuse)

```python
class CodeEvaluator:
    def __init__(self, timeout: int = 5): ...
    def evaluate_pass_at_1(self, model, dataloader: DataLoader) -> float: ...
    def execute_code(self, code: str, test_cases: list) -> bool: ...
```

---

### 8. Visualization (`utils/visualization.py`)

**Dependencies**: matplotlib, seaborn, h-m1 visualizer

```python
def plot_weight_trajectory_phase2(weight_history: dict, save_path: str): ...
def plot_quality_vs_correctness(quality_history: dict, pass1_history: dict, save_path: str): ...
def plot_phase2_improvement_rates(metrics: dict, save_path: str): ...
def plot_harmonic_mean_progress(harmonic_history: dict, h_m1_baseline: dict, save_path: str): ...
def plot_gate_metrics(metrics: dict, targets: dict, save_path: str): ...
```

---

### 9. Checkpoint Logger (`utils/checkpoint_logger.py`)

**Dependencies**: h-m1 implementation (reuse and extend)

```python
class CheckpointLogger:
    def __init__(self, log_dir: str = "./checkpoints"): ...
    def log_weights(self, progress: float, weights: dict): ...
    def log_quality(self, progress: float, score: float): ...
    def log_pass_at_1(self, progress: float, score: float): ...
    def save_checkpoint_file(self, progress: float, data: dict): ...
    def load_all_checkpoints(self) -> dict: ...
```

---

### 10. Configuration (`config/experiment_config.py`)

**Dependencies**: dataclasses, yaml

```python
@dataclass
class Phase2Config:
    checkpoints: list = field(default_factory=lambda: [0.30, 0.40, 0.50, 0.60, 0.70])
    phase2_start: float = 0.30
    phase2_end: float = 0.70
    ai_peak_progress: float = 0.50
    total_episodes: int = 10000
    eval_samples: int = 104
    
@dataclass
class TrainingConfig:
    h_m1_checkpoint_path: str = "../h-m1/checkpoints/checkpoint_progress_0.30.pt"
    learning_rate: float = 1e-5
    batch_size: int = 64
    seed: int = 42
    device: str = "cuda"
    
def load_config(config_path: str) -> dict: ...
```

---

### 11. Gate Validator (`evaluation/gate_validator.py`)

**Dependencies**: Phase2Metrics

```python
class Phase2GateValidator:
    def __init__(self, weight_trajectory: dict, quality_trajectory: dict, pass1_trajectory: dict): ...
    def validate_gate1_ai_peak(self) -> bool: ...
    def validate_gate2_quality_improved(self) -> bool: ...
    def validate_gate3_correctness_maintained(self) -> bool: ...
    def validate_all_gates(self) -> dict: ...
    def generate_gate_report(self) -> str: ...
```

---

### 12. Main Experiment Runner (`run_h_m2_experiment.py`)

**Dependencies**: All above modules

```python
def setup_environment(seed: int = 42): ...
def load_h_m1_checkpoint(checkpoint_path: str): ...
def run_phase2_experiment(config: dict) -> dict: ...
def main(): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TriModalAggregator | `from h_m1.code.models.tri_modal_aggregator import TriModalAggregator` | `h-m1/code/models/tri_modal_aggregator.py` |
| Phase1AnalysisTriModalAggregator | `from h_m1.code.models.phase1_tri_modal_aggregator import Phase1AnalysisTriModalAggregator` | `h-m1/code/models/phase1_tri_modal_aggregator.py` |
| Phase1PPOTrainer | `from h_m1.code.train.phase1_ppo_trainer import Phase1PPOTrainer` | `h-m1/code/train/phase1_ppo_trainer.py` |
| CodeGenerationDataset | `from h_m1.code.data.dataset import CodeGenerationDataset` | `h-m1/code/data/dataset.py` |
| FeedbackCollector | `from h_m1.code.models.feedback_collectors import FeedbackCollector` | `h-m1/code/models/feedback_collectors.py` |
| CodeEvaluator | `from h_m1.code.evaluation.evaluator import CodeEvaluator` | `h-m1/code/evaluation/evaluator.py` |
| CheckpointLogger | `from h_m1.code.utils.checkpoint_logger import CheckpointLogger` | `h-m1/code/utils/checkpoint_logger.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

---

## File Organization

```
h-m2/
├── code/
│   ├── models/
│   │   └── phase2_tri_modal_aggregator.py    # Phase 2 AI peak weight scheduling
│   ├── train/
│   │   └── phase2_ppo_trainer.py             # Phase 2 PPO trainer (loads h-m1 checkpoint)
│   ├── evaluation/
│   │   ├── phase2_metrics.py                 # Phase 2 analysis metrics
│   │   ├── quality_evaluator.py              # Quality score evaluation
│   │   └── gate_validator.py                 # SHOULD_WORK gate validation
│   ├── utils/
│   │   └── visualization.py                  # Phase 2 visualizations
│   ├── config/
│   │   └── experiment_config.py              # Phase 2 specific config
│   ├── run_h_m2_experiment.py                # Main entry point
│   ├── requirements.txt
│   └── README.md
├── checkpoints/                               # Training checkpoints
│   ├── progress_0.30.json
│   ├── progress_0.40.json
│   ├── progress_0.50.json
│   ├── progress_0.60.json
│   └── progress_0.70.json
├── logs/
│   ├── weights_phase2.csv                    # Weight trajectory data
│   ├── quality_trajectory.csv                # Quality over time
│   └── pass_at_1_trajectory.csv              # Pass@1 over time
└── figures/                                   # Generated visualizations
    ├── gate_metrics.png
    ├── weight_trajectory.png
    ├── quality_vs_correctness.png
    └── harmonic_mean.png
```

---

## Data Flow

**Training Flow**:
1. Load h-m1 dataset (830 train, 104 val, 104 test) → Reuse h-m1 splits
2. Load h-m1 checkpoint at 30% progress
3. Initialize Phase2TriModalAggregator (AI peak scheduling)
4. Initialize Phase2PPOTrainer with loaded checkpoint
5. Training loop:
   - Compute training_progress = (current_episode + 3000) / 10000 (30%→70%)
   - At checkpoints [0.30, 0.40, 0.50, 0.60, 0.70]:
     - Log weight coefficients
     - Evaluate pass@1 and quality on validation set
     - Save checkpoint
   - Standard PPO update with Phase 2 tri-modal reward
6. Post-training analysis via Phase2Analyzer

**Evaluation Flow**:
1. Load all checkpoint data (Phase 2 range)
2. Phase2Analyzer computes:
   - AI weight peak location: argmax(AI_weight) in [30%, 70%]
   - Quality improvement rate: (quality_70% - quality_30%) / 0.40
   - Correctness maintenance: pass1_70% / pass1_30% ≥ 0.95
3. Generate 4 required figures
4. Validate gate criteria (SHOULD_WORK)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Phase2 Aggregator Implementation | Implement Phase2TriModalAggregator with AI peak scheduling | 10 | 3+2+3+2 |
| B-2 | Checkpoint Loader | Load h-m1 checkpoint at 30% and resume training | 7 | 2+2+2+1 |
| B-3 | Phase2 PPO Trainer | Extend PPO trainer for Phase 2 (30-70% range) | 9 | 3+2+2+2 |
| B-4 | Quality Evaluator | Implement quality score evaluation with cached annotations | 8 | 2+2+2+2 |
| B-5 | Phase2 Metrics Module | Implement AI peak detection, quality rate, correctness maintenance | 11 | 3+2+4+2 |
| B-6 | Gate Validator | Implement SHOULD_WORK gate validation logic | 8 | 2+2+2+2 |
| B-7 | Visualization Extension | Create Phase 2 specific plots (weight, quality, harmonic mean) | 9 | 2+2+3+2 |
| B-8 | Integration Testing | Full Phase 2 training run with gate validation | 10 | 2+3+3+2 |

**Total Complexity**: 72 (8 tasks)

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [B-1, B-3, B-5, B-7, B-8]
- Low (4-8): [B-2, B-4, B-6]

---

## Task Details

### B-1: Phase2 Aggregator Implementation (Complexity: 10)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- Implement Phase2TriModalAggregator with Gaussian AI peak at 50% progress
- Weight schedule: AI peak at 50%, execution decay (0.50→0.20), human increase (0.10→0.20)
- Phase 2 checkpoints: [0.30, 0.40, 0.50, 0.60, 0.70]
- Log weights at checkpoints for gate validation
- Detect AI weight peak location

**Acceptance Criteria**:
- AI weight peaks at ~50% progress (mid-Phase 2)
- Weights sum to 1.0 at all progress points (±1e-6 tolerance)
- AI weight is highest among three signals at peak
- Checkpoint logging triggers at exact progress values
- Unit test: verify Gaussian peak shape and normalization

**Files**:
- `models/phase2_tri_modal_aggregator.py`

---

### B-2: Checkpoint Loader (Complexity: 7)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(1)

**Scope**:
- Load h-m1 checkpoint at 30% progress
- Verify checkpoint metadata: training_progress=0.30, phase="Phase 1"
- Extract model state_dict, optimizer state
- Initialize Phase2PPOTrainer with loaded checkpoint
- Device management (CUDA)

**Acceptance Criteria**:
- Checkpoint loads without error
- Metadata verified: progress=0.30
- Model architecture matches h-m1 (CodeGen-350M-mono)
- Pass@1 at 30% verified (~0.616 expected)
- Unit test: verify checkpoint integrity

**Files**:
- `train/phase2_ppo_trainer.py` (load_h_m1_checkpoint method)
- `run_h_m2_experiment.py` (checkpoint loading logic)

---

### B-3: Phase2 PPO Trainer (Complexity: 9)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Extend h-m1 PPO trainer for Phase 2 (30-70% range)
- Adjust training progress computation: (current_episode + 3000) / 10000
- Reduced learning rate: 1e-5 (from Phase 1's 5e-5)
- Checkpoint frequency: Every 1,000 steps (10% increments)
- Evaluation frequency: Every 500 steps

**Acceptance Criteria**:
- Training resumes from 30% checkpoint
- Training progress correctly mapped to 30-70% range
- Checkpoints triggered at [0.30, 0.40, 0.50, 0.60, 0.70]
- Each checkpoint saves: model state, weights, pass@1, quality
- Learning rate schedule: linear decay from 1e-5

**Files**:
- `train/phase2_ppo_trainer.py`

---

### B-4: Quality Evaluator (Complexity: 8)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Implement QualityEvaluator using cached human annotations
- Load h-m1 annotation cache (500 samples with preference scores)
- Evaluate quality on validation set (104 samples)
- Compute average preference score (0-1 range)

**Acceptance Criteria**:
- Annotation cache loaded successfully (500 samples)
- Quality evaluation runs on validation set
- Returns normalized quality score (0-1 range)
- Cache hit rate tracked (samples with annotations)
- Fallback: use AI feedback if annotation missing

**Files**:
- `evaluation/quality_evaluator.py`

---

### B-5: Phase2 Metrics Module (Complexity: 11)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(4) + Integration(2)

**Scope**:
- Phase2Analyzer class for gate validation
- Metric 1: AI weight peak detection - find argmax(AI_weight) in [30%, 70%]
- Metric 2: Quality improvement rate - (quality_70% - quality_30%) / 0.40
- Metric 3: Correctness maintenance - pass1_70% / pass1_30% ≥ 0.95
- Gate validation logic (3 gates)

**Acceptance Criteria**:
- `find_ai_weight_peak()` returns peak location and weights at peak
- `compute_quality_improvement_rate()` returns positive rate (success) or negative (failure)
- `compute_correctness_maintenance()` returns ratio ≥ 0.95 (pass) or < 0.95 (fail)
- `validate_gate_criteria()` returns overall PASS/FAIL decision
- Unit test: verify metrics computation with synthetic data

**Files**:
- `evaluation/phase2_metrics.py`

---

### B-6: Gate Validator (Complexity: 8)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Phase2GateValidator class implementing SHOULD_WORK gate logic
- Gate 1: AI weight is highest at peak (vs execution, human)
- Gate 2: Quality improvement rate > 0
- Gate 3: Correctness maintained (max 5% regression)
- Generate gate validation report

**Acceptance Criteria**:
- `validate_gate1_ai_peak()` checks AI > max(exec, human) at peak
- `validate_gate2_quality_improved()` checks positive improvement rate
- `validate_gate3_correctness_maintained()` checks pass1_70% ≥ 0.95 × pass1_30%
- `validate_all_gates()` returns dict with all gate results
- Report includes: gate status, metric values, overall PASS/FAIL

**Files**:
- `evaluation/gate_validator.py`

---

### B-7: Visualization Extension (Complexity: 9)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- Figure 1: Gate Metrics Bar Chart (mandatory)
- Figure 2: Weight Trajectory (Phase 2 range, highlight AI peak)
- Figure 3: Quality vs. Correctness (dual-axis line plot)
- Figure 4: Harmonic Mean Progress (compare to h-m1 baseline)
- Publication-quality formatting

**Acceptance Criteria**:
- All 4 figures saved to `figures/` as PNG
- Gate metrics figure shows target vs actual (green/red bars)
- Weight trajectory highlights AI peak location (vertical line)
- Quality vs. correctness shows both metrics on same plot (no regression visible)
- Harmonic mean compares h-m2 Phase 2 to h-m1 trajectory

**Files**:
- `utils/visualization.py`

---

### B-8: Integration Testing (Complexity: 10)

**Breakdown**: Module_Size(2) + Dependencies(3) + Algorithm(3) + Integration(2)

**Scope**:
- Full Phase 2 training run (10k episodes, 30%→70%)
- Load h-m1 checkpoint at 30%
- Run Phase 2 training with AI peak scheduling
- Evaluate at all checkpoints (30%, 40%, 50%, 60%, 70%)
- Run gate validation
- Generate all figures

**Acceptance Criteria**:
- Training completes without error
- All checkpoints saved with correct data
- Weight trajectory shows AI peak at ~50%
- Quality improves from 30% to 70%
- Correctness maintained (max 5% regression)
- Gate validation runs successfully
- All 4 figures generated

**Files**:
- `run_h_m2_experiment.py`
- `tests/test_integration.py`

---

## Dependencies & Integration

**External Libraries**:
- PyTorch 2.0+ (same as h-m1)
- Transformers 4.30+ (same as h-m1)
- Datasets 2.12+ (same as h-m1)
- scipy 1.10+ (for metrics)
- matplotlib 3.7+, seaborn 0.12+ (visualization)

**Hardware Requirements**:
- 1x NVIDIA A100 (40GB) or 4x V100 (32GB)
- CUDA 11.8+
- Storage: ~50GB (checkpoints + logs + figures)

**Inter-Module Dependencies**:
```
h-m1 modules (base) → Phase2TriModalAggregator, Phase2PPOTrainer
h-m1 checkpoint (30%) → Phase2PPOTrainer (starting point)
Phase2TriModalAggregator → Phase2PPOTrainer
QualityEvaluator → Phase2PPOTrainer (evaluation)
CheckpointLogger → Phase2PPOTrainer, Phase2Analyzer
Phase2Analyzer → Gate Validator → Visualization
All modules → run_h_m2_experiment
```

---

## Success Criteria

**PoC Pass Conditions**:
1. Code runs without error through full Phase 2 training (10k episodes)
2. All checkpoints logged correctly
3. Quality trajectory tracked

**Gate Validation (SHOULD_WORK)**:
- Primary Criterion 1: AI weight peaks in Phase 2 (30-70%) AND is highest among three signals at peak
- Primary Criterion 2: Quality improvement rate > 0 (positive improvement from 30% to 70%)
- Primary Criterion 3: Correctness maintained (pass1_70% ≥ 0.95 × pass1_30%)

**Gate Decision**:
- PASS: All 3 primary criteria satisfied
- FAIL: Any criterion fails → Re-evaluate AI reward model quality or switch to human-only Phase 2

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation (Agent-based)  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m2/03_architecture.md`
