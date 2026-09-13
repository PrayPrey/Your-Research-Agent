---
title: "PRD: H-E1 — DPO/SFT Alignment Fingerprint Detection"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
date: "2026-08-31"
author: yoon303@ust.ac.kr
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - data_specification
  - success_criteria
  - dependencies
phase: Phase 3
source: 02c_experiment_brief.md
---

# PRD: H-E1 — DPO/SFT Alignment Fingerprint Detection via 4-Benchmark Trustworthiness Suite

## 1. Executive Summary

This experiment tests whether the alignment strategy (DPO vs. SFT) of 7B language models leaves a detectable "fingerprint" in 4-dimensional trustworthiness benchmark score vectors. We evaluate ≥6 matched DPO/SFT 7B model pairs on TruthfulQA MC2, BBQ, WinoGrande, and WinoGender using lm-evaluation-harness, then apply a k-NN (k=1) classifier with leave-one-out cross-validation and a permutation test (1000 iterations) to determine if alignment strategy is linearly separable in benchmark space.

**Gate:** MUST_WORK — LOO accuracy ≥0.67 AND permutation p≤0.05 required for H-M1 activation.

## 2. Problem Statement

Alignment research produces DPO- and SFT-aligned models at scale, but it is unclear whether standard trustworthiness benchmarks (TruthfulQA, BBQ, WinoGrande, WinoGender) carry systematic information about alignment strategy beyond raw performance. If they do, benchmark score vectors form a detectable "alignment fingerprint" — a prerequisite for the mechanism hypotheses (H-M1, H-M2, H-M3).

**Research Question:** Do 4D benchmark score vectors of DPO-aligned 7B models systematically separate from SFT-aligned models at k-NN LOO accuracy ≥67%, permutation p≤0.05?

## 3. Functional Requirements

### FR-1: Model Pair Curation
- **FR-1.1**: Curate ≥6 matched DPO/SFT 7B (±1B) model pairs from HuggingFace Hub.
- **FR-1.2**: Each pair must share the same base model checkpoint, training data (or comparable), and differ only in alignment strategy (DPO vs. SFT).
- **FR-1.3**: Record each pair in `model_pairs.json` with fields: `sft_model_id`, `dpo_model_id`, `base_model_id`, `sft_dataset`, `dpo_dataset`, `source`.
- **FR-1.4 (Primary Pair):** Include `HuggingFaceH4/zephyr-7b-sft-full` (SFT) vs `HuggingFaceH4/zephyr-7b-dpo-full` (DPO) as the controlled pair.

### FR-2: Benchmark Evaluation
- **FR-2.1**: Run lm-evaluation-harness v0.4.3 for all models across tasks: `truthfulqa_mc2`, `bbq`, `winogrande`, `winograd_wsc`.
- **FR-2.2**: Use full test sets (no subsampling): TruthfulQA=817, BBQ≈58,000, WinoGrande=1267, WinoGender=273.
- **FR-2.3**: Inference only — no training, no weight modification. bfloat16, batch_size=8.
- **FR-2.4**: Save per-model results to `results/<model_id>/results.json`.
- **FR-2.5 (Risk R2):** If `bbq` task unavailable in pinned version, substitute `winogrande` as fairness proxy and document substitution.

### FR-3: Score Matrix Construction
- **FR-3.1**: Load all model result JSONs and construct score matrix `X: (2n, 4)` where rows=models, cols=[TruthfulQA_MC2, BBQ, WinoGrande, WinoGender].
- **FR-3.2**: Construct label vector `y: (2n,)` where 0=SFT, 1=DPO. Labels must be balanced (n_SFT = n_DPO).
- **FR-3.3**: Verify all 4 scores present and in [0, 1] for every model. Raise assertion error if any missing.

### FR-4: Classification Pipeline
- **FR-4.1**: Fit k-NN classifier (k=1, Euclidean distance) with sklearn `KNeighborsClassifier`.
- **FR-4.2**: Run leave-one-out cross-validation (`LeaveOneOut()`) and compute mean accuracy.
- **FR-4.3**: Run permutation test: `sklearn.model_selection.permutation_test_score` with 1000 permutations, LOO CV, accuracy scoring, random_state=42.
- **FR-4.4 (Sensitivity, Risk R5):** Also run and report LOO accuracy for k=3 and k=5.

### FR-5: Visualization
- **FR-5.1 (Mandatory):** Gate metrics bar chart — LOO accuracy vs 0.67 threshold vs 0.50 chance; p-value annotated.
- **FR-5.2:** PCA 2D projection of 4D score vectors, colored by DPO/SFT.
- **FR-5.3:** Per-benchmark boxplots (DPO vs SFT for each of 4 tasks).
- **FR-5.4:** Permutation null distribution histogram vs observed LOO accuracy.
- **FR-5.5:** Model pair heatmap (rows=models, cols=4 benchmarks, color=alignment strategy).
- **FR-5.6:** Save all figures to `docs/youra_research/h-e1/figures/`.

### FR-6: Validation & Reporting
- **FR-6.1**: Print classification report: LOO accuracy, p-value, permutation distribution stats.
- **FR-6.2**: Determine PASS/FAIL/INCONCLUSIVE based on success criteria.
- **FR-6.3**: Save results summary to `results/summary.json`.

## 4. Data Specification

| Benchmark | lm-eval Task | Metric | Full Test Size | Download |
|-----------|-------------|--------|----------------|----------|
| TruthfulQA MC2 | `truthfulqa_mc2` | MC2 accuracy | 817 questions | Auto (lm-eval) |
| BBQ | `bbq` | Accuracy (ambiguous) | ~58,000 Q | Auto (lm-eval) |
| WinoGrande | `winogrande` | Accuracy | 1,267 | Auto (lm-eval) |
| WinoGender | `winograd_wsc` | Accuracy | 273 items | Auto (lm-eval) |

**All datasets auto-downloaded by lm-eval from HuggingFace Datasets. No manual download required.**

### Model Pairs

**Primary pair (controlled):**
- SFT: `HuggingFaceH4/zephyr-7b-sft-full` — Mistral-7B-v0.1 base, UltraChat-200k
- DPO: `HuggingFaceH4/zephyr-7b-dpo-full` — same base + UltraFeedback

**Community pairs (≥5 additional):** Curated at runtime per FR-1.2–1.3. Total ≥6 pairs (≥12 models).

## 5. Non-Functional Requirements

| NFR | Value |
|-----|-------|
| Reproducibility | Pin lm-eval to v0.4.3; random_state=42 throughout |
| Hardware | CUDA GPU ≥24GB VRAM (bfloat16 inference for 7B models) |
| Statistical power | ≥6 pairs (12 models) for permutation test validity |
| Evaluation standard | 0-shot for all tasks (TruthfulQA and BBQ standard) |
| Inference framework | lm-evaluation-harness (no custom model code) |

## 6. Success Criteria

| Outcome | Condition | Action |
|---------|-----------|--------|
| PASS | LOO accuracy ≥ 0.67 AND p ≤ 0.05 | H-E1 gate satisfied → activate H-M1 |
| FAIL | LOO accuracy < 0.50 | H-E1 FAILS — publish as informative null; stop |
| INCONCLUSIVE | 0.50 ≤ LOO accuracy < 0.67 | Explore additional pairs, alternative metrics |

## 7. Dependencies

### 7.1 Python Packages

```
lm-eval==0.4.3
scikit-learn>=1.3.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
transformers>=4.35.0
torch>=2.0.0
huggingface_hub>=0.19.0
```

### 7.2 External Repositories (Reference Only)

| Repo | URL | Use |
|------|-----|-----|
| lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | Benchmark evaluation |
| alignment-handbook | https://github.com/huggingface/alignment-handbook | Model pair documentation |

### 7.3 Compute Requirements

- GPU: A100 40GB or equivalent (bfloat16 7B inference)
- Storage: ~100GB (7B model weights × ≥12 models; benchmark datasets cached by lm-eval)
- Time: ~1.5–2h per model pair (4 benchmarks, full test sets); ~9–12h total for ≥6 pairs

## 8. Traceability

| Item | Source |
|------|--------|
| 4-benchmark suite | 02c_experiment_brief.md §Dataset |
| ≥6 pairs | 02c_experiment_brief.md §Models |
| k-NN LOO + permutation | 02c_experiment_brief.md §Evaluation |
| Sensitivity k=3,k=5 | 02c_experiment_brief.md §Training Protocol (R5) |
| BBQ fallback | 02c_experiment_brief.md §Mechanism Failure Detection (R2) |
| Visualization specs | 02c_experiment_brief.md §Visualization Requirements |
