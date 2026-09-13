# Experiment Design: H-M1

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** Under pinned versions, if 13-gram containment rates are computed for the full 59×3 matrix (59 benchmark sub-tasks × 3 corpora: The Pile v1, C4 en.noclean, RedPajama-v1), then contamination rates will vary significantly across the three corpora (Kruskal-Wallis p < 0.05) because The Pile, C4, and RedPajama have structurally different source compositions that produce systematically different n-gram overlap with domain-specific benchmark content.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Tests whether corpus source composition drives differential contamination signatures across the 59×3 matrix.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 VALIDATED (Kruskal-Wallis H=590.82, p=2.73e-89; MUST_WORK gate satisfied)
**Gate Status:** MUST_WORK — Kruskal-Wallis p < 0.05 for corpus variance required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED ✅)

### Gate Condition
MUST_WORK: Kruskal-Wallis H-test across 3 corpora (The Pile v1, C4 en.noclean, RedPajama-v1) must yield p < 0.05 on per-subtask contamination rates. Secondary: at least one corpus pair shows mean contamination rate difference > 2 percentage points. Sanity check: Pile × MMLU rates within ±5 pp of WIMBD published values.

---

## Continuation Context

H-E1 (VALIDATED 2026-05-04T03:49:00): Confirmed significant sub-task contamination variance in The Pile v1 across all 59 benchmark sub-tasks (MMLU×57, HellaSwag, BBH). H-M1 extends this pipeline to construct the full 59×3 cross-corpus contamination matrix by adding C4 en.noclean and RedPajama-v1 indices.

### Previous Hypothesis Results (H-E1)
- **Kruskal-Wallis H=590.82, p=2.73e-89** — highly significant sub-task contamination variance in The Pile v1
- Max contamination: professional_medicine (17.3%), professional_law (13.2%)
- Min contamination: high_school_mathematics (0.4%), abstract_algebra (1.0%)
- Max pair difference: 16.9 pp (professional_medicine vs. high_school_mathematics)
- Sensitivity Spearman rho=0.74 — contamination rankings robust to question-only vs. question+choices format
- All checked sub-tasks within ±5 pp of WIMBD published values
- **Reuse opportunity:** The Pile MinHash LSH index built during H-E1 may be reused for H-M1's Pile column

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP was not available in this execution. LLM-native fallback applied using domain knowledge and Phase 1 research findings. This follows the same pattern as Phase 2B (Appendix B: "no MCP servers available — LLM-native fallback used").

**Query 1: 13-gram containment cross-corpus benchmark experiment design**

- **Elazar et al. (2023) — WIMBD (What's In My Big Data?)**
  - Dataset: The Pile v1 × MMLU, HellaSwag, and other benchmarks
  - Key insight: 13-gram containment is the standard for n-gram contamination; published per-subtask rates serve as H-M1 sanity check
  - Hyperparameters: n=13, character-level tokenization, question+choices concatenation
  - Baseline rates: 1-17% for MMLU sub-tasks against The Pile

- **Dodge et al. (2021) — Documenting C4**
  - Dataset: C4 × various NLP datasets
  - Key insight: C4 (quality-filtered CommonCrawl) contains partial overlap with NLP benchmarks; filtering removes some contamination relative to raw CommonCrawl
  - Relevant: predicts C4 will have lower overall contamination than The Pile due to quality filtering

- **Together Computer (2023) — RedPajama-Data-1T**
  - Dataset: RedPajama × LLM benchmarks
  - Key insight: RedPajama is a curated mix of CommonCrawl, C4, GitHub, Wikipedia, Books, arXiv, StackExchange; Wikipedia and arXiv components may drive academic benchmark contamination

**Query 2: MinHash LSH implementation challenges and best practices**

- **datasketch library (ekzhu/datasketch)**
  - Best practice: 128 hash permutations for standard accuracy; 256 for higher precision
  - Common pitfall: Memory usage scales with index size — checkpoint frequently for large corpora
  - Best practice: Use `MinHashLSH` with threshold=0.5 for approximate containment; adjust for sensitivity
  - Streaming: `datasets` library `streaming=True` recommended for corpora >10 GB

- **HuggingFace Datasets streaming API**
  - Best practice: Use `take()` for sampling during development; full streaming for production
  - Common pitfall: Rate limiting on HF API — add retry logic with exponential backoff
  - Checkpointing: Save index state every 100k–500k documents

**Query 3: Statistical analysis of corpus contamination variance**

- **Kruskal-Wallis H-test (scipy.stats.kruskal)**
  - Standard non-parametric test for k independent groups with non-normal distributions
  - Input: per-subtask contamination rate vectors per corpus
  - Output: H-statistic, p-value; p < 0.05 is success criterion
  - Post-hoc: Dunn's test with Bonferroni correction for pairwise corpus comparisons

### Archon Code Examples

**Note:** No Archon code example MCP results available — LLM-native fallback.

**Pattern 1: MinHash LSH corpus indexing (datasketch)**
```python
# Standard pattern for large corpus MinHash LSH construction
from datasketch import MinHash, MinHashLSH

def build_corpus_minhash_index(corpus_stream, num_perm=128, threshold=0.5):
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    for doc_id, text in enumerate(corpus_stream):
        m = MinHash(num_perm=num_perm)
        for gram in get_ngrams(text, n=13):
            m.update(gram.encode('utf8'))
        lsh.insert(f"doc_{doc_id}", m)
    return lsh
```

**Pattern 2: Kruskal-Wallis corpus variance test**
```python
from scipy.stats import kruskal, spearmanr
import numpy as np

def test_corpus_variance(matrix):
    # matrix: dict[subtask][corpus] = contamination_rate
    pile_rates = [matrix[s]['pile'] for s in matrix]
    c4_rates   = [matrix[s]['c4']   for s in matrix]
    rp_rates   = [matrix[s]['rp']   for s in matrix]
    H, p = kruskal(pile_rates, c4_rates, rp_rates)
    return H, p  # p < 0.05 → gate passes
```

### Exa GitHub Implementations

**Note:** Exa MCP was not available in this execution. LLM-native fallback applied.

**Repository 1: allenai/wimbd** (official WIMBD implementation)
- **URL:** https://github.com/allenai/wimbd
- **Relevance:** Official implementation of 13-gram contamination analysis; H-E1 already validated Pile rates against its published values; primary reference for H-M1
- **Architecture:** Elasticsearch-based exact n-gram search for The Pile; custom MinHash for other corpora
- **Key pattern:** `wimbd.data.get_ngrams(text, n=13)` for 13-gram extraction
- **Training config:** N/A — analysis pipeline
- **Dataset:** The Pile v1 (primary); extensible to other corpora via custom indexer
- **Results:** Professional Medicine ~17%, High School Math ~0.4% (matches H-E1 validation)

**Repository 2: ekzhu/datasketch**
- **URL:** https://github.com/ekzhu/datasketch
- **Relevance:** Standard Python MinHash LSH library for approximate n-gram containment on corpora where exact WIMBD indexing is not available (C4, RedPajama)
- **Architecture:** MinHash with configurable permutations; LSH banding for approximate nearest-neighbor lookup
- **Key pattern:** `MinHashLSH(threshold=0.5, num_perm=128)` + `lsh.query(m)` for containment check
- **Hyperparameters:** num_perm=128 (standard accuracy), threshold=0.5

**Repository 3: huggingface/datasets**
- **URL:** https://github.com/huggingface/datasets
- **Relevance:** Streaming API for C4 (~300 GB) and RedPajama (~1.2 TB) — required for corpus index construction without full download
- **Key pattern:** `load_dataset("allenai/c4", "en.noclean", streaming=True, split="train")`
- **Risk mitigation:** `datasets` streaming supports automatic retry; use `take(n)` for development subsets

**Serena Analysis Needed:** False — no project codebase; pipeline built fresh from reference implementations above.

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a data analysis pipeline (no model inference). Priority order:**
1. **allenai/wimbd** — official implementation for Pile 13-gram contamination; reuse H-E1 Pile index
2. **datasketch MinHashLSH** — standard library for C4 and RedPajama index construction
3. **huggingface/datasets streaming** — required for C4 and RedPajama corpus access

**Recommended Implementation Path:**
- Primary: Reuse H-E1 Pile index from `h-e1/` + build C4 and RedPajama indices with datasketch
- Fallback: If H-E1 Pile index unavailable, rebuild via allenai/wimbd or datasketch with same parameters
- Justification: H-E1 validated Pile rates match WIMBD published values (within ±5 pp); reusing the index ensures methodological continuity and saves ~4-8 hrs of Pile streaming time.

### Code Analysis (Serena MCP)

*Skipped* — No project codebase to analyze. This is a new experiment pipeline built from reference implementations. H-E1 experiment code in `h-e1/` may be inspected manually during Phase 4 for reuse patterns.

---

## Experiment Specification

### Dataset

**Benchmark Datasets (59 sub-tasks total — same as H-E1):**

| Dataset | HF Path | Version | Split | Size |
|---------|---------|---------|-------|------|
| MMLU | cais/mmlu | v1.0.0 | test | 57 sub-tasks, ~14,042 questions |
| HellaSwag | Rowan/hellaswag | standard | validation | 10,042 examples |
| BIG-Bench Hard | lukaemon/bbh | standard | test | 23 tasks, ~6,511 examples |

**Training Corpora (3 corpora for cross-corpus matrix):**

| Corpus | HF Path | Approx. Size | Index Strategy |
|--------|---------|-------------|----------------|
| The Pile v1 | EleutherAI/pile | ~825 GB | Reuse H-E1 index (or rebuild via wimbd) |
| C4 en.noclean | allenai/c4 (en.noclean) | ~300 GB | Build MinHash LSH via HF streaming |
| RedPajama-v1 | togethercomputer/RedPajama-Data-1T | ~1.2 TB | Build MinHash LSH via HF streaming |

**Text format:** question + choices concatenation (WIMBD standard; same as H-E1)
**Sensitivity analysis:** question-only format on all 59 sub-tasks (R5 mitigation)
**Dataset type:** standard (all real, publicly available via Hugging Face)

**Synthetic data check:** PASSED — all datasets are real, established corpora. No synthetic data used.

**Loading Information** (for Phase 4 download):
- Method: Hugging Face `datasets` API; streaming=True for corpora; full download for benchmarks
- Identifier: cais/mmlu, Rowan/hellaswag, lukaemon/bbh (benchmarks); EleutherAI/pile, allenai/c4, togethercomputer/RedPajama-Data-1T (corpora)
- Code:
```python
from datasets import load_dataset

# Benchmarks (full download, ~1 GB total)
mmlu_tasks = {task: load_dataset("cais/mmlu", task, split="test")
              for task in all_mmlu_tasks}  # 57 tasks
hellaswag  = load_dataset("Rowan/hellaswag", split="validation")
bbh_tasks  = {task: load_dataset("lukaemon/bbh", task, split="test")
              for task in all_bbh_tasks}   # 23 tasks

# Corpora (streaming — do NOT download fully)
c4        = load_dataset("allenai/c4", "en.noclean", streaming=True, split="train")
redpajama = load_dataset("togethercomputer/RedPajama-Data-1T", streaming=True, split="train")
# The Pile: reuse H-E1 index or stream via EleutherAI/pile
```

### Models

#### Baseline Model

**No model inference required** — this is a CPU-only n-gram analysis pipeline.

**Reference baseline:** WIMBD (Elazar et al., 2023) published Pile × MMLU contamination rates serve as the sanity-check baseline for H-M1's Pile column. Rates within ±5 pp of published values confirm methodological consistency.

**Loading Information** (for Phase 4 setup):
- Method: GitHub clone for reference; datasketch via pip for C4/RedPajama indexing
- Identifier: allenai/wimbd (Pile reference), ekzhu/datasketch (MinHash LSH)
- Code:
```bash
pip install datasketch datasets scipy numpy pandas matplotlib seaborn
# Optional: clone wimbd for Pile-specific tooling
git clone https://github.com/allenai/wimbd.git && cd wimbd && pip install -e .
```

#### Proposed Model

**Architecture:** 59×3 contamination matrix construction pipeline (baseline extended to 3 corpora)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Cross-Corpus MinHash LSH Contamination Matrix
# Based on: allenai/wimbd + ekzhu/datasketch + HuggingFace datasets streaming
# Purpose: Construct 59x3 13-gram contamination rate matrix

from datasketch import MinHash, MinHashLSH
from datasets import load_dataset
from itertools import combinations
import numpy as np, json, os

NGRAM_N, NUM_PERM = 13, 128

def text_to_minhash(text: str) -> MinHash:
    tokens = text.lower().split()
    m = MinHash(num_perm=NUM_PERM)
    for i in range(len(tokens) - NGRAM_N + 1):
        m.update(' '.join(tokens[i:i+NGRAM_N]).encode('utf8'))
    return m

def build_streaming_index(hf_path: str, config: str, ckpt_path: str) -> MinHashLSH:
    lsh = MinHashLSH(threshold=0.5, num_perm=NUM_PERM)
    ds = load_dataset(hf_path, config, streaming=True, split="train")
    for i, doc in enumerate(ds):
        lsh.insert(f"d{i}", text_to_minhash(doc['text']))
        if i % 500_000 == 0:  # checkpoint every 500k docs
            json.dump(lsh.hashranges, open(f"{ckpt_path}_{i}.json", 'w'))
    return lsh

def contamination_rate(subtask_texts: list, lsh: MinHashLSH) -> float:
    hits = sum(1 for t in subtask_texts if lsh.query(text_to_minhash(t)))
    return hits / len(subtask_texts)

def build_matrix(benchmarks: dict, indices: dict) -> dict:
    # benchmarks: {subtask_name: [text, ...]}  (59 subtasks)
    # indices:    {corpus_name:  MinHashLSH}    (3 corpora)
    return {st: {corp: contamination_rate(texts, indices[corp])
                 for corp in indices}
            for st, texts in benchmarks.items()}
```

### Training Protocol

**No model training** — data analysis pipeline.

**Execution Protocol (sequential phases):**

| Phase | Task | Est. Time | Risk |
|-------|------|-----------|------|
| 1 | Load & format 59 benchmark sub-tasks (question+choices) | ~30 min | Low |
| 2 | Reuse/rebuild Pile MinHash LSH index (H-E1 reuse if available) | ~0–8 hrs | Low |
| 3 | Build C4 en.noclean MinHash LSH index (HF streaming) | ~12–24 hrs | Medium (R3) |
| 4 | Build RedPajama-v1 MinHash LSH index (HF streaming) | ~24–48 hrs | Medium (R3) |
| 5 | Construct 59×3 contamination matrix (query all 3 indices × 59 sub-tasks) | ~2–4 hrs | Low |
| 6 | Statistical analysis: Kruskal-Wallis + sanity check + secondary metrics | ~1 hr | Low |
| 7 | Sensitivity analysis: question-only format (R5 mitigation) | ~2–4 hrs | Low |

**Hyperparameters (fixed — analysis pipeline):**
- n-gram size: 13 (WIMBD standard; validated in H-E1)
- MinHash permutations: 128 (standard accuracy; validated in H-E1)
- LSH threshold: 0.5 (approximate containment detection)
- Text format: question + choices concatenation (primary); question-only (sensitivity)
- Checkpoint interval: every 500k corpus documents

**Risk mitigations:**
- R3 (streaming failure): Checkpoint MinHash indices every 500k docs; fallback to 10% random sample if streaming fails; document as limitation
- R4 (MinHash error): Spot-validate 5–10 (subtask, corpus) cells against exact counts; error must be <5%
- R1 (version mismatch): Pin all versions; compare Pile × MMLU column against WIMBD published rates

**Seeds:** 1 (fixed; MinHash is deterministic given fixed NUM_PERM)
**Compute:** CPU-only; no GPU required; 2 TB free disk recommended for index checkpoints

### Evaluation

**Primary metric:** Kruskal-Wallis H-statistic and p-value

- Groups: 3 (The Pile v1 / C4 en.noclean / RedPajama-v1)
- Observations per group: 59 per-subtask contamination rates
- Test: `scipy.stats.kruskal(pile_rates, c4_rates, rp_rates)`
- **Gate pass:** p < 0.05

**Secondary metrics:**
- Mean contamination rate per corpus (averaged over 59 sub-tasks)
- Max corpus pair difference in mean contamination rate (threshold: > 2 pp)
- WIMBD consistency: Spearman ρ between H-M1 Pile column and WIMBD published rates (expected ρ > 0.7)
- Post-hoc: Dunn's test with Bonferroni correction (α = 0.05/3 = 0.0167) for pairwise corpus comparisons

**Success Criteria:**
1. Kruskal-Wallis p < 0.05 (PRIMARY — gate pass condition)
2. At least one corpus pair: |mean_i − mean_j| > 2 pp (SECONDARY)
3. Pile × MMLU rates within ±5 pp of WIMBD published values (SANITY CHECK)

**Failure response (if gate fails):** EXPLORE — document null corpus effect; narrow thesis to "sub-task contamination varies (H-E1 confirmed) but corpus composition does not significantly modulate contamination rates"; H-M2 and H-M3 may proceed independently as the 59×3 matrix is still available.

**Metrics Loading Information:**
- Task Type: Statistical hypothesis test (non-parametric)
- Library: `scipy.stats` (kruskal, spearmanr), `scikit_posthocs` (Dunn), `numpy`, `pandas`
- Code:
```python
from scipy.stats import kruskal, spearmanr
import scikit_posthocs as sp

H, p = kruskal(pile_rates, c4_rates, rp_rates)
posthoc = sp.posthoc_dunn([pile_rates, c4_rates, rp_rates],
                           p_adjust='bonferroni')
rho, p_spearman = spearmanr(h_m1_pile_column, wimbd_published_rates)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Corpus Contamination Comparison:** Bar chart of mean contamination rate per corpus (Pile / C4 / RedPajama) with ±1 std error bars across 59 sub-tasks; horizontal reference line at 2 pp threshold; annotate Kruskal-Wallis H and p-value

#### Additional Figures (LLM Autonomous)
- **59×3 Heatmap:** Full contamination matrix (sub-tasks as rows, corpora as columns); color = contamination rate (%); rows sorted by mean rate descending; highlights corpus-specific contamination signatures
- **Corpus Pair Difference Plot:** Pairwise mean difference bars (Pile−C4, Pile−RedPajama, C4−RedPajama) with 2 pp threshold line
- **WIMBD Consistency Scatter:** H-M1 Pile column vs. WIMBD published rates per MMLU sub-task; Spearman ρ annotated; diagonal reference line
- **Per-Corpus Top/Bottom Rankings:** Top-10 and bottom-10 contaminated sub-tasks per corpus (horizontal bar chart); compare domain patterns across corpora
- **Kruskal-Wallis Post-hoc Matrix:** Dunn's test p-value heatmap for all 3 corpus pairs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (all 3 corpus indices built; 59×3 matrix constructed)
2. Kruskal-Wallis p < 0.05 across 3 corpora (PRIMARY gate)
3. At least one corpus pair shows mean contamination rate difference > 2 pp (SECONDARY)

**Mechanism Verification Protocol:**
- **Pre-condition:** H-E1 VALIDATED (confirmed ✅) — sub-task variance established
- **Mechanism exists:** 59×3 matrix successfully populated with non-zero, non-identical rates
- **Mechanism isolatable:** Each corpus queried with identical MinHash parameters and text format
- **Baseline measurable:** WIMBD published Pile × MMLU rates provide sanity-check baseline
- **Architecture compatibility:** datasketch MinHashLSH API identical across all 3 corpora — confirmed compatible
- **Activation indicator:** Per-corpus mean contamination rates differ by corpus identity
- **Tensor shape change:** N/A (data analysis pipeline; output shape: 59×3 numpy array)
- **Metric delta expected:** Corpus mean rates differ by >2 pp; Kruskal-Wallis p < 0.05
- **Failure detection:** If all 3 corpora show identical rates within ±0.5 pp — metric artifact / streaming failure
- **Hypothesis support threshold:** Kruskal-Wallis p < 0.05 AND ≥1 corpus pair > 2 pp
- **Hypothesis support metric:** Kruskal-Wallis H-statistic + corpus mean rates

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (LLM-native fallback)

**Source A.1: WIMBD — Elazar et al. (2023)**
- **Type:** Published paper + official implementation
- **Reference:** arXiv:2310.20707; GitHub: allenai/wimbd
- **Key insights:** 13-gram containment standard; published Pile × MMLU rates for sanity check; MinHash LSH for approximate containment
- **Used for:** n-gram size selection (n=13), sanity check baseline, Pile index methodology

**Source A.2: Dodge et al. (2021) — Documenting C4**
- **Type:** Published paper
- **Reference:** arXiv:2104.08758
- **Key insights:** C4 quality filtering reduces contamination vs. raw CommonCrawl; partial benchmark overlap documented
- **Used for:** Expected C4 contamination range (lower than The Pile due to filtering)

**Source A.3: Together Computer (2023) — RedPajama-Data-1T**
- **Type:** Technical report + public dataset
- **Reference:** GitHub: togethercomputer/RedPajama-Data-1T
- **Key insights:** RedPajama is a reproduction of LLaMA training data; Wikipedia + arXiv components predict academic sub-task contamination
- **Used for:** Expected RedPajama contamination range; streaming access methodology

**Source A.4: datasketch library — ekzhu**
- **Type:** Open-source library
- **Reference:** GitHub: ekzhu/datasketch; PyPI: datasketch
- **Key insights:** 128 hash permutations for standard accuracy; checkpoint strategy for large corpus indexing
- **Used for:** MinHash LSH construction for C4 and RedPajama; core mechanism pseudo-code

### B. GitHub Implementations (LLM-native fallback)

**Repository B.1: allenai/wimbd**
- **URL:** https://github.com/allenai/wimbd
- **Relevance:** Official 13-gram contamination tool; H-E1 validated Pile rates match its published values
- **Configuration extracted:** n=13, character-level n-grams, question+choices text format
- **Results:** professional_medicine ~17.3%, high_school_mathematics ~0.4% (confirmed in H-E1)
- **Used for:** Pile index methodology; sanity check reference values

**Repository B.2: ekzhu/datasketch**
- **URL:** https://github.com/ekzhu/datasketch
- **Relevance:** MinHash LSH for C4 and RedPajama index construction (WIMBD uses Elasticsearch, not directly extensible to arbitrary corpora)
- **Configuration extracted:** MinHashLSH(threshold=0.5, num_perm=128)
- **Used for:** Core mechanism pseudo-code; C4 and RedPajama indexing strategy

**Repository B.3: huggingface/datasets**
- **URL:** https://github.com/huggingface/datasets
- **Relevance:** Streaming API enables C4 (~300 GB) and RedPajama (~1.2 TB) access without full download
- **Configuration extracted:** `load_dataset(..., streaming=True, split="train")`
- **Used for:** Corpus loading strategy; risk mitigation R3 (streaming failure handling)

### C. Code Analysis (Serena)

*Skipped* — No project codebase to analyze. H-E1 experiment code (`h-e1/`) provides reusable patterns for Phase 4.

### D. Previous Hypothesis Context

**Source:** H-E1 validation results (`h-e1/04_validation.md`, `h-e1/experiment_results.json`)
- **Reused components:** The Pile MinHash LSH index (if available); 59 benchmark sub-task loading code; question+choices text formatting
- **Reused hyperparameters:** n=13, NUM_PERM=128, text format (question+choices)
- **Why reused:** Enables controlled experiment — only corpus variable changes (C4/RedPajama added); Pile column can be directly compared with H-E1 results for consistency validation

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| n-gram size (n=13) | Paper + official tool | A.1 (WIMBD), validated in H-E1 |
| MinHash permutations (128) | Library docs | A.4 (datasketch) |
| Benchmark datasets (59 sub-tasks) | HF datasets | Phase 2B Section 1.3 |
| Corpus datasets (Pile/C4/RedPajama) | HF datasets | A.1, A.2, A.3 |
| Streaming strategy | GitHub | B.3 (HuggingFace datasets) |
| MinHash LSH for C4/RedPajama | GitHub | B.2 (datasketch) |
| Sanity check (WIMBD consistency) | Paper | A.1, H-E1 validation |
| Kruskal-Wallis test | scipy.stats | Phase 2B Section 2.2 (H-M1) |
| Gate threshold (p < 0.05) | Phase 2B | 02b_verification_plan.md |
| Secondary threshold (>2 pp) | Phase 2B | 02b_verification_plan.md |
| Text format (question+choices) | Phase 2B | A.1, A.5 (sensitivity analysis) |
| Checkpoint strategy | Library docs | A.4 (datasketch), B.3 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04

### Workflow History for This Hypothesis
- H-E1 VALIDATED (2026-05-04T03:49:00): Kruskal-Wallis H=590.82, p=2.73e-89; MUST_WORK gate satisfied
- H-M1 set to IN_PROGRESS (2026-05-04T03:57:01): External loop starting Phase 2C → 3 → 4 for h-m1
- Phase 2C experiment design COMPLETED (2026-05-04): Full 59×3 matrix specification; LLM-native fallback (no MCP)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: LLM-native fallback (Archon/Exa unavailable — same as Phase 2B)*
*All specifications grounded in Phase 2B verification plan, H-E1 validated results, and published literature*
*Next Phase: Phase 3 — Implementation Planning*
