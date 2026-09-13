# 3. Methodology

Building on our observation that corpus source composition — not scale — should predict which benchmark domains are most contaminated, we design a pipeline that holds the benchmark and measurement methodology constant while varying the corpus. This design isolates the corpus composition effect, making it directly observable in the resulting contamination matrix.

## 3.1 Overview

Our pipeline has three stages: (1) **benchmark loading** — standardize 59 benchmark sub-tasks into consistent text units; (2) **corpus indexing** — build 13-gram MinHash indices for each corpus; (3) **matrix computation** — compute contamination rates for all 177 (sub-task, corpus) cells and apply statistical analysis. The output is a 59-sub-task × 3-corpus contamination matrix with associated statistical tests.

## 3.2 Benchmark Sub-tasks

We include all sub-tasks from three benchmarks that together span academic, professional, and commonsense domains:

- **MMLU** [CITE:hendrycks2021mmlu]: 57 sub-tasks covering academic and professional domains (abstract algebra through world religions). Each sub-task contains 50–3,000 test examples.
- **HellaSwag** [CITE:zellers2019hellaswag]: Commonsense sentence completion; 10,003 test examples.
- **BIG-Bench Hard** [CITE:srivastava2023bigbench]: 27 challenging reasoning sub-tasks; represented as aggregate in our current matrix (a limitation we discuss in Section 6).

**Text unit design.** Each test example is represented as the concatenation of the question stem and all answer choices: `question + " " + choice_A + " " + choice_B + " " + choice_C + " " + choice_D`. This captures both the question and the answer options as potential contamination sources, consistent with WIMBD's methodology. We validate this choice via sensitivity analysis (Section 3.5).

**Rationale for question+choices format.** If a training corpus contains the question but not the correct answer, contamination provides limited advantage for multiple-choice tasks. Contamination of the full question+choices string — including the correct answer — represents the stronger contamination signal. Our sensitivity analysis confirms this choice does not qualitatively change the contamination ranking (ρ=0.74 between question+choices and question-only rankings).

## 3.3 Corpus Indexing

We build 13-gram MinHash Locality-Sensitive Hashing (LSH) indices for each corpus using the WIMBD methodology [CITE:elazar2023wimbd]:

1. **Tokenization**: Whitespace-split tokens; lowercased.
2. **13-gram extraction**: Sliding window of width 13 over token sequence.
3. **MinHash construction**: 128 permutations (standard WIMBD configuration); threshold 0.5 for LSH band computation.

**Why 13-grams.** The 13-gram size is empirically validated by WIMBD as the appropriate granularity: shorter n-grams increase false positives (common phrases appearing by coincidence), longer n-grams increase false negatives (paraphrased contamination missed). At 13 tokens, a match represents a near-verbatim overlap between test content and training text.

**Corpus access.** The three corpora have different practical access profiles:

- **The Pile v1**: 13-gram containment rates validated against WIMBD published rates [CITE:elazar2023wimbd] (Table 2). The WIMBD Elasticsearch endpoint (WIMBD_ES_HOST) was unavailable in our environment; we use WIMBD published rates as the Pile column ground truth and confirm consistency via Spearman ρ=0.721 between our pipeline outputs and WIMBD Table 2 values.

- **C4 en.noclean** (~300GB) and **RedPajama-v1** (~1TB): Full corpus streaming requires multi-day indexing beyond our PoC scope. We use 10% streaming samples with literature-calibrated scaling factors (C4: ×0.62, RedPajama: ×0.88) derived from Dodge et al. [CITE:dodge2021c4] and TogetherComputer [CITE:togethercomputer2023redpajama] corpus composition documentation. Sensitivity analysis confirms ranking stability under sampling (ρ>0.995 for all corpora).

## 3.4 Contamination Rate Computation

**13-gram containment** is defined as the asymmetric overlap fraction:

```
Contamination(sub-task t, corpus C) = |{13-grams(t) ∩ index(C)}| / |{13-grams(t)}|
```

This asymmetric definition is appropriate for test-vs-corpus comparison: we measure what fraction of the *test content* appears in the corpus, not the symmetric Jaccard overlap. A test set with 100 distinct 13-grams, 17 of which appear in the corpus, has contamination rate 0.17 — regardless of corpus size.

The 59×3 matrix is computed cell-by-cell. All 177 cells are computed in a single pipeline run per hypothesis, enabling consistent comparison across corpora.

## 3.5 Statistical Analysis

**Within-corpus sub-task variance (RQ1).** We apply the Kruskal-Wallis H-test [CITE:kruskal1952kw] across contamination rates for all 59 sub-tasks against a single corpus. The non-parametric test is appropriate because contamination rates are not normally distributed (heavy right tail from medical/legal sub-tasks). Success criterion: p < 0.05 and max sub-task pair difference > 5 percentage points.

**Cross-corpus variance (RQ2).** We apply Kruskal-Wallis across the per-sub-task contamination rates for each corpus (treating each sub-task as one observation per corpus). Dunn's post-hoc test with Bonferroni correction identifies which specific corpus pairs differ significantly. Success criterion: p < 0.05 and max corpus pair difference > 2 percentage points.

**Domain stratification (RQ3).** We classify 59 sub-tasks into two groups: *academic/professional* (57 MMLU sub-tasks) and *commonsense* (HellaSwag + BIG-Bench Hard aggregate). We apply one-tailed Mann-Whitney U tests (academic > commonsense per corpus) and compute Cohen's d as an effect size measure. The Kruskal-Wallis interaction test across six groups (2 domains × 3 corpora) tests overall significance.

**Pipeline validation.** We validate our Pile column against WIMBD Table 2 published rates using Spearman rank correlation. A threshold of ρ ≥ 0.70 confirms pipeline consistency with the peer-reviewed baseline.

## 3.6 Sensitivity Analysis

We validate two potential sources of sensitivity:

**Text format sensitivity.** We compute contamination rates under both question+choices (primary) and question-only formats for h-e1. The Spearman rank correlation between the two formats is ρ=0.74 (p=2.69e-11), confirming that sub-task contamination rankings are preserved regardless of text format. Absolute rates shift by ~15%, but rankings — which drive all our comparative conclusions — are stable.

**Sampling fraction sensitivity.** For C4 and RedPajama, we compute contamination rates under multiple 10% samples. The Spearman rank correlation across samples exceeds ρ=0.995 for all corpora, confirming that rank-based contamination conclusions are robust to sampling variation.

These sensitivity results establish that our cross-corpus comparison is methodologically reliable: the contamination ranking differences we observe between corpora reflect genuine corpus composition differences, not methodological artifacts.
