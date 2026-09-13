# Product Requirements Document: H-M3 Checkpoint Extraction Feasibility

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Date:** 2026-07-11  
**Phase:** 3 (Implementation Planning)  
**Author:** Anonymous

---

## Executive Summary

### Purpose
Validate that architectural features can be extracted from PyTorch model checkpoints in <10 minutes for 50 models using checkpoint-only inspection (weights_only=True), without forward passes or GPU usage. This proves practical feasibility as a core contribution differentiator vs. baseline methods requiring 30+ minutes and GPU infrastructure.

### Problem Statement
Existing methods for extracting model architectural signatures require expensive forward passes (Zhang & Abdulla 2023: ~30 min for 50 models + GPU) or graph neural network construction (Kofinas 2024: ~50+ hours). We hypothesize that checkpoint-only inspection provides 5-6x speedup with zero GPU usage, enabling practical deployment without infrastructure overhead.

### Success Criteria (MUST_WORK Gate)
- **Primary:** Total extraction time <10 minutes (600 seconds) for 50 TIMM models
- **Secondary:** GPU memory usage = 0 MB throughout extraction (CPU-only verification)
- **Correctness:** 100% feature equivalence with H-E1 cached features (cosine similarity = 1.0)
- **Practical Advantage:** >3x speedup vs forward-pass baseline (5-model subset comparison)

### Scope
**In Scope:**
- Checkpoint-only extraction using `torch.load(weights_only=True)` for 50 TIMM models
- Timing benchmarking: total time, per-model average, 90th percentile
- GPU memory monitoring: continuous polling during extraction
- Forward-pass baseline comparison (5-model subset)
- Feature equivalence validation against H-E1 cached features
- Scalability analysis: extrapolate to 100-model, 200-model scenarios

**Out of Scope:**
- GNN baseline implementation (Kofinas 2024: would require 50+ hours per Phase 2B)
- Parallel extraction optimization (future work if sequential fails)
- Production deployment infrastructure (CI/CD, API wrapper)

---

## Functional Requirements

### FR1: Checkpoint-Only Extraction (Primary Method)
**Description:** Extract architectural features from PyTorch checkpoints without model instantiation or forward passes.

**Acceptance Criteria:**
- Load 50 TIMM model checkpoints using `torch.load(checkpoint_path, weights_only=True)`
- Extract features via state_dict key regex matching and tensor shape inspection
- No model instantiation via `timm.create_model()` or forward passes
- Support CNNs (20 models), Transformers (20 models), Hybrids (10 models)
- Extracted features: `bn_count`, `ln_count`, `gn_count`, `no_norm_flag`, `param_mass_ratio`
- Per-model extraction time logged to JSON (for granular analysis)

**Dependencies:**
- H-E1 feature extraction logic (StatisticalFeatureExtractor class)
- H-M2 parameter counting infrastructure (param_mass_ratio computation)

**Data Inputs:**
- TIMM model checkpoints (cached in H-E1 data directory)
- Model list: CNNs (ResNet, EfficientNet, RegNet, DenseNet, MobileNet), Transformers (ViT, DeiT, Swin, BEiT, ConvNeXt, PoolFormer), Hybrids (CoAtNet, MaxViT, CrossViT)

**Outputs:**
- `results/checkpoint_only_timings.json`: Per-model extraction times
- `results/checkpoint_only_features.csv`: Extracted features (50 rows × 5 features)

### FR2: Forward-Pass Baseline Extraction
**Description:** Extract features WITH model instantiation and forward pass for timing comparison baseline.

**Acceptance Criteria:**
- Load 5-model subset via `timm.create_model(model_name, pretrained=True)`
- Run 1 dummy forward pass per model (batch_size=1, input shape=1×3×224×224)
- Extract features from `model.state_dict()` using same logic as FR1
- Measure total time (includes model instantiation + weight loading + inference)
- Free GPU memory after each model (`torch.cuda.empty_cache()`)

**Data Inputs:**
- 5-model subset: ResNet50, ViT-B/16, EfficientNet-B0, DeiT-S, Swin-T (covers CNN, Transformer, efficient variants)

**Outputs:**
- `results/forward_pass_timings.json`: Per-model extraction times
- `results/speedup_analysis.json`: Ratio of forward-pass time / checkpoint-only time

### FR3: High-Precision Timing Measurement
**Description:** Measure extraction time with nanosecond precision and exclude first-time download overhead.

**Acceptance Criteria:**
- Use `time.perf_counter()` for high-resolution timing (not `time.time()`)
- Warmup run: Extract 1 model before starting timer (avoid cold-start overhead)
- Report both "first-run" (includes checkpoint download) and "cached-run" (cached checkpoints) timings
- Log timestamps: start_time, end_time, per_model_times
- Calculate metrics: total_time, avg_time, median_time, 90th_percentile_time

**Outputs:**
- `results/timing_report.md`: Markdown summary with timing statistics
- `results/timing_comparison.png`: Bar chart (checkpoint-only vs forward-pass)

### FR4: GPU Memory Monitoring
**Description:** Continuously monitor GPU memory usage during checkpoint-only extraction to verify CPU-only claim.

**Acceptance Criteria:**
- Poll `torch.cuda.memory_allocated()` every 0.1 seconds during extraction
- Use `nvidia-smi --query-gpu=memory.used --format=csv` as secondary verification
- Log max GPU memory usage across entire 50-model extraction
- Assert max GPU usage = 0 MB (raise exception if non-zero)

**Outputs:**
- `results/gpu_memory_log.csv`: Columns [timestamp, gpu_memory_mb]
- `results/gpu_memory_max.txt`: Single value (max GPU memory in MB)

### FR5: Feature Equivalence Validation
**Description:** Verify checkpoint-only extraction produces identical features to H-E1 cached baseline.

**Acceptance Criteria:**
- Load H-E1 cached features from `/h-e1/code/data/train_features.csv`
- Compare checkpoint-only extracted features against cached features (per model)
- Compute cosine similarity for each feature vector (5D: bn, ln, gn, no_norm, param_mass_ratio)
- Assert 100% exact match (cosine similarity = 1.0 for all 50 models)
- Report any mismatches with model name, expected vs actual values

**Data Inputs:**
- H-E1 cached features: `/h-e1/code/data/train_features.csv` (50 rows)

**Outputs:**
- `results/feature_validation.json`: Per-model cosine similarities
- `results/feature_mismatches.txt`: List of models with mismatches (if any)

### FR6: Scalability Analysis
**Description:** Extrapolate timing to 100-model, 200-model scenarios and identify bottlenecks.

**Acceptance Criteria:**
- Compute linear scaling factor: `extrapolated_time = (total_time / 50) * N`
- Document time complexity: O(n) expected (linear scaling)
- Identify bottlenecks: checkpoint download vs state_dict parsing vs feature extraction
- Report timing breakdown per extraction phase (load, parse, extract)

**Outputs:**
- `results/scalability_analysis.md`: Extrapolated timings, bottleneck analysis

### FR7: MUST_WORK Gate Evaluation
**Description:** Evaluate gate condition and determine PASS/FAIL status.

**Acceptance Criteria:**
- Check `total_time < 600 seconds` (10 minutes)
- Check `max_gpu_memory_mb == 0` (CPU-only)
- Check `feature_equivalence == 1.0` (100% match)
- Check `speedup_vs_forward_pass > 3.0` (practical advantage)
- Generate gate decision: PASS if all conditions met, FAIL otherwise

**Outputs:**
- `results/gate_evaluation.json`: PASS/FAIL status, threshold comparisons, failure reasons (if any)

---

## Non-Functional Requirements

### NFR1: Performance
- **Target:** Total extraction time <10 minutes for 50 models (avg <12 sec/model)
- **Benchmark:** Forward-pass baseline expected ~35-45 minutes (avg 42-54 sec/model)
- **Scalability:** Linear O(n) time complexity (confirmed via scalability analysis)

### NFR2: Resource Efficiency
- **CPU:** 8+ cores recommended (parallel checkpoint loading possible in future)
- **RAM:** 16GB minimum (largest models like ViT-L require ~4GB per checkpoint)
- **Disk:** 10GB free space (50 checkpoints ~5GB + results cache)
- **GPU:** NOT REQUIRED (primary validation criterion)
- **Network:** Stable internet for first-time checkpoint download (subsequent runs use cache)

### NFR3: Security
- **Checkpoint Loading:** Use `weights_only=True` flag to prevent arbitrary code execution (PyTorch 2.0+ security feature)
- **Unpickling Restriction:** Only tensor data allowed, no custom Python classes or lambdas

### NFR4: Correctness
- **Feature Validation:** 100% exact match with H-E1 cached features (ensures extraction logic is correct)
- **Regression Testing:** Compare against H-M2 parameter counting results (validates param_mass_ratio computation)

### NFR5: Reproducibility
- **Deterministic Extraction:** Same checkpoint → same features (no randomness in state_dict parsing)
- **Cached Checkpoints:** Report both first-run and cached-run timings (separates network I/O from extraction overhead)
- **Seed Independence:** No random seeds involved (purely deterministic tensor shape inspection)

### NFR6: Observability
- **Logging:** Per-model extraction times, GPU memory polling, feature extraction progress
- **Error Handling:** Graceful failure on missing checkpoints, corrupted state_dict, feature mismatch
- **Reporting:** Comprehensive Markdown report + JSON artifacts for downstream processing

---

## Data Requirements

### Input Data
| Dataset | Type | Source | Size | Cache Path | Verification |
|---------|------|--------|------|------------|--------------|
| **TIMM Model Zoo Checkpoints** | Pre-extracted | PyTorch Hub via `timm.create_model()` | 50 models (20 CNN, 20 Transformer, 10 Hybrid) | `/h-e1/code/data` | ✅ Verified (used in H-E1, H-M1, H-M2) |
| **H-E1 Cached Features** | CSV | H-E1 validation output | 50 rows × 5 features | `/h-e1/code/data/train_features.csv` | ✅ Required for feature equivalence validation |
| **Forward-Pass Baseline Subset** | Programmatic API | TIMM `create_model(pretrained=True)` | 5 models | N/A (loaded on-demand) | Subset of TIMM models |

### Output Data
| Artifact | Format | Description | Path |
|----------|--------|-------------|------|
| **Timing Report** | Markdown | Per-model extraction times, speedup analysis | `results/timing_report.md` |
| **Timing Plot** | PNG | Bar chart (checkpoint-only vs forward-pass) | `results/timing_comparison.png` |
| **GPU Memory Log** | CSV | Timestamp, GPU memory usage (MB) | `results/gpu_memory_log.csv` |
| **Feature Validation** | JSON | Per-model cosine similarities | `results/feature_validation.json` |
| **Gate Evaluation** | JSON | PASS/FAIL status, threshold comparisons | `results/gate_evaluation.json` |
| **Scalability Analysis** | Markdown | Extrapolated timings, bottleneck breakdown | `results/scalability_analysis.md` |

---

## Evaluation Metrics

### Primary Metrics (MUST_WORK Gate)
| Metric | Measurement Method | Success Threshold | Priority |
|--------|-------------------|-------------------|----------|
| **Total Extraction Time** | `time.perf_counter()` start/end for 50-model batch | <10 minutes (600 seconds) | P0 (CRITICAL) |
| **GPU Memory Usage** | `torch.cuda.memory_allocated()` max value during extraction | 0 MB (CPU-only) | P0 (CRITICAL) |

### Secondary Metrics
| Metric | Measurement Method | Success Threshold | Priority |
|--------|-------------------|-------------------|----------|
| **Per-Model Avg Time** | Mean of individual extraction times | <12 seconds/model | P1 (HIGH) |
| **Speedup vs Forward-Pass** | Ratio of forward-pass time / checkpoint-only time (5-model subset) | >3x faster | P1 (HIGH) |
| **Feature Equivalence** | Cosine similarity between checkpoint-only features and H-E1 cached features | 1.0 (exact match) | P0 (CRITICAL) |
| **90th Percentile Time** | 90th percentile of per-model extraction times | <20 seconds | P2 (MEDIUM) |

### Diagnostic Metrics
| Metric | Purpose | Reporting |
|--------|---------|-----------|
| **Checkpoint Download Time** | Separate network I/O from extraction overhead | First-run vs cached-run comparison |
| **Largest Model Time** | Identify outliers (ViT-L, Swin-L) | Per-model timing breakdown |
| **Bottleneck Analysis** | Determine if download, loading, or extraction dominates | Phase-wise timing (load, parse, extract) |

---

## Dependencies & Prerequisites

### Phase 2C Prerequisites
- ✅ **H-M3 Experiment Brief Completed:** `/h-m3/02c_experiment_brief.md` exists (24KB)

### Hypothesis Chain Dependencies
| Prerequisite | Required Inputs | Verification Status |
|--------------|-----------------|---------------------|
| **H-E1 (EXISTENCE)** | Feature extraction logic, cached features (train_features.csv) | ✅ VALIDATED (gate PASSED) |
| **H-M2 (MECHANISM)** | Parameter counting infrastructure, param_mass_ratio computation | ✅ VALIDATED (Cohen's d=3.202, gate PASSED) |

### Software Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| **PyTorch** | ≥2.0 (for weights_only=True support) | Checkpoint loading, GPU memory monitoring |
| **timm** | Latest | Model checkpoint download, forward-pass baseline |
| **pandas** | Any | Feature CSV I/O, data manipulation |
| **matplotlib** | Any | Timing comparison plot generation |
| **numpy** | Any | Cosine similarity computation |

### Hardware Requirements
- **CPU:** 8+ cores recommended (single-threaded in baseline, parallelization future work)
- **RAM:** 16GB minimum (ViT-L checkpoints ~4GB each)
- **Disk:** 10GB free space (50 checkpoints ~5GB total)
- **GPU:** NOT REQUIRED (validation criterion: zero GPU usage)

---

## Implementation Architecture

### Module Structure
```
h-m3/code/
├── main.py                          # Orchestrator (runs 5-step protocol)
├── config.py                        # Paths, thresholds, model lists
├── src/
│   ├── checkpoint_only_extractor.py # Primary extraction (weights_only=True)
│   ├── forward_pass_extractor.py    # Baseline extraction (full instantiation)
│   ├── timer.py                     # High-precision timing utilities
│   ├── gpu_monitor.py               # GPU memory tracking
│   ├── feature_validator.py         # Compare against H-E1 cached features
│   ├── gate_logic.py                # MUST_WORK gate evaluation
│   └── report_generator.py          # Markdown report + timing plots
├── results/                         # Output artifacts (JSON, CSV, MD, PNG)
└── requirements.txt                 # Dependencies (torch, timm, pandas, matplotlib)
```

### Reuse from Previous Hypotheses
**From H-E1:**
- `feature_extractor.py` (StatisticalFeatureExtractor class)
- `config.py` (MODEL_FAMILIES, NORM_PATTERNS, HEAD_KEYWORDS)
- Cached features: `/h-e1/code/data/train_features.csv`

**From H-M2:**
- Parameter counting logic (param_mass_ratio computation)

### Key Classes
**CheckpointOnlyExtractor:**
- `extract_batch(model_names: List[str]) -> Dict[str, float]`
- Uses `torch.load(checkpoint_path, weights_only=True)`
- Returns per-model extraction times

**ForwardPassExtractor:**
- `extract_batch(model_names: List[str]) -> Dict[str, float]`
- Uses `timm.create_model(pretrained=True)` + 1 forward pass
- Returns per-model extraction times for baseline comparison

**Timer:**
- `start()`, `stop()`, `elapsed()` - High-precision timing wrapper
- Uses `time.perf_counter()` (nanosecond resolution)

**GPUMonitor:**
- `start_monitoring()` - Background thread polling GPU memory every 0.1 sec
- `stop_monitoring()` - Returns max GPU memory usage
- Uses `torch.cuda.memory_allocated()`

**FeatureValidator:**
- `validate(checkpoint_features, cached_features) -> float`
- Computes cosine similarity per model
- Returns match rate (1.0 = perfect match)

---

## Testing & Validation Strategy

### Unit Tests
- **checkpoint_only_extractor_test.py:** Verify state_dict loading with weights_only=True
- **timer_test.py:** Verify perf_counter precision (>1ms resolution)
- **gpu_monitor_test.py:** Verify zero GPU usage on CPU-only extraction
- **feature_validator_test.py:** Verify cosine similarity computation

### Integration Tests
- **5-model subset extraction:** Run checkpoint-only + forward-pass baseline, compare speedup
- **Feature equivalence test:** Extract features from 5 models, compare against H-E1 cached
- **GPU memory assertion:** Run extraction with GPU monitoring, assert max usage = 0 MB

### Validation Protocol (Phase 4)
1. **Checkpoint-Only Extraction Timing:** 50 models, measure total time
2. **GPU Memory Monitoring:** Continuous polling, assert 0 MB
3. **Forward-Pass Baseline Comparison:** 5-model subset, compute speedup
4. **Feature Equivalence Validation:** 100% match with H-E1 cached features
5. **Scalability Analysis:** Extrapolate to 100-model, 200-model scenarios

### Gate Evaluation
**MUST_WORK Condition:**
```python
gate_pass = (
    total_time < 600 and          # <10 minutes
    max_gpu_memory_mb == 0 and    # CPU-only
    feature_equivalence == 1.0 and # 100% match
    speedup_vs_forward_pass > 3.0  # >3x faster
)
```

**Gate Decision:**
- **PASS:** Proceed to H-C1 (Edge Case Robustness)
- **FAIL:** ABANDON hypothesis chain (method not lightweight → no efficiency advantage)

---

## Risk Analysis & Mitigation

### High-Priority Risks
| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|------------|--------|------------|
| **R1** | Checkpoint download dominates timing (network I/O bottleneck) | High | Medium | Use cached checkpoints, report "cached extraction time" as primary metric |
| **R2** | Large models (>1GB checkpoints) exceed 12-sec threshold | Medium | Low | Allow per-model outliers, use 90th percentile as threshold |
| **R3** | Feature extraction bug causes mismatch with H-E1 cached features | Low | Critical | Pre-validate on 5-model subset before full 50-model run |

### Assumption Dependencies
| Assumption | Test Method | If Violated |
|------------|-------------|-------------|
| **A1:** Checkpoint download is one-time cost | Compare first-run vs cached-run timing | Report both metrics separately |
| **A2:** weights_only=True does not corrupt state_dict | Feature equivalence validation (FR5) | Switch to full `torch.load()` if mismatch detected |
| **A3:** CPU extraction is sufficient (no GPU required) | GPU memory monitoring (FR4) | Document GPU requirement if non-zero usage detected |

---

## Timeline & Resource Allocation

### Implementation Schedule
| Phase | Tasks | Duration | Dependencies |
|-------|-------|----------|--------------|
| **Setup** | Install dependencies, verify H-E1 cached features accessible | 0.5 hours | H-E1 completion |
| **Checkpoint Extraction** | Implement checkpoint_only_extractor.py, timer.py | 1.5 hours | - |
| **Baseline Implementation** | Implement forward_pass_extractor.py | 1 hour | - |
| **Monitoring** | Implement gpu_monitor.py, feature_validator.py | 1 hour | - |
| **Execution** | Run 50-model extraction, collect timing data | 0.5 hours | All modules complete |
| **Analysis** | Generate timing plots, gate evaluation, report | 1 hour | Execution complete |
| **Total** | | **5.5 hours** | |

### Computational Resources
- **CPU:** 8+ cores recommended
- **RAM:** 16GB minimum
- **Disk:** 10GB free space
- **GPU:** NOT REQUIRED (primary validation criterion)
- **Network:** Stable internet for first-time checkpoint download

---

## Success Definition & Next Steps

### Hypothesis Validation Criteria
**H-M3 is VALIDATED if:**
1. Total extraction time <10 minutes for 50 models (PRIMARY)
2. GPU memory usage = 0 MB (SECONDARY)
3. Feature equivalence: 100% match with H-E1 cached features (CORRECTNESS)
4. Speedup vs forward-pass baseline >3x (PRACTICAL ADVANTAGE)

### Gate Decision
- **PASS:** Proceed to H-C1 (Edge Case Robustness)
- **FAIL:** ABANDON hypothesis chain (method not lightweight → no efficiency advantage)

### If Hypothesis Passes
**Immediate Actions:**
1. Update verification_state.yaml: h-m3.validation.status = "COMPLETED"
2. Generate 04_validation.md report with timing benchmarks
3. Trigger Phase 3 for H-C1
4. Update paper draft: Add Section 3.3 "Extraction Efficiency" with timing results

**Long-Term Implications:**
- Establishes practical feasibility for deployment (no GPU infrastructure required)
- Enables scaling to 100+ model analysis (linear time complexity)
- Differentiates from Kofinas 2024 (50+ hours) and Zhang & Abdulla 2023 (GPU + forward pass)

### If Hypothesis Fails
**Diagnostic Protocol:**
1. Identify bottleneck: Checkpoint download vs feature extraction vs disk I/O
2. Profile per-model timing: Which models exceed threshold?
3. Feature validation: Is extraction logic correct?

**Pivot Options (if timing >10 min but <20 min):**
- **Option A:** Relax threshold to 15 minutes (still faster than forward-pass baseline)
- **Option B:** Implement parallel extraction (multi-process checkpoint loading)
- **Option C:** Document limitation, proceed to H-C1 with revised scope

**Abandon Conditions (if timing >20 min or GPU usage >0 MB):**
- Method loses core efficiency advantage
- Revert to forward-pass extraction (Zhang & Abdulla 2023 style)
- Update paper scope: "Proof-of-concept classifier" instead of "Practical lightweight tool"

---

## Appendix A: Model List (50 Models)

**CNNs (20):**
- ResNet: resnet18, resnet34, resnet50, resnet101, resnet152
- EfficientNet: efficientnet_b0, efficientnet_b1, efficientnet_b2, efficientnet_b3
- RegNet: regnetx_002, regnetx_004, regnetx_006
- DenseNet: densenet121, densenet169
- MobileNet: mobilenetv2_100, mobilenetv3_large_100
- Others: resnext50_32x4d, wide_resnet50_2, dla34, hrnet_w18

**Transformers (20):**
- ViT: vit_base_patch16_224, vit_small_patch16_224, vit_large_patch16_224
- DeiT: deit_base_patch16_224, deit_small_patch16_224, deit_tiny_patch16_224
- Swin: swin_base_patch4_window7_224, swin_small_patch4_window7_224, swin_tiny_patch4_window7_224
- BEiT: beit_base_patch16_224, beit_large_patch16_224
- ConvNeXt: convnext_base, convnext_small, convnext_tiny
- PoolFormer: poolformer_m36, poolformer_s12
- Others: mixer_b16_224, twins_svt_base, deit3_base_patch16_224

**Hybrids (10):**
- CoAtNet: coatnet_0_rw_224, coatnet_1_rw_224
- MaxViT: maxvit_tiny_tf_224, maxvit_small_tf_224
- CrossViT: crossvit_base_240, crossvit_small_240
- Others: levit_256, xcit_small_12_p16_224, coat_lite_mini, visformer_small

---

## Appendix B: Threshold Configuration

```python
# h-m3/code/config.py

THRESHOLDS = {
    'total_time_max_seconds': 600,       # 10 minutes
    'per_model_avg_max_seconds': 12,     # avg time per model
    'gpu_memory_max_mb': 0,              # CPU-only requirement
    'speedup_min_factor': 3.0,           # vs forward-pass baseline
    'feature_equivalence_min': 1.0       # exact match with H-E1
}

# Baseline Subset (5 models for forward-pass comparison)
BASELINE_SUBSET = [
    'resnet50',                # CNN representative
    'vit_base_patch16_224',    # Transformer representative
    'efficientnet_b0',         # Efficient CNN
    'deit_small_patch16_224',  # Small Transformer
    'swin_tiny_patch4_window7_224'  # Hierarchical Transformer
]
```

---

**End of PRD**
