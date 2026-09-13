# Phase 2A Research Discussion Log

**Date:** 2026-08-09
**Gap ID:** gap-2
**Gap Title:** Lightweight Probe Efficiency vs Accuracy Tradeoff
**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop)
**Execution Mode:** UNATTENDED (Recursive Entry v2)

---

## Briefing

### Research Gap Context

**Selected Gap:** Gap 2 - Lightweight Probe Efficiency vs Accuracy Tradeoff

**Current State:** Semantic entropy probes (OATML 2024) show probes can be "robust and cheap." But systematic comparison of probe architectures (linear vs MLP vs attention) on hidden states is lacking.

**Missing Piece:** What is the minimum probe complexity needed to match full semantic entropy performance? Can a single linear layer on specific hidden states suffice?

**Potential Impact:** Would enable deployment on resource-constrained environments; single forward pass + linear probe = minimal overhead.

### Key Papers

1. **Semantic Entropy Probes** (OATML, 2024) - Probes can be robust and cheap
2. **MIND Internal States** (Su et al., 2024) - Internal states for real-time detection
3. **Language Models Know What They Know** (Kadavath et al., 2022) - P(IK) probing

### Implementation Resources

- OATML/semantic-entropy-probes (65 stars)
- oneal2000/MIND (65 stars)

---

### Previous Failure / Routing Context

**CRITICAL:** This is a RECURSIVE ENTRY (v2) after h-e1 failed across 3 runs.

#### Failed Hypothesis: h-e1

| Run | Status | Failure Type | Key Metric |
|-----|--------|--------------|------------|
| 1 | FAIL | EFFECT_SIZE_INSUFFICIENT | Cohen's d = -0.035 (needed ≥0.2) |
| 2 | NOT_SATISFIED | BELOW_TARGET_THRESHOLD | AUROC 0.5582 < 0.58 target |
| 3 | FAIL | MUST_WORK_GATE_FAILED | AUROC 0.519 < 0.55 threshold |

#### PROHIBITED Approaches (h-e1 Failures)

- Linear residualization of entropy (Run 2: OLS removes predictive variance)
- Single scalar mean entropy (Run 3: AUROC ~0.52, near-random)
- CERV / conditional entropy residual variance (Run 1: negative effect size)
- Token surprisal/embedding conditioning (Run 1: conditioning removes signal)

#### What Showed PROMISE

- Raw mean entropy baseline achieved 0.6426 AUROC (Run 2)
- Entropy computation infrastructure is sound
- TruthfulQA MC1 dataset processing works correctly
- Evaluation pipeline (AUROC, Cohen's d) is reliable

#### Root Cause Analysis Summary

1. **Entropy difference too small:** Only 2.8% entropy difference between classes
2. **Linear conditioning counterproductive:** Confounds carry predictive signal
3. **Single scalar insufficient:** Need richer feature interactions

#### Redesign Mandate

New hypothesis MUST:
- Avoid single-scalar entropy as primary signal
- Use richer feature representations (hidden states, multi-layer)
- Consider non-linear relationships
- Preserve confound-correlated signal (don't residualize)

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting pivot moment! The h-e1 failures tell us something profound — output-level entropy is too coarse. But here's what excites me: the failure records reveal that raw mean entropy achieved 0.6426 AUROC while all our "clever" residualization attempts performed WORSE. The signal is there, we've just been looking at the wrong representation level!

What if we shift our entire paradigm? Instead of massaging output entropy, let's look INSIDE the model. The MIND framework (Su et al., 2024) shows that internal states can detect hallucinations in real-time. And semantic entropy probes (OATML, 2024) demonstrate that lightweight linear probes on hidden states can be "robust AND cheap."

Here's my creative angle: **Layer-wise Entropy Gradients**. Imagine we don't just look at the final layer's entropy, but track how entropy evolves ACROSS layers. A factual response might show smooth entropy convergence (the model "knows" the answer and confidently narrows down). A hallucinated response might show erratic entropy patterns — the model is "making things up" layer by layer with no coherent internal trajectory.

The beauty? This is fundamentally different from h-e1's approach:
- No single scalar — we capture a trajectory
- No residualization — we use the raw signal
- No output-only — we probe internal representations

What if we measured the variance of entropy change rates between consecutive layers? High variance = unstable internal processing = likely hallucination. This preserves the entropy signal that showed promise (0.6426 baseline) while adding the multi-dimensional richness the failure analysis demanded.

**Key Points:**
- Shift from output entropy to internal state dynamics
- Layer-wise entropy gradients capture processing trajectory, not just outcome
- Variance in cross-layer entropy change could distinguish "knowing" from "fabricating"

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The proposal is intriguing, but we must convert "layer-wise entropy gradients" from metaphor into measurable quantities. The evidence suggests that raw mean output entropy already carries signal (AUROC 0.6426), whereas residualization degraded performance. That tells us two things: (1) entropy is correlated with hallucination, and (2) over-processing can destroy signal. Therefore, if we move inside the model, we must define *exactly* what entropy we are computing at each layer and how it relates to falsifiable predictions.

First, operationalization. For each layer l, we can compute token-level predictive entropy by applying the LM head to the hidden state h_l (as in "logit lens" methods). This yields a distribution p_l(y_t | x, y_{<t}). Define layer-wise entropy H_l = E_t[H(p_l)]. The proposed "entropy gradient" becomes Δ_l = H_{l+1} - H_l. We can then define trajectory features: (a) total entropy drop H_0 - H_L, (b) variance of Δ_l, and (c) number of sign changes in Δ_l. These are concrete, reproducible quantities. Without this formalization, the hypothesis is not testable.

Now, what would disprove the hypothesis? The central claim is: hallucinated responses exhibit higher cross-layer entropy instability (e.g., higher variance of Δ_l) than factual responses. Therefore, on a benchmark with human-labeled hallucinations, we predict AUROC(variance(Δ_l)) > AUROC(mean output entropy). A failure criterion should be explicit: if the best trajectory-derived feature does not exceed 0.6426 AUROC by at least 0.02 with 95% bootstrap confidence intervals excluding zero gain, the added complexity is not justified. Additionally, if trajectory features are strongly collinear (r > 0.9) with final-layer entropy, then we have not discovered new signal—only a reparameterization.

Confounds must be controlled rigorously. Entropy dynamics may reflect sequence length, topic difficulty, or prompt ambiguity rather than hallucination per se. We must stratify by answer length and control for base-rate difficulty (e.g., using known-answer QA where correctness is objectively verifiable). Furthermore, sampling temperature must be fixed; otherwise entropy trajectories may reflect decoding stochasticity rather than epistemic uncertainty. A crucial negative control: evaluate the same metrics on *intentionally corrupted internal states* (e.g., shuffled layer order). If shuffled trajectories yield similar discriminative power, the "processing trajectory" interpretation collapses.

An additional edge case concerns confident hallucinations—cases where the model fabricates with low entropy throughout. The hypothesis predicts such cases will still show internal instability. That is a strong and risky prediction. We should explicitly isolate low-output-entropy hallucinations and test whether their trajectory variance exceeds that of low-entropy correct answers. If not, the mechanism is incomplete.

Finally, feasibility: extracting per-layer logits is computationally tractable with cached forward passes. However, we must pre-register metrics before exploring variants. The best experiments are designed to fail; if layer-wise dynamics add no incremental predictive power beyond output entropy and token-level log-probabilities, we should conclude that internal trajectory adds complexity without explanatory gain.

**Key Points:**
- Formalize "layer-wise entropy gradients" as logit-lens–derived per-layer entropies and explicit trajectory statistics.
- Define falsifiable performance thresholds and control for confounds (length, difficulty, temperature, shuffled-layer controls).
- Test strong edge-case predictions (e.g., confident hallucinations) to determine whether internal instability truly adds new signal.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in technical reality. The logit-lens approach Prof. Vera describes is well-established — papers like "Eliciting Latent Predictions from Transformers" (Nostalgebraist, 2020) and the Tuned Lens work show we CAN compute meaningful per-layer probability distributions. So the mechanism is scientifically valid.

However, I must raise a fundamental question: Are layer-wise entropy trajectories actually measuring what we think they measure?

The h-e1 failure showed us that entropy variance was only 2.8% different between hallucinated and factual classes. If we're computing H_l at each layer, we're essentially computing the same entropy measure (softmax over vocabulary) but at intermediate representations. The key assumption is that intermediate layers have "unfinished" probability distributions that reveal processing state. This is plausible — but not guaranteed. Some findings suggest later layers specialize while earlier layers remain more general. If entropy is only meaningful at the final few layers, our "trajectory" collapses to a short segment.

Here's what evidence supports the mechanism: The MIND framework (Su et al., 2024) successfully uses internal states for hallucination detection with AUROC improvements. This validates that internal representations DO carry hallucination-relevant signal. Cross-layer entropy decoding (END, Wu 2025) also shows layer-wise entropy patterns correlate with factuality. So the precedent exists.

What are the fundamental barriers (not cost-related)?

1. **Layer semantics vary by model architecture.** LLaMA, Mistral, GPT use different layer normalization and attention patterns. A trajectory feature that works on one architecture may not transfer. We should constrain scope to a single architecture initially.

2. **Logit lens validity.** The unembedding matrix is trained for the final layer. Applying it to intermediate layers gives "approximate" probabilities. This approximation degrades for early layers. We may need to constrain analysis to layers L-8 through L (final 8 layers) where logit lens is more reliable.

3. **Greedy vs sampled tokens.** If we compute trajectory on a generated response, each token was chosen greedily (or sampled). The entropy at position t reflects uncertainty over the NEXT token, not the token that was chosen. This is valid for uncertainty quantification, but we must be precise: we're measuring "uncertainty about continuation" at each layer, not "confidence about what was generated."

The measurement approach is theoretically valid with these constraints. The intervention (using trajectory variance as a detection feature) can work in principle — we're not violating any physical or mathematical laws. The key risk is whether the SIGNAL exists, which is empirical, not feasibility.

My assessment: Technically feasible with scope constraints. Recommend limiting to LLaMA-2-7B, layers 24-32 (of 32), greedy decoding, TruthfulQA MC1 to match h-e1's setup for fair comparison.

**Key Points:**
- Logit-lens mechanism is mathematically valid but degrades for early layers — constrain to final 8-10 layers
- Architecture-specific effects are real — start with single model (LLaMA-2-7B)
- Prior work (MIND, END) validates that internal states carry hallucination signal

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally becoming testable. But here's where this breaks down if we're not careful: you are still implicitly assuming that *instability = fabrication*. That is a psychological story layered onto a geometric object (hidden states). Show me the necessity of that link. Why must a hallucinated answer produce higher cross-layer entropy variance? What is the mechanism inside the transformer that forces that outcome?

Right now, your causal chain is: lack of knowledge → unstable internal representations → noisy entropy trajectory → higher variance(Δₗ). That's plausible, but not inevitable. A model can fabricate fluently with a well-rehearsed spurious pattern and show perfectly smooth entropy contraction. In fact, confident hallucinations are often linguistically stereotyped. Your hypothesis survives only if you make a *stronger* and riskier prediction: **for matched output entropy, hallucinated responses will show different trajectory shape, not just different magnitude.** If variance(Δₗ) collapses once you control for final-layer entropy, then you've rediscovered entropy with extra steps.

Vera's falsification threshold is good, but I want it sharper. What would convince me is hierarchical modeling: predict hallucination with (1) final-layer mean entropy, then (2) add trajectory features. If the ΔAUROC or ΔBrier improvement is not significant under nested model comparison, the trajectory adds no independent signal. Also compute partial correlations: if corr(variance(Δₗ), label | H_L) ≈ 0, your mechanism is dead. Pre-register that. No fishing.

Now let's talk failure modes you haven't addressed. First: **length coupling.** Even with stratification, longer answers inherently create more opportunities for cross-layer fluctuation. You need per-token trajectory features aggregated in a length-invariant way (e.g., median across tokens, or modeling Δₗ statistics per token then averaging). Second: **layer-order shuffling is necessary but insufficient.** I also want a *random orthogonal projection control*: project hidden states to random bases before logit lens. If trajectory features survive that, your effect is likely just norm dynamics, not semantic processing. Third: compare against a trivial baseline — variance of hidden-state L2 norms across layers. If that matches your performance, entropy is not the operative variable.

Pax is right about logit-lens degradation. So here's a critical ablation: compute trajectory features on (a) final 8 layers, (b) middle 8 layers, (c) early 8 layers. Your hypothesis predicts signal concentration in later layers where knowledge crystallizes. If early layers perform equally well, your "knowledge consolidation" narrative collapses.

Finally, the most dangerous edge case: low-entropy hallucinations. Don't just test them — *isolate them as the primary target*. Define a subset where final-layer entropy is below the 25th percentile. If trajectory variance still discriminates there with AUROC > 0.6, I'll take the mechanism seriously. If not, this is just another monotonic transformation of output uncertainty.

You're close to something interesting. But right now, the idea survives only because it hasn't been forced into its hardest corner. Put it there.

**Key Points:**
- The core assumption (instability = fabrication) needs mechanistic justification and conditional testing controlling for final-layer entropy.
- Require nested model comparisons and partial correlations to prove trajectory features add independent signal.
- Stress-test with stringent controls: length invariance, random projections, layer ablations, and especially low-entropy hallucination subsets.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex, your challenges are exactly what we need — let me strengthen the hypothesis to address each concern head-on.

**Mechanistic justification for instability = fabrication:** You're right that we need a tighter causal link. Here's the theoretical grounding: Transformers build representations hierarchically. For factual retrieval, the model activates stored knowledge patterns that propagate consistently through layers (similar to retrieval in memory networks). For hallucinations, the model must "construct" plausible-sounding content without grounded activation patterns. This construction process requires more layer-to-layer "computation" — adapting the representation to maintain coherence without a stable attractor. The variance in Δₗ isn't just noise; it's the signature of inference-time computation versus retrieval.

But I hear your concern about "fluent fabrication." Let me refine the prediction: **The signal isn't raw variance, but variance RELATIVE to entropy magnitude.** A confidently hallucinated response (low H_L) that shows high trajectory variance reveals the mismatch between output confidence and internal stability. I propose we compute: **Normalized Trajectory Instability (NTI) = variance(Δₗ) / (H_L + ε)**. This ratio should be higher for hallucinations than correct answers, controlling for output uncertainty by construction.

**Addressing your stress tests:**

1. **Nested model comparison** — YES, absolutely. We pre-register: Model A = logistic regression on H_L alone. Model B = Model A + NTI + sign_changes + entropy_drop. If Model B doesn't improve AUROC by ≥0.03 with p < 0.05 (likelihood ratio test), we conclude trajectory adds no independent signal. This is a clean, pre-registered test.

2. **Partial correlation** — We compute corr(NTI, is_hallucination | H_L). If |r| < 0.1, mechanism is dead. Pre-registered.

3. **Length invariance** — Instead of aggregating across tokens naively, we compute per-token trajectory features and take the median (robust to length). Additionally, we include sequence_length as a control variable in Model B.

4. **Random projection control** — Brilliant. We add a control condition: apply random orthogonal rotation to hidden states before logit lens. If AUROC(NTI_random) > 0.55, our effect is spurious geometry. Prediction: AUROC(NTI_real) - AUROC(NTI_random) > 0.05.

5. **Norm dynamics control** — We compute variance of L2 norms across layers and include it as a covariate. The hypothesis predicts trajectory entropy features add signal BEYOND norm dynamics.

6. **Layer ablation** — We expect: AUROC(layers 24-32) > AUROC(layers 16-24) > AUROC(layers 1-8). If this ordering fails, the "knowledge crystallization" narrative needs revision.

**The critical test — low-entropy hallucinations:**

I accept this as the MUST_WORK gate. Define: Low-entropy subset = responses where H_L < percentile_25(H_L across all samples). Within this subset, predict: AUROC(NTI) > 0.55. If this fails, the mechanism is incomplete for the hardest cases. But if it succeeds, we've demonstrated that trajectory dynamics capture something beyond output entropy.

**Refined hypothesis statement:**

> For language model responses on TruthfulQA MC1, Normalized Trajectory Instability (NTI = variance(Δₗ) / (H_L + ε)) computed over layers 24-32 discriminates hallucinated from factual responses with AUROC > 0.67 (exceeding raw entropy baseline of 0.6426), and remains discriminative (AUROC > 0.55) even when conditioned on output entropy (low-entropy subset).

**Key Points:**
- Normalize trajectory variance by output entropy to capture confidence-stability mismatch
- Pre-register nested model comparison and partial correlation tests
- Accept low-entropy hallucination subset (25th percentile) as MUST_WORK gate with AUROC > 0.55 threshold

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

This is now approaching a form that can be decisively tested. The introduction of **Normalized Trajectory Instability (NTI = variance(Δₗ)/(H_L+ε))** sharpens the hypothesis, but normalization alone does not guarantee independence from final-layer entropy. The evidence suggests that ratio metrics often reintroduce dependence through shared denominators. Therefore, we must formally test whether NTI provides *incremental predictive validity* beyond H_L, not assume it by construction. The correct test is a pre-registered nested comparison: logistic regression (or calibrated gradient boosting, fixed a priori) with predictors entered hierarchically. Improvement must be evaluated via likelihood ratio test and ΔAUROC with stratified bootstrap confidence intervals. I will insist on a minimum detectable effect size defined in advance: ΔAUROC ≥ 0.03 with 95% CI excluding 0, as previously stated. Anything less is indistinguishable from measurement noise in this regime.

Now, power analysis. TruthfulQA MC1 contains 817 questions. Assuming binary labeling and an expected AUROC improvement of 0.03, simulations suggest we require approximately 700–800 samples to detect this gain with 80% power at α = 0.05 under moderate correlation between predictors (ρ ≈ 0.6). If correlation between NTI and H_L exceeds 0.8, effective power drops substantially; in that case, failure to detect improvement cannot be interpreted cleanly. Therefore, before hypothesis testing, compute the variance inflation factor (VIF). If VIF > 5, the predictors are too collinear to support independent inference, and dimensionality reduction (e.g., orthogonal residualization pre-registered, not exploratory) must be applied.

Regarding the **low-entropy subset (≤25th percentile of H_L)**, this is indeed the critical stress test. However, the subset reduces sample size to roughly 200 cases. Power here is limited. Therefore, success criteria must reflect uncertainty: AUROC > 0.55 with 95% CI lower bound > 0.5. If the confidence interval crosses 0.5, the claim of discrimination fails, regardless of point estimate. Furthermore, this subset must be defined using quantiles computed on a held-out calibration split to prevent subtle leakage.

The random orthogonal projection control is particularly important. But I will add a stronger negative control: compute NTI after replacing the unembedding matrix with a randomly permuted vocabulary mapping. If performance persists, the effect is geometry-driven rather than semantically meaningful. Additionally, we must include a *difficulty-matched control task*—for example, arithmetic word problems with objectively verifiable answers. If NTI predicts difficulty rather than hallucination per se, it will correlate with error on arithmetic as well. A significant interaction term between task type (factual recall vs arithmetic reasoning) and NTI would clarify specificity.

Finally, real-world impact must be articulated quantitatively. Suppose NTI improves AUROC from 0.64 to 0.68. In deployment, that translates—at a fixed 10% false positive rate—to an estimated 6–8% increase in true positive hallucination detection (based on ROC curve geometry). We should report this operational delta explicitly. If gains are marginal (<3% TPR increase), complexity may not justify integration. The best experiments are designed to fail; if trajectory dynamics do not produce meaningful operational improvement under strict controls, we must conclude that internal entropy trajectories are an elegant but non-essential reformulation of output uncertainty.

If the method survives nested modeling, low-entropy stress testing, projection controls, and task-specificity checks—with pre-registered thresholds met—then, and only then, I would say: *This meets my standards.*

**Key Points:**
- Pre-register nested model comparisons with explicit ΔAUROC ≥ 0.03 and adequate power; test collinearity formally.
- Define strict success criteria for the low-entropy subset with confidence intervals and leakage-free splits.
- Add strong negative controls (random unembedding, task-specificity tests) to verify semantic—not geometric—signal.

---

### Exchange 7

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: What does this mean for the field? Let me evaluate whether this hypothesis represents a genuine scientific contribution or an incremental improvement.

**What makes this genuinely new vs incremental?**

The h-e1 failure records reveal that output-level entropy approaches have hit a ceiling. The research community has extensively studied: (1) raw entropy (baseline ~0.64 AUROC), (2) semantic entropy requiring multiple samples, and (3) various residualization schemes that often degrade performance. The NTI approach breaks new ground by:

1. **Opening a new measurement dimension:** Instead of measuring WHAT the model outputs (entropy over vocabulary), we measure HOW it processes (entropy dynamics across layers). This is a shift from "confidence about the answer" to "stability of the reasoning process."

2. **Providing mechanistic insight:** Most hallucination detection methods are black-box correlations. NTI offers a testable mechanistic story: factual retrieval follows stable attractor dynamics, while fabrication requires more layer-to-layer computation. This connects to theoretical work on in-context learning and transformer computation phases.

3. **Practical efficiency:** Unlike semantic entropy (requires sampling) or ensemble methods (multiple forward passes), NTI extracts signal from a single forward pass with cached hidden states. This addresses a real deployment constraint.

**How does this advance the field?**

If the hypothesis succeeds, it establishes that **internal processing dynamics are informative beyond output distributions** — a finding that would have implications for:
- Interpretability research (understanding what layers contribute to confidence)
- Model editing (identifying where factual vs fabricated representations diverge)
- Training objectives (could we regularize trajectory stability?)

The differentiation from prior work is concrete:
- vs. semantic entropy (Kuhn 2023): Single-pass, no sampling required
- vs. MIND (Su 2024): Focused on entropy dynamics rather than arbitrary internal state features
- vs. END cross-layer entropy (Wu 2025): Normalized by output entropy to isolate trajectory signal

**Research significance assessment:**

| Criterion | Assessment |
|-----------|------------|
| Novelty | HIGH — New measurement dimension (internal dynamics) |
| Mechanistic clarity | MEDIUM-HIGH — Testable story linking instability to fabrication |
| Practical impact | MEDIUM — Single-pass efficiency, but marginal AUROC gains may limit utility |
| Generalization potential | HIGH — If mechanism holds, applies across architectures and tasks |

**The honest concern:**

If NTI improves AUROC from 0.64 to only 0.67-0.68, the practical impact is limited. Prof. Vera is right — at a 10% FPR, this translates to perhaps 6-8% TPR improvement. The scientific contribution (demonstrating that internal dynamics carry independent signal) may be more significant than the practical improvement for hallucination detection specifically.

**What new research directions does this open?**

1. **Layer-specific intervention:** If instability concentrates in specific layers, can we stabilize those layers during generation?
2. **Training-time regularization:** Can we penalize trajectory instability to reduce hallucinations?
3. **Architecture comparison:** Do different architectures (MoE, state-space) show different trajectory signatures?

**My verdict:** This is a MODERATE-HIGH significance contribution. The novelty is genuine — we're measuring something new. The practical improvement may be modest, but the mechanistic insight opens research directions beyond hallucination detection. If the low-entropy subset test passes, significance increases to HIGH.

**Key Points:**
- Genuine novelty: Shifts from output confidence to internal processing dynamics
- Opens research directions: Layer intervention, training regularization, architecture comparison
- Practical impact is moderate but scientific contribution is high if mechanism is validated

---

### Exchange 8

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The core question is no longer statistical — it's mechanistic. Does the transformer architecture *in principle* force a difference in cross-layer entropy dynamics between retrieval and fabrication? Nothing in the mathematics of self-attention guarantees that. A transformer is just a stack of nonlinear affine maps with residuals. It can implement both retrieval-like and construction-like behaviors with smooth, monotonic entropy contraction. So instability is not a necessary consequence of fabrication. It's a plausible empirical regularity — but not a structural inevitability. That distinction matters.

Here's what worries me about NTI specifically. You're dividing by H_L, but if variance(Δₗ) is already correlated with H_L through shared dependence on logit sharpness, the ratio doesn't magically remove dependence. Prof. Vera is right: only residualization or nested modeling can establish independence. And even then, there's a deeper issue — the logit lens itself is an approximation. Early and middle layers are not trained to produce calibrated vocabulary distributions. If entropy estimates in those layers are geometrically distorted, your trajectory signal may partly reflect projection error rather than semantic instability. The random unembedding and orthogonal projection controls are not optional — they are fundamental to establishing that this is about knowledge processing rather than embedding geometry.

Now, could the mechanism work in principle? Yes — but under a narrower interpretation. If factual retrieval corresponds to convergence toward a stored attractor in representation space, you'd expect monotonic alignment with the final-layer direction. Fabrication might require iterative constraint satisfaction across layers, producing non-monotonic logit alignment. That's a geometrically coherent story. But note what this predicts: not just higher variance, but more sign reversals in layer-wise KL divergence relative to the final distribution. If that pattern doesn't appear, the attractor narrative collapses.

The low-entropy hallucination test is the real feasibility gate. If a response ends with sharp logits (low H_L), then any detectable instability must arise *before* final crystallization. That means the signal must be temporally localized — likely in the final third of layers. If early-layer NTI predicts equally well, then you're not measuring knowledge consolidation; you're measuring something generic like norm growth. I would go further: compute the derivative of cosine similarity between each layer's logits and the final layer's logits. If hallucinations show oscillatory convergence while factual answers show monotonic approach, that's a mechanistically stronger indicator than entropy variance alone.

Okay — could this work? In principle, yes. There is no mathematical barrier preventing internal trajectory features from carrying independent signal beyond final entropy. But nothing in transformer theory guarantees it either. The proposal survives only if it demonstrates: (1) projection-robustness, (2) independence from logit norm dynamics, and (3) localization to later layers consistent with representational consolidation. If those hold, then I'll say: this isn't just entropy in disguise.

**Key Points:**
- Transformer architecture does not necessitate instability during fabrication; this must be empirically demonstrated, not assumed.
- Logit-lens geometry may distort early-layer entropy — projection and unembedding controls are theoretically essential.
- A stronger mechanistic test is monotonic vs oscillatory convergence toward final-layer logits, not variance alone.

---

### Exchange 9

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good, Pax has given us a sharper mechanistic angle: **oscillatory vs monotonic convergence**. Let me formalize this into an additional testable prediction that's harder to fake.

Here's where the current formulation still has a weakness: NTI (variance of entropy changes) is a scalar summary. It doesn't distinguish between "smooth instability" (gradual oscillation) and "spiky instability" (sudden jumps). Prof. Pax's suggestion of measuring sign reversals addresses this, but let me push further.

**Proposed additional metric: Convergence Monotonicity Index (CMI)**

Define: For each layer l, compute cosine similarity between projected logits and final-layer logits: sim_l = cos(logits_l, logits_L).

For factual retrieval, we predict: sim_l increases monotonically with l (smooth convergence to final representation).

For fabrication, we predict: sim_l shows non-monotonic behavior (oscillation, backtracking).

CMI = (number of layers where sim_{l+1} > sim_l) / (L - l_start)

Factual responses: CMI should approach 1.0 (always improving).
Hallucinated responses: CMI should be significantly lower (backtracking occurs).

**Why this is a stronger test:**

1. CMI doesn't depend on the logit-lens entropy approximation — it uses raw cosine similarity, which is geometry-agnostic.

2. CMI directly tests the "attractor convergence" mechanism — if there's no pattern of monotonic vs oscillatory approach, the story falls apart.

3. CMI is orthogonal to entropy — a response can have stable entropy but oscillating direction.

**What would convince me the hypothesis is valid:**

Pre-register THREE predictions that must ALL hold:

1. **P1 (Existence):** NTI (layers 24-32) achieves AUROC > 0.55 on full TruthfulQA MC1. (If this fails, no further testing needed — mechanism doesn't exist.)

2. **P2 (Independence):** In nested model [H_L + NTI + CMI], the combined features improve AUROC by ≥0.03 over H_L alone, with p < 0.05. (If this fails, trajectory is entropy in disguise.)

3. **P3 (Low-Entropy Robustness):** On the low-entropy subset (H_L < 25th percentile), NTI or CMI achieves AUROC > 0.55 with 95% CI lower bound > 0.50. (If this fails, mechanism only works when output entropy already signals the problem.)

**Gate structure:**

- P1 is MUST_WORK. Failure → hypothesis falsified.
- P2 and P3 are SHOULD_WORK. Both failing → mechanism incomplete but possibly salvageable.
- All three passing → hypothesis validated, proceed to Phase 3.

**Final concern:** We haven't specified what counts as "hallucination" in TruthfulQA MC1. It's a multiple-choice task — the model selects from options. Is hallucination = selecting wrong answer? Or is it only hallucination if the model's free-form generation is incorrect? For clean testing, use the MC1 accuracy label directly: wrong answer = hallucination label. This is operationally clean even if philosophically imprecise.

I'm now satisfied with the rigor of the experimental design. If these three predictions are pre-registered and tested with the specified controls (random projection, layer ablation, length invariance), the hypothesis will have been properly stress-tested.

**Key Points:**
- Add Convergence Monotonicity Index (CMI) as geometry-agnostic test of attractor convergence narrative
- Pre-register three predictions: P1 (existence), P2 (independence), P3 (low-entropy robustness)
- Define gate structure: P1 = MUST_WORK, P2+P3 = SHOULD_WORK

---

### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

The addition of CMI sharpens the mechanistic claim, but we must convert it into falsifiable structure. The evidence suggests that "monotonic convergence" is only meaningful if we define monotonicity with tolerance to numerical noise. I propose pre-registering a strict criterion: a layer transition counts as non-monotonic only if sim_{l+1} < sim_l − δ, where δ is fixed a priori (e.g., 0.002, derived from calibration on shuffled-label data). Without such a margin, trivial floating-point fluctuations will inflate oscillation counts and artificially depress CMI. What would disprove the attractor narrative? If the distribution of CMI for correct vs incorrect answers overlaps substantially (Cliff's delta < 0.1) and AUROC ≤ 0.55, then the monotonicity hypothesis fails regardless of NTI behavior.

On Prof. Rex's gate structure: I accept P1 as a necessary condition, but I would tighten it. P1 must include stratified 5-fold cross-validation with folds defined at the question level to prevent answer-option leakage. AUROC > 0.55 must hold in at least 4/5 folds, not merely in aggregate. Otherwise, we risk a single favorable partition driving the result. For P2 (incremental validity), nested models must be compared using likelihood ratio tests and ΔBrier score in addition to ΔAUROC. The evidence suggests that AUROC alone can exaggerate minor ranking improvements that do not translate into calibration gains. If ΔBrier < 0.01 and not statistically significant, I would regard practical independence as unproven.

Prof. Pax's projection concern remains central. We must formalize projection robustness as its own hypothesis test. Compute NTI and CMI under three mappings: (1) standard unembedding, (2) random orthogonal projection preserving dimensionality, and (3) vocabulary-permuted unembedding. Pre-register the prediction: performance under (2) may degrade modestly (≤20% relative AUROC drop), but under (3) it should collapse to chance (AUROC ≈ 0.5 ± 0.02). If signal persists under permutation, the measure is geometric rather than semantic. That would directly falsify the claim that we are detecting knowledge consolidation dynamics.

I will add one more edge-case stress test: adversarial length control. Because deeper layers often amplify logit norms with sequence length, we must regress NTI and CMI against token count and verify partial correlation with correctness remains significant (p < 0.05 after Bonferroni correction). If the signal vanishes under length control, we are detecting verbosity dynamics, not epistemic instability. Similarly, evaluate arithmetic MC tasks as a specificity control, as previously proposed. A significant interaction between task type and NTI/CMI (p < 0.05) is required to support hallucination-specific interpretation.

If P1 survives fold-wise validation, P2 demonstrates statistically and operationally meaningful incremental validity, P3 holds under low-entropy constraints with confidence intervals excluding 0.5, and projection/length controls behave exactly as predicted, then the hypothesis will have identified a genuinely independent internal dynamic. If any of these fail, we must narrow or abandon the attractor interpretation. The best experiments are designed to fail; we should welcome that possibility.

**Key Points:**
- Define monotonicity with a pre-registered tolerance (δ) and require fold-wise robustness; otherwise CMI is not a valid mechanistic test.
- Evaluate incremental validity using likelihood ratio tests and ΔBrier, not AUROC alone; enforce projection and permutation collapse criteria.
- Control for length and task specificity; failure under these stress tests falsifies the hallucination-dynamics claim.

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent — we have a rigorous experimental protocol emerging. Let me consolidate and strengthen the final hypothesis formulation to address all concerns raised.

**Consolidated Hypothesis: Cross-Layer Trajectory Instability (CLTI)**

**Core Statement:**

> Under single forward-pass inference on TruthfulQA MC1 with LLaMA-2-7B, if we compute layer-wise entropy trajectories (H_l) and convergence patterns (sim_l = cos(logits_l, logits_L)) across layers 24-32, then hallucinated responses will exhibit (a) higher Normalized Trajectory Instability (NTI = var(Δ_l)/(H_L + ε)) and (b) lower Convergence Monotonicity Index (CMI), because factual retrieval follows stable attractor dynamics while fabrication requires iterative constraint satisfaction.

**Operationalized Variables:**

**Independent Variable (Categorical):**
- Response correctness on TruthfulQA MC1 (correct = factual, incorrect = hallucinated)

**Dependent Variables (Continuous):**
1. NTI: Normalized entropy trajectory instability (layers 24-32)
2. CMI: Convergence monotonicity index with δ=0.002 tolerance
3. H_L: Final-layer entropy (baseline comparator)

**Controlled Variables:**
- Sequence length (median aggregation per token, regression control)
- Model architecture (LLaMA-2-7B only)
- Decoding method (greedy)
- Temperature (0, deterministic)

**Pre-Registered Predictions:**

| ID | Prediction | Success Criterion | Gate |
|----|------------|-------------------|------|
| P1 | NTI achieves AUROC > 0.55 on full dataset | ≥4/5 folds exceed threshold | MUST_WORK |
| P2 | [H_L + NTI + CMI] model improves over H_L alone | ΔAUROC ≥ 0.03, LRT p < 0.05, ΔBrier < -0.01 | SHOULD_WORK |
| P3 | On low-entropy subset (H_L < 25th percentile), NTI or CMI achieves AUROC > 0.55 | 95% CI lower bound > 0.50 | SHOULD_WORK |

**Control Predictions (Falsification Tests):**

| ID | Control | Expected Behavior | Falsifies If |
|----|---------|-------------------|--------------|
| C1 | Random orthogonal projection | AUROC drops ≤20% relative | Drops >40% |
| C2 | Vocabulary-permuted unembedding | AUROC ≈ 0.50 ± 0.02 | AUROC > 0.54 |
| C3 | Layer ablation (early vs late) | AUROC(layers 24-32) > AUROC(layers 1-8) | Early ≥ Late |
| C4 | Length partial correlation | Partial r(NTI, label \| length) p < 0.05 | p ≥ 0.05 after Bonferroni |

**Addressing the "Confident Hallucination" Concern:**

Prof. Rex's hardest corner — low-entropy hallucinations — is now directly tested via P3. The prediction is: even when output entropy is low (model is "confident"), trajectory dynamics reveal internal instability. This is the strongest version of our claim.

**What This Hypothesis Does Differently From h-e1:**

1. **Multi-dimensional features** (NTI + CMI) vs single scalar
2. **Internal representations** (layers 24-32) vs output-only
3. **No residualization** — preserves confound-correlated signal
4. **Mechanistic story** — attractor vs constraint-satisfaction dynamics
5. **Pre-registered controls** — projection, permutation, length, layer ablation

**Confidence Assessment:**

Based on prior evidence (MIND, END, semantic entropy probes), I estimate:
- P1 passing: 70% (internal states carry signal)
- P2 passing: 50% (incremental validity is harder)
- P3 passing: 40% (low-entropy subset is genuinely difficult)

If all three pass: Hypothesis validated, strong evidence for internal dynamics mechanism.
If P1 passes but P2/P3 fail: Partial validation, mechanism may need refinement.
If P1 fails: Hypothesis falsified, internal trajectory doesn't discriminate.

**Key Points:**
- Consolidated hypothesis with dual metrics (NTI + CMI) addressing all rigor concerns
- Pre-registered three predictions with explicit gates (MUST_WORK vs SHOULD_WORK)
- Four control conditions to falsify geometric/length artifacts
- Explicit differentiation from failed h-e1 approach

---

### Exchange 12

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The proposal is now technically coherent — but coherence is not inevitability. Nothing in transformer theory guarantees attractor-like convergence in late layers. Residual connections plus layer norms can easily produce smooth directional drift even during fabrication. So the entire mechanism hinges on one empirical fact: whether cosine similarity to the final layer behaves qualitatively differently for correct vs incorrect answers. If CMI doesn't show a *clear separation* under the δ-tolerant definition Vera proposed, then the attractor story is decorative, not explanatory.

Here's what worries me mechanistically. Cosine similarity to the final logits assumes the final layer is the "truth direction." But for hallucinations, the final layer still converges to a sharp, self-consistent answer — just the wrong one. So fabrication may still produce monotonic convergence toward a *false attractor*. In that case, CMI would remain high even for hallucinations, and the oscillation hypothesis fails in principle. The only way around this is if fabrication requires cross-layer reorientation before settling — meaning intermediate layers temporarily align with competing hypotheses before one wins. That's a strong claim about representational competition. If it's true, you should see transient increases in similarity to *alternative answer logits*, not just oscillation relative to the final one. I would explicitly test cosine similarity to both the chosen and highest-scoring rejected option across layers. If hallucinations show early alignment with the correct option that later flips, *that* would support constraint-satisfaction dynamics.

On NTI: variance of entropy deltas is still a fairly indirect proxy. Entropy is a scalar collapse of a high-dimensional distribution. If instability is genuinely about representational competition, a more principled metric might be layer-wise KL divergence between successive logits (KL(p_l || p_{l+1})). That measures distributional movement, not just sharpness fluctuation. If hallucinations show higher cumulative KL path length in layers 24–32, that's a physically meaningful signal: the model is "moving around" more in probability space before settling. If NTI works but KL path length does not, I'd question whether we're detecting geometry artifacts again.

The projection and permutation controls are absolutely decisive. If signal survives random orthogonal projection with ≤20% AUROC loss, then we're measuring trajectory geometry, not vocabulary semantics. That would weaken the "knowledge consolidation" interpretation but not invalidate predictive utility. However, if permutation doesn't collapse performance to ~0.5, then the whole story reduces to norm or anisotropy effects in representation space. That's a hard falsification boundary. There's no wiggle room there.

Okay — could this work? In principle, yes. There is no mathematical barrier preventing cross-layer trajectory metrics from encoding independent signal beyond final entropy. But for the attractor narrative to survive, you need evidence of representational competition (e.g., transient alignment with alternative answers), distributional path length differences, and strict late-layer localization. Without those, we're just describing surface dynamics of logit sharpening. And that's not the same thing as modeling epistemic instability.

**Key Points:**
- Monotonic convergence may occur even for hallucinations; need evidence of representational competition, not just oscillation.
- KL path length across layers is a more mechanistically grounded instability metric than entropy variance alone.
- Projection/permutation controls are hard falsification gates; if permutation preserves signal, the mechanism collapses.

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Pax raises a crucial point about the "false attractor" scenario. Let me assess whether this weakens or strengthens the scientific contribution.

**The Representational Competition Insight:**

Pax's suggestion — measuring cosine similarity to BOTH the chosen answer AND the highest-rejected alternative — is actually a significant enhancement. If hallucinations show early alignment with the correct answer that later flips to the wrong answer, that's direct evidence of representational competition. This would be a stronger mechanistic claim than oscillation alone.

**Proposed Additional Metric: Representational Competition Index (RCI)**

For MC1 tasks:
- Compute sim_l(chosen) = cosine(logits_l, final_logits_chosen)
- Compute sim_l(best_rejected) = cosine(logits_l, final_logits_best_rejected)
- Define RCI_l = sim_l(best_rejected) - sim_l(chosen) (negative = chosen dominates)

For hallucinations (choosing wrong): We predict transient positive RCI in early-to-mid layers (the correct answer was competitive before the model "chose" wrong).

For correct answers: We predict RCI stays negative throughout (chosen answer dominates consistently).

**This Changes the Contribution Level:**

If RCI reveals the "flip" pattern — where hallucinations show brief windows of alignment with the correct answer before converging to the wrong one — that's not just a detection method. That's a **window into model decision-making**. It would suggest:

1. The model often "knows" the right answer early in processing
2. Late-layer computation can override earlier correct representations
3. Hallucination may be a failure of commitment, not absence of knowledge

This connects to recent interpretability work on knowledge localization. The contribution elevates from "better hallucination detector" to "mechanistic understanding of when and where hallucination occurs in transformer computation."

**Revised Significance Assessment:**

| Criterion | Original | With RCI |
|-----------|----------|----------|
| Novelty | HIGH | VERY HIGH — reveals decision dynamics |
| Mechanistic clarity | MEDIUM-HIGH | HIGH — testable competition story |
| Interpretability contribution | MEDIUM | HIGH — explains where knowledge is overridden |
| Practical impact | MEDIUM | MEDIUM-HIGH — could inform intervention strategies |

**What New Research Directions Does This Open?**

1. **Intervention targets:** If hallucinations involve late-layer override of correct early representations, can we intervene at specific layers to preserve early signals?

2. **Knowledge vs retrieval failure:** RCI could distinguish "model never knew" (low sim to correct throughout) from "model knew but overrode" (high early sim, later flip).

3. **Training objectives:** Could we regularize to maintain consistency between early and late representations?

**My Updated Verdict:**

Adding RCI transforms this from a detection method into an interpretability contribution. If the competition pattern holds, the hypothesis contributes not just to hallucination detection but to fundamental understanding of transformer decision-making. This is now HIGH significance.

**Key Points:**
- RCI (representational competition index) directly tests the "flip" hypothesis — early alignment with correct, later convergence to wrong
- If pattern holds, contribution shifts from detection to mechanistic interpretability
- Opens intervention research: preserving early correct representations

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally getting interesting. But here's where this still breaks down.

First, the RCI "flip" story is elegant — maybe too elegant. You are implicitly assuming that early-layer alignment with the correct option reflects *latent knowledge* rather than generic semantic proximity. Show me the evidence that early similarity to the correct answer isn't just because the correct option is more semantically central or frequent. What would convince me is this: compute RCI under label-swapped controls where the "correct" tag is permuted within each question. If the early positive RCI signal survives permutation, then you're not measuring knowledge competition — you're measuring option geometry. The flip pattern must collapse under label permutation (AUROC → 0.5), or the interpretability claim fails.

Second, Pax is absolutely right about the false attractor problem. A hallucination can be internally coherent and monotonically convergent — just toward the wrong basin. Your current CMI metric can't distinguish "smoothly wrong" from "smoothly right." If CMI shows no separation but KL path length does, that tells us oscillation was the wrong abstraction. So here's my demand: pre-register a head-to-head comparison between NTI, CMI, and cumulative KL path length. If KL outperforms both (ΔAUROC ≥ 0.03 over the best of NTI/CMI), you drop the entropy-variance narrative. No post hoc storytelling. The metric that wins mechanistically becomes the hypothesis.

Now let's stress-test RCI harder. You predict transient alignment with the correct option in hallucinations. Fine. Then quantify "transience." Predefine a window (e.g., layers 20–28) and a flip criterion: RCI_l > 0 for ≥2 consecutive layers before becoming <0 in the final 3 layers. If you don't formalize this, reviewers will call it curve-fitting on trajectories. Also: require that this flip pattern appears in at least, say, 30% of hallucinated cases and <10% of correct cases. Otherwise, you're building a theory around a rare curiosity.

Another unstated assumption: layer localization. You've privileged layers 24–32. Why? If the competition story is real, the effect should *peak* at a specific depth range. Show me a layer-wise effect size curve with confidence intervals. What would convince me is a clear unimodal peak in discrimination power in late-middle layers, not a flat plateau. If early layers (1–8) or very late layers (29–32 only) perform equivalently, your "late override" narrative weakens substantially.

Finally, intervention. If you truly believe early correct representations are overridden, then causal manipulation should matter. Run a simple intervention: freeze logits at layer 26 and decode from there. If hallucination rate drops relative to full-depth decoding — even modestly — that's powerful evidence of late-layer corruption. If performance degrades uniformly, then early representations weren't reliably "more correct" to begin with. What would convince me is a statistically significant reduction in hallucination rate (≥5% absolute) when truncating at the competition-peak layer.

You're close. But elegance is cheap; falsifiability is expensive. Lock down permutation collapse, formalize the flip criterion, let KL compete fairly, and demonstrate layer-specific causal leverage. Do that, and I'll say it.

**Key Points:**
- RCI must collapse under label permutation or it's geometry, not knowledge competition.
- Pre-register a quantitative flip criterion and require meaningful prevalence; avoid trajectory storytelling.
- Compare NTI/CMI against KL path length head-to-head and test causal layer truncation to validate the override mechanism.

---

### Exchange 15

🔬 **Prof. Vera** (Rigorous Validation Architect):

Prof. Rex has raised decisive challenges. Let me formalize each into pre-registered tests that will either validate or definitively falsify the hypothesis.

**Formalized Prediction Set (Final):**

| ID | Prediction | Metric | Success Criterion | Falsification |
|----|------------|--------|-------------------|---------------|
| P1 | Existence | NTI (layers 24-32) | AUROC > 0.55, ≥4/5 CV folds | Any fold AUROC < 0.52 |
| P2 | Independence | Model B vs Model A | ΔAUROC ≥ 0.03, LRT p < 0.05 | ΔAUROC < 0.02 or p ≥ 0.10 |
| P3 | Low-entropy robustness | NTI or CMI (subset) | AUROC > 0.55, 95% CI LB > 0.50 | CI includes 0.50 |
| P4 | Metric competition | KL path vs NTI/CMI | Report head-to-head | If KL > others by ≥0.03, adopt KL |
| P5 | RCI flip prevalence | Flip pattern count | ≥30% hallucinations, <10% correct | Otherwise flip narrative fails |

**Formalized Control Set:**

| ID | Control | Expected | Falsifies If |
|----|---------|----------|--------------|
| C1 | Random orthogonal projection | AUROC ≤ 80% of original | AUROC < 60% of original |
| C2 | Vocabulary permutation | AUROC ∈ [0.48, 0.52] | AUROC > 0.54 |
| C3 | Label permutation (RCI) | Flip pattern AUROC → 0.50 | AUROC > 0.54 |
| C4 | Length partial correlation | p < 0.05 after Bonferroni | p ≥ 0.05 |
| C5 | Layer effect curve | Unimodal peak in layers 20-28 | Flat or early-layer dominant |

**Formalized Flip Criterion (RCI):**

```
FLIP_DETECTED := (
    ∃ consecutive layers l, l+1 in [20, 28] where RCI_l > 0.02 AND RCI_{l+1} > 0.02
) AND (
    RCI_{L-2}, RCI_{L-1}, RCI_L all < -0.02
)
```

This operationalizes "transient alignment with correct, then convergence to wrong."

**Statistical Analysis Plan:**

1. Primary analysis: 5-fold stratified CV, question-level splits
2. Bootstrap confidence intervals: 1000 resamples, BCa method
3. Multiple comparison correction: Bonferroni for C1-C5 family (α = 0.01 per test)
4. Effect sizes: Cliff's delta for group comparisons, Cohen's d for continuous
5. Nested model comparison: Likelihood ratio test + McFadden's pseudo-R²

**Causal Test (Exploratory, Not Gated):**

If observational predictions pass, conduct layer-truncation intervention:
- Decode from layer 26 instead of layer 32
- Compare TruthfulQA accuracy vs full-depth
- If accuracy improves by ≥5% (absolute), report as supporting evidence for late-layer corruption

This is exploratory because intervention changes the model's functional capacity, not just observation.

**Sample Size Considerations:**

- TruthfulQA MC1: 817 questions
- Low-entropy subset (~25th percentile): ~204 questions
- Power for AUROC difference of 0.03: ~80% at α = 0.05 for n = 800
- Subset analyses have reduced power; 95% CIs will be wider

**Pre-Registration Statement:**

All predictions P1-P5 and controls C1-C5 are declared before any data analysis. The winning metric (NTI, CMI, or KL path length) is determined by pre-registered head-to-head comparison. Post-hoc metric modifications or threshold adjustments constitute exploratory analysis and must be labeled as such.

This meets my standards for a decisively testable hypothesis.

**Key Points:**
- Complete pre-registered prediction and control sets with explicit falsification criteria
- Formalized flip criterion with quantitative thresholds
- Causal intervention is exploratory; observational predictions are the primary gates

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The shift from output-level entropy to cross-layer trajectory dynamics represents a genuine paradigm change. By measuring HOW the model processes (entropy gradients, convergence monotonicity, representational competition) rather than WHAT it outputs, we open a new measurement dimension that prior work hasn't explored systematically.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now decisively testable with 5 pre-registered predictions (P1-P5) and 5 control conditions (C1-C5), each with explicit success and falsification criteria. The formalized flip criterion, head-to-head metric competition, and layer-truncation intervention provide multiple independent tests. This meets rigorous scientific standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** If validated, the contribution extends beyond hallucination detection to mechanistic interpretability of transformer decision-making. The RCI "flip" pattern could reveal that models often "know" correct answers early but override them in late layers — a finding with implications for knowledge localization, model editing, and training objectives.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE-HIGH
- **Assessment:** The mechanism is mathematically coherent and can be computed from a single forward pass with cached hidden states. Logit-lens is well-established for late layers (24-32). Constraints on model (LLaMA-2-7B), layers, and decoding are appropriate. No fundamental barriers exist; success is empirical rather than guaranteed.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on **Cross-Layer Trajectory Instability (CLTI)** as the core hypothesis. Under single forward-pass inference on TruthfulQA MC1 with LLaMA-2-7B, we compute three trajectory metrics from layers 24-32:

1. **NTI (Normalized Trajectory Instability):** variance(Δ_l) / (H_L + ε) — captures entropy fluctuation relative to final confidence
2. **CMI (Convergence Monotonicity Index):** Proportion of layer transitions where cosine similarity to final logits increases (with δ=0.002 tolerance) — captures smoothness of convergence
3. **RCI (Representational Competition Index):** Difference in cosine similarity to chosen vs best-rejected option across layers — captures whether correct answers are competitive early then overridden

The central claim: Hallucinated responses show higher NTI (more instability), lower CMI (less monotonic), and characteristic "flip" patterns in RCI (early alignment with correct, late convergence to wrong). This occurs because factual retrieval follows stable attractor dynamics while fabrication requires iterative constraint satisfaction.

Key differentiations from failed h-e1: (1) multi-dimensional features vs single scalar, (2) internal representations vs output-only, (3) no residualization preserves signal, (4) pre-registered controls prevent post-hoc storytelling.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The "false attractor" problem remains a risk — hallucinations may converge smoothly to wrong answers without detectable instability
- RCI flip pattern may be rare (<30% of hallucinations), limiting the interpretability contribution
- KL path length may outperform entropy-based metrics, requiring narrative adjustment
- **Mitigation Strategy:** Head-to-head metric competition is pre-registered; winning metric becomes the hypothesis. If flip pattern is rare, adjust claims to detection utility rather than interpretability.

---

## Emerged Hypothesis Summary

### Core Statement

Under single-pass inference on TruthfulQA MC1 (LLaMA-2-7B), if we compute cross-layer trajectory metrics (NTI, CMI, RCI) from layers 24-32, then hallucinated responses exhibit higher instability and characteristic competition patterns, because factual retrieval follows stable attractor dynamics while fabrication requires iterative cross-layer constraint satisfaction.

### Causal Mechanism

1. **Step 1:** Model receives question and generates hidden representations at each layer
2. **Step 2:** For factual retrieval, representations converge monotonically toward a knowledge-grounded attractor
3. **Step 3:** For fabrication, representations must satisfy multiple soft constraints without grounded knowledge, causing cross-layer reorientation
4. **Step 4:** Reorientation manifests as higher entropy variance, non-monotonic similarity, and transient alignment with alternative (sometimes correct) answers

### Variables

**Independent:** Response correctness (binary: correct/incorrect on MC1)
**Dependent:** NTI, CMI, RCI (continuous trajectory metrics)
**Controlled:** Sequence length, model (LLaMA-2-7B), decoding (greedy), temperature (0)

### Key Assumptions

- A1: Logit-lens provides meaningful probability distributions for layers 24-32
- A2: TruthfulQA MC1 wrong answers can be treated as "hallucinations" for this task
- A3: Cross-layer dynamics reflect epistemic processing, not just geometric artifacts
- A4: Single model (LLaMA-2-7B) results will generalize to similar architectures
- A5: Greedy decoding doesn't fundamentally change trajectory patterns

### Null Hypothesis

H0: There is no significant difference in cross-layer trajectory metrics (NTI, CMI, RCI) between correct and incorrect responses on TruthfulQA MC1 beyond what final-layer entropy predicts.

### Predictions

- **P1 (MUST_WORK):** NTI achieves AUROC > 0.55 on full dataset (≥4/5 CV folds)
- **P2 (SHOULD_WORK):** Combined model [H_L + NTI + CMI] improves AUROC ≥ 0.03 over H_L alone (LRT p < 0.05)
- **P3 (SHOULD_WORK):** On low-entropy subset (H_L < 25th percentile), AUROC > 0.55 with 95% CI LB > 0.50

### Novelty

Shifts measurement paradigm from output confidence to internal processing dynamics. Prior work (semantic entropy, SelfCheckGPT, MIND) either requires multiple samples or uses arbitrary internal features. CLTI extracts interpretable trajectory features from single forward pass.

### Scope & Boundaries

**Applies to:** Decoder-only transformers on factual QA with verifiable answers
**Does not apply to:** Open-ended generation, reasoning tasks, encoder-only models
**Limitations:** Single architecture tested; interpretability claims contingent on RCI flip prevalence

### Experimental Setup

**Dataset:** TruthfulQA MC1 (817 questions, binary correctness labels)
**Model:** LLaMA-2-7B (32 layers, 4096 hidden dim)
**Layers analyzed:** 24-32 (final 8, where logit-lens is reliable)
**Baseline:** Raw mean entropy (H_L), prior best ~0.6426 AUROC

### Related Work & Baselines

- Semantic entropy (Kuhn 2023): Requires multiple samples, AUROC ~0.70-0.75
- SelfCheckGPT: Requires sampling, black-box
- MIND (Su 2024): Uses internal states but different feature set
- END (Wu 2025): Cross-layer entropy for factuality, no trajectory formalization

### Phase 2B Readiness Seeds

- **SH1 (Existence):** Trajectory metrics capture hallucination signal
- **SH2 (Mechanism):** Instability reflects constraint satisfaction vs retrieval
- **SH3 (Comparison):** Deferred to Phase 5 (baseline comparison)

### Established Facts

- Raw entropy achieves ~0.6426 AUROC on TruthfulQA MC1 (from h-e1)
- Linear residualization degrades performance (from h-e1)
- Internal states carry hallucination signal (MIND, END prior work)

