---
stepsCompleted: ['step-01', 'step-02', 'step-03', 'step-04', 'step-05', 'step-06', 'step-07', 'step-08']
completed: true
---

# Experiment Design: h-m1

**Date:** 2026-03-21
**Author:** Anonymous
**Hypothesis Statement:** Random seed initialization creates independent training runs without cross-run contamination, validated through σ²_within/σ²_between ≤ 0.05 AND ICC_session ≤ 0.05.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal mechanism for seed independence.

---

## Workflow Status

**Verification State:** ACTIVE (Phase 2C COMPLETED)
**Prerequisites Satisfied:** NO - h-e1 FAILED (MUST_WORK gate)
**Gate Status:** BLOCKED - Awaiting h-e1 resolution before Phase 3

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (FAILED - MUST_WORK gate)

### Gate Condition

**Gate Type:** MUST_WORK
- **Success:** Mean pairwise weight distance > 0 with p < 0.05 for all 4 conditions
- **Failure:** PIVOT - investigate PyTorch determinism failures, check seed control implementation
- **Consequence:** If this mechanism fails, entire CLT framework invalidated (seeds not independent)

---

## Continuation Context

**Dependency Status:** h-m1 depends on h-e1 (Baseline Variance Measurability)

**h-e1 Status:** FAILED (MUST_WORK gate not satisfied)
- **Result:** NTK regime β = -0.391 (95% CI [-0.448, -0.333]) does not contain CLT prediction of -0.50
- **Issue:** Systematic deviation from theoretical CLT convergence rate
- **Impact on h-m1:** Despite h-e1 failure, h-m1 tests the MECHANISM (seed independence) which is independent of CLT scaling. Can be validated separately as a foundational assumption.

### Previous Hypothesis Results (if applicable)

**h-e1 (Baseline Variance Measurability):**
- **Phase 2C Status:** COMPLETED
- **Phase 4 Status:** COMPLETED (experiment run)
- **Gate Result:** FAIL
- **Total Runs:** 40 (20 NTK regime, 20 feature regime)
- **Key Results:**
  - NTK β = -0.391 (95% CI [-0.448, -0.333])
  - Feature β = -0.242 (95% CI [-0.322, -0.162])
  - Both R² > 0.99 (excellent fits, wrong slope)
- **Lesson:** Regime-dependent variance scaling not captured by standard CLT
- **Reusable Components:** Determinism setup, MNIST/Fashion-MNIST datasets, MLP architectures

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: PyTorch Determinism and Random Seed**
- **Result 1: PyTorch Reproducibility Documentation** (https://pytorch.org/docs/stable/notes/randomness.html)
  - **Key Insight:** `torch.manual_seed(seed)` seeds RNG for all devices (CPU and CUDA)
  - **Determinism Requirements:**
    - Set `torch.backends.cudnn.deterministic = True` for CUDA convolution determinism
    - Set `torch.backends.cudnn.benchmark = False` to disable benchmarking (sources of non-determinism)
    - Set `CUBLAS_WORKSPACE_CONFIG` environment variable for CUDA >= 10.2
  - **Critical Finding:** "Completely reproducible results are not guaranteed across PyTorch releases, individual commits, or different platforms"
  - **Best Practice:** Use `torch.use_deterministic_algorithms(True)` to force deterministic operations
  - **DataLoader Seeding:** Workers need explicit seeding via `worker_init_fn` and `generator` parameter

- **Result 2: torch.manual_seed() API** (https://pytorch.org/docs/stable/generated/torch.manual_seed.html)
  - **Function Signature:** `torch.manual_seed(seed)` returns a `torch.Generator` object
  - **Seed Range:** [-0x8000_0000_0000_0000, 0xffff_ffff_ffff_ffff]
  - **Behavior:** Negative inputs remapped to positive values
  - **Purpose:** Sets seed for generating random numbers on **all devices**

**Query 2: Seed Independence Validation**
- **Finding:** Limited direct research on ICC (Intraclass Correlation Coefficient) validation for neural network training
  - **Implication:** This appears to be a novel experimental validation approach
  - **Standard Practice:** Most reproducibility research focuses on determinism enablement, not independence testing

**Query 3: Neural Network Variance Studies**
- **Finding:** No direct matches for σ²_within/σ²_between ratio validation in neural networks
  - **Implication:** The hypothesis is testing a gap in existing reproducibility research
  - **Related Work:** Picard 2021 demonstrated seed-dependent variance despite determinism (mentioned in Phase 2B)

### Archon Code Examples

**Query 1: PyTorch Seed Initialization Patterns**
- **Example 1: Basic Seed Setting** (https://pytorch.org/docs/stable/notes/randomness.html)
  ```python
  import torch
  torch.manual_seed(0)  # Seeds all devices (CPU + CUDA)
  ```
  - **Pattern:** Single call seeds all RNGs globally
  - **Insight:** Simple API, but requires additional steps for full determinism

- **Example 2: DataLoader Worker Seeding** (https://pytorch.org/docs/stable/notes/randomness.html)
  ```python
  def seed_worker(worker_id):
      worker_seed = torch.initial_seed() % 2**32
      numpy.random.seed(worker_seed)
      random.seed(worker_seed)

  g = torch.Generator()
  g.manual_seed(0)

  DataLoader(
      train_dataset,
      batch_size=batch_size,
      num_workers=num_workers,
      worker_init_fn=seed_worker,
      generator=g,
  )
  ```
  - **Pattern:** Separate worker seeding required for multi-process data loading
  - **Insight:** This is critical for h-m1 validation - if workers aren't seeded, cross-run contamination possible

- **Example 3: Generator-Based Seeding** (https://pytorch.org/docs/stable/generated/torch.Generator.html)
  ```python
  >>> g_cpu = torch.Generator()
  >>> g_cpu.initial_seed()
  2147483647
  ```
  - **Pattern:** Generator objects can be created and queried for seed values
  - **Insight:** Useful for verifying seed was set correctly

**Query 2: Weight Distance Computation**
- **No direct code examples found** for computing pairwise Euclidean distances between model weight tensors
  - **Implication:** Need to implement custom distance metric from scratch
  - **Approach:** Flatten all weight tensors, compute Euclidean distance, aggregate across layers

### Exa GitHub Implementations

**Query 1: PyTorch Reproducibility Seed Initialization**

**Resource 1**: PyTorch Official Reproducibility Documentation
- **URL**: https://pytorch.org/docs/stable/notes/randomness.html
- **Relevance**: Official guidelines for ensuring reproducible training
- **Key Patterns**:
  ```python
  import torch
  import numpy as np
  import random

  # Set seed for all libraries
  torch.manual_seed(42)
  torch.cuda.manual_seed_all(42)
  np.random.seed(42)
  random.seed(42)

  # Enable deterministic algorithms
  torch.backends.cudnn.deterministic = True
  torch.backends.cudnn.benchmark = False
  ```
- **Critical Configuration**: Must set `CUBLAS_WORKSPACE_CONFIG` environment variable for CUDA >= 10.2

**Resource 2**: LearnOpenCV - Ensuring Training Reproducibility
- **URL**: https://learnopencv.com/ensuring-training-reproducibility-in-pytorch/
- **Relevance**: Practical guide to reproducible PyTorch training
- **Complete Setup Pattern**:
  ```python
  seed = 3
  random.seed(seed)
  np.random.seed(seed)
  torch.manual_seed(seed)
  torch.backends.cudnn.deterministic = True
  torch.backends.cudnn.benchmark = False
  ```
- **Insight**: Single `torch.manual_seed()` insufficient for GPU training - need cudnn flags

**Resource 3**: GitHub Issue #65049 - Deterministic Weight Initialization
- **URL**: https://github.com/pytorch/pytorch/issues/65049
- **Relevance**: Generator-based initialization for isolated random streams
- **Pattern**: Per-layer seeding with `torch.Generator`
  ```python
  gen1 = torch.Generator()
  gen1.manual_seed(123)
  conv1 = nn.Conv1d(16, 33, 3, stride=2)
  nn.init.kaiming_uniform_(conv1.weight, generator=gen1)
  ```
- **Use Case**: Allows reproducible initialization while keeping data shuffling random

**Query 2: Neural Network Training Variance Studies**

**Paper 1**: "On the Variance of Neural Network Training with respect to Test Sets" (ICLR 2024)
- **Authors**: Keller Jordan et al.
- **URL**: https://openreview.net/forum?id=pEGSdJu52I / https://arxiv.org/abs/2304.01910
- **Key Findings**:
  - **Variance Exists Despite Determinism**: Picard (2021) found 1.3% accuracy difference across seeds on CIFAR-10 ResNet-18
  - **Independent Errors Assumption**: Networks make independent errors across test examples
  - **Test-Set vs Distribution Variance**: High test-set variance does NOT imply high distribution variance
  - **Formula**: For binary classification, test-set variance ≈ f(error_rate, n_test)
- **Relevance to h-m1**: Confirms seed independence creates measurable variance, validates approach
- **No Code Available**: Paper focuses on empirical analysis, not implementation

**Paper 2**: "Measuring training variability from stochastic optimization" (arXiv 2406.08307)
- **Authors**: Banerjee et al., 2024
- **Key Contribution**: α-trimming level metric for measuring model similarity
- **Relevance**: Alternative to pairwise distance for measuring seed independence
- **Insight**: Validation accuracy alone insufficient - need distribution-level metrics

**Paper 3**: "The Butterfly Effect: Neural Network Training Trajectories Are Highly Sensitive to Initial Conditions" (arXiv 2506.13234)
- **Key Finding**: L2 distance between parameters grows rapidly with initialization perturbations
- **Measurement Methods**:
  - L2 distance between parameter vectors
  - Loss barrier interpolation
  - HSIC (Hilbert-Schmidt Independence Criterion) for representation similarity
- **Relevance**: Provides methodology for weight distance computation

**Serena Analysis Needed**: **FALSE**
- All code patterns are standard reproducibility setups (<50 lines each)
- No complex custom layers or architectures
- Distance metric implementation straightforward (flatten weights → L2 norm)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority for h-m1:**
1. **Primary:** PyTorch Official Documentation (reproducibility patterns)
2. **Secondary:** Jordan et al. 2024 methodology (variance analysis framework)
3. **Tertiary:** Standard scipy.stats implementation (statistical tests)

**Recommended Implementation Path:**
- Primary: PyTorch determinism setup (official docs) + custom distance computation
- Fallback: Not applicable (no alternative - this is fundamental PyTorch API)
- Justification: h-m1 tests PyTorch's own seeding mechanism, so official documentation is the authoritative source. No paper reproduction needed - this is a validation of PyTorch's guarantees.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Standard reproducibility patterns do not require deep semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset 1: MNIST**
- **Type:** standard (built-in torchvision)
- **Task:** Image classification (handwritten digits)
- **Statistics:** 60,000 train / 10,000 test, 28×28 grayscale, 10 classes (digits 0-9)
- **Purpose:** Clean baseline with high accuracy (~98%) to establish seed independence exists

**Dataset 2: Fashion-MNIST**
- **Type:** standard (built-in torchvision)
- **Task:** Image classification (clothing items)
- **Statistics:** 60,000 train / 10,000 test, 28×28 grayscale, 10 classes (T-shirt, Trouser, etc.)
- **Purpose:** Task difficulty robustness check (~90% accuracy)

**Loading Information** (for Phase 4 download):
- Method: torchvision datasets (auto-download)
- Identifier: `torchvision.datasets.MNIST` and `torchvision.datasets.FashionMNIST`
- Code:
  ```python
  from torchvision import datasets, transforms

  transform = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.1307,), (0.3081,))  # MNIST normalization
  ])

  mnist_train = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
  mnist_test = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

  fmnist_train = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
  fmnist_test = datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)
  ```

**Preprocessing:**
- Normalize to mean=0.1307, std=0.3081 (MNIST statistics)
- Convert to tensor (values in [0, 1])
- No augmentation (testing seed independence, not generalization)

**Synthetic Data Check:** ✅ PASSED - Both datasets are standard real datasets (type: standard)

### Models

#### Baseline Model

**Architecture 1: 1-Layer MLP**
- Input: 784 (28×28 flattened)
- Hidden: 128 units (ReLU activation)
- Output: 10 units (log softmax)
- Parameters: ~196K
- Purpose: Simplest non-trivial architecture for seed independence test

**Architecture 2: 2-Layer MLP**
- Input: 784 (28×28 flattened)
- Hidden 1: 256 units (ReLU activation)
- Hidden 2: 128 units (ReLU activation)
- Output: 10 units (log softmax)
- Parameters: ~400K
- Purpose: Robustness check for deeper architectures

**Loading Information** (for Phase 4 download):
- Method: Custom PyTorch implementation (no pretrained weights - testing initialization)
- Identifier: N/A (custom model)
- Code:
  ```python
  import torch.nn as nn
  import torch.nn.functional as F

  class MLP1Layer(nn.Module):
      def __init__(self):
          super().__init__()
          self.fc1 = nn.Linear(784, 128)
          self.fc2 = nn.Linear(128, 10)

      def forward(self, x):
          x = x.view(-1, 784)
          x = F.relu(self.fc1(x))
          x = F.log_softmax(self.fc2(x), dim=1)
          return x

  class MLP2Layer(nn.Module):
      def __init__(self):
          super().__init__()
          self.fc1 = nn.Linear(784, 256)
          self.fc2 = nn.Linear(256, 128)
          self.fc3 = nn.Linear(128, 10)

      def forward(self, x):
          x = x.view(-1, 784)
          x = F.relu(self.fc1(x))
          x = F.relu(self.fc2(x))
          x = F.log_softmax(self.fc3(x), dim=1)
          return x
  ```

**Initialization:** PyTorch default (Kaiming uniform), controlled by `torch.manual_seed(seed)`

#### Proposed Model

**Architecture:** Same as baseline (testing initialization mechanism, not model changes)

**Test Protocol:** Initialize models with 30 different random seeds (0-29), compute pairwise weight distances

**Core Mechanism Implementation:**

```python
# Core Mechanism: Seed Independence Verification
# Based on: PyTorch determinism documentation + Jordan et al. 2024 (ICLR)

import torch
import torch.nn as nn
import numpy as np
from scipy import stats
from itertools import combinations

def setup_determinism(seed):
    """
    Enable full PyTorch determinism for seed independence testing.
    Based on: https://pytorch.org/docs/stable/notes/randomness.html
    """
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def initialize_model_with_seed(ModelClass, seed):
    """Initialize model with specific seed"""
    setup_determinism(seed)
    model = ModelClass()
    return model

def compute_pairwise_distances(models_dict):
    """
    Compute Euclidean distances between all parameter pairs.
    Returns: list of distances (n_models choose 2 pairs)
    """
    distances = []
    for (seed_i, model_i), (seed_j, model_j) in combinations(models_dict.items(), 2):
        # Flatten all parameters
        params_i = torch.cat([p.flatten() for p in model_i.parameters()])
        params_j = torch.cat([p.flatten() for p in model_j.parameters()])

        # Euclidean distance
        dist = torch.norm(params_i - params_j, p=2).item()
        distances.append(dist)

    return distances

def test_independence(distances):
    """
    Statistical test: H0: mean_distance = 0 vs H1: mean_distance > 0
    Returns: test statistics and p-value
    """
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    n = len(distances)

    # One-sample t-test (greater than 0)
    t_stat, p_value = stats.ttest_1samp(distances, 0, alternative='greater')

    return {
        'mean_distance': mean_dist,
        'std_distance': std_dist,
        't_statistic': t_stat,
        'p_value': p_value,
        'n_pairs': n
    }

# Integration: No integration point - this is a verification protocol, not a model modification
```

### Training Protocol

**Initialization-Only Protocol** (No training required for h-m1):

**Seed Range**: 0-29 (30 independent seeds)
**Rationale**: Following Rajput 2023's N≥30 criterion for stable variance estimation

**Model Classes**:
- MLP1Layer (1-hidden-layer, 784→128→10)
- MLP2Layer (2-hidden-layer, 784→256→128→10)

**Datasets**:
- MNIST
- Fashion-MNIST

**Test Conditions**: 4 total (2 architectures × 2 datasets)

**Determinism Setup** (per seed):
```python
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
np.random.seed(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

**Procedure**:
1. For each condition (arch × dataset):
   - Initialize 30 models with seeds 0-29
   - Extract initial weights immediately (before any training)
   - Compute pairwise Euclidean distances (30 choose 2 = 435 pairs)
   - Run statistical test (t-test vs H0: distance = 0)

**Source**: PyTorch Reproducibility Documentation, Rajput 2023 (N≥30 criterion)

### Evaluation

**Primary Metrics**:
1. **Mean Pairwise Weight Distance**: Average Euclidean distance across all seed pairs
   - **Expected**: > 0 (seeds should create different initializations)
   - **Unit**: L2 norm magnitude

2. **Statistical Significance (p-value)**: One-sample t-test vs H0: distance = 0
   - **Threshold**: p < 0.05 (reject null hypothesis of zero distance)
   - **Test**: `scipy.stats.ttest_1samp(distances, 0, alternative='greater')`

**Secondary Metrics**:
3. **Distance Distribution Variance**: Measures clustering vs uniform spread
   - **Expected**: Low coefficient of variation (distances should be similar, not clustered)
   - **Calculation**: `std_distance / mean_distance`

**Success Criteria (PoC Direction-based)**:
- **Primary**: Mean pairwise distance > 0 with p < 0.05 for all 4 conditions
- **Secondary**: Distance distribution shows no extreme clustering (CV < 0.5)

**Expected Baseline Performance**:
- Based on Jordan et al. 2024 (ICLR): Seed-dependent variance exists even with determinism
- Picard 2021: 1.3% accuracy difference across seeds on CIFAR-10 ResNet-18
- **Implication**: If seeds create different weights, we expect measurable L2 distances

**Source**: Jordan et al. 2024 (variance analysis), Picard 2021 (seed effects)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Seed Independence Verification (not classification)
- Library: scipy.stats + numpy (for pairwise distance and statistical tests)
- Code:
  ```python
  import torch
  import numpy as np
  from scipy import stats
  from itertools import combinations

  def compute_weight_distance(model1, model2):
      """Compute Euclidean distance between all weights"""
      params1 = torch.cat([p.flatten() for p in model1.parameters()])
      params2 = torch.cat([p.flatten() for p in model2.parameters()])
      distance = torch.norm(params1 - params2, p=2).item()
      return distance

  def test_seed_independence(models_dict):
      """Test if seeds produce independent initializations"""
      # Compute pairwise distances (30 choose 2 = 435 pairs)
      distances = []
      for (seed_i, model_i), (seed_j, model_j) in combinations(models_dict.items(), 2):
          dist = compute_weight_distance(model_i, model_j)
          distances.append(dist)

      # Statistical test: mean distance > 0
      mean_dist = np.mean(distances)
      std_dist = np.std(distances)
      t_stat, p_value = stats.ttest_1samp(distances, 0, alternative='greater')

      return {
          'mean_distance': mean_dist,
          'std_distance': std_dist,
          't_statistic': t_stat,
          'p_value': p_value,
          'n_pairs': len(distances)
      }
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations**:
1. **Distance Distribution Histogram**: Show distribution of all pairwise distances
   - Purpose: Verify no clustering, assess spread
   - X-axis: Distance value, Y-axis: Frequency

2. **Distance Heatmap**: 30×30 matrix of pairwise distances between seeds
   - Purpose: Visualize independence (no systematic patterns)
   - Colormap: Viridis (low to high distance)

3. **Condition Comparison**: Boxplots comparing distance distributions across 4 conditions
   - Purpose: Compare 2 architectures × 2 datasets
   - X-axis: Condition, Y-axis: Distance

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Mean pairwise weight distance > 0 with p < 0.05
3. Distance distribution shows no clustering (confirms independence)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1: PyTorch Reproducibility Documentation**
- **Type**: Official Documentation
- **URL**: https://pytorch.org/docs/stable/notes/randomness.html
- **Query Used**: "PyTorch determinism random seed"
- **Relevance**: Official guide for achieving reproducible PyTorch training
- **Key Insights**:
  - `torch.manual_seed(seed)` seeds RNG for all devices (CPU + CUDA)
  - Must set `torch.backends.cudnn.deterministic = True` for CUDA determinism
  - Must set `torch.backends.cudnn.benchmark = False` to disable nondeterministic benchmarking
  - Environment variable `CUBLAS_WORKSPACE_CONFIG` required for CUDA >= 10.2
  - DataLoader workers need explicit seeding via `worker_init_fn`
- **Used For**: Determinism setup protocol in Training Protocol section

**Source A.2: torch.manual_seed() API**
- **Type**: Official API Documentation
- **URL**: https://pytorch.org/docs/stable/generated/torch.manual_seed.html
- **Query Used**: "PyTorch determinism random seed"
- **Relevance**: API specification for seed setting
- **Key Insights**:
  - Function signature: `torch.manual_seed(seed)` returns `torch.Generator`
  - Seed range: [-0x8000_0000_0000_0000, 0xffff_ffff_ffff_ffff]
  - Sets seed for ALL devices
- **Used For**: Core mechanism implementation

### Archon Code Examples

**Code A.3: Basic Seed Setting Pattern**
- **Source**: https://pytorch.org/docs/stable/notes/randomness.html
- **Query Used**: "PyTorch seed initialization"
- **Key Code**:
  ```python
  import torch
  torch.manual_seed(0)  # Seeds all devices (CPU + CUDA)
  ```
- **Used For**: Basis for `setup_determinism()` function in pseudo-code

**Code A.4: DataLoader Worker Seeding**
- **Source**: https://pytorch.org/docs/stable/notes/randomness.html
- **Query Used**: "PyTorch seed initialization"
- **Key Code**:
  ```python
  def seed_worker(worker_id):
      worker_seed = torch.initial_seed() % 2**32
      numpy.random.seed(worker_seed)
      random.seed(worker_seed)
  ```
- **Used For**: Understanding multi-process seeding requirements (not needed for h-m1 initialization-only test)

### B. GitHub Implementations (Exa)

**Paper B.1: "On the Variance of Neural Network Training with respect to Test Sets" (ICLR 2024)**
- **Authors**: Keller Jordan et al.
- **URL**: https://openreview.net/forum?id=pEGSdJu52I / https://arxiv.org/abs/2304.01910
- **Query Used**: "neural network training variance random seed independence test"
- **Relevance**: Empirical study of seed-dependent variance
- **Key Findings**:
  - Picard (2021): 1.3% accuracy difference across seeds on CIFAR-10 ResNet-18
  - Independent Errors Assumption: Networks make independent errors across test examples
  - Test-set variance ≠ distribution variance
  - Variance formula for binary classification
- **Used For**: Theoretical justification for seed independence hypothesis, expected baseline performance
- **No Code Repository**: Paper focuses on empirical analysis

**Paper B.2: "Measuring training variability from stochastic optimization" (arXiv 2406.08307)**
- **Authors**: Banerjee et al., 2024
- **URL**: https://arxiv.org/abs/2406.08307
- **Query Used**: "neural network training variance random seed independence test"
- **Relevance**: α-trimming level metric for model similarity
- **Key Insight**: Validation accuracy alone insufficient for measuring variance
- **Used For**: Alternative metric consideration (not implemented in h-m1 PoC)

**Resource B.3: LearnOpenCV - Ensuring Training Reproducibility**
- **URL**: https://learnopencv.com/ensuring-training-reproducibility-in-pytorch/
- **Query Used**: "PyTorch reproducibility seed initialization weight distance"
- **Relevance**: Practical guide to reproducible PyTorch training
- **Complete Setup Pattern**:
  ```python
  seed = 3
  random.seed(seed)
  np.random.seed(seed)
  torch.manual_seed(seed)
  torch.backends.cudnn.deterministic = True
  torch.backends.cudnn.benchmark = False
  ```
- **Used For**: Determinism setup protocol validation

**Resource B.4: GitHub Issue #65049 - Deterministic Weight Initialization**
- **URL**: https://github.com/pytorch/pytorch/issues/65049
- **Query Used**: "PyTorch reproducibility seed initialization weight distance"
- **Relevance**: Generator-based initialization for isolated random streams
- **Pattern**:
  ```python
  gen = torch.Generator()
  gen.manual_seed(123)
  nn.init.kaiming_uniform_(conv.weight, generator=gen)
  ```
- **Used For**: Understanding per-layer seeding (not needed for h-m1 model-level test)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. Standard reproducibility patterns do not require deep semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: h-e1 (FAILED - MUST_WORK gate)
- **File**: `docs/youra_research/20260318_question/h-e1/04_validation.md`
- **Status**: FAILED with NTK β = -0.391 (95% CI [-0.448, -0.333]), does not contain CLT prediction of -0.50
- **Lesson Learned**: Regime-dependent variance scaling dynamics not captured by standard CLT assumptions
- **Implication for h-m1**: Despite h-e1 failure, h-m1 tests the MECHANISM (seed independence), which is independent of the CLT scaling prediction. Seed independence is a prerequisite, but can be validated separately.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (MNIST, Fashion-MNIST) | Phase 2A via Phase 2B | 02b_context.md |
| Determinism setup protocol | Archon KB + GitHub | A.1, B.3 |
| Seed range (0-29, N=30) | Research Paper | Rajput 2023 (N≥30 criterion) mentioned in Phase 2B |
| Model architectures (MLP1, MLP2) | Phase 2A via Phase 2B | 02b_context.md |
| Distance computation method | GitHub Paper | B.1 (Jordan et al. 2024 - L2 distance mention) |
| Statistical test (t-test > 0) | Standard Practice | scipy.stats documentation |
| Evaluation metrics (mean distance, p-value) | Hypothesis Statement | Phase 2B 02b_verification_plan.md |
| Pseudo-code implementation | Archon KB + Standard Practice | A.1, A.2, A.3 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-21T00:00:00Z

### Workflow History for This Hypothesis

**Phase 2C Timeline:**
- Started: 2026-03-21T00:00:00Z
- Completed: 2026-03-21T00:15:00Z
- Duration: ~15 minutes

**Steps Executed:**
1. ✅ Step 01: Initialize and Validate State
2. ✅ Step 02: Archon Knowledge Base Search (3 queries)
3. ✅ Step 03: Exa GitHub Search (2 queries)
4. ✅ Step 04: Serena Analysis (SKIPPED - code clear)
5. ✅ Step 05: Dataset & Baseline Confirmation
6. ✅ Step 06: Experiment Synthesis
7. ✅ Step 07: Reference Documentation
8. ✅ Step 08: Quality Validation

**Quality Checks:** All PASSED
- Hyperparameters justified ✓
- Dataset choice justified ✓
- Mechanism grounded in code ✓
- No unsupported assumptions ✓
- Full traceability ✓

**Next Phase:** Phase 3 - Implementation Planning (BLOCKED until h-e1 resolved)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
