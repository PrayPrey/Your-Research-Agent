# Product Requirements Document: H-M3
## Mechanism Discrimination — H1 vs H2 vs H3 (Logit Perturbation Diagnosis)

**stepsCompleted**: [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**Hypothesis ID**: H-M3
**Type**: MECHANISM (INCREMENTAL — extends H-M2)
**Tier**: FULL (30 tasks max)
**Date**: 2026-03-15
**Phase 2C Source**: h-m3/02c_experiment_brief.md

---

## 1. Executive Summary

H-M3 determines which of three mechanistic hypotheses (H1, H2, H3) explains the alignment-induced Brier reliability increase confirmed in H-E1 and H-M2. This is a **data-extraction continuation experiment** — no new MMLU GPU-hours required. It extends the validated H-E1/H-M2 pipeline with three new analyses:

1. **Per-item Spearman ρ** over 4-option log-prob vectors (base vs aligned) — H1 discriminator
2. **Shared/changed-argmax Brier partition** — H1 signature (reliability concentrated in shared-argmax)
3. **TruthfulQA MC1 ECE** via lm-eval — H3 framing susceptibility diagnostic

**Gate:** SHOULD_WORK — mean Spearman ρ ≥ 0.9 for all 9 alignment-base pairs (H1 confirmed)

---

## 2. Problem Statement

H-E1 confirmed alignment increases Brier reliability (overconfidence). H-M2 confirmed logit margin inflation (PPO≥DPO>SFT). H-M3 asks: **which mechanism caused this?**

- **H1 (scale distortion):** Alignment inflates logit scale uniformly → rank order preserved (ρ≥0.9), reliability increase concentrated in shared-argmax items
- **H2 (boundary shift):** Alignment restructures decision boundaries → rank order disrupted (ρ<0.85), reliability increases more in changed-argmax items
- **H3 (framing susceptibility):** Alignment makes models sensitive to distractor framing → diagnosed via TruthfulQA MC1 ECE alignment interaction

**Prerequisite results:**
- H-E1: ΔBrier reliability PPO>DPO>SFT confirmed (MUST_WORK PASS)
- H-M1: ECE_base < 0.15 for all 3 Pythia sizes (MUST_WORK PASS)
- H-M2: Δmargin > 0 for PPO in ≥2/3 sizes, margin inflation consistent with H1 (SHOULD_WORK PASS)

---

## 3. Functional Requirements

### FR-1: Data Reuse — MMLU lm-eval Outputs
- **FR-1.1:** Load per-item (N=14042) log-prob matrices (N, 4) from H-E1/H-M2 lm-eval JSONL outputs for all 12 Pythia models (3 base + 9 aligned)
- **FR-1.2:** Use `load_lmeval_samples(model_key, results_dir)` from H-E1 `calibration_analysis.py` (Path A)
- **FR-1.3:** Fallback (Path B): re-run lm-eval `--tasks mmlu` with `--log_samples` for all 12 models if H-E1 outputs not available
- **FR-1.4:** Model keys follow format `pythia-{size}-{alignment}` (e.g., `pythia-1.4b-base`, `pythia-2.8b-ppo`)

### FR-2: TruthfulQA MC1 Evaluation
- **FR-2.1:** Run lm-eval `--tasks truthfulqa_mc1` for all 12 Pythia models (817 items each) if not cached
- **FR-2.2:** Load per-item log-prob matrices for TruthfulQA MC1 (N=817, variable options per item)
- **FR-2.3:** Compute ECE per alignment method on TruthfulQA MC1 using `compute_ece()` from H-E1 `calibration_analysis.py`
- **FR-2.4:** TruthfulQA outputs stored at: `h-m3/code/results/truthfulqa/`

### FR-3: Spearman ρ Analysis (H1/H2 Discrimination)
- **FR-3.1:** Compute per-item Spearman ρ over 4-option log-prob vector for each of 9 base-aligned pairs
  - Input: `base_logprobs[i]` and `aligned_logprobs[i]` — 4-element vectors per item
  - Method: `scipy.stats.spearmanr(base_logprobs[i], aligned_logprobs[i]).correlation`
  - Output: `rho_per_item` (N=14042), `mean_rho` (float) per model pair
- **FR-3.2:** Compute mean Spearman ρ aggregated over all 14042 MMLU items, per model pair (9 values)
- **FR-3.3:** H1 threshold: mean ρ ≥ 0.9 → H1 confirmed (scale distortion, rank preserved)
- **FR-3.4:** H2 threshold: mean ρ < 0.85 → H2 dominant (boundary restructuring)

### FR-4: Shared/Changed-Argmax Brier Partition (H1 Signature)
- **FR-4.1:** Partition MMLU items into shared-argmax and changed-argmax subsets per model pair:
  - `shared_mask = (np.argmax(base_logprobs, axis=1) == np.argmax(aligned_logprobs, axis=1))`
  - `changed_mask = ~shared_mask`
- **FR-4.2:** Compute Brier reliability separately for each subset (base and aligned models)
- **FR-4.3:** H1 signature: `reliability_shared_aligned > reliability_shared_base` (confidence inflation in correctly-ranked items)
- **FR-4.4:** H2 check: reliability increase larger in `changed_mask` than `shared_mask` → H2 dominant
- **FR-4.5:** Compute Cohen's d for PPO condition (shared-argmax subset): `d = (rel_shared_aligned - rel_shared_base) / pooled_std`
  - Gate secondary: Cohen's d ≥ 0.1 for PPO

### FR-5: Mechanism Discrimination Logic
- **FR-5.1:** Determine dominant mechanism based on ρ values and subset Brier partitioning:
  - H1: mean_rho ≥ 0.9 AND shared-argmax reliability increase > changed-argmax increase
  - H2: mean_rho < 0.85 (any size)
  - H3: TruthfulQA ECE increase significantly larger than MMLU ECE increase
- **FR-5.2:** Report mechanism diagnosis per alignment method (SFT/DPO/PPO) and size (1.4B/2.8B/6.9B)
- **FR-5.3:** Document 6.9B-PPO exception (from H-M2: Δmargin negative) in mechanism report

### FR-6: Visualization
- **FR-6.1 (MANDATORY):** Gate metrics bar chart — mean Spearman ρ per alignment method × Pythia size with H1/H2 thresholds annotated (saved: `h-m3/figures/figure_01_spearman_rho.png`)
- **FR-6.2:** Violin/histogram of per-item ρ distribution per alignment method (saved: `h-m3/figures/figure_02_rho_distribution.png`)
- **FR-6.3:** Grouped bar chart — Brier reliability for shared vs changed argmax subsets, 3 sizes × 3 alignment methods, Cohen's d annotations (saved: `h-m3/figures/figure_03_brier_partition.png`)
- **FR-6.4:** Stacked bar — % shared-argmax vs changed-argmax per model (saved: `h-m3/figures/figure_04_argmax_proportion.png`)
- **FR-6.5:** TruthfulQA MC1 ECE comparison — ECE per alignment method vs MMLU ECE (saved: `h-m3/figures/figure_05_truthfulqa_ece.png`)

### FR-7: Reporting
- **FR-7.1:** Write `h-m3/04_validation.md` with: gate result, per-pair Spearman ρ table, mechanism diagnosis, subset Brier analysis, TruthfulQA H3 diagnostic
- **FR-7.2:** Update `verification_state.yaml` with gate result and key metrics on completion
- **FR-7.3:** Save `h-m3/experiment_results.json` with all computed metrics

---

## 4. Data Specification

### Primary Dataset: MMLU (Reuse)
- **Source:** H-E1 lm-eval JSONL outputs (`h-e1/code/results/`)
- **Size:** Full test set, N=14042 items, 57 subjects
- **Format:** 4-option multiple-choice (logprob vectors shape: (N, 4))
- **Access:** `load_lmeval_samples(model_key, results_dir)` from `calibration_analysis.py`
- **Download required:** No (reuse from H-E1)

### Secondary Dataset: TruthfulQA MC1
- **Source:** lm-eval `--tasks truthfulqa_mc1` (HuggingFace, auto-download)
- **Size:** 817 questions, variable options per item
- **Format:** Multiple-choice, single correct answer
- **Access:** lm-eval `--log_samples`, parse JSONL output
- **Download required:** lm-eval handles auto-download (if not cached from H-E1 run)

---

## 5. Non-Functional Requirements

- **NFR-1 Reproducibility:** Seed=42 for all bootstrap; greedy decoding (temperature=1.0) for all lm-eval runs
- **NFR-2 Compute:** MMLU 0 new GPU-hours; TruthfulQA ~30 min/model × 12 models if not cached
- **NFR-3 Single GPU:** `CUDA_VISIBLE_DEVICES=<empty_gpu>` required before lm-eval runs
- **NFR-4 Inheritance:** Import patterns mirror H-M2 `load_data.py` (sys.path insertion for h-e1 code)
- **NFR-5 Testing:** Minimum 3 test methods per module with real assertions (no mock data)
- **NFR-6 Logging:** All intermediate results logged at INFO level; save to `h-m3/code/experiment.log`

---

## 6. Success Criteria

### Primary Gate (SHOULD_WORK)
- Mean Spearman ρ ≥ 0.9 for all 9 alignment-base pairs on MMLU logprob vectors

### Secondary Gate
- Brier reliability increase concentrated in shared-argmax subset with Cohen's d ≥ 0.1 for PPO

### Failure Responses
- If ρ < 0.85: Document H2 (boundary restructuring) as dominant mechanism
- If neither H1/H2: Test H3 framing via TruthfulQA ECE interaction
- Any mechanism diagnosis (H1/H2/H3) is scientifically valid — discrimination is the contribution

---

## 7. Dependencies

### 7.1 Python Packages
```
lm-eval==0.4.11
scipy>=1.10.0        # scipy.stats.spearmanr
numpy>=1.24.0        # array operations, argmax
matplotlib>=3.7.0    # figure generation
pyyaml>=6.0          # verification_state.yaml read/write
```

### 7.2 Internal Dependencies (from prior hypotheses)
- `h-e1/code/calibration_analysis.py` — `load_lmeval_samples()`, `compute_brier_decomposition()`, `compute_ece()`, `compute_delta_reliability()`
- `h-m2/code/margin_analysis.py` — `compute_logit_margins()` (logprob extraction pattern)
- `h-e1/code/results/` — lm-eval JSONL output files (Path A data source)

### 7.3 Model Registry (Risk R1 active — public fallback models)
| Size | Base | SFT | DPO | PPO |
|------|------|-----|-----|-----|
| 1.4b | EleutherAI/pythia-1.4b | lomahony/pythia-1.4b-deduped-tldr | Leogrin/pythia-1.4b-sft-tldr-dpo | usvsnsp/pythia-1.4b-sft-tldr-ppo |
| 2.8b | EleutherAI/pythia-2.8b | lomahony/pythia-2.8b-deduped-tldr | Leogrin/pythia-2.8b-sft-tldr-dpo | usvsnsp/pythia-2.8b-sft-tldr-ppo |
| 6.9b | EleutherAI/pythia-6.9b | lomahony/pythia-6.9b-deduped-tldr | Leogrin/pythia-6.9b-sft-tldr-dpo | usvsnsp/pythia-6.9b-sft-tldr-ppo |

---

## 8. Constraints

- **No training** — analysis-only, no gradient computation
- **No new MMLU runs** — reuse H-E1 lm-eval outputs (Path A)
- **TruthfulQA runs needed** — secondary dataset not in H-E1 cache
- **Single GPU** — lm-eval inference for TruthfulQA if Path A unavailable
- **Public fallback models** — Risk R1 active (same as H-E1/H-M2)
- **Sample size:** Full test sets (MMLU: 14042, TruthfulQA: 817) — no subsampling

---

*PRD generated from Phase 2C experiment brief (h-m3/02c_experiment_brief.md) and prior hypothesis validation results (H-E1, H-M1, H-M2)*
*Phase 3 — Implementation Planning | Anonymous Pipeline*
