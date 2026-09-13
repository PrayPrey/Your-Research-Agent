# System Architecture: H-E1 Joint Training Existence

**Hypothesis:** H-E1  
**Type:** EXISTENCE (PoC)  
**Author:** Architecture Agent  
**Date:** 2026-07-13  
**Status:** Ready for Implementation

---

## Applied Patterns

Applied: Weighted Multi-Task Loss Summation (from HuggingFace Diffusers joint training)
Applied: AdamW Optimizer with Linear Warmup + Cosine Decay (from PyTorch LLM training)
Applied: Reference Policy Frozen Parameters Pattern (from DPO paper specification)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing code to analyze. Fresh implementation based on DPO (Rafailov et al. 2023) and SteerLM (Dong et al. 2023) specifications.

---

## System Overview

**Mission:** Validate joint DPO + attribute training convergence (MUST_WORK gate).

**Architecture Tier:** EXISTENCE - Minimal structure for "does it work?" validation.

**Core Components:**
- Data loading (HH-RLHF + OpenAssistant attributes)
- Baseline DPO-only model
- Joint DPO + attribute model
- Training loop with gradient monitoring
- Dual evaluation (preference + steering)

**Technology Stack:**
- PyTorch 2.0+
- HuggingFace Transformers 4.30+
- GPT-2 XL (1.5B) base model
- Single A100 40GB GPU

---

## Module Specifications

### DataModule (`code/data/dataset.py`)

**Dependencies:** HuggingFace Datasets, Transformers

```python
class JointDataset:
    def __init__(self, hh_rlhf_split: str, oasst_split: str, tokenizer, max_length: int = 512): ...
    def __getitem__(self, idx: int) -> dict: ...
    def __len__(self) -> int: ...

def load_datasets() -> tuple:
    """Returns (train_dataset, test_dataset)"""
    ...

def create_dataloaders(train_dataset, test_dataset, batch_size: int) -> tuple: ...
```

**Interface:**
- Input: Dataset identifiers ("Anthropic/hh-rlhf", "OpenAssistant/oasst1")
- Output: DataLoader yielding batches with keys: ["prompt_ids", "chosen_ids", "rejected_ids", "attributes"]
- Attributes format: dict {"helpfulness": int, "verbosity": int, "creativity": int} (1-5 scale)

---

### ModelModule (`code/models/model.py`)

**Dependencies:** PyTorch, Transformers

```python
class BaselineDPO(nn.Module):
    def __init__(self, model_name: str = "gpt2-xl", beta: float = 0.1): ...
    def forward(self, chosen_ids, rejected_ids, ref_chosen_logprobs, ref_rejected_logprobs) -> torch.Tensor: ...
    def compute_dpo_loss(self, chosen_logits, rejected_logits, ref_chosen, ref_rejected) -> torch.Tensor: ...

class JointDPOAttribute(nn.Module):
    def __init__(self, model_name: str = "gpt2-xl", beta: float = 0.1, alpha: float = 0.7, 
                 num_attributes: int = 3, num_levels: int = 5): ...
    def forward(self, chosen_ids, rejected_ids, ref_chosen_logprobs, ref_rejected_logprobs, 
                target_attrs) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]: ...
    def compute_dpo_loss(self, chosen_logits, rejected_logits, ref_chosen, ref_rejected) -> torch.Tensor: ...
    def compute_attr_loss(self, chosen_logits, target_attrs) -> torch.Tensor: ...

class ReferencePolicy(nn.Module):
    def __init__(self, model_name: str = "gpt2-xl"): ...
    @torch.no_grad()
    def compute_logprobs(self, input_ids, attention_mask) -> torch.Tensor: ...
```

**Interface:**
- BaselineDPO: Returns single loss (L_DPO)
- JointDPOAttribute: Returns (L_total, L_DPO, L_attr)
- ReferencePolicy: Frozen, computes log probabilities for DPO reference

---

### TrainingModule (`code/training/trainer.py`)

**Dependencies:** ModelModule, DataModule, PyTorch

```python
class JointTrainer:
    def __init__(self, model, ref_policy, train_loader, optimizer, scheduler, device, 
                 log_dir: str, checkpoint_dir: str): ...
    def train_step(self, batch: dict) -> dict: ...
    def compute_gradient_angle(self, loss_dpo: torch.Tensor, loss_attr: torch.Tensor) -> float: ...
    def save_checkpoint(self, step: int, metrics: dict): ...
    def train(self, num_steps: int, log_interval: int = 100, checkpoint_interval: int = 1000): ...
```

**Interface:**
- train_step(): Returns {"loss_total": float, "loss_dpo": float, "loss_attr": float, "gradient_angle": float}
- compute_gradient_angle(): Returns angle in degrees (0-180)
- train(): Main training loop with logging and checkpointing

---

### EvaluationModule (`code/evaluation/evaluate.py`)

**Dependencies:** ModelModule, OpenAI API, HuggingFace pipelines

```python
class PreferenceEvaluator:
    def __init__(self, gpt4_api_key: str): ...
    def evaluate(self, model, test_prompts: list, baseline_model) -> dict: ...
    def _judge_single(self, prompt: str, response_a: str, response_b: str) -> str: ...

class SteeringEvaluator:
    def __init__(self, attr_predictor_model: str): ...
    def evaluate(self, model, test_configs: list) -> dict: ...
    def _predict_attributes(self, response: str) -> dict: ...
    def _compute_accuracy(self, predicted: dict, target: dict, tolerance: float = 0.5) -> float: ...

def run_full_evaluation(joint_model, baseline_model, test_data, config) -> dict:
    """Returns {'win_rate': float, 'steering_accuracy': float, 'per_sample_results': list}"""
    ...
```

**Interface:**
- PreferenceEvaluator: Returns {"win_rate": float, "results": list[dict]}
- SteeringEvaluator: Returns {"accuracy": float, "per_attr_accuracy": dict, "results": list[dict]}
- run_full_evaluation(): Unified evaluation returning all gate metrics

---

### ConfigModule (`code/config/config.py`)

**Dependencies:** dataclasses, yaml

```python
@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "gpt2-xl"
    beta: float = 0.1
    alpha: float = 0.7
    
    # Training
    learning_rate: float = 1e-5
    batch_size: int = 128
    num_steps: int = 15000
    warmup_steps: int = 500
    weight_decay: float = 0.01
    
    # Data
    max_length: int = 512
    train_split: str = "train"
    test_split: str = "test"
    
    # Evaluation
    eval_samples: int = 1000
    steering_test_configs: int = 6
    
    # Infrastructure
    device: str = "cuda"
    seed: int = 42
    log_interval: int = 100
    checkpoint_interval: int = 1000

def load_config(config_path: str = None) -> ExperimentConfig: ...
def save_config(config: ExperimentConfig, path: str): ...
```

---

### VisualizationModule (`code/visualization/plots.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
def plot_training_curves(log_data: pd.DataFrame, save_path: str): ...
def plot_gradient_angles(angles: list, save_path: str): ...
def plot_gate_metrics(targets: dict, actuals: dict, save_path: str): ...
def plot_steering_heatmap(results: dict, save_path: str): ...
def plot_preference_distribution(results: list, save_path: str): ...
```

**Interface:**
- All functions accept data + save_path, return None (save figures to disk)
- plot_gate_metrics(): Mandatory figure with pass/fail indicators

---

### MainRunner (`code/main.py`)

**Dependencies:** All modules

```python
def setup_experiment(config: ExperimentConfig) -> dict:
    """Initialize datasets, models, optimizers. Returns {'train_loader': ..., 'model': ..., ...}"""
    ...

def run_training(config: ExperimentConfig, components: dict):
    """Execute training loop, save checkpoints and logs."""
    ...

def run_evaluation(config: ExperimentConfig, components: dict) -> dict:
    """Run preference + steering evaluation. Returns gate metrics."""
    ...

def generate_report(config: ExperimentConfig, metrics: dict, log_data: pd.DataFrame):
    """Generate 04_validation.md with pass/fail determination."""
    ...

def main():
    config = load_config()
    components = setup_experiment(config)
    run_training(config, components)
    metrics = run_evaluation(config, components)
    generate_report(config, metrics, log_data)
```

---

## File Structure

```
code/
├── data/
│   └── dataset.py          # DataModule
├── models/
│   └── model.py            # BaselineDPO, JointDPOAttribute, ReferencePolicy
├── training/
│   └── trainer.py          # JointTrainer
├── evaluation/
│   └── evaluate.py         # PreferenceEvaluator, SteeringEvaluator
├── config/
│   └── config.py           # ExperimentConfig
├── visualization/
│   └── plots.py            # All plotting functions
├── main.py                 # Main runner
└── requirements.txt        # Dependencies
```

---

## Data Flow

1. **Setup Phase:**
   - Load HH-RLHF + OpenAssistant datasets
   - Initialize GPT-2 XL base model
   - Create reference policy (frozen copy)
   - Initialize joint model with attribute head

2. **Training Loop (15k steps):**
   - Batch: {prompt_ids, chosen_ids, rejected_ids, attributes}
   - Reference policy: Compute logprobs (frozen)
   - Joint model forward: Compute L_DPO, L_attr
   - Combined loss: L_total = 0.7·L_DPO + 0.3·L_attr
   - Backward pass with gradient angle monitoring
   - Optimizer step (AdamW with schedule)
   - Log metrics every 100 steps
   - Checkpoint every 1000 steps

3. **Evaluation Phase:**
   - Load best checkpoint (lowest L_total)
   - Preference evaluation: 1000 prompts vs baseline
   - Steering evaluation: 6 configs × 100 prompts
   - Compute gate metrics: win_rate, steering_accuracy
   - Generate visualizations

4. **Reporting:**
   - Create 04_validation.md with pass/fail
   - Save all figures to figures/
   - Archive logs and checkpoints

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| Epic-1 | Data Pipeline | Load HH-RLHF + OpenAssistant, merge attributes, create dataloaders | 8/20 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| Epic-2 | Model Implementation | Implement BaselineDPO + JointDPOAttribute + ReferencePolicy | 12/20 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| Epic-3 | Training Loop | Implement trainer with gradient monitoring, checkpointing, logging | 10/20 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| Epic-4 | Evaluation System | GPT-4 preference judge + attribute steering accuracy evaluation | 9/20 | Module(2) + Deps(3) + Algo(2) + Integ(2) |
| Epic-5 | Visualization & Reporting | Generate required plots + 04_validation.md report | 5/20 | Module(1) + Deps(1) + Algo(1) + Integ(2) |

**Complexity Distribution:**
- High (9-12): Epic-2, Epic-3, Epic-4
- Medium (5-8): Epic-1, Epic-5
- Low (1-4): None

**Total Complexity:** 44/100 (5 epics, average 8.8/20)

**Estimated Timeline:** 3-5 days implementation + 3-5 days training/evaluation

---

## Key Design Decisions

**1. Reference Policy Strategy:**
- Frozen copy of base GPT-2 XL (no SFT pre-training for PoC simplicity)
- Alternative considered: SFT on high-quality subset (deferred to avoid dependency)

**2. Attribute Integration:**
- Prediction head on final hidden state (simple approach)
- Alternative considered: Attribute embeddings as input (rejected for PoC - adds complexity)

**3. Gradient Monitoring:**
- Compute angle between ∇L_DPO and ∇L_attr every 100 steps
- Alert threshold: 120° (catastrophic interference)
- Does NOT modify gradients (pure monitoring for PoC)

**4. Evaluation Infrastructure:**
- GPT-4 judge (external API dependency accepted)
- Attribute predictor: Use pre-trained model from HuggingFace
- No human evaluation (cost/time prohibitive for PoC)

---

## Dependencies & Constraints

**External Services:**
- HuggingFace Hub: Dataset and model downloads
- OpenAI API: GPT-4 judge for preference evaluation

**Hardware Requirements:**
- 1× NVIDIA A100 40GB GPU (minimum 32GB VRAM)
- 64GB system RAM
- 100GB storage (checkpoints + datasets)

**Software Requirements:**
- PyTorch 2.0+ with CUDA 11.8+
- HuggingFace Transformers 4.30+
- HuggingFace Datasets 2.12+
- OpenAI Python client

**Runtime Constraints:**
- No distributed training (single GPU)
- No hyperparameter tuning (fixed config)
- No multi-seed runs (single seed=42)

---

## Validation Criteria

**MUST_WORK Gate Metrics:**
1. Training Convergence: Both L_DPO and L_attr decrease monotonically
2. Preference Win Rate: ≥50% (better than random)
3. Steering Accuracy: ≥60% (better than chance)
4. Gradient Angle: <120° (no catastrophic interference)

**Success Condition:** ALL four metrics pass

**Failure Condition:** ANY metric fails → STOP entire H-BD1-v1 hypothesis chain

---

## Implementation Notes for Phase 4

**Critical Path:**
1. Epic-1 (Data) → Epic-2 (Model) → Epic-3 (Training) → Epic-4 (Eval) → Epic-5 (Report)
2. Must verify dataset accessibility BEFORE training (fail-fast pattern)
3. Gradient NaN detection → immediate training halt
4. Checkpoint corruption → automatic revert to previous valid checkpoint

**Testing Strategy:**
- Unit tests for DPO loss computation (verify against paper equations)
- Integration test with small dataset (100 samples, 50 steps)
- Full experiment run (15k steps)

**Logging Requirements:**
- Training: JSON lines format with {step, loss_dpo, loss_attr, loss_total, gradient_angle, lr}
- Evaluation: JSON with full per-sample results for error analysis
- Checkpoints: Include optimizer state for resumability

---

**Architecture Status:** Complete - Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder Agent
