# Experiment Design: H-M1

**Date:** 2026-04-14
**Author:** Anonymous
**Hypothesis Statement:** Under ERM training, if we compute the second derivative of normalized loss curves, then minority samples will show delayed curvature stabilization (sign-flip epoch ≥3 epochs later than majority in ≥70% of seeds), because prolonged optimization conflict delays the transition from convex to stable loss landscape.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis Template** - Tests specific mechanism of trajectory divergence.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASSED (AUROC = 0.9452)
**Gate Status:** SHOULD_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED ✅)

### Gate Condition
SHOULD_WORK: Curvature timing gap ≥ 3 epochs in ≥ 70% of seeds
- If fails: PIVOT to alternative temporal signatures (e.g., variance patterns)

---

## Continuation Context

This is a **continuation experiment** from H-E1. H-M1 extends the proven trajectory divergence existence (H-E1, AUROC=0.9452) to test a specific mechanistic claim about curvature timing.

### Previous Hypothesis Results (H-E1)
- **Gate:** MUST_WORK - **PASSED**
- **AUROC:** 0.9452 ± 0.0072 (threshold: 0.75)
- **Key Finding:** Initial loss (L₁) is the most discriminative trajectory feature
- **Infrastructure:** Per-sample loss logging, 4 trajectory features extracted
- **Reusable Components:**
  - Dataset loading (Waterbirds with group labels)
  - Model (ResNet-50 pretrained)
  - Training protocol (SGD, lr=0.001, batch_size=128)
  - Loss trajectory tracking infrastructure

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "loss curvature second derivative training dynamics"**
- Results: Diffusion model training patterns (not directly relevant)
- No specific spurious correlation curvature analysis in KB
- General insight: Standard PyTorch loss computation patterns available

**Query 2: "loss landscape optimization convergence neural network"**
- Results: LoRA training, consistency distillation
- Insight: Loss landscape concepts are well-studied but not in spurious correlation context
- Note: This confirms novelty of our research direction

**Key Observation:** Archon KB lacks specific curvature-based spurious correlation research. This confirms the novelty of H-M1's mechanism hypothesis. Implementation will use standard numerical differentiation patterns.

### Archon Code Examples

**Query: "loss trajectory PyTorch second derivative"**
- Source: CLIP/DALLE training patterns
- Pattern: Standard PyTorch training loop with loss computation
- Insight: Can extend H-E1's per-sample loss tracking to compute curvature

**Applicable Patterns for H-M1:**
1. Reuse H-E1's loss trajectory infrastructure
2. Apply second derivative via finite differences
3. Detect sign-flip epoch using threshold-based criteria

### Exa GitHub Implementations

**Query 1: "loss curvature second derivative training dynamics PyTorch"**

**Repository 1**: facebookresearch/scalable-curvature (⭐ 23)
- **URL**: https://github.com/facebookresearch/scalable-curvature
- **Relevance**: State-of-the-art curvature measurement for training dynamics
- **Key Concept**: Critical sharpness (λc) as computationally efficient curvature measure
- **Paper**: "A Scalable Measure of Loss Landscape Curvature for Analyzing Training Dynamics of LLMs" (2026)
- **Insight**: Forward-pass-only curvature estimation possible, but our approach is simpler (numerical differentiation of loss curves)

**Repository 2**: f-dangel/hbp (Hessian Backpropagation) (⭐ 22)
- **URL**: https://github.com/f-dangel/hbp
- **Relevance**: Block-diagonal curvature approximations
- **Note**: More complex than needed for H-M1 (we only need second derivative of scalar loss curves)

**Repository 3**: cybertronai/pytorch-sso (⭐ 149)
- **URL**: https://github.com/cybertronai/pytorch-sso
- **Relevance**: Second-order optimization with curvature estimation
- **Insight**: K-FAC approximation for large-batch training

**Query 2: "spurious correlation minority group detection training dynamics"**

**Paper Reference**: "Identifying Spurious Biases Early in Training through the Lens of Simplicity Bias" (ICLR 2024)
- **URL**: https://openreview.net/pdf?id=ebf182a791caa3374260923deaaa622024643d09
- **Relevance**: DIRECTLY relevant - uses gradient trajectories to identify spurious biases early
- **Key Finding**: Spurious features can be detected in initial training iterations
- **Connection to H-M1**: Supports our hypothesis that minority samples show different temporal dynamics

**Paper Reference**: "When Majorities Prevent Learning: Eliminating Bias" (ICLR 2023)
- **URL**: https://openreview.net/pdf?id=W7udwvFMnAd
- **Relevance**: Tracks gradient trajectories to find majority/minority subgroups
- **Key Finding**: Gradient trajectory tracking enables majority subpopulation identification
- **Application**: Validates trajectory-based group detection approach

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Confidence | Use Case |
|----------|--------|------------|----------|
| 1 (HIGHEST) | H-E1 codebase | Very High | Loss trajectory infrastructure, dataset, model |
| 2 | scipy.differentiate | Very High | Second derivative computation |
| 3 | numpy.gradient | Very High | Alternative differentiation method |

**Recommended Implementation Path:**
- Primary: Extend H-E1's LossTrajectoryTracker with curvature computation
- Fallback: Use scipy.differentiate.derivative for robust second derivative
- Justification: H-E1 infrastructure is proven (AUROC=0.9452), extending it minimizes implementation risk

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear.

H-M1 uses standard numerical methods:
1. **Second derivative**: Finite difference formula `d²L/dt² = (L[t+1] - 2*L[t] + L[t-1]) / Δt²`
2. **Sign-flip detection**: Find first epoch where curvature stabilizes (κ > threshold for N consecutive epochs)
3. **Statistical comparison**: Compare median sign-flip epochs between minority and majority groups

No complex custom architectures require Serena analysis.

---

## Experiment Specification

### Dataset

**Dataset**: Waterbirds (CONTINUATION from H-E1)
**Type**: standard (REAL dataset - NOT synthetic)
**Source**: Sagawa et al. (2020) - Distributionally Robust Neural Networks

**Statistics** (same as H-E1):
- Total training samples: 4,795
- Validation samples: 1,199
- Test samples: 5,794
- Classes: 2 (waterbird, landbird)
- Groups: 4 (bird_type × background)
  - G1: Landbirds on land BG - 3,498 (majority)
  - G2: Landbirds on water BG - 184 (minority)
  - G3: Waterbirds on water BG - 1,057 (majority)
  - G4: Waterbirds on land BG - 56 (minority)

**Preprocessing** (same as H-E1):
- Resize: 224×224
- Normalization: ImageNet mean/std

**Loading Information** (for Phase 4 download):
- Method: Reuse H-E1 data loading (already cached)
- Identifier: `waterbirds` (WILDS) or direct download
- Code:
```python
# Reuse H-E1 data loading
# Data path: .data_cache/datasets/waterbirds/waterbird_complete95_forest2water2/
```

### Models

#### Baseline Model

**Architecture**: ResNet-50 (CONTINUATION from H-E1)
**Type**: CNN pretrained on ImageNet
**Source**: torchvision.models

**Configuration** (same as H-E1):
- Backbone: ResNet-50 (pretrained on ImageNet)
- Final layer: Linear(2048, 2) for binary classification
- Standard ERM training

**Loading Information** (for Phase 4 download):
- Method: torchvision (reuse H-E1 model loading)
- Identifier: `resnet50` with `weights=IMAGENET1K_V1`
- Code:
```python
# Reuse H-E1 model loading code
import torchvision.models as models
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
model.fc = nn.Linear(model.fc.in_features, 2)
```

#### Proposed Model

**Architecture:** ResNet-50 (ERM) + Per-Sample Loss Curvature Analysis

**Integration Point:**
- Loss tracking: Reuse H-E1's per-sample loss logging
- Curvature computation: After loss trajectory collection (post-epoch)
- Sign-flip detection: After curvature computation (post-training)

**Modification from H-E1:**
- Add curvature (second derivative) computation from loss trajectories
- Add sign-flip epoch detection algorithm
- Compare sign-flip epochs between minority and majority groups

**Core Mechanism Implementation:**

```python
# Core Mechanism: Loss Curvature Sign-Flip Detection
# Based on: H-E1 LossTrajectoryTracker + scipy finite differences
# Paper context: facebookresearch/scalable-curvature concepts adapted for per-sample analysis

import numpy as np
from scipy.ndimage import gaussian_filter1d

class CurvatureTimingAnalyzer:
    """
    Analyze curvature timing of per-sample loss trajectories.
    H-M1 Hypothesis: Minority samples show delayed curvature stabilization
    (sign-flip epoch ≥3 epochs later than majority in ≥70% of seeds).
    """
    def __init__(self, loss_history, kappa_threshold=-0.002, consecutive_epochs=2):
        """
        Args:
            loss_history: (N, E) array of per-sample losses from H-E1
            kappa_threshold: Curvature threshold for stabilization (default: -0.002)
            consecutive_epochs: Epochs above threshold required (default: 2)
        """
        self.loss_history = loss_history  # (num_samples, num_epochs)
        self.kappa_threshold = kappa_threshold
        self.consecutive_epochs = consecutive_epochs
        self.num_samples, self.num_epochs = loss_history.shape
    
    def compute_normalized_loss(self):
        """Normalize loss by initial value (L_t / L_1) for scale invariance."""
        L = self.loss_history
        L_norm = L / (L[:, 0:1] + 1e-8)  # Avoid division by zero
        return L_norm
    
    def compute_curvature(self, sigma=1.0):
        """
        Compute second derivative of normalized loss curves.
        Uses Gaussian smoothing + central difference formula.
        
        Args:
            sigma: Gaussian smoothing parameter (default: 1.0)
        Returns:
            curvature: (N, E-2) array of second derivatives
        """
        L_norm = self.compute_normalized_loss()
        
        # Optional smoothing to reduce noise
        if sigma > 0:
            L_smooth = gaussian_filter1d(L_norm, sigma=sigma, axis=1)
        else:
            L_smooth = L_norm
        
        # Second derivative via central differences: d²L/dt² = L[t+1] - 2*L[t] + L[t-1]
        # Spacing Δt = 1 (one epoch)
        curvature = L_smooth[:, 2:] - 2 * L_smooth[:, 1:-1] + L_smooth[:, :-2]
        
        return curvature  # (N, E-2)
    
    def detect_sign_flip_epoch(self, curvature):
        """
        Detect sign-flip epoch: first epoch where curvature > threshold
        for consecutive_epochs consecutive epochs.
        
        Sign-flip represents transition from convex (negative curvature)
        to stable (near-zero curvature) loss landscape.
        
        Args:
            curvature: (N, E-2) array of second derivatives
        Returns:
            sign_flip_epochs: (N,) array of sign-flip epochs per sample
        """
        N, E = curvature.shape
        sign_flip_epochs = np.full(N, E + 2)  # Default: never stabilized
        
        # Check each sample
        for i in range(N):
            for t in range(E - self.consecutive_epochs + 1):
                # Check if curvature > threshold for consecutive epochs
                if np.all(curvature[i, t:t+self.consecutive_epochs] > self.kappa_threshold):
                    sign_flip_epochs[i] = t + 1  # +1 for 1-indexed epochs
                    break
        
        return sign_flip_epochs
    
    def compute_timing_gap(self, group_labels):
        """
        Compute timing gap between minority and majority groups.
        
        Args:
            group_labels: (N,) array of group labels (0-3 for Waterbirds)
        Returns:
            gap: median(minority) - median(majority) sign-flip epochs
            minority_median: median sign-flip epoch for minority
            majority_median: median sign-flip epoch for majority
        """
        curvature = self.compute_curvature()
        sign_flip_epochs = self.detect_sign_flip_epoch(curvature)
        
        # Minority groups: G2 (label=1) and G4 (label=3)
        minority_mask = (group_labels == 1) | (group_labels == 3)
        majority_mask = ~minority_mask
        
        minority_median = np.median(sign_flip_epochs[minority_mask])
        majority_median = np.median(sign_flip_epochs[majority_mask])
        
        gap = minority_median - majority_median
        
        return {
            'timing_gap': gap,
            'minority_median_epoch': minority_median,
            'majority_median_epoch': majority_median,
            'minority_sign_flips': sign_flip_epochs[minority_mask],
            'majority_sign_flips': sign_flip_epochs[majority_mask]
        }

# Usage in experiment:
# 1. Reuse H-E1's loss_history (num_samples, num_epochs)
# 2. analyzer = CurvatureTimingAnalyzer(loss_history)
# 3. results = analyzer.compute_timing_gap(group_labels)
# 4. Check: gap >= 3 epochs in >= 70% of seeds
```

### Training Protocol

> **MECHANISM Hypothesis**: Multiple seeds required to test "≥70% of seeds" criterion.

**Training Configuration** (CONTINUATION from H-E1):
- **Optimizer**: SGD
  - momentum: 0.9
  - weight_decay: 0.0001
  - **Source**: H-E1 validated configuration

- **Learning Rate**: 0.001
  - **Source**: H-E1 validated configuration

- **Batch Size**: 128
  - **Source**: H-E1 validated configuration

- **Epochs**: 20 (with trajectory logging for all epochs)
  - **Rationale**: Curvature stabilization may occur later than epoch 5
  - Need full trajectory for accurate sign-flip detection

- **Loss Function**: CrossEntropyLoss with `reduction='none'`
  - Reuse H-E1's per-sample loss tracking

- **Seeds**: 5+ (minimum for "70% of seeds" criterion)
  - **Rationale**: Need statistical power for percentage-based success criterion
  - 5 seeds: 70% = at least 3.5 → need 4/5 to pass
  - 10 seeds: 70% = 7/10 to pass

**Per-Sample Loss Logging Protocol** (same as H-E1):
1. After each training epoch, run deterministic evaluation pass
2. Disable data augmentation (only resize + center crop)
3. Compute loss with `reduction='none'`
4. Store per-sample losses indexed by sample ID
5. After all epochs, compute curvature and sign-flip epochs

### Evaluation

> **MECHANISM Hypothesis**: Tests specific mechanistic claim about timing.

**Primary Metric**: Curvature Timing Gap (epochs)
- Definition: median(minority_sign_flip_epoch) - median(majority_sign_flip_epoch)
- Target: Gap ≥ 3 epochs in ≥ 70% of seeds

**Secondary Metrics**:
- Sign-flip epoch distribution (minority vs majority)
- Gap direction consistency (minority always later)
- Per-group curvature trajectories

**Success Criteria**:
- ✅ PASS: Timing gap ≥ 3 epochs in ≥ 70% of seeds (e.g., 4/5 or 7/10 seeds)
- ❌ FAIL: Timing gap < 3 epochs OR gap in < 70% of seeds

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical comparison (median epochs)
- Library: numpy, scipy.stats
- Code:
```python
import numpy as np
from scipy import stats

def evaluate_timing_gap(results_per_seed):
    """
    Evaluate H-M1 success criterion across seeds.
    
    Args:
        results_per_seed: List of dicts from CurvatureTimingAnalyzer per seed
    Returns:
        pass_rate: Fraction of seeds with gap >= 3 epochs
        gaps: List of timing gaps per seed
    """
    gaps = [r['timing_gap'] for r in results_per_seed]
    passes = [g >= 3 for g in gaps]
    pass_rate = np.mean(passes)
    
    return {
        'pass_rate': pass_rate,  # Target: >= 0.70
        'gaps': gaps,
        'mean_gap': np.mean(gaps),
        'std_gap': np.std(gaps),
        'passes': passes,
        'gate_passed': pass_rate >= 0.70
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Timing gap vs 3-epoch threshold, pass rate vs 70% threshold

#### Additional Figures (LLM Autonomous)

Based on H-M1 hypothesis (curvature timing mechanism), recommended visualizations:

1. **Curvature Trajectory Comparison** (recommended)
   - Plot: Second derivative (κ) over epochs
   - Groups: Minority vs Majority (mean ± std)
   - Highlight: Sign-flip epoch markers
   - Purpose: Visualize curvature dynamics and stabilization delay

2. **Sign-Flip Epoch Distribution** (recommended)
   - Plot: Histogram/violin of sign-flip epochs
   - Groups: Minority vs Majority
   - Purpose: Show timing gap distribution

3. **Per-Seed Timing Gap** (recommended)
   - Plot: Bar chart of timing gaps per seed
   - Threshold line: 3 epochs
   - Purpose: Show consistency across seeds

4. **Normalized Loss Curves with Curvature Annotations** (optional)
   - Plot: Loss trajectories with curvature sign-flip markers
   - Purpose: Connect loss dynamics to curvature timing

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: Curvature can be computed from loss trajectories (simple numerical differentiation)
- **mechanism_isolatable**: Sign-flip epoch is a discrete, measurable quantity per sample
- **baseline_measurable**: Majority group sign-flip epoch provides clear baseline

### Architecture Compatibility
- **Compatible**: Any model producing per-sample loss trajectories
- **Requirement**: At least 5 epochs of loss history for meaningful curvature computation
- **H-E1 Infrastructure**: Fully compatible (extends LossTrajectoryTracker)

### Activation Indicators
- **mechanism_log_message**: "Computing curvature: d²L/dt² = {value:.6f} at epoch {epoch}"
- **tensor_shape_change**: loss_history (N, E) → curvature (N, E-2) → sign_flip_epochs (N,)
- **metric_delta_expected**: Timing gap > 0 (minority later than majority)

### Mechanism Verification Code
```python
def verify_curvature_mechanism(loss_history, group_labels, logger):
    """Verify curvature mechanism is working correctly."""
    
    # 1. Check curvature can be computed
    analyzer = CurvatureTimingAnalyzer(loss_history)
    curvature = analyzer.compute_curvature()
    assert curvature.shape == (loss_history.shape[0], loss_history.shape[1] - 2), \
        f"Curvature shape mismatch: {curvature.shape}"
    logger.info(f"✓ Curvature computed: shape {curvature.shape}")
    
    # 2. Check curvature values are reasonable (not all zeros or NaN)
    assert not np.all(curvature == 0), "Curvature is all zeros - mechanism not activating"
    assert not np.any(np.isnan(curvature)), "Curvature contains NaN - numerical issue"
    logger.info(f"✓ Curvature values valid: mean={curvature.mean():.6f}, std={curvature.std():.6f}")
    
    # 3. Check sign-flip can be detected
    sign_flip_epochs = analyzer.detect_sign_flip_epoch(curvature)
    detected_count = np.sum(sign_flip_epochs < curvature.shape[1] + 2)
    logger.info(f"✓ Sign-flip detected for {detected_count}/{len(sign_flip_epochs)} samples")
    
    # 4. Check group comparison is possible
    results = analyzer.compute_timing_gap(group_labels)
    logger.info(f"✓ Timing gap computed: {results['timing_gap']:.2f} epochs")
    logger.info(f"  Minority median: {results['minority_median_epoch']:.2f}")
    logger.info(f"  Majority median: {results['majority_median_epoch']:.2f}")
    
    return True
```

### Hypothesis Support Criteria
- **hypothesis_support_threshold**: timing_gap >= 3 epochs in >= 70% of seeds
- **hypothesis_support_metric**: pass_rate (fraction of seeds meeting criterion)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: General Training Loop Patterns
- **Type**: Code examples
- **Query Used**: "loss trajectory PyTorch second derivative"
- **Relevance**: Standard PyTorch training patterns
- **Key Insights**: Loss computation with reduction='none' for per-sample tracking
- **Used For**: Extending H-E1's training loop

**Note**: Archon KB lacks specific curvature-based spurious correlation research, confirming novelty.

### B. GitHub Implementations (Exa)

**Repository B.1**: facebookresearch/scalable-curvature (⭐ 23)
- **URL**: https://github.com/facebookresearch/scalable-curvature
- **Query Used**: "loss curvature second derivative training dynamics PyTorch"
- **Relevance**: State-of-the-art curvature measurement for training dynamics
- **Key Concept**: Critical sharpness (λc = 2/ηc) as efficient curvature measure
- **Paper**: Kalra et al. "A Scalable Measure of Loss Landscape Curvature" (2026)
- **Insight**: Forward-pass-only curvature estimation; our approach is simpler (numerical differentiation)
- **Used For**: Conceptual validation that curvature-based analysis is sound

**Repository B.2**: scipy.differentiate
- **URL**: https://docs.scipy.org/doc/scipy/reference/differentiate.html
- **Query Used**: "numerical second derivative finite difference"
- **Relevance**: Standard numerical differentiation methods
- **Key Formula**: d²f/dx² = (f(x+h) - 2f(x) + f(x-h)) / h²
- **Used For**: Second derivative computation in CurvatureTimingAnalyzer

**Paper Reference B.3**: "Identifying Spurious Biases Early in Training" (ICLR 2024)
- **URL**: https://openreview.net/pdf?id=ebf182a791caa3374260923deaaa622024643d09
- **Query Used**: "spurious correlation minority group detection training dynamics"
- **Relevance**: Uses gradient trajectories to identify spurious biases early
- **Key Finding**: Spurious features detectable in initial training iterations
- **Used For**: Theoretical support for trajectory-based analysis

**Paper Reference B.4**: "When Majorities Prevent Learning" (ICLR 2023)
- **URL**: https://openreview.net/pdf?id=W7udwvFMnAd
- **Query Used**: Same as B.3
- **Relevance**: Gradient trajectory tracking for majority/minority identification
- **Key Finding**: Tracking gradient trajectories enables subpopulation identification
- **Used For**: Validation of trajectory-based group detection approach

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

H-M1 uses standard numerical methods (finite differences) which don't require deep semantic analysis.

### D. Previous Hypothesis Context

**Source**: H-E1 Validation Results
- **Hypothesis**: H-E1 (Trajectory Divergence Existence)
- **Gate**: MUST_WORK - **PASSED**
- **AUROC**: 0.9452 ± 0.0072
- **Key Finding**: Trajectory features successfully predict minority group membership
- **Reused Components**:
  - Dataset loading (Waterbirds)
  - Model (ResNet-50)
  - Training protocol (SGD, lr=0.001)
  - LossTrajectoryTracker class
- **Why Reused**: H-E1 established infrastructure for per-sample loss tracking; H-M1 extends with curvature analysis

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Waterbirds) | Previous hypothesis | H-E1 (validated) |
| Model (ResNet-50) | Previous hypothesis | H-E1 (validated) |
| Training protocol | Previous hypothesis | H-E1 (validated) |
| Loss trajectory infrastructure | Previous hypothesis | H-E1 LossTrajectoryTracker |
| Curvature computation | scipy docs + paper | B.2 (scipy), B.1 (scalable-curvature) |
| Sign-flip detection | Phase 2B | 02b_verification_plan.md §H-M1 |
| Success criteria | Phase 2B | 02b_verification_plan.md (Gap ≥ 3, 70% seeds) |
| Theoretical support | ICLR papers | B.3 (Simplicity Bias), B.4 (Majorities) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-14

### Workflow History for This Hypothesis
- Phase 2C started: 2026-04-14
- Prerequisite H-E1: PASSED (AUROC = 0.9452)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Continuation from: H-E1 (validated infrastructure)*
*Next Phase: Phase 3 - Implementation Planning*
