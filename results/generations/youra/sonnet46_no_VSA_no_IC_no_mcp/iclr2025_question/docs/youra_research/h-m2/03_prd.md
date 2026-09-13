---
stepsCompleted:
  - executive-summary
  - problem-statement
  - functional-requirements
  - non-functional-requirements
  - data-specification
  - evaluation-metrics
  - dependencies
  - success-criteria
hypothesis_id: h-m2
hypothesis_type: MECHANISM
gate_type: SHOULD_WORK
tier: FULL
generated_at: "2026-08-25T17:30:00+00:00"
---

# PRD: H-M2 — SE NLI Clustering Ablation Study

## 1. Executive Summary

H-M2 tests whether NLI clustering is the **causal mechanism** responsible for SE's AUROC advantage over token entropy (TE). Building on H-M1 (which confirmed real within-cluster paraphrase variance at 7.15 nats²), H-M2 ablates the NLI clustering step and measures AUROC degradation. The experiment reuses all cached artifacts from H-E1 and H-M1 — no new LLM inference required.

**Gate:** SHOULD_WORK — ΔAUROC = AUROC(SE_clustered) − AUROC(ablated_predictor) ≥ 0.03

## 2. Problem Statement

SE achieves higher AUROC than TE on TriviaQA (H-E1: gap ~0.05). H-M1 confirmed that NLI clustering groups semantically equivalent paraphrases and that within-cluster TE variance is real (7.15 nats²). H-M2 determines whether ablating NLI clustering — forcing each K=10 sample to its own cluster — degrades SE's discrimination ability, thus establishing the NLI grouping as a causally active mechanism.

**Critical Design Constraint:** Pure identity ablation yields constant SE = log(K) ≈ 2.303 for all questions → undefined AUROC. The corrected ablation uses the **within-cluster entropy fraction** as the ablated predictor: `entropy_saved / log(K)` per question. ΔAUROC = AUROC(SE_clustered) − AUROC(within_cluster_fraction_predictor) measures NLI clustering's causal contribution.

## 3. Functional Requirements

### FR-1: Cache Loading
- Load K=10 sample cache from H-E1 (exact question strings, no re-generation)
- Load pre-computed cluster IDs from H-M1 (76/98 questions have ≥1 multi-member cluster)
- Load binary EM labels from H-E1 (ground truth for AUROC)
- Load NLI model: `cross-encoder/nli-deberta-v3-large` (cached from H-M1)
- **Validation:** Assert cache files exist; assert N=98 questions loaded

### FR-2: Standard SE Computation (Control Condition)
- Compute SE_clustered for all N=98 questions using cached cluster IDs
- Formula: `−Σ p_i · log(p_i + 1e-10)` over cluster distribution
- **Validation:** Assert SE values in range [0, log(10)]

### FR-3: Ablation Predictor Computation
- For each question, compute `within_cluster_fraction = (log(K) − SE_clustered) / log(K)`
- This is the fraction of maximum entropy "saved" by NLI grouping
- **Validation:** Assert fractions in [0, 1]; assert >0 for ≥70/98 questions (from H-M1: 76 eligible)

### FR-4: AUROC Computation with Bootstrap
- AUROC_clustered: `roc_auc_score(em_labels, se_clustered_scores)` — N=98
- AUROC_ablated: `roc_auc_score(em_labels, within_cluster_fractions)` — N=98
- Bootstrap: 1000 iterations (stratified resample), compute 95% CI for each AUROC
- **Validation:** Both AUROCs in [0, 1]; CI width reasonable (<0.15)

### FR-5: ΔAUROC Computation and Gate Evaluation
- ΔAUROC = AUROC_clustered − AUROC_ablated
- Gate check: ΔAUROC ≥ 0.03 → PASS (SHOULD_WORK)
- Report: ΔAUROC value, 95% CI for each AUROC, gate verdict
- **Validation:** ΔAUROC computed; verdict logged

### FR-6: Secondary Metric — Within-Cluster Entropy Fraction
- Compute mean within_cluster_fraction across N=98 questions
- Gate: mean fraction > 0.0 (NLI grouping provides non-trivial entropy reduction)
- Secondary check: fraction < 10% indicates low contribution (expected if H-M2 FAILS)
- **Validation:** Mean fraction computed and logged

### FR-7: Tertiary Metric — Entailment Pair Co-clustering Rate
- On 20-question paraphrase-confirmed subset: verify NLI pairs co-clustered ≥ 90%
- Re-verifies H-M1 clustering quality on subset
- **Validation:** Rate computed; warn if < 90%

### FR-8: Mechanism Activation Verification
- Run `verify_mechanism_activated(results)`:
  - `clustering_reduces_n`: mean cluster count < 10.0
  - `entropy_saving_nonzero`: mean within_cluster_frac > 0.0
  - `auroc_delta_positive`: AUROC_clustered > AUROC_ablated
  - `delta_meets_gate`: ΔAUROC ≥ 0.03
- Log all indicators; overall gate verdict

### FR-9: Visualization
- **Required:** Bar chart — AUROC_clustered vs AUROC_ablated with 95% CI error bars
- **Additional:** Scatter plot — within-cluster fraction vs question-level AUROC contribution (20-question subset)
- **Additional:** Histogram — cluster count distribution (N=98)
- **Additional:** Box plot — SE entropy per question (clustered vs ablated)
- Save all figures to `docs/youra_research/h-m2/figures/`

### FR-10: Results Reporting
- Save structured results to `docs/youra_research/h-m2/results.json`
- Print gate verdict with all metric values
- Include mechanism activation indicators
- Format for Phase 4 validation report consumption

## 4. Data Specification

### 4.1 Primary Dataset

| Attribute | Value |
|-----------|-------|
| Name | TriviaQA dev |
| Source | mandarjoshi/trivia_qa (HuggingFace) |
| Split | validation |
| N questions | 98 (full set for AUROC); 20-question subset for within-cluster analysis |
| Download | NOT required — use existing H-E1 cache |
| Cache location | `docs/youra_research/h-e1/cache/` |

**No manual download needed** — all data pre-cached from H-E1.

### 4.2 Cached Artifacts (Reused from H-E1/H-M1)

| Artifact | Source | Location |
|----------|--------|----------|
| K=10 sample strings | H-E1 generation | `docs/youra_research/h-m1/code/` or H-E1 cache |
| Cluster IDs (all 98 questions) | H-M1 computation | `docs/youra_research/h-m1/code/` |
| Binary EM labels | H-E1 | `docs/youra_research/h-m1/code/` or H-E1 cache |
| NLI model weights | H-M1 | HuggingFace cache (~900MB) |

### 4.3 20-Question Paraphrase Subset

- Identified in H-M1: questions with ≥1 multi-member NLI cluster
- 76/98 questions eligible; 20-question structured subset for within-cluster analysis
- Load from H-M1 metadata or recompute cluster membership

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Runtime | < 10 minutes total (no LLM inference; NLI model already loaded) |
| Reproducibility | Fixed seed=42; results deterministic given cache |
| Memory | < 4GB GPU for NLI model + cache |
| Correctness | AUROC computed identically to H-E1 (sklearn roc_auc_score) |
| Isolation | Only ablation flag changes; all other parameters from H-M1 |

## 6. Evaluation Metrics

| Metric | Formula | Gate Threshold | Type |
|--------|---------|----------------|------|
| ΔAUROC | AUROC_clustered − AUROC_ablated | ≥ 0.03 | Primary |
| Mean within-cluster fraction | mean(entropy_saved / log(K)) | > 0.0; secondary check < 10% | Secondary |
| Entailment pair co-cluster rate | pairs_co-clustered / total_entailment_pairs | ≥ 90% | Tertiary |

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.30.0
sentence-transformers>=2.2.0
datasets>=2.14.0
scikit-learn>=1.3.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
tqdm>=4.65.0
```

### 7.2 External Repositories / Code

| Reference | Purpose | Location |
|-----------|---------|---------|
| h-m1 codebase | Primary code reuse (get_semantic_ids, cached artifacts) | `docs/youra_research/h-m1/code/` |
| lorenzkuhn/semantic_uncertainty | Reference SE implementation | GitHub (reference only; use h-m1 code) |

### 7.3 Hardware

- GPU: 1× NVIDIA A100 or equivalent (for NLI model cross-encoder)
- RAM: 16GB system RAM
- Storage: < 5GB (models cached; no new downloads)

## 8. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Code runs without error | All FRs execute | Must |
| ΔAUROC ≥ 0.03 | Primary gate | Must for PASS |
| Mean within-cluster fraction > 0.0 | Secondary gate | Should |
| All figures generated | 4 figures in figures/ | Must |
| Results JSON saved | Structured output | Must |
| Runtime < 10 minutes | NFR | Should |

**Gate Verdict Logic:**
- ΔAUROC ≥ 0.03 → PASS (SHOULD_WORK gate satisfied)
- ΔAUROC in [0.01, 0.03) → PARTIAL (document limitation; explore secondary metrics)
- ΔAUROC < 0.01 → FAIL (explore alternative mechanism)
