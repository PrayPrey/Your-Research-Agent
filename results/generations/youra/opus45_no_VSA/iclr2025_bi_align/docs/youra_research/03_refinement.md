# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-08T03:15:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1_unified_bidirectional_metrics
- **Gap Title**: Absence of Unified Bidirectional Alignment Metrics
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 17

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 17

**Convergence Reason**: All 6 convergence criteria met — specific claim, mechanism, predictions, novelty, feasibility, and objections addressed.

### Key Insights

1. Existing preference datasets may contain a latent "agency preservation" signal that current reward models systematically underweight
2. This signal can be extracted via pattern-based proxies without LLM-as-judge (avoiding circularity)
3. Representational probing with adversarial training can validate independence from reward prediction

### Breakthrough Moments

- **Exchange 9**: Predictive asymmetry framing — test via existing behavioral datasets instead of causal manipulation
- **Exchange 12**: Adversarial dual-objective probing as stronger independence test than linear residualization
- **Exchange 17**: Data audit reveals behavioral validation must be deferred; scope refined to construct validity

---

## Final Hypothesis

### Title
Bidirectional Alignment Index (BAI): Extracting Human-to-AI Alignment from Existing Preference Data

### Core Claim
Under conditions where four agency proxies (clarifying questions, option enumeration, epistemic hedging, explicit deferral) achieve ≥0.8 AUROC against pre-existing prompt annotations, if we compute a length-normalized Bidirectional Alignment Index from these proxies, then BAI will form a statistically independent dimension in model representation space (adversarial probe AUROC ≥0.7 after gradient reversal) and show systematic disagreement with reward scores (≥20% high-BAI/low-reward pairs), because agency-preserving AI behaviors constitute a latent dimension that current helpfulness-oriented evaluation systematically underweights.

### Mechanism
1. Agency-preserving behaviors are encoded in AI responses (extractable via pattern detectors)
2. These behaviors form an orthogonal representational dimension (testable via adversarial probing)
3. Current reward models penalize these behaviors as "unhelpful" (evidenced by disagreement cases)
4. Agency preservation reduces cognitive offloading and improves human error detection (theoretical; deferred validation)

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | BAI remains decodable after adversarial gradient reversal | AUROC ≥0.7 | AUROC <0.6 |
| P2 | BAI and reward show systematic disagreement | ≥20% disagreement rate | <10% disagreement |
| P3 | Disagreement cases are semantically coherent | Majority show agency patterns | Random/noise patterns |

---

## Novelty

**Key Innovation**: First operationalization of Human→AI alignment using existing benchmark infrastructure

**Differentiation**:
- Shen et al. (2024): Conceptual framework → BAI provides computable metric
- HumanAgencyBench: LLM-as-judge → BAI uses automated pattern detectors
- RewardBench: AI→Human only → BAI extracts orthogonal second axis

---

## Experimental Design

**Datasets**: HH-RLHF (advisory subset), RewardBench (Chat/Safety)

**Models**: Llama-3-8B, Mistral-7B, Qwen-2-7B (open-weight for hidden state access)

**Baselines**: Reward score only; verbosity-normalized BAI

---

## Limitations

1. **Causal mechanism not testable**: Cannot run A/B experiment within feasibility constraints
2. **Behavioral validation deferred**: No public dataset contains human error detection traces
3. **Domain-conditional**: Scoped to advisory/moral prompts; factual QA generalization uncertain

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Causal mechanism theoretical; domain generalization untested |

---

*Phase 2A Complete — Ready for Phase 2B hypothesis verification planning*
