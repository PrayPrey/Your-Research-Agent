# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-06
**Author:** Pray
**Research Topic:** Scientific Methods for Understanding Deep Learning (NeurIPS 2024)
**Hypothesis ID:** H1 - Universal Computational Motif Library
**Confidence:** 0.815
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis**: Deep learning architectures exhibit conserved computational motifs (information convergence, multiplicative gating, residual bypass patterns) across structurally different implementations. A universal motif library combined with graph neural network-based pattern detection can enable automated mechanistic discovery across transformers, diffusion models, and state space models by recognizing functional graph patterns rather than architecture-specific circuits.

**Key Innovation**: Shifts mechanistic interpretability from architecture-specific circuit tracing to architecture-agnostic motif detection, inspired by neuroscience conserved synaptic motifs in biological connectomics.

**Gap Addressed**: Gap 2 (Automated Tools for Mechanistic Discovery Across Architectures)

**Implementation Difficulty**: MEDIUM (7-12 weeks, 4 phases with pilot study de-risking)

---

## Core Testable Predictions

| ID | Prediction | Success Criterion | Falsification Criterion |
|----|------------|------------------|------------------------|
| **P1** | Motif conservation across architectures | ≥70% conservation rate (pilot study) | <50% conservation → H0 accepted |
| **P2** | On-architecture performance | F1 ≥ 0.80 vs ACDC baseline | F1 < 0.70 OR >15% worse than ACDC |
| **P3** | Cross-architecture generalization | Zero-shot F1 ≥ 0.60, exceeds HAGD 67% | F1 < 0.40 on either unseen architecture |
| **P4** | Interpretability preservation | Expert rating ≥ 4.0/5.0 | Mean score < 3.5 OR <60% rated ≥4 |

---

## Variables

**Independent**:
- Architecture Type: {GPT-2, DiT, Mamba}
- Motif Type: {Information Convergence, Multiplicative Gating, Residual Bypass}

**Dependent**:
- Motif Detection Accuracy (F1 Score)
- Cross-Architecture Generalization (Transfer Accuracy)
- Interpretability Quality (5-point Likert scale)

**Controlled**:
- Model Size: 100M-1B parameters
- Training Data: 50-100 labeled instances per motif
- GNN Architecture: 3-5 layers, 128-256 hidden dimensions

---

## Causal Mechanism

```
Functional Requirements (task-imposed)
    ↓
Architectural Implementations (structure-specific)
    ↓
Computational Graph Patterns (conserved motifs)
    ↓
GNN Pattern Learning (functional equivalence)
    ↓
Cross-Architecture Discovery (automation)
```

**Critical Assumption**: Computational motifs are functionally conserved despite architectural differences (testable via pilot study P1).

---

## Key Assumptions

1. **Motif Conservation** (HIGH RISK): Motifs conserve ≥70% across architectures → Tested via pilot study (P1)
2. **GNN Capability** (MEDIUM RISK): GNNs can learn functional equivalence from graph structure → Tested via zero-shot evaluation (P3)
3. **Training Data Sufficiency** (LOW RISK): Existing papers provide 50-100+ labeled instances per motif → Validated by manual extraction
4. **Graph Representation Adequacy** (LOW RISK): Computational graphs capture motif structure → Standard autodiff representation

**De-Risking Strategy**: Pilot study (Week 2-4) validates Assumption 1 before full GNN implementation.

---

## Sub-Hypothesis Preview (Phase 2B Decomposition)

**SH1 (Existence)**: Computational motifs are conserved across GPT-2, DiT, Mamba with ≥70% conservation rate
- **Verification**: Manual expert annotation, inter-rater reliability (Cohen's kappa ≥ 0.70)
- **Success**: Mean conservation ≥ 0.70
- **Failure**: Conservation < 0.50 → Pivot to architecture-family-specific libraries

**SH2 (Mechanism)**: GNN learns architecture-agnostic motif representations enabling zero-shot detection
- **Verification**: Train on GPT-2, test zero-shot on DiT/Mamba
- **Success**: On-arch F1 ≥ 0.80, cross-arch F1 ≥ 0.60
- **Failure**: F1 < 0.60 → GNN learning insufficient, try alternative detection methods

**SH3 (Comparison)**: Motif detection matches ACDC (on-arch) and exceeds HAGD (cross-arch) while preserving interpretability
- **Verification**: Benchmark comparisons + expert evaluation
- **Success**: ACDC parity (within 5% F1), HAGD superiority (>67%), interpretability ≥4/5
- **Failure**: Underperforms baselines → Method works but doesn't improve SOTA

**Causal Chain**: SH1 → SH2 → SH3 → Main Hypothesis Validated

---

## Contributions

### Theoretical
1. **Motif-Level Abstraction**: New abstraction level between circuits (too specific) and features (too coarse) for mechanistic interpretability
2. **Cross-Domain Bridge**: Formalizes neuroscience conserved synaptic motifs → DL computational motifs mapping
3. **Universality Hypothesis**: Core computational functions manifest as conserved graph patterns across architectures

### Methodological
1. **Universal Motif Library Framework**: Systematic curation of architecture-agnostic motifs from literature
2. **GNN-Based Cross-Arch Detection**: First application of GNNs to mechanistic interpretability with zero-shot generalization
3. **Pilot Validation Protocol**: Rigorous de-risking via conservation rate measurement before full implementation
4. **Comprehensive Baseline Comparison**: Multi-faceted evaluation (on-arch vs ACDC, cross-arch vs HAGD, interpretability vs manual)

### Practical
1. **Automated Tool**: ~99% time reduction per model (8 weeks → <1 hour) after initial setup
2. **Cross-Architecture Toolkit**: Single unified tool works across transformers, diffusion, SSM (eliminates architecture-specific expertise barrier)
3. **Architecture Design Insights**: Mechanistic comparisons inform design decisions (e.g., "Model A uses 40% more convergence motifs → better for multi-source integration tasks")

---

## Baselines

| Baseline | Task | Metric | Expected Outcome |
|----------|------|--------|------------------|
| **ACDC** | Modular arithmetic (GPT-2) | F1 score | Match within 5% (≥0.80 F1) |
| **HAGD** | Cross-arch generalization | Transfer accuracy | Exceed 67% similarity (≥0.60 F1) |
| **Manual Analysis** | Interpretability quality | Expert rating (5-point) | Match gold standard (≥4.0/5) |

---

## Related Work Positioning

**Closest Existing Work**:
- **ACDC** (Conmy 2023): Automates circuit discovery but architecture-specific → This adds cross-arch capability
- **HAGD** (2026): Cross-arch via attribution graphs, 67% similarity → This aims for >70% via motif abstraction
- **Grokking** (Nanda 2023): Manual reverse-engineering → This provides training data for motif library

**Unique Contributions**:
- First motif-level abstraction for mechanistic interpretability
- First GNN-based cross-architecture motif detection
- First rigorous pilot study for motif conservation validation
- First unified framework combining on-arch quality + cross-arch generalization

**Gap Filled**: Addresses Phase 1 Gap 2 (automated cross-architecture mechanistic discovery) via novel motif abstraction paradigm.

---

## Statistical Design Summary

**Sample Sizes**:
- Training: 150-1000 labeled motif instances (50-100 per motif × 3-10 motifs)
- Test: 50-100 instances per architecture (GPT-2, DiT, Mamba)

**Statistical Tests**:
- P1: One-sided binomial test (conservation ≥ 0.70, α=0.05)
- P2: One-sided binomial test (F1 ≥ 0.80) + paired t-test vs ACDC
- P3: One-sided binomial test (F1 ≥ 0.60) + two-sample t-test vs HAGD, Bonferroni correction (α=0.025 per architecture)
- P4: One-sample t-test (mean ≥ 4.0) + inter-rater reliability (Cohen's kappa ≥ 0.70)

**Reproducibility**:
- Code/data release (GitHub, MIT license)
- Fixed random seeds (3 seeds reported for variance estimation)
- Full hyperparameter documentation

---

## Implementation Plan (4 Phases, 7-12 Weeks)

**Phase 1: Motif Library Construction** (1-2 weeks)
- Extract 5-10 motifs from ACDC, grokking, attention analysis papers
- Codify as graph templates with functional semantics
- Manual effort: 1-2 weeks expert time

**Phase 2: Pilot Validation** (2-4 weeks) ⚠️ **CRITICAL DE-RISKING**
- Test motif conservation: 2-3 motifs across GPT-2, DiT, Mamba
- Success: ≥70% conservation → Proceed to Phase 3
- Failure: <50% conservation → Pivot to architecture-family-specific libraries

**Phase 3: GNN Detector Training** (2-3 weeks)
- Train GNN on labeled GPT-2 motifs
- 5-fold cross-validation for hyperparameter tuning
- Validate on held-out GPT-2 test set (P2)

**Phase 4: Cross-Architecture Evaluation** (2-3 weeks)
- Zero-shot inference on DiT, Mamba (P3)
- Baseline comparisons: ACDC (on-arch), HAGD (cross-arch)
- Expert evaluation: 3 experts × 50 motifs (P4)

---

## Scope Boundaries

**In Scope**:
- Architectures: GPT-2 (transformer), DiT (diffusion), Mamba (SSM)
- Motifs: Convergence, Gating, Residual Bypass (+ 2-7 more)
- Model Scale: 100M-1B parameters
- Validation: On-arch + cross-arch + interpretability

**Out of Scope**:
- CNNs, RNNs, GNNs (future work)
- Very large models (>10B params) - scalability unclear
- Automated motif discovery (library is manually curated)
- Causal attribution (detects motifs, doesn't explain causal role)
- Production deployment optimization

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Motif conservation fails (<50%) | HIGH | Pilot study gates full implementation; pivot condition to architecture-family-specific libraries |
| GNN learning insufficient | MEDIUM | Standard GNN architectures (PyTorch Geometric) + fallback to rule-based pattern matching |
| Training data collection too slow | MEDIUM | Realistic 1-2 week estimate; parallel expert annotation if needed |
| Baseline comparison unfavorable | MEDIUM | Even if not superior, unified tool is still valuable; focus on accessibility gains |

---

## Phase 2B Readiness Checklist

✅ Core hypothesis clearly stated (Main + Alternative H0)
✅ Variables operationally defined (Independent, Dependent, Controlled)
✅ Causal mechanism articulated with evidence
✅ Assumptions explicit and testable (pilot study de-risks critical assumption)
✅ Scope boundaries defined (in/out of scope)
✅ Testable predictions specified (P1-P4 with success/failure criteria)
✅ Falsification criteria explicit (< thresholds trigger pivot/failure)
✅ Baselines identified (ACDC, HAGD, manual analysis)
✅ Statistical design outlined (sample sizes, tests, α=0.05)
✅ Contributions clearly articulated (Theoretical, Methodological, Practical)
✅ Related work surveyed (10 key papers, positioning vs ACDC/HAGD)
✅ Sub-hypotheses preview-decomposed (SH1 → SH2 → SH3 causal chain)
✅ Implementation plan structured (4 phases, 7-12 weeks)
✅ Risks identified with mitigation strategies

---

## Open Questions for Phase 2B

1. **Motif Library Completeness**: Are 3-10 motifs sufficient coverage? (Measure % graph nodes in motifs)
2. **GNN Architecture Selection**: Which variant (GCN/GraphSAGE/GAT/GIN)? (Cross-validation comparison)
3. **Training Data Distribution**: Balanced vs frequency-weighted? (Test both, use focal loss if needed)
4. **Interpretability Evaluation**: How to ensure unbiased expert ratings? (Blind evaluation protocol)
5. **Motif Compositionality**: Do complex behaviors need compositional motifs? (Test motif pairs in SH2.5)
6. **Architecture Family Diversity**: Are transformer/diffusion/SSM sufficiently diverse? (Pilot study empirically tests)
7. **Alternative Motif Definitions**: What if chosen motifs are non-natural? (Sensitivity analysis in pilot)

---

## Next Steps

**Immediate Action**: Proceed to **Phase 2B - Detailed Verification Planning**

Phase 2B will decompose each sub-hypothesis (SH1, SH2, SH3) into detailed experimental protocols with:
- Step-by-step procedures
- Resource estimates (compute, time, expert effort)
- Success criteria per experiment
- Risk mitigation strategies
- Dependencies between experiments
- Timeline with milestones

**Expected Output**: Comprehensive verification roadmap ready for Phase 2C (Experiment Design) and Phase 3 (Implementation Planning).

---

## File References

**Full Document**: `02a_extended_hypothesis_full.md` (complete clarification with all details)

**Source Files**:
- Phase 0: `00_brainstorm_session.md`
- Phase 1: `01_targeted_research.md`
- Phase 2A: `02a_validated_hypotheses.md`, `02a_round_1_discussion.md`

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*Date: 2026-02-06*
*Hypothesis: H1 - Universal Computational Motif Library for Cross-Architecture Mechanistic Interpretability*
*Confidence: 0.815*
*Implementation Difficulty: MEDIUM*
*Status: ✅ Ready for Phase 2B*
