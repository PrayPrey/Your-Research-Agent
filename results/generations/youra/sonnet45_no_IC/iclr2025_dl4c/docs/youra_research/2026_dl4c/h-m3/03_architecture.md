# System Architecture: h-m3
# Phase 3 Human Feedback Peak Validation

**Hypothesis ID**: h-m3  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Date**: 2026-07-12  
**Applied Patterns**: RL Weight Scheduling (diffusion model timestep weighting analogy), RLHF Refinement (OpenAI instruction-following principles), Incremental Extension (h-m2 validated framework)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: patterns found from base code  
**Analyzed Path**: `docs/youra_research/h-m2/code/`  
**Findings**: h-m2 implementation validated (SHOULD_WORK gate passed). Phase2TriModalAggregator with AI peak scheduling (30-70%), Phase2PPOTrainer, checkpoint logging, quality tracking operational. Will extend with Phase 3 weight scheduling (70-100%) and conflict case evaluation.

---

## Architecture Overview

**Mission**: Validate Phase 3 human feedback weight increase hypothesis by extending h-m2 framework to Phase 3 (70-100% progress) with human-heavy weight scheduling and conflict case evaluation.

**Core Strategy**: Minimal extension of h-m2 architecture - reuse validated tri-modal framework, add Phase 3 weight schedule (human weight 0.40→0.70), implement conflict case filtering and evaluation.

**Key Differences from h-m2**:
- Phase 3 weight range (70-100% vs 30-70%)
- Human weight dominance (vs AI peak in Phase 2)
- Conflict case evaluation (new metric: preference score on edge cases)

**Components**:
1. Data Pipeline (100% reuse from h-m2)
2. Phase3TriModalAggregator (new - human peak scheduling)
3. Phase3PPOTrainer (extend h-m2 trainer)
4. ConflictCaseDataset (new - edge case filtering)
5. Phase3Metrics (new - conflict case tracking, gate validation)
6. Visualization (extend h-m2 visualizer)

---

## Module Structure

### 1. Data Pipeline (`data/dataset.py`)

**Dependencies**: h-m2 implementation (100% reuse)

```python
class CodeGenerationDataset:
    def __init__(self, cache_dir: str = "./.data_cache/datasets"): ...
    def load_datasets(self): ...
    def create_splits(self, train_ratio: float = 0.8, val_ratio: float = 0.1): ...
    def get_dataloader(self, split: str, batch_size: int = 8): ...
```

---

### 2. ConflictCaseDataset (`data/conflict_cases.py`)

**Dependencies**: h-m2 CodeGenerationDataset, h-m1 execution baseline results

```python
class ConflictCaseDataset:
    def __init__(self, h_m1_baseline_results: dict, target_count: int = 50): ...
    def filter_conflict_cases(self, pass_at_1_threshold: float = 1.0, preference_threshold: float = 0.3): ...
    def save_conflict_cases(self, output_path: str): ...
    def load_conflict_cases(self, input_path: str): ...
    def get_dataloader(self, batch_size: int = 8): ...
```

---

### 3. Phase3TriModalAggregator (`models/phase3_tri_modal_aggregator.py`)

**Dependencies**: h-m2 Phase2TriModalAggregator

```python
class Phase3TriModalAggregator(Phase2TriModalAggregator):
    def __init__(self, config: dict, phase3_checkpoints: list = [0.70, 0.80, 0.90, 1.00]): ...
    def compute_dynamic_weights(self, training_progress: float) -> dict: ...
    def forward(self, exec_r: Tensor, ai_r: Tensor, human_r: Tensor, progress: float) -> Tensor: ...
    def log_phase3_checkpoint(self, progress: float, weights: dict): ...
    def validate_human_weight_increase(self) -> bool: ...
```

---

### 4. Phase3PPOTrainer (`train/phase3_ppo_trainer.py`)

**Dependencies**: h-m2 Phase2PPOTrainer, Phase3TriModalAggregator

```python
class Phase3PPOTrainer(Phase2PPOTrainer):
    def __init__(self, model, aggregator, feedback_collector, config: dict, start_episode: int = 7000): ...
    def load_h_m2_checkpoint(self, checkpoint_path: str): ...
    def compute_training_progress(self, current_episode: int) -> float: ...
    def train_step(self, batch: dict, current_episode: int) -> dict: ...
    def evaluate_checkpoint(self, dataloader: DataLoader) -> dict: ...
    def train(self, dataloader: DataLoader, num_episodes: int = 3000) -> dict: ...
    def save_checkpoint(self, path: str, progress: float, metrics: dict): ...
```

---

### 5. Feedback Collectors (`models/feedback_collectors.py`)

**Dependencies**: h-m2 implementation (100% reuse)

```python
class FeedbackCollector:
    def __init__(self): ...
    def collect_execution_feedback(self, code: str, test_cases: list) -> float: ...
    def collect_ai_feedback(self, code: str, prompt: str) -> float: ...
    def collect_human_feedback(self, code: str, sample_id: str) -> float: ...
    def collect_all(self, code: str, context: dict) -> dict: ...
```

---

### 6. Phase3Metrics (`evaluation/phase3_metrics.py`)

**Dependencies**: scipy, numpy, h-m2 CheckpointLogger

```python
class Phase3Analyzer:
    def __init__(self, checkpoint_data: dict, conflict_case_results: dict): ...
    def validate_human_weight_increase(self) -> Tuple[bool, dict]: ...
    def compute_conflict_case_preference(self) -> Tuple[float, dict]: ...
    def compute_correctness_maintenance(self) -> dict: ...
    def validate_gate_criteria(self) -> dict: ...
    def generate_report(self) -> str: ...
```

---

### 7. ConflictCaseEvaluator (`evaluation/conflict_case_evaluator.py`)

**Dependencies**: h-m2 QualityEvaluator, ConflictCaseDataset

```python
class ConflictCaseEvaluator:
    def __init__(self, conflict_dataset: ConflictCaseDataset): ...
    def evaluate_conflict_cases(self, model, dataloader: DataLoader) -> dict: ...
    def compute_preference_score(self, generated_code: str, sample_id: str) -> float: ...
    def compute_median_preference(self, results: dict) -> float: ...
    def check_collapse(self, median_preference: float) -> bool: ...
```

---

### 8. CodeEvaluator (`evaluation/evaluator.py`)

**Dependencies**: h-m2 implementation (100% reuse)

```python
class CodeEvaluator:
    def __init__(self, timeout: int = 5): ...
    def evaluate_pass_at_1(self, model, dataloader: DataLoader) -> float: ...
    def execute_code(self, code: str, test_cases: list) -> bool: ...
```

---

### 9. Visualization (`utils/visualization.py`)

**Dependencies**: matplotlib, seaborn, h-m2 visualizer

```python
def plot_weight_trajectory_phase3(weight_history: dict, save_path: str): ...
def plot_conflict_case_distribution(conflict_results: dict, baseline_results: dict, save_path: str): ...
def plot_phase3_correctness_maintenance(pass1_history: dict, save_path: str): ...
def plot_gate_metrics(metrics: dict, targets: dict, save_path: str): ...
```

---

### 10. Checkpoint Logger (`utils/checkpoint_logger.py`)

**Dependencies**: h-m2 implementation (reuse and extend)

```python
class CheckpointLogger:
    def __init__(self, log_dir: str = "./checkpoints"): ...
    def log_weights(self, progress: float, weights: dict): ...
    def log_conflict_preference(self, progress: float, score: float): ...
    def log_pass_at_1(self, progress: float, score: float): ...
    def save_checkpoint_file(self, progress: float, data: dict): ...
    def load_all_checkpoints(self) -> dict: ...
```

---

### 11. Configuration (`config/experiment_config.py`)

**Dependencies**: dataclasses, yaml

```python
@dataclass
class Phase3Config:
    checkpoints: list = field(default_factory=lambda: [0.70, 0.80, 0.90, 1.00])
    phase3_start: float = 0.70
    phase3_end: float = 1.00
    human_peak_progress: float = 1.00
    total_episodes: int = 10000
    conflict_case_count: int = 50
    
@dataclass
class TrainingConfig:
    h_m2_checkpoint_path: str = "../h-m2/checkpoints/checkpoint_progress_0.70.pt"
    learning_rate: float = 1e-5
    batch_size: int = 64
    seed: int = 42
    device: str = "cuda"
    
def load_config(config_path: str) -> dict: ...
```

---

### 12. Gate Validator (`evaluation/gate_validator.py`)

**Dependencies**: Phase3Metrics

```python
class Phase3GateValidator:
    def __init__(self, weight_trajectory: dict, conflict_results: dict, pass1_trajectory: dict): ...
    def validate_gate1_human_increase(self) -> bool: ...
    def validate_gate2_conflict_non_collapse(self) -> bool: ...
    def validate_gate3_correctness_maintained(self) -> bool: ...
    def validate_all_gates(self) -> dict: ...
    def generate_gate_report(self) -> str: ...
```

---

### 13. Main Experiment Runner (`run_phase3_experiment.py`)

**Dependencies**: All above modules

```python
def setup_environment(seed: int = 42): ...
def load_h_m2_checkpoint(checkpoint_path: str): ...
def prepare_conflict_cases(h_m1_baseline_path: str, target_count: int = 50) -> ConflictCaseDataset: ...
def run_phase3_experiment(config: dict) -> dict: ...
def main(): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Phase2TriModalAggregator | `from h_m2.code.models.phase2_tri_modal_aggregator import Phase2TriModalAggregator` | `h-m2/code/models/phase2_tri_modal_aggregator.py` |
| Phase2PPOTrainer | `from h_m2.code.train.phase2_ppo_trainer import Phase2PPOTrainer` | `h-m2/code/train/phase2_ppo_trainer.py` |
| CodeGenerationDataset | `from h_m2.code.data.dataset import CodeGenerationDataset` | `h-m2/code/data/dataset.py` |
| FeedbackCollector | `from h_m2.code.models.feedback_collectors import FeedbackCollector` | `h-m2/code/models/feedback_collectors.py` |
| CodeEvaluator | `from h_m2.code.evaluation.evaluator import CodeEvaluator` | `h-m2/code/evaluation/evaluator.py` |
| CheckpointLogger | `from h_m2.code.utils.checkpoint_logger import CheckpointLogger` | `h-m2/code/utils/checkpoint_logger.py` |
| Phase2Metrics | `from h_m2.code.evaluation.phase2_metrics import Phase2Metrics` | `h-m2/code/evaluation/phase2_metrics.py` |

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation)

---

## File Organization

```
h-m3/
├── code/
│   ├── models/
│   │   └── phase3_tri_modal_aggregator.py    # Phase 3 human peak weight scheduling
│   ├── train/
│   │   └── phase3_ppo_trainer.py             # Phase 3 PPO trainer (loads h-m2 checkpoint)
│   ├── data/
│   │   └── conflict_cases.py                 # Conflict case filtering and dataset
│   ├── evaluation/
│   │   ├── phase3_metrics.py                 # Phase 3 analysis metrics
│   │   ├── conflict_case_evaluator.py        # Conflict case evaluation
│   │   └── gate_validator.py                 # SHOULD_WORK gate validation
│   ├── utils/
│   │   └── visualization.py                  # Phase 3 visualizations
│   ├── config/
│   │   └── experiment_config.py              # Phase 3 specific config
│   ├── run_phase3_experiment.py              # Main entry point
│   ├── requirements.txt
│   └── README.md
├── checkpoints/                               # Training checkpoints
│   ├── progress_0.70.json
│   ├── progress_0.80.json
│   ├── progress_0.90.json
│   └── progress_1.00.json
├── data/
│   └── conflict_cases.json                   # 50 filtered conflict cases
├── logs/
│   ├── weights_phase3.csv                    # Weight trajectory data
│   ├── conflict_preference_trajectory.csv    # Conflict case preference over time
│   └── pass_at_1_trajectory.csv              # Pass@1 over time
└── figures/                                   # Generated visualizations
    ├── gate_metrics.png
    ├── weight_trajectory.png
    ├── conflict_case_distribution.png
    └── correctness_maintenance.png
```

---

## Data Flow

**Training Flow**:
1. Load h-m2 dataset (830 train, 104 val, 104 test) → Reuse h-m2 splits
2. Load h-m2 checkpoint at 70% progress
3. Initialize Phase3TriModalAggregator (human peak scheduling)
4. Initialize Phase3PPOTrainer with loaded checkpoint
5. Training loop:
   - Compute training_progress = (current_episode + 7000) / 10000 (70%→100%)
   - At checkpoints [0.70, 0.80, 0.90, 1.00]:
     - Log weight coefficients
     - Evaluate pass@1 on validation set
     - Evaluate conflict cases (if checkpoint ≥ 0.80)
     - Save checkpoint
   - Standard PPO update with Phase 3 tri-modal reward
6. Post-training analysis via Phase3Analyzer

**Conflict Case Preparation Flow**:
1. Load h-m1 execution-only baseline results
2. Filter samples with pass@1=1.0 AND preference<0.3
3. Select 50 samples for conflict case dataset
4. Save to `data/conflict_cases.json`

**Evaluation Flow**:
1. Load all checkpoint data (Phase 3 range)
2. Load conflict case dataset (50 samples)
3. Phase3Analyzer computes:
   - Human weight increase: w_human(100%) > w_human(70%)
   - Conflict case median preference: median(preference_scores) ∈ [0.1, 0.4]
   - Correctness maintenance: pass1_100% / pass1_70% ≥ 0.95
4. Generate 4 required figures
5. Validate gate criteria (SHOULD_WORK)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Conflict Case Dataset Preparation | Filter and prepare 50 conflict cases from h-m1 baseline | 8 | 2+2+2+2 |
| C-2 | Phase3 Aggregator Implementation | Implement Phase3TriModalAggregator with human peak scheduling | 10 | 3+2+3+2 |
| C-3 | Checkpoint Loader | Load h-m2 checkpoint at 70% and resume training | 7 | 2+2+2+1 |
| C-4 | Phase3 PPO Trainer | Extend PPO trainer for Phase 3 (70-100% range) | 9 | 3+2+2+2 |
| C-5 | Conflict Case Evaluator | Implement conflict case evaluation with preference scoring | 9 | 2+2+3+2 |
| C-6 | Phase3 Metrics Module | Implement human weight tracking, conflict metrics, correctness | 11 | 3+2+4+2 |
| C-7 | Gate Validator | Implement SHOULD_WORK gate validation logic | 8 | 2+2+2+2 |
| C-8 | Visualization Extension | Create Phase 3 specific plots (weight, conflict, correctness) | 9 | 2+2+3+2 |
| C-9 | Integration Testing | Full Phase 3 training run with gate validation | 10 | 2+3+3+2 |

**Total Complexity**: 81 (9 tasks)

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [C-2, C-4, C-5, C-6, C-8, C-9]
- Low (4-8): [C-1, C-3, C-7]

---

## Task Details

### C-1: Conflict Case Dataset Preparation (Complexity: 8)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Implement ConflictCaseDataset class
- Load h-m1 execution-only baseline results
- Filter samples: pass@1=1.0 AND human_preference<0.3
- Select exactly 50 samples
- Save to JSON format
- Document conflict case characteristics

**Acceptance Criteria**:
- 50 conflict cases identified and saved
- All samples have pass@1=1.0 (verified)
- All samples have preference<0.3 from h-m1 baseline
- JSON file contains: sample_id, prompt, test_cases, baseline_preference
- Conflict case characteristics documented (why execution passes but quality low)
- Unit test: verify filtering logic with synthetic data

**Files**:
- `data/conflict_cases.py`
- `data/conflict_cases.json` (output)

---

### C-2: Phase3 Aggregator Implementation (Complexity: 10)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- Implement Phase3TriModalAggregator extending Phase2TriModalAggregator
- Weight schedule: Human increases (0.40→0.70), execution decays (0.40→0.20), AI maintains (~0.25)
- Phase 3 checkpoints: [0.70, 0.80, 0.90, 1.00]
- Log weights at checkpoints for gate validation
- Validate human weight increase trajectory

**Acceptance Criteria**:
- Human weight at 100% > human weight at 70% (increasing trend)
- Weights sum to 1.0 at all progress points (±1e-6 tolerance)
- Human weight is highest among three signals at 100%
- Checkpoint logging triggers at exact progress values
- Unit test: verify weight schedule and normalization

**Files**:
- `models/phase3_tri_modal_aggregator.py`

---

### C-3: Checkpoint Loader (Complexity: 7)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(1)

**Scope**:
- Load h-m2 checkpoint at 70% progress
- Verify checkpoint metadata: training_progress=0.70, phase="Phase 2"
- Extract model state_dict, optimizer state
- Initialize Phase3PPOTrainer with loaded checkpoint
- Device management (CUDA)

**Acceptance Criteria**:
- Checkpoint loads without error
- Metadata verified: progress=0.70
- Model architecture matches h-m2 (CodeGen-350M-mono)
- Pass@1 at 70% verified (~0.636 from h-m2 validation)
- Unit test: verify checkpoint integrity

**Files**:
- `train/phase3_ppo_trainer.py` (load_h_m2_checkpoint method)
- `run_phase3_experiment.py` (checkpoint loading logic)

---

### C-4: Phase3 PPO Trainer (Complexity: 9)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Extend h-m2 PPO trainer for Phase 3 (70-100% range)
- Adjust training progress computation: (current_episode + 7000) / 10000
- Reduced learning rate: 1e-5 (consistent with h-m2)
- Checkpoint frequency: Every 1,000 steps (10% increments)
- Evaluation frequency: Every 500 steps

**Acceptance Criteria**:
- Training resumes from 70% checkpoint
- Training progress correctly mapped to 70-100% range
- Checkpoints triggered at [0.70, 0.80, 0.90, 1.00]
- Each checkpoint saves: model state, weights, pass@1, conflict preference
- Learning rate schedule: linear decay from 1e-5

**Files**:
- `train/phase3_ppo_trainer.py`

---

### C-5: Conflict Case Evaluator (Complexity: 9)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- Implement ConflictCaseEvaluator class
- Load conflict case dataset (50 samples)
- Evaluate conflict cases at each checkpoint
- Compute preference scores (human annotations)
- Compute median preference score
- Check for collapse (median < 0.1)

**Acceptance Criteria**:
- Conflict case dataset loaded successfully
- Preference evaluation runs on all 50 samples
- Returns median preference score (0-1 range)
- Detects collapse: median < 0.1 (execution-only behavior)
- Target verification: median ∈ [0.1, 0.4] (non-collapsed)

**Files**:
- `evaluation/conflict_case_evaluator.py`

---

### C-6: Phase3 Metrics Module (Complexity: 11)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(4) + Integration(2)

**Scope**:
- Phase3Analyzer class for gate validation
- Metric 1: Human weight increase - w_human(100%) > w_human(70%)
- Metric 2: Conflict case median preference - median ∈ [0.1, 0.4]
- Metric 3: Correctness maintenance - pass1_100% / pass1_70% ≥ 0.95
- Gate validation logic (3 gates)

**Acceptance Criteria**:
- `validate_human_weight_increase()` returns True if w_human increases
- `compute_conflict_case_preference()` returns median and distribution
- `compute_correctness_maintenance()` returns ratio ≥ 0.95 (pass) or < 0.95 (fail)
- `validate_gate_criteria()` returns overall PASS/FAIL decision
- Unit test: verify metrics computation with synthetic data

**Files**:
- `evaluation/phase3_metrics.py`

---

### C-7: Gate Validator (Complexity: 8)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Phase3GateValidator class implementing SHOULD_WORK gate logic
- Gate 1: Human weight at 100% > human weight at 70%
- Gate 2: Conflict case median preference ∈ [0.1, 0.4]
- Gate 3: Correctness maintained (max 5% regression)
- Generate gate validation report

**Acceptance Criteria**:
- `validate_gate1_human_increase()` checks w_human(100%) > w_human(70%)
- `validate_gate2_conflict_non_collapse()` checks median ∈ [0.1, 0.4]
- `validate_gate3_correctness_maintained()` checks pass1_100% ≥ 0.95 × pass1_70%
- `validate_all_gates()` returns dict with all gate results
- Report includes: gate status, metric values, overall PASS/FAIL

**Files**:
- `evaluation/gate_validator.py`

---

### C-8: Visualization Extension (Complexity: 9)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- Figure 1: Gate Metrics Bar Chart (mandatory)
- Figure 2: Weight Trajectory (Phase 3 range, highlight human increase)
- Figure 3: Conflict Case Preference Distribution (tri-modal vs execution-only baseline)
- Figure 4: Correctness Maintenance (pass@1 trajectory 70%→100%)
- Publication-quality formatting

**Acceptance Criteria**:
- All 4 figures saved to `figures/` as PNG
- Gate metrics figure shows target vs actual (green/red bars)
- Weight trajectory highlights human weight increase (ascending line)
- Conflict case distribution shows median line and target range [0.1, 0.4]
- Correctness maintenance shows no regression (ratio ≥ 0.95)

**Files**:
- `utils/visualization.py`

---

### C-9: Integration Testing (Complexity: 10)

**Breakdown**: Module_Size(2) + Dependencies(3) + Algorithm(3) + Integration(2)

**Scope**:
- Full Phase 3 training run (3k episodes, 70%→100%)
- Load h-m2 checkpoint at 70%
- Prepare conflict case dataset (50 samples)
- Run Phase 3 training with human peak scheduling
- Evaluate at all checkpoints (70%, 80%, 90%, 100%)
- Run gate validation
- Generate all figures

**Acceptance Criteria**:
- Training completes without error
- All checkpoints saved with correct data
- Weight trajectory shows human weight increase 70%→100%
- Conflict case median preference ∈ [0.1, 0.4]
- Correctness maintained (max 5% regression)
- Gate validation runs successfully
- All 4 figures generated

**Files**:
- `run_phase3_experiment.py`
- `tests/test_integration.py`

---

## Dependencies & Integration

**External Libraries**:
- PyTorch 2.0+ (same as h-m2)
- Transformers 4.30+ (same as h-m2)
- Datasets 2.12+ (same as h-m2)
- scipy 1.10+ (for metrics)
- matplotlib 3.7+, seaborn 0.12+ (visualization)

**Hardware Requirements**:
- 1x NVIDIA A100 (40GB) or 4x V100 (32GB)
- CUDA 11.8+
- Storage: ~50GB (checkpoints + logs + figures)

**Inter-Module Dependencies**:
```
h-m2 modules (base) → Phase3TriModalAggregator, Phase3PPOTrainer
h-m2 checkpoint (70%) → Phase3PPOTrainer (starting point)
h-m1 baseline results → ConflictCaseDataset (filtering)
Phase3TriModalAggregator → Phase3PPOTrainer
ConflictCaseEvaluator → Phase3PPOTrainer (evaluation)
CheckpointLogger → Phase3PPOTrainer, Phase3Analyzer
Phase3Analyzer → Gate Validator → Visualization
All modules → run_phase3_experiment
```

---

## Success Criteria

**PoC Pass Conditions**:
1. Code runs without error through full Phase 3 training (3k episodes)
2. All checkpoints logged correctly
3. Conflict case preference tracked

**Gate Validation (SHOULD_WORK)**:
- Primary Criterion 1: Human weight at 100% > human weight at 70% (positive correlation)
- Primary Criterion 2: Conflict case median preference ∈ [0.1, 0.4] (not collapsed)
- Secondary Criterion 3: Correctness maintained (pass1_100% ≥ 0.95 × pass1_70%)

**Gate Decision**:
- PASS: All 3 criteria satisfied
- FAIL: Any criterion fails → Document limitation, continue pipeline (SHOULD_WORK, not blocking)

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation (Agent-based)  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m3/03_architecture.md`
