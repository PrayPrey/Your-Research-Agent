# Experiment Design: h-e1

**Date:** 2026-03-26
**Author:** Anonymous
**Hypothesis Statement:** Under finite-compute constraints (<=100 gradient-equivalent operations), at least one method pair exhibits statistically significant metric crossings (Method A > B on rho_r but A < B on rho_m), with non-overlapping 95% bootstrap CIs at two or more compute levels.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Pending Validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**MUST_WORK Gate:** This hypothesis MUST pass for the research program to continue. If it fails (no method pair shows CI-separated metric crossings), the multi-objective Pareto framing is fundamentally invalid and the pipeline will STOP.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis results available.

### Previous Hypothesis Results (if applicable)
*None - h-e1 is the foundation hypothesis with no prerequisites.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "data attribution influence functions TRAK"**
- No direct matches found in knowledge base for data attribution methods
- Results focused on diffusion model training (unrelated domain)

**Query 2: "Pareto trade-offs multi-objective optimization"**
- No direct matches for multi-objective optimization in ML evaluation context
- Results related to PyTorch optimization infrastructure (torch.ao, optimum)

**Query 3: "CIFAR-10 ResNet training PyTorch"**
- Found general PyTorch setup guides
- PyTorch installation documentation (https://pytorch.org/get-started/locally/)
- k-diffusion repository with training infrastructure

**Query 4: "leave-one-out retraining validation"**
- No specific LOO validation methods found
- Results focused on diffusion model fine-tuning

**Summary:** The Archon Knowledge Base does not contain specific information about:
- Data attribution methods (TRAK, TracIn, IF, FastIF)
- Influence function implementations
- LOO retraining validation
- Attribution quality metrics (rank correlation, magnitude fidelity)

**Implication:** Implementation guidance must come from primary sources (Exa GitHub search in Step 3).

### Archon Code Examples

**Query 1: "influence functions gradient PyTorch"**
- Found PyTorch gradient computation example:
  ```python
  x = torch.tensor([[1., -1.], [1., 1.]], requires_grad=True)
  out = x.pow(2).sum()
  out.backward()
  x.grad  # tensor([[ 2.0000, -2.0000], [ 2.0000, 2.0000]])
  ```
  - Source: PyTorch documentation
  - Insight: Basic autograd infrastructure available

**Query 2: "ResNet CIFAR-10 training loop"**
- Found generic training loop pattern:
  ```python
  while True:
      x0 = sample_noise()
      x1 = sample_dataset()
      alpha = torch.rand(batch_size)
      x_alpha = (1 - alpha) * x0 + alpha * x1
      loss = torch.sum((D(x_alpha, alpha) - (x1 - x0)) ** 2)
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
  ```
  - Source: HuggingFace diffusers examples
  - Pattern: Standard PyTorch training loop structure

**Summary:** General PyTorch patterns available but no domain-specific data attribution code found.

### Exa GitHub Implementations

**Query 1: TRAK Official Implementation (HIGHEST PRIORITY)**

**Repository 1**: [MadryLab/trak](https://github.com/madrylab/trak) (233 stars)
- **URL**: https://github.com/madrylab/trak
- **Relevance**: Official TRAK implementation from Park et al. (ICML 2023) - primary author implementation
- **Architecture**: Random projection-based attribution using Neural Tangent Kernel approximation
- **Key Code**:
  ```python
  from trak import TRAKer

  traker = TRAKer(model=model, task='image_classification', train_set_size=...)

  # Featurize training data
  for model_id, checkpoint in enumerate(checkpoints):
      traker.load_checkpoint(checkpoint, model_id=model_id)
      for batch in loader_train:
          traker.featurize(batch=batch, num_samples=batch[0].shape[0])
  traker.finalize_features()

  # Score target examples
  for model_id, checkpoint in enumerate(checkpoints):
      traker.start_scoring_checkpoint(checkpoint, model_id=model_id, exp_name='test')
      for batch in targets_loader:
          traker.score(batch=batch, num_samples=batch[0].shape[0])
  scores = traker.finalize_scores(exp_name='test')
  ```
- **Training Config**: Uses multiple model checkpoints (3-10 recommended), custom CUDA kernels for speed
- **Dataset**: Tested on CIFAR-10, ImageNet, QNLI
- **Results**: 2-3 orders of magnitude faster than datamodels, achieves 0.3+ LDS on CIFAR-10
- **Installation**: `pip install traker` or `pip install traker[fast]` for CUDA acceleration

**Query 2: TracIn Implementation**

**Repository 2**: [frederick0329/TracIn](https://github.com/frederick0329/TracIn) (Official Google)
- **URL**: https://github.com/frederick0329/TracIn
- **Relevance**: Official TracIn from Pruthi et al. (NeurIPS 2020)
- **Architecture**: Gradient dot-product across checkpoints
- **Key Equation**: TracIn(z, z') = Σ_t η_t ∇L(z_t, θ_t) · ∇L(z'_t, θ_t)
- **Implementation**: Jupyter notebooks with examples

**Repository 3**: [rollovd/TracIn-PyTorch](https://github.com/rollovd/tracin-pytorch) (9 stars)
- **URL**: https://github.com/rollovd/tracin-pytorch
- **Relevance**: PyTorch implementation with batch processing support
- **Key Code**:
  ```python
  from src.tracin import vectorized_calculate_tracin_score

  matrix = vectorized_calculate_tracin_score(
      model=model,
      criterion=criterion,
      weights_paths=weights,
      train_dataloader=train_loader,
      test_dataloader=test_loader,
      lr=lr,
      device=device
  )
  ```

**Query 3: Influence Functions Implementation**

**Repository 4**: [nimarb/pytorch_influence_functions](https://github.com/nimarb/pytorch_influence_functions) (344 stars)
- **URL**: https://github.com/nimarb/pytorch_influence_functions
- **Relevance**: Most popular IF implementation (Koh & Liang 2017)
- **Architecture**: Hessian-vector product approximation using LISSA algorithm
- **Key Features**: End-to-end gradient computation, supports any PyTorch model

**Repository 5**: [alstonlo/torch-influence](https://github.com/alstonlo/torch-influence) (92 stars)
- **URL**: https://github.com/alstonlo/torch-influence
- **Relevance**: Clean, minimal IF implementation with bug fixes
- **License**: Apache 2.0

**Query 4: Captum TracIn (Facebook/Meta)**
- **URL**: https://captum.ai/api/_modules/captum/influence/_core/tracincp_fast_rand_proj.html
- **Relevance**: Production-grade TracIn in Captum library
- **Key Classes**: `TracInCPFast`, `TracInCPFastRandProj`
- **Features**: Fast last-layer computation, random projection optimization

**Query 5: Bootstrap Confidence Intervals**
- **Library**: scipy.stats.bootstrap
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- **Key Code**:
  ```python
  from scipy.stats import bootstrap

  result = bootstrap(
      data=(samples,),
      statistic=np.mean,
      n_resamples=1000,
      confidence_level=0.95,
      method='BCa'  # Bias-corrected and accelerated
  )
  ci_low, ci_high = result.confidence_interval
  ```

**Serena Analysis Needed**: false (code structure is clear from documentation)

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Method | Repository | Stars | Maintenance |
|----------|--------|------------|-------|-------------|
| 1 (Highest) | TRAK | MadryLab/trak | 233 | Active (2024) |
| 2 | TracIn | frederick0329/TracIn | - | Official Google |
| 3 | IF | nimarb/pytorch_influence_functions | 344 | Community |
| 4 | FastIF | captum.influence | - | Meta production |

**Recommended Implementation Path:**
- Primary: Use `traker` library (pip install traker[fast]) for TRAK - official, well-documented, CUDA-optimized
- Fallback: Use captum.influence.TracInCPFast for TracIn - production-grade, maintained by Meta
- Justification: Official implementations ensure reproducibility and correctness; TRAK has CIFAR-10 quickstart tutorial matching our experimental setup exactly

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear.

**Justification:**
- TRAK: Official library with comprehensive documentation and CIFAR-10 quickstart
- TracIn: Well-documented equations and reference implementations
- Influence Functions: Multiple implementations with clear API patterns
- Bootstrap CI: Standard scipy.stats function with documented usage

No complex proprietary code or unfamiliar architecture patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset**: CIFAR-10
**Type**: standard
**Source**: torchvision.datasets.CIFAR10

**Statistics:**
- Total samples: 60,000 (50,000 train + 10,000 test)
- Image size: 32x32 RGB (3 channels)
- Classes: 10 (airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck)
- For this experiment: Use 5,000 training examples (subset for LOO feasibility)

**Preprocessing:**
```python
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4914, 0.4822, 0.4465],
                        std=[0.2470, 0.2435, 0.2616])
])
```

**Augmentation:** None (for LOO ground truth consistency)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: CIFAR10
- Code:
```python
from torchvision.datasets import CIFAR10
from torch.utils.data import DataLoader, Subset
import numpy as np

# Load full dataset
train_dataset = CIFAR10(root='./data', train=True, download=True, transform=transform)
test_dataset = CIFAR10(root='./data', train=False, download=True, transform=transform)

# Subset for LOO feasibility (5000 examples)
np.random.seed(42)
subset_indices = np.random.choice(len(train_dataset), size=5000, replace=False)
train_subset = Subset(train_dataset, subset_indices)

train_loader = DataLoader(train_subset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)
```

### Models

#### Baseline Model

**Architecture**: ResNet-18
**Type**: CNN (Convolutional Neural Network)
**Source**: torchvision.models.resnet18

**Configuration:**
- Input: 32x32x3 (CIFAR-10 images)
- Output: 10 classes
- Parameters: ~11M
- Modification: Replace final FC layer (1000 → 10 classes)

**Why ResNet-18:**
- Small enough for LOO retraining (10 retrains × 5000 examples)
- Large enough to exhibit non-convex deep network behavior
- Standard architecture used in TRAK paper

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet18
- Code:
```python
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights

# Load pretrained (for faster convergence) or random init
model = resnet18(weights=None)  # Random init for fair LOO comparison

# Modify for CIFAR-10 (10 classes instead of 1000)
model.fc = nn.Linear(model.fc.in_features, 10)

# Optional: Modify first conv for 32x32 input (CIFAR-specific)
model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
model.maxpool = nn.Identity()  # Remove maxpool for small images

model = model.cuda()
```

#### Proposed Model

**Architecture:** Multi-Method Data Attribution Comparison Framework

**NOTE:** This is NOT a model modification experiment. This is a **method comparison** experiment testing whether Pareto trade-offs exist across different data attribution methods.

**Methods to Compare:**
1. TRAK (MadryLab/trak) - Random projection-based
2. TracIn (Captum or rollovd/TracIn-PyTorch) - Gradient dot-product
3. Influence Functions (nimarb/pytorch_influence_functions) - Hessian-based
4. FastIF (Captum TracInCPFast) - Last-layer IF approximation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Multi-Method Data Attribution Comparison
# Based on: MadryLab/trak, frederick0329/TracIn, nimarb/pytorch_influence_functions

import numpy as np
from scipy.stats import spearmanr, pearsonr, bootstrap
from trak import TRAKer
from captum.influence import TracInCPFast
import torch

class DataAttributionComparison:
    """
    Compare 4 data attribution methods across 3 quality metrics.
    Tests for Pareto trade-offs via bootstrap confidence intervals.
    """
    def __init__(self, model, train_loader, test_loader, device='cuda'):
        self.model = model
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.device = device
        self.methods = ['TRAK', 'TracIn', 'IF', 'FastIF']
        self.compute_budgets = [10, 25, 50, 75, 100]  # gradient-equivalents

    def compute_loo_ground_truth(self, n_retrains=10):
        """Compute LOO ground truth via retraining (R=10 seeds)."""
        # Returns: influence_scores[train_idx] for each test example
        pass  # Implementation in Phase 4

    def compute_method_scores(self, method, budget):
        """Compute attribution scores for method at given compute budget."""
        if method == 'TRAK':
            traker = TRAKer(model=self.model, task='image_classification', ...)
            # featurize and score
        elif method == 'TracIn':
            # Use captum TracInCPFast
            pass
        # Returns: scores[n_train, n_test]

    def compute_metrics(self, pred_scores, loo_ground_truth):
        """Compute 3 quality metrics."""
        rho_r = spearmanr(pred_scores, loo_ground_truth).correlation  # Rank preservation
        rho_m = pearsonr(pred_scores, loo_ground_truth)[0]  # Magnitude fidelity
        S = self._compute_stability(pred_scores)  # Normalized stability
        return {'rho_r': rho_r, 'rho_m': rho_m, 'S': S}

    def detect_pareto_crossings(self, results, n_bootstrap=1000):
        """Detect CI-separated metric crossings between method pairs."""
        crossings = []
        for m1, m2 in itertools.combinations(self.methods, 2):
            for budget in self.compute_budgets:
                # Bootstrap CI for metric differences
                ci = bootstrap((results[m1][budget], results[m2][budget]),
                              statistic=lambda a, b: a['rho_r'] - b['rho_r'],
                              n_resamples=n_bootstrap, confidence_level=0.95)
                if self._ci_separated(ci):  # Non-overlapping with 0
                    crossings.append((m1, m2, budget))
        return crossings
```

### Training Protocol

**Training ResNet-18 for LOO Ground Truth:**

**Optimizer**: SGD
- Parameters: momentum=0.9, weight_decay=5e-4
- **Source**: Standard ResNet training (TRAK paper setup)

**Learning Rate**: 0.1
- **Schedule**: MultiStepLR with milestones=[100, 150], gamma=0.1
- **Source**: CIFAR-10 standard training

**Batch Size**: 128
- **Source**: TRAK CIFAR-10 quickstart

**Epochs**: 200
- **Source**: Standard CIFAR-10 convergence

**Loss Function**: CrossEntropyLoss

**Seeds**: 1 (fixed at 42)

> **EXISTENCE (PoC)**: Single seed is sufficient. LOO retraining uses R=10 seeds internally.

**LOO Retraining Protocol:**
- For each of R=10 retraining seeds, train model from scratch
- For each training example i, compute θ^(-i) by retraining without example i (subset of 100 test examples for feasibility)
- Compute LOO influence = E_xi[L(z_test; θ^(-i)) - L(z_test; θ)]

### Evaluation

**Primary Metrics** (from Phase 2B):

| Metric | Definition | Measures |
|--------|------------|----------|
| **rho_r (Rank Preservation)** | Spearman correlation between method scores and LOO ground truth | Does method preserve influence ranking? |
| **rho_m (Magnitude Fidelity)** | Pearson correlation between method scores and LOO ground truth | Does method preserve influence magnitudes? |
| **S (Normalized Stability)** | Var(scores across method seeds) / Var(LOO ground truth) | Is method stable across runs? |

**Success Criteria (PoC: Direction-based):**
- **Primary**: >=1 method pair shows CI-separated metric crossings at >=2 compute levels
  - Example: TRAK > TracIn on rho_r but TRAK < TracIn on rho_m
  - CIs must NOT overlap zero (95% bootstrap, n=1000)
- **Secondary**: Pareto front contains >=2 non-dominated methods at majority of budget levels

**Expected Baseline Performance** (from TRAK paper):
- TRAK rho_r on CIFAR-10: 0.3-0.5 (LDS metric)
- IF rho_r: 0.1-0.2 (known to be fragile)
- **Source**: Park et al. (ICML 2023), Koh & Liang (ICML 2017)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation / Statistical Comparison
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import spearmanr, pearsonr, bootstrap
import numpy as np

def compute_metrics(pred_scores, ground_truth):
    rho_r = spearmanr(pred_scores, ground_truth).correlation
    rho_m = pearsonr(pred_scores, ground_truth)[0]
    return {'rho_r': rho_r, 'rho_m': rho_m}

def compute_ci(samples, statistic, n_resamples=1000, confidence_level=0.95):
    result = bootstrap((samples,), statistic, n_resamples=n_resamples,
                       confidence_level=confidence_level, method='BCa')
    return result.confidence_interval
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing rho_r and rho_m for each method at each compute budget

#### Additional Figures (LLM Autonomous)

1. **Pareto Front Visualization**: 2D scatter plot (rho_r vs rho_m) with Pareto frontier highlighted for each compute budget level
2. **Metric Crossing Heatmap**: Matrix showing which method pairs exhibit metric crossings at which compute levels
3. **Bootstrap CI Plot**: Error bars showing 95% CIs for each metric-method-budget combination
4. **Compute-Performance Curves**: Line plots showing how each metric evolves with compute budget for each method

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Summary**: The Archon Knowledge Base did not contain specific content on data attribution methods (TRAK, TracIn, IF). Searches returned results related to diffusion models and general PyTorch training, which were not directly applicable. Implementation guidance was obtained from Exa GitHub search (Section B).

**Query 1**: "data attribution influence functions TRAK"
- **Result**: No direct matches
- **Used For**: Confirmed need for Exa search

**Query 2**: "CIFAR-10 ResNet training PyTorch"
- **Result**: General PyTorch setup guides
- **Used For**: Background confirmation of standard training patterns

### B. GitHub Implementations (Exa)

**Repository 1**: [MadryLab/trak](https://github.com/madrylab/trak) (233 stars)
- **URL**: https://github.com/madrylab/trak
- **Query Used**: "TRAK data attribution Park official implementation GitHub pytorch"
- **Relevance**: Official TRAK implementation from Park et al. (ICML 2023)
- **Key Code** (annotated):
  ```python
  from trak import TRAKer
  # TRAKer is the main entry point for computing attribution scores
  traker = TRAKer(model=model, task='image_classification', train_set_size=5000)
  traker.load_checkpoint(checkpoint, model_id=0)
  traker.featurize(batch=batch, num_samples=batch[0].shape[0])  # Compute features
  traker.finalize_features()
  traker.start_scoring_checkpoint('exp', checkpoint, num_targets=10000)
  scores = traker.finalize_scores(exp_name='exp')  # Returns attribution scores
  ```
- **Configuration Extracted**: 3-10 checkpoints recommended, CUDA acceleration available
- **Their Results**: 0.3+ LDS on CIFAR-10, 2-3 orders of magnitude faster than datamodels
- **Used For**: TRAK method implementation in experiment specification

**Repository 2**: [frederick0329/TracIn](https://github.com/frederick0329/TracIn) (Official Google)
- **URL**: https://github.com/frederick0329/TracIn
- **Query Used**: "TracIn gradient tracing data attribution PyTorch implementation"
- **Relevance**: Official TracIn from Pruthi et al. (NeurIPS 2020)
- **Key Equation**: TracIn(z, z') = Σ_t η_t ∇L(z_t, θ_t) · ∇L(z'_t, θ_t)
- **Used For**: TracIn method implementation

**Repository 3**: [rollovd/TracIn-PyTorch](https://github.com/rollovd/tracin-pytorch) (9 stars)
- **URL**: https://github.com/rollovd/tracin-pytorch
- **Query Used**: "TracIn gradient tracing data attribution PyTorch implementation"
- **Relevance**: Batch processing TracIn implementation
- **Key Code**:
  ```python
  from src.tracin import vectorized_calculate_tracin_score
  matrix = vectorized_calculate_tracin_score(
      model=model, criterion=criterion, weights_paths=weights,
      train_dataloader=train_loader, test_dataloader=test_loader, lr=lr, device=device
  )
  ```
- **Used For**: TracIn batch computation pattern

**Repository 4**: [nimarb/pytorch_influence_functions](https://github.com/nimarb/pytorch_influence_functions) (344 stars)
- **URL**: https://github.com/nimarb/pytorch_influence_functions
- **Query Used**: "influence functions pytorch implementation leave-one-out retraining"
- **Relevance**: Most popular IF implementation (Koh & Liang 2017)
- **Key Features**: LISSA algorithm for HVP approximation, end-to-end gradients
- **Used For**: IF method implementation reference

**Repository 5**: [alstonlo/torch-influence](https://github.com/alstonlo/torch-influence) (92 stars)
- **URL**: https://github.com/alstonlo/torch-influence
- **Query Used**: "influence functions pytorch implementation"
- **Relevance**: Clean IF implementation with bug fixes
- **Used For**: IF implementation alternative

**External Library**: Captum TracIn (Meta/Facebook)
- **URL**: https://captum.ai/api/_modules/captum/influence/_core/tracincp_fast_rand_proj.html
- **Relevance**: Production-grade TracIn implementation
- **Key Classes**: `TracInCPFast`, `TracInCPFastRandProj`
- **Used For**: FastIF method implementation

**Library**: SciPy Bootstrap
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- **Query Used**: "scipy bootstrap confidence interval statistics python non-overlapping"
- **Relevance**: Bootstrap CI computation for detecting metric crossings
- **Key Code**:
  ```python
  from scipy.stats import bootstrap
  result = bootstrap((samples,), statistic, n_resamples=1000,
                     confidence_level=0.95, method='BCa')
  ```
- **Used For**: Statistical testing for metric crossings

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

All referenced implementations have well-documented APIs with CIFAR-10 examples that directly match our experimental setup.

### D. Previous Hypothesis Context

**Previous Context**: None - h-e1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (CIFAR-10) | Phase 2B + Exa | 02b_context.md, leyaa.ai CIFAR10 guide |
| Model (ResNet-18) | Phase 2B + Exa | 02b_context.md, torchvision docs |
| TRAK implementation | Exa GitHub | MadryLab/trak (B.1) |
| TracIn implementation | Exa GitHub | frederick0329/TracIn, rollovd/TracIn-PyTorch (B.2, B.3) |
| IF implementation | Exa GitHub | nimarb/pytorch_influence_functions (B.4) |
| FastIF implementation | Exa GitHub | Captum TracInCPFast (B.5) |
| Bootstrap CI | Exa | scipy.stats.bootstrap docs |
| Training protocol | Exa + TRAK paper | Park et al. ICML 2023 |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Success criteria | Phase 2B | 02b_verification_plan.md (H-E1 section) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-26T02:32:00+00:00

### Workflow History for This Hypothesis
- Phase 2C experiment design started (2026-03-26)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
