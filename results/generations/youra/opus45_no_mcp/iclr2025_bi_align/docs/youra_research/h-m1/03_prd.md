# Product Requirements Document: H-M1
## RLHF Reward Signal Conflation Analysis

**Date:** 2026-08-19
**Hypothesis:** H-M1 (MECHANISM)
**Author:** Anonymous
**Tier:** FULL (30 tasks max)

---

## 1. Executive Summary

This experiment tests whether RLHF-trained models optimize for a conflated reward signal that doesn't distinguish between correctness tasks and user-state-modeling tasks. Building on H-E1's finding of systematic calibration inversion clusters (silhouette=0.6016, k=2), we analyze whether model confidence patterns support the reward conflation hypothesis.

**Success Criteria:** Distribution overlap > 0.7 OR mean confidence difference < 0.1 between task types.

---

## 2. Problem Statement

### 2.1 Background
H-E1 established that calibration inversion patterns cluster non-randomly (silhouette=0.6016). The next question is WHY these clusters exist. H-M1 hypothesizes that RLHF reward models conflate correctness with user-state-modeling, causing similar confidence regardless of task type.

### 2.2 Hypothesis
Under standard RLHF training, if we analyze the reward signal, then models optimize for annotator approval (not correctness alone), because annotator ratings conflate multiple dimensions.

### 2.3 Gate Condition (MUST_WORK)
- PASS: Distribution overlap > 0.7 OR mean_diff < 0.1
- FAIL: Overlap < 0.5 AND mean_diff > 0.2

---

## 3. Functional Requirements

### FR-1: Task Classification System
Classify 2212 benchmark tasks into Type A (correctness) vs Type B (user-state-modeling):
- **Type A:** Single factual answer, no user-state modeling (e.g., TruthfulQA factual)
- **Type B:** Requires user belief consideration, context-dependent, hedged responses

**Classification Features:**
- `user_belief_reference`: "you think", "your opinion", "do you believe"
- `context_dependent`: "given that", "considering", "in this situation"
- `hedged_answer`: "might", "could", "possibly", "it depends"

### FR-2: Confidence Extraction
Extract sequence-level confidence from 3 RLHF models:
- Llama-2-7B-Chat (primary)
- Llama-2-13B-Chat (cross-validation)
- Mistral-7B-Instruct (cross-validation)

**Method:** Length-normalized log probability of generated answer.

### FR-3: Distribution Overlap Analysis
Compare confidence distributions between Type A and Type B tasks:
- Histogram intersection for overlap score
- Mean confidence difference
- Point-biserial correlation with H-E1 cluster labels

### FR-4: Cross-Model Consistency
Verify conflation pattern holds across all 3 models:
- Generate overlap scores per model
- Heatmap visualization

### FR-5: Visualization Suite
Generate figures:
- Gate metrics comparison (overlap vs thresholds)
- Confidence distribution histograms (Type A vs Type B overlay)
- Cross-model consistency heatmap
- Cluster-task correlation scatter plot

---

## 4. Data Specification

### 4.1 Datasets (Reuse from H-E1)

| Dataset | Tasks | Source | Auto-Download |
|---------|-------|--------|---------------|
| TruthfulQA | 817 | `truthful_qa` | Yes |
| MMLU moral_scenarios | 895 | `cais/mmlu` | Yes |
| Anthropic HH-RLHF | 500 | `Anthropic/hh-rlhf` | Yes |
| **Total** | **2212** | - | - |

**Note:** All datasets auto-download via HuggingFace. No manual download needed.

### 4.2 H-E1 Artifacts (Required Input)
- Cluster labels: `h-e1/code/outputs/results.json`
- Task metadata: Reuse from H-E1 evaluation

### 4.3 Static Baselines
None - this is an analysis experiment, not a training experiment.

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Batch size: 16 (memory-efficient, from H-E1)
- Inference: float16, device_map="auto"
- Expected runtime: ~2 hours on single GPU

### NFR-2: Reproducibility
- Fixed seed: 42
- Deterministic operations where possible
- Full logging of classification decisions

### NFR-3: Statistical Validity
- Minimum 500+ samples per task type (full datasets, not subsamples)
- Standard statistical tests (scipy.stats)
- Effect size reporting

---

## 6. Success Criteria

### Primary Metrics
| Metric | Threshold | Gate |
|--------|-----------|------|
| Distribution Overlap | > 0.7 | PASS |
| Mean Confidence Diff | < 0.1 | PASS |
| Cluster-TaskType Correlation | > 0.3 | Supporting |

### Gate Logic
```python
gate_pass = (overlap > 0.7) or (mean_diff < 0.1)
gate_fail = (overlap < 0.5) and (mean_diff > 0.2)
```

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0
transformers>=4.30
datasets
scipy
numpy
matplotlib
seaborn
pyyaml
tqdm
```

### 7.2 Hardware
- GPU: NVIDIA with 24GB+ VRAM (for 13B model)
- Fallback: 16GB for 7B models only

### 7.3 External References
- H-E1 code: `h-e1/code/` (confidence extraction infrastructure)
- H-E1 results: `h-e1/code/outputs/results.json` (cluster labels)

---

## 8. Ablation Variants

### ABL-1: Classification Threshold Sensitivity
Test bidirectional score thresholds: 1, 2, 3 features required for Type B.

### ABL-2: Single Feature Analysis
Isolate each feature's contribution to task classification.

### ABL-3: Per-Dataset Analysis
Compare overlap scores within each benchmark (TruthfulQA, MMLU, HH-RLHF).

---

## 9. Traceability

| Requirement | Source |
|-------------|--------|
| Task classification | Shen et al. 2024, Bidirectional Alignment |
| Confidence extraction | H-E1 validation code |
| Success criteria | Phase 2B verification plan |
| Datasets | Phase 2A experimental setup |

---

*Generated for Phase 3 Implementation Planning*
*Next: Architecture Design*
