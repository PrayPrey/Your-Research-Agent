# Product Requirements Document: H-M1
# Deduplication N-gram Contamination — Mechanism Verification

**Hypothesis:** H-M1 (MECHANISM / MUST_WORK)
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Phase 2C Source:** docs/youra_research/h-m1/02c_experiment_brief.md
**Tier:** FULL (≤30 tasks)
**Base Hypothesis:** H-E1 (VALIDATED — PASS)

---

## 1. Executive Summary

H-M1 tests the first causal link in the contamination-correction chain: whether documents removed by exact substring deduplication show measurably higher 13-gram overlap with standard benchmark test sets than retained documents. This is a corpus analysis experiment (no neural training) that uses the Pile/dedup-Pile document populations to verify that deduplication selectively removes benchmark-adjacent content.

Success (p < 0.0125 for ≥2 benchmarks via Mann-Whitney U) supports contamination-correction as the mechanism behind the h-e1 performance signature. Failure pivots to a data-quality alternative explanation.

---

## 2. Problem Statement

**Research Question:** Do documents removed by exact substring deduplication show significantly higher 13-gram overlap with MMLU, HellaSwag, ARC-Challenge, and WinoGrande test sets than retained documents?

**Null Hypothesis (H0):** Removed and retained documents have equal 13-gram overlap distributions with benchmark test sets (no benchmark achieves p < 0.0125).

**Alternative Hypothesis (H1):** Removed documents show significantly higher 13-gram overlap (Mann-Whitney U, one-tailed, p < 0.0125 Bonferroni-corrected) for ≥2 benchmarks.

**Failure Consequence:** If H0 is supported → PIVOT: deduplication improves performance via data-quality (not contamination-correction); downstream h-m2 through h-m4 require re-scoping.

---

## 3. Goals and Non-Goals

### Goals
- Identify removed document population (Pile minus dedup-Pile) via streaming corpus diff
- Sample ~10,000 removed and ~10,000 retained documents (size-distribution-matched across Pile subsets)
- Extract 13-gram sets from full test sets of all 4 benchmarks via lm-evaluation-harness
- Compute per-document 13-gram overlap rate for all 20,000 documents × 4 benchmarks
- Apply Mann-Whitney U (one-tailed) with Bonferroni correction per benchmark
- Produce mandatory figure (bar chart) + additional figures (violin plots, rank correlation, subset breakdown)
- Run ablation variants (8-gram, unigram, ARC-Easy, subset-stratified)
- Generate validation report confirming/refuting H1

### Non-Goals
- Training or evaluating any neural model
- Modifying lm-evaluation-harness internals
- Analyzing intermediate Pile checkpoints
- Estimating min-k% probability (H-M2 scope)

---

## 4. Functional Requirements

### FR-1: Corpus Streaming and Document Identification
- Stream both Pile (`EleutherAI/pile`) and dedup-Pile (`EleutherAI/the_pile_deduplicated`) via HuggingFace Datasets
- Identify removed documents: documents in Pile but NOT in dedup-Pile (matched by SHA-256 hash of text)
- Track Pile subset label for each document (for size-distribution matching and subset ablation)
- Output: streaming iterator over (doc_text, doc_id, pile_subset, is_removed) tuples

### FR-2: Stratified Document Sampling
- Draw ~10,000 removed documents: reservoir sample from Pile-only stream, stratified by Pile subset proportions
- Draw ~10,000 retained documents: reservoir sample from dedup-Pile stream, matching removed-population Pile subset distribution
- Random seed: 42 (deterministic)
- Minimum per-subset sample: ≥50 documents if subset present in removed population
- Output: `sampled_removed.jsonl` and `sampled_retained.jsonl` (text + metadata)

### FR-3: Benchmark N-gram Extraction
- Load full test sets for MMLU (14,042 items), HellaSwag (10,042), ARC-Challenge (1,172), WinoGrande (1,267)
- Use lm-evaluation-harness `doc_to_text()` for each benchmark to extract text
- Construct 13-gram character sets from all test item texts per benchmark
- Output: `benchmark_ngrams_13.pkl` (dict: benchmark → frozenset of 13-gram strings)

### FR-4: Per-Document N-gram Overlap Computation
- For each of 20,000 documents, compute 13-gram character overlap rate per benchmark
- overlap_rate = |doc_ngrams ∩ benchmark_ngrams| / |doc_ngrams| (0 if doc has 0 ngrams)
- Parallelized via `multiprocessing.Pool` (CPU-bound, no GPU needed)
- Output: `overlap_scores.npz` (arrays: removed_overlaps[N_removed × 4], retained_overlaps[N_retained × 4])

### FR-5: Statistical Testing
- Mann-Whitney U test (one-tailed, alternative='greater') per benchmark: removed > retained
- Bonferroni correction: α_corrected = 0.05 / 4 = 0.0125
- Compute rank-biserial r = 1 - 2U/(n1×n2) as effect size
- Spearman correlation: mean overlap differences vs expected contamination ranking [MMLU, ARC-Challenge, HellaSwag, WinoGrande]
- Output: `statistical_results_hm1.json` with per-benchmark {U, p_value, r, significant, mean_removed, mean_retained, ratio}

### FR-6: Mechanism Verification Check (Sanity)
- Assert: mean removed overlap > mean retained overlap for MMLU (ratio ≥ 1.2× expected)
- Assert: removed MMLU mean > random web baseline (sampled 100-doc check)
- Raise RuntimeError with message if sanity check fails: "Mechanism check fail: removed/retained ratio = {X:.2f}×"
- Log per-benchmark: "Removed docs: mean overlap = {X:.4f}; Retained docs: mean overlap = {Y:.4f}; Ratio = {X/Y:.1f}×"

### FR-7: Ablation Variants
- **8-gram:** Repeat FR-4 with n=8; compare ranking consistency with 13-gram results
- **Unigram:** Repeat FR-4 with n=1 (word tokens, space-split); validate word-level contamination direction
- **ARC-Easy:** Extend FR-3 and FR-4 to include ARC-Easy test set; compare with ARC-Challenge
- **Subset-stratified:** Within each Pile subset (Pile-CC, Books3, Wikipedia, etc.), compare removed vs retained overlap; verify effect holds within subsets

### FR-8: Visualization
- **Mandatory (gate metrics):** Bar chart — mean 13-gram overlap rate (removed vs retained) per benchmark; 95% CI error bars; significance markers (*** p<0.001, ** p<0.01, * p<0.05, ns); saved as `figures/fig_overlap_comparison.png`
- **Violin plots:** Per-benchmark overlap distributions for removed vs retained; shows skewness; saved as `figures/fig_overlap_distributions.png`
- **Rank correlation plot:** Scatter of (expected contamination rank, observed mean overlap difference) for 4 benchmarks; saved as `figures/fig_rank_correlation.png`
- **Subset breakdown:** Mean 13-gram overlap by Pile subset for removed docs; saved as `figures/fig_subset_breakdown.png`

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Total wall-clock time: ≤8 hours on 8-core CPU, 16GB RAM
- Overlap computation: parallelized with ≥4 workers
- Corpus streaming: must handle ~825GB Pile without full download (HuggingFace streaming)

### NFR-2: Reproducibility
- All random operations seeded at 42
- Results must be exactly reproducible across runs given same corpus versions
- All intermediate outputs saved (sampled docs, ngram sets, overlap arrays)

### NFR-3: Memory
- Peak RAM ≤ 16GB (benchmark ngram sets fit in memory; docs processed in batches)
- 13-gram sets for 26,523 benchmark items: estimated ~500MB–2GB depending on text length

### NFR-4: Correctness
- Character-level 13-grams (not word n-grams) per GPT-4 TR standard
- One-tailed Mann-Whitney U (not two-tailed) — directional hypothesis
- Bonferroni correction applied BEFORE declaring any single benchmark significant

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Primary: ≥2 benchmarks significant | p < 0.0125 (Mann-Whitney U, one-tailed) | `statistical_results_hm1.json` |
| Effect direction | removed_mean > retained_mean for all significant benchmarks | ratio field |
| Ranking consistency | MMLU overlap > WinoGrande overlap for removed docs | Spearman correlation sign |
| Sanity check | removed/retained MMLU ratio ≥ 1.2× | mechanism check log |
| Ablations complete | All 4 ablations run and reported | ablation section of report |

---

## 7. Data Specification

### 7.1 Primary Corpora
| Dataset | HuggingFace ID | Size | Access Method |
|---------|---------------|------|---------------|
| The Pile | `EleutherAI/pile` | ~825GB / ~299B tokens | Streaming (train split) |
| The Pile Deduplicated | `EleutherAI/the_pile_deduplicated` | ~207B tokens | Streaming (train split) |

### 7.2 Benchmark Test Sets
| Benchmark | Source | Test Items | Load Method |
|-----------|--------|-----------|-------------|
| MMLU | lm-evaluation-harness | 14,042 | `get_task_dict(["mmlu"])` |
| HellaSwag | lm-evaluation-harness | 10,042 | `get_task_dict(["hellaswag"])` |
| ARC-Challenge | lm-evaluation-harness | 1,172 | `get_task_dict(["arc_challenge"])` |
| WinoGrande | lm-evaluation-harness | 1,267 | `get_task_dict(["winogrande"])` |
| ARC-Easy (ablation) | lm-evaluation-harness | ~2,376 | `get_task_dict(["arc_easy"])` |

### 7.3 Outputs
| File | Location | Format | Contents |
|------|----------|--------|----------|
| sampled_removed.jsonl | h-m1/ | JSONL | 10,000 removed doc texts + metadata |
| sampled_retained.jsonl | h-m1/ | JSONL | 10,000 retained doc texts + metadata |
| benchmark_ngrams_13.pkl | h-m1/ | Pickle | 13-gram frozensets per benchmark |
| overlap_scores.npz | h-m1/ | NumPy archive | overlap arrays [N×4] |
| statistical_results_hm1.json | h-m1/ | JSON | per-benchmark stats |
| figures/ | h-m1/figures/ | PNG | all 4 figures |

---

## 8. Dependencies

### 8.1 Python Packages
```
datasets>=2.14.0          # HuggingFace streaming
lm-eval>=0.4.0             # Benchmark test set extraction
scipy>=1.10.0              # Mann-Whitney U, Spearman correlation
numpy>=1.24.0              # Array operations
matplotlib>=3.7.0          # Figures
seaborn>=0.12.0            # Violin plots
tqdm>=4.65.0               # Progress bars
```

### 8.2 External Repositories
- `EleutherAI/lm-evaluation-harness` — benchmark test set text extraction via `doc_to_text()`
- `EleutherAI/pythia` — HuggingFace dataset identifiers for Pile/dedup-Pile
- `google-research/deduplicate-text-datasets` — reference for document identification methodology

### 8.3 Hardware
- CPU: ≥8 cores (for multiprocessing.Pool)
- RAM: ≥16GB
- Storage: ~10GB for intermediate outputs (sampled docs, ngram sets, overlap arrays)
- GPU: Not required

### 8.4 Base Hypothesis Dependencies (H-E1)
- Same benchmark set (MMLU, HellaSwag, ARC-Challenge, WinoGrande) enables controlled experiment
- lm-evaluation-harness already validated in h-e1; same version required
- No code reuse from h-e1 (different experiment type: corpus analysis vs model evaluation)

---

## 9. Validation Report Requirements

`04_validation.md` must include:
- Per-benchmark results table: {benchmark, mean_removed, mean_retained, ratio, U, p_value, r, significant}
- Gate decision: PASS (≥2 significant) or FAIL (< 2 significant) with pivot recommendation
- Ablation summary table: {variant, MMLU_significant, HellaSwag_significant, ARC_significant, WinoGrande_significant}
- Failure analysis (if FAIL): ratio values, likely mechanism alternatives
- Figures: all 4 figure paths confirmed

---

*stepsCompleted: PRD*
