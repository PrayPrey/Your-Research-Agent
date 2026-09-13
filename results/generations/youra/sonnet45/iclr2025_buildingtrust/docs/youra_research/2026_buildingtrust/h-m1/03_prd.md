# Product Requirements Document: H-M1
## Logit Delta Anisotropy Analysis — RLHF Alignment Geometric Structure

**Hypothesis ID:** H-M1
**Type:** MECHANISM (INCREMENTAL — extends H-E1 infrastructure)
**Date:** 2026-03-17
**Author:** Anonymous
**Phase 2C Source:** h-m1/02c_experiment_brief.md
**Base Hypothesis:** H-E1 (COMPLETED, gate PASS)
**Tier:** FULL (max 30 tasks)

---

## 1. Executive Summary

This experiment validates the structural non-isotropy of alignment-induced logit perturbations in RLHF-aligned LLMs. Building directly on H-E1's validated logit extraction pipeline, H-M1 adds a covariance eigendecomposition analysis module to test whether alignment-induced logit deltas (Δ = aligned_logits − base_logits) are axis-specific and non-isotropic (structured perturbations) rather than isotropic noise.

**Gate Condition (MUST_WORK):** Anisotropy ratio r = λ₁ / mean(λ₂, λ₃, λ₄) significantly > 1.0 (paired t-test p < 0.05) in ≥ 2 of 3 model families.

**Key Innovation:** Extension of H-E1 4D MCQ logit extraction with Δ covariance matrix eigendecomposition — approximately 50 lines of new analysis code on top of a fully validated pipeline.

---

## 2. Problem Statement

H-E1 confirmed that pre-alignment confidence margin predicts post-alignment argmax flip probability (β₁=-4.33, AUROC=0.867). However, the structural mechanism behind this prediction is unknown. H-M1 investigates whether alignment-induced logit perturbations are geometrically structured (non-isotropic) — i.e., concentrated along specific axes in the 4D logit space — which would explain why some items are more vulnerable to flipping than others.

**Scientific Question:** Are RLHF alignment-induced logit changes structured perturbations (axis-specific) or random noise (isotropic)?

**Theoretical Basis:** Li et al. [2024] confirmed heterogeneous axis-specific trustworthiness changes post-RLHF. If true, the covariance matrix of Δ vectors should have one dominant eigenvalue (r >> 1.0) rather than equal eigenvalues (r ≈ 1.0 for isotropic noise).

---

## 3. Functional Requirements

### FR-1: Logit Delta Extraction
- **FR-1.1:** Extend H-E1 logit extraction pipeline to extract 4D logits from BOTH base and aligned models per pair
- **FR-1.2:** Compute Δ_i = aligned_4D_logits_i − base_4D_logits_i for each MCQ item i
- **FR-1.3:** Stack Δ across N items to form matrix [N, 4]
- **FR-1.4:** Save logit tensors to disk as numpy `.npy` files per model pair

### FR-2: Anisotropy Analysis
- **FR-2.1:** Center Δ matrix (zero-mean per axis): δ = Δ − mean(Δ, axis=0)
- **FR-2.2:** Compute 4×4 covariance matrix Σ = cov(δᵀ) using `np.cov`
- **FR-2.3:** Eigendecompose Σ using `np.linalg.eigh`: λ₁ ≥ λ₂ ≥ λ₃ ≥ λ₄
- **FR-2.4:** Compute anisotropy ratio r = λ₁ / mean(λ₂, λ₃, λ₄)
- **FR-2.5:** Statistical test: paired t-test (λ₁ vs mean of λ₂..λ₄), p < 0.05 threshold
- **FR-2.6:** Report results per model family; gate passes if ≥ 2/3 families satisfy r > 1.0 AND p < 0.05

### FR-3: Model Pairs (3 families)
- **FR-3.1:** pair2 — base: `allenai/tulu-2-7b`, aligned: `allenai/tulu-2-dpo-7b` (DPO, 7B)
- **FR-3.2:** pair4 — base: `EleutherAI/pythia-6.9b`, aligned: `dvruette/oasst-pythia-6.9b-4000-steps` (SFT, 6.9B)
- **FR-3.3:** pair_new — base: `EleutherAI/pythia-1.4b`, aligned: `pvduy/pythia-1.4b-rl-trlx-dolly15k` (PPO/TRLX, 1.4B)
- **FR-3.4:** Tokenizer compatibility check for pair_new before full run (pilot test: 100 items)
- **FR-3.5:** If pair_new tokenizer mismatch: skip and document; gate still passable with pair2 + pair4

### FR-4: Datasets (All from H-E1 — standard, real benchmarks)
- **FR-4.1:** Primary: MMLU — `cais/mmlu`, `all`, `test` split, 14,042 items (57 subjects)
- **FR-4.2:** Secondary: TruthfulQA — `truthful_qa`, `multiple_choice`, `validation`, 817 items
- **FR-4.3:** Secondary: ARC-Challenge — `allenai/ai2_arc`, `ARC-Challenge`, `test`, 1,172 items
- **FR-4.4:** Load via HuggingFace `datasets` library: `load_dataset("cais/mmlu", "all", split="test")`
- **FR-4.5:** Total evaluation items: 16,031 across 3 benchmarks

### FR-5: Secondary Analysis
- **FR-5.1:** Decision axis projection — variance of Δ projected onto (top1_logit − top2_logit) direction
- **FR-5.2:** Method comparison — anisotropy ratio comparison across DPO vs SFT vs PPO
- **FR-5.3:** Margin quintile stratification — anisotropy ratio by confidence margin quintile (bridges to H-M2)
- **FR-5.4:** Cross-benchmark — replicate anisotropy analysis on TruthfulQA and ARC-Challenge

### FR-6: Visualization (Mandatory)
- **FR-6.1:** Gate Metrics Comparison: bar chart of anisotropy ratio per model family vs threshold (r=1.0)
- **FR-6.2:** Eigenvalue spectrum plot: 4 eigenvalues per model pair (isotropic=flat, anisotropic=spike)
- **FR-6.3:** Logit delta PCA visualization: 2D PCA scatter of Δ vectors colored by margin quintile
- **FR-6.4:** Anisotropy by margin quintile: line chart of r vs quintile (bridge to H-M2)
- **FR-6.5:** DPO vs SFT vs PPO comparison: box plots of per-item Δ variance along decision vs orthogonal axes
- **FR-6.6:** All figures saved to `h-m1/figures/`

### FR-7: Mechanism Verification
- **FR-7.1:** Verify delta shape [N, 4] per pair (N ≈ 14,042 for MMLU)
- **FR-7.2:** Validate eigenvalue positivity (no numerical degeneracy)
- **FR-7.3:** Sanity check: compute anisotropy ratio on synthetic isotropic noise (expected r ≈ 1.0)
- **FR-7.4:** Log activation indicators per pair (delta shape, cov computed, eigenvalues valid)

---

## 4. Data Specification

### Primary Dataset
| Property | Value |
|----------|-------|
| Name | MMLU (Massive Multitask Language Understanding) |
| HF Identifier | `cais/mmlu`, split `all`, subset `test` |
| Size | 14,042 items (57 subjects) |
| Format | 4-option MCQ (A/B/C/D) — 4D logit extraction |
| Download | Auto via HuggingFace `datasets` library |
| Cache | `h-m1/cache/mmlu/` |
| Validated in H-E1 | ✅ Fully functional |

### Secondary Datasets
| Dataset | HF ID | Size | Purpose |
|---------|-------|------|---------|
| TruthfulQA | `truthful_qa`, `multiple_choice`, `validation` | 817 | Cross-benchmark replication |
| ARC-Challenge | `allenai/ai2_arc`, `ARC-Challenge`, `test` | 1,172 | Cross-benchmark replication |

### Data Preprocessing
- Extract 4D option log-probabilities per item via model forward pass (tokens A, B, C, D)
- Compute Δ = aligned_4D_logits − base_4D_logits per item (no normalization before covariance)
- Margin quintile stratification for secondary analysis
- Sequential model loading (base then aligned per pair — insufficient VRAM for simultaneous loading)

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Batch size 8–16 items per forward pass (H100 NVL validated in H-E1)
- Sequential loading: base model → extract → save → aligned model → extract → save
- GPU: Single H100 NVL, `CUDA_VISIBLE_DEVICES=0`

### NFR-2: Reproducibility
- Fixed seed: 1 (consistent with H-E1 for controlled comparison)
- All intermediate results (logit tensors) saved as `.npy` files
- Result JSON: `h-m1/experiment_results.json`

### NFR-3: Error Handling
- Tokenizer mismatch → skip pair, document, continue (gate still passable with 2/3)
- Model not found (404) → log and skip, try fallback model IDs
- Degenerate covariance (all eigenvalues ≈ 0) → check logit normalization; flag as analysis error
- Isotropic result for a family → document null result; count toward family failures

### NFR-4: Infrastructure Reuse
- Conda environment: `youra-h-e1` (Python 3.10, H100 NVL)
- Direct extension of H-E1 codebase — logit extraction already functional
- Avoid known broken model IDs: `allenai/tulu-2-ppo-7b` (404), `reciprocate/ppo_hh_pythia-1B` (tokenizer error)

---

## 6. Evaluation Metrics & Success Criteria

### Primary Metrics (Gate Evaluation)

| Metric | Definition | Gate Threshold |
|--------|-----------|----------------|
| Anisotropy ratio (r) | λ₁ / mean(λ₂, λ₃, λ₄) of Δ covariance matrix | r > 1.0 |
| Statistical significance | Paired t-test: λ₁ vs trailing eigenvalues | p < 0.05 |
| Family count | Number of families where r > 1.0 AND p < 0.05 | ≥ 2/3 |

### Gate Pass Condition
- **PASS:** Anisotropy ratio > 1.0 with p < 0.05 in ≥ 2 of 3 model families (MMLU, N≈14K)
- **FAIL → EXPLORE:** Mechanism chain narrows to H-E1; pipeline continues with documentation

### Expected Performance
- If Li et al. [2024] generalizes: r ∈ [2.0, 10.0] for DPO/PPO pairs
- H-E1 η²=0.289 (large effect) suggests strong structured perturbation in tulu-2 DPO
- Isotropic null: r ≈ 1.0

### Secondary Metrics

| Metric | Purpose |
|--------|---------|
| Decision axis projection variance | Directional test of anisotropy |
| DPO vs SFT vs PPO anisotropy ratio | Method-specific signatures (feeds H-M2) |
| Cross-benchmark consistency (TruthfulQA, ARC) | Generalization |
| Anisotropy by margin quintile | Bridge to H-M2 mechanism |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 Infrastructure Dependencies
- **H-E1 codebase:** `h-e1/code/` — logit extraction pipeline (reuse directly)
- **Conda environment:** `youra-h-e1` (Python 3.10, already installed)
- **HuggingFace Hub:** Model downloading (3 base + 3 aligned = 6 model downloads)
- **GPU:** H100 NVL, CUDA_VISIBLE_DEVICES=0, ~40GB VRAM per 7B model

### 7.3 External Repositories
- H-E1 validated code patterns: `h-e1/code/` (primary reference)
- Li et al. [2024]: Axis-specific trustworthiness methodology (theoretical foundation)

---

## 8. Ablation Variants

| Variant | Description | Purpose |
|---------|-------------|---------|
| DPO (pair2) | Tulu-2 DPO 7B | Primary validated pair |
| SFT (pair4) | Pythia 6.9B SFT | Isotropic-vs-structured baseline comparison |
| PPO (pair_new) | Pythia 1.4B TRLX | Scale variant; PPO mechanism signature |
| Margin quintile | Per-quintile anisotropy analysis | Bridge to H-M2 hypothesis |
| Cross-benchmark | TruthfulQA + ARC replication | Generalization test |
| Isotropic sanity | Synthetic Gaussian Δ control | Null hypothesis validation |

---

## 9. Output Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Experiment results | `h-m1/experiment_results.json` | All metrics per pair + gate evaluation |
| MMLU logit cache | `h-m1/cache/{pair_id}_base_logits.npy` | Saved logit tensors |
| Figures | `h-m1/figures/` | 5 required plots |
| Validation report | `h-m1/04_validation.md` | Phase 4 output |
| Checkpoint | `h-m1/04_checkpoint.yaml` | Phase 4 progress tracking |

---

## 10. Phase 4 Coder Notes

**CRITICAL Infrastructure Rules:**
1. Do NOT load both base and aligned models simultaneously — insufficient VRAM
2. Sequential: load base → extract all 14K items → save → unload → load aligned → extract → compute Δ
3. Tokenizer compatibility MUST be verified for pair_new before full run
4. Use `np.linalg.eigh` (not `eig`) for symmetric covariance matrix — more numerically stable
5. Gate evaluation: count families where r > 1.0 AND p < 0.05; pipeline continues even if gate fails (EXPLORE route)

**Code Starting Point:** `h-e1/code/` — extend `extract_logits.py` with Δ computation; add new `analysis_anisotropy.py`

---

*Generated by Phase 3 Step 2 (PRD) — UNATTENDED mode*
*BMAD PRD workflow not installed; generated from Phase 2C experiment brief directly*
*Base hypothesis H-E1 infrastructure reused per INCREMENTAL design*
