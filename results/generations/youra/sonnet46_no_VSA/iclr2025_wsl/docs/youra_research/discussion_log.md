# Phase 2A Research Discussion Log
**Gap:** Gap 1 — No Empirical Comparison of Architecturally Invariant vs Non-Invariant Weight Encoders on OrbitVar + Downstream R² on ModelZooDataset CIFAR10-GS
**Timestamp:** 2026-08-03T18:00:00Z
**Execution Mode:** UNATTENDED
**Architecture:** Self-Contained Tikitaka Loop (Dual-Exchange)

---

## Research Briefing

**Research Question:** Does an architecturally permutation-invariant weight encoder (DeepSets-style channel pooling or Neural Functional Network layer) achieve OrbitVar < 0.001 under S_16³ channel permutations on ModelZooDataset CIFAR10-GS, and does this improve LightGBM R² vs CISE baseline (OrbitVar = 0.010333)?

**CISE Baseline (sh1 PASS):** mean OrbitVar(CISE) = 0.010333, n_models=100, n_permutations=100.

**Available Papers:**
- P1: arxiv_1703_06114.md — Deep Sets (Zaheer et al., 2017; 3096 citations)
- P2: arxiv_2302_14040.md — Permutation Equivariant Neural Functionals / NFN (Zhou et al., 2023; 78 citations)
- P3: arxiv_2301_12780.md — Equivariant Architectures for Deep Weight Spaces / DWSNet (Navon et al., 2023; 115 citations)
- P4: arxiv_2002_11448.md — Predicting Neural Network Accuracy from Weights (Unterthiner et al., 2020; 136 citations)
- P5: arxiv_2403_12143.md — Graph Neural Networks for Equivariant Representations of NNs (Kofinas et al., 2024; 65 citations)

**Available Repos:**
- AllanYangZhou/nfn (93★) — pip install nfn; NF-Layers
- AvivNavon/DWSNets (90★) — DWSNet ICML 2023
- manzilzaheer/DeepSets (315★) — canonical reference
- mkofinas/neural-graphs (85★) — GNN-for-NNs ICLR 2024

---

### Previous Failure / Routing Context

**Recursive Entry: v3** (2 prior archive entries found)

#### h-m1 (Run 1) — FAIL: MATHEMATICAL_INVARIANCE
- **Date:** 2026-08-03T15:00:00Z
- **What failed:** Per-layer quantile encoder (order statistics) — OrbitVar(C1) = 1.24e-33 (machine epsilon)
- **Root cause:** Order statistics are provably permutation-invariant by construction. Aliasing is mathematically impossible for any encoder using sorted values/histograms/quantiles over the permuted dimension.
- **Lesson:** NEVER use order-statistic-based encoders for aliasing experiments. Must verify encoder is NOT invariant to the test symmetry group before running.
- **PROHIBITED direction:** Any encoder using quantile, sorted values, or histogram features over channel dimension.

#### sh1 (Run 1) — PASS: MUST_WORK (Baseline Established)
- **Date:** 2026-08-03T16:10:00Z
- **What succeeded:** CISE encoder with sinusoidal positional encoding: mean OrbitVar(CISE) = 0.010333 (threshold: 0.01, margin: +3.3%)
- **Key finding:** Sinusoidal PE formula sin(cπ/C), cos(cπ/C) breaks permutation symmetry cleanly. This is the non-invariant baseline to beat.
- **Reusable artifacts:** sh1/code/experiment/{cise_encoder.py, permutation.py, evaluate.py, data_loader.py}
- **Dataset:** Zenodo record 6620869, file `dataset_cifar_small_hyp_rand.pt`

#### sh2 (Run 1) — FAIL: MUST_WORK_FAIL
- **Date:** 2026-08-03T17:00:00Z
- **What failed:** Hungarian canonical ordering (LAP) to reduce OrbitVar(CISE) — OrbitVar(CISE_aligned) = 0.010325, reduction ratio 1.0×
- **Root cause:** OrbitVar measures within-model orbit variance. Hungarian LAP is cross-model alignment. These are orthogonal operations — cross-model alignment cannot reduce within-model orbit variance.
- **Lesson:** Post-hoc alignment methods (LAP/Hungarian) do NOT address OrbitVar. Need encoder-level architectural changes.
- **PROHIBITED direction:** Post-hoc alignment (LAP, Hungarian, Sinkhorn) as mechanism for reducing OrbitVar.

#### PROHIBITED DESIGN FAMILIES (DO NOT EXPLORE):
1. Encoders using order statistics (quantiles, sorted values, histograms) over channel dimension
2. Post-hoc cross-model alignment (LAP/Hungarian) as OrbitVar reduction mechanism
3. Any approach relying on cross-model operations to address within-orbit (within-model) variance

#### VALIDATED APPROACH (Build on this):
- **Architectural permutation-invariance** inside the encoder — DeepSets-style sum/mean pooling, NFN layers
- Deep Sets theorem (Zaheer 2017): ρ(Σφ(xᵢ)) guarantees OrbitVar = 0 by construction for any permutation group
- Anti-sh2 gate: verify `encoder(permute(W)) == encoder(W)` before full run
- Anti-h-m1 gate: confirm encoder uses symmetric pooling (NOT order statistics)

---


### Exchange 1

🔬 **Prof. Vera** (Rigorous Validation Architect):

The theoretical foundation is clear. Theorem 2 in DeepSets states that any permutation-invariant set function must decompose as f(X) = ρ(Σφ(x)) for suitable φ, ρ [Zaheer et al., 2017]. If our channel dimension is treated as a set, then a DeepSets-style encoder should yield **OrbitVar = 0 up to numerical precision** for any permutation in S_16³. The evidence suggests that if OrbitVar exceeds ~1e-12 (float64) or ~1e-6 (float32), the implementation is not truly invariant. Therefore, the first experiment is not empirical performance — it is a *mathematical invariance audit*. What would disprove invariance? A single counterexample where ||E(W) - E(π·W)||₂ > ε for fixed tolerance ε under exhaustive or high-coverage permutation sampling. If such a case exists, the architecture is not compliant with Theorem 2.

We must separate **invariance verification** from **predictive utility**. It is logically possible that OrbitVar ≈ 0 yet downstream R² does not improve over CISE. The hypothesis under test is therefore twofold:
1. H₁: DeepSets encoder achieves mean OrbitVar < 0.001 (targeting numerical zero).
2. H₂: LightGBM trained on invariant embeddings achieves higher cross-validated R² than CISE baseline.

For H₁, success criteria: mean OrbitVar < 1e-6 and max OrbitVar < 1e-5 across 100 models × 100 permutations. For H₂: mean 5-fold CV R² increase ≥ 0.02 absolute, paired t-test p < 0.01.

A potential Achilles' heel: **expressivity collapse**. Sum pooling removes channel identity entirely. If predictive signal depends on structured channel interactions, DeepSets may be too coarse. Theorem 2 guarantees invariance, not predictive sufficiency. We must be willing to accept that result.

Confounds require control: identical preprocessing, embedding dimensionality, and LightGBM hyperparameters across encoders. Perform adversarial stress test: inject random channel relabelings at training time for CISE. If CISE R² degrades under such augmentation while DeepSets remains stable, that constitutes causal evidence that invariance improves robustness.

**Key Points:**
- Define strict numerical tolerances for OrbitVar invariance (mean < 1e-6, max < 1e-5).
- Separate invariance verification from downstream R² testing with explicit statistical thresholds.
- Stress-test via adversarial channel relabeling to establish causal link between invariance and robustness.

---

### Exchange 2

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

🔬 Prof. Vera has framed the invariance audit precisely — and I agree the mathematical guarantee from Deep Sets Theorem 2 is airtight for sum/mean pooling. But here's where this breaks down: **Vera's framing conflates the property of the architecture with the property of the implemented encoder on THIS specific dataset.**

Unterthiner et al. [2020] established that simple weight statistics — per-layer moment features like mean, variance, spectral norms — already achieve R² > 0.98 on ModelZooDataset CIFAR10-GS. This is a brutal baseline. If the non-invariant CISE encoder with sinusoidal PE already sits near this ceiling, then a DeepSets encoder achieving OrbitVar ≈ 0 faces: **what variance is left to explain?** If R² ceiling effects limit the measurable gain to < 0.02 absolute, Vera's threshold of Δ R² ≥ 0.02 may be unachievable — not because invariance fails, but because prediction is already near-solved.

The specific logical gap: the hypothesis chain is OrbitVar ↓ → representation consistency ↑ → R² ↑. Step (b)→(c) is unproven. The sh2 result showed OrbitVar did NOT change with cross-model alignment — and R² was not tested for alignment. We have ZERO empirical data linking any reduction in OrbitVar to any change in R². Show me the evidence for this mechanism.

Second critical stress point: **what specific CISE R² baseline value exists?** If sh1 only established OrbitVar = 0.010333 but never measured CISE R² on the CIFAR10-GS held-out test, then H₂ has no concrete comparison point. Confirm the exact sh1 LightGBM R² value before running any new encoder.

Third: expressivity collapse is understated. DeepSets sum pooling computes per-channel φ(w_c) then sums across C=16 channels. The CISE encoder computes per-channel statistics PLUS sinusoidal PE injecting channel-position information — that's exactly the information that both breaks invariance AND potentially encodes useful structure. Removing the PE to achieve invariance may throw away the predictively useful features. This echoes h-m1: trivially invariant encoders achieve OrbitVar ≈ 0 but lose signal.

**What would convince me:** (1) Confirm sh1 LightGBM R² from logs as exact baseline; (2) Define fallback: if DeepSets achieves OrbitVar < 0.001 but R² < CISE_R², redirect to NFN; (3) Anti-h-m1 filter: explicitly verify no order statistics in φ(w_c).

**Key Points:**
- R² ceiling from Unterthiner 2020 (R²>0.98 from simple statistics) may make Δ R² ≥ 0.02 unachievable.
- H₂ needs concrete sh1 CISE R² baseline from experimental logs, not just OrbitVar.
- Add NFN fallback branch: if DeepSets achieves OrbitVar ≈ 0 but R² regresses, escalate to expressive invariant encoder.

---


### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Achieving OrbitVar ≈ 0 with a DeepSets encoder is *technically trivial* if implemented correctly. Theorem 2 from Zaheer et al. guarantees invariance for sum-decomposition architectures, and Vera is right: any deviation beyond floating-point tolerance is an implementation bug, not a research question. So H₁ is not scientifically interesting — it's a compliance check. The real issue is H₂: whether strict invariance *in this dataset* can improve R² over an already-strong baseline.

Here's what worries me: the CIFAR10-GS setting is not an abstract set of independent channels. In an MLP, hidden neuron permutations act *jointly* on adjacent weight matrices (Eq. 5 in [DWSNet, Navon et al., 2023]). A DeepSets encoder applied independently to channels of a single layer ignores that coupling. DWSNet explicitly models these shared permutation indices using equivariant linear blocks and proves this spans all linear equivariant maps (Theorem 5.1). In other words, DeepSets gives you invariance, but not necessarily the *right invariance structure*. If predictive signal lives in cross-layer interactions preserved under the group action, a per-layer sum encoder may collapse it.

On the causal chain OrbitVar ↓ → R² ↑, we currently have no mechanistic justification. DWSNet results show large performance gains over non-equivariant baselines (e.g., 85.7% vs 58.9% on MNIST INRs) when the task is explicitly invariant [Navon et al., 2023]. But those tasks have *substantial performance headroom*. If CIFAR10-GS regression is already at R² ≈ 0.98 per Unterthiner [2020], then invariance cannot add 0.02 unless current error is symmetry-induced. The ceiling matters mathematically: if Bayes R² ≈ 0.99 and you're at 0.98, the maximum achievable gain is 0.01.

Feasibility test I'd insist on: First, quantify symmetry-induced variance directly — compute Var_π[ŷ(π·W)] for the trained CISE+LightGBM pipeline. If this is <1% of total prediction variance, eliminating OrbitVar cannot yield measurable R² gain. Second, run a permutation-robustness experiment: evaluate CISE-trained LightGBM on randomly permuted test weights. If R² degrades under permutation, invariance could help. If it doesn't, the downstream model has already learned approximate invariance, and architectural enforcement won't change much.

On DeepSets vs DWS/NFN: DWS-style equivariant layers are strictly more expressive under the same symmetry group because they characterize *all* linear equivariant maps over the full weight-space representation. DeepSets only captures invariants over a single set index. So if invariance is beneficial but DeepSets underperforms due to expressivity collapse, escalating to DWS-like encoder is theoretically sound.

**Key Points:**
- OrbitVar ≈ 0 is a compliance property, not evidence that invariance improves R².
- DeepSets enforces invariance but may collapse cross-layer structure; DWS-style equivariance is strictly more expressive under the full permutation group.
- Before expecting ΔR² ≥ 0.02, quantify symmetry-induced prediction variance and confirm headroom below the statistical ceiling.

---


### Exchange 4

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax and Prof. Rex have raised the right challenges — and YES, these are addressable. Let me strengthen the hypothesis against each.

On the R² ceiling concern: Unterthiner et al. [2020] reported R² > 0.98 using *simple* weight statistics (moments, spectral norms) on a held-out test set of 120K CNNs across all CIFAR datasets combined. But the CIFAR10-GS SMALL zoo subset used in sh1 (Zenodo 6620869, synthetic Kaiming-init weights) is a much narrower distribution. The CISE baseline R² on this specific subset is unknown — sh1 only measured OrbitVar, not R². Critically, CISE's sinusoidal PE introduces *representational noise* (within-orbit variance = 0.010333) that LightGBM must average over at inference. If LightGBM sees 100 different representations of the same model due to channel permutation, its predictions scatter. Measuring that scatter directly — Var_π[ŷ(π·W)] — is Prof. Pax's proposed feasibility gate, and I fully support adding it as Prediction P3.

On the expressivity collapse: DeepSets sum pooling per channel IS coarse. But here's the strengthening: we don't need to choose one encoder. The hypothesis should be structured as three sub-experiments with a clear ladder:
- **SH3**: DeepSets achieves OrbitVar < 0.001 (compliance gate — expected PASS)  
- **SH4**: DeepSets R² vs CISE R² — tests whether basic invariance helps or hurts
- **SH5** (if SH4 shows NFN is needed): NFN/DWS-style encoder achieves both lower OrbitVar AND higher R² than DeepSets

This ladder structure prevents the outcome where DeepSets achieves near-zero OrbitVar but worse R² from killing the entire research direction. Instead it routes to the more expressive encoder.

On the causal mechanism: Prof. Rex is right that OrbitVar ↓ → R² ↑ is unproven. But we can make it testable. The mechanism is: reduced OrbitVar → reduced prediction variance across permutations of the same model → reduced expected squared error on any single representation → improved R². This is falsifiable: if DeepSets achieves OrbitVar < 0.001 AND Var_π[ŷ] drops substantially, but R² does NOT improve, then the mechanism is wrong — the prediction variance reduction is not the driver of R². This null result is scientifically valuable.

The key refinement: reframe H₂ as a **relative** comparison. Instead of requiring absolute ΔR² ≥ 0.02, require that DeepSets R² is ≥ CISE R² (with a one-sided test). The research question is whether architectural invariance helps or hurts — not whether it helps by a fixed threshold.

**Key Points:**
- Structure as a three-step ladder (SH3 compliance → SH4 R² comparison → SH5 expressive escalation) to prevent false negatives.
- Reframe H₂ as relative comparison (DeepSets R² ≥ CISE R²) rather than absolute threshold.
- Add Prediction P3: measure Var_π[ŷ(π·W)] for CISE baseline as mechanistic gate before H₂.

---


### Exchange 5

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — the ladder structure is cleaner. But here's where this still breaks down: you're proposing to improve on a regime where the paper already shows R² = 0.984 on CIFAR10-GS using simple per-layer statistics Ŵ_L with GBM [Unterthiner et al., 2020, Table 2]. That leaves **1.6% unexplained variance**. So before we talk about architectural elegance, answer this: *what fraction of that remaining 1.6% is plausibly due to permutation-induced representation noise?* If it's 0.2%, your entire program has a mathematical ceiling of 0.002 in absolute R². That's below typical CV noise.

Now let's interrogate the mechanism. You're claiming: OrbitVar ↓ → Var_π[ŷ(π·W)] ↓ → E[(y-ŷ)²] ↓ → R² ↑. That second arrow is nontrivial. LightGBM is a tree ensemble. Trees partition feature space. If CISE embeddings under permutation remain within the same leaf regions most of the time, prediction variance may already be negligible even if embedding variance (OrbitVar) is 0.01. The paper's invariance probe shows that permuting within convolutional layers yields MAD < 0.05 in predictions for raw-weight predictors [Unterthiner et al., 2020]. That's partial robustness already. Show me that your CISE pipeline has prediction MAD large enough to matter relative to residual error.

Second unstated assumption: invariance is not already *implicitly learned*. Table 1 shows raw W and W⁴ features perform nearly as well as per-layer statistics. That means GBM is already extracting low-order symmetric summaries from unordered tensors. If downstream learners approximate invariance statistically, hard-coding it architecturally may yield no gain.

Third: DeepSets may be the wrong invariance class. Pax is correct — the symmetry group here is not independent channel permutations per layer; it's *coupled permutations across adjacent layers*. Unterthiner's results that W⁴ alone gives R²=0.969 (CIFAR10-GS) suggest final-layer signal is disproportionate. A naive sum-pooling encoder could wash out structured interactions within that layer.

Here's what would actually convince me:
1. Empirically show permutation-induced prediction variance accounts for ≥20% of residual MSE under CISE.
2. Demonstrate DeepSets reduces that component by ≥80%.
3. Show resulting R² gain matches the predicted MSE reduction within error bars.

**Key Points:**
- The remaining headroom above R²=0.984 is only 1.6%; quantify how much is permutation-induced before promising gains.
- OrbitVar reduction does not guarantee prediction variance reduction; measure permutation-induced MSE directly.
- DeepSets must beat strong per-layer statistics (Ŵ_L), not just CISE, or the hypothesis is mis-targeted.

---


### Exchange 6

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something — but I think Prof. Rex's framing is accidentally saving us from a weak hypothesis and pointing us toward a MUCH stronger one. What if we completely reframe the research question?

Rex's critical insight is that Unterthiner 2020's simple Ŵ_L statistics (R²=0.984) are already *approximately* permutation-invariant by design — per-layer moment features (mean, variance) are computed via order statistics which ARE permutation-invariant over the channel set! So the baseline comparison is not CISE (a non-invariant encoder) vs DeepSets (an invariant encoder). The baseline is already an approximately invariant encoder. The question becomes: *does ARCHITECTURALLY ENFORCED permutation-invariance add anything over STATISTICALLY APPROXIMATE invariance?*

This is the paradigm shift: imagine the invariance space as a spectrum from (a) statistically approximate (Ŵ_L moments, R²=0.984) → (b) non-invariant but channel-identity-aware (CISE sinusoidal PE, OrbitVar=0.010333, R²=?) → (c) architecturally guaranteed (DeepSets sum pooling, OrbitVar→0). The *surprising* direction is that (b) might underperform (a) because CISE introduces variance without adding useful structure! And (c) might recover (a)'s performance through a cleaner theoretical route.

What if the research finds: DeepSets achieves OrbitVar→0 AND matches or slightly improves Unterthiner's Ŵ_L baseline (R²≈0.984)? That result has triple novelty: (1) first measurement of architecturally invariant encoder OrbitVar on ModelZooDataset, (2) first comparison to Ŵ_L baseline confirming equivalence via cleaner architecture, (3) CISE as negative control showing that non-invariant encoders with PE perform WORSE than simple invariant baselines.

The experiment design insight this unlocks: our experiment should have THREE encoder conditions:
- **C0**: Simple per-layer statistics Ŵ_L (Unterthiner baseline, approximately invariant) — already have R²≈0.984
- **C1_CISE**: CISE with sinusoidal PE (non-invariant, OrbitVar=0.010333) — measure R², compare to C0
- **C2_DeepSets**: DeepSets sum pooling (architecturally invariant, OrbitVar→0) — measure R², compare to C0 and C1

The hypothesis becomes: architectural invariance (C2) achieves R² ≥ C0 (approximately invariant baseline), while C1 (non-invariant CISE) achieves R² < C0 — demonstrating that channel-identity noise in the encoder actively HURTS performance.

This is genuinely new! No paper has run CISE vs DeepSets vs Ŵ_L on OrbitVar+R² simultaneously on ModelZooDataset. The negative result for CISE (if it underperforms Ŵ_L) would be publishable on its own.

**Key Points:**
- Reframe: Ŵ_L moments ARE approximately permutation-invariant — they're the true baseline, not CISE.
- Three-condition design (C0=Ŵ_L, C1=CISE, C2=DeepSets) tests whether architectural invariance adds to approximate invariance.
- Hypothesis: CISE underperforms Ŵ_L because it adds channel-identity noise; DeepSets matches or improves Ŵ_L through cleaner architecture.

---


### Exchange 7

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let us tighten this into a falsifiable program. The evidence suggests we are conflating three distinct quantities: (i) representation-level invariance (OrbitVar in embedding space), (ii) prediction-level permutation variance Var_π[ŷ(π·W)], and (iii) residual error E[(y-ŷ)²]. Only (ii) can causally influence (iii). Theorem 2 in DeepSets [Zaheer et al., 2017] guarantees architectural invariance of the form f(X) = ρ(Σφ(x)); for DeepSets, OrbitVar should be zero up to floating-point tolerance. That is a compliance check. What we must test is whether nonzero prediction-level permutation variance under CISE accounts for a material fraction of the residual MSE relative to the Ŵ_L baseline (R²≈0.984).

Decomposition experiment: for each model W, sample K independent permutations π_k. Define:
- MSE_perm = E_W[Var_π(ŷ(π·W))] — permutation-induced prediction variance
- MSE_res = E_W[(y - ȳ_W)²] — residual after orbit-averaging
- Identity: E[(y-ŷ)²] = MSE_res + MSE_perm (by bias-variance decomposition across orbits)

This gives a measurable upper bound: eliminating permutation sensitivity can improve total MSE by at most MSE_perm. What would disprove the invariance-benefit hypothesis? Finding MSE_perm / MSE_total < 0.2 under CISE would indicate permutation noise explains <20% of residual error — insufficient to justify architectural intervention.

The comparison must be three-way as Dr. Nova suggests (C0 = Ŵ_L, C1 = CISE, C2 = DeepSets). Pre-registered success criteria: (a) C2 achieves MSE_perm ≤ 1e-6 (numerical invariance check); (b) C1 shows MSE_perm > 0.01 × MSE_total (nontrivial sensitivity); (c) observed ΔMSE between C1 and C2 matches MSE_perm within ±10% relative error. Condition (c) tests the mechanism: if total MSE reduction does not equal the eliminated permutation component, invariance is not the driver.

To guard against a stronger counterexample: train LightGBM on CISE embeddings augmented with explicit permutation indices as nuisance features. If prediction variance increases, the model was implicitly suppressing index information. Additionally, compare to a permutation-averaged predictor ŷ_avg(W) = (1/K)Σŷ(π_k·W). If ŷ_avg significantly outperforms single-pass CISE, then invariance was not internally learned.

If these criteria are met and the MSE decomposition closes numerically: *This meets my standards.*

**Key Points:**
- Decompose total MSE into permutation-induced and residual components for a hard upper bound on possible R² gains.
- Pre-register falsification criteria linking eliminated permutation variance to observed ΔMSE (±10% closure test).
- Control for implicit invariance learning in LightGBM via nuisance-feature augmentation and orbit-averaged predictor.

---


### Exchange 8

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field? And having read the NFN paper [Zhou et al., 2023] carefully, I want to make an impact argument that elevates this discussion above a narrow benchmark comparison.

NFN's key finding is that permutation-equivariant neural functionals — architectures that respect the symmetry group of the weight space — outperform non-equivariant baselines on weight-space tasks including generalization prediction, INR classification, and policy evaluation. Critically, NFN doesn't just achieve invariance by pooling; it achieves *equivariance* — the output transforms consistently with input permutations. For invariant prediction tasks (predicting a scalar like test accuracy), equivariance reduces to invariance. But the richer structure of equivariant representations may capture cross-layer weight relationships that pure invariance (DeepSets pooling) discards.

This matters because Dr. Nova's three-condition experiment (C0=Ŵ_L, C1=CISE, C2=DeepSets) is excellent for establishing the basic invariance-utility relationship, but it misses the MOST IMPORTANT comparison: C3=NFN. If NFN achieves BOTH lower OrbitVar than CISE AND higher R² than Ŵ_L, that establishes that *architectural equivariance strictly outperforms approximate invariance from simple statistics*. That result would be significant for the field because it answers a question the DWSNet and NFN papers raise but don't directly answer: "Is the benefit of equivariant encoders above and beyond simple permutation-robust statistics?"

The significance framework: this research could establish the first empirically grounded answer to: "Does architectural symmetry enforcement add value beyond statistically robust baselines on model zoo performance prediction?" The answer structure has three possible outcomes, all valuable:
1. DeepSets ≈ Ŵ_L >> CISE: architectural invariance recovers simple-statistics performance without PE noise
2. DeepSets < Ŵ_L: expressivity collapse; need more structure (NFN/DWS)
3. NFN > Ŵ_L ≥ DeepSets: equivariant structure is strictly beneficial — strongest publishable result

The research opens new questions regardless of outcome: what is the minimum symmetry structure needed for model zoo prediction? Does the answer depend on the dataset distribution (diversity of architectures, training procedures)?

The mandatory feasibility constraints are satisfied: ModelZooDataset exists, Unterthiner's Ŵ_L baseline exists with known R², NFN pip-installable. This is immediately runnable research.

**Key Points:**
- Add C3=NFN as the fourth condition — the most impactful comparison is equivariant (not just invariant) architecture vs approximate invariance.
- Three possible outcome structures, all scientifically valuable; the NFN>Ŵ_L result would be the strongest publishable finding.
- Research answers the open question: does architectural symmetry enforcement add value beyond statistically robust weight statistics?

---


### Exchange 9

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — adding C3 = NFN is the right escalation. But here's where I'm pressing hard: NFN beats STATNN on Kendall's τ by 0.934 vs 0.915 on CIFAR-10-GS [Zhou et al., 2023, Table 2]. So if C0 baseline is Unterthiner-style statistics (STATNN), you are testing "does *linear equivariant structure with cross-layer couplings* matter beyond pooled statistics?" — not just "does invariance matter?" Those are different hypotheses. Be precise.

Here's the conceptual breakdown: DeepSets (C2) only guarantees invariance of the form ρ(Σφ(x)). But NF-Layer in Eq. (2) explicitly models row sums, column sums, adjacent-layer couplings, and pointwise terms — the *complete* characterization of linear NP-equivariant maps [Zhou et al., 2023]. DeepSets cannot express cross-layer equivariant interactions. So if NFN > Ŵ_L ≥ DeepSets, the win is **structured equivariance with inter-layer coupling** — not "architectural invariance" per se. Don't conflate those.

Second unstated assumption: symmetry group alignment. The Small CNN Zoo uses CNNs with channel permutations, but spatial filter dimensions are *not* permutable. NFN handles this by folding spatial dimensions into channels before applying NP-equivariant layers. If your CISE or DeepSets encoders treat flattened tensors as arbitrary sets without respecting the coupled row/column action, you are not matching the true symmetry group. Show me your C2 implementation respects the same group action as NFN — simultaneous row/column permutations across adjacent layers — or the comparison is invalid.

NFN's gain over STATNN in τ is about 0.019 absolute on CIFAR-10-GS. That's modest. Translate to R² space before promising anything dramatic. What would convince me: (1) replicate STATNN-level performance with C0, (2) replicate NFN-level gap over C0 comparable to their τ gap, (3) show this gap persists after orbit-averaging C1 predictions. If orbit-averaging closes the gap, your mechanism is permutation noise. If not, the gain is structural expressivity.

**Key Points:**
- NFN's gains reflect structured equivariant cross-layer coupling, not just invariance — don't conflate mechanisms.
- Ensure symmetry group alignment (coupled row/column permutations) or DeepSets comparison is invalid.
- Pre-register whether gains stem from permutation noise elimination or relational expressivity; test via orbit-averaging.

---


### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex just identified the most technically critical flaw, and I want to make it concrete using DWSNet [Navon et al., 2023]. Let me be direct: the symmetry group in our experiment is NOT what you think it is.

DWSNet (Sec. 2) formalizes this precisely: for a two-layer MLP W₂σ(W₁x), simultaneously permuting rows of W₁ and columns of W₂ (W₁ → P^T W₁, W₂ → W₂P) generates a *functionally identical* network. The symmetry group is the product of permutation groups acting **jointly across adjacent layers** — not independent per-layer permutations. The CIFAR10-GS small CNN zoo contains CNNs with 3 convolutional layers plus a dense layer. The true symmetry group is S₁₆ × S₁₆ × S₁₆ × S_dense acting on the coupled (row, column) pairs of adjacent weight matrices.

This is the feasibility problem: our S_16³ symmetry group notation in sh1/sh2 was treating 3 independent channel permutations. If those were actually applied independently (permuting only rows OR only columns of each layer, not coupled), then the "permutation" in sh1/sh2 did NOT correspond to functional symmetries of the network. It produced changed weight matrices that represent DIFFERENT functions. OrbitVar measured under non-functional permutations is measuring noise in a space where there is no symmetry, not within-orbit variance of the equivalence class.

The feasibility gate before any H₂ experiment: verify that permutations used in sh1/sh2 were FUNCTIONALLY SYMMETRIC (applied as coupled row-column pairs across adjacent layers as in DWSNet Eq. 5). If they were not, then OrbitVar(CISE) = 0.010333 was measuring response to non-functional perturbations. The CISE encoder's OrbitVar under functional permutations may be completely different.

Mechanically, this is testable: pick any model from ModelZooDataset, apply the coupled permutation (P^T W_l, W_{l+1} P simultaneously), evaluate the network on a fixed input, compare output to original. If outputs match to float precision, permutation is functional. If they differ, permutation was incorrect.

This does NOT kill the research direction — it refines it. The correct S_16³ group under functionally equivalent permutations is well-defined and implementable using DWSNet's framework. The reusable permutation.py from sh1 must be audited to confirm it implements coupled permutations. If it does, we proceed. If not, fix it first.

**Key Points:**
- The true symmetry group requires coupled row-column permutations across adjacent layers (DWSNet Eq. 5), not independent per-layer permutations.
- Audit sh1's permutation.py to verify it implements functional permutations (network output preserved).
- OrbitVar measurements are only meaningful under functionally symmetric permutations; verify this before any H₂ comparison.

---


### Exchange 11

🔬 **Prof. Vera** (Rigorous Validation Architect):

Before any comparison among C0–C3, we must close the symmetry audit Prof. Pax raised. The DWSNet formalism is unambiguous: the true group action is the coupled permutation of adjacent layers with G = S_d1 × ... × S_d(M-1) acting by simultaneous row/column permutations [Navon et al., 2023]. A necessary precondition experiment: for N randomly sampled zoo models and K random group elements g ∈ G, measure Δ_func = max_x ||f_v(x) - f_{g·v}(x)||_∞ over a fixed input set. Acceptance criterion: Δ_func ≤ 1e-6. Any deviation falsifies functional symmetry. Without this, OrbitVar is uninterpretable.

Assuming the group is validated, we must distinguish mechanism. DeepSets-style invariance (C2) only enforces invariance of the form ρ(Σφ(·)); it does not span all equivariant linear maps over the direct-sum space V = ⊕_m (W_m ⊕ B_m). Theorem 5.1 in DWSNet shows the complete space of linear equivariant maps decomposes into structured blocks between (W_m, B_l), implementable via pooling, broadcasting, dense maps, and Hartford-style two-index equivariant forms [Navon et al., 2023]. Therefore, NFN/DWSNet (C3) has strictly greater linear equivariant capacity than DeepSets (C2).

Testable prediction: if performance(C3) > performance(C2) and the gap persists after orbit-averaging C1, then the driver is relational expressivity, not permutation noise elimination. What would disprove this? If C2 ≈ C3 within statistical error after symmetry alignment, then structured cross-layer equivariance provides no measurable benefit.

Pre-registered decomposition criteria:
- (A) C2 and C3 must satisfy MSE_perm ≤ 1e-6 (numerical invariance).
- (B) ΔMSE(C1→C2) must equal MSE_perm^C1 within ±10% relative error if invariance is the mechanism.
- (C) Any additional gain C3 over C2 must manifest as reduction in MSE_res, not MSE_perm.

Statistical requirements: identical train/val/test splits across C0–C3; mean ± 95% CI over ≥5 random seeds. Power analysis: detect ΔR² ≥ 0.01 with power 0.8 at α=0.05.

**Key Points:**
- Verify functional symmetry via coupled row-column action before interpreting OrbitVar; require Δ_func ≤ 1e-6.
- Decompose MSE into permutation and residual components; pre-register closure criteria (±10%) to test mechanism.
- Any NFN gain over DeepSets must be attributed to reduced residual error under matched symmetry alignment.

---


### Exchange 12

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — and now I can see exactly how to strengthen this into a complete, defensible hypothesis. Let me synthesize what the discussion has converged on.

The core strengthened hypothesis is:

**Under S_16³ functional permutations (coupled row-column per-layer as in DWSNet), architecturally permutation-invariant weight encoders (DeepSets C2, NFN C3) will achieve near-zero OrbitVar AND each achieves downstream LightGBM R² at least as high as simple per-layer statistics (C0 = Ŵ_L, R²≈0.984), while the non-invariant CISE encoder (C1) achieves lower R² because permutation-induced prediction variance MSE_perm^C1 contributes materially to total MSE.**

The mechanism now has three testable links:
1. **Invariance check**: C2, C3 achieve OrbitVar < 1e-6 (architectural guarantee under correct group)
2. **Noise attribution**: MSE_perm^C1 ≥ 0.1 × MSE_total^C1 (permutation noise is non-negligible for CISE)
3. **Mechanism closure**: ΔMSE(C1→C2) ≈ MSE_perm^C1 (within 10%) — if this holds, invariance is the driver

The critical addition Dr. Sage and Prof. Rex contributed: NFN (C3) is tested as the *expressive* equivariant encoder against DeepSets (C2) as the *simple* invariant encoder. If NFN > DeepSets ≥ Ŵ_L, the finding is that structured equivariance adds beyond approximate invariance. If DeepSets ≈ Ŵ_L > CISE, the finding is that the PE in CISE introduces noise without adding predictive value.

The feasibility constraints are all satisfied: ModelZooDataset Zenodo 6620869 available, Unterthiner Ŵ_L statistics implementable (mean/var per layer), NFN pip-installable, permutation.py from sh1 to audit. The anti-h-m1 gate (no order statistics in φ) and anti-sh2 gate (architectural not post-hoc) are both met by C2/C3 design.

What would address Prof. Rex's remaining concern about functional permutation validity: audit sh1's apply_channel_permutation() to confirm it implements W_l → P^T W_l, W_{l+1} → W_{l+1} P jointly. If sh1 used per-layer independent permutations (only rows, not coupled columns), the OrbitVar = 0.010333 result must be re-run with functional permutations.

**Key Points:**
- Synthesized hypothesis: invariant encoders (DeepSets, NFN) achieve R² ≥ Ŵ_L; CISE underperforms because MSE_perm is non-negligible.
- Three-link mechanism chain now fully testable with pre-registered criteria from Prof. Vera.
- Single feasibility prerequisite remaining: audit sh1 apply_channel_permutation() for functional (coupled) vs independent permutations.

---


### Exchange 13

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. The hypothesis is finally sharp enough to attack. Now I'm going to try to break it.

First, on symmetry: if Eq. (5) from DWSNet [Navon et al., 2023] is not implemented exactly — coupled row/column permutations across adjacent layers — your entire OrbitVar story collapses. If your C2 encoder ignores shared indices and treats each W_m as an independent set of vectors, it is invariant to the wrong group. That would artificially handicap it relative to NFN/DWSNet, which is built from the block-decomposition characterization (Theorem 5.1). Alignment of representation space is not optional.

Second: you're assuming LightGBM cannot compensate for encoder structure gaps. If LightGBM is sufficiently expressive, it can reintroduce cross-layer interactions even with pooled statistics. So if C2 ≈ C3 under LightGBM, it might not mean structured equivariance is useless — it might mean the downstream model compensates. What would convince me: an ablation using a *matched linear head* for C2 and C3. If C3 > C2 under a linear head, the advantage is representational. If the gap only appears with a powerful head, you're measuring encoder bias × booster capacity interaction.

Third: your mechanism closure criterion ΔMSE(C1→C2) ≈ MSE_perm^C1 within ±10% assumes permutation noise and residual error are additive and independent. That's unstated. What if invariance reshapes representation geometry so the regressor generalizes better? Then ΔMSE could exceed MSE_perm^C1. Pre-register an excess-gain interpretation clause: if ΔMSE ≫ MSE_perm^C1, attribute excess to representation smoothing beyond noise removal.

Fourth: STATNN's τ=0.915 vs NFN's τ=0.934 is not a landslide. Add a stress test: train on CIFAR-10 zoo, test on CIFAR-10-C zoo (corrupted variants). If structured equivariance captures functional semantics, it should degrade less under distribution shift. That's where small R² gains become credible.

Finally: "CISE underperforms because MSE_perm is non-negligible" is only defensible if orbit-averaged C1 predictions match C2 performance. If orbit-averaging closes the gap, invariance is the mechanism. If not, CISE is simply a worse representation.

**Key Points:**
- Ensure DeepSets C2 respects exact coupled group action from DWSNet Eq. (5), or comparisons to NFN/DWSNet are invalid.
- Test representational advantage under matched linear head to separate encoder expressivity from downstream capacity.
- Pre-register excess-gain interpretation clause and add distribution-shift robustness axis (CIFAR-10 → CIFAR-10-C).

---


### Exchange 14

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me consolidate and frame the impact case for the field, because I believe we've arrived at the core hypothesis. The discussion has refined the question from "does DeepSets reduce OrbitVar?" (trivially YES by Theorem 2) to something much more interesting:

**Does architecturally enforced permutation-invariance, implemented with correct symmetry group alignment (coupled row-column permutations), improve ModelZooDataset performance prediction over a non-invariant encoder (CISE) AND over approximate-invariant baselines (Ŵ_L moment statistics), and is this improvement causally mediated by reduced permutation-induced prediction variance?**

The significance: this research will be among the first to jointly measure (1) OrbitVar as an explicit encoder symmetry metric, (2) permutation-induced prediction variance (MSE_perm) as a mechanistic quantity, and (3) downstream R² comparison across the invariance spectrum. NFN and DWSNet papers show downstream performance improvements but never report OrbitVar or MSE_perm as metrics. Unterthiner 2020 reports R² but with no invariance metrics. We're proposing the FIRST paper to connect all three measurements in a closed causal loop.

Prof. Rex's distribution-shift robustness test is exactly the kind of additional finding that makes a small R² gain publishable — it shows the mechanism is about generalization quality, not just in-sample noise reduction.

Regarding feasibility constraints from the pipeline: all experiments use ModelZooDataset CIFAR10-GS (existing), no new benchmarks, no human annotation, no synthetic data. NFN is pip-installable. The experiment is self-contained.

The research matters because it establishes whether OrbitVar is a *valid diagnostic metric* for encoder quality in model zoo settings. If MSE_perm correlates with R² improvement, practitioners can use OrbitVar as a cheap proxy to select encoders. If not, OrbitVar is merely an encoder property without downstream relevance — a negative finding that saves future researchers from chasing the wrong metric.

**Key Points:**
- First paper to jointly measure OrbitVar, MSE_perm, and R² across the invariance spectrum in a closed causal loop.
- Distribution-shift robustness (CIFAR-10 → CIFAR-10-C) makes small R² gains publishable by demonstrating generalization mechanism.
- Establishes OrbitVar's validity as a diagnostic metric for encoder quality — positive or negative, this result informs the field.

---


### Exchange 15

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let me tighten this into a falsifiable program with quantitative gates.

The symmetry audit is non-negotiable. Two-part validation:
1. **Functional invariance test:** For each model v, sample K random g ∈ G and compute Δ_func = max_x ||f_v(x) - f_{g·v}(x)||_∞. Acceptance criterion: Δ_func ≤ 1e-6. Any violation falsifies correct implementation of DWSNet Eq. (5).
2. **Encoder equivariance test (for C3):** For each linear block L inside the DWSNet stack, numerically verify L(g·v) = g·L(v) to tolerance 1e-6. Theorem 5.1 claims completeness; any measurable deviation indicates implementation error.

Second, separate *invariance as noise removal* from *equivariance as relational expressivity* via a **matched linear head** atop frozen encoders C2 and C3. If C3 > C2 under a linear regressor, structured cross-layer blocks contribute representational power beyond pooled invariance. If gap only appears with LightGBM, effect is downstream model compensation. Pre-registered criterion: detect ΔR² ≥ 0.01 with 95% CI excluding zero across ≥5 seeds.

Third, mechanism closure test: ΔMSE(C1→C2) = MSE_perm^C1 ± 10%. If orbit-averaged C1 predictions match C2, invariance suffices. If orbit-averaged C1 remains inferior, representation geometry matters. If ΔMSE ≫ MSE_perm^C1, attribute excess to representation smoothing (separate testable hypothesis).

Fourth, additional diagnostic: **orbit diameter** D_orbit(v) = max_g ||φ(v) - φ(g·v)||₂. Prediction: C2/C3 have D_orbit ≤ 1e-6; C3 shows lower local Lipschitz variance than C2 if relational structure stabilizes embeddings.

On distribution shift (CIFAR-10 → CIFAR-10-C): pre-register degradation ordering: ΔR²_shift(C3) < ΔR²_shift(C2) ≤ ΔR²_shift(C1). If no ordering within statistical power, robustness claims are unsupported.

*This meets my standards if all pre-registered criteria are met with explicit falsifiers.*

**Key Points:**
- Strict symmetry audit aligned to DWSNet Eq. (5); functional deviation >1e-6 falsifies group correctness.
- Matched linear-head ablation with ΔR² ≥ 0.01 detection threshold to isolate representational expressivity.
- Extend diagnostics to orbit-diameter and Lipschitz stability; pre-register distribution-shift degradation ordering.

---


### Exchange 16

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something genuinely original! What if we flip the entire framing? The conversation has been treating Unterthiner's Ŵ_L moments as a "near-ceiling" that limits our ambition. But I see a different opportunity: **use the moments as a scaffold, not a ceiling.**

Here's the paradigm shift: instead of comparing CISE vs DeepSets vs Ŵ_L vs NFN as four separate encoders, design a **Hybrid Invariant Encoder (HIE)** that concatenates:
1. Ŵ_L statistics (permutation-invariant moments, the strong baseline)
2. DeepSets φ(w_c) sum-pooled per-layer features (architecturally invariant additional features)

The HIE is automatically permutation-invariant (both components are), potentially richer than either alone, and directly testable: HIE R² ≥ max(C0, C2)? This is a stronger hypothesis than any comparison between existing encoders, because it proposes a practical synthesis. If Ŵ_L captures order-statistic invariant features and DeepSets captures deeper per-element nonlinear features, the combination might recover Ŵ_L's strong baseline AND add complementary signal.

The novelty: no paper has proposed this combination for model zoo performance prediction. It directly addresses Prof. Rex's concern about "ceiling effects" — we're not trying to beat 0.984 by a little, we're building a richer invariant representation and testing whether the combination exceeds either component.

For NFN: use it as the C3_expressive condition, but now compare against HIE rather than separately. If NFN > HIE, structured equivariance truly adds beyond even a rich invariant baseline. That's a clean signal.

The distribution-shift test Prof. Rex proposed becomes even more interesting for HIE: does combining order-statistic features with learned nonlinear invariant features improve robustness beyond either alone?

**Key Points:**
- Propose HIE (Hybrid Invariant Encoder = Ŵ_L moments + DeepSets φ-sum) as a synthesis hypothesis: richer than either alone.
- HIE is automatically permutation-invariant — no separate invariance verification needed (both components guarantee it).
- Positions NFN as the "pure equivariant" reference against HIE "combined invariant": cleanest test of whether relational structure adds beyond combined statistics.

---


---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is genuinely novel on three axes: (1) first paper to jointly measure OrbitVar, MSE_perm, and R² across the invariance spectrum, (2) HIE (Ŵ_L + DeepSets) as a practical synthesis encoder not proposed before, (3) distribution-shift robustness as the second axis confirming that permutation structure captures functional semantics. The reframing — simple statistics as approximate invariance, CISE as noise-adding non-invariance, DeepSets as architectural invariance, NFN as structured equivariance — is a clean conceptual taxonomy that advances the field.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has explicit pre-registered quantitative gates: functional symmetry test (Δ_func ≤ 1e-6), mechanism closure (ΔMSE = MSE_perm^C1 ± 10%), matched linear head ΔR² criterion (≥ 0.01, 95% CI), and ordered robustness degradation (C3 ≤ C2 ≤ C1 under shift). Each has a clear falsification: if Δ_func > 1e-6 the group is wrong; if ΔMSE ≫ MSE_perm the mechanism is wrong; if C2 ≈ C3 structured equivariance is unnecessary. This structure meets scientific standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The research establishes whether OrbitVar is a valid diagnostic metric for encoder quality — a standing open question in weight-space learning. The closed causal loop (OrbitVar → MSE_perm → R²) is novel, the result is applicable to any model-zoo performance prediction task, and negative outcomes (orbit-averaging closes the gap, or C2 ≈ C3) are equally valuable. The distribution-shift axis makes small R² gains publishable. Positioned to contribute to ICML/NeurIPS.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All feasibility requirements satisfied. ModelZooDataset CIFAR10-GS exists at Zenodo 6620869, NFN is pip-installable, Ŵ_L statistics are standard (mean/var per layer), sh1 code artifacts reusable. The symmetry audit (functional permutation validation) is a concrete executable test before any expensive experiment. The HIE is implementable as a simple concatenation. Anti-h-m1 gate (no order statistics in DeepSets φ) and anti-sh2 gate (architectural not post-hoc) are both satisfied. The mechanism is physically/mathematically valid.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is substantially refined from the original research question. Under S_16³ functional permutations (coupled row-column actions across adjacent layers, as formalized in DWSNet [Navon et al., 2023]), the research investigates whether architecturally permutation-invariant weight encoders achieve both (a) near-zero OrbitVar and (b) LightGBM prediction R² at least matching the simple per-layer statistics baseline (Ŵ_L, R²≈0.984 from Unterthiner et al. [2020]), while the CISE encoder (non-invariant, OrbitVar=0.010333) underperforms because permutation-induced prediction variance MSE_perm is non-negligible.

The experiment uses four encoder conditions: C0 = Ŵ_L moment statistics (approximately invariant baseline), C1 = CISE with sinusoidal PE (non-invariant), C2 = DeepSets sum pooling (architecturally invariant), C3 = NFN (structured equivariant). A fifth condition, HIE = C0 + C2 concatenated, tests whether combining hand-engineered invariant features with learned invariant features outperforms either alone. The mechanistic test links OrbitVar reduction to prediction variance reduction (MSE_perm) to R² improvement via a bias-variance decomposition over permutation orbits, with pre-registered closure criterion (ΔMSE = MSE_perm^C1 ± 10%). A distribution-shift stress test (CIFAR-10 → CIFAR-10-C) assesses whether invariant encoders show ordered robustness degradation, converting small in-sample R² gains into a publishable robustness claim.

The key predictions are: (P1) DeepSets and NFN achieve OrbitVar < 1e-6 under functionally verified permutations; (P2) CISE achieves R² < Ŵ_L due to non-negligible MSE_perm; (P3) DeepSets achieves R² ≥ Ŵ_L; (P4) NFN achieves R² ≥ DeepSets under matched linear head if structured equivariance adds relational expressivity. The hypothesis avoids all prohibited design families: no order statistics (anti-h-m1), no post-hoc alignment (anti-sh2).

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The functional symmetry of sh1's permutation.py must be audited before any experiment — if it did not implement coupled row-column permutations, OrbitVar = 0.010333 is measured under a non-functional group and the CISE baseline must be re-run.
- LightGBM's implicit invariance learning may compress the C1 vs C2 gap; the matched linear head ablation is mandatory to isolate encoder expressivity from downstream model capacity.
- MSE_perm quantification requires MC sampling over permutation orbits (K ≥ 100 per model), which is computationally more intensive than simple R² comparison — must be feasibility-checked on ModelZooDataset subset first.
- **Mitigation Strategy:** Run permutation.py audit as Phase 2A prerequisite gate; report results before Phase 4 coding. Include matched linear head as mandatory SH (sub-hypothesis). Use K=50 permutations per model for MSE_perm estimation with standard error bounds.

