---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - data_specification
  - evaluation_metrics
  - dependencies
  - success_criteria
hypothesis_id: H-M1
hypothesis_type: MECHANISM
date: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Product Requirements Document: H-M1

**Hypothesis:** Under Llama-2-7B on TriviaQA dev, if K=10 stochastic samples are generated for high- vs. low-uncertainty questions, then token entropy varies across semantically equivalent paraphrases (same meaning, different surface form), because TE aggregates over vocabulary distributions that encode surface variation, not semantic content.

---

## 1. Executive Summary

H-M1 is a **mechanism verification experiment** that confirms whether token entropy (TE) is sensitive to surface-level paraphrase variation within NLI-confirmed semantic clusters. This is a pure analysis task over existing H-E1 pipeline outputs — no new model inference is required. The experiment identifies questions from the 98-question TriviaQA pool that have ≥1 multi-member NLI cluster (paraphrase pair), then measures within-cluster TE variance.

**Scientific purpose:** Confirm the noise-filtering rationale for Semantic Entropy (SE) over TE. If TE does NOT vary within paraphrase pairs, the SE/TE gap observed in H-E1 (AUROC gap=0.155) cannot be attributed to paraphrase noise — requiring redesign of H-M2/H-M3.

**Gate type:** MUST_WORK. Failure triggers EXPLORE, not ABANDON.

---

## 2. Problem Statement

### 2.1 Research Question

Does token entropy (TE) vary across semantically equivalent paraphrases (same NLI cluster) in the K=10 stochastic samples generated for TriviaQA dev questions under Llama-2-7B?

### 2.2 Mechanism Being Tested

TE computes Shannon entropy over per-position vocabulary distributions and averages across tokens. Two responses with identical semantic content but different surface form (e.g., "Paris" vs "the city of Paris") produce different token paths, yielding different per-position entropy profiles. This experiment isolates and measures that effect.

### 2.3 Why This Matters

- H-E1 showed SE outperforms TE (AUROC gap = 0.155 ≥ 0.05 threshold)
- The theoretical explanation: TE suffers paraphrase noise; SE's NLI clustering removes it
- H-M1 empirically confirms this noise exists before H-M2/M3 design proceeds
- avg_clusters = 7.31 from H-E1 predicts ~20–30 questions with multi-member clusters in the 98-question pool

### 2.4 Context (Previous Result)

| Metric | H-E1 Value |
|--------|------------|
| AUROC SE | 0.717 |
| AUROC TE | 0.562 |
| Gap | 0.155 |
| N questions | 98 |
| K samples | 10 |
| avg_clusters | 7.31 |

---

## 3. Functional Requirements

### FR-1: H-E1 Output Loading

The system MUST load persisted H-E1 pipeline outputs:
- K=10 sample texts per question (98 questions)
- Per-sample mean token entropy values (scalar per sample)
- NLI cluster assignments (dict: sample_idx → cluster_id, per question)
- Binary EM correctness labels

**Fallback (FR-1b):** If logprob outputs not cached, re-run H-E1 generation with `logprob_save=True` flag using Llama-2-7B. If cluster assignments not cached, re-run NLI clustering with DeBERTa-large-mnli.

### FR-2: Paraphrase Pair Identification

The system MUST identify questions from the 98-question pool where ≥1 NLI cluster contains ≥2 samples (paraphrase pairs confirmed by bidirectional entailment).

**Output:** List of eligible question IDs (expected: 20–30 from 98)

**Assertion:** `len(eligible) >= 20` — failure triggers check on NLI model loading.

### FR-3: Intra-Cluster TE Variance Computation

For each eligible question, the system MUST compute:
- Group samples by NLI cluster ID
- For each cluster with ≥2 members: compute `np.var(member_token_entropies)`
- Per-question: `mean_intra_cluster_variance = mean(cluster_variances)` where `len(members) >= 2`

```python
def compute_intra_cluster_variance(cluster_assignments, token_entropies):
    clusters = defaultdict(list)
    for idx, cid in cluster_assignments.items():
        clusters[cid].append(token_entropies[idx])
    variances = [np.var(m) for m in clusters.values() if len(m) >= 2]
    return np.mean(variances) if variances else None
```

### FR-4: Primary Gate Verification

The system MUST implement and call `verify_mechanism_activated(results)`:
- Count eligible questions with `mean_intra_cluster_variance > 0.1 nats`
- Assert ≥15/20 eligible questions pass
- Return `(primary_pass: bool, indicators: dict)`

### FR-5: Inter-Cluster TE Variance (Control)

The system MUST compute inter-cluster TE variance as a control:
- For each question: compute variance across cluster means (between-cluster)
- Expected: inter-cluster variance > intra-cluster variance for correct-vs-incorrect questions

### FR-6: Stratified Analysis

The system MUST compare intra-cluster TE variance between:
- High-uncertainty questions (SE > median SE across 98 questions)
- Low-uncertainty questions (SE ≤ median SE)

### FR-7: Visualization

The system MUST generate all figures to `docs/youra_research/h-m1/figures/`:

| Figure | Type | Required |
|--------|------|----------|
| Gate metrics bar chart | Mean intra-cluster variance vs 0.1 nats threshold | MANDATORY |
| Violin plot | Distribution of per-question intra-cluster variance | Recommended |
| Scatter plot | Cluster size vs TE variance | Recommended |
| NLI heatmap | Pairwise entailment for 3 representative questions | Recommended |
| Threshold sensitivity bar | Fraction passing at {0.05, 0.1, 0.2, 0.5} nats thresholds | Recommended |

### FR-8: Results Persistence

The system MUST save results to `docs/youra_research/h-m1/results/`:
- `h_m1_results.json` — per-question analysis results
- `h_m1_summary.json` — gate metrics, indicators, pass/fail verdict
- `experiment.log` — run log with mechanism activation check output

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | TriviaQA dev (H-E1 pool) |
| Source | mandarjoshi/trivia_qa, rc.nocontext |
| Split | validation (dev) |
| N | 98 questions (same random sample as H-E1/h-e2-v2) |
| Synthetic | NO |
| Download | HuggingFace: `load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation")` |
| Cache | Reuse H-E1 cached outputs — no re-download required |

**CRITICAL: No new data download needed.** H-M1 is a pure analysis task on H-E1 outputs.

### 4.2 H-E1 Pipeline Outputs (Primary Data Source)

| Output | Format | Path (Expected) |
|--------|--------|-----------------|
| Sample texts | list[list[str]] | h-e1 results cache |
| Per-sample token entropy | list[list[float]] | h-e1 results cache |
| NLI cluster assignments | dict[question_id, dict[int, int]] | h-e1 results cache |
| EM correctness labels | list[bool] | h-e1 results cache |

**Fallback data source:** Re-run H-E1 generation script with `logprob_save=True`.

### 4.3 Subset for H-M1

From 98 questions: filter to those with ≥1 multi-member NLI cluster.
- Expected yield: 20–30 questions
- Minimum required: 20 (assert; see FR-4)

---

## 5. Evaluation Metrics

### 5.1 Primary Metric

| Metric | Formula | Threshold | Evaluation |
|--------|---------|-----------|------------|
| Mean intra-cluster TE variance | `mean(np.var(cluster_members))` per question | > 0.1 nats | Primary gate |
| Fraction passing | `n_passing / n_eligible` | ≥ 15/20 = 75% | Pass criterion |

### 5.2 Secondary Metrics

| Metric | Formula | Threshold |
|--------|---------|-----------|
| NLI clustering accuracy | Fraction of entailment pairs → same cluster | ≥ 90% |
| Inter-cluster variance | `np.var([cluster_means])` per question | Expected > intra-cluster |
| Mean intra-cluster variance overall | Across all eligible questions | Expected 0.2–0.5 nats |

### 5.3 Diagnostics

| Diagnostic | Purpose |
|-----------|---------|
| n_eligible_questions | Confirm ≥20 questions have paraphrase pairs |
| Variance by uncertainty stratum | High-SE vs low-SE question variance comparison |
| Threshold sensitivity table | Robustness of result to threshold choice |

---

## 6. Non-Functional Requirements

### 6.1 Performance

- Total runtime: < 5 minutes on CPU (no GPU required if H-E1 cache hit)
- NLI re-clustering fallback: ~10 minutes on single GPU
- Memory: < 4GB RAM

### 6.2 Reproducibility

- Single seed analysis (deterministic; K=10 samples already fixed from H-E1)
- All intermediate results saved to `h-m1/results/`
- Analysis script self-contained with fixed random seed for any shuffles

### 6.3 Code Quality

- Pure Python + NumPy + scipy.stats (no DL frameworks for analysis)
- Follows lorenzkuhn/semantic_uncertainty code patterns
- All intermediate computations logged to `experiment.log`

---

## 7. Dependencies

### 7.1 Python Packages

```
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
seaborn>=0.12
datasets>=2.14  # HuggingFace datasets (for re-loading TriviaQA if needed)
transformers>=4.31  # Only if NLI re-clustering needed
torch>=2.0  # Only if NLI re-clustering needed
```

### 7.2 External Repositories (Reference)

| Repository | URL | Purpose |
|-----------|-----|---------|
| lorenzkuhn/semantic_uncertainty | https://github.com/lorenzkuhn/semantic_uncertainty | TE computation patterns, NLI clustering protocol |
| rdgbrandon/semanticentropy | https://github.com/rdgbrandon/semanticentropy | Cluster visualization reference |

### 7.3 H-E1 Pipeline (Critical Dependency)

The H-E1 pipeline code in `docs/youra_research/h-e1/code/` must have saved:
- Sample generations with per-sample token logprobs
- NLI cluster assignments (bidirectional DeBERTa-large-mnli)

Phase 4 MUST check cache existence before proceeding.

---

## 8. Success Criteria

### 8.1 PoC Pass

| Criterion | Threshold |
|-----------|-----------|
| Code runs without error | Required |
| mean_intra_cluster_variance > 0.1 nats | ≥ 15/20 eligible questions |
| NLI clustering assigns entailment pairs to same cluster | ≥ 90% |

### 8.2 Gate Outcome

| Result | Next Action |
|--------|-------------|
| PASS (≥15/20) | H-M2, H-M3 proceed with mechanism confirmed |
| FAIL (<10/20) | EXPLORE: Try BERTScore similarity instead of NLI entailment |
| PARTIAL (10–14/20) | Document limitations, proceed with caution |

### 8.3 Expected Values

| Metric | Expected Range |
|--------|---------------|
| Mean intra-cluster TE variance | 0.2–0.5 nats |
| Inter-cluster TE variance (control) | 0.5–1.5 nats |
| n_eligible questions | 20–30 of 98 |
| n_passing primary threshold | ≥ 15 |
