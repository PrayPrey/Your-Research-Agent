# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** Round 1 (Differential Pluralistic Alignment via Voting-Theoretic Reward Aggregation)
**Hypothesis ID:** H-neurips2023_mp2-001
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
Replacing implicit majority-voting aggregation in RLHF with explicit, context-adaptive voting rules from social choice theory—constrained by fairness axioms from participatory budgeting (IFS, GFS) and parameterized by interpretable membership vectors—enables AI systems to represent pluralistic values with formal guarantees against systematic marginalization of minority perspectives, achieving minority representation score > 0.5 (vs < 0.3 for standard RLHF) with alignment tax < 10%.

**Confidence Level:** 85%

**Core Innovation:**
- **Voting-theoretic RLHF**: Differentiable voting rules (Borda, Copeland, Kemeny, Maximal Lottery) as loss functions
- **Fairness constraints**: IFS/GFS from participatory budgeting preventing minority marginalization
- **Interpretable value profiles**: Membership vectors revealing annotator moral dimensions
- **Context-adaptive selection**: Voting rule varies by moral dilemma type (high-stakes → Copeland, value-diverse → Maximal Lottery)

**Target Gap:** Gap 3 - Lack of Methodologies for Systematic Pluralistic Value Incorporation Beyond Current RLHF Paradigm

**Implementation Difficulty:** MEDIUM (3-6 months for PhD student)

**Key Contributions:**
1. **Theoretical**: First formal connection between social choice axioms and AI pluralistic alignment guarantees
2. **Methodological**: Systematic framework combining voting + fairness + personalization
3. **Practical**: Open-source implementation on PERSONA benchmark with interpretability dashboard

---

## Quick Reference

### Testable Predictions
1. **Minority representation**: Maximal Lottery voting → minority score > 0.5 (vs < 0.3 for Borda)
2. **Fairness guarantee**: IFS constraint → no perspective gets < 1/n influence
3. **Interpretability**: Membership vectors → predict annotator profile with > 70% accuracy
4. **Robustness**: Copeland rule → +20% alignment with Condorcet winner vs Borda
5. **Trade-off**: λ increase (0.1→1.0) → linear alignment tax, improved minority representation

### Baselines
- Standard RLHF (Borda only) - PRIMARY
- Distributional RLHF (uniform weights)
- Constitutional AI (principle-based)
- Oracle (separate model per persona) - UPPER BOUND

### Success Criteria
- **Minimum viable**: Minority representation > 0.5, IFS satisfaction > 90%
- **Strong success**: Distributional calibration error < 0.2
- **Acceptable trade-off**: Alignment tax < 10%

### Phase 2B Decomposition Preview
- **SH1 (Existence)**: Voting rules improve minority representation over Borda
- **SH2 (Mechanism)**: Fairness constraints prevent systematic marginalization
- **SH3 (Comparison)**: Context-adaptive selection outperforms fixed-rule baselines

---

*For full details, see 02a_extended_hypothesis_full.md*
