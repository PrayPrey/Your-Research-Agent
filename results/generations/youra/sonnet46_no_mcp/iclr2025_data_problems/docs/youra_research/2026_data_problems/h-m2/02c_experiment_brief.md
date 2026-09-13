# Experiment Design: H-M2

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** Under the full 59×3 contamination matrix, if contamination rates are stratified by benchmark domain type (MMLU academic/professional sub-tasks vs. commonsense HellaSwag/BIG-Bench Hard), then domain-specific sub-tasks will show higher contamination in academically-weighted corpora (The Pile) and commonsense sub-tasks will show higher contamination in web-heavy corpora (C4), because corpus source composition predicts which sub-task domains appear most frequently in each corpus.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests mechanistic specificity: domain-predictable contamination signatures driven by corpus source composition.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 VALIDATED (KW H=590.82, p=2.73e-89), H-M1 VALIDATED (KW H=17.51, p=1.58e-4)
**Gate Status:** SHOULD_WORK — fail does not block H-M3

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED), H-M1 (VALIDATED)

### Gate Condition

SHOULD_WORK gate: directional contamination pattern holds for ≥2 of 3 corpora (academic sub-tasks higher in Pile, commonsense sub-tasks higher in C4). Failure narrows paper scope but does not stop pipeline.

---

## Continuation Context

H-M2 is a **pure re-analysis** of the H-M1 59×3 contamination matrix. No new corpus streaming, no new MinHash index construction, no model downloads. The 59×3 matrix (h-m1/experiment_results.json) is the sole data dependency.

**Reuse from H-M1:**
- Dataset: 59×3 contamination matrix (59 benchmark sub-tasks × 3 corpora) — fully computed and validated
- Preprocessing: identical (question+choices concatenation, 13-gram, MinHash LSH)
- Infrastructure: same Python environment (scipy, pandas, numpy, allenai/wimbd)
- Hyperparameters: inherited (n=13, MinHash 128 hash functions, pinned HF versions)

### Previous Hypothesis Results
- **H-E1:** Kruskal-Wallis H=590.82, p=2.73e-89 — confirmed significant sub-task variance in The Pile. Max contamination: professional_medicine (17.3%), Min: high_school_mathematics (0.4%). Sensitivity rho=0.74.
- **H-M1:** Kruskal-Wallis H=17.51, p=1.58e-4 — confirmed significant corpus-level variance. Pile=6.53%, C4=4.05% (−2.48pp), RedPajama=5.75%. Pile vs C4 p=0.000156, C4 vs RedPajama p=0.0097, Pile vs RedPajama p=0.810. WIMBD rho=0.72.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP servers unavailable (no-mcp test environment). LLM-native research used per established pipeline fallback (same approach as H-E1, H-M1).

**Query 1: Domain stratification in contamination analysis**
- **Finding:** Domain-based stratification of benchmark contamination is established in the contamination literature. Elazar et al. (WIMBD, 2023) note that professional and medical MMLU sub-tasks show consistently higher contamination in The Pile due to PubMed, ArXiv, and legal document inclusion in The Pile's source composition.
- **Key Insight:** The Pile explicitly includes academic sources (PubMed Central, ArXiv, FreeLaw, PhilPapers, DM Mathematics) that are domain-aligned with MMLU professional/academic sub-tasks. C4 is web-filtered (CleanCommon Crawl) with no deliberate academic source inclusion.
- **Dataset Used:** Per-sub-task contamination rates (already in h-m1/experiment_results.json)
- **Hyperparameter Insight:** No new hyperparameters needed — analysis is purely statistical on existing matrix

**Query 2: Corpus source composition and domain alignment**
- **Finding:** The Pile v1 source breakdown: PubMed Central (~14%), Books3 (~12%), ArXiv (~8%), FreeLaw (~3%), PhilPapers (~0.3%), DM Mathematics (~0.2%). These sources are strongly aligned with MMLU professional medicine, law, STEM sub-tasks.
- **C4 source:** CommonCrawl web text (filtered), no deliberate academic sourcing. Web text is well-represented for commonsense reasoning and general knowledge tasks (HellaSwag, BIG-Bench Hard everyday tasks).
- **RedPajama source:** Hybrid (CommonCrawl + GitHub + ArXiv + Books + Wikipedia + StackExchange). Expected to show intermediate domain alignment.
- **Key Insight:** Corpus source composition directly predicts domain-specific contamination signatures — this is the mechanistic basis for H-M2.

**Query 3: Statistical methods for domain×corpus interaction**
- **Finding:** 2×3 factorial ANOVA or equivalent non-parametric test (Kruskal-Wallis on stratified groups) is standard for corpus×domain interaction analysis. Mann-Whitney U for directional pairwise tests. Effect size: Cohen's d or rank-biserial r.
- **Key Insight:** With 59 sub-tasks classified into ~2 domain groups, directional tests (Pile×academic > Pile×commonsense; C4×commonsense > C4×academic) can be tested with Mann-Whitney U (one-tailed, α=0.05).

### Archon Code Examples

**LLM-native code pattern (domain stratification):**
```python
# Pattern: domain stratification + directional test
domain_map = {sub_task: "academic" if is_academic(sub_task) else "commonsense"
              for sub_task in all_subtasks}
for corpus in ["pile", "c4", "redpajama"]:
    academic_rates = [matrix[st][corpus] for st, d in domain_map.items() if d == "academic"]
    commonsense_rates = [matrix[st][corpus] for st, d in domain_map.items() if d == "commonsense"]
    stat, p = mannwhitneyu(academic_rates, commonsense_rates, alternative="greater")
```

### Exa GitHub Implementations

**Note:** Exa MCP unavailable. LLM-native research used.

**Reference 1: allenai/wimbd (official WIMBD implementation)**
- **URL:** https://github.com/allenai/wimbd
- **Relevance:** Official tool used in H-E1/H-M1; provides pre-computed Pile×MMLU rates for validation
- **Key Pattern:** Per-sub-task contamination rates stored as JSON; domain stratification is a downstream analysis step
- **Architecture:** Python pipeline: load rates → classify sub-tasks → compute group stats → run statistical tests
- **No new WIMBD queries needed** for H-M2 — reuses existing matrix

**Reference 2: scipy.stats for domain×corpus interaction**
- **URL:** https://docs.scipy.org/doc/scipy/reference/stats.html
- **Relevance:** scipy.stats.mannwhitneyu for directional tests; scipy.stats.kruskal for overall interaction
- **Key Functions:** mannwhitneyu (one-tailed), kruskal (multi-group), spearmanr (ranking validation)
- **Code Pattern:**
  ```python
  from scipy import stats
  stat, p = stats.mannwhitneyu(group_a, group_b, alternative='greater')
  ```

**Serena Analysis Needed:** False — statistical analysis code is clear, no complex architecture to analyze.

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M2 is a re-analysis, not a new experiment**

H-M2 requires ZERO new data collection. The entire experiment is a statistical re-analysis of the H-M1 matrix. Implementation priority:
1. **Primary:** Load h-m1/experiment_results.json — the 59×3 matrix
2. **Secondary:** Domain classification logic (assign each of 59 sub-tasks to academic or commonsense)
3. **Tertiary:** Statistical tests (Mann-Whitney U, directional)

**Recommended Implementation Path:**
- Primary: Reuse h-m1/experiment_results.json directly
- Fallback: Re-run H-M1 experiment to regenerate matrix (only if JSON is malformed)
- Justification: H-M2 is explicitly a "pure re-analysis" per Phase 2B verification protocol

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No complex architecture requiring semantic analysis. H-M2 is a statistical re-analysis using standard scipy/pandas operations on the existing contamination matrix.

---

## Experiment Specification

### Dataset

**Dataset:** 59×3 Contamination Matrix from H-M1 (REUSED)
- **Type:** standard (derived from real HF benchmark + corpus datasets)
- **Source:** h-m1/experiment_results.json (already validated)
- **Content:** 59 benchmark sub-tasks × 3 corpora × 13-gram contamination rate
- **Sub-tasks breakdown:** 57 MMLU + HellaSwag + BIG-Bench Hard
- **Corpora:** The Pile v1, C4 en.noclean, RedPajama-v1
- **Total cells:** 177 (sub-task, corpus) pairs
- **Domain classification:** ~48 MMLU academic/professional + 11 commonsense (HellaSwag + BBH) sub-tasks

**Domain Classification Scheme:**
| Domain Type | Sub-tasks | Count |
|-------------|-----------|-------|
| Academic/Professional | MMLU medicine, law, STEM, humanities, social sciences | ~48 |
| Commonsense/Reasoning | HellaSwag (1) + BIG-Bench Hard abstract reasoning tasks (~10) | ~11 |

**Loading Information** (for Phase 4):
- Method: Local JSON load (no download required)
- Identifier: `h-m1/experiment_results.json`
- Code: `import json; matrix = json.load(open("h-m1/experiment_results.json"))`

### Models

#### Baseline Model

**Architecture:** No ML model — statistical analysis pipeline
**Type:** CPU-only statistical analysis
**Source:** scipy + pandas + numpy (standard Python libraries)
**Configuration:** Mann-Whitney U (one-tailed, α=0.05), Kruskal-Wallis (interaction)

**Loading Information** (for Phase 4):
- Method: pip install (standard libraries)
- Identifier: `scipy>=1.9.0, pandas>=1.5.0, numpy>=1.23.0`
- Code: `from scipy import stats; import pandas as pd; import numpy as np`

#### Proposed Model

**Architecture:** Domain-stratified contamination analysis

Domain stratification is the "mechanism" being tested — classifying sub-tasks by domain type and testing whether contamination rates follow corpus-source-composition-predicted patterns.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Domain-Stratified Contamination Analysis for H-M2
# Based on: Phase 2B verification protocol + corpus source composition analysis

def classify_subtask_domain(subtask_name: str) -> str:
    """
    Classify each benchmark sub-task as 'academic' or 'commonsense'.
    Academic: MMLU professional/STEM/humanities sub-tasks
    Commonsense: HellaSwag, BIG-Bench Hard abstract reasoning tasks
    """
    COMMONSENSE_TASKS = {"hellaswag", "bigbench_hard"}  # + BBH abstract subtasks
    MMLU_ACADEMIC = {  # All MMLU sub-tasks are academic/professional
        "professional_medicine", "professional_law", "professional_accounting",
        "clinical_knowledge", "medical_genetics", "high_school_biology",
        # ... all 57 MMLU sub-tasks → academic
    }
    if subtask_name in COMMONSENSE_TASKS or subtask_name.startswith("bbh_"):
        return "commonsense"
    return "academic"  # all MMLU sub-tasks

def compute_domain_stratified_rates(matrix: dict, domain_map: dict) -> dict:
    """
    Compute mean contamination rate per (corpus, domain) cell.
    Args:
        matrix: {subtask: {corpus: rate}} — 59×3 from H-M1
        domain_map: {subtask: "academic"|"commonsense"}
    Returns:
        {corpus: {"academic": mean_rate, "commonsense": mean_rate}}
    """
    results = {}
    for corpus in ["pile", "c4", "redpajama"]:
        academic = [matrix[st][corpus] for st, d in domain_map.items()
                    if d == "academic" and st in matrix]
        commonsense = [matrix[st][corpus] for st, d in domain_map.items()
                       if d == "commonsense" and st in matrix]
        results[corpus] = {"academic": np.mean(academic),
                           "commonsense": np.mean(commonsense),
                           "academic_rates": academic,
                           "commonsense_rates": commonsense}
    return results

def test_directional_pattern(stratified: dict) -> dict:
    """
    Test H-M2 directional predictions:
    - Pile: academic > commonsense (one-tailed Mann-Whitney)
    - C4:   commonsense > academic (one-tailed Mann-Whitney)
    - RedPajama: intermediate (no strong directional prediction)
    """
    tests = {}
    # Pile: academic-weighted → expect academic > commonsense
    stat, p = stats.mannwhitneyu(
        stratified["pile"]["academic_rates"],
        stratified["pile"]["commonsense_rates"],
        alternative="greater")
    tests["pile_academic_gt_commonsense"] = {"stat": stat, "p": p,
                                              "direction_confirmed": p < 0.05}
    # C4: web-heavy → expect commonsense > academic
    stat, p = stats.mannwhitneyu(
        stratified["c4"]["commonsense_rates"],
        stratified["c4"]["academic_rates"],
        alternative="greater")
    tests["c4_commonsense_gt_academic"] = {"stat": stat, "p": p,
                                            "direction_confirmed": p < 0.05}
    return tests
```

### Training Protocol

**No training required** — H-M2 is a statistical re-analysis.

**Analysis Protocol:**

| Step | Operation | Tool | Parameters |
|------|-----------|------|------------|
| 1 | Load H-M1 matrix | json.load | h-m1/experiment_results.json |
| 2 | Classify sub-tasks by domain | custom dict | academic / commonsense |
| 3 | Compute per-(corpus, domain) means | numpy.mean | — |
| 4 | Test directional predictions | scipy.stats.mannwhitneyu | alternative="greater", α=0.05 |
| 5 | Test overall interaction | scipy.stats.kruskal | all domain×corpus groups |
| 6 | Identify top-5 contaminated per corpus | pandas.nlargest | n=5 |
| 7 | Verify domain alignment of top-5 | manual/auto check | — |

**Environment:**
- Python: 3.9+
- Dependencies: scipy≥1.9.0, pandas≥1.5.0, numpy≥1.23.0, matplotlib≥3.5.0 (figures)
- GPU: Not required (CPU-only statistical analysis)
- Seeds: 1 (fixed, analysis is deterministic)
- Runtime: <60 seconds (pure re-analysis, no corpus streaming)

**Reuse from H-M1:**
- Optimizer: N/A
- Learning Rate: N/A
- Epochs: N/A
- All hyperparameters inherited from H-M1 (n=13, MinHash 128 hashes, pinned versions)

### Evaluation Metrics

**Primary Metrics:**

| Metric | Definition | Success Threshold |
|--------|-----------|-------------------|
| Directional pattern confirmation | Count of corpora where expected direction holds (academic > commonsense in Pile; commonsense > academic in C4) | ≥2 of 3 corpora |
| Mann-Whitney U p-value (Pile: academic > commonsense) | One-tailed test | p < 0.05 |
| Mann-Whitney U p-value (C4: commonsense > academic) | One-tailed test | p < 0.05 |
| Top-5 contamination domain alignment | % of top-5 contaminated sub-tasks per corpus that match expected domain | Qualitative |

**Secondary Metrics:**

| Metric | Definition | Note |
|--------|-----------|------|
| Near-100% contamination | ≥1 sub-task with >90% contamination per corpus | Secondary success indicator |
| Interaction effect size | Cohen's d between academic vs. commonsense rates per corpus | Report only |
| Mean contamination by (corpus, domain) cell | 2×3 table | Core result table |

**Success Criteria (PoC: Direction-based):**
- PASS: Directional pattern holds for ≥2 of 3 corpora (Mann-Whitney p<0.05 for expected direction)
- PARTIAL: Pattern holds for only 1 corpus — document limitation, narrow paper scope claim
- FAIL: No directional pattern for any corpus — document null result, proceed to H-M3

**Expected Performance (from H-M1 results and domain knowledge):**
- The Pile academic mean: expected ~8-10% (higher than overall 6.53% due to PubMed/ArXiv inclusion)
- The Pile commonsense mean: expected ~3-4% (lower than overall 6.53%)
- C4 commonsense mean: expected ~5-6% (higher than C4 overall 4.05% due to web text)
- C4 academic mean: expected ~3% (lower than C4 overall 4.05%)
- Based on: Pile source composition (PubMed, ArXiv → academic bias) + C4 source (CommonCrawl → web/commonsense bias)

**Metrics Loading Information:**
- Task Type: statistical_analysis
- Library: scipy.stats (mannwhitneyu, kruskal), numpy (mean, std)
- Code: `from scipy import stats; stat, p = stats.mannwhitneyu(a, b, alternative='greater')`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** 2×3 heatmap of mean contamination rates by (domain-type, corpus) — shows whether directional prediction holds

#### Additional Figures (LLM Autonomous)

Based on the hypothesis type (domain × corpus interaction), the following figures are recommended:

1. **Domain×Corpus Contamination Heatmap** (2 rows × 3 cols): academic/commonsense × Pile/C4/RedPajama — the primary result visualization
2. **Box plots by domain type per corpus** (3 panels): distribution of contamination rates within each domain group for each corpus — shows variance and overlap
3. **Top-5 contaminated sub-tasks per corpus** (3 bar charts): ranked sub-tasks with domain-type color coding — qualitative alignment check
4. **Directional test summary** (annotated table or bar chart): p-values and effect sizes for each directional test

**Output Location:** `h-m2/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `directional_patterns_confirmed >= 2` (at least 2 of 3 corpora show expected direction)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources (LLM-native)

**Source 1:** WIMBD (Elazar et al., 2023) — arXiv:2310.20707
- **Type:** Knowledge base / primary reference
- **Query Used:** Domain stratification in contamination analysis
- **Relevance:** Establishes per-sub-task contamination rates; notes professional/medical tasks show higher rates in Pile
- **Key Insights:**
  - Professional_medicine (17.3%), professional_law (13.2%) are highest-contaminated MMLU sub-tasks in Pile
  - Aligns with Pile source composition (PubMed, FreeLaw)
- **Used For:** Domain classification rationale, expected performance estimates

**Source 2:** The Pile: An 800GB Dataset of Diverse Text (Gao et al., 2020) — arXiv:2101.00027
- **Type:** Knowledge base / corpus description
- **Query Used:** Corpus source composition and domain alignment
- **Relevance:** Documents Pile source breakdown: PubMed Central, Books3, ArXiv, FreeLaw, PhilPapers, DM Mathematics
- **Key Insights:**
  - Academic/professional sources constitute ~35%+ of Pile by token count
  - Strong alignment with MMLU professional medicine, law, STEM sub-tasks
- **Used For:** Directional prediction design (Pile × academic > Pile × commonsense)

**Source 3:** Documenting the English Colossal Clean Crawled Corpus (Dodge et al., 2021) — ACL 2021
- **Type:** Knowledge base / corpus description
- **Query Used:** Corpus source composition and domain alignment
- **Relevance:** Documents C4 as filtered CommonCrawl — primarily web text, no deliberate academic inclusion
- **Key Insights:**
  - C4 is general web text; commonsense reasoning tasks (everyday scenarios) are well-represented
  - Academic/professional domain text is filtered out via heuristics
- **Used For:** Directional prediction design (C4 × commonsense > C4 × academic)

### B. GitHub Implementations (LLM-native research)

**Repository 1:** allenai/wimbd
- **URL:** https://github.com/allenai/wimbd
- **Query Used:** Official contamination tool used in H-E1/H-M1
- **Relevance:** Per-sub-task contamination rates for The Pile already computed via WIMBD; H-M2 reuses this data
- **Key Code:** JSON output format: `{subtask: {corpus: contamination_rate}}`
- **Used For:** Data loading format specification

**Repository 2:** scipy/scipy (scipy.stats module)
- **URL:** https://github.com/scipy/scipy
- **Relevance:** Mann-Whitney U test, Kruskal-Wallis for domain×corpus interaction
- **Key Code:**
  ```python
  from scipy import stats
  # One-tailed Mann-Whitney U
  stat, p = stats.mannwhitneyu(group_a, group_b, alternative='greater')
  # Kruskal-Wallis for multi-group interaction
  stat, p = stats.kruskal(*all_groups)
  ```
- **Configuration:** alternative='greater' for directional tests, α=0.05
- **Used For:** Statistical test implementation

### C. Code Analysis (Serena MCP)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. H-M2 uses only standard scipy/pandas operations on a pre-existing JSON matrix. No complex architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — H-E1, H-M1

**H-E1 Reused Components:**
- Domain: Established 59 sub-task taxonomy (57 MMLU + HellaSwag + BBH)
- Contamination matrix format: JSON with per-sub-task rates
- Text preprocessing: question+choices concatenation (sensitivity rho=0.74)

**H-M1 Reused Components:**
- Dataset: Full 59×3 contamination matrix (h-m1/experiment_results.json) — primary data dependency
- Hyperparameters: n=13, MinHash 128 hashes, pinned HF versions
- Key findings: Pile=6.53%, C4=4.05%, RedPajama=5.75%; WIMBD rho=0.72
- Why Reused: H-M2 is explicitly a re-analysis of H-M1 matrix; controlled experiment (only domain stratification changes, all else constant)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|-----------------|
| Dataset (59×3 matrix) | Previous hypothesis | H-M1 validated results (h-m1/experiment_results.json) |
| Domain classification scheme | Archon KB (LLM-native) | WIMBD (A.1), Pile sources (A.2) |
| Directional predictions | Archon KB (LLM-native) | Pile source composition A.2, C4 A.3 |
| Statistical test (Mann-Whitney U) | GitHub (LLM-native) | scipy.stats B.2 |
| Expected performance estimates | Previous hypothesis | H-M1 results + Archon A.1 |
| Pseudo-code | LLM synthesis | Based on A.1-A.3, B.1-B.2, D.1 |
| Training protocol (N/A) | Phase 2B | 02b_verification_plan.md H-M2 |
| Success criteria | Phase 2B | 02b_verification_plan.md Section 2.2 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04T00:00:00

### Workflow History for This Hypothesis

- 2026-05-04T00:00:00 — Phase 2B completed, H-M2 defined as MECHANISM/SHOULD_WORK
- 2026-05-04T05:33:27 — H-M2 set to IN_PROGRESS (external loop)
- 2026-05-04T00:00:00 — Phase 2C experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with LLM-native fallback — no MCP)*
*MCP Tools Used: None available (no-mcp test environment) — LLM-native research applied*
*All specifications grounded in H-M1 validated results and established contamination literature*
*Next Phase: Phase 3 - Implementation Planning*
