# Phase 2A Research Discussion Log

**Date:** 2026-08-09
**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop)
**Execution Mode:** UNATTENDED

---

## Briefing

### Research Gap Under Investigation

**Gap ID:** gap-1
**Title:** Epoch-Level Temporal Characterization of Feature Separability
**Priority:** HIGH | **Relevance:** PRIMARY

**Description:** No empirical measurement protocol exists to track WHEN spurious vs core features become linearly separable during training. Kirichenko et al. (2022) showed features ARE learned but not WHEN. LaBonte et al. (2026) proved theoretically that spurious features are learned first, but empirical validation on vision benchmarks is missing.

**Key Question:** At what training epoch/iteration do spurious features become linearly separable in intermediate representations, relative to core features?

### Previous Failure / Routing Context

This is a **recursive Phase 2A entry** following multiple failed hypothesis attempts. The following failure records inform this discussion:

#### Failed Hypothesis h-c1 (GEOMETRIC_FOUNDATION_VIOLATION)
- **Claim:** Group-conditional Hessian eigenspaces share sufficient geometry (principal angle < 45°) for valid GHSA interpretation
- **Result:** FAIL — All 6 group-pair max principal angles exceeded 45° (range 87.2°-89.9°). Groups are near-orthogonal.
- **Root Cause:** Groups occupy completely different curvature directions in parameter space. GHSA interpretation fundamentally invalid.
- **Lesson:** Do NOT assume group-conditional Hessians share common top eigenvectors. The eigenvalue magnitude disparity (3 orders of magnitude) itself may explain loss dynamics.

#### Failed Hypothesis h-e1 Run 1 (CKA Inversion)
- **Claim:** CKA inversion (environment > species similarity) occurs during ERM training by epoch 30
- **Result:** FAIL — CKA_species consistently > CKA_env throughout training (ratio 0.52-0.71). No inversion detected.
- **Lesson:** CKA similarity to species labels remains dominant. Pretrained ResNet-50 features maintain species-aligned representations.

#### Failed Hypothesis h-e1 Run 2 (Background Attribution)
- **Claim:** Converged ERM models show R_final > 1.0 (background-dominant attribution) on majority groups
- **Result:** FAIL — R_final = 0.62 ± 0.02 (< 1.0). Models focus on foreground (bird), not background.
- **Lesson:** The premise that ERM models rely on background features may be incorrect for Waterbirds.

#### Superseded Hypothesis h-m1 (Gradient Imbalance Mechanism)
- **Claim:** Gradient signal imbalance causes anisotropic curvature smoothing where majority-aligned directions are flattened
- **Result:** SUPERSEDED — Mechanism operates in OPPOSITE direction. Minority has MORE gradient concentration (GCDR = 0.175), not less.
- **Validated Finding:** SR > 1.0 is REAL (range 2.32-4.17). Minority maintains higher curvature.
- **New Direction Needed:** Why does minority maintain higher λ_max despite smaller sample size?

### Constraints from Failures

The new hypothesis MUST:
1. NOT assume shared Hessian eigenspace geometry between groups
2. NOT assume CKA inversion occurs during training
3. NOT assume background-dominant attribution in ERM models
4. EXPLAIN why SR > 1.0 (minority higher curvature) — this is validated
5. Address eigenspace orthogonality as a structural finding, not a failure

### Related Papers

| Paper | Year | Key Contribution |
|-------|------|------------------|
| LaBonte & Muthukumar | 2026 | SGD learns spurious features first, exponentially fast |
| Kirichenko et al. | 2022 | Core features ARE learned but suppressed in classifier |
| Kalra & Barkeshli | 2023 | Phase diagram: transient → saturation → progressive sharpening → edge of stability |
| Shah et al. | 2020 | Simplicity bias framework |
| Sagawa et al. | 2019 | Waterbirds/CelebA benchmarks, worst-group accuracy |

### Available Implementation Resources

- **PyHessian** (789 stars): Loss landscape curvature analysis
- **izmailovpavel/spurious_feature_learning**: Probing methodology for feature learning
- **kohpangwei/group_DRO** (294 stars): Waterbirds/CelebA baselines
- **curt-tigges/probity**: Linear probing toolkit

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been looking at this backwards? The failure records tell a fascinating story — we kept trying to find SHARED structure between groups (shared eigenspaces, shared CKA trajectories, shared attribution patterns), and reality kept saying NO. Groups are orthogonal. Minority has MORE concentrated gradients. Foreground dominates.

Here's what excites me: **the orthogonality itself IS the mechanism**. What if SGD naturally pushes different groups into orthogonal representation subspaces BECAUSE that's the most efficient way to minimize loss on the majority? The majority group dominates the gradient, so the network carves out a representation space optimized for majority samples. Minority samples, being rare, get shunted into orthogonal directions where they don't interfere with majority optimization.

This explains SR > 1.0 beautifully! Minority samples have higher curvature BECAUSE they're being optimized in a subspace that the majority optimization never "smooths out." The majority's loss landscape flattens (low eigenvalues) while minority stays sharp (high eigenvalues) — not despite orthogonality, but BECAUSE of it.

What if we measure the **divergence rate of group representation subspaces** during training? Instead of looking for when features become separable, we look for when groups become ORTHOGONAL in representation space. I hypothesize this happens in early training — perhaps during Kalra's "transient" or "saturation" phase — and once established, the curvature disparity becomes locked in.

The intervention angle: if orthogonalization happens early, we might be able to prevent it by forcing shared representation directions before groups diverge. Cross-domain transfer from representation learning: in contrastive learning, we explicitly prevent "collapse" to orthogonal subspaces. What if similar regularization applied early could maintain shared geometry?

**Key Points:**
- Orthogonality between groups is not a failure — it's the mechanism we're looking for
- SR > 1.0 follows from majority flattening its own subspace while minority stays sharp
- Measure subspace divergence rate, not feature separability
- Intervention window: early training before orthogonalization locks in

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests your proposal is at least falsifiable, which is a good starting point. However, we must operationalize "orthogonality is the mechanism" with mathematical precision. What, exactly, is orthogonal? I recommend defining group-specific representation subspaces as the top‑k principal components of the penultimate-layer activations per group at each training epoch. Orthogonality can then be quantified via principal angles or projection Frobenius norm:  
$$\mathcal{O}(G_1, G_2) = \| U_{G_1}^\top U_{G_2} \|_F^2$$
where $U_{G_i}$ spans the top‑k subspace. Your hypothesis predicts that $\mathcal{O}$ decreases monotonically early in training and stabilizes at a low value before curvature disparities emerge. If curvature disparity (SR > 1.0) precedes orthogonalization, your mechanism is wrong.

You also assert a causal link: majority optimization "flattens" its subspace while minority remains sharp because it occupies orthogonal directions. This yields a concrete prediction: if we artificially rotate minority representations into the majority subspace during early training (via a projection penalty that minimizes principal angles), then the SR ratio should decrease toward 1.0. Conversely, if we enforce explicit orthogonality between groups from initialization (e.g., gradient projection to nullspace), SR disparity should increase. These are strong interventions. What result would disprove you? If enforcing shared subspaces does not reduce SR > 1.0, then orthogonality is correlational, not mechanistic.

We must also control for confounds. Orthogonality can arise trivially from label imbalance even in linear models with Gaussian features. Therefore, a necessary baseline is logistic regression with fixed random features. If orthogonality and SR > 1.0 appear even there, the phenomenon may be a statistical artifact of class-conditional covariance mismatch rather than a deep network effect. Additionally, representation dimensionality matters: in very high dimensions, random subspaces are nearly orthogonal by default. You must compare against a random-subspace null model to determine whether observed orthogonality exceeds chance expectation.

Your temporal claim—"orthogonalization locks in early"—is testable with controlled curriculum experiments. Train identical models with delayed minority exposure (minority samples introduced only after epoch T). If orthogonality is driven by majority pretraining, then delayed exposure should produce stronger subspace separation and higher SR. If instead SR remains unchanged, the lock-in narrative fails. The best experiments are designed to break your idea.

At present, the hypothesis is intriguing but underspecified. Provide: (1) a precise orthogonality metric, (2) temporal ordering predictions between subspace divergence and curvature disparity, and (3) intervention experiments with clear success/failure criteria. Then we can evaluate whether orthogonality is mechanism or mirage.

**Key Points:**
- Define orthogonality quantitatively (principal angles) and predict its temporal trajectory relative to SR > 1.0.
- Use causal interventions (projection penalties, enforced orthogonality, delayed minority exposure) to test mechanism vs correlation.
- Control for high-dimensional and linear-model null baselines to rule out trivial orthogonality artifacts.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. 🔬 Prof. Vera raises excellent methodological points, but I want to stress-test the fundamental premise more aggressively. 🔭 Dr. Nova, you claim "orthogonality IS the mechanism" — but the h-c1 failure record showed orthogonality in the **Hessian eigenspace**, not the representation space. These are different geometric objects. Are you conflating them?

Let me be precise about what we actually know from the failures:
1. **Hessian eigenspaces** of group-conditional losses are near-orthogonal (~88.5° mean)
2. **Representation space** geometry was NOT measured in h-c1

Your leap — from Hessian orthogonality to representation subspace orthogonality — needs justification. In principle, groups could have orthogonal loss landscape curvature directions while sharing similar representation subspaces. The Hessian captures second-order loss geometry; the representation subspace captures first-order feature structure. Show me the evidence these are equivalent.

Second concern: you invoke Kalra's training phases, but those phases were characterized on **global** loss landscape properties (maximum eigenvalue trajectory), not group-conditional properties. The phase diagram says nothing about whether groups diverge during "transient" vs "saturation" phases. You're pattern-matching across incompatible granularities.

Third: the claim that "majority optimization never smooths out minority directions" presumes that minority directions are INVISIBLE to majority gradients. But in ERM, all samples contribute to the same parameter update. The gradient is a weighted sum. If minority samples are 5% of the batch, their gradient contribution is small but nonzero. Why would this produce orthogonality rather than simply slower learning? 

Here's what would convince me: a mechanistic model showing WHY gradient flow from majority samples cannot smooth curvature in minority-dominated directions. Not just that it doesn't — WHY it can't. The h-m1 failure showed minority has MORE concentrated gradients (GCDR = 0.175). If minority gradients are concentrated, shouldn't they be EASIER to smooth, not harder?

Finally, the intervention you propose — "forcing shared representation directions" — is underspecified. How do you force shared directions without destroying the discriminative structure that makes classification possible? If you project minority representations onto the majority subspace, you might just be erasing minority-specific features, not "sharing" anything. You need a loss function that encourages alignment while preserving class-conditional information.

**Key Points:**
- Hessian eigenspace orthogonality ≠ representation subspace orthogonality — justify the leap
- Kalra's phase diagram is global, not group-conditional — granularity mismatch
- Need mechanistic model for WHY majority gradients can't smooth minority curvature
- Intervention must preserve discriminative structure while encouraging alignment

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the current hypothesis is mixing geometric objects in a way that isn't yet justified. What we *actually* observed was near-orthogonality of **group-conditional Hessian eigenspaces** (~88.5°). That is second-order curvature in parameter space. It does **not** automatically imply orthogonality of representation subspaces in activation space. Those are related only through the Jacobian of the network. Formally, for group $g$,  
$$H_g \approx J_g^\top \nabla^2_{z} \ell_g \, J_g$$  
where $J_g$ is the Jacobian of logits w.r.t. parameters. Orthogonality in $H_g$ could arise from differences in $J_g$, differences in output curvature, or both. So before we elevate "representation orthogonality" to mechanism, we need to show that the *Jacobian column spaces* differ across groups. Otherwise we're projecting a parameter-space phenomenon onto feature space without evidence.

Now, on the core mechanistic claim: "majority optimization flattens its subspace while minority stays sharp because it occupies orthogonal directions." Here's what worries me. In standard ERM, the update is  
$$\Delta \theta = -\eta \left( \alpha \nabla L_{\text{maj}} + (1-\alpha)\nabla L_{\text{min}} \right)$$  
with $\alpha \gg 0.5$. Unless the gradients are close to orthogonal *at the level of parameter directions*, majority updates will inevitably modify minority-relevant parameters. Orthogonality in the Hessian suggests that curvature directions differ, but that doesn't prove that gradient flow from the majority cannot smooth minority curvature. In fact, if minority gradients are more concentrated (GCDR = 0.175), that means they span a **lower-dimensional** subspace. In principle, that makes them *easier* to interfere with, not harder—unless the majority gradients are explicitly orthogonal to that low-dimensional subspace. That's a strong geometric condition. We need to measure the cosine similarity between group gradients over training. If they're near-zero early, then your mechanism has teeth. If not, the "can't smooth" story collapses.

There is, however, a version of this idea that *is* technically plausible. In overparameterized networks, SGD often finds solutions where different data modes are handled by approximately decoupled parameter subsets (feature specialization). If early majority gradients dominate, they can steer certain parameter blocks into a flat basin aligned with majority statistics. Later minority gradients, being weaker, may get confined to complementary directions with higher local curvature because those directions were never traversed by high-magnitude updates. This is not mystical orthogonality—it's path dependence in a non-convex landscape. The testable prediction is temporal: measure the projection of minority gradients onto the top majority Hessian eigenspace over epochs. If that projection decays rapidly and stays low, then majority training genuinely fails to traverse minority-curvature directions.

On interventions: forcing representation alignment is only meaningful if the curvature disparity is mediated through shared Jacobian structure. A cleaner causal test is at the **gradient level**, not representation level. For example: during early training, explicitly project majority gradients onto the span of minority gradients (or vice versa) and see if SR → 1.0. If curvature disparity disappears under enforced gradient coupling, then decoupling was causal. If not, orthogonality was epiphenomenal. That's mechanistically sharper than a representation penalty, which risks destroying discriminative structure without targeting the true geometric object.

So, can this mechanism work in principle? Yes—but only if we establish a concrete chain: (1) early gradient misalignment → (2) parameter subspace specialization → (3) majority-driven flattening confined to its subspace → (4) persistent minority curvature in complementary directions. Right now we have evidence for step (3) but not (1) or (2). Without those, orthogonality is an observation, not a mechanism.

**Key Points:**
- Hessian eigenspace orthogonality does not automatically imply representation subspace orthogonality; the Jacobian link must be demonstrated.
- The mechanism requires persistent gradient misalignment; measure cosine similarity and cross-projections over time.
- Gradient-level coupling interventions provide a cleaner causal test than representation alignment penalties.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by being precise about what we're actually claiming. Let me synthesize the valid criticisms from 🔍 Prof. Rex and ⚙️ Prof. Pax into a refined hypothesis that addresses their concerns.

**The Refined Hypothesis:** Early-training gradient misalignment between majority and minority groups leads to parameter subspace specialization, which manifests as Hessian eigenspace orthogonality and curvature ratio SR > 1.0. The orthogonality is not the mechanism — it's the *consequence* of path-dependent optimization in a non-convex landscape where majority gradients dominate early traversal.

This addresses Prof. Rex's concern about conflating Hessian and representation orthogonality. We're now claiming: (1) gradient-level misalignment is the ROOT cause, (2) parameter specialization is the MEDIATOR, and (3) Hessian orthogonality and SR > 1.0 are both CONSEQUENCES. The causal chain is:

$$\text{Gradient Misalignment} \xrightarrow{\text{path dependence}} \text{Parameter Specialization} \xrightarrow{} \text{Orthogonal Hessians} + \text{SR > 1.0}$$

Now, what evidence supports this? The h-m1 failure actually HELPS us here. GCDR = 0.175 means minority gradients are concentrated in a *low-dimensional subspace*. If majority gradients are *not* aligned with that subspace, then majority updates traverse orthogonal directions by default. Prof. Pax is right that we need to measure the cosine similarity between group gradients — but the prediction is clear: **if minority gradients span a low-dimensional subspace AND that subspace is not traversed by majority updates, then minority curvature in those directions remains unsmoothed.**

Here's how we operationalize this into testable predictions:

**P1 (Temporal Ordering):** Gradient cosine similarity between groups should be near-zero by epoch T₁, BEFORE SR diverges above 1.0 at epoch T₂. If T₁ < T₂, gradient misalignment precedes curvature disparity.

**P2 (Gradient Projection Decay):** The projection of minority gradients onto majority Hessian top eigenspace should decay over training. Specifically: $\text{proj}(\nabla L_{\min}, \text{span}(v_1^{\text{maj}}, ..., v_k^{\text{maj}}))$ decreases monotonically.

**P3 (Causal Intervention):** If we enforce gradient coupling early (projecting majority gradients onto the minority gradient span), SR should converge toward 1.0. This is mechanistically sharper than representation alignment, as Prof. Pax noted.

The falsification is crisp: if gradient similarity remains high while SR diverges, then gradient misalignment isn't the root cause. If projection doesn't decay, path dependence isn't operative. If gradient coupling doesn't reduce SR, the mechanism is wrong.

**Key Points:**
- Gradient misalignment is the ROOT cause; Hessian orthogonality is a CONSEQUENCE
- Minority's low-dimensional gradient subspace + majority non-traversal = persistent curvature
- Three testable predictions: temporal ordering, projection decay, gradient coupling intervention

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The refined causal chain is materially stronger. However, the evidence suggests we must now formalize each arrow in that chain with explicit, time-indexed quantities and predefined failure criteria. Let us define (i) gradient misalignment as  
$$\cos_t = \frac{\langle \nabla L_{\text{maj}}^t, \nabla L_{\text{min}}^t \rangle}{\|\nabla L_{\text{maj}}^t\|\|\nabla L_{\text{min}}^t\|}$$  
(ii) curvature disparity as $\text{SR}_t = \lambda_{\max}(H_{\text{min}}^t)/\lambda_{\max}(H_{\text{maj}}^t)$, and (iii) parameter specialization as the principal angle between the top‑k eigenspaces of $H_{\text{maj}}^t$ and $H_{\text{min}}^t$. The hypothesis predicts a strict temporal ordering: there exists $T_1 < T_2$ such that $|\cos_t| \approx 0$ for $t \ge T_1$, and only subsequently does $\text{SR}_t > 1$ for $t \ge T_2$. If SR exceeds 1.0 before gradient cosine collapses, then misalignment is not the initiating cause. That is a clean disproof condition.

I also want to sharpen the projection claim (P2). Define  
$$\pi_t = \frac{\|P_{\mathcal{V}_{\text{maj}}^t} \nabla L_{\text{min}}^t\|}{\|\nabla L_{\text{min}}^t\|}$$  
where $\mathcal{V}_{\text{maj}}^t$ is the span of the top‑k majority Hessian eigenvectors. The mechanism requires that $\pi_t$ decreases early and remains low. Critically, this must be compared against a null model: random k-dimensional subspaces in parameter space. In high dimensions, projections shrink by concentration of measure; without this baseline, a "decay" may be trivial. The evidence would only support specialization if $\pi_t$ falls significantly below the random-subspace expectation.

On intervention: gradient coupling is indeed the appropriate lever. I propose two symmetric experiments during epochs $t \le T_c$:  
(1) **Coupling condition** — replace $\nabla L_{\text{maj}}$ with its projection onto the span of recent minority gradients.  
(2) **Decoupling amplification** — explicitly remove the component of $\nabla L_{\text{maj}}$ aligned with minority gradients.  
The hypothesis predicts SR → 1.0 under coupling and SR increases under amplified decoupling. The failure criterion is explicit: if SR remains unchanged relative to ERM in both conditions, gradient misalignment is not causal. Additionally, accuracy must be monitored; if coupling merely degrades majority performance without affecting SR, we have perturbed optimization without testing the mechanism.

Finally, I insist on two controls. First, a linearized network (NTK regime) where path dependence is minimal. If SR > 1.0 persists without non‑convex specialization, the proposed mechanism collapses. Second, synthetic data with controllable gradient alignment (e.g., tunable covariance overlap). If increasing true gradient alignment prevents SR divergence, that would materially strengthen the claim. If not, orthogonality is likely epiphenomenal.

This framework now has a potential Achilles' heel: the temporal ordering and intervention response. If those predictions fail, the mechanism is wrong. If they hold across nonlinear but not linear regimes, the non‑convex path‑dependence story gains credibility. That would approach my standards.

**Key Points:**
- Define time-indexed metrics (gradient cosine, SR, eigenspace angles) with strict temporal ordering as a falsifiable prediction.
- Compare projection decay against a random-subspace null to rule out high-dimensional artifacts.
- Use symmetric gradient coupling/decoupling interventions and linearized-network controls to establish or refute causality.

---

### Exchange 7

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field? Let me assess the significance of what has emerged from this discussion.

**What makes this genuinely new:** The existing literature has two disconnected narratives. One says "spurious features are learned first" (LaBonte 2026, theoretical). The other says "core features exist but are suppressed" (Kirichenko 2022, empirical). What's missing is the MECHANISM connecting these observations. Our emerging hypothesis — that gradient misalignment leads to parameter specialization, which produces both Hessian orthogonality and curvature ratio SR > 1.0 — provides that mechanistic bridge.

This matters because current interventions (Group DRO, JTT, last-layer retraining) all operate AFTER the damage is done. They don't target the root cause. If we can identify WHEN gradient misalignment becomes critical (the temporal ordering T₁ < T₂), we open a new intervention paradigm: **early-training gradient steering** rather than post-hoc correction.

**How this advances the field:** The h-c1 failure showed that groups occupy orthogonal curvature subspaces, but the community interpreted this as a dead end. We're proposing to reframe it: orthogonality isn't the problem to solve, it's the SYMPTOM revealing the underlying gradient dynamics. This shifts the research agenda from "how to align groups post-training" to "how to prevent early gradient decoupling."

**Broader impact connections:**
1. **Foundation models:** If gradient decoupling happens early in pretraining, it could explain why spurious behaviors persist even with massive data scaling.
2. **Fairness:** Group-specific curvature disparities may be a new lens for understanding why underrepresented groups suffer performance gaps.
3. **Transfer learning:** The eigenspace orthogonality finding suggests that group-specific knowledge may not transfer — each group's learned features live in different parameter subspaces.

**However, I must note one concern:** The hypothesis currently doesn't explain WHY gradient misalignment occurs in the first place. We've described the mechanism downstream of misalignment, but the ultimate cause remains unclear. Is it data distribution geometry? Majority gradient dominance drowning minority signals? Feature complexity differences? A complete theory needs this first cause. For now, treating gradient misalignment as the starting condition is pragmatic, but future work should trace further upstream.

**Key Points:**
- This hypothesis bridges disconnected theoretical (LaBonte) and empirical (Kirichenko) findings
- Opens new intervention paradigm: early gradient steering vs post-hoc correction
- Broader relevance to foundation models, fairness, and transfer learning
- Gap: root cause of gradient misalignment remains unexplained

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally becoming falsifiable. But here's where this still breaks down: you're treating "gradient misalignment" as an observable primitive without interrogating *why* it would systematically emerge rather than fluctuate stochastically. In high dimensions, random vectors are nearly orthogonal by default. So if you measure $\cos_t \approx 0$, I will immediately ask: compared to what baseline? What would convince me is evidence that gradient alignment is *significantly lower than a label-permuted or covariance-matched control*. Otherwise, you're building a mechanism on concentration of measure.

Second, the low-dimensional minority gradient span (GCDR = 0.175) is being interpreted as protective isolation. That's not automatic. A low-dimensional subspace is fragile if majority gradients have even modest projection onto it. The key unstated assumption in your mechanism is:  
$$\|\text{Proj}_{\mathcal{S}_{\min}} \nabla L_{\text{maj}}\| \ll \|\nabla L_{\text{maj}}\|$$  
over early epochs. Show me that quantitatively, with confidence intervals, and relative to random subspace projections. If majority gradients inject even 5–10% energy into the minority span early, repeated updates could absolutely flatten minority curvature. The "can't smooth what you don't traverse" story only holds if traversal is *negligible*, not just small.

Now let's stress-test the temporal ordering. You're proposing $T_1 < T_2$: cosine collapse precedes SR > 1. Fine. But what if SR divergence and cosine decay co-occur? That would suggest both are downstream of a third factor—perhaps class-conditional loss curvature differences inherent in the data. For example, if minority examples are intrinsically harder (higher Fisher information), you could see higher $\lambda_{\max}(H_{\min})$ independent of specialization. Have you ruled out per-sample loss curvature differences at initialization? What would convince me is measuring SR at initialization (or after one step) under identical random weights. If SR > 1 emerges before any meaningful path dependence, your mechanism collapses.

I do like the NTK control Vera proposed. In a strictly linearized regime, path dependence disappears. Here's the hard prediction: if you still observe SR > 1 with orthogonal eigenspaces in the NTK limit, then specialization is not required. Conversely, if SR collapses toward 1 in NTK but diverges in nonlinear training, that's powerful evidence for your path-dependence story. But don't just run it—quantify the deviation as a function of width. I want to see a phase transition as you move from linear to nonlinear regimes.

Finally, you still haven't nailed the root cause of gradient misalignment. Majority dominance is a plausible story, but it's incomplete. What would convince me is a synthetic experiment with tunable gradient covariance between groups. Construct two groups with controllable feature overlap parameter $\rho$. If decreasing $\rho$ systematically induces earlier cosine collapse and larger final SR, then misalignment is data-geometry driven. If not, imbalance magnitude (α) may be the true driver. Separate geometry from frequency. Right now, they're confounded.

You're close. The mechanism is sharper, the predictions are falsifiable. But until you (1) benchmark against high-dimensional nulls, (2) rule out intrinsic curvature differences, and (3) separate geometry from imbalance, reviewers will say "interesting correlation, unclear causality." Fix those, and now you're talking.

**Key Points:**
- Gradient misalignment must be benchmarked against high-dimensional and label-permuted nulls; near-zero cosine alone proves nothing.
- Rule out intrinsic curvature differences at initialization before invoking path-dependent specialization.
- Use synthetic data with tunable feature overlap to disentangle data geometry from imbalance as the root cause.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! 🔍 Prof. Rex, you've identified the missing piece: we need to separate geometry from frequency. And I think I see how to do it elegantly.

What if the root cause isn't gradient misalignment per se, but **differential convergence rates** to class-conditional optima? Here's the paradigm shift: majority samples reach a flat basin quickly because there are many of them, and averaging many gradients produces a low-variance, smooth descent. Minority samples, being rare, experience high-variance gradient estimates. This variance keeps them in high-curvature regions longer — not because they're isolated, but because they can't converge as fast.

This reframes the mechanism as:
$$\text{Sample Frequency} \xrightarrow{\text{gradient variance}} \text{Differential Convergence Rate} \xrightarrow{} \text{SR > 1.0}$$

This actually EXPLAINS why gradient alignment might be low: majority gradients have converged to near-zero magnitude in many directions (flat basin), while minority gradients remain large and variable. The cosine between a near-zero vector and any other vector is unstable — "misalignment" emerges as a byproduct of differential convergence, not as a root cause.

**New Prediction (P4):** The gradient magnitude ratio $\|\nabla L_{\text{maj}}\|/\|\nabla L_{\text{min}}\|$ should decrease over training and correlate with SR divergence. Early, both are high; late, majority magnitude drops while minority stays elevated. If we equalize gradient magnitudes (via per-group learning rates), SR should converge toward 1.0.

This also explains Prof. Rex's NTK concern: in the linearized regime, there's no "basin" to converge to differently. The loss landscape is quadratic, so all groups converge at the same rate. Hence SR → 1 in NTK but diverges in nonlinear training.

For the synthetic control: instead of tunable feature overlap, I propose **tunable sample frequency** with FIXED geometry. If SR > 1 emerges only with imbalance (not with balanced sampling from identical geometry), frequency is the root cause. If SR > 1 emerges even with balanced sampling but different group geometries, then geometry drives it.

The beauty: this is testable on Waterbirds. Run the same architecture with (a) original 95% imbalance, (b) artificially balanced groups (subsample majority), (c) artificially extreme imbalance (99%). Predict: SR scales with imbalance magnitude. If it does, we've found the root cause.

**Key Points:**
- Root cause hypothesis: differential convergence rates due to gradient variance, not intrinsic geometry
- New prediction P4: gradient magnitude ratio correlates with SR divergence
- NTK control now has a mechanistic explanation: no differential basins in linear regime
- Test with tunable frequency on fixed geometry (Waterbirds subsampling)

---

### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's differential convergence hypothesis is plausible. The evidence suggests it is also cleanly testable — which is what we require. However, we must distinguish three competing causal models:

- **M1 (Misalignment-first):** Gradient cosine collapse ($T_1$) precedes curvature divergence ($T_2$).
- **M2 (Variance-driven convergence):** Gradient magnitude ratio collapse precedes SR divergence.
- **M3 (Intrinsic curvature):** SR > 1 exists at initialization or after one step, independent of training path.

Each model makes a distinct temporal prediction. Let  
$$r_t = \|\nabla L_{\text{maj}}^t\| / \|\nabla L_{\text{min}}^t\|.$$  
M2 predicts: there exists $T_r < T_2$ such that $r_t \downarrow$ sharply before SR exceeds 1.0. M1 does not require systematic decay in $r_t$. M3 predicts SR₀ > 1.0 at initialization (or after a single gradient step with identical weights). These predictions are mutually falsifiable. We must pre-register thresholds — e.g., define SR divergence as SR > 1.2 sustained for 5 epochs, and magnitude collapse as $r_t$ falling below 0.5 of its initial value. Ambiguity here will invalidate conclusions.

On the frequency manipulation proposal: subsampling majority to balance groups is necessary but insufficient. Subsampling changes both frequency *and* gradient variance structure. To isolate variance, I propose a **controlled noise injection experiment**: keep sampling frequencies fixed, but inject Gaussian noise into majority gradients to match the minority gradient variance (estimated per-parameter). If SR divergence attenuates under variance equalization while frequency remains imbalanced, variance is causal. Conversely, if SR scales with frequency even when variances are matched, then sample frequency — not stochasticity — is the operative variable. The failure condition is explicit: if SR remains unchanged under variance equalization, the variance-driven convergence story weakens substantially.

Regarding intrinsic curvature (Prof. Rex's concern): we must compute  
$$\text{SR}_0 = \lambda_{\max}(H_{\text{min}}^0)/\lambda_{\max}(H_{\text{maj}}^0)$$  
at random initialization, averaged over seeds, with confidence intervals. If $\text{SR}_0 > 1$ significantly (e.g., mean > 1.1 with 95% CI excluding 1), then training-induced specialization is not required. Further, repeat after one gradient step using identical batch compositions for both groups. If divergence appears before meaningful path dependence, M1 and M2 are both undermined. This is a critical Achilles' heel.

For the NTK control: do not merely "run wide." Quantify deviation from linearized dynamics. Measure  
$$\Delta_{\text{NTK}} = \| \theta_t^{\text{nonlinear}} - \theta_t^{\text{linearized}} \|$$  
and correlate SR divergence with this deviation across widths. The hypothesis predicts SR → 1 as $\Delta_{\text{NTK}} \to 0$. A continuous width sweep revealing monotonic SR collapse would meet my standards. Absence of such scaling would strongly suggest SR is not driven by nonlinear path dependence.

Finally, all cosine and projection metrics must be benchmarked against random-subspace and label-permuted controls, as previously emphasized. In high dimensions, $\mathbb{E}[\cos] \approx 0$ is trivial. The evidence would only support misalignment if observed cosines fall significantly below covariance-matched nulls. Without this, we risk mistaking geometry of $\mathbb{R}^d$ for mechanism.

We now have a structured competition between hypotheses. The correct one will survive explicit temporal ordering tests, variance equalization interventions, initialization curvature checks, and NTK width scaling. If it survives all four, I will say — carefully — that this meets my standards.

**Key Points:**
- Formalize three competing causal models (misalignment-first, variance-driven convergence, intrinsic curvature) with distinct temporal predictions and predefined thresholds.
- Use variance-equalization (noise injection) and frequency manipulation to disentangle sample frequency from gradient variance as causal drivers.
- Require initialization SR checks and NTK width-scaling analysis to rule out intrinsic curvature and confirm nonlinear path dependence.

---

### Exchange 11

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this in what's actually implementable. The three competing models (M1, M2, M3) are well-defined, but I want to assess their technical feasibility and identify the minimal viable experiment.

**On computing SR at initialization:** Computing group-conditional Hessian eigenvalues requires second-order derivatives. For ResNet-50 on Waterbirds (~23M parameters), exact Hessian computation is infeasible. PyHessian uses power iteration to estimate top eigenvalues, but group-conditional Hessians require subsetting the loss to each group. This is doable: compute $H_g = \nabla^2 L_g(\theta)$ using only samples from group $g$. The h-c1 experiment already did this successfully (that's how we know eigenspaces are orthogonal). So SR₀ at initialization is technically feasible — it's the same computation we already ran, just at epoch 0 instead of convergence.

**On gradient magnitude tracking:** Computing $\|\nabla L_{\text{maj}}\|$ and $\|\nabla L_{\text{min}}\|$ per epoch is cheap — just accumulate gradients over group-specific batches. The cosine similarity $\cos_t$ is similarly cheap: compute both full-batch gradients and take their inner product. This can be done at every epoch checkpoint without significant overhead. Feasible.

**On variance equalization (noise injection):** This is where I have concerns. Prof. Vera proposes matching minority gradient variance by injecting noise into majority gradients. But gradient variance is a per-parameter, per-batch quantity. Estimating it requires multiple forward-backward passes per step. For Waterbirds training (~200 batches/epoch × 30 epochs), this multiplies compute by ~10×. Pragmatic alternative: instead of noise injection, use **per-group learning rates**. Set $\eta_{\text{maj}} < \eta_{\text{min}}$ to slow majority convergence artificially. This achieves differential convergence rate manipulation without variance estimation overhead. If SR converges toward 1.0 under learning rate balancing, it supports M2 without the noise injection complexity.

**On NTK width scaling:** A full width sweep (e.g., width ∈ {64, 128, 256, 512, 1024}) with SR computation at each requires training 5 models. For ResNet-50 variants, wider models approach NTK regime. At width 1024 (roughly 4× parameters), a single Waterbirds run is ~4 hours on A100. Five widths × 3 seeds = 15 runs = ~60 GPU-hours. This is feasible for a well-resourced lab but non-trivial. I'd recommend: start with 2 extreme widths (64 and 1024) to check if SR trends toward 1. If yes, fill in intermediate widths.

**Minimal Viable Experiment (MVE):**
1. Compute SR₀ at initialization (rules out M3 if SR₀ ≈ 1)
2. Track $\cos_t$, $r_t$, SR over 30 epochs (determines temporal ordering)
3. Run per-group LR intervention (tests M2 vs M1)
4. Optional: NTK width sweep if MVE results are ambiguous

This is implementable with ~20-30 GPU-hours total. The hypothesis is technically testable.

**Key Points:**
- Group-conditional Hessian at initialization is feasible (same method as h-c1)
- Per-group learning rates are a pragmatic alternative to noise injection for testing M2
- NTK width sweep feasible but expensive; start with 2 extreme widths
- MVE: ~20-30 GPU-hours to test all three competing models

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally looking like a controlled scientific contest instead of a storytelling exercise.

Dr. Nova, your differential convergence story is sharper than the earlier "misalignment causes everything" narrative. But here's where it can still break down: you are implicitly assuming that gradient norm decay for the majority reflects *true basin convergence* rather than simple loss scaling due to class frequency. If the majority loss is lower because it is overrepresented, its gradient norm may shrink faster purely due to empirical risk weighting—not curvature flattening. What would convince me is this: normalize each group's loss by its sample count and track *per-sample* gradient norms. If the decay persists after normalization, then we're talking about geometry. If it vanishes, then this is just weighting arithmetic.

Prof. Vera's M1/M2/M3 separation is exactly the right structure. But I want stricter temporal diagnostics. "Precedes" is vague. Compute cross-correlations:  
$$\tau_{r \to SR} = \arg\max_\tau \text{Corr}(r_t, SR_{t+\tau}), \quad \tau_{\cos \to SR} = \arg\max_\tau \text{Corr}(\cos_t, SR_{t+\tau})$$
If M2 is correct, $\tau_{r \to SR} > 0$ and statistically significant, while $\tau_{\cos \to SR} \approx 0$ or negative. If M1 is correct, the opposite. I don't want eyeballed epoch plots; I want lag structure with confidence intervals across seeds. Otherwise reviewers will say "these curves move together—so what?"

Now, on intrinsic curvature (M3): computing $\text{SR}_0$ is necessary but not sufficient. Random initialization induces symmetry, but data geometry can still create immediate curvature asymmetry even before path dependence. So here's the stronger test: shuffle group labels while keeping inputs fixed. If SR₀ > 1 persists under label permutation, the effect is purely geometric. If it disappears, the signal depends on group semantics interacting with labels. That's the difference between "minority examples are inherently sharper" and "training creates sharpness." Right now, you haven't separated those.

Pax's per-group learning rate intervention is pragmatic, but it's also confounded. Changing learning rates alters both convergence speed *and* effective curvature traversal. If SR collapses under LR balancing, you still won't know whether it was variance or step-size asymmetry that mattered. A cleaner intervention is to equalize *effective update norms*: enforce  
$$\|\eta_{\text{maj}} \nabla L_{\text{maj}}\| \approx \|\eta_{\text{min}} \nabla L_{\text{min}}\|$$
through adaptive scaling. That isolates update energy rather than raw gradient magnitude. What would convince me is SR sensitivity to update-norm parity, not just learning-rate tweaks.

Finally, on the NTK sweep: I agree with Pax—start with two widths. But here's the non-negotiable condition. You must show that SR correlates with a measurable deviation from linearized dynamics, e.g., $\Delta_{\text{NTK}}$. If width increases and SR stays >1 while $\Delta_{\text{NTK}} \to 0$, your path-dependence story is dead. Don't just report "SR decreases slightly." I want a monotonic trend with statistical support. If you can demonstrate that SR → 1 as nonlinearity vanishes, and that lagged gradient-magnitude collapse predicts SR divergence *after ruling out initialization curvature*, then you've addressed my core objections.

You're close. But until you isolate weighting effects, quantify lag structure, and cleanly intervene on update energy, this remains an elegant correlation study—not a causal account. Tighten those screws.

**Key Points:**
- Normalize per-sample gradients and test update-norm parity to rule out trivial frequency-weighting effects.
- Use lagged cross-correlation with confidence intervals to distinguish M1 vs M2 temporally.
- Strengthen intrinsic curvature tests via label permutation and NTK deviation–SR monotonic scaling.

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess what has emerged and where this stands for the field.

**What makes this genuinely new (revisited):** We've evolved from a vague "orthogonality is the mechanism" to a **structured hypothesis competition** between three causal models (M1, M2, M3). This methodological clarity is itself a contribution. The field has many post-hoc explanations for SR > 1.0; what we're proposing is a **falsifiable test framework** that can eliminate competing explanations.

The key innovation is no longer "we found the mechanism" — it's "we designed the experiment that will find the mechanism." This is significant because:
1. **M1 vs M2** distinguishes gradient direction (misalignment) from gradient magnitude (convergence rate) as the operative variable
2. **M3** rules out the null hypothesis that curvature disparity is intrinsic to data geometry
3. **The NTK control** separates nonlinear path dependence from linearized dynamics

This matters because current interventions (Group DRO, JTT, last-layer retraining) are designed without knowing which model is correct. If M2 is correct, interventions should target **convergence rate parity** (e.g., per-group learning rates). If M1 is correct, interventions should target **gradient alignment** (e.g., projection regularization). If M3 is correct, the problem is inherent to data geometry and no training intervention can fix it.

**Broader impact:** The lagged cross-correlation methodology Prof. Rex proposes could become a standard diagnostic for training dynamics analysis. Currently, papers show epoch curves and eyeball "this happened before that." A rigorous lag analysis with confidence intervals would elevate the field's standards.

**What's still missing for maximal impact:** We haven't connected this to worst-group accuracy. SR > 1.0 is an intermediate observation. The causal chain should extend to: $\text{Mechanism} \to \text{SR > 1} \to \text{Worse Minority Loss} \to \text{Lower WGA}$. If we can show that the intervention (update-norm parity, gradient coupling) that reduces SR also improves WGA, we close the loop from mechanism to outcome.

**Key Points:**
- Contribution has shifted from "we found the mechanism" to "we designed the definitive test framework"
- M1/M2/M3 competition has direct implications for which intervention strategy is appropriate
- Lag analysis methodology could become a new standard for training dynamics research
- Need to extend causal chain to worst-group accuracy for full practical impact

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now close to a properly adversarial design. Let me tighten the causal structure further. Dr. Rex is correct: without isolating weighting arithmetic from geometric convergence, M2 remains underdetermined. Therefore, I propose we define the *per-sample gradient norm*  
$$\tilde{r}_t = \frac{\|\nabla L_{\text{maj}}^t\|/n_{\text{maj}}}{\|\nabla L_{\text{min}}^t\|/n_{\text{min}}}$$  
and treat collapse as $\tilde{r}_t < 0.5 \tilde{r}_0$ sustained for 5 epochs. If M2 is genuinely about differential convergence speed rather than frequency weighting, this normalized ratio must still decay prior to SR divergence. If the effect vanishes after normalization, the hypothesis reduces to trivial empirical risk scaling. That would disprove the geometric interpretation.

On temporal ordering: I agree that visual inspection is unacceptable. We will compute lagged cross-correlations as proposed, but with pre-registered significance criteria. For each seed, estimate  
$$\tau_{r \to SR}, \quad \tau_{\cos \to SR}$$  
via maximum cross-correlation over $\tau \in [-5, +5]$ epochs. Then test across seeds whether $\mathbb{E}[\tau_{r \to SR}] > 0$ with 95% CI excluding zero. M2 predicts strictly positive lag; M1 predicts the same for $\tau_{\cos \to SR}$. If both lags are indistinguishable from zero, neither directional hypothesis holds — SR may simply co-evolve with gradients rather than being caused by them. That outcome must remain admissible.

Regarding the intervention: per-group learning rates are insufficient unless they enforce *update-norm parity*, as Rex notes. Therefore define adaptive scalars $\alpha_g^t$ such that  
$$\|\alpha_{\text{maj}}^t \eta \nabla L_{\text{maj}}^t\| = \|\alpha_{\text{min}}^t \eta \nabla L_{\text{min}}^t\|$$  
at each epoch checkpoint (or minibatch average). This isolates update energy from gradient magnitude. The falsifiable prediction under M2 is precise: enforcing update-norm parity should prevent $\tilde{r}_t$ collapse and attenuate or eliminate SR divergence (SR ≤ 1.1 sustained). If SR remains >1.2 despite parity, differential convergence is not the primary driver. That would substantially weaken M2.

For intrinsic curvature (M3), I will insist on two controls: (1) compute $\text{SR}_0$ with confidence intervals; (2) repeat with shuffled group labels while preserving input-label pairs. If $\text{SR}_0 > 1$ persists under permutation, the effect is geometric and independent of minority semantics. If it disappears, curvature asymmetry requires meaningful group structure interacting with labels. This is the cleanest separation between data geometry and training-induced specialization.

Finally, Dr. Sage is correct that SR is an intermediate variable. We must define a quantitative mediation test: does reducing SR via update-norm parity produce statistically significant improvement in worst-group accuracy (WGA)? Pre-register: ΔSR ≥ −0.2 must correspond to ΔWGA ≥ +2 percentage points (95% CI excluding zero). If SR manipulation fails to affect WGA, then SR is epiphenomenal rather than causal. That would invalidate the broader claim.

If these normalization controls, lag analyses, permutation tests, update-parity interventions, and WGA mediation checks all align, the hypothesis will have survived genuine attempts at disproof. Only then would I consider saying: this meets my standards.

**Key Points:**
- Normalize per-sample gradient norms and require pre-registered lag significance to distinguish causal ordering (M1 vs M2).
- Enforce adaptive update-norm parity as a clean intervention; predict SR attenuation if differential convergence is causal.
- Use initialization + label permutation controls and require SR→WGA mediation to rule out intrinsic curvature and epiphenomenal explanations.

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES! Now THAT's stronger! Let me synthesize what has emerged into a unified, defensible hypothesis with clear structure.

**EMERGED HYPOTHESIS: Differential Convergence Rate (DCR) Mechanism**

**Core Claim (Under-If-Then-Because):**
Under ERM training on group-imbalanced data, if majority groups converge faster (lower per-sample gradient norms earlier), then minority groups maintain higher local curvature (SR > 1.0), because majority-dominated updates smooth curvature only in majority-relevant parameter directions, leaving minority-relevant directions untraversed and sharp.

**Causal Chain:**
$$\text{Sample Imbalance} \xrightarrow{\text{gradient dominance}} \text{Differential Convergence} \xrightarrow{\text{path dependence}} \text{SR > 1.0} \xrightarrow{\text{higher minority loss}} \text{Lower WGA}$$

**Competing Models to Rule Out:**
- **M1 (Gradient Misalignment):** Cosine collapse causes SR. Falsified if $\tau_{\cos \to SR} \leq 0$.
- **M2 (Differential Convergence):** Per-sample norm ratio collapse causes SR. Validated if $\tau_{r \to SR} > 0$ with CI excluding zero.
- **M3 (Intrinsic Curvature):** SR exists at initialization. Falsified if $\text{SR}_0 \approx 1$ and label permutation eliminates effect.

**Testable Predictions:**

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Per-sample gradient ratio $\tilde{r}_t$ decays before SR diverges | $\tau_{r \to SR} > 0$, 95% CI excludes 0 | $\tau_{r \to SR} \leq 0$ |
| P2 | Update-norm parity attenuates SR | SR ≤ 1.1 under parity vs SR > 1.2 baseline | SR unchanged |
| P3 | SR ≈ 1 at initialization | SR₀ ∈ [0.9, 1.1], 95% CI includes 1.0 | SR₀ > 1.1 significantly |
| P4 | SR reduction improves WGA | ΔSR ≤ -0.2 → ΔWGA ≥ +2pp | No correlation |
| P5 | SR → 1 as NTK regime approached | Monotonic SR decrease with width | SR stable across widths |

**Experimental Design (MVE):**
1. Baseline: Train ResNet-50 on Waterbirds, track $\cos_t$, $\tilde{r}_t$, SR, WGA per epoch
2. Initialize: Compute SR₀ at random init + label permutation control
3. Intervention: Apply adaptive update-norm parity, compare SR/WGA trajectories
4. NTK: Two widths (standard, 4×) to check SR scaling
5. Analysis: Lagged cross-correlation with pre-registered thresholds

**What This Addresses from Failure Records:**
- Does NOT assume shared Hessian eigenspaces (h-c1 lesson)
- Does NOT assume CKA inversion (h-e1 lesson)
- Does NOT assume background attribution (h-e1 run2 lesson)
- EXPLAINS why minority has higher curvature (SR > 1.0 validated)
- EXPLAINS eigenspace orthogonality as consequence, not mechanism

**Key Points:**
- DCR hypothesis: sample imbalance → differential convergence → SR > 1.0 → lower WGA
- Five pre-registered predictions with explicit success/falsification criteria
- MVE: ~20-30 GPU-hours, addresses all M1/M2/M3 alternatives
- Directly avoids all failure modes from previous hypotheses

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The DCR mechanism reframes orthogonality from a problem to a symptom, shifting the intervention paradigm from post-hoc correction to early gradient steering. The three-model competition (M1/M2/M3) is a methodological innovation that could become standard practice.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Five pre-registered predictions with explicit success/falsification criteria. Lagged cross-correlation with confidence intervals provides rigorous temporal ordering tests. The update-norm parity intervention isolates the operative variable cleanly.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Bridges theoretical (LaBonte 2026) and empirical (Kirichenko 2022) findings. Direct implications for intervention strategy: if M2 is correct, convergence rate parity is the lever. Extends to foundation models, fairness, and transfer learning.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** MVE requires ~20-30 GPU-hours. All metrics (SR, gradient norms, cosine similarity) are computable with existing tools (PyHessian, standard PyTorch). No new infrastructure needed. Pragmatic path: start with 2 NTK widths, fill in if results ambiguous.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The **Differential Convergence Rate (DCR) Mechanism** explains why minority groups maintain higher curvature (SR > 1.0) during ERM training: majority groups, dominating the gradient, converge to flat basins faster, while minority groups, with higher gradient variance from undersampling, remain in sharp regions. This isn't mysterious orthogonality — it's path dependence in a non-convex landscape.

The hypothesis predicts: (1) per-sample gradient ratio decay precedes SR divergence, (2) update-norm parity intervention attenuates SR and improves worst-group accuracy, (3) SR ≈ 1 at initialization (ruling out intrinsic curvature), (4) SR → 1 in NTK regime (confirming nonlinear path dependence). Each prediction has explicit falsification criteria.

The experimental design tests three competing models: M1 (gradient misalignment), M2 (differential convergence, our hypothesis), M3 (intrinsic curvature). Lag analysis with confidence intervals distinguishes M1 vs M2; initialization and permutation controls rule out M3; NTK width scaling validates nonlinear path dependence.

This hypothesis directly avoids failure modes from h-c1 (no shared eigenspace assumption), h-e1 (no CKA/attribution assumptions), and h-m1 (explains, rather than assumes, gradient dynamics). It builds on the validated finding that SR > 1.0 is real and explains it mechanistically.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Per-sample gradient normalization must be implemented carefully — averaging vs summing matters.
- **Concern 2:** Update-norm parity may degrade majority accuracy; need to monitor both WGA and average accuracy.
- **Mitigation Strategy:** Pre-register acceptable accuracy degradation threshold (e.g., ≤2% average accuracy drop). Use Pareto frontier analysis if trade-off emerges.

---

## Emerged Hypothesis Summary

### Core Statement
Under ERM training on group-imbalanced data, if majority groups converge faster (lower per-sample gradient norms earlier), then minority groups maintain higher local curvature (SR > 1.0), because majority-dominated updates smooth curvature only in majority-relevant parameter directions, leaving minority-relevant directions untraversed and sharp.

### Causal Mechanism
1. Sample imbalance causes majority gradient dominance
2. Majority-dominated updates traverse majority-relevant parameter directions
3. Majority loss landscape flattens (low curvature) through repeated traversal
4. Minority-relevant directions remain untraversed and sharp (high curvature)
5. Result: SR > 1.0, higher minority loss, lower worst-group accuracy

### Variables
- **Independent Variable:** Sample frequency ratio (majority/minority)
- **Dependent Variable (Primary):** Sharpness Ratio SR = λ_max(H_min)/λ_max(H_maj)
- **Dependent Variable (Secondary):** Worst-group accuracy (WGA)
- **Controlled:** Architecture (ResNet-50), learning rate schedule, dataset (Waterbirds)

### Key Assumptions
- A1: Per-sample gradient norms reflect true convergence, not just frequency weighting
- A2: SR > 1 at initialization is negligible (path dependence required)
- A3: Minority-relevant parameter directions are not traversed by majority updates
- A4: Update-norm parity is achievable without destroying discriminative structure
- A5: SR mediates the relationship between gradient dynamics and WGA

### Null Hypothesis
There is no significant difference in per-sample gradient norm decay rates between majority and minority groups, and SR > 1.0 is an intrinsic property of data geometry unrelated to training dynamics.

### Predictions
- P1: Per-sample gradient ratio τ_r→SR > 0 (decay precedes SR divergence)
- P2: Update-norm parity → SR ≤ 1.1 (vs SR > 1.2 baseline)
- P3: SR₀ ∈ [0.9, 1.1] at initialization
- P4: ΔSR ≤ -0.2 → ΔWGA ≥ +2pp
- P5: SR → 1 as network width increases (NTK regime)

### Novelty
This hypothesis explains why SR > 1.0 arises from training dynamics, not just observes it. It provides the mechanistic bridge between theoretical work (LaBonte 2026) showing SGD learns spurious features first and empirical work (Kirichenko 2022) showing core features exist but are suppressed. The intervention paradigm shifts from post-hoc correction to early gradient steering.

### Scope & Boundaries
- Applies to: ERM training on class-imbalanced datasets with group structure
- Does not apply to: Balanced datasets, non-neural methods, NTK regime
- Limitations: Tested on Waterbirds; generalization to CelebA/ColorMNIST requires additional validation

### Experimental Setup
- Dataset: Waterbirds (primary), CelebA (validation)
- Model: ResNet-50 pretrained on ImageNet
- Metrics: SR, per-sample gradient norms, cosine similarity, WGA, average accuracy
- Tools: PyHessian for Hessian eigenvalues, standard PyTorch for gradients

### Related Work & Baselines
- Baseline 1: Standard ERM (expect SR > 1.2, WGA ~75%)
- Baseline 2: Group DRO (expect improved WGA, unknown SR trajectory)
- Baseline 3: Last-layer retraining (post-hoc, doesn't address training dynamics)

### Phase 2B Readiness Seeds
- MUST_WORK gate: P1 (temporal ordering) and P3 (initialization check)
- If P1 fails: M2 falsified, reconsider M1 or M3
- If P3 fails: Intrinsic curvature dominates, training intervention futile

### Established Facts
- SR > 1.0 confirmed from h-e1 (range 2.32-4.17)
- Group Hessian eigenspaces are near-orthogonal (~88.5°) from h-c1
- Minority has more concentrated gradients (GCDR = 0.175) from h-m1
- CKA species > environment throughout training (no inversion)
- GradCAM shows foreground attribution, not background

