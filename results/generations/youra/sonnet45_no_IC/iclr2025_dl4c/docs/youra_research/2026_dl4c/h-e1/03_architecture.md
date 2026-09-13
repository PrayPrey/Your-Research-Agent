# System Architecture: h-e1
# Tri-Modal RL Framework for Code Generation

**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC)  
**Gate**: MUST_WORK  
**Date**: 2026-07-12  
**Applied Patterns**: PyTorch RL Training Loop, HuggingFace Model Integration, RLHF Reward Model Training

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: green-field - no code to analyze  
**Analyzed Path**: N/A  
**Findings**: New implementation from scratch. No existing h-e1 codebase found. This is the foundation EXISTENCE hypothesis.

---

## Architecture Overview

**Mission**: Validate tri-modal RL framework combining execution, AI, and human feedback with dynamic weight scheduling for code generation.

**Core Components**:
1. Data Pipeline (HumanEval + MBPP)
2. Baseline Models (3 single-feedback RL variants)
3. Tri-Modal Reward Aggregator (novel mechanism)
4. PPO Training Loop
5. Evaluation Pipeline

**Design Philosophy**: Minimal PoC structure - baseline + proposed mechanism only. No ablation modules.

---

## Module Structure

### 1. DataLoader (`src/data_loader.py`)

**Dependencies**: datasets (HuggingFace), transformers

```python
class CodeDataset:
    def __init__(self, split: str, tokenizer, max_length: int = 512): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...
    
def load_humaneval_mbpp(split: str) -> Dataset: ...
def create_dataloaders(tokenizer, batch_size: int = 32) -> tuple[DataLoader, DataLoader, DataLoader]: ...
```

---

### 2. Baseline Models (`src/baseline_models.py`)

**Dependencies**: transformers, torch, trl (PPO)

```python
class ExecutionOnlyPPO:
    def __init__(self, model_name: str = "Salesforce/codegen-1.5B-mono", lr: float = 5e-5): ...
    def train(self, dataloader: DataLoader, steps: int = 10000) -> dict: ...
    def generate(self, prompt: str) -> str: ...
    
class HumanOnlyPPO:
    def __init__(self, model_name: str, lr: float = 5e-5): ...
    def train(self, dataloader: DataLoader, steps: int = 10000) -> dict: ...
    def generate(self, prompt: str) -> str: ...
    
class AIOnlyPPO:
    def __init__(self, model_name: str, reward_model_path: str, lr: float = 5e-5): ...
    def train(self, dataloader: DataLoader, steps: int = 10000) -> dict: ...
    def generate(self, prompt: str) -> str: ...
```

---

### 3. Tri-Modal Reward Aggregator (`src/tri_modal_aggregator.py`)

**Dependencies**: torch

```python
class TriModalRewardAggregator(nn.Module):
    def __init__(self, num_phases: int = 3): ...
    def forward(self, execution_reward: Tensor, ai_reward: Tensor, human_reward: Tensor, training_progress: float) -> Tensor: ...
    def _compute_phase_weights(self, progress: float) -> Tensor: ...
    def _percentile_normalize(self, rewards: Tensor) -> Tensor: ...
    def get_current_weights(self, progress: float) -> dict: ...
```

---

### 4. Feedback Collectors (`src/feedback.py`)

**Dependencies**: subprocess (for execution), torch (for AI model)

```python
class ExecutionFeedback:
    def __init__(self, timeout: int = 5): ...
    def compute_reward(self, code: str, test_cases: list[dict]) -> float: ...
    
class AIFeedback:
    def __init__(self, reward_model_path: str): ...
    def compute_reward(self, code: str, prompt: str) -> float: ...
    
class HumanFeedback:
    def __init__(self, annotation_cache_path: str): ...
    def compute_reward(self, code: str, sample_id: str) -> float: ...
    def request_annotation(self, code: str, sample_id: str) -> float: ...
```

---

### 5. Reward Model (`src/reward_model.py`)

**Dependencies**: transformers, torch

```python
class CodeRewardModel(nn.Module):
    def __init__(self, base_model: str = "Salesforce/codegen-350M-mono"): ...
    def forward(self, input_ids: Tensor, attention_mask: Tensor) -> Tensor: ...
    
def train_reward_model(train_data: Dataset, val_data: Dataset, epochs: int = 3) -> CodeRewardModel: ...
def load_reward_model(checkpoint_path: str) -> CodeRewardModel: ...
```

---

### 6. PPO Trainer (`src/ppo_trainer.py`)

**Dependencies**: trl, transformers, torch

```python
class TriModalPPOTrainer:
    def __init__(self, model_name: str, aggregator: TriModalRewardAggregator, 
                 exec_feedback: ExecutionFeedback, ai_feedback: AIFeedback, 
                 human_feedback: HumanFeedback, ppo_config: dict): ...
    def train_step(self, batch: dict, training_progress: float) -> dict: ...
    def train(self, dataloader: DataLoader, steps: int = 10000) -> dict: ...
    def save_checkpoint(self, path: str): ...
    def load_checkpoint(self, path: str): ...
```

---

### 7. Evaluation (`src/evaluate.py`)

**Dependencies**: numpy, sklearn

```python
def evaluate_pass_at_1(model, test_loader: DataLoader) -> float: ...
def evaluate_human_preference(model, test_loader: DataLoader, annotation_interface) -> float: ...
def compute_harmonic_mean(pass_at_1: float, human_pref: float) -> float: ...
def run_full_evaluation(model_paths: list[str], test_loader: DataLoader) -> dict: ...
```

---

### 8. Visualization (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn

```python
def plot_weight_trajectory(weight_history: dict, save_path: str): ...
def plot_reward_trends(reward_history: dict, save_path: str): ...
def plot_baseline_comparison(results: dict, save_path: str): ...
def plot_training_curves(metrics: dict, save_path: str): ...
def plot_gate_metrics(target: float, actual: float, save_path: str): ...
```

---

### 9. Annotation Interface (`src/annotation_interface.py`)

**Dependencies**: flask, json

```python
class AnnotationServer:
    def __init__(self, port: int = 5000): ...
    def run(self): ...
    def display_sample(self, problem: str, code: str) -> int: ...
    def export_annotations(self, output_path: str): ...
```

---

### 10. Configuration (`src/config.py`)

**Dependencies**: dataclasses, yaml

```python
@dataclass
class DataConfig:
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    max_length: int = 512
    batch_size: int = 32

@dataclass
class PPOConfig:
    clip_ratio: float = 0.2
    value_loss_coef: float = 0.5
    entropy_coef: float = 0.01
    gae_lambda: float = 0.95
    discount_gamma: float = 0.99
    
@dataclass
class TrainingConfig:
    model_name: str = "Salesforce/codegen-1.5B-mono"
    lr: float = 5e-5
    steps: int = 10000
    seed: int = 42
    device: str = "cuda"
    
def load_config(config_path: str) -> dict: ...
def save_config(config: dict, output_path: str): ...
```

---

### 11. Training Script (`src/train.py`)

**Dependencies**: All above modules

```python
def train_baseline_execution(config: TrainingConfig) -> str: ...
def train_baseline_human(config: TrainingConfig) -> str: ...
def train_baseline_ai(config: TrainingConfig) -> str: ...
def train_tri_modal(config: TrainingConfig) -> str: ...
def main(args): ...
```

---

### 12. Main Experiment Runner (`run_experiment.py`)

**Dependencies**: src modules, argparse

```python
def setup_environment(seed: int = 42): ...
def run_all_experiments(config_path: str) -> dict: ...
def main(): ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py                    # Configuration management
│   │   ├── data_loader.py               # HumanEval + MBPP loading
│   │   ├── baseline_models.py           # 3 single-feedback baselines
│   │   ├── tri_modal_aggregator.py      # Dynamic reward aggregation (CORE)
│   │   ├── feedback.py                  # Execution, AI, Human feedback collectors
│   │   ├── reward_model.py              # AI reward model training/inference
│   │   ├── ppo_trainer.py               # Tri-modal PPO integration
│   │   ├── evaluate.py                  # Pass@1, preference, harmonic mean
│   │   ├── visualize.py                 # 5 required figures
│   │   ├── annotation_interface.py      # Human annotation web interface
│   │   └── train.py                     # Training orchestration
│   ├── run_experiment.py                # Main entry point
│   ├── requirements.txt
│   └── README.md
├── data/
│   ├── humaneval/                       # Downloaded from HF
│   ├── mbpp/                            # Downloaded from HF
│   └── annotations/                     # Human preference annotations
│       └── annotations.json
├── models/                              # Saved checkpoints
│   ├── baseline_execution.pt
│   ├── baseline_human.pt
│   ├── baseline_ai.pt
│   ├── reward_model.pt
│   └── tri_modal.pt
├── results/
│   ├── eval_metrics.json                # Final evaluation results
│   └── training_logs/                   # Tensorboard logs
└── figures/                             # Generated visualizations
    ├── weight_trajectory.png
    ├── reward_trends.png
    ├── baseline_comparison.png
    ├── training_curves.png
    └── gate_metrics.png
```

---

## Data Flow

**Training Phase**:
1. `data_loader.py` → Load HumanEval + MBPP → Split train/val/test
2. `reward_model.py` → Train AI reward model on execution + human annotations
3. `baseline_models.py` → Train 3 single-feedback baselines (execution/human/AI only)
4. `tri_modal_aggregator.py` + `ppo_trainer.py` → Train proposed tri-modal model
5. All models save checkpoints to `models/`

**Evaluation Phase**:
1. Load 4 model checkpoints (3 baselines + tri-modal)
2. `evaluate.py` → Compute pass@1, human preference, harmonic mean on test set
3. `visualize.py` → Generate 5 figures
4. Save results to `results/eval_metrics.json`

**Feedback Collection**:
- **Execution**: `feedback.py` runs test cases via subprocess
- **AI**: `reward_model.py` inference on generated code
- **Human**: `annotation_interface.py` serves Flask UI → saves to `annotations.json`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Load HumanEval + MBPP, create splits, tokenize | 8 | 2+2+2+2 |
| A-2 | Baseline Models | Implement 3 single-feedback PPO baselines | 12 | 3+3+3+3 |
| A-3 | Tri-Modal Aggregator | Core dynamic reward weighting mechanism | 10 | 3+2+3+2 |
| A-4 | Feedback Collectors | Execution/AI/Human feedback modules | 11 | 3+3+3+2 |
| A-5 | Reward Model Training | Train AI reward model on combined data | 9 | 2+2+3+2 |
| A-6 | PPO Integration | Integrate tri-modal aggregator into PPO loop | 13 | 4+3+3+3 |
| A-7 | Evaluation Pipeline | Pass@1, preference, harmonic mean computation | 7 | 2+2+2+1 |
| A-8 | Visualization | Generate 5 required figures | 6 | 2+1+2+1 |

**Total Complexity**: 76 (8 tasks)

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-2, A-3, A-4, A-6]
- Low (4-8): [A-1, A-5, A-7, A-8]

**Complexity Breakdown Legend**:
- Module_Size (1-5): Lines of code / complexity
- Dependencies (1-5): Number of external dependencies
- Algorithm (1-5): Algorithm complexity
- Integration (1-5): Integration effort with other modules

---

## Task Details

### A-1: Data Pipeline (Complexity: 8)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2)

**Scope**:
- Load HumanEval (164 problems) from `openai/humaneval`
- Load MBPP (500 problems) from `google-research/mbpp`
- Combine and split: 80% train, 10% val, 10% test
- Tokenize with CodeGen tokenizer (max 512 tokens)
- Extract test case input/output pairs

**Acceptance Criteria**:
- `create_dataloaders()` returns 3 PyTorch DataLoaders
- Test set contains exactly 67 problems (10% of 664)
- Each sample has: `{prompt, code, test_cases, sample_id}`

**Files**:
- `src/data_loader.py`
- `src/config.py` (DataConfig)

---

### A-2: Baseline Models (Complexity: 12)

**Breakdown**: Module_Size(3) + Dependencies(3) + Algorithm(3) + Integration(3)

**Scope**:
- Implement `ExecutionOnlyPPO`: reward = test pass/fail
- Implement `HumanOnlyPPO`: reward = cached human preference
- Implement `AIOnlyPPO`: reward = learned reward model score
- All use same PPO config: clip=0.2, lr=5e-5, 10k steps
- Save checkpoints every 1000 steps

**Acceptance Criteria**:
- Each baseline trains without error for 10k steps
- Checkpoints saved to `models/baseline_{type}.pt`
- Training logs include loss, reward, KL divergence

**Files**:
- `src/baseline_models.py`
- `src/feedback.py` (ExecutionFeedback, HumanFeedback)
- `src/reward_model.py` (for AI baseline)

---

### A-3: Tri-Modal Aggregator (Complexity: 10)

**Breakdown**: Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- `TriModalRewardAggregator` PyTorch module
- Learnable weight schedule parameters (9 total)
- Dynamic phase-based weighting:
  - Phase 1 (0-30%): execution dominant
  - Phase 2 (30-70%): AI dominant
  - Phase 3 (70-100%): human dominant
- Percentile normalization for reward alignment
- Gaussian-like weight curves

**Acceptance Criteria**:
- `forward()` takes 3 reward tensors + progress → returns aggregated reward
- Weights sum to 1 at each timestep
- `get_current_weights()` returns interpretable weight dict
- Unit tests for weight computation

**Files**:
- `src/tri_modal_aggregator.py`

---

### A-4: Feedback Collectors (Complexity: 11)

**Breakdown**: Module_Size(3) + Dependencies(3) + Algorithm(3) + Integration(2)

**Scope**:
- `ExecutionFeedback`: Run test cases via subprocess, compute pass rate
- `AIFeedback`: Query reward model for code quality score
- `HumanFeedback`: Load cached annotations or request new ones
- Timeout handling for execution (5 seconds)
- Error handling for malformed code

**Acceptance Criteria**:
- Each feedback module has `compute_reward(code, context) -> float` interface
- Execution feedback returns [0,1] (fraction of tests passed)
- AI feedback returns normalized score [-1,1]
- Human feedback returns cached score [0,1] or triggers annotation

**Files**:
- `src/feedback.py`
- `src/annotation_interface.py` (for human feedback)

---

### A-5: Reward Model Training (Complexity: 9)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(3) + Integration(2)

**Scope**:
- Train CodeRewardModel on combined execution + human annotation data
- Base model: CodeGen-350M (smaller for reward model)
- Binary classification head: good code (1) vs bad code (0)
- Training data: 500 annotated samples + execution results
- Validation split for early stopping

**Acceptance Criteria**:
- Reward model achieves >70% validation accuracy
- Checkpoint saved to `models/reward_model.pt`
- Inference API: `predict_reward(code, prompt) -> float`

**Files**:
- `src/reward_model.py`

---

### A-6: PPO Integration (Complexity: 13)

**Breakdown**: Module_Size(4) + Dependencies(3) + Algorithm(3) + Integration(3)

**Scope**:
- `TriModalPPOTrainer` class integrating aggregator + PPO
- Collect all 3 feedback signals per generated code sample
- Track per-signal rewards for analysis
- Log weight schedule trajectory
- Standard PPO update loop with tri-modal reward
- Checkpoint management

**Acceptance Criteria**:
- Full training run (10k steps) completes without error
- Training logs include: loss, reward, KL, per-signal rewards, weights
- Checkpoint saved to `models/tri_modal.pt`
- Weight trajectory logged to `results/weight_history.json`

**Files**:
- `src/ppo_trainer.py`
- `src/train.py` (orchestration)

---

### A-7: Evaluation Pipeline (Complexity: 7)

**Breakdown**: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(1)

**Scope**:
- `evaluate_pass_at_1()`: Test execution on held-out test set (67 problems)
- `evaluate_human_preference()`: Annotator ratings (3 per sample, majority vote)
- `compute_harmonic_mean()`: 2*p*h/(p+h)
- Run for all 4 models (3 baselines + tri-modal)
- Blind evaluation protocol

**Acceptance Criteria**:
- `results/eval_metrics.json` contains:
  - `{model_name: {pass_at_1, human_pref, harmonic_mean}}`
- Tri-modal harmonic mean > best baseline harmonic mean (PoC pass)

**Files**:
- `src/evaluate.py`

---

### A-8: Visualization (Complexity: 6)

**Breakdown**: Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(1)

**Scope**:
- Figure 1: Weight trajectory (3 lines: exec, AI, human over progress)
- Figure 2: Per-signal reward trends (3 lines over steps)
- Figure 3: Baseline comparison bar chart (pass@1, pref, harmonic for 4 models)
- Figure 4: Training curves (loss, reward, KL over steps)
- Figure 5: Gate metrics comparison (target vs actual harmonic mean)

**Acceptance Criteria**:
- All 5 figures saved to `figures/` as PNG
- Publication-quality formatting (labels, legend, axes)
- Gate metrics figure shows ≥3% improvement

**Files**:
- `src/visualize.py`

---

## Key Design Decisions

**Decision 1: Single Aggregator vs Separate Models**
- Choice: Single TriModalRewardAggregator module
- Rationale: Centralized weight management, easier to track phase transitions
- Alternative: 3 separate reward models with external scheduler (more complex)

**Decision 2: Cached Human Annotations vs Real-Time**
- Choice: Hybrid - cache 500 training samples, request new for test set
- Rationale: PoC budget constraint (500 samples), test set needs blind evaluation
- Implementation: `annotation_interface.py` serves Flask UI

**Decision 3: Reward Model Architecture**
- Choice: CodeGen-350M with binary classification head
- Rationale: Smaller than policy model (1.5B), faster inference, standard RLHF approach
- Alternative: Same-size model (more expensive, no clear benefit for PoC)

---

## Dependencies & Integration

**External Libraries**:
- PyTorch 2.0+
- Transformers 4.30+ (HuggingFace)
- Datasets 2.12+ (HuggingFace)
- TRL 0.4+ (PPO implementation)
- Flask 2.0+ (annotation interface)
- Matplotlib, Seaborn (visualization)

**Hardware Requirements**:
- 1× A100 GPU (40GB) minimum
- Gradient checkpointing for 1.5B model
- Mixed precision training (fp16)

**Inter-Module Dependencies**:
```
data_loader → baseline_models, ppo_trainer
reward_model → baseline_models (AI-only), feedback (AIFeedback)
tri_modal_aggregator → ppo_trainer
feedback → ppo_trainer, baseline_models
ppo_trainer → train
train → run_experiment
evaluate → visualize
```

---

## Risk Mitigation

**Risk 1: Human Annotation Cost**
- Impact: High (500 samples, 3 annotators = 1500 annotations)
- Mitigation: Start with 100 samples, validate inter-annotator agreement (α ≥ 0.6), expand if budget permits

**Risk 2: Reward Model Training Instability**
- Impact: Medium (affects AI baseline + tri-modal performance)
- Mitigation: Use standard RLHF techniques (Bradley-Terry model, preference pairs), validate on held-out set

**Risk 3: PPO Convergence**
- Impact: Medium (PoC validation depends on training success)
- Mitigation: Standard PPO hyperparameters from literature (clip=0.2, lr=5e-5), monitor KL divergence

**Risk 4: Single-Seed Variance**
- Impact: Low (PoC only validates direction, not significance)
- Mitigation: Accept limitation, document in paper, flag for future multi-seed validation

---

## Success Criteria

**PoC Pass Conditions**:
1. Code runs without error through full training loop (10k steps)
2. `harmonic_mean_trimodal > harmonic_mean_best_baseline` (any positive improvement)

**Gate Validation (MUST_WORK)**:
- If PoC passes → Proceed to dependent hypotheses (H-M1, H-M2, H-M3)
- If PoC fails → ABANDON approach, route to Phase 0 for new research question

**Target Metrics**:
- Harmonic mean ≥ 0.515 (≥3% over best baseline ~0.50)
- Pass@1: Competitive with execution-only baseline (~0.45)
- Human preference: Competitive with human-only baseline (~0.7)

---

**Document Status**: ✅ COMPLETED  
**Next Phase**: Phase 4 - Implementation (Agent-based)  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-e1/03_architecture.md`
