# Hypothesis Context: H-E1

**Generated:** 2026-07-11
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

**ID:** H-E1
**Type:** EXISTENCE
**Statement:** Under ML reengineering workflows, if API behavioral invariants (structural, metamorphic, composition-level) are expressible as lightweight executable contracts, then ≥40% of environment-stage API defects from Jiang et al.'s corpus are contractable with ≤10s validation time and version stability across ±2 minor releases.

**Rationale:** This hypothesis validates the foundational assumption (A1) that a sufficient proportion of real-world API defects can be expressed as executable contracts. Without this, the entire approach becomes impractical.

---

## Variables

- **Independent:** Defect type (structural, metamorphic, composition-level)
- **Dependent:** Contractability rate (% of defects expressible as contracts)
- **Controlled:** Repository maturity, defect corpus source (Jiang et al. 2023)

---

## Experimental Setup (from Phase 2B Section 1.3)

### Dataset
- **Name:** Jiang et al. 348-Defect Corpus + Live GitHub Repos
- **Type:** Standard + Real-world
- **Source:** Published dataset (Jiang et al. 2023) + ≥1K stars CV repos from GitHub
- **Details:** Jiang et al. provides ecological validity (real reengineering defects); live trial tests marginal value in practice
- **Processing:** Phase 1: Retrospective coding, Phase 2: Version-Transition Benchmark, Phase 3: Randomized trial on live repos

### Model
- **Name:** API contract validation framework
- **Type:** Pre-built library for PyTorch/HuggingFace/JAX + auto-generation pipeline
- **Details:** Contracts are the 'model' — hypothesis tests their defect detection efficacy

---

## Baseline & Comparison Targets

| Method | Performance | Dataset |
|--------|-------------|---------|
| No-CI (Control) | Version pinning only, no automated testing | Mirrors 75% of ML repos per Wolter et al. |
| CI-Only (Best-Practice Baseline) | pytest + integration tests + version pinning | Current best practice |
| Execution-Only (Adversarial Baseline) | Import + minimal forward pass | Catches obvious crashes, not subtle invariant violations |

---

## Verification Protocol

1. Load Jiang et al. 348-defect corpus, filter for environment-stage API defects
2. Two independent coders apply 3-question filter: (1) Documented invariant exists? (2) Evaluable in ≤10s? (3) Version-stable ±2 releases?
3. Calculate contractability rate with 95% CI, check inter-rater reliability (Cohen's kappa ≥0.7)
4. Stratify by defect category (structural, metamorphic, composition-level)
5. Compare contractability rate to 40% threshold

---

## Success Criteria

- **Primary:** Contractability rate ≥40% with 95% CI lower bound >35%
- **Secondary:** Inter-rater reliability Cohen's kappa ≥0.7

---

## Gate Condition

- **Type:** MUST_WORK
- **Pass Condition:** Contractability ≥40%
- **Fail Action:** If <40%, PIVOT to structural-only contracts with reduced scope claims

---

## Dependencies

**Prerequisites:** None (foundation hypothesis)

**Dependent Hypotheses:**
- H-M1 (Structural Invariant Validation) - depends on H-E1
- H-M2, H-M3, H-M4 (downstream mechanisms) - transitively depend on H-E1

---

## Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | ≥40% of environment-stage API defects are expressible as version-stable, lightweight executable invariants | 88% of environment defects are interface defects — if structural/binding assumptions, likely contractable | If <40% contractability, the 30% reduction claim becomes implausible |

---

## Previous Context

None - This is the foundation hypothesis with no prerequisites.
