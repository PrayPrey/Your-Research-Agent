# Product Requirements Document: H-M2

**Date:** 2026-08-10
**Author:** PrayPrey
**Hypothesis:** High-entropy tasks tolerate eviction better - stratified by entropy, high-entropy group shows higher accuracy retention under eviction
**Type:** MECHANISM
**Tier:** FULL (30 tasks max)

---

## 1. Executive Summary

This experiment tests whether high-entropy attention tasks tolerate KV cache eviction better than low-entropy tasks. Using entropy stratification from H-M1 results, we compare accuracy retention under H2O eviction between high-entropy and low-entropy task groups.

**Success Criteria:** High-entropy group retention > Low-entropy group retention (p<0.05, Cohen's d > 0.5)

---

## 2. Problem Statement

H-M1 established that attention entropy discriminates task domains (F=38.05, eta²=0.522). The next question: does this entropy difference predict tolerance to compression? Specifically, we hypothesize that high-entropy tasks (with more distributed attention patterns) tolerate token eviction better because they rely less on individual token positions.

---

## 3. Functional Requirements

### FR-1: Entropy Stratification
- Load entropy results from H-M1 (`h-m1/code/entropy_matrix.npy`, `domain_means.json`)
- Compute median entropy across 6 domains
- Stratify: High-entropy group (entropy > median), Low-entropy group (entropy ≤ median)
- Expected split: ~90 samples per group

### FR-2: Baseline Accuracy Measurement
- Run Llama-2-7B with full KV cache on all 180 samples
- Compute per-sample accuracy using task-appropriate metrics
- Store as baseline for retention calculation

### FR-3: H2O Eviction Implementation
- Integrate FMInference/H2O (NeurIPS'23) for KV cache eviction
- Configuration: 40% retention (aggressive), 80% retention (moderate)
- Heavy:Recent ratio = 50:50 (standard H2O configuration)

### FR-4: Eviction Accuracy Measurement
- Run with H2O eviction at 40% and 80% retention levels
- Compute per-sample accuracy under eviction
- Calculate accuracy retention = evicted_acc / full_acc

### FR-5: Statistical Comparison
- Independent samples t-test: high-entropy vs low-entropy retention
- Effect size: Cohen's d
- Alternative: Mann-Whitney U if non-normal distribution

### FR-6: Visualization
- Required: Bar chart comparing high vs low entropy group retention with error bars
- Additional: Box plot, scatter plot (entropy vs retention), heatmap

---

## 4. Data Specification

### 4.1 Primary Dataset

| Attribute | Value |
|-----------|-------|
| Name | LongBench-v2 |
| Source | THUDM/LongBench (HuggingFace) |
| Domains | 6 (same as H-M1) |
| Samples per domain | 30 |
| Total samples | 180 |
| Download | Auto-download via HuggingFace datasets |

**Loading Code:**
```python
from datasets import load_dataset
dataset = load_dataset("THUDM/LongBench", split="test")
```

### 4.2 Prerequisite Artifacts (from H-M1)

| Artifact | Path | Usage |
|----------|------|-------|
| Entropy matrix | h-m1/code/entropy_matrix.npy | Stratification basis |
| Domain means | h-m1/code/domain_means.json | Median computation |

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed for all operations
- Deterministic batch ordering

### NFR-2: Memory Efficiency
- Single sample inference (batch_size=1)
- H2O eviction reduces memory by 60-80%

### NFR-3: Experiment Duration
- Estimated: ~2 hours for 180 samples × 3 conditions (full, 40%, 80%)

---

## 6. Success Criteria

| Metric | Threshold | Description |
|--------|-----------|-------------|
| Primary | p < 0.05 | t-test for high vs low entropy retention |
| Secondary | Cohen's d > 0.5 | Medium-large effect size |
| Direction | High > Low | High-entropy mean retention exceeds low-entropy |

**Gate:** SHOULD_WORK (exploratory mechanism validation)

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.10.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
```

### 7.2 External Repositories

| Repository | URL | Purpose |
|------------|-----|---------|
| H2O (Primary) | https://github.com/FMInference/H2O | Official NeurIPS'23 H2O implementation |
| awslabs/keys_values | https://github.com/awslabs/keys_values | Alternative H2OKVCache class |

### 7.3 Model Access

| Model | Source | Notes |
|-------|--------|-------|
| Llama-2-7B | meta-llama/Llama-2-7b-hf | Requires HuggingFace token |

---

## 8. Constraints

- **Compute:** Single GPU with 24GB+ VRAM (A100 recommended)
- **Time:** ~2 hours total inference time
- **Storage:** ~15GB for model weights

---

## 9. Out of Scope

- Training or fine-tuning (inference-only experiment)
- Other compression methods (quantization tested in H-M3)
- Multiple model architectures (Llama-2-7B only)

---

## 10. Appendix: H-M1 Results Reference

**Prerequisite Passed:** F=38.05, p=2.92e-26, eta²=0.522
- Entropy discriminates task domains
- Foundation for entropy-based stratification
