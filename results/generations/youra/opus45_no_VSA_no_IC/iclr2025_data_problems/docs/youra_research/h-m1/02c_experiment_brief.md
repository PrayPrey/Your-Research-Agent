# Experiment Design: h-m1

**Date:** 2026-08-24
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Different mathematical operations (gradient projection, checkpoint proximity, K-FAC) create systematically different sensitivities to influence modes
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Testing whether mathematical differences in attribution methods produce measurable sensitivity differences to memorization, feature transfer, and spurious association modes.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** None

### Gate Condition
MUST_WORK: If this fails, downstream hypotheses (h-m2, h-c1, h-c2) cannot proceed.

---

## Continuation Context

First hypothesis in sequence (no prior context).

### Previous Hypothesis Results (if applicable)
N/A - h-m1 has no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "TRAK TracIn influence functions experiment"**
- Limited direct results; found related papers on influence functions in deep learning
- Key insight: Influence methods require careful hyperparameter tuning (damping, projection dimension)

**Query 2: "data attribution LLM training"**
- Found OpenReview paper M3Y74vmsMcY on LLM training data
- HuggingFace 4-bit transformers documentation (quantization affects gradient computation)

### Archon Code Examples

**Query: "influence function gradient PyTorch"**
- PyTorch scaled_dot_product_attention implementation
- PyTorch autograd gradient computation example
- Useful for understanding gradient flow in influence computation

### Exa GitHub Implementations

**Repository 1**: MadryLab/trak (235 stars)
- **URL**: https://github.com/MadryLab/trak
- **Method**: TRAK (Tracing with Randomly-Projected After Kernel)
- **Mathematical Operation**: Gradient projection via random JL projection
- **Key API**:
  ```python
  from trak import TRAKer
  traker = TRAKer(model=model, task='image_classification', train_set_size=N)
  traker.featurize(batch=batch)  # Compute projected gradients
  scores = traker.finalize_scores()  # Get influence scores
  ```
- **Installation**: `pip install traker[fast]`
- **Key Parameters**: proj_dim=2048, use_half_precision=True

**Repository 2**: pytorch/captum + KuchikiRenji/Empirical-Influence-Function
- **URL**: https://github.com/pytorch/captum, https://github.com/KuchikiRenji/Empirical-Influence-Function
- **Method**: TracIn (Tracing Gradient Descent)
- **Mathematical Operation**: Checkpoint-based gradient dot product
- **Key API**:
  ```python
  from src.IF import TracIn
  IF = TracIn(dl_train=trainloader, model=model, 
              param_filter_fn=lambda name, param: 'fc' in name,
              criterion=nn.CrossEntropyLoss(reduction="none"))
  scores = IF.query_influence(test_input, test_target)
  ```
- **Formula**: TracIn(z,z') = Σ_k η_k * ∇ℓ(w_k, z) · ∇ℓ(w_k, z')

**Repository 3**: pomonam/kronfluence (Official)
- **URL**: https://github.com/pomonam/kronfluence
- **Method**: Kronfluence (K-FAC / EK-FAC based influence)
- **Mathematical Operation**: Eigenvalue-corrected Kronecker-factored curvature approximation
- **Key API**:
  ```python
  from kronfluence.analyzer import Analyzer, prepare_model
  model = prepare_model(model=model, task=task)
  analyzer = Analyzer(analysis_name="exp", model=model, task=task)
  analyzer.fit_all_factors(factors_name="factors", dataset=train_dataset)
  analyzer.compute_pairwise_scores(scores_name="scores", ...)
  scores = analyzer.load_pairwise_scores(scores_name="scores")
  ```
- **Installation**: `pip install kronfluence`
- **Supports**: DDP, AMP, torch.compile, FSDP

### 🎯 Implementation Priority Assessment

**CRITICAL: All three methods have official, well-maintained implementations**

| Method | Official Repo | Mathematical Core | LLM Support |
|--------|--------------|-------------------|-------------|
| TRAK | MadryLab/trak | Random projection of gradients | ✅ (BERT, QNLI examples) |
| TracIn | pytorch/captum | Checkpoint gradient dot product | ⚠️ (requires adaptation) |
| Kronfluence | pomonam/kronfluence | K-FAC Hessian approximation | ✅ (LLaMA 8B examples) |

**Recommended Implementation Path:**
- Primary: Use official libraries (trak, kronfluence) + captum TracIn
- Fallback: KuchikiRenji/Empirical-Influence-Function for TracIn
- Justification: Official implementations ensure correct mathematical operations for fair comparison

### Code Analysis (Serena MCP)

Not performed - official implementations from Exa search are well-documented and provide clear APIs. Code is sufficiently modular for integration.

---

## Experiment Specification

### Dataset

**Name:** CIFAR-10 (standard benchmark, used in TRAK examples)
**Type:** standard
**Source:** torchvision.datasets.CIFAR10
**Statistics:** 50,000 train / 10,000 test images, 10 classes, 32x32 RGB

**Contrastive Probes:** 1000 pairs per mode (Memorization, Feature Transfer, Spurious Association)
- **Memorization probes:** Near-duplicate train-test pairs
- **Feature transfer probes:** Same-class pairs with different visual features
- **Spurious probes:** Pairs sharing spurious correlation (e.g., background)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `torchvision.datasets.CIFAR10`
- Code:
  ```python
  from torchvision.datasets import CIFAR10
  from torchvision import transforms
  
  transform = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
  ])
  train_dataset = CIFAR10(root='./data', train=True, download=True, transform=transform)
  test_dataset = CIFAR10(root='./data', train=False, download=True, transform=transform)
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-18 (pretrained on ImageNet, fine-tuned on CIFAR-10)
**Configuration:** 
- Output classes: 10
- Final layer replaced for CIFAR-10

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `torchvision.models.resnet18`
- Code:
  ```python
  import torch
  import torchvision.models as models
  
  model = models.resnet18(pretrained=True)
  model.fc = torch.nn.Linear(model.fc.in_features, 10)  # CIFAR-10 classes
  ```

#### Proposed Model

**Architecture:** Baseline + Attribution Sensitivity Analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: Attribution Method Comparison
# Compare influence scores from 3 attribution methods

import torch
from trak import TRAKer
from kronfluence.analyzer import Analyzer, prepare_model
from src.IF import TracIn  # From Empirical-Influence-Function

def compute_attribution_profiles(model, train_loader, test_loader, probes, checkpoints):
    """
    Compute influence scores using 3 mathematically distinct methods.
    
    Args:
        model: Trained model (ResNet-18)
        train_loader: Training data
        test_loader: Test data with mode labels
        probes: Dict[mode_name -> List[probe_pairs]]
        checkpoints: List of training checkpoints for TracIn
    
    Returns:
        Dict[method -> Dict[mode -> scores]]  # Shape: (num_probes,)
    """
    results = {}
    
    # Method 1: TRAK (gradient projection)
    traker = TRAKer(model=model, task='image_classification', 
                    train_set_size=len(train_loader.dataset), proj_dim=2048)
    # ... featurize and score
    results['trak'] = compute_mode_scores(traker, probes)
    
    # Method 2: TracIn (checkpoint proximity)
    tracin = TracIn(dl_train=train_loader, model=model,
                    criterion=torch.nn.CrossEntropyLoss(reduction="none"))
    results['tracin'] = compute_mode_scores_tracin(tracin, probes, checkpoints)
    
    # Method 3: Kronfluence (K-FAC)
    analyzer = Analyzer(analysis_name="kron", model=prepare_model(model, task), task=task)
    analyzer.fit_all_factors(factors_name="factors", dataset=train_loader.dataset)
    results['kronfluence'] = compute_mode_scores_kron(analyzer, probes)
    
    return results

# Integration: Run after model training, before evaluation
```

### Training Protocol

**Model Training (Baseline):**
- **Optimizer:** SGD (momentum=0.9, weight_decay=5e-4)
- **Learning Rate:** 0.1 with cosine annealing
- **Batch Size:** 128
- **Epochs:** 200
- **Loss:** CrossEntropyLoss
- **Checkpoints:** Save every 20 epochs (for TracIn)

**Attribution Computation:**
- Compute influence for 1000 probes per mode (3 modes = 3000 probes)
- Each probe: pair of (train_example, test_example)
- Run all 3 methods on same probes for fair comparison

**Sources:** TRAK paper defaults, Kronfluence LLM paper recommendations

### Evaluation

**Primary Metrics:**
- Mode sensitivity scores per method: mean influence score per mode
- Method x Mode interaction matrix (3x3)

**Success Criteria (MECHANISM hypothesis):**
- Proposed: Different methods show different mode sensitivity patterns
- Baseline comparison: Methods produce identical patterns (null hypothesis)
- Success: Observable pattern differences between methods

**Expected Baseline Performance:**
- Random attribution: No mode differentiation
- Methods should show systematic differences in mode rankings

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: influence score comparison
- Library: scipy.stats, numpy
- Code:
  ```python
  import numpy as np
  from scipy import stats
  
  # Compare mode sensitivities across methods
  def compute_mode_sensitivity(scores, mode_labels):
      """Mean influence score for each mode."""
      return {mode: np.mean(scores[mode_labels == mode]) for mode in ['mem', 'transfer', 'spurious']}
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Method x Mode heatmap showing sensitivity patterns

#### Additional Figures (LLM Autonomous)
- Mode sensitivity radar chart per method
- Influence score distributions per mode
- Method correlation matrix

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions:**
- mechanism_exists: True (3 distinct attribution methods with different math)
- mechanism_isolatable: True (each method runs independently)
- baseline_measurable: True (random baseline provides null comparison)

**Architecture Compatibility:**
- TRAK: Supports any PyTorch model via gradient hooks
- TracIn: Requires checkpoint access
- Kronfluence: Requires nn.Linear and nn.Conv2d layers (ResNet-18 compatible)

**Activation Indicators:**
- mechanism_log_message: "Attribution scores computed: {method} on {mode}"
- tensor_shape_change: Influence scores shape = (num_probes,)
- metric_delta_expected: Mode rankings differ across methods

**Verification Code:**
```python
def verify_mechanism_active(results):
    """Verify methods produce different mode sensitivity patterns."""
    # Check 1: Non-zero scores
    for method, scores in results.items():
        assert np.std(scores) > 0, f"{method} produces constant scores"
    
    # Check 2: Methods differ
    trak_rank = rank_modes(results['trak'])
    tracin_rank = rank_modes(results['tracin'])
    kron_rank = rank_modes(results['kronfluence'])
    
    # Success: At least one method has different ranking
    return (trak_rank != tracin_rank) or (tracin_rank != kron_rank)
```

**Hypothesis Support:**
- threshold: At least 2 methods show different mode sensitivity rankings
- metric: Mode ranking order per method

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 3 methods
2. Methods produce non-trivial influence scores (variance > 0)
3. At least one method shows different mode sensitivity pattern than others

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Limited direct results for attribution methods. Used for general influence function context.

### B. GitHub Implementations (Exa)

**Repository 1**: MadryLab/trak
- **URL**: https://github.com/MadryLab/trak
- **Query**: "TRAK training data attribution MadryLab official implementation PyTorch"
- **Used For**: TRAK API and implementation details

**Repository 2**: pytorch/captum + KuchikiRenji/Empirical-Influence-Function
- **URLs**: https://github.com/pytorch/captum, https://github.com/KuchikiRenji/Empirical-Influence-Function
- **Query**: "TracIn influence functions checkpoint gradient PyTorch implementation"
- **Used For**: TracIn API and formula verification

**Repository 3**: pomonam/kronfluence
- **URL**: https://github.com/pomonam/kronfluence
- **Query**: "Kronfluence K-FAC influence functions LLM implementation"
- **Used For**: Kronfluence API and LLM scaling patterns

### C. Papers Referenced

1. Park et al. (2023). "TRAK: Attributing Model Behavior at Scale." arXiv:2303.14186
2. Pruthi et al. (2020). "TracIn: A Simple Method for Estimating Training Data Influence." NeurIPS 2020
3. Grosse et al. (2023). "Studying Large Language Model Generalization with Influence Functions." arXiv:2308.03296

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| TRAK implementation | GitHub | MadryLab/trak |
| TracIn implementation | GitHub | pytorch/captum |
| Kronfluence implementation | GitHub | pomonam/kronfluence |
| Dataset (CIFAR-10) | Standard | torchvision |
| Model (ResNet-18) | Standard | torchvision |
| Training protocol | Research | TRAK paper defaults |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C experiment design started
- 2026-08-24: Exa search completed (3 official repositories found)
- 2026-08-24: Experiment specification synthesized
- 2026-08-24: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
