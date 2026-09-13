# Product Requirements Document: H-M2
## NLI Clustering Aggregation Behavior Analysis

**Hypothesis:** H-M2 (MECHANISM — Causal Step 2)
**Type:** INCREMENTAL (builds on H-M1)
**Date:** 2026-05-11
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Tier:** FULL (30 task max)

---

## 1. Executive Summary

H-M2 tests whether deberta-large-mnli NLI clustering produces meaningful semantic aggregation on HaluEval-QA stochastic samples. Specifically: does the cluster count distribution show fewer clusters than samples (cluster_count < 5) for at least 50% of examples? This is a **pure analysis experiment** — zero new LLM inference or NLI computation is required. All cluster count data was already computed in H-E1 via `lorenzkuhn/semantic_uncertainty`. The SHOULD_WORK gate passes if aggregation_rate ≥ 0.50 with bootstrap 95% CI lower bound ≥ 0.30. Critical context from H-M1: mean_clusters=4.644 (out of 5), suggesting low aggregation — a likely PIVOT condition.

---

## 2. Problem Statement

**Research Question:** Does deberta-large-mnli NLI clustering produce meaningful semantic aggregation (cluster_count < N=5) for a majority of HaluEval-QA examples with N=5 stochastic LLaMA-2-7B-chat samples?

**Motivation:** Semantic entropy relies on NLI clustering reducing N responses to fewer semantic clusters. If most examples retain 5 distinct clusters (no aggregation), the clustering mechanism fails to filter surface-form noise — violating the core assumption of semantic entropy. H-M1 found mean_clusters=4.644, which implies the aggregation rate may be well below 50%. H-M2 quantifies this distribution and determines whether it constitutes a mechanism failure or an acceptable degenerate case.

**Success Condition:** aggregation_rate ≥ 0.50 (fraction of examples with cluster_count < 5), with bootstrap 95% CI lower bound ≥ 0.30 (SHOULD_WORK gate — failure triggers PIVOT, not stop).

---

## 3. Functional Requirements

### FR-1: Load H-E1 Cluster Count Data
- **Primary source:** `../h-e1/code/outputs/uq_scores/semantic_entropy.json` — check if cluster counts are stored alongside entropy
- **Fallback source:** `../h-m1/code/outputs/experiment_results.json` — H-M1 computed cluster distribution (mean_clusters=4.644, std=0.657, N_singleton=4)
- **Secondary fallback:** Re-run `get_semantic_ids()` from `lorenzkuhn/semantic_uncertainty` on H-E1 stochastic samples (`../h-e1/code/outputs/stochastic_samples.jsonl`)
- **Action:** Load cluster_counts as numpy array shape `(2000,)` with integer values in [1, 5]
- **Validation:** Assert `len(cluster_counts) == 2000` and `all(1 <= c <= 5 for c in cluster_counts)`

### FR-2: Compute Aggregation Rate (Primary Gate Metric)
- **Metric:** `aggregation_rate = np.mean(cluster_counts < N)` where N=5
- **Bootstrap:** N_resample=1,000 resamples, seed=42, with-replacement
- **CI:** 95% CI via percentile method [2.5, 97.5] on bootstrapped aggregation rates
- **Gate check:** `aggregation_rate >= 0.50` AND `ci_lower >= 0.30` → PASS
- **Report:** aggregation_rate, ci_lower, ci_upper, gate_pass (bool)

### FR-3: Compute Full Collapse Rate (Secondary Metric)
- **Metric:** `collapse_rate = np.mean(cluster_counts == 1)` (all samples semantically identical)
- **Success:** collapse_rate < 0.20
- **Report:** collapse_rate (fraction, 0–1)

### FR-4: Cluster Count Distribution Statistics
- **Metrics:**
  - `mean_cluster_count`: np.mean(cluster_counts)
  - `std_cluster_count`: np.std(cluster_counts)
  - `histogram`: frequency of each count value 1, 2, 3, 4, 5
  - `median_cluster_count`: np.median(cluster_counts)
- **Report:** Full distribution table

### FR-5: Point-Biserial Correlation with Hallucination Labels
- **Metric:** `r_pb, p_value = scipy.stats.pointbiserialr(labels, cluster_counts)`
- **Labels source:** `../h-e1/code/data/halueval_qa_2k.json` (field: `hallucination`, int 0/1)
- **Success:** `|r_pb| >= 0.10` (meaningful association between cluster count and hallucination)
- **Direction hypothesis:** lower cluster_count → more agreement → factual (label=0) → expected r_pb > 0
- **Report:** r_pb, p_value (two-tailed)

### FR-6: Stratified Analysis by Question Type (Optional if available)
- **If HaluEval-QA examples have question_type field:** Compute aggregation_rate per type
- **Report:** aggregation_rate by type if available, else skip

### FR-7: Gate Evaluation and Results Serialization
- **Gate:** SHOULD_WORK — aggregation_rate ≥ 0.50 AND ci_lower ≥ 0.30
- **PIVOT condition:** aggregation_rate < 0.50 → document as A2 violation (deberta-large-mnli does not generalize to HaluEval-QA response style)
- **Output:** `experiment_results.json` with all metrics + gate_result (PASS/PARTIAL/PIVOT)
- **Output:** `04_validation.md` report

### FR-8: Visualization
- **Required (mandatory):** Aggregation rate bar chart vs. 50% threshold with bootstrap CI error bar. Saved to `h-m2/figures/aggregation_rate.png`
- **Additional (LLM autonomous):**
  - Cluster count distribution histogram (1–5) → `h-m2/figures/cluster_count_dist.png`
  - Cluster count by hallucination label (box plot) → `h-m2/figures/cluster_count_by_label.png`
  - Cumulative distribution (CDF) of cluster counts with N-1=4 threshold line → `h-m2/figures/cluster_count_cdf.png`
  - Stratified aggregation rate by question type (if available) → `h-m2/figures/aggregation_by_type.png`
- **Output dir:** `h-m2/figures/` (create if not exists)

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

### 4.2 Pre-computed Inputs (Reused from H-E1 / H-M1)
| File | Shape | Description |
|------|-------|-------------|
| `../h-e1/code/outputs/stochastic_samples.jsonl` | 2000 lines | 5 stochastic samples per example (fallback for re-clustering) |
| `../h-e1/code/data/halueval_qa_2k.json` | 2000 dicts | Dataset with hallucination labels |
| `../h-m1/code/outputs/experiment_results.json` | dict | H-M1 cluster distribution summary (mean=4.644, std=0.657) |

**Primary cluster count source (priority order):**
1. Load from H-E1 NLI outputs if cluster_counts stored per-example
2. Re-run NLI clustering on H-E1 stochastic samples using `lorenzkuhn/semantic_uncertainty` `get_semantic_ids()`

### 4.3 No Synthetic Data
Policy: ✅ COMPLIANT — real benchmark dataset only.

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- All randomness seeded: `seed=42` for bootstrap resampling
- No new LLM inference (zero stochasticity from generation)
- NLI re-run (if needed) uses deterministic deberta-large-mnli with fixed inputs

### NFR-2: Compute Budget
- **GPU:** NOT REQUIRED for analysis path (CPU only)
- **GPU required only if:** NLI re-clustering needed (fallback path)
- **Estimated runtime:**
  - Analysis-only path: < 2 minutes (CPU)
  - NLI re-clustering fallback: ~30 minutes (GPU) for 2000 × C(5,2)=10 NLI pairs

### NFR-3: Error Handling
- Missing H-E1 cluster data → Fallback to re-clustering (FR-1 priority order)
- Missing stochastic_samples.jsonl → `FileNotFoundError` with clear message
- Cluster counts outside [1,5] → Clamp and warn
- Empty cluster counts array → Exit with descriptive error

### NFR-4: Code Structure
- Single experiment script: `h-m2/code/run_experiment.py`
- Reuse H-E1 utility functions where applicable (data.py via sys.path)
- Reuse H-M1 cluster analysis utilities where applicable

### NFR-5: Statistical Rigor
- Bootstrap CI uses percentile method (N=1,000 resamples)
- Two-tailed p-values for all significance tests
- Report exact values in experiment_results.json

---

## 6. Evaluation Metrics

### Primary (Gate — SHOULD_WORK)
| Metric | Computation | Gate Threshold |
|--------|-------------|----------------|
| Aggregation Rate | `np.mean(cluster_counts < 5)` | ≥ 0.50 |
| Bootstrap 95% CI lower | Percentile [2.5] of 1000 bootstrap rates | ≥ 0.30 → confirmed PASS |

### Secondary (Informative)
| Metric | Computation | Expected |
|--------|-------------|----------|
| Collapse Rate | `np.mean(cluster_counts == 1)` | < 0.20 |
| Mean Cluster Count | `np.mean(cluster_counts)` | 2–4 (meaningful clustering) |
| Point-Biserial r | `scipy.stats.pointbiserialr(labels, counts)` | \|r\| ≥ 0.10 |

### PIVOT Condition
| Condition | Value | Interpretation |
|-----------|-------|----------------|
| PASS | aggregation_rate ≥ 0.50 | NLI clustering works on HaluEval-QA |
| PARTIAL | 0.30 ≤ aggregation_rate < 0.50 | Weak aggregation — document and continue |
| PIVOT | aggregation_rate < 0.30 | A2 violation — clustering mechanism fails |

---

## 7. Dependencies

### 7.1 Python Packages
```
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
seaborn>=0.12
tqdm>=4.65
transformers>=4.30    # Only if NLI re-clustering needed (fallback)
torch>=2.0            # Only if NLI re-clustering needed (fallback)
```

### 7.2 Internal Dependencies (H-E1 / H-M1 Reuse)
- `../h-e1/code/data.py` — `load_dataset_from_disk()`, `load_halueval_qa()`
- `../h-e1/code/uq_signals.py` — `get_semantic_ids()` (NLI clustering, fallback only)
- H-E1 data files (see 4.2)
- H-M1 cluster distribution summary (`experiment_results.json`)

### 7.3 External References
- lorenzkuhn/semantic_uncertainty — Official NLI clustering implementation (Kuhn et al. 2023)
- `microsoft/deberta-large-mnli` — NLI model (HuggingFace, already cached from H-E1)

---

## 8. Success Criteria

### Primary (SHOULD_WORK Gate)
- [ ] Cluster counts loaded (from H-E1 outputs or re-computed)
- [ ] aggregation_rate computed with bootstrap 95% CI
- [ ] experiment_results.json written with all metrics
- [ ] 04_validation.md report written with gate decision (PASS/PARTIAL/PIVOT)

### Secondary
- [ ] collapse_rate computed and reported
- [ ] Point-biserial correlation with hallucination labels computed
- [ ] Full cluster count distribution (histogram 1–5) reported
- [ ] All figures generated in h-m2/figures/

### Infrastructure
- [ ] Code runs end-to-end without crash
- [ ] All H-E1/H-M1 input files loaded successfully
- [ ] Runtime < 2 minutes (analysis path) or documented if fallback needed

---

## 9. Out of Scope

- New LLM inference (no forward passes on LLaMA-2 or Mistral)
- Model fine-tuning or training
- New dataset download (all data reused from H-E1)
- Multi-model comparison (H-M3 scope)
- Alternative NLI model testing (H-M3 scope if PIVOT triggered)
- SelfCheckGPT analysis (H-E1 scope)

---

## 10. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cluster counts not cached per-example in H-E1 | HIGH | Medium | Fallback: re-run NLI clustering on stochastic_samples.jsonl |
| aggregation_rate < 0.50 (PIVOT condition) | HIGH (H-M1 mean=4.644) | Medium | SHOULD_WORK gate: document as PIVOT, continue pipeline |
| H-E1 stochastic_samples.jsonl missing | Low | High | FileNotFoundError + clear remediation message |
| NLI re-clustering produces different cluster counts than H-E1 | Low | Low | Use same seed and model config as H-E1 |

---

*Generated by Phase 3 PRD Workflow (inline execution — TEST no-MCP environment)*
*Input: h-m2/02c_experiment_brief.md | Phase 2C COMPLETED 2026-05-11*
*Next: 03_architecture.md (Architecture Agent)*
