# Phase 2C Checklist: h-m1

**Hypothesis ID**: h-m1  
**Generated**: 2026-08-24  
**Phase**: 2C (Experiment Design)

---

## Document Completion

- [x] **Experiment Brief** (`02c_experiment_brief.md`)
  - [x] Hypothesis statement
  - [x] Dataset specification (Waterbirds, standard, real dataset)
  - [x] Baseline architectures (ResNet-18-BN, ResNet-18-LN)
  - [x] Gradient flow measurement protocol
  - [x] Training configuration (controlled variables)
  - [x] Evaluation protocol (gradient ratio, statistical test)
  - [x] Success/falsification criteria
  - [x] Expected outcomes
  - [x] Complexity assessment (Tier 1.5, 350-550 tokens)
  - [x] Risks and mitigations

- [x] **Hypothesis Summary** (`hypothesis_summary.md`)
  - [x] Statement
  - [x] Prerequisites (h-e1 validated)
  - [x] Causal mechanism
  - [x] Test method
  - [x] Success/falsification criteria

- [x] **Research Context** (`research_context.md`)
  - [x] Main hypothesis connection
  - [x] Related work (BN literature, spurious correlation literature)
  - [x] Novel contribution
  - [x] Open questions
  - [x] Connection to future hypotheses (h-m2, h-c1)

- [x] **Implementation Requirements** (`implementation_requirements.md`)
  - [x] Code reuse from h-e1 (data loader, models, training loop, evaluation)
  - [x] New components (gradient hooks, group gradients, enhanced training, analysis, visualization)
  - [x] File structure
  - [x] Dependencies (no new dependencies)
  - [x] Computational requirements
  - [x] Quality assurance checklist
  - [x] Phase 3 deliverables preview

---

## Experiment Design Validation

### Dataset Quality
- [x] Real dataset (not synthetic): Waterbirds from WILDS benchmark
- [x] Statistically meaningful sample size: 600 test samples, 10 seeds
- [x] Reuses h-e1 dataset (efficiency gain, consistency)

### Hypothesis Alignment
- [x] Experiment measures hypothesis claim: gradient ratio (spurious/core) in early training
- [x] Mechanistic test: batch-level vs instance-level statistics hypothesis
- [x] Controlled variables match Phase 2B: LR=0.01, batch size=64, 10 seeds

### Falsifiability
- [x] Clear success criterion: BN gradient ratio ≥20% higher, p<0.05, Cohen's d≥0.5
- [x] Clear falsification criterion: p>0.05 OR BN ratio <10% higher OR Cohen's d<0.3
- [x] Independent t-test (not paired; BN and LN are independent models)

### Complexity Justification
- [x] Tier 1.5 complexity justified: gradient hooks add moderate complexity (~100 LoC)
- [x] Budget estimate reasonable: 350-550 tokens (80% code reuse from h-e1)
- [x] No over-engineering: uses standard backward hooks, no custom autograd

---

## Gate Alignment

- [x] **Gate Type**: SHOULD_WORK (mechanism hypothesis)
- [x] **Does NOT block Phase 5 if fails**: Documented in experiment brief
- [x] **Prerequisite validated**: h-e1 PASSED (9.41pp gap, p<0.001)

---

## Code Reuse Strategy

- [x] Identified reusable h-e1 components: data_loader, models, train, evaluate
- [x] Estimated reuse: 80% (saves ~200 LoC, ~2-3 days implementation time)
- [x] New components clearly separated: gradient_hooks, group_gradients, analyze_gradients

---

## Risks Assessed

- [x] Gradient measurement noise → mitigation: 10 seeds, 5-epoch smoothing
- [x] Spurious/core feature proxy validity → mitigation: majority/minority group gradient
- [x] Computational overhead → mitigation: measure gradients on validation set only
- [x] h-e1 code availability → mitigation: h-e1 already validated in Phase 4

---

## Open Questions Addressed

- [x] Feature definition (spurious vs core): Majority/minority group proxy
- [x] Gradient measurement approach: Backward hooks on normalization layers
- [x] Statistical power: 10 seeds, independent t-test
- [x] Null result interpretation: BN-LN gap exists but mechanism unclear (does NOT invalidate h-e1)

---

## Phase 3 Readiness

- [x] Experiment brief is self-contained (Phase 3 can proceed without clarification)
- [x] All design decisions documented (dataset, architectures, metrics, statistical test)
- [x] Archon task breakdown previewed (EPIC-GRAD-HOOKS, EPIC-GROUP-SPLIT, etc.)
- [x] Success criterion is measurable (gradient ratio, p-value, effect size)

---

## Checklist Summary

**Total Items**: 35  
**Completed**: 35  
**Completion Rate**: 100%

**Phase 2C Status**: COMPLETED  
**Ready for Phase 3**: YES  
**Blocking Issues**: NONE

---

## Sign-off

**Experiment Design Reviewed**: 2026-08-24  
**Reviewer**: Automated checklist (Phase 2C validation)  
**Approval**: APPROVED for Phase 3 (Implementation Planning)

**Next Phase**: Phase 3 (Implementation Planning)
- Generate PRD, Architecture, Logic, Config documents
- Initialize Archon project with experiment brief
- Break into Epic-level tasks
- Estimate 350-550 token budget (Tier 1.5)
