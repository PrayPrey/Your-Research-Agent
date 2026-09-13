# Product Requirements Document: H-M1
## Token Entropy vs. Semantic Entropy Divergence Analysis

**Hypothesis:** H-M1 (MECHANISM — Causal Step 1)
**Type:** INCREMENTAL (builds on H-E1)
**Date:** 2026-05-11
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Tier:** FULL (30 task max)

---

## 1. Executive Summary

H-M1 tests whether token-level entropy and semantic entropy capture *different* uncertainty sources by measuring their Pearson correlation on 2,000 HaluEval-QA examples. This is a **pure analysis experiment** — zero new LLM inference required. All UQ scores are reused from H-E1 validated outputs. The MUST_WORK gate passes if the 95% bootstrap CI upper bound for Pearson r is below 0.9, confirming signal non-redundancy.

**Critical context from H-E1:** Semantic entropy showed degenerate behavior (AUROC=0.5, zero-width CI), suggesting NLI clustering may produce constant cluster counts. H-M1 must diagnose and document this behavior as primary experimental output.

---

## 2. Problem Statement

**Research Question:** Do token entropy and semantic entropy capture fundamentally different sources of uncertainty in LLM outputs on factual QA tasks?

**Motivation:** If the two signals are highly correlated (r ≥ 0.9), semantic entropy offers no mechanistic advantage over simpler token entropy. If they diverge (r < 0.9), this confirms that NLI clustering filters surface-form noise, providing a distinct uncertainty signal. The H-E1 finding of degenerate semantic entropy adds an important diagnostic dimension: understanding *why* the signals may be uncorrelated (true divergence vs. clustering collapse).

**Success Condition:** Pearson r < 0.9 with 95% bootstrap CI upper bound < 0.9 (OR documented degenerate case as evidence of mechanism divergence).

---

## 3. Functional Requirements

### FR-1: Load Pre-computed UQ Scores from H-E1
- **Source:** `../h-e1/code/outputs/uq_scores/token_entropy_mean.json` (2,000 floats)
- **Source:** `../h-e1/code/outputs/uq_scores/semantic_entropy.json` (2,000 floats)
- **Action:** Load both JSON arrays, convert to numpy arrays of shape `(2000,)`
- **Validation:** Assert `len(te) == len(se) == 2000`

### FR-2: Degenerate Case Diagnosis
- **Check:** `np.std(se) < 1e-6` → semantic entropy is constant
- **If degenerate:**
  - Load stochastic samples from `../h-e1/code/outputs/stochastic_samples.jsonl`
  - Re-run NLI clustering (using h-e1/code/uq_signals.py) with cluster_id logging
  - Compute cluster count distribution: mean, std, histogram of cluster counts (1–5) across 2,000 examples
  - Report: "NLI clustering collapsed to single cluster for X% of examples"
  - Gate interpretation: degenerate SE (std≈0) is itself evidence of mechanism divergence (r is undefined, not ≥0.9)
- **If non-degenerate:** Proceed to Pearson r analysis

### FR-3: Pearson Correlation with Bootstrap CI
- **Metric:** Pearson r between token_entropy_mean and semantic_entropy
- **Bootstrap:** N=1000 resamples, seed=42, with-replacement
- **CI:** 95% CI via percentile method `[2.5, 97.5]`
- **Gate check:** `ci_upper < 0.9` → PASS
- **Report:** r_obs, ci_lower, ci_upper, gate_pass (bool)

### FR-4: Spearman Rank Correlation (Robustness Check)
- **Metric:** Spearman ρ between token_entropy_mean and semantic_entropy
- **Library:** `scipy.stats.spearmanr`
- **Report:** ρ, p-value (two-tailed)

### FR-5: Divergence Analysis
- **Metric:** Pointwise absolute divergence: `divergence = |te - se|` for each of 2,000 examples
- **High-divergence threshold:** `mean(divergence) + std(divergence)`
- **Report:** n_high_divergence examples, threshold value

### FR-6: Lexical Diversity Analysis (TTR)
- **Scope:** High-divergence examples identified in FR-5
- **Source:** `../h-e1/code/outputs/stochastic_samples.jsonl` (5 stochastic samples per example)
- **Metric:** Type-Token Ratio (TTR) = unique_tokens / total_tokens across N=5 samples
- **Report:** Mean TTR for high-divergence vs. low-divergence examples

### FR-7: AUROC Context Report
- **Source:** Pre-computed from H-E1 (`experiment_results.json`) or re-computed from UQ scores + labels
- **Labels:** `../h-e1/code/data/halueval_qa_2k.json` (field: `hallucination`, binary)
- **Report:** AUROC for token_entropy_mean and semantic_entropy (context only, NOT gate metric)

### FR-8: Gate Evaluation and Report
- **Gate:** MUST_WORK — Pearson r < 0.9 with 95% CI upper bound < 0.9
- **Degenerate case treatment:** SE constant → r undefined → gate interpretation = PASS with documentation
- **Output:** `experiment_results.json` with all metrics + gate_result (PASS/FAIL)
- **Output:** `04_validation.md` report

### FR-9: Visualization
- **Required (mandatory):** Scatter plot of token_entropy_mean vs. semantic_entropy with Pearson r annotation and identity line (y=x). Saved to `h-m1/figures/scatter_te_vs_se.png`
- **Additional (LLM autonomous):**
  - Cluster count distribution histogram (1–5 clusters) → `h-m1/figures/cluster_count_dist.png`
  - Divergence distribution plot (|TE-SE|) → `h-m1/figures/divergence_dist.png`
  - TTR vs. divergence scatter → `h-m1/figures/ttr_vs_divergence.png`
  - Bootstrap Pearson r CDF with gate threshold → `h-m1/figures/bootstrap_ci.png`
- **Output dir:** `h-m1/figures/` (create if not exists)

---

## 4. Data Specification

### 4.1 Primary Dataset (Reused from H-E1)
- **Name:** HaluEval-QA (QA Subset)
- **Source paper:** Li et al. (2023) arXiv:2305.11747
- **HuggingFace:** pminervini/HaluEval (qa_samples)
- **Size:** 2,000 stratified examples (1,000 hallucinated + 1,000 factual, seed=42)
- **Cache:** `../h-e1/code/data/halueval_qa_2k.json`
- **Format:** JSON list of dicts with `question`, `answer`, `hallucination` (int 0/1)
- **Download:** NOT REQUIRED — already cached from H-E1
- **Preprocessing:** None required

### 4.2 Pre-computed Inputs (Reused from H-E1)
| File | Shape | Description |
|------|-------|-------------|
| `../h-e1/code/outputs/uq_scores/token_entropy_mean.json` | (2000,) float | Token entropy mean per example |
| `../h-e1/code/outputs/uq_scores/semantic_entropy.json` | (2000,) float | Semantic entropy per example |
| `../h-e1/code/outputs/stochastic_samples.jsonl` | 2000 lines | 5 stochastic samples per example |
| `../h-e1/code/data/halueval_qa_2k.json` | 2000 dicts | Dataset with labels |

### 4.3 No Synthetic Data
Policy: ✅ COMPLIANT — real benchmark dataset only.

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- All randomness seeded: `seed=42` for bootstrap resampling
- No new LLM inference (zero stochasticity from generation)
- Results deterministic given fixed H-E1 outputs

### NFR-2: Compute Budget
- **GPU:** NOT REQUIRED — pure CPU analysis
- **Estimated runtime:** < 2 minutes total
  - Score loading: < 1 second
  - Bootstrap N=1000: < 5 seconds
  - TTR analysis: < 10 seconds
  - Visualization: < 30 seconds

### NFR-3: Error Handling
- Missing H-E1 score files → `FileNotFoundError` with clear message and remediation
- Constant SE (std < 1e-6) → Degenerate case handling (FR-2), not crash
- NaN in Pearson r → Both signals constant; report and document
- Corrupted JSON → Validate array length before proceeding

### NFR-4: Code Structure
- Single experiment script: `h-m1/code/run_experiment.py`
- Reuse H-E1 utility functions where applicable (data.py, uq_signals.py)
- No new ML model loading

### NFR-5: Statistical Rigor
- Bootstrap CI with Fisher z-transform for robustness on bounded correlation values
- Two-tailed p-values for all significance tests
- Report exact values (not rounded) in experiment_results.json

---

## 6. Evaluation Metrics

### Primary (Gate)
| Metric | Computation | Gate Threshold |
|--------|-------------|----------------|
| Pearson r | `np.corrcoef(te, se)[0,1]` | r < 0.9 |
| 95% CI upper bound | Bootstrap percentile [97.5] | CI_upper < 0.9 → PASS |

### Secondary (Informative)
| Metric | Computation | Expected |
|--------|-------------|----------|
| Spearman ρ | `scipy.stats.spearmanr` | 0.3–0.8 |
| n_high_divergence | \|TE-SE\| > mean+1SD | > 0 |
| Mean TTR (high-div) | unique_tokens/total per example | > Mean TTR (low-div) |
| Cluster count dist. | NLI cluster_ids per example | Mean < 5 (aggregation) |

### Diagnostic
| Metric | Trigger | Action |
|--------|---------|--------|
| SE std | < 1e-6 | Flag degenerate, run cluster diagnosis |
| Pearson r NaN | both constant | Report double-degenerate case |

---

## 7. Dependencies

### 7.1 Python Packages
```
numpy>=1.24
scipy>=1.10
scikit-learn>=1.2  # for roc_auc_score
matplotlib>=3.7
seaborn>=0.12
tqdm>=4.65
```

### 7.2 Internal Dependencies (H-E1 Reuse)
- `../h-e1/code/uq_signals.py` — compute_semantic_entropy() with cluster_id access
- `../h-e1/code/data.py` — load_halueval_qa()
- `../h-e1/code/evaluate.py` — compute_auroc()
- H-E1 UQ score files (see 4.2)

### 7.3 External References
- lorenzkuhn/semantic_uncertainty — NLI clustering reference implementation
- Kuhn et al. (2023) arXiv:2302.09664 — correlation analysis methodology

---

## 8. Success Criteria

### Primary (MUST_WORK Gate)
- [ ] Pearson r computed without error (or degenerate case documented)
- [ ] 95% CI upper bound < 0.9 (or degenerate SE documented as gate-pass evidence)
- [ ] experiment_results.json written with all metrics
- [ ] 04_validation.md report written with gate decision

### Secondary
- [ ] Spearman ρ computed as robustness check
- [ ] Divergence analysis completed (n_high_divergence reported)
- [ ] TTR analysis on high-divergence examples (if n_high_divergence > 0)
- [ ] All 5 figures generated in h-m1/figures/

### Infrastructure
- [ ] Code runs end-to-end without crash
- [ ] All H-E1 input files loaded successfully
- [ ] Runtime < 2 minutes

---

## 9. Out of Scope

- New LLM inference (no forward passes)
- Model fine-tuning or training
- New dataset download (all data reused from H-E1)
- Mistral-7B analysis (H-M3 scope)
- SelfCheckGPT analysis (H-E1 scope)
- Multi-model comparison (H-M3 scope)

---

## 10. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SE scores constant (degenerate) | HIGH (H-E1 evidence) | Medium | FR-2 degenerate case handling; treat as gate-pass evidence |
| H-E1 score files missing/corrupted | Low | High | FR-3 FileNotFoundError + clear remediation message |
| Both TE and SE constant | Very Low | Medium | NaN handling in Pearson r; report double-degenerate |
| CI_upper ≥ 0.9 (gate FAIL) | Low | High | Report mechanism not confirmed; feed forward to H-M2 design |

---

*Generated by Phase 3 PRD Workflow (inline execution — TEST no-MCP environment)*
*Input: h-m1/02c_experiment_brief.md | Phase 2C COMPLETED 2026-05-11*
*Next: 03_architecture.md (Architecture Agent)*
