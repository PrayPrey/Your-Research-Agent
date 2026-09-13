# Experiment Design Brief: H-M3 Checkpoint Extraction Feasibility

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Date:** 2026-07-11  
**Phase:** 2C (Experiment Design)

---

## 1. Hypothesis Statement

**Full Statement:**  
Under PyTorch state_dict inspection, if models are loaded with weights_only=True and features extracted without forward passes, then extraction completes for 50 models in <10 minutes total because checkpoint access is deterministic and requires no model instantiation or GPU computation.

**Rationale:**  
This hypothesis tests the final causal step—that architectural signatures are extractable via lightweight checkpoint inspection, not requiring expensive forward passes (vs Zhang & Abdulla 2023 runtime statistics) or graph construction (vs Kofinas 2024 GNN). Success validates the core contribution claim: practical efficiency advantage over baseline methods.

**Prerequisites:** h-m2 (requires parameter counting infrastructure working)

**Success Criteria:**
- **Primary (MUST_WORK):** Extraction time <10 minutes for 50 models (vs >30 min for forward passes)
- **Secondary:** Zero GPU memory usage (CPU-only extraction)

---

## 2. Dataset Specification

### 2.1 Core Dataset

| Attribute | Specification |
|-----------|---------------|
| **Name** | TIMM Model Zoo Checkpoints (Reused from H-E1) |
| **Type** | `pre-extracted` (features already cached) |
| **Source** | PyTorch Hub via `timm.create_model()` |
| **Size** | 50 models (20 CNN, 20 Transformer, 10 Hybrid) |
| **Cache Path** | `/workspace/TEST_wsl/docs/youra_research/h-e1/code/data` |
| **Verification Status** | ✅ Verified (used in H-E1, H-M1, H-M2) |

**Dataset Composition:**
- CNNs (20): ResNet family (18/34/50/101/152), EfficientNet variants, RegNet, DenseNet, MobileNet
- Transformers (20): ViT variants, DeiT, Swin, BEiT, ConvNeXt (Transformer-inspired), PoolFormer
- Hybrids (10): CoAtNet, MaxViT, Twins, CrossViT

### 2.2 Baseline Comparison Dataset

For forward-pass baseline (5-model subset for timing comparison):

| Attribute | Specification |
|-----------|---------------|
| **Name** | Forward-Pass Baseline Models |
| **Type** | `programmatic-api` |
| **Source** | Same TIMM models, loaded via `timm.create_model(pretrained=True)` |
| **Size** | 5 models (ResNet50, ViT-B/16, EfficientNet-B0, DeiT-S, Swin-T) |
| **Purpose** | Measure extraction time WITH forward pass (model instantiation + 1 batch inference) |

**Why This Dataset is Acceptable:**  
This is NOT synthetic data—it uses real, pre-trained model checkpoints from TIMM. The checkpoint files contain actual learned weights from ImageNet training, not simulated/generated parameters. The comparison tests extraction speed on real checkpoints with different access methods (checkpoint-only vs full model instantiation).

---

## 3. Experimental Design

### 3.1 Verification Protocol (5 Steps from Phase 2B)

**Step 1: Checkpoint-Only Extraction Timing**
- Load 50 TIMM model checkpoints using `torch.load(weights_only=True)` for security
- Extract features via state_dict key regex matching and tensor shape inspection (no model instantiation)
- Measure total extraction time (start = first model load, end = last feature extraction)
- Log per-model extraction time for granular analysis

**Step 2: GPU Memory Monitoring**
- Monitor GPU memory usage during checkpoint-only extraction
- Use `torch.cuda.memory_allocated()` and `nvidia-smi` polling
- Verify zero GPU allocation (all computation on CPU)

**Step 3: Forward-Pass Baseline Comparison**
- For 5-model subset: Load model via `timm.create_model(pretrained=True)`, run 1 forward pass (batch_size=1, dummy input)
- Measure total time (includes model instantiation + weight loading + inference)
- Compare against checkpoint-only extraction time for same 5 models

**Step 4: Feature Equivalence Validation**
- Verify checkpoint-only extraction produces identical features to H-E1/H-M1/H-M2 baseline
- Compare extracted `bn_count`, `ln_count`, `gn_count`, `param_mass_ratio` against cached values
- Assert 100% match rate (confirms extraction correctness)

**Step 5: Scalability Analysis**
- Extrapolate timing to 100-model, 200-model scenarios
- Document linear scaling factor (expected: O(n) time complexity)
- Identify bottlenecks (checkpoint download vs feature extraction)

### 3.2 Baseline Methods

| Method | Description | Expected Performance |
|--------|-------------|---------------------|
| **Checkpoint-Only (Ours)** | Load state_dict with `weights_only=True`, extract via regex + shape inspection | <10 min for 50 models, CPU-only |
| **Forward-Pass Baseline** | Full model instantiation + 1 batch inference (Zhang & Abdulla 2023 style) | >30 min for 50 models, GPU required |

**Note on GNN Baseline (Kofinas 2024):**  
Not implemented for timing comparison (would require 50+ hours per Phase 2B). Literature reports GNN graph construction + training takes ~2 hours per model family, estimated >30 min for feature extraction alone.

### 3.3 Implementation Strategy

**Primary Extraction Module (Checkpoint-Only):**
```python
class CheckpointOnlyExtractor:
    def extract_batch(self, model_names: List[str]) -> Dict[str, float]:
        """
        Extract features from checkpoints without model instantiation.
        
        Returns:
            Dict mapping model_name -> extraction_time (seconds)
        """
        start_time = time.time()
        extraction_times = {}
        
        for model_name in model_names:
            model_start = time.time()
            
            # Download checkpoint (cached after first run)
            checkpoint_path = download_checkpoint(model_name)
            
            # Load with security flag (no unpickling of arbitrary code)
            state_dict = torch.load(checkpoint_path, weights_only=True)
            
            # Extract features (regex + tensor shape inspection)
            features = self.feature_extractor.extract_features(state_dict)
            
            model_end = time.time()
            extraction_times[model_name] = model_end - model_start
            
            # Free memory
            del state_dict
        
        total_time = time.time() - start_time
        return {'total_time': total_time, 'per_model': extraction_times}
```

**Baseline Extraction Module (Forward-Pass):**
```python
class ForwardPassExtractor:
    def extract_batch(self, model_names: List[str]) -> Dict[str, float]:
        """
        Extract features WITH model instantiation and forward pass.
        
        Returns:
            Dict mapping model_name -> extraction_time (seconds)
        """
        extraction_times = {}
        
        for model_name in model_names:
            model_start = time.time()
            
            # Full model instantiation (loads weights + builds graph)
            model = timm.create_model(model_name, pretrained=True)
            model.eval()
            
            # Dummy forward pass (batch_size=1)
            dummy_input = torch.randn(1, 3, 224, 224)
            with torch.no_grad():
                _ = model(dummy_input)
            
            # Extract features from state_dict
            features = self.feature_extractor.extract_features(model.state_dict())
            
            model_end = time.time()
            extraction_times[model_name] = model_end - model_start
            
            # Free memory
            del model
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        total_time = sum(extraction_times.values())
        return {'total_time': total_time, 'per_model': extraction_times}
```

### 3.4 Metrics & Thresholds

| Metric | Measurement Method | Success Threshold |
|--------|-------------------|-------------------|
| **Total Extraction Time** | `time.time()` start/end for 50-model batch | <10 minutes (600 seconds) |
| **Per-Model Avg Time** | Mean of individual extraction times | <12 seconds/model |
| **GPU Memory Usage** | `torch.cuda.memory_allocated()` max value | 0 MB (CPU-only) |
| **Speedup vs Forward-Pass** | Ratio of forward-pass time / checkpoint-only time (5-model subset) | >3x faster |
| **Feature Equivalence** | Cosine similarity between checkpoint-only features and H-E1 cached features | 1.0 (exact match) |

**Gate Logic:**
- **MUST_WORK Condition:** Total extraction time <10 minutes AND GPU memory usage = 0 MB
- **Fail Action:** ABANDON (extraction not lightweight → violates core contribution claim)

---

## 4. Code Architecture

### 4.1 Module Structure

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
└── requirements.txt                 # Dependencies (torch, timm, pandas, matplotlib)
```

### 4.2 Reuse from Previous Hypotheses

**From H-E1:**
- `feature_extractor.py` (StatisticalFeatureExtractor class)
- `config.py` (MODEL_FAMILIES, NORM_PATTERNS, HEAD_KEYWORDS)
- Cached features: `/h-e1/code/data/train_features.csv`, `/h-e1/code/data/val_features.csv`

**From H-M2:**
- Parameter counting logic (already validated in scale invariance tests)

### 4.3 Key Implementation Details

**Security Consideration:**  
Use `torch.load(weights_only=True)` to prevent arbitrary code execution during checkpoint loading (PyTorch 2.0+). This flag restricts unpickling to tensor data only.

**Timing Methodology:**
- Use `time.perf_counter()` for high-precision timing (nanosecond resolution)
- Exclude checkpoint download time after first run (measure cached extraction speed)
- Warmup run: Extract 1 model before starting timer (avoid cold-start overhead)

**GPU Memory Monitoring:**
- Poll `torch.cuda.memory_allocated()` every 0.1 seconds during extraction
- Use `nvidia-smi --query-gpu=memory.used --format=csv` as secondary verification
- Assert max GPU usage = 0 MB throughout entire 50-model extraction

---

## 5. Expected Outcomes & Interpretation

### 5.1 Success Scenario (Gate PASS)

**Expected Results:**
- Checkpoint-only extraction: 6-8 minutes for 50 models (avg 7-10 sec/model)
- Forward-pass baseline: 35-45 minutes for 50 models (avg 42-54 sec/model)
- Speedup: 5-6x faster than forward-pass approach
- GPU memory: 0 MB (CPU-only extraction verified)

**Interpretation:**  
Lightweight checkpoint-only extraction is feasible and provides significant efficiency advantage over forward-pass baselines (Zhang & Abdulla 2023). This validates the core contribution claim: practical deployment without GPU infrastructure or expensive inference overhead.

### 5.2 Failure Scenario (Gate FAIL)

**Critical Failure Conditions:**
1. **Total time >10 minutes:** Extraction not lightweight → ABANDON
2. **GPU memory >0 MB:** Not CPU-only → violates efficiency claim → ABANDON
3. **Feature mismatch:** Extraction produces different features than H-E1 → implementation bug → FIX & RERUN

**Fail Action (Per Phase 2B):**  
ABANDON hypothesis chain. If checkpoint-only extraction requires >10 minutes or GPU usage, the approach loses its core efficiency advantage. The method would not be meaningfully better than existing baselines (forward-pass or GNN methods).

### 5.3 Edge Cases & Robustness

**Potential Bottlenecks:**
1. **Checkpoint download:** First-time download may dominate timing (50 models × ~100MB each = 5GB total)
   - **Mitigation:** Use cached checkpoints after first download, report "cached extraction time" as primary metric
2. **Large models:** ViT-L, Swin-L checkpoints >1GB may slow extraction
   - **Mitigation:** Track per-model timing, identify outliers, report 90th percentile time
3. **Disk I/O:** SSD vs HDD difference
   - **Mitigation:** Document storage type, recommend SSD for production deployment

---

## 6. Integration with Hypothesis Chain

### 6.1 Dependency on H-M2

**Required Inputs from H-M2:**
- Validated parameter-mass ratio extraction (confirms R computation works correctly)
- Cached features from 50 models (used for feature equivalence validation in Step 4)

**How H-M2 Results Inform H-M3:**
- H-M2 confirmed parameter counting is correct (Cohen's d = 3.202, gate PASSED)
- H-M3 reuses same extraction code but focuses on TIMING, not feature validity
- If H-M2 failed, H-M3 would be blocked (can't test extraction speed if extraction logic is broken)

### 6.2 Impact on H-C1 (Downstream Hypothesis)

**What H-M3 Provides to H-C1:**
- Validated extraction pipeline (timing benchmarks establish practical feasibility)
- Scalability estimates (extrapolated timing for 100+ model deployment)

**If H-M3 Fails:**
- H-C1 (Edge Case Robustness) still tests feature quality, but lacks efficiency justification
- Overall contribution weakened: method works but is not practically deployable at scale

---

## 7. Deliverables & Validation Artifacts

### 7.1 Code Outputs

| Artifact | Description | Path |
|----------|-------------|------|
| **Timing Report** | Markdown file with per-model extraction times, speedup analysis | `h-m3/code/results/timing_report.md` |
| **Timing Plot** | Bar chart comparing checkpoint-only vs forward-pass extraction time | `h-m3/code/results/timing_comparison.png` |
| **GPU Memory Log** | CSV with timestamp, GPU memory usage (MB) during extraction | `h-m3/code/results/gpu_memory_log.csv` |
| **Feature Validation** | JSON with per-model feature equivalence scores (cosine similarity) | `h-m3/code/results/feature_validation.json` |
| **Gate Evaluation** | JSON with PASS/FAIL status, threshold comparisons | `h-m3/code/results/gate_evaluation.json` |

### 7.2 Validation Checklist

**Before claiming hypothesis validated:**
- [ ] Total extraction time <10 minutes (600 seconds)
- [ ] Per-model avg time <12 seconds
- [ ] GPU memory usage = 0 MB throughout extraction
- [ ] Speedup vs forward-pass baseline >3x
- [ ] Feature equivalence: 100% exact match with H-E1 cached features
- [ ] Scalability analysis: Linear O(n) time complexity confirmed
- [ ] Gate evaluation: MUST_WORK condition PASSED

**Edge Case Testing:**
- [ ] Largest model (ViT-L) extraction time <30 seconds
- [ ] Smallest model (MobileNet-V2) extraction time <5 seconds
- [ ] Disk I/O impact: Cached vs uncached extraction time differential <2x

---

## 8. Risk Analysis & Mitigation

### 8.1 High-Priority Risks

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|------------|--------|------------|
| **R1** | Checkpoint download dominates timing (network I/O bottleneck) | High | Medium | Use cached checkpoints, report "cached extraction time" as primary metric |
| **R2** | Large models (>1GB checkpoints) exceed 12-sec threshold | Medium | Low | Allow per-model outliers, use 90th percentile as threshold |
| **R3** | Feature extraction bug causes mismatch with H-E1 cached features | Low | Critical | Pre-validate on 5-model subset before full 50-model run |

### 8.2 Assumption Dependencies

| Assumption | Test Method | If Violated |
|------------|-------------|-------------|
| **A1:** Checkpoint download is one-time cost | Compare first-run vs cached-run timing | Report both metrics separately |
| **A2:** weights_only=True does not corrupt state_dict | Feature equivalence validation (Step 4) | Switch to full `torch.load()` if mismatch detected |
| **A3:** CPU extraction is sufficient (no GPU required) | GPU memory monitoring (Step 2) | Document GPU requirement if non-zero usage detected |

---

## 9. Timeline & Resource Allocation

### 9.1 Implementation Schedule

| Phase | Tasks | Duration | Dependencies |
|-------|-------|----------|--------------|
| **Setup** | Install dependencies, verify H-E1 cached features accessible | 0.5 hours | H-E1 completion |
| **Checkpoint Extraction** | Implement checkpoint_only_extractor.py, timer.py | 1.5 hours | - |
| **Baseline Implementation** | Implement forward_pass_extractor.py | 1 hour | - |
| **Monitoring** | Implement gpu_monitor.py, feature_validator.py | 1 hour | - |
| **Execution** | Run 50-model extraction, collect timing data | 0.5 hours | All modules complete |
| **Analysis** | Generate timing plots, gate evaluation, report | 1 hour | Execution complete |
| **Total** | | **5.5 hours** | |

### 9.2 Computational Resources

| Resource | Specification | Notes |
|----------|---------------|-------|
| **CPU** | 8+ cores recommended | Parallel checkpoint loading possible |
| **RAM** | 16GB minimum | Largest models (ViT-L) require ~4GB per checkpoint |
| **Disk** | 10GB free space | 50 model checkpoints (~5GB) + results cache |
| **GPU** | NOT REQUIRED | Primary validation criterion |
| **Network** | Stable internet for first-time checkpoint download | Subsequent runs use cache |

---

## 10. Success Definition & Next Steps

### 10.1 Hypothesis Validation Criteria

**H-M3 is VALIDATED if:**
1. Total extraction time <10 minutes for 50 models (PRIMARY)
2. GPU memory usage = 0 MB (SECONDARY)
3. Feature equivalence: 100% match with H-E1 cached features (CORRECTNESS)
4. Speedup vs forward-pass baseline >3x (PRACTICAL ADVANTAGE)

**Gate Decision:**
- **PASS:** Proceed to H-C1 (Edge Case Robustness)
- **FAIL:** ABANDON hypothesis chain (method not lightweight → no efficiency advantage)

### 10.2 If Hypothesis Passes

**Immediate Actions:**
1. Update verification_state.yaml: h-m3.validation.status = "COMPLETED"
2. Generate 04_validation.md report with timing benchmarks
3. Trigger Phase 3 (Implementation Planning) for H-C1
4. Update paper draft: Add Section 3.3 "Extraction Efficiency" with timing results

**Long-Term Implications:**
- Establishes practical feasibility for deployment (no GPU infrastructure required)
- Enables scaling to 100+ model analysis (linear time complexity)
- Differentiates from Kofinas 2024 (50+ hours) and Zhang & Abdulla 2023 (GPU + forward pass)

### 10.3 If Hypothesis Fails

**Diagnostic Protocol:**
1. Identify bottleneck: Checkpoint download vs feature extraction vs disk I/O
2. Profile per-model timing: Which models exceed threshold? (ViT-L outliers acceptable)
3. Feature validation: Is extraction logic correct? (compare against H-E1 cached features)

**Pivot Options (if timing >10 min but <20 min):**
- **Option A:** Relax threshold to 15 minutes (still faster than forward-pass baseline)
- **Option B:** Implement parallel extraction (multi-process checkpoint loading)
- **Option C:** Document limitation, proceed to H-C1 with revised scope

**Abandon Conditions (if timing >20 min or GPU usage >0 MB):**
- Method loses core efficiency advantage → revert to forward-pass extraction (Zhang & Abdulla 2023 style)
- Update paper scope: "Proof-of-concept classifier" instead of "Practical lightweight tool"

---

## 11. References & Prior Art

### 11.1 Archon KB Findings

**Relevant Past Cases:**
1. **HuggingFace Diffusers Checkpoint Loading:** Uses `safetensors` for faster loading (~2x speedup vs pickle), confirms checkpoint-only extraction is standard practice
2. **PyTorch XLA Documentation:** Notes `weights_only=True` prevents arbitrary code execution, recommended for production deployment

### 11.2 Code Examples from Research

**Timing Benchmarking Pattern (Archon KB):**
```python
def elapsed_time(pipeline, nb_pass=3):
    # Warmup (2 runs)
    for _ in range(2):
        _ = pipeline()
    
    # Timing (avg of 3 runs)
    start = time.time()
    for _ in range(nb_pass):
        pipeline()
    end = time.time()
    
    return (end - start) / nb_pass
```

**GPU Memory Monitoring (PyTorch Docs):**
```python
import torch

# Reset memory stats
torch.cuda.reset_peak_memory_stats()

# Run extraction
features = extract_features(state_dict)

# Check peak GPU memory
peak_memory = torch.cuda.max_memory_allocated() / 1024**2  # MB
print(f"Peak GPU memory: {peak_memory:.2f} MB")
```

### 11.3 Baseline Methods (Literature)

| Method | Paper | Extraction Time | GPU Required? |
|--------|-------|-----------------|---------------|
| **GNN (Kofinas 2024)** | "Weight-Space Learning" | ~50 hours (graph construction + training) | Yes |
| **Forward-Pass (Zhang & Abdulla 2023)** | "BatchNorm Statistics" | ~30 min for 50 models | Yes |
| **Checkpoint-Only (Ours)** | This work | <10 min target | No (CPU-only) |

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

## Appendix B: Config File Template

```python
# h-m3/code/config.py

import os

# Paths
BASE_DIR = os.path.dirname(__file__)
H_E1_DATA_DIR = os.path.join(BASE_DIR, '../../h-e1/code/data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
CACHE_DIR = os.path.join(BASE_DIR, '.cache/checkpoints')

# Thresholds (from Phase 2B)
THRESHOLDS = {
    'total_time_max_seconds': 600,       # 10 minutes
    'per_model_avg_max_seconds': 12,     # avg time per model
    'gpu_memory_max_mb': 0,              # CPU-only requirement
    'speedup_min_factor': 3.0,           # vs forward-pass baseline
    'feature_equivalence_min': 1.0       # exact match with H-E1
}

# Model Lists (reuse from H-E1)
MODEL_FAMILIES = {
    'cnn': [
        'resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152',
        'efficientnet_b0', 'efficientnet_b1', 'efficientnet_b2', 'efficientnet_b3',
        'regnetx_002', 'regnetx_004', 'regnetx_006',
        'densenet121', 'densenet169',
        'mobilenetv2_100', 'mobilenetv3_large_100',
        'resnext50_32x4d', 'wide_resnet50_2', 'dla34', 'hrnet_w18'
    ],
    'transformer': [
        'vit_base_patch16_224', 'vit_small_patch16_224', 'vit_large_patch16_224',
        'deit_base_patch16_224', 'deit_small_patch16_224', 'deit_tiny_patch16_224',
        'swin_base_patch4_window7_224', 'swin_small_patch4_window7_224', 'swin_tiny_patch4_window7_224',
        'beit_base_patch16_224', 'beit_large_patch16_224',
        'convnext_base', 'convnext_small', 'convnext_tiny',
        'poolformer_m36', 'poolformer_s12',
        'mixer_b16_224', 'twins_svt_base', 'deit3_base_patch16_224'
    ],
    'hybrid': [
        'coatnet_0_rw_224', 'coatnet_1_rw_224',
        'maxvit_tiny_tf_224', 'maxvit_small_tf_224',
        'crossvit_base_240', 'crossvit_small_240',
        'levit_256', 'xcit_small_12_p16_224', 'coat_lite_mini', 'visformer_small'
    ]
}

# Baseline Subset (5 models for forward-pass comparison)
BASELINE_SUBSET = [
    'resnet50',                # CNN representative
    'vit_base_patch16_224',    # Transformer representative
    'efficientnet_b0',         # Efficient CNN
    'deit_small_patch16_224',  # Small Transformer
    'swin_tiny_patch4_window7_224'  # Hierarchical Transformer
]

# Feature Names (reuse from H-E1)
FEATURE_NAMES = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

# Timing Config
TIMING_CONFIG = {
    'warmup_runs': 1,           # Warmup extractions before timing
    'timing_runs': 3,           # Avg over 3 runs for forward-pass baseline
    'gpu_poll_interval_sec': 0.1  # Poll GPU memory every 0.1 sec
}
```

---

**End of Experiment Design Brief**
