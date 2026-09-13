# Hypothesis Context: H-E1

**Generated:** 2026-08-28
**Source:** 02b_verification_plan.md (Section 2.2)

---

## Hypothesis Information

**ID:** H-E1
**Type:** EXISTENCE
**Statement:** Base models (0 RLHF steps) produce outputs with preference entropy H_base ≥ 1.8 nats on subjective tasks

**Full Specification (from Phase 2B):**
Under RLHF preference datasets (Anthropic-HH), if we have access to raw pairwise comparison data, then we can compute Shannon entropy H = -Σ p_i log(p_i) for preference distributions, because the dataset publishes response frequency counts rather than only aggregated win rates.

**Rationale:**
Validates the foundational measurement assumption (A5). Without computable entropy, the entire mechanism chain fails. This existence hypothesis confirms that our primary dependent variable can be reliably extracted from existing benchmarks without new data collection.

---

## Variables

- **Independent:** Dataset access level (raw counts vs aggregated stats)
- **Dependent:** Entropy computability (binary: yes/no)
- **Controlled:** Dataset source (Anthropic-HH fixed)

---

## Verification Protocol

1. Download Anthropic-HH pairwise comparison data from public repository.
2. Parse response frequency distributions for sample prompts (n=100).
3. Compute Shannon entropy H for each prompt's preference distribution.
4. Validate entropy range [0, log(2)] for binary comparisons.
5. Report entropy computation success rate across sample.

---

## Success Criteria

**Primary:** Entropy computable for ≥95% of sampled prompts
**Secondary:** Computed entropy shows variance (not all zero or constant)

---

## Gate Condition

**Gate Type:** MUST_WORK
**Failure Response:** IF fails: ABANDON (mechanism untestable without entropy measure)

---

## Dependencies

**Prerequisites:** None
**Dependent Hypotheses:** H-M1, H-M2, H-M3, H-M4

---

## Experimental Setup (from Phase 2A)

### Dataset
- **Name:** Anthropic-HH (Helpful & Harmless)
- **Type:** standard
- **Source:** https://github.com/anthropics/hh-rlhf
- **Paths:** hh-rlhf/helpful-base and hh-rlhf/harmless-base
- **Scale:** 160K+ pairwise comparisons
- **Justification:** Contains pairwise preference comparisons across diverse conversational tasks (QA, creative, opinion, advice). Includes both base model and RLHF-tuned model responses, enabling retrospective analysis.

### Model (for follow-on hypotheses)
- **Name:** Pythia-1B
- **Type:** decoder-only transformer
- **Source:** EleutherAI Pythia suite
- **Justification:** Open-source with published checkpoints, compute-feasible (12 GPU-hours), small enough for rapid iteration

---

## Key Assumptions

**A5 (Critical for H-E1):** Existing RLHF preference datasets (Anthropic-HH, WebGPT) contain sufficient raw preference distributions to compute entropy (not just aggregated win rates)
- **Evidence:** Anthropic-HH publishes pairwise comparison data; entropy computable from response frequency distributions
- **Violation Impact:** If datasets only publish summary statistics, entropy cannot be calculated — requires access to raw preference counts

---

## Source
Phase 2A Section 5 (SH1 Existence)
