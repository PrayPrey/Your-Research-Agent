# Product Requirements Document: H-E1
# Cross-Sub-Task Contamination Variance in The Pile v1

**Hypothesis:** H-E1
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK — Kruskal-Wallis p < 0.05
**Generated:** 2026-05-04
**Phase:** 3 — Implementation Planning
**Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

H-E1 is the foundation hypothesis for the Cross-Corpus Contamination Atlas. It tests whether 13-gram containment rates vary **significantly** across 59 benchmark sub-tasks (57 MMLU + HellaSwag + BIG-Bench Hard) when queried against The Pile v1 training corpus. Success requires Kruskal-Wallis p < 0.05, providing the statistical evidence that contamination is non-uniform across domains — the prerequisite for all downstream hypotheses (H-M1, H-M2, H-M3).

This is a **measurement pipeline**, not a neural architecture. The "model" is the allenai/wimbd Elasticsearch index over The Pile v1.

---

## 2. Problem Statement

**Research question:** Do 13-gram contamination rates differ significantly across NLP benchmark sub-tasks when measured against The Pile v1 training corpus?

**Why this matters:** If contamination is uniform, it cannot explain differential LLM performance across tasks. If non-uniform (as predicted by WIMBD paper), corpus-specific contamination signatures explain task-level performance gaps.

**Current gap:** No systematic, reproducible contamination atlas exists across all 57 MMLU sub-tasks + HellaSwag + BIG-Bench Hard simultaneously, with pinned dataset versions.

---

## 3. Functional Requirements

### FR-1: Benchmark Data Loading

**FR-1.1** Load all 57 MMLU sub-tasks from `cais/mmlu` (v1.0.0, split="test")
- Expected: ~14,042 test instances across 57 sub-tasks (~246/sub-task avg)
- Format: `question` + `choices` fields

**FR-1.2** Load HellaSwag from `Rowan/hellaswag` (split="validation")
- Expected: 10,042 instances
- Format: `ctx` + `endings` fields

**FR-1.3** Load BIG-Bench Hard from `lukaemon/bbh` (split="test", treated as single sub-task)
- Expected: 6,511 instances

**FR-1.4** Text formatting (WIMBD standard):
- Primary: `f"{question} {' '.join(choices)}"` (question+choices concatenation)
- Ablation: question-only format (`question` field only)

**FR-1.5** Dataset versions must be pinned (no floating latest):
- MMLU: cais/mmlu v1.0.0
- HellaSwag: Rowan/hellaswag standard split
- BIG-Bench Hard: lukaemon/bbh standard

### FR-2: N-gram Extraction

**FR-2.1** Extract all 13-grams from each formatted benchmark instance
- Method: sliding window over whitespace-tokenized text
- `tokens = text.split(); ngrams = [" ".join(tokens[i:i+13]) for i in range(len(tokens)-12)]`

**FR-2.2** No lowercasing, no punctuation removal (WIMBD standard — case-sensitive)

**FR-2.3** Minimum token length: skip instances with < 13 tokens (log count)

### FR-3: The Pile v1 Index Query (Primary Path — wimbd)

**FR-3.1** Use allenai/wimbd pre-built Elasticsearch index for The Pile v1
- Install: `pip install git+https://github.com/allenai/wimbd.git`
- Requires: `WIMBD_ES_HOST` environment variable

**FR-3.2** Per-item contamination label:
- `contaminated = any(has_ngram(ng, n=13, index="pile") for ng in get_ngrams(item))`
- Returns: 0 (clean) or 1 (contaminated)

**FR-3.3** Fallback path (if wimbd unavailable): MinHash LSH via `datasketch`
- `MinHashLSH(threshold=0.5, num_perm=128)` over The Pile streaming
- Must be flagged in output as "fallback mode"

**FR-3.4** Per-sub-task contamination rate:
- `rate = sum(labels) / len(labels)` where labels are per-item contamination (0/1)

### FR-4: Statistical Testing

**FR-4.1** Kruskal-Wallis H-test across all 59 sub-tasks
- Input: per-item contamination lists for each sub-task (0/1 vectors)
- `from scipy.stats import kruskal; stat, p = kruskal(*subtask_label_lists)`
- Gate condition: `p < 0.05`

**FR-4.2** Secondary check: max sub-task pair contamination rate difference
- `max_diff = max(rates.values()) - min(rates.values())`
- Expected: > 5 percentage points

**FR-4.3** Sensitivity analysis: repeat FR-2 through FR-4.2 with question-only format

**FR-4.4** Sanity check: compare our Pile×MMLU rates vs. WIMBD published values (Elazar et al. 2023 Table 2)
- Tolerance: ±5 percentage points for matching sub-tasks

### FR-5: Output and Reporting

**FR-5.1** Save per-sub-task contamination rates to CSV:
- `h-e1/results/contamination_rates.csv` with columns: `subtask`, `corpus`, `n_items`, `n_contaminated`, `rate`

**FR-5.2** Save Kruskal-Wallis result:
- `h-e1/results/statistical_tests.json` with fields: `kruskal_stat`, `p_value`, `gate_pass`, `max_pair_diff`

**FR-5.3** Generate required visualization (mandatory):
- Bar chart: per-sub-task contamination rates (59 bars), sorted by rate, with p-value annotation
- Save to: `h-e1/figures/contamination_rates_barplot.png`

**FR-5.4** Generate additional visualizations (autonomous):
- Heatmap: sub-task × rate matrix sorted by academic domain
- Distribution: histogram/KDE of contamination rates
- Domain comparison: box plot (MMLU academic vs. commonsense benchmarks)
- Top/bottom sub-tasks: horizontal bar chart (top-10 and bottom-10)
- Sensitivity: scatter plot question-only vs. question+choices per sub-task (Spearman ρ)
- Save all to: `h-e1/figures/`

**FR-5.5** Console logging during execution:
- `f"Querying wimbd for sub-task {name}: {count}/{total} items contaminated ({rate:.3f})"`

### FR-6: Gate Assertion

**FR-6.1** Hard assertion at end of pipeline:
- `assert p_value < 0.05, f"Gate FAILED: p={p_value:.4f} >= 0.05"`

**FR-6.2** Structured gate result in output JSON (FR-5.2)

---

## 4. Data Specification

### 4.1 Benchmark Datasets (Query Side)

| Dataset | HuggingFace ID | Sub-tasks | Test Size | Download Required |
|---------|---------------|-----------|-----------|-------------------|
| MMLU | cais/mmlu v1.0.0 | 57 | ~14,042 | Auto (HuggingFace datasets) |
| HellaSwag | Rowan/hellaswag | 1 | 10,042 | Auto (HuggingFace datasets) |
| BIG-Bench Hard | lukaemon/bbh | 1 | 6,511 | Auto (HuggingFace datasets) |

> All datasets auto-download via HuggingFace datasets — **no manual download task needed**.

### 4.2 Training Corpus (Index Side)

| Corpus | Access | Manual Download |
|--------|--------|-----------------|
| The Pile v1 | allenai/wimbd pre-built ES index (remote) | **No** — accessed via API |

> The Pile v1 (~825 GB) is **not downloaded**. Accessed via wimbd remote Elasticsearch.
> If wimbd endpoint unavailable: fallback to datasketch MinHash LSH (requires ~16 GB RAM).

---

## 5. Non-Functional Requirements

**NFR-1: Reproducibility**
- Fixed seed: 1 (deterministic pipeline)
- Pinned dataset versions (see FR-1.5)
- All results saved to files for re-verification

**NFR-2: Performance**
- Primary run: 4-8 hours (wimbd API latency bottleneck, ~30,595 queries)
- CPU-only (no GPU required)
- RAM: ≤ 16 GB (MinHash fallback); < 4 GB (wimbd primary path)

**NFR-3: Error Handling**
- Log failed wimbd queries with retry (3 attempts)
- Skip items with < 13 tokens; log skipped count
- Handle missing HuggingFace sub-tasks gracefully (log + continue)

**NFR-4: Environment**
- CPU-only: `CUDA_VISIBLE_DEVICES=""`
- Python 3.9+
- Dependencies: wimbd, datasets, scipy, numpy, pandas, matplotlib, seaborn

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Kruskal-Wallis p-value | p < 0.05 | MUST_WORK gate |
| Max sub-task pair rate difference | > 5 pp | Secondary |
| Sanity check (vs. WIMBD Table 2) | Within ±5 pp | Validation |
| Code runs without error | All 59 sub-tasks queried | Required |
| Sensitivity analysis complete | question-only rates saved | Required |

---

## 7. Dependencies

### 7.1 Python Packages

```
wimbd (git+https://github.com/allenai/wimbd.git)
datasets>=2.14.0
scipy>=1.10.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
datasketch>=1.6.0
tqdm>=4.65.0
```

### 7.2 External Repositories (Reference)

| Repository | Purpose |
|------------|---------|
| https://github.com/allenai/wimbd | Primary The Pile v1 index tool |
| https://github.com/ekzhu/datasketch | MinHash LSH fallback |

### 7.3 Environment Variables

| Variable | Purpose |
|----------|---------|
| `WIMBD_ES_HOST` | URL of wimbd Elasticsearch endpoint |
| `CUDA_VISIBLE_DEVICES` | Set to `""` (CPU-only) |

---

## 8. Constraints

- **No GPU required**: Pure statistical measurement pipeline
- **Single run sufficient**: EXISTENCE hypothesis, deterministic
- **WIMBD dependency**: Primary path requires network access to wimbd ES endpoint
- **Full test sets**: Use complete test splits (no subsampling) — statistical validity requires N ≥ 246/sub-task
- **Pinned versions**: Do not use latest/floating dataset versions

---

## 9. Traceability

| Requirement | Source |
|-------------|--------|
| FR-1: 59 sub-tasks | 02c_experiment_brief.md §Dataset |
| FR-2: 13-gram, case-sensitive | Elazar et al. (2023) WIMBD methodology |
| FR-3: wimbd primary path | 02c_experiment_brief.md §Implementation Priority |
| FR-4: Kruskal-Wallis p<0.05 | 02b_verification_plan.md §H-E1 gate |
| FR-4.3: Sensitivity analysis | 02b_verification_plan.md §Risk R5 |
| FR-4.4: Sanity check | 02b_verification_plan.md §Risk R1 |
| FR-5.3: Bar chart (required) | 02c_experiment_brief.md §Visualization |
