# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T02:05:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1
- **Gap Title**: Systematic Granularity Comparison Under Controlled Conditions
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met - specific claim, mechanism, predictions, novelty, feasibility, objections addressed

### Key Insights
- Feedback granularity is fundamentally a credit assignment problem
- RLTF's U_line/U_ignore error categorization provides natural gating criterion
- Effect size depends on U_ignore frequency (~10-15% of errors)
- Error distribution likely shifts during training toward U_line types

### Breakthrough Moments
- Exchange 7: Pivot from "phase-dependent granularity" to "conditional aggregation"
- Exchange 13: Credit assignment framing connects to deep RL theory
- Exchange 14: Gradient concentration metric for mechanism testing

---

## Final Hypothesis

### Title
Error-Type-Gated Fine-Grained Execution Feedback for Code RL

### Core Claim
Under controlled RL fine-tuning of code LLMs (same model, dataset, compute budget), if fine-grained execution feedback is applied only to errors with reliable source localization (U_line category errors where traceback provides accurate line numbers), then training sample efficiency improves compared to unconditional fine-grained application, because gating reduces noisy credit assignment from unreliably-localized errors.

### Mechanism
Fine-grained feedback assigns credit to specific tokens (the error line). When error localization is unreliable (U_ignore errors like IndentationError), credit is misassigned, adding noise to gradients. Gating by error type filters unreliable assignments, improving gradient signal-to-noise ratio.

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | Yes | Fine-gated reaches 30% pass@1 >10% faster than Fine-always on APPS | (Steps_fine_always - Steps_fine_gated) / Steps_fine_always > 0.10 |
| P2 | No | Error type distribution shifts toward U_line during training | U_ignore fraction decreases by >5 percentage points |
| P3 | No | Fine-gated advantage increases in second half of training | Efficiency gap at epoch 4 > efficiency gap at epoch 2 |
| P4 | No | Fine-gated shows higher gradient concentration at error-line tokens | Fine-gated ratio > Fine-always ratio (p<0.05) |

---

## Novelty

**Key Innovation**: Error-type-gated application of fine-grained feedback based on localization reliability

**Differentiation**:
- vs RLTF: RLTF applies all feedback types unconditionally; we gate by error type
- vs VeRPO: VeRPO addresses cardinality bias; we address localization reliability
- vs RLEF: RLEF uses textual feedback in prompts; we modify reward signal structure

---

## Experimental Design

**Model**: CodeT5-large (770M parameters)

**Dataset**: APPS (5000 training problems)

**Conditions**:
| Condition | Fine-grained applied to | Coarse applied to |
|-----------|-------------------------|-------------------|
| Coarse-only | None | All errors |
| Fine-always (RLTF default) | All errors | All errors |
| Fine-gated | U_line errors only | All errors |
| Fine-gated+compensate | U_line errors only | All errors + fallback for U_ignore |

**Runs**: 3-5 seeds per condition

**Compute**: ~12 GPU-days (4× A100, 24h per run)

---

## Limitations

- Tests only on APPS dataset; MBPP may show different patterns
- Uses CodeT5-large; larger models may have different learning dynamics
- Gating is binary (apply/don't apply); continuous weighting unexplored
- Does not apply to multi-file or repository-level code generation
- Purely logic errors (tests fail but no exception) not addressed

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Effect size may be small; error shift needs cross-condition comparison |

---

*Phase 2A Complete - Ready for Phase 2B*
