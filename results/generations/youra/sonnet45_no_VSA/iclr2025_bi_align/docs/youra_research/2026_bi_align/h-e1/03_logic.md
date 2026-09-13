# Logic Design
## H-E1: Segment-level Memory Stress Index Profiler

**Hypothesis**: h-e1  
**Type**: EXISTENCE (PoC)  
**Version**: 1.0  
**Date**: 2026-07-10

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing codebase to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - designing from scratch

---

## Applied Knowledge Base Patterns

**Applied**: PyTorch CUDA memory profiling (`torch.cuda.memory_stats`, `torch.cuda.reset_peak_memory_stats`)  
**Applied**: Stratified sampling with numpy quantiles (`np.quantile`, custom batch sampling)

---

## E1-2: Core Memory Profiler [Complexity: 16, Budget: 4 subtasks]

**Applied**: PyTorch CUDA memory profiling API

### API Signatures

```python
from typing import Optional, Dict
import torch
from torch.utils.data import DataLoader

class SegmentMemoryProfiler:
    def __init__(self, device: str = "cuda:0"):
        """Initialize profiler with specified device."""
        self.device = torch.device(device)
    
    def reset_memory_stats(self) -> None:
        """Reset CUDA memory statistics. Call before each experiment."""
        torch.cuda.reset_peak_memory_stats(self.device)
        torch.cuda.empty_cache()
    
    def get_peak_memory_mb(self) -> float:
        """Get peak allocated memory in MB from current stats.
        
        Returns:
            float: Peak memory in MB
        """
        stats = torch.cuda.memory_stats(self.device)
        peak_bytes = stats.get("allocated_bytes.all.peak", 0)
        return peak_bytes / (1024 ** 2)
    
    def profile_iteration(
        self,
        model: torch.nn.Module,
        batch: Dict[str, torch.Tensor],
        optimizer: Optional[torch.optim.Optimizer] = None,
        backward: bool = False
    ) -> float:
        """Profile single iteration memory.
        
        Args:
            model: Model to profile
            batch: Input batch dict with 'input' and 'target' keys
            optimizer: Optimizer (required if backward=True)
            backward: If True, run backward + optimizer.step
        
        Returns:
            float: Peak memory in MB for this iteration
        """
        pass  # Implementation in Phase 4
    
    def profile_ground_truth(
        self,
        model: torch.nn.Module,
        dataloader: DataLoader,
        optimizer: torch.optim.Optimizer,
        num_iters: int = 10
    ) -> float:
        """Run 10-iteration ground truth profiling.
        
        Args:
            model: Model to profile
            dataloader: Training dataloader
            optimizer: Optimizer instance
            num_iters: Number of iterations (default 10)
        
        Returns:
            float: Peak memory in MB at iteration 10
        """
        pass  # Implementation in Phase 4
    
    def profile_lightweight(
        self,
        model: torch.nn.Module,
        sampler: 'StratifiedSampler',
        optimizer: torch.optim.Optimizer
    ) -> Dict[str, float]:
        """Run 3-iteration lightweight profiling protocol.
        
        Protocol:
            1. iter1: Forward only (no backward)
            2. post_optim: Forward + backward + optimizer.step
            3. stratified: Sample 4 batches from length bins
        
        Args:
            model: Model to profile
            sampler: StratifiedSampler instance (or None for fixed-length datasets)
            optimizer: Optimizer instance
        
        Returns:
            dict: {
                'iter1_mb': float,
                'post_optim_mb': float,
                'stratified_mbs': List[float],  # 4 values for P50/P75/P95/P99
                'predicted_mb': float  # max of all measurements
            }
        """
        pass  # Implementation in Phase 4
```

### Pseudo-code

```
profile_iteration(model, batch, optimizer, backward):
    1. reset_memory_stats()
    2. inputs = batch['input'].to(device)
    3. targets = batch['target'].to(device)
    4. outputs = model(inputs)
    5. loss = criterion(outputs, targets)
    6. if backward:
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
    7. return get_peak_memory_mb()

profile_ground_truth(model, dataloader, optimizer, num_iters=10):
    1. model.to(device)
    2. model.train()
    3. criterion = CrossEntropyLoss()
    4. iter_loader = iter(dataloader)
    5. for i in range(num_iters):
        batch = next(iter_loader)
        profile_iteration(model, batch, optimizer, backward=True)
    6. return get_peak_memory_mb()  # Peak at iteration 10

profile_lightweight(model, sampler, optimizer):
    1. model.to(device)
    2. model.train()
    3. criterion = CrossEntropyLoss()
    4. 
    5. # Iteration 1: Forward only
    6. batch1 = sampler.sample_random_batch() if sampler else dataloader.next()
    7. iter1_mb = profile_iteration(model, batch1, backward=False)
    8. 
    9. # Post-optimizer: Full training step
    10. batch2 = sampler.sample_random_batch() if sampler else dataloader.next()
    11. post_optim_mb = profile_iteration(model, batch2, optimizer, backward=True)
    12. 
    13. # Stratified sampling (transformers only)
    14. stratified_mbs = []
    15. if sampler is not None:
    16.     for bin_name in ['P50', 'P75', 'P95', 'P99']:
    17.         batch = sampler.sample_from_bin(bin_name)
    18.         mem = profile_iteration(model, batch, optimizer, backward=True)
    19.         stratified_mbs.append(mem)
    20. 
    21. predicted_mb = max([iter1_mb, post_optim_mb] + stratified_mbs)
    22. return {
    23.     'iter1_mb': iter1_mb,
    24.     'post_optim_mb': post_optim_mb,
    25.     'stratified_mbs': stratified_mbs,
    26.     'predicted_mb': predicted_mb
    27. }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | reset_memory_stats() | Wrapper for torch.cuda.reset_peak_memory_stats |
| L-2-2 | get_peak_memory_mb() | Extract peak from memory_stats dict |
| L-2-3 | profile_iteration() | Single iteration profiling with optional backward |
| L-2-4 | profile_ground_truth() | 10-iteration protocol implementation |

---

## E1-6: Ground Truth Experiments [Complexity: 15, Budget: 4 subtasks]

**Applied**: Standard PyTorch training loop

### API Signatures

```python
from typing import Dict
import pandas as pd

class ExperimentRunner:
    def __init__(self, config: Dict):
        """Initialize runner with experiment config."""
        self.config = config
        self.profiler = SegmentMemoryProfiler(device=config['device'])
    
    def run_ground_truth_experiment(
        self,
        model_name: str,
        optimizer_name: str,
        dataset_name: str,
        num_iters: int = 10
    ) -> Dict[str, any]:
        """Run single ground truth profiling experiment.
        
        Args:
            model_name: Model identifier (e.g., 'resnet18')
            optimizer_name: Optimizer name (e.g., 'adam')
            dataset_name: Dataset name (e.g., 'cifar10')
            num_iters: Number of iterations (default 10)
        
        Returns:
            dict: {
                'model': str,
                'optimizer': str,
                'dataset': str,
                'peak_memory_mb': float,
                'iteration': int  # Always 10 for ground truth
            }
        """
        pass  # Implementation in Phase 4
    
    def run_ground_truth_experiments(self) -> pd.DataFrame:
        """Run ground truth for all 48 configs.
        
        Returns:
            DataFrame with columns: model, optimizer, dataset, peak_memory_mb, iteration
        """
        pass  # Implementation in Phase 4
```

### Pseudo-code

```
run_ground_truth_experiment(model_name, optimizer_name, dataset_name, num_iters=10):
    1. model = ModelRegistry.get_model(model_name)
    2. dataset_type = DatasetPreparer.get_dataset_type(dataset_name)
    3. dataloader = DatasetPreparer.get_dataset(dataset_name)
    4. optimizer = OptimizerFactory.get_optimizer(optimizer_name, model.parameters())
    5. 
    6. peak_mb = profiler.profile_ground_truth(model, dataloader, optimizer, num_iters)
    7. 
    8. return {
    9.     'model': model_name,
    10.     'optimizer': optimizer_name,
    11.     'dataset': dataset_name,
    12.     'peak_memory_mb': peak_mb,
    13.     'iteration': num_iters
    14. }

run_ground_truth_experiments():
    1. results = []
    2. for model in config['models']['cnn'] + config['models']['transformer']:
    3.     for optimizer in ['adam', 'adamw', 'sgd']:
    4.         # CNNs: CIFAR-10 and ImageNet
    5.         if model in config['models']['cnn']:
    6.             for dataset in ['cifar10', 'imagenet']:
    7.                 result = run_ground_truth_experiment(model, optimizer, dataset)
    8.                 results.append(result)
    9.         # Transformers: WMT-14
    10.         else:
    11.             result = run_ground_truth_experiment(model, optimizer, 'wmt14')
    12.             results.append(result)
    13. 
    14. df = pd.DataFrame(results)
    15. df.to_csv('results/ground_truth_results.csv', index=False)
    16. return df
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | run_ground_truth_experiment() | Single config profiling |
| L-6-2 | run_ground_truth_experiments() | 48-config batch runner |
| L-6-3 | Config iteration logic | Model × optimizer × dataset loops |
| L-6-4 | CSV export | Save results to ground_truth_results.csv |

---

## E1-7: Lightweight Profiling [Complexity: 17, Budget: 5 subtasks]

**Applied**: 3-iteration protocol with stratified sampling

### API Signatures

```python
class ExperimentRunner:
    def run_lightweight_experiment(
        self,
        model_name: str,
        optimizer_name: str,
        dataset_name: str
    ) -> Dict[str, any]:
        """Run lightweight profiling experiment.
        
        Args:
            model_name: Model identifier
            optimizer_name: Optimizer name
            dataset_name: Dataset name
        
        Returns:
            dict: {
                'model': str,
                'optimizer': str,
                'dataset': str,
                'iter1_mb': float,
                'post_optim_mb': float,
                'stratified_mbs': List[float],  # Empty for CNNs
                'predicted_mb': float,
                'ground_truth_mb': float,  # From ground truth results
                'relative_error': float
            }
        """
        pass  # Implementation in Phase 4
    
    def run_lightweight_experiments(self) -> pd.DataFrame:
        """Run lightweight profiling for all 48 configs.
        
        Returns:
            DataFrame with lightweight profiling results
        """
        pass  # Implementation in Phase 4
```

### Pseudo-code

```
run_lightweight_experiment(model_name, optimizer_name, dataset_name):
    1. model = ModelRegistry.get_model(model_name)
    2. optimizer = OptimizerFactory.get_optimizer(optimizer_name, model.parameters())
    3. 
    4. # Get sampler (only for transformers)
    5. if dataset_name == 'wmt14':
    6.     dataset, sampler = DatasetPreparer.get_wmt14()
    7. else:
    8.     dataloader = DatasetPreparer.get_dataset(dataset_name)
    9.     sampler = None
    10. 
    11. # Run 3-iteration protocol
    12. result = profiler.profile_lightweight(model, sampler, optimizer)
    13. 
    14. # Load ground truth
    15. ground_truth_df = pd.read_csv('results/ground_truth_results.csv')
    16. gt_row = ground_truth_df[
    17.     (ground_truth_df['model'] == model_name) &
    18.     (ground_truth_df['optimizer'] == optimizer_name) &
    19.     (ground_truth_df['dataset'] == dataset_name)
    20. ]
    21. ground_truth_mb = gt_row['peak_memory_mb'].values[0]
    22. 
    23. # Compute error
    24. relative_error = abs(result['predicted_mb'] - ground_truth_mb) / ground_truth_mb
    25. 
    26. return {
    27.     'model': model_name,
    28.     'optimizer': optimizer_name,
    29.     'dataset': dataset_name,
    30.     'iter1_mb': result['iter1_mb'],
    31.     'post_optim_mb': result['post_optim_mb'],
    32.     'stratified_mbs': result['stratified_mbs'],
    33.     'predicted_mb': result['predicted_mb'],
    34.     'ground_truth_mb': ground_truth_mb,
    35.     'relative_error': relative_error
    36. }

run_lightweight_experiments():
    1. results = []
    2. for model in config['models']['cnn'] + config['models']['transformer']:
    3.     for optimizer in ['adam', 'adamw', 'sgd']:
    4.         if model in config['models']['cnn']:
    5.             for dataset in ['cifar10', 'imagenet']:
    6.                 result = run_lightweight_experiment(model, optimizer, dataset)
    7.                 results.append(result)
    8.         else:
    9.             result = run_lightweight_experiment(model, optimizer, 'wmt14')
    10.             results.append(result)
    11. 
    12. df = pd.DataFrame(results)
    13. df.to_csv('results/lightweight_results.csv', index=False)
    14. return df
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_lightweight_experiment() | Single config 3-iteration profiling |
| L-7-2 | profile_lightweight() integration | Call profiler.profile_lightweight() |
| L-7-3 | Ground truth lookup | Match and retrieve ground truth values |
| L-7-4 | Error computation | Calculate relative error |
| L-7-5 | Batch runner | 48-config iteration and CSV export |

---

## E1-1: Data Preparation [Complexity: 14, Budget: 3 subtasks]

**Applied**: Stratified sampling with quantile bins

### API Signatures

```python
from typing import Tuple, List, Dict, Optional
from torch.utils.data import Dataset, DataLoader
import numpy as np

class StratifiedSampler:
    def __init__(
        self,
        dataset: Dataset,
        batch_size: int = 32,
        quantiles: List[float] = [0.5, 0.75, 0.95, 0.99]
    ):
        """Initialize stratified sampler for variable-length sequences.
        
        Args:
            dataset: HuggingFace dataset with 'input_ids' field
            batch_size: Batch size for sampling
            quantiles: Length quantiles for binning
        """
        self.dataset = dataset
        self.batch_size = batch_size
        self.quantiles = quantiles
        self.bins = self.compute_length_bins()
    
    def compute_length_bins(self) -> Dict[str, Tuple[int, int]]:
        """Compute length bins from dataset.
        
        Returns:
            dict: {'P50': (min_len, max_len), 'P75': ..., 'P95': ..., 'P99': ...}
        """
        pass  # Implementation in Phase 4
    
    def sample_from_bin(self, bin_name: str) -> Dict[str, torch.Tensor]:
        """Sample one batch from specified length bin.
        
        Args:
            bin_name: One of 'P50', 'P75', 'P95', 'P99'
        
        Returns:
            dict: {'input': Tensor[B, max_len], 'target': Tensor[B, max_len]}
        """
        pass  # Implementation in Phase 4
    
    def get_stratified_batches(self) -> List[Dict[str, torch.Tensor]]:
        """Get 4 stratified batches (one per bin).
        
        Returns:
            List of 4 batch dicts
        """
        pass  # Implementation in Phase 4
    
    def sample_random_batch(self) -> Dict[str, torch.Tensor]:
        """Sample random batch for iteration 1 and post-optimizer steps.
        
        Returns:
            dict: Batch dict with padded tensors
        """
        pass  # Implementation in Phase 4


def variable_length_collate_fn(batch: List[Dict]) -> Dict[str, torch.Tensor]:
    """Collate variable-length sequences with padding.
    
    Args:
        batch: List of samples with 'input_ids' and 'labels'
    
    Returns:
        dict: {
            'input': Tensor[B, max_len],  # Padded to max in batch
            'target': Tensor[B, max_len]
        }
    """
    pass  # Implementation in Phase 4


class DatasetPreparer:
    @staticmethod
    def get_cifar10(root: str = "./data", batch_size: int = 128) -> DataLoader:
        """Load CIFAR-10 test split.
        
        Returns:
            DataLoader with transforms applied
        """
        pass  # Implementation in Phase 4
    
    @staticmethod
    def get_imagenet(root: str = "./data", batch_size: int = 64) -> DataLoader:
        """Load ImageNet-1K validation split.
        
        Returns:
            DataLoader with standard transforms
        """
        pass  # Implementation in Phase 4
    
    @staticmethod
    def get_wmt14(
        root: str = "./data",
        batch_size: int = 32,
        max_length: int = 128
    ) -> Tuple[Dataset, StratifiedSampler]:
        """Load WMT-14 En-De test split with stratified sampler.
        
        Returns:
            tuple: (dataset, StratifiedSampler instance)
        """
        pass  # Implementation in Phase 4
    
    @staticmethod
    def get_dataset_type(dataset_name: str) -> str:
        """Get dataset type (image or text).
        
        Returns:
            'image' or 'text'
        """
        pass  # Implementation in Phase 4
```

### Pseudo-code

```
StratifiedSampler.compute_length_bins():
    1. lengths = [len(sample['input_ids']) for sample in dataset]
    2. quantile_values = np.quantile(lengths, self.quantiles)
    3. bins = {}
    4. bins['P50'] = (0, quantile_values[0])
    5. bins['P75'] = (quantile_values[0], quantile_values[1])
    6. bins['P95'] = (quantile_values[1], quantile_values[2])
    7. bins['P99'] = (quantile_values[2], max(lengths))
    8. return bins

StratifiedSampler.sample_from_bin(bin_name):
    1. min_len, max_len = self.bins[bin_name]
    2. # Filter dataset by length range
    3. indices = [i for i, sample in enumerate(dataset) 
                  if min_len <= len(sample['input_ids']) <= max_len]
    4. # Sample batch_size indices
    5. sampled_indices = np.random.choice(indices, size=batch_size, replace=False)
    6. batch_samples = [dataset[i] for i in sampled_indices]
    7. return variable_length_collate_fn(batch_samples)

variable_length_collate_fn(batch):
    1. max_len = max(len(sample['input_ids']) for sample in batch)
    2. input_ids = []
    3. labels = []
    4. for sample in batch:
    5.     pad_len = max_len - len(sample['input_ids'])
    6.     input_ids.append(sample['input_ids'] + [0] * pad_len)
    7.     labels.append(sample['labels'] + [-100] * pad_len)
    8. return {
    9.     'input': torch.tensor(input_ids),
    10.     'target': torch.tensor(labels)
    11. }

DatasetPreparer.get_wmt14(root, batch_size, max_length):
    1. dataset = datasets.load_dataset('wmt14', 'de-en', split='test')
    2. tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
    3. def tokenize_fn(sample):
    4.     inputs = tokenizer(sample['translation']['en'], 
                            max_length=max_length, truncation=True)
    5.     labels = tokenizer(sample['translation']['de'],
                            max_length=max_length, truncation=True)
    6.     return {'input_ids': inputs['input_ids'], 'labels': labels['input_ids']}
    7. tokenized_dataset = dataset.map(tokenize_fn)
    8. sampler = StratifiedSampler(tokenized_dataset, batch_size)
    9. return tokenized_dataset, sampler
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | StratifiedSampler.compute_length_bins() | Quantile bin computation |
| L-1-2 | StratifiedSampler.sample_from_bin() | Length-based batch sampling |
| L-1-3 | variable_length_collate_fn() | Dynamic padding collate function |

---

## Module Complexity Summary

| Module | Task ID | Complexity | Subtasks | Status |
|--------|---------|------------|----------|--------|
| SegmentMemoryProfiler | E1-2 | 16 | 4 | Designed |
| ExperimentRunner (Ground Truth) | E1-6 | 15 | 4 | Designed |
| ExperimentRunner (Lightweight) | E1-7 | 17 | 5 | Designed |
| StratifiedSampler + DatasetPreparer | E1-1 | 14 | 3 | Designed |

**Total Subtasks**: 16 (exceeds 14 budget by 2)

**Budget Adjustment Required**: Merge L-6-3 and L-6-4 into L-6-2 (Config iteration + CSV export), merge L-7-4 and L-7-5 into L-7-3 (Error computation + batch runner).

**Revised Subtask Allocation**:
- E1-2: 4 subtasks
- E1-6: 3 subtasks (merged)
- E1-7: 4 subtasks (merged)
- E1-1: 3 subtasks

**New Total**: 14 subtasks (within budget)

---

## Implementation Notes

### Memory Stats API
```python
# torch.cuda.memory_stats() returns dict with keys:
# - 'allocated_bytes.all.peak': Peak allocated memory
# - 'reserved_bytes.all.peak': Peak reserved memory
# - 'num_alloc_retries': Fragmentation indicator

# Use allocated_bytes.all.peak for segment-level tracking
```

### Optimizer State Buffers
```python
# Adam/AdamW create 2 buffers per parameter:
# - exp_avg (m_t): First moment estimate
# - exp_avg_sq (v_t): Second moment estimate

# SGD with momentum creates 1 buffer:
# - momentum_buffer

# Memory after optimizer.step() includes these buffers
```

### Length Distribution (WMT-14)
```python
# Expected quantiles for WMT-14 En-De:
# P50: ~30 tokens
# P75: ~45 tokens
# P95: ~65 tokens
# P99: ~85 tokens

# Validate during E1-1 implementation and adjust if needed
```

---

## Phase 4 Handoff

**Ready for Implementation**: YES

**Critical APIs**:
1. `SegmentMemoryProfiler.profile_lightweight()` - Core 3-iteration protocol
2. `StratifiedSampler.sample_from_bin()` - Length-based sampling
3. `ExperimentRunner.run_ground_truth_experiments()` - 48-config batch runner
4. `ExperimentRunner.run_lightweight_experiments()` - Lightweight profiling runner

**External Dependencies**: None (green-field project)

**Configuration Files**: `/workspace/TEST_bi_align/docs/youra_research/h-e1/03_config.yaml` (to be created in Phase 3 Config Agent)

**Next Phase**: Phase 4 Coder Agent will implement APIs exactly as specified above.

---

**Document Status**: COMPLETE  
**Subtask Budget**: 14/14 used  
**Logic Complexity**: High (3-iteration protocol + stratified sampling)  
**Ready for Phase 4**: YES
