# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T08:15:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Inline Self-Play - Independent Controller Ablation)
- **Gap ID**: Gap 1
- **Gap Title**: Theoretical Frameworks for FM-Specific Data Selection Scaling Laws
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met - SPECIFIC (clear core claim), MECHANISM (information-theoretic foundation), PREDICTIONS (3 testable predictions with quantitative thresholds), NOVELTY (Pareto frontier framework for quality-compute tradeoffs), FEASIBILITY (measurable with existing metrics and benchmarks), OBJECTIONS (stationarity concern acknowledged with empirical mitigation strategy)

### Key Insights

1. **Pareto Frontier Reframing**: Dr. Nova's Exchange 7 breakthrough - shifting from "add Q(D) term to scaling law" to "map quality-compute tradeoff frontier" provides more powerful theoretical framework
2. **Information Theory Foundation**: Rate-distortion theory, compression, and compressed sensing provide mathematical grounding for quality-quantity tradeoffs
3. **Scalar Projection Justification**: Dr. Ally's analogy to parameter count (multi-dimensional transformer → single capacity metric) justifies reducing multi-dimensional quality to learnable scalar Q(D)
4. **Feasibility Confirmation**: Prof. Pax verified measurability using existing proxies (dedup ratio, perplexity, domain diversity) and existing benchmarks (MMLU, HellaSwag, ARC)

### Breakthrough Moments

1. **Exchange 7 (Dr. Nova)**: Reframed hypothesis as constrained optimization with data-compute tradeoff surface - more interesting theoretical contribution than additive scaling term
2. **Exchange 5 (Dr. Ally)**: Parameter count analogy justified scalar Q(D) despite multi-dimensional reality - "learnable projection" resolves Prof. Pax's concern
3. **Exchange 4 (Prof. Pax)**: Confirmed feasibility without new benchmarks - existing infrastructure sufficient for validation
4. **Exchange 2 (Prof. Vera)**: Established testability via systematic ablations (dedup levels, mixing ratios, filter thresholds) with power-law predictions

---

## Final Hypothesis

### Title
Data Quality as Compute Efficiency Multiplier in Foundation Model Scaling Laws

### Hypothesis ID
H-QualityScaling-v1

### Core Claim
Under foundation model pretraining conditions, if data quality Q(D) is increased through systematic curation (deduplication, filtering, mixing), then model performance at fixed compute budget improves following a predictable tradeoff surface, because Q(D) acts as a compute efficiency multiplier where higher quality data reduces compute required to reach target performance.

### Mechanism

**Causal Chain (3 steps):**

1. **Information Density Increase**: Data curation (deduplication, filtering, mixing) increases information density per token by removing redundancy and balancing domain coverage. Grounded in information theory (compression removes redundancy, rate-distortion predicts quality-quantity tradeoffs).

2. **Gradient Signal Amplification**: Higher information density means each training token provides more 'bits of learning' - model extracts more gradient signal per example. Analogous to compressed sensing (fewer high-quality measurements suffice).

3. **Compute Efficiency Multiplier**: More gradient signal per token means same performance target reachable with fewer tokens (less compute). This creates Q(D) as a compute multiplier in the scaling relationship.

**Operational Definition**: Q(D) = w1·dedup_ratio + w2·domain_diversity + w3·avg_perplexity_score + w4·token_efficiency, where weights are learned from validation performance.

---

## Predictions

### P1 (Primary): Convex Iso-Performance Curves
**Statement**: Iso-performance curves in (compute, Q(D)) space are convex - achieving fixed target loss requires less compute at higher Q(D), with diminishing returns.

**Test Method**: Train models at grid of (compute budget, quality level) combinations. Plot curves connecting points with same final loss. Check convexity via second derivative.

**Success Criterion**: Curves are convex for at least 2 out of 3 target loss values tested. Compute reduction >15% when Q(D) increases by 1 standard deviation.

**Falsification**: If curves are concave or irregular, tradeoff relationship does not hold. If compute reduction <5%, effect is negligible.

### P2: Quality Variance Explanation
**Statement**: Data quality Q(D) explains >20% of performance variance beyond model size and compute in regression analysis.

**Test Method**: Fit regression: Loss ~ α·log(params) + β·log(compute) + γ·Q(D) + ε. Measure R² improvement when adding Q(D) term.

**Success Criterion**: ΔR² > 0.20 when Q(D) added to baseline. γ coefficient statistically significant (p < 0.01).

**Falsification**: If ΔR² < 0.05, quality is negligible factor. If γ not significant, relationship is noise.

### P3: Power-Law Quality Relationships
**Statement**: Systematic quality variations (deduplication level, filter threshold) produce power-law performance changes when plotted log-log.

**Test Method**: Vary single quality dimension (e.g., dedup ratio: 0%, 50%, 80%, 95%) while holding others constant. Train to same compute budget. Plot log(quality metric) vs log(loss).

**Success Criterion**: Log-log plot is approximately linear (R² > 0.85) indicating power-law relationship. Holds for at least 2 out of 3 quality dimensions tested.

**Falsification**: If relationship is non-monotonic or non-linear in log-log space, power-law assumption invalid.

---

## Novelty

**Key Innovation**: First formal theory treating data quality as compute efficiency multiplier in FM scaling laws. Proposes Pareto frontier framework for quality-compute tradeoffs with operationalized Q(D) metric.

**Differentiation from Prior Work**:
- **Chinchilla scaling laws**: Assumes uniform data quality. Our work adds Q(D) as explicit parameter and predicts quality-compute tradeoffs.
- **Data-centric AI (Andrew Ng)**: Qualitative emphasis on quality over quantity. Our work provides quantitative predictive framework via scaling law formulation.
- **Data filtering studies (GPT-3, Pile)**: Ad-hoc filtering decisions without theory. Our work provides theoretical foundation for predicting filtering impact on compute efficiency.

---

## Experimental Design

### Dataset
**C4 (Colossal Clean Crawled Corpus)** - Publicly available via HuggingFace. Has documented filtering pipeline enabling controlled quality variations. Large enough for scaling experiments. Used in T5, GPT-Neo, and other scaling studies.

### Model
**GPT-2 architecture (decoder-only transformer)** - Standard implementation via HuggingFace transformers library. Well-studied architecture with known scaling properties. Enables comparison to existing scaling law literature.

### Baselines
1. **Chinchilla-optimal**: Train with standard Chinchilla token-parameter ratios, no quality variations
2. **Unfiltered training**: Train on raw C4 without additional deduplication or quality filtering
3. **Model-size-only scaling**: Vary model size at fixed compute and data quality

### Quality Variations
- **Deduplication levels**: 0%, 50%, 80%, 95%
- **Domain mixing ratios**: Vary proportions of web/books/code content
- **Quality filter thresholds**: Apply classifier-based filtering at different cutoff scores

### Evaluation
- **Primary metric**: Validation loss (bits-per-token) on held-out C4 subset
- **Secondary metrics**: Downstream benchmark performance (MMLU, HellaSwag, ARC)

---

## Limitations

### Known Constraints
1. **Scope**: Decoder-only transformer language models, pretraining phase only, web-scale text datasets, 1B-100B parameter range, English primarily
2. **Stationarity assumption**: Q(D) weights may vary across model scales (1B vs 100B) - requires empirical validation
3. **Linear combinability**: Assumes quality dimensions combine linearly without interactions - non-linear effects could break scalar Q(D)
4. **Domain specificity**: Optimal Q(D) weights may differ for code vs language vs mixed domains

### Does Not Apply To
- Encoder-only or encoder-decoder architectures
- Fine-tuning or RLHF phases (quality definition differs)
- Multimodal pretraining (text+vision requires separate theory)
- Models below 1B parameters (may not exhibit scaling law behavior)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 7 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (stationarity concern acknowledged with mitigation strategy) |

---

## Phase 2B Readiness

**Status**: READY

**Sub-Hypothesis 1 (Existence)**: Data quality Q(D) metrics (dedup ratio, domain diversity, perplexity scores) must be measurable and correlate with information density.

**Sub-Hypothesis 2 (Mechanism)**: Q(D) acts as compute efficiency multiplier - higher quality reduces compute needed for target performance via increased gradient signal per token.

**Sub-Hypothesis 3 (Comparison)**: Compare Q(D)-optimized training vs Chinchilla baseline and unfiltered training to quantify compute savings (deferred to Phase 5).

**Open Questions**:
- Optimal Q(D) weight values per domain (code, language, mixed)
- Stationarity of Q(D) across model scales (1B vs 100B)
- Threshold effects: does quality stop helping beyond some point?

---

*End of Phase 2A Refinement Summary*
