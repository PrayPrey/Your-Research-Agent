# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Spurious features converge at least 2 epochs earlier than core features across all 4 datasets (CMNIST, Waterbirds, CelebA, NICO++)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.
> ⚠️ **MCP UNAVAILABLE** - Generated from Phase 2B specification without implementation search

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for h-e1)
**Gate Status:** MUST_WORK (failure blocks h-e2, h-e3, h-m1, h-m2)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK**: Failure stops entire workflow and blocks all dependent hypotheses (h-e2, h-e3, h-m1, h-m2). Main hypothesis H-TemporalGradient-v1 would be falsified.

---

## Continuation Context

This is the first hypothesis in the verification pipeline. No previous hypothesis results available.

### Previous Hypothesis Results (if applicable)
N/A - h-e1 is the foundation hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP Server unavailable - Phase 2C proceeded without implementation search.*

**Fallback Strategy:** Use Phase 2B specification and standard spurious correlation benchmark implementations.

### Archon Code Examples

*Not available (MCP unavailable)*

### Exa GitHub Implementations

*Not available (MCP unavailable)*

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

*MCP unavailable - Cannot perform automated implementation search.*

**Recommended Implementation Path:**
- Primary: Standard PyTorch implementation following Phase 2B protocol
- Fallback: Adapt from published spurious correlation benchmark repositories
- Justification: Phase 2B provides sufficient specification for implementation without MCP search

### Code Analysis (Serena MCP)

*Not available (MCP unavailable)*

---

## Experiment Specification

### Dataset

**Datasets (Multi-dataset validation required):**

1. **CMNIST (Colored MNIST)**
   - Type: standard (synthetic corruption)
   - Source: Torchvision MNIST + color bias injection
   - Spurious Feature: Digit color (biased with label)
   - Core Feature: Digit shape
   - Splits: Train/Val/Test with standard bias ratios
   - Preprocessing: Normalize to ImageNet stats, resize to 224×224 for ResNet compatibility

2. **Waterbirds**
   - Type: standard benchmark
   - Source: Wilds benchmark dataset
   - Spurious Feature: Background (land/water)
   - Core Feature: Bird species (landbird/waterbird)
   - Splits: Standard Wilds splits
   - Preprocessing: Standard ImageNet preprocessing

3. **CelebA**
   - Type: standard benchmark
   - Source: Standard CelebA dataset
   - Spurious Feature: Gender (male/female)
   - Core Feature: Target attribute (e.g., Blond_Hair)
   - Splits: Standard CelebA splits filtered for bias
   - Preprocessing: Center crop + resize to 224×224, ImageNet normalization

4. **NICO++**
   - Type: standard benchmark
   - Source: NICO++ benchmark
   - Spurious Feature: Context (background scene)
   - Core Feature: Object class
   - Splits: Standard NICO++ splits
   - Preprocessing: Resize to 224×224, ImageNet normalization

**Loading Information** (for Phase 4 download):
- Method: Download from official sources or use benchmark libraries
- Identifier: 
  - CMNIST: torchvision.datasets.MNIST + custom coloring
  - Waterbirds: wilds.get_dataset('waterbirds')
  - CelebA: torchvision.datasets.CelebA
  - NICO++: Official NICO++ repository
- Code: Standard PyTorch DataLoader with transforms

### Models

#### Baseline Model

**Architecture:**
- CMNIST: ResNet-18 (smaller dataset, simpler features)
- Waterbirds/CelebA/NICO++: ResNet-50 (standard for spurious correlation benchmarks)

**Initialization:** ImageNet pretrained weights (standard practice for transfer learning on spurious correlation benchmarks)

**Output:** Binary classification head (replaced final FC layer)

**Loading Information** (for Phase 4 download):
- Method: torchvision.models
- Identifier: 
  - ResNet-18: torchvision.models.resnet18(pretrained=True)
  - ResNet-50: torchvision.models.resnet50(pretrained=True)
- Code: Replace final FC layer with nn.Linear(num_features, num_classes)

#### Proposed Model

**Architecture:** Baseline ResNet + Ablation Training Strategy

**Core Mechanism Implementation:**

```python
# Ablation Training Strategy for Convergence Measurement
# Three training variants per dataset:

class AblationTrainer:
    """
    Train three variants to measure temporal convergence:
    1. Spurious-only: mask core features during training
    2. Core-only: mask spurious features during training  
    3. Baseline: full features (ERM)
    """
    
    def __init__(self, model, dataset_name):
        self.model = model
        self.dataset = dataset_name
        self.gradient_history = []  # Track per-epoch gradient norms
        
    def train_variant(self, variant_type):
        """
        variant_type: 'spurious', 'core', 'baseline'
        """
        for epoch in range(max_epochs):
            # Forward pass with feature masking
            if variant_type == 'spurious':
                features = self.extract_spurious_only(inputs)
            elif variant_type == 'core':
                features = self.extract_core_only(inputs)
            else:  # baseline
                features = inputs
            
            # Compute loss and gradients
            outputs = self.model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            
            # Track gradient norm for convergence detection
            grad_norm = self.compute_gradient_norm()
            self.gradient_history.append(grad_norm)
            
            # Check convergence criterion
            if self.check_convergence(grad_norm):
                return epoch  # Return convergence epoch E_s or E_c
                
            optimizer.step()
            optimizer.zero_grad()
    
    def compute_gradient_norm(self):
        """Compute L2 norm of all gradients"""
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                total_norm += p.grad.data.norm(2).item() ** 2
        return total_norm ** 0.5
    
    def check_convergence(self, current_norm):
        """
        Convergence criterion: gradient norm < 10% of peak for 3 consecutive epochs
        """
        if len(self.gradient_history) < 4:
            return False
        
        peak_norm = max(self.gradient_history)
        threshold = 0.1 * peak_norm
        
        # Check last 3 epochs below threshold
        recent_norms = self.gradient_history[-3:]
        return all(norm < threshold for norm in recent_norms)
    
    def extract_spurious_only(self, inputs):
        """Dataset-specific spurious feature extraction"""
        if self.dataset == 'CMNIST':
            # Keep only color channels, blur shape
            return gaussian_blur(inputs, kernel_size=15)
        elif self.dataset == 'Waterbirds':
            # Keep only background regions (GradCAM-based masking)
            return mask_foreground(inputs)
        # Similar for CelebA, NICO++
    
    def extract_core_only(self, inputs):
        """Dataset-specific core feature extraction"""
        if self.dataset == 'CMNIST':
            # Keep only shape, remove color (grayscale)
            return rgb_to_grayscale(inputs)
        elif self.dataset == 'Waterbirds':
            # Keep only bird region (foreground segmentation)
            return mask_background(inputs)
        # Similar for CelebA, NICO++

# Experiment execution per dataset
for dataset in ['CMNIST', 'Waterbirds', 'CelebA', 'NICO++']:
    for seed in range(10):  # 10 random seeds for statistical power
        trainer = AblationTrainer(model, dataset)
        
        E_s = trainer.train_variant('spurious')
        E_c = trainer.train_variant('core')
        E_baseline = trainer.train_variant('baseline')
        
        results.append({
            'dataset': dataset,
            'seed': seed,
            'E_spurious': E_s,
            'E_core': E_c,
            'E_baseline': E_baseline
        })
```

### Training Protocol

**Optimizer:** SGD with momentum 0.9

**Learning Rate:**
- CMNIST: 0.001 (cosine annealing)
- Waterbirds: 0.001 (step decay at epochs 30, 60)
- CelebA: 0.0001 (cosine annealing)
- NICO++: 0.001 (cosine annealing)

**Batch Size:**
- CMNIST: 128
- Waterbirds/CelebA/NICO++: 64

**Max Epochs:** 
- CMNIST: 50
- Waterbirds: 100
- CelebA: 80
- NICO++: 100

**Loss Function:** Binary cross-entropy

**Regularization:** Weight decay 1e-4

**Random Seeds:** 10 per dataset (total 40 runs for statistical validation)

**Feature Extraction Methods:**
- Spurious-only: Dataset-specific masking (color blur for CMNIST, background masking for Waterbirds)
- Core-only: Dataset-specific masking (grayscale for CMNIST, foreground segmentation for Waterbirds)

### Evaluation

**Primary Metrics:**

1. **Convergence Epoch (E_s, E_c)**
   - Definition: First epoch where gradient norm < 10% of peak for 3 consecutive epochs
   - Measured for spurious-only, core-only, and baseline variants

2. **Temporal Gap (Δ)**
   - Δ = E_c - E_s
   - Expected: Δ ≥ 2 epochs

**Statistical Tests:**

**Test 1: Paired t-test on (E_s, E_c)**
- Null hypothesis: E_s = E_c (no temporal ordering)
- Alternative: E_s < E_c (spurious converges earlier)
- Success criterion: p < 0.05 AND mean(Δ) ≥ 2 epochs
- Applied per dataset (4 independent tests)

**Multi-dataset Validation:**
- All 4 datasets must show significant temporal gap (p < 0.05)
- At least 3 of 4 datasets must show mean(Δ) ≥ 2 epochs

**PoC Success Criterion (Simplified):**
- Direction check: E_s < E_c for majority of seeds (>5/10) on all datasets
- Magnitude check: mean(Δ) ≥ 2 epochs on at least 2/4 datasets

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification + convergence tracking
- Library: PyTorch (gradient norm computation), scipy.stats (t-test)
- Code: 
  ```python
  from scipy.stats import ttest_rel
  t_stat, p_value = ttest_rel(E_c_samples, E_s_samples)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean(E_s) vs mean(E_c) for each dataset with error bars (±1 std)
- Filename: `figures/convergence_comparison.png`

#### Additional Figures (LLM Autonomous)

1. **Gradient Norm Trajectories**
   - Line plots showing gradient norm vs epoch for spurious/core/baseline variants
   - One subplot per dataset (4-panel figure)
   - Highlights convergence points E_s and E_c

2. **Temporal Gap Distribution**
   - Histogram of Δ = E_c - E_s across all seeds and datasets
   - Reference line at Δ = 2 (success threshold)

3. **Per-Dataset Statistical Results**
   - Table or bar chart showing:
     - Mean Δ per dataset
     - p-values from paired t-test
     - Success/failure indicator per dataset

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `E_s < E_c` for majority of seeds (>5/10) on all 4 datasets

**Full Success Condition (for gate validation):**
- Statistical Test 1 passes on all 4 datasets (p < 0.05 AND mean(Δ) ≥ 2)

---

## Appendix: Reference Implementations

**Key Papers with Code:**

1. **Nam et al. (2020) - Learning from Failure**
   - Repository: https://github.com/alinlab/LfF
   - Relevant: CMNIST implementation, spurious feature masking

2. **Sagawa et al. (2020) - Distributionally Robust Neural Networks**
   - Repository: https://github.com/kohpangwei/group_DRO
   - Relevant: Waterbirds dataset loading, group-based evaluation

3. **Liu et al. (2021) - Just Train Twice**
   - Repository: https://github.com/anniesch/jtt
   - Relevant: CelebA spurious correlation setup

4. **Zhang et al. (2022) - NICO++**
   - Repository: https://github.com/xxgege/NICO-plus
   - Relevant: NICO++ dataset loading and preprocessing

**Implementation Notes:**
- Feature masking strategies must be dataset-specific
- Convergence detection requires careful gradient norm tracking
- Multi-dataset validation critical for generalization claim

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T22:21:00Z

### Workflow History for This Hypothesis
- 2026-08-28T22:21:00Z: Phase 2C initiated (experiment design)
- Status: IN_PROGRESS
- Next: Phase 3 (implementation planning)

---

*MCP Tools Used: NONE (MCP servers unavailable - fallback mode)*
*Specifications derived from Phase 2B verification plan*
*Next Phase: Phase 3 - Implementation Planning*
