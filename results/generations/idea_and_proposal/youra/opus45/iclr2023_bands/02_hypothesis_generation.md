# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ZKShield-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under conditions where third-party model training provenance is uncertain, if Zero-Knowledge Proofs are used to cryptographically verify that backdoor-critical training components (data provenance, gradient bounds, final layer constraints) followed a certified secure protocol, then backdoor attacks that must manifest through these verified components will be detectable or prevented, because ZKP verification provides cryptographic guarantees of protocol compliance without revealing training data.

**Alternative Hypothesis (H0):**
ZKP-based training verification provides no meaningful additional security guarantees against backdoor attacks compared to existing output-level certification methods, because (a) the verification overhead is prohibitively expensive, (b) the attack coverage is too narrow to be practically useful, or (c) adaptive attacks can bypass process-level verification.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Verification Scope | Independent | Set of training components verified | {data_only, gradient_only, all_critical} |
| Proof System | Independent | Choice of ZKP system | {zkSNARK, zkSTARK, Nova/folding} |
| Circuit Optimization | Independent | Optimization level applied | {standard, hierarchical, recursive} |
| Verification Overhead | Dependent | Proof time / Training time ratio | 10x - 100x |
| Guarantee Coverage | Dependent | % attack classes covered | 60% - 90% |
| Attack Class Immunity | Dependent | Detection rate per attack class | {data_poison: Y/N, gradient: Y/N} |
| Training Protocol | Controlled | Fixed protocol specification | Standardized protocol v1.0 |
| Threat Model | Controlled | Adversary capability bounds | Data/gradient manipulation only |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
[Data Commitment Verification]
    → [Gradient Norm Bound Verification]
    → [Final Layer Constraint Verification]
    → [Recursive Proof Aggregation]
    → [Verifiable Backdoor-Resistant Training Certificate]
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Engineering Trustworthy MLOps (2025) | ZKP proves data matches commitment | Strong |
| Step2 → Step3 | CRFL (2021) | Gradient clipping prevents large injections | Strong |
| Step3 → Step4 | Spectral Signatures (2018) | Backdoors manifest in final layers | Medium |
| Step4 → Outcome | RzkFL (2025), zkDL (2023) | Recursive proofs achieve 10-50x overhead | Strong |

**Key Tension:**
- **Tension:** zkDL (2023) achieves <1 second proofs for inference verification, but training verification is fundamentally more complex
- **Resolution:** Strategic component verification (DSperse approach) limits verification to backdoor-critical components only, making training ZKP tractable

### 1.4 Key Assumptions

1. **Backdoor Manifestation:** Backdoor attacks manifest through detectable signatures in gradient norms, layer weights, or data distributions
   - **If violated:** Clean-label attacks could evade detection → limits coverage to ~60-70%

2. **Critical Component Identification:** Components where backdoors MUST manifest can be formally characterized
   - **If violated:** Verification provides false sense of security

3. **Acceptable Overhead:** 10-50x proof generation overhead is acceptable for security-critical scenarios
   - **If violated:** Practical deployment blocked → theory-only contribution

4. **Cryptographic Soundness:** Adversary cannot forge ZKP proofs (honest prover assumption)
   - **If violated:** Complete security failure → fundamental assumption

### 1.5 Scope & Boundaries

**Applies to:** Data poisoning attacks, gradient manipulation attacks, federated learning, model marketplace verification

**Does NOT apply to:** Clean-label attacks with minimal gradient deviation, attacks exploiting unverified components, hardware-level attacks

**Known limitations:** Coverage limited to ~60-90% of attack classes; requires formal attack characterization for new threats

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Verification Overhead Target):**
ZK-Shield will achieve verification overhead ≤ 50x compared to standard training time for models up to 10M parameters.

*Measurement*: Overhead ratio = Proof time / Training time, target ≤ 50x with p < 0.05
*Success*: Overhead ≤ 50x | *Falsification*: Overhead > 100x

**Secondary Predictions:**

**P2 (Attack Coverage):** ≥70% of known backdoor attack classes detected/prevented

**P3 (Component Coverage):** Critical-only verification equivalent to full verification (p > 0.05)

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure**: Verification overhead > 100x standard training
2. **Mechanism Failure**: Attack coverage < 50% of known attack classes
3. **Component Failure**: Critical-only verification misses >20% of attacks caught by full verification

### 1.7 SOTA Baseline

*Not applicable - This hypothesis targets a new guarantee type (process-level certification) rather than improving existing performance metrics.*

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 runs per configuration (9 configurations = 180+ runs)
**Statistical Tests:** One-sample t-test (overhead), Chi-square (coverage), Two-sample t-test (equivalence)
**Significance Level:** α = 0.05
**Report Format:** Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can ZKP-based training verification achieve acceptable overhead (≤50x) for models up to 10M parameters using current zkML infrastructure?"

**SH2 (Mechanism):**
"Does ZKP verification of backdoor-critical components provide detection/prevention guarantees against attacks that manifest through those components?"
- Will decompose into 4 sub-hypotheses (H-M1 through H-M4)

**SH3 (Comparison):**
"Does strategic backdoor-critical component verification provide equivalent security guarantees to full verification while achieving significantly lower overhead?"

**Total Sub-Hypotheses:** 2 + 4 = 6 sub-hypotheses

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-ZKShield-v1
- [x] Confidence: 0.80
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized (8 variables)
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Key assumptions with consequences (4)
- [x] Testable predictions with primary marked (P1, P2, P3)
- [x] Falsification criteria defined (3)
- [x] Baselines identified (CRFL, BagFlip, Neural Cleanse)
- [x] SH1, SH2, SH3 clear

**All 13 items verified ✓**

### Open Questions

1. **Resource Requirements:** GPU type, memory for zkDL/EZKL benchmarks?
2. **Data Availability:** BackdoorBench datasets (CIFAR-10, GTSRB)?
3. **Technical Feasibility:** Custom circuit design needed?
4. **Priority:** SH1 first (overhead feasibility gate)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
