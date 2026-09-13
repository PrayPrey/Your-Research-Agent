# Product Requirements Document: h-e1 Variance Measurement System

**Date:** 2026-03-21
**Author:** anonymous
**Hypothesis ID:** h-e1
**Hypothesis Type:** EXISTENCE
**Gate Type:** MUST_WORK
**Version:** 3.0 (Dual-Dataset/Dual-Architecture)
**Phase:** 3 (Implementation Planning)

---

## Executive Summary

### Purpose

This PRD defines the requirements for a variance measurement system that validates the foundational hypothesis h-e1: test accuracy variance across random seed initializations is statistically detectable for neural network training under controlled conditions.

This is the **foundation hypothesis** of the entire verification workflow. Without measurable variance (σ² ≥ 0.3%), the variance measurement infrastructure is invalid, and all subsequent mechanism hypotheses (h-m1, h-m2, h-m3) become meaningless.

### Scope

**In Scope:**
- Deterministic training infrastructure for PyTorch MLPs
- Dual-dataset evaluation (MNIST + Fashion-MNIST)
- Dual-architecture evaluation (1-layer + 2-layer MLP)
- Statistical variance measurement across 30 random seeds per condition
- Automated experiment orchestration for 120 total training runs
- Variance metrics calculation and validation

**Out of Scope:**
- Mechanism analysis (h-m1, h-m2, h-m3 will address this)
- Hyperparameter optimization
- Advanced architectures beyond simple MLPs
- CLT convergence rate analysis (failed in Version 2, removed from Version 3)
- Multi-GPU training
- Model deployment or production inference

### Success Criteria

**Primary Success Criteria (MUST_WORK Gate):**
1. **Code Execution:** All 120 experiments complete without errors
2. **Variance Detection:** Test accuracy variance σ² ≥ 0.3% for **at least 2 out of 4 conditions**
   - Conditions: (MNIST, 1-layer), (MNIST, 2-layer), (Fashion-MNIST, 1-layer), (Fashion-MNIST, 2-layer)

**Secondary Success Criteria:**
3. **Reproducibility:** Identical seed produces identical test accuracy on re-run
4. **Statistical Validity:** 30 samples per condition enable stable variance estimation (Rajput 2023)
5. **Performance Baseline:** Mean accuracy within expected ranges:
   - MNIST: 97-98%
   - Fashion-MNIST: 85-90%

**Failure Consequences:**
- Gate FAIL → **ABANDON entire verification plan** (variance infrastructure invalid)

---

## Problem Statement

### Research Question

**Core Question:** Does test accuracy exhibit measurable variance across random seed initializations in deterministic neural network training?

**Scientific Context:**
- **Prior Work (Version 1):** MNIST-only design showed 0.128% variance with kurtosis violations
- **Prior Work (Version 2):** Scaled experiment (40 runs) passed implementation but FAILED gate validation due to CLT mismatch (β=-0.391 vs expected -0.50)
- **Current Approach (Version 3):** Simplify to EXISTENCE validation, expand to dual-dataset/dual-architecture design

### Hypothesis Details

**Hypothesis Statement:**
> "Test accuracy variance σ² is statistically non-zero (p < 0.05) for all 4 conditions (2 architectures × 2 datasets)"

**Hypothesis Type:** EXISTENCE (Proof-of-Concept)
- Goal: Demonstrate phenomenon exists (not mechanism explanation)
- Pass Condition: Direction-based (variance ≥ threshold)

**Prerequisites:** None (foundation hypothesis)

**Gate Condition:**
- **Type:** MUST_WORK
- **Threshold:** σ² ≥ 0.3% for ≥2 conditions
- **Rationale:** 0.3% is the practical detectability limit from Phase 2B analysis
- **Consequence:** Failure invalidates all downstream hypotheses

### Significance

**Scientific Impact:**
- Establishes baseline variance measurement capability
- Validates experimental infrastructure for mechanism studies
- Provides empirical variance ranges for sample size planning

**Methodological Impact:**
- Demonstrates reproducible variance measurement protocol
- Tests task difficulty sensitivity (MNIST vs Fashion-MNIST)
- Tests architecture sensitivity (1-layer vs 2-layer)

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing

**FR-1.1: MNIST Dataset**
- **Requirement:** Load MNIST dataset via `torchvision.datasets.MNIST`
- **Statistics:** 60,000 train + 10,000 test images, 28×28 grayscale, 10 classes
- **Preprocessing:**
  - `transforms.ToTensor()` - Convert to [0,1] range
  - `transforms.Normalize((0.1307,), (0.3081,))` - MNIST-specific normalization
- **Storage:** Auto-download to `./data/` directory
- **Validation:** Verify dataset shape (60000, 1, 28, 28) for train set

**FR-1.2: Fashion-MNIST Dataset**
- **Requirement:** Load Fashion-MNIST dataset via `torchvision.datasets.FashionMNIST`
- **Statistics:** 60,000 train + 10,000 test images, 28×28 grayscale, 10 classes
- **Preprocessing:**
  - `transforms.ToTensor()` - Convert to [0,1] range
  - `transforms.Normalize((0.5,), (0.5,))` - Fashion-MNIST normalization
- **Storage:** Auto-download to `./data/` directory
- **Validation:** Verify dataset shape (60000, 1, 28, 28) for train set

**FR-1.3: DataLoader Configuration**
- **Requirement:** Create deterministic DataLoaders with reproducible shuffling
- **Parameters:**
  - Train batch size: 64
  - Test batch size: 64
  - Shuffle: True (train), False (test)
  - Num workers: 0 (disable multi-processing for determinism)
- **Reproducibility:** Use `generator` parameter seeded per experiment
- **Code Reference:**
  ```python
  g = torch.Generator()
  g.manual_seed(seed)
  train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, generator=g)
  test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)
  ```

**FR-1.4: No Data Augmentation**
- **Requirement:** Disable all random augmentations (determinism requirement)
- **Rationale:** Random augmentations introduce variance unrelated to weight initialization

### FR-2: Model Architecture

**FR-2.1: 1-Layer MLP Architecture**
- **Requirement:** Implement simple feedforward network
- **Structure:**
  - Input: 784 (28×28 flattened)
  - Hidden Layer 1: 128 units, ReLU activation
  - Output: 10 units (logits, no softmax)
- **Parameters:** ~196K (784×128 + 128×10 + biases)
- **Implementation:**
  ```python
  class SimpleMLP1Layer(nn.Module):
      def __init__(self):
          super().__init__()
          self.fc1 = nn.Linear(28 * 28, 128)
          self.fc2 = nn.Linear(128, 10)

      def forward(self, x):
          x = x.view(-1, 28 * 28)
          x = F.relu(self.fc1(x))
          x = self.fc2(x)
          return x
  ```

**FR-2.2: 2-Layer MLP Architecture**
- **Requirement:** Implement deeper feedforward network for architecture sensitivity test
- **Structure:**
  - Input: 784 (28×28 flattened)
  - Hidden Layer 1: 256 units, ReLU activation
  - Hidden Layer 2: 128 units, ReLU activation
  - Output: 10 units (logits, no softmax)
- **Parameters:** ~400K (784×256 + 256×128 + 128×10 + biases)
- **Implementation:**
  ```python
  class SimpleMLP2Layer(nn.Module):
      def __init__(self):
          super().__init__()
          self.fc1 = nn.Linear(28 * 28, 256)
          self.fc2 = nn.Linear(256, 128)
          self.fc3 = nn.Linear(128, 10)

      def forward(self, x):
          x = x.view(-1, 28 * 28)
          x = F.relu(self.fc1(x))
          x = F.relu(self.fc2(x))
          x = self.fc3(x)
          return x
  ```

**FR-2.3: Weight Initialization**
- **Requirement:** Use PyTorch default initialization (Kaiming uniform for Linear layers)
- **Reproducibility:** Initialization controlled by `torch.manual_seed(seed)`
- **Validation:** Verify identical weights on identical seeds

### FR-3: Training Protocol

**FR-3.1: Deterministic Environment Setup**
- **Requirement:** Enforce full determinism for reproducible training
- **Implementation:**
  ```python
  def set_seed(seed):
      torch.manual_seed(seed)
      np.random.seed(seed)
      random.seed(seed)
      torch.backends.cudnn.deterministic = True
      torch.backends.cudnn.benchmark = False
      if torch.cuda.is_available():
          torch.cuda.manual_seed(seed)
          torch.cuda.manual_seed_all(seed)
  ```
- **Environment Variable:** `CUBLAS_WORKSPACE_CONFIG=:4096:8` (CUDA 10.2+)
- **Validation:** Re-run with same seed must produce identical test accuracy

**FR-3.2: Optimizer Configuration**
- **Requirement:** Use SGD with momentum
- **Parameters:**
  - Learning rate: 0.01
  - Momentum: 0.9
  - Weight decay: 0 (no regularization)
- **Rationale:** Standard MNIST baseline (kirenz.github.io, clay-atlas.com tutorials)

**FR-3.3: Loss Function**
- **Requirement:** CrossEntropyLoss for multi-class classification
- **Implementation:** `criterion = nn.CrossEntropyLoss()`

**FR-3.4: Training Loop**
- **Requirement:** Train for 10 epochs per experiment
- **Epochs:** 10 (sufficient for MNIST/Fashion-MNIST convergence)
- **Batch Processing:**
  ```python
  for epoch in range(10):
      model.train()
      for data, target in train_loader:
          optimizer.zero_grad()
          output = model(data.to(device))
          loss = criterion(output, target.to(device))
          loss.backward()
          optimizer.step()
  ```

**FR-3.5: Experiment Orchestration**
- **Requirement:** Run 30 independent experiments per condition
- **Total Experiments:** 4 conditions × 30 seeds = 120 runs
- **Conditions:**
  1. MNIST + 1-layer MLP (seeds 0-29)
  2. MNIST + 2-layer MLP (seeds 0-29)
  3. Fashion-MNIST + 1-layer MLP (seeds 0-29)
  4. Fashion-MNIST + 2-layer MLP (seeds 0-29)
- **Seed Range:** 0-29 (30 independent seeds)
- **Parallelization:** Sequential execution (determinism priority)

### FR-4: Evaluation and Metrics

**FR-4.1: Test Accuracy Calculation**
- **Requirement:** Evaluate on test set after 10 epochs of training
- **Implementation:**
  ```python
  def evaluate(model, test_loader, device):
      model.eval()
      correct = 0
      total = 0
      with torch.no_grad():
          for data, target in test_loader:
              data, target = data.to(device), target.to(device)
              output = model(data)
              pred = output.argmax(dim=1, keepdim=True)
              correct += pred.eq(target.view_as(pred)).sum().item()
              total += target.size(0)
      accuracy = 100.0 * correct / total
      return accuracy
  ```
- **Output:** Test accuracy as percentage (0-100%)

**FR-4.2: Variance Metrics Calculation**
- **Requirement:** Compute variance statistics for each condition (30 test accuracies)
- **Metrics:**
  1. **Sample Variance (σ²):** `np.var(test_accuracies, ddof=1)`
  2. **Sample Standard Deviation (σ):** `np.std(test_accuracies, ddof=1)`
  3. **Mean Accuracy (μ):** `np.mean(test_accuracies)`
  4. **Coefficient of Variation (CV%):** `(σ / μ) × 100`
  5. **Min/Max Range:** `[np.min(test_accuracies), np.max(test_accuracies)]`

**FR-4.3: Statistical Testing**
- **Requirement:** Validate variance is statistically non-zero
- **Test:** Levene's test for homogeneity of variances
  - **Null Hypothesis:** σ² = 0 (no variance)
  - **Alternative:** σ² > 0 (variance exists)
  - **Significance Level:** α = 0.05
  - **Implementation:** `scipy.stats.levene(*groups)` or bootstrap confidence intervals
- **Output:** p-value for each condition

**FR-4.4: Bootstrap Confidence Intervals**
- **Requirement:** Compute 95% CI for variance estimates
- **Method:** Bootstrap resampling (1000 iterations)
- **Implementation:**
  ```python
  from scipy.stats import bootstrap
  rng = np.random.default_rng(seed=42)
  res = bootstrap((test_accuracies,), np.var, n_resamples=1000, random_state=rng)
  ci_lower, ci_upper = res.confidence_interval
  ```
- **Output:** (ci_lower, ci_upper) for each condition

### FR-5: Results Storage and Logging

**FR-5.1: Experiment Logs**
- **Requirement:** Log each training run's metadata and results
- **Format:** JSON or CSV
- **Fields:**
  - `condition` (str): "mnist_1layer", "mnist_2layer", "fmnist_1layer", "fmnist_2layer"
  - `seed` (int): 0-29
  - `test_accuracy` (float): Final test accuracy (%)
  - `train_time` (float): Training duration (seconds)
  - `timestamp` (str): ISO 8601 format
- **File Path:** `{hypothesis_folder}/results/experiment_logs.csv`

**FR-5.2: Variance Summary**
- **Requirement:** Save aggregated variance metrics
- **Format:** JSON
- **Fields (per condition):**
  - `mean_accuracy` (float)
  - `variance` (float)
  - `std_dev` (float)
  - `cv_percent` (float)
  - `min_accuracy` (float)
  - `max_accuracy` (float)
  - `p_value` (float): Statistical test p-value
  - `ci_lower` (float): Bootstrap CI lower bound
  - `ci_upper` (float): Bootstrap CI upper bound
- **File Path:** `{hypothesis_folder}/results/variance_summary.json`

**FR-5.3: Gate Validation Results**
- **Requirement:** Save gate pass/fail status
- **Format:** JSON
- **Fields:**
  - `gate_type` (str): "MUST_WORK"
  - `pass_condition` (str): "variance >= 0.3% for >= 2 conditions"
  - `conditions_passed` (int): Count of conditions meeting threshold
  - `gate_result` (str): "PASS" or "FAIL"
  - `details` (dict): Per-condition variance values
- **File Path:** `{hypothesis_folder}/results/gate_result.json`

### FR-6: Visualization

**FR-6.1: Gate Metrics Comparison (Mandatory)**
- **Requirement:** Bar chart comparing target (0.3%) vs actual variance for each condition
- **X-axis:** 4 conditions
- **Y-axis:** Variance (σ²) in percentage points
- **Components:**
  - Red horizontal line at 0.3% (threshold)
  - Bars for actual variance with error bars (95% CI)
- **File Path:** `{hypothesis_folder}/figures/gate_metrics_comparison.png`

**FR-6.2: Variance by Condition**
- **Requirement:** Bar chart showing σ² for all 4 conditions
- **X-axis:** Conditions (MNIST 1L, MNIST 2L, FMNIST 1L, FMNIST 2L)
- **Y-axis:** Variance (σ²) in percentage points
- **File Path:** `{hypothesis_folder}/figures/variance_by_condition.png`

**FR-6.3: Distribution Histograms**
- **Requirement:** 2×2 subplot of test accuracy distributions
- **Subplots:** One histogram per condition (30 values each)
- **X-axis:** Test accuracy (%)
- **Y-axis:** Frequency
- **Annotations:** Mean, σ, CV% on each subplot
- **File Path:** `{hypothesis_folder}/figures/accuracy_distributions.png`

**FR-6.4: Coefficient of Variation Comparison**
- **Requirement:** Bar chart comparing CV% across conditions
- **X-axis:** 4 conditions
- **Y-axis:** CV% (coefficient of variation)
- **File Path:** `{hypothesis_folder}/figures/cv_comparison.png`

**FR-6.5: Accuracy Ranges**
- **Requirement:** Box plots or error bar plots showing min/max/mean per condition
- **Components:**
  - Mean accuracy (marker)
  - Min/max range (error bars)
  - Median (line)
- **File Path:** `{hypothesis_folder}/figures/accuracy_ranges.png`

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**NFR-1.1: Seed Control**
- **Requirement:** Identical seed must produce identical results on re-run
- **Validation:** Re-run seed=0 for each condition, verify test accuracy matches
- **Tolerance:** Absolute difference ≤ 0.01%

**NFR-1.2: Deterministic Operations**
- **Requirement:** All operations must be deterministic (no randomness beyond controlled seed)
- **Implementation:** cuDNN deterministic mode, fixed DataLoader seed
- **Validation:** No warnings about non-deterministic operations

**NFR-1.3: Environment Specification**
- **Requirement:** Document all dependencies and versions
- **Components:**
  - PyTorch version
  - torchvision version
  - CUDA version (if GPU)
  - Python version
  - OS and hardware specifications
- **File Path:** `{hypothesis_folder}/results/environment.json`

### NFR-2: Performance

**NFR-2.1: Training Time**
- **Requirement:** Each experiment completes within 30 seconds
- **Expected:** 5-10 seconds per experiment (Phase 2B estimate)
- **Total Time Budget:** 120 experiments × 30 sec = 60 minutes maximum

**NFR-2.2: GPU Utilization**
- **Requirement:** Use single GPU if available (CUDA_VISIBLE_DEVICES set)
- **Fallback:** CPU execution if no GPU available
- **Validation:** Check `nvidia-smi` for empty GPU before experiment start

**NFR-2.3: Memory Usage**
- **Requirement:** Peak GPU memory ≤ 2GB per experiment
- **Rationale:** Small models (≤400K parameters), batch size 64

### NFR-3: Logging and Monitoring

**NFR-3.1: Progress Tracking**
- **Requirement:** Log progress for each experiment completion
- **Format:** "Completed [condition] seed [X]/30 - Accuracy: [Y]%"
- **Frequency:** After each experiment (120 total log entries)

**NFR-3.2: Error Handling**
- **Requirement:** Catch and log all errors without crashing entire workflow
- **Implementation:**
  - Try-catch around each experiment
  - Save partial results if failure occurs
  - Log error message and stack trace
- **Output:** `{hypothesis_folder}/results/errors.log`

**NFR-3.3: Checkpointing**
- **Requirement:** Save intermediate results every 10 experiments
- **Rationale:** Enable recovery if process crashes
- **Implementation:** Write `experiment_logs.csv` incrementally

### NFR-4: Code Quality

**NFR-4.1: Modularity**
- **Requirement:** Separate functions for dataset loading, model creation, training, evaluation
- **Structure:**
  ```python
  def load_dataset(name: str) -> (DataLoader, DataLoader)
  def create_model(architecture: str) -> nn.Module
  def train_model(model, train_loader, optimizer, criterion, epochs: int) -> None
  def evaluate_model(model, test_loader, device) -> float
  def run_experiment(condition: str, seed: int) -> float
  ```

**NFR-4.2: Type Hints**
- **Requirement:** All functions must have type annotations
- **Example:** `def evaluate_model(model: nn.Module, test_loader: DataLoader, device: str) -> float`

**NFR-4.3: Documentation**
- **Requirement:** Docstrings for all functions describing purpose, args, returns
- **Format:** Google-style docstrings

**NFR-4.4: Configuration Management**
- **Requirement:** All hyperparameters in single config dictionary or YAML file
- **Parameters:**
  - Learning rate: 0.01
  - Momentum: 0.9
  - Batch size: 64
  - Epochs: 10
  - Seeds: [0, 1, ..., 29]

---

## Success Criteria

### Primary Success Criteria

**SC-1: Code Execution Success**
- **Requirement:** All 120 experiments complete without errors
- **Validation:** Check `experiment_logs.csv` has 120 rows
- **Metric:** 100% completion rate

**SC-2: Variance Detection (MUST_WORK Gate)**
- **Requirement:** σ² ≥ 0.3% for at least 2 out of 4 conditions
- **Validation:**
  - Count conditions where `variance >= 0.003` (0.3% in decimal)
  - Gate PASS if count ≥ 2
  - Gate FAIL if count < 2
- **Metric:** `conditions_passed / 4`

### Secondary Success Criteria

**SC-3: Statistical Significance**
- **Requirement:** p < 0.05 for variance test in all 4 conditions
- **Validation:** All p-values in `variance_summary.json` < 0.05
- **Metric:** Proportion of conditions with significant variance

**SC-4: Reproducibility Validation**
- **Requirement:** Re-run seed=0 produces identical accuracy
- **Validation:** Absolute difference ≤ 0.01% for all 4 conditions
- **Metric:** Max absolute difference across conditions

**SC-5: Baseline Performance**
- **Requirement:** Mean accuracy within expected ranges
- **Validation:**
  - MNIST 1-layer: 97-98%
  - MNIST 2-layer: 97-98%
  - Fashion-MNIST 1-layer: 85-90%
  - Fashion-MNIST 2-layer: 87-92%
- **Metric:** All conditions within ±3% of expected range

**SC-6: Visualization Quality**
- **Requirement:** All 5 required figures generated and saved
- **Validation:** Check existence of 5 PNG files in `figures/` directory
- **Metric:** 5/5 figures present

---

## Dependencies

### Software Dependencies

**Python Libraries:**
- **PyTorch:** >= 1.10.0 (core training framework)
- **torchvision:** >= 0.11.0 (dataset loading)
- **NumPy:** >= 1.21.0 (variance calculations)
- **SciPy:** >= 1.7.0 (statistical testing)
- **Matplotlib:** >= 3.4.0 (visualization)
- **pandas:** >= 1.3.0 (optional, for CSV handling)

**System Requirements:**
- **Python:** >= 3.8
- **CUDA:** >= 10.2 (optional, for GPU acceleration)
- **GPU:** Single NVIDIA GPU with ≥2GB memory (recommended)

**Environment Variables:**
- `CUDA_VISIBLE_DEVICES`: Set to single empty GPU ID (check via `nvidia-smi`)
- `CUBLAS_WORKSPACE_CONFIG`: `:4096:8` (for CUDA 10.2+ determinism)

### Data Dependencies

**Datasets:**
- **MNIST:** Auto-download via torchvision (60MB)
- **Fashion-MNIST:** Auto-download via torchvision (60MB)
- **Storage:** `./data/` directory (120MB total)

**Pre-trained Models:** None (train from scratch)

### Infrastructure Dependencies

**Compute Resources:**
- **Estimated Total Time:** 10-60 minutes (120 experiments × 5-30 sec each)
- **GPU Memory:** 2GB per experiment
- **Disk Space:** 200MB (datasets + results)

---

## Evaluation Metrics

### Primary Metrics

**M-1: Test Accuracy Variance (σ²)**
- **Definition:** Sample variance of 30 test accuracies per condition
- **Formula:** `σ² = Σ(x_i - μ)² / (n - 1)` where n=30
- **Unit:** Percentage points squared (e.g., 0.5% variance)
- **Target:** ≥ 0.3% for ≥2 conditions (gate threshold)

**M-2: Levene's Test p-value**
- **Definition:** Statistical test for variance non-zero hypothesis
- **Formula:** `scipy.stats.levene(*groups)` p-value
- **Unit:** Probability (0-1)
- **Target:** < 0.05 (reject null hypothesis of zero variance)

**M-3: Bootstrap CI Width**
- **Definition:** Width of 95% confidence interval for variance estimate
- **Formula:** `ci_upper - ci_lower`
- **Unit:** Percentage points
- **Target:** Narrow CI indicates stable variance estimate

### Secondary Metrics

**M-4: Standard Deviation (σ)**
- **Definition:** Sample standard deviation of test accuracies
- **Formula:** `σ = sqrt(σ²)`
- **Unit:** Percentage points (e.g., 0.7%)
- **Purpose:** Interpretable variance measure

**M-5: Coefficient of Variation (CV%)**
- **Definition:** Normalized variance measure
- **Formula:** `CV% = (σ / μ) × 100`
- **Unit:** Percent (relative to mean)
- **Purpose:** Compare variance across conditions with different mean accuracies

**M-6: Mean Test Accuracy (μ)**
- **Definition:** Average test accuracy across 30 seeds
- **Formula:** `μ = Σx_i / n` where n=30
- **Unit:** Percentage (0-100%)
- **Purpose:** Baseline performance validation

**M-7: Accuracy Range**
- **Definition:** Difference between max and min test accuracy
- **Formula:** `range = max(accuracies) - min(accuracies)`
- **Unit:** Percentage points
- **Purpose:** Dynamic range assessment

### Baseline Comparisons

**Expected Performance (from Phase 2C research):**

| Condition | Mean Accuracy | Expected σ | Expected σ² |
|-----------|---------------|------------|-------------|
| MNIST 1-layer | 97-98% | 0.3-0.5% | 0.09-0.25% |
| MNIST 2-layer | 97-98% | 0.4-0.7% | 0.16-0.49% |
| Fashion-MNIST 1-layer | 85-87% | 0.5-1.0% | 0.25-1.0% |
| Fashion-MNIST 2-layer | 87-90% | 0.7-1.2% | 0.49-1.44% |

**Sources:**
- GitHub tutorials (CSCfi, kirenz.github.io, shaheer776)
- Phase 2B verification plan empirical estimates

---

## Risk Assessment

### High-Risk Items

**R-1: Gate Failure (MUST_WORK)**
- **Risk:** Variance < 0.3% for all conditions → ABANDON verification plan
- **Likelihood:** Low (Version 3 dual-dataset/dual-architecture design reduces risk)
- **Impact:** CRITICAL (entire verification workflow blocked)
- **Mitigation:**
  - Fashion-MNIST expected to have higher variance than MNIST
  - 2-layer MLP expected to have higher variance than 1-layer
  - 4 conditions provide redundancy (only need 2/4 to pass)

**R-2: Non-Determinism Failures**
- **Risk:** Identical seeds produce different results on re-run
- **Likelihood:** Medium (cuDNN, CUDA versioning issues)
- **Impact:** HIGH (invalidates reproducibility requirement)
- **Mitigation:**
  - Force `torch.backends.cudnn.deterministic = True`
  - Set `CUBLAS_WORKSPACE_CONFIG` environment variable
  - Document exact PyTorch/CUDA versions
  - Fallback to CPU if GPU non-determinism persists

### Medium-Risk Items

**R-3: Performance Baseline Mismatch**
- **Risk:** Mean accuracy outside expected range (e.g., MNIST < 95%)
- **Likelihood:** Low (standard architectures, proven hyperparameters)
- **Impact:** MEDIUM (suggests implementation bug, but doesn't fail gate)
- **Mitigation:**
  - Use proven hyperparameters from Phase 2C research
  - Validate training loss convergence
  - Compare to published MNIST/Fashion-MNIST baselines

**R-4: Training Time Overruns**
- **Risk:** 120 experiments take > 2 hours (≫ 60 min budget)
- **Likelihood:** Low (each experiment ~5-10 sec per Phase 2B)
- **Impact:** MEDIUM (delays workflow, but doesn't affect correctness)
- **Mitigation:**
  - Use GPU if available
  - Optimize DataLoader settings (num_workers=0 for determinism, but test num_workers=2 if safe)

### Low-Risk Items

**R-5: Visualization Errors**
- **Risk:** Figure generation fails or produces incorrect plots
- **Likelihood:** Low (matplotlib is stable, simple plots)
- **Impact:** LOW (doesn't affect gate validation)
- **Mitigation:**
  - Test visualization code on subset of data
  - Save raw data separately from figures

---

## Acceptance Criteria

### Phase 3 → 4 Handoff (PRD Acceptance)

**AC-1: PRD Completeness**
- All functional requirements (FR-1 to FR-6) specified
- All non-functional requirements (NFR-1 to NFR-4) specified
- Success criteria (SC-1 to SC-6) defined with measurable metrics
- Dependencies and environment requirements documented
- Risk assessment completed

**AC-2: Technical Specification Clarity**
- Dataset loading code snippets provided
- Model architecture code provided
- Training protocol pseudo-code provided
- Metrics calculation formulas specified
- File paths for all outputs defined

### Phase 4 Implementation Acceptance

**AC-3: Code Implementation**
- All 4 conditions (2 datasets × 2 architectures) implemented
- Deterministic environment setup verified
- 30 seeds per condition (120 total experiments) executed
- Experiment logs saved to CSV
- Variance summary saved to JSON

**AC-4: Gate Validation**
- Variance metrics calculated for all 4 conditions
- Gate result computed (PASS if ≥2 conditions meet threshold)
- Gate result saved to `gate_result.json`
- If FAIL: document root cause and recommendation

**AC-5: Visualization**
- All 5 required figures generated and saved
- Gate metrics comparison figure clearly shows threshold line
- Figures are publication-quality (labeled axes, legends, titles)

**AC-6: Reproducibility**
- Re-run with seed=0 produces identical accuracy (within 0.01%)
- Environment documented in `environment.json`
- All dependencies pinned to specific versions

### Phase 5 Baseline Integration Acceptance

**AC-7: Results Handoff**
- `variance_summary.json` contains all required fields
- `gate_result.json` indicates PASS/FAIL status
- Experiment logs ready for Phase 5 baseline comparison
- Figures ready for inclusion in final report

---

## Appendix: Reference Information

### A. Prior Hypothesis Versions

**Version 1 (2026-03-20):**
- Design: MNIST-only, 1-layer MLP, 20 seeds
- Result: PARTIAL (variance 0.128%, kurtosis violation)
- Issue: Variance too low, distribution non-normal

**Version 2 (2026-03-20):**
- Design: Fashion-MNIST-only, 1-layer MLP, 40 runs (2 regimes × 20 seeds)
- Result: FAIL (CLT convergence rate mismatch)
- Issue: β=-0.391 (observed) vs -0.50 (CLT prediction)
- Status: Implementation VERIFIED, Gate FAILED

**Version 3 (Current, 2026-03-21):**
- Design: Dual-dataset (MNIST + Fashion-MNIST), Dual-architecture (1-layer + 2-layer), 30 seeds
- Focus: EXISTENCE validation (not CLT convergence)
- Rationale: Simplify hypothesis, increase robustness via multiple conditions

### B. Implementation Resources

**PyTorch Documentation:**
- Reproducibility: https://pytorch.org/docs/stable/notes/randomness.html
- Datasets: https://pytorch.org/vision/stable/datasets.html

**GitHub Implementations:**
- CSCfi/machine-learning-scripts: https://github.com/CSCfi/machine-learning-scripts
- shaheer776/fashion-mnist-pytorch: https://github.com/shaheer776/fashion-mnist-pytorch

**Tutorials:**
- kirenz.github.io: MNIST PyTorch deterministic training
- clay-atlas.com: PyTorch seed setting and reproducibility

**Academic References:**
- Rajput et al. 2023: N≥30 criterion for variance estimation

### C. File Structure

```
docs/youra_research/20260318_question/h-e1/
├── 02c_experiment_brief.md        (Phase 2C output, input to this PRD)
├── 03_prd.md                       (This document)
├── results/
│   ├── experiment_logs.csv         (120 experiments × metadata)
│   ├── variance_summary.json       (4 conditions × metrics)
│   ├── gate_result.json            (PASS/FAIL status)
│   ├── environment.json            (reproducibility metadata)
│   └── errors.log                  (error logs if any)
└── figures/
    ├── gate_metrics_comparison.png (mandatory)
    ├── variance_by_condition.png
    ├── accuracy_distributions.png
    ├── cv_comparison.png
    └── accuracy_ranges.png
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-20 | anonymous | Initial PRD (MNIST-only, 20 seeds) |
| 2.0 | 2026-03-20 | anonymous | Fashion-MNIST-only, 40 runs, CLT focus |
| 3.0 | 2026-03-21 | anonymous | Dual-dataset/dual-architecture, EXISTENCE focus |

---

*Generated for Phase 3 (Implementation Planning)*
*Next Phase: Phase 4 (Coding and Experimentation)*
*Source Document: 02c_experiment_brief.md*
*MUST_WORK Gate: Variance ≥ 0.3% for ≥2 conditions*
