# Product Requirements Document: H-E1

**Hypothesis:** H-E1 - LoRA Adapter Geometric Signatures Existence Proof
**Date:** 2026-04-13
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## 1. Executive Summary

This PRD defines the requirements for validating hypothesis H-E1: Under controlled experimental conditions with verified identical base model and fixed LoRA hyperparameters, within-cluster Grassmann distances between LoRA adapter B matrix column spaces will be significantly smaller than between-cluster distances (p < 0.05, Cohen's d > 0.5).

**Scope:** Proof-of-Concept (PoC) validation for EXISTENCE hypothesis with MUST_WORK gate.

**Key Deliverables:**
1. In-house LoRA adapter generation pipeline (200 adapters)
2. Grassmann distance computation module
3. Statistical analysis for hypothesis validation
4. Visualization of distance distributions

---

## 2. Problem Statement

### 2.1 Background
LoRA (Low-Rank Adaptation) constrains weight updates to a low-rank subspace defined by the B matrix column space. We hypothesize that semantically similar tasks induce similar geometric modifications to these weight spaces.

### 2.2 Objective
Validate that within-cluster (same FLAN category) Grassmann distances are significantly smaller than between-cluster distances, establishing the existence of task-specific geometric signatures in LoRA adapters.

### 2.3 Success Criteria (MUST_WORK Gate)
- **Primary:** p < 0.05 AND Cohen's d > 0.5
- **Secondary:** 95% CI excludes zero
- **Effect Direction:** within_cluster_mean < between_cluster_mean

---

## 3. Functional Requirements

### FR-1: LoRA Adapter Generation Pipeline
**Priority:** P0 (Critical)
**Description:** Generate controlled LoRA adapters with identical provenance

| Requirement | Specification |
|-------------|---------------|
| FR-1.1 | Load base model (Llama-3.2-1B-Instruct) with SHA-256 verification |
| FR-1.2 | Configure PEFT LoraConfig: r=32, alpha=64, dropout=0.05 |
| FR-1.3 | Train adapters on 8 source datasets (4 Reasoning, 4 NLU) |
| FR-1.4 | Generate 20 adapters per task = 160 adapters |
| FR-1.5 | Generate 5 seed variants × 4 tasks = 20 additional adapters (P3 control) |
| FR-1.6 | Total: 200 LoRA adapters with deterministic training |
| FR-1.7 | Save adapter weights and training metadata |

### FR-2: Dataset Preparation
**Priority:** P0 (Critical)
**Description:** Load and preprocess source datasets for LoRA training

| Category | Dataset | HuggingFace ID | Task Type |
|----------|---------|----------------|-----------|
| Reasoning | GSM8K | `gsm8k` (main split) | Math word problems |
| Reasoning | ARC-Challenge | `allenai/ai2_arc:ARC-Challenge` | Science QA |
| Reasoning | LogiQA | `lucasmccabe/logiqa` | Logical reasoning |
| Reasoning | StrategyQA | `wics/strategy-qa` | Multi-hop reasoning |
| NLU | MNLI | `nyu-mll/multi_nli` | Natural Language Inference |
| NLU | QQP | `SetFit/qqp` | Paraphrase detection |
| NLU | SST-2 | `SetFit/sst2` | Sentiment analysis |
| NLU | MRPC | `SetFit/mrpc` | Paraphrase detection |

### FR-3: Grassmann Distance Computation
**Priority:** P0 (Critical)
**Description:** Compute pairwise Grassmann distances between LoRA B matrix column spaces

| Requirement | Specification |
|-------------|---------------|
| FR-3.1 | Extract B matrices from all LoRA adapter layers |
| FR-3.2 | Compute orthonormal basis via QR decomposition |
| FR-3.3 | Calculate principal angles using scipy.linalg.subspace_angles |
| FR-3.4 | Compute Grassmann geodesic distance: sqrt(sum(θ²)) |
| FR-3.5 | Generate pairwise distance matrix for all adapters |
| FR-3.6 | Support per-layer analysis (q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, gate_proj) |

### FR-4: Statistical Analysis
**Priority:** P0 (Critical)
**Description:** Validate hypothesis using statistical tests

| Requirement | Specification |
|-------------|---------------|
| FR-4.1 | Separate distances into within-cluster and between-cluster groups |
| FR-4.2 | Perform Mann-Whitney U test (non-parametric) |
| FR-4.3 | Calculate Cohen's d effect size |
| FR-4.4 | Compute 95% confidence intervals |
| FR-4.5 | Generate statistical summary report |

### FR-5: Visualization
**Priority:** P1 (High)
**Description:** Generate figures for result interpretation

| Requirement | Specification |
|-------------|---------------|
| FR-5.1 | Bar chart: within vs between cluster means with error bars |
| FR-5.2 | Histogram/KDE: distance distributions |
| FR-5.3 | Heatmap: pairwise distance matrix with category annotations |
| FR-5.4 | Box plot: per-category distance distributions |
| FR-5.5 | Save all figures to hypothesis_folder/figures/ |

---

## 4. Data Specification

### 4.1 Input Data

#### 4.1.1 Source Datasets (Auto-Download)
All datasets are available via HuggingFace `datasets` library and will auto-download:
- No manual download required
- Cache path: HuggingFace default cache

#### 4.1.2 Base Model (Auto-Download)
- Model: `meta-llama/Llama-3.2-1B-Instruct`
- Method: HuggingFace transformers AutoModelForCausalLM
- Requires: HuggingFace token with Llama access

### 4.2 Generated Data

#### 4.2.1 LoRA Adapters
- Location: `{hypothesis_folder}/adapters/`
- Format: PEFT adapter format (adapter_model.safetensors + adapter_config.json)
- Count: 200 adapters
- Naming: `{task}_{seed}/` (e.g., `gsm8k_42/`, `mnli_43/`)

#### 4.2.2 Distance Matrices
- Location: `{hypothesis_folder}/results/`
- Format: NumPy .npy files
- Files: `pairwise_distances.npy`, `within_distances.npy`, `between_distances.npy`

#### 4.2.3 Statistical Results
- Location: `{hypothesis_folder}/results/`
- Format: JSON
- File: `statistical_results.json`

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Deterministic training with fixed seeds (42, 43, 44, 45, 46)
- torch.backends.cudnn.deterministic = True
- SHA-256 hash verification for base model

### NFR-2: Performance
- Training time: ~10-15 minutes per adapter (estimated)
- Total training time: ~33-50 hours for 200 adapters
- Distance computation: O(n²) for n adapters

### NFR-3: Resource Requirements
- GPU: Single GPU with 16GB+ VRAM (recommended)
- Storage: ~50GB for adapters + cache
- Memory: 32GB+ RAM recommended

---

## 6. Success Criteria

### 6.1 Gate Conditions (MUST_WORK)

| Metric | Threshold | Status |
|--------|-----------|--------|
| p-value | < 0.05 | Required |
| Cohen's d | > 0.5 | Required |
| Effect direction | within < between | Required |

### 6.2 Expected Performance
Based on Phase 2B preliminary analysis:
- Expected Cohen's d: ~0.91 (from underpowered n=8 study)
- Confidence: Effect direction confirmed

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.36.0
peft>=0.7.0
datasets>=2.14.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
tqdm>=4.65.0
safetensors>=0.4.0
accelerate>=0.24.0
```

### 7.2 External Services
- HuggingFace Hub (model/dataset download)
- HuggingFace token with Llama model access

### 7.3 Reference Implementations
- Grassmann distance: jyopari.github.io/posts/grassman
- scipy.linalg.subspace_angles documentation
- PEFT library documentation

---

## 8. Constraints

### 8.1 Technical Constraints
- Single GPU training (for controlled conditions)
- Fixed LoRA hyperparameters (no tuning)
- Deterministic training required

### 8.2 Scope Constraints
- EXISTENCE proof only (no mechanism explanation)
- Single base model (Llama-3.2-1B)
- Two-category clustering (Reasoning vs NLU)

---

## 9. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Training instability | High | Low | Use deterministic settings, checkpoint regularly |
| Insufficient effect size | High | Medium | Scale from 200 to 320 adapters if needed |
| Memory constraints | Medium | Medium | Use gradient checkpointing, reduce batch size |
| Dataset loading failures | Low | Low | Pre-cache datasets, retry logic |

---

## 10. Timeline (Estimated)

| Phase | Duration | Description |
|-------|----------|-------------|
| Setup | 1 hour | Environment, dependencies, model download |
| Data Prep | 2 hours | Dataset loading and preprocessing |
| Training | 40 hours | 200 adapters @ ~12 min each |
| Analysis | 2 hours | Distance computation, statistics |
| Visualization | 1 hour | Figure generation |
| **Total** | ~46 hours | End-to-end execution |

---

*Generated by Phase 3 PRD Workflow | Anonymous Research Pipeline*
*Source: 02c_experiment_brief.md (Phase 2C)*
