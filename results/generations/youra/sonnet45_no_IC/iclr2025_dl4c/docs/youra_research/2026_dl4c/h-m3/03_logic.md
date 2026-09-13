# Logic Design: h-m3
# Phase 3 Human Feedback Peak Validation

**Hypothesis ID**: h-m3  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Date**: 2026-07-12  
**Budget**: 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from base code  
**Analyzed Path**: `docs/youra_research/h-m2/code/`  
**Relevant Symbols**: Phase2TriModalAggregator, Phase2PPOTrainer, FeedbackCollector, CheckpointLogger

**Critical Findings**:
- h-m2 implementation fully operational and validated (SHOULD_WORK gate passed)
- Verified actual API signatures from h-m2 implementation code
- Key parameter names confirmed: `training_progress` (float [0,1]), `test_cases` (str)
- Phase 2 checkpoint system operational at 70% progress - resuming for Phase 3
- All feedback collectors return proper types (torch.Tensor or float)
- Phase2TriModalAggregator extends Phase1AnalysisTriModalAggregator with AI peak scheduling
- Phase2PPOTrainer supports checkpoint loading and resume from h-m1 checkpoint at 30%

---

## Knowledge Base Research (Archon)

**Applied**: PyTorch Checkpoint Loading and Resume Pattern  
**Applied**: Progressive Weight Scheduling (from diffusion model training)  
**Applied**: RLHF Late-Stage Training Principles  
**Applied**: Conflict Case Evaluation Pattern

---

## C-2: Phase3 Aggregator Implementation (Complexity: 10, Budget: 3)

**Applied**: Progressive Weight Scheduling, RLHF Human Peak Pattern

### API Signatures

```python
from typing import Dict, Tuple
import torch
import torch.nn as nn
from torch import Tensor
import numpy as np

# Import h-m2 base class
from models.phase2_tri_modal_aggregator import Phase2TriModalAggregator


class Phase3TriModalAggregator(Phase2TriModalAggregator):
    def __init__(
        self,
        config: dict = None,
        phase3_checkpoints: list = None,
        human_peak_progress: float = 1.00
    ):
        """Extend h-m2 aggregator with Phase 3 human peak scheduling."""
        ...
    
    def compute_dynamic_weights(self, training_progress: float) -> Dict[str, float]:
        """Compute Phase 3 weights with human peak at 100%. Returns: {execution, ai, human}"""
        ...
    
    def forward(
        self,
        execution_reward: Tensor,  # [B]
        ai_reward: Tensor,  # [B]
        human_reward: Tensor,  # [B]
        training_progress: float  # [0,1]
    ) -> Tensor:
        """Forward pass with Phase 3 human peak scheduling. Returns: [B]"""
        ...
    
    def log_phase3_checkpoint(self, progress: float, weights: Dict[str, float]):
        """Log checkpoint data for Phase 3 analysis."""
        ...
    
    def validate_human_weight_increase(self) -> bool:
        """Validate human weight increases from 70% to 100%. Returns: True if w_human(100%) > w_human(70%)"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| execution_reward | [B] | Inherited from h-m2 |
| ai_reward | [B] | Inherited from h-m2 |
| human_reward | [B] | Inherited from h-m2 |
| aggregated_reward | [B] | Weighted combination |

### Pseudo-code

```
compute_dynamic_weights(training_progress):
    1. Map progress to Phase 3 range: phase3_progress = (progress - 0.70) / 0.30
    2. Clip to [0, 1]
    3. Human weight: Linear increase (dominant)
       human_weight = 0.40 + 0.30 * phase3_progress  # 0.40 → 0.70
    4. Execution weight: Linear decay
       exec_weight = 0.40 - 0.20 * phase3_progress  # 0.40 → 0.20
    5. AI weight: Maintain mid-level support
       ai_weight = 0.20 + 0.05 * phase3_progress  # 0.20 → 0.25
    6. Normalize: total = exec_weight + ai_weight + human_weight
    7. Return {execution: exec_weight/total, ai: ai_weight/total, human: human_weight/total}

validate_human_weight_increase():
    1. Get weights at 70%: w_70 = compute_dynamic_weights(0.70)
    2. Get weights at 100%: w_100 = compute_dynamic_weights(1.00)
    3. Return w_100['human'] > w_70['human']
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Human peak scheduling | Implement linear human weight increase 0.40 → 0.70 |
| L-2-2 | Weight normalization | Ensure weights sum to 1.0 at all progress points |
| L-2-3 | Human weight validation | Verify w_human(100%) > w_human(70%) |

---

## C-4: Phase3 PPO Trainer (Complexity: 9, Budget: 2)

**Applied**: PyTorch Checkpoint Loading, Training Progress Tracking

### API Signatures

```python
from typing import Dict, List
from pathlib import Path
import torch
from torch.utils.data import DataLoader

# Import h-m2 base class
from train.phase2_ppo_trainer import Phase2PPOTrainer


class Phase3PPOTrainer(Phase2PPOTrainer):
    def __init__(
        self,
        model,
        aggregator,  # Phase3TriModalAggregator
        feedback_collector,
        config: dict,
        start_episode: int = 7000  # 70% of 10k total episodes
    ):
        """Initialize Phase 3 PPO trainer by loading h-m2 checkpoint at 70%."""
        ...
    
    def load_h_m2_checkpoint(self, checkpoint_path: str) -> Dict:
        """Load h-m2 checkpoint at 70% progress. Returns: checkpoint dict"""
        ...
    
    def compute_training_progress(self, current_episode: int) -> float:
        """Map episode to training progress. Returns: [0.70, 1.00]"""
        ...
    
    def train(
        self,
        dataloader: DataLoader,
        num_episodes: int = 3000  # 30% of training (70% → 100%)
    ) -> Dict[str, List[float]]:
        """Training loop for Phase 3 (70%→100%). Returns: history dict"""
        ...
    
    def evaluate_checkpoint(self, dataloader: DataLoader) -> Dict[str, float]:
        """Evaluate pass@1 and quality at checkpoint. Returns: {pass@1, quality}"""
        ...
    
    def save_checkpoint(self, path: str, progress: float, metrics: Dict):
        """Save Phase 3 checkpoint with metadata."""
        ...
```

### Pseudo-code

```
compute_training_progress(current_episode):
    1. Adjust for Phase 3 start: adjusted = current_episode + 7000
    2. Compute progress: progress = adjusted / 10000
    3. Return progress  # Range: [0.70, 1.00]

load_h_m2_checkpoint(checkpoint_path):
    1. Load checkpoint: ckpt = torch.load(checkpoint_path)
    2. Verify metadata: assert ckpt['progress'] == 0.70, "Expected 70% checkpoint"
    3. Return ckpt

train(dataloader, num_episodes):
    1. Initialize history: {loss: [], reward: [], weights: [], pass_at_1: [], quality: []}
    2. For episode in range(num_episodes):
       a. Get batch from dataloader
       b. Compute training_progress = compute_training_progress(episode)
       c. Call train_step (inherited from Phase2PPOTrainer)
       d. If checkpoint milestone [0.70, 0.80, 0.90, 1.00]:
          - Evaluate: metrics = evaluate_checkpoint(val_dataloader)
          - Get weights: weights = aggregator.compute_dynamic_weights(progress)
          - Log: checkpoint_logger.log_weights(progress, weights)
          - Log: checkpoint_logger.log_pass_at_1(progress, metrics['pass@1'])
          - Save: save_checkpoint(path, progress, metrics)
       e. Append metrics to history
    3. Return history
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Checkpoint loading | Load h-m2 70% checkpoint and resume training |
| L-4-2 | Progress mapping | Map episode to Phase 3 progress range [70%, 100%] |

---

## C-5: Conflict Case Evaluator (Complexity: 9, Budget: 2)

**Applied**: Conflict Case Evaluation Pattern, Median Preference Scoring

### API Signatures

```python
from typing import Dict, List
import torch
from torch.utils.data import DataLoader
import numpy as np


class ConflictCaseEvaluator:
    def __init__(self, conflict_dataset):
        """Initialize conflict case evaluator."""
        ...
    
    def evaluate_conflict_cases(
        self,
        model,
        dataloader: DataLoader,
        feedback_collector
    ) -> Dict[str, float]:
        """Evaluate conflict cases. Returns: {median_preference, preference_scores, num_samples}"""
        ...
    
    def compute_preference_score(
        self,
        generated_code: str,
        sample_id: str,
        feedback_collector
    ) -> float:
        """Compute preference score for one sample. Returns: [0,1]"""
        ...
    
    def compute_median_preference(self, preference_scores: List[float]) -> float:
        """Compute median preference score. Returns: median value"""
        ...
    
    def check_collapse(self, median_preference: float) -> bool:
        """Check if collapsed to execution-only. Returns: True if median < 0.1"""
        ...
```

### Pseudo-code

```
evaluate_conflict_cases(model, dataloader, feedback_collector):
    1. Set model.eval()
    2. Initialize: preference_scores = []
    3. For batch in dataloader:
       a. Generate code: outputs = model.generate(batch['input_ids'])
       b. Decode: codes = tokenizer.batch_decode(outputs)
       c. For code, sample_id in batch:
          - pref = compute_preference_score(code, sample_id, feedback_collector)
          - preference_scores.append(pref)
    4. Compute median: median = compute_median_preference(preference_scores)
    5. Check collapse: is_collapsed = check_collapse(median)
    6. Return {median_preference: median, preference_scores: preference_scores, 
              num_samples: len(preference_scores), collapsed: is_collapsed}

compute_preference_score(generated_code, sample_id, feedback_collector):
    1. Collect human feedback: score = feedback_collector.collect_human_feedback(generated_code, sample_id)
    2. Return score  # [0,1]

compute_median_preference(preference_scores):
    1. Return np.median(preference_scores)

check_collapse(median_preference):
    1. Return median_preference < 0.1  # Collapsed to execution-only if True
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Preference scoring | Compute human preference on conflict cases |
| L-5-2 | Median computation | Compute median and check collapse threshold |

---

## C-6: Phase3 Metrics Module (Complexity: 11, Budget: 3)

**Applied**: Statistical Analysis, Gate Validation Logic

### API Signatures

```python
from typing import Tuple, Dict, List
import numpy as np
from scipy.stats import pearsonr


class Phase3Analyzer:
    def __init__(self, checkpoint_data: List[Dict], conflict_case_results: Dict):
        """Initialize analyzer with Phase 3 checkpoint data and conflict results."""
        ...
    
    def validate_human_weight_increase(self) -> Tuple[bool, Dict[str, float]]:
        """Validate human weight increases. Returns: (passed, {w_70, w_100, increase})"""
        ...
    
    def compute_conflict_case_preference(self) -> Tuple[float, Dict]:
        """Compute conflict case median preference. Returns: (median, {distribution, target_range})"""
        ...
    
    def compute_correctness_maintenance(self) -> Dict[str, float]:
        """Check correctness maintained. Returns: {ratio, pass_70, pass_100, threshold, maintained}"""
        ...
    
    def validate_gate_criteria(self) -> Dict[str, bool]:
        """Validate all 3 gates. Returns: {gate1, gate2, gate3, overall}"""
        ...
    
    def generate_report(self) -> str:
        """Generate gate validation report. Returns: formatted markdown string"""
        ...
```

### Pseudo-code

```
validate_human_weight_increase():
    1. Find 70% checkpoint: cp_70 = [cp for cp in data if abs(cp['progress'] - 0.70) < 0.01][0]
    2. Find 100% checkpoint: cp_100 = [cp for cp in data if abs(cp['progress'] - 1.00) < 0.01][0]
    3. Extract weights: w_70 = cp_70['weights']['human'], w_100 = cp_100['weights']['human']
    4. Check increase: passed = (w_100 > w_70)
    5. Return (passed, {w_70: w_70, w_100: w_100, increase: w_100 - w_70})

compute_conflict_case_preference():
    1. Extract preference scores: scores = conflict_case_results['preference_scores']
    2. Compute median: median = np.median(scores)
    3. Check target range: in_range = (0.1 <= median <= 0.4)
    4. Return (median, {distribution: scores, target_range: [0.1, 0.4], in_range: in_range})

compute_correctness_maintenance():
    1. Find checkpoints at 70% and 100%
    2. Extract pass@1 scores: pass_70 = cp_70['metrics']['pass@1'], pass_100 = cp_100['metrics']['pass@1']
    3. Compute ratio: ratio = pass_100 / pass_70
    4. Check threshold: maintained = (ratio >= 0.95)
    5. Return {ratio: ratio, pass_70: pass_70, pass_100: pass_100, threshold: 0.95, maintained: maintained}

validate_gate_criteria():
    1. Gate 1: Human weight increase
       a. passed_1, data_1 = validate_human_weight_increase()
    2. Gate 2: Conflict case preference
       a. median, data_2 = compute_conflict_case_preference()
       b. passed_2 = data_2['in_range']
    3. Gate 3: Correctness maintenance
       a. data_3 = compute_correctness_maintenance()
       b. passed_3 = data_3['maintained']
    4. Overall: overall = passed_1 and passed_2 and passed_3
    5. Return {gate1: passed_1, gate2: passed_2, gate3: passed_3, overall: overall}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Human weight validation | Verify w_human(100%) > w_human(70%) |
| L-6-2 | Conflict preference analysis | Compute median and check target range [0.1, 0.4] |
| L-6-3 | Correctness check | Verify pass@1 regression ≤ 5% |

---

## C-7: Gate Validator (Complexity: 8, Budget: 0)

**Note**: Core logic in C-6 (Phase3Analyzer). Wrapper class for report generation.

**Applied**: Gate Validation Pattern

### API Signatures

```python
class Phase3GateValidator:
    def __init__(
        self,
        weight_trajectory: List[Dict],
        conflict_results: Dict,
        pass1_trajectory: List[Dict]
    ):
        """Initialize gate validator with trajectories."""
        self.analyzer = Phase3Analyzer(weight_trajectory, conflict_results)
        ...
    
    def validate_gate1_human_increase(self) -> bool:
        """Validate Gate 1: Human weight increases. Returns: True/False"""
        ...
    
    def validate_gate2_conflict_non_collapse(self) -> bool:
        """Validate Gate 2: Conflict cases not collapsed. Returns: True/False"""
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

## External Dependencies API (Base Hypothesis h-m2)

### API Signatures (From Actual Code)

The following APIs are called from base hypothesis. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-m2/code/models/phase2_tri_modal_aggregator.py (ACTUAL CODE)
class Phase2TriModalAggregator(Phase1AnalysisTriModalAggregator):
    def __init__(
        self,
        config: dict = None,
        phase2_checkpoints: list = None,
        ai_peak_progress: float = 0.50
    ):
        """Extend h-m1 aggregator with Phase 2 AI peak scheduling."""
        ...
    
    def compute_dynamic_weights(self, training_progress: float) -> Dict[str, float]:
        """Compute Phase 2 weights with AI peak at ~50%. Returns: {execution, ai, human}"""
        ...
    
    def forward(
        self,
        execution_reward: Tensor,  # [B]
        ai_reward: Tensor,  # [B]
        human_reward: Tensor,  # [B]
        training_progress: float  # [0,1] - VERIFIED PARAMETER NAME
    ) -> Tensor:
        """Forward pass with Phase 2 AI peak scheduling. Returns: [B]"""
        ...
    
    def find_ai_weight_peak(self) -> Tuple[float, Dict[str, float]]:
        """Find AI weight peak location. Returns: (peak_progress, weights_at_peak)"""
        ...
    
    def log_phase2_checkpoint(self, progress: float, weights: Dict[str, float]):
        """Log checkpoint data for Phase 2 analysis."""
        ...


# From: docs/youra_research/h-m2/code/train/phase2_ppo_trainer.py (ACTUAL CODE)
class Phase2PPOTrainer(Phase1PPOTrainer):
    def __init__(
        self,
        model,
        aggregator,
        feedback_collector,
        config: dict,
        start_episode: int = 3000  # VERIFIED DEFAULT VALUE
    ):
        """Initialize Phase 2 PPO trainer."""
        ...
    
    def compute_training_progress(self, current_episode: int) -> float:
        """Compute training progress for Phase 2. Returns: [0,1]"""
        ...
    
    def train(
        self,
        dataloader: DataLoader,
        num_episodes: int = 4000
    ) -> Dict:
        """Train Phase 2 (30% → 70% progress). Returns: results dict"""
        ...
    
    def evaluate_checkpoint(self, dataloader: DataLoader) -> Dict:
        """Evaluate model at checkpoint. Returns: {pass@1, quality, samples}"""
        ...
    
    def save_checkpoint(self, path: str, progress: float, metrics: Dict):
        """Save model checkpoint."""
        ...


# From: docs/youra_research/h-m2/code/models/feedback_collectors.py (ACTUAL CODE)
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


# From: docs/youra_research/h-m2/code/data/dataset.py (inherited from h-m1)
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


# From: docs/youra_research/h-m2/code/utils/checkpoint_logger.py (inherited from h-m1)
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
```

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation, NOT spec!)

**Critical Parameter Names**:
- `training_progress` (float [0,1]) in aggregator.forward()
- `test_cases` (str) in feedback collectors
- `start_episode` (int) in Phase2PPOTrainer (default 3000)
- `num_episodes` (int) in trainer.train() (default 4000)
- All return types verified from actual code

---

## Integration Points

### Data Flow

```
1. Load h-m2 checkpoint at 70% progress
2. Initialize Phase3TriModalAggregator with human peak scheduling
3. Initialize Phase3PPOTrainer with loaded checkpoint
4. Prepare conflict case dataset (50 samples filtered from h-m1 baseline)
5. Training loop (episodes 0→3,000 mapped to 70%→100%):
   - Compute training_progress = (episode + 7000) / 10000
   - At checkpoints [70%, 80%, 90%, 100%]:
     - Log weights via CheckpointLogger
     - Evaluate pass@1 and quality
     - Evaluate conflict cases (at 80%, 90%, 100%)
     - Save checkpoint
   - Standard PPO update with Phase 3 tri-modal reward
6. Post-training analysis:
   - Phase3Analyzer loads all checkpoint data
   - validate_human_weight_increase()
   - compute_conflict_case_preference()
   - compute_correctness_maintenance()
   - validate_gate_criteria()
7. Generate 4 required figures
8. Output gate validation report
```

### Checkpoint Structure (Phase 3)

```python
checkpoint = {
    'progress': 0.80,  # float [0.70, 1.00]
    'phase': 'Phase 3',
    'episode': 8000,
    'model_state_dict': {...},
    'optimizer_state_dict': {...},
    'aggregator_state_dict': {...},
    'metrics': {
        'loss': 0.38,
        'reward': 0.74,
        'execution_weight': 0.32,
        'ai_weight': 0.24,
        'human_weight': 0.55,  # Increasing toward 70% at 100%
        'pass_at_1': 0.65,
        'quality': 0.61,
        'conflict_median_preference': 0.23  # Target: [0.1, 0.4]
    }
}
```

---

## Budget Summary

| Task | Complexity | Allocated | Used |
|------|------------|-----------|------|
| C-2: Phase3 Aggregator | 10 | 3 | 3 |
| C-4: Phase3 PPO Trainer | 9 | 2 | 2 |
| C-5: Conflict Case Evaluator | 9 | 2 | 2 |
| C-6: Phase3 Metrics | 11 | 3 | 3 |
| C-7: Gate Validator | 8 | 0 | 0 |
| **Total** | **47** | **10** | **10** |

**Note**: C-7 logic embedded in C-6. C-1 (conflict case dataset), C-3 (checkpoint loader), C-8 (visualization), C-9 (integration) allocated to Config Agent.

---

## Implementation Notes

### Error Handling

**Checkpoint Loading**: Verify checkpoint metadata (progress=0.70, phase="Phase 2") before loading  
**Float Comparison**: Use tolerance `abs(progress - checkpoint) < 0.01` for milestone detection  
**Conflict Case Evaluation**: Handle missing samples gracefully, log warning if < 50 samples  
**Median Computation**: Handle edge cases (empty list, single sample)

### Configuration

```python
# Phase 3 checkpoints
phase3_checkpoints = [0.70, 0.80, 0.90, 1.00]

# Training config
learning_rate = 1e-5  # Consistent with h-m2
total_episodes = 10000  # Full training (70% already done)
batch_size = 64  # Same as h-m2
phase3_start_episode = 7000  # 70% of 10k

# Human peak configuration
human_peak_progress = 1.00  # End of training
target_human_weight = 0.70  # 70% weight at 100% progress

# Gate thresholds
conflict_preference_range = [0.1, 0.4]  # Non-collapsed range
correctness_threshold = 0.95  # Max 5% regression
```

### Dependencies

```python
# From h-m2
from models.phase2_tri_modal_aggregator import Phase2TriModalAggregator
from train.phase2_ppo_trainer import Phase2PPOTrainer
from models.feedback_collectors import FeedbackCollector
from utils.checkpoint_logger import CheckpointLogger
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
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m3/03_logic.md`
