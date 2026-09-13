# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-20T00:00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap_1
- **Gap Title**: Lack of Systematic Cross-Paradigm Benchmarking of UQ Methods Under Controlled LLM Architecture Variations
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16
- **Hypothesis ID**: H-EGSH-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: All six criteria met — SPECIFIC core claim, MECHANISM (4-step causal chain), PREDICTIONS (P1-P3+D with quantitative thresholds), NOVELTY (G_corrected and d_50 as new metrics), FEASIBILITY (all infrastructure confirmed), OBJECTIONS (training confound, dimensionality artifact, output diversity, argmax instability all addressed)

### Key Insights
- The research question reframing — from "which UQ method ranks first?" to "how does uncertainty reorganize with scale?" — is the central novelty
- Convergence across three independent diagnostic types (AUROC interaction + probe gap + MI depth) is required to claim structural reorganization; any single diagnostic is insufficient
- Permutation-corrected layer-wise probe gap G_corrected(l) is a new methodological contribution that isolates epistemic accessibility from generic representational expressiveness
- Training-regime confound (different pretraining at 8B vs 70B) is irreducible but bounded — base-model control mitigates RLHF; within-scale instruct comparison provides additional discriminant
- TruthfulQA attenuation (P4) makes the hypothesis more precise, not weaker — it defines the scope boundary between factual retrieval and adversarial misconception settings

### Breakthrough Moments
- **Exchange 4 (Prof. Rex)**: Identified that the hypothesis conflated a ranking claim (testable by AUROC) with a mechanistic claim (requires internal diagnostics) — led to adding KLE and SelfCheck scorer stratification
- **Exchange 7 (Prof. Pax)**: Proposed layer-wise mutual information analysis — transformed a confound control into the primary mechanistic finding (d* depth shift)
- **Exchange 13 (Prof. Pax)**: Proposed nonlinear MLP probe baseline and decodability inflation factor — closed the geometry-vs-information gap
- **Exchange 15 (Prof. Rex)**: Proposed cumulative-MI depth quantile d_50 and layer-wise permutation correction G_corrected(l) — eliminated argmax instability concern and coarse-correction artifact

---

## Final Hypothesis

### Title
**Epistemic Geometry Scaling Hypothesis (EGSH)**

### Core Claim
Under the Llama-3 model family evaluated on standard factual QA benchmarks (TriviaQA, NaturalQuestions), if model scale increases from 8B to 70B base checkpoints while holding dataset splits, evaluation harness, and benchmark conditions fixed, then semantic-structural UQ methods (SE, KLE) will show a significantly larger AUROC advantage over token-probability than at smaller scale, AND correctness-predictive information will shift to deeper transformer layers — because larger model capacity enables richer semantic equivalence class representations that surface-level token distributions cannot capture.

**H0 (Null)**: There is no significant method × scale interaction; all UQ methods scale proportionally, preserving relative AUROC rankings (no migration, no depth shift).

### Mechanism
1. Larger model capacity enables richer semantic equivalence class representations in deeper transformer layers (analogous to vision transformer feature hierarchies)
2. Token-probability saturates as a UQ signal as scale increases because lexical ambiguity is compressed; semantic-level aggregators (SE, KLE) capture the remaining uncertainty at the equivalence-class level
3. This semantic-structure advantage manifests as a method × scale AUROC interaction: Δ_70B > Δ_8B
4. Linear/nonlinear decodability of correctness from hidden states increases with scale at deeper layers (probe gap narrows, d_50 shifts deeper)

---

## Predictions

| ID | Primary | Statement | Success Criterion | Falsification |
|----|---------|-----------|------------------|---------------|
| P1 | ✅ | AUROC advantage of SE and KLE over token-prob widens from 8B to 70B on TriviaQA and NQ | Δ > 0.02 with 95% bootstrap CI excluding zero on both datasets, both base variants | Δ ≤ 0.02 or CI includes zero on either dataset for both SE and KLE |
| P2 | ❌ | Partial correlation between SelfCheck-NLI and SE increases from 8B to 70B after controlling for lexical diversity; BERTScore shows smaller increase | Partial correlation (SelfCheck-NLI, SE) increases significantly; BERTScore partial correlation smaller | BERTScore and NLI show equivalent partial correlation increases (diversity artifact) |
| P3 | ❌ | Permutation-corrected probe gap G_corrected(l) narrows and d_50 shifts deeper at 70B | d_50_70B > d_50_8B with 95% CI; effect persists under JL-projection dimensionality control | d_50 does not shift or shifts shallower; JL-projection eliminates the effect |
| P4 | ❌ | Method × scale interaction attenuated on TruthfulQA vs TriviaQA/NQ | Δ on TruthfulQA significantly smaller than on TriviaQA and NQ | Δ on TruthfulQA equivalent to factual retrieval benchmarks |

---

## Novelty

**What's new**: No prior work treats scale as the independent variable for UQ method comparison or measures internal representational depth reorganization as a function of scale. The UQ survey [Kang et al. 2025] identifies evaluation fragmentation as the key limitation — EGSH directly addresses it.

**Methodological contributions**:
1. Permutation-corrected layer-wise probe gap G_corrected(l) = G_true(l) − G_perm(l) — isolates epistemic accessibility from generic representational expressiveness
2. Cumulative-MI 50th-percentile depth d_50 — scale-robust depth measure robust to argmax instability
3. Convergent multi-diagnostic framework (external AUROC interaction + internal depth shift) for structural UQ claims

**Differentiation from prior work**:
- vs SE [Farquhar et al. 2024]: SE evaluates at fixed scale; EGSH uses scale as IV and adds internal depth diagnostics
- vs SEPs [Kossen et al. 2024]: SEPs vs generative SE at fixed scale; EGSH tests how probe-generative gap changes with scale
- vs LM-Polygraph: compares methods but does not test scale as variable or measure representational depth
- vs Kang et al. 2025 survey: identifies fragmentation as problem; EGSH provides the controlled solution with mechanistic diagnostics

---

## Experimental Design

**Models**: Llama-3-8B-Base, Llama-3-70B-Base (primary); Llama-3-70B-Instruct (within-scale control)

**Datasets**: TriviaQA (rc.nocontext), NaturalQuestions (open-domain), TruthfulQA (mc1, scope test)

**UQ Methods** (all applied through UQLM unified harness):
- Token-probability (max softmax)
- SelfCheckGPT-BERTScore (N=10)
- SelfCheckGPT-NLI (N=10, stratified for P2)
- Semantic Entropy — jlko/semantic_uncertainty (N=10)
- Kernel Language Entropy (KLE) — Nikitin et al. 2024
- Semantic Entropy Probes (linear) — OATML/semantic-entropy-probes
- 2-layer MLP probe (1024 hidden, ReLU, 5-fold CV, fixed hyperparameters)

**Key Controls**:
- Base vs instruct 70B: separates scale-driven from post-training effects
- JL-projection (70B → 8B dimensionality): rules out feature-count advantage in probes
- Layer-wise permutation baselines: rules out generic representational expressiveness inflation
- Lexical diversity partial correlation: rules out output-diversity inflation in SelfCheck-SE convergence
- Two-way ANOVA interaction term: distinguishes reorganization from uniform scaling

---

## Limitations

- Two-point scale comparison (8B, 70B) is correlational; cannot prove scale causes reorganization
- Training-data mixture and optimization schedule differences between 8B/70B checkpoints are irreducible confounds even with base-model controls
- Layer-wise MI estimation at 70B scale is computationally intensive; probe-based approximations require validation on small-scale sanity checks first
- Results scoped to Llama-3 family on factual QA; generalization to other families requires separate validation
- Forward-looking intervention prediction (late-layer regularizer asymmetry) is not part of Phase 2B experiment — deferred to Phase 2C/3

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-EGSH-v1 |
| **Discussion Convergence** | Converged at exchange 16 (all 6 criteria met) |
| **Clarity Verified** | Yes |
| **Feasibility Confirmed** | Yes (all infrastructure exists) |
| **Phase 2B Ready** | Yes |
| **Remaining Objections** | Training-data confound (scoped); MI validation at 70B (Phase 2B prerequisite); intervention prediction (Phase 2C) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Pipeline: YouRA Research — Uncertainty Quantification in Foundation Models*
