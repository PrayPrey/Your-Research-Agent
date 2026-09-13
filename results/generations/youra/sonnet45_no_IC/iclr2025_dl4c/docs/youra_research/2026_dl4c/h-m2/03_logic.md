# Logic Design: h-m2
# Phase 2 AI Feedback Peak Validation

**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Date**: 2026-07-12  
**Budget**: 6 subtasks

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from base code  
**Analyzed Path**: `docs/youra_research/h-m1/code/`  
**Relevant Symbols**: Phase1AnalysisTriModalAggregator, Phase1PPOTrainer, CheckpointLogger, FeedbackCollector

**Critical Findings**:
- h-m1 implementation fully operational and validated (MUST_WORK gate passed)
- Verified actual API signatures from implementation code
- Key parameter names confirmed: `training_progress` (float [0,1]), `test_cases` (str)
- Phase 1 checkpoint system operational - extending to Phase 2
- All feedback collectors return proper types (torch.Tensor or float)

---

## Knowledge Base Research (Archon)

**Applied**: PyTorch Checkpoint Loading Pattern  
**Applied**: Gaussian Weight Scheduling (from diffusion models)  
**Applied**: Training Progress Tracking  
**Applied**: Dynamic Weight Configuration

---

## B-1: Phase2 Aggregator Implementation (Complexity: 10, Budget: 3)

**Applied**: Gaussian Weight Scheduling, Dynamic Weight Configuration

### API Signatures

```python
from typing import Tuple, Dict
import torch
import torch.nn as nn
from torch import Tensor
import numpy as np
import sys
import os

# Import h-m1 base class
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../h-m1/code'))
from models.phase1_tri_modal_aggregator import Phase1AnalysisTriModalAggregator


class Phase2TriModalAggregator(Phase1AnalysisTriModalAggregator):
    def __init__(
        self,
        config: dict = None,
        phase2_checkpoints: list = None,
        ai_peak_progress: float = 0.50
    ):
        """Extend h-m1 aggregator with Phase 2 AI peak scheduling."""
        super().__init__(config, phase1_checkpoints=phase2_checkpoints or [0.30, 0.40, 0.50, 0.60, 0.70])
        self.phase2_start = 0.30
        self.phase2_end = 0.70
        self.ai_peak_progress = ai_peak_progress
    
    def compute_dynamic_weights(self, training_progress: float) -> Dict[str, float]:
        """Compute Phase 2 weights with AI peak at ~50%. Returns: {execution, ai, human}"""
        ...
    
    def forward(
        self,
        execution_reward: Tensor,  # [B]
        ai_reward: Tensor,  # [B]
        human_reward: Tensor,  # [B]
        training_progress: float  # [0,1]
    ) -> Tensor:
        """Forward pass with Phase 2 AI peak scheduling. Returns: [B]"""
        ...
    
    def find_ai_weight_peak(self) -> Tuple[float, Dict[str, float]]:
        """Find AI weight peak location. Returns: (peak_progress, weights_at_peak)"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| execution_reward | [B] | Inherited from h-m1 |
| ai_reward | [B] | Inherited from h-m1 |
| human_reward | [B] | Inherited from h-m1 |
| aggregated_reward | [B] | Weighted combination |

### Pseudo-code

```
compute_dynamic_weights(training_progress):
    1. Map progress to Phase 2 range: phase2_progress = (progress - 0.30) / 0.40
    2. Clip to [0, 1]
    3. AI weight: Gaussian peak at 0.5 Phase 2 progress
       ai_weight = 0.50 * exp(-((phase2_progress - 0.5)^2) / 0.05)
       ai_weight = max(0.30, ai_weight)  # Floor at 30%
    4. Execution weight: Linear decay
       exec_weight = 0.50 - 0.30 * phase2_progress  # 0.50 → 0.20
    5. Human weight: Linear increase
       human_weight = 0.10 + 0.10 * phase2_progress  # 0.10 → 0.20
    6. Normalize: total = exec_weight + ai_weight + human_weight
    7. Return {execution: exec_weight/total, ai: ai_weight/total, human: human_weight/total}

find_ai_weight_peak():
    1. Extract all AI weights from checkpoint_data (Phase 2 range)
    2. Find argmax: peak_idx = np.argmax(ai_weights)
    3. Return (checkpoint_data[peak_idx]['progress'], checkpoint_data[peak_idx])
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Gaussian AI peak | Implement Gaussian weight curve centered at 50% Phase 2 |
| L-1-2 | Weight normalization | Ensure weights sum to 1.0 at all progress points |
| L-1-3 | Peak detection | Find argmax of AI weight trajectory |

---

## B-3: Phase2 PPO Trainer (Complexity: 9, Budget: 2)

**Applied**: PyTorch Checkpoint Loading, Training Progress Tracking

### API Signatures

```python
from typing import Dict, List
from pathlib import Path
import torch
from torch.utils.data import DataLoader
import sys
import os

# Import h-m1 base class
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../h-m1/code'))
from train.phase1_ppo_trainer import Phase1PPOTrainer


class Phase2PPOTrainer(Phase1PPOTrainer):
    def __init__(
        self,
        checkpoint_path: str,
        aggregator,  # Phase2TriModalAggregator
        feedback_collector,
        config: dict
    ):
        """Initialize Phase 2 PPO trainer by loading h-m1 checkpoint at 30%."""
        # Load checkpoint first
        checkpoint = self.load_h_m1_checkpoint(checkpoint_path)
        
        # Initialize with loaded state
        super().__init__(checkpoint['model_name'], aggregator, feedback_collector, config)
        
        # Load model state
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        # Phase 2 configuration
        self.phase2_start_episode = 3000  # 30% of 10k total episodes
        self.checkpoint_milestones = [0.30, 0.40, 0.50, 0.60, 0.70]
    
    def load_h_m1_checkpoint(self, checkpoint_path: str) -> Dict:
        """Load h-m1 checkpoint at 30% progress. Returns: checkpoint dict"""
        ...
    
    def compute_training_progress(self, current_episode: int, total_episodes: int) -> float:
        """Map episode to training progress. Returns: [0.30, 0.70]"""
        ...
    
    def train(
        self,
        dataloader: DataLoader,
        total_episodes: int = 10000
    ) -> Dict[str, List[float]]:
        """Training loop for Phase 2 (30%→70%). Returns: history dict"""
        ...
    
    def evaluate_checkpoint(self, dataloader: DataLoader) -> Dict[str, float]:
        """Evaluate pass@1 and quality at checkpoint. Returns: {pass_at_1, quality}"""
        ...
    
    def save_checkpoint(self, path: str, progress: float, metrics: Dict):
        """Save Phase 2 checkpoint with metadata."""
        ...
```

### Pseudo-code

```
compute_training_progress(current_episode, total_episodes):
    1. Adjust for Phase 2 start: adjusted = current_episode + 3000
    2. Compute progress: progress = adjusted / total_episodes
    3. Return progress  # Range: [0.30, 0.70]

train(dataloader, total_episodes):
    1. Initialize history: {loss: [], reward: [], weights: [], pass_at_1: [], quality: []}
    2. For episode in range(total_episodes):
       a. Get batch from dataloader
       b. Compute training_progress = compute_training_progress(episode, total_episodes)
       c. Call train_step (inherited from Phase1PPOTrainer)
       d. If checkpoint milestone:
          - Evaluate: metrics = evaluate_checkpoint(val_dataloader)
          - Log: checkpoint_logger.log_weights(progress, weights)
          - Log: checkpoint_logger.log_pass_at_1(progress, metrics['pass_at_1'])
          - Log: checkpoint_logger.log_quality(progress, metrics['quality'])
          - Save: save_checkpoint(path, progress, metrics)
       e. Append metrics to history
    3. Return history

evaluate_checkpoint(dataloader):
    1. Set model.eval()
    2. Initialize: total_passed = 0, total_quality = 0, total_samples = 0
    3. For batch in dataloader:
       a. Generate code: outputs = model.generate(batch['input_ids'])
       b. Decode: codes = tokenizer.batch_decode(outputs)
       c. For code, tests, task_id in batch:
          - Execution: exec_reward = feedback_collector.execution.compute_reward(code, tests)
          - Quality: quality_score = feedback_collector.human.compute_reward(code, task_id)
          - total_passed += exec_reward
          - total_quality += quality_score
          - total_samples += 1
    4. Set model.train()
    5. Return {pass_at_1: total_passed/total_samples, quality: total_quality/total_samples}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Checkpoint loading | Load h-m1 30% checkpoint and resume training |
| L-3-2 | Progress mapping | Map episode to Phase 2 progress range [30%, 70%] |

---

## B-5: Phase2 Metrics Module (Complexity: 11, Budget: 3)

**Applied**: Statistical Analysis, Gate Validation Logic

### API Signatures

```python
from typing import Tuple, Dict, List
import numpy as np
from scipy.stats import pearsonr


class Phase2Analyzer:
    def __init__(self, checkpoint_data: List[Dict]):
        """Initialize analyzer with Phase 2 checkpoint data."""
        self.checkpoint_data = checkpoint_data
        self.phase2_range = (0.30, 0.70)
    
    def find_ai_weight_peak(self) -> Tuple[float, Dict[str, float]]:
        """Find AI weight peak in Phase 2. Returns: (peak_progress, weights_at_peak)"""
        ...
    
    def compute_quality_improvement_rate(self) -> float:
        """Compute quality improvement rate. Returns: (quality_70% - quality_30%) / 0.40"""
        ...
    
    def compute_correctness_maintenance(self) -> Dict[str, float]:
        """Check correctness maintained. Returns: {ratio, pass_30, pass_70, threshold}"""
        ...
    
    def validate_gate_criteria(self) -> Dict[str, bool]:
        """Validate all 3 gates. Returns: {gate1, gate2, gate3, overall}"""
        ...
    
    def generate_report(self) -> str:
        """Generate gate validation report. Returns: formatted string"""
        ...
```

### Pseudo-code

```
find_ai_weight_peak():
    1. Filter checkpoints: phase2_data = [cp for cp in data if 0.30 <= cp['progress'] <= 0.70]
    2. Extract AI weights: ai_weights = [cp['ai_weight'] for cp in phase2_data]
    3. Find peak: peak_idx = np.argmax(ai_weights)
    4. Get peak data: peak_checkpoint = phase2_data[peak_idx]
    5. Return (peak_checkpoint['progress'], peak_checkpoint)

compute_quality_improvement_rate():
    1. Find 30% checkpoint: cp_30 = [cp for cp in data if abs(cp['progress'] - 0.30) < 0.01][0]
    2. Find 70% checkpoint: cp_70 = [cp for cp in data if abs(cp['progress'] - 0.70) < 0.01][0]
    3. Compute rate: rate = (cp_70['quality'] - cp_30['quality']) / 0.40
    4. Return rate

compute_correctness_maintenance():
    1. Find checkpoints at 30% and 70%
    2. Extract pass@1 scores: pass_30 = cp_30['pass_at_1'], pass_70 = cp_70['pass_at_1']
    3. Compute ratio: ratio = pass_70 / pass_30
    4. Check threshold: maintained = (ratio >= 0.95)
    5. Return {ratio, pass_30, pass_70, threshold: 0.95, maintained}

validate_gate_criteria():
    1. Gate 1: AI peak detection
       a. peak_progress, weights = find_ai_weight_peak()
       b. gate1 = (weights['ai'] > weights['execution']) and (weights['ai'] > weights['human'])
    2. Gate 2: Quality improvement
       a. improvement_rate = compute_quality_improvement_rate()
       b. gate2 = (improvement_rate > 0)
    3. Gate 3: Correctness maintenance
       a. maintenance = compute_correctness_maintenance()
       b. gate3 = maintenance['maintained']
    4. Overall: overall = gate1 and gate2 and gate3
    5. Return {gate1, gate2, gate3, overall}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | AI peak detection | Find argmax of AI weight in Phase 2 range |
| L-5-2 | Quality improvement | Compute improvement rate from 30% to 70% |
| L-5-3 | Correctness check | Verify pass@1 regression ≤ 5% |

---

## B-6: Gate Validator (Complexity: 8, Budget: 0)

**Note**: Core logic in B-5 (Phase2Analyzer). Wrapper class for report generation.

**Applied**: Gate Validation Pattern

### API Signatures

```python
class Phase2GateValidator:
    def __init__(
        self,
        weight_trajectory: List[Dict],
        quality_trajectory: List[Dict],
        pass1_trajectory: List[Dict]
    ):
        """Initialize gate validator with trajectories."""
        self.analyzer = Phase2Analyzer(weight_trajectory)
        self.quality_trajectory = quality_trajectory
        self.pass1_trajectory = pass1_trajectory
    
    def validate_gate1_ai_peak(self) -> bool:
        """Validate Gate 1: AI weight is highest at peak. Returns: True/False"""
        ...
    
    def validate_gate2_quality_improved(self) -> bool:
        """Validate Gate 2: Quality improved. Returns: True/False"""
        ...
    
    def validate_gate3_correctness_maintained(self) -> bool:
        """Validate Gate 3: Pass@1 maintained. Returns: True/False"""
        ...
    
    def validate_all_gates(self) -> Dict[str, bool]:
        """Validate all gates. Returns: {gate1, gate2, gate3, overall}"""
        ...
    
    def generate_gate_report(self) -> str:
        """Generate formatted gate report. Returns: markdown string"""
        ...
```

---

## B-7: Visualization Extension (Complexity: 9, Budget: 2)

**Applied**: Matplotlib Publication-Quality Plotting

### API Signatures

```python
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_weight_trajectory_phase2(
    weight_history: List[Dict],
    save_path: str,
    h_m1_history: List[Dict] = None
):
    """Plot Phase 2 weight trajectory with AI peak highlight."""
    ...


def plot_quality_vs_correctness(
    quality_history: List[Dict],
    pass1_history: List[Dict],
    save_path: str
):
    """Dual-axis plot: quality and correctness over Phase 2."""
    ...


def plot_phase2_improvement_rates(
    metrics: Dict[str, float],
    save_path: str
):
    """Bar chart: quality improvement rate and correctness maintenance."""
    ...


def plot_harmonic_mean_progress(
    harmonic_history: List[Dict],
    h_m1_baseline: List[Dict],
    save_path: str
):
    """Harmonic mean(pass@1, quality) comparison with h-m1."""
    ...


def plot_gate_metrics(
    metrics: Dict[str, float],
    targets: Dict[str, float],
    save_path: str
):
    """Bar chart: Gate metrics vs targets (green=pass, red=fail)."""
    ...
```

### Pseudo-code

```
plot_weight_trajectory_phase2(weight_history, save_path):
    1. Extract: progress = [w['progress'] for w in weight_history if 0.30 <= w['progress'] <= 0.70]
    2. Extract weights: exec_weights, ai_weights, human_weights
    3. Find AI peak: peak_idx = np.argmax(ai_weights)
    4. Create figure: fig, ax = plt.subplots(figsize=(10, 6))
    5. Plot lines: ax.plot(progress, exec_weights, label='Execution', color='blue')
                   ax.plot(progress, ai_weights, label='AI', color='green')
                   ax.plot(progress, human_weights, label='Human', color='red')
    6. Highlight peak: ax.axvline(progress[peak_idx], color='green', linestyle='--', alpha=0.5)
    7. Annotate: ax.text(progress[peak_idx], ai_weights[peak_idx], 'AI Peak')
    8. Labels: xlabel='Training Progress', ylabel='Weight', title='Phase 2 Weight Trajectory'
    9. Save: plt.savefig(save_path, dpi=300, bbox_inches='tight')

plot_gate_metrics(metrics, targets, save_path):
    1. Prepare data: gate_names = ['AI Peak', 'Quality Improved', 'Correctness Maintained']
                     actual = [metrics['gate1'], metrics['gate2'], metrics['gate3']]
                     target = [targets['gate1'], targets['gate2'], targets['gate3']]
    2. Create figure: fig, ax = plt.subplots(figsize=(8, 6))
    3. Bar positions: x = np.arange(len(gate_names))
    4. Plot bars: ax.bar(x - 0.2, target, width=0.4, label='Target', color='gray', alpha=0.5)
                  colors = ['green' if a >= t else 'red' for a, t in zip(actual, target)]
                  ax.bar(x + 0.2, actual, width=0.4, label='Actual', color=colors)
    5. Labels: xlabel='Gate Criteria', ylabel='Pass (1) / Fail (0)', title='Gate Validation'
    6. Save: plt.savefig(save_path, dpi=300)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Weight trajectory plot | Phase 2 weight curves with AI peak highlight |
| L-7-2 | Gate metrics plot | Bar chart showing gate results (mandatory figure) |

---

## B-8: Integration Testing (Complexity: 10, Budget: 0)

**Note**: Allocated to Config Agent (testing utilities)

---

## External Dependencies API (Base Hypothesis h-m1)

### API Signatures (From Actual Code)

The following APIs are called from base hypothesis. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-m1/code/models/phase1_tri_modal_aggregator.py (ACTUAL CODE)
class Phase1AnalysisTriModalAggregator(TriModalAggregator):
    def __init__(self, config: dict = None, phase1_checkpoints: list = None):
        """Extend h-e1 aggregator with Phase 1 checkpoint logging."""
        ...
    
    def log_phase1_checkpoint(
        self,
        progress: float,
        exec_w: float,
        ai_w: float,
        human_w: float
    ):
        """Log checkpoint data for Phase 1 analysis."""
        ...
    
    def forward(
        self,
        execution_reward: torch.Tensor,  # [B]
        ai_reward: torch.Tensor,  # [B]
        human_reward: torch.Tensor,  # [B]
        training_progress: float  # [0,1] - VERIFIED PARAMETER NAME
    ) -> torch.Tensor:
        """Forward pass with Phase 1 checkpoint logging. Returns: [B]"""
        ...
    
    def get_checkpoint_data(self) -> list:
        """Return all logged checkpoint data for analysis."""
        ...


# From: docs/youra_research/h-m1/code/train/phase1_ppo_trainer.py (ACTUAL CODE)
class Phase1PPOTrainer(SimplifiedPPOTrainer):
    def __init__(
        self,
        model_name: str,
        aggregator,
        feedback_collector,
        config: dict
    ):
        """Extend h-e1 PPO trainer with Phase 1 progress tracking."""
        ...
    
    def compute_training_progress(
        self,
        current_episode: int,
        total_episodes: int
    ) -> float:
        """Compute training progress as fraction complete. Returns: [0,1]"""
        ...
    
    def evaluate_checkpoint(self, dataloader) -> float:
        """Evaluate pass@1 on validation set. Returns: pass_at_1 score"""
        ...


# From: docs/youra_research/h-m1/code/utils/checkpoint_logger.py (ACTUAL CODE)
class CheckpointLogger:
    def __init__(self, log_dir: str = "./checkpoints"):
        """Initialize checkpoint logger."""
        ...
    
    def log_weights(self, progress: float, weights: Dict[str, float]):
        """Log weight coefficients at checkpoint."""
        ...
    
    def log_pass_at_1(self, progress: float, score: float):
        """Log pass@1 score at checkpoint."""
        ...
    
    def log_quality(self, progress: float, score: float):
        """Log quality score at checkpoint."""
        ...
    
    def save_checkpoint_file(self, progress: float, data: dict):
        """Save checkpoint to JSON file."""
        ...
    
    def load_all_checkpoints(self) -> Dict:
        """Load all checkpoints from directory. Returns: {progress: data}"""
        ...


# From: docs/youra_research/h-m1/code/models/feedback_collectors.py (ACTUAL CODE)
class FeedbackCollector:
    def __init__(
        self,
        execution_timeout: float = 5.0,
        reward_model_name: str = "microsoft/codebert-base",
        reward_model_path: str = None,
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
    def compute_reward(
        self,
        code: str,
        test_cases: str,  # VERIFIED PARAMETER NAME
        entry_point: str = "main"
    ) -> float:
        """Execute code. Returns: [0,1] pass rate"""
        ...


class HumanFeedback:
    def compute_reward(self, code: str, task_id: str) -> float:
        """Human preference from cache. Returns: [0,1] quality score"""
        ...


# From: docs/youra_research/h-m1/code/data/dataset.py (ACTUAL CODE)
class CodeGenerationDataset:
    def __init__(self, cache_dir: str = "./.data_cache/datasets"):
        """Initialize dataset loader for HumanEval + MBPP."""
        ...
    
    def load_datasets(self):
        """Load HumanEval and MBPP from HuggingFace."""
        ...
    
    def create_splits(
        self,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1
    ):
        """Create train/val/test splits."""
        ...
    
    def get_dataloader(
        self,
        split: str,
        batch_size: int = 8
    ):
        """Get DataLoader for split. Returns: DataLoader"""
        ...
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, NOT spec!)

**Critical Parameter Names**:
- `training_progress` (float [0,1]) in aggregator.forward()
- `test_cases` (str) in feedback collectors
- `progress` (float) in checkpoint logger methods
- All return types verified from actual code

---

## Integration Points

### Data Flow

```
1. Load h-m1 checkpoint at 30% progress
2. Initialize Phase2TriModalAggregator with AI peak scheduling
3. Initialize Phase2PPOTrainer with loaded checkpoint
4. Training loop (episodes 0→10,000 mapped to 30%→70%):
   - Compute training_progress = (episode + 3000) / 10000
   - At checkpoints [30%, 40%, 50%, 60%, 70%]:
     - Log weights via CheckpointLogger
     - Evaluate pass@1 and quality
     - Save checkpoint
   - Standard PPO update with Phase 2 tri-modal reward
5. Post-training analysis:
   - Phase2Analyzer loads all checkpoint data
   - find_ai_weight_peak()
   - compute_quality_improvement_rate()
   - compute_correctness_maintenance()
   - validate_gate_criteria()
6. Generate 4 required figures
7. Output gate validation report
```

### Checkpoint Structure (Phase 2)

```python
checkpoint = {
    'progress': 0.50,  # float [0.30, 0.70]
    'phase': 'Phase 2',
    'episode': 5000,
    'model_state_dict': {...},
    'optimizer_state_dict': {...},
    'aggregator_state_dict': {...},
    'metrics': {
        'loss': 0.42,
        'reward': 0.71,
        'execution_weight': 0.35,
        'ai_weight': 0.45,  # Peak at 50%
        'human_weight': 0.20,
        'pass_at_1': 0.64,
        'quality': 0.58
    }
}
```

---

## Budget Summary

| Task | Complexity | Allocated | Used |
|------|------------|-----------|------|
| B-1: Phase2 Aggregator | 10 | 3 | 3 |
| B-3: Phase2 PPO Trainer | 9 | 2 | 2 |
| B-5: Phase2 Metrics | 11 | 3 | 3 |
| B-6: Gate Validator | 8 | 0 | 0 |
| B-7: Visualization | 9 | 2 | 2 |
| B-8: Integration Testing | 10 | 0 | 0 |
| **Total** | **57** | **10** | **10** |

**Note**: B-6 logic embedded in B-5. B-8 allocated to Config Agent.

---

## Implementation Notes

### Error Handling

**Checkpoint Loading**: Verify checkpoint metadata (progress=0.30, phase="Phase 1") before loading  
**Float Comparison**: Use tolerance `abs(progress - checkpoint) < 0.01` for milestone detection  
**Evaluation Failure**: Log warning and return 0.0 if evaluation fails  
**Peak Detection**: Handle case where no peak found (return first/last checkpoint)

### Configuration

```python
# Phase 2 checkpoints
phase2_checkpoints = [0.30, 0.40, 0.50, 0.60, 0.70]

# Training config
learning_rate = 1e-5  # Reduced from Phase 1's 5e-6
total_episodes = 10000  # Full training (30% already done in Phase 1)
batch_size = 64  # Increased from Phase 1's 8
phase2_start_episode = 3000  # 30% of 10k

# AI peak configuration
ai_peak_progress = 0.50  # Mid-Phase 2 (50% overall = 0.5 Phase 2 progress)
gaussian_sigma = 0.05  # Narrow peak
```

### Dependencies

```python
# From h-m1
from models.phase1_tri_modal_aggregator import Phase1AnalysisTriModalAggregator
from train.phase1_ppo_trainer import Phase1PPOTrainer
from utils.checkpoint_logger import CheckpointLogger
from models.feedback_collectors import FeedbackCollector
from data.dataset import CodeGenerationDataset

# Standard libraries
torch>=2.0.0
transformers>=4.30.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation (Agent-based)  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m2/03_logic.md`
