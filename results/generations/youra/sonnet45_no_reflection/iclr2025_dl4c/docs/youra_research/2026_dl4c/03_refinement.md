# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-11T10:58:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap_1
- **Gap Title**: Unified Multi-Objective Alignment for Code Generation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 15

**Convergence Reason**: Established fully falsifiable, end-to-end causal chain from outcome-space geometry → representation alignment → architectural factorization → controllable multi-objective behavior, with permutation, rotation, purity, and human counterfactual tests

### Key Insights

- **Paradigm shift**: From "optimize better" (weight-tuning) to "represent better" (geometry discovery). If separability exists, alignment becomes discovering natural axes of improvement embedded in human code evolution, not just preference aggregation.

- **Complete falsifiable pipeline**: Every phase has pre-registered success/failure criteria with clear pivots. If Phase 0 metrics fail validation, stop. If Phase 1 shows flat spectrum, publish negative result that multi-objective code alignment is intrinsically entangled.

- **Negative results equally valuable**: Proving intrinsic entanglement redirects field toward co-adaptive methods that embrace coupling rather than fighting it. Either outcome (latent alignment or intrinsic entanglement) meaningfully advances understanding.

- **Causal chain across four levels**: Hypothesis requires alignment at outcome level (spectral structure), representation level (CCA), architectural level (sample-efficiency gap), and behavioral level (controllability bands + human discrimination).

### Breakthrough Moments

- **Exchange 5 (Dr. Sage)**: Reframing contribution from "escaping Pareto frontier" to "discovering whether code aspects are empirically less conflicting than assumed" made hypothesis testable with clear empirical falsification.

- **Exchange 9 (Prof. Rex)**: Adding spectral gap criterion (λ₄/λ₅>2.0) + permutation test + directional stability transformed separability from architectural intuition to falsifiable empirical claim with statistical rigor.

- **Exchange 14 (Prof. Rex)**: Identifying the metric-representation gap led to CCA bridge test, completing the causal chain from outcome space to model internal geometry.

- **Exchange 15 (Prof. Pax)**: Demonstrating feasibility of all refinements (~100 GPU-hours + $2K + 2× training runs) kept hypothesis practical while maintaining rigor.

---

## Final Hypothesis

### Title
**Geometry-First Alignment: Exploiting Empirically Validated Aspect-Dominant Structure for Post-Training Multi-Objective Controllability in Code Generation**

### Core Claim

Under multi-objective code generation contexts (correctness, quality, security, efficiency), if human expert code modifications exhibit aspect-dominant directional structure in outcome space (validated via spectral analysis of commit-level causal edits with representation-space alignment), then aspect-factorized policy architectures (gated LoRA adapters with orthogonality constraints) enable post-training multi-objective controllability on existing benchmarks, because the model exploits empirically discovered latent geometry that mirrors human expert cognitive factorization of programming concerns.

### Mechanism

The framework operates through a **four-phase causal chain**:

1. **Human Cognitive Factorization → Low-Rank Outcome Structure**  
   Developers mentally factorize concerns (security fixes affect security dominantly, refactors affect quality dominantly). This manifests as low-rank structure in metric delta space: spectral gap λ₄/λ₅>2.0, median cross-aspect effects ≤0.2× primary effects, directional stability under projection (z-score >2.0).

2. **Outcome Structure → Model Representation Alignment**  
   Pretrained code models encode patterns from similar human-authored code. Metric eigenvectors align with representation principal directions (CCA >0.7 for ≥3/4 aspects at middle-late layers), establishing that model's internal geometry reflects outcome structure.

3. **Natural-Axis Training → Sample Efficiency**  
   Aspect-specific gated adapters trained on discovered natural axes exploit aligned geometry more efficiently than arbitrary rotated axes (30% fewer steps to controllability threshold), demonstrating architectural inductive bias matches discovered structure.

4. **Learned Subspaces → Post-Training Controllability**  
   Steering along learned aspect subspaces enables controllable multi-objective behavior: local bands with width ≥1.0 (monotonic target improvement, <5% correctness degradation), human discrimination ≥60% (correct vs mismatched aspect steering), robustness under distribution shift (security-CTF, refactoring tasks).

---

## Predictions

### P1: Empirical Separability (Primary)
**Statement**: Real-world labeled commits exhibit aspect-dominant structure with median cross-aspect effect ≤0.2× primary effect and spectral gap λ₄/λ₅ > 2.0

**Test Method**: Collect 10K minimal-diff commits (AST distance <20) with labels (security, refactor, performance, bugfix). Compute residual covariance after regressing on edit-size and file-entropy confounds. Perform eigenanalysis + permutation test (1000 label shuffles) + directional stability (project commits onto eigenvectors) + leave-one-repo-out analysis.

**Success**: Cross-effects ≤0.2× (95% CI), spectral gap exceeds 95th percentile of permutation null, on-axis projection z-score >2.0, eigenvector angles shift <15° across repository folds

**Falsification**: Flat spectrum (λ₄/λ₅ ≤ 2.0), failed permutation test, or cross-effects >0.3× → latent alignment doesn't exist → publish negative result, pivot to co-adaptive methods

### P2: Representation-Metric Alignment (Primary)
**Statement**: Metric eigenvectors align with model representation principal directions (CCA > 0.7 for ≥3/4 aspects) at middle-late transformer layers

**Test Method**: Freeze CodeLlama-7B, pass pre/post-commit code through model, extract Δh at layers [8,16,24]. Compute CCA between metric eigenvectors (from P1) and representation PCA directions at each layer.

**Success**: CCA coefficients >0.7 for at least 3 out of 4 aspects at any layer (typically layers 16-24)

**Falsification**: CCA <0.5 across all aspects/layers → model geometry doesn't reflect outcome structure → architectural factorization becomes external supervision not latent discovery (still useful, different theoretical claim)

### P3: Sample-Efficiency Gap
**Statement**: Gated aspect-specific adapters trained on natural axes reach controllability threshold 30% faster than rotated-axes training

**Test Method**: Train both natural-axis and rotated-axis configurations for fixed 50K steps. Measure (1) step at which controllability band width ≥1.0 first achieved, (2) final controllability metrics. Also run rotation test: train on randomly rotated metric space, measure degradation.

**Success**: Natural-axes reaches threshold in ≥30% fewer steps AND achieves better final performance, plus rotation test shows >30% degradation under random rotation

**Falsification**: No sample-efficiency gap or no degradation under rotation → architecture is flexible not structure-aligned → simpler architecture may suffice

### Graded Predictions (Explanatory Framework)
Based on software engineering knowledge, predict ex ante:
- **High separability** (cross-effect <0.15×): Correctness vs Quality (different properties: tests vs structure)
- **Moderate separability** (0.15-0.25×): Security vs Quality, Security vs Correctness (some overlap: validation affects both)
- **Low separability** (0.25-0.35×): Efficiency vs Correctness (optimization can break algorithms)

If empirical results match rank-order, framework is explanatory not just descriptive.

---

## Novelty

### Key Innovation
**Three-part contribution**:

1. **Empirical discovery**: First systematic quantification of aspect-dominant structure in real code modifications via spectral analysis with directional stability tests, permutation significance, and representation-space alignment validation (CCA)

2. **Architectural innovation**: Gated aspect-factorized adapters (LoRA + learned sparse routing) validated through rotation test (proves exploitation of natural geometry vs imposed flexibility) and ablations (isolates factorization contribution)

3. **Validation methodology**: Establishes new standard for multi-objective alignment claims through permutation-tested separability + sample-efficiency gaps + counterfactual human discrimination tests

### Differentiation

**vs. Standard weighted multi-objective RL**: We validate data-level separability FIRST, then exploit discovered structure. Weighted methods assume conflicting objectives and require per-domain tuning. We discover whether conflict exists empirically.

**vs. General disentanglement literature**: We apply to *alignment* (not just representation learning) for *code generation* (not general tasks) with *intervention-based validation* (not just probing) and demonstrate *post-training controllability* tied to human code review feedback.

**vs. PPOCoder (Shojaee et al. 2023)**: PPOCoder optimizes single objective (execution correctness). We discover and exploit multi-aspect structure with post-training controllability unavailable in single-objective or weight-tuned approaches.

---

## Experimental Design

### Datasets
- **GitHub Commit Corpus**: 10K minimal-diff commits (AST distance <20) with aspect labels (security, refactor, performance, bugfix), validated purity >70% via expert annotation (n=500 subset)
- **HumanEval, MBPP**: Function-level code generation benchmarks
- **Security-CTF tasks**: Adversarial security scenarios for distribution shift testing
- **Refactoring benchmarks**: Long-horizon maintenance tasks for robustness validation

### Models
- **Base**: CodeLlama-7B (frozen for representation analysis, fine-tuned with LoRA for experiments)
- **Variants**: LoRA-only, LoRA+orthogonal, LoRA+gated routing (≤2 aspects per token)
- **Baselines**: 25 weighted PPOCoder configurations (grid search over [0,1]^4 weight space)

### Metrics
- **Correctness**: HumanEval/MBPP pass@1 (unit test pass rate)
- **Quality**: SonarQube maintainability index
- **Security**: CodeQL alert count
- **Efficiency**: pytest-benchmark execution time and memory profiling

### Validation Pipeline
**Phase 0**: Metric validation (ICC≥0.8, construct validity r≥0.7, discriminability)  
**Phase 1A**: Empirical separability (covariance, eigenanalysis, permutation, directional stability, leave-one-repo-out)  
**Phase 1B**: Representation alignment (CCA at layers [8,16,24])  
**Phase 1C**: Commit purity (expert annotation n=500, mixture correction if <70%)  
**Phase 2**: Architecture training (natural vs rotated axes, ablations, sample-efficiency measurement)  
**Phase 3**: Controllability (steering bands, human discrimination n=100)  
**Phase 4**: Pareto dominance (effect-size criterion ≥0.5 SD) + distribution shift

---

## Limitations

### Known Constraints
- Requires ≥10K labeled commits for stable covariance estimation
- Spectral analysis assumes commits sample underlying aspect-dominant manifold - repository clustering may affect stability (tested via leave-one-repo-out)
- Controllability assumes local linearity in steering space - controllability bands characterize valid range, beyond which nonlinearity expected
- Human validation limited to n=100 code review tasks - tests semantic alignment but not exhaustive coverage

### Remaining Concerns (from Prof. Rex)
1. **Weak representation-metric alignment** (CCA <0.5): Would shift theoretical story from "exploiting latent model geometry" to "imposing external structure via supervised regression" - still useful but different claim
2. **Multi-aspect commits** (purity <70%): Could induce spurious separability through mixture artifacts - requires mixture modeling with expert-weighted covariance correction

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Complete falsifiable causal chain with pre-registered criteria at every phase |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Two concerns with clear mitigation strategies (see above) |

### Verdict Summary
- **Novelty**: STRONG (geometry-first alignment paradigm, generalizable methodology)
- **Falsifiability**: STRONG (pre-registered criteria, permutation tests, rotation tests, human discrimination)
- **Significance**: STRONG (field-shaping if successful, valuable negative result if failed)
- **Feasibility**: STRONG (100 GPU-hours + $2K, all existing tools/benchmarks)

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
