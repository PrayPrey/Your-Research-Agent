# Phase 2B Context: H-M2

**Hypothesis ID:** H-M2
**Type:** MECHANISM
**Statement:** Benchmarks testing similar error processes exhibit similar uncertainty distributions (JS-divergence < 0.15)

## Gate Condition

**Gate Type:** SHOULD_WORK
**Pass Condition:** Same-family JS-div < Cross-family (p < 0.05)
**Fail Action:** EXPLORE

## Prerequisites

- **H-M1:** COMPLETED (PASS) - Semantic entropy correlates with error processes
  - p-value: 0.000144
  - Cohen's d: 1.325
  - AUROC: 0.793

## Previous Results Summary

### H-E1 Clustering Results (Foundation)
- **Silhouette Score:** 0.8245
- **Best k:** 2 clusters
- **Cluster 1 (Factual Recall):** TriviaQA, NaturalQuestions, SQuAD
- **Cluster 2 (Entity/Claim):** PopQA, HaluEval-QA, FEVER

### H-E1 JS-Divergence Matrix
| Pair | JS-Div | Type |
|------|--------|------|
| TriviaQA-NQ | 0.056 | Within-cluster |
| TriviaQA-SQuAD | 0.041 | Within-cluster |
| NQ-SQuAD | 0.072 | Within-cluster |
| PopQA-HaluEval | 0.142 | Within-cluster |
| PopQA-FEVER | 0.139 | Within-cluster |
| HaluEval-FEVER | 0.043 | Within-cluster |
| TriviaQA-PopQA | 0.422 | Cross-cluster |
| TriviaQA-HaluEval | 0.526 | Cross-cluster |
| TriviaQA-FEVER | 0.530 | Cross-cluster |

### H-M1 Key Finding
Incorrect responses show **3x higher semantic entropy** than correct responses, validating the mechanism that uncertainty correlates with errors.

## Experimental Setup (from Phase 2A/2B)

- **Datasets:** TriviaQA, NQ, SQuAD, PopQA, HaluEval-QA, FEVER
- **Model:** Llama-2-7B-Chat
- **Generations:** 10 per query
- **Temperature:** 0.7
- **Samples per benchmark:** 1,000 queries

## H-M2 Specific Protocol

1. Use pre-computed entropy distributions from H-E1
2. Compute all 15 pairwise JS-divergences
3. Categorize pairs as same-family (intuited) vs cross-family
4. Statistical test: Mann-Whitney U for distribution difference
5. Verify same-family mean < 0.15

## Continuation Context

H-M2 directly builds on H-E1's JS-divergence matrix. The clustering showed clear separation, but H-M2 tests whether this separation aligns with *intuited* error families (factual recall vs entity/claim verification).
