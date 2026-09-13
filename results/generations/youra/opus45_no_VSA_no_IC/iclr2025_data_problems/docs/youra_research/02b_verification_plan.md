# Phase 2B Verification Plan

## Main Hypothesis
**ID:** H-AttributionFingerprint-v1  
**Title:** Attribution Method Fingerprinting via Contrastive Mode Probing  
**Statement:** Different LLM data attribution methods exhibit characteristic and stable mode profiles—systematic patterns of sensitivity to memorization, feature transfer, and spurious association—that dissociate across methods and transfer across model families.

## Sub-Hypotheses

| ID | Type | Gate | Statement | Prerequisites | Status |
|----|------|------|-----------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | Attribution methods (TRAK, TracIn, Kronfluence) compute influence via mathematically distinct operations | None | READY |
| h-m1 | MECHANISM | MUST_WORK | Different mathematical operations create systematically different sensitivities to influence modes | None | READY |
| h-m2 | MECHANISM | MUST_WORK | Mode profiles exhibit dissociation: inter-method variance > intra-method variance (F > 4.0, d > 0.5) | h-m1 | NOT_STARTED |
| h-c1 | CONDITION | SHOULD_WORK | Mode profiles stable within methods: Cronbach's alpha > 0.8 | h-m1 | NOT_STARTED |
| h-c2 | CONDITION | SHOULD_WORK | Mode profiles transfer across model families: cross-model r > 0.7 | h-m1 | NOT_STARTED |

## Dependency Graph (DAG)

```
h-e1 (foundation)
    ↓
h-m1 (mechanism: operation → sensitivity)
    ├── h-m2 (primary prediction P1: dissociation)
    ├── h-c1 (stability P2)
    └── h-c2 (transfer P3)
```

## Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| TracIn LLM adaptation | Medium | Adapt checkpoint-based method for LLM setting; fallback to 2-method comparison |
| Mode entanglement | Medium | Use continuous profile vectors instead of binary labels |
| Training data overlap confound | Low | Include CodeLLaMA as domain-shifted control |
| Effect size uncertainty | Medium | Cohen's d > 0.5 threshold for practical significance |
| Hyperparameter sensitivity | Medium | 3-setting sensitivity analysis per method |

## Experimental Design Summary

**Models:** LLaMA-2-7B, Mistral-7B, Qwen-7B, CodeLLaMA-7B (control)  
**Methods:** TRAK, TracIn, Kronfluence  
**Modes:** Memorization, Feature Transfer, Spurious Association  
**Probes:** 1000 contrastive pairs per mode per model  
**Baselines:** Random attribution, BM25 lexical similarity

## Success Criteria

- **P1 (h-m2):** F-ratio > 4.0, Cohen's d > 0.5 for method dissociation
- **P2 (h-c1):** Cronbach's alpha > 0.8 for within-method stability
- **P3 (h-c2):** Cross-model Pearson r > 0.7 for profile transfer

## Archon Project

- **Project ID:** a2d71497-e81f-4512-913d-d2f0562891b1
- **Task Mapping:**
  - h-e1: 073fc356-f83c-4ff4-91ff-36d6eeb894b7
  - h-m1: e39b3ecf-ca6b-4347-89cb-6d92daa3ece9
  - h-m2: 427414ca-12d6-4849-bb30-dc28aa93f3ce
  - h-c1: 6786ea3a-9e8b-44e9-891f-00875f0280e8
  - h-c2: f01c074f-8e71-4076-8278-eff123cd0b03

## Next Steps

1. Begin Phase 2C with h-e1 (READY, no prerequisites)
2. Generate experiment design for each sub-hypothesis
3. Proceed through Phase 3 implementation planning
4. Execute Phase 4 PoC validation
