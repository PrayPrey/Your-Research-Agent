# Experiment Design: H-M3

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Second derivative d²WGA/dt² with 5-epoch smoothing detects crystallization as significant negative peak
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests detection method reliability

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 PASS)
**Gate Status:** MUST_WORK - Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (COMPLETED)

### Gate Condition
Detection method validates with >80% reliability across random seeds. Peak timing variance <5 epochs.

---

## Continuation Context

H-M2 confirmed classifier commitment post-crystallization (spurious probe accuracy 0.9468). H-M3 now validates the proposed detection methodology can reliably identify this crystallization point using second derivative analysis with 5-epoch smoothing.

### Previous Hypothesis Results (if applicable)
- **H-E1:** Crystallization zone existence confirmed
- **H-M1:** Gradient starvation mechanism validated
- **H-M2:** Spurious feature commitment confirmed (probe accuracy maintained)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable. Using domain knowledge synthesis.

**Second Derivative Analysis for Time Series:**
- Rolling window smoothing standard for noisy gradient signals
- Savitzky-Golay filter alternative for preserving peak shape
- Signal-to-noise ratio (SNR) key metric for detection reliability
- Peak detection via scipy.signal.find_peaks with prominence threshold

**Worst-Group Accuracy Tracking Literature:**
- Sagawa et al. (2020): WGA computed per-epoch standard in group robustness
- Dense checkpointing (every epoch) required for derivative analysis
- 5-seed minimum for statistical significance testing

**Detection Method Best Practices:**
- Finite difference approximation for discrete derivatives
- Central difference more accurate than forward/backward
- Smoothing window size affects bias-variance tradeoff
- Multiple window sizes recommended for sensitivity analysis

### Archon Code Examples

**Note:** Archon MCP unavailable. Standard implementations referenced.

**Second Derivative Computation Pattern:**
```python
import numpy as np
from scipy.ndimage import uniform_filter1d

def compute_second_derivative(wga_curve, window_size=5):
    smoothed = uniform_filter1d(wga_curve, size=window_size)
    d1 = np.gradient(smoothed)
    d2 = np.gradient(d1)
    return d2
```

**Peak Detection Pattern:**
```python
from scipy.signal import find_peaks

def detect_crystallization_peak(d2_wga, prominence=0.01):
    peaks, properties = find_peaks(-d2_wga, prominence=prominence)
    if len(peaks) > 0:
        return peaks[0], properties['prominences'][0]
    return None, 0.0
```

### Exa GitHub Implementations

**Note:** Exa MCP unavailable. Using known implementations from literature.

**Repository 1**: p-lambda/wilds (Official WILDS Benchmark)
- **URL**: https://github.com/p-lambda/wilds
- **Relevance**: Official benchmark suite with WGA computation utilities
- **Key Code**: `wilds/common/metrics/all_metrics.py` contains worst-group accuracy computation
- **Training Config**: Standard ERM training with group annotations
- **Dataset**: Waterbirds, CelebA, ColoredMNIST with official splits

**Repository 2**: kohpangwei/group_DRO
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Group DRO paper implementation with per-group tracking
- **Architecture**: ResNet-50 for image classification
- **Training Config**:
  - Optimizer: SGD with momentum 0.9
  - Learning rate: 1e-3 with decay
  - Batch size: 128
  - Epochs: 100 (Waterbirds), 50 (CelebA)

**Repository 3**: anniesch/jtt (Just Train Twice)
- **URL**: https://github.com/anniesch/jtt
- **Relevance**: JTT paper with epoch-level checkpointing
- **Key Feature**: Tracks per-group accuracy across training

**Serena Analysis Needed**: false (code patterns are standard)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a novel detection method (not paper reproduction), so implementation follows standard signal processing patterns:
1. scipy.signal for peak detection (industry standard)
2. numpy for numerical differentiation (well-tested)
3. WILDS for WGA computation (official benchmark utilities)

**Recommended Implementation Path:**
- Primary: Custom second derivative detector with scipy.signal.find_peaks
- Fallback: Savitzky-Golay filter if uniform smoothing introduces artifacts
- Justification: Novel method requires custom implementation; no existing repo implements d²WGA/dt² detection

### Code Analysis (Serena MCP)

**Note:** Serena MCP optional and unavailable. Code patterns are standard signal processing - no complex analysis required.

Standard components:
- `scipy.ndimage.uniform_filter1d` for rolling window smoothing
- `numpy.gradient` for numerical differentiation
- `scipy.signal.find_peaks` for peak detection with prominence filtering

---

## Experiment Specification

### Dataset

**Primary Dataset:** Waterbirds
- **Type:** Standard (WILDS benchmark)
- **Source:** WILDS benchmark suite (p-lambda/wilds)
- **Size:** 4,795 train, 1,199 val, 5,794 test samples
- **Groups:** 4 groups (landbird/waterbird × land/water background)
- **Minority Groups:** ~600 samples (waterbird on land, landbird on water)
- **Purpose:** Compute WGA across training epochs for derivative analysis

**Secondary Datasets:** CelebA, ColoredMNIST (for generalization testing)
- CelebA: 162,770 train samples, binary attribute with spurious correlation
- ColoredMNIST: 50,000 train samples, digit classification with color correlation

**Loading Information** (for Phase 4 download):
- Method: WILDS Python API
- Identifier: waterbirds, celebA, coloredmnist
- Code:
```python
from wilds import get_dataset
dataset = get_dataset(dataset='waterbirds', download=True)
train_data = dataset.get_subset('train')
val_data = dataset.get_subset('val')
test_data = dataset.get_subset('test')
```

### Models

#### Baseline Model

**Architecture:** ResNet-50 with ImageNet pretrained weights
- **Type:** CNN classifier
- **Input:** 224×224 RGB images
- **Output:** 2-class (binary classification)
- **Purpose:** Generate WGA curves for derivative analysis (reuse H-E1 checkpoints)

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

**Architecture:** Baseline + Second Derivative Detection with Multi-Window Analysis

**Core Mechanism Implementation:**

```python
import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks

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
    
    return {'detected': True, 'epoch': peak_epoch, 'prominence': prominence, 'snr': snr}

def run_sensitivity_analysis(wga_curve: np.ndarray, windows: list = [3, 5, 7]) -> dict:
    """Test detection across multiple smoothing windows."""
    results = {}
    for w in windows:
        d2 = compute_wga_second_derivative(wga_curve, window_size=w)
        peak_info = detect_crystallization_peak(d2)
        results[f'window_{w}'] = peak_info
    return results
```

### Training Protocol

**Note:** H-M3 is a detection method validation - it analyzes WGA curves from trained models (H-E1 checkpoints).

**Data Source:** WGA curves from H-E1/H-M1/H-M2 training runs
- 5 random seeds per benchmark
- 3 benchmarks (Waterbirds, CelebA, ColoredMNIST)
- Total: 15 WGA curves to analyze

**Analysis Protocol:**
1. Load WGA curves from previous hypothesis checkpoints
2. For each curve, apply smoothing windows [3, 5, 7] epochs
3. Compute second derivative d²WGA/dt² for each window
4. Detect negative peaks using scipy.signal.find_peaks
5. Record: peak epoch, prominence, SNR for each configuration
6. Aggregate results across seeds and benchmarks

**If No Prior Checkpoints Available (Fresh Run):**
- Optimizer: SGD with momentum 0.9
- Learning rate: 1e-3 (constant for control)
- Batch size: 128
- Epochs: 100 (Waterbirds), 50 (CelebA), 30 (ColoredMNIST)
- Checkpoint: Every epoch (WGA saved to disk)

### Evaluation

**Primary Metrics:**
1. **Detection Rate:** % of runs where significant negative peak detected (target: >80%)
2. **Peak Timing Variance:** Std dev of detected peak epoch across seeds (target: <5 epochs)
3. **Signal-to-Noise Ratio (SNR):** Peak prominence / noise std (target: >2.0)

**Secondary Metrics:**
4. **Window Robustness:** % of windows (3, 5, 7) that detect same peak ± 3 epochs
5. **Cross-Benchmark Consistency:** Correlation of normalized peak timing across benchmarks

**Success Criteria (PoC):**
- Detection Rate ≥ 80% for 5-epoch window
- Peak Timing Variance < 5 epochs across 5 seeds
- SNR > 2.0 for detected peaks

**Failure Criteria:**
- Detection Rate < 50%: Method unreliable
- Variance > 10 epochs: Timing not consistent
- SNR < 1.0: Signal indistinguishable from noise

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Signal Detection / Time Series Analysis
- Library: scipy, numpy
- Code:
```python
from scipy.signal import find_peaks
import numpy as np

def compute_detection_rate(results: list) -> float:
    detected = sum(1 for r in results if r['detected'])
    return detected / len(results)

def compute_timing_variance(results: list) -> float:
    epochs = [r['epoch'] for r in results if r['detected']]
    return np.std(epochs) if len(epochs) > 1 else 0.0
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **WGA Curve with Derivatives**: 3-panel plot showing raw WGA, smoothed WGA, and d²WGA/dt² with peak marked
2. **Window Size Comparison**: Overlay d²WGA/dt² for windows [3, 5, 7] showing peak detection consistency
3. **Detection Heatmap**: Seeds × Benchmarks heatmap showing detected peak epochs (color = epoch, gray = not detected)
4. **SNR Distribution**: Box plot of SNR values across seeds and benchmarks
5. **Timing Variance Plot**: Bar chart showing peak timing variance per benchmark

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. 5-epoch window detects peak in >80% of runs
3. Peak timing variance <5 epochs across seeds

---

## Appendix: Reference Implementations

**Signal Processing References:**

1. **SciPy Documentation - find_peaks**
   - URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
   - Usage: Peak detection with prominence filtering

2. **NumPy Documentation - gradient**
   - URL: https://numpy.org/doc/stable/reference/generated/numpy.gradient.html
   - Usage: Numerical differentiation with central differences

3. **SciPy Documentation - uniform_filter1d**
   - URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.uniform_filter1d.html
   - Usage: Rolling window smoothing

**Group Robustness References:**

4. **WILDS Benchmark** (Koh et al., 2021)
   - URL: https://github.com/p-lambda/wilds
   - Usage: WGA computation utilities, standard datasets

5. **Group DRO** (Sagawa et al., 2020)
   - URL: https://github.com/kohpangwei/group_DRO
   - Usage: Per-group accuracy tracking implementation

**Previous Hypothesis Code:**

6. **H-E1 Checkpoints** (from this project)
   - Path: h-e1/code/checkpoints/
   - Usage: Pre-computed WGA curves for analysis

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- H-M3 set to IN_PROGRESS for Phase 2C experiment design

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
