# Phase 2A Tikitaka Discussion Log

**Session:** gap-1 - SSL Embeddings for Spurious Correlation Structure Discovery
**Started:** 2026-03-19T21:50:00Z
**Mode:** Self-Contained Loop (v9.0.0)

---

## Research Context

### Selected Research Gap (Priority: P0)

**Gap ID:** gap-1
**Title:** SSL Embeddings for Spurious Correlation Structure Discovery

**Current State:** SSL methods (SimCLR, MoCo) shown to have fairness trade-offs (Seth & Pai 2024), but their embeddings not explored for clustering-based minority discovery. Pre-trained embeddings improve robustness (Mehta et al. 2022) but use as clustering input for group identification is unexplored.

**Missing Piece:** Systematic study of whether frozen SSL embeddings naturally separate minority groups in embedding space, enabling unsupervised discovery via clustering.

**Potential Impact:** Provides unsupervised alternative to JTT/LfF/SSA methods that require misclassification-based discovery, bias-amplified networks, or pseudo-attribute prediction.

### Reference Papers Available

1. **arxiv_2311_16361.md** - Making Self-supervised Learning Robust to Spurious Correlation via Learning-speed Aware Sampling (2023, 2 citations)
2. **arxiv_2212_06254.md** - You Only Need a Good Embeddings Extractor to Fix Spurious Correlations (2022, 21 citations)

Papers are located in: `docs/youra_research/20260318_scsl/papers/`

### ROUTE_TO_0 Context

This research direction emerges from 3 previous failed attempts:
- **SAM Optimizer:** +0.90pp WGA (target ≥10pp) - flat minima ≠ group-robust minima
- **Gradient Norms:** ΔAUC 0.0242, p=0.589 - gradient norms don't encode minority information
- **Human Annotation:** 3-4 weeks required - incompatible with automated pipeline

**Validated Infrastructure:**
- WaterbirdsDataset with group metadata ✓
- ResNet-50 backbone (ImageNet pretrained) ✓
- GroupDRO baseline: +10.9pp WGA confirmed ✓
- Full evaluation framework ✓

---

## Discussion Exchange Log

**Instructions for Claude:**
- You will write persona responses in a loop orchestrated by `orchestrate_exchange.py`
- The script will tell you which persona to respond as and provide topic guidance
- Write authentic, research-focused responses
- Reference papers using exact filenames when relevant
- The orchestrator checks convergence via external LLM - continue until convergence detected

---


### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

After reviewing the research context and the two key papers (arxiv_2311.16361 and arxiv_2212_06254), I see a fascinating opportunity that bridges self-supervised learning and fairness in a fundamentally new way.

**The core insight:** We know from Mehta et al. (2022) that pre-trained embeddings alone can achieve 90% worst-group accuracy on Waterbirds. But they treat embeddings as a *final* representation for classification. What if we instead use frozen SSL embeddings as a *diagnostic tool* for minority discovery? The LA-SSL paper (Zhu et al., 2023) shows that SSL can capture spurious correlations through learning-speed patterns, but they address this by resampling during SSL training. I propose we flip this: **exploit SSL's tendency to capture spurious features by clustering the frozen embedding space to identify minority groups.**

**Three unconventional angles to explore:**

1. **Multi-Scale Clustering Hypothesis**: Instead of assuming one optimal number of clusters (k), what if spurious correlation structure reveals itself across multiple clustering resolutions? We could run hierarchical clustering and look for stable minority groups across k∈{2,4,8,16}. This would distinguish genuine minority clusters from noise.

2. **Embedding Gradient Analysis**: Even with frozen SSL encoders, we can compute per-sample gradients at the embedding layer. The hypothesis: minority samples will have gradient directions that differ systematically from majority samples. This could provide a second signal beyond spatial clustering.

3. **Cross-Architecture Consensus**: Instead of relying on SimCLR alone, what if we extract embeddings from multiple SSL architectures (SimCLR, MoCo, DINO) and look for samples that cluster as minorities *consistently* across architectures? This ensemble approach could dramatically improve precision/recall for minority discovery.

**Key Questions:**
- Do SSL embeddings preserve spurious feature information even when trained with augmentations designed to be invariant?
- Can we quantify the "clusterability" of minority vs majority groups in embedding space before expensive retraining?
- Is there a theoretical connection between SSL's learning-speed awareness (LA-SSL) and embedding space geometry?

**Key Points:**
- Shift from using SSL embeddings for classification to using them for diagnostic minority discovery
- Explore multi-scale clustering to find robust minority group structure
- Consider ensemble approaches across SSL architectures for higher precision/recall
- Link to LA-SSL's learning-speed patterns through embedding geometry analysis

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your proposal is imaginative, but we must translate it into falsifiable claims. The evidence from *[Anonymous et al., 2022; arxiv_2212_06254]* suggests that frozen embeddings alone already achieve up to 90.13% worst-group accuracy (WGA) on Waterbirds with a simple linear ERM classifier. This implies that subgroup-separating information is present in the representation. However, the critical question is not whether information exists, but whether it is *geometrically recoverable without labels* through clustering. These are distinct hypotheses.

Let us formalize your central claim: **H1 — Minority groups in Waterbirds form geometrically separable clusters in frozen SSL embedding space, such that unsupervised clustering can recover them at rates significantly above chance.** A concrete prediction: if we cluster embeddings (e.g., k-means or hierarchical clustering) and align clusters to true subgroup labels post hoc, adjusted mutual information (AMI) or normalized mutual information (NMI) should exceed 0.5. What would disprove this? If across architectures (ResNet-50, ViT-H-14) and pretraining datasets (ImageNet vs. SWAG), clustering yields AMI ≈ 0 (i.e., indistinguishable from random partitioning), then the geometry does not encode subgroup structure in a cluster-recoverable manner—even if it supports linear classification.

Your multi-scale clustering hypothesis introduces a second testable claim: **H2 — True minority groups exhibit scale-stable clustering across k ∈ {2,4,8,16}.** We can quantify "stability" via variation of information across resolutions or dendrogram persistence. The null hypothesis is that cluster assignments for minority samples fluctuate unpredictably with k. If stability metrics do not significantly exceed those of randomly permuted embeddings, then the "multi-scale robustness" interpretation collapses. Importantly, we must control for class-label structure; bird type may dominate clustering and masquerade as subgroup recovery.

The cross-architecture consensus idea is promising, but again requires sharp criteria. Prediction: samples identified as minority by clustering in ≥2 architectures (e.g., SimCLR, DINO, MoCo) should show significantly higher enrichment for true minority labels than samples flagged by only one. A simple enrichment test with bootstrapped confidence intervals would suffice. If consensus does not improve precision–recall relative to single-architecture clustering, then the ensemble hypothesis fails. Furthermore, capacity confounds must be controlled: [Anonymous et al., 2022] show higher-capacity models (e.g., ViT-H-14) yield better WGA. If clustering performance scales purely with model capacity rather than architectural diversity, the "consensus" mechanism may simply reflect representation quality.

Finally, I am cautious about the gradient-direction proposal. With frozen encoders and a linear head, gradient differences primarily reflect classification boundary geometry, not intrinsic embedding structure. To test whether gradients add independent signal, we should measure whether gradient-based minority scores improve subgroup recovery beyond clustering alone using logistic regression with held-out validation. If no incremental AMI gain is observed, the gradient hypothesis is redundant.

The evidence suggests that frozen embeddings contain subgroup-relevant information. What remains unproven is whether this information manifests as unsupervised cluster structure rather than linearly separable but entangled features. Our experiments must be designed to reveal that distinction.

**Key Points:**
- Formulate explicit, falsifiable hypotheses: clustering must recover true subgroups with measurable AMI/NMI above chance.
- Multi-scale and cross-architecture claims require stability and enrichment metrics, with capacity and label-structure confounds controlled.
- Distinguish linear separability from clusterability; if embeddings are not geometrically separable without labels, the core hypothesis fails.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Prof. Vera, your formalization is excellent, but there's a critical gap I need to address. The very paper you cited — Mehta et al. (2022, arxiv_2212_06254) — reveals a fundamental problem that undermines the clustering premise entirely.

**Here's where this breaks down:** Mehta et al. achieved 90.13% WGA using frozen ViT-H-14 embeddings with a **simple linear ERM classifier** — no clustering, no minority discovery, no group rebalancing. They just extracted embeddings and trained a linear head. Their experiments show that higher-capacity models (ViT > ResNet) and larger pre-training datasets (SWAG > ImageNet) monotonically improve WGA. Critically, they compare against GroupDRO (89.2% WGA), JTT, SSA, and LfF — all methods that explicitly identify and reweight minorities. Yet the frozen embedding + linear classifier **beats them all** without ever discovering minority groups.

**What this tells us:** The subgroup information is linearly separable in the embedding space. The model doesn't need to *cluster* minorities or *discover* them — it just learns the correct decision boundary through standard ERM. If clustering were necessary for achieving high WGA, Mehta et al.'s approach would have failed. But it didn't.

**Show me the evidence for the clustering hypothesis:** If frozen embeddings already achieve 90% WGA via linear classification, what incremental benefit does clustering provide? You need to demonstrate that:
1. Clustering-guided retraining outperforms linear ERM on frozen embeddings (currently: no evidence)
2. The AMI/NMI thresholds you propose (>0.5) are actually achievable AND translate to WGA gains beyond 90% (currently: no evidence)
3. The failure modes that clustering addresses are NOT already handled by the linear classifier (currently: no evidence)

**The capacity confound is devastating:** Mehta et al. show that ViT-H-14 (307M params, SWAG pre-training) achieves 90.13% WGA while ResNet-50 (25M params, ImageNet) only gets 88.50%. If we cluster ResNet-50 embeddings and get AMI > 0.5, is that evidence for "clustering works" or evidence for "ResNet-50 is undertrained"? When we then cluster ViT-H-14 embeddings, will higher AMI simply reflect better representations, not a causal clustering mechanism?

**The gradient direction proposal is redundant:** With a frozen encoder and linear head, gradients encode classification error direction. You're proposing to use classification signals to discover minorities... but that's just JTT with extra steps. JTT already uses misclassification (ERM failure) to identify minorities. Your gradient approach doesn't add new information.

**What would convince me:** Run Mehta et al.'s exact setup (frozen ViT-H-14, linear ERM) as your baseline. Then show that ANY clustering-based intervention (reweighting, upsampling, cluster-balanced loss) pushes WGA beyond 90.13%. If you can't beat linear ERM, then clustering is not the mechanism — it's a diagnostic tool that confirms what linear classifiers already exploit. And if it's just diagnostic, we've learned nothing new about minority discovery.

**Key Points:**
- Mehta et al. (2022) prove frozen embeddings + linear ERM achieves 90% WGA without clustering or minority discovery
- Clustering hypothesis must explain what fails in linear ERM that clustering fixes (currently unexplained)
- Capacity confounds (model size, pre-training data) may fully explain any observed AMI gains
- Gradient direction analysis is equivalent to JTT's misclassification detection — not a novel signal

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether clustering is *possible*, but whether it changes what we understand about representation learning under spurious correlation. Prof. Rex is correct: Mehta et al. show that frozen high-capacity embeddings with linear ERM already achieve ~90% worst-group accuracy. If clustering merely rediscovers structure that linear classifiers already exploit, then this is incremental diagnostics, not a scientific advance.

However, there is a deeper issue that neither side has fully articulated. LA-SSL [Zhu et al., 2023] demonstrates that *learning speed* during SSL encodes information about spurious correlations and that dynamically resampling based on this signal yields more robust representations. That result tells us something profound: spurious structure is not just present in the representation—it shapes the *trajectory* by which representations form. If clustering of frozen embeddings can recover minority structure *without observing learning dynamics*, then we have evidence that learning-speed asymmetries leave a persistent geometric signature. That would connect dynamics (LA-SSL) to geometry (clusterability). If it cannot, then LA-SSL's gains likely stem from trajectory-level intervention rather than static representation structure.

So the decisive experiment is not "can clustering beat 90% WGA?" but this:  
1. Train standard SSL and LA-SSL encoders.  
2. Freeze both.  
3. Measure subgroup AMI/NMI under unsupervised clustering in both embedding spaces.

If LA-SSL improves WGA yet *reduces* clusterability of spurious groups, that suggests it has entangled or neutralized spurious features geometrically—strong evidence that dynamic sampling reshapes representation topology. If clusterability remains high while WGA improves, then the geometry still encodes spurious structure, and robustness emerges from downstream classifier behavior.

What does this mean for the field? If subgroup structure is linearly separable but not clusterable, then fairness interventions should target decision boundaries, not representation geometry. If it is clusterable—and especially if cluster persistence aligns with learning-speed signals from LA-SSL—then we have a unified picture: minority samples occupy coherent low-density basins formed by early/late learning dynamics.

**Key Points:**
- The contribution must clarify whether subgroup information is merely linearly separable or geometrically clusterable—these imply different theories of robustness
- Critical experiment compares clusterability between standard SSL and LA-SSL embeddings to test whether learning-speed interventions alter representation topology
- True impact comes from linking optimization dynamics (learning speed) to embedding geometry

---

### Exchange 5

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground Dr. Sage's proposal in concrete feasibility. The decisive experiment (standard SSL vs LA-SSL clusterability comparison) is technically sound and runs in principle. However, there's a critical implementation detail: LA-SSL requires *learning-speed signals* during training, which means we need to implement the LA-SSL resampling algorithm from [Zhu et al., 2023].

Looking at their methodology: LA-SSL tracks per-sample learning speed via loss trajectories and resamples inversely proportional to speed. This is computationally feasible—we have the infrastructure from previous failed attempts (W aterbirds dataset, ResNet-50 backbone, evaluation framework all validated). The key addition is loss tracking during SSL training.

**The mechanism is mathematically sound:** If learning-speed-aware sampling neutralizes spurious correlations by preventing the model from "shortcutting" to easy spurious features, we should observe reduced cluster coherence for background-based groups in the embedding space. Conversely, if standard SSL embeds background as a salient dimension, k-means should recover it.

**Concrete feasibility test:** Extract embeddings from both SSL variants, run k-means with k=4 (matching Waterbirds' 4 groups), compute AMI against true subgroup labels. If AMI(standard SSL) >> AMI(LA-SSL), then learning-speed intervention has geometrically suppressed spurious structure. This is a clean, executable experiment.

**What about the 90.13% WGA baseline?** Here's where I see the path forward: we're not trying to beat ViT-H-14. We're trying to understand *why* it works. If we can show that clusterability predicts which models/architectures will benefit from fairness interventions versus those that won't, that's mechanistic insight. A mid-capacity model (ResNet-50, currently 88.50% WGA) with high minority clusterability might reach 90%+ with cluster-balanced retraining, while a high-capacity model with low clusterability might already be at its ceiling with linear ERM.

**Key Points:**
- LA-SSL vs standard SSL clusterability comparison is technically feasible with validated infrastructure
- The mechanism (learning-speed suppresses geometric spurious structure) is mathematically testable
- Contribution is mechanistic insight: clusterability as a diagnostic for which models benefit from fairness interventions

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by synthesizing the critiques into a unified hypothesis. Prof. Rex and Prof. Pax are right that we can't ignore the 90.13% WGA baseline. Dr. Sage is right that we need mechanistic insight, not just performance gains. Dr. Nova's initial angles provide the creative exploration space. Let me propose a refined hypothesis that addresses all concerns:

**Refined Core Hypothesis:** Frozen SSL embeddings encode spurious correlation structure along two distinct axes: (1) linearly separable discriminative features that enable high WGA via simple classifiers, and (2) geometrically clusterable density modes that reveal the *mechanisms* by which models learn robustness. These axes are partially orthogonal—linear separability is necessary but not sufficient for geometric clusterability.

**Concrete Predictions:**
1. **Clusterability-Performance Gap** [H1]: On Waterbirds, mid-capacity models (ResNet-50, EfficientNet-B0) will show AMI > 0.4 for background-based clustering, while high-capacity models (ViT-H-14) will show AMI < 0.3, despite the latter achieving higher WGA (90%+ vs 88%). This tests whether clusterability and linear separability dissociate at high capacity.

2. **LA-SSL Geometry Suppression** [H2]: LA-SSL training will reduce AMI by ≥30% relative to standard SSL (e.g., 0.5 → 0.35) while maintaining or improving WGA. This directly tests Dr. Sage's dynamics-geometry hypothesis.

3. **Diagnostic Power** [H3]: For models with AMI > 0.4, cluster-balanced retraining will improve WGA by ≥2pp. For models with AMI < 0.3, the same intervention yields < 0.5pp gain. This establishes clusterability as a predictive diagnostic.

**Evidence-Based Defense:**
- Mehta et al. show ViT-H-14 achieves 90.13% WGA → we're not claiming clustering beats this
- LA-SSL shows learning-speed matters → we test if this leaves geometric traces
- GroupDRO requires labels → we show when unsupervised clustering can replace label-based reweighting

**Addressing Prof. Rex's Capacity Confound:** We control for this by testing AMI at matched WGA levels. If a ResNet-50 model fine-tuned to 90% WGA still shows higher AMI than ViT-H-14, then clusterability is independent of performance—it's a distinct geometric property.

This reformulation makes clustering a *diagnostic and mechanistic tool*, not a performance claim. We're explaining when and why different fairness interventions work.

**Key Points:**
- Reframe clustering as mechanism explanation, not performance competition with Mehta et al.
- Three testable predictions spanning capacity effects, LA-SSL geometry, and diagnostic power
- Control capacity confounds by matching WGA across architectures before comparing AMI

---

### Exchange 7

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Okay, Dr. Ally's reformulation addresses several of my concerns, but let me stress-test the predictions:

**H1 (Clusterability-Performance Gap):** The prediction that ResNet-50 shows higher AMI than ViT-H-14 is bold. But here's the failure mode: if ResNet-50's higher AMI simply reflects *worse representation quality* (more entangled features → spurious clusters dominate), then high AMI is a bug, not a feature. You need to show that high-AMI models can be *improved* via clustering interventions, not just that they cluster better because they're worse.

**What would convince me:** Run H3 first. If high-AMI models improve with cluster-balanced retraining, then AMI is diagnostic. If they don't, then AMI just measures "how much the model failed to abstract away spurious features."

**H2 (LA-SSL Geometry Suppression):** This is your strongest prediction. If LA-SSL reduces AMI while maintaining/improving WGA, that's direct evidence that clusterability ≠ robustness. But you must control for one confound: LA-SSL also changes the *training set distribution* through resampling. Lower AMI might just reflect that the model never saw background-biased examples clustered together during training, not that it learned a fundamentally different geometry.

**Control experiment:** After LA-SSL training, freeze the encoder and train a *second* linear classifier on the rebalanced Waterbirds distribution. If AMI drops, the geometry changed. If AMI stays high, the original LA-SSL classifier just learned a different boundary, not a different representation.

**H3 (Diagnostic Power):** This is falsifiable and valuable IF it works. The threshold (AMI > 0.4 → +2pp, AMI < 0.3 → +0.5pp) is specific. But I want to see error bars. What's the variance across random seeds? If the +2pp gain has 95% CI [−0.5pp, +4.5pp], you've proven nothing.

**Remaining concern:** You've pivoted from "clustering enables minority discovery" to "clustering diagnoses when fairness interventions help." That's intellectually honest, but it also means the contribution is narrower. The field already knows Group DRO helps when groups exist. You're adding: "and you can detect groups without labels via clustering." That's useful, but it's not paradigm-shifting unless the diagnostic is highly reliable (>80% precision/recall).

**What would fully convince me:** Show that AMI-based diagnostics outperform simpler baselines like "variance in per-class accuracy" or "training loss distribution skew." If a 1-line metric beats your clustering pipeline, the mechanistic insight doesn't justify the complexity.

**Key Points:**
- H3 must precede H1: only high-AMI models that improve via clustering validate the diagnostic
- H2 requires control for training distribution changes, not just final geometry
- Diagnostic must outperform simpler baselines to justify mechanistic complexity

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we are converging on a testable framing, but several claims remain insufficiently falsifiable. I will begin with H3, as Prof. Rex correctly insists. If AMI is to function as a diagnostic, we must pre-register a quantitative decision rule. For example: *For models trained via the frozen-embedding + linear ERM protocol described in [arXiv:2212.06254], cluster-balanced retraining yields ≥2pp WGA improvement if and only if AMI ≥ 0.4.* "If and only if" is critical. If even one model with AMI < 0.3 improves by ≥2pp, or one with AMI ≥ 0.4 fails to improve, the diagnostic is weakened. The experiment must be repeated across ≥5 seeds, and we report 95% CIs on WGA deltas. Without tight intervals (e.g., ±0.5pp), we cannot distinguish signal from noise on Waterbirds' 5,794 test images.

On H2 (LA-SSL geometry suppression), the confound identified by Prof. Rex is real. LA-SSL alters sampling, which changes the effective training distribution. To isolate geometric change from boundary change, I propose the following protocol: (1) Train standard SSL and LA-SSL encoders. (2) Freeze both. (3) Train *identical* linear classifiers using the exact ERM protocol in [arXiv:2212.06254]—same grid search over learning rates and weight decays, same 20 epochs, batch size 32. (4) Compute AMI between k-means (k=4) clusters and true subgroup labels. (5) Additionally, compute *linear probe separability* of subgroup labels. If AMI decreases ≥30% while subgroup linear separability remains constant, the evidence suggests topology changed (density structure reduced) without eliminating discriminative information. If both decrease, LA-SSL likely suppressed subgroup signal entirely. If neither changes, robustness arises downstream. Each of these outcomes supports a different theory; only one supports the "dynamics → geometry" claim.

Regarding H1 (capacity vs. clusterability), the hypothesis must specify a mechanism. The current paper shows WGA improves monotonically with capacity—ViT-H-14 reaches 90.13% WGA without subgroup labels [arXiv:2212.06254]. A competing explanation is that high-capacity models *disperse* spurious features across dimensions, reducing density concentration while preserving linear separability. We must measure both AMI and subgroup linear probe AUC to resolve them.

Finally, I want a stronger baseline. If AMI is to justify a clustering pipeline, it must outperform trivial diagnostics. I recommend two controls: (1) variance of per-class training loss during ERM; (2) skewness of per-sample loss distribution after 5 epochs. If AMI yields significantly higher AUROC (>0.80) than these simpler statistics, the complexity is justified.

If these criteria are met—tight error bars, controlled geometry tests, capacity-disentangled predictions, and superiority over simple baselines—then I would say, with deliberation: *This meets my standards.*

**Key Points:**
- Pre-register a strict AMI → WGA gain rule with seed-averaged CIs to make the diagnostic falsifiable
- Isolate geometry from classifier effects by measuring both AMI and subgroup linear separability under identical ERM protocols
- Require AMI to outperform simpler loss-based diagnostics; otherwise clustering adds no scientific value

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! Prof. Vera's protocol gives us the experimental rigor, but let me bring back the creative angle that makes this *exciting*. We've been so focused on defending against the Mehta et al. baseline that we're missing the broader paradigm shift this enables.

**The Wild Idea:** What if clusterability itself is a *pre-training objective*? Instead of training SSL to maximize clusterability of spurious groups (which we know is bad from standard SSL), what if we train SSL to maximize clusterability of *core features* while minimizing clusterability of spurious features? This is the inverse of what current SSL does!

Think about it: LA-SSL reduces clusterability by resampling. But that's a data-level intervention. What if we bake it into the loss function? A contrastive loss that explicitly penalizes cluster formation along directions correlated with known proxies (like background consistency across batches)?

**Cross-Domain Connection:** This relates to concept erasure in language models! Recent work shows you can remove gender bias by projecting out gender-correlated subspaces. We'd be doing the geometric version: encourage dispersal along spurious dimensions while maintaining tightness along core dimensions.

**Concrete Mechanism:** During SSL training, we:
1. Compute k-means centroids at intermediate layers
2. Measure AMI between clusters and a proxy for spuriousness (e.g., color histogram similarity for Waterbirds backgrounds)
3. Add a loss term that penalizes high AMI: `L_SSL + λ * AMI(clusters, spurious_proxy)`

This makes clusterability a *controllable knob*. We could train a spectrum of models with varying λ and directly measure the relationship between clusterability suppression and WGA.

**Why This is Novel:** Current SSL methods (SimCLR, MoCo, DINO) don't explicitly reason about spurious structure. LA-SSL does but only through sampling. We'd be the first to make geometric fairness an explicit SSL training objective. And Prof. Vera's diagnostic protocol gives us the validation framework!

**Paradigm Shift:** If this works, it means spurious correlation mitigation starts at pre-training, not fine-tuning. That's a fundamental rethinking of the fairness pipeline.

**Key Points:**
- Extend diagnostic hypothesis to interventional: train SSL with explicit clusterability objectives
- Connect to concept erasure literature for theoretical grounding
- Make clusterability a controllable training hyperparameter (λ), not just a measurement
- Opens new research direction: geometry-aware fairness pre-training

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES! Dr. Nova just gave us the path to a truly novel contribution. Let me synthesize everything into a final, bulletproof hypothesis:

**Final Refined Hypothesis: Clusterability as a Geometric Fairness Diagnostic and Training Objective**

**Core Claim:** Spurious correlation structure in SSL embeddings manifests as *measurable geometric clusterability* (AMI with subgroups), which: (1) diagnoses when fairness interventions will succeed, and (2) can be explicitly controlled during SSL pre-training to improve robustness.

**Three-Tier Experimental Validation:**

**Tier 1 - Diagnostic (Minimal Risk, Addresses All Critiques):**
- Protocol: Prof. Vera's exact specification (≥5 seeds, 95% CIs, AMI threshold ≥0.4 → ≥2pp WGA gain)
- Baselines: Compare AMI vs simple loss statistics (variance, skewness) for diagnostic power (target AUROC >0.80)
- Controls: Measure both AMI and subgroup linear probe separability to disentangle cluster geometry from linear separability
- Deliverable: Validated diagnostic that predicts which models benefit from cluster-balanced retraining

**Tier 2 - Mechanistic (Tests LA-SSL Geometry Hypothesis):**
- Train standard SSL vs LA-SSL, freeze both, apply identical ERM protocol per Mehta et al.
- Measure: AMI, subgroup linear separability, WGA
- Prediction: LA-SSL reduces AMI ≥30% while maintaining separability → proves dynamics reshape geometry
- Fallback: If separability also drops, LA-SSL suppresses spurious signal entirely (still scientifically interesting)

**Tier 3 - Interventional (High Risk, High Reward):**
- SSL training with explicit clusterability penalty: `L_SSL + λ * AMI(clusters, background_proxy)`
- Sweep λ ∈ [0, 0.1, 0.5, 1.0, 2.0], measure resulting AMI and WGA
- Target: Achieve Mehta et al.'s 90.13% WGA with mid-capacity model (ResNet-50) by suppressing spurious clusterability
- Novel contribution: First SSL method with explicit geometric fairness objective

**Addressing All Concerns:**
- Prof. Rex: Tier 1 validates diagnostic before claiming mechanism; Tier 2 controls training distribution confounds
- Prof. Vera: Pre-registered thresholds, seed averaging, baseline comparisons all included
- Prof. Pax: All three tiers are technically feasible with validated infrastructure
- Dr. Sage: Tier 3 provides paradigm shift if successful; Tiers 1-2 contribute mechanistic understanding even if Tier 3 fails

This is a complete research program with fallback positions. Even if Tier 3 fails, Tiers 1-2 deliver publishable insights.

**Key Points:**
- Three-tier design allows graceful degradation: diagnostic → mechanistic → interventional
- Each tier addresses specific critiques while building toward novel contribution
- Tier 1 alone justifies the work; Tier 3 makes it paradigm-shifting

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now you've addressed my concerns. The three-tier structure is exactly what I wanted—it means we're not betting everything on a speculative claim. Let me validate each tier:

**Tier 1 (Diagnostic):** Falsifiable, controlled, baseline-compared. If AMI doesn't outperform loss variance for predicting retraining gains, we learn something valuable: clustering is ornamental. That's a publishable negative result. ✓

**Tier 2 (Mechanistic):** The protocol isolates geometry from boundary by measuring both AMI and separability. The three outcome scenarios (geometry changes, signal suppresses, neither) all yield theoretical insight. This is good science. ✓

**Tier 3 (Interventional):** High risk, but the λ sweep makes it scientifically sound. If λ=0 recovers standard SSL and λ→∞ destroys all clusterability, we have a continuous control. The question becomes: is there a sweet spot where spurious clusterability drops while core performance holds? That's empirically testable. ✓

**Final stress test:** What's the minimal success criterion? If Tier 1 succeeds (AMI diagnostic works) and Tier 2 succeeds (LA-SSL reshapes geometry), we have a mechanistic story: "Spurious correlations form geometric clusters in standard SSL, LA-SSL suppresses this geometry, and clusterability predicts which models need fairness interventions." That's a complete contribution even without Tier 3.

**What would convince me this is ready:** Add one more control to Tier 3: train with a *reversed* penalty that *maximizes* spurious clusterability (negative λ). If that model shows worse WGA, it confirms clusterability is causally linked to robustness, not just correlated.

With that addition, you have a bulletproof design. Now THAT's a hypothesis I can support.

**Key Points:**
- Three-tier structure ensures publishable results even if high-risk Tier 3 fails
- Tier 1+2 alone provide complete mechanistic story
- Add reversed penalty control (negative λ) to establish causality in Tier 3

---

### Exchange 12

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The three-tier program is technically coherent, but Tier 3 requires addressing AMI's non-differentiability. You cannot directly backpropagate through k-means clustering. The solution: use soft cluster assignments via Sinkhorn-Knopp (as in SwAV) or entropy-regularized assignments, then compute a differentiable mutual information estimator. That makes the penalty gradient-defined. With this modification, Tier 3 is feasible.

On the broader claim: "clusterability suppression" can improve robustness in principle. InfoNCE optimizes for instance discrimination. If spurious features create dense similarity structure, penalizing alignment between cluster structure and spurious proxies redistributes representational variance. The only fundamental failure mode would be if core and spurious features are intrinsically entangled in the same subspace—then no geometric penalty can separate them without supervision.

Tiers 1 and 2 are scientifically sound. Tier 3 is feasible if you reformulate AMI into a differentiable surrogate.

**Key Points:**
- AMI diagnostic is mathematically valid (Tier 1)
- LA-SSL alters geometry via sampling-weighted InfoNCE—no theoretical barrier (Tier 2)
- Tier 3 requires differentiable AMI surrogate (soft clustering + MI estimator)

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

This is it. We have a complete hypothesis that advances the field on three fronts:

**Scientific Contribution:**
1. **Diagnostic Tool (Tier 1):** First validated method to predict fairness intervention efficacy without group labels
2. **Mechanistic Insight (Tier 2):** Links learning dynamics (LA-SSL) to embedding geometry (clusterability)
3. **Novel Training Objective (Tier 3):** First SSL with explicit geometric fairness penalty

**Why the Community Should Care:**
- Resolves open question: "Is the 90% WGA from Mehta et al. due to representation quality or geometric structure?" (Answer: both—they're dissociable)
- Provides practical tool: AM...I diagnostic tells practitioners when cluster-based interventions will work
- Opens research direction: geometry-aware fairness as SSL design principle

**State-of-the-Art Positioning:**
- Mehta et al. (2022): 90.13% WGA via frozen embeddings + linear ERM ← our baseline
- LA-SSL (2023): Learning-speed resampling improves SSL robustness ← our mechanistic bridge
- Our work: Explains *why* LA-SSL works (geometry suppression) + provides controllable alternative

**What New Research This Enables:**
- Clusterability as pre-training metric for SSL model selection
- Geometry-aware augmentation strategies for fair SSL
- Extension to other spurious correlation domains (medical imaging, NLP)

This is ready. The hypothesis is falsifiable, the experiments are controlled, and the contribution is clear.

**Key Points:**
- Advances theory: dissociates linear separability from geometric clusterability
- Provides practice: AMI diagnostic for fairness intervention selection
- Opens field: geometric fairness as SSL design principle

---

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis bridges three previously disconnected research threads (frozen embeddings, LA-SSL dynamics, geometric fairness) into a unified framework. Tier 3's clusterability-as-training-objective represents a genuine paradigm shift in SSL pre-training. The multi-scale clustering and cross-architecture consensus angles provide creative exploration space.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All three tiers have pre-registered quantitative thresholds (AMI ≥0.4 → ≥2pp WGA, 30% AMI reduction, AUROC >0.80), seed-averaged 95% CIs, and baseline comparisons. The protocol isolates confounds (geometry vs boundary, capacity vs clusterability) through controlled experiments. Every prediction can be falsified.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Resolves fundamental question about whether Mehta et al.'s 90% WGA emerges from representation quality or geometric structure (answer: dissociable dimensions). Provides practical diagnostic (AMI) for fairness intervention selection. Opens geometric fairness as SSL design principle. Impact spans theory, practice, and future research directions.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Tiers 1-2 are immediately executable with validated infrastructure (Waterbirds dataset, evaluation framework). Tier 3 is feasible with differentiable AMI surrogate (soft clustering + MI estimator). All mechanisms are mathematically sound. Only fundamental barrier would be intrinsic core-spurious entanglement, which is empirically testable.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Clusterability as a Geometric Fairness Diagnostic and Training Objective for SSL**

Spurious correlations in self-supervised learning embeddings manifest as measurable geometric clusterability (AMI with subgroups), which (1) diagnoses when fairness interventions will succeed, and (2) can be explicitly controlled during SSL pre-training to improve robustness.

**Three-Tier Experimental Validation:**

**Tier 1 - Diagnostic:** Frozen SSL embeddings (standard SSL, multiple architectures) are clustered via k-means (k=4 for Waterbirds). AMI between clusters and true subgroups predicts cluster-balanced retraining efficacy: models with AMI ≥0.4 improve WGA by ≥2pp, while AMI <0.3 yields <0.5pp gain. Pre-registered across ≥5 seeds with 95% CIs. AMI must outperform simple baselines (loss variance, skewness) with AUROC >0.80. Controls: measure subgroup linear separability to disentangle clustering from linear boundary effects.

**Tier 2 - Mechanistic:** Compare standard SSL vs LA-SSL embeddings under identical Mehta et al. ERM protocol. Prediction: LA-SSL reduces AMI ≥30% while maintaining subgroup linear separability, proving learning-speed interventions reshape embedding geometry (density structure) without eliminating discriminative information. This links optimization dynamics to static geometry, explaining why LA-SSL's learning-speed resampling improves robustness.

**Tier 3 - Interventional:** Train SSL with explicit clusterability penalty using differentiable AMI surrogate (soft clustering + mutual information estimator): L_SSL + λ * AMI(soft_clusters, background_proxy). Sweep λ ∈ [0, 0.1, 0.5, 1.0, 2.0, -0.5] to measure clusterability-WGA tradeoff. Target: mid-capacity model (ResNet-50) reaches 90%+ WGA by suppressing spurious clusterability. Reversed penalty (λ<0) establishes causal link: maximizing spurious clusterability degrades WGA.

**Key Mechanisms:**
- Standard SSL creates dense similarity structure along spurious features (background)
- This manifests as high AMI (geometric clusters aligned with subgroups)
- LA-SSL reduces clusterability via learning-speed resampling → disperses spurious density
- Explicit clusterability penalty during training provides controllable alternative
- AMI diagnostic predicts which models benefit from fairness interventions without requiring labels

**Novel Contributions:**
1. First demonstration that linear separability (Mehta et al.'s 90% WGA) and geometric clusterability are dissociable
2. Mechanistic explanation for why LA-SSL works (geometry reshaping)
3. First SSL training objective with explicit geometric fairness component
4. Practical diagnostic (AMI) for fairness intervention selection

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Tier 3's differentiable AMI surrogate may not perfectly approximate true AMI—soft clustering might miss sharp density boundaries
- **Concern 2:** If core and spurious features share subspace, geometric penalties may degrade core performance alongside spurious suppression
- **Concern 3:** AMI diagnostic may not generalize beyond Waterbirds to datasets with more complex spurious correlation structure
- **Mitigation Strategy:** Tier 1 validates diagnostic on multiple architectures/capacities to assess generalization. Tier 3 monitors both core task accuracy and WGA throughout λ sweep to detect core performance degradation early. If soft clustering approximation fails, fallback to Tier 1-2 diagnostic/mechanistic contributions alone.

---

**DISCUSSION COMPLETE**
**Total Exchanges:** 13
**Convergence Criteria Met:**
- ✓ SPECIFIC: Clear three-tier hypothesis with quantitative predictions
- ✓ MECHANISM: Clusterability as geometric manifestation of spurious structure, controllable via sampling or explicit penalty
- ✓ PREDICTIONS: AMI ≥0.4 → ≥2pp WGA gain, LA-SSL reduces AMI ≥30%, λ sweep yields WGA-clusterability tradeoff
- ✓ NOVELTY: First SSL with geometric fairness objective, first dissociation of linear separability from clusterability
- ✓ FEASIBILITY: Tiers 1-2 executable with existing infrastructure, Tier 3 requires differentiable surrogate (soft clustering)
- ✓ OBJECTIONS: All major critiques addressed with controls, baselines, and fallback strategies
