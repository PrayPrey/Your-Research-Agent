---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
hypothesis_id: h-m3
date: "2026-08-25"
author: "yoon303@ust.ac.kr"
---

# Product Requirements Document: H-M3

## 1. Executive Summary

H-M3 tests whether SelfCheckGPT BERTScore (SCG) achieves practical equivalence (AUROC within 0.03) to Semantic Entropy (SE) on hallucination detection for Llama-2-7B on TriviaQA dev. This is a continuation experiment reusing the h-e2-v2 K=10 sample cache (N=98 questions). The proposed method (SCG) uses pairwise BERTScore consistency without NLI inference — a structurally independent predictor addressing H-M2's failure (monotone transform). The gate is SHOULD_WORK (non-blocking).

**Deliverable:** Runnable Python experiment producing per-question SCG uncertainty scores, AUROC comparison (SCG vs SE vs TE), bootstrap 95% CIs, mechanism verification indicators, and figures.

---

## 2. Problem Statement

**Research Gap:** No published direct comparison of SCG-BERTScore vs SE AUROC on TriviaQA at 7B scale exists (Manakul et al. 2023 evaluated on WikiBio; Xiong et al. 2023 used verbalized confidence).

**Hypothesis:** BERTScore agreement implicitly captures semantic consistency without NLI inference. If true, practitioners can skip the expensive NLI model at 7B scale.

**Context:** H-E1 established SE AUROC ≈ 0.54–0.57 and TE AUROC ≈ 0.49–0.52 on N=98. H-M2 failed due to experiment design error (ablated predictor was monotone transform of SE). H-M3 uses SCG — genuinely independent of SE.

---

## 3. Functional Requirements

### FR-1: Data Loading
- **FR-1.1:** Load K=10 stochastic samples per question from h-e2-v2 cache
  - Cache: `_archive/20260825T162535_routing_recovery/h-e2-v2/code/results/interim_cache.jsonl`
  - Via: `sys.path.insert(0, "../../h-e1/code"); from data import load_h_e2v2_samples`
- **FR-1.2:** Load SE scores and EM labels from h-e1 results cache
  - `../../h-e1/results.json` → fields: `se_scores`, `em_labels`
- **FR-1.3:** Load TE scores from h-e1 results cache
  - `../../h-e1/results.json` → field: `te_scores` (or recompute token entropy if missing)
- **FR-1.4:** Validate alignment: N=98, K=10 samples per question, binary EM labels

### FR-2: SCG BERTScore Computation (Proposed Model)
- **FR-2.1:** Install/import `selfcheckgpt` package: `from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore`
- **FR-2.2:** Initialize with `rescale_with_baseline=True`
- **FR-2.3:** For each question: treat each answer as a single sentence (no segmentation)
- **FR-2.4:** Use samples[0] as primary response; samples[1:] as K-1=9 stochastic samples
- **FR-2.5:** Call `selfcheck.predict(sentences=[primary], sampled_passages=others)`
- **FR-2.6:** SCG uncertainty = `float(sent_scores.mean())` — higher = more uncertain
- **FR-2.7:** Produce `scg_scores: dict[question_id, float]`, all values in [0, 1]

### FR-3: Mechanism Verification
- **FR-3.1:** Implement `verify_scg_mechanism(scg_scores, em_labels, se_auroc) -> (bool, dict, float)`
- **FR-3.2:** Check 4 indicators: `scores_in_range`, `scores_have_variance` (std > 0.01), `auroc_computable` (both labels present), `auroc_not_random` (AUROC > 0.45)
- **FR-3.3:** Log mechanism activation result

### FR-4: Baseline Models (Reuse)
- **FR-4.1:** SE baseline — load `se_scores` from h-e1 results (no recomputation)
- **FR-4.2:** TE baseline — load `te_scores` from h-e1 results (no recomputation)

### FR-5: Evaluation
- **FR-5.1:** Reuse `bootstrap_auroc(scores, labels, n_boot=1000, seed=42)` from `h-m2/code/evaluate.py`
- **FR-5.2:** Compute: `auroc_scg`, `auroc_se`, `auroc_te` with 95% CIs
- **FR-5.3:** Compute gate metric: `delta = |auroc_scg - auroc_se|`
- **FR-5.4:** Compute secondary: `scg_vs_te_advantage = auroc_scg - auroc_te`
- **FR-5.5:** Gate pass: `delta <= 0.03`

### FR-6: Ablation / Mechanism Indicators (All Required)
- **FR-6.1:** `scores_in_range`: all scg_scores in [0.0, 1.0]
- **FR-6.2:** `scores_have_variance`: std(scg_scores) > 0.01
- **FR-6.3:** `auroc_computable`: both 0 and 1 present in em_labels
- **FR-6.4:** `auroc_not_random`: scg_auroc > 0.45

### FR-7: Results Persistence
- **FR-7.1:** Save `results.json` to `h-m3/` with fields: `scg_scores`, `se_scores`, `te_scores`, `auroc_scg`, `auroc_se`, `auroc_te`, `delta`, `gate_passed`, `mechanism_indicators`, `ci_scg`, `ci_se`, `ci_te`
- **FR-7.2:** Save all figures to `h-m3/figures/`

### FR-8: Visualization
- **FR-8.1 (Mandatory):** Bar chart — SCG AUROC vs SE AUROC vs TE AUROC with 95% CI error bars → `figures/auroc_comparison.png`
- **FR-8.2:** Distribution plot — SCG uncertainty scores split by EM correct/incorrect → `figures/scg_score_distribution.png`
- **FR-8.3:** Scatter plot — SCG score vs SE score per question → `figures/scg_vs_se_scatter.png`
- **FR-8.4:** ROC curves — SCG, SE, TE on same axes → `figures/roc_curves.png`

---

## 4. Data Specification

| Dataset | Source | Size | Access |
|---------|--------|------|--------|
| TriviaQA dev (N=98) | h-e2-v2 cache (local JSONL) | 98 questions × 10 samples | Local file, no download |
| SE scores | h-e1/results.json | 98 floats | Local file, no download |
| TE scores | h-e1/results.json | 98 floats | Local file, no download |
| EM labels | h-e1/results.json | 98 binary ints | Local file, no download |

**No manual dataset download required.** All data reused from prior hypotheses.

---

## 5. Non-Functional Requirements

- **NFR-1 Performance:** SCG computation ≤ 15 min CPU (7 min expected per brief); GPU optional
- **NFR-2 Reproducibility:** All randomness controlled by seed=42; deterministic bootstrap
- **NFR-3 Compatibility:** Python 3.9+; PyTorch; `selfcheckgpt>=0.1.0`; `bert_score`
- **NFR-4 Code Quality:** Single self-contained `run.py`; reuse `evaluate.py` from h-m2
- **NFR-5 Path compatibility:** Relative path imports from h-e1, h-m2 codebases
- **NFR-6 Mechanism logging:** Print mechanism indicators before AUROC computation

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Gate passed | \|SCG AUROC − SE AUROC\| ≤ 0.03 | bootstrap_auroc() |
| Mechanism activated | All 4 indicators TRUE | verify_scg_mechanism() |
| Semantic advantage | SCG AUROC > TE AUROC | bootstrap_auroc() comparison |
| Code runs | No runtime errors | End-to-end execution |
| Results saved | results.json + figures/ | File existence check |

**Gate type:** SHOULD_WORK — failure is non-blocking.

---

## 7. Dependencies

### 7.1 Python Packages (pip install)
```
selfcheckgpt>=0.1.0
bert_score
torch
numpy
sklearn
matplotlib
scipy
```

### 7.2 External Code References (no install — local path)
- `../../h-e1/code/data.py` — `load_h_e2v2_samples()`
- `../../h-m2/code/evaluate.py` — `bootstrap_auroc()`
- `../../h-e1/results.json` — SE/TE scores, EM labels

### 7.3 No External Repository Downloads Required

---

## 8. Out of Scope

- Retraining or fine-tuning any model
- Using model logits (SCG is black-box)
- Processing full TriviaQA test set beyond N=98 pilot
- Comparing additional UQ methods beyond SE, TE, SCG
