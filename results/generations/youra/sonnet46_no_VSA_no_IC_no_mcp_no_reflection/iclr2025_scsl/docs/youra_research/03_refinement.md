# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-31T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation — no orchestrate_exchange.py)
- **Gap ID**: gap1
- **Gap Title**: Mechanistic Characterization of SGD-Driven Temporal Feature Learning Order
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 11

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 11

**Convergence Reason**: All 6 criteria (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) met at Exchange 10–11. Endorsed by all personas including Prof. Rex with precision caveats.

### Key Insights
1. **Directional vs. magnitude gradient signals**: The key novelty is that gradient cosine similarity (direction) distinguishes spurious-minority samples from hard-but-spurious-majority samples — a distinction magnitude-based methods (JTT, LfF) cannot make.
2. **Last-layer tractability**: Computing per-sample gradients only at the last linear layer (4096 floats for ResNet-50) makes the method computationally feasible within a single GPU run.
3. **Mechanism precision**: The signal detects "statistical minority in batch" not strictly "spurious feature direction" — these coincide on Waterbirds/CelebA, making the empirical claims valid while limiting mechanistic generality.
4. **Single-pass advantage**: GAD operates online in a single training run, eliminating JTT's two-stage compute overhead.

### Breakthrough Moments
- **Exchange 4** (Prof. Pax): Identified that last-layer-only gradient tracking makes the method computationally feasible (~200MB, 30 GPU-hours total)
- **Exchange 5** (Dr. Ally): Synthesized the directional vs. magnitude novelty claim and two-level validation structure (diagnostic P1 gates intervention P2)
- **Exchange 7** (Dr. Nova): Articulated the hard-spurious-majority differentiating prediction that distinguishes GAD from JTT
- **Exchange 11** (Prof. Rex): Precision caveat on mechanism scope — clarifies what the method detects and ensures claims are not overclaimed

---

## Final Hypothesis

### Title
**Gradient Alignment Debiasing (GAD)**: Online Annotation-Free Upweighting via Per-Sample Gradient Cosine Similarity

### Hypothesis ID
`H-GAD-v1`

### Core Claim (Under-If-Then-Because)
Under standard ERM training on spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI) with random mini-batch sampling, **if** we compute the cosine similarity between per-sample last-layer gradients and the batch-mean gradient during training and use the EMA-smoothed inverse alignment score as an online importance weight, **then** the trained model will achieve better worst-group accuracy than JTT and LfF baselines, **because** gradient alignment direction specifically captures spurious-minority membership (conflicting gradient direction with majority batch) in a way that magnitude-based proxies cannot distinguish from hard-but-spurious-majority samples.

### Mechanism
1. Spurious-majority samples dominate random mini-batches (~82% on Waterbirds); the batch-mean gradient encodes the spurious feature direction.
2. Spurious-minority samples cannot be classified via the spurious feature; their gradients conflict with the batch-mean gradient → low cosine similarity.
3. Hard-but-spurious-majority samples have high loss but aligned gradients (they still encode the correct spurious-direction gradient).
4. Inverse alignment score (EMA-smoothed, clipped at 5×) upweights spurious-minority samples online during training.
5. Online upweighting prevents the model from fully committing to the spurious feature during the critical early training phase — in a single pass.

---

## Predictions

### P1 (Primary — Diagnostic)
**Gradient alignment ROC-AUC > per-sample loss ROC-AUC** for predicting spurious-minority membership on Waterbirds and CelebA at ≥ 1 training epoch (using existing group annotations as evaluation ground truth only).

- **Test**: Track alignment and loss at epochs {1, 5, 10, 25, 50}; compute ROC-AUC; compare.
- **Success**: Alignment ROC-AUC > loss ROC-AUC at ≥ 1 epoch on BOTH datasets.
- **Falsification**: Alignment ROC-AUC ≤ loss ROC-AUC at ALL epochs on EITHER dataset.

### P2 (Intervention)
**GAD worst-group accuracy ≥ JTT** on Waterbirds and CelebA (single training run, 3 seeds, mean ± std).

- **Test**: Train GAD (ERM + online alignment upweighting); compare to JTT (anniesch/jtt).
- **Success**: GAD ≥ JTT on BOTH datasets.
- **Falsification**: GAD < JTT on EITHER dataset (outside error bars).

### P3 (Mechanistic — Temporal Analysis)
**Penultimate-layer gradient alignment** becomes predictive of spurious-minority membership (ROC-AUC > 0.6) at an earlier training epoch than last-layer gradient alignment.

- **Test**: Track both layers at same epochs; compare first epoch of ROC-AUC > 0.6.
- **Success**: Penultimate layer achieves > 0.6 ROC-AUC at earlier epoch on ≥ 1 dataset.

---

## Novelty

**Key innovation**: First annotation-free debiasing method using per-sample gradient *cosine similarity* (directional) as a training-time spurious-minority proxy. No existing method (JTT, LfF, DFR) exploits gradient direction information.

| Prior Work | Our Difference |
|-----------|---------------|
| JTT (Liu 2021) | Binary misclassification after 2-stage training; 2× compute; conflates hard examples. GAD: continuous directional signal, single pass, handles hard-spurious-majority correctly. |
| LfF (Nam 2020) | Parallel biased model (2× memory); GCE hyperparameter. GAD: last-layer tracking only (~200MB), no biased model. |
| DFR (Kirichenko 2022) | Requires group-labeled held-out set. GAD: fully annotation-free during training. |

---

## Experimental Design

**Datasets**: Waterbirds, CelebA (primary); MultiNLI (secondary)  
**Model**: ResNet-50 (pretrained, ImageNet); BERT-base (MultiNLI)  
**Codebase**: Fork of kohpangwei/group_DRO; add ~50 lines PyTorch using torch.func.vmap  
**Compute**: ~30 GPU-hours total; single machine feasible  
**Batch size**: 32 (required for per-sample gradient tracking on ResNet-50 last layer)  

**Experiment 1** (Diagnostic): ERM training → track alignment + loss at 5 checkpoints → ROC-AUC comparison vs. group annotations  
**Experiment 2** (Intervention): GAD vs. ERM / JTT / LfF / ERM+L2 → worst-group accuracy  
**Ablations**: EMA β ∈ {0.5, 0.9, 0.99}; weight clip ∈ {2, 5, 10}; balanced vs. random batching; last-layer vs. penultimate layer

---

## Limitations

1. **Mechanism precision**: The signal detects "statistical minority in batch," which coincides with spurious-minority on Waterbirds/CelebA but is not guaranteed to generalize to settings with class-balanced batching.
2. **Batch size constraint**: Per-sample gradient computation requires batch_size ≤ 32; larger models (ViT-B) require gradient checkpointing.
3. **EMA hyperparameter sensitivity**: β must be tuned; extreme values cause lag (β = 0.99) or instability (β = 0.5).
4. **Scope limited to random-sampling training**: Method does not apply to group-balanced or class-balanced mini-batch strategies.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-GAD-v1 |
| **Discussion Convergence** | 11 exchanges; all 6 criteria met; all personas endorsed |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Mechanism precision caveat (benign for target benchmarks); memory constraint (documented) |

---

*Phase: 2A — Dialogue*  
*Total discussion time: 11 exchanges (self-contained loop, inline, unattended)*  
*Architecture: Independent Controller Ablation (no external orchestrate_exchange.py)*
