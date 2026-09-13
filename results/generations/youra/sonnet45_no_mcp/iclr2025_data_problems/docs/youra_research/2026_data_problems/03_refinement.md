# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-15T01:30:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: Gap 1
- **Gap Title**: Optimal Data Mixing Ratios for Multi-Domain Foundation Models
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 22

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 22

**Convergence Reason**: Elevated a curriculum effect into a rigorously specified, falsifiable "predictive diversity law" with cross-domain correlation, taxonomy robustness, cumulative-matched controls, and variance-explained criteria. Integrated mechanism (early gradient covariance geometry) with pre-registered statistical thresholds and regression tests linking geometry to robustness, continual learning, and OOD performance.

### Key Insights

1. **From Curriculum to Law**: Dr. Nova's initial temporal curriculum proposal evolved through rigorous stress-testing into a predictive diversity law based on corpus statistics, enabling a priori schedule optimization without expensive hyperparameter searches.

2. **Gradient Primacy Disambiguation**: Prof. Rex's challenge about gradient primacy vs curriculum coherence led to the shuffled-order control design, which cleanly separates these mechanisms—both outcomes publishable with appropriate narrative framing.

3. **Multi-Layer Validation**: Prof. Vera's insistence on rigorous falsification produced a six-phase validation framework with pre-registered quantitative thresholds and explicit failure modes where geometric claims collapse independently of performance gains.

4. **Practical Impact Pathway**: Dr. Sage's demand for field significance elevated the contribution from single-domain recipe to domain-agnostic law with practical tools (corpus-statistics prediction) and strategic importance (continual learning, OOD robustness).

5. **Feasibility Confirmation**: Prof. Pax's technical validation ensured all proposed measurements are implementable with existing tools, overhead stays under practical limits (4-6%), and mechanism is grounded in established optimization theory.

### Breakthrough Moments

- **Exchange 1**: Dr. Nova reframes data mixing as temporal curriculum, proposing dynamic schedules that evolve during training
- **Exchange 4**: Prof. Rex identifies gradient primacy as potential alternative mechanism, demands shuffled-order control
- **Exchange 6**: Prof. Vera formalizes four-condition experimental design with matched token counts and pre-registered thresholds
- **Exchange 12**: Prof. Vera specifies exact statistical estimators (participation ratio, bootstrapped CKA, power analysis)
- **Exchange 18**: Dr. Sage demands domain-agnostic validation, elevating to general law vs single recipe
- **Exchange 20**: Dr. Nova proposes predictive framework from corpus diversity statistics
- **Exchange 21**: Prof. Rex completes validation with diversity-PR correlation requirement and taxonomy robustness tests

---

## Final Hypothesis

### Title
**Gradient-Geometric Data Scheduling for Foundation Models**

### Core Claim
Under foundation model pretraining with mixed-domain corpora, if training domains are ordered from high to low diversity (measured by corpus statistics: vocabulary entropy, syntactic complexity, semantic spread), then final model performance, continual learning robustness, and out-of-distribution generalization improve significantly, because early high-diversity data establishes broader gradient covariance geometry through path-dependent optimization that persists throughout training.

### Mechanism

**Four-Step Causal Chain:**

1. **Early Diversity Shapes Gradient Geometry**: High-diversity domains (web text: broad vocabulary, varied syntax, distributed semantics) induce higher-rank gradient covariance matrices measurable via participation ratio.

2. **Path-Dependent Subspace Formation**: Early gradient covariance constrains the representational subspace for all subsequent learning due to non-convex SGD basin selection, manifesting as persistent CKA similarity between early and final checkpoints.

3. **Stable Specialization**: Later low-diversity, domain-specific training (code, scientific papers) operates within the established broad subspace, enabling specialization without collapsing representation geometry or gradient subspace orthogonality.

4. **Downstream Benefits**: Broader, more stable representational geometry produces: (a) better multi-domain benchmark performance, (b) reduced catastrophic forgetting during continual learning (measurable via Fisher overlap), and (c) improved out-of-distribution robustness.

---

## Predictions

### P1: Performance at 1B Scale
Diversity-ranked scheduling (high→low diversity) will exceed best static mixture by **≥2.0% absolute** on composite benchmarks (MMLU + Big-Bench + domain-specific) at 1B parameters, with 95% confidence intervals excluding zero across n≥5 seeds.

**Success Criterion**: ≥2.0% improvement, statistically significant (p<0.05)  
**Falsification**: If Δ < 0.5% or non-significant, performance claim fails at 1B

### P2: Scaling to 7B
At 7B parameters, diversity-ranked maintains **≥0.5% absolute improvement** with statistical significance and power ≥70% (n=5 seeds).

**Success Criterion**: ≥0.5% improvement, significant, power-validated  
**Falsification**: If effect vanishes or underpowered null, scaling persistence claim fails

### P3: Geometric Mechanism
At 25% training, diversity-ranked shows **≥15% higher participation ratio** and **≥10% higher CKA persistence** vs reversed schedules, with directional ordering: diversity-ranked > shuffled > static > reversed.

**Success Criterion**: Both metrics meet thresholds, ≥70% of layers for CKA  
**Falsification**: If <5% difference or inconsistent directionality, mechanism claim weakens

### P4: Continual Learning Robustness
After new domain injection, diversity-ranked exhibits **≤50% catastrophic forgetting** vs reversed (p<0.01), coupled with **≥10% higher Fisher overlap**.

**Success Criterion**: Both conditions must hold (coupled requirement)  
**Falsification**: If forgetting reduction <20% OR Fisher Δ <5%, stability claim rejected

### P5: Predictive Law from Corpus Statistics
Across 6-8 domains, pre-training corpus diversity metrics correlate with early gradient participation ratio at **Spearman ρ ≥ 0.7**.

**Success Criterion**: ρ ≥ 0.7, statistically significant  
**Falsification**: If ρ < 0.5, corpus-statistics prediction collapses to post-hoc explanation

---

## Novelty

**Key Innovation**: First work to (1) establish temporal data composition as a first-class design principle with optimization-theoretic grounding, (2) propose predictive schedules from corpus statistics rather than expensive hyperparameter searches, and (3) integrate performance, geometric mechanism, and continual learning stability in a unified experimental framework.

**Differentiation from Prior Work**:
- **Curriculum learning**: Applies to task difficulty progression (Bengio et al.), not systematic domain source ordering with geometric validation
- **Static data mixing**: DoReMi and domain reweighting research focus on static ratios, ignore temporal dynamics and gradient geometry
- **Multi-phase training**: Pretrain + finetune uses sharp transitions without principled schedules, geometric mechanism validation, or predictive frameworks
- **Continual learning**: EWC and rehearsal methods apply post-hoc regularization; this work provides pretraining-time intervention via data scheduling geometry

---

## Experimental Design

### Six-Phase Validation Framework

**Phase 1: Diversity-PR Correlation** (Cross-Domain Validation)
- Select 6-8 diverse domains, compute corpus diversity metrics pre-training
- Train 1B models with each domain as sole early phase (0-25%), then mixed (25-100%)
- Measure participation ratio at 10% and 25% for each
- **Success**: Spearman ρ(diversity rank, PR rank) ≥ 0.7

**Phase 2: Main Experimental Protocol**
- **Conditions**: Static (grid-searched), Diversity-Ranked (high→low), Reversed (low→high), Shuffled (matched per-step, randomized order)
- **Parametric sweep**: α ∈ {0, 0.25, 0.5, 0.75, 1.0} interpolating diversity-ranked ↔ reversed
- **Scales**: 1B (n=5), 7B (n=5)
- **Success**: All performance and geometric thresholds met (P1-P3)

**Phase 3: Taxonomy Robustness**
- Test with coarse vs fine domain partitions (e.g., "web" vs "blogs/news/forums")
- Recompute diversity ranking under both taxonomies
- **Success**: Kendall τ ≥ 0.6 between schedule orderings

**Phase 4: Cumulative-Matched Control**
- Create cumulative-matched reversed: identical per-checkpoint cumulative token counts as diversity-ranked, but opposite order
- **Success**: Effects persist under strict token matching (path dependence confirmed)

**Phase 5: Geometry-Robustness Regression**
- Across all runs: regress OOD accuracy and continual learning forgetting on PR@25% + final perplexity + schedule type
- **Success**: PR coefficient significant, R²(PR) ≥ 0.4 beyond perplexity

**Phase 6: Domain-Agnostic Generalization**
- Swap domain axis: reasoning-synthetic (high diversity) → naturalistic web (lower diversity)
- Measure corpus diversity stats, predict optimal order, validate
- **Success**: Same geometric and performance patterns emerge

### Contribution Tiers
- **5/5 phases met**: Field-defining predictive law with domain-agnostic generalization
- **4/5 phases met**: Strong contribution with caveats
- **3/5 phases met**: Publishable curriculum effect, narrow scope
- **≤2/5 phases met**: Major revision needed

---

## Limitations

1. **Diversity Metrics Validation**: Corpus statistics → gradient covariance correlation requires Phase 1 validation; if ρ < 0.7, predictive framework weakens

2. **Taxonomy Dependence**: Effects may depend on how domains are partitioned unless Phase 3 robustness validated (Kendall τ ≥ 0.6)

3. **Scaling Extrapolation**: Validation at 1B and 7B; scaling beyond 13B uncertain without additional experiments

4. **Computational Cost**: ~45,000 GPU-hours total limits accessibility to well-resourced labs (university clusters or industry research teams)

5. **Contingent Mechanisms**: If shuffled = monotonic, gradient primacy (not curriculum coherence) is causal—still publishable but different narrative

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Rigorous predictive diversity law with six-phase validation |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |
| **Novelty** | Strong - First optimization-theoretic framework for temporal data composition |
| **Falsifiability** | Strong - Pre-registered thresholds across six phases |
| **Significance** | Strong - Reframes pretraining as trajectory engineering |
| **Feasibility** | Strong - All measurements implementable, ~45K GPU-hours realistic |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
