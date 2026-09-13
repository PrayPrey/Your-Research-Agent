# PRD: H-M2 — Domain-Stratified Contamination Analysis

**Version:** 1.0
**Date:** 2026-05-04
**Hypothesis:** H-M2
**Type:** MECHANISM
**Gate:** SHOULD_WORK (fail does not block H-M3)

---

## 1. Executive Summary

H-M2 is a pure statistical re-analysis of the 59×3 contamination matrix produced by H-M1. The goal is to determine whether contamination rates follow domain-predictable patterns: MMLU academic/professional sub-tasks showing higher contamination in academically-weighted corpora (The Pile), and commonsense sub-tasks (HellaSwag, BIG-Bench Hard) showing higher contamination in web-heavy corpora (C4). No new data collection is required. The entire experiment runs in under 60 seconds on CPU.

**PASS condition:** Directional pattern holds for ≥2 of 3 corpora (Mann-Whitney U p < 0.05 for expected direction per corpus).

---

## 2. Problem Statement

H-E1 confirmed significant sub-task variance in contamination rates (KW H=590.82, p=2.73e-89). H-M1 confirmed significant cross-corpus variance (KW H=17.51, p=1.58e-4). H-M2 asks: *is that variance structured by domain type?* Specifically, does corpus source composition (The Pile's academic sources vs. C4's web text) predict which benchmark domains are more contaminated in each corpus?

This is a mechanistic question about *why* contamination rates differ across corpora — the answer directly supports the "contamination atlas" narrative in the final paper.

---

## 3. Scope

**In scope:**
- Domain classification of all 59 sub-tasks (academic vs. commonsense)
- Per-(corpus, domain) mean contamination rate computation
- Directional statistical tests (Mann-Whitney U, one-tailed)
- Overall interaction test (Kruskal-Wallis on 6 groups)
- Top-5 contaminated sub-tasks per corpus with domain annotation
- Figure generation (heatmap, box plots, bar charts)

**Out of scope:**
- New corpus streaming or n-gram computation
- MinHash index construction
- Any ML model training
- Modifications to the H-M1 matrix

---

## 4. Data Specification

### 4.1 Primary Dataset (REUSED — no download)

| Field | Value |
|-------|-------|
| Source | `h-m1/experiment_results.json` |
| Format | JSON: `{subtask_name: {corpus_key: contamination_rate}}` |
| Content | 59 benchmark sub-tasks × 3 corpora = 177 cells |
| Sub-tasks | 57 MMLU sub-tasks + HellaSwag + BIG-Bench Hard |
| Corpora keys | `pile`, `c4`, `redpajama` |
| Load method | `import json; matrix = json.load(open("h-m1/experiment_results.json"))` |
| Verified | Yes — H-M1 VALIDATED (gate.satisfied = true) |

### 4.2 Domain Classification

| Domain Type | Sub-tasks | Count |
|-------------|-----------|-------|
| `academic` | All 57 MMLU sub-tasks (professional, STEM, humanities, social sciences, other) | ~48 |
| `commonsense` | HellaSwag (1) + BIG-Bench Hard abstract reasoning tasks (~10) | ~11 |

**Classification logic:**
- Sub-tasks starting with `bbh_` or named `hellaswag` → `commonsense`
- All MMLU sub-tasks → `academic`

### 4.3 No Additional Downloads Required

H-M2 requires zero new data. All inputs are local.

---

## 5. Functional Requirements

### FR-1: Data Loading
Load `h-m1/experiment_results.json` and validate schema (59 sub-tasks, 3 corpus keys each). Provide fallback: if JSON malformed, raise explicit error with instructions to re-run H-M1.

### FR-2: Domain Classification
Classify all 59 sub-tasks into `academic` or `commonsense` using deterministic rule-based logic. Output: `domain_map: dict[str, str]`.

### FR-3: Per-(Corpus, Domain) Statistics
Compute mean and std of contamination rates for each of the 6 (corpus, domain) cells. Output: 2×3 table of means.

### FR-4: Directional Mann-Whitney U Tests
For each corpus, run one-tailed Mann-Whitney U tests:
- The Pile: academic_rates > commonsense_rates (H-M2 prediction)
- C4: commonsense_rates > academic_rates (H-M2 prediction)
- RedPajama: academic_rates > commonsense_rates (exploratory, no strong directional prior)

Record: U statistic, p-value, direction_confirmed (bool, p < 0.05).

### FR-5: Overall Interaction Test
Run Kruskal-Wallis across all 6 (corpus, domain) groups to test overall interaction. Report H statistic and p-value.

### FR-6: Top-5 Per Corpus
For each of the 3 corpora, identify top-5 contaminated sub-tasks with domain annotation. Output: list of (subtask, rate, domain) triples.

### FR-7: Gate Evaluation
Evaluate SHOULD_WORK gate: `directional_patterns_confirmed >= 2` (count of corpora where expected direction is confirmed at p < 0.05). Record result (PASS / PARTIAL / FAIL) and save to `experiment_results.json`.

### FR-8: Figure Generation
Generate required figures and save to `h-m2/figures/`:
- `domain_corpus_heatmap.png` — 2×3 mean contamination heatmap
- `domain_boxplots.png` — box plots by domain per corpus (3 panels)
- `top5_per_corpus.png` — top-5 bar charts with domain color coding
- `directional_test_summary.png` — p-value table visualization

### FR-9: Results Persistence
Save all results to `h-m2/experiment_results.json` with schema matching H-E1/H-M1 output format for pipeline consistency.

---

## 6. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Runtime | < 60 seconds (CPU-only, pure re-analysis) |
| Reproducibility | Fixed seed (seed=1), deterministic JSON parsing |
| Dependencies | scipy≥1.9.0, pandas≥1.5.0, numpy≥1.23.0, matplotlib≥3.5.0 |
| Python version | 3.9+ |
| GPU | Not required |
| Code style | PEP 8, type hints on all public functions |
| Error handling | Explicit errors for missing/malformed H-M1 matrix |

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.9.0
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

All are standard scientific Python packages, already installed in H-M1 environment.

### 7.2 Internal Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| H-M1 matrix | `h-m1/experiment_results.json` | VALIDATED |
| Sub-task taxonomy | H-E1 (57 MMLU + HellaSwag + BBH) | VALIDATED |
| Corpus key schema | H-M1 (pile, c4, redpajama) | VALIDATED |

### 7.3 No External Repository Downloads

H-M2 uses only local files and standard Python libraries. No HuggingFace dataset streaming, no model downloads.

---

## 8. Success Criteria

| Criterion | Definition | Pass Threshold |
|-----------|-----------|----------------|
| PASS | ≥2 directional patterns confirmed (p < 0.05) | ≥2 of 3 corpora |
| PARTIAL | 1 directional pattern confirmed | Exactly 1 corpus |
| FAIL | 0 directional patterns confirmed | 0 corpora |

**Gate:** SHOULD_WORK — FAIL does not block H-M3. Documents null result in paper.

---

## 9. Evaluation Metrics

### Primary
- `directional_patterns_confirmed`: count of corpora with expected direction at p < 0.05
- `pile_academic_gt_commonsense_p`: p-value for Pile directional test
- `c4_commonsense_gt_academic_p`: p-value for C4 directional test
- `redpajama_academic_gt_commonsense_p`: p-value for RedPajama directional test (exploratory)

### Secondary
- `kruskal_H_interaction`: overall interaction KW H statistic
- `kruskal_p_interaction`: overall interaction KW p-value
- `mean_contamination_table`: 2×3 table (domain × corpus)
- `cohen_d_per_corpus`: effect size for academic vs. commonsense per corpus
- `top5_per_corpus`: top-5 contaminated sub-tasks per corpus with domain

---

## 10. Output Files

| File | Description |
|------|-------------|
| `h-m2/experiment_results.json` | All metrics, gate result, domain classification |
| `h-m2/figures/domain_corpus_heatmap.png` | 2×3 mean contamination heatmap |
| `h-m2/figures/domain_boxplots.png` | Box plots by domain per corpus |
| `h-m2/figures/top5_per_corpus.png` | Top-5 bar charts |
| `h-m2/figures/directional_test_summary.png` | Directional test p-values |
| `h-m2/04_validation.md` | Phase 4 validation report (generated by Phase 4) |

---

## Appendix: Reuse from H-M1

| Component | H-M1 Source | H-M2 Usage |
|-----------|-------------|------------|
| 59×3 matrix | `h-m1/experiment_results.json` | Primary data input |
| Sub-task names | H-E1 taxonomy | Domain classification |
| Corpus keys | `pile`, `c4`, `redpajama` | Statistical grouping |
| scipy environment | H-M1 setup | Reused directly |
| Text preprocessing | question+choices (13-gram) | Already done (no re-run) |

---

*Generated by Phase 3 PRD step (LLM-native inline — no MCP available in test environment)*
*stepsCompleted: [executive_summary, problem_statement, functional_requirements, data_spec, dependencies, success_criteria, metrics]*
