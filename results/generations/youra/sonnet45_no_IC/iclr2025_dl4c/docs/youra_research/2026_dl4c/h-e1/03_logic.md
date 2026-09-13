# Logic Design: h-e1
# Tri-Modal RL Framework for Code Generation

**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC)  
**Gate**: MUST_WORK  
**Date**: 2026-07-12  
**Budget**: 5 subtasks (A-6: 2, A-2: 2, A-4: 1)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: green-field - new API design  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## Knowledge Base Research (Archon)

**Applied**: PyTorch RL Training Loop  
**Applied**: HuggingFace TRL PPO  
**Applied**: Subprocess Code Execution Pattern  
**Applied**: RL Reward Normalization

---

## A-6: PPO Integration (Complexity: 13, Budget: 2)

**Applied**: PyTorch RL Training Loop, HuggingFace TRL PPO

### API Signatures

```python
from typing import Dict, Optional, List
import torch
from torch import Tensor
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import PPOTrainer as BasePPOTrainer, PPOConfig

class TriModalPPOTrainer:
    def __init__(
        self,
        model_name: str,
        aggregator: 'TriModalRewardAggregator',
        exec_feedback: 'ExecutionFeedback',
        ai_feedback: 'AIFeedback',
        human_feedback: 'HumanFeedback',
        ppo_config: PPOConfig,
        device: str = "cuda"
    ):
        """Initialize tri-modal PPO trainer."""
        ...

    def train_step(
        self,
        batch: Dict[str, Tensor],
        training_progress: float
    ) -> Dict[str, float]:
        """
        Single PPO training step with tri-modal reward.
        batch: {input_ids: [B, L], test_cases: List, sample_ids: List}
        training_progress: [0,1]
        Returns: {loss, reward, kl, exec_reward, ai_reward, human_reward}
        """
        ...

    def train(
        self,
        dataloader: 'DataLoader',
        steps: int = 10000
    ) -> Dict[str, List[float]]:
        """Full training loop. Returns: history dict"""
        ...

    def save_checkpoint(self, path: str):
        """Save model + optimizer + aggregator."""
        ...

    def load_checkpoint(self, path: str):
        """Load checkpoint."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | Tokenized prompts, B=32, L=512 |
| generated_ids | [B, L_gen] | Generated code |
| exec_reward | [B] | Pass rate [0,1] |
| ai_reward | [B] | AI score [-1,1] |
| human_reward | [B] | Preference [0,1] |
| aggregated_reward | [B] | Final reward |

### Pseudo-code

```
1. Generate: generated_ids = model.generate(input_ids)  # [B, L_gen]
2. Collect rewards (parallel):
   exec_reward = exec_feedback.compute_reward(code, test_cases)  # [B]
   ai_reward = ai_feedback.compute_reward(code, prompts)  # [B]
   human_reward = human_feedback.compute_reward(code, sample_ids)  # [B]
3. Aggregate: aggregated = aggregator(exec_reward, ai_reward, human_reward, progress)  # [B]
4. PPO update: loss = ppo_trainer.step(input_ids, generated_ids, aggregated)
5. Log metrics + weight trajectory
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Reward collection | Parallel collection of 3 feedback signals per batch |
| L-6-2 | PPO loop integration | Replace single reward with aggregator output |

---

## A-2: Baseline Models (Complexity: 12, Budget: 2)

**Applied**: Standard PyTorch RL baseline pattern

### API Signatures

```python
from trl import PPOTrainer, PPOConfig

class ExecutionOnlyPPO:
    def __init__(
        self,
        model_name: str = "Salesforce/codegen-1.5B-mono",
        lr: float = 5e-5,
        device: str = "cuda"
    ):
        """Execution feedback only baseline."""
        ...

    def train(
        self,
        dataloader: 'DataLoader',
        steps: int = 10000
    ) -> Dict[str, List[float]]:
        """Train with execution reward. Returns: {loss, reward, kl}"""
        ...

    def generate(self, prompt: str) -> str:
        """Generate code from prompt."""
        ...


class HumanOnlyPPO:
    def __init__(
        self,
        model_name: str = "Salesforce/codegen-1.5B-mono",
        lr: float = 5e-5,
        device: str = "cuda"
    ):
        """Human feedback only baseline."""
        ...

    def train(
        self,
        dataloader: 'DataLoader',
        steps: int = 10000
    ) -> Dict[str, List[float]]:
        """Train with human preference. Returns: {loss, reward, kl}"""
        ...

    def generate(self, prompt: str) -> str:
        """Generate code from prompt."""
        ...


class AIOnlyPPO:
    def __init__(
        self,
        model_name: str = "Salesforce/codegen-1.5B-mono",
        reward_model_path: str = "models/reward_model.pt",
        lr: float = 5e-5,
        device: str = "cuda"
    ):
        """AI reward model only baseline."""
        ...

    def train(
        self,
        dataloader: 'DataLoader',
        steps: int = 10000
    ) -> Dict[str, List[float]]:
        """Train with AI reward. Returns: {loss, reward, kl}"""
        ...

    def generate(self, prompt: str) -> str:
        """Generate code from prompt."""
        ...
```

### Shared Configuration

```python
ppo_config = PPOConfig(
    batch_size=32,
    learning_rate=5e-5,
    clip_range=0.2,
    vf_coef=0.5,
    ent_coef=0.01,
    gae_lambda=0.95,
    gamma=0.99
)
```

### Pseudo-code

```
# Shared pattern
1. Load CodeGen-1.5B model
2. Initialize PPOTrainer with config
3. For each step:
   a. generated = model.generate(input_ids)
   b. reward = feedback.compute_reward(code, context)  # Source differs
   c. loss = ppo_trainer.step(input_ids, generated, reward)
4. Save checkpoint
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Baseline infrastructure | Shared PPO setup and training loop |
| L-2-2 | Reward source switching | Parameterize reward source (exec/human/AI) |

---

## A-4: Feedback Collectors (Complexity: 11, Budget: 1)

**Applied**: Code execution sandbox, RLHF reward modeling

### API Signatures

```python
from typing import List, Dict, Optional
import subprocess
import torch
from torch import Tensor

class ExecutionFeedback:
    def __init__(self, timeout: int = 5):
        """Execute code against test cases."""
        ...

    def compute_reward(
        self,
        code: str,
        test_cases: List[Dict[str, any]]
    ) -> float:
        """
        Run tests and return pass rate.
        code: Generated Python code
        test_cases: [{input: ..., expected_output: ...}, ...]
        Returns: [0,1] - fraction passed
        """
        ...


class AIFeedback:
    def __init__(self, reward_model_path: str):
        """Load trained reward model."""
        ...

    def compute_reward(
        self,
        code: str,
        prompt: str
    ) -> float:
        """
        Score code quality.
        code: Generated code
        prompt: Problem description
        Returns: [-1,1] - normalized score
        """
        ...


class HumanFeedback:
    def __init__(self, annotation_cache_path: str = "data/annotations/annotations.json"):
        """Load cached annotations."""
        ...

    def compute_reward(
        self,
        code: str,
        sample_id: str
    ) -> float:
        """
        Retrieve preference score.
        code: Generated code
        sample_id: Unique ID
        Returns: [0,1] - averaged annotator scores
        """
        ...
```

### Pseudo-code

```
# ExecutionFeedback
1. For each test case:
   a. Run code via subprocess with timeout (5s)
   b. Compare output to expected
2. Return: num_passed / num_total

# AIFeedback
1. Tokenize prompt + code
2. Forward: logits = reward_model(input_ids)  # [1, 2]
3. Normalize: score = sigmoid(logits[1] - logits[0])  # [-1,1]

# HumanFeedback
1. Load cache (JSON)
2. Lookup sample_id
3. If cached: return avg score (3 annotators)
4. If missing: return neutral (0.5)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Unified feedback interface | Common `compute_reward()` API for all types |

---

## Core Module: Tri-Modal Reward Aggregator

**Applied**: Dynamic weight scheduling, percentile normalization

### API Signatures

```python
import torch
import torch.nn as nn
from torch import Tensor

class TriModalRewardAggregator(nn.Module):
    def __init__(self, num_phases: int = 3):
        """
        Dynamic reward aggregation with learnable weights.
        Parameters (9 learnable): peak_timesteps[3], sigma[3], scale[3]
        """
        super().__init__()
        self.peak_timesteps = nn.Parameter(torch.tensor([0.15, 0.5, 0.85]))
        self.sigma = nn.Parameter(torch.tensor([0.2, 0.2, 0.2]))
        self.scale = nn.Parameter(torch.tensor([1.0, 1.0, 1.0]))

    def forward(
        self,
        execution_reward: Tensor,  # [B] [0,1]
        ai_reward: Tensor,  # [B] [-1,1]
        human_reward: Tensor,  # [B] [0,1]
        training_progress: float  # [0,1]
    ) -> Tensor:
        """Aggregate rewards. Returns: [B] weighted sum"""
        ...

    def _compute_phase_weights(self, progress: float) -> Tensor:
        """Compute Gaussian weights. Returns: [3] summing to 1"""
        # weights = scale * exp(-((progress - peak_timesteps)^2) / (2 * sigma^2))
        # weights = weights / sum(weights)
        ...

    def _percentile_normalize(self, rewards: Tensor) -> Tensor:
        """Rank-based normalization. [B] -> [B] [0,1]"""
        ...

    def get_current_weights(self, progress: float) -> Dict[str, float]:
        """Return {execution: w1, ai: w2, human: w3}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| execution_reward | [B] | Raw pass rates [0,1] |
| ai_reward | [B] | Raw AI scores [-1,1] |
| human_reward | [B] | Raw preferences [0,1] |
| norm_exec/ai/human | [B] | Percentile-normalized [0,1] |
| weights | [3] | Phase weights [w_exec, w_ai, w_human] |
| aggregated_reward | [B] | Final reward |

### Pseudo-code

```
1. Normalize: norm_exec/ai/human = percentile_normalize(rewards)  # [B] -> [0,1]
2. Compute weights: weights = scale * exp(-((t - peaks)^2) / (2*sigma^2))  # [3]
3. Normalize weights: weights = weights / sum(weights)
4. Aggregate: aggregated = weights[0]*norm_exec + weights[1]*norm_ai + weights[2]*norm_human  # [B]
```

### Weight Trajectory

**Phase 1 (0-30%)**: Execution-dominant (w_exec≈0.7, w_ai≈0.2, w_human≈0.1)  
**Phase 2 (30-70%)**: AI-dominant (w_exec≈0.2, w_ai≈0.6, w_human≈0.2)  
**Phase 3 (70-100%)**: Human-dominant (w_exec≈0.1, w_ai≈0.2, w_human≈0.7)

---

## Training Configuration

### PPOConfig

```python
from dataclasses import dataclass

@dataclass
class PPOConfig:
    batch_size: int = 32
    learning_rate: float = 5e-5
    clip_range: float = 0.2
    vf_coef: float = 0.5
    ent_coef: float = 0.01
    gae_lambda: float = 0.95
    gamma: float = 0.99
    max_grad_norm: float = 1.0
    seed: int = 42
```

### Model Configuration

```python
@dataclass
class ModelConfig:
    model_name: str = "Salesforce/codegen-1.5B-mono"
    max_length: int = 512
    temperature: float = 0.8
    top_p: float = 0.95
```

---

## Integration Points

### Data Flow

```
DataLoader → {prompts, test_cases, sample_ids}
  ↓
Model.generate(prompts) → Generated code
  ↓
Parallel feedback collection:
  - ExecutionFeedback(code, test_cases) → exec_reward [B]
  - AIFeedback(code, prompts) → ai_reward [B]
  - HumanFeedback(code, sample_ids) → human_reward [B]
  ↓
TriModalAggregator(exec, ai, human, progress) → aggregated [B]
  ↓
PPOTrainer.step(prompts, generated, aggregated) → loss
  ↓
Optimizer.step() → Updated model
```

### Checkpoint Structure

```python
checkpoint = {
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "aggregator_state_dict": aggregator.state_dict(),
    "training_progress": current_step / total_steps,
    "step": current_step,
    "metrics_history": {
        "loss": [...],
        "reward": [...],
        "exec_reward": [...],
        "ai_reward": [...],
        "human_reward": [...],
        "weights": {"execution": [...], "ai": [...], "human": [...]}
    }
}
```

---

## Budget Summary

| Task | Complexity | Allocated | Used |
|------|------------|-----------|------|
| A-6: PPO Integration | 13 | 2 | 2 |
| A-2: Baseline Models | 12 | 2 | 2 |
| A-4: Feedback Collectors | 11 | 1 | 1 |
| **Total** | **36** | **5** | **5** |

---

## Implementation Notes

### Error Handling

**ExecutionFeedback**: Timeout/error → reward = 0.0  
**AIFeedback**: Inference error → reward = 0.0  
**HumanFeedback**: Missing annotation → reward = 0.5

### Logging

```python
# Every 10 steps
log_dict = {
    "step": current_step,
    "loss": loss.item(),
    "reward": aggregated_reward.mean().item(),
    "kl": kl_div.item(),
    "exec_reward": exec_reward.mean().item(),
    "ai_reward": ai_reward.mean().item(),
    "human_reward": human_reward.mean().item(),
    **aggregator.get_current_weights(progress)
}
```

### Dependencies

```
torch>=2.0.0
transformers>=4.30.0
trl>=0.4.0
datasets>=2.12.0
```

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-e1/03_logic.md`
