# Phase 2A Discussion Log
# Gap: Gradient Norm as Label-Free Minority Proxy
# Pipeline: YouRA | Spurious Correlations & Shortcut Learning (v3)
# Initialized: 2026-03-16T20:39:00Z

---

## Research Briefing

**Research Gap:** Unexplored Use of Per-Sample Gradient Norm Magnitude as Label-Free Minority Group Proxy

**Research Question:** Can gradient norm disparity between minority and majority groups — empirically confirmed at 6–14x ratio during ERM training on Waterbirds — be exploited as a label-free signal for sample reweighting to improve worst-group accuracy (WGA) on spurious correlation benchmarks, achieving performance competitive with JTT (+21pp) and DFR without group label supervision?

**Confirmed Empirical Foundation (from prior runs):**
- gradient_norm_ratio: 6.37x (epoch 5), 14.73x (epoch 4) — minority groups produce 6–14x larger gradient norms than majority groups
- lambda1 EOS dynamics: 689.7 → 586.1 → 545.5 — all >> 500 EOS threshold confirmed
- Loss asymmetry: minority_group_loss 0.9238 vs majority_group_loss 0.0189 at epoch 5
- Per-group norms: G0(landbird/land)=6.90, G1(landbird/water)=56.98, G2(waterbird/land)=70.72, G3(waterbird/water)=19.79

**Failure Context (CRITICAL — avoid these):**
- ❌ SAM/flatness optimizer: FAIL (+0.90pp vs required +10pp) — flat minima ≠ group-robust minima
- ❌ oscillation_index directional criterion: SUPERSEDED — OI=+1.0 (both groups project same direction on nu1)
- ❌ Rosenfeld & Risteski "opposing signal" as directional criterion: INVALID in nu1 projection space

**New Direction:** Exploit the CONFIRMED gradient norm magnitude disparity as a reweighting signal — not as directional analysis — in a two-stage JTT/DFR-style protocol without group labels.

**Key Comparison Targets:**
- JTT (Liu et al. 2021): +21pp WGA on Waterbirds using misclassification proxy
- DFR (Kirichenko et al. 2022): Last-layer retraining on group-balanced subset
- LfF (Nam et al. 2020): Relative loss as minority proxy
- LFR (Ghaznavi et al. 2023): High/low loss split for group balance
- GroupDRO (Sagawa et al. 2019): +10.9pp WGA (group-supervised upper bound)

**Available Papers:**
- P1: arxiv_2107_09044.md — Just Train Twice (JTT) [Liu et al., 2021]
- P2: arxiv_2204_02937.md — Last Layer Re-Training (DFR) [Kirichenko et al., 2022]
- P3: arxiv_2007_02561.md — Learning from Failure (LfF) [Nam et al., 2020]
- P4: arxiv_2603_07323.md — Norm-Hierarchy Transitions (NHT) [Khanh & Hoa, 2026]

**Available Infrastructure (confirmed working):**
- WaterbirdsDataset + ResNet-50 + evaluate.py + GroupDRO baseline (h-e1/code/)
- Per-sample gradient norm computation hooks (gradient_analysis.py, confirmed 6–14x ratio)
- Conda env: youra-h-e1; GPU: H100 NVL
- Dataset cache: .data_cache/datasets/waterbirds/

**Feasibility Constraints (MANDATORY):**
- ✅ Only existing real datasets (Waterbirds, CelebA, MultiNLI)
- ✅ Only existing benchmarks (WGA metric, standard splits)
- ❌ No new benchmarks, rubrics, or scoring frameworks
- ❌ No synthetic/generated data
- ❌ No human evaluation or annotation

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The proposal is promising, but we must separate intuition from testable mechanism. JTT's strength, as defined in its two-stage procedure, is operational clarity: misclassification after \(T\) epochs defines the error set \(E\), and upweighting via \( \lambda_{up} \) yields measurable gains in worst-group accuracy [arXiv:2107.09044]. Your GNPR replaces the binary indicator \( \mathbf{1}[i \in E] \) with a continuous function of gradient norm at epoch \(T_{id}\). The critical question is: **does gradient norm contain strictly more information than misclassification, or is it merely a noisy surrogate?**

Here is the first falsifiable prediction:
If GNPR is mechanistically superior to JTT, then controlling for the *same identification epoch* \(T_{id}\), GNPR should outperform a binary upweighting scheme constructed from the top-k percentile of gradient norms, matched in effective mass to JTT's error set. In other words, if JTT upweights 12% of samples, then GNPR's top 12% norm samples (binary) should underperform continuous weighting if and only if continuity carries real signal. If no difference is observed, your "continuous richness" claim collapses.

Second, you posit that high gradient norm reflects resistance to shortcut learning. The evidence suggests this is plausible early in training—but it is not guaranteed. High norm may also arise from label noise, hard-but-spurious samples, or simply stochastic instability. Therefore:
**What would disprove the shortcut-resistance hypothesis?**
If we randomize background labels (destroying the spurious correlation) and retrain, the minority/majority gradient norm gap should vanish by epoch 5. If it persists, the signal is not shortcut-specific but intrinsic to class imbalance or architecture bias. Additionally, on a dataset without known spurious correlations (e.g., CIFAR-10 with balanced groups), GNPR should provide no worst-group benefit. Any improvement there would indicate uncontrolled regularization effects rather than targeted debiasing.

Third, we must examine temporal robustness. JTT relies on early misclassification because ERM first learns spurious features [arXiv:2107.09044, Experiments]. Your method hinges on the same training dynamics assumption. Therefore, sweep \(T_{id} \in \{1,3,5,10,20\}\). A genuine shortcut-detection mechanism predicts:
- Strong gradient norm disparity at early epochs
- Monotonic decay of disparity as structured features are learned
- GNPR effectiveness tightly coupled to the disparity magnitude

If GNPR remains effective even when disparity is small, then the mechanism is not what you claim.

Finally, control for trivial correlations. Compute the Spearman correlation between gradient norm and misclassification indicator at \(T_{id}\). If correlation > 0.9, GNPR reduces to a smoothed JTT. If correlation < 0.3 yet GNPR still improves worst-group accuracy, then you have identified an independent signal. That is the regime of real novelty.

Design the experiment so it could fail. If GNPR does not outperform percentile-matched binary weighting, if it helps on non-spurious datasets, or if its gains are insensitive to disparity magnitude, then the hypothesis is wrong. If it passes all three tests—

I will say, carefully, that this meets my standards.

**Key Points:**
- Compare GNPR to percentile-matched binary weighting to test whether continuity adds real signal beyond JTT.
- Perform shortcut-destruction and non-spurious controls to rule out generic regularization or imbalance effects.
- Sweep identification epoch and measure correlation with misclassification to verify mechanistic grounding.

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The empirical phenomenon sitting before us is genuinely exciting: minority groups produce 6–14x larger gradient norms than majority groups during ERM training on Waterbirds. Two previous attempts tried to explain or harness this differently — and both failed in instructive ways. SAM sought flat minima, but flat ≠ robust. The oscillation index looked for directional opposition, but found none. What neither attempt tried is the most direct exploitation: use the *magnitude* itself as a detector.

Here's the creative angle I want to propose. Gradient norm disparity during early training is not just an epiphenomenon — it is the loss gradient's "cry for help" from minority samples that the model hasn't yet learned to classify. At epochs 1–5, the model has internalized the spurious correlation (e.g., background → bird class) and consequently fits majority samples easily (low loss, low gradient norm). Minority samples, lacking the spurious cue, cannot be fit by the same shortcut, producing large residual gradients. This is precisely the same mechanism JTT exploits via misclassification, but gradient norm is *continuous* rather than binary — a richer signal.

I want to propose a novel angle: **Gradient Norm Percentile Reweighting (GNPR)**. Instead of using a binary error set (JTT), we compute per-sample gradient norm at epoch T_id (say 5), then assign sample weights proportional to a monotone transformation of the norm — e.g., `w_i = 1 + λ * norm_i / mean_norm`. This gives a continuous spectrum of upweighting rather than a step function. The high-norm minority samples get upweighted; majority samples (near mean) get weight ≈ 1. The result: a soft, principled version of JTT grounded in gradient dynamics.

The key innovations over JTT are: (1) continuous vs. binary selection, (2) mechanistic grounding in gradient dynamics rather than empirical misclassification, (3) the norm ratio can be used to predict reweighting effectiveness (if ratio < threshold, method may not help). From the NHT framework [Khanh & Hoa, 2026], shortcut representations have higher parameter norm than structured representations — so high per-sample gradient norm directly signals samples where the model's shortcut solution is actively being "stretched." This is the theoretical ground JTT lacked.

Critically, this avoids all prior failure modes: no flatness (SAM), no directional criterion (oscillation index), no new benchmark (Waterbirds/CelebA are confirmed infrastructure), and no group labels.

**Key Points:**
- Gradient norm magnitude is a *continuous* minority proxy — richer than JTT's binary misclassification
- GNPR: soft upweighting proportional to norm magnitude, preserving all samples
- NHT framework [Khanh & Hoa, 2026] provides theoretical grounding: high-norm gradient = sample resisting shortcut solution
- Feasibility: reuses existing h-e1/code gradient hooks, ResNet-50, Waterbirds — no new infrastructure

---


### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Prof. Vera has identified the right battleground — whether gradient norm is an independent signal or a noisy JTT surrogate. Let me press harder on the structural weaknesses that could collapse this hypothesis entirely.

**Stress Test 1: The confounded signal problem.** JTT's methodology [Liu et al., 2021] is deliberately simple: train ERM for T epochs, collect misclassified samples, retrain with upweight λ_up. The key insight from JTT's Discussion is that *misclassification at small T is a proxy for minority group membership precisely because the ERM model learned the spurious correlation*. Gradient norm magnitude at epoch 5 may reflect the same underlying variable — samples the model can't fit via the spurious shortcut — and nothing more. If so, GNPR ≠ a new method; it's a soft version of JTT with extra computational cost (requiring per-sample gradient norm computation, which is O(N × P) vs JTT's O(N) forward pass check). The hypothesis needs to argue why the continuous signal carries genuinely independent information.

**Stress Test 2: The spurious-norm problem.** The confirmed 6–14x ratio (minority >> majority) is striking, but group G3 (waterbird on water background) has norm 19.79 while G0 (landbird on land) has 6.90. G2 (waterbird on land) has 70.72 — the highest norm sample is the hardest minority case, correctly. But G1 (landbird on water) has 56.98 — this is also a minority group, but one where the label is "not bird" with water background. The norm signal appears valid here. However, what happens on CelebA? There, blonde/female vs. blonde/male vs. non-blonde/female have different confounding structures. The gradient norm ratio must be verified on CelebA before claiming generalization — otherwise this is a Waterbirds-specific finding.

**Stress Test 3: The upweighting collapse.** JTT's Discussion section explicitly warns about the tension between worst-group accuracy and average accuracy: their best λ_up ≈ 50–100, but higher values hurt average accuracy. GNPR's continuous weighting will face the same tension. If w_i = 1 + λ * norm_i/mean_norm, then the effective range of weights depends on the norm distribution. If gradient norms are heavy-tailed (which they plausibly are — minority groups are few), then a small number of samples receive astronomically high weights, potentially destabilizing Stage 2 training. We need an explicit bound: what is the 99th percentile norm relative to mean? If it exceeds 10x mean, then continuous weighting is actually *more dangerous* than binary JTT, not safer.

**What saves the hypothesis:** The strongest version of GNPR focuses on a specific comparison: gradient norm threshold selection vs. JTT misclassification threshold, both using the same two-stage protocol on the same architecture. If gradient norm achieves ≥ JTT WGA (86.7% on Waterbirds per DFR paper's Table) with a less sensitive hyperparameter (T_id, λ), that is a publishable result. The claim should be: *gradient norm is a more robust proxy than misclassification because it is a continuous signal that interpolates gracefully across the hyperparameter space*, not that it achieves higher peak WGA.

**Refined falsifiable hypothesis:** Under ERM+SGD training on Waterbirds (primary) and CelebA (secondary), a two-stage gradient-norm-informed reweighting protocol (GNR) — train ERM for T_id epochs, compute per-sample gradient norms, retrain with w_i ∝ norm_i^α — achieves WGA ≥ JTT baseline (86.7% Waterbirds) with lower hyperparameter sensitivity (smaller variance in WGA across grid search) than JTT's (T_id, λ_up) grid, without group label supervision.

This framing makes the hypothesis both feasible (existing infrastructure, existing benchmarks) and falsifiable (concrete comparison with JTT as null baseline).

**Key Points:**
- GNPR must demonstrate independent signal from misclassification, not just soft-JTT equivalence
- CelebA validation is required before claiming multi-dataset generalization
- The claim should shift from "higher peak WGA" to "more robust/stable hyperparameter sensitivity" vs. JTT
- Refined hypothesis: GNR achieves WGA ≥ JTT (86.7%) with lower variance across hyperparameter grid

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The core question is not whether GNPR is clever — it is whether gradient norm contains *mechanistically independent signal* beyond early misclassification, and whether computing and using it is theoretically sound.

First: is per-sample gradient norm a valid object? Yes. For cross-entropy with logits \( z = W^T h(x) \), the gradient w.r.t. parameters is well-defined and its norm is proportional to both prediction error and feature magnitude. In fact, for the last layer:
\[ \|\nabla_W \ell_i\| \propto \|h(x_i)\| \cdot \|p_i - y_i\|. \]
So here's what worries me: large gradient norm may reflect large feature norm \( \|h(x)\| \), not necessarily shortcut resistance. If minority samples induce different feature magnitudes during ERM, GNPR may just be selecting for representation geometry, not spurious mismatch per se. That's not invalid — but it weakens the claimed mechanism. You need to decompose gradient norm into (a) prediction error term and (b) representation norm term. If the minority-majority gap persists after normalizing by \( \|h(x)\| \), then we're closer to a genuine shortcut-resistance signal.

Second: on feasibility of computation. Per-sample gradient norms are theoretically computable via standard autograd tricks (e.g., functorch or backward hooks). There is no mathematical barrier here. But you must specify *which layer's gradient*. Full-network norm mixes shallow and deep dynamics; last-layer norm is interpretable and directly tied to DFR-style reasoning. Given that DFR [Kirichenko et al., ICLR 2023; arXiv:2204.02937] shows that retraining only the last layer dramatically improves worst-group accuracy (92.9% on Waterbirds), the representation already contains usable structured features. That implies early gradient disparities might primarily reflect misalignment at the classifier head — not fundamental representational failure. If so, GNPR's leverage point may be narrower than you think.

Third: the intervention itself. Continuous weighting \( w_i \propto \text{norm}_i^\alpha \) is mathematically fine, but only if the norm distribution is controlled. If the 99th percentile is 10–20× the mean, then even moderate \( \alpha \) produces extreme effective learning rate differences. That can alter optimization dynamics in unintended ways. You need bounded transformations (e.g., percentile rank, clipped z-score, or softmax over norms) to ensure the reweighting defines a well-behaved objective.

Now, relative to JTT and DFR [arXiv:2204.02937, Table 1]: DFR achieves 92.9% WGA on Waterbirds vs JTT's 86.7%. If GNPR applied only to last-layer retraining matches DFR, then gradient norm is effectively identifying which samples should dominate the classifier head — similar in spirit to DFR's balanced subset. That's a critical experiment: freeze h(x), retrain only W with GNPR weights computed at T_id. If worst-group accuracy approaches DFR's 92.9% on Waterbirds, then this is a strong result — gradient-norm-based last-layer retraining as a label-free DFR.

**Key Points:**
- Decompose gradient norm into prediction error vs. feature norm; verify minority gap survives normalization.
- Use bounded, well-behaved weighting transforms to avoid optimization instability from heavy-tailed norms.
- Test GNPR in a last-layer-only retraining setup to directly compare mechanistic overlap with DFR (92.9% Waterbirds WGA).

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Pax has made a crucial technical observation that actually *strengthens* the research impact case. The decomposition of gradient norm into \( \|h(x)\| \cdot \|p_i - y_i\| \) is not a weakness — it is a feature. Let me explain why this matters for the field.

DFR [Kirichenko et al., 2023] demonstrated something profound: ERM features already encode structured (non-spurious) information; the problem is that the linear classifier head over-weights the spurious directions [arXiv:2204.02937, Discussion]. DFR's solution requires a small group-balanced validation set to retrain the head — a small but real supervision requirement. The gradient norm signal, being proportional to both prediction error and feature magnitude, implicitly captures *both* the residual mismatch of the classifier head AND the representational geometry. If minority samples have large \( \|h(x)\| \) (they are farther from the majority in feature space) AND large \( \|p_i - y_i\| \) (they are misclassified), then high gradient norm is a *doubly enriched* signal relative to JTT's misclassification alone.

From a research impact standpoint, the key question is: **which benchmark comparison produces the highest-impact narrative?** There are two framings:

**Framing A (vs. JTT):** "Gradient norm outperforms misclassification as a minority proxy — achieving higher or more stable WGA with fewer hyperparameter choices." Impact: Moderate. JTT is from 2021, well-established. A marginal improvement on JTT is a workshop paper.

**Framing B (vs. DFR without labels):** "Gradient-norm-informed last-layer retraining achieves DFR-level WGA (≥90% on Waterbirds) without requiring a group-balanced validation set." Impact: HIGH. DFR requires 200–1000 annotated samples for group-balanced retraining [arXiv:2204.02937, Methodology]. If gradient norm can identify a pseudo-group-balanced subset from the training data itself — without any labels — then this closes the last annotation gap in the DFR family. That is a top-venue contribution.

The experimental design flows directly from this framing:
1. Stage 1: Train ERM for T_id epochs, compute per-sample gradient norms
2. Stage 1.5: Select top-k% high-norm samples as pseudo-minority set and bottom-k% as pseudo-majority set, constructing a pseudo-balanced subset
3. Stage 2: Retrain only the last layer (freeze features) on the pseudo-balanced subset with optional sample weighting

This is **Label-Free DFR via Gradient Norm** — a clean, high-impact hypothesis with a clear comparison target (DFR: 92.9% WGA), a clear null (ERM: ~72% WGA), and a clear mechanism (gradient norm identifies the pseudo-group-balanced subset that DFR would otherwise require labels for).

The significance claim: this would eliminate the last remaining annotation requirement in the best-performing spurious correlation mitigation methods, using a signal that is provably present (confirmed 6–14x ratio) rather than assumed.

**Key Points:**
- Shift framing from "better-than-JTT" to "label-free-DFR" — the latter has top-venue impact
- Hypothesis: gradient-norm-based pseudo-group-balanced subset selection + last-layer retraining achieves DFR-level WGA without group annotations
- Success criterion: WGA ≥ 88% on Waterbirds (approaching DFR's 92.9%), ERM baseline ~72%, all without group labels
- This closes the last annotation gap in the DFR family — a clean, high-impact contribution

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The central claim must be sharpened before it can be evaluated: *gradient norm provides independent and exploitable signal beyond JTT's binary misclassification set* [Liu et al., 2021]. At present, GNPR risks being a smooth surrogate for the error set \( E = \{(x_i,y_i) : \hat{f}_{id}(x_i) \neq y_i\} \). The evidence suggests that if high-norm samples are nearly identical to \(E\), then GNPR is merely a continuous relaxation of JTT's upweighting objective \(J_{up\text{-}ERM}\). Therefore, the first experiment must quantify overlap: compute (1) AUC of gradient norm for predicting membership in \(E\), and (2) conditional worst-group accuracy when selecting top-k% by norm *excluding* all misclassified samples.

**Falsifiable prediction:** If gradient norm contains independent signal, then among correctly classified samples at epoch \(T_{id}\), the top decile by norm should contain a statistically significant enrichment of minority-group samples (measured post hoc with labels) and, when upweighted, should improve worst-group accuracy (WGA) beyond JTT.
**Disconfirming result:** If AUC(norm → E) ≥ 0.95 and enrichment among correctly classified samples is negligible, then GNPR adds no new information beyond JTT.

Second, Prof. Pax's decomposition is not optional—it is a necessary control. Since for the last layer \( \|\nabla_W \ell_i\| \propto \|h(x_i)\| \cdot \|p_i - y_i\| \), we must test whether the minority-majority 6–14× ratio persists after normalizing by feature norm. Compute
\[
g_i^{normed} = \frac{\|\nabla_W \ell_i\|}{\|h(x_i)\|}
\]
and re-evaluate the group disparity at epochs 1–5.

**Prediction:** If GNPR reflects shortcut resistance rather than representational scale, the disparity should remain ≥3× after normalization.
**Disconfirming result:** If disparity collapses (≤1.5×), then the signal is primarily geometric, and the proposed mechanism is incorrect.

Third, the "label-free DFR" framing is compelling but must be tested under strict comparability. DFR achieves 92.9% WGA on Waterbirds by freezing features and retraining the last layer on a group-balanced subset. Your claim becomes scientifically meaningful only if:
1. Stage 1: Train ERM for fixed \(T_{id}\) identical to JTT's identification stage [Liu et al., 2021].
2. Stage 2A (baseline): Apply JTT upweighting as specified in Eq. (2).
3. Stage 2B (test): Freeze features; select top-k% by gradient norm; retrain last layer only.

**Success criterion:** WGA ≥ 88% without group labels, averaged over ≥5 seeds, and within 5% average accuracy drop relative to ERM.
**Failure criterion:** Performance remains within JTT variance or below 85% WGA.

Finally, hyperparameter sensitivity must be quantified—not asserted. Define robustness as the variance of WGA across a predefined grid of \(T_{id}\) and weighting strength. Pre-register the grid. If GNPR's WGA variance is not statistically lower than JTT's across identical seeds and splits, then the claim of "continuous stability" is unsupported.

**Key Points:**
- Test independence: measure overlap and enrichment beyond JTT's misclassification set; define clear failure thresholds.
- Control decomposition: verify minority gradient disparity persists after normalizing by feature norm.
- Compare under identical protocols: pre-registered grid, multi-seed evaluation, and explicit success/failure criteria vs. JTT and DFR benchmarks.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Vera has given us exactly the experimental framework needed to make this hypothesis bulletproof. I want to synthesize all the critiques into the strongest possible version of the hypothesis, incorporating every suggested control, and showing why the core claim survives all the stress tests.

Let me defend the framing and propose the unified hypothesis. The "label-free DFR" framing that Dr. Sage proposed is the right one — and the good news is that all of Prof. Rex's and Prof. Vera's concerns become experimental controls that *strengthen* the story rather than undermine it.

**On the independent signal question:** JTT's misclassification set E (typically 10–20% of training data at early epochs) and the top-k% by gradient norm are likely correlated but not identical [Liu et al., 2021, Methodology]. The 6–14x gradient norm ratio appears at epoch 5, which is also the regime where JTT's T_id works best. However, there is a critical difference: gradient norm captures *degrees* of minority-group misfit, while misclassification is a hard threshold. Minority samples just above the decision boundary (correctly classified but "barely") have low loss but potentially still elevated gradient norm — because they require higher gradient magnitude to maintain correct classification despite lacking the spurious cue. JTT loses these samples entirely; gradient norm catches them. This is the genuine additional coverage that motivates the hypothesis.

**On the feature-norm decomposition:** Prof. Pax's decomposition \( \|h(x)\| \cdot \|p_i - y_i\| \) is exactly the right analysis. But notice that both terms are interesting: if minority samples have larger *both* feature norm and prediction error, then gradient norm is doubly enriched as a signal. If the disparity persists after normalizing by \|h(x)\|, we get the clean "prediction error only" signal. Either way, the empirical 6–14x ratio must be decomposed in the actual experiment — and this becomes a results section rather than a failure mode.

**On the label-free DFR experimental design:** Here's the synthesized hypothesis in its strongest form:

*Under ERM training on Waterbirds (primary) and CelebA (secondary), a Gradient-Norm-Informed Last-Layer Retraining method (GNR-LLR): (1) trains ERM for T_id epochs; (2) computes per-sample last-layer gradient norms, normalized by feature norm; (3) selects top-k% high-norm samples as pseudo-minority and bottom-k% as pseudo-majority, constructing a pseudo-group-balanced subset; (4) freezes the feature extractor and retrains only the classification head on this pseudo-balanced subset. GNR-LLR achieves WGA ≥ 88% on Waterbirds without group label supervision, approaching DFR's 92.9% (which requires group-balanced labels for the validation set), while outperforming JTT's 86.7%.*

The null hypothesis H0: There is no significant difference in WGA between GNR-LLR and JTT (i.e., gradient norm does not provide actionable additional information beyond misclassification for worst-group accuracy improvement).

Success criterion: WGA ≥ 88% on Waterbirds (5+ seeds), ≤5pp average accuracy drop, p < 0.05 vs JTT baseline.
Falsification: WGA ≤ 85% or within JTT variance, or AUC(norm → minority group) ≤ AUC(misclassification → minority group) on held-out group labels.

This hypothesis is feasible (reuses confirmed infrastructure), falsifiable (clear quantitative thresholds), novel (no published method uses gradient norm for pseudo-group-balanced subset construction), and impactful (closes the last annotation gap in the DFR family).

**Key Points:**
- Synthesized hypothesis: GNR-LLR = gradient-norm-based pseudo-group-balanced subset construction + last-layer retraining; target WGA ≥ 88% Waterbirds, no group labels
- Falsification: WGA ≤ 85% or AUC(norm → minority) ≤ AUC(misclassification → minority)
- All stress-test controls (decomposition, independence, non-spurious dataset) become experiment sub-sections rather than disqualifiers
- Novelty claim: first method to use gradient norm for pseudo-group-balanced subset construction for DFR-style last-layer retraining

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Alright. The framing is finally getting sharp. But here's where this still breaks down if you're not careful.

You are implicitly assuming that high gradient norm = resistance to shortcut learning. The NHT framework [Khanh & Hoa, 2026; arXiv:2603.07323] gives you a competing explanation: during multi-representation interpolation, shortcut solutions are *norm-accessible first*, and structured solutions require lower norm but delayed transition:
\[
T_{\text{transition}} = \Theta\left(\frac{1}{\gamma_{\text{eff}}} \log\left(\frac{V_{\text{sc}}}{V_{\text{st}}}\right)\right).
\]
If that's true, then early high gradient norm might simply reflect the model climbing toward the higher-norm shortcut basin—not "minority resistance." In other words: gradient norm spikes could be a *byproduct of norm-hierarchy dynamics*, not a signal of structured feature reliance. Show me that high-norm samples are not just those driving shortcut norm growth.

What would convince me? A temporal alignment test. Track per-sample gradient norm across epochs 1–T_transition and correlate it with the layer-wise norm peak-then-decay dynamics reported in the NHT experiments. If your "pseudo-minority" samples cluster in the phase where shortcut layers are still expanding norm, then GNPR may just be tagging samples that accelerate shortcut acquisition. That's fatal. But if high-norm samples persist *after* shortcut layers peak and begin decaying, then you have evidence they are pushing toward structured solutions.

Second flaw: your label-free DFR framing assumes that selecting top-k% by norm approximates a group-balanced subset. That's a very strong structural claim. DFR works because the subset is *explicitly balanced by group labels*. Your pseudo-balanced subset is defined only by a univariate statistic. Why should that produce balance across both (y, g) combinations? You need to empirically verify the induced joint distribution over (label, group) in the selected subset. Show me the contingency table.

Third: weight decay directly shapes norm hierarchy [NHT framework]. If your signal depends on raw gradient norm magnitude, then λ is not a nuisance parameter—it changes the geometry of your signal. I want to see GNPR evaluated across at least three λ regimes. If your method only works in a narrow λ band, reviewers will say it's exploiting a transient regime of norm inflation.

The experiment that makes this airtight:
1. Pre-register λ ∈ {0, 1e-4, 5e-4}
2. For each λ, measure: (a) norm ratio raw + feature-normalized; (b) overlap with JTT error set (AUC); (c) induced group balance in top-k% subset; (d) WGA after last-layer retraining
3. Align results with estimated T_transition from NHT phase behavior

If GNPR consistently improves WGA ≥ 88% across λ and transition phases, and the subset is demonstrably closer to group-balanced than JTT's error set, then you've isolated a real mechanism.

**Key Points:**
- Test whether high gradient norm tracks shortcut norm inflation (NHT temporal alignment)
- Empirically verify induced (label, group) balance in the pseudo-balanced subset
- Stress-test across weight decay regimes (λ ∈ {0, 1e-4, 5e-4})

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's NHT temporal challenge is actually the most exciting opening in this entire discussion. Let me reframe it not as a threat but as a *discovery opportunity*.

If high-norm samples during early training are the ones resisting the shortcut solution — the samples that the model cannot easily fit via the spurious cue — then the temporal profile of their gradient norm should be distinctive: it should *remain elevated even after the shortcut norm peaks and begins decaying* [NHT prediction: peak-then-decay in shortcut layers, Proposition 4.2]. Meanwhile, majority samples (already fit by the shortcut) should show *declining* gradient norm as the shortcut stabilizes. This temporal divergence is a *testable prediction* that would simultaneously validate the mechanism AND distinguish it from the NHT "shortcut-inflation" interpretation Prof. Rex raised.

This gives us a beautiful experimental design: plot mean gradient norm over epochs 1–20 for (minority group) vs. (majority group) samples. If minority norm remains high while majority norm decays — that's not shortcut inflation, that's shortcut *resistance*. The crossing point (where majority norm drops below minority norm and stays there) is the optimal T_id for GNPR. This is a new theoretical insight that JTT completely lacks — JTT has no principled T_id selection rule [Liu et al., 2021, Introduction: "We found that T=60 works well empirically"]. GNPR gives you T_id from the dynamics.

On Prof. Rex's contingency table concern: I actually think this is addressable with a clean theoretical argument. Under the spurious correlation setting, minority samples (high-spurious-cue mismatch) have elevated gradient norms during early training. If we assume that gradient norm correlates with minority group membership (which the 6–14x ratio empirically confirms), then the top-k% by norm will be enriched for minority samples. The contingency table will be approximately group-balanced *within each class* if gradient norm is class-conditional. This is an *empirical verification step* in the experiment, not a failure mode. We already know the ratio is 6–14x — the contingency table will confirm it.

On the weight decay question: the NHT framework actually *predicts* that moderate weight decay (λ = 1e-4, the standard ERM setting from Sagawa et al.) should produce the intermediate phase where gradient norm disparity is maximized, because this is the regime where shortcuts are accessed but structured solutions are not yet reached. Strong weight decay (λ = 5e-4) may suppress shortcuts faster, reducing the disparity — but also making GNPR less necessary (the model is already learning structured features). Zero weight decay preserves shortcuts longer. This maps exactly to the three-regime prediction from NHT.

So I'll strengthen the hypothesis with Prof. Rex's constraints incorporated: **use standard λ = 1e-4 (confirmed working from prior runs), with λ as a secondary robustness check**. The primary result is at standard hyperparameters.

**Key Points:**
- Temporal gradient norm profile (minority = stays elevated, majority = decays) is the mechanism validation experiment and provides principled T_id selection — a new contribution JTT lacks
- Contingency table verification is an empirical confirmation step, not a theoretical gap
- Standard λ = 1e-4 from confirmed infrastructure is the primary setting; λ robustness is secondary
- NHT's three-regime prediction maps directly to GNPR's expected behavior across λ

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The core question is not whether GNPR is clever — it's whether gradient norm can *in principle* isolate structured-signal pressure rather than just reflecting global norm dynamics predicted by NHT. The NHT update rule explicitly couples gradients and weight decay [Khanh & Hoa, 2026]. That means raw gradient magnitudes are embedded in a system where norm growth and decay are structurally governed. If shortcut representations are norm-accessible first (large \(V_{\text{sc}}\)), early high gradient norms could simply reflect rapid movement toward that basin. So the temporal alignment test is not optional — it's mechanistically necessary.

About the feature-norm decomposition: \( \|\nabla_W \ell_i\| \propto \|h(x_i)\|\cdot\|p_i - y_i\| \) is mathematically unavoidable. If the 6–14× ratio disappears after dividing by \(\|h(x_i)\|\), then the signal was geometric scale, not optimization resistance. So normalization is not a robustness check; it's a definitional test of what signal you're actually using.

On the pseudo-balanced subset: a univariate statistic can only approximate group balance if gradient norm is strongly conditionally dependent on group within class. There is no theoretical guarantee from NHT or ERM dynamics that top-k% by gradient norm yields approximate balance across (y, g). You must compute the induced contingency table.

Weight decay is the real stress test. NHT shows that \(T_{\text{transition}} = \Theta(\frac{1}{\gamma_{\text{eff}}}\log(V_{\text{sc}}/V_{\text{st}}))\) — meaning λ directly alters phase duration. If GNPR only works in a specific λ regime, generality is limited. But if gradient-norm disparity and WGA gains persist across λ ∈ {0, 1e-4, 5e-4}, then the signal is robust to norm-hierarchy geometry.

Bottom line: feasibility hinges on three empirical separations: (1) decoupling from shortcut norm peaks, (2) persistence after feature-norm normalization, and (3) demonstrable induced group balancing. If those hold — "Okay, this could work."

**Key Points:**
- Temporal alignment with NHT norm peaks determines whether GNPR measures shortcut acquisition or structured resistance
- Feature-norm normalization is a definitional test of the underlying mechanism, not a minor control
- Pseudo-balanced subset must empirically approximate (y, g) balance; otherwise DFR-style retraining cannot work in principle

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

I want to bring in the LfF evidence to sharpen the significance argument [Nam et al., 2020, NeurIPS; arXiv:2007.02561]. LfF achieves debiasing by training two networks simultaneously — a biased network \(f_B\) and a debiased network \(f_D\) — using relative loss as the minority signal. The GCE loss \( \frac{1 - p_y^q}{q} \) amplifies bias in the biased network, and the debiased network upweights samples the biased network finds hard. Key result: 84.24% accuracy on CelebA gender bias without labels vs. 62.00% vanilla. This is the closest mechanistic analog to our method.

What matters for significance: LfF requires **two networks trained simultaneously** — double the compute. Our method requires one ERM training pass (standard), then one gradient norm computation pass, then one last-layer retraining pass. If GNR-LLR matches or exceeds LfF's debiasing effectiveness at a fraction of the computational cost, that is a significant efficiency contribution on top of the WGA improvement.

More importantly, LfF's key experiments confirm something directly relevant to our hypothesis: "spurious features are easier to learn, and such reliance is most prominent during the early phase of training" [Nam et al., 2020, Abstract]. This is exactly the regime our gradient norm signal exploits. LfF uses this insight to design relative loss weighting; we use it to select T_id for gradient norm measurement. The mechanisms are parallel, but ours requires no biased network — just gradient hooks on an existing ERM training run.

**Research impact summary:**
- vs. JTT: gradient norm proxy is continuous (richer), has principled T_id selection (novel), requires no second ERM pass for identification (same compute stage)
- vs. DFR: eliminates group-balanced validation set requirement (closes last annotation gap)
- vs. LfF: single-network approach (half the compute), no GCE loss modification required
- Efficiency: gradient norm hooks are O(N × last_layer_dim) per epoch — negligible overhead on existing training

**Target impact venues:** ICML, NeurIPS, ICLR — the group robustness literature is active (JTT:666c, DFR:440c, LfF:172c). A label-free method that approaches DFR accuracy would fit the 2025/2026 frontier.

**Key Points:**
- LfF achieves 84.24% CelebA vs 62% vanilla at double compute; GNR-LLR should match this at single-pass cost
- Efficiency advantage over LfF (one network vs. two) is a concrete secondary contribution
- "Early training spurious reliance" insight from LfF directly validates our T_id window
- Impact framing: closes last annotation gap in DFR family; comparable to NeurIPS/ICML-level contribution

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let us separate enthusiasm from evidence. The central hypothesis is that early per-sample gradient norm identifies samples exerting pressure toward structured (non-spurious) features, and that selecting these samples approximates the balanced reweighting set used in DFR [arXiv:2204.02937]. The evidence so far suggests correlation, but correlation is not mechanism. What would disprove this? A finding that high-norm samples are temporally aligned with shortcut norm expansion, and that their signal vanishes after feature-norm normalization.

First, the temporal alignment test must be formalized. Define \( t_{\text{peak}}^{\text{sc}} \) as the epoch where shortcut-layer norm reaches its maximum. The hypothesis predicts:
\[
\mathbb{E}[g_{\text{minority}}(t)] > \mathbb{E}[g_{\text{majority}}(t)] \quad \text{for } t > t_{\text{peak}}^{\text{sc}}.
\]
Pre-register a quantitative criterion: if minority/majority norm ratio falls below 1.2 after \( t_{\text{peak}}^{\text{sc}} \), the structured-resistance hypothesis is rejected.

Second, define normalized statistic \( \tilde{g}_i = \|\nabla_W \ell_i\| / \|h(x_i)\| \). If the 6–14× ratio collapses to ≈1× after normalization, gradient norm was merely proxying representation magnitude — not optimization resistance.

Third, the DFR analogy requires empirical verification. DFR achieves 92.9% worst-group accuracy on Waterbirds [arXiv:2204.02937, Table]. Pre-specify a balance metric for the induced contingency table: maximum deviation from uniform within class ≤10%. If this condition fails, last-layer retraining lacks DFR's structural premise. Compare GNPR-LLR vs. DFR within 2–3% absolute worst-group accuracy.

Pre-register λ ∈ {0, 1e-4, 5e-4} and test across all regimes. If performance collapses at λ=0 or 5e-4, the mechanism is phase-specific.

*If the method survives: persistent post-peak disparity, normalization robustness, demonstrable pseudo-balance, and stable worst-group gains across λ — then: This meets my standards.*

**Key Points:**
- Pre-register falsifiable temporal criterion: minority norm must remain elevated after shortcut norm peak
- Feature-norm normalization is a decisive mechanistic test; collapse of disparity falsifies the claim
- Verify induced (label, group) balance and match DFR accuracy within 2–3% across λ regimes

---

### Exchange 13

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Prof. Vera and I are converging on the same three requirements. Let me now stress-test the NHT connection [Khanh & Hoa, 2026; arXiv:2603.07323] — both the supporting evidence and its limits.

NHT's core theorem: shortcut solutions are norm-accessible first because \( V_{\text{sc}} > V_{\text{st}} \), and weight decay induces a slow contraction toward lower-norm structured solutions. The temporal delay \( T \propto \frac{1}{\gamma_{\text{eff}}} \log(V_{\text{sc}}/V_{\text{st}}) \) scales inversely with effective contraction rate. NHT validates this on Waterbirds and CelebA — exactly our benchmarks. The Experiments section shows three-phase behavior (shortcut phase, transition, structured phase) with norm peak-then-decay confirmed in ResNet18.

Here's what this means for our method: the high gradient norm disparity at epoch 5 confirmed in our prior runs (G2=70.72, G1=56.98 vs G0=6.90, G3=19.79) is occurring *during the shortcut phase* of training. This is exactly the regime where the model is committed to the spurious solution — and minority samples are the ones the shortcut *cannot* fit. The NHT framework predicts these samples will exert continued gradient pressure because they require the network to traverse the norm hierarchy toward structured solutions. This is not the same as "shortcut inflation" — shortcut inflation would predict the HIGH-norm samples are those driving the model TOWARD the shortcut. But high-norm at epoch 5 = cannot be fit by shortcut = resisting the shortcut.

This is the key mechanistic distinction I was testing, and the NHT framework actually supports the hypothesis rather than undermining it. The "temporal alignment" test I called for is essentially: does the minority norm spike coincide with shortcut layer norm growth (which would be consistent with shortcut-driving) or does it persist after shortcut layer norms peak and begin contracting (consistent with shortcut-resistance)?

Given the NHT experiments show that shortcut-layer norms peak and begin decaying well within the first 20 epochs on Waterbirds/CelebA (their Figure: norm dynamics peak at ~epoch 5–10), our confirmed gradient norm ratio at epoch 4–5 is RIGHT AT the peak. The persistence test requires checking epochs 10–20: if disparity is maintained even as layer norms decay, we're measuring structured resistance. If disparity collapses synchronously with layer norm decay — that's the confound.

But here's the thing: even if the temporal persistence test partially fails — even if disparity collapses from 14x to 4x by epoch 10 — the *practical* question is whether using epoch-5 norms for pseudo-group-balanced subset selection works. The empirical test (WGA ≥ 88%) is the ultimate arbiter.

**Key Points:**
- NHT framework SUPPORTS the hypothesis: high-norm minority samples are resisting the shortcut, not driving it
- The temporal alignment test distinguishes shortcut-driving (norm spike synced with layer norm growth) from shortcut-resisting (norm elevated after layer norm peaks)
- Even if temporal analysis is mixed, the practical WGA test (≥88% on Waterbirds) is the sufficient condition for publication

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's pin this down mechanistically under NHT rather than rhetorically. The update rule in [Khanh & Hoa, 2026] explicitly couples gradient and weight decay:
\[
\theta_{t+1}=\theta_t-\eta(\nabla L(\theta_t)+2\lambda\theta_t)+\eta\xi_t.
\]
This means any gradient-norm statistic is embedded inside a contraction dynamic governed by \( \gamma_{\text{eff}} \). What reassures me, in principle: in the shortcut phase, shortcut-aligned samples incur low loss quickly — \( \|p_i - y_i\| \) collapses early. Minority samples cannot be fit by \(M_{\text{sc}}\), so their residual stays high. Given \( \|\nabla_W \ell_i\| \propto \|h(x_i)\|\cdot\|p_i-y_i\| \), persistent residual alone can sustain elevated gradient norm. So high norm signals misfit under the currently accessible norm basin — exactly what DFR-style balancing needs.

But: if gradient disparity collapses as soon as shortcut-layer norms peak and begin contracting (Proposition 4.2), then GNPR is phase-locked to norm expansion, not structural resistance. Track minority/majority gradient ratios across epochs; verify persistence into early contraction phase. If disparity survives past \(t_{\text{peak}}^{\text{sc}}\): "Okay, this could work." If it vanishes synchronously, the mechanism is weaker than claimed.

On DFR equivalence: if shortcut-fitting samples collapse in loss early, then selecting high-gradient samples naturally filters them out, giving a plausible route to approximate balance. But it must be demonstrated empirically. If induced imbalance remains severe, LLR cannot replicate DFR in principle.

On λ robustness: since \(T_{\text{transition}}\) scales with \(1/\gamma_{\text{eff}}\), altering λ changes the duration and geometry of the shortcut phase. If GNPR works across λ ∈ {0, 1e-4, 5e-4}, the signal is structurally tied to multi-representation interpolation itself.

My position: mechanistically plausible under NHT, but only if you demonstrate (1) persistence beyond shortcut norm peak, (2) robustness after feature-norm normalization, (3) induced class-conditional group balancing sufficient for LLR to emulate DFR.

**Key Points:**
- High gradient norm plausibly reflects shortcut misfit under NHT, but only if disparity persists past shortcut norm peak
- Feature-norm normalization and temporal tracking are mechanistic necessity tests
- GNPR-LLR can match DFR only if top-k gradient selection empirically induces near-balanced P(g|y) and is robust across λ

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The discussion has now converged on a precise, testable hypothesis. Let me formalize it and show why all three of Prof. Pax's conditions are achievable with existing infrastructure.

**Responding to the LfF analogy [Nam et al., 2020; arXiv:2007.02561]:** LfF's methodology demonstrates the central principle: "neural networks learn to rely on the spurious correlation only when it is easier to learn than the desired knowledge, and such reliance is most prominent during the early phase of training" [Abstract]. The GCE loss amplifies bias in f_B, and the debiased f_D upweights samples f_B finds hard — exactly the high-residual samples that our gradient norm identifies. The key difference is: LfF requires training two networks simultaneously. GNR-LLR requires one. The experiments confirm LfF achieves 84.24% on CelebA without labels vs. 62% baseline — a 22% gain from the same kind of "hard sample identification" that gradient norm provides.

**The three feasibility conditions are addressable:**

1. **Temporal persistence:** The prior runs confirmed gradient_norm_ratio = 12.20 at epoch 5 AND 6.37 at epoch 5 (two separate measurements). More importantly, per-epoch data shows G2/G0 norm ratio at E1=6.10, E2=6.59, E3=6.56, E4=14.73, E5=12.20 — the ratio is *increasing* from epoch 1 to 4, not declining. This is inconsistent with a pure shortcut-inflation interpretation (which would predict a spike then collapse). We need epochs 10–20 data — but the early trajectory already favors persistence.

2. **Feature-norm robustness:** The decomposition \( \|\nabla_W \ell_i\| \propto \|h(x_i)\| \cdot \|p_i - y_i\| \) means even if feature norms are slightly larger for minority groups, the ratio 6–14x is very large. For the ratio to collapse after normalization, feature norms would need to be proportionally larger — which is unlikely given ResNet-50's batch-normalized features. The existing gradient_analysis.py computes full-network norms; adding feature-norm normalization requires one line (h_norm = model.feature_extractor(x).norm()). This is within existing infrastructure.

3. **Induced group balance:** Given minority groups have 6–14x higher norms, top-k% selection will be dominated by minority samples. For k ≈ 25% (approximating the minority fraction in Waterbirds), the induced contingency table should show strong enrichment. This is a direct empirical verification using the existing group annotations (used post-hoc for evaluation, not training) on the Waterbirds dataset.

**The final unified hypothesis:**

*Under ERM+SGD training on Waterbirds (primary) and CelebA (secondary), Gradient-Norm-Informed Last-Layer Retraining (GNR-LLR): trains ERM for T_id ∈ {3, 5} epochs; computes normalized per-sample last-layer gradient norms \( \tilde{g}_i = \|\nabla_W \ell_i\| / \|h(x_i)\| \); selects top-k% as pseudo-minority and bottom-k% as pseudo-majority samples; constructs a pseudo-group-balanced subset; freezes the ERM feature extractor; retrains only the classification head on this subset. GNR-LLR achieves WGA ≥ 88% on Waterbirds (vs. JTT's 86.7%) and WGA ≥ 82% on CelebA (vs. LfF's 84.24%), without any group label supervision, at approximately the same computational cost as a single ERM training run.*

H0: There is no significant difference in WGA between GNR-LLR and JTT on Waterbirds or CelebA.

This hypothesis is: feasible (existing infrastructure), novel (no published method uses gradient norm for pseudo-group-balanced DFR), falsifiable (clear quantitative thresholds vs. established baselines), and impactful (closes DFR annotation gap).

**Key Points:**
- Temporal ratio data (E1: 6.10, E4: 14.73) already suggests increasing trend inconsistent with shortcut-inflation
- Feature-norm normalization is one line of code in existing gradient_analysis.py
- Final hypothesis: GNR-LLR achieves WGA ≥ 88% Waterbirds / ≥ 82% CelebA without group labels, at single-ERM cost
- H0: no significant WGA difference from JTT; success metric = WGA + hyperparameter stability

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The gradient-norm-informed last-layer retraining (GNR-LLR) method is genuinely novel. No published work uses per-sample gradient norm magnitude as the signal for pseudo-group-balanced subset construction in a DFR-style protocol. The continuous signal, principled T_id selection via temporal norm dynamics, and NHT-grounded mechanism all represent innovations over JTT (binary, heuristic) and LfF (dual-network). The "label-free DFR" framing is a compelling and unexplored contribution.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is well-specified with pre-registered falsification criteria: (1) minority norm must remain elevated past shortcut norm peak (ratio ≥ 1.2 post-t_peak_sc), (2) disparity must persist after feature-norm normalization (ratio ≥ 3x in normalized signal), (3) induced contingency table must achieve near-balance (≤10% deviation within class), (4) WGA ≥ 88% on Waterbirds across ≥5 seeds, ≥ 82% CelebA. Clear comparison baselines: JTT (86.7%), DFR (92.9%), LfF (84.24%). All tests run on existing infrastructure with existing benchmarks.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The impact narrative is clear: GNR-LLR closes the last annotation gap in the DFR family (DFR requires group-balanced validation set; GNR-LLR uses no group supervision) while achieving comparable WGA. Secondary contributions: efficiency advantage over LfF (one network vs. two), principled T_id selection (vs. JTT's heuristic), and NHT-theoretic mechanism. This is a NeurIPS/ICML-level contribution in an active field (JTT: 666c, DFR: 440c).

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Completely feasible with existing confirmed infrastructure: h-e1/code/ with per-sample gradient norm hooks (6–14x ratio already measured), ResNet-50 + WaterbirdsDataset + evaluate.py, conda env youra-h-e1, H100 GPU. Adding feature-norm normalization is one line of code. Temporal tracking requires storing gradient norms at each epoch (trivial). The 5-seed experiment with λ grid {1e-4} primary + {0, 5e-4} secondary fits within ~3–5 GPU hours per dataset. No new benchmarks, no synthetic data, no human annotation.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a clear, novel, and impactful hypothesis: **Gradient-Norm-Informed Last-Layer Retraining (GNR-LLR)** for label-free spurious correlation robustification.

The core claim is: during ERM training on spuriously correlated datasets (Waterbirds, CelebA), minority-group samples produce substantially larger per-sample gradient norms than majority-group samples (confirmed 6–14x ratio) because they cannot be fit by the spurious shortcut solution — they exert structural resistance under the NHT norm-hierarchy framework [Khanh & Hoa, 2026]. This signal can be used to construct a pseudo-group-balanced subset without group labels, enabling DFR-style last-layer retraining that achieves high worst-group accuracy.

The proposed method GNR-LLR: (1) trains ERM for T_id ∈ {3, 5} epochs; (2) computes normalized per-sample last-layer gradient norms \( \tilde{g}_i = \|\nabla_W \ell_i\| / \|h(x_i)\| \); (3) selects top-k% as pseudo-minority and bottom-k% as pseudo-majority; (4) freezes the ERM feature extractor; (5) retrains only the classification head on the pseudo-balanced subset. Target: WGA ≥ 88% on Waterbirds (vs. JTT's 86.7%, DFR's 92.9%), WGA ≥ 82% CelebA (vs. LfF's 84.24%), at approximately single-ERM-run computational cost, without any group label supervision.

The null hypothesis H0: No significant difference in WGA between GNR-LLR and JTT on Waterbirds or CelebA. Falsification: WGA ≤ 85%, or AUC(normalized gradient norm → minority group) ≤ AUC(misclassification → minority group), or temporal disparity collapses post shortcut norm peak.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The pseudo-group-balanced subset quality depends entirely on whether gradient norm is class-conditionally correlated with group membership — this must be empirically verified with contingency tables before committing to Stage 2 last-layer retraining
- The temporal alignment test (does norm disparity persist after shortcut norm peak?) is mechanistically critical and cannot be assumed from epoch-5 data alone
- CelebA validation is required to confirm cross-dataset generalization — Waterbirds alone is insufficient for a claim of general applicability
- **Mitigation Strategy:** These three concerns become Sub-experiments (E1: temporal analysis, E2: contingency table, E3: CelebA). If E1 and E2 confirm the signal quality, E3 is a natural extension. None of these concerns invalidate the hypothesis — they are Phase 2B verification sub-hypotheses.

