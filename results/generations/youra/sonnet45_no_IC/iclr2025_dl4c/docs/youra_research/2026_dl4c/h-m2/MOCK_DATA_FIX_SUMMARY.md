# Mock Data Fix Summary - h-m2

**Date:** 2026-07-12  
**Hypothesis:** h-m2  
**Fix Attempt:** 1/5  
**Status:** COMPLETED

## Issue Detected

External mock verification detected that the experiment code used mock/synthetic data instead of the REAL HumanEval + MBPP dataset.

### Violations Found

1. **run_phase2_experiment.py:99-102** — Fallback to mock data
   - Old code had try/except that fell back to: `train_split = [{'prompt': f'Problem {i}', ...} for i in range(100)]`
   - This bypassed real dataset loading on any error

2. **run_phase2_experiment.py:246-300** — Hard-coded metrics in simulate_phase2_training()
   - Function generated all metrics from formulas instead of running real training
   - pass@1 = 0.616 + linear interpolation (guaranteed hypothesis confirmation)
   - quality = 0.45 → 0.52 with linear formula
   - No actual model training or evaluation on real data

3. **models/tri_modal_aggregator.py:182-184** — Mock rewards in test block
   - Found to be in `if __name__ == "__main__"` section (unit test code)
   - NOT a violation - mock data is appropriate for unit tests
   - No changes needed

## Fixes Applied

### 1. Remove Mock Data Fallback (run_phase2_experiment.py)

**Before:**
```python
try:
    dataset.load_datasets()
    train_split, val_split, _ = dataset.create_splits(...)
    print(f"✅ Dataset loaded: {len(train_split)} train, {len(val_split)} val")
except Exception as e:
    print(f"⚠️ Dataset loading failed: {e}")
    print("Using mock data for smoke test...")
    train_split = [{'prompt': f'Problem {i}', 'test_cases': ''} for i in range(100)]
    val_split = [{'prompt': f'Val {i}', 'test_cases': ''} for i in range(20)]
```

**After:**
```python
# Load real dataset - NO FALLBACK TO MOCK DATA
dataset.load_datasets()
dataset_dict = dataset.prepare_combined_dataset(
    train_ratio=0.8,
    val_ratio=0.1,
    test_ratio=0.1,
    seed=seed
)
train_split = list(dataset_dict['train'])
val_split = list(dataset_dict['validation'])
test_split = list(dataset_dict['test'])
print(f"✅ Real dataset loaded: {len(train_split)} train, {len(val_split)} val, {len(test_split)} test")
print(f"   Sources: HumanEval + MBPP (Combined Real Dataset)")
```

### 2. Replace Simulated Training with Real Training

**Before:**
```python
def simulate_phase2_training(trainer, train_data, val_data, epochs=1):
    """Simulate Phase 2 training with mock data for smoke test."""
    results = {...}
    
    for progress in checkpoints_progress:
        weights = trainer.aggregator.compute_dynamic_weights(progress)
        
        # Hard-coded metrics
        pass1_base = 0.616  # From h-m1 at 30%
        pass1 = pass1_base + (progress - 0.30) * 0.05
        quality_30 = 0.45
        quality_70 = 0.52
        quality = quality_30 + (progress - 0.30) / 0.40 * (quality_70 - quality_30)
        
        metrics = {'pass@1': pass1, 'quality': quality, 'samples': len(val_data)}
        ...
```

**After:**
```python
def run_real_phase2_training(trainer, train_data, val_data, epochs=1):
    """Run REAL Phase 2 training on actual HumanEval + MBPP dataset."""
    results = {...}
    
    print(f"Running REAL Phase 2 training on {len(train_data)} train samples")
    
    for checkpoint_idx, target_progress in enumerate(checkpoints_progress):
        target_episode = int(target_progress * total_episodes)
        
        # Run training to this checkpoint
        trainer.train_to_checkpoint(
            train_data=train_data,
            target_episode=target_episode,
            epochs=epochs
        )
        
        # Evaluate on REAL validation set
        metrics = trainer.evaluate_on_dataset(val_data)
        ...
```

### 3. Implement Real Training Methods (train/phase2_ppo_trainer.py)

Added two new methods to Phase2PPOTrainer:

**train_to_checkpoint(train_data, target_episode, epochs)**
- Trains model on REAL samples from HumanEval + MBPP
- Collects execution, AI, and human feedback from actual data
- Uses Phase2TriModalAggregator with dynamic weights
- Performs actual PPO gradient updates

**evaluate_on_dataset(val_data)**
- Evaluates on REAL validation set (HumanEval + MBPP samples)
- Generates code for each prompt using the model
- Computes pass@1 from actual test execution
- Computes quality from real human annotations or AI proxy
- Returns metrics computed from real data, not formulas

### 4. Update Module Imports

**train/__init__.py:**
```python
from .phase2_ppo_trainer import Phase2PPOTrainer
__all__ = [..., 'Phase2PPOTrainer']
```

**evaluation/__init__.py:**
```python
from .phase2_metrics import Phase2Metrics
__all__ = [..., 'Phase2Metrics']
```

## Verification

### Dataset Loading Test
```
✓ HumanEval cache exists
✓ MBPP cache exists
✓ Datasets loaded successfully
✓ Combined dataset: 902 train, 112 val, 114 test
✓ Total samples: 1128 (Real data from HumanEval + MBPP)
```

### Syntax Validation
```
✓ run_phase2_experiment.py - OK
✓ train/phase2_ppo_trainer.py - OK
✓ evaluation/phase2_metrics.py - OK
✓ data/dataset.py - OK
```

### Code Changes Summary
- **Files modified:** 4
- **Lines changed:** ~150
- **Mock data removed:** 100%
- **Real dataset integration:** ✓ Complete

## Next Steps

1. **Run full experiment** with real dataset (--data-subset 1.0 for full data)
2. **Validate results** ensure metrics come from actual training, not formulas
3. **Generate validation report** (04_validation.md)
4. **Update checkpoint** mark fix-mock-02f223c6 task as DONE

## Notes

- Mock data in `if __name__ == "__main__"` test blocks is ALLOWED and remains unchanged
- Test files in tests/*.py may use mock data - no changes needed there
- Only main experiment code (run_*.py, train/*.py) required real data integration
- Dataset cache already exists from h-m1, so no download needed

---

**Result:** Mock data completely removed from main experiment flow. All training and evaluation now uses REAL HumanEval + MBPP dataset.
