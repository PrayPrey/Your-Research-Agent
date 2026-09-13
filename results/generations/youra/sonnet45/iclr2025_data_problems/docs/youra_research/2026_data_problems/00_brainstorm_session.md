---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Data Quality Metrics and FM Benchmark Performance"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-17
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Data curation and quality metrics for foundation models — specifically whether pretraining data quality signals (perplexity filtering, deduplication rate, domain composition) predictably correlate with downstream benchmark performance using existing model evaluation data

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — Reflection 3)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Foundation models (FMs) have become central to modern machine learning, with data playing a crucial role in their development and sparking increased attention to data-related challenges such as curation and attribution. Adapting traditional data-centric methods to FMs is challenging due to the scale of both data and model architectures. This research is positioned within the ICLR 2025 Workshop on Navigating and Addressing Data Problems for Foundation Models (DATA-FM), which focuses on persistent and emerging data-related challenges in FM deployment including data collection and curation, attribution, copyright, synthetic data and model collapse, safety/privacy/fairness, and benchmarks/evaluations.

Source Type: Workshop CFP / Structured Input | Retrying after TWO previous failures:
- h-e1 Run 1: TDA regime-stratification → MUST_WORK_FAIL
- h-e1 Run 2: LONGEST-MATCH contamination detection → PARTIAL (scale constraint, 0/8 contaminated cells, requires >100M docs)

---

## Lessons from Previous Attempts

### What Was Tried Before

**Attempt 1 (h-e1 Run 1): TDA Method Comparison Across Regime Strata**
- Hypothesis: Method × Regime interaction on LDS (Source > TracIn in High-KL, LoRIF ≥5× storage reduction)
- Approach: OLMo-1B checkpoint pairs, ANOVA interaction test on LDS metric
- Result: MUST_WORK_FAIL (1/4 checks passed)

**Attempt 2 (h-e1 Run 2): Benchmark Contamination Detection via LONGEST-MATCH**
- Hypothesis: Cross-Benchmark × Cross-Corpus contamination matrix with ≥3 elevated cells
- Approach: LONGEST-MATCH n-gram z-score (n=13, mincount=5) on 10k-doc corpus sample
- Result: PARTIAL → LIMITATION_RECORDED (0/8 contaminated cells; scale constraint — needs >100M docs for reliable z-score normality; ROOTS corpus gated)

### Why They Failed

**Attempt 1 failures:**
1. OLMo-1B checkpoint KL divergence too small (1.22) — regime simulation insufficient
2. n=1000 PoC scale too small for ANOVA interaction detection (p=0.8844)
3. Storage ratio measurement bug (47% vs required ≤20%)
4. Pre-registered thresholds too strict for PoC scale

**Attempt 2 failures:**
1. **Scale constraint**: n=13, mincount=5 requires >100M docs; PoC 10k-doc sample → all-zero contamination z-scores (normality check fails for all cells)
2. **Corpus access**: ROOTS (bigscience/roots) is gated — institutional access required
3. **Statistical requirements**: n-gram z-score baseline requires large variance not achievable at 10k docs

### How This New Direction Avoids Those Pitfalls

- **PIVOT AWAY from corpus streaming**: The new direction uses **pre-computed statistics** from existing curated datasets and published model evaluation results — no streaming of 100M+ documents required
- **PIVOT AWAY from gradient computation**: No TDA, no LoRIF, no LDS metric computation
- **PIVOT AWAY from n-gram scale requirements**: Instead of computing contamination from scratch, uses existing pretraining data documentation (datasheets, filtering pipeline descriptions) and model training reports
- **Concrete measurable outcomes**: Correlation between documented data quality metrics and published benchmark scores — directly computable from existing Open LLM Leaderboard data
- **All required data already exists**: Open LLM Leaderboard (thousands of model evaluations), published model cards and training reports (document data filtering choices), C4/OpenWebText/RedPajama statistics in existing papers

---

## Session Plan

Auto-extracted from structured input (Workshop CFP: ICLR 2025 DATA-FM Workshop) with ROUTE_TO_0 failure context integration (Reflection 3). New direction: Data Collection and Curation topic area — examining whether data quality filtering signals (as documented in model cards) predict downstream benchmark performance using existing evaluation leaderboard data.

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode — failure context analysis (2 previous attempts) + structured input extraction

---

## Research Question Development

### Initial Question

Do the data curation choices documented in LLM training reports (deduplication aggressiveness, perplexity filtering threshold, domain mix ratios) systematically correlate with downstream benchmark performance, and can these signals predict which benchmarks are most sensitive to data quality?

### Refined Question

Can data quality signals extractable from published LLM training documentation (deduplication rate, perplexity filtering ratio, domain composition) significantly predict benchmark performance variance across models on standard evaluation suites (MMLU, ARC, HellaSwag, TruthfulQA), as measured using the Open LLM Leaderboard, and do different benchmark types (knowledge, reasoning, truthfulness) respond differently to specific data quality dimensions?

### Detailed Sub-Questions

1. Across models documented on the Open LLM Leaderboard with published training data descriptions, does deduplication aggressiveness (% documents removed via exact/near-dedup) correlate with benchmark accuracy on knowledge-intensive tasks (MMLU, ARC)?
2. Does perplexity-based filtering (fraction of documents removed by perplexity threshold from a quality LM) predict reasoning benchmark performance (HellaSwag, WinoGrande) more strongly than knowledge benchmark performance (MMLU)?
3. Is there a statistically significant interaction between data domain mix (web crawl fraction vs. curated source fraction) and benchmark type (knowledge vs. reasoning vs. truthfulness) in predicting benchmark score, after controlling for model size (parameter count)?
4. Among data curation dimensions (deduplication, perplexity filtering, domain mix, decontamination), which has the highest partial correlation with benchmark performance variance after controlling for model scale, as estimated from existing published model documentation?
5. Do models trained on datasets with documented decontamination procedures (explicit removal of benchmark data) score differently on standard benchmarks compared to undocumented models of similar size, providing empirical evidence of contamination's effect size?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

Data curation is one of the most impactful but least understood variables in FM training — practitioners must choose filtering thresholds, deduplication strategies, and domain mixes without clear empirical guidance on downstream effects. The DATA-FM workshop explicitly lists "Practical strategies for curating data (e.g., filtering, mixing, repairing) tailored to FM training stages" and "Theoretical frameworks for guiding data selection and scaling laws" as target topics. If data quality signals predictably correlate with benchmark performance, this would provide actionable guidelines for dataset curation and explain benchmark score variance beyond just model architecture and scale. The Open LLM Leaderboard makes this question empirically tractable using existing public data.

### Feasibility Check

All proposed sub-questions are testable using existing real datasets and existing benchmarks:
- **Model evaluation data**: Open LLM Leaderboard (HuggingFace) provides benchmark scores for thousands of models — publicly available, no new evaluation needed
- **Data quality documentation**: Published model cards, technical reports (LLaMA-2, Mistral, Falcon, Pythia, GPT-NeoX), and dataset papers (C4, RedPajama, Dolma, OpenWebText) document filtering choices
- **Benchmark suite**: MMLU, ARC, HellaSwag, TruthfulQA, WinoGrande — all pre-existing, no new benchmarks needed
- **Statistical analysis**: Correlation, partial correlation, linear regression on a tabular dataset of (model, data_quality_metrics, benchmark_scores) — no GPU required, feasible on standard hardware
- **Decontamination effect**: Subset of models with documented decontamination vs. those without — subset analysis using existing leaderboard data

**Feasibility constraints fully satisfied:**
- ✅ No new benchmarks required — uses existing Open LLM Leaderboard
- ✅ No synthetic/generated data — uses published model documentation and existing benchmark scores
- ✅ No human evaluation or annotation — all metrics from published sources
- ✅ Immediately testable with publicly available resources
- ✅ No corpus streaming at 100M+ scale
- ✅ No gradient computation
- ✅ No gated corpus access required

**Key risk mitigation vs. previous failures:**
- Primary dataset (Open LLM Leaderboard) is fully public and static — no access barriers
- Statistical analysis is computationally trivial (correlation, OLS regression on ~500-2000 model records)
- Data quality features are extracted from published text (model cards) — no large-scale corpus processing

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can data quality signals extractable from published LLM training documentation (deduplication rate, perplexity filtering ratio, domain composition) significantly predict benchmark performance variance across models on standard evaluation suites (MMLU, ARC, HellaSwag, TruthfulQA), as measured using the Open LLM Leaderboard, and do different benchmark types (knowledge, reasoning, truthfulness) respond differently to specific data quality dimensions?

### detailed_question
1. Across models documented on the Open LLM Leaderboard with published training data descriptions, does deduplication aggressiveness (% documents removed via exact/near-dedup) correlate with benchmark accuracy on knowledge-intensive tasks (MMLU, ARC)?
2. Does perplexity-based filtering (fraction of documents removed by perplexity threshold from a quality LM) predict reasoning benchmark performance (HellaSwag, WinoGrande) more strongly than knowledge benchmark performance (MMLU)?
3. Is there a statistically significant interaction between data domain mix (web crawl fraction vs. curated source fraction) and benchmark type (knowledge vs. reasoning vs. truthfulness) in predicting benchmark score, after controlling for model size (parameter count)?
4. Among data curation dimensions (deduplication, perplexity filtering, domain mix, decontamination), which has the highest partial correlation with benchmark performance variance after controlling for model scale, as estimated from existing published model documentation?
5. Do models trained on datasets with documented decontamination procedures (explicit removal of benchmark data) score differently on standard benchmarks compared to undocumented models of similar size, providing empirical evidence of contamination's effect size?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Both previous failures (TDA regime-stratification and contamination n-gram detection) shared a common root cause: requiring computation at scale that exceeds PoC feasibility (large KL divergence between checkpoints, 100M+ doc streaming). The new direction avoids scale bottlenecks by using pre-existing published data.
- The Open LLM Leaderboard represents a unique opportunity: thousands of models evaluated on the same benchmarks, with varying levels of data documentation — a natural observational dataset for studying data curation effects.
- Data quality research is directly actionable: unlike TDA method comparison (academic) or contamination detection (forensic), understanding which curation choices improve downstream performance gives practitioners immediate guidance.
- The DATA-FM workshop explicitly targets scaling laws and data selection frameworks — this direction aligns with the "Theoretical frameworks for guiding data selection and scaling laws" subtopic.
- Partial correlation analysis controlling for model size allows disentangling data quality effects from scale effects — methodologically rigorous and feasible with standard statistics.
- Decontamination effect (sub-question 5) creates a natural bridge to the contamination detection direction — the two failed approaches become complementary rather than redundant.

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode (structured input extraction + failure context integration from 2 previous attempts)

### Areas for Further Exploration

- Benchmark contamination detection at full scale (deferred from h-e1 Run 2 — infrastructure exists, needs proper scale parameters: n=8, mincount=1, mC4 instead of ROOTS)
- TDA method comparison with proper scale (deferred from h-e1 Run 1 — direction correct, needs OLMo-7B with KL>2.0 and n=5000+ samples)
- Synthetic data quality metrics: do models trained on synthetic data show different benchmark sensitivity patterns?
- RAG-specific curation: does retrieval corpus quality interact with pretraining corpus quality?
- Multimodal data curation: does image-text alignment quality in pretraining correlate with VQA/captioning benchmarks?

---

## Next Steps

Proceed to Phase 1 - Targeted Research on data curation quality metrics, Open LLM Leaderboard analysis methods, existing data quality studies, and scaling law frameworks for data selection.

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
