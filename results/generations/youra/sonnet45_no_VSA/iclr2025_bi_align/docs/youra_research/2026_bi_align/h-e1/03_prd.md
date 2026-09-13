# Product Requirements Document (PRD)
## H-E1: Segment-level Memory Stress Index Profiler

**Document ID**: h-e1-prd  
**Version**: 1.0  
**Created**: 2026-07-10  
**Hypothesis**: 3-iteration stratified sampling (1st iteration, post-optimizer.step, P50/P75/P95/P99 length bins) predicts 10-iteration segment peak memory with ≤10% median relative error for CNNs, ≤15% for transformers  
**Type**: EXISTENCE (MUST_WORK gate)

---

## 1. Executive Summary

### 1.1 Purpose
Build a lightweight memory profiling system that predicts peak GPU memory usage for deep learning training with ≤10-15% median error using only 3 iterations instead of full 10-iteration profiling. This enables fast Memory Stress Index (MSI) calculation for dual-axis model routing without expensive full-training profiling.

### 1.2 Key Requirements
- **Accuracy**: Median relative error ≤10% for CNNs, ≤15% for transformers
- **Efficiency**: 3 iterations vs 10 iterations (~70% compute reduction)
- **Coverage**: 48 configurations (16 models × 3 optimizers)
- **Scope**: CIFAR-10, ImageNet-1K (CNNs), WMT-14 (transformers)

### 1.3 Success Criteria
- Median error meets thresholds for all architecture classes
- P95 error ≤25% across all 48 configs
- Statistical significance (p<0.05) vs 2-iteration baseline

---

## 2. Problem Statement

### 2.1 Current Limitations
- Full 10-iteration profiling takes ~50 GPU-hours for 48 configs
- Tensor-level sums underestimate memory (miss allocator fragmentation + optimizer workspace)
- Variable-length sequences (transformers) have high activation variance
- VeritasEst 2-iteration baseline doesn't capture post-optimizer workspace allocations

### 2.2 Proposed Solution
**3-iteration stratified profiling**:
1. Iteration 1: Capture base model + activation memory
2. Post-optimizer.step: Capture Adam workspace buffers (m_t, v_t)
3. Stratified sampling: Sample P50/P75/P95/P99 length bins (transformers) to address activation variance

### 2.3 Non-Goals (Out of Scope)
- Mixture-of-Experts (MoE) architectures
- Flash Attention / custom kernels
- Multi-GPU distributed training
- Gradient accumulation scenarios
- Model parallelism / pipeline parallelism

---

## 3. Functional Requirements

### FR-1: Memory Profiler Core
**Priority**: P0 (Blocking)

**Requirements**:
- FR-1.1: Implement segment-level memory tracking via `torch.cuda.memory_stats()`
- FR-1.2: Support 3-iteration profiling protocol:
  - Iteration 1: Forward pass only
  - Post-optimizer.step: After backward + optimizer update
  - Stratified sampling: 4 samples from length quantile bins (transformers)
- FR-1.3: Implement 10-iteration ground truth profiling for validation
- FR-1.4: Track peak memory at segment level (not tensor sums)
- FR-1.5: Support memory reset between experiments (`torch.cuda.reset_peak_memory_stats()`)

**Acceptance Criteria**:
- Returns peak memory in MB for any (model, optimizer, batch) triple
- Correctly captures optimizer workspace allocations (Adam m_t/v_t buffers)
- Ground truth values stable across repeated runs (±2% variance)

---

### FR-2: Stratified Length Sampler
**Priority**: P0 (Blocking for transformers)

**Requirements**:
- FR-2.1: Bucket sequences by length into P50/P75/P95/P99 quantile bins
- FR-2.2: Sample 1 batch per bin for memory profiling
- FR-2.3: Compute quantiles from full dataset before sampling
- FR-2.4: Custom collate_fn for variable-length batching (padding to max in batch)

**Acceptance Criteria**:
- Length bins cover full distribution (e.g., WMT-14: ~30/45/65/85 tokens at P50/75/95/99)
- Each bin has ≥100 samples available
- Fixed-length datasets (CIFAR-10, ImageNet) skip stratification (sample randomly)

**Dataset-Specific Behavior**:
- **WMT-14**: Apply stratified sampling (variable-length text)
- **CIFAR-10**: No stratification (fixed 32×32 images)
- **ImageNet-1K**: No stratification (fixed 224×224 crops)

---

### FR-3: Model Registry
**Priority**: P0 (Blocking)

**Requirements**:
- FR-3.1: Support 8 CNN architectures from torchvision:
  - ResNet-18, ResNet-34, ResNet-50
  - VGG-16
  - DenseNet-121
  - MobileNetV2
  - EfficientNet-B0
  - ShuffleNetV2
- FR-3.2: Support 8 transformer architectures from HuggingFace:
  - BERT-base, RoBERTa-base
  - GPT-2-small
  - T5-small
  - DistilBERT
  - ALBERT-base
  - DeBERTa-base
  - ViT-base (vision transformer)
- FR-3.3: Provide unified interface: `get_model(name: str, num_classes: int)`
- FR-3.4: Initialize with standard pretrained weights where available

**Acceptance Criteria**:
- All 16 models load successfully
- Forward pass works on standard inputs (CIFAR-10: 32×32, ImageNet: 224×224, WMT-14: variable tokens)
- Models compatible with Adam/AdamW/SGD optimizers

---

### FR-4: Data Preparation Pipeline
**Priority**: P0 (Blocking)

**Requirements**:
- FR-4.1: **CIFAR-10** (via torchvision.datasets):
  - Download test split (10,000 images)
  - Apply ToTensor() transform
  - Batch size: 128
- FR-4.2: **ImageNet-1K** (via torchvision.datasets):
  - Download validation split (50,000 images)
  - Apply Resize(256) → CenterCrop(224) → ToTensor()
  - Batch size: 64
- FR-4.3: **WMT-14 En-De** (via HuggingFace datasets):
  - Download test split (3,003 sentence pairs)
  - Tokenize with BERT tokenizer (max_length=128)
  - Dynamic batching by length (stratified sampling)
  - Batch size: 32

**Acceptance Criteria**:
- All datasets download automatically (no manual steps)
- Data loaders yield batches in correct format for each model type
- WMT-14 length distribution matches expected quantiles (P50≈30, P75≈45, P95≈65, P99≈85 tokens)

---

### FR-5: Optimizer Configuration
**Priority**: P0 (Blocking)

**Requirements**:
- FR-5.1: Support 3 optimizer variants:
  - **Adam**: β1=0.9, β2=0.999, lr=1e-4
  - **AdamW**: β1=0.9, β2=0.999, lr=1e-4, weight_decay=0.01
  - **SGD**: lr=0.1, momentum=0.9 (control condition - no workspace)
- FR-5.2: Initialize optimizer with model.parameters()
- FR-5.3: Support optimizer.step() after backward pass

**Acceptance Criteria**:
- Adam/AdamW create m_t and v_t buffers (visible in memory stats)
- SGD shows minimal workspace allocation (validates optimizer effect)
- All optimizers complete 10 iterations without OOM

---

### FR-6: Evaluation Harness
**Priority**: P0 (Blocking)

**Requirements**:
- FR-6.1: Compute relative error: `|predicted - ground_truth| / ground_truth`
- FR-6.2: Aggregate errors across all batches per config:
  - Median relative error
  - 95th percentile error
- FR-6.3: Generate per-architecture breakdown (CNN vs transformer)
- FR-6.4: Export results to CSV with columns:
  - model, optimizer, dataset, median_error, p95_error, ground_truth_mb, predicted_mb
- FR-6.5: Statistical testing: Wilcoxon signed-rank test (3-iter vs 2-iter baseline)

**Acceptance Criteria**:
- Median error calculated correctly for all 48 configs
- Results reproducible across runs (deterministic seeding)
- Statistical test reports p-value and effect size

---

### FR-7: Baseline Experiments
**Priority**: P0 (Required for validation)

**Requirements**:
- FR-7.1: **Ground Truth (10-iteration)**:
  - Run full 10 iterations per config
  - Record peak memory at iteration 10 (stabilized state)
  - Store in `ground_truth_results.csv`
- FR-7.2: **Lightweight (3-iteration + stratified)**:
  - Run 3-iteration protocol (see FR-1.2)
  - Predict peak memory: `max(iter1, post_optim, max(stratified_samples))`
  - Store in `lightweight_results.csv`
- FR-7.3: **Ablation (2-iteration)**:
  - Run 2-iteration protocol (VeritasEst baseline)
  - Skip post-optimizer sampling
  - Store in `ablation_2iter_results.csv`

**Acceptance Criteria**:
- Ground truth results show optimizer state stabilization (iteration 10 ≥ iteration 2)
- 3-iteration results outperform 2-iteration (lower median error)
- All results saved with timestamps and config metadata

---

### FR-8: Visualization & Reporting
**Priority**: P1 (Nice-to-have)

**Requirements**:
- FR-8.1: Generate violin plot: Error distribution (CNN vs transformer)
- FR-8.2: Scatter plot: Predicted vs ground truth memory (with correlation R²)
- FR-8.3: Length bin analysis: Error by P50/P75/P95/P99 bins (transformers only)
- FR-8.4: Export summary statistics to Markdown table

**Acceptance Criteria**:
- Visualizations clearly show CNN vs transformer error separation
- Length bin plot demonstrates stratified sampling effectiveness
- Summary table shows all metrics from Section 3 (success criteria)

---

## 4. Data Specification

### 4.1 Input Datasets

| Dataset | Type | Split | Size | Download Method | Purpose |
|---------|------|-------|------|-----------------|---------|
| CIFAR-10 | standard | test | 10,000 images | torchvision.datasets.CIFAR10 | CNN validation (fixed-length) |
| ImageNet-1K | standard | val | 50,000 images | torchvision.datasets.ImageNet | CNN validation (real-world scale) |
| WMT-14 En-De | standard | test | 3,003 pairs | datasets.load_dataset('wmt14', 'de-en') | Transformer validation (variable-length) |

**Total Evaluation Samples**: 63,003

### 4.2 Output Data
- `ground_truth_results.csv`: 48 rows (configs) × 5 columns (model, optimizer, dataset, peak_memory_mb, iteration)
- `lightweight_results.csv`: Same schema + predicted_memory_mb column
- `ablation_2iter_results.csv`: Same schema as lightweight
- `error_analysis.csv`: 48 rows × 7 columns (model, optimizer, dataset, median_error, p95_error, ground_truth_mb, predicted_mb)

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- **Profiling Speed**: Lightweight profiling completes in ≤3 GPU-hours (vs 50 hours for ground truth)
- **Memory Overhead**: Profiler adds <5% memory overhead (instrumentation cost)

### NFR-2: Accuracy
- **Median Error**: ≤10% for CNNs, ≤15% for transformers
- **Worst-Case Error**: P95 ≤25% across all configs

### NFR-3: Reproducibility
- **Deterministic Seeding**: All random operations use fixed seed (42)
- **Version Pinning**: Lock torch==2.0.1, transformers==4.30.0, datasets==2.13.0

### NFR-4: Maintainability
- **Code Structure**: Separate modules for profiler, sampler, models, eval
- **Documentation**: Docstrings for all public APIs
- **Logging**: Progress bars for long-running experiments (tqdm)

---

## 6. Success Metrics

### 6.1 Primary Metrics
- **Median relative error ≤10%** for all 8 CNN architectures
- **Median relative error ≤15%** for all 8 transformer architectures (contingency threshold)
- **P95 error ≤25%** across all 48 configurations

### 6.2 Secondary Metrics
- **Statistical significance**: p < 0.05 vs 2-iteration baseline (Wilcoxon test)
- **Compute efficiency**: 3-iteration profiling ≤10% of 10-iteration time
- **Coverage**: All 16 models × 3 optimizers = 48 configs validated

### 6.3 Failure Thresholds
- If median >15% for transformers → Extend to 5-iteration sampling
- If P95 >30% → Add confidence intervals or architecture-specific calibration
- If statistical test p≥0.05 → Stratified sampling not significantly better than baseline

---

## 7. Dependencies & Constraints

### 7.1 Python Packages
**Core**:
- torch>=2.0.0 (CUDA memory profiling APIs)
- torchvision>=0.15.0 (CNN models + CIFAR-10/ImageNet)
- transformers>=4.30.0 (HuggingFace models)
- datasets>=2.13.0 (WMT-14 loading)

**Utilities**:
- numpy>=1.24.0 (statistical computations)
- pandas>=2.0.0 (CSV export)
- matplotlib>=3.7.0 (visualization)
- scipy>=1.10.0 (Wilcoxon test)
- tqdm>=4.65.0 (progress bars)

### 7.2 Hardware Requirements
- **GPU**: 1× NVIDIA A100 (40GB VRAM) or equivalent
- **Storage**: ~200GB for ImageNet-1K download
- **Compute**: ~53 GPU-hours total (50 ground truth + 3 lightweight)

### 7.3 External Repositories (Reference Only)
- PyTorch CUDA Allocator Source: `c10/cuda/CUDACachingAllocator.cpp`
- VeritasEst Prior Work: `/docs/youra_research/_archive/.../h-m1/src/profiling/profiler.py`

---

## 8. Risk Assessment

### 8.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Allocator simulation fails for transformers | 30% | High | Contingency threshold ≤15% acceptable |
| Gradient accumulation edge cases | 20% | Medium | Scope to validated architectures (no MoE/Flash Attention) |
| ImageNet download timeout | 15% | Low | Use streaming datasets or cached splits |
| WMT-14 length distribution skewed | 10% | Low | Validate quantile bins before profiling |

### 8.2 Timeline Risks
- **ImageNet Download**: ~150GB can take 6-24 hours (bandwidth-dependent)
- **Ground Truth Profiling**: 50 GPU-hours = 2 days on single GPU
- **Mitigation**: Parallelize across multiple GPUs if available

---

## 9. Validation & Testing

### 9.1 Unit Tests
- `test_memory_profiler.py`: Validate reset_stats, get_peak_memory APIs
- `test_stratified_sampler.py`: Validate length bucketing, quantile computation
- `test_model_registry.py`: Validate all 16 models load and forward pass works

### 9.2 Integration Tests
- `test_end_to_end.py`: Run 3-iteration profiling on 1 config, verify error <20%
- `test_ground_truth.py`: Run 10-iteration profiling, verify iteration-10 peak ≥ iteration-2

### 9.3 Acceptance Tests
- Run full 48-config evaluation
- Verify median error meets thresholds (≤10/15%)
- Verify P95 error ≤25%
- Verify statistical test p<0.05

---

## 10. Deliverables

### 10.1 Code Artifacts
1. `src/profiler/segment_memory_profiler.py` - Core profiling logic
2. `src/data/stratified_sampler.py` - Length-based sampling
3. `src/models/registry.py` - Model loading interface
4. `src/eval/error_analysis.py` - Metrics and statistical tests
5. `experiments/run_evaluation.py` - Main experiment script

### 10.2 Data Artifacts
1. `ground_truth_results.csv` - 10-iteration baseline
2. `lightweight_results.csv` - 3-iteration predictions
3. `ablation_2iter_results.csv` - 2-iteration baseline
4. `error_analysis.csv` - Aggregated metrics

### 10.3 Documentation
1. `README.md` - Setup instructions, usage examples
2. `RESULTS.md` - Quantitative results, figures, analysis
3. `04_validation.md` - Phase 4 validation report (MUST_WORK gate)

---

## 11. Timeline & Milestones

### Phase 3 (Implementation Planning)
- **Duration**: 1 week
- **Deliverables**: PRD (this document), Architecture, Logic, Config

### Phase 4 (Implementation)
- **Week 1**: Core profiler + stratified sampler + model registry
- **Week 2**: Data preparation + optimizer configs + evaluation harness
- **Week 3**: Ground truth profiling + lightweight profiling + error analysis

### Phase 4 Gate Check
- **Criteria**: Median error ≤10/15%, P95 ≤25%, p<0.05
- **Action if PASS**: Proceed to h-m1 (orthogonality analysis)
- **Action if FAIL**: Extend to 5-iteration or add confidence intervals → Re-run validation

---

## 12. Open Questions

### 12.1 Resolved
- ✅ Q: Use tensor sums or segment-level memory?  
  A: Segment-level (`torch.cuda.memory_stats()`) - tensor sums underestimate
- ✅ Q: How many iterations needed?  
  A: 3 (iter1 + post-optim + stratified) balances accuracy and speed
- ✅ Q: Length bins for transformers?  
  A: P50/P75/P95/P99 quantiles from full dataset

### 12.2 Deferred to Implementation
- ⏳ Q: Exact quantile thresholds for WMT-14?  
  A: Compute during data preparation (expected ~30/45/65/85 tokens)
- ⏳ Q: Batch size impact on memory?  
  A: Use standard sizes (128 CIFAR, 64 ImageNet, 32 WMT-14) - ablate if needed

---

## 13. Appendix

### 13.1 Hypothesis Context
- **Parent Hypothesis**: None (FOUNDATION)
- **Dependent Hypotheses**: h-m1 (orthogonality), h-m2 (dual-axis routing)
- **Gate Type**: MUST_WORK (blocks h-m1/h-m2 if failed)

### 13.2 Archon References
- **Pipeline Project**: `969e983e-0a40-4910-bedf-4c70577c6f04`
- **Hypothesis Task**: `302fe353-3274-4ac0-ad1b-bab7242aace5`
- **Phase 2C Document**: `h-e1/02c_experiment_brief.md`

### 13.3 Related Documents
- `h-e1/01_hypothesis.md` - Original hypothesis statement
- `h-e1/02b_verification_plan.md` - Research planning context
- `h-e1/02c_experiment_brief.md` - Detailed experiment design (source for this PRD)

---

**Document Status**: COMPLETE  
**Ready for Architecture Design**: YES  
**Next Step**: Phase 3 Architecture Agent (Epic task breakdown)
