# Phase 2C: Experiment Design Brief
## H-E1: Segment-level MSI from 3-iteration sampling

**Hypothesis ID**: h-e1  
**Generated**: 2026-07-10T17:10:00Z  
**Pipeline Project**: `969e983e-0a40-4910-bedf-4c70577c6f04`  
**Archon Parent Task**: `302fe353-3274-4ac0-ad1b-bab7242aace5`

---

## 1. Hypothesis Statement

**Statement**: 3-iteration stratified sampling (1st iteration, post-optimizer.step, P50/P75/P95/P99 length bins) predicts 10-iteration segment peak memory with ≤10% median relative error for CNNs, ≤15% for transformers.

**Type**: EXISTENCE (validates that MSI can be measured accurately)  
**Gate**: MUST_WORK (blocks downstream hypotheses h-m1, h-m2 if failed)

---

## 2. Research Context & Motivation

### 2.1 Background from Phase 2B

From verification plan (02b_verification_plan.md):
- VeritasEst demonstrated 2-iteration optimizer state stabilization
- Stratified sampling addresses activation memory variance via length quantiles
- Segment-level simulation (BFC allocator) is non-negotiable for memory prediction
- Tensor sums fail under Adam optimizer due to workspace allocations

### 2.2 Why This Matters

**Critical Path Position**: h-e1 is the foundation for the dual-axis framework:
- Enables MSI (Memory Stress Index) calculation for 4-quadrant routing
- Validates that lightweight profiling (3 iterations vs 10 full iterations) is accurate
- Blocks h-m1 orthogonality analysis (requires validated MSI values)

**Falsification Risk**: If median error >15% or P95 >30%, stratified sampling is insufficient → fallback to 5-iteration or confidence intervals

---

## 3. Success Criteria (from 02b)

### 3.1 Primary Metrics
- **Median relative error ≤10%** for CNNs (8 architectures: ResNet-18/34/50, VGG-16, DenseNet-121, MobileNetV2, EfficientNet-B0, ShuffleNetV2)
- **Median relative error ≤15%** for transformers (8 architectures: BERT-base, GPT-2-small, DistilBERT, RoBERTa-base, T5-small, ALBERT-base, DeBERTa-base, ViT-base)
- **95th percentile error ≤25%** across all 16 models

### 3.2 Validation Scope
- **48 configuration matrix**: 16 models × 3 optimizers (Adam, AdamW, SGD) × variable batch sizes
- **Dataset diversity**: CIFAR-10 (fixed-length), WMT-14 En-De (variable-length), ImageNet-1K (for CNNs)
- **Length distribution coverage**: P50/P75/P95/P99 bins for transformers to capture activation variance

### 3.3 Falsification Thresholds
- If median >15% → Extend to 5-iteration sampling
- If P95 >30% → Add confidence intervals or architecture-specific calibration

---

## 4. Experimental Design

### 4.1 Dataset Specification

| Dataset | Type | Purpose | Split | Sample Size | Justification |
|---------|------|---------|-------|-------------|---------------|
| **CIFAR-10** | standard | CNN validation (fixed-length images) | test | 10,000 images | Standard benchmark, eliminates length variance, tests allocator on pure CNN workloads |
| **ImageNet-1K** | standard | CNN validation (real-world scale) | val | 50,000 images | Real-world image classification, tests allocator under production-scale data |
| **WMT-14 En-De** | standard | Transformer validation (variable-length text) | test | 3,003 sentence pairs | Standard MT benchmark, long-tail length distribution (critical for stratified sampling validation) |

**Dataset Type Policy**: ALL datasets are real, established benchmarks (CIFAR-10/ImageNet/WMT-14). NO synthetic/simulated data.

**Why these datasets**:
1. **CIFAR-10**: Eliminates confounding length variance for CNNs (32×32 fixed size)
2. **ImageNet-1K**: Tests allocator generalization to production-scale images (224×224 typical)
3. **WMT-14**: Provides natural length variance (10-100 tokens) to validate stratified sampling bins

**Sample Size Justification**:
- CIFAR-10 test set: 10,000 samples (full standard split)
- ImageNet-1K val set: 50,000 samples (full standard split)
- WMT-14 test set: 3,003 pairs (full standard split)
- Total evaluation samples: 63,003 (statistically robust across 48 configs)

### 4.2 Profiling Protocol

**Ground Truth Collection** (10-iteration full profiling):
1. Initialize model + optimizer on GPU
2. Run 10 iterations with torch.cuda.memory_stats() instrumentation
3. Record segment-level peak memory at iteration 10 (after optimizer state stabilizes)
4. Use PyTorch memory profiler with BFC allocator simulation (see Implementation Search below)

**Lightweight Profiling** (3-iteration stratified):
1. **Iteration 1**: Initial forward pass (measures base model + activation memory)
2. **Post-optimizer.step**: After first backward + optimizer update (captures workspace allocations)
3. **Stratified sampling**: For transformers, sample 4 batches from P50/P75/P95/P99 length bins
   - CIFAR-10/ImageNet: No stratification (fixed-length)
   - WMT-14: Bucket sentences by length → sample 1 batch per quantile bin

**Why 3 iterations + stratification**:
- Iteration 1 captures activation memory baseline
- Post-optimizer.step captures Adam workspace (m_t, v_t buffers)
- Stratified bins address M_act variance from variable-length sequences (critical for transformers)

### 4.3 Architecture Matrix

**CNNs (8 architectures)**:
- ResNet-18, ResNet-34, ResNet-50 (depth scaling)
- VGG-16 (sequential convolutions, high memory)
- DenseNet-121 (feature concatenation patterns)
- MobileNetV2 (depthwise separable convs)
- EfficientNet-B0 (compound scaling)
- ShuffleNetV2 (channel shuffle operations)

**Transformers (8 architectures)**:
- BERT-base, RoBERTa-base (encoder-only, 12 layers)
- GPT-2-small (decoder-only, 12 layers)
- T5-small (encoder-decoder, 6+6 layers)
- DistilBERT (knowledge distillation, 6 layers)
- ALBERT-base (parameter sharing)
- DeBERTa-base (disentangled attention)
- ViT-base (vision transformer, patch embeddings)

**Optimizer Configurations**:
- Adam (β1=0.9, β2=0.999, lr=1e-4)
- AdamW (β1=0.9, β2=0.999, lr=1e-4, weight_decay=0.01)
- SGD (lr=0.1, momentum=0.9, no workspace allocations → control condition)

**Total Configs**: 16 models × 3 optimizers = **48 configurations**

### 4.4 Evaluation Metrics

For each configuration (model, optimizer, dataset):

**Relative Error** = |predicted_memory - ground_truth_memory| / ground_truth_memory

**Aggregation**:
- **Median relative error** across all batches (robust to outliers)
- **95th percentile error** (captures worst-case predictions)
- **Per-architecture breakdown** (CNN vs transformer analysis)

**Success Definition**:
- Median ≤ 10% for CNNs
- Median ≤ 15% for transformers (contingency threshold)
- P95 ≤ 25% across all models

---

## 5. Implementation Search (MCP-Powered)

### 5.1 Archon Knowledge Base Findings

**Query**: "memory profiling iteration sampling CNN transformer accuracy"

**Relevant Sources**:
1. **PixArt-alpha** (GitHub): Diffusion model with memory-efficient attention
   - Implements gradient checkpointing + memory tracking
   - Demonstrates multi-iteration profiling patterns
2. **HuggingFace Transformers**: Standard model implementations
   - Provides pretrained BERT/GPT-2/T5 models
   - Includes memory optimization utilities
3. **Apple Neural Engine Transformers**: On-device transformer optimization
   - Memory profiling techniques for constrained devices

### 5.2 Exa Implementation Search

**Query**: "PyTorch memory profiling segment simulation BFC allocator"

**Key Findings**:
1. **PyTorch CUDA Caching Allocator Documentation** (2026-06-01 DevLog)
   - Explains BFC allocator fragmentation patterns
   - Source: `c10/cuda/CUDACachingAllocator.cpp`
   - Memory visualization: `torch/cuda/_memory_viz.py`

2. **PyTorch Memory Profiler API**:
   - `torch.cuda.memory_stats()` for segment-level metrics
   - `torch.cuda.max_memory_allocated()` for peak tracking
   - `torch.profiler.profile()` with memory_profile=True

**Query**: "stratified sampling batch length bins CNN transformer training"

**Key Findings**:
1. **Variance Reduced Training with Stratified Sampling** (arXiv:2103.02062)
   - Demonstrates stratified sampling for forecasting models
   - Validates variance reduction from length-based binning

2. **TensorFlow bucket_by_sequence_length API**:
   - Reference for length-based batching
   - PyTorch equivalent: custom collate_fn with length bucketing

3. **NeMo Sequence Packing** (NVIDIA docs):
   - Length-aware batching for LLMs
   - Demonstrates P50/P75/P95/P99 quantile binning

### 5.3 Archived Implementation Reference

From `/docs/youra_research/_archive/.../h-m1/src/profiling/profiler.py`:
- `AttentionMemoryProfiler` class implements:
  - `reset_memory_stats()` → `torch.cuda.reset_peak_memory_stats()`
  - `get_peak_memory_mb()` → `torch.cuda.max_memory_allocated() / (1024**2)`
  - `profile_batch()` → forward pass + memory capture

**Reusable Pattern**:
```python
self.reset_memory_stats()
with torch.no_grad():
    _ = self.model(input_ids, attention_mask=attention_mask)
peak_memory_mb = self.get_peak_memory_mb()
```

---

## 6. Baseline Experiments

### 6.1 Ground Truth Baseline (10-iteration profiling)

**Purpose**: Establish reference memory values for comparison

**Protocol**:
1. For each of 48 configs (model, optimizer, dataset):
   - Run 10 full training iterations (forward + backward + optimizer.step)
   - Track memory at each iteration with `torch.cuda.memory_stats()`
   - Record peak memory at iteration 10 (stabilized optimizer state)
2. Store ground truth values: `ground_truth[model][optimizer] = peak_memory_mb`

**Expected Compute**: 48 configs × 10 iterations × (100 batches per dataset) = ~50 GPU-hours

### 6.2 Lightweight Profiling (3-iteration + stratified)

**Purpose**: Test if 3-iteration sampling achieves ≤10/15% error vs ground truth

**Protocol**:
1. For each config:
   - **Iteration 1**: Forward pass only → measure M_model + M_act
   - **Post-optimizer.step**: After backward + update → measure M_workspace
   - **Stratified sampling** (transformers only):
     - Bucket batches by length (P50/P75/P95/P99 bins)
     - Profile 1 batch per bin (4 batches total)
   - **Fixed-length** (CNNs):
     - Profile 4 random batches (no stratification needed)
2. Predict peak memory: `max(iteration_1_mem, post_optim_mem, max(stratified_samples))`
3. Compute relative error vs ground truth

**Expected Compute**: 48 configs × 3 iterations × (20 batches) = ~3 GPU-hours

### 6.3 Ablation: 2-iteration (VeritasEst baseline)

**Purpose**: Validate that 3-iteration + stratified outperforms 2-iteration

**Protocol**:
- Same as 6.2 but without post-optimizer.step sampling
- Only uses iteration 1 + iteration 2 (pre-optimizer state)

**Expected Result**: Higher error for transformers (misses workspace allocations)

---

## 7. Validation Protocol

### 7.1 Statistical Tests

**Primary Comparison**:
- H0: Median relative error ≥ 10% (for CNNs) or ≥15% (for transformers)
- H1: Median relative error < thresholds
- Test: Wilcoxon signed-rank test (non-parametric, robust to outliers)
- Significance: p < 0.05

**Secondary Analysis**:
- Per-architecture breakdown (identify failure modes)
- Optimizer effect (SGD vs Adam/AdamW)
- Length distribution impact (CIFAR vs WMT-14)

### 7.2 Failure Mode Analysis

If median error >15%:
1. **Diagnose root cause**:
   - Transformer-specific? → Check stratified bin coverage
   - Optimizer-specific? → Validate workspace allocation tracking
   - Dataset-specific? → Length distribution analysis
2. **Contingency actions**:
   - Extend to 5-iteration sampling
   - Add confidence intervals (±20% tolerance)
   - Architecture-specific calibration

### 7.3 Success Gate

**MUST_WORK criteria** (blocks h-m1 if failed):
- [x] Median ≤10% for CNNs OR Median ≤15% for all models (contingency)
- [x] P95 ≤25% across all 48 configs
- [x] Statistically significant improvement over 2-iteration baseline (p<0.05)

---

## 8. Implementation Roadmap (for Phase 3)

### 8.1 Core Components

1. **Memory Profiler** (`src/profiler/segment_memory_profiler.py`)
   - BFC allocator simulation (via `torch.cuda.memory_stats()`)
   - 3-iteration + stratified sampling logic
   - Ground truth 10-iteration profiling

2. **Stratified Sampler** (`src/data/stratified_sampler.py`)
   - Length-based bucketing (P50/P75/P95/P99 quantiles)
   - Custom collate_fn for variable-length batching

3. **Model Registry** (`src/models/registry.py`)
   - 8 CNN architectures (torchvision models)
   - 8 transformer architectures (HuggingFace transformers)

4. **Evaluation Harness** (`src/eval/error_analysis.py`)
   - Relative error computation
   - Statistical tests (Wilcoxon signed-rank)
   - Per-architecture breakdown

### 8.2 Data Preparation

**CIFAR-10** (via torchvision):
```python
from torchvision import datasets, transforms
test_dataset = datasets.CIFAR10(root='./data', train=False, download=True,
                                transform=transforms.ToTensor())
```

**ImageNet-1K** (via torchvision):
```python
val_dataset = datasets.ImageNet(root='./data/imagenet', split='val',
                                transform=transforms.Compose([
                                    transforms.Resize(256),
                                    transforms.CenterCrop(224),
                                    transforms.ToTensor()
                                ]))
```

**WMT-14 En-De** (via HuggingFace datasets):
```python
from datasets import load_dataset
wmt14 = load_dataset('wmt14', 'de-en', split='test')
```

### 8.3 Compute Requirements

**Hardware**: 1× NVIDIA A100 (40GB VRAM) or equivalent
**Duration**:
- Ground truth profiling: ~50 GPU-hours
- Lightweight profiling: ~3 GPU-hours
- Total: **~53 GPU-hours** (~$55 at $1/GPU-hour)

**Bottlenecks**:
- ImageNet download (~150GB)
- WMT-14 tokenization (can cache)

---

## 9. Expected Outcomes & Deliverables

### 9.1 Quantitative Results

**Tables**:
1. **Error by Architecture** (16 rows: 8 CNNs + 8 transformers)
   - Columns: Median error, P95 error, Ground truth memory (MB), Predicted memory (MB)
2. **Error by Optimizer** (3 rows: Adam, AdamW, SGD)
   - Demonstrates workspace allocation impact
3. **Ablation Comparison** (2-iter vs 3-iter stratified)
   - Validates VeritasEst improvement

**Figures**:
1. **Error distribution** (violin plot: CNN vs transformer)
2. **Scatter plot**: Predicted vs ground truth memory (correlation analysis)
3. **Length bin analysis**: Error by P50/P75/P95/P99 bins (transformers only)

### 9.2 Qualitative Analysis

**Success scenario** (median ≤10/15%):
- Confirms stratified sampling addresses activation variance
- Validates BFC allocator simulation for segment-level prediction
- Gates open for h-m1 (orthogonality analysis)

**Failure scenario** (median >15%):
- Root cause diagnosis (transformer-specific? optimizer-specific?)
- Contingency: Extend to 5-iteration or add confidence intervals
- Document limitations (e.g., MoE/Flash Attention excluded)

### 9.3 Archon Deliverables

**Outputs for Phase 3**:
1. `02c_experiment_brief.md` (this document) → PRD input
2. Implementation search summaries → Architecture design
3. Dataset specifications → Data preparation tasks
4. Validation protocol → Test harness design

**Archon Task Updates**:
- Mark Phase 2C task (`b4eb551b-1b85-48c8-8ba5-e061c242803b`) as DONE
- Create Phase 3 subtasks for h-e1 implementation

---

## 10. Risk Mitigation

### 10.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Allocator simulation fails for transformers | 30% | High | Contingency threshold ≤15% acceptable |
| Gradient accumulation edge cases | 20% | Medium | Scope to validated architectures (no MoE/Flash Attention) |
| ImageNet download timeout | 15% | Low | Use streaming datasets or cached splits |
| WMT-14 length distribution skewed | 10% | Low | Validate quantile bins (P50/P75/P95/P99) |

### 10.2 Timeline Risks

**Estimated Phase 2C Duration**: Completed (this document)  
**Estimated Phase 3 Duration**: 1 week (PRD + Architecture)  
**Estimated Phase 4 Duration**: 3 weeks (implementation + validation)

**Critical Path**: h-e1 (3 weeks) → h-m1 (1 week) → h-m2 (2 weeks) → Phase 5 (4 weeks)

**Slack**: 2 weeks built into 12-week total timeline

---

## 11. Hypothesis Loop Integration

### 11.1 State Transitions

**Current State** (from verification_state.yaml):
- `status: IN_PROGRESS` (Phase 2C executing)
- `experiment_design.status: NOT_STARTED` → `COMPLETED` (after this document)

**Next State** (after Phase 2C):
- `experiment_design.status: COMPLETED`
- `experiment_design.completed_at: 2026-07-10T17:10:00Z`
- `route_to: phase3` (triggers PRD generation)

### 11.2 Archon Task Mapping

**Parent Task**: `302fe353-3274-4ac0-ad1b-bab7242aace5` (h-e1)  
**Phase 2C Task**: `b4eb551b-1b85-48c8-8ba5-e061c242803b`

**Subtasks to Create (Phase 3)**:
1. PRD: Memory profiler specification
2. Architecture: Segment-level BFC simulator design
3. Architecture: Stratified sampler design
4. PRP: Phase 4 coding plan

---

## 12. References

### 12.1 Prior Art
- VeritasEst: 2-iteration optimizer state stabilization (from Phase 2B context)
- PyTorch CUDA Allocator: BFC fragmentation patterns (2026-06-01 DevLog)
- Stratified Sampling for Forecasting: Variance reduction (arXiv:2103.02062)

### 12.2 Datasets
- CIFAR-10: https://www.cs.toronto.edu/~kriz/cifar.html
- ImageNet-1K: https://image-net.org/
- WMT-14 En-De: https://huggingface.co/datasets/wmt14

### 12.3 Model Implementations
- torchvision.models: ResNet, VGG, DenseNet, MobileNet, EfficientNet, ShuffleNet
- transformers (HuggingFace): BERT, GPT-2, T5, DistilBERT, RoBERTa, ALBERT, DeBERTa, ViT

---

## Appendix A: Length Distribution Analysis (WMT-14)

**Purpose**: Validate stratified sampling bin boundaries

**Protocol**:
1. Load WMT-14 test set (3,003 pairs)
2. Tokenize with standard BERT tokenizer
3. Compute length quantiles:
   - P50: ~30 tokens
   - P75: ~45 tokens
   - P95: ~65 tokens
   - P99: ~85 tokens
4. Create 4 buckets: [0-30], [31-45], [46-65], [66+]
5. Sample 1 batch per bucket for profiling

**Validation**: Ensures stratified sampling covers full length distribution

---

## Appendix B: BFC Allocator Simulation Details

**PyTorch Memory API**:
- `torch.cuda.memory_stats()`: Returns segment-level allocator metrics
  - `allocated_bytes.all.current`: Active allocations
  - `reserved_bytes.all.current`: Total reserved from GPU
  - `num_alloc_retries`: Fragmentation indicator
- `torch.cuda.max_memory_allocated()`: Peak memory since last reset

**Segment-level vs Tensor-level**:
- Tensor sums (Σ tensor.nbytes) **underestimate** due to:
  1. Allocator fragmentation (BFC best-fit bins)
  2. Optimizer workspace (Adam m_t, v_t buffers)
  3. Gradient accumulation buffers
- Segment-level (`memory_stats()`) captures **actual GPU memory usage**

**Why 3 iterations**:
- Iteration 1: Model + activations allocated
- Post-optimizer.step: Workspace buffers allocated (Adam-specific)
- Iteration 3: Stabilized allocator state (fragmentation settled)

---

**Document Status**: COMPLETE  
**Ready for Phase 3**: YES  
**Estimated Phase 3 Start**: 2026-07-10 (immediately after this document)
