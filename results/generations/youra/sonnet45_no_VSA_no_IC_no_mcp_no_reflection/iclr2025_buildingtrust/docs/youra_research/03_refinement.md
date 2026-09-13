# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T08:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: Gap 1
- **Gap Title**: Unified Multi-Dimensional Trustworthiness Evaluation Framework
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 8

**Convergence Reason**: All convergence criteria met at Exchange 8. SPECIFIC (core claim stated), MECHANISM (hierarchical clustering specified), PREDICTIONS (4-phase protocol), NOVELTY (scale-invariant taxonomy), FEASIBILITY (all methods validated), OBJECTIONS (confounds addressed via stratification).

### Key Insights

1. **Interconnected Failure Modes** (Exchange 1, Dr. Nova): Trustworthiness dimensions may not be independent — treating them as isolated properties misses shared root causes that produce correlated failures across reliability, robustness, and fairness.

2. **Correlation Analysis Insufficient Alone** (Exchange 3, Dr. Sage): Finding correlations is descriptive, not explanatory. The theoretical contribution emerges from failure mode taxonomy that guides intervention design, not just correlation reporting.

3. **Stratification Addresses Confounds** (Exchange 7, Dr. Nova): Instead of controlling for confounding variables (model size), stratify by them and test if patterns persist within strata. Scale-invariance provides stronger evidence than statistical control.

4. **Intervention Validation Critical** (Exchange 4-5, Prof. Pax & Dr. Ally): Clustering must guide practical improvements. Testing whether interventions targeting one failure mode improve all dimensions in that cluster validates the taxonomy's actionability.

### Breakthrough Moments

1. **Exchange 1**: Reframing trustworthiness dimensions as interconnected failure modes revealed through cross-benchmark correlation patterns, rather than isolated properties measured independently.

2. **Exchange 7**: Flipping the confound control problem into a validation strength by using stratified analysis + Mantel test to demonstrate scale-invariance of failure patterns.

3. **Exchange 8**: Complete 4-phase experimental protocol with falsification criteria at each stage, integrating statistical rigor (Prof. Vera), theoretical contribution (Dr. Sage), and feasibility validation (Prof. Pax).

---

## Final Hypothesis

### Title
Scale-Invariant Failure Mode Taxonomy for Multi-Dimensional LLM Trustworthiness

### Core Claim
Multi-dimensional trustworthiness failures in LLMs exhibit statistically significant correlations across existing benchmarks (TruthfulQA for reliability, AdvBench for robustness, BOLD for fairness). These correlations, when analyzed via hierarchical clustering, reveal distinct failure modes representing shared root causes that persist across model architectures and scales.

### Mechanism
Correlation matrices computed from per-model benchmark scores undergo hierarchical clustering (Ward linkage) to identify failure mode clusters. Cluster stability is validated via bootstrap resampling (1000 iterations). Cross-strata Mantel tests confirm patterns are scale-invariant, not confound-driven.

**Causal Chain:**
1. LLM failures arise from shared underlying properties (e.g., poor calibration, brittle representations, biased training data) rather than dimension-specific issues
2. Shared root causes produce correlated failure patterns detectable via pairwise correlation analysis across benchmarks
3. Correlated patterns cluster into distinct failure modes via hierarchical clustering, validated as stable (not sampling artifacts) through bootstrap resampling
4. Failure mode clusters persist across model scales (small <1B, medium 1-10B, large >10B params), indicating fundamental LLM properties rather than architecture-specific confounds

---

## Predictions

**P1 (PRIMARY)**: Pairwise failure correlations across TruthfulQA, AdvBench, BOLD exceed random chance (Spearman r > 0.3, p < 0.01 after Bonferroni correction) for ≥70% of model comparisons.
- **Falsification**: If correlations not significantly different from random (p > 0.05) or effect size small (r < 0.2), hypothesis rejected at Phase 1.

**P2**: Hierarchical clustering identifies 2-5 stable failure modes (silhouette score > 0.5, stable across 80%+ of 1000 bootstrap iterations).
- **Falsification**: If silhouette score < 0.3 or bootstrap consistency < 60%, clusters are unstable noise.

**P3**: Correlation pattern similarity across model size strata (Mantel test r > 0.7 for all 3 pairwise strata comparisons) demonstrates scale-invariance.
- **Falsification**: If Mantel r < 0.5 for any comparison, failure modes are architecture/scale-specific (hypothesis still valid but interpretation changes).

**P4**: Interventions targeting one failure mode improve ALL benchmarks in that cluster (Cohen's d > 0.5) without degrading other clusters (d < 0.1).
- **Falsification**: If intervention improves <50% of cluster benchmarks OR degrades other clusters (d < -0.3), taxonomy not actionable.

---

## Novelty

### What's New
Paradigm shift from "score each dimension independently" to "map the trustworthiness failure space via correlation clustering". Prior work (HELM) aggregates multiple benchmarks but doesn't analyze cross-dimensional patterns. This work proposes correlations ARE the diagnostic signal, enabling holistic model diagnosis and intervention targeting shared root causes.

### Differentiation from Prior Work

**vs HELM (Holistic Evaluation)**: HELM reports separate scores per dimension. This work analyzes cross-dimensional correlations to discover shared failure modes, not just aggregate metrics.

**vs Single-Dimension Papers**: TruthfulQA, AdvBench, BOLD papers focus on isolated dimensions. This work explicitly tests whether failures correlate across dimensions and clusters them into actionable failure modes with intervention validation.

**vs General Alignment Observations**: Existing work notes "alignment improves multiple dimensions" without formalization. This work quantifies which dimensions co-vary via failure mode taxonomy, enabling targeted intervention selection based on diagnosis rather than trial-and-error.

---

## Experimental Design

### Dataset
Public LLM benchmark results aggregated from leaderboards (TruthfulQA, AdvBench, BOLD) and model cards for ≥15 models across 3 size strata (<1B, 1-10B, >10B parameters).

### Models
Multi-model corpus: GPT series, LLaMA series, Claude series, Mistral, Phi, etc. — minimum 5 models per size stratum for statistical power.

### Baselines
1. **Random Correlation Null Model**: Permutation test generating null distribution by shuffling benchmark scores
2. **Single-Dimension Evaluation**: Isolated benchmark scores (current practice)
3. **HELM Aggregation**: Aggregate benchmark reporting without cross-dimensional correlation analysis

### 4-Phase Experimental Protocol

**Phase 1: Correlation Discovery**
- Collect public benchmark scores for ≥15 models across 3 size strata
- Compute Spearman correlation matrices (pairwise across TruthfulQA, AdvBench, BOLD)
- Run permutation test for significance (p < 0.01, Bonferroni corrected)

**Phase 2: Failure Mode Clustering**
- Apply hierarchical clustering (Ward linkage) to correlation matrices
- Validate cluster stability via bootstrap resampling (1000 iterations)
- Compute silhouette scores for cluster quality (target > 0.5)

**Phase 3: Cross-Strata Validation**
- Perform Mantel test comparing correlation matrices between size strata
- Criterion: r > 0.7 (high similarity) → failure modes are scale-invariant
- Alternative: r < 0.5 → failure modes are architecture-specific (different interpretation)

**Phase 4: Intervention Validation**
- Select emergent failure mode with highest silhouette score
- Apply targeted intervention (e.g., calibration training for epistemic uncertainty cluster)
- Measure pre/post intervention effect sizes (Cohen's d) on all benchmarks
- Control: Track benchmarks in other clusters for tradeoff detection

---

## Limitations

### Sample Size
TruthfulQA (~800 questions) may be insufficient for stable correlation estimation across multiple model comparisons. Bootstrap resampling mitigates but doesn't eliminate this concern.

**Mitigation**: Supplement with additional benchmarks if correlations appear unstable during analysis.

### Benchmark Coverage
Only 3 trustworthiness dimensions tested (reliability, robustness, fairness). Explainability not included due to lack of standard non-human-eval benchmarks.

### Cluster Labeling Subjectivity
Interpretive labels like "epistemic uncertainty" require qualitative judgment despite quantitative clustering.

**Mitigation**: Report clusters as "Cluster A, B, C" with descriptive statistics. Interpretive labels optional for communication, not required scientifically.

### Intervention Scope
Phase 4 tests only ONE failure mode intervention (calibration or adversarial training). Full intervention spectrum untested.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas participated, all convergence criteria met at Exchange 8 |
| **Clarity Verified** | Yes - 4-phase protocol with quantitative success criteria |
| **Remaining Objections** | 2 acknowledged limitations (sample size, cluster labeling) with mitigation strategies |

---

## Why This Matters

Current trustworthiness evaluation practice is fragmented — papers report TruthfulQA OR robustness OR fairness, never the full picture. Practitioners lack holistic diagnostic tools. Researchers lack guidance on which interventions fix multiple dimensions simultaneously.

This framework transforms trustworthiness evaluation from fragmented scorecards into actionable diagnostics by:

1. **Discovering** which trustworthiness properties co-vary through correlation analysis
2. **Diagnosing** model weaknesses holistically via failure mode clustering
3. **Guiding** intervention selection to target shared root causes rather than isolated symptoms

The paradigm shift: from "optimize each dimension independently and hope they don't trade off" to "identify shared failure modes and fix them at the root."
