# Product Requirements Document: H-E2 SAT Profiler

**Hypothesis ID:** H-E2  
**Hypothesis Type:** EXISTENCE  
**Date:** 2026-07-10  
**Author:** Anonymous  
**Version:** 1.0  

---

## Executive Summary

### Purpose
Implement a GPU-normalized SAT (Stall-time Amplitude Throughput) profiling system to validate whether batch time variance can predict epoch-time degradation in deep learning training workloads with ≥80% precision.

### Scope
Profiling validation experiment across 48 natural training configurations (16 models × 3 optimizers/datasets) plus synthetic jitter causality tests. This is NOT a production system but a research validation tool.

### Success Criteria
- Precision ≥0.80 for predicting ≥15% epoch degradation when SAT >1.5
- Recall ≥0.70 (acceptable false negatives)
- Synthetic jitter validates causal link (SAT increases only when GPU utilization drops)

---

## Problem Statement

### Background
Current throughput risk assessment in training experiments relies on epoch-time extrapolation from 20-batch timing, which assumes uniform batch time distribution and cannot isolate data loading bottlenecks from system noise.

### User Pain Points
1. Cannot predict which training configs will experience epoch-time degradation
2. Batch time variance not distinguished from GPU compute variance
3. No causal metric isolating data loading bottlenecks

### Hypothesis
GPU-normalized SAT (P95/Median batch time × GPU utilization fraction) causally predicts ≥15% epoch-time degradation with ≥80% precision when GPU utilization <90%.

---

## Functional Requirements

### FR-1: Profiling Infrastructure

**FR-1.1: SATProfiler Class**
- Measure per-batch timing with torch.cuda.synchronize()
- Track GPU utilization via torch.cuda.utilization()
- Compute SAT = (P95/Median) × (GPU_util / 100)
- Store batch times and GPU utilization lists

**FR-1.2: Batch Time Measurement**
- `profile_step(model, batch, optimizer, criterion)` → batch_time
- Synchronize before/after training step
- Record time for forward + backward + optimizer step

**FR-1.3: Epoch Time Validation**
- `measure_epoch_time(dataloader)` → total_epoch_time
- Profile ALL batches in one epoch
- Calculate degradation vs baseline

### FR-2: Natural Workload Experiments

**FR-2.1: CNN Profiling (24 configs)**
- **Models (8):** ResNet-18, ResNet-50, VGG-16, EfficientNet-B0, DenseNet-121, MobileNetV2, ShuffleNetV2, SqueezeNet
- **Datasets:** CIFAR-10, ImageNet subset
- **Optimizers:** SGD, Adam, AdamW
- **Batch sizes:** 16-128 (vary by model size)
- **Duration:** 50 batches for SAT + 1 epoch for validation

**FR-2.2: Transformer Profiling (24 configs)**
- **Models (8):** GPT-2-small, BERT-base, T5-small, DistilBERT, RoBERTa-base, ALBERT-base, ELECTRA-small, DeBERTa-base
- **Datasets:** WildChat, PersonaChat
- **Optimizers:** Adam, AdamW, Adafactor
- **Sequence lengths:** 128-512
- **Duration:** 50 batches for SAT + 1 epoch for validation

**FR-2.3: Configuration Management**
- Store config metadata: model_name, dataset, optimizer, batch_size, SAT, epoch_time, degradation
- Save per-config profiling logs

### FR-3: Synthetic Jitter Experiments

**FR-3.1: Controlled Delay Injection**
- Inject time.sleep() in DataLoader between batches
- Delay levels: 0ms (control), 50ms, 100ms, 200ms
- Measure SAT increase vs baseline

**FR-3.2: Causality Validation**
- Verify SAT increases proportionally with injected delay
- Verify effect only appears when GPU utilization drops
- Compare high GPU util configs (>90%) vs low (<90%)

### FR-4: Evaluation Metrics

**FR-4.1: Degradation Prediction**
- Binary classification: ≥15% degradation (positive class)
- Threshold: SAT > 1.5
- Metrics: Precision, Recall, F1-score (sklearn.metrics)

**FR-4.2: Success Thresholds**
- Precision ≥ 0.80 (target)
- Recall ≥ 0.70 (target)
- F1-score ≥ 0.75 (derived)

**FR-4.3: Causality Metrics**
- Correlation: SAT_jitter vs injected_delay
- Conditional effect: SAT increase only when GPU_util <90%

### FR-5: Visualization

**FR-5.1: Required Figures**
- SAT vs Epoch Degradation scatter plot (with decision boundary)
- Precision-Recall curve (varying SAT threshold)
- Synthetic jitter validation (SAT vs delay, stratified by GPU util)
- Per-architecture SAT distribution (violin plot)
- Confusion matrix (TP/FP/TN/FN)

**FR-5.2: Figure Output**
- Save to `{hypothesis_folder}/figures/`
- Format: PNG, 300 DPI
- Include gate metrics comparison bar chart

---

## Data Requirements

### DR-1: Dataset Downloads

**DR-1.1: CNN Datasets**
```python
# CIFAR-10
torchvision.datasets.CIFAR10(root='./data', train=True, download=True)

# ImageNet subset (1000 classes)
torchvision.datasets.ImageNet(root='./data/imagenet', split='train')
```

**DR-1.2: Transformer Datasets**
```python
# WildChat (10k samples)
from datasets import load_dataset
load_dataset("Anthropic/wildchat-1m", split="train[:10000]")

# PersonaChat (8k samples)
load_dataset("bavard/personachat_truecased", split="train")
```

### DR-2: Model Loading

**DR-2.1: CNN Models**
```python
import torchvision.models as models
# ResNet-18, ResNet-50, VGG-16, EfficientNet-B0, DenseNet-121, 
# MobileNetV2, ShuffleNetV2, SqueezeNet
model = models.resnet18(pretrained=True)
```

**DR-2.2: Transformer Models**
```python
from transformers import AutoModel, AutoModelForCausalLM
# GPT-2, BERT-base, T5-small, DistilBERT, RoBERTa, ALBERT, ELECTRA, DeBERTa
model = AutoModelForCausalLM.from_pretrained("gpt2")
```

### DR-3: Preprocessing

**DR-3.1: CNN Preprocessing**
- Normalization: ImageNet mean/std
- Resize: 224×224
- Augmentation: RandomHorizontalFlip, RandomCrop (training only)

**DR-3.2: Transformer Preprocessing**
- Tokenization: max_length 128-512
- Padding/truncation to fixed length
- No augmentation (natural sequence variation)

---

## Non-Functional Requirements

### NFR-1: Performance

**NFR-1.1: Profiling Overhead**
- Batch time measurement overhead <5% of actual batch time
- torch.cuda.synchronize() only at profiling points

**NFR-1.2: Execution Time**
- Per-config profiling: ~2 hours (50 batches + 1 epoch)
- Total experiment: ~96 GPU-hours (48 configs × 2 hours)

### NFR-2: Reproducibility

**NFR-2.1: Seeding**
- Fixed seed: 42
- Seed torch, numpy, random
- Deterministic CUDA operations where possible

**NFR-2.2: Environment**
- PyTorch ≥2.0
- CUDA 11.8+
- Single GPU execution (no DDP for profiling)

### NFR-3: Data Management

**NFR-3.1: Output Structure**
```
{hypothesis_folder}/
  03_prd.md (this file)
  03_architecture.md
  03_logic.md
  03_config.md
  03_tasks.yaml
  data/
    cifar10/
    imagenet/
    wildchat/
    personachat/
  results/
    profiling_results.json
    metrics_summary.json
  figures/
    sat_vs_degradation.png
    precision_recall_curve.png
    jitter_validation.png
    architecture_sat_dist.png
    confusion_matrix.png
```

**NFR-3.2: Result Logging**
- JSON format for structured results
- CSV format for per-config metrics
- Log file for execution trace

### NFR-4: Error Handling

**NFR-4.1: Dataset Download Failures**
- Retry with exponential backoff (3 attempts)
- Skip config if dataset unavailable, log warning

**NFR-4.2: Model Loading Failures**
- Catch HuggingFace/torchvision errors
- Skip config, continue experiment

**NFR-4.3: CUDA OOM**
- Reduce batch size by 50%
- Retry once with smaller batch
- Skip config if still fails

---

## Dependencies

### Internal Dependencies
- Phase 2C experiment brief (02c_experiment_brief.md)
- verification_state.yaml (hypothesis status)

### External Dependencies
- PyTorch ≥2.0
- torchvision
- transformers (HuggingFace)
- datasets (HuggingFace)
- scikit-learn (metrics)
- numpy, matplotlib, seaborn

### Hardware Dependencies
- NVIDIA GPU with CUDA support
- Minimum 16GB GPU memory (for largest models)
- 100GB disk space (datasets + checkpoints)

---

## Success Metrics

### Primary Metrics
1. **Precision ≥ 0.80** for SAT >1.5 predicting ≥15% degradation
2. **Recall ≥ 0.70** for same threshold
3. **Synthetic jitter causality**: SAT increases only when GPU util <90%

### Secondary Metrics
- F1-score ≥ 0.75
- Per-architecture SAT variance >0.1 (validates measurement sensitivity)
- All 48 configs profiled successfully (100% completion rate)

### Gate Compliance
- **Gate Type:** MUST_WORK
- **Pass Condition:** Precision ≥0.80 AND Recall ≥0.70 AND Causality validated
- **Fail Consequence:** SAT contaminated by non-accessibility variance → Multi-source decomposition needed → Workflow stops

---

## Out of Scope

### Explicitly Excluded
- Production deployment of profiling system
- Multi-GPU profiling (DDP, FSDP)
- Streaming/online profiling during live training
- Automated bottleneck remediation
- Integration with existing ML platforms

### Future Enhancements (Post-Gate)
- Real-time profiling dashboard
- Automated DataLoader tuning recommendations
- Integration with H-E1 (MSI) for joint profiling

---

## Risks and Mitigation

### Risk 1: Dataset Download Failures
- **Probability:** Medium
- **Impact:** Blocks experiment execution
- **Mitigation:** Pre-download datasets, fallback to cached versions

### Risk 2: GPU Utilization API Unavailable
- **Probability:** Low
- **Impact:** Cannot compute GPU-normalized SAT
- **Mitigation:** Fallback to nvidia-smi polling, manual GPU util estimation

### Risk 3: High Profiling Overhead
- **Probability:** Medium
- **Impact:** SAT measurement contaminated by profiling overhead
- **Mitigation:** Validate overhead <5%, use torch.profiler for low-overhead measurement

### Risk 4: SAT Fails to Predict Degradation
- **Probability:** Medium (this is what experiment validates)
- **Impact:** Hypothesis MUST_WORK gate fails
- **Mitigation:** Contingency: Multi-source variance decomposition in follow-up hypothesis

---

## Appendix

### A. Phase 2C Traceability

| Phase 2C Item | PRD Section |
|---------------|-------------|
| 16 baseline models | FR-2.1, FR-2.2 |
| 48 configs | FR-2.1, FR-2.2 |
| Synthetic jitter | FR-3 |
| Precision/Recall metrics | FR-4 |
| 5 visualization requirements | FR-5 |
| Dataset specifications | DR-1 |
| Preprocessing | DR-3 |

### B. Baseline Comparison
- **Current Baseline:** 20-batch timing extrapolation (assumes uniform distribution)
- **Proposed SAT:** P95/Median × GPU_util (models variance + isolates accessibility)
- **Expected Improvement:** From 50% random prediction to ≥80% precision

### C. Archon Task Scope
This experiment requires:
- **Infrastructure tasks:** 2-3 (dataset download, environment setup)
- **Profiling tasks:** 4-6 (SATProfiler, natural workload, synthetic jitter)
- **Evaluation tasks:** 2-3 (metrics, visualization)
- **Total:** ≤15 tasks (LIGHT budget for EXISTENCE hypothesis)

---

**Document Status:** ✅ Complete  
**Next Phase:** Architecture Design (03_architecture.md)  
**Gate Status:** MUST_WORK (not yet tested)
