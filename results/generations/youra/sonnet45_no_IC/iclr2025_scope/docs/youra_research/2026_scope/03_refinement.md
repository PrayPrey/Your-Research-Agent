# Phase 2A Refinement Summary

**Hypothesis ID:** H-MetaMethodSelector-v1  
**Generated:** 2026-07-13  
**Gap:** GAP-1 - No Single Optimal Method Across Dataset Diversity  
**Confidence Level:** 0.70

---

## Core Hypothesis

**Under** supervised learning settings with existing benchmark datasets, **if** a meta-classifier is trained on aggregated benchmark results (50-60 datasets) using fast-to-compute dataset features (sample size, dimensionality, class imbalance, signal statistics), **then** it will predict method families (Linear/Polynomial/RNN/Augmentation) that achieve top-30% ranking performance on held-out datasets with >50% success rate, **because** systematic performance patterns correlate dataset characteristics with method strengths.

---

## Causal Mechanism

1. **Dataset characteristics → Structural advantages:** Sample size, dimensionality, and signal properties determine which method families have structural advantages (e.g., small datasets benefit from augmentation, structured problems favor polynomial bases)

2. **Aggregated benchmark results → Training examples:** Published literature provides 50-60 benchmarks with documented baseline comparisons, sufficient to learn feature-method relationships

3. **Meta-classifier extracts patterns:** Random Forest trained on dataset features learns generalizable patterns (not domain folklore), validated via ablation testing

4. **Predicted method achieves competitive performance:** Recommended method family ranks in top-30% on new datasets without exhaustive search, reducing wasted computational resources

---

## Testable Predictions

### P1 (Primary): Cross-Validation Performance
On 5 held-out benchmarks from leave-5-out CV, meta-classifier's recommended method family achieves top-30% ranking in ≥3/5 cases (60% success rate). **Success:** Chi-square p < 0.05 vs. 30% random baseline. **Failure:** ≤40% success rate or p > 0.05.

### P2: Feature Independence from Domain Folklore  
Removing domain labels from features reduces accuracy by <5%, indicating features are predictive independent of domain encoding. **Success:** Accuracy drop <5%, SHAP importance (domain) <0.2. **Failure:** Drop >20% or SHAP (domain) >0.5.

### P3: Temporal Generalization
Meta-classifier trained on pre-2024 benchmarks predicts method rankings on post-2024 benchmarks with ≥40% top-30% accuracy. **Success:** ≥40% on new benchmarks. **Failure:** <30% (no better than random).

---

## Key Variables

**Independent Variables (Features):**
- Tier 1 (universal, 1 sec): Sample size, dimensionality, class imbalance (Gini), signal-to-noise ratio
- Tier 2 (domain-conditional, 5-15 sec): Autocorrelation (time-series), edge density (vision), correlation rank (tabular)

**Dependent Variable:**
- Predicted method ranking percentile (target: ≤30% = top-30%)

**Controlled Variables:**
- Train/test split (leave-5-out CV), method representative selection, feature computation budget (<1 min)

---

## Experimental Setup

**Dataset Collection:** Mine literature for 50-60 benchmarks - OGB (15), FedML (6), LEAF (5), pFL-Bench (8), Champneys NLSI (5), Zhou medical FL (9), Papers with Code (10+)

**Model:** scikit-learn RandomForestClassifier (n_estimators=100, max_depth=10)

**Baselines:** Random selection (30% expected), domain folklore (40-50%), majority class (30-40%)

**Evaluation:** Leave-5-out cross-validation, predict method family, check if representative achieves top-30% ranking

---

## Novelty & Impact

**What's New:** First trainable predictive model for dataset-to-method selection, transforming descriptive observations into actionable guidance. Prior work (Afkanpour 2024, Liao 2025) provides only qualitative reviews.

**Significance:** 
- **Practitioner value:** Informed method recommendation reduces wasted compute vs. exhaustive search
- **Benchmark design:** Reveals which dataset characteristics drive method performance
- **Methodological transparency:** Makes implicit assumptions explicit ("method wins because dataset has X property")

**Differentiation:**
- Zhou et al. 2025: Reports rankings on 9 datasets but provides no predictor for NEW datasets
- Champneys et al. 2024: Baseline comparisons without meta-analysis of predictive features
- Afkanpour/Liao: Descriptive problem statements, no decision framework

---

## Key Assumptions & Risks

**A1:** 50-60 published benchmarks sufficient for robust learning. **Risk:** If <30 collectible, meta-classifier overfits.

**A2:** Tier 1+2 fast features capture sufficient dataset characteristics. **Risk:** If hidden structure (e.g., W-H saturation) not detectable, need expensive Tier 3 probing.

**A3:** Method families exhibit consistent behavior across similar datasets. **Risk:** If rankings are chaotic (no feature correlation), meta-learning impossible.

**A4:** Cross-validation approximates zero-shot generalization. **Risk:** If CV accuracy high but new-benchmark accuracy low, learned benchmark-specific artifacts.

**A5:** Top-30% ranking represents useful guidance. **Risk:** If practitioners demand >90% accuracy (measured via survey), adoption unlikely.

---

## Scope & Boundaries

**Applies to:** Supervised learning (classification, regression) across vision/time-series/tabular domains with published baseline comparisons, sample size n ∈ [100, 100K]

**Does NOT apply to:** Unsupervised learning, RL, generative models (insufficient baselines); Real-time systems (<1 sec latency constraint); Extreme-scale datasets (n > 1M, slow feature computation); Novel domains (<10 published benchmarks)

---

## Success/Failure Criteria

**SUCCESS:** >50% top-30% accuracy on held-out benchmarks, p < 0.05  
**PARTIAL:** 40-50% accuracy → Investigate feature sufficiency, try Tier 3 or expand benchmark collection  
**FAIL:** <40% accuracy → Reject hypothesis, features insufficient or method rankings too chaotic

---

## Persona Consensus

**Overall Verdict:** PROCEED_WITH_VERIFICATION (Confidence: 0.70)

**Support:** Dr. Nova (High), Prof. Vera (Medium-High, conditional), Prof. Pax (Medium), Dr. Sage (High), Dr. Ally (High), Prof. Rex (Medium, conditional)

**Key Strengths:** Addresses real problem, feasible with existing resources, testable, novel framing

**Key Risks:** Sample size borderline (50-60), feature sufficiency uncertain, temporal stability unverified, adoption threshold unknown

**Recommendation:** Proceed to Phase 2B with vigilant verification. Prioritize: (1) Confirm 50+ benchmarks collectible, (2) Validate Tier 1+2 features achieve >40% baseline, (3) Run ablation test to rule out domain folklore.

---

**Phase 2A Complete** | Next: Phase 2B - Research Planning
