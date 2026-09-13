# Real Data Collection Instructions for H-M3

## Problem Statement

The Papers with Code API (https://paperswithcode.com/api/v1/) is currently unavailable (returns 302 redirect to HuggingFace).

However, **H-M3 requires REAL benchmark performance data** to compute coefficient of variation (CV) and test the hypothesis that artifact quality reduces performance variance.

## Required Data

For each benchmark, we need:
- **Benchmark name** (already have from H-M1)
- **Multiple performance results** (≥5 independent reproductions)
  - Metric: Accuracy or F1 score
  - From different papers/implementations
- **Artifact metadata**:
  - GitHub repository presence
  - Dataset card presence
  - Reproducibility badge

## Data Collection Options

### Option 1: Manual Collection from Papers with Code Website

1. Visit https://paperswithcode.com/sota
2. For each benchmark in H-M1 list:
   - Navigate to benchmark page
   - Copy all reported results (accuracy/F1 values)
   - Note artifact presence (GitHub links, badges)
   - Save to CSV format

**Time estimate:** ~2 hours for 100 benchmarks

### Option 2: Use Published Benchmark Studies

Several papers have already collected this data:

1. **Bouthillier et al. 2021** - "Accounting for Variance in ML Benchmarks"
   - Paper: https://arxiv.org/abs/2103.03098
   - Dataset: Variance measurements for ImageNet, CIFAR, etc.
   - Contact authors for raw data

2. **Dodge et al. 2019** - "Show Your Work: Improved Reporting of Experimental Results"
   - Paper: https://arxiv.org/abs/1909.03004
   - Dataset: Reproducibility study with multiple runs per benchmark

3. **Papers with Code Archive** (HuggingFace snapshot)
   - May exist as cached dataset on HuggingFace
   - Search for "paperswithcode" in datasets library

### Option 3: Use Standard Benchmark Leaderboards

For well-known benchmarks, use official leaderboards:

1. **ImageNet** - https://image-net.org/challenges/LSVRC/
2. **CIFAR-10/100** - https://paperswithcode.com/dataset/cifar-10
3. **GLUE** - https://gluebenchmark.com/leaderboard
4. **SuperGLUE** - https://super.gluebenchmark.com/leaderboard

Copy performance values from top papers (≥5 submissions per benchmark).

## Minimum Viable Dataset

To satisfy Phase 4 requirements, create a **minimal real dataset**:

- **20 benchmarks** minimum (10 high-artifact, 10 low-artifact)
- **≥5 real results per benchmark** from published papers
- **Document sources** for every datapoint

This is sufficient for proof-of-concept validation.

## Data Format

Save collected data as: `real_benchmark_data.csv`

```csv
benchmark_id,benchmark_name,paper_source,accuracy,f1,has_github,has_dataset_card,has_badge
imagenet,ImageNet,ResNet50 (He 2015),76.2,,1,1,0
imagenet,ImageNet,EfficientNet (Tan 2019),84.3,,1,1,1
imagenet,ImageNet,Vision Transformer (Dosovitskiy 2020),87.1,,1,1,1
...
```

## Implementation

Use `manual_data_loader.py` (provided) to load this real dataset:

```python
from data.manual_data_loader import load_real_benchmark_data

df = load_real_benchmark_data("real_benchmark_data.csv")
# Returns properly formatted DataFrame ready for H-M3 analysis
```

## Status

- ❌ Papers with Code API unavailable
- ⏳ Manual collection in progress
- ✅ Real data required (no mock fallback)
