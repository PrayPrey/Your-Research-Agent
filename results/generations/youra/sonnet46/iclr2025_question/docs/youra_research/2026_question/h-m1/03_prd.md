# Product Requirements Document: H-M1

**Hypothesis:** H-M1 (MECHANISM PoC)
**Type:** MECHANISM
**Gate:** MUST_WORK
**Generated:** 2026-03-16
**Phase:** 3 — Implementation Planning
**Prerequisite:** H-E1 (COMPLETED, PASS — AUROC=0.709 Dialogue, 0.644 QA)

---

## Executive Summary

This PRD specifies implementation requirements for H-M1, a mechanism proof-of-concept that validates DeBERTa-v3-large-mnli's MNLI pretraining encodes graded support sensitivity sufficient to detect factual inconsistency between grounding context and generated response. This is a **pure statistical analysis experiment** — no new model inference is required. The experiment operates entirely on pre-computed NLI score matrices from H-E1 (`h-e1/results/h-e1_results.json`), applying KL divergence and Wilcoxon rank-sum statistical tests to measure distribution non-uniformity and score separation.

**Hypothesis Statement:**
> DeBERTa-v3-large-mnli's MNLI pretraining encodes graded support sensitivity sufficient to detect factual inconsistency between grounding context and generated response — demonstrated by NLI score distributions being significantly non-uniform on HaluEval (KL divergence from uniform > 0.05; Wilcoxon p < 0.05 for hallucinated vs. non-hallucinated score separation).

---

## 1. Problem Statement

### 1.1 Research Question

Does DeBERTa-v3-large-mnli's MNLI pretraining encode graded support sensitivity that manifests as statistically non-uniform NLI score distributions on HaluEval, with significant separation between hallucinated and non-hallucinated examples? This validates the mechanism underlying H-E1's positive AUROC results.

### 1.2 Motivation

- H-E1 confirmed NLI contradiction scores achieve AUROC=0.709 (Dialogue) and 0.644 (QA), but did not characterize *why* — specifically whether DeBERTa encodes graded sensitivity or produces binary-like scores
- Understanding the distribution shape (non-uniform vs. near-uniform) determines whether net-contradiction framing (H-M3) and sentence-level aggregation (H-M4) will be effective
- KL divergence from uniform quantifies the degree of graded sensitivity; Wilcoxon rank-sum tests whether that sensitivity is discriminatively targeted at hallucination detection
- H-E1 already passed non_uniform=True for all 3 tasks — H-M1 formally quantifies this with rigorous statistical tests

### 1.3 Scope

- **In scope:** Statistical analysis of pre-computed H-E1 NLI scores; KL divergence computation; Wilcoxon rank-sum testing; near-uniform proportion analysis; visualization of score distributions
- **Out of scope:** New model inference (H-E1 scores reused); model fine-tuning; training; new dataset loading beyond labels; ablation variants (deferred to H-M2/M3/M4)
- **Critical dependency:** `h-e1/results/h-e1_results.json` must exist with shape (20000, 3) per task

---

## 2. Functional Requirements

### FR-1: Data Loading

**FR-1.1 Load Pre-computed H-E1 Score Matrices**
- Load `../h-e1/results/h-e1_results.json` (relative to h-m1/code/) or absolute equivalent
- Expected format: `{"dialogue": [[p_c, p_n, p_e], ...], "qa": [...], "summarization": [...]}`
- Expected shape: 20,000 rows × 3 columns per task (60,000 total NLI evaluations)
- Verify: `len(scores_by_task[task]) == 20000` for each of 3 tasks
- Convert to numpy arrays: `scores_nxt3 = np.array(scores_by_task[task_name])  # shape (N,3)`
- Log: "H-E1 scores loaded: {N} pairs per task, shape {scores_nxt3.shape}"

**FR-1.2 Load HaluEval Labels**
- Load labels from `pminervini/HaluEval` (expected cached from H-E1 run)
- Dialogue: `load_dataset("pminervini/HaluEval", "dialogue_data")` — field `hallucination` ("yes"→1, "no"→0)
- QA: `load_dataset("pminervini/HaluEval", "qa_data")` — field `hallucination`
- Summarization: `load_dataset("pminervini/HaluEval", "summarization_data")` — field `hallucination`
- Apply same balanced-pair interleaving logic as H-E1 to produce N=20,000 binary labels per task
- Verify: `labels_n.shape == (20000,)` and `labels_n.sum() == 10000` (balanced 50/50)

**FR-1.3 Uniform Baseline Distribution**
- Construct analytically: `uniform = np.array([1/3, 1/3, 1/3])`
- Represents null hypothesis (no discriminative NLI capability)
- Used as reference for KL divergence computation

### FR-2: Statistical Analysis

**FR-2.1 KL Divergence from Uniform**
- For each task: compute `kl_divergence = entropy(class_means + 1e-10, uniform + 1e-10)`
  - `class_means = scores_nxt3.mean(axis=0)  # shape (3,) — per-class mean probability`
  - Use `scipy.stats.entropy(pk, qk)` (relative entropy / KL divergence)
  - Also compute per-class: KL for P(contradiction), P(neutral), P(entailment) marginals
- Pass threshold: `kl_divergence > 0.05` (nats) — **must pass on ALL 3 tasks** for gate
- Report: `kl_divergence_from_uniform` per task (float, nats)

**FR-2.2 Wilcoxon Rank-Sum Test**
- For each task: separate P(contradiction) scores by label
  - `contra_scores = scores_nxt3[:, 0]  # P(contradiction) column`
  - `hal_scores = contra_scores[labels_n == 1]  # hallucinated examples`
  - `corr_scores = contra_scores[labels_n == 0]  # non-hallucinated examples`
- Compute: `stat, pvalue = scipy.stats.ranksums(hal_scores, corr_scores)`
- Pass threshold: `pvalue < 0.05` — **must pass on ≥ 2/3 tasks** for gate
- Report: `wilcoxon_pvalue` and `wilcoxon_statistic` per task

**FR-2.3 Near-Uniform Proportion**
- Compute proportion of examples where ALL 3 class probabilities are within 0.05 of 1/3:
  - `near_uniform = np.all(np.abs(scores_nxt3 - 1/3) < 0.05, axis=1)`
  - `p_near_uniform = near_uniform.mean()`
- Diagnostic: if `p_near_uniform > 0.50` → investigate 512-token truncation; if all tasks > 0.50 → mechanism fails
- Report: `p_near_uniform` per task (float, proportion)

**FR-2.4 Class Means and Cohen's d**
- Report `class_means = scores_nxt3.mean(axis=0).tolist()` per task (for interpretability)
- Compute Cohen's d for P(contradiction) separation:
  - `d = (mean_hal - mean_corr) / pooled_std`
  - `pooled_std = sqrt(((n1-1)*std1^2 + (n2-1)*std2^2) / (n1+n2-2))`
- Report: `cohens_d` per task

**FR-2.5 Gate Evaluation**
- After all 3 tasks analyzed:
  - `kl_all_pass = all(results[task]["kl_passes"] for task in tasks)`
  - `wilcoxon_count = sum(results[task]["wilcoxon_passes"] for task in tasks)`
  - `gate_pass = kl_all_pass and wilcoxon_count >= 2`
- Log gate result: "GATE: {'PASS' if gate_pass else 'FAIL'} (KL_all={kl_all_pass}, Wilcoxon_count={wilcoxon_count}/3)"

### FR-3: Mechanism Activation Verification

**FR-3.1 Pre-Condition Check**
- Verify H-E1 results file exists: `h-e1/results/h-e1_results.json`
- Verify shape: each task has 20,000 rows × 3 columns
- If file missing: log `ERROR: h-e1/results/h-e1_results.json not found — re-run H-E1 first` → EXIT

**FR-3.2 Mechanism Indicator Logging**
- Log per-task mechanism indicators:
  - `"kl_passes": kl_divergence > 0.05`
  - `"wilcoxon_passes": pvalue < 0.05`
  - `"not_near_uniform": p_near_uniform < 0.10`
- Log activation summary: "Mechanism indicators: KL={kl_all_pass}, Wilcoxon={wilcoxon_count}/3, Not-Near-Uniform={all not_near_uniform checks}"

**FR-3.3 Failure Detection**
- If `p_near_uniform > 0.50` on any task → Log WARN: "Near-uniform scores detected — possible 512-token truncation artifact"
- If `kl_divergence < 0.05` on any task → Log WARN: "KL below threshold on {task} — investigating"
- If all AUROCs < 0.50 (from H-E1, already verified) → Note inconsistency (H-E1 already passed)

### FR-4: Results Persistence

**FR-4.1 JSON Results File**
- Save per-task results to `h-m1/results/h_m1_results.json`:
```json
{
  "hypothesis": "H-M1",
  "gate": "MUST_WORK",
  "gate_pass": true/false,
  "tasks": {
    "dialogue": {
      "kl_divergence_from_uniform": 0.xxx,
      "kl_passes": true/false,
      "wilcoxon_pvalue": 0.xxx,
      "wilcoxon_statistic": xxx,
      "wilcoxon_passes": true/false,
      "p_near_uniform": 0.xxx,
      "class_means": [p_c, p_n, p_e],
      "cohens_d": 0.xxx
    },
    "qa": { ... },
    "summarization": { ... }
  },
  "summary": {
    "kl_all_pass": true/false,
    "wilcoxon_pass_count": N,
    "mechanism_activated": true/false
  }
}
```

**FR-4.2 Summary File**
- Save `h-m1/results/h_m1_summary.json` with gate-relevant fields only
- Keys: `gate_pass`, `kl_all_pass`, `wilcoxon_pass_count`, per-task KL and p-values

### FR-5: Visualization

**FR-5.1 Mandatory Figure — Gate Metrics Comparison**
- Bar chart: KL divergence per task (3 bars) with threshold line at KL=0.05
- Second subplot: Wilcoxon p-values per task (log scale) with threshold line at p=0.05
- Save to: `h-m1/figures/gate_metrics_comparison.png`

**FR-5.2 NLI Score Distribution Violin Plots (Autonomous)**
- Per-task violin plots: P(contradiction), P(neutral), P(entailment) for hallucinated vs. non-hallucinated
- Overlaid with uniform reference line (1/3)
- 3 tasks × 3 classes = 9-panel or 3-panel figure
- Save to: `h-m1/figures/score_distributions_violin.png`

**FR-5.3 KL Divergence Summary (Autonomous)**
- Bar chart: KL divergence from uniform per task × per NLI class (3×3 = 9 bars)
- Threshold line at KL=0.05
- Save to: `h-m1/figures/kl_divergence_summary.png`

**FR-5.4 Score Separation Box Plot (Autonomous)**
- Box plots: P(contradiction) for hallucinated (orange) vs. correct (blue) per task
- Annotated with Wilcoxon p-values
- Save to: `h-m1/figures/score_separation_boxplot.png`

**FR-5.5 Near-Uniform Proportion (Autonomous)**
- Stacked bar chart: p_near_uniform (failure indicator) per task
- Target: < 5% near-uniform examples
- Save to: `h-m1/figures/near_uniform_proportion.png`

---

## 3. Non-Functional Requirements

### NFR-1: Performance
- Total execution time: < 60 seconds (statistical analysis only — no GPU inference)
- No GPU required; CPU-only execution acceptable

### NFR-2: Reproducibility
- Fixed random seed: 42 (for bootstrap CIs if any)
- Deterministic: KL divergence and Wilcoxon tests are deterministic given same inputs
- Single run (MECHANISM PoC — no ensemble)

### NFR-3: Resource Usage
- No GPU requirement (statistical analysis only)
- RAM: < 4GB (60,000 × 3 float32 = ~720KB for scores)
- Disk: `h-e1/results/h-e1_results.json` must be accessible (read-only)

### NFR-4: Output Format
- Results: `h-m1/results/h_m1_results.json` (full per-task details)
- Summary: `h-m1/results/h_m1_summary.json` (gate-relevant fields)
- Figures: `h-m1/figures/*.png` (5 figures)

### NFR-5: Code Quality
- Reuse H-E1 infrastructure where possible (data.py, config.py)
- Statistical analysis in dedicated `analyze.py` or inline in `run_experiment.py`
- YAML config file (FULL tier): `h-m1/code/config.yaml` with dataclass

### NFR-6: Error Handling
- Graceful failure if H-E1 results missing (with instructive error message)
- Handle potential label alignment issues (verify N matches between scores and labels)

---

## 4. Data Specification

### 4.1 Primary Data Source

**Pre-computed Scores:** `h-e1/results/h-e1_results.json`
- Type: Local file (output of H-E1 Phase 4 execution)
- Format: JSON dictionary keyed by task name
- Shape: (20,000, 3) per task — [P(contradiction), P(neutral), P(entailment)]

**Labels:** `pminervini/HaluEval` via HuggingFace datasets (cached)

| Subset | Config | H-E1 Pairs | Balanced Split |
|--------|--------|-----------|----------------|
| Dialogue | `dialogue_data` | 20,000 pairs | 10,000 hallucinated + 10,000 correct |
| QA | `qa_data` | 20,000 pairs | 10,000 hallucinated + 10,000 correct |
| Summarization | `summarization_data` | 20,000 pairs | 10,000 hallucinated + 10,000 correct |
| **Total** | | **60,000 pairs** | **30,000 per class** |

### 4.2 Statistical Reference Baseline

- Uniform distribution: `np.array([1/3, 1/3, 1/3])`
- Represents null hypothesis H₀: DeBERTa produces random, non-informative scores
- Used for KL divergence computation only (no model inference)

---

## 5. Model Specification

### 5.1 Baseline (Statistical Reference)

| Property | Value |
|----------|-------|
| Name | Uniform distribution baseline |
| Type | Analytical (no model) |
| Output | [1/3, 1/3, 1/3] for all examples |
| Purpose | Null hypothesis for KL divergence |

### 5.2 Proposed (Pre-computed Scores)

| Property | Value |
|----------|-------|
| Model | cross-encoder/nli-deberta-v3-large |
| Source | Pre-computed scores from H-E1 |
| Parameters | ~435M (inference already done) |
| Output | (N, 3) softmax arrays loaded from JSON |
| Mode | Analysis only — no inference required |

### 5.3 Statistical Analysis Configuration

| Parameter | Value |
|-----------|-------|
| KL divergence library | `scipy.stats.entropy` |
| Rank-sum test | `scipy.stats.ranksums` |
| Significance level | α = 0.05 |
| Near-uniform threshold | 0.05 (within 5% of 1/3) |
| Random seed | 42 |
| GPU | Not required |

---

## 6. Success Criteria

### 6.1 Gate Condition (MUST_WORK)

**PASS (both conditions required):**
1. KL divergence from uniform > 0.05 nats on **ALL 3 tasks** (mechanism is globally active)
2. Wilcoxon rank-sum p < 0.05 on **≥ 2/3 tasks** (hallucination discrimination is statistically reliable)

**FAIL (any of the following):**
- KL < 0.05 on any task → mechanism not encoding graded sensitivity
- Wilcoxon p ≥ 0.05 on all tasks OR only 1 task → no reliable discrimination
- H-E1 results file missing → cannot execute experiment

**On FAIL:** Investigate 512-token truncation effect; run on shorter subset; if still failing → MECHANISM FAILS → STOP pipeline, write Serena failure memory

### 6.2 Expected Performance (Conservative Estimates)

| Task | Expected KL | Expected Wilcoxon p | Basis |
|------|-------------|---------------------|-------|
| Dialogue | ~0.20-0.35 | << 0.05 | H-E1 AUROC=0.709, non_uniform=True |
| QA | ~0.15-0.30 | << 0.05 | H-E1 AUROC=0.644, non_uniform=True |
| Summarization | ~0.05-0.15 | < 0.05 | H-E1 AUROC=0.530, non_uniform=True |

Note: H-E1 already confirmed `non_uniform=True` for all 3 tasks — H-M1 is expected to PASS.

---

## 7. Dependencies

### 7.1 Hard Dependencies

| Dependency | Required | Fallback |
|-----------|----------|---------|
| `h-e1/results/h-e1_results.json` | YES | Re-run H-E1 inference (~30 min GPU) |
| `pminervini/HaluEval` (HuggingFace, cached) | YES | Re-download |
| H-E1 validated: gate.satisfied=true | YES (prerequisite) | Already verified |

### 7.2 Python Packages

```
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
datasets>=2.14.0
pyyaml>=6.0
```

Note: No `torch`, `sentence-transformers`, or `transformers` required (no inference).

### 7.3 External References

- HaluEval paper: Li et al. (2023) — `pminervini/HaluEval`
- SummaC: Laban et al. (2022) — NLI-based factual consistency, graded sensitivity
- TRUE: Honovich et al. (2022) — NLI generalization to factuality (zero-shot AUROC ~0.60-0.65)
- H-E1 Implementation: local `h-e1/code/` — predecessor, source of pre-computed scores

---

## 8. Risks and Mitigations

| Risk | Probability | Mitigation |
|------|-------------|------------|
| H-E1 results.json missing | Low (H-E1 completed) | Check file before running; log clear error message |
| Label alignment mismatch (N ≠ 20000) | Low | Verify `len(scores) == len(labels)` per task |
| Near-uniform scores (p_near_uniform > 0.50) | Low (H-E1 non_uniform=True) | Investigate truncation; run on <200-token subset |
| KL below threshold on summarization | Medium | Summarization had lowest AUROC (0.530) — KL may be borderline |
| Wilcoxon p borderline on summarization | Medium | Only 2/3 required — dialogue and QA expected to pass strongly |

---

## 9. Code Architecture (FULL Tier)

### 9.1 Directory Structure

```
h-m1/
├── code/
│   ├── config.py          # ExperimentConfig dataclass (reuse/extend H-E1)
│   ├── config.yaml        # YAML configuration file
│   ├── data.py            # Score loading + label loading utilities
│   ├── analyze.py         # KL divergence, Wilcoxon, near-uniform analysis
│   ├── visualize.py       # All 5 required figures
│   └── run_experiment.py  # Main entry point
├── results/
│   ├── h_m1_results.json  # Full per-task results
│   └── h_m1_summary.json  # Gate-relevant summary
└── figures/
    ├── gate_metrics_comparison.png
    ├── score_distributions_violin.png
    ├── kl_divergence_summary.png
    ├── score_separation_boxplot.png
    └── near_uniform_proportion.png
```

### 9.2 Main Execution Flow

```python
# run_experiment.py (main)
1. Load config from config.yaml
2. Pre-condition check: verify h-e1/results/h-e1_results.json exists
3. Load pre-computed scores (FR-1.1)
4. Load HaluEval labels (FR-1.2)
5. For each task in [dialogue, qa, summarization]:
   a. Run analyze_nli_distribution(scores_nxt3, labels_n, task_name)
   b. Log mechanism indicators
6. Evaluate gate: kl_all_pass AND wilcoxon_count >= 2
7. Save results JSON (FR-4.1, FR-4.2)
8. Generate all 5 figures (FR-5.x)
9. Log final gate result: PASS or FAIL
```

---

## 10. Traceability

| Specification | Source |
|--------------|--------|
| Dataset: HaluEval | Phase 2B §1.3, H-E1 implementation |
| Dataset size: 20,000 pairs per task (balanced) | H-E1 data.py, h-e1/04_validation.md |
| Pre-computed scores reuse | Phase 2C 02c_experiment_brief.md §Continuation Context |
| KL divergence threshold (0.05 nats) | Phase 2B §2.2 H-M1 verification protocol |
| Wilcoxon rank-sum test | Phase 2B §2.2 H-M1 verification protocol |
| Success: KL > 0.05 on ALL 3 tasks | Phase 2C 02c_experiment_brief.md §Gate Condition |
| Success: Wilcoxon p < 0.05 on ≥2/3 | Phase 2C 02c_experiment_brief.md §Gate Condition |
| scipy.stats.entropy, ranksums | Standard library — phase 2C pseudo-code |
| Visualization requirements | Phase 2C 02c_experiment_brief.md §Visualization |
| FULL tier (MECHANISM type) | workflow.yaml task_constraints |

---

*PRD generated inline by Phase 3 workflow (BMAD PRD workflow files not found — generated directly)*
*Hypothesis: H-M1 | Type: MECHANISM | Tier: FULL | Budget: 30 tasks*
