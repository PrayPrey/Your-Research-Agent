# Product Requirements Document: H-M1
## RLHF Co-Optimization of Safety and Ethics in LLM Trustworthiness

**Hypothesis:** H-M1  
**Type:** MECHANISM (Incremental — extends H-E1)  
**Date:** 2026-08-04  
**Phase:** 3 — Implementation Planning  
**Gate:** MUST_WORK — ρ_partial(safety, ethics) > 0.5 (p < 0.0033) AND ≥2/3 LLaMA-2 within-family pairs show Δ_safety > 0 AND Δ_ethics > 0 simultaneously

---

## 1. Executive Summary

H-M1 tests the mechanism by which RLHF jointly optimizes safety and ethics in LLMs. Using the TrustLLM 16-model × 6-dimension evaluation dataset (reused from H-E1), we conduct two analyses: (1) verify that ρ_partial(safety, machine_ethics) > 0.5 from H-E1 results (pre-confirmed at 0.841), and (2) apply a within-family natural experiment comparing LLaMA-2 base vs Chat variants at 7B, 13B, and 70B scales to test whether RLHF alignment simultaneously improves both safety and ethics scores.

**This is a statistical analysis experiment — no model training required. Runtime < 5 seconds (CPU only).**

**Key H-E1 inheritance:** The partial correlation gate (primary) is already satisfied by H-E1 output. H-M1's distinctive contribution is the directional within-family RLHF effect test.

---

## 2. Problem Statement

RLHF training uses preference learning with human feedback that penalizes harmful and unethical outputs. The H-E1 results show strong partial correlation between safety and machine_ethics (ρ=0.841). H-M1 tests whether this co-movement is mechanistically caused by RLHF: if so, RLHF Chat variants should consistently outscore base variants on BOTH dimensions simultaneously at matched model scales, forming a "co-optimization signature."

**Baseline condition:** LLaMA-2 base variants (pre-training only, no RLHF alignment)  
**Proposed condition:** LLaMA-2 Chat variants (RLHF-aligned via PPO on human preference data)  
**Natural experiment design:** Size-matched pairs (7B, 13B, 70B) control for scale confound

---

## 3. Functional Requirements

### FR-1: Data Loading (Reuse from H-E1)
- Load H-E1 results JSON: `h-e1/experiment_results_phase3.json`
- Extract: 16×6 scores matrix, model metadata (name, log10_params, is_RLHF), ρ_partial 6×6 matrix
- Fallback: if h-e1 JSON unavailable, re-clone TrustLLM and rebuild (same as H-E1 FR-1)
- Validate: 16 models present, 6 dimensions, LLaMA-2 variants identified correctly

### FR-2: Pre-Confirm Primary Gate from H-E1
- Read ρ_partial(safety, machine_ethics) from loaded h-e1 matrix
- safety_idx = DIMS.index("safety"), ethics_idx = DIMS.index("machine_ethics")
- Report: value, gate threshold (0.5), pass/fail status
- Expected: 0.841 (pre-confirmed PASS)
- This is verification only — no new computation required

### FR-3: LLaMA-2 Family Extraction
- Filter 16-model set to LLaMA-2 family: 7B-base, 7B-chat, 13B-base, 13B-chat, 70B-base, 70B-chat
- Form 3 within-family pairs: (7B-base, 7B-chat), (13B-base, 13B-chat), (70B-base, 70B-chat)
- For each pair extract: safety score (base), safety score (chat), ethics score (base), ethics score (chat)
- Validate: exactly 6 LLaMA-2 models found; 3 pairs correctly matched by scale

### FR-4: Within-Family Delta Computation (Secondary Gate)
- For each of 3 LLaMA-2 size pairs:
  - Δ_safety = chat_safety_score − base_safety_score
  - Δ_ethics = chat_ethics_score − base_ethics_score
  - both_positive = (Δ_safety > 0) AND (Δ_ethics > 0)
- Count: n_both_positive = sum(both_positive for all 3 pairs)
- Secondary gate condition: n_both_positive ≥ 2 (at least 2 of 3 pairs)
- Binomial sign test: scipy.stats.binom_test(n_both_positive, 3, p=0.5, alternative='greater')

### FR-5: Baseline Comparison Metrics
- Report all 6 individual dimension score comparisons for LLaMA-2 family (not just safety/ethics)
- Compute direction (base vs chat) for: truthfulness, safety, fairness, robustness, privacy, machine_ethics
- Context: compare with Li et al. (2025) ICLR finding that RLHF doesn't auto-guarantee trustworthiness

### FR-6: Visualization
- **Required:** Bar chart showing ρ_partial(safety, ethics) vs threshold (0.5), and n_pairs_both_positive vs gate (2/3)
- **Additional:** Within-family delta plot — grouped bar chart of Δ_safety and Δ_ethics for each scale (7B, 13B, 70B), annotated with sign test result
- **Additional:** Scatter plot — all 16 models, safety vs ethics scores, colored by is_RLHF (base=blue, chat=red), arrows connecting base→chat LLaMA-2 pairs at same scale
- **Additional:** 2D delta space scatter — (Δ_safety, Δ_ethics) for 3 LLaMA-2 pairs, quadrant lines at (0,0), positive quadrant shaded
- **Additional:** ρ_partial heatmap (6×6, reuse from H-E1) with safety-ethics cell highlighted
- Output location: `h-m1/figures/`

### FR-7: Results Serialization
- Save all results to `h-m1/experiment_results_phase3.json`:
  - rho_safety_ethics: float (from h-e1 matrix)
  - primary_gate_pass: bool
  - deltas: [{scale, delta_safety, delta_ethics, both_positive}] × 3
  - n_both_positive: int
  - secondary_gate_pass: bool
  - binom_pvalue: float
  - overall_gate_pass: bool (primary AND secondary)
  - individual_scores: full 6×6 LLaMA-2 family score table

---

## 4. Data Specification

### Primary Dataset
**Name:** TrustLLM Published Score Tables (reused from H-E1)  
**Source:** `h-e1/experiment_results_phase3.json` (primary); fallback: https://github.com/HowieHwong/TrustLLM (results/ folder)  
**Version:** v0.3.0 (ICML 2024, Sun et al., 2024)  
**Format:** JSON (pre-computed from H-E1); fallback raw JSON files per dimension per model  
**Size:** N=16 models × 6 dimensions (full evaluation set — no subsampling)

**H-M1 Specific Subset:**
| Model | Scale | is_RLHF | log10_params |
|-------|-------|---------|-------------|
| LLaMA-2-7b-base | 7B | 0 | 9.845 |
| LLaMA-2-7b-chat | 7B | 1 | 9.845 |
| LLaMA-2-13b-base | 13B | 0 | 10.114 |
| LLaMA-2-13b-chat | 13B | 1 | 10.114 |
| LLaMA-2-70b-base | 70B | 0 | 10.845 |
| LLaMA-2-70b-chat | 70B | 1 | 10.845 |

**6 Dimensions (same as H-E1):**
1. truthfulness (idx 0)
2. safety (idx 1)
3. fairness (idx 2)
4. robustness (idx 3)
5. privacy (idx 4)
6. machine_ethics (idx 5)

**Preprocessing:** None required beyond H-E1 — scores already loaded and validated.

**Manual Download Required:** No (reuse from H-E1 JSON). Fallback: GitHub clone same as H-E1.

### No Training Data / No Validation Split
This experiment uses the full 16-model evaluation set. No train/val/test split. N=16 models for correlation; N=3 pairs for within-family delta test (full LLaMA-2 set at TrustLLM scale).

---

## 5. Baseline Models

### Baseline Condition: LLaMA-2 Base Variants (No RLHF)
- LLaMA-2-7b-base: pre-training only
- LLaMA-2-13b-base: pre-training only  
- LLaMA-2-70b-base: pre-training only

**Measurement:** TrustLLM published safety and ethics scores for base variants (from H-E1 data)

### Reference Baseline (from H-E1)
Raw Spearman correlation (uncontrolled) — context only, not recomputed in H-M1.

---

## 6. Proposed Model / Method

### Proposed Condition: LLaMA-2 Chat Variants (RLHF-Aligned)
- LLaMA-2-7b-chat: RLHF via PPO on human safety/helpfulness labels
- LLaMA-2-13b-chat: RLHF via PPO  
- LLaMA-2-70b-chat: RLHF via PPO

### Core Analysis: Within-Family RLHF Co-Optimization Test
```python
def compute_rlhf_cooptimization_effect(scores_matrix, model_metadata, rho_partial):
    DIMS = ["truthfulness","safety","fairness","robustness","privacy","machine_ethics"]
    safety_idx, ethics_idx = DIMS.index("safety"), DIMS.index("machine_ethics")

    # Extract LLaMA-2 pairs
    llama2_pairs = extract_llama2_pairs(scores_matrix, model_metadata)
    # [(base_scores_7B, chat_scores_7B), (13B...), (70B...)]

    # Compute signed within-family deltas
    deltas = []
    for base_s, chat_s in llama2_pairs:
        deltas.append({
            "delta_safety": chat_s[safety_idx] - base_s[safety_idx],
            "delta_ethics": chat_s[ethics_idx] - base_s[ethics_idx]
        })

    # Sign test: count both-positive
    n_both_positive = sum(1 for d in deltas
                          if d["delta_safety"] > 0 and d["delta_ethics"] > 0)

    # Verify rho from H-E1
    rho_safety_ethics = rho_partial[safety_idx][ethics_idx]

    return {
        "deltas": deltas,
        "n_pairs_both_positive": n_both_positive,
        "secondary_gate_pass": n_both_positive >= 2,
        "rho_safety_ethics": rho_safety_ethics,
        "primary_gate_pass": abs(rho_safety_ethics) > 0.5
    }
```

---

## 7. Non-Functional Requirements

### NFR-1: Compute
- CPU-only, runtime < 5 seconds
- No GPU required

### NFR-2: Reproducibility
- Deterministic (no random seeds needed — pure statistical analysis)
- Results fully reproducible given same h-e1 experiment_results_phase3.json

### NFR-3: Reuse
- MUST load from `h-e1/experiment_results_phase3.json` as primary data source
- DO NOT re-download TrustLLM unless fallback required
- Reuse h-e1 OLS residualization code if partial correlation recomputation needed

### NFR-4: Outputs
- All figures saved to PNG at 300 DPI in `h-m1/figures/`
- All numeric results serialized to `h-m1/experiment_results_phase3.json`
- Summary printed to console and `h-m1/experiment.log`

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Primary gate | ρ_partial(safety, ethics) > 0.5, p < 0.0033 [pre-confirmed: 0.841] | MUST_WORK |
| Secondary gate | ≥2/3 LLaMA-2 pairs: Δ_safety > 0 AND Δ_ethics > 0 | MUST_WORK |
| Code runs without error | True | Required |
| Exactly 3 LLaMA-2 pairs extracted | count=3 | Required |
| All 4 figures generated | count=4+ | Required |
| Results JSON saved | File exists | Required |

---

## 9. Dependencies

### Python Packages
```
numpy>=1.24
pandas>=1.5
scipy>=1.10
matplotlib>=3.7
seaborn>=0.12
```

Note: numpy, pandas, scipy, matplotlib, seaborn are inherited from H-E1. No new packages required.

### External Repositories
- HowieHwong/TrustLLM (fallback only — primary data from h-e1 JSON)
- AI4LIFE-GROUP/RLHF_Trust (reference: Li et al. 2025, ICLR Oral — methodology context)

### Internal Dependencies (H-E1 Outputs — REQUIRED)
- `h-e1/experiment_results_phase3.json` — primary data source (scores_matrix, model_metadata, rho_partial_matrix)
- `h-e1/code/data_loader.py` — reusable for TrustLLM parsing (fallback)
- `h-e1/code/analysis.py` — reusable OLS residualization (fallback)

---

## 10. Out of Scope

- Model training or fine-tuning of any kind
- Re-computing partial correlations (pre-computed by H-E1)
- HELM dataset analysis (H-M3)
- Pythia scaling series analysis (H-M2)
- Other model families (Mistral, Falcon, Vicuna, GPT, Claude, etc.) — LLaMA-2 only for delta test
- Bootstrap stability analysis (H-E2 scope)
- Any dataset larger than the 16-model TrustLLM set

---

*Generated by Phase 3 Implementation Planning (UNATTENDED mode)*  
*Source: h-m1/02c_experiment_brief.md*  
*Base Hypothesis: H-E1 (experiment_results_phase3.json)*
