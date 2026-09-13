# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-04T00:00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0 (Free-Parse)
- **Gap ID**: gap-1
- **Gap Title**: SGD Temporal Feature Learning Gap — Lack of Systematic Measurement Framework
- **Execution Mode**: UNATTENDED (#batch-mode)
- **Discussion Exchanges**: 8
- **Convergence**: All 6 criteria met at Exchange 8

---

## Research Dialogue Context

**Participants**: Dr. Nova (🔭), Prof. Vera (🔬), Dr. Sage (🎯), Prof. Pax (⚙️), Dr. Ally (🛡️), Prof. Rex (🔍)

**Total Exchanges**: 8

**Convergence Reason**: All 6 convergence criteria satisfied (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Separating measurement (label-aided) from intervention (annotation-free) is the critical framing decision that resolves the label leakage concern
- Gap area A = integral of delta(t) dt is a more robust scalar metric than point-in-time t* — resilient to oscillation and sharpness ambiguity
- DFR's mechanistic explanation via the temporal gap is a stronger contribution than numerically beating DFR
- Three-tier hypothesis structure (measurement → mechanistic explanation → intervention) makes the work robust to intervention underperformance

### Breakthrough Moments
- **Exchange 5** (Dr. Ally): Two-component framing (measurement vs. intervention) dissolved the label leakage concern raised by Prof. Pax
- **Exchange 7** (Dr. Nova): Reframing the DFR explanation as the primary contribution rather than a side effect
- **Exchange 6** (Prof. Rex): Operational definition of t* with 3-consecutive-checkpoint robustness criterion and gap area A as backup metric

---

## Final Hypothesis

### Title
**Temporal Feature Learning Gap: Measuring and Exploiting the Spurious-Before-Core Dynamics of SGD**

### Hypothesis ID
`H-TemporalGap-v1`

### Core Claim (Under-If-Then-Because)
Under standard ERM training on spurious correlation benchmarks (Waterbirds, CelebA), if checkpoint linear probing is applied to measure spurious-label and core-label probe accuracy at regular training intervals, then a measurable temporal gap delta(t) = spurious_probe_acc(t) - core_probe_acc(t) > 0 will be observed during early training, because SGD simplicity bias causes spurious (lower-complexity) features to be learned faster than core (higher-complexity) features — and the transition epoch t* where delta closes explains the success of post-hoc annotation-free methods (DFR, JTT).

### Null Hypothesis
There is no significant temporal ordering in spurious vs. core feature learning under standard ERM training on Waterbirds/CelebA. delta(t) <= 0 at all training checkpoints across all seeds, and DFR worst-group accuracy improvement is uncorrelated with epochs trained past t*.

### Mechanism (4-Step Causal Chain)
1. **SGD Simplicity Bias**: Lower-complexity features generate lower-variance gradient signals and are learned preferentially in early training (Frequency Principle, Simplicity Bias)
2. **Feature Complexity Ordering**: In Waterbirds/CelebA, spurious features (background texture, hair color) are measurably simpler than core features (bird species morphology, gender)
3. **Temporal Gap Window**: A measurable window exists where spurious probe accuracy exceeds core probe accuracy — delta(t) > 0 — closing at transition epoch t*
4. **DFR Mechanistic Explanation**: DFR succeeds because it applies last-layer reweighting after t*, at which point the backbone already encodes sufficient core features

---

## Predictions

### P1 (Primary)
**Statement**: delta(t) > 0 for a statistically significant contiguous window of early training epochs, replicated across at least 3 seeds on Waterbirds and CelebA

**Test Method**: Checkpoint linear probe battery (ResNet-50 ERM, checkpoint every 2 epochs, held-out-split L2 logistic regression probes for spurious and core labels)

**Success Criterion**: delta(t) > 0 for at least 10% of training epochs (contiguous), p < 0.05 across seeds, replicated on CelebA

**Falsification**: delta(t) <= 0 at all checkpoints across all seeds on both datasets

### P2 (Secondary)
**Statement**: DFR worst-group accuracy improvement positively correlates (Pearson r > 0.7) with epochs the ERM backbone was trained past t*

**Test Method**: Run DFR with 5 truncated ERM backbones (before t*, at t*, three points past t*); correlate DFR WGA improvement with (training_epochs - t*)

**Success Criterion**: Pearson r > 0.7, p < 0.05; monotonic increase in DFR WGA with epochs past t*

**Falsification**: No significant correlation between DFR WGA improvement and epochs trained past t*

### P3 (Secondary)
**Statement**: Early stopping at t* + last-layer reweighting achieves WGA within 3pp of DFR with at most 50% of DFR computational cost

**Test Method**: Train ERM to t*, stop, apply DFR-style LLR; compare WGA to full DFR on Waterbirds/CelebA

**Success Criterion**: Early-stop LLR WGA within 3pp of DFR WGA; one training run vs. two

**Falsification**: Early-stop LLR WGA more than 5pp below DFR WGA

---

## Novelty

**Key Innovation**: First standardized checkpoint linear probe battery producing delta(t) and gap area A metrics for temporal feature learning dynamics on standard spurious correlation benchmarks

**How it differs from prior work**:
- *vs. Mangalam & Girshick 2021*: They show shortcuts emerge early but provide no standardized measurement protocol, no delta(t) metric, and no connection to annotation-free baselines
- *vs. JTT*: JTT exploits training dynamics heuristically; our work provides the mechanistic explanation for why this heuristic works
- *vs. DFR*: DFR provides an effective method but no mechanistic explanation; our t* measurement provides this
- *vs. Frequency Principle + Simplicity Bias*: General theoretical findings; we provide the first empirical operationalization on spurious correlation benchmarks

---

## Experimental Design

**Primary Dataset**: Waterbirds (Sagawa et al. 2020) via kohpangwei/group_DRO

**Replication Dataset**: CelebA via kohpangwei/group_DRO

**Model**: ResNet-50 (ImageNet pretrained, torchvision)

**Probe**: L2 Logistic Regression (scikit-learn) on frozen backbone features, held-out validation split

**Baselines**:
| Method | WGA (Waterbirds) | Group Labels? |
|--------|-----------------|---------------|
| ERM | ~72% | No |
| JTT | ~86% | No |
| DFR | ~88% | No |
| GroupDRO | ~91% | Yes (upper bound) |

**Compute**: ~10 GPU-hours per dataset on single GPU

---

## Limitations

- Effect size of delta(t) is empirically unknown — measurement contribution holds regardless, but intervention story weakens if delta_max < 2%
- t* may be dataset-specific (different epochs for Waterbirds vs. CelebA) — cross-dataset t* comparison is a secondary finding
- t* identification in the primary protocol uses group labels (spurious + core) — annotation-free t* via proxy is a secondary contribution with higher uncertainty
- All paper IDs are inferred (TEST environment) — verification recommended before Phase 4 implementation
- MultiNLI/CivilComments replication requires BERT experiments — added compute cost

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-TemporalGap-v1 |
| **Discussion Exchanges** | 8 |
| **Discussion Convergence** | All 6 criteria met at Exchange 8 |
| **Clarity Verified** | Yes |
| **Feasibility** | STRONG — ~100 lines code, ~10 GPU-hours, existing datasets |
| **Novelty** | STRONG — first systematic temporal gap measurement protocol |
| **Remaining Objections** | Effect size unknown; DFR explanation requires controlled experiments |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Execution Mode: UNATTENDED (#batch-mode)*
*Next Phase: Phase 2B — Hypothesis Decomposition and Sub-hypothesis Planning*
