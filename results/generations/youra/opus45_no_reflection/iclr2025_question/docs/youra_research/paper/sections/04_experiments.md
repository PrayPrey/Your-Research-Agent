# Experiments

Our experiments address three questions derived from our hypothesis:

**Q1 (Existence).** Do hidden states encode a correctness signal surpassing random chance?  
**Q2 (Mechanism).** Which layer depth is optimal, and does the inverted-U pattern hold?  
**Q3 (Comparison).** Does the probe exceed output-level baselines?

## Experimental Setup

**Model.** Llama-3-8B-Instruct with greedy decoding (temperature=0) and max 128 new tokens.

**Dataset.** TriviaQA validation split: 9,500 training samples, 1,700 validation samples. We use exact-match evaluation against reference answers for correctness labels.

**Hidden state extraction.** We extract last-token hidden states at each target layer using PyTorch forward hooks. Extraction adds negligible overhead (verified: -3.4% vs baseline timing).

**Probe training.** Logistic regression with $C=10^{-3}$, balanced class weights, LBFGS solver. We standardize features (StandardScaler) before training.

## Experiment 1: Existence (H-E1)

**Goal.** Verify hidden states contain *any* correctness signal above random (AUROC > 0.60).

**Method.** Train probe on layer 15 (50% depth) hidden states. Evaluate AUROC on held-out validation set.

**Success criterion.** AUROC > 0.60 (substantially above random 0.50).

## Experiment 2: Layer Sweep (H-M2)

**Goal.** Characterize AUROC across layers and identify optimal depth.

**Method.** Train separate probes at 8 layer depths: L3 (12.5%), L7 (25%), L11 (37.5%), L15 (50%), L18 (60%), L23 (75%), L27 (87.5%), L31 (100%). Each uses 500 training samples for efficiency; final evaluation on 200 held-out samples.

**Success criteria.**
1. Peak AUROC at middle layers (40–70% depth)
2. L60% AUROC > L100% AUROC (middle > final)
3. Inverted-U pattern: early < middle > late

## Experiment 3: Baseline Comparison (H-M4)

**Goal.** Quantify probe advantage over output-level uncertainty metrics.

**Method.** On same validation set, compute token entropy and sequence NLL for each sample. Compare AUROC: probe vs. entropy vs. NLL.

**Success criterion.** Probe exceeds token entropy by ≥5 AUROC points.

## Implementation Verification (H-M1, H-M3)

**Hook non-intrusiveness (H-M1).** Before main experiments, we verify that forward hooks do not affect model outputs. We generate answers with and without hooks, measuring output identity rate and timing overhead. Required: 100% identity, <10% overhead.

**Probe convergence (H-M3).** We verify the linear probe learns a non-trivial mapping by tracking training convergence and comparing to random baseline (AUROC ≈ 0.50).
