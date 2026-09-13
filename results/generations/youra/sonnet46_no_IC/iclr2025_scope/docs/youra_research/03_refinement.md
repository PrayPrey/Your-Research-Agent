# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-05T00:00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1
- **Gap Title**: No Empirical Study Linking Pre-Trained Weight Effective Rank to Optimal LoRA Rank
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Version**: v11 (recursive entry from h-e1 Phase 4 FAIL)

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15 (MIN_EXCHANGES=15 reached; converged exactly at threshold)

**Convergence Reason**: All 6 criteria (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) PASS at Exchange 15. All 6 personas participated.

### Key Insights

1. **h-e1 failure was metric ceiling, not mechanism failure**: Spectral entropy CV is inherently bounded ~0.03-0.08 for pretrained transformers. Effective rank (erank) uses the normalized singular value distribution and has a wider dynamic range — the redesign is principled.

2. **Marginal oracle is scientifically valid**: The PARA oracle (per-layer independent rank sweep, other layers frozen at r=8) measures each layer's marginal contribution — the same conceptual framing as AdaLoRA's per-triplet importance scoring. Marginal ≠ joint-optimal, but it's the right ground truth for a per-layer predictor.

3. **Positive direction theoretically derived**: High-erank matrices have spread-out singular spectra → no dominant subspace → task-relevant LoRA updates must span non-dominated directions → higher rank needed. This derivation enables one-tailed preregistration, preventing post-hoc direction flip.

4. **IFCLoRA validates the structural-predictor premise**: IFCLoRA (2026) shows that pre-training structure predicts optimal rank before fine-tuning using activation statistics. erank does the same with purely structural information (no data required) — a qualitative improvement in task-agnosticity.

### Breakthrough Moments

- **Exchange 4**: Prof. Pax's marginal oracle clarification — resolved the joint-vs-marginal concern by establishing conceptual alignment with AdaLoRA's per-triplet scoring.
- **Exchange 7**: Dr. Nova's positive direction derivation — transformed Prof. Rex's falsification concern into a theoretical contribution and enabled one-tailed preregistration.
- **Exchange 11**: Dr. Ally's complete H-erank-v1 synthesis with P1-P5 — the hypothesis became fully specified and testable.
- **Exchange 13**: erank-truncation criterion (oracle-free secondary analysis) — potential bypass for the expensive 15-day oracle sweep.

---

## Final Hypothesis

### Title
Effective Rank as Zero-Shot LoRA Rank Predictor: erank(W₀) Correlation with Per-Layer Marginal PARA Oracle Ranks

### Hypothesis ID
H-erank-v1

### Core Claim
Under pre-trained transformer models {BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224} with adequate fine-tuning (≥3 epochs NLP; ≥5 epochs ViT), if per-layer effective rank erank(W₀) = exp(H(σ/‖σ‖₁)) is computed from pretrained weights (fp32, before fine-tuning), then it demonstrates statistically significant positive Pearson correlation (r ≥ 0.65, one-tailed H₁: α > 0) with per-layer marginal PARA oracle ranks (argmax over r ∈ {4,8,16,32,64} on validation accuracy, all non-target layers frozen at r=8) across ≥2 of 3 model families, because effective rank captures the geometric complexity of each layer's pre-training representation.

### Mechanism
Pre-training shapes weight matrix singular value distributions. Layers performing complex, distributed transformations (deep FFN, later attention) develop spread-out singular spectra (high erank). During LoRA fine-tuning, these layers require higher-rank updates because task-relevant signal must be captured in directions not dominated by pre-training structure. Layers with concentrated spectra (low erank) need only low-rank updates — task signal aligns with dominant singular directions. The PARA oracle independently discovers this structure, producing oracle ranks that positively correlate with erank(W₀).

---

## Predictions

| ID | Type | Statement | Success Criterion |
|----|------|-----------|-------------------|
| P1 | **PRIMARY** | Pearson r(erank, oracle_rank) ≥ 0.65 in ≥2/3 families | r ≥ 0.65, one-tailed p < 0.05, ≥2/3 families |
| P2 | Secondary | erank-proportional assignment within 1% of oracle, outperforms uniform r=8 | accuracy gap ≤ 1% vs oracle AND above uniform baseline |
| P3 | Mechanism | ‖ΔW_opt‖_F/‖W₀‖_F correlates with erank at Spearman ρ ≥ 0.5 | ρ ≥ 0.5 for ≥2/3 families |
| P4 | Tercile | Levene p < 0.05 on oracle ranks by erank tercile or layer-type | p < 0.05 in ≥2/3 families |
| P5 | Alt-metric | Spearman ρ(erank, PR) ≥ 0.8 | ρ ≥ 0.8 for all 3 families |

**Failure taxonomy (pre-specified):**
- r < 0 for ≥2/3 families → direction wrong, mechanism needs revision
- 0 < r < 0.65 for all families → signal exists but too weak; threshold miscalibrated; partial success
- r ≥ 0.65 in ≥2/3 families → P1 validated, full success

---

## Novelty

**What's New**: First empirical study correlating erank(W₀) with PARA oracle ranks per layer. First zero-data (no calibration), task-agnostic, purely structural LoRA rank predictor. First cross-architecture evaluation (NLP + ViT) of a W₀-based rank predictor.

**Differentiation**:
- vs AdaLoRA (2023): erank uses W₀ before training; AdaLoRA uses ΔW during training
- vs IFCLoRA (2026): erank requires no calibration data; IFCLoRA requires 128-sample forward pass
- vs LAARA (2026): erank requires no gradient computation; LAARA uses training warmup gradients
- vs PiSSA/LoRA-XS: those use W₀ SVD for initialization only — rank is still fixed

---

## Experimental Design

**Models**: BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224 (HuggingFace pretrained, fp32)

**Tasks**: GLUE MNLI + SST-2 (NLP); CIFAR-10 (Vision)

**PARA Oracle Protocol**: For each layer l, sweep r ∈ {4,8,16,32,64} with other layers at r=8; oracle_rank_l = argmax_r validation_accuracy. ~360 runs for BERT-base (5 ranks × ~72 matrices). Parallelize 5 matrices/GPU on 5×H100. Estimated total: ~15 days.

**Stage 1 Quick-Check** (recommended before full sweep): Compute erank for DeBERTa-v3-base; compare to AdaLoRA's published learned rank allocations. If correlation is promising (r > 0.4), proceed to full oracle.

**Baselines**: Uniform LoRA r=8; AdaLoRA; PARA oracle (upper bound)

---

## Limitations

- Marginal oracle ≠ joint-optimal allocation; cross-layer compensation effects not measured
- Tested only on base-scale models; generalization to large LLMs (LLaMA-7B+) not validated
- Cross-architecture tested only on CIFAR-10; other vision tasks (detection, segmentation) not covered
- erank collapses full singular value spectrum to one scalar; full spectrum has more information
- P1 has no prior direct empirical support — direction is theoretically derived, not previously measured

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria PASS at Exchange 15 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | P1 no prior empirical support (acknowledged); oracle duration ~15 days (Stage 1 check recommended); task-agnosticity needs ≥2 NLP tasks (SST-2 added) |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A-Dialogue Self-Play Loop (IC-ablation, v11 recursive entry)*
*Hypothesis: H-erank-v1 | Gap: gap-1 | Exchanges: 15 | Convergence: Exchange 15*
