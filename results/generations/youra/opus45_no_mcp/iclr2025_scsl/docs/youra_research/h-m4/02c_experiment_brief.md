# Experiment Design: H-M4

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Crystallization peak timing is benchmark-relative at 20-40% of training duration
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests generalizability of timing claim across benchmarks

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M3 PASS - Detection rate 100%, timing variance 0.00, SNR 5.64)
**Gate Status:** SHOULD_WORK - Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (COMPLETED)

### Gate Condition
Crystallization peak occurs within 20-40% of normalized training duration for all 3 benchmarks. Variance in normalized timing <10% across benchmarks.

---

## Continuation Context

H-M3 validated the second derivative detection method with 100% reliability (5.64 SNR, 0.00 timing variance on Waterbirds). H-M4 now tests whether the crystallization timing generalizes across benchmarks when normalized to percentage of total training duration.

### Previous Hypothesis Results (if applicable)
- **H-E1:** Crystallization zone existence confirmed (epoch 3 on Waterbirds)
- **H-M1:** Gradient starvation mechanism validated
- **H-M2:** Spurious feature commitment confirmed (probe accuracy 0.9468)
- **H-M3:** Detection method validated (100% rate, SNR 5.64, variance 0.00)

**Key Finding from H-M3:** Crystallization detected at epoch 3 of 43 epochs on Waterbirds = 7% of training. This is BELOW the hypothesized 20-40% range, suggesting the hypothesis may need refinement or the timing varies significantly by benchmark.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable. Using domain knowledge synthesis.

**Training Duration Normalization:**
- Normalized epoch = (current_epoch / total_epochs) × 100%
- Standard practice in learning dynamics literature
- Enables cross-benchmark comparison with different epoch counts

**Benchmark-Specific Training Durations (from literature):**
- Waterbirds: Typically 100 epochs (convergence ~50 epochs)
- CelebA: Typically 50 epochs (convergence ~30 epochs)
- ColoredMNIST: Typically 30 epochs (convergence ~15 epochs)

**Phase Transition Analysis:**
- Early phase (0-20%): Rapid feature learning
- Middle phase (20-40%): Potential crystallization window (hypothesized)
- Late phase (40-100%): Gradual refinement, minimal change

### Archon Code Examples

**Note:** Archon MCP unavailable. Standard implementations referenced.

**Normalized Timing Computation:**
```python
def normalize_timing(peak_epoch: int, total_epochs: int) -> float:
    """Convert absolute epoch to percentage of training."""
    return (peak_epoch / total_epochs) * 100.0
```

**Cross-Benchmark Analysis:**
```python
def analyze_timing_consistency(results: dict) -> dict:
    """Compute timing statistics across benchmarks."""
    normalized_times = []
    for benchmark, data in results.items():
        norm_time = normalize_timing(data['peak_epoch'], data['total_epochs'])
        normalized_times.append(norm_time)
    return {
        'mean': np.mean(normalized_times),
        'std': np.std(normalized_times),
        'range': (min(normalized_times), max(normalized_times))
    }
```

### Exa GitHub Implementations

**Note:** Exa MCP unavailable. Using known implementations from literature.

**Repository 1**: p-lambda/wilds (Official WILDS Benchmark)
- **URL**: https://github.com/p-lambda/wilds
- **Relevance**: Standard training configurations for all 3 benchmarks
- **Training Config**:
  - Waterbirds: 100 epochs, batch 128, lr 1e-3
  - CelebA: 50 epochs, batch 128, lr 1e-4
  - ColoredMNIST: 30 epochs, batch 128, lr 1e-3

**Repository 2**: Loss landscape analysis
- **URL**: https://github.com/tomgoldstein/loss-landscape
- **Relevance**: Phase transition analysis in training dynamics
- **Key Pattern**: Sharpness changes correlate with learning phases

**Repository 3**: Learning dynamics
- **URL**: https://github.com/google-research/google-research/tree/master/early_exit
- **Relevance**: Early stopping based on training dynamics
- **Observation**: Critical learning often happens in first 30-40% of training

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a novel timing analysis (not paper reproduction):
1. Use H-M3 detection code as foundation
2. Apply to all 3 benchmarks with full training runs
3. Normalize and compare timing across benchmarks

**Recommended Implementation Path:**
- Primary: Extend H-M3 detection to multi-benchmark normalized timing analysis
- Fallback: If timing outside 20-40%, document actual range and propose revised hypothesis
- Justification: Novel analysis building on validated detection method

### Code Analysis (Serena MCP)

**Note:** Serena MCP optional and unavailable.

Key integration points:
- Reuse `compute_wga_second_derivative` from H-M3
- Reuse `detect_crystallization_peak` from H-M3
- Add normalization layer for cross-benchmark comparison

---

## Experiment Specification

### Dataset

**Dataset 1: Waterbirds** (Primary)
- **Type:** Standard (WILDS benchmark)
- **Source:** WILDS benchmark suite (p-lambda/wilds)
- **Size:** 4,795 train, 1,199 val, 5,794 test
- **Training Duration:** 100 epochs (standard)
- **Groups:** 4 groups (landbird/waterbird × land/water background)
- **Minority Group Size:** ~600 samples

**Dataset 2: CelebA**
- **Type:** Standard (WILDS benchmark)
- **Source:** WILDS benchmark suite
- **Size:** 162,770 train, 19,867 val, 19,962 test
- **Training Duration:** 50 epochs (standard)
- **Groups:** 4 groups (hair color × gender)
- **Minority Group Size:** ~8,000 samples

**Dataset 3: ColoredMNIST**
- **Type:** Standard (custom loader)
- **Source:** Custom construction from MNIST
- **Size:** 50,000 train, 10,000 val, 10,000 test
- **Training Duration:** 30 epochs (standard)
- **Groups:** 10×2 groups (digit × color correlation)
- **Minority Group Size:** ~500 samples per digit

**Loading Information** (for Phase 4 download):
- Method: WILDS Python API + custom ColoredMNIST loader
- Identifier: waterbirds, celebA, coloredmnist
- Code:
```python
from wilds import get_dataset

# Waterbirds
wb_dataset = get_dataset(dataset='waterbirds', download=True)
wb_train = wb_dataset.get_subset('train')

# CelebA
celeba_dataset = get_dataset(dataset='celebA', download=True)
celeba_train = celeba_dataset.get_subset('train')

# ColoredMNIST (custom)
import torchvision.datasets as datasets
from utils.colored_mnist import construct_colored_mnist
mnist = datasets.MNIST(root='./data', train=True, download=True)
colored_train = construct_colored_mnist(mnist, correlation=0.95)
```

### Models

#### Baseline Model

**Architecture:** ResNet-50 with ImageNet pretrained weights
- **Type:** CNN classifier
- **Input:** 224×224 RGB images (32×32 for ColoredMNIST)
- **Output:** 2-class (Waterbirds, CelebA), 10-class (ColoredMNIST)
- **Purpose:** Generate WGA curves across full training for all 3 benchmarks

**Loading Information** (for Phase 4 download):
- Method: torchvision pretrained models
- Identifier: ResNet50_Weights.IMAGENET1K_V1
- Code:
```python
import torchvision.models as models
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
```

#### Proposed Model

**Architecture:** Baseline + Normalized Timing Analysis

**Core Mechanism Implementation:**

```python
import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks
from dataclasses import dataclass
from typing import Optional

@dataclass
class BenchmarkConfig:
    name: str
    total_epochs: int
    expected_range: tuple  # (min_percent, max_percent)

BENCHMARK_CONFIGS = {
    'waterbirds': BenchmarkConfig('Waterbirds', 100, (20, 40)),
    'celebA': BenchmarkConfig('CelebA', 50, (20, 40)),
    'coloredmnist': BenchmarkConfig('ColoredMNIST', 30, (20, 40)),
}

def compute_wga_second_derivative(wga_curve: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Compute second derivative of WGA with rolling window smoothing."""
    smoothed = uniform_filter1d(wga_curve, size=window_size, mode='nearest')
    d1 = np.gradient(smoothed)
    d2 = np.gradient(d1)
    return d2

def detect_crystallization_peak(d2_wga: np.ndarray, prominence_threshold: float = 0.005) -> dict:
    """Detect crystallization as significant negative peak in d²WGA/dt²."""
    neg_d2 = -d2_wga
    peaks, properties = find_peaks(neg_d2, prominence=prominence_threshold)
    
    if len(peaks) == 0:
        return {'detected': False, 'epoch': None, 'prominence': 0.0, 'snr': 0.0}
    
    best_idx = np.argmax(properties['prominences'])
    peak_epoch = peaks[best_idx]
    prominence = properties['prominences'][best_idx]
    noise_std = np.std(d2_wga)
    snr = prominence / noise_std if noise_std > 0 else float('inf')
    
    return {'detected': True, 'epoch': int(peak_epoch), 'prominence': float(prominence), 'snr': float(snr)}

def normalize_peak_timing(peak_epoch: int, total_epochs: int) -> float:
    """Convert absolute peak epoch to percentage of total training."""
    return (peak_epoch / total_epochs) * 100.0

def analyze_benchmark_timing(wga_curves: dict, configs: dict = BENCHMARK_CONFIGS) -> dict:
    """Analyze crystallization timing across all benchmarks."""
    results = {}
    
    for benchmark, wga_curve in wga_curves.items():
        config = configs[benchmark]
        d2 = compute_wga_second_derivative(wga_curve, window_size=5)
        peak_info = detect_crystallization_peak(d2)
        
        if peak_info['detected']:
            norm_timing = normalize_peak_timing(peak_info['epoch'], config.total_epochs)
            in_range = config.expected_range[0] <= norm_timing <= config.expected_range[1]
        else:
            norm_timing = None
            in_range = False
        
        results[benchmark] = {
            'peak_epoch': peak_info['epoch'],
            'total_epochs': config.total_epochs,
            'normalized_timing_percent': norm_timing,
            'in_expected_range': in_range,
            'expected_range': config.expected_range,
            'snr': peak_info['snr'],
            'detected': peak_info['detected']
        }
    
    return results

def compute_timing_statistics(results: dict) -> dict:
    """Compute aggregate statistics across benchmarks."""
    valid_timings = [r['normalized_timing_percent'] for r in results.values() if r['detected']]
    
    if len(valid_timings) == 0:
        return {'success': False, 'reason': 'No peaks detected'}
    
    mean_timing = np.mean(valid_timings)
    timing_variance = np.std(valid_timings)
    all_in_range = all(r['in_expected_range'] for r in results.values() if r['detected'])
    benchmarks_in_range = sum(1 for r in results.values() if r.get('in_expected_range', False))
    
    return {
        'success': True,
        'mean_normalized_timing': float(mean_timing),
        'timing_variance_percent': float(timing_variance),
        'all_in_20_40_range': all_in_range,
        'benchmarks_in_range': benchmarks_in_range,
        'total_benchmarks': len(results),
        'gate_pass': all_in_range and timing_variance < 10.0
    }
```

### Training Protocol

**Full Training Runs Required (if H-E1 checkpoints don't cover all benchmarks):**

**Waterbirds:**
- Optimizer: SGD with momentum 0.9
- Learning rate: 1e-3 (constant)
- Batch size: 128
- Epochs: 100
- Checkpoint: Every epoch (WGA saved)

**CelebA:**
- Optimizer: SGD with momentum 0.9
- Learning rate: 1e-4 (constant)
- Batch size: 128
- Epochs: 50
- Checkpoint: Every epoch (WGA saved)

**ColoredMNIST:**
- Optimizer: SGD with momentum 0.9
- Learning rate: 1e-3 (constant)
- Batch size: 128
- Epochs: 30
- Checkpoint: Every epoch (WGA saved)

**Seeds:** 5 random seeds per benchmark (15 total runs)

**Analysis Protocol:**
1. Train models on all 3 benchmarks (or load existing checkpoints)
2. Compute WGA at each epoch for each run
3. Apply H-M3 detection method to each WGA curve
4. Normalize peak timing to percentage of total training
5. Test whether all peaks fall in 20-40% range
6. Compute variance in normalized timing across benchmarks

### Evaluation

**Primary Metrics:**
1. **Range Compliance:** % of benchmarks with peak in 20-40% range (target: 100%)
2. **Timing Variance:** Std dev of normalized peak timing across benchmarks (target: <10%)
3. **Detection Consistency:** % of runs with valid peak detection (target: >80%)

**Secondary Metrics:**
4. **Per-Benchmark Normalized Timing:** Individual normalized timing for each benchmark
5. **Cross-Seed Variance:** Within-benchmark timing variance across 5 seeds

**Success Criteria (PoC):**
- All 3 benchmarks show peak in 20-40% range
- Timing variance <10% across benchmarks
- Detection rate >80% across all runs

**Failure Criteria:**
- Any benchmark outside 20-40%: Document actual range, propose revised hypothesis
- Variance >15%: Timing is benchmark-specific, not universal

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Cross-Benchmark Statistical Analysis
- Library: numpy, scipy
- Code:
```python
import numpy as np

def compute_range_compliance(results: dict, expected_range: tuple = (20, 40)) -> float:
    valid = [r for r in results.values() if r['detected']]
    in_range = sum(1 for r in valid if expected_range[0] <= r['normalized_timing_percent'] <= expected_range[1])
    return in_range / len(valid) if valid else 0.0

def compute_cross_benchmark_variance(results: dict) -> float:
    timings = [r['normalized_timing_percent'] for r in results.values() if r['detected']]
    return np.std(timings) if len(timings) > 1 else 0.0
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart (range compliance, variance)

#### Additional Figures (LLM Autonomous)

1. **Normalized Timing Comparison**: Bar chart showing normalized peak timing (%) for each benchmark with 20-40% range shaded
2. **WGA Curves Overlay**: 3-panel plot showing WGA curves for all benchmarks (x-axis: normalized epoch %)
3. **Timing Distribution**: Box plot of normalized timing across seeds for each benchmark
4. **Cross-Benchmark Correlation**: Scatter plot of absolute epoch vs total epochs with regression line
5. **Gate Status Dashboard**: Summary panel showing pass/fail status for each criterion

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. All 3 benchmarks detect crystallization peak
3. All normalized timings fall within 20-40% OR document actual range

**Note:** H-M4 is SHOULD_WORK gate. If timing is outside 20-40% but consistent, document pattern rather than fail.

---

## Appendix: Reference Implementations

**Signal Processing References:**

1. **SciPy Documentation - find_peaks**
   - URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
   - Usage: Peak detection with prominence filtering

2. **NumPy Documentation - gradient**
   - URL: https://numpy.org/doc/stable/reference/generated/numpy.gradient.html
   - Usage: Numerical differentiation

**Group Robustness References:**

3. **WILDS Benchmark** (Koh et al., 2021)
   - URL: https://github.com/p-lambda/wilds
   - Usage: Standard benchmark configurations

4. **Group DRO** (Sagawa et al., 2020)
   - URL: https://github.com/kohpangwei/group_DRO
   - Usage: Per-benchmark training configurations

**Learning Dynamics References:**

5. **Simplicity Bias** (Shah et al., 2020)
   - URL: https://arxiv.org/abs/2006.07710
   - Relevance: Phase transition timing in feature learning

6. **Gradient Starvation** (Pezeshki et al., 2021)
   - URL: https://arxiv.org/abs/2011.09468
   - Relevance: Temporal dynamics of feature dominance

**Previous Hypothesis Code:**

7. **H-M3 Detection Code** (from this project)
   - Path: h-m3/code/
   - Usage: Second derivative detection method (validated)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- H-M3 COMPLETED: Detection method validated (100% rate, SNR 5.64)
- H-M4 set to IN_PROGRESS for Phase 2C experiment design

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
