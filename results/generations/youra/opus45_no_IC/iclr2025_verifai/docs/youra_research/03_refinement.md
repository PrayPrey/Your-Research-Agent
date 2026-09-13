# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-12T05:35:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap_1
- **Gap Title**: No Unified Comparative Study Across All Three Strategies
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 criteria met at Exchange 12 (natural convergence)

### Key Insights
- Verification strategies operate at fundamentally different abstraction levels (syntax, semantics, specifications)
- Error class independence is testable and determines multiplicative vs. additive improvement effects
- Bidirectional hypothesis design ensures any outcome (synergy, independence, interference) is scientifically interpretable

### Breakthrough Moments
- Exchange 5: Dr. Ally proposed multiplicative improvement model based on error independence
- Exchange 7: Dr. Nova reframed error overlap concern as a discovery mechanism itself
- Exchange 8: Prof. Vera crystallized three quantitative predictions with explicit thresholds

---

## Final Hypothesis

### Title
Verification Pipeline for LLM Code Generation: Error Class Independence Framework

### Core Claim
Under standard code generation benchmarks (HumanEval, MBPP), if formal verification strategies are combined in a pipeline ordered by abstraction level (grammar constraints → static analysis → SMT-guided repair), then the combined pass@k improvement exceeds individual strategy improvements, because each strategy targets largely independent error classes (syntax, semantics, specifications) enabling multiplicative error reduction.

### Mechanism
1. **Grammar constraints** enforce syntactic validity via token-level logit masking, eliminating compilation errors
2. **Static analysis** identifies semantic patterns (security vulnerabilities, reliability issues) in syntactically valid code
3. **SMT-guided repair** enforces formal specification satisfaction on semantically-filtered code
4. Each stage operates on a different error class, reducing noise for downstream stages

---

## Predictions

### P1 (Primary): Error Overlap
- **Statement**: Error overlap between grammar constraints and static analysis < 30%
- **Metric**: Jaccard index on set of problems improved by each strategy
- **Success**: Jaccard < 0.30
- **Falsification**: Jaccard >= 0.30 violates independence assumption

### P2: Marginal Contribution
- **Statement**: Each pipeline stage contributes > 5% marginal improvement
- **Metric**: Sequential measurement of remaining errors after each stage
- **Success**: Marginal improvement >= 5% for each stage
- **Falsification**: Any stage < 5% indicates diminishing returns

### P3: Synergy Coefficient
- **Statement**: Synergy coefficient S between 0.8 and 1.2
- **Metric**: S = (Combined - Baseline) / (Sum of individual deltas)
- **Success**: 0.8 <= S <= 1.2 confirms independence
- **Falsification**: S < 0.8 (interference) or S > 1.2 (unexpected synergy)

---

## Novelty

**Key Innovation**: First unified comparison of all three verification strategies (grammar constraints, static analysis, SMT-guided repair) on identical benchmarks with consistent metrics.

**Theoretical Contribution**: Error-class-independence framework that predicts when combination yields multiplicative vs. additive improvements.

**Differentiation from Prior Work**:
- Mundler et al. (2025): Grammar constraints alone → we test in pipeline
- Blyth et al. (2025): Static analysis alone → we measure interaction effects
- ContractEval (2025): SMT alone → we measure marginal contribution after other stages

---

## Experimental Design

### Datasets
- HumanEval (164 problems) - full pipeline for grammar + static
- HumanEval-Verus (23 problems with specs) - full pipeline including SMT

### Models
- CodeLlama-7B (open-source, accessible)
- GPT-4 (frontier capability)

### Tools
- eth-sri/type-constrained (grammar constraints)
- Bandit/Pylint (static analysis)
- Z3/Verus (SMT-guided repair)

### Design
Sequential pipeline with per-stage measurement: baseline → grammar → static → SMT

---

## Limitations

- SMT stage limited to 23 spec-annotated problems (14% of HumanEval)
- Short function scope may not capture integration-level errors
- Benchmark problems may not reflect production code complexity
- Python-specific; cross-language generalization untested

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 12 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all mitigated) |

---

*Phase 2A Complete - Ready for Phase 2B*
