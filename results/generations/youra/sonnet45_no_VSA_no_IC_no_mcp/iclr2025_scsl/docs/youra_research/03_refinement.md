# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24T22:40:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Loop (Independent Controller Ablation)
- **Gap ID**: Gap1
- **Gap Title**: Quantitative Architecture-Temporal Correlation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All convergence criteria met — SPECIFIC (clear core claim), MECHANISM (BN/LN/attention temporal filtering), PREDICTIONS (3 testable with falsifiers), NOVELTY (temporal-architectural joint analysis), FEASIBILITY (validated measurements), OBJECTIONS (confounds addressed)

### Key Insights

1. **Temporal dimension reveals WHEN architectures fail, not just WHETHER** (Dr. Sage): This enables temporal interventions rather than just characterizing convergence robustness.

2. **Accuracy-matched comparison eliminates training-speed confound** (Prof. Rex → Dr. Nova): Comparing worst-group gap at fixed average accuracy (e.g., 90%) isolates architectural effects from BN's known training acceleration.

3. **Stochastic vs deterministic spurious correlation distinction** (Dr. Nova): Gradient ambiguity from stochastic spurious correlations (85-95% co-occurrence) may be where architectural components matter. CMNIST (90% deterministic) tests this boundary.

4. **Attention effect partially confounded but testable** (Prof. Rex, Dr. Ally): ResNet-CBAM ablation provides partial isolation. If CBAM shows correction, attention contributes; if not, ViT correction is due to global architecture.

### Breakthrough Moments

- **Exchange 3 (Dr. Sage)**: Identified temporal robustness as new research direction — not just "which architecture is robust?" but "when do architectures become robust?"

- **Exchange 4 (Prof. Pax)**: Confirmed measurement validity and computational feasibility (~2 GPU-hours for full experiment)

- **Exchange 6 (Prof. Rex)**: Challenged epoch-based comparison as confounded by BN's training speed, leading to accuracy-matched comparison refinement

- **Exchange 7 (Dr. Nova)**: Proposed stochastic-vs-deterministic spurious correlation hypothesis — gradient ambiguity resolution as mechanism

---

## Final Hypothesis

### Title
Architectural Components as Temporal Filters in Spurious Correlation Learning

### Hypothesis ID
H-TemporalArchSig-v1

### Core Claim
Under stochastic spurious correlations (Waterbirds 85% co-occurrence, CelebA 95% co-occurrence), if we compare neural network architectures with different normalization (Batch Normalization vs Layer Normalization) and attention mechanisms (ResNet-CBAM, Vision Transformer) during training, then we will observe DISTINCT worst-group accuracy gap trajectories when measured against training progress (average accuracy on x-axis), because normalization and attention mechanisms differ in how they resolve gradient ambiguity from stochastic spurious correlations.

**Under-If-Then-Because Breakdown:**
- **Under:** Stochastic spurious correlations (datasets like Waterbirds, CelebA with 85-95% co-occurrence)
- **If:** Compare architectures with different normalization (BN vs LN) and attention (ResNet-CBAM, ViT)
- **Then:** Observe distinct worst-group accuracy gap trajectories (measured vs training progress)
- **Because:** Architectural components differ in gradient ambiguity resolution for stochastic correlations

### Mechanism

**Step 1: BN Amplifies Early Spurious Learning**
Batch Normalization normalizes using batch statistics (mean, variance across batch). When spurious correlations exist at batch level (e.g., landbirds disproportionately with grass backgrounds within batches), BN makes batch-level patterns easier to learn than instance-level core features. Early gradients flow to spurious batch correlations.

**Step 2: LN Reduces Early Spurious Amplification**
Layer Normalization normalizes per-instance (mean, variance within each example's activations), eliminating batch-level spurious signal. Spurious correlations must be learned from instance-level features, slowing acquisition relative to BN. Core features compete more evenly.

**Step 3: Attention Enables Mid-Training Correction**
Attention mechanisms (multi-head self-attention in ViT, CBAM in ResNet-CBAM) globally aggregate features. Once core features begin emerging (epoch 15-30), attention reweights activations to prioritize core over spurious, enabling gap correction. Local-only architectures lack this global correction mechanism.

**Key Tension:** ViT differs from ResNet in multiple ways beyond attention (global receptive field, parameter count, optimization). ResNet-CBAM ablation isolates attention better, but CBAM is channel-attention not spatial self-attention. Accept: if CBAM shows correction, attention contributes; if not, ViT correction is due to global architecture.

---

## Predictions

### P1 (Primary): BN Amplification
**Statement:** ResNet-BN shows ≥5 percentage point higher worst-group accuracy gap than ResNet-LN when both reach 90% average accuracy on Waterbirds.

**Test Method:** Train ResNet-BN and ResNet-LN on Waterbirds for 100 epochs, log worst-group gap and average accuracy every epoch. For each of 10 seeds, identify epoch where each architecture first reaches 90% average accuracy, record worst-group gap at that epoch. Compute mean gap difference across 10 seeds, perform paired t-test (α=0.05).

**Success Criterion:** Mean gap difference (BN - LN) ≥ 5pp AND p < 0.05 AND Cohen's d ≥ 0.8

**Falsification:** If p > 0.05 OR mean gap difference < 3pp OR effect size < 0.5, BN amplification rejected. Interpretation: normalization type does not significantly affect early spurious learning.

### P2 (Primary): Attention Correction
**Statement:** ViT or ResNet-CBAM shows steeper worst-group gap reduction slope (more negative, faster correction) from epoch 20-50 compared to ResNet-BN on Waterbirds.

**Test Method:** For each architecture and seed, compute linear regression slope of worst-group gap vs epoch for epochs 20-50. Compute mean slope and 95% CI across 10 seeds for each architecture. Compare ViT and ResNet-CBAM slope CIs against ResNet-BN slope CI.

**Success Criterion:** ViT or ResNet-CBAM slope CI does NOT overlap with ResNet-BN slope CI AND slope is more negative by ≥ 0.3pp/epoch

**Falsification:** If slope CIs overlap OR difference < 0.2pp/epoch, attention correction rejected. Weaken claim to "ViT architecture corrects" (not attention alone) if ViT succeeds but CBAM fails.

### P3 (Secondary): Signature Consistency
**Statement:** Architecture ranking by worst-group gap (at 90% avg accuracy) consistent from Waterbirds to CelebA, Spearman ρ > 0.8.

**Test Method:** For each architecture, compute mean worst-group gap at 90% avg accuracy across 10 seeds on Waterbirds. Rank architectures 1-4 (lowest gap = best). Repeat on CelebA. Compute Spearman rank correlation.

**Success Criterion:** Spearman ρ > 0.8 (strong positive correlation)

**Falsification:** If ρ < 0.6 OR ranking reversal, signature consistency rejected. Interpretation: temporal signatures are dataset-specific, not purely architectural.

---

## Novelty

### What's New
First systematic temporal comparison of architectural components (normalization, attention) on spurious correlation learning dynamics. Novel framing: worst-group gap trajectories as architectural signatures.

### Key Innovation
Accuracy-matched temporal comparison eliminates training-speed confounds. Stochastic vs deterministic spurious correlation hypothesis. Temporal metrics (gap vs average accuracy, gap convergence slope) enable architecture design for robustness.

### Differentiation from Prior Work

| Prior Work | Difference |
|------------|-----------|
| **Toneva et al. 2019 (Example Forgetting)** | Toneva studied temporal dynamics within ResNet only. This systematizes temporal analysis ACROSS architectures (BN/LN/CBAM/ViT). |
| **Sagawa et al. 2020 (Group DRO)** | Sagawa evaluated worst-group accuracy at convergence only. This tracks worst-group gap DURING training. |
| **Geirhos et al. 2020 (Shortcut Learning)** | Geirhos qualitatively noted architectural differences. This quantifies temporal learning signatures with statistical tests. |
| **Santurkar et al. 2019 (BN helps optimization)** | Santurkar showed BN smooths loss landscape but didn't study spurious correlations. This hypothesizes BN's batch statistics amplify spurious learning. |

---

## Experimental Design

### Datasets
- **Waterbirds** (Sagawa et al. 2020): 5.9k examples, 4 groups (bird type × background), 85% spurious correlation
- **CelebA** (Liu et al. 2015): Hair color attribute, gender spurious feature, 95% spurious correlation
- **CMNIST** (DomainBed): Color-digit deterministic spurious correlation, 90% (scope boundary test)

### Models
- **ResNet-18-BN**: Baseline, expected early spurious amplification
- **ResNet-18-LN**: Normalization ablation, expected reduced early amplification
- **ResNet-18-CBAM**: Attention ablation, tests if attention enables correction with local receptive fields
- **ViT-Small / DeiT**: Global architecture comparison, expected mid-training correction (confounded by global structure)

### Training Protocol
- **Learning Rate:** Constant 0.01 (no schedule) to isolate architectural effects
- **Batch Size:** 64 (all experiments)
- **Initialization:** He initialization
- **Seeds:** 10 seeds (0-9) for statistical power (2pp detectable effect)
- **Epochs:** 100
- **Measurement:** Log worst-group accuracy and average accuracy every epoch, apply 5-epoch smoothing

### Evaluation Metrics
- **Primary:** Worst-group accuracy gap at 90% average accuracy
- **Secondary:** Gap convergence slope (epochs 20-50)
- **Consistency:** Spearman rank correlation Waterbirds→CelebA

---

## Limitations

### Known Limitations

1. **Attention effect partially confounded:** ViT differs from ResNet in global receptive field, parameter count, optimization dynamics, not just attention. ResNet-CBAM ablation provides partial isolation (channel attention), but cannot fully isolate spatial self-attention. If CBAM shows correction, attention contributes; if not, ViT correction is due to global architecture.

2. **Optimization confounds:** Constant LR=0.01 isolates architectural effects but may not reflect real training (where LR schedules are common). Future work: test with realistic schedules.

3. **Dataset-specific signatures possible:** If Spearman ρ<0.6 between Waterbirds and CelebA, temporal signatures don't generalize. This is accepted as scope limitation.

4. **Scope limited to stochastic spurious correlations:** CMNIST test determines whether signatures exist for deterministic spurious correlations (90% co-occurrence). If not, hypothesis scope is stochastic-only.

### Mitigation Strategies

- **Measurement noise:** 5-epoch smoothing, validation set measurement
- **Statistical power:** 10 seeds for 2pp detectable effect (α=0.05, power=0.80)
- **Confound isolation:** Accuracy-matched comparison, multiple datasets, ResNet-CBAM ablation
- **Null result value:** Frame as "optimization-dominance vs architecture-dominance" finding

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas participated with STRONG verdicts. Convergence after 7 exchanges. |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (confounds addressed or accepted as limitations) |
| **Novelty** | STRONG (first temporal-architectural joint analysis) |
| **Falsifiability** | STRONG (3 predictions with quantitative falsifiers) |
| **Significance** | STRONG (opens temporal robustness research direction) |
| **Feasibility** | STRONG (validated measurements, ~2 GPU-hours) |

---

## Phase 2B Readiness

**Status:** READY

**Sub-Hypothesis 1 (Existence):** Worst-group accuracy gap must be measurable (requires group-labeled datasets), architectural variants must be implementable (BN→LN swap, CBAM, ViT), statistical power must be adequate (10 seeds).

**Sub-Hypothesis 2 (Mechanism):** Test causal mechanism — BN amplifies (P1), LN reduces (P1 falsification), attention enables correction (P2). Measure temporal gap trajectories at accuracy-matched checkpoints.

**Sub-Hypothesis 3 (Comparison):** Compare 4 architectures on 3 datasets. Baseline: ResNet-BN standard training. Evaluation: worst-group gap at 90% avg accuracy, gap convergence slope, signature consistency.

**Open Questions:**
- Will CMNIST (deterministic spurious) show signatures or confirm stochastic-only scope?
- Will ResNet-CBAM isolate attention effect or confirm ViT correction is due to global architecture?
- Will signature ranking transfer from Waterbirds to CelebA (Spearman ρ>0.8) or reveal dataset-dependence?

---

*Phase: 2A - Hypothesis Generation and Refinement*  
*Total processing time: ~10 minutes*  
*Convergence: 7 exchanges (self-play, independent controller ablation)*
