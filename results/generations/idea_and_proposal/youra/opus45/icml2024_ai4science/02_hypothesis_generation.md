# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-RDIF-v1
**Confidence Level:** 0.81

**Main Hypothesis:**
Under scientific AI modeling conditions with domain ontology availability, if model representations are optimized for mutual information alignment with scientific concepts using CLUB estimation, then there exists a quantifiable Pareto frontier between prediction accuracy and interpretability that can be efficiently discovered using surrogate-accelerated multi-objective optimization, because scaling increases model capacity at the cost of representation sparsity relative to known concepts.

**Alternative Hypothesis (H0):**
There is no systematic trade-off between scaling and interpretability in scientific AI; either (a) scaling does not reduce concept alignment, or (b) interpretability cannot be meaningfully quantified via mutual information with domain concepts.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Model architecture | Independent | Architecture descriptor encoding depth, width, attention patterns | 10M - 10B parameters |
| Training data size | Independent | Number of training samples in domain dataset | 10K - 10M samples |
| Compute budget | Independent | GPU-hours or FLOPS allocated for training | 10 - 10,000 GPU-hours |
| Task accuracy | Dependent | Domain-specific metrics: AUROC (MoleculeNet), RMSE (ClimateLearn), accuracy (ProteinGym), MAE (MatBench) | 0.0 - 1.0 or domain-specific |
| Interpretability score I(m) | Dependent | CLUB_estimate(φ(x), C) measuring MI between representations and concept vocabulary | 0.0 - log(|C|) nats |
| Domain ontology | Controlled | Fixed concept vocabulary from ChEBI, CMIP6, Gene Ontology, or Materials Project | Domain-specific |
| Benchmark dataset | Controlled | Standard benchmarks: MoleculeNet, ClimateLearn, ProteinGym, MatBench | Fixed per domain |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Scaling model size/data]
        ↓ (Link 1)
[Increased representation capacity]
        ↓ (Link 2)
[Decreased concept alignment]
        ↓ (Link 3)
[Lower interpretability score I(m)]
```

**Link 1: Scaling → Increased Capacity**
- Mechanism: Larger models learn more complex feature hierarchies with higher-dimensional representations
- Evidence: Beyond Chinchilla (Sardana et al. 2023) shows models continue improving to 10,000 tokens/parameter
- Falsification: Would break if scaling provides diminishing returns before representation capacity increases

**Link 2: Increased Capacity → Decreased Concept Alignment**
- Mechanism: High-dimensional distributed representations become less sparse relative to discrete concept vocabularies
- Evidence: Rate-distortion theory (Isik et al. 2021) shows compression-quality trade-off in neural networks
- Falsification: Would break if larger models maintain sparse, concept-aligned representations despite increased capacity

**Link 3: Decreased Concept Alignment → Lower Interpretability**
- Mechanism: MI between representations φ(x) and concepts C decreases when representations encode task-specific but concept-orthogonal features
- Evidence: CLUB estimator (Cheng et al. 2020) provides reliable MI measurement for this assessment
- Falsification: Would break if interpretability can be measured independently of concept alignment

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Beyond Chinchilla (Sardana et al. 2023) | LLMs continue improving at extreme token/parameter ratios (up to 10,000) | Strong |
| Step2 → Step3 | Rate-Distortion for NN (Isik et al. 2021) | Rate-distortion theory applies to NN compression; pruning achieves theoretical limits | Strong |
| Step3 → Outcome | CLUB Estimator (Cheng et al. 2020) | Contrastive Log-ratio Upper Bound provides reliable MI estimation in high dimensions | Strong |

**Key Tension:**
- Tension: Rate-distortion theory suggests a fundamental trade-off, but recent work on concept bottleneck models shows that explicit concept regularization can maintain interpretability during scaling
- Resolution: This verification plan tests whether the Pareto frontier can be navigated (via multi-objective optimization) or is fundamentally constrained

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Scientific concepts can be enumerated via domain ontologies | ChEBI: 170k+ entities; GO: 44k+ terms; CMIP6: standardized variables; Materials Project: composition descriptors | Framework would require alternative concept extraction (e.g., learned concepts) |
| A2 | MI between representations and concepts is estimable via CLUB | Cheng et al. 2020 ICML: theoretical guarantees + practical implementation (github.com/Linear95/CLUB) | Would need alternative interpretability metric (e.g., feature attribution, probing) |
| A3 | Genuine trade-off exists (Pareto frontier structure) | Rate-distortion theory; AlphaFold achieves accuracy but limited interpretability | If no trade-off exists, framework provides trivial solution (maximize both) |
| A4 | Surrogate models can predict (accuracy, interpretability) | Consistency distillation shows model-to-model prediction works; standard in NAS | Would require full MO-NAS (10-100x compute increase) |

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Scientific AI domains with well-defined concept vocabularies (molecular, climate, protein, materials)
- Models with intermediate representations that can be probed for concept alignment
- Domains where interpretability is valued alongside prediction accuracy

**Where Hypothesis Does NOT Apply:**
- Open-ended scientific discovery where concepts are not predefined
- Domains without established ontologies (e.g., emerging scientific fields)
- Real-time inference scenarios where MI estimation is too expensive
- Black-box models without accessible intermediate representations

**Known Limitations:**
- CLUB estimator provides upper bound, not exact MI (acknowledged proxy)
- Surrogate Pareto learning may miss non-smooth regions of the frontier
- Cross-domain generalization requires retraining surrogates
- Concept vocabulary completeness varies by domain

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Pareto Frontier Existence):**
If model architectures are varied systematically while measuring both task accuracy and interpretability (MI with concepts), then the resulting (accuracy, interpretability) pairs will trace a Pareto frontier with hypervolume indicator > 0.5 (normalized), demonstrating a genuine trade-off.

*Measurement*:
- Hypervolume indicator > 0.5 with p < 0.05
- Statistical test: Bootstrap confidence intervals over 20+ architecture samples
- Domain: At least 2 of 4 target domains (MoleculeNet, ClimateLearn, ProteinGym, MatBench)

*Success Criteria for Phase 2B*:
- Primary: Hypervolume > 0.5 in majority of domains
- Falsification: Hypervolume ≤ 0.3 across all domains (no meaningful trade-off)

**Secondary Predictions:**

**P2 (Surrogate Efficiency):**
Surrogate Pareto Learning will achieve ≥90% of full MO-NAS hypervolume coverage at ≤10% of the computational cost.

**P3 (Cross-Domain Generalizability):**
Qualitatively similar Pareto frontier shapes will emerge across all 4 scientific domains, with Spearman correlation ≥ 0.7.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Hypervolume ≤ 0.3 in all 4 domains (No meaningful Pareto frontier exists)

2. **Mechanism Failure**: CLUB estimation fails to correlate with human interpretability judgments (Spearman ρ < 0.3)

3. **Surrogate Failure**: Surrogate predictions have R² < 0.5 with actual (accuracy, interpretability) values

### 1.7 SOTA Baseline (Optional)

*Not applicable - This hypothesis proposes a new framework/methodology rather than performance improvement.*

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 architecture samples per domain
**Statistical Tests:**
- Hypervolume: Bootstrap 95% CI with 1000 resamples
- Surrogate accuracy: 5-fold cross-validation with R² metric
- Cross-domain: Spearman rank correlation with permutation test
- Significance level: α = 0.05

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does a quantifiable Pareto frontier exist between prediction accuracy and MI-based interpretability in scientific AI models?"
- Maps to: Primary prediction P1
- Verification type: Empirical (hypervolume measurement)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the scaling → capacity → alignment → interpretability causal chain the actual mechanism underlying the trade-off?"
- Maps to: Causal mechanism (N=3 steps)
- Verification type: Causal analysis (ablation studies)
- Phase 2B will decompose into:
  - H-M1: Scaling increases representation capacity
  - H-M2: Increased capacity decreases concept alignment
  - H-M3: Decreased alignment reduces MI-based interpretability

**SH3 (Comparison):**
"Does Surrogate Pareto Learning achieve ≥90% hypervolume at ≤10% compute cost compared to full MO-NAS?"
- Maps to: Secondary prediction P2
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-RDIF-v1
- [x] Confidence level specified: 0.81
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Causal chain length (N=3) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2/P3 secondary)
- [x] Falsification criteria are defined
- [x] Baselines identified (Full MO-NAS, AlphaFold, PINNs)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** Estimated 100-500 GPU-hours for initial architecture sampling + surrogate training across 4 domains.

2. **Data Availability:** Verify access to MoleculeNet, ClimateLearn, ProteinGym, MatBench with sufficient samples.

3. **Priority Verification Order:** SH1 (Existence) first - if Pareto frontier doesn't exist, framework is invalidated.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
