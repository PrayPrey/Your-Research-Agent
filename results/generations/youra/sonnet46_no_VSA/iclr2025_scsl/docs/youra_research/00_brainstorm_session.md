---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Per-Sample Hessian Trace Asymmetry as Mechanistic Evidence for Spurious Feature Reliance in ERM"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-04
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Spurious correlations and shortcut learning — specifically, whether **per-sample last-layer Hessian trace (Hutchinson estimator, K=20 Rademacher vectors)** provides a validated mechanistic minority membership signal, now empirically confirmed (AUROC=0.9086 at K=20, K=50 AUROC=0.9130), directly addressing SCSL Foundations track: "exploring the effect of shortcuts and spurious features on the loss landscape." This 9th iteration pivots from existence validation (h-e2-k CONFIRMED the signal works) to mechanistic characterization: **when does the Hessian trace gap emerge, grow, and saturate during ERM training, and does it predict robustification outcomes?**

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — 9th iteration. h-e2-k CONFIRMED Hessian trace signal (K=20 AUROC=0.9086, K=50 AUROC=0.9130) but failed only K=10 plateau calibration sub-test. Existence validated. Now advancing to mechanism characterization and downstream application via DFR with ERM-trained features — addressing h-m4's feature bottleneck using ERM features instead of frozen pretrained features.)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Deep learning models exhibit a well-documented simplicity bias: during SGD training, they preferentially learn spurious correlations and shortcuts over invariant causal features. This arises from inductive biases at multiple levels — data preprocessing, architecture, and optimization. As a result, models rely on spurious patterns rather than understanding underlying causal relationships, making them vulnerable to failure in real-world scenarios involving under-represented groups or minority populations.

The ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning (SCSL) highlights three key research tracks: (i) development of comprehensive evaluation benchmarks, (ii) novel robustification methods for supervised and self-supervised paradigms, and (iii) **foundational understanding of how shortcut reliance arises in DNNs via SGD and loss landscape dynamics** — specifically: mathematical formulations describing the issue and its origins, the role of gradient-descent-based optimization in shortcut reliance, and **the effect of shortcuts and spurious features on the loss landscape**.

Source Type: Workshop CFP / Structured Input

**Recovery Context:** Re-entering Phase 0 after EIGHT prior hypothesis attempts spanning multiple failure types. The most recent hypothesis **h-e2-k CONFIRMED** that per-sample last-layer Hessian trace via Hutchinson estimator IS a strong minority membership signal (K=20 AUROC=0.9086, K=50 AUROC=0.9130, analytical AUROC=0.9189). The h-e2-k failure was a calibration sub-test failure (K=10 plateau delta=0.011 > 0.01 threshold), NOT a signal failure. The core 8th brainstorm hypothesis — Hessian trace asymmetry as loss landscape signal — is validated. Next step: advance from existence hypothesis to **mechanism characterization** and **downstream application**.

---

## Lessons from Previous Attempts

### Attempt 1: h-e1 (Run 1) — Temporal Gradient Norm Variance Across Epochs Too Coarse
**What was tried:** CV of last-layer gradient norms across epochs 16–20 as minority membership signal.
**Why it failed:** AUROC≈0.60 vs. loss AUROC≈0.897. Across-epoch temporal variance is global training noise, not per-sample identity signal.
**Lesson:** Across-epoch variance is too coarse. Single-epoch point estimates are more reliable.

### Attempt 2: h-m1 — Phase I→II Transition Requires ≥15 Epochs, Not 5
**What was tried:** CV_ratio (majority/minority gradient norm CV) peak as Phase I→II transition marker, epochs 1–5.
**Why it failed:** CV_ratio stable at ~3.1 throughout; 5-epoch window entirely in Phase I.
**Lesson:** Phase transition dynamics need ≥15-epoch training.

### Attempt 3: h-m4 — Frozen Pretrained Features Have ~62–65% WGA Ceiling
**What was tried:** Top-k% gradient-norm proxy + DFR on frozen pretrained ResNet-50 features → WGA ≥ 85%.
**Why it failed:** Feature bottleneck at ~62–65% regardless of proxy quality.
**Critical lesson for 9th iteration:** DFR requires **ERM-trained** features (not frozen pretrained). Gradient norm IS a valid proxy signal (secondary gate PASS). **This bottleneck is now addressable**: h-e1 PASS confirms gradient norms work at t*; h-e2-k PASS confirms Hessian trace achieves AUROC=0.909. Both signals are now available with ERM-trained features.

### Attempt 4 (Superseded h-e1) — Within-Centroid Gradient Direction: Wrong Discriminator
**What was tried:** Cosine similarity of per-sample gradients to within-group class centroid.
**Why it failed:** Within-centroid measures intra-group cohesion, not inter-group separability. AUROC=0.436.
**Lesson:** Discriminator design matters fundamentally.

### Attempt 5: h-e2 (Run 1) — Between-Centroid Direction Is Pretrained ImageNet Artifact
**What was tried:** Between-centroid gradient direction score.
**Why it failed:** AUROC_y1≈0.987 at epoch 0 (before Waterbirds training) — gap = −0.005. Pretrained artifact.
**Critical lesson:** The gradient direction family is exhausted.

### Attempt 6: h-e1 (Run 2) — Mini-Batch Gradient CV at Epoch 1 Inverted
**What was tried:** CV of gradient norms across B=20 SGD micro-steps at epoch 1.
**Why it failed:** AUROC=0.2828, signal inverted (majority CV=1.198 > minority CV=0.536). Imbalance correction dominates at epoch 1.
**Lesson:** Mini-batch stochasticity at epoch 1 is dominated by 73% majority imbalance correction.

### Attempt 7 (8th Brainstorm → h-e2-k): Hessian Trace Existence — SIGNAL CONFIRMED
**What was tried (as h-e2-k):** Hutchinson trace estimator (K=10) plateau calibration test for per-sample last-layer Hessian trace.
**What happened:** K=10 AUROC=0.8974, K=20 AUROC=0.9086, K=50 AUROC=0.9130, Analytical=0.9189. **Signal is real and strong.** Failed only on K=10 plateau criterion (delta_10_20=0.011 > 0.01).
**Critical lesson for 9th iteration:** The Hessian trace signal is CONFIRMED at AUROC > 0.90. The 8th brainstorm hypothesis was correct. We now need to advance to MECHANISM and APPLICATION.

### What the 9th Direction Must Accomplish

1. **Build on confirmed Hessian trace signal** (K=20 AUROC=0.9086 validated)
2. **Characterize the mechanism**: when does curvature asymmetry emerge during training? Is it present at epoch 0 (pretrained artifact) or grows with ERM spurious feature exploitation?
3. **Address h-m4's bottleneck with correct features**: Use Hessian trace as DFR proxy with ERM-trained features (not frozen pretrained) → should achieve WGA ≥ 85%
4. **Remain within mandatory feasibility constraints**: existing datasets (Waterbirds, CelebA), existing infrastructure (h-e1 vmap + h-e2-k Hutchinson pipeline), no new benchmarks

---

## Session Plan

ROUTE_TO_0 Auto-extraction from: (1) Serena Memory failure records (h-e1 run1, h-m1, h-m4, superseded_h-e1, h-e2 run1, h-e1 run2, **h-e2-k run1 CONFIRMED signal**), (2) Snapshots (h-e1 PASS: AUROC=0.9402; h-e2-k: K=20 AUROC=0.9086; h-m4: frozen feature ceiling 0.621), (3) ICLR 2025 SCSL Workshop CFP — Foundations track loss landscape pillar, (4) mandatory feasibility constraints.

**Key synthesis**: The 9th iteration has a confirmed signal (Hessian trace AUROC > 0.90) and two open questions: (A) mechanism characterization (training dynamics of curvature asymmetry), (B) application as annotation-free DFR proxy with ERM features. Both are testable immediately.

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Research direction derived from: Hessian trace signal confirmed (h-e2-k AUROC=0.9086, AUROC=0.9130 at K=50) + training dynamics unexplored (h-e2-k measured at single epoch t*; curvature trajectory not characterized) + h-m4 DFR application failed on feature type (pretrained → ERM fix available) + SCSL Foundations track loss landscape explicitly calls for mechanism characterization + mandatory feasibility constraint verification.

---

## Research Question Development

### Initial Question

Given that:
- Per-sample last-layer Hessian trace (Hutchinson estimator, K=20) achieves AUROC=0.9086 on Waterbirds 95% spuriosity (h-e2-k CONFIRMED)
- Gradient norm magnitude (h-e1 PASS) achieves AUROC=0.9402 at t*
- h-m4 DFR failed due to frozen pretrained feature bottleneck (~62% WGA ceiling) — fix: use ERM-trained features
- SCSL Foundations track calls for: "exploring the effect of shortcuts and spurious features on the loss landscape"
- The curvature asymmetry trajectory during ERM training (does it grow with shortcut exploitation?) has not been characterized
- Both signals (gradient norm, Hessian trace) are available at each epoch checkpoint

Can we (1) **characterize the training dynamics of per-sample Hessian trace asymmetry** (curvature gap majority−minority across epochs 1–20, measured via K=50 Hutchinson estimator) to provide mechanistic evidence that spurious feature exploitation coincides with increasing loss landscape flatness for majority samples relative to minority samples, and (2) **use Hessian trace (K=50) as annotation-free DFR proxy with ERM-trained features** to achieve worst-group accuracy ≥ 85% on Waterbirds test set across ≥4/5 seeds — demonstrating that loss landscape curvature is both a mechanistic indicator and a practical robustification tool for spurious correlation?

### Refined Question

**Under ERM training with SGD on Waterbirds (95% spuriosity, ResNet-50 ImageNet pretrained), does the per-sample last-layer Hessian trace trajectory — measured via Hutchinson estimator (K=50 Rademacher vectors, last fc layer only) at training checkpoints t ∈ {0, 1, 5, 10, 20} — (i) exhibit a monotonically growing curvature asymmetry (minority Hessian trace / majority Hessian trace) that tracks the ERM model's increasing exploitation of the spurious feature (measured by spurious feature reliance ratio), providing causal-direction mechanistic evidence linking loss landscape curvature to shortcut learning dynamics; and (ii) serve as an annotation-free proxy for DFR upweighting on ERM-trained features to achieve worst-group accuracy ≥ 85% on Waterbirds test set across ≥4/5 seeds, surpassing the h-m4 frozen pretrained feature ceiling (62%) and matching oracle DFR with group labels — using only existing benchmarks (Waterbirds at `/home/PrayPrey/data/waterbirds_v1.0/`), validated Hutchinson infrastructure (h-e2-k), and ERM checkpoints saved during training?**

This question:
- Advances beyond existence (h-e2-k PASS-level signal) to **mechanism characterization** (training dynamics)
- Addresses h-m4's bottleneck with the correct fix: ERM-trained features instead of frozen pretrained
- Directly targets SCSL Foundations track pillar 3: "effect of shortcuts and spurious features on the loss landscape" — the trajectory analysis IS the mechanistic evidence
- Is immediately testable: K=50 Hutchinson estimator validated in h-e2-k; ERM checkpoints only need saving during standard training; DFR on ERM features is standard (Kirichenko et al., 2022)
- Two-gate hypothesis: Gate 1 (mechanism) = curvature ratio monotonically increases across epochs with Spearman rho ≥ 0.8 in ≥4/5 seeds; Gate 2 (application) = WGA ≥ 85% in ≥4/5 seeds using Hessian-DFR on ERM features

### Detailed Sub-Questions

1. **Curvature trajectory dynamics**: At checkpoints t ∈ {0, 1, 5, 10, 20}, does the per-sample Hessian trace ratio (mean_minority / mean_majority) grow monotonically — i.e., does increasing spurious feature exploitation in ERM create progressively flatter loss landscape for majority samples relative to minority samples? (Spearman rho ≥ 0.8 between epoch index and Hessian ratio in ≥4/5 seeds)

2. **Epoch 0 check (pretrained artifact detection)**: Is the Hessian trace asymmetry present at epoch 0 (before any Waterbirds fine-tuning) — analogous to h-e2's pretrained artifact finding? Or does it emerge only after ERM training begins exploiting the spurious feature? This distinguishes between pretrained representation geometry and learned shortcut curvature.

3. **Optimal epoch for DFR proxy**: Which epoch t* maximizes the Hessian-DFR WGA on the validation set? Does the optimal t* for DFR application match the optimal t* for AUROC discrimination (t*=4 from h-e1, t* maximizing AUROC from h-e2-k)?

4. **Hessian-DFR vs. gradient-norm-DFR**: Does using Hessian trace (K=50) as DFR proxy on ERM features achieve higher WGA than gradient norm (h-e1 signal) as DFR proxy — testing whether the loss landscape curvature provides additional information beyond first-order gradient magnitude for identifying upweighting candidates?

5. **Minority identification accuracy**: What fraction of the top-k% highest-Hessian-trace training samples are true minority group members (precision) and what fraction of all minority samples are captured (recall)? Does this match or exceed the precision/recall achievable with gradient norm proxy (h-e1)?

---

## Reference Papers

Not provided - will discover in Phase 1

Key Phase 1 search targets (informed by all failure history + confirmed Hessian signal + mechanism characterization + DFR application):

**Confirmed Core:**
- Sagawa et al. (2020) — Waterbirds benchmark; ERM training protocol; group definitions; DFR baseline comparison
- Hutchinson (1989) + h-e2-k confirmed implementation — K=50 Rademacher trace estimator
- Kirichenko et al. (2022) DFR — ERM feature extraction + last-layer retraining; oracle WGA baseline; methodology for ERM checkpoint-based DFR

**Mechanism/Trajectory:**
- LaBonte & Muthukumar (2026) — Phase I/II gradient dynamics; theoretical predictions about curvature during spurious vs. invariant feature learning phases
- Foret et al. (2021) SAM — per-sample sharpness; loss landscape flatness and generalization
- Hochreiter & Schmidhuber (1997) / Keskar et al. (2017) — flat minima; sharpness and loss landscape
- Yao et al. (2020) PyHessian — per-layer Hessian trace estimation; epoch-by-epoch sharpness measurement methodology

**Loss Landscape + Spurious Correlations:**
- Hermann & Lampinen (2020) / Shah et al. (2020) — simplicity bias and loss landscape in ERM with spurious features; does majority group create flatter minima?
- Liu et al. (2021) JTT — implicit upweighting via misclassification; analogous to Hessian-DFR in spirit
- Nam et al. (2020) GEORGE; Zhang et al. (2022) SSA — annotation-free spurious correlation correction baselines
- Park et al. (2023) or similar — loss landscape analysis in presence of group imbalance
- Sagawa et al. (2020) ERM failure analysis — spurious feature reliance coefficient / group accuracy gap as function of training epoch

**DFR Application with ERM Features:**
- Kirichenko et al. (2022) DFR — Table 1: Waterbirds ERM features → WGA 88% with group labels; Table showing annotation-free variants
- Any proxy-DFR methods (e.g., confidence-based upweighting, loss-based upweighting, last-layer gradient norm upweighting) on ERM features with Waterbirds

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 Workshop on Spurious Correlation and Shortcut Learning, Foundations track) — significance pre-validated. The 9th iteration:

1. **Confirmed signal, advancing to mechanism**: h-e2-k validated Hessian trace AUROC=0.9086 (K=20), 0.9130 (K=50). The 9th iteration is not re-testing existence but characterizing the training trajectory — directly addressing the SCSL Foundations pillar "exploring the effect of shortcuts and spurious features on the loss landscape" at the mechanistic level.

2. **Novel contribution: curvature trajectory as shortcut learning evidence**: No existing work (to our knowledge) measures per-sample last-layer Hessian trace at multiple training checkpoints to demonstrate that majority samples achieve progressively flatter loss minima as ERM exploits the spurious feature. This trajectory analysis would be the first direct per-sample curvature evidence for the loss landscape mechanism of shortcut learning.

3. **Solves h-m4's bottleneck correctly**: h-m4 used frozen pretrained features (62% WGA ceiling). The fix is known: ERM-trained features. The gradient norm signal (h-e1) and Hessian trace signal (h-e2-k) are both validated at AUROC > 0.90, making Hessian-DFR on ERM features a well-motivated, immediately testable downstream application. Expected WGA ≥ 85% (matching oracle DFR).

4. **Two-in-one hypothesis**: Mechanism characterization (Foundations track) + practical annotation-free robustification (Solutions track). This dual contribution increases SCSL workshop relevance.

5. **Theoretically grounded asymmetry direction**: Majority samples (spurious feature consistently aligned) achieve a flat loss minimum (spurious feature reliably minimized). Minority samples (spurious feature absent or anti-correlated) cannot reach a flat minimum through the spurious feature — higher Hessian trace predicted. This is consistent with h-e2-k empirical finding (Hessian trace discriminates minority at AUROC=0.909) and the simplicity bias literature.

6. **Epoch-0 falsifiability**: If Hessian trace asymmetry exists at epoch 0 (pretrained model, no Waterbirds training), it is a pretrained artifact (like h-e2). If it grows with training, it is genuine shortcut learning evidence. This falsifiability strengthens the mechanistic claim.

### Feasibility Check

All sub-questions testable immediately using:
- **Waterbirds** — data at `/home/PrayPrey/data/waterbirds_v1.0/`; 4795 train samples; group labels for AUROC/WGA evaluation only (not training)
- **h-e2-k validated Hutchinson infrastructure** — `run_experiment.py`: WaterbirdsDataset, load_model (fc-replace before load_state_dict), compute_hutchinson_traces, compute_analytical_traces; K=50 operationally confirmed
- **h-e1 infrastructure** — `src/h_e1/train.py` with checkpoint saving at t ∈ {0,1,5,10,20} (add checkpoint_dir argument)
- **DFR on ERM features** — standard logistic regression on h-e1's last-layer features at t*; no new training pipeline needed; reuse h-e1's eval infrastructure

**Infrastructure extensions needed** (minimal):
```python
# Extension 1: Save ERM checkpoints during training
train_one_epoch(model, loader, epoch, checkpoint_dir="{t}.pt")

# Extension 2: Hutchinson trace at multiple epochs (K=50)
# Already validated in h-e2-k; just run at each checkpoint

# Extension 3: DFR with ERM features (Kirichenko et al., 2022 pattern)
# Extract last-layer features from ERM checkpoint t*
# Identify top-k% highest Hessian trace samples
# Fit ℓ₁ logistic regression on reweighted features
# Evaluate WGA on test set
```

**No new benchmarks, synthetic data, or human annotation required**:
- ✅ No new benchmarks (Waterbirds existing; CelebA as secondary generalization)
- ✅ No synthetic/generated data
- ✅ No human evaluation or annotation (group labels for evaluation only)
- ✅ Immediately testable with existing validated infrastructure
- ✅ No new datasets needed

**Compute estimate**:
- Checkpoint save: 5 epochs (t=0,1,5,10,20) × standard ERM training time = ~5× h-e1 training
- Hessian trace at K=50: ~5× h-e2-k compute per checkpoint = ~25× h-e2-k total (feasible on existing GPU)
- DFR fitting: seconds (logistic regression on 4795 × 2048 features)
- Total: approximately 2–4 hours on existing hardware (estimated from h-e1 and h-e2-k run times)

---

## Phase 1 Input Package

<phase1-input>

### research_question
Under ERM training with SGD on Waterbirds (95% spuriosity, ResNet-50 ImageNet pretrained), does the per-sample last-layer Hessian trace trajectory — measured via Hutchinson estimator (K=50 Rademacher vectors, last fc layer only) at training checkpoints t ∈ {0, 1, 5, 10, 20} — (i) exhibit monotonically growing curvature asymmetry (minority Hessian trace / majority Hessian trace) tracking ERM's spurious feature exploitation (Spearman rho ≥ 0.8 in ≥4/5 seeds, with epoch 0 as artifact-detection control); and (ii) serve as annotation-free DFR proxy on ERM-trained features to achieve worst-group accuracy ≥ 85% on Waterbirds test set across ≥4/5 seeds — using only existing benchmarks (Waterbirds at `/home/PrayPrey/data/waterbirds_v1.0/`), the validated Hutchinson infrastructure from h-e2-k (K=50 confirmed at AUROC=0.9130), and ERM checkpoints saved during standard training?

### detailed_question
1. At checkpoints t ∈ {0, 1, 5, 10, 20}, does the per-sample Hessian trace ratio (mean_minority / mean_majority) grow monotonically — providing mechanistic evidence that ERM spurious feature exploitation creates progressively flatter loss landscape for majority samples? (Spearman rho ≥ 0.8 in ≥4/5 seeds; t=0 as pretrained artifact control)
2. Is Hessian trace asymmetry absent at t=0 (distinguishing learned shortcut curvature from pretrained ImageNet geometry) — specifically: does epoch-0 AUROC < 0.70 while epoch t* AUROC > 0.90, confirming the asymmetry emerges from ERM training?
3. Which epoch t* maximizes Hessian-DFR WGA on validation set, and does it match t* from AUROC discrimination (expected ~epoch 4 from h-e1 / h-e2-k)?
4. Does Hessian-DFR on ERM features achieve WGA ≥ 85% in ≥4/5 seeds, solving h-m4's 62% frozen feature ceiling and matching oracle DFR (Kirichenko et al., 2022)?
5. Does Hessian trace (K=50) outperform gradient norm (h-e1 signal) as DFR proxy on ERM features — testing whether second-order curvature captures additional minority-identifying information beyond first-order magnitude?

### reference_papers
Not provided - will discover in Phase 1

Key targets: Sagawa et al. (2020) Waterbirds ERM/SGD protocol + group definitions; Kirichenko et al. (2022) DFR oracle WGA baseline (ERM features → WGA 88%); Hutchinson (1989) trace estimator (K=50 confirmed in h-e2-k); Foret et al. (2021) SAM per-sample sharpness; Yao et al. (2020) PyHessian per-epoch trajectory methodology; LaBonte & Muthukumar (2026) Phase I/II curvature predictions; Hermann & Lampinen (2020) / Shah et al. (2020) simplicity bias and loss landscape; Liu et al. (2021) JTT annotation-free upweighting baseline; Nam et al. (2020) GEORGE; Zhang et al. (2022) SSA; Hochreiter & Schmidhuber (1997) / Keskar et al. (2017) flat minima theory.

</phase1-input>

---

## Session Insights

### Key Discoveries

- **h-e2-k CONFIRMS Hessian trace signal (AUROC=0.9086 at K=20, 0.9130 at K=50)**: The 8th brainstorm's primary hypothesis was correct. The signal failure was only in the K=10 calibration sub-test (delta_10_20=0.011 > 0.01 threshold), not in the discriminability claim. This is the most important finding from the Serena Memory synthesis.
- **h-m4's bottleneck is now addressable**: ERM-trained features (h-e1 training produces them) + Hessian trace proxy (h-e2-k validated) = annotation-free DFR at WGA ≥ 85% (predicted). Previous failure was specifically due to frozen pretrained features, not proxy quality.
- **Trajectory analysis is the missing piece**: All previous hypotheses measured at a single t*. The SCSL Foundations track explicitly asks for understanding of how shortcut reliance emerges. A monotonically growing Hessian trace ratio across training epochs IS the mechanistic evidence — and it has never been measured.
- **Epoch-0 falsifiability control**: Checking Hessian trace at epoch 0 (pretrained, no Waterbirds training) directly tests whether the asymmetry is a pretrained artifact (like h-e2) or a genuine ERM-learned curvature gap. This design distinguishes the 9th iteration from h-e2.
- **Two-in-one contribution**: Mechanism (trajectory characterization → SCSL Foundations) + Application (Hessian-DFR on ERM features → SCSL Solutions). Dual relevance maximizes workshop impact.

### Techniques Used

ROUTE_TO_0 Mode — 9th iteration. Synthesis from: Serena Memory (h-e1 run1/run2 FAIL, h-m1 FAIL, h-m4 FAIL, superseded_h-e1, h-e2 run1 FAIL, h-e2-k run1 FAIL-but-SIGNAL-CONFIRMED) + Snapshots (h-e1 PASS AUROC=0.9402; h-e2-k K=20 AUROC=0.9086 K=50 AUROC=0.9130; h-m4 ERM feature fix identified) + archived brainstorms (8th iteration: Hessian trace existence → NOW CONFIRMED) + ICLR 2025 SCSL Workshop CFP extraction (Foundations pillar 3: loss landscape, trajectory characterization) + feasibility constraints (existing data, existing infrastructure, K=50 Hutchinson already validated).

### Areas for Further Exploration

- **SAM intervention test**: If minority samples have higher Hessian trace (sharper curvature), SAM training should preferentially reduce minority sample sharpness → does SAM reduce the Hessian trace gap between minority and majority? This would be a mechanistic explanation of SAM's robustness benefits.
- **NLP generalization**: CivilComments, MultiNLI — does Hessian trace asymmetry generalize to language models with lexical spurious correlations? Transformer architecture with different inductive biases.
- **Fisher information matrix trace**: Equivalent to Hessian under cross-entropy at convergence; computationally cheaper if using empirical Fisher; per-sample FIM trace as alternative curvature measure.
- **CelebA secondary benchmark**: Per-sample Hessian trace at multiple epochs on CelebA (hair color / gender spurious correlation) — generalization of trajectory findings.
- **Mathematical connection**: Formal derivation linking clean/spurious feature decomposition to predicted Hessian trace asymmetry direction — would strengthen SCSL Foundations paper contribution.
- **ViT/transformer architectures**: Attention-based models have different curvature profiles; does Hessian trace asymmetry persist without convolutional inductive biases?

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

Focus Phase 1 search on:
1. **DFR with ERM features and annotation-free proxies** (Kirichenko et al., 2022): What WGA does DFR achieve on Waterbirds with ERM features? What annotation-free proxy variants exist? Confirm oracle WGA baseline (~88%).
2. **Per-sample Hessian trace trajectory during ERM training**: Does any existing work measure per-sample or per-group Hessian trace across training epochs? Monotonicity predictions?
3. **Sharpness and spurious correlations connection**: Does existing work connect SAM / flat minima to group robustness? Any curvature-based analysis of minority vs. majority loss landscape?
4. **LaBonte & Muthukumar (2026) Phase I/II theory**: Specific predictions about Hessian trace / loss landscape curvature during Phase I (shortcut exploitation) and Phase II (invariant feature learning)?
5. **Yao et al. (2020) PyHessian**: Per-layer Hessian trace methodology across training; epoch-by-epoch sharpness tracking implementation reference.
6. **Sagawa et al. (2020)**: Exact SGD training protocol, checkpoint saving, group accuracy at each epoch — confirm t*=4 from h-e1 is the right DFR epoch.
7. **h-e2-k infrastructure**: Confirm K=50 implementation details for 5-checkpoint trajectory computation; estimate total compute budget.

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Mode: ROUTE_TO_0 (Failure Recovery — 9th iteration: h-e2-k CONFIRMED Hessian trace signal at AUROC=0.9086 K=20 / 0.9130 K=50; advancing to trajectory mechanism characterization + DFR application on ERM features)*
*Ready for: Phase 1 - Targeted Research*
