# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-05T06:30:00Z
- **Workflow**: phase2a-dialogue 
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation) 
- **Gap ID**: GAP-001
- **Gap Title**: No training-free, single-pass evaluation of raw logit-lens uncertainty statistics (entropy / max-prob) as per-layer hallucination-detection AUROC scores
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Self-judged convergence at exchange 15 (minimum threshold): all 6 criteria (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) passed with per-exchange evidence; all 6 personas participated; Prof. Rex closed the stress-test ledger with no remaining design objections.

### Key Insights
- The h-e1 failure is best explained as calibration suppression at the final layer, not absence of signal — the mechanism retrodicts both the 0.5186 miss and the direction inversion.
- Kim et al. 2025's adversarial alignment result is answered by measurement scope: single-token trajectories are not full-distribution statistics; their own 97%-positive prediction-depth correlations show residual signal.
- Within-model rescue framing (intermediate vs final on the same LLaMA-2 checkpoint) cancels the base/instruct confound by construction.
- Honest vocabulary adopted: "training-free scoring, label-efficient selection"; the logistic fusion is quarantined as the only trained component.
- P1 (rescue) and P2 (transfer) are separable claims: a transfer failure must not contaminate the rescue verdict.

### Breakthrough Moments
- **Exchange 6** — Dr. Ally's within-model restructure of the rescue claim, dissolving Prof. Rex's confound objection by construction.
- **Exchange 7** — Dr. Nova's unresolved-candidate-competition mechanism, converting Entropy-Lens's validated expansion/pruning reading into a hallucination account that makes all three signals natural rather than ad hoc.
- **Exchange 8** — Prof. Vera's leak-closing protocol: direction signs frozen from the selection split, paired bootstrap on AUROC differences — turning a 192-candidate fishing risk into disciplined selection.
- **Exchange 13** — Mechanism upgraded to three falsifiable steps that retrodict both h-e1 anomalies.

---

## Final Hypothesis

### Title
Depth-Resolved Logit-Lens Uncertainty Signals for Architecture-Robust Hallucination Detection (H-LayerLensUQ-v2, confidence 0.72)

### Core Claim
Under white-box, single-greedy-pass inference on TriviaQA and TruthfulQA with LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct, **if** hallucination scores are computed as per-layer logit-lens uncertainty statistics (Shannon entropy, max-token probability, adjacent-layer KL divergence, averaged over answer tokens) with (layer, signal, direction) selected per model on a held-out selection split, **then** the selected intermediate-layer score achieves test-split AUROC ≥ 0.60 on both datasets for all three models AND on LLaMA-2-7B exceeds the final-layer entropy baseline (0.5186) with a 95% paired-bootstrap CI on the difference excluding zero, **because** intermediate layers preserve the separation between resolved (factual) and unresolved (hallucinated) candidate competition that final-layer output calibration — tokenizer- and tuning-dependent — suppresses.

### Mechanism
1. **Separation exists at depth**: factual answers resolve candidate competition at intermediate layers; hallucinations show elevated entropy, contested max-prob leaders, and persistent inter-layer revision (grounded in Entropy-Lens's validated expansion/pruning correspondence, Spearman 0.74–0.88).
2. **Final-layer calibration suppresses it**: tokenizer- and tuning-dependent output sharpening collapses the gap at layer 32.
3. **Suppression is architecture-dependent**: worst in base LLaMA-2-7B, mildest in RLHF-tuned LLaMA-3-8B-Instruct — retrodicting both the h-e1 miss and its direction inversion; per-model depth selection restores robustness.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (primary) | LLaMA-2-7B rescue: selected intermediate layer beats final-layer entropy | AUROC ≥ 0.60 both datasets AND paired-bootstrap ΔAUROC CI > 0 on TriviaQA | No screened layer clears CI separation → hypothesis dies (Tier 1) |
| P2 | Cross-dataset layer transfer TriviaQA↔TruthfulQA | Transfer gap ≤ 0.05 AUROC and ≥ 0.60, both directions, per model | Either direction below tolerance → per-domain selection required (separable finding) |
| P3 | KL-entropy complementarity via 2-parameter logistic fusion | Fusion gain ≥ 0.02 with CI excluding zero (majority of cells) | Gain indistinguishable from zero → turbulence redundant with width (informative null) |
| P4 | No-regression guard on Mistral/LLaMA-3 | Intermediate ≥ final − 0.02 on all four cells | Pivot sacrifices working architectures → robustness rejected |

---

## Novelty
First AUROC evaluation of raw logit-lens uncertainty statistics as training-free, single-pass hallucination-detection scores with per-model held-out layer selection; first cross-dataset layer-transfer measurement; first controlled rescue test on an architecture with a documented final-layer failure baseline. Differentiated from Entropy-Lens (identical feature, never for detection), FEPoID (supervised probing + intrinsic-dimension selection), Kim et al. 2025 (final-token trajectories only — answered by scope), SAPLMA (trained probe), END/DoLa (decoding-time only), and h-e1 (final-layer scalar only). HalluShift novelty check scheduled in Phase 2B.

---

## Experimental Design
- **Datasets**: TriviaQA rc.nocontext validation[:1000]; TruthfulQA generation validation (817) — h-e1 prompts/labels verbatim.
- **Models**: LLaMA-2-7B base (rescue stress test), Mistral-7B-v0.1, LLaMA-3-8B-Instruct — identical to h-e1.
- **Extraction**: one greedy pass, `output_hidden_states=True`, per-layer `lm_head(model.norm(h_l))` in float32; 3 signals × 32 layers, mean over answer tokens; per-token stats cached; streaming scalars only; v1 code + 871/1000 llama2/TriviaQA cache reused.
- **Discipline**: stratified 50/50 selection/test (seed 42, test locked); degeneracy screen, selection, direction freezing, fusion fitting on selection split only; paired bootstrap n=1000 on test.
- **Baselines**: final-layer mean entropy (must reproduce h-e1 refs ±0.03), final-layer max-prob; FEPoID supervised skyline deferred to Phase 5.
- **Diagnostics**: direction-pattern report (familiarity flag), length-stratified AUROC, mechanism-activation indicators.

---

## Limitations
- **R1 Recall shadow**: the diagnostic can flag but not exclude a familiarity-based mechanism (Chi et al. 2025); claims are "separation under standard labels," never "truthfulness detection."
- **R2 Transfer fragility**: SAPLMA's layer shift and FEPoID's cross-dataset variability make P2 genuinely uncertain; P1/P2 reported separably.
- **R3 Instruct asymmetry**: LLaMA-3 is the only instruct model; cross-model depth patterns stay descriptive.
- **R4 Generalization ceiling**: two QA datasets, three 7–8B families, greedy decoding; TruthfulQA n=817 gives wide CIs (CI clauses anchor on TriviaQA).

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Self-judged CONVERGED at exchange 15/15 minimum; all 6 criteria passed; ledger closed |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (permanent caveats R1–R4 attached with mitigations) |

---
