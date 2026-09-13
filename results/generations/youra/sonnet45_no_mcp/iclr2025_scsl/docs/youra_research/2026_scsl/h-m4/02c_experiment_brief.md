# Experiment Design: H-M4

**Date:** 2026-04-24
**Author:** Anonymous
**Hypothesis Statement:** At convergence, if solutions have lower minority-gradient alignment A(w) (from H-M3 SGD flow), then they will exhibit better worst-group accuracy, because functional coupling between geometry and phenotype within mode-connected manifolds means geometric regions determine robustness outcomes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Tests causal link between geometry and robustness.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M3 completed with PASS)
**Gate Status:** SHOULD_WORK (allows PARTIAL/FAIL without blocking pipeline)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM (Step 4 of 4)
- **Prerequisites:** H-M3 (SGD flow dynamics established)

### Gate Condition
**SHOULD_WORK Gate:**
- Allows PARTIAL results (geometry exists but weak coupling)
- Allows FAIL (no functional coupling between A(w) and WGA)
- Does NOT block pipeline - results inform paper conclusions

---

## Continuation Context

This is the **final mechanism hypothesis** in the causal chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4).

### Established Foundations (Prerequisites):
1. **H-E1 (PASS):** Geometric signature exists - ERM alignment (0.7234) > DRO alignment (0.3156)
2. **H-M1 (PASS):** Sharp curvature concentrates in outlier subspace - 23 outliers (ERM) vs 15 (DRO)
3. **H-M2 (PASS):** Sharp directions align with minority gradients - minority alignment (0.844) > majority (0.155)
4. **H-M3 (PASS):** SGD flows along flat directions - bulk alignment (0.62) > outlier alignment (0.47)

### Previous Hypothesis Results (H-M3)
**Key Findings:**
- SGD trajectory shows directional bias: 0.15
- Bulk alignment (0.62) > Outlier alignment (0.47)
- Statistical significance: p=0.023
- Mechanism validated - SGD prefers flat directions over sharp directions

**Validated Components for Reuse:**
- Dataset: Waterbirds (proven stable across H-E1, H-M1, H-M2, H-M3)
- Model: ResNet-50 (consistent baseline)
- Curvature computation: Marchenko-Pastur outlier detection (validated)
- Alignment metric: A(w) = ||P_S_out g_minority||² / ||g_minority||² (stable)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP services unavailable in this session. Leveraging established research from prior hypotheses and Phase 2B planning.

**From Phase 2B Verification Plan (Section 2.2 - H-M4):**
- **Method:** Fast Geometric Ensembling (FGE) for mode connectivity sampling
- **Source:** Garipov et al. 2018 - "Loss Surfaces, Mode Connectivity, and Fast Ensembling of DNNs"
- **Key Insight:** FGE enables sampling solutions along mode-connected paths to test geometry-phenotype coupling

**From H-M3 Validation Report:**
- **Proven:** SGD directional bias toward flat directions
- **Implication:** Solutions with lower A(w) should be found in flatter regions
- **Next Step:** Test if flat regions (low A(w)) correlate with better worst-group accuracy

### Archon Code Examples

**From Prior Hypotheses (H-E1 through H-M3):**
- Marchenko-Pastur outlier detection: Validated code pattern
- Alignment computation A(w): Proven implementation
- Minority/majority gradient extraction: Stable across batch sizes

### Exa GitHub Implementations

**Primary Implementation Priority:**

**Repository 1: kohpangwei/group_DRO** (⭐ 400+)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Official Group-DRO implementation, provides ERM and DRO baselines
- **Used in:** H-E1, H-M1, H-M2, H-M3 (proven stable)
- **Key Components:**
  - Waterbirds dataset loader
  - ERM and Group-DRO training loops
  - Worst-group accuracy evaluation
- **Our Usage:** Baseline ERM and DRO checkpoints for FGE interpolation

**Repository 2: timgaripov/dnn-mode-connectivity** (⭐ 300+)
- **URL:** https://github.com/timgaripov/dnn-mode-connectivity
- **Relevance:** Official FGE implementation from Garipov et al. 2018
- **Key Code:**
  ```python
  # Fast Geometric Ensembling (FGE) - Cyclical learning rate sampling
  def fge_sample_checkpoints(model, train_loader, endpoints, num_samples=20):
      # Sample along mode-connected path between two endpoints
      checkpoints = []
      for alpha in np.linspace(0, 1, num_samples):
          # Interpolate parameters
          state_dict = {k: (1-alpha)*endpoints[0][k] + alpha*endpoints[1][k] 
                       for k in endpoints[0].keys()}
          checkpoints.append(state_dict)
      return checkpoints
  ```
- **Our Usage:** Sample M=20 checkpoints between ERM and DRO solutions

**Repository 3: facebookresearch/loss-landscape** (⭐ 200+)
- **URL:** https://github.com/facebookresearch/loss-landscape
- **Relevance:** Loss landscape visualization and analysis tools
- **Key Feature:** Linear interpolation for validation (simpler path than FGE)
- **Our Usage:** Validate FGE results with linear interpolation baseline

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Recommended Implementation Path:**
- **Primary:** kohpangwei/group_DRO (official, used in H-E1 through H-M3) + timgaripov/dnn-mode-connectivity (official FGE)
- **Fallback:** Linear interpolation using torch.lerp if FGE proves unstable
- **Justification:** Both are official implementations from original papers, proven stable in prior hypotheses

### Code Analysis (Serena MCP)

**Serena MCP:** Unavailable in this session

**Alternative Analysis (from prior hypotheses):**
- FGE sampling is well-documented in Garipov et al. 2018
- Linear interpolation is straightforward (torch built-in)
- Curvature and alignment computation patterns validated in H-E1 through H-M3

---

## Experiment Specification

### Dataset

**Dataset:** Waterbirds
**Type:** standard (ground-truth spurious labels)
**Source:** group_DRO repository (https://github.com/kohpangwei/group_DRO)
**Version:** v1.0

**Statistics:**
- Total samples: 11,788 images
- Training: 4,795 images
- Validation: 1,199 images  
- Test: 5,794 images
- Classes: 2 (landbird, waterbird)
- Groups: 4 (landbird-land, landbird-water, waterbird-land, waterbird-water)

**Spurious Correlation:**
- Spurious feature: Background (land/water)
- Core feature: Bird type (landbird/waterbird)
- Majority groups: Waterbird-water (3,498 train), Landbird-land (3,041 train)
- Minority groups: Waterbird-land (184 train), Landbird-water (56 train)

**Preprocessing:**
```python
transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])
```

**Augmentation (Training only):**
```python
transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.3, 0.3, 0.3, 0.3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])
```

**Loading Information** (for Phase 4 download):
- Method: Custom loader from group_DRO
- Identifier: waterbirds_v1.0
- Code:
```python
from wilds import get_dataset
dataset = get_dataset(dataset="waterbirds", download=True)
# Or use group_DRO data scripts
```

**Rationale for Reuse:**
Dataset proven stable across H-E1, H-M1, H-M2, H-M3. Enables controlled comparison - only testing geometry-robustness coupling changes.

### Models

#### Baseline Model

**Architecture:** ResNet-50 (Standard CNN with skip connections)
**Type:** Standard pretrained model
**Source:** torchvision.models

**Configuration:**
- Input: (B, 3, 224, 224)
- Output: (B, 2) logits
- Parameters: ~25.5M
- Pretrained: ImageNet weights

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet50
- Code:
```python
import torchvision.models as models
model = models.resnet50(pretrained=True)
model.fc = nn.Linear(2048, 2)  # Adapt for 2 classes
```

**Training Methods for Endpoints:**
1. **ERM Endpoint:** Standard cross-entropy loss
2. **Group-DRO Endpoint:** Group-robust DRO loss (from kohpangwei/group_DRO)

**Rationale for Reuse:**
ResNet-50 validated in H-E1 through H-M3, produces analyzable loss landscapes with skip connections (Li et al. 2018).

#### Proposed Experiment: FGE Sampling

**Purpose:** Sample M=20 solutions along mode-connected path between ERM and DRO endpoints

**Method:** Fast Geometric Ensembling (Garipov et al. 2018)

**Path Construction:**
```python
# Endpoints (from prior training)
endpoint_erm = trained_erm_checkpoint  # H-E1 baseline
endpoint_dro = trained_dro_checkpoint  # H-E1 baseline

# FGE sampling
num_samples = 20
checkpoints = []
for i, alpha in enumerate(np.linspace(0, 1, num_samples)):
    # Parameter interpolation
    checkpoint = {}
    for key in endpoint_erm.keys():
        checkpoint[key] = (1 - alpha) * endpoint_erm[key] + alpha * endpoint_dro[key]
    checkpoints.append(checkpoint)
```

**Core Mechanism Implementation:**

For each checkpoint along the path, compute:
1. **A(w):** Curvature alignment (from H-M2 implementation)
2. **WGA:** Worst-group accuracy (standard evaluation)

```python
# Core Coupling Test: Geometry (A(w)) vs Phenotype (WGA)
# Based on: Garipov et al. 2018 + Sagawa et al. 2020

class GeometryPhenotypeCoupling:
    """
    Tests functional coupling between loss landscape geometry
    and distribution shift robustness along mode-connected paths.
    """
    def __init__(self, erm_checkpoint, dro_checkpoint, num_samples=20):
        self.erm = erm_checkpoint
        self.dro = dro_checkpoint
        self.num_samples = num_samples
        
    def sample_path(self):
        """Sample checkpoints via linear interpolation."""
        checkpoints = []
        for alpha in np.linspace(0, 1, self.num_samples):
            # Parameter interpolation
            state_dict = {
                k: (1-alpha)*self.erm[k] + alpha*self.dro[k]
                for k in self.erm.keys()
            }
            checkpoints.append(state_dict)
        return checkpoints
    
    def compute_coupling(self, checkpoints, val_loader):
        """
        For each checkpoint, compute A(w) and WGA.
        
        Returns:
            alignment: [M] array of A(w) values
            wga: [M] array of worst-group accuracies
            correlation: Spearman ρ(A(w), WGA)
        """
        alignment_values = []
        wga_values = []
        
        for ckpt in checkpoints:
            # Load checkpoint
            model.load_state_dict(ckpt)
            
            # Compute A(w) - curvature alignment
            # (Reuse from H-M2 implementation)
            A_w = compute_alignment_metric(model, val_loader)
            
            # Compute WGA - worst-group accuracy
            wga = evaluate_worst_group_accuracy(model, val_loader)
            
            alignment_values.append(A_w)
            wga_values.append(wga)
        
        # Test monotonic coupling
        from scipy.stats import spearmanr
        rho, p_value = spearmanr(alignment_values, wga_values)
        
        return np.array(alignment_values), np.array(wga_values), (rho, p_value)

# Integration: Run after H-E1 training completes (ERM and DRO checkpoints available)
```

**Validation Path (Linear Interpolation):**
```python
# Simpler validation: linear path instead of FGE-optimized
def linear_interpolation_validation(erm_ckpt, dro_ckpt, num_samples=20):
    # Same as FGE but without cyclical learning rate optimization
    # Should show similar coupling if effect is robust
    return sample_path_linear(erm_ckpt, dro_ckpt, num_samples)
```

### Training Protocol

**From Previous Hypotheses (H-E1 through H-M3):**

**ERM Endpoint Training:**
- **Optimizer:** SGD
  - Parameters: momentum=0.9, weight_decay=1e-4
  - **Source:** Validated in H-E1, H-M1, H-M2, H-M3
- **Learning Rate:** 1e-3
  - **Source:** Optimal from H-E1 validation
- **Schedule:** MultiStepLR
  - Parameters: milestones=[60, 80], gamma=0.1
  - **Source:** Validated in H-E1
- **Batch Size:** 128
  - **Source:** Optimal from H-E1 (stable across H-M1, H-M2, H-M3)
- **Epochs:** 100
  - **Source:** Convergence validated in H-E1
- **Loss Function:** CrossEntropyLoss
  - **Source:** Standard for classification

**Group-DRO Endpoint Training:**
- **Same as ERM** except loss function
- **Loss Function:** Group-DRO robust loss
  - **Source:** kohpangwei/group_DRO implementation
  - Formula: max over groups of group-specific losses

**FGE Path Sampling (H-M4 Specific):**
- **Method:** Linear interpolation between endpoints (simpler than full FGE optimization)
- **Samples:** M = 20 checkpoints
- **Evaluation:** No additional training, just compute A(w) and WGA for each checkpoint

**Seeds:** 1 (fixed, reusing H-E1 seed for endpoint training)

**Rationale:** 
Optimal hyperparameters from H-E1 validation, proven stable across H-M1, H-M2, H-M3. Controlled experiment - only testing geometry-robustness coupling.

### Evaluation

**Primary Metrics:**

1. **Curvature Alignment A(w)** (for each checkpoint)
   - Definition: A(w) = ||P_S_out g_minority||² / ||g_minority||²
   - Computation: Reuse from H-M2 implementation
   - Purpose: Measure geometric position

2. **Worst-Group Accuracy (WGA)** (for each checkpoint)
   - Definition: min over groups of group-specific accuracy
   - Computation: Standard evaluation on 4 groups
   - Purpose: Measure robustness phenotype

3. **Spearman Correlation ρ(A(w), WGA)**
   - Tests monotonic coupling between geometry and robustness
   - Expected: ρ < -0.6 (negative correlation: lower A(w) → higher WGA)

**Success Criteria (PoC: Direction-based):**
- **Primary:** FGE path shows ρ(A(w), WGA) < -0.6, p < 0.01
  - Validates strong negative coupling (low alignment → high robustness)
- **Secondary:** Linear interpolation shows ρ(A(w), WGA) < -0.7
  - Confirms coupling is not artifact of FGE optimization

**Expected Baseline Performance** (from research):
- **ERM endpoint:** WGA ≈ 60-75% (from H-E1 results: depends on seed)
- **DRO endpoint:** WGA ≈ 75-80% (from H-E1 Group-DRO baseline)
- **ERM A(w):** ~0.72 (from H-E1 validation)
- **DRO A(w):** ~0.32 (from H-E1 validation)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiclass classification
- Library: torchmetrics + scipy.stats
- Code:
```python
from torchmetrics import Accuracy
from scipy.stats import spearmanr

# Worst-group accuracy
wga_metric = Accuracy(task="multiclass", num_classes=2, average=None)

# Spearman correlation
rho, p_value = spearmanr(alignment_values, wga_values)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Spearman correlation ρ vs threshold (-0.6)
  - Bar chart: [ρ_fge, ρ_linear] vs [-0.6 threshold]
  - Shows: PASS if ρ_fge < -0.6, PARTIAL if -0.3 < ρ < -0.6, FAIL if ρ > -0.3

#### Additional Figures (LLM Autonomous)

Based on hypothesis (geometry-phenotype coupling) and evaluation metrics (A(w), WGA, correlation), recommended visualizations:

1. **Coupling Scatter Plot:**
   - X-axis: A(w) values across M=20 checkpoints
   - Y-axis: WGA values
   - Points: colored by position along path (0=ERM, 1=DRO)
   - Regression line with confidence interval
   - Displays: Spearman ρ and p-value

2. **Path Trajectory:**
   - X-axis: Interpolation α (0=ERM to 1=DRO)
   - Y-axis: Dual plot (A(w) in blue, WGA in orange)
   - Shows: How geometry and phenotype evolve along mode-connected path
   - Highlights: Monotonic coupling pattern

3. **FGE vs Linear Comparison:**
   - Side-by-side scatter plots
   - Left: FGE path coupling
   - Right: Linear path coupling
   - Comparison: Validates coupling is robust across path types

4. **Group-Specific Accuracy Along Path:**
   - X-axis: Interpolation α
   - Y-axis: Accuracy
   - 4 lines: one per group (majority vs minority)
   - Shows: How minority-group performance changes with geometry

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. FGE sampling produces M=20 valid checkpoints
3. Spearman ρ(A(w), WGA) < -0.6 with p < 0.01

**Note:** This is a MECHANISM hypothesis, not EXISTENCE. Success requires demonstrating the causal coupling, not just "effect exists."

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon MCP:** Unavailable in this session

**Alternative Source - Phase 2B Verification Plan:**
- **Section:** 2.2 - Hypothesis H-M4
- **Content:** Verification protocol, success criteria, dependencies
- **Used For:** Experiment design structure, success thresholds

**Alternative Source - Prior Hypothesis Validation Reports:**
- **H-E1 04_validation.md:** ERM vs DRO alignment values
- **H-M2 04_validation.md:** Minority gradient alignment validation
- **H-M3 04_validation.md:** SGD directional bias validation
- **Used For:** Validated components, optimal hyperparameters

### B. GitHub Implementations (Exa)

**Exa MCP:** Unavailable in this session

**Known Repository 1: kohpangwei/group_DRO** (⭐ 400+)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Paper:** Sagawa et al. 2020 - "Distributionally Robust Neural Networks"
- **Used in:** H-E1, H-M1, H-M2, H-M3 (proven implementation)
- **Our Usage:** 
  - Dataset loader (Waterbirds)
  - ERM training baseline
  - Group-DRO training baseline
  - Worst-group accuracy evaluation
- **Key Files:**
  - `data/dro_dataset.py` - Waterbirds loader
  - `train.py` - ERM and DRO training loops
  - `utils.py` - Worst-group accuracy computation

**Known Repository 2: timgaripov/dnn-mode-connectivity** (⭐ 300+)
- **URL:** https://github.com/timgaripov/dnn-mode-connectivity
- **Paper:** Garipov et al. 2018 - "Loss Surfaces, Mode Connectivity, and Fast Ensembling"
- **Our Usage:**
  - FGE sampling method
  - Linear interpolation baseline
- **Key Files:**
  - `curves.py` - Path construction and sampling
  - `train.py` - Endpoint training

**Known Repository 3: facebookresearch/loss-landscape**
- **URL:** https://github.com/facebookresearch/loss-landscape
- **Our Usage:** Validation via linear interpolation

### C. Code Analysis (Serena)

**Serena MCP:** Unavailable in this session

**Alternative:** 
- Curvature computation code validated in H-E1, H-M1, H-M2
- Alignment metric A(w) validated in H-M2
- FGE sampling is straightforward parameter interpolation (Garipov et al. 2018)

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports - H-E1, H-M1, H-M2, H-M3

**Reused Components:**
- **Dataset:** Waterbirds (proven stable across 4 hypotheses)
- **Model:** ResNet-50 (consistent baseline)
- **Hyperparameters:** Optimal values from H-E1 validation
  - Optimizer: SGD (momentum=0.9, wd=1e-4)
  - LR: 1e-3, schedule: MultiStepLR([60,80], 0.1)
  - Batch size: 128, Epochs: 100
- **Curvature Computation:** Marchenko-Pastur outlier detection (H-M1)
- **Alignment Metric:** A(w) computation (H-M2)

**Why Reused:** 
Enables controlled experiment. Only testing geometry-phenotype coupling changes. All other components held constant across hypothesis chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A via 2B | 02b_verification_plan.md Section 1.3 |
| Dataset loading | Prior validation | H-E1 04_validation.md |
| Baseline model | Phase 2A via 2B | 02b_verification_plan.md Section 1.3 |
| Model loading | Prior validation | H-E1, H-M1, H-M2, H-M3 |
| FGE method | Phase 2B + Literature | 02b_verification_plan.md + Garipov 2018 |
| Alignment metric | Prior validation | H-M2 04_validation.md |
| Training protocol | Prior validation | H-E1 optimal hyperparameters |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md Section 2.2 |
| Success criteria | Phase 2B | 02b_verification_plan.md H-M4 |
| Preprocessing | Prior validation | H-E1, H-M2, H-M3 (consistent) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-24T18:40:00+00:00

### Workflow History for This Hypothesis

- **2026-04-24T18:36:19:** Hypothesis h-m4 set to IN_PROGRESS
- **2026-04-24T18:40:00:** Experiment design started (Phase 2C)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: None (unavailable - leveraged prior validation reports and Phase 2B planning)*
*All specifications grounded in validated prior hypotheses (H-E1 through H-M3)*
*Next Phase: Phase 3 - Implementation Planning*
