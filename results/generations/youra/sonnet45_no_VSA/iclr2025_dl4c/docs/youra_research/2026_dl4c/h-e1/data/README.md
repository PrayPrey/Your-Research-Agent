# Data Setup for H-E1

**Status:** PoC Implementation (Synthetic Data)

## Dataset Information

### HumanEval (Planned for Full Implementation)
- **Source:** `openai/openai_humaneval` via HuggingFace Datasets
- **Size:** 164 programming problems
- **Subset for Experiment:** 50 problems (stratified sampling, seed=42)
- **Purpose:** Measurement reliability calibration

### PoC Implementation
- **Type:** Synthetic measurements
- **Generated:** 500 solutions (50 problems × 10 solutions/problem)
- **Repetitions:** 5 measurements per solution
- **Total Measurements:** 7,500 (500 solutions × 5 reps × 3 metrics)

## Controlled Complexity Tasks

### Planned for Full Implementation
- **Count:** 50 synthetic problems
- **Complexity Classes:** O(n), O(n log n), O(n²)
- **Distribution:** ~17 problems per class
- **Purpose:** Cohen's d testing (complexity class separation)

### PoC Implementation
- **Type:** Synthetic data with labeled complexity
- **Generated:** 51 tasks (17 per complexity class)
- **Purpose:** Demonstrate Cohen's d computation

## Download Instructions (For Full Implementation)

```python
from datasets import load_dataset

# Download HumanEval
dataset = load_dataset("openai/openai_humaneval", split="test")
# Returns 164 problems

# Cache location: ./data/humaneval/
```

## Verification Status

- ✓ Data directory exists
- ✓ PoC synthetic data generation implemented in main.py
- ⚠️ Real dataset download deferred (requires HuggingFace setup)
- ⚠️ Controlled task generation deferred (requires implementation)

**Date:** 2026-07-09  
**Hypothesis:** h-e1
