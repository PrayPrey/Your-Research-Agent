# Logic Design: h-m1
# Phase 1 Execution-Heavy Weight Validation

**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Date**: 2026-07-12  
**Budget**: 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from base code  
**Analyzed Path**: `docs/youra_research/h-e1/code/`  
**Relevant Symbols**: TriModalAggregator, SimplifiedPPOTrainer, FeedbackCollector, ExecutionFeedback, AIFeedback, HumanFeedback

**Critical Findings**:
- Base h-e1 implementation fully operational
- Verified actual API signatures from implementation (not specs)
- Key parameter names confirmed: `training_progress` (not `progress`), `test_cases` (not `test_suite`)
- All feedback collectors return torch.Tensor types

---

## Knowledge Base Research (Archon)

**Applied**: PyTorch Checkpoint Pattern  
**Applied**: Training Progress Tracking  
**Applied**: State Dict Save/Load Pattern

---

## A-1: Phase1 Aggregator Extension (Complexity: 7, Budget: 2)

**Applied**: PyTorch Module Extension Pattern

### API Signatures

```python
from typing import Tuple, Dict
import torch
from torch import Tensor
from h_e1.code.models.tri_modal_aggregator import TriModalAggregator


class Phase1AnalysisTriModalAggregator(TriModalAggregator):
    def __init__(
        self,
        num_phases: int = 3,
        initial_weights: list = None,
        peak_timesteps: list = None,
        decay_rates: list = None,
        percentile_window: int = 100,
        phase1_checkpoints: list = None
    ):
        """Extend h-e1 aggregator with Phase 1 checkpoint logging."""
        super().__init__(num_phases, initial_weights, peak_timesteps, decay_rates, percentile_window)
        self.phase1_checkpoints = phase1_checkpoints or [0.0, 0.1, 0.2, 0.3]
        self.checkpoint_logger = None  # Set externally
    
    def forward(
        self,
        execution_reward: Tensor,  # [B]
        ai_reward: Tensor,  # [B]
        human_reward: Tensor,  # [B]
        training_progress: float  # [0,1]
    ) -> Tuple[Tensor, Dict[str, float]]:
        """Forward with checkpoint logging. Returns: ([B], weights_dict)"""
        # Call parent forward
        aggregated_reward, weight_dict = super().forward(
            execution_reward,
            ai_reward,
            human_reward,
            training_progress
        )
        
        # Log checkpoints
        if self._is_checkpoint(training_progress) and self.checkpoint_logger:
            self.checkpoint_logger.log_weights(training_progress, weight_dict)
        
        return aggregated_reward, weight_dict
    
    def _is_checkpoint(self, progress: float) -> bool:
        """Check if current progress is a checkpoint."""
        for cp in self.phase1_checkpoints:
            if abs(progress - cp) < 0.001:  # Tolerance for float comparison
                return True
        return False
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| execution_reward | [B] | Inherited from h-e1 |
| ai_reward | [B] | Inherited from h-e1 |
| human_reward | [B] | Inherited from h-e1 |
| aggregated_reward | [B] | Inherited from h-e1 |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Checkpoint detection | Float comparison with tolerance for progress milestones |
| L-1-2 | Logger integration | External logger injection for weight logging |

---

## A-2: Phase1 PPO Trainer Extension (Complexity: 9, Budget: 2)

**Applied**: PyTorch Checkpoint Pattern, Training Progress Tracking

### API Signatures

```python
from typing import Dict, List
from pathlib import Path
import torch
from h_e1.code.train.ppo_trainer import SimplifiedPPOTrainer


class Phase1PPOTrainer(SimplifiedPPOTrainer):
    def __init__(
        self,
        model_name: str,
        aggregator,  # Phase1AnalysisTriModalAggregator
        feedback_collector,
        checkpoint_logger,
        learning_rate: float = 5e-6,
        clip_range: float = 0.2,
        device: str = "cuda",
        total_episodes: int = 10000,
        eval_dataloader = None
    ):
        """Extend h-e1 PPO trainer with Phase 1 monitoring."""
        super().__init__(model_name, aggregator, feedback_collector, learning_rate, clip_range, device)
        self.total_steps = total_episodes
        self.checkpoint_logger = checkpoint_logger
        self.eval_dataloader = eval_dataloader
        self.phase1_checkpoints = [0.0, 0.1, 0.2, 0.3, 0.7, 1.0]
        
        # Inject logger into aggregator
        self.aggregator.checkpoint_logger = checkpoint_logger
    
    def train(
        self,
        dataloader,
        total_episodes: int = 10000
    ) -> Dict[str, List[float]]:
        """Training loop with Phase 1 checkpoints."""
        self.total_steps = total_episodes
        history = {'loss': [], 'reward': [], 'weights': []}
        
        for episode in range(total_episodes):
            # Get batch
            batch = next(iter(dataloader))
            
            # Training step (calls parent train_step)
            metrics = self.train_step(
                prompts=batch['prompts'],
                test_cases=batch['test_cases'],
                task_ids=batch['task_ids']
            )
            
            # Compute progress
            training_progress = episode / total_episodes
            
            # Checkpoint evaluation
            if self._is_checkpoint(training_progress):
                pass_at_1 = self._evaluate_checkpoint()
                self.checkpoint_logger.log_pass_at_1(training_progress, pass_at_1)
                self._save_checkpoint(training_progress, metrics)
            
            # Log metrics
            history['loss'].append(metrics['loss'])
            history['reward'].append(metrics['reward'])
            history['weights'].append(metrics)
        
        return history
    
    def _is_checkpoint(self, progress: float) -> bool:
        """Check if progress is a checkpoint."""
        for cp in self.phase1_checkpoints:
            if abs(progress - cp) < 0.001:
                return True
        return False
    
    def _evaluate_checkpoint(self) -> float:
        """Evaluate pass@1 on validation set. Returns: [0,1]"""
        if self.eval_dataloader is None:
            return 0.0
        
        self.model.eval()
        total_passed = 0
        total_samples = 0
        
        with torch.no_grad():
            for batch in self.eval_dataloader:
                # Generate code
                inputs = self.tokenizer(batch['prompts'], return_tensors="pt", padding=True).to(self.device)
                outputs = self.model.generate(**inputs, max_new_tokens=256)
                codes = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                
                # Execute tests
                for code, tests in zip(codes, batch['test_cases']):
                    exec_reward = self.feedback_collector.execution.compute_reward(code, tests)
                    total_passed += exec_reward
                    total_samples += 1
        
        self.model.train()
        return total_passed / max(total_samples, 1)
    
    def _save_checkpoint(self, progress: float, metrics: Dict):
        """Save checkpoint to file."""
        checkpoint_data = {
            'progress': progress,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'aggregator_state_dict': self.aggregator.state_dict(),
            'metrics': metrics
        }
        self.checkpoint_logger.save_checkpoint_file(progress, checkpoint_data)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Checkpoint evaluation | Pass@1 computation at milestones |
| L-2-2 | Checkpoint saving | Model + optimizer + aggregator state persistence |

---

## A-3: Checkpoint Logger (Complexity: 6, Budget: 0)

**Note**: Allocated to Config Agent (utilities)

---

## A-4: Phase1 Metrics Module (Complexity: 10, Budget: 0)

**Note**: Allocated to Config Agent (analysis)

---

## External Dependencies API (Base Hypothesis h-e1)

### API Signatures (From Actual Code)

The following APIs are called from base hypothesis. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1/code/models/tri_modal_aggregator.py (ACTUAL CODE)
class TriModalAggregator(nn.Module):
    def __init__(
        self,
        num_phases: int = 3,
        initial_weights: list = None,
        peak_timesteps: list = None,
        decay_rates: list = None,
        percentile_window: int = 100
    ):
        """Initialize tri-modal aggregator with learnable weights."""
        ...
    
    def forward(
        self,
        execution_reward: torch.Tensor,  # [B] [0,1]
        ai_reward: torch.Tensor,  # [B] [-1,1]
        human_reward: torch.Tensor,  # [B] [0,1]
        training_progress: float  # [0,1] - VERIFIED PARAMETER NAME
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Aggregate rewards. Returns: ([B], weights_dict)"""
        ...
    
    def _compute_phase_weights(self, progress: float) -> torch.Tensor:
        """Compute Gaussian weights. Returns: [3]"""
        ...
    
    def get_current_weights(self, training_progress: float) -> Dict[str, float]:
        """Get current weights. Returns: {execution, ai, human}"""
        ...


# From: docs/youra_research/h-e1/code/train/ppo_trainer.py (ACTUAL CODE)
class SimplifiedPPOTrainer:
    def __init__(
        self,
        model_name: str,
        aggregator,
        feedback_collector,
        learning_rate: float = 5e-5,
        clip_range: float = 0.2,
        device: str = "cuda"
    ):
        """Initialize PPO trainer."""
        ...
    
    def train_step(
        self,
        prompts: list,  # List[str]
        test_cases: list,  # List[str] - VERIFIED PARAMETER NAME
        task_ids: list,  # List[str]
        max_new_tokens: int = 256
    ) -> Dict:
        """Single PPO step. Returns: metrics dict"""
        ...
    
    def save_checkpoint(self, checkpoint_dir: str):
        """Save model + aggregator."""
        ...


# From: docs/youra_research/h-e1/code/models/feedback_collectors.py (ACTUAL CODE)
class FeedbackCollector:
    def __init__(
        self,
        execution_timeout: float = 5.0,
        reward_model_name: str = "microsoft/codebert-base",
        reward_model_path: Optional[str] = None,
        annotation_cache_path: str = "./data/annotations/cache.json",
        device: str = "cuda"
    ):
        """Initialize all feedback collectors."""
        ...
    
    def collect_all(
        self,
        code: str,
        prompt: str,
        test_cases: str,  # VERIFIED PARAMETER NAME
        task_id: str,
        entry_point: str = "main"
    ) -> Dict[str, torch.Tensor]:
        """Collect all feedback. Returns: {execution, ai, human} as tensors"""
        ...


class ExecutionFeedback:
    def __init__(self, timeout: float = 5.0, sandbox: bool = True):
        """Initialize execution feedback."""
        ...
    
    def compute_reward(
        self,
        code: str,
        test_cases: str,  # VERIFIED PARAMETER NAME
        entry_point: str = "main"
    ) -> float:
        """Execute code. Returns: [0,1] pass rate"""
        ...


class AIFeedback(nn.Module):
    def compute_reward(
        self,
        code: str,
        prompt: str,
        device: str = "cuda"
    ) -> torch.Tensor:
        """AI reward. Returns: Tensor [-1,1]"""
        ...


class HumanFeedback:
    def compute_reward(
        self,
        code: str,
        task_id: str
    ) -> float:
        """Human preference. Returns: [0,1]"""
        ...
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, NOT spec!)

**Critical Parameter Names**:
- `training_progress` (not `progress` in aggregator.forward)
- `test_cases` (not `test_suite` in feedback collectors)
- Return types: All feedback collectors return torch.Tensor or float

---

## Integration Points

### Data Flow

```
DataLoader → {prompts, test_cases, task_ids}
  ↓
Phase1PPOTrainer.train()
  ↓
  For each episode:
    1. train_step() → calls parent SimplifiedPPOTrainer.train_step()
    2. Aggregator logs weights at checkpoints
    3. At checkpoints: evaluate_checkpoint() → pass@1
    4. save_checkpoint() → model + optimizer + aggregator
  ↓
CheckpointLogger → weights_phase1.csv, pass_at_1_trajectory.csv, progress_X.json
```

### Checkpoint Structure

```python
checkpoint = {
    'progress': 0.3,  # float [0,1]
    'model_state_dict': {...},
    'optimizer_state_dict': {...},
    'aggregator_state_dict': {...},
    'metrics': {
        'loss': 0.45,
        'reward': 0.67,
        'execution_weight': 0.72,
        'ai_weight': 0.18,
        'human_weight': 0.10
    }
}
```

---

## Budget Summary

| Task | Complexity | Allocated | Used |
|------|------------|-----------|------|
| A-1: Phase1 Aggregator | 7 | 2 | 2 |
| A-2: Phase1 PPO Trainer | 9 | 2 | 2 |
| **Total** | **16** | **4** | **4** |

**Remaining Tasks**: A-3 (Checkpoint Logger), A-4 (Phase1 Metrics) allocated to Config Agent

---

## Implementation Notes

### Error Handling

**Checkpoint Detection**: Use tolerance `abs(progress - checkpoint) < 0.001` for float comparison  
**Evaluation Failure**: Return 0.0 if eval_dataloader is None  
**Save Failure**: Log error but continue training

### Configuration

```python
# Phase 1 checkpoints
phase1_checkpoints = [0.0, 0.1, 0.2, 0.3, 0.7, 1.0]

# Training config (from h-e1)
learning_rate = 5e-6  # Updated from h-e1 optimal
total_episodes = 10000
batch_size = 8
```

### Dependencies

```
torch>=2.0.0
transformers>=4.30.0
```

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m1/03_logic.md`
