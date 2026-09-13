# 4. Experimental Setup

Section 3 described a pipeline whose every component answers a documented failure; we now specify the tests it was built to pass. The staged verification design evaluates its first tier here — existence — and we state at the outset what that tier does and does not measure: all quantities below are computed on the selection split, from a single seed, with no confidence intervals. The locked test splits were never evaluated. Nothing in this paper is held-out performance, and we flag this at every point where a reader might otherwise assume it.

## 4.1 Research questions

Three questions structure the evaluation, each instantiating one of the Introduction's contributions.

**RQ1 (Existence — Contribution 1).** Does at least one screened intermediate (layer, signal) pair per model achieve selection-split corrected AUROC $\geq 0.55$ on *both* datasets — that is, in all six model $\times$ dataset cells? This is the gate the entire staged design conditions on: if no training-free signal exists at depth, the deployable-detector tier has nothing to deploy.

**RQ2 (Depth beats final — Contribution 2).** Does the best screened intermediate layer exceed the *same sweep's* final-layer entropy readout in every cell? A yes, even as a point estimate, extends the intermediate-over-final consensus to statistics that need no probe, and is the direction the calibration-suppression reading predicts.

**RQ3 (Protocol-internal validity — Contribution 4).** Is the evaluation protocol internally valid by its own instruments — donor-cache identity verified before any reuse, within-sweep baselines computed per cell, and zero spurious halts? RQ3 exists because its predecessor failed: the v1 anchor, gated on cross-protocol numbers, was unsatisfiable by construction (Section 3.5), and the redesign must demonstrate that validity checking survives without it.

## 4.2 Datasets

We evaluate on TriviaQA (rc.nocontext, the first 1,000 validation questions — a deterministic slice, not a random sample) and TruthfulQA (generation split, all 817 questions). The pairing is deliberate on two axes. First, lineage: both datasets carry the documented final-layer failure record that motivates this study, so the comparison to that record's conditions is as controlled as a cross-protocol comparison can be. Second, label protocol: TriviaQA labels come from normalized-alias exact match, TruthfulQA labels from similarity to curated correct and incorrect reference answers. These are different measurement instruments for "hallucination," and passing the existence gate under both is a robustness check on the signal rather than an accident of one label rule.

Each dataset is split 50/50 into selection and test splits, stratified by label, seed 42 (500/500 on TriviaQA; 408/409 on TruthfulQA). The test split is locked at split time and never read by any analysis reported here; all selection-sensitive operations — screening, tuple selection, direction correction, gating — are confined to the selection split.

## 4.3 Baselines

The baseline for RQ2 is the **within-sweep final-layer entropy AUROC**: L32 entropy from the same greedy pass, same teacher-forced re-forward, same labels, same split, computed per cell (final-layer max-probability is recorded alongside). This choice is not convenience but consequence. The anchor forensics of Section 3.5 showed that six protocol differences moved a final-layer AUROC on the same model and nominal dataset by more than double the anchor tolerance; after that demonstration, a cross-protocol number pasted in as a baseline is not a baseline, and the only comparison we consider valid is one computed inside the protocol it is compared against.

Supervised intermediate-layer probes (FEPoID-class methods, reported AUROC roughly 0.73–0.85) are cited as a skyline but not re-run: they consume labeled training data and per-model probe fitting, a different resource class from training-free selection, and re-running them under this protocol is outside the existence tier's scope. No external baselines were re-executed; every comparison in Section 5 is within-sweep.

## 4.4 Implementation details

All three checkpoints — LLaMA-2-7B, Mistral-7B-v0.1, LLaMA-3-8B-Instruct — are frozen 32-layer pre-LN decoders run in fp16 on a single H100. Each example receives one greedy generation (`do_sample=False`, `max_new_tokens=32`) followed by one teacher-forced re-forward with `output_hidden_states=True`; all statistics are computed in float32 with a $\log(p + 10^{-12})$ guard. The full sweep scores 5,451 generations (1,817 per model) and streams per-example rows to resumable caches keyed by example id — the sweep survived three session interruptions without losing more than the in-flight example. The LLaMA-2/TriviaQA cell was reproduced from the prior run's finalized cache after the identity check of Section 3.5 passed 10/10, making it a zero-GPU cell; the remaining five cells were generated fresh (~2.5 GPU-hours). The implementation passes 37/37 tests and a REAL_MODEL reality check confirming that reported numbers derive from actual model forwards rather than fixtures.

## 4.5 Metrics and gate constants

The primary metric is **corrected AUROC**: $\max(a, 1-a)$ with the score direction recorded, selected on the selection split and frozen thereafter. AUROC is threshold-free and comparable across cells of very different base rates; the direction correction is not cosmetic but addresses the documented inversion failure mode — the motivating record's final-layer entropy flipped sign across checkpoints, and a method that assumes monotonicity inherits that fragility.

Gate constants, fixed before the sweep: existence requires corrected AUROC $\geq 0.55$; the degeneracy screen drops layers whose mean entropy lies within 1% of $\ln|V|$ or whose top-1 agreement with the final layer is below 5%, with screen health requiring $\geq 5$ retained layers per model. RQ2 is evaluated as a per-cell direction check on point estimates — the existence tier pre-registers no statistical test, and we report it accordingly.
