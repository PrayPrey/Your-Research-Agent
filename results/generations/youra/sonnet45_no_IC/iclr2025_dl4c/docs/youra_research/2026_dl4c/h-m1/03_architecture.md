# System Architecture: h-m1
# Phase 1 Execution-Heavy Weight Validation

**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Date**: 2026-07-12  
**Applied Patterns**: PyTorch Training Checkpoint Pattern, HuggingFace Model Integration, PPO Training Loop

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: patterns found from base code  
**Analyzed Path**: `docs/youra_research/h-e1/code/`  
**Findings**: h-e1 implementation validated and functional. Tri-modal aggregator, PPO trainer, data pipeline, and evaluation modules all operational. Will extend with Phase 1 monitoring.

---

## Architecture Overview

**Mission**: Validate Phase 1 execution-heavy weight hypothesis by extending h-e1 tri-modal framework with checkpoint logging and pass@1 improvement rate tracking.

**Core Strategy**: Minimal extension to h-e1 - add Phase 1 monitoring without modifying core mechanism.

**Components**:
1. Data Pipeline (100% reuse from h-e1)
2. Tri-Modal Aggregator (extend with Phase 1 checkpoints)
3. PPO Trainer (extend with progress tracking)
4. Phase 1 Metrics (new module)
5. Visualization (extend h-e1 visualizer)

---

## Module Structure

### 1. Data Pipeline (`data/dataset.py`)

**Dependencies**: h-e1 implementation (100% reuse)

```python
class CodeGenerationDataset:
    def __init__(self, cache_dir: str = "./.data_cache/datasets"): ...
    def load_datasets(self): ...
    def create_splits(self, train_ratio: float = 0.8, val_ratio: float = 0.1): ...
    def get_dataloader(self, split: str, batch_size: int = 8) -> DataLoader: ...
```

---

### 2. Phase1AnalysisTriModalAggregator (`models/phase1_tri_modal_aggregator.py`)

**Dependencies**: h-e1 TriModalAggregator

```python
class Phase1AnalysisTriModalAggregator(TriModalAggregator):
    def __init__(self, config: dict, phase1_checkpoints: list = [0.0, 0.1, 0.2, 0.3]): ...
    def forward(self, exec_r: Tensor, ai_r: Tensor, human_r: Tensor, progress: float) -> Tensor: ...
    def compute_weights(self, progress: float) -> Tuple[Tensor, Tensor, Tensor]: ...
    def log_phase1_checkpoint(self, progress: float, weights: dict): ...
```

---

### 3. Phase1PPOTrainer (`train/phase1_ppo_trainer.py`)

**Dependencies**: h-e1 SimplifiedPPOTrainer, Phase1AnalysisTriModalAggregator

```python
class Phase1PPOTrainer(SimplifiedPPOTrainer):
    def __init__(self, model_name: str, aggregator, feedback_collector, config: dict): ...
    def compute_training_progress(self, current_episode: int, total_episodes: int) -> float: ...
    def train_step(self, batch: dict, current_episode: int) -> dict: ...
    def evaluate_checkpoint(self, dataloader: DataLoader) -> float: ...
    def train(self, dataloader: DataLoader, total_episodes: int = 10000) -> dict: ...
    def save_checkpoint(self, path: str, progress: float, metrics: dict): ...
```

---

### 4. Feedback Collectors (`models/feedback_collectors.py`)

**Dependencies**: h-e1 implementation (100% reuse)

```python
class FeedbackCollector:
    def __init__(self): ...
    def collect_execution_feedback(self, code: str, test_cases: list) -> float: ...
    def collect_ai_feedback(self, code: str, prompt: str) -> float: ...
    def collect_human_feedback(self, code: str, sample_id: str) -> float: ...
    def collect_all(self, code: str, context: dict) -> dict: ...
```

---

### 5. Phase1Metrics (`evaluation/phase1_metrics.py`)

**Dependencies**: scipy, numpy

```python
class Phase1Analyzer:
    def __init__(self, checkpoint_data: dict): ...
    def compute_weight_dominance(self) -> dict: ...
    def compute_pass_at_1_improvement_rates(self) -> dict: ...
    def compute_weight_correlation(self) -> Tuple[float, float]: ...
    def validate_gate_criteria(self) -> dict: ...
    def generate_report(self) -> str: ...
```

---

### 6. CodeEvaluator (`evaluation/evaluator.py`)

**Dependencies**: h-e1 implementation (100% reuse)

```python
class CodeEvaluator:
    def __init__(self, timeout: int = 5): ...
    def evaluate_pass_at_1(self, model, dataloader: DataLoader) -> float: ...
    def execute_code(self, code: str, test_cases: list) -> bool: ...
```

---

### 7. Visualization (`utils/visualization.py`)

**Dependencies**: matplotlib, seaborn

```python
def plot_weight_trajectory(weight_history: dict, save_path: str, highlight_phase1: bool = True): ...
def plot_pass_at_1_trajectory(pass_at_1_history: dict, save_path: str): ...
def plot_phase_improvement_rates(rates: dict, save_path: str): ...
def plot_gate_metrics(metrics: dict, targets: dict, save_path: str): ...
```

---

### 8. Checkpoint Logger (`utils/checkpoint_logger.py`)

**Dependencies**: json, pathlib

```python
class CheckpointLogger:
    def __init__(self, log_dir: str = "./checkpoints"): ...
    def log_weights(self, progress: float, weights: dict): ...
    def log_pass_at_1(self, progress: float, score: float): ...
    def save_checkpoint_file(self, progress: float, data: dict): ...
    def load_all_checkpoints(self) -> dict: ...
```

---

### 9. Configuration (`config/experiment_config.py`)

**Dependencies**: dataclasses, yaml

```python
@dataclass
class Phase1Config:
    checkpoints: list = field(default_factory=lambda: [0.0, 0.1, 0.2, 0.3, 0.7, 1.0])
    total_episodes: int = 10000
    eval_samples: int = 113
    
@dataclass
class TrainingConfig:
    model_name: str = "Salesforce/codegen-350M-mono"
    learning_rate: float = 5e-6
    batch_size: int = 8
    seed: int = 42
    device: str = "cuda"
    
def load_config(config_path: str) -> dict: ...
```

---

### 10. Main Experiment Runner (`run_h_m1_experiment.py`)

**Dependencies**: All above modules

```python
def setup_environment(seed: int = 42): ...
def run_phase1_experiment(config: dict) -> dict: ...
def main(): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TriModalAggregator | `from h_e1.code.models.tri_modal_aggregator import TriModalAggregator` | `h-e1/code/models/tri_modal_aggregator.py` |
| SimplifiedPPOTrainer | `from h_e1.code.train.ppo_trainer import SimplifiedPPOTrainer` | `h-e1/code/train/ppo_trainer.py` |
| CodeGenerationDataset | `from h_e1.code.data.dataset import CodeGenerationDataset` | `h-e1/code/data/dataset.py` |
| FeedbackCollector | `from h_e1.code.models.feedback_collectors import FeedbackCollector` | `h-e1/code/models/feedback_collectors.py` |
| CodeEvaluator | `from h_e1.code.evaluation.evaluator import CodeEvaluator` | `h-e1/code/evaluation/evaluator.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## File Organization

```
h-m1/
├── code/
│   ├── models/
│   │   └── phase1_tri_modal_aggregator.py    # Extended aggregator with Phase 1 logging
│   ├── train/
│   │   └── phase1_ppo_trainer.py             # Extended PPO trainer with progress tracking
│   ├── evaluation/
│   │   └── phase1_metrics.py                 # Phase 1 analysis metrics
│   ├── utils/
│   │   ├── checkpoint_logger.py              # Checkpoint management
│   │   └── visualization.py                  # Extended visualizer
│   ├── config/
│   │   └── experiment_config.py              # Phase 1 specific config
│   ├── run_h_m1_experiment.py                # Main entry point
│   ├── requirements.txt
│   └── README.md
├── checkpoints/                               # Training checkpoints
│   ├── progress_0.0.json
│   ├── progress_0.1.json
│   ├── progress_0.2.json
│   ├── progress_0.3.json
│   ├── progress_0.7.json
│   └── progress_1.0.json
├── logs/
│   ├── weights_phase1.csv                    # Weight trajectory data
│   └── pass_at_1_trajectory.csv              # Pass@1 over time
└── figures/                                   # Generated visualizations
    ├── gate_metrics.png
    ├── weight_trajectory.png
    ├── pass_at_1_trajectory.png
    └── phase_improvement_rates.png
```

---

## Data Flow

**Training Flow**:
1. Load h-e1 dataset (902 train, 113 val, 113 test) → Reuse h-e1 splits
2. Initialize Phase1AnalysisTriModalAggregator (extends h-e1 aggregator)
3. Initialize Phase1PPOTrainer with aggregator
4. Training loop:
   - Compute training_progress = current_episode / total_episodes
   - At checkpoints [0.0, 0.1, 0.2, 0.3, 0.7, 1.0]:
     - Log weight coefficients
     - Evaluate pass@1 on validation set
     - Save checkpoint
   - Standard PPO update with tri-modal reward
5. Post-training analysis via Phase1Analyzer

**Evaluation Flow**:
1. Load all checkpoint data
2. Phase1Analyzer computes:
   - Weight dominance: execution_weight > max(ai_weight, human_weight) at [0%, 10%, 20%, 30%]
   - Pass@1 improvement rates: Phase 1 (0-30%) vs later phases (30-100%)
   - Weight correlation: Pearson ρ(execution_weight, progress) in Phase 1
3. Generate 4 required figures
4. Validate gate criteria (MUST_WORK)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Phase1 Aggregator Extension | Extend h-e1 TriModalAggregator with checkpoint logging | 7 | 2+1+2+2 |
| A-2 | Phase1 PPO Trainer Extension | Extend h-e1 PPOTrainer with progress tracking and checkpoints | 9 | 3+2+2+2 |
| A-3 | Checkpoint Logger | Implement checkpoint logging and loading utilities | 6 | 2+1+2+1 |
| A-4 | Phase1 Metrics Module | Implement weight dominance, improvement rate, and correlation metrics | 10 | 3+2+3+2 |
| A-5 | Visualization Extension | Extend h-e1 visualizer with Phase 1 specific plots | 7 | 2+1+3+1 |
| A-6 | Configuration Setup | Create Phase 1 specific configuration and validation | 5 | 1+1+2+1 |
| A-7 | Integration Testing | Full training run with checkpoint validation (smoke test) | 8 | 2+2+2+2 |
| A-8 | Gate Validation Analysis | Validate gate criteria and generate validation report | 9 | 2+2+3+2 |

**Total Complexity**: 61 (8 tasks)

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-2, A-4, A-8]
- Low (4-8): [A-1, A-3, A-5, A-6, A-7]

---

## Task Details

### A-1: Phase1 Aggregator Extension (Complexity: 7)

**Breakdown**: Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(2)

**Scope**:
- Extend h-e1 `TriModalAggregator` with Phase 1 checkpoint logging
- Add `phase1_checkpoints` attribute: [0.0, 0.1, 0.2, 0.3]
- Override `forward()` to log weights at checkpoints
- Maintain all h-e1 functionality (Gaussian weight curves, normalization)

**Acceptance Criteria**:
- `Phase1AnalysisTriModalAggregator` inherits from h-e1 `TriModalAggregator`
- Checkpoint logging triggers at exact progress values
- Logged data includes: progress, execution_weight, ai_weight, human_weight
- Unit test: verify weights sum to 1.0 at checkpoints

**Files**:
- `models/phase1_tri_modal_aggregator.py`

---

### A-2: Phase1 PPO Trainer Extension (Complexity: 9)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Extend h-e1 `SimplifiedPPOTrainer` with training progress tracking
- Add `compute_training_progress()`: current_episode / total_episodes
- Add `evaluate_checkpoint()`: pass@1 evaluation at checkpoints
- Modify `train()` to trigger checkpoint logging
- Save checkpoint files at progress milestones

**Acceptance Criteria**:
- Training progress computed correctly at each episode
- Checkpoints triggered at [0.0, 0.1, 0.2, 0.3, 0.7, 1.0]
- Each checkpoint saves: model state, optimizer state, weights, pass@1
- Pass@1 evaluated on validation set (113 samples)

**Files**:
- `train/phase1_ppo_trainer.py`

---

### A-3: Checkpoint Logger (Complexity: 6)

**Breakdown**: Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(1)

**Scope**:
- `CheckpointLogger` class for managing checkpoint data
- Save weight trajectory to CSV: `weights_phase1.csv`
- Save pass@1 trajectory to CSV: `pass_at_1_trajectory.csv`
- Save full checkpoint to JSON: `progress_{X}.json`
- Load all checkpoints for analysis

**Acceptance Criteria**:
- CSV files human-readable with headers
- JSON files contain all checkpoint data
- `load_all_checkpoints()` returns dictionary with all progress points
- Directory auto-created if missing

**Files**:
- `utils/checkpoint_logger.py`

---

### A-4: Phase1 Metrics Module (Complexity: 10)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- `Phase1Analyzer` class for gate validation
- Metric 1: Weight dominance - execution_weight > max(ai_weight, human_weight) at [0%, 10%, 20%, 30%]
- Metric 2: Pass@1 improvement rates - Phase 1 vs later phases
- Metric 3: Weight correlation - Pearson ρ(execution_weight, progress) in Phase 1
- Gate validation logic

**Acceptance Criteria**:
- `compute_weight_dominance()` returns PASS/FAIL per checkpoint
- `compute_pass_at_1_improvement_rates()` returns Phase 1 rate and later rate
- `compute_weight_correlation()` returns (ρ, p-value)
- `validate_gate_criteria()` returns final PASS/FAIL decision

**Files**:
- `evaluation/phase1_metrics.py`

---

### A-5: Visualization Extension (Complexity: 7)

**Breakdown**: Module_Size(2) + Dependencies(1) + Algorithm(3) + Integration(1)

**Scope**:
- Figure 1: Gate Metrics Bar Chart (mandatory)
- Figure 2: Weight Trajectory (highlight Phase 1 region 0-30%)
- Figure 3: Pass@1 Trajectory (mark phase boundaries)
- Figure 4: Phase Improvement Rates (3 bars)
- Publication-quality formatting

**Acceptance Criteria**:
- All 4 figures saved to `figures/` as PNG
- Gate metrics figure shows target vs actual values
- Weight trajectory highlights Phase 1 region
- Pass@1 trajectory marks phases: Phase 1 (0-30%), Phase 2 (30-70%), Phase 3 (70-100%)

**Files**:
- `utils/visualization.py`

---

### A-6: Configuration Setup (Complexity: 5)

**Breakdown**: Module_Size(1) + Dependencies(1) + Algorithm(2) + Integration(1)

**Scope**:
- `Phase1Config` dataclass: checkpoints, total_episodes, eval_samples
- `TrainingConfig` dataclass: model_name, lr, batch_size, seed, device
- YAML config file: `config/phase1_config.yaml`
- Config validation

**Acceptance Criteria**:
- Config loaded from YAML file
- Default values match h-e1 optimal hyperparameters
- Validation checks: checkpoints in [0, 1], total_episodes > 0

**Files**:
- `config/experiment_config.py`
- `config/phase1_config.yaml`

---

### A-7: Integration Testing (Complexity: 8)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Smoke test: Full training run with 100 episodes (reduced for speed)
- Verify checkpoint logging works
- Verify pass@1 evaluation runs
- Verify weight trajectory logged

**Acceptance Criteria**:
- Training completes without error
- All checkpoints saved with correct data
- Weight trajectory CSV contains 6 rows (checkpoints)
- Pass@1 trajectory CSV contains 6 rows

**Files**:
- `tests/test_smoke.py`

---

### A-8: Gate Validation Analysis (Complexity: 9)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- Run full experiment (10k episodes)
- Load all checkpoint data
- Run Phase1Analyzer validation
- Generate final report
- Create all required figures

**Acceptance Criteria**:
- Gate criteria validated (PASS/FAIL)
- Report includes: weight dominance results, pass@1 improvement rates, weight correlation
- All 4 figures generated
- Results match PRD success criteria

**Files**:
- `run_h_m1_experiment.py`

---

## Dependencies & Integration

**External Libraries**:
- PyTorch 2.0+ (same as h-e1)
- Transformers 4.30+ (same as h-e1)
- Datasets 2.12+ (same as h-e1)
- scipy 1.10+ (for Pearson correlation)
- matplotlib 3.7+, seaborn 0.12+ (visualization)

**Hardware Requirements**:
- 5x NVIDIA H100 NVL (80GB) - same as h-e1
- CUDA 11.8+
- Storage: ~50GB (same as h-e1)

**Inter-Module Dependencies**:
```
h-e1 modules (base) → Phase1AnalysisTriModalAggregator, Phase1PPOTrainer
Phase1AnalysisTriModalAggregator → Phase1PPOTrainer
CheckpointLogger → Phase1PPOTrainer, Phase1Analyzer
Phase1Analyzer → Visualization
All modules → run_h_m1_experiment
```

---

## Success Criteria

**PoC Pass Conditions**:
1. Code runs without error through full training (10k episodes)
2. All checkpoints logged correctly

**Gate Validation (MUST_WORK)**:
- Primary Criterion 1: execution_weight > max(ai_weight, human_weight) at ALL checkpoints [0%, 10%, 20%, 30%]
- Primary Criterion 2: Phase 1 improvement rate > Later phases improvement rate
- Secondary Criterion: Pearson ρ < -0.6 for execution_weight vs training_progress in Phase 1

**Gate Decision**:
- PASS: Primary criteria 1 AND 2 satisfied
- FAIL: Either primary criterion fails → MUST redesign mechanism

---

**Document Status**: ✅ COMPLETED  
**Next Phase**: Phase 4 - Implementation (Agent-based)  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m1/03_architecture.md`
