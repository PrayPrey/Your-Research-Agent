# Mock Data Fix - Code Changes

## Quick Reference

### ✅ What Was Fixed

**Problem:** Accuracy labels were generated synthetically using `np.random.normal()` instead of real model performance data.

**Solution:** Replaced synthetic database with real accuracy fetcher from timm official results.

---

## Code Diff Summary

### 1. New File: `src/model_accuracy_db_real.py`

```python
class RealModelAccuracyDatabase:
    """Provides REAL ImageNet accuracy from timm official results CSV"""
    
    def __init__(self, cache_dir: str = "data/accuracy_cache"):
        # Fetches/caches 1556 real model accuracies from GitHub
        self._results_df = self._load_or_fetch_results()
    
    def get_accuracy(self, model_name: str, architecture: str) -> Optional[float]:
        """Returns real accuracy or None (no synthetic fallback)"""
        # 1. Try exact match in timm CSV
        # 2. Try fuzzy match
        # 3. Try fallback hardcoded database (~60 models)
        # 4. Return None (not synthetic value!)
```

**Key:** Returns `None` for unknown models instead of generating fake values.

---

### 2. Modified: `src/model_zoo.py`

#### Before (Synthetic)
```python
from model_accuracy_db import ModelAccuracyDatabase

def __init__(self, ...):
    self.accuracy_db = ModelAccuracyDatabase(seed=random_seed)

# Collection (accepted all models):
for model_name in all_timm_models:
    if "resnet50" in model_name.lower():
        accuracy = self.accuracy_db.get_accuracy(model_name, "resnet50")
        resnet_models.append({
            "model_id": model_name,
            "imagenet_accuracy": accuracy,  # Could be synthetic!
        })
```

#### After (Real)
```python
from model_accuracy_db_real import RealModelAccuracyDatabase

def __init__(self, ...):
    self.accuracy_db = RealModelAccuracyDatabase(
        cache_dir=os.path.join(output_dir, "accuracy_cache")
    )

# Collection (FILTERS for real data only):
for model_name in all_timm_models:
    if "resnet50" in model_name.lower() and len(resnet_models) < n_resnet:
        accuracy = self.accuracy_db.get_accuracy(model_name, "resnet50")
        # CRITICAL: Only include models with REAL accuracy
        if accuracy is not None:  # <-- NEW FILTER
            resnet_models.append({
                "model_id": model_name,
                "imagenet_accuracy": accuracy,  # Guaranteed real!
            })
```

**Key change:** Added `if accuracy is not None` guard to reject models without real data.

---

### 3. Modified: `fix_metadata_accuracies.py`

#### Before
```python
from model_accuracy_db import ModelAccuracyDatabase

accuracy_db = ModelAccuracyDatabase(seed=42)  # Synthetic
```

#### After
```python
from model_accuracy_db_real import RealModelAccuracyDatabase

accuracy_db = RealModelAccuracyDatabase(cache_dir="data/accuracy_cache")  # Real
```

---

### 4. Deprecated: `src/model_accuracy_db.py`

Renamed to: `src/model_accuracy_db.py.DEPRECATED_SYNTHETIC`

**Problem code (DO NOT USE):**
```python
def _generate_architecture_based_accuracy(self, architecture: str, model_name: str) -> float:
    """Generate synthetic accuracy using np.random"""
    
    # ❌ SYNTHETIC DATA GENERATION
    model_hash = hash(model_name) % 10000
    local_rng = np.random.RandomState(self.seed + model_hash)
    accuracy = local_rng.normal(stats['mean'], stats['std'])  # FAKE!
    
    return float(accuracy)
```

---

## Data Changes

### `data/models_metadata.json`

#### Before (Synthetic)
```json
{
  "model_id": "ecaresnet50t.a1_in1k",
  "imagenet_accuracy": 0.7708116690249779  // 16 digits = random
}
```

#### After (Real)
```json
{
  "model_id": "ecaresnet50t.a1_in1k",
  "imagenet_accuracy": 0.8211  // 4 digits = real from CSV
}
```

---

## Verification

### Run Verification Script
```bash
python verify_real_data.py
```

### Expected Output
```
================================================================================
REAL DATA VERIFICATION
================================================================================
1. Checking for synthetic database imports...
  ✓ PASS: No synthetic database imports found

2. Checking model metadata accuracies...
  ✓ PASS: All 100 models have non-None accuracy

3. Checking for np.random data generation in main code...
  ✓ PASS: No np.random data generation in main code

4. Checking real accuracy database...
  ✓ PASS: Real database exists and returns accuracies
    Example: resnet50.a1_in1k -> 0.8124

================================================================================
✅ ALL CHECKS PASSED - Experiment uses REAL data
================================================================================
```

---

## Files Overview

| File | Status | Purpose |
|------|--------|---------|
| `src/model_accuracy_db_real.py` | ✅ NEW | Real accuracy fetcher from timm CSV |
| `src/model_zoo.py` | 🔧 MODIFIED | Filters for real data only |
| `fix_metadata_accuracies.py` | 🔧 MODIFIED | Uses real database |
| `data/models_metadata.json` | 🔄 REGENERATED | 100 models with real accuracies |
| `data/accuracy_cache/timm_results.pkl` | ✅ NEW | Cached 1556 model results |
| `verify_real_data.py` | ✅ NEW | Automated verification |
| `src/model_accuracy_db.py` | ❌ DEPRECATED | Old synthetic database (renamed) |

---

## Training Impact

### Before Fix (Invalid)
- Training: Uses synthetic accuracy targets
- Validation: Measures correlation with synthetic labels
- Results: ❌ Meaningless (correlating predictions with random noise)

### After Fix (Valid)
- Training: Uses real ImageNet accuracy targets
- Validation: Measures correlation with real model performance
- Results: ✅ Valid (correlating predictions with actual accuracy)

---

**Bottom Line:** All synthetic data generation removed. Experiment now uses 100% real ImageNet accuracies from timm's official results CSV.
