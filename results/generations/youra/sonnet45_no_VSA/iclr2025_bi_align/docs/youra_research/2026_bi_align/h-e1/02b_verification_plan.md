# Phase 2B: Verification Plan
## H-E1: Segment-level MSI from 3-iteration sampling

**Hypothesis ID**: h-e1  
**Generated**: 2026-07-10T16:30:00Z  
**Status**: VERIFICATION_DESIGN_COMPLETE  

---

## 1. Hypothesis Recap

**Statement**: 3-iteration stratified sampling (1st iteration, post-optimizer.step, P50/P75/P95/P99 length bins) predicts 10-iteration segment peak memory with ≤10% median relative error for CNNs, ≤15% for transformers.

**Type**: EXISTENCE  
**Gate**: MUST_WORK  

---

## 2. Verification Strategy

### 2.1 Core Approach

**Method**: Comparative profiling study
- **Ground truth**: 10-iteration full profiling (segment-level peak memory)
- **Lightweight method**: 3-iteration + stratified sampling
- **Comparison metric**: Relative error = |predicted - ground_truth| / ground_truth

**Why this approach**:
- Direct measurement (not simulation)
- Clear falsification criterion (error threshold)
- Replicable across architectures

### 2.2 Prior Art Validation

**VeritasEst findings** (baseline):
- 2-iteration optimizer state stabilization demonstrated
- Limitation: No stratified sampling for activation variance
- Our extension: Add 3rd iteration + stratified bins for transformers

**Key insight to validate**:
Stratified sampling addresses activation memory variance in variable-length sequences (critical for transformers).

---

## 3. Statistical Tests

### 3.1 Primary Test

**Hypothesis test**:
- H0: Median relative error ≥ 10% (CNNs) or ≥15% (transformers)
- H1: Median relative error < thresholds

**Test**: Wilcoxon signed-rank test
- **Why**: Non-parametric, robust to outliers, handles paired data
- **Significance level**: α = 0.05
- **Power**: 0.80 (requires n≥30 per group)

**Sample size justification**:
- 48 configurations (16 models × 3 optimizers)
- Multiple batches per config → >100 measurements total
- Well above n=30 requirement

### 3.2 Secondary Analyses

**Per-architecture breakdown**:
- Test: Kruskal-Wallis H-test (compare CNNs vs transformers)
- Purpose: Identify architecture-specific failure modes

**Optimizer effect**:
- Test: Friedman test (repeated measures across 3 optimizers)
- Purpose: Validate workspace allocation tracking

**Length distribution impact**:
- Test: Spearman correlation (error vs sequence length)
- Purpose: Validate stratified sampling effectiveness

---

## 4. Dataset Requirements

### 4.1 Selection Criteria

**MUST have**:
1. Real, established benchmark (not synthetic)
2. Standard train/test splits
3. Sufficient sample size (>1000 samples per split)
4. Diverse characteristics (fixed vs variable length)

### 4.2 Selected Datasets

| Dataset | Justification | Split | Size | Characteristic |
|---------|---------------|-------|------|----------------|
| **CIFAR-10** | Standard CV benchmark, eliminates length variance for CNNs | test | 10,000 | Fixed 32×32 images |
| **ImageNet-1K** | Production-scale CV, tests generalization | val | 50,000 | Fixed 224×224 (typical) |
| **WMT-14 En-De** | Standard MT benchmark, long-tail length distribution | test | 3,003 | Variable 10-100 tokens |

**Why multiple datasets**:
- CIFAR-10: Control for length variance (all fixed size)
- ImageNet-1K: Real-world scale validation
- WMT-14: Critical for stratified sampling validation (variable length)

### 4.3 Data Preparation

**CIFAR-10**:
```python
from torchvision.datasets import CIFAR10
dataset = CIFAR10(root='./data', train=False, download=True)
```

**ImageNet-1K**:
```python
from torchvision.datasets import ImageNet
dataset = ImageNet(root='./data/imagenet', split='val')
```

**WMT-14**:
```python
from datasets import load_dataset
dataset = load_dataset('wmt14', 'de-en', split='test')
```

---

## 5. Metrics & Success Criteria

### 5.1 Primary Metrics

**Relative Error**:
```
error = |predicted_memory_mb - ground_truth_memory_mb| / ground_truth_memory_mb
```

**Aggregation**:
- **Median error**: Robust to outliers
- **95th percentile error**: Captures worst-case performance

### 5.2 Success Thresholds

**Primary criteria**:
- Median ≤ 10% for CNNs (8 architectures)
- Median ≤ 15% for transformers (8 architectures, contingency threshold)
- P95 ≤ 25% across all 16 models

**Statistical significance**:
- Wilcoxon signed-rank p < 0.05 vs 2-iteration baseline

### 5.3 Falsification Thresholds

**Hard failure** (hypothesis rejected):
- Median > 15% for any architecture family
- P95 > 30% overall

**Contingency** (extend method):
- Median 10-15% for CNNs → acceptable with documentation
- P95 25-30% → add confidence intervals

---

## 6. Baseline Comparisons

### 6.1 Ground Truth Baseline

**10-iteration full profiling**:
- Purpose: Establish reference memory values
- Protocol: Run 10 training iterations, track memory each iteration
- Why iteration 10: VeritasEst showed optimizer state stabilizes by iteration 2; iteration 10 provides safety margin

### 6.2 Ablation: 2-iteration (VeritasEst)

**Purpose**: Validate that 3-iteration + stratified improves accuracy

**Protocol**:
- Same as lightweight method but only iterations 1-2 (no post-optimizer.step)
- No stratified sampling

**Expected outcome**: Higher error for transformers (misses workspace allocations)

### 6.3 Control: SGD Optimizer

**Purpose**: Test workspace allocation tracking

**Rationale**:
- Adam/AdamW allocate workspace (m_t, v_t buffers)
- SGD has no workspace allocations
- If 3-iteration helps for Adam but not SGD → validates workspace tracking hypothesis

---

## 7. Confound Mitigation

### 7.1 Length Variance Confound

**Problem**: Variable-length sequences cause activation memory variance

**Mitigation**: Stratified sampling
- Bucket batches by length (P50/P75/P95/P99 quantiles)
- Sample 1 batch per bin
- Ensures coverage of length distribution

**Validation**: Correlation test (error vs length) should show no significant relationship after stratification

### 7.2 Optimizer Workspace Confound

**Problem**: Adam allocates workspace after first backward pass

**Mitigation**: Post-optimizer.step measurement
- Capture memory AFTER first optimizer.step() call
- Ensures workspace buffers are allocated

**Validation**: SGD (no workspace) vs Adam/AdamW comparison

### 7.3 Allocator Fragmentation Confound

**Problem**: Tensor-level sums underestimate memory due to BFC allocator fragmentation

**Mitigation**: Segment-level tracking
- Use `torch.cuda.memory_stats()` (not tensor.nbytes sums)
- Captures actual GPU memory reserved, not just allocated

**Validation**: Compare segment-level vs tensor-level predictions (expect segment > tensor)

### 7.4 Architecture Diversity

**Problem**: Method may work for CNNs but fail for transformers (or vice versa)

**Mitigation**: 8 architectures per family
- CNNs: ResNet-18/34/50, VGG-16, DenseNet-121, MobileNetV2, EfficientNet-B0, ShuffleNetV2
- Transformers: BERT-base, GPT-2-small, DistilBERT, RoBERTa-base, T5-small, ALBERT-base, DeBERTa-base, ViT-base

**Validation**: Per-architecture breakdown (Kruskal-Wallis test)

---

## 8. Implementation Requirements

### 8.1 Memory Profiling Infrastructure

**Segment-level tracking** (mandatory):
```python
import torch

# Reset before profiling
torch.cuda.reset_peak_memory_stats()

# Run forward/backward/optimizer step
output = model(input)
loss.backward()
optimizer.step()

# Capture segment-level peak
peak_memory_mb = torch.cuda.max_memory_allocated() / (1024**2)
```

**Why NOT tensor sums**:
- Underestimates due to allocator fragmentation
- Misses optimizer workspace allocations
- Does not reflect actual GPU memory usage

### 8.2 Stratified Sampling Implementation

**Length bucketing**:
1. Load dataset, compute length for each sample
2. Calculate quantiles: P50, P75, P95, P99
3. Create 4 buckets: [0-P50], [P50-P75], [P75-P95], [P95+]
4. Sample 1 batch per bucket for profiling

**For fixed-length datasets** (CIFAR-10, ImageNet):
- No stratification needed
- Sample 4 random batches

### 8.3 Architecture Loading

**CNNs** (via torchvision):
```python
import torchvision.models as models
model = models.resnet18(pretrained=False)
```

**Transformers** (via HuggingFace):
```python
from transformers import AutoModel
model = AutoModel.from_pretrained('bert-base-uncased')
```

---

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Allocator simulation fails for transformers | 30% | High | Contingency threshold ≤15% acceptable |
| Gradient accumulation edge cases | 20% | Medium | Scope to validated architectures only |
| ImageNet download timeout | 15% | Low | Use streaming datasets or cached splits |
| WMT-14 length distribution skewed | 10% | Low | Validate quantile bins empirically |

### 9.2 Statistical Risks

**Insufficient power**:
- Risk: n<30 per group → underpowered test
- Mitigation: 48 configs × multiple batches = >100 measurements

**Multiple testing**:
- Risk: False positives from multiple comparisons
- Mitigation: Bonferroni correction for secondary analyses

**Outliers**:
- Risk: Extreme values skew results
- Mitigation: Use median (robust) instead of mean

---

## 10. Expected Outcomes

### 10.1 Success Scenario

**Quantitative**:
- Median error: 8% (CNNs), 12% (transformers)
- P95 error: 22% overall
- Wilcoxon p < 0.001 vs 2-iteration baseline

**Interpretation**:
- Stratified sampling addresses activation variance
- 3-iteration profiling is accurate and practical
- Gates open for h-m1 (orthogonality analysis)

### 10.2 Failure Scenario

**Quantitative**:
- Median error: 18% (transformers)
- P95 error: 35% overall

**Root cause analysis**:
1. Check stratified bin coverage (are P50/P75/P95/P99 sufficient?)
2. Validate workspace allocation tracking (compare SGD vs Adam)
3. Test architecture-specific patterns (which models fail?)

**Contingency actions**:
- Extend to 5-iteration sampling
- Add confidence intervals (±20% tolerance)
- Architecture-specific calibration factors

---

## 11. Key Insights from Prior Work

### 11.1 VeritasEst Learnings

**Validated**:
- 2-iteration optimizer state stabilization
- Segment-level tracking captures allocator fragmentation

**Limitations**:
- No stratified sampling → misses activation variance
- No workspace tracking → underestimates Adam memory

**Our extension**:
- Add 3rd iteration (post-optimizer.step) → capture workspace
- Add stratified sampling → address length variance

### 11.2 Tensor Sums Failure

**VeritasEst finding**: Tensor-level sums underestimate memory under Adam optimizer

**Root cause**: Workspace allocations (m_t, v_t buffers) not counted

**Our mitigation**: Segment-level tracking via `torch.cuda.memory_stats()`

### 11.3 BFC Allocator Fragmentation

**PyTorch CUDA allocator**: Best-Fit with Coalescing (BFC)
- Allocates in power-of-2 bins
- Fragmentation from mixed tensor sizes
- Segment-level tracking captures this overhead

---

## 12. Next Steps (Phase 2C)

**Experiment Design Brief**:
1. Detailed profiling protocol (step-by-step)
2. Implementation search (Archon KB + Exa for code examples)
3. Compute requirements (GPU-hours, storage)
4. Risk mitigation strategies
5. Deliverables specification

**Timeline**:
- Phase 2B → 2C: Same day (design refinement)
- Phase 2C → 3: 1 day (PRD generation)

---

## 13. Success Gate Definition

**MUST_WORK criteria** (gates h-m1, h-m2):
- [ ] Median ≤10% for CNNs OR ≤15% for all models (contingency)
- [ ] P95 ≤25% across all 48 configs
- [ ] Statistically significant vs 2-iteration baseline (p<0.05)

**If ANY criterion fails**:
- Block h-m1 hypothesis execution
- Trigger contingency planning (5-iteration, confidence intervals)
- Document failure modes for future work

---

**Document Status**: COMPLETE  
**Next Phase**: 2C (Experiment Design Brief)  
**Ready for**: Implementation search and detailed protocol design
