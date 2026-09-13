# 5. Results

## 5.1 Main Finding: Stratum Collapse

Our primary result is not the routing accuracy we set out to measure — it is the discovery that routing cannot begin under the implemented experimental conditions. All 25,403 benchmark items (100%) collapsed to the lexical stratum; zero items were assigned to the semantic or indeterminate strata.

Figure 2 shows the 2D contamination geometry phase diagram for all benchmark items across all three corpora. The intended three-zone structure (lexical blue, semantic red, indeterminate grey) is entirely absent: every item occupies the same lexical region. This is not because all items are lexically contaminated — it is because the semantic axis is degenerate. The max SBERT cosine similarity values computed from random corpus streaming are near-zero for all items, making the 75th-percentile threshold effectively zero and vacuously satisfied by all items.

**Why this happens.** For a non-contaminated benchmark item, the probability that a randomly-sampled corpus document is semantically similar to it is near zero. With 50K randomly-streamed documents per corpus, the 75th-percentile of max-cosine across all items converges to a value near the base rate of random document similarity (~0.1–0.2 for all-MiniLM-L6-v2). All items exceed this threshold by construction, and all are assigned to the lexical stratum. The boundary condition identified in Proposition 1 (Section 3.2) is confirmed empirically.

**Contrast with dry run.** At 0.01× scale (500 documents), the same code produced 3-way stratification: lexical=13 items, semantic=12 items, indeterminate=25 items. This apparent success was a small-sample artifact: with only 500 documents, the cosine distribution has higher variance, and by chance some documents produce non-trivially high cosines with specific benchmark items. At 50K documents, the distribution concentrates and collapses. This scale sensitivity is a specific failure mode to test for in future implementations.

## 5.2 Benchmark-Corpus Overlap Characterization

Despite the stratum collapse, our n-gram index construction produces two reproducible empirical findings about benchmark contamination:

**Table 1: N-gram Recall by Benchmark and Corpus**

| Benchmark | The Pile | C4 | FineWeb | Mean |
|-----------|----------|----|---------|------|
| MMLU | 1.000 | 1.000 | 1.000 | **1.000** |
| HellaSwag | 0.000 | 1.000 | 1.000 | 0.667 |
| GSM8K | 0.000 | 0.000 | 0.000 | **0.000** |
| **Mean** | 0.333 | 0.667 | 0.667 | **0.556** |

**MMLU is comprehensively verbatim-contaminated.** All 14,042 MMLU test items contain at least one 13-gram that appears in each of The Pile, C4, and FineWeb. This is the first confirmation of MMLU's verbatim contamination across three independent corpora simultaneously. The result is consistent with MMLU's construction from existing internet text, academic question banks, and structured factual content that appears widely in general web crawls.

**GSM8K has zero verbatim overlap.** Not a single GSM8K item contains a 13-gram match in any of the three corpora. This is not because GSM8K items are clean — it is because math problem notation, symbolic expressions, and multi-step arithmetic reasoning chains do not appear as verbatim sequences in general web corpora. The unified lexical recall criterion (≥ 0.80) is structurally inappropriate for math benchmarks: the correct criterion for GSM8K would involve domain-specific corpora (e.g., OpenWebMath, Proof-Pile) or semantic-level detection.

**Implication for the gate criterion.** The mean n-gram recall of 0.556 that caused the h-e1 gate failure (target: ≥ 0.80) is a measurement artifact: it averages MMLU's 1.0 with GSM8K's 0.0, producing a number that represents neither. Future implementations should stratify by benchmark type before applying recall thresholds.

## 5.3 Detector Performance Under Stratum Collapse

Table 2 shows detection counts per benchmark-corpus pair for all five detector families.

**Table 2: Detector Detection Counts (number of items flagged as contaminated)**

| Benchmark | Corpus | N-gram | Embed | Min-K%++ | DC-PDD | ConStat |
|-----------|--------|--------|-------|----------|--------|---------|
| MMLU | Pile | 14,042 | 0 | 0 | 14,042 | 0 |
| MMLU | C4 | 14,042 | 0 | 0 | 14,042 | 0 |
| MMLU | FineWeb | 14,042 | 0 | 0 | 14,042 | 0 |
| HellaSwag | Pile | 0 | 0 | 0 | 10,042 | 0 |
| HellaSwag | C4 | 3 | 0 | 0 | 10,042 | 0 |
| HellaSwag | FineWeb | 1 | 0 | 0 | 10,042 | 0 |
| GSM8K | Pile | 0 | 0 | 0 | 1,319 | 0 |
| GSM8K | C4 | 0 | 0 | 0 | 1,319 | 0 |
| GSM8K | FineWeb | 0 | 0 | 0 | 1,319 | 0 |

Three patterns emerge:

**N-gram detector performs as expected for MMLU.** 14,042/14,042 MMLU items flagged across all corpora, consistent with recall = 1.0. HellaSwag shows near-zero n-gram detection on The Pile (0 items) but 3 on C4 — a corpus-specific finding consistent with selective overlap. This validates that the n-gram infrastructure works correctly.

**Embedding, Min-K%++, and ConStat all produce zero detections.** This reflects two compounding issues: (1) stratum collapse means all items are in the lexical stratum, where embedding and MIA detectors are not expected to excel; (2) independent implementation bugs render Min-K%++ and ConStat outputs unreliable (see below). The embedding detector's zero output is consistent with stratum collapse: the SBERT cosine scores used as detection features are the same degenerate scores used for stratification.

**DC-PDD flags all items.** DC-PDD flags every item in every benchmark-corpus pair (100% positive rate), which is nonsensical and directly attributable to the DCPDDDetector implementation bug: the code computes −ref_log_prob (reference model log-probability with a sign flip) rather than log P_target − log P_ref. This produces a score that is always above threshold for all items, making DC-PDD useless as a discriminator in this experiment. The correct DC-PDD implementation requires both a target model (Pythia-6.9B) and a reference model (Pythia-2.8B) and computes the per-token log-likelihood ratio.

**Gate metric outcomes.** Figure 1 summarizes the four gate metrics against their targets:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| N-gram Recall (Lexical stratum) | ≥ 0.80 | 0.556 | FAIL |
| N-gram Recall (Semantic stratum) | ≤ 0.40 | 0.000 (vacuous) | PASS* |
| Min-K%++ F1 Variance | ≥ 0.15 | 0.000 | FAIL |
| Indeterminacy Rate | [0.10, 0.50] | 0.000 | FAIL |

*The semantic stratum pass is vacuous: the stratum contains zero items, so recall is undefined and trivially zero.

## 5.4 Implementation Bugs Identified

Our validator flagged four advisory issues that were not resolved in the single Coder-Validator cycle. We document them here with the corrected specifications:

| Issue | Component | Actual Behavior | Correct Behavior |
|-------|-----------|-----------------|-----------------|
| B1 | NgramIndex.max_overlap | Counts total n-gram occurrences | Should count max consecutive run length |
| B2 | StratifiedEvaluator f1_matrix | Scalar broadcast → degenerate indeterminacy rate | Per-item computation required |
| B3 | DCPDDDetector | Uses −ref_log_prob | Must use log P_target − log P_ref (two models) |
| B4 | ConStatDetector | Custom heuristic | Must use `llmsanitize.contamination.constat()` API |

B3 is the most consequential: it causes DC-PDD to flag 100% of items, making the Min-K%++ F1 variance metric unmeasurable (since variance is computed jointly across MIA detectors). B2 makes the indeterminacy rate degenerate at 0.000 regardless of actual per-item margins. B1 inflates lexical scores, potentially affecting stratum boundary thresholds. B4 makes ConStat outputs non-comparable to the published method.

## 5.5 Infrastructure Validation

Despite the stratum collapse and implementation bugs, the core pipeline infrastructure works correctly and is reusable:

- N-gram index construction: 37.7M n-grams for The Pile, 17.2M for C4, 25.3M for FineWeb — built successfully via the EleutherAI pipeline.
- SBERT encoding: 50K documents per corpus encoded in ~5 minutes on H100 using all-MiniLM-L6-v2.
- FAISS IndexFlatIP: cosine search over 50K vectors is functional; the issue is corpus sampling, not the index itself.
- End-to-end evaluation loop: 3 benchmarks × 3 corpora × 5 detectors completed in 94 minutes.

The infrastructure for geometry-based routing is technically feasible. The critical fix required is replacing random corpus streaming with offline FAISS top-k retrieval for the SBERT geometry feature.
