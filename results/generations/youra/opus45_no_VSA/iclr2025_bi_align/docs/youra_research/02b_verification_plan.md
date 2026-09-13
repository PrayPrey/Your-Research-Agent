# Phase 2B: Verification Plan
## Hypothesis H-BAI-v1: Bidirectional Alignment Index

**Generated:** 2026-08-08T03:15:00Z  
**Archon Project:** 59d8d6b4-ba8c-4cd9-b4b2-fc43503652ba

---

## Main Hypothesis

**Statement:** Under conditions where four agency proxies (clarifying questions, option enumeration, epistemic hedging, explicit deferral) achieve ≥0.8 AUROC against pre-existing prompt annotations, if we compute a length-normalized Bidirectional Alignment Index (BAI) from these proxies, then BAI will form a statistically independent dimension in model representation space (adversarial probe AUROC ≥0.7 after gradient reversal) and show systematic disagreement with reward scores (≥20% high-BAI/low-reward pairs).

**Null Hypothesis (H0):** BAI does not form an independent representational dimension — either BAI decodability collapses to chance (AUROC <0.6) after removing reward-predictive variance, OR BAI shows <10% disagreement rate with reward scores.

---

## Sub-Hypotheses

### H-E1: Agency Proxy Extraction (EXISTENCE)
- **Statement:** Four agency proxies can be reliably extracted from HH-RLHF/RewardBench responses with AUROC ≥0.8 against pre-existing prompt annotations.
- **Gate:** MUST_WORK
- **Prerequisites:** None
- **Status:** READY
- **Archon Task:** 6d5b129d-0adf-426d-9584-d3818ec87aae

### H-M1: Representational Independence (MECHANISM)
- **Statement:** BAI remains decodable from model hidden states (AUROC ≥0.7) after adversarial gradient reversal removes reward-predictive variance, while reward probe R² degrades <2%.
- **Gate:** MUST_WORK
- **Prerequisites:** H-E1
- **Status:** NOT_STARTED
- **Archon Task:** c9b39810-ed44-45a6-b67e-563f492c0560

### H-M2: Systematic Disagreement Rate (MECHANISM)
- **Statement:** BAI and reward scores show systematic disagreement with ≥20% of response pairs falling in high-BAI/low-reward or low-BAI/high-reward quartiles.
- **Gate:** SHOULD_WORK
- **Prerequisites:** H-E1
- **Status:** NOT_STARTED
- **Archon Task:** e6f111b1-1f59-4449-ad5d-9d85fb8b61a5

### H-C1: Semantic Coherence (CONDITION)
- **Statement:** Disagreement cases are semantically coherent, with majority exhibiting interpretable agency-preserving patterns rather than noise or verbosity artifacts.
- **Gate:** SHOULD_WORK
- **Prerequisites:** H-M2
- **Status:** NOT_STARTED
- **Archon Task:** ed4da081-fb45-4b9b-a2f6-c13e7364f727

---

## Dependency Graph (DAG)

```
H-E1 (MUST_WORK)
  ├── H-M1 (MUST_WORK)
  └── H-M2 (SHOULD_WORK)
         └── H-C1 (SHOULD_WORK)
```

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Proxy AUROC <0.8 | Medium | High (blocks H-M1/H-M2) | Use ensemble of pattern detectors; tune thresholds |
| Insufficient agency-preserving responses in data | Medium | High | Pre-filter advisory/moral prompts; verify 15%+ prevalence |
| Gradient reversal fails to isolate orthogonal subspace | Low | High | Try multiple probing layers; use CKA as secondary metric |
| Disagreement cases are verbosity artifacts | Medium | Medium | Residualize against length/politeness before analysis |

---

## Timeline Estimate

| Phase | Hypothesis | Duration | Dependencies |
|-------|------------|----------|--------------|
| 2C | H-E1 | 1 day | None |
| 2C | H-M1 | 1 day | H-E1 complete |
| 2C | H-M2 | 0.5 day | H-E1 complete |
| 2C | H-C1 | 0.5 day | H-M2 complete |
| 3 | All | 2 days | 2C complete |
| 4 | All | 3 days | Phase 3 complete |

**Total estimated:** 8 days

---

## Experimental Resources

- **Datasets:** HH-RLHF (Anthropic), RewardBench (Allen AI)
- **Models:** Llama-3-8B, Mistral-7B, Qwen-2-7B
- **Evaluation samples:** Full test sets (minimum 500+ per model)
- **Baselines:** Reward score only, Verbosity-normalized BAI

---

## Next Action

Begin Phase 2C with H-E1 (first READY hypothesis).
