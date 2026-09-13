# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-07-12T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: Gap 3
- **Gap Title**: Unified Meta-Analysis Framework for Benchmark Characteristics
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) after 15 exchanges with genuine persona disagreement and adversarial stress-testing

### Key Insights
- **Performance variance as reproducibility proxy** enables scale (4000+ benchmarks) where direct replication studies are sparse (<100 papers)
- **≥2 artifact threshold** balances sensitivity and specificity, providing concrete policy guideline
- **Regression discontinuity design** around policy changes (NeurIPS 2020 datasheet mandate) offers stronger causal inference than cross-sectional comparison

### Breakthrough Moments
1. **Exchange 6 (Dr. Ally)**: Switching from direct reproducibility measurement to performance variance as a scalable proxy—solved the "replication studies are too sparse" problem
2. **Exchange 12 (Dr. Ally)**: Cohen's d effect size specification replacing arbitrary 30% threshold—brought statistical rigor
3. **Exchange 15 (Dr. Nova)**: Longitudinal within-benchmark analysis for benchmarks gaining artifacts post-publication—provides within-subject controls

---

## Final Hypothesis

### Title
**Quantifying Documentation Artifact Impact on ML Benchmark Reproducibility via Performance Variance Analysis**

### Hypothesis ID
H-DocArtifactVariance-v1

### Core Claim
Under the scope of ML classification benchmarks published 2019-2024 in Papers with Code, if a benchmark's original paper includes ≥2 documentation artifacts (GitHub repository, dataset card, reproducibility badge), then the benchmark exhibits 30-50% lower performance variance (coefficient of variation) across independent reproduction attempts, because documentation artifacts enable precise replication by reducing implementation ambiguity across research groups.

### Mechanism (3-Step Causal Chain)
1. **Documentation artifacts provide implementation details** - GitHub repos contain code, dataset cards specify data collection/splits/intended use, badges signal reproducibility verification
2. **Implementation details reduce interpretation ambiguity** - Independent research groups attempting reproduction have precise specifications for preprocessing, splits, evaluation protocols
3. **Reduced ambiguity leads to lower cross-lab variance** - Performance variance (CV of reported metrics) decreases as replication becomes more consistent

**Key Tension**: Performance variance measures consistency, not correctness—labs could consistently reproduce WRONG results (reproducibility ≠ validity)

---

## Predictions

### P1 (Primary) - Effect Size
**Statement**: Benchmarks with ≥2 artifacts show statistically significantly lower performance variance (CV) than benchmarks with <2 artifacts

**Test Method**: Mann-Whitney U test comparing CV distributions between high-artifact and low-artifact groups

**Success Criterion**: p<0.05 (two-tailed) with Cohen's d >0.5 (medium effect size)

**Falsification**: p>0.05 OR Cohen's d <0.3 (small/negligible effect)

### P2 (Secondary) - Dose-Response
**Statement**: Artifact count (0-3) shows negative dose-response relationship with performance variance

**Test Method**: Spearman rank correlation between artifact count and CV

**Success Criterion**: ρ<-0.3 (moderate negative correlation), p<0.05

**Falsification**: ρ>-0.1 (weak/no correlation) OR p>0.05

### P3 (Exploratory) - Domain Heterogeneity
**Statement**: Documentation artifact effect size is larger in computer vision than NLP

**Test Method**: Stratified analysis computing Cohen's d separately for CV and NLP benchmarks

**Success Criterion**: d_CV >0.6 AND d_NLP >0.3 AND d_CV - d_NLP >0.2

**Falsification**: No significant difference between domains (d_CV ≈ d_NLP within 0.1)

---

## Novelty

### Preserved Novelty
First quantitative measurement of documentation artifact impact on performance consistency at scale (4000+ benchmarks)

### Key Innovation
Performance variance (CV across independent reproductions) as a scalable reproducibility proxy, bypassing the sparsity of direct replication studies

### Differentiation from Prior Work
- **vs Semmelrock et al. 2024**: We QUANTIFY effect size (d>0.5) rather than qualitatively cataloging barriers
- **vs Koch et al. 2021**: We link documentation to reproducibility OUTCOMES, not just reuse patterns  
- **vs Kapoor & Narayanan 2023**: Preventive measurement (artifact impact) vs retrospective leakage detection

---

## Experimental Design

### Data Sources
- **Primary**: Papers with Code Benchmark Results Database (API access)
  - 4000+ benchmarks with aggregated results from independent groups
  - Enables variance calculation at scale
- **Secondary**: Semantic Scholar API (for sampling validation)
  - Check for bias toward well-documented papers in Papers with Code coverage

### Variables
- **Independent**: Documentation artifact count, binarized as ≥2 vs <2 (GitHub repo, dataset card, reproducibility badge)
- **Dependent (Primary)**: Performance variance (CV = σ/μ) from ≥5 independent result reports per benchmark
- **Controls**: Benchmark age (years since publication), task domain (CV/NLP), metric type (accuracy/F1)

### Sample
- N=100 classification benchmarks (2019-2024) with ≥5 reported results
- Power analysis: Detects Cohen's d=0.57 with 80% power, α=0.05 (two-tailed)
- Scope restrictions: Classification tasks only (metric standardization), 2019+ (artifact badge availability)

### Baselines
1. **Benchmark age as control**: Linear regression CV ~ years_since_publication
2. **Null model**: No relationship between artifacts and variance (H0)

---

## Limitations

### Known Constraints
1. **Performance variance ≠ validity**: Measures consistency across labs, not absolute correctness—labs could consistently reproduce wrong results
2. **Sampling bias risk**: Papers with Code may preferentially include well-documented papers (mitigation: propensity weighting)
3. **Metric heterogeneity**: Even within classification, accuracy variants (balanced accuracy, top-5 accuracy) create noise
4. **Temporal confounding**: Older benchmarks have more time for documentation improvement AND more reported results

### Scope Boundaries
- **Applies to**: Classification benchmarks 2019-2024 with standardized accuracy-based metrics from Papers with Code
- **Does NOT apply to**: Generative tasks (heterogeneous metrics like FID, BLEU), regression/ranking tasks, papers pre-2019, benchmarks with <5 results

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed via mitigation strategies) |
| **Phase 2B Readiness** | READY |

---

## Validation Strategy

### Internal Validity
- Control for benchmark age, task domain, metric type via stratified analysis
- Inter-rater reliability check for artifact coding (Cohen's kappa >0.8)
- Pre-registration of analysis plan to prevent p-hacking
- Outlier handling: Winsorize CV at 95th percentile

### External Validity
- Generalizability: Findings apply to classification benchmarks 2019+, not generative tasks
- Sampling validation: Compare Papers with Code coverage rate for high vs low artifact papers
- Temporal validity: Account for COVID-19 confound (2020 policy changes coincide with cultural shifts toward open science)

---

*Phase 2A Complete - Ready for Phase 2B Research Planning*
