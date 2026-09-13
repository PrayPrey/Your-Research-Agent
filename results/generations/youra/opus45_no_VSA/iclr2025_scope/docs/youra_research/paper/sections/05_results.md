# Results

Our experiments validate the core IPCR mechanism while revealing important limitations. We present results for each research question, with interpretation of what the findings mean for our hypothesis.

## Main Results: IPCR Achieves 95% of Oracle Performance

Table 1 presents end-to-end routing performance on held-out FLAN task families.

| Routing Strategy | Performance | Relative to Oracle |
|------------------|-------------|-------------------|
| Oracle | 91.39% | 100.00% |
| **IPCR (ours)** | **86.82%** | **95.00%** |
| Uniform | 36.79% | 40.26% |
| Random | 14.97% | 16.38% |

**Key finding:** IPCR achieves 95.00% of oracle performance, exceeding our 90% threshold. The improvement over Uniform is highly significant (t = 68.99, p = 7.05e-224), confirming that routing provides substantial benefit beyond naive adapter aggregation.

This result validates our central claim: zero-shot adapter routing is achievable without validation data when instruction embeddings contain sufficient task signal.

## Task Family Separability (H-E0)

The prerequisite for effective routing is that instruction embeddings cluster by task type.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Macro-F1 | 0.995 | ≥0.75 | ✅ Pass |
| Accuracy | 0.998 | — | — |
| Baseline F1 | 0.115 | — | — |

**Per-family F1 scores:** All 9 tested families exceed F1 = 0.98, ranging from 0.982 (strategyqa) to 1.000 (sensemaking).

**Interpretation:** Near-perfect linear separability (F1 = 0.995) demonstrates that MiniLM embeddings encode strong task-type signal. This aligns with our hypothesis that instruction semantics and adapter specializations share geometric structure. The 8.6x improvement over random baseline (0.995 vs 0.115) confirms the signal is genuine, not artifacts.

Figure 1 shows t-SNE visualization of the embedding space, with clear clustering by task family.

## Adapter Selection Accuracy (H-E1)

Given separable embeddings, can the linear probe select the correct adapter?

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Top-1 Accuracy | 72.67% | ≥70% | ✅ Pass |
| Top-3 Accuracy | 95.78% | ≥85% | ✅ Pass |
| vs Random | 14.8x | >1x | ✅ Pass |

**Interpretation:** The high top-3 accuracy (95.78%) indicates that even when top-1 prediction is wrong, the correct adapter is nearly always in the top 3 candidates. This supports a routing-with-fallback strategy for deployment: select top-1 by default, but top-3 coverage provides safety margin.

The 14.8x improvement over random selection confirms the linear probe extracts meaningful routing signal from frozen embeddings.

## Robustness Analysis (H-M2): A Critical Limitation

We tested whether routing is robust to instruction variations—a requirement for real-world deployment.

### Paraphrase Robustness

| Variant | Cosine Mean | Routing Consistency |
|---------|-------------|---------------------|
| WordNet synonyms | 0.720 | 72.5% |
| Embedding-filtered | 0.843 | 79.6% |
| **Combined** | **0.782** | **76.1%** |

**Threshold:** Cosine ≥ 0.90. **Result:** ❌ Fail (0.782)

### Keyword Masking

| Masking Rate | Original Acc | Masked Acc | Drop |
|--------------|--------------|------------|------|
| 20% keywords | 74.9% | 48.9% | 26.0% |
| 50% keywords | 74.9% | 30.4% | 44.4% |

**Threshold:** Drop < 10%. **Result:** ❌ Fail (44.4%)

**Interpretation:** The robustness failure reveals a fundamental characteristic of IPCR: routing depends on lexical keywords, not deep semantic invariants. WordNet synonym substitutions (e.g., "calculate" → "compute", "capital" → "Washington") cause embedding drift beyond routing tolerance.

This is not a minor limitation—it determines IPCR's deployment scope. The method is appropriate for controlled instruction formats (APIs, templates, chatbot interfaces with canonical phrasing) but fragile for open-ended queries with arbitrary paraphrasing.

**Root cause analysis:** MiniLM's mean-pooling architecture captures token presence rather than compositional meaning. Task discrimination emerges from keyword clusters in FLAN templates, not from understanding instruction semantics. This "lexical anchoring" hypothesis explains both our success (FLAN instructions contain task-indicative keywords) and our limitation (paraphrased instructions lose the anchor tokens).

## Per-Class Analysis

Robustness varies substantially across task families:

| Task Family | Routing Consistency | Interpretation |
|-------------|---------------------|----------------|
| cot_qasc | 97.2% | Robust — distinctive vocabulary |
| stream_aqua | 89.0% | Robust — math keywords |
| cot_esnli | 49.2% | Fragile — open-domain NLI |
| cot_creak | 62.9% | Fragile — claim verification |

Tasks with distinctive vocabulary (math: "calculate", "equation") maintain routing stability. Open-domain tasks with less keyword anchoring are most vulnerable.
