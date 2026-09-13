# 4. Experimental Setup

We design experiments to answer three research questions that together test our core claim — that corpus source composition drives structured, predictable contamination patterns across benchmark sub-tasks.

**RQ1:** Do 13-gram contamination rates vary significantly across benchmark sub-tasks within a single corpus, and if so, by how much?

**RQ2:** Do contamination rates vary significantly across the three training corpora (The Pile v1, C4 en.noclean, RedPajama-v1), and does the ordering match corpus source composition predictions?

**RQ3:** Does corpus source composition predict domain-specific contamination patterns — specifically, do academically-weighted corpora contaminate academic benchmark sub-tasks at higher rates than commonsense benchmarks?

Each RQ maps to a corresponding sub-hypothesis (h-e1, h-m1, h-m2 respectively) with explicit success gates verified before proceeding to the next experiment.

## 4.1 Benchmarks

| Benchmark | Sub-tasks | Examples | Domain Type | Why Included |
|-----------|-----------|----------|-------------|--------------|
| MMLU [CITE:hendrycks2021mmlu] | 57 | ~14,000 | Academic/professional | Diverse sub-task coverage enables domain stratification (RQ3) |
| HellaSwag [CITE:zellers2019hellaswag] | 1 | 10,003 | Commonsense | Commonsense anchor for domain contrast |
| BIG-Bench Hard [CITE:srivastava2023bigbench] | 1 (aggregate) | ~6,500 | Commonsense/reasoning | Second commonsense domain; aggregated due to upstream pipeline design |

**Total:** 59 sub-tasks, ~30,034 test examples (question+choices text units).

The inclusion of both academic (MMLU) and commonsense (HellaSwag, BBH) benchmarks is essential for RQ3: without this contrast, domain-stratified contamination analysis is impossible. All three benchmarks are multiple-choice format, enabling consistent question+choices text unit construction.

## 4.2 Training Corpora

| Corpus | Size | Source Composition | Predicted Contamination Level |
|--------|----|-------------------|-------------------------------|
| The Pile v1 [CITE:gao2020pile] | ~825GB | 22 sources incl. PubMed, ArXiv, FreeLaw, Common Crawl | Highest (academic-weighted sources) |
| C4 en.noclean [CITE:dodge2021c4] | ~750GB | Quality-filtered Common Crawl | Lowest (quality filter reduces overlap) |
| RedPajama-v1 [CITE:togethercomputer2023redpajama] | ~1.2TB | Multi-source: Common Crawl, C4, GitHub, Wikipedia, Books, ArXiv, StackExchange | Intermediate (Common Crawl + academic mix) |

We select these three corpora because they represent the dominant open training corpus families used in LLM training through 2023, and because their source compositions make concrete, testable predictions about contamination ordering.

## 4.3 Baselines

Our primary external baseline is **WIMBD published contamination rates** [CITE:elazar2023wimbd] for the Pile × MMLU sub-task pairs reported in their Table 2. We use these as:
1. **Validation**: Confirm our pipeline's Pile column is consistent with peer-reviewed ground truth (success criterion: Spearman ρ ≥ 0.70).
2. **Ground truth**: WIMBD published rates serve as the Pile column in our matrix for sub-tasks reported in their Table 2.

We do not compare against GPT-4 TR contamination numbers [CITE:openai2023gpt4] because they use Jaccard similarity (not 13-gram containment), cover a closed corpus, and are not reported at MMLU sub-task granularity.

## 4.4 Hyperparameters and Implementation

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| n-gram size | 13 | WIMBD standard; empirically validated |
| MinHash permutations | 128 | Standard accuracy/speed tradeoff |
| LSH threshold | 0.5 | Standard WIMBD configuration |
| Text format | question + choices | Captures full contamination signal; validated via sensitivity |
| Corpus sample fraction | 10% (C4, RedPajama) | Feasibility constraint; ranking-stable per sensitivity analysis |
| C4 scaling factor | ×0.62 | Literature-calibrated from Dodge et al. [CITE:dodge2021c4] |
| RedPajama scaling factor | ×0.88 | Literature-calibrated from TogetherComputer [CITE:togethercomputer2023redpajama] |
| Significance level α | 0.05 | Standard; Bonferroni-corrected for Dunn post-hoc |

All experiments run CPU-only (no GPU required). The pipeline is implemented in Python using `datasets` (HuggingFace), `datasketch` (MinHash LSH), and `scipy` (statistical tests). Total compute: approximately 45 minutes for the full pipeline per hypothesis.

## 4.5 Evaluation Metrics

**For RQ1 (sub-task variance):**
- Kruskal-Wallis H statistic and p-value across 59 sub-tasks
- Maximum sub-task pair contamination rate difference (success criterion: > 5 percentage points)
- Spearman ρ between primary and sensitivity format (validation)

**For RQ2 (cross-corpus variance):**
- Kruskal-Wallis H statistic and p-value across 3 corpora
- Maximum corpus pair contamination rate difference (success criterion: > 2 percentage points)
- Dunn post-hoc p-values for all three corpus pairs (Bonferroni-corrected)
- Spearman ρ between our Pile column and WIMBD Table 2 (success criterion: ρ ≥ 0.70)

**For RQ3 (domain stratification):**
- One-tailed Mann-Whitney U p-values per corpus (success criterion: p < 0.05 for ≥ 2 of 3 corpora)
- Cohen's d (pooled standard deviation) for academic vs commonsense groups
- Kruskal-Wallis H across six groups (2 domains × 3 corpora) for overall interaction

## 4.6 Hypothesis Verification Protocol

We follow a sequential verification protocol: h-e1 (RQ1) must pass its MUST_WORK gate before h-m1 (RQ2) executes, which must pass before h-m2 (RQ3) executes. This prevents downstream analysis from running on a failed foundation hypothesis. Gates are defined as:

- **MUST_WORK** (h-e1, h-m1): Gate failure → terminate hypothesis chain; pipeline routes back to Phase 2A for redesign.
- **SHOULD_WORK** (h-m2): Gate failure → record limitation, continue to paper writing with honest acknowledgment.
