# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-10T08:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap1-feedback-type-comparison
- **Gap Title**: Systematic Comparison of Feedback Types
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: All 6 criteria met at Exchange 16 with full persona participation

### Key Insights
- Different feedback types may carry orthogonal information, but test pass may subsume compile/runtime
- FGO converts execution traces to token masking—implicitly transfers trace information
- Credit assignment precision (error localization) explains differential learning dynamics

### Breakthrough Moments
- Exchange 6: Dr. Ally proposes separating content from granularity as orthogonal factors
- Exchange 11: Refined hypothesis structure with H1 (content) and H2 (granularity)
- Exchange 14: Prof. Vera formalizes 2x3 factorial design with statistical criteria

---

## Final Hypothesis

### Title
Content-Granularity Disentanglement for Execution Feedback in Code RL

### Core Claim
Under controlled PPO training on code generation benchmarks (HumanEval, MBPP), if we independently vary feedback content (compile, test, combined) and granularity mechanism (standard PPO vs. FGO token masking), then we observe that (1) granularity provides larger performance gains than content variation, (2) combined content with FGO achieves best overall performance, and (3) FGO transfers trace information benefit without explicit trace reward, because FGO enables precise credit assignment by masking non-executed code, addressing the sparse reward problem regardless of feedback content.

### Mechanism
FGO converts sparse episode rewards into dense token-level credit by masking tokens that were never executed during test runs. This addresses the credit assignment problem in RL—the model receives gradient signal only for code that actually ran. Content variation (compile vs. test) provides complementary error types, but without fine-grained credit assignment, this benefit is limited.

---

## Predictions

| ID | Statement | Success Criterion |
|----|-----------|-------------------|
| P1 | FGO improves performance across ALL feedback content types | Paired t-test p<0.05; eta-squared > 0.3 |
| P2 | Combining compile and test feedback outperforms single types | ANOVA post-hoc Tukey HSD p<0.05 |
| P3 | FGO effect size exceeds Content effect size (granularity dominates) | eta-squared(FGO) > eta-squared(Content) |

---

## Novelty

**Key Innovation**: First controlled study to disentangle content vs. granularity effects in execution feedback for code RL.

**Differentiation**:
- vs. PPOCoder: Uses only test feedback with episode reward; we test content variations with FGO
- vs. StepCoder: Conflates compile content with FGO granularity; we disentangle them
- vs. RLPF: Uses staged rewards; we add RLPF as baseline and test FGO orthogonally

---

## Experimental Design

**Model**: CodeLlama-7B-Instruct

**Benchmarks**: HumanEval (164 problems), MBPP (974 problems)

**Design**: 2 (Granularity: Standard/FGO) × 3 (Content: Compile/Test/Combined) + RLPF baseline = 7 conditions

**Metrics**: pass@1 (primary), pass@10, training efficiency

**Compute**: ~50-100 GPU-hours (21 runs × 3 seeds)

**Baselines**:
- Standard PPO (Test-only)
- PPO + RLPF Staged Rewards
- StepCoder (Compile + FGO)

---

## Limitations

- HumanEval near-saturation may limit visibility of training improvements at pass@1
- FGO masking threshold sensitivity not yet characterized
- Transfer to complex benchmarks (SWE-bench) untested
- Results may not generalize to non-Python languages or 13B+ models

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 16 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (minor concerns mitigated) |

---
