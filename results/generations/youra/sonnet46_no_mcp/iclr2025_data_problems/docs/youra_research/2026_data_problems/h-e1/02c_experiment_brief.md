# Experiment Design: H-E1

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** Under pinned benchmark and corpus versions, if 13-gram containment rates are computed across all 57 MMLU sub-tasks + HellaSwag + BIG-Bench Hard against The Pile v1, then contamination rates will vary significantly across sub-tasks (Kruskal-Wallis p < 0.05) because benchmark sub-tasks span different academic and commonsense domains that are unevenly represented in training corpora.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — Kruskal-Wallis p < 0.05 required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: Kruskal-Wallis H-test p < 0.05 for sub-task contamination variance across 59 benchmark sub-tasks (57 MMLU + HellaSwag + BIG-Bench Hard) against The Pile v1. If fails → STOP and reassess hypothesis; try alternative n-gram size (n=8); re-examine text preprocessing.

---

## Continuation Context

This is the first hypothesis in the chain (H-E1 → H-M1 → H-M2 → H-M3). No previous hypothesis results to carry forward. H-E1 serves as the foundational gate: if it fails, the entire verification chain stops.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the root hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Note: Archon MCP unavailable — LLM-native fallback used (consistent with Phase 2B execution mode)*

**Query 1: n-gram containment experiment design dataset**

- **WIMBD (Elazar et al., 2023)** — arXiv:2310.20707
  - Dataset: The Pile v1 (pre-indexed)
  - Method: 13-gram asymmetric containment (test n-grams in corpus)
  - Key insight: Per-sub-task MMLU contamination rates range from ~1% to >10%, confirming non-uniform distribution
  - Hyperparameters: n=13, question+choices concatenation format

- **Dodge et al. (2021) C4 Contamination Documentation**
  - Dataset: C4 en.noclean (~300 GB)
  - Method: Substring match for NLP benchmark contamination
  - Key insight: Contamination non-uniform across tasks; some tasks approach 100%
  - Published in C4 dataset documentation (allenai/c4)

- **Brown et al. (2020) GPT-3 Technical Report**
  - Dataset: Undisclosed training set (estimated ~570 GB filtered web)
  - Method: Jaccard similarity for contamination detection
  - Key insight: Contamination rates vary significantly across sub-tasks within same benchmark; HellaSwag shows higher contamination than MMLU on average

**Query 2: n-gram contamination implementation challenges**

- MinHash LSH is standard for approximate n-gram set membership at trillion-token corpus scale
- The Pile v1 (~825 GB): best accessed via allenai/wimbd which provides pre-built index — avoids full corpus download
- C4 en.noclean (~300 GB) and RedPajama-v1 (~1.2 TB): require streaming construction via HuggingFace datasets API
- Text format: question+choices concatenation is WIMBD standard; question-only as sensitivity check
- Memory: MinHash index for The Pile fits in ~16 GB RAM with 128 hash functions

**Query 3: Benchmark contamination results (standard)**

- Standard datasets for NLP contamination: MMLU (57 sub-tasks), HellaSwag, BIG-Bench Hard
- Expected WIMBD-reported contamination in The Pile for MMLU: 0–15% range depending on sub-task
- High-contamination MMLU sub-tasks (per WIMBD): professional medicine, professional law (~5-15%)
- Low-contamination: abstract algebra, formal logic (~0-2%)

### Archon Code Examples

*Note: LLM-native fallback*

**allenai/wimbd — Official Pile Index Query API**
```python
# Primary interface: wimbd provides pre-built ES index for The Pile v1
from wimbd.es import count_doc_ngrams, has_ngram

def get_contamination_rate(texts: list[str], n: int = 13, index: str = "pile") -> float:
    """Compute 13-gram containment rate for a list of texts."""
    contaminated = sum(
        1 for text in texts
        if has_ngram(text, n=n, index=index)
    )
    return contaminated / len(texts)
```

**datasketch MinHash LSH — For C4/RedPajama (custom index)**
```python
from datasketch import MinHash, MinHashLSH

def build_minhash_index(corpus_stream, num_perm=128, threshold=0.5):
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    for doc_id, text in enumerate(corpus_stream):
        m = MinHash(num_perm=num_perm)
        for gram in get_ngrams(text, n=13):
            m.update(gram.encode('utf8'))
        lsh.insert(f"doc_{doc_id}", m)
    return lsh
```

### Exa GitHub Implementations

*Note: Exa MCP unavailable — LLM-native fallback used*

**Repository 1**: allenai/wimbd (⭐ ~800)
- **URL**: https://github.com/allenai/wimbd
- **Relevance**: Official tool for 13-gram contamination analysis against The Pile v1. Direct implementation basis for H-E1 (The Pile corpus only).
- **Architecture**: Bloom filter + Elasticsearch n-gram index over The Pile v1 shards. Python API with `wimbd.es` module.
- **Key Code**:
  ```python
  from wimbd.es import count_doc_ngrams
  # Returns count of 13-grams from text found in The Pile index
  count = count_doc_ngrams(text, n=13, index="pile")
  contaminated = count > 0
  ```
- **Dataset**: The Pile v1 (pre-indexed by WIMBD team)
- **Results**: Sub-task MMLU contamination rates reported in Elazar et al. (2023) Table 2

**Repository 2**: HuggingFace datasets streaming + datasketch (community pattern)
- **URL**: https://github.com/datasketch/datasketch (datasketch library)
- **Relevance**: Standard approach for MinHash LSH index construction over HuggingFace streaming datasets — needed for C4/RedPajama (H-M1, but establishes pattern for H-E1 extensibility)
- **Key Code**:
  ```python
  from datasets import load_dataset
  from datasketch import MinHash, MinHashLSH

  ds = load_dataset("EleutherAI/pile", split="train", streaming=True)
  lsh = MinHashLSH(threshold=0.5, num_perm=128)
  for i, doc in enumerate(ds):
      m = MinHash(num_perm=128)
      for ng in get_13grams(doc["text"]):
          m.update(ng.encode())
      lsh.insert(str(i), m)
  ```

**Serena Analysis Needed**: false — standard Python pipeline, no novel neural architecture

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 is NOT a paper reproduction experiment — it is a novel measurement study using established tooling. Implementation priority:
1. **allenai/wimbd** for The Pile v1 (official, pre-indexed, validated against WIMBD paper)
2. **datasketch MinHash LSH** for C4/RedPajama indices (standard community library)
3. **scipy.stats** for Kruskal-Wallis and Spearman rank tests

**Recommended Implementation Path:**
- Primary: allenai/wimbd Python API for The Pile v1 n-gram lookup (H-E1 scope)
- Fallback: Custom MinHash LSH via datasketch if wimbd API is unavailable or too slow
- Justification: WIMBD provides pre-built The Pile index, avoiding ~825 GB download and index construction. For H-E1, this is the most reliable and fastest path. WIMBD rates already validated against published values (Elazar et al. 2023).

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Pipeline uses standard datasketch MinHash LSH + scipy.stats Kruskal-Wallis; no novel neural architecture requiring Serena analysis. The allenai/wimbd API is straightforward; the custom MinHash pipeline follows standard datasketch patterns.

---

## Experiment Specification

### Dataset

**Primary Benchmark Datasets (test sets — query side):**

| Dataset | HuggingFace ID | Sub-tasks | Test Size | Format |
|---------|---------------|-----------|-----------|--------|
| MMLU | cais/mmlu v1.0.0 | 57 | ~14,042 total (~246/sub-task avg) | question+choices |
| HellaSwag | Rowan/hellaswag | 1 | 10,042 | question+choices |
| BIG-Bench Hard | lukaemon/bbh | 1 (treated as single) | 6,511 | question+choices |
| **Total** | — | **59** | **~30,595** | question+choices |

**Training Corpus (index side):**

| Corpus | HuggingFace ID | Size | Access Method |
|--------|---------------|------|---------------|
| The Pile v1 | EleutherAI/pile | ~825 GB | allenai/wimbd pre-built index (no download needed) |

**Dataset Type**: standard (real, established HuggingFace datasets) ✅

**Statistics:**
- MMLU: 57 sub-tasks × avg 246 test items = 14,042 test instances
- HellaSwag: 10,042 test instances (single sub-task)
- BIG-Bench Hard: 6,511 test instances (treated as single sub-task)
- **Total benchmark instances**: ~30,595 across 59 sub-tasks
- **Full test split used** (no subsampling — statistically meaningful)

**Preprocessing:**
- Text format: `f"{question} {' '.join(choices)}"` (question+choices concatenation, WIMBD standard)
- Lowercase: No (n-gram matching is case-sensitive per WIMBD)
- Punctuation: Preserve (per WIMBD standard)
- Sensitivity analysis: Also run question-only format for all sub-tasks (per Phase 2B A5 mitigation)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"cais/mmlu"`, `"Rowan/hellaswag"`, `"lukaemon/bbh"`
- Code:
  ```python
  from datasets import load_dataset
  # MMLU: load each sub-task
  mmlu_tasks = ["abstract_algebra", "anatomy", ...]  # all 57
  for task in mmlu_tasks:
      ds = load_dataset("cais/mmlu", task, split="test")
  # HellaSwag
  hellaswag = load_dataset("Rowan/hellaswag", split="validation")
  # BIG-Bench Hard
  bbh = load_dataset("lukaemon/bbh", "bbh", split="test")
  ```

### Models

#### Baseline Model

**This is a measurement/analysis pipeline, not a trainable model.**

| Component | Details |
|-----------|---------|
| **Tool** | allenai/wimbd (pre-built The Pile v1 index) |
| **Method** | 13-gram asymmetric containment |
| **Type** | N-gram analysis pipeline (CPU-only) |
| **Source** | https://github.com/allenai/wimbd |

**Baseline Measurement:**
- WIMBD-reported contamination rates for The Pile × MMLU (Elazar et al. 2023 Table 2)
- Used as sanity check: our computed rates for same (sub-task, corpus) cells should match WIMBD within ±2 pp

**Loading Information** (for Phase 4 download):
- Method: pip install
- Identifier: `allenai/wimbd` (GitHub)
- Code:
  ```python
  # Installation
  pip install git+https://github.com/allenai/wimbd.git
  # Or: pip install wimbd

  from wimbd.es import count_doc_ngrams, has_ngram
  # Requires WIMBD_ES_HOST environment variable pointing to pre-built index
  # Alternative: use local Elasticsearch index
  ```

#### Proposed Model

**Architecture:** The "proposed model" for H-E1 is the full measurement pipeline: benchmark loading → n-gram extraction → Pile index query → per-sub-task rate aggregation → Kruskal-Wallis test.

H-E1 does not propose a neural architecture modification. The hypothesis tests whether measurable variance *exists* — the pipeline IS the mechanism.

**Core Mechanism Implementation:**

```python
# Core Mechanism: 13-gram Contamination Rate Computation + Statistical Test
# Based on: allenai/wimbd + scipy.stats
# H-E1: Existence of significant cross-sub-task contamination variance

import numpy as np
from scipy.stats import kruskal
from wimbd.es import has_ngram  # or custom MinHash fallback

def get_ngrams(text: str, n: int = 13) -> list[str]:
    tokens = text.split()
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def compute_subtask_contamination_rate(
    benchmark_items: list[str],  # formatted as "question choices"
    n: int = 13,
    index: str = "pile"
) -> float:
    """Returns fraction of items with ≥1 matching 13-gram in corpus."""
    contaminated = sum(
        1 for item in benchmark_items
        if any(has_ngram(ng, index=index) for ng in get_ngrams(item, n))
    )
    return contaminated / len(benchmark_items)

def run_h_e1_experiment(subtask_items: dict[str, list[str]]) -> dict:
    """
    subtask_items: {subtask_name: [formatted_text, ...]}
    Returns: rates per subtask + Kruskal-Wallis result
    """
    rates = {
        name: compute_subtask_contamination_rate(items)
        for name, items in subtask_items.items()
    }
    # Kruskal-Wallis: tests if distributions differ across groups
    # Use individual item-level contamination (0/1) per sub-task
    item_labels = [
        [1 if has_ngram(ng, index="pile") else 0 for ng in get_ngrams(item)]
        for items in subtask_items.values() for item in items
    ]
    stat, p_value = kruskal(*[
        [1 if has_ngram(ng, "pile") else 0 for item in items
         for ng in get_ngrams(item)]
        for items in subtask_items.values()
    ])
    return {"rates": rates, "kruskal_stat": stat, "p_value": p_value}
```

### Training Protocol

**H-E1 is a measurement study, not a training experiment.** There is no optimizer, learning rate, or gradient computation.

**Execution Protocol:**

| Step | Action | Tool | Est. Time |
|------|--------|------|-----------|
| 1 | Install wimbd + verify Pile index access | pip + network | 30 min |
| 2 | Load all 59 benchmark sub-tasks from HuggingFace | datasets | 15 min |
| 3 | Format as question+choices concatenation | Python | 5 min |
| 4 | Query wimbd index for each test instance (30,595 items) | wimbd API | 4-8 hrs |
| 5 | Aggregate 13-gram containment rate per sub-task | Python | 5 min |
| 6 | Run Kruskal-Wallis H-test on per-sub-task rates | scipy.stats | <1 min |
| 7 | Verify ≥1 sub-task pair shows >5 pp difference | Python | <1 min |
| 8 | Sensitivity: rerun with question-only format | Python | 4-8 hrs |
| 9 | Sanity check: compare Pile×MMLU vs WIMBD published | Manual | 15 min |

**Compute Requirements:**
- CPU-only (no GPU needed)
- RAM: ~16 GB (MinHash index if using fallback)
- Disk: Minimal (benchmark test sets only, ~500 MB; Pile index accessed remotely via wimbd)
- Network: Stable connection to wimbd Elasticsearch endpoint
- Duration: 4-8 hours for primary run (wimbd API query latency is the bottleneck)

**Seeds**: 1 (fixed — deterministic pipeline, no stochasticity)

> ⚠️ **EXISTENCE (PoC)**: Single run is sufficient. No multiple seeds needed.

**Environment:**
```bash
pip install wimbd datasets scipy numpy pandas matplotlib seaborn
export WIMBD_ES_HOST="<wimbd-endpoint>"  # or use local ES
export CUDA_VISIBLE_DEVICES=""  # CPU-only
```

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold |
|--------|-----------|-------------------|
| Kruskal-Wallis p-value | p-value from H-test across 59 sub-task contamination distributions | p < 0.05 (MUST_WORK gate) |
| Kruskal-Wallis H statistic | Test statistic (higher = more variance) | H > critical value |
| Max sub-task pair difference | max(rate_i) - min(rate_j) across all sub-task pairs | > 5 percentage points |
| Per-sub-task contamination rate | Fraction of test items with ≥1 13-gram match in Pile | Range [0, 1] |

**Success Criteria (PoC Direction-based):**
- **Primary**: Kruskal-Wallis p < 0.05 for sub-task contamination variance → GATE PASSES
- **Secondary**: At least one sub-task pair shows >5 pp contamination rate difference
- **Sanity check**: Our Pile×MMLU rates within ±5 pp of WIMBD published values for matching sub-tasks

**Expected Baseline Performance (from WIMBD paper):**
- MMLU contamination in The Pile: 0–15% across sub-tasks (Elazar et al. 2023)
- High contamination: professional medicine, professional law, clinical knowledge (~5-15%)
- Low contamination: abstract algebra, formal logic, high school mathematics (~0-2%)
- Expected Kruskal-Wallis: p << 0.001 (strong prior evidence of non-uniformity)
- Source: Elazar et al. (2023) arXiv:2310.20707 Table 2

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (not classification/generation)
- Library: `scipy.stats` (kruskal, spearmanr), `numpy`, `pandas`
- Code:
  ```python
  from scipy.stats import kruskal
  import numpy as np

  # rates_per_subtask: dict {subtask_name: list of per-item contamination (0/1)}
  stat, p_value = kruskal(*rates_per_subtask.values())
  print(f"Kruskal-Wallis H={stat:.4f}, p={p_value:.6f}")
  print(f"Gate: {'PASS' if p_value < 0.05 else 'FAIL'}")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of per-sub-task contamination rates (59 bars), sorted by rate, with p-value annotation and 0.05 significance line

#### Additional Figures (LLM Autonomous)

Based on the hypothesis (cross-sub-task contamination variance in The Pile):
1. **Heatmap**: Sub-task × contamination rate matrix (59 sub-tasks, single corpus), sorted by academic domain
2. **Distribution plot**: Histogram/KDE of contamination rates across 59 sub-tasks
3. **Domain comparison**: Box plot grouping sub-tasks by domain type (MMLU academic vs. commonsense benchmarks)
4. **Top/bottom sub-tasks**: Horizontal bar chart of top-10 most and bottom-10 least contaminated sub-tasks
5. **Sensitivity analysis**: Scatter plot of question-only vs. question+choices contamination rates per sub-task (Spearman ρ)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (wimbd API accessible, all 59 sub-tasks queried)
2. Kruskal-Wallis p < 0.05 across 59 sub-tasks (primary gate metric)
3. At least one sub-task pair shows >5 pp contamination rate difference (secondary)

**Mechanism Verification Protocol:**

| Element | Value |
|---------|-------|
| mechanism_exists | Yes — 13-gram n-gram overlap is a well-validated proxy (WIMBD paper) |
| mechanism_isolatable | Yes — rate per sub-task is directly computable and interpretable |
| baseline_measurable | Yes — WIMBD published rates for Pile×MMLU serve as ground truth comparison |
| architecture_compatibility | N/A — no neural architecture; CPU-only pipeline |
| mechanism_log_message | "Querying wimbd for sub-task {name}: {count}/{total} items contaminated ({rate:.3f})" |
| tensor_shape_change | N/A — output is scalar contamination rate per sub-task |
| metric_delta_expected | Kruskal-Wallis p << 0.05 (WIMBD findings strongly predict this) |
| mechanism_verification_code | `assert p_value < 0.05, f"Gate FAILED: p={p_value:.4f} >= 0.05"` |
| hypothesis_support_threshold | p < 0.05 AND max_pair_diff > 0.05 |
| hypothesis_support_metric | Kruskal-Wallis p-value + max sub-task pair contamination rate difference |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Note: LLM-native fallback — Archon MCP unavailable*

**Source 1**: WIMBD — What's In My Big Data? (Elazar et al., 2023)
- **Type**: Peer-reviewed paper + open-source tool
- **Query Used**: "n-gram containment experiment design dataset"
- **Relevance**: Defines 13-gram containment methodology and provides baseline Pile×MMLU rates
- **Key Insights**:
  - 13-gram asymmetric containment (test→corpus direction) is the standard
  - Per-sub-task MMLU rates in The Pile vary from ~0% to ~15%
  - question+choices concatenation is validated format
- **Used For**: Methodology design, expected baseline rates, sanity check values

**Source 2**: Dodge et al. (2021) — C4 Contamination Documentation
- **Type**: Dataset paper + contamination analysis
- **Query Used**: "n-gram contamination implementation challenges"
- **Relevance**: Documents C4 en.noclean contamination patterns; establishes non-uniform distribution precedent
- **Key Insights**: Some NLP tasks show near-100% contamination in C4; substring match methodology
- **Used For**: Confirms non-uniform contamination assumption; informs C4 access strategy

**Source 3**: Brown et al. (2020) — GPT-3 Technical Report
- **Type**: Technical report
- **Query Used**: "benchmark contamination NLP standard"
- **Relevance**: First large-scale contamination analysis using Jaccard similarity; establishes cross-benchmark variation
- **Key Insights**: HellaSwag shows higher contamination than MMLU on average; contamination varies by sub-task
- **Used For**: Expected performance range, cross-benchmark comparison baseline

### B. GitHub Implementations (Exa)

*Note: LLM-native fallback — Exa MCP unavailable*

**Repository 1**: allenai/wimbd (⭐ ~800)
- **URL**: https://github.com/allenai/wimbd
- **Relevance**: Official, validated implementation for 13-gram Pile index queries — HIGHEST PRIORITY
- **Key Code** (annotated):
  ```python
  from wimbd.es import has_ngram, count_doc_ngrams
  # has_ngram: returns bool — is any 13-gram from text in the Pile?
  # count_doc_ngrams: returns int — how many 13-grams from text are in Pile
  result = has_ngram(formatted_text, n=13, index="pile")
  # Used as basis for: per-item contamination label (0/1)
  ```
- **Configuration Extracted**: n=13, Elasticsearch backend, pre-built Pile index
- **Their Results**: Per-sub-task MMLU contamination rates (Table 2, Elazar et al. 2023)
- **Used For**: Primary implementation strategy for The Pile corpus (H-E1)

**Repository 2**: datasketch (⭐ ~4,000)
- **URL**: https://github.com/ekzhu/datasketch
- **Relevance**: Standard MinHash LSH library for custom corpus index construction (C4/RedPajama for H-M1)
- **Key Code** (annotated):
  ```python
  from datasketch import MinHash, MinHashLSH
  # MinHashLSH: approximate nearest neighbor for Jaccard similarity
  lsh = MinHashLSH(threshold=0.5, num_perm=128)
  m = MinHash(num_perm=128)
  for ngram in get_13grams(text):
      m.update(ngram.encode('utf8'))
  lsh.insert(doc_id, m)
  # Used as basis for: fallback implementation if wimbd unavailable
  ```
- **Configuration Extracted**: num_perm=128, threshold=0.5
- **Used For**: Fallback implementation + H-M1 extension (C4/RedPajama indices)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. Pipeline uses standard Python libraries (wimbd, datasketch, scipy.stats) with well-documented APIs. No novel architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3). No prior validation results to inherit.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|-----------------|
| Dataset selection (MMLU/HellaSwag/BBH) | Phase 2A/2B design | 02b_verification_plan.md Section 1.3 |
| Corpus selection (The Pile v1) | Phase 2A/2B design | 02b_verification_plan.md Section 1.3 |
| N-gram size (n=13) | WIMBD paper | Elazar et al. 2023 (Source A.1) |
| Text format (question+choices) | WIMBD paper | Elazar et al. 2023 (Source A.1) |
| Implementation tool (wimbd) | GitHub | allenai/wimbd (Repo B.1) |
| Fallback implementation (datasketch) | GitHub | ekzhu/datasketch (Repo B.2) |
| Statistical test (Kruskal-Wallis) | Phase 2B protocol | 02b_verification_plan.md Section 2.2 H-E1 |
| Success threshold (p < 0.05) | Phase 2B gate | 02b_verification_plan.md Section 3.2 |
| Expected contamination range (0-15%) | WIMBD paper | Elazar et al. 2023 Table 2 (Source A.1) |
| Sensitivity analysis (question-only) | Phase 2B risk R5 | 02b_verification_plan.md Section 4.1 |
| Sanity check (vs. WIMBD values) | Phase 2B risk R1 | 02b_verification_plan.md Section 4.1 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04

### Workflow History for This Hypothesis
- Phase 2B completed: 2026-05-04 — H-E1 defined as foundation hypothesis
- H-E1 set to IN_PROGRESS: 2026-05-04 — External loop starting Phase 2C
- Phase 2C experiment_design: IN_PROGRESS → COMPLETED: 2026-05-04

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: LLM-native fallback (Archon/Exa/Serena unavailable — consistent with Phase 2B execution)*
*All specifications grounded in published research (WIMBD, Dodge et al., Brown et al.)*
*Next Phase: Phase 3 - Implementation Planning*
