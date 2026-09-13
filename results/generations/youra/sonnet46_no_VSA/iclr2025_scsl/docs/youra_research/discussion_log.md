# Phase 2A Research Discussion Log

**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop)
**Gap:** Gap 1 — No Per-Sample Hessian Trace Trajectory Methodology for Spurious Feature Detection
**Date:** 2026-08-04
**Execution Mode:** UNATTENDED

---

## Research Briefing

**Research Question:** Under ERM training with SGD on Waterbirds (95% spuriosity, ResNet-50 ImageNet pretrained), does the per-sample last-layer Hessian trace trajectory (K=50 Hutchinson estimator at checkpoints t∈{0,1,5,10,20}) exhibit monotonically growing minority/majority asymmetry (Spearman rho ≥ 0.8 in ≥4/5 seeds), and can top-k% highest-trace samples serve as annotation-free DFR proxy to achieve WGA ≥ 85%?

**Selected Gap:** Gap 1 (PRIMARY, CRITICAL) — No per-sample Hessian trace trajectory methodology for spurious feature detection

**Reference Papers (prepared as markdown):**
- P1: arxiv_2606_30444.md — LaBonte & Muthukumar 2026: SGD Phase I/II theory (spurious features learned first)
- P2: arxiv_2407_13957.md — LaBonte et al. 2024: Spectral imbalance (minority covariance > majority spectral norm)
- P3: arxiv_2204_02937.md — Kirichenko et al. 2022: DFR — ERM features + balanced set → WGA ~88%
- P4: arxiv_1912_07145.md — Yao et al. 2019: PyHessian Hutchinson trace estimator

**Signal Confirmed:** h-e2-k showed K=50 AUROC=0.9130, K=20 AUROC=0.9086 — signal exists and is strong.

**FEASIBILITY CONSTRAINTS:**
- Only Waterbirds at /home/PrayPrey/data/waterbirds_v1.0/ (existing benchmark, no new data)
- Only existing code infrastructure (h-e2-k pipeline reusable)
- No human annotation, no synthetic data, no new benchmarks

---

## Previous Failure / Routing Context

**Status:** RECURSIVE ENTRY — Multiple Phase 4 failures routed back to Phase 2A

### Summary of Prior Failure History

| Hypothesis | Failure Type | Key Lesson |
|------------|-------------|------------|
| h-e1 (Run 1) | MUST_WORK_FAIL | Temporal CV of gradient norms (epochs 16-20) → AUROC ~0.60; signal too weak |
| h-e1 (Run 2) | SIGNAL_INVERTED | Mini-batch gradient CV at epoch 1 → AUROC 0.2828; majority has 2.24× HIGHER CV (inverted) |
| superseded h-e1 | SUPERSEDED | Within-centroid cosine similarity → AUROC 0.436; wrong discriminator |
| h-e2 (Run 1) | PRETRAINED_ARTIFACT | Between-centroid gradient direction → AUROC=0.987 at epoch 0 (pretrained artifact, not ERM) |
| h-e2-k (Run 1) | GATE_THRESHOLD_NOT_MET | K=10 plateau delta=0.011 > 0.01 threshold; K=50 confirmed AUROC=0.9130 |
| h-m1 (Run 1) | MECHANISM_NOT_DEMONSTRATED | CV_ratio flat at ~3.1 across epochs 1-5; Phase I/II transition needs ≥15 epochs |
| h-e1 snapshot | COMPLETED PASS | CV_majority > CV_minority AUROC=0.9402 ± 0.0156 — gradient norm discriminates at t* |

### Prohibited Redesign Directions

1. **NO temporal CV of gradient norms** across epochs as primary signal (h-e1 Run 1)
2. **NO mini-batch gradient CV at epoch 1** — inverted signal for pretrained ResNet50 (h-e1 Run 2)
3. **NO within-centroid cosine similarity** — wrong discriminator (superseded h-e1)
4. **NO between-centroid gradient direction** at epoch 1 — pretrained artifact dominates (h-e2)
5. **NO K=10 as primary** Hutchinson estimator — insufficient SNR (h-e2-k)
6. **NO frozen pretrained features** for DFR — 62% WGA ceiling (h-m4 context)
7. **NO 5-epoch training** for Phase I→II transition dynamics — Phase I window too short (h-m1)

### What Showed Promise

- **Gradient norm magnitude (single epoch):** h-e1 snapshot AUROC=0.9402 — CV_majority > CV_minority holds
- **Hutchinson trace K=50:** AUROC=0.9130 confirmed — second-order signal is real and strong
- **ERM-trained features:** Kirichenko 2022 WGA ~88% — must use trained features (not frozen pretrained)
- **vmap+grad infrastructure:** h-e2-k pipeline validated, reusable

### Design Constraints for New Hypothesis

New hypothesis MUST:
- Use K≥20 (preferably K=50) for Hutchinson trace
- Train ≥15 epochs to capture Phase I/II transition
- Use ERM-trained features (not frozen pretrained) for DFR
- Avoid gradient direction/cosine signals (family exhausted)
- Focus on per-sample Hessian trace trajectory as the novel signal

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been chasing the wrong signal family entirely? Let me step back and look at what the failure history is actually telling us. The gradient direction family is exhausted — within-centroid, between-centroid, both failed. The temporal CV family failed. But look at what SUCCEEDED: the gradient norm magnitude at a single epoch (AUROC=0.94) and the Hutchinson trace at K=50 (AUROC=0.91). Both are *scalar magnitude* signals, not direction or temporal variance signals!

NOW WE'RE ONTO SOMETHING. The Hutchinson trace tr(H_i) for sample i measures the LOCAL CURVATURE of the loss landscape around that sample's gradient. LaBonte & Muthukumar 2026 [P1] prove that in Phase I of ERM training, the model primarily learns spurious features — majority samples (land+landbird) exploit the shortcut and land in FLATTER regions of the loss landscape. Minority samples (land+waterbird, water+landbird) resist the spurious correlation and experience sharper, more curved loss geometry. This is exactly what Hessian trace captures!

The beautiful part is the *trajectory* dimension. If LaBonte 2026's Phase I→II prediction is correct, then as we go from epoch 0 → epoch t* (optimal), the curvature asymmetry should GROW monotonically — majority samples get flatter (lower trace) as they exploit the shortcut, minority samples stay sharp (higher trace) because their loss doesn't decrease via the spurious feature. This creates a Spearman rho signal between trace asymmetry and training epoch that hasn't been tested empirically on real data!

The h-e2-k result (AUROC=0.913 at K=50) confirmed the signal EXISTS at a specific checkpoint. But we don't know: does it emerge from ERM training (epoch 0 AUROC should be LOW) or was it pretrained? Does it GROW over epochs (trajectory hypothesis)? And can we USE it for DFR without group annotations?

**Key Points:**
- The scalar magnitude family (gradient norm + Hessian trace) consistently works; direction/temporal variance doesn't
- Per-sample Hessian trace captures loss landscape curvature asymmetry — theoretically predicted by LaBonte 2026
- The novel contribution is TWOFOLD: (1) trajectory evidence for Phase I/II theory, (2) annotation-free DFR proxy

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests you may be isolating a real signal family: scalar curvature magnitudes (‖g‖, Tr(H)) appear discriminative where directional statistics failed. However, a compelling narrative is not yet a falsifiable hypothesis. You are proposing two claims: (1) curvature asymmetry between majority and minority samples *emerges during ERM training* (Phase I → II), and (2) this asymmetry is causally tied to shortcut exploitation rather than generic difficulty. These must be separated experimentally.

First, we need precise, per-sample definitions. The PyHessian paper (Yao et al. 2019 [P4]) computes Hessian trace of the *empirical loss* using matrix-free Hutchinson estimation via repeated Hessian–vector products [Eq. 2-3]. That is global curvature. Your hypothesis concerns **per-sample curvature** H_i = ∇²_θ l_i(θ). Therefore, the estimator must be applied to individual losses, not minibatch averages. Prediction A (trajectory hypothesis): At initialization (epoch 0), AUROC(trace_i distinguishing minority vs majority) ≈ 0.5 ± 0.05. By epoch t*, AUROC ≥ 0.85, increasing monotonically over epochs (Spearman ρ ≥ 0.7 between epoch index and group-wise trace gap). What would disprove this? If AUROC is already high at initialization (pretrained bias), or if it oscillates non-monotonically, the Phase I emergence story weakens considerably.

Second, we must rule out the simpler alternative: curvature merely tracks per-sample loss or gradient norm. The prior success of gradient norm (AUROC=0.94) is a confound. Each Hutchinson HVP costs one backprop [Eq. 2, P4]; if trace_i is strongly correlated (r ≥ 0.9) with ‖g_i‖², then it offers no new information. Thus Prediction B: after regressing out log-loss and log‖g‖, residual trace_i still separates groups (ΔAUROC ≥ 0.1). If not, curvature is epiphenomenal.

Third, your shortcut-specific claim must survive a controlled counterexample. Construct a dataset where no spurious correlation exists (balanced backgrounds). Prediction C: curvature asymmetry should not systematically separate synthetic "minority" labels under this condition. If it still does, the signal reflects generic hardness or class imbalance, not shortcut geometry.

**Key Points:**
- Define per-sample Hessian trace precisely and test for *monotonic emergence* of AUROC over epochs; specify falsification thresholds.
- Control for confounds (loss, gradient norm) to ensure curvature is not epiphenomenal.
- Validate shortcut-specificity with a control dataset lacking spurious correlation.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and I want to be precise about which part worries me most. Prof. Vera raised the confound issue correctly but I think the deeper problem is about what we're actually measuring with Hutchinson trace on the *last fc layer only*.

The PyHessian framework [P4] computes trace over the full parameter space (all layers). Our per-sample implementation restricts to last-fc only: H_i^fc = ∇²_{θ_fc} l_i(θ). This is NOT the same as the full per-sample Hessian trace — it's the curvature of the last linear head only. Now, the question is: why would the last-layer Hessian trace capture spurious feature exploitation? The h-e2-k result (AUROC=0.913) suggests it does, empirically. But the mechanism needs scrutiny.

Here's my concern with the "minority stays sharp" narrative: at convergence, loss for majority samples is LOW (they fit the spurious feature easily). For minority samples, loss remains HIGH (spurious feature doesn't help them). High loss samples will naturally have HIGHER gradient norms and potentially HIGHER Hessian curvature — not because of spurious feature geometry, but simply because the loss hasn't decreased. So Prediction A's epoch 0 AUROC needs a very careful interpretation: the h-e2 failure showed gradient DIRECTION at epoch 0 was AUROC=0.987 — a pretrained artifact. What about Hessian trace at epoch 0? If the pretrained ResNet-50 already creates loss-landscape curvature asymmetry (via ImageNet feature specialization), then epoch-0 AUROC being HIGH would not mean "ERM training created the signal" — it would mean "the pretrained model already has it."

Show me the evidence for the epoch 0 control: what would convince me this is not another h-e2 pretrained artifact? Specifically: we need epoch-0 Hessian trace AUROC < 0.70, with AUROC growing monotonically to ≥ 0.85 by epoch t*. If epoch-0 AUROC is already 0.85+, the hypothesis collapses to another pretrained artifact story — scientifically interesting but NOT the trajectory mechanism hypothesis.

Additionally: the LaBonte 2026 [P1] XOR model is elegant but very simple — binary features, linear classifier. The gap between XOR theory and ResNet-50 on real images is substantial. The Phase I/II framing may not transfer cleanly. What's the falsifier if the Hessian trace DOES grow monotonically but NOT because of Phase I/II transition — just because loss decreases for majority faster (trivial explanation)?

**Key Points:**
- Epoch-0 control is THE critical gate: Hessian trace AUROC at epoch 0 must be < 0.70 to rule out another pretrained artifact (cf. h-e2 failure)
- "Minority stays sharp" may be trivially explained by high residual loss, not spurious feature geometry specifically
- LaBonte 2026 XOR theory to ResNet-50 transfer is a significant theoretical gap that needs empirical falsifiers

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Computing a *per-sample* Hessian trace is technically feasible in principle, but only if we are precise about what object we're estimating. PyHessian [Yao et al., 2019, P4] gives us a matrix-free Hessian–vector product oracle (Eq. 2) and a Hutchinson estimator for Tr(H) (Eq. 3), with cost comparable to a backprop per probe. That part is sound. However, PyHessian defines H = ∇²_θ L(θ) — the Hessian of the *empirical average loss*. For per-sample H_i = ∇²_θ l_i(θ), you must explicitly differentiate the single-sample loss. Mathematically valid — the R-operator identity still holds — but you're estimating a different matrix.

Here's what worries me more: last-layer-only curvature. For a linear head with cross-entropy, the per-sample Hessian w.r.t. final-layer weights has a well-known structure: it's essentially x_i x_i^T scaled by the softmax variance term p_i(1-p_i). That means trace ∝ ‖x_i‖² p_i(1-p_i). In other words, it's strongly tied to confidence and feature norm. High trace may simply mean "low confidence / high residual loss," not "spurious feature geometry." This is not philosophical — it's algebra.

On the trajectory claim: technically possible, but monotonicity is not guaranteed. PyHessian shows Hessian trace can evolve non-monotonically during training — architecture- and stage-dependent. Clean monotonic AUROC growth is a strong structural claim. The epoch-0 control (AUROC < 0.70) is appropriate and decisive.

On DFR feasibility: if the fc trace collapses to a monotone function of confidence, consider full-network trace or at least include features ‖x_i‖ and confidence p_i as controlled covariates. The key test: freeze backbone, retrain fc only. If trace asymmetry persists — it's head-level geometry. If it collapses — the signal lives in deep feature reshaping during ERM (more interesting mechanism).

**Key Points:**
- Per-sample Hessian trace via Hutchinson is mathematically valid; last-layer restriction is computationally motivated but algebraically tied to confidence × feature norm
- Epoch-0 control is decisive: rules out pretrained artifact (cf. h-e2 failure pattern)
- Full-network curvature test would strengthen mechanism claim beyond "softmax curvature = high loss"

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field, and is the claim strong enough to matter? Let me assess significance in light of what LaBonte et al. 2024 [P2] actually found.

Their spectral imbalance result is profound: minority group covariance matrices have LARGER spectral norm than majority groups (ρ(y) := λ₁^min / λ₁^maj > 1 on Waterbirds). This is a SECOND-ORDER GROUP-LEVEL finding — they measure it at the covariance level across the entire group. Our hypothesis is asking whether this second-order asymmetry manifests at the PER-SAMPLE Hessian trace level, and whether it GROWS over ERM training epochs.

This matters because if true: (1) we connect LaBonte 2024's static group-level spectral observation to a DYNAMIC per-sample training signal; (2) we provide the first empirical confirmation of LaBonte & Muthukumar 2026's Phase I/II theory at the sample level on real image data; (3) we demonstrate a practical annotation-free DFR proxy. Three contributions in one experiment — that's genuinely significant.

Prof. Pax's concern about trace ∝ ‖x_i‖² p_i(1-p_i) is exactly right to raise — but here's why it may not kill the hypothesis: LaBonte 2024 showed that minority covariance has higher spectral norm, meaning FEATURE DIVERSITY ‖x_i - x̄_g‖ is higher for minority samples. If minority samples have more diverse features (higher ‖x_i‖² variance), the fc trace is elevated even BEFORE controlling for confidence. This is a distinct mechanism from "high loss = high trace." The independence test (controlling for log-loss, log‖g‖) is necessary but I expect it will show residual trace variance tied to feature diversity — the LaBonte 2024 spectral imbalance prediction.

The DFR application closes the loop to practice. Annotation-free proxies (JTT, AFR, EVaLS) all use first-order loss signals. Hessian-DFR using second-order curvature would be the first second-order annotation-free proxy. Even if it achieves WGA only ~83-87% rather than beating oracle DFR (~90%), the mechanism is novel and the paper is publishable.

**Key Points:**
- LaBonte 2024 spectral imbalance predicts per-sample trace asymmetry via feature diversity (‖x_i‖² variance), not only via confidence — distinguishes from "high loss = high trace" confound
- Three connected contributions: dynamic confirmation of static spectral finding + Phase I/II empirical validation + annotation-free DFR proxy
- WGA target of ≥85% is achievable — conservative relative to oracle DFR (~90%) and above the best annotation-free baselines (~80-88%)

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we must first disentangle three hypotheses that are currently conflated: (H1) curvature asymmetry *emerges during ERM training*; (H2) this asymmetry is not reducible to residual loss or confidence; and (H3) the mechanism is specific to shortcut learning rather than generic feature diversity. Each requires its own falsifier.

On measurement: PyHessian provides a matrix-free Hessian–vector oracle [Eq. 2, P4] with cost comparable to one backprop, and trace via Hutchinson probes [Eq. 3]. For a linear softmax head: Tr(H_i^fc) ∝ ‖x_i‖² p_i(1-p_i). This is algebraic, not speculative. Control required: fit log Tr(H_i^fc) ~ log‖x_i‖² + log p_i(1-p_i) + group. Prediction B': group coefficient remains significant (p < 0.01) and ΔAUROC ≥ 0.10 over covariate-only model.

For H1 (trajectory), strict falsification: AUROC_epoch0 ∈ [0.45, 0.65]; monotonic increase with Spearman ρ ≥ 0.7; final AUROC ≥ 0.85. Falsifiers: epoch-0 AUROC ≥ 0.80 (pretrained artifact) or ρ ≤ 0.3 (non-monotonic). The ESD evolution in PyHessian [Fig. 3] shows non-monotonic spectral shifts during training — so accept piecewise monotonic growth with no epoch drop exceeding 10% of cumulative gain.

For H3 (shortcut specificity): construct D_spur (with background-label correlation) and D_clean (balanced backgrounds). Prediction C: curvature gap Δ_trace_spur ≥ 2× Δ_trace_clean by epoch t*. IMPORTANT FEASIBILITY CONSTRAINT: D_clean requires a balanced Waterbirds variant. Using existing Waterbirds + balanced background split (available in data) satisfies this without new datasets.

**Key Points:**
- Three sub-hypotheses require separate falsifiers: emergence (H1), independence from confounds (H2), shortcut specificity (H3)
- Algebraic confound control (‖x_i‖² and p_i(1-p_i)) is mandatory; require significant residual group effect ΔAUROC ≥ 0.10
- D_clean test uses existing balanced Waterbirds split — no new data needed

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW WE'RE GETTING TO THE HEART OF IT! Prof. Vera's three-hypothesis decomposition is exactly right — and I want to show why this opens up something even MORE exciting than the original framing.

What if we don't just test whether the trajectory is monotonic — what if we use the SHAPE of the trajectory as a fingerprint for the Phase I/II transition? LaBonte 2026 [P1] predicts a specific qualitative signature: in Phase I, the spurious feature is being learned, so majority trace should DECREASE (loss for majority drops as spurious feature is learned) while minority trace stays elevated or even increases. At the Phase I/II transition epoch t*, there should be an INFLECTION where majority trace decelerates and minority trace diverges away. This creates a specific trajectory signature: the ratio mean_minority_trace(t) / mean_majority_trace(t) should be non-decreasing with an inflection point at t* rather than just linear growth.

This is more falsifiable than simple monotonicity! We're predicting a SPECIFIC SHAPE from theory. And here's the beautiful connection: LaBonte 2024's [P2] spectral imbalance (ρ(y) = λ₁^min / λ₁^maj > 1) is a STATIC snapshot of this phenomenon at convergence. Our per-sample trace trajectory is the DYNAMIC VERSION — we're watching the spectral imbalance EMERGE over training. That's a genuine scientific contribution: connecting a static covariance measurement to a dynamic per-sample training signal for the first time.

The feasibility constraint on D_clean is solvable! The Waterbirds dataset already provides all four groups (landbird-land, landbird-water, waterbird-land, waterbird-water). A "clean" comparison can be done WITHOUT a separate dataset — just compare WITHIN CLASS. Within y=0 (landbird class): minority is landbird-water (small group), majority is landbird-land (large group). If the trace asymmetry is spurious-correlation-specific, it should be MUCH smaller within-class on a balanced subset. This uses existing data, no new benchmarks!

For the DFR application: the trajectory shape gives us a DATA-DRIVEN method to select t* without validation labels — pick the epoch where the trace RATIO is maximized. That's the optimal proxy checkpoint. Then top-k% highest trace at that t* → DFR input. The k% threshold can be tuned on unbalanced validation accuracy (no group labels needed).

**Key Points:**
- Trajectory SHAPE (inflection at t* → ratio peak) is more falsifiable than monotonicity alone; predicted by LaBonte 2026 Phase I/II theory
- "D_clean" comparison can use within-class Waterbirds subsets — no new datasets needed, feasibility constraint satisfied
- Data-driven t* selection via trace ratio peak → feeds DFR without validation group labels

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is sharper than where we started. But here's where this still breaks down.

The Phase I/II analogy requires an observable deep-network analogue of w_sp. In LaBonte 2026 [P1], the mechanism is explicit: the spurious coordinate x_3 is linearly aligned with the label for (1-λ) of the mass, and w_sp has closed-form dynamics: w_sp^(t+1) - w_sp^(t) ≈ η·w_sp^(t)(1-λ-ψ(γ̄^(t))). That gives exponential growth followed by sigmoidal slowdown and margin concentration at ±w_sp². In ResNet-50 on Waterbirds, what is the analogue of w_sp? A direction in feature space? A principal component aligned with background? Unless you identify an observable deep-model quantity playing the role of w_sp, the "trajectory fingerprint" claim is metaphorical, not mechanistic.

For the per-sample fc Hessian trace: the algebraic identity Tr(H_i^fc) ∝ ‖x_i‖² p_i(1-p_i) is exact. So here's the hard question: if I regress log-trace on log-loss *alone*, how much AUROC do I already get? If ≥0.80, the curvature story is parasitic on first-order residuals. Prof. Vera's ΔAUROC ≥ 0.10 is the bare minimum. I'd further require: within narrow bins of predicted confidence (e.g., 0.7–0.75), does minority still have systematically higher trace? If not, the signal is just miscalibration.

For shortcut specificity: background-swap augmentation is the cleanest test. Randomize backgrounds at inference time, recompute trace. If the gap COLLAPSES under background randomization, that's strong shortcut-specific evidence. If it persists, you're measuring generic example hardness.

Three things I need to see: (1) observable deep-network w_sp analogue, (2) residual group signal under tight confidence matching, (3) trajectory shape pre-registered with hard thresholds (R(0)≈1, inflection, bounded drops). Without these, reviewers will say it's a beautifully told story about loss dynamics.

**Key Points:**
- Phase I/II framing needs observable w_sp analogue in ResNet-50 feature space — otherwise metaphor, not mechanism
- fc Hessian trace must show residual signal under strict confidence matching (within-bin test) beyond loss-only AUROC
- Background-swap augmentation is the decisive shortcut-specificity test; trajectory shape needs pre-registered thresholds

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Here's what worries me — and here's where I think this actually works. Let me separate the mechanism concern from the feasibility concern.

On the w_sp analogue question: I think Prof. Rex is setting an impossibly high bar. We don't need to prove the ResNet-50 equivalent of w_sp to USE the Hessian trace as a practical signal. The h-e2-k result (AUROC=0.913 at K=50) already confirmed empirically that the signal exists without requiring us to map it to XOR theory. The theoretical story (LaBonte 2026) is motivation and framing — it doesn't need to be a literal proof at the ResNet level to justify the experiment. We can state this clearly: "motivated by LaBonte 2026, we empirically test whether..." The background-swap test addresses shortcut specificity empirically without needing the theoretical mapping.

On the algebraic concern: Tr(H_i^fc) ∝ ‖x_i‖² p_i(1-p_i) is exact for a two-class linear head. But this doesn't mean trace adds nothing — it means that IF minority samples have systematically higher ‖x_i‖² (feature norm) OR lower p_i (confidence) than majority, BOTH interpretations are scientifically interesting. The LaBonte 2024 [P2] spectral imbalance finding tells us minority groups have HIGHER feature diversity (larger λ₁ of Σ_g), which translates to higher ‖x_i‖² variance. So the trace signal may be MEDIATED by feature norm — still a genuine shortcut-learning signal, just operating through a specific algebraic channel.

The feasibility constraint on background-swap: this requires inference on augmented data. Background randomization on Waterbirds is possible using the dataset's provided metadata (place=0/1 labels exist) and standard augmentation — no new dataset needed. The infrastructure from h-e2-k is sufficient: load model, compute trace on augmented samples.

Okay, this could work IF the hypothesis is scoped correctly. The claim should be: "per-sample fc Hessian trace captures a compound signal (‖x_i‖² × confidence) that is empirically predictive of spurious group membership, emerges from ERM training (epoch-0 control), grows monotonically (Spearman ρ ≥ 0.8), and enables annotation-free DFR at WGA ≥ 85%."

**Key Points:**
- Background-swap augmentation uses existing Waterbirds metadata — no new data; feasibility confirmed
- Algebraic decomposition Tr ∝ ‖x_i‖² p_i(1-p_i) is an EXPLANATION of the signal channel, not a falsifier — both feature norm and confidence are spurious-feature-related
- Hypothesis should be scoped to empirical claims (trajectory, DFR WGA), not require proving deep ResNet-50 = XOR model

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this add beyond what DFR already established? Kirichenko et al. 2022 [P3] showed something profound — ERM on Waterbirds achieves only ~38.4% worst-group accuracy, yet the SAME representation achieves ~94% on FG-only (bird-only) inputs. DFR then retrains only the last-layer on a group-balanced validation set and reaches 92.9% WGA. The core features exist — the head misweights them.

So if curvature asymmetry is proposed as a signal, it must do more than restate "the head misweights features." The genuine opportunity is sharper: provide the FIRST DYNAMIC, TRAINING-TIME indicator that final-layer weighting is drifting toward shortcut reliance — BEFORE worst-group collapse is visible. DFR is post-hoc correction; your curvature trajectory becomes an early-warning system. That would be new.

On the mechanism debate: scientific contribution doesn't require isomorphism to XOR model — it requires falsifiable predictions. The proof experiment is three things:
1. **Emergence**: AUROC from trace starts near chance at epoch 0, rises monotonically (ρ ≥ 0.8)
2. **Independence**: Within tight confidence bins (0.7–0.75), minority still has higher trace; ΔAUROC ≥ 0.10 over loss-only
3. **Specificity**: Under background swap on Waterbirds, trace gap collapses

If these hold, curvature is not metaphor — it is a predictive statistic with shortcut specificity.

The DFR application closes the loop: if top-k% by trace at t* achieves WGA ≥ 85% WITHOUT group labels (recall Kirichenko 2022 DFR needs balanced validation with implicit group info), we've opened "unsupervised minority discovery via second-order signals" — a new research direction. The broader implication: trace-guided selection could generalize to ImageNet-scale texture/shape bias detection.

**Key Points:**
- Curvature trajectory as "early-warning system" for shortcut reliance is the genuine novel contribution over DFR's post-hoc correction
- Three-test protocol (emergence, independence, specificity) transforms narrative into falsifiable science
- WGA ≥ 85% without group labels would open "unsupervised minority discovery" as a new research direction

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this further by addressing the concerns directly. Let me synthesize what we've built and propose a concrete, defensible hypothesis statement.

Here's what the discussion has converged on: the mechanism concern (w_sp analogue) can be resolved by SCOPING the claim appropriately. We're NOT claiming per-sample Hessian trace is the ResNet-50 equivalent of w_sp — we're claiming it's an EMPIRICAL SIGNAL that tracks the shortcut learning process, grounded in three falsifiable criteria. Prof. Pax gave us the algebraic decomposition: Tr(H_i^fc) ∝ ‖x_i‖² p_i(1-p_i). LaBonte 2024 [P2] tells us minority groups have higher feature diversity (larger λ₁ of Σ_g). So the trace signal operates through a theoretically-motivated channel: minority samples have higher ‖x_i‖² AND lower p_i → higher trace. That's not a bug — it's the mechanism, expressed algebraically.

The independence test (ΔAUROC ≥ 0.10 within confidence bins) is the key gate that makes this more than "high loss = high trace." If minority samples within the SAME confidence bin show higher trace, then ‖x_i‖² (feature diversity) is doing the discriminative work — exactly what LaBonte 2024's spectral imbalance predicts.

For the DFR application: Kirichenko 2022 [P3] uses a balanced VALIDATION SET with implicit group info (group-balanced subsetting). Our annotation-free proxy replaces that with top-k% Hessian trace training samples — selected from the training set, no validation group labels needed. The pipeline from izmailovpavel/spurious_feature_learning is already mapped out. k% can be tuned on unbalanced validation accuracy.

The COMPLETE hypothesis is now clear:

**H-E3 (Existence):** Under ERM training on Waterbirds (ResNet-50, SGD, 20 epochs), per-sample last-fc Hessian trace (K=50 Hutchinson) achieves AUROC ≥ 0.85 for minority membership at epoch t* (argmax_t mean_minority_trace/mean_majority_trace), with:
- Epoch-0 AUROC < 0.70 (ERM emergence, not pretrained artifact)
- Spearman ρ ≥ 0.8 between trace ratio R(t) and epoch t (trajectory monotonicity)
- ΔAUROC ≥ 0.10 over loss-only model within confidence bins (independence)
- Trace gap collapses under background-swap augmentation (shortcut specificity)

**H-E3-DFR (Application):** Top-k% highest-trace training samples (k tuned on unbalanced val) → DFR on ERM-trained features → WGA ≥ 85% in ≥4/5 seeds

**Key Points:**
- Hypothesis is now fully scoped: empirical signal (not XOR analogy), three falsifiable gates (emergence, independence, specificity), DFR application
- The algebraic decomposition Tr ∝ ‖x_i‖² p_i(1-p_i) connects to LaBonte 2024 spectral imbalance via feature diversity — it's the mechanism, not a confound
- Pipeline is completely mapped: h-e2-k infrastructure (K=50, last-fc, vmap+grad) + izmailovpavel DFR

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

The hypothesis is now close to testable, but precision must tighten further. What would disprove H-E3? A single condition suffices: if within narrow confidence bins (width ≤ 0.02), minority and majority samples exhibit indistinguishable trace distributions (two-sided KS test, α=0.01), then independence from first-order residuals collapses. Pre-register this as a binary gate.

On emergence: "epoch-0 AUROC < 0.70" is necessary but not sufficient. Add permutation control: freeze randomly initialized classifier head and compute trace before any training updates. If AUROC > 0.60 even then, the signal is architectural bias, not ERM-induced. Additionally: compute trace under label shuffling for 1 epoch — if R(t) still rises monotonically (ρ ≥ 0.8), emergence claim is falsified.

On specificity: quantify collapse. Let Δ(t*) be the mean trace gap at peak epoch. After background randomization: require Δ_swap(t*) ≤ 0.25·Δ(t*) — i.e., ≥75% collapse. Plus foreground-only masking (as in Kirichenko 2022 [P3]) as second perturbation: if trace equalizes under FG-only inputs while accuracy stays high, that supports shortcut specificity.

On DFR: trace-guided selection must beat matched baselines — top-k% by loss AND top-k% by ‖x_i‖² alone — by ≥5% absolute WGA. Plus show Hutchinson estimator stability: CV of trace estimates ≤10% across probe resampling at K=50 [per PyHessian methodology, P4].

This meets my standards — IF the above conditions are pre-registered.

**Key Points:**
- Pre-register confidence-bin KS separation, permutation/label-shuffle controls, quantitative 75% collapse criterion for background swap
- Trace-guided DFR must beat loss-only AND norm-only baselines by ≥5% WGA absolute
- Hutchinson stability: CV ≤10% across probe resampling at K=50

---

### Exchange 13

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I want to add one more concern before I'm satisfied. Prof. Vera's regime of controls is excellent — but there's a scoping issue with the 20-epoch training window.

Recall h-m1 failure: 5-epoch training was entirely in Phase I (CV_ratio flat at ~3.1). The current proposal uses 20 epochs, which should capture the Phase I→II transition. BUT: the Waterbirds ERM with ResNet-50 typically converges in 50-100 epochs for reasonable WGA. At 20 epochs, are we in Phase II or still Phase I? The trajectory hypothesis requires observing BOTH phases — the rising segment (Phase I, spurious feature being learned) AND the deceleration or inflection (Phase I→II transition).

If 20 epochs only captures Phase I and the trace ratio is still rising at epoch 20, we cannot observe the inflection point t* and the trajectory shape prediction becomes underdetermined.

Proposed fix: train for 50 epochs (5 checkpoints: t∈{0,1,5,10,20,50}) instead of just 20. This adds one checkpoint but dramatically improves the chance of capturing the full Phase I→II trajectory. OR: use early stopping from unbalanced validation loss — stop when validation loss plateaus (typically epoch 10-30 for Waterbirds) and take that as t_max.

What would convince me is: (1) extend training to ≥50 epochs with checkpoint at t=50; (2) show the trace ratio R(t) either reaches a peak OR continues growing (if still in Phase I, the DFR claim still holds, but the trajectory claim is weakened). This is the one structural gap I see — and it doesn't require new infrastructure, just saving one more checkpoint.

Also: the h-e2-k result was computed at a specific checkpoint (unclear from memory which epoch). If that was epoch 1 or epoch 5 (pretrained initialization), the K=50 AUROC=0.913 might be a pretrained artifact — exactly like h-e2. The epoch-0 control is decisive.

**Key Points:**
- 20-epoch training may only capture Phase I — extend to 50 epochs with t=50 checkpoint to detect Phase I→II inflection
- The h-e2-k K=50 AUROC=0.913 checkpoint epoch must be verified: if epoch 1 → risk of pretrained artifact
- Early stopping at validation loss plateau as alternative to fixed 50-epoch training

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic. The LaBonte 2026 [P1] synthetic result gives us a mechanistic template, not a guarantee of transfer. In their two-layer ReLU model, w_sp grows geometrically in Phase Ib and then slows sigmoidal in Phase II. In ResNet-50, we do not have an explicit w_sp axis. The only defensible claim is phenomenological: if shortcut reliance creates margin polarization across groups, and margin affects curvature, then trace might reflect that polarization. We cannot claim structural equivalence.

Here's the deeper feasibility question: does shortcut dominance necessarily induce higher curvature on minority samples? In the XOR paper, minority margins become highly negative under extreme λ. But curvature in logistic models peaks at *uncertain* points (p≈0.5), not confidently wrong ones. So for the mechanism to work, minority samples must cluster near the decision boundary during the spurious-dominated phase — NOT be confidently misclassified. If ERM drives minority margins deeply negative early (analogous to extreme λ), then p(1-p)→0 and curvature will NOT separate groups. This is a fundamental dynamical dependency, not a tuning issue.

On the 50-epoch question: I agree with Prof. Rex. Without checkpoints extending to ≥50 epochs, you may miss the phase where curvature asymmetry is detectable. If margins polarize early and p(1-p) collapses for both groups, the signal window is transient. Checkpoints at t∈{0,1,5,10,20,50} are needed.

On DFR: trace-guided selection works in principle but only if minority samples ARE near the decision boundary during training. If they're confidently wrong (like h-e2 showed gradient direction inverted), the signal collapses.

**Key Points:**
- Fundamental mechanism contingency: minority samples must remain near decision boundary (p≈0.5) for Tr(H_i^fc) to be elevated; if confidently misclassified, trace collapses
- 50-epoch checkpoint mandatory to detect transient curvature-separation window
- Phenomenological claim (shortcut reliance → margin polarization → trace asymmetry) is defensible; structural ResNet = XOR equivalence is not

---

### Exchange 15

🔭 **Dr. Nova** (Creative Novelty Explorer):

This is exactly the kind of concern that turns a good hypothesis into a great one! Prof. Pax has identified the fundamental mechanism contingency — minority samples must be NEAR THE DECISION BOUNDARY, not confidently misclassified. Let me reframe this as a FEATURE, not a bug.

Here's the crucial insight: the h-e1 snapshot data (AUROC=0.9402, mean AUROC across seeds) was computed at t* = argmax CV_ratio, which was epoch 4 for seeds 0-1 and epoch 1 for seeds 2-4. At those early epochs, Waterbirds ERM has NOT yet driven minority samples to confident misclassification — minority loss is still high and fluctuating. This means the scenario Prof. Pax describes (p(1-p)→0 for confidently wrong samples) applies to CONVERGENCE, not early epochs! At t∈{1,5,10}, minority samples are likely still in the intermediate confidence range where trace IS elevated.

This actually gives us a STRONGER prediction: the trace AUROC signal should be HIGHEST at the epoch where minority samples are most uncertain (medium confidence), and DECLINE as training progresses and minority samples reach saturation (confidently wrong). So R(t) = mean_minority_trace(t)/mean_majority_trace(t) should have a PEAK at t*, then DECLINE. This is more falsifiable AND more informative than monotonic growth!

For the DFR application: this tells us EXACTLY when to select t* — it's the epoch where mean_minority_trace / mean_majority_trace is maximized AND minority confidence is in the range [0.3, 0.7]. This is a data-driven, annotation-free t* selection criterion! No validation group labels needed.

Extended checkpoints t∈{0,1,5,10,20,50} let us observe the FULL trajectory: rise (Phase I shortcut learning, majority gains confidence while minority stays uncertain), peak at t*, and potential decline (Phase II, minority also gets classified with low confidence after shortcut saturates).

**Key Points:**
- The PEAK in R(t) is not a bug — it's a PREDICTION: trace AUROC peaks at the epoch where minority samples are most uncertain (Phase I/II boundary), then declines as ERM drives minority confidently wrong
- This makes t* selection ANNOTATION-FREE: argmax_t R(t) identifies optimal DFR checkpoint without group labels
- Extended checkpoint set t∈{0,1,5,10,20,50} maps the full rise-peak-decline trajectory

---


## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis introduces a genuinely novel signal class — per-sample Hessian trace trajectory — as an annotation-free proxy for spurious group membership. The trajectory-peak mechanism (rise-peak-decline of R(t) tracking Phase I/II transition) has never been proposed or tested empirically on Waterbirds. The connection to LaBonte 2024's static spectral imbalance via dynamic per-sample curvature is the most creative scientific contribution: we're watching the covariance imbalance EMERGE during training at per-sample resolution.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis now has pre-registered, quantitative falsification criteria for every sub-claim: epoch-0 AUROC < 0.70 (emergence), ΔAUROC ≥ 0.10 within confidence bins (independence), ≥75% trace gap collapse under background swap (specificity), Hutchinson CV ≤10% (stability), WGA ≥5% over loss/norm baselines (DFR utility). The permutation control and label-shuffle control address confounds rigorously. This structure meets scientific rigor standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Repositioning from post-hoc DFR correction to a dynamic early-warning system for shortcut reliance is the most significant framing. If trace-guided annotation-free DFR achieves WGA ≥ 85%, it opens unsupervised minority discovery as a new research direction. The dual contribution — mechanistic trajectory evidence + practical DFR proxy — is publishable at top venues even if WGA falls slightly short of 85%, provided the trajectory evidence is clean.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE-STRONG
- **Assessment:** The mechanism contingency (minority samples must remain near decision boundary for trace to separate) is a genuine risk but empirically resolvable. The h-e1 snapshot data suggests minority samples ARE in the uncertain regime at early epochs. The extended checkpoint set t∈{0,1,5,10,20,50} captures the full trajectory. The Hutchinson K=50 infrastructure from h-e2-k is directly reusable. The primary feasibility risk is the transient signal window — if minority samples reach confident misclassification before the trace peak, the DFR proxy becomes unreliable.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerging hypothesis is: **H-E3** — Under ERM training with SGD on Waterbirds (ResNet-50, ImageNet pretrained, 95% spuriosity, SGD, 50 epochs with checkpoints at t∈{0,1,5,10,20,50}), the per-sample last-fc Hessian trace (K=50 Rademacher Hutchinson estimator via torch.func vmap+vjp) exhibits a transient asymmetry — the trace ratio R(t) = mean_minority_trace(t) / mean_majority_trace(t) rises from ≈1.0 at initialization, reaches a peak at t* (argmax_t R(t)), then declines as majority margins saturate. This trajectory provides: (1) mechanistic evidence that ERM spurious feature exploitation creates differential loss landscape curvature (minority samples remain near decision boundary while majority gains confidence early); and (2) a practical annotation-free DFR proxy — top-k% highest-trace samples at t* replace the balanced validation set in Kirichenko et al. 2022, achieving WGA ≥ 85% without group annotations.

The core statement is: trace AUROC at t* ≥ 0.85 (with epoch-0 AUROC < 0.70 ruling out pretrained artifact), Spearman ρ ≥ 0.8 between trace ratio and epoch t across the rising segment, ΔAUROC ≥ 0.10 within confidence bins vs. loss-only, trace gap ≥75% collapse under background-swap augmentation, and Hutchinson CV ≤10% at K=50. The DFR application: top-k% by trace at t* → L1 logistic regression on ERM features → WGA ≥ 85% in ≥4/5 seeds.

The hypothesis avoids all prohibited directions: no gradient direction signals (family exhausted), no temporal CV, no frozen pretrained features for DFR, K=50 throughout (K=10 confirmed insufficient). It directly addresses the research question and reuses validated h-e2-k infrastructure.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The epoch-0 control is decisive but carries the h-e2 ghost: if Hutchinson trace at epoch 0 is AUROC ≥ 0.85 (like h-e2's gradient direction was), the entire existence hypothesis collapses to another pretrained artifact. This must be the FIRST gate tested before any other analysis.
- The mechanism contingency (minority must be near boundary) is empirically contingent — if Waterbirds with 95% spuriosity drives minority to confident misclassification BEFORE t*, the trace signal collapses and DFR fails. Need to verify minority mean confidence at early epochs.
- **Mitigation Strategy:** Run a quick pilot (1 seed, 5 epochs) to verify epoch-0 AUROC and minority confidence trajectory before committing to full 5-seed 50-epoch training. If epoch-0 AUROC is already high, route to Phase 0 for new signal family.

