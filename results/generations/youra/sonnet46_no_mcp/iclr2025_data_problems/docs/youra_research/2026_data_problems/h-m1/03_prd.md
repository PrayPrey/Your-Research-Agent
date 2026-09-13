# Product Requirements Document: H-M1
# Cross-Corpus Contamination Variance Across The Pile v1, C4 en.noclean, and RedPajama-v1

**Hypothesis:** H-M1
**Type:** MECHANISM (PoC)
**Gate:** MUST_WORK — Kruskal-Wallis p < 0.05 (corpus variance)
**Generated:** 2026-05-04
**Phase:** 3 — Implementation Planning
**Source:** 02c_experiment_brief.md
**Prerequisite:** H-E1 VALIDATED (Kruskal-Wallis H=590.82, p=2.73e-89)

---

## 1. Executive Summary

H-M1 tests the **core mechanism** of the Cross-Corpus Contamination Atlas: whether the three training corpora (The Pile v1, C4 en.noclean, RedPajama-v1) produce **significantly different 13-gram contamination rates** across the same 59 benchmark sub-tasks. It extends the H-E1 Pile-only pipeline to the full **59×3 contamination matrix** by adding C4 and RedPajama MinHash LSH indices via HuggingFace streaming.

Success requires Kruskal-Wallis p < 0.05 on per-corpus contamination rate distributions. This validates the "corpus-as-variable" claim central to the paper — that corpus source composition drives systematically different contamination signatures.

This is a **CPU-only data analysis pipeline**, not a neural architecture. The H-E1 Pile MinHash LSH index is reused (or rebuilt); C4 and RedPajama indices are constructed fresh via `datasketch`.

---

## 2. Problem Statement

**Research question:** Do 13-gram contamination rates vary significantly across The Pile v1, C4 en.noclean, and RedPajama-v1 when measuring the same 59 benchmark sub-tasks?

**Why this matters:** H-E1 confirmed sub-task contamination variance within a single corpus (The Pile). H-M1 tests whether corpus identity is a significant variable — if different corpora produce structurally different contamination signatures, the atlas has scientific validity beyond a single corpus analysis.

**Current gap:** No unified cross-corpus (3+) × cross-benchmark (57+ sub-tasks) contamination rate matrix exists in the literature. WIMBD covers only The Pile. This is the novel contribution the entire paper rests on.

---

## 3. Functional Requirements

### FR-1: Benchmark Data Loading (Reuse from H-E1)

**FR-1.1** Load all 57 MMLU sub-tasks from `cais/mmlu` (v1.0.0, split="test")
- Expected: ~14,042 test instances across 57 sub-tasks (~246/sub-task avg)
- Format: `question` + `choices` fields

**FR-1.2** Load HellaSwag from `Rowan/hellaswag` (split="validation")
- Expected: 10,042 instances
- Format: `ctx` + `endings` fields

**FR-1.3** Load BIG-Bench Hard from `lukaemon/bbh` (split="test")
- Expected: ~6,511 instances across 23 tasks; treated as one sub-task group

**FR-1.4** Text formatting (WIMBD standard — same as H-E1):
- Primary: `f"{question} {' '.join(choices)}"` (question+choices concatenation)
- Sensitivity: question-only format (`question` field only)

**FR-1.5** Dataset versions must be pinned (no floating latest):
- MMLU: `cais/mmlu` v1.0.0
- HellaSwag: `Rowan/hellaswag` standard split
- BIG-Bench Hard: `lukaemon/bbh` standard

### FR-2: N-gram Extraction (Identical to H-E1)

**FR-2.1** Extract all 13-grams from each formatted benchmark instance
- Method: sliding window over whitespace-tokenized text
- `tokens = text.lower().split(); ngrams = [" ".join(tokens[i:i+13]) for i in range(len(tokens)-12)]`
- Note: Use lowercase for MinHash consistency (datasketch recommendation)

**FR-2.2** Minimum token length: skip instances with < 13 tokens (log count)

**FR-2.3** Fixed seed: 1 (deterministic MinHash)

### FR-3: Corpus Index Construction (New for H-M1)

#### FR-3.1: The Pile v1 Index (Reuse H-E1)

**FR-3.1a** Primary path: Reuse H-E1 MinHash LSH index if available in `h-e1/` directory
- Check: `h-e1/pile_index.pkl` or equivalent checkpoint

**FR-3.1b** Fallback path: Rebuild via `datasketch` MinHash LSH over `EleutherAI/pile` HF streaming
- `MinHashLSH(threshold=0.5, num_perm=128)`
- Checkpoint every 500k documents

**FR-3.1c** Sanity check: Pile×MMLU rates must be within ±5 pp of WIMBD published values (Elazar et al. 2023)

#### FR-3.2: C4 en.noclean Index (New)

**FR-3.2a** Stream C4 from HuggingFace:
```python
load_dataset("allenai/c4", "en.noclean", streaming=True, split="train")
```

**FR-3.2b** Build MinHash LSH index:
- `MinHashLSH(threshold=0.5, num_perm=128)`
- Checkpoint every 500k documents to `h-m1/indices/c4_ckpt_{N}.pkl`

**FR-3.2c** Retry logic: 3 attempts with exponential backoff on HF API failures

**FR-3.2d** Fallback: If streaming fails after 3 attempts, use 10% random sample; flag in results as "C4_SAMPLED"

#### FR-3.3: RedPajama-v1 Index (New)

**FR-3.3a** Stream RedPajama from HuggingFace:
```python
load_dataset("togethercomputer/RedPajama-Data-1T", streaming=True, split="train")
```

**FR-3.3b** Build MinHash LSH index:
- `MinHashLSH(threshold=0.5, num_perm=128)`
- Checkpoint every 500k documents to `h-m1/indices/redpajama_ckpt_{N}.pkl`

**FR-3.3c** Retry logic: 3 attempts with exponential backoff on HF API failures

**FR-3.3d** Fallback: If streaming fails, use 10% random sample; flag in results as "RP_SAMPLED"

### FR-4: 59×3 Contamination Matrix Construction

**FR-4.1** For each of 59 sub-tasks × 3 corpora, compute per-item contamination label:
```python
contaminated = bool(lsh.query(text_to_minhash(item_text)))
```

**FR-4.2** Per-cell contamination rate:
```python
rate = sum(labels) / len(labels)  # where labels are per-item 0/1 values
```

**FR-4.3** Output matrix shape: `matrix[subtask_name][corpus_name] = float` (59×3)

**FR-4.4** Save full matrix to `h-m1/results/contamination_matrix.csv`:
- Columns: `subtask`, `corpus`, `n_items`, `n_contaminated`, `rate`
- 177 rows (59 × 3)

### FR-5: Statistical Testing

**FR-5.1** Kruskal-Wallis H-test across 3 corpora:
```python
from scipy.stats import kruskal
pile_rates = [matrix[s]['pile'] for s in matrix]   # 59 values
c4_rates   = [matrix[s]['c4']   for s in matrix]   # 59 values
rp_rates   = [matrix[s]['rp']   for s in matrix]   # 59 values
H, p = kruskal(pile_rates, c4_rates, rp_rates)
```
- **Gate condition:** `p < 0.05`

**FR-5.2** Secondary check: Max corpus-pair mean contamination rate difference:
```python
means = {corp: np.mean(rates) for corp, rates in ...}
max_pair_diff = max(abs(m1-m2) for m1, m2 in combinations(means.values(), 2))
```
- Expected: > 2 percentage points

**FR-5.3** Post-hoc pairwise analysis (Dunn's test with Bonferroni correction):
```python
import scikit_posthocs as sp
posthoc = sp.posthoc_dunn([pile_rates, c4_rates, rp_rates], p_adjust='bonferroni')
```

**FR-5.4** WIMBD consistency check (Spearman correlation):
```python
from scipy.stats import spearmanr
rho, p_spearman = spearmanr(h_m1_pile_rates, wimbd_published_rates)
```
- Expected: ρ > 0.7

**FR-5.5** Sensitivity analysis: repeat FR-4 through FR-5.4 with question-only text format

### FR-6: Output and Reporting

**FR-6.1** Save contamination matrix: `h-m1/results/contamination_matrix.csv` (177 rows)

**FR-6.2** Save statistical test results: `h-m1/results/statistical_tests.json`
```json
{
  "kruskal_H": float,
  "kruskal_p": float,
  "gate_pass": bool,
  "corpus_means": {"pile": float, "c4": float, "redpajama": float},
  "max_pair_diff_pp": float,
  "wimbd_spearman_rho": float,
  "wimbd_spearman_p": float,
  "dunn_posthoc": {...},
  "sensitivity_kruskal_p": float
}
```

**FR-6.3** Generate REQUIRED visualization:
- Bar chart: mean contamination rate per corpus (Pile/C4/RedPajama) with ±1 std error bars
- Horizontal reference line at 2 pp threshold
- Annotate Kruskal-Wallis H and p-value
- Save to: `h-m1/figures/corpus_comparison_barplot.png`

**FR-6.4** Generate additional visualizations (autonomous):
- 59×3 Heatmap: sub-tasks as rows (sorted by mean rate desc), corpora as columns; color = rate (%)
  Save: `h-m1/figures/contamination_matrix_heatmap.png`
- Corpus pair difference: pairwise mean difference bars (Pile−C4, Pile−RP, C4−RP) with 2 pp threshold line
  Save: `h-m1/figures/corpus_pair_differences.png`
- WIMBD consistency scatter: H-M1 Pile column vs. WIMBD published rates; Spearman ρ annotated
  Save: `h-m1/figures/wimbd_consistency_scatter.png`
- Per-corpus top/bottom rankings: top-10 and bottom-10 sub-tasks per corpus (horizontal bar)
  Save: `h-m1/figures/per_corpus_rankings.png`
- Dunn's test p-value heatmap for 3 corpus pairs
  Save: `h-m1/figures/dunn_posthoc_heatmap.png`

**FR-6.5** Console logging during execution:
- Index construction: `f"Building {corpus} index: {doc_id:,} docs processed"`
- Matrix query: `f"Querying {corpus} for sub-task {name}: {count}/{total} contaminated ({rate:.3f})"`

### FR-7: Gate Assertion

**FR-7.1** Hard assertion at end of pipeline:
```python
assert p_value < 0.05, f"Gate FAILED: Kruskal-Wallis p={p_value:.4f} >= 0.05"
```

**FR-7.2** Structured gate result in output JSON (FR-6.2)

---

## 4. Data Specification

### 4.1 Benchmark Datasets (Query Side — identical to H-E1)

| Dataset | HuggingFace ID | Sub-tasks | Test Size | Download Required |
|---------|---------------|-----------|-----------|-------------------|
| MMLU | cais/mmlu v1.0.0 | 57 | ~14,042 | Auto (HuggingFace datasets) |
| HellaSwag | Rowan/hellaswag | 1 | 10,042 | Auto (HuggingFace datasets) |
| BIG-Bench Hard | lukaemon/bbh | 1 | ~6,511 | Auto (HuggingFace datasets) |

> All benchmark datasets auto-download via HuggingFace — **no manual download task needed**.

### 4.2 Training Corpora (Index Side — 3 corpora)

| Corpus | HuggingFace ID | Approx. Size | Access Strategy | Manual Download |
|--------|---------------|-------------|-----------------|-----------------|
| The Pile v1 | EleutherAI/pile | ~825 GB | Reuse H-E1 MinHash index OR HF streaming | **No** — streamed/reused |
| C4 en.noclean | allenai/c4 (en.noclean) | ~300 GB | HF streaming | **No** — streamed |
| RedPajama-v1 | togethercomputer/RedPajama-Data-1T | ~1.2 TB | HF streaming | **No** — streamed |

> Corpora are accessed via HuggingFace streaming API — full corpus not downloaded.
> Index checkpoints saved to `h-m1/indices/` (~2-5 GB per corpus).

---

## 5. Non-Functional Requirements

**NFR-1: Reproducibility**
- Fixed seed: 1 (deterministic MinHash construction)
- Pinned dataset versions (see FR-1.5)
- All results saved to files

**NFR-2: Performance**
- Index construction: ~12-24 hrs per new corpus (C4, RedPajama) via streaming
- Matrix query: ~2-4 hrs (59 × 3 cells)
- CPU-only (no GPU required)
- RAM: ≤ 32 GB recommended (MinHash LSH index in memory)
- Disk: ≥ 20 GB for index checkpoints

**NFR-3: Error Handling**
- Retry streaming failures: 3 attempts with exponential backoff
- Checkpoint MinHash indices every 500k documents
- Log and skip corpus documents with missing `text` field
- Fallback to 10% sample if full streaming fails (flagged in output)

**NFR-4: Environment**
- CPU-only: `CUDA_VISIBLE_DEVICES=""`
- Python 3.9+
- Disk: ≥ 20 GB free for index checkpoints

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Kruskal-Wallis p-value (corpus variance) | p < 0.05 | MUST_WORK gate |
| Max corpus-pair mean rate difference | > 2 pp | Secondary |
| WIMBD consistency (Spearman ρ, Pile×MMLU) | ρ > 0.7 | Sanity check |
| 59×3 matrix populated | 177 non-null cells | Required |
| Code runs without error | All 3 indices built | Required |
| Sensitivity analysis complete | Question-only rates saved | Required |

---

## 7. Dependencies

### 7.1 Python Packages

```
datasets>=2.14.0
datasketch>=1.6.0
scipy>=1.10.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-posthocs>=0.7.0
tqdm>=4.65.0
```

Optional (Pile primary path):
```
wimbd (git+https://github.com/allenai/wimbd.git)
```

### 7.2 External Repositories (Reference)

| Repository | Purpose |
|------------|---------|
| https://github.com/allenai/wimbd | Pile v1 contamination reference values (sanity check) |
| https://github.com/ekzhu/datasketch | MinHash LSH for C4 and RedPajama index construction |

### 7.3 Environment Variables

| Variable | Purpose |
|----------|---------|
| `CUDA_VISIBLE_DEVICES` | Set to `""` (CPU-only) |
| `HF_DATASETS_CACHE` | Optional: set custom HF cache path |

### 7.4 Reused Artifacts from H-E1

| Artifact | Path | Usage |
|----------|------|-------|
| Pile MinHash LSH index | `h-e1/pile_index.pkl` (if exists) | Reuse for Pile column in H-M1 matrix |
| 59 sub-task benchmark loading code | `h-e1/code/` | Reuse text formatting and loading logic |
| Benchmark text format | question+choices | Apply identically to all 3 corpora |

---

## 8. Constraints

- **No GPU required**: Pure n-gram statistical analysis pipeline
- **Streaming required**: C4 (~300 GB) and RedPajama (~1.2 TB) are too large to download fully
- **Checkpoint required**: Index construction takes 12-48 hrs; must be resumable
- **Full benchmark test sets**: No subsampling — statistical validity requires complete test splits (N ≥ 246 per MMLU sub-task, full HellaSwag/BBH)
- **Pinned versions**: Do not use latest/floating dataset versions
- **MinHash parameters fixed**: `n=13, num_perm=128` — identical to H-E1 for comparability

---

## 9. Traceability

| Requirement | Source |
|-------------|--------|
| FR-1: 59 sub-tasks (same as H-E1) | 02c_experiment_brief.md §Dataset; H-E1 validation |
| FR-2: 13-gram, lowercase | Elazar et al. (2023) WIMBD + datasketch conventions |
| FR-3: MinHash LSH for C4/RedPajama | 02c_experiment_brief.md §Core Mechanism; ekzhu/datasketch |
| FR-3.1: Reuse H-E1 Pile index | 02c_experiment_brief.md §Reuse opportunity |
| FR-4: 59×3 matrix | 02c_experiment_brief.md §Architecture |
| FR-5.1: Kruskal-Wallis p<0.05 | 02b_verification_plan.md §H-M1 gate |
| FR-5.2: >2 pp corpus pair diff | 02b_verification_plan.md §H-M1 secondary |
| FR-5.3: Dunn's test Bonferroni | 02c_experiment_brief.md §Secondary metrics |
| FR-5.4: WIMBD consistency | 02b_verification_plan.md §Risk R1; H-E1 methodology |
| FR-6.3: Bar chart (required) | 02c_experiment_brief.md §Visualization Required |
| FR-6.4: Additional figures | 02c_experiment_brief.md §Additional Figures |
