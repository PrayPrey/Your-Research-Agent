# Phase 2A Research Discussion Log
# Workflow: phase2a-dialogue v10.0.0 (Self-Contained Tikitaka Loop)
# Generated: 2026-05-08T06:00:00Z
# Gap: Gap 1 — No Static Pre-Fine-Tuning Signal for Per-Layer LoRA Rank Allocation

## Research Briefing

**Research Question:**
Does layer-wise MLP activation sparsity in LLaMA-3-8B predict per-layer LoRA rank sensitivity during fine-tuning, such that a sparsity-guided adaptive rank allocation strategy achieves ≥95% of uniform-r=16 GLUE quality at ≤60% of total LoRA parameter count?

**Key Context:**
- Prior failed runs (Runs 1-2): KV cache eviction via attention Gini/entropy → both FAILED due to directional inversion and degenerate entropy. Full domain pivot warranted.
- New direction: Static pre-fine-tuning activation sparsity (fraction of near-zero MLP activations) as rank predictor — BEFORE fine-tuning begins, zero gradient computation needed.
- Critical gap: ALL existing adaptive rank methods (AdaLoRA, ARD-LoRA, La-LoRA, DyLoRA, Sensitivity-LoRA) use TRAINING-TIME signals. No paper demonstrates static calibration-based rank prediction.
- Infrastructure: HF PEFT `rank_pattern` dict directly supports per-layer rank specification. Forward hooks for sparsity measurement are trivial.

**Reference Papers Available:**
- P1: AdaLoRA (Zhang et al., 2023) — arXiv:2303.10512 — training-time SVD rank allocation
- P2: DyLoRA (Valipour et al., 2022) — arXiv:2210.07558 — dynamic search-free rank, GLUE evaluation
- P3: TEAL — Training-Free Activation Sparsity in LLMs (Liu et al., 2024) — arXiv:2408.14690
- P4: Intrinsic Dimensionality (Aghajanyan et al., 2021) — arXiv:2012.13255 — theoretical basis for low-rank
- P5: Lazy Neuron Phenomenon (Li et al., 2022) — arXiv:2210.06313 — MLP activation sparsity in transformers
- P6: ReLU Strikes Back (Mirzadeh et al., 2023) — arXiv:2310.04564 — activation sparsity across LLMs

**Feasibility Constraints (MANDATORY — Pipeline-Enforced):**
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- ONLY existing real datasets (GLUE, Alpaca/FLAN-mini) and existing benchmarks

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if the key insight we've been missing is this: the entire literature on adaptive LoRA rank has been asking "which layers need more rank AFTER we've already started training?" But what if layers are *self-announcing* their rank requirements before any gradient has flowed? 

Consider what activation sparsity actually means mechanistically. In LLaMA-3-8B's MLP layers, the SiLU gate function creates a gating mechanism — activations that fall below a threshold are effectively zeroed out. A layer with 80% sparse activations is operating in a low-dimensional subspace by nature. When you apply LoRA to such a layer, you're trying to redirect a transformation that already lives in low-dimensional space. High rank there is redundant by construction. A layer with 30% sparsity — dense activations throughout — is projecting into a rich, high-dimensional space where fine-tuning requires genuine expressive capacity.

This is the conceptual leap: **activation sparsity is a proxy for the effective intrinsic dimensionality of the layer's representations**. And intrinsic dimensionality [Aghajanyan et al., 2021] is exactly what LoRA rank should track! The theoretical chain is: sparsity → effective rank of activation subspace → required LoRA rank for quality-preserving fine-tuning. What excites me most is that this chain requires exactly ONE calibration forward pass — no gradient, no SVD, no training iteration.

Now the novel angle that truly sets this apart from Act-LoRA (which uses L2-norm to BINARY-select layers): we're proposing CONTINUOUS rank allocation scaled by sparsity magnitude. High sparsity (say, 80%) → rank 2. Medium sparsity (50%) → rank 8. Low sparsity (20%) → rank 16. The rank profile is derived analytically from the sparsity profile, and the total parameter budget is preserved by design.

And here's the paradigm shift that differentiates this from EVERYTHING in the AdaLoRA lineage: the rank decision is made BEFORE the first training step. No iterative rank reassignment. No SVD overhead during training. No meta-objective for scaling factors. Just a single observation of the model's natural activation patterns on a general calibration set (Alpaca/FLAN-mini) — and you have your rank schedule for free.

**Key Points:**
- Activation sparsity proxies effective intrinsic dimensionality per-layer — theoretically grounded in [Aghajanyan et al., 2021]
- Continuous rank scaling (not binary layer selection like Act-LoRA) — occupies a distinct position in the design space
- Rank schedule derived BEFORE training — eliminates ALL training-time overhead of AdaLoRA/ARD-LoRA/DyLoRA
- Single calibration forward pass on GLUE-appropriate data (Alpaca/FLAN-mini) — no synthetic data, no new benchmarks needed

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The proposal is intellectually coherent: sparsity → reduced effective activation subspace → lower required adaptation rank. However, coherence is not evidence. The critical question is: *what specific empirical observation would falsify the sparsity→intrinsic-dimension→rank chain?* At present, the argument assumes that activation sparsity during a single forward pass reliably estimates the dimensionality of the function class needed for downstream adaptation. The evidence from [Aghajanyan et al., 2021] shows that intrinsic dimension varies by architecture and task, and importantly, that structure-aware allocation (SAID) significantly outperforms structure-agnostic allocation (DID). This already cautions us: intrinsic dimension is not merely a global property but depends on structured parameter interactions. Sparsity alone may be an insufficient statistic.

The evidence suggests we must decouple three quantities that are currently conflated: (1) activation sparsity (fraction of near-zero units), (2) numerical rank of the activation covariance matrix, and (3) minimal LoRA rank achieving ≥90% of full fine-tuning performance. Your hypothesis predicts a monotonic relationship among these. Therefore, the first experiment should be purely diagnostic: across layers in LLaMA-3-8B, compute activation sparsity on a calibration set, estimate empirical activation covariance rank, and then sweep LoRA ranks per layer while freezing others to identify the minimal rank preserving 90% task performance. The hypothesis is falsified if sparsity correlates weakly (Spearman ρ < 0.3) with minimal effective LoRA rank, or if covariance rank explains substantially more variance than sparsity.

A deeper stress test concerns task dependence. Intrinsic dimension in [Aghajanyan et al., 2021] varies across MRPC and QQP despite identical architectures. If sparsity is measured once on Alpaca/FLAN-mini and fixed before training, your hypothesis implies that the optimal rank schedule should transfer across downstream tasks with minimal degradation. What would disprove this? If task-specific rank reallocation (post hoc AdaLoRA-style adaptation) yields >1–2% absolute improvement over the precomputed sparsity schedule under equal parameter budgets, then sparsity is not capturing task-conditioned intrinsic dimension.

We must also identify edge cases. Consider layers with high sparsity but high directional sensitivity — sparse gating where the active units rotate dramatically across samples. Such a layer may exhibit high sparsity yet span a high-dimensional union of subspaces. Thus, the calibration must measure not only mean sparsity but stability of the active set across samples (Jaccard similarity of active neurons). A decisive experiment would compare three allocation rules under equal budgets: (A) sparsity-proportional rank, (B) covariance-effective-rank-proportional, and (C) random allocation. If (B) matches or exceeds (A), then sparsity is merely a crude proxy for a richer second-order statistic.

**Key Points:**
- Define falsifiable criteria: correlation between sparsity and minimal LoRA rank must be strong and predictive of ≥90% performance thresholds.
- Control for confounds: compare against covariance-based effective rank and task-specific reallocation baselines.
- Test edge cases: measure active-set stability to detect sparse-but-high-dimensional unions of subspaces.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

🔬 Prof. Vera has identified the right fault lines — but I want to press harder on one she mentioned in passing, because it's the *load-bearing assumption* of this hypothesis.

Looking at DyLoRA [Valipour et al., 2022] Experiments & Results carefully: DyLoRA trains across a *range* of ranks (r_min to r_max) simultaneously and achieves 4-7x faster rank search. The GLUE results show rank matters differently per task — SST-2 shows minimal degradation from rank 1 to rank 8 (94.5 → 94.36), while CoLA is more rank-sensitive. This reveals something uncomfortable: **the "correct" rank is not a property of the layer alone — it's a joint property of (layer, task)**. Sparsity measured on Alpaca/FLAN-mini calibration data captures the model's static activation geometry, but fine-tuning quality under a given rank is a function of the downstream task's loss landscape. These are not the same thing.

The Discussion & Conclusion of DyLoRA explicitly notes that "rank settings influence task-specific performance." If I run a calibration forward pass on general instruction data (Alpaca) and measure sparsity, I'm measuring activation geometry for *that input distribution*. GLUE SST-2 (sentiment) and MNLI (NLI) have very different input distributions. A layer that is 70% sparse on Alpaca may be only 40% sparse on long-form NLI premises. The sparsity measurement itself may not be stable across input distributions, and therefore the rank allocation it produces may not be optimal for the actual fine-tuning task.

So the hypothesis needs tighter scope: it must specify what calibration distribution is used AND demonstrate that the rank schedule derived from THAT distribution transfers to GLUE SST-2/MNLI. If calibration must be task-specific, the method becomes another form of task-aware rank selection. If task-agnostic, the gap between calibration and fine-tuning distribution is a genuine confound needing direct validation. A falsifiable version: if mean layer sparsity on 512 Alpaca samples achieves Pearson r ≤ -0.5 with per-layer rank sensitivity (delta-accuracy from r=16 to r=4 on SST-2), and this holds for MNLI too, THEN the sparsity signal is task-transfer-robust.

I'll also flag one entirely unstated assumption: the rank sensitivity measurement itself. "Delta-accuracy when reducing rank from r=16 to r=4" requires separate fine-tuning runs per layer with all others fixed at r=16. We're measuring *marginal* rank sensitivity, not *joint* rank sensitivity — two very different quantities. A layer may be insensitive in isolation but critical when all other layers are also low-rank. The experiment must specify this clearly.

**Key Points:**
- Rank sensitivity is task-conditioned (DyLoRA shows rank-task interaction) — sparsity measured on Alpaca may not transfer to GLUE distribution without explicit validation
- The calibration distribution must be specified and its transfer to fine-tuning tasks must be explicitly tested
- Rank sensitivity measurement protocol (marginal vs. joint) must be defined clearly before experiments run

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The sparsity → intrinsic dimension → required LoRA rank chain is *plausible*, but it is not automatically mechanically valid. Sparsity in an MLP after SiLU gating tells you how many neurons are near zero **for a given input distribution**. It does **not** directly tell you the rank of the Jacobian of the layer with respect to its weights, which is what ultimately governs how many directions LoRA needs to modify to affect the function. Those are related quantities — but not identical. That's the first theoretical gap.

Here's what worries me: activation sparsity is a first-order statistic. LoRA rank is about how many *independent parameter-space directions* are required to induce useful function changes. A layer could be 80% sparse per sample yet activate different 20% subsets across samples, forming a high-dimensional union of subspaces (as Prof. Vera noted). In that case, the *average* sparsity is high, but the *span across the dataset* could be large. In that regime, a low LoRA rank would be insufficient in principle. So unless you measure cross-sample covariance or active-set stability, sparsity alone may be an underpowered proxy.

Now, comparing this to DyLoRA [Valipour et al., 2022]: their mechanism explicitly acknowledges that rank sensitivity is task-conditioned. They train across a sampled rank b ∈ [r_min, r_max] and compute loss per truncated rank, effectively learning a parameterization that is stable across ranks. The empirical table shows SST-2 is relatively insensitive to rank (94.5 vs. 94.36 at rank 8), whereas CoLA is more sensitive. That means the minimal effective rank is not purely structural; it interacts with the loss landscape of the task. So if your sparsity-based schedule is computed pre-training on Alpaca and then frozen, the feasibility question is: **can a task-agnostic statistic approximate a task-conditioned optimum?** It might — but only if rank sensitivity is dominated by architectural geometry rather than task-specific gradients. That's an empirical question, not an assumed truth.

Technically, though, your proposal is implementable and coherent. A single calibration forward pass to measure per-layer activation sparsity is straightforward and stable. Continuous rank allocation under a fixed total budget is mathematically trivial. There is no physical or optimization-theoretic impossibility here. The real feasibility hinge is *predictive power*. If sparsity explains a meaningful fraction of variance in minimal effective rank across layers (say R² ≥ 0.4), then this is scientifically viable. So here's the clean feasibility test: (1) compute per-layer sparsity and covariance effective rank on calibration set; (2) measure minimal LoRA rank achieving ≥90% of full-rank performance per layer; (3) regress minimal rank against sparsity vs. covariance-effective-rank. If sparsity performs competitively, this could work.

**Key Points:**
- Activation sparsity is not mathematically equivalent to required LoRA rank; the link must be empirically validated.
- Task-conditioned rank sensitivity (as seen in DyLoRA) challenges purely task-agnostic allocation.
- The proposal is technically feasible in principle, but viability depends on whether sparsity meaningfully predicts minimal effective rank (R² ≥ 0.4 threshold).

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this contribution actually mean for the field if it succeeds? Because Prof. Vera, Prof. Rex, and Prof. Pax are all raising implementation-level falsification tests — all valid — but they're spending less time on whether the core scientific *contribution* is meaningful even if confirmed.

The Discussion & Conclusion of [Aghajanyan et al., 2021] makes a striking point: "pre-training appears to simplify subsequent learning tasks by optimizing the intrinsic dimension of representations." Larger models have *lower* intrinsic dimension — a counterintuitive but empirically robust finding. This suggests that the intrinsic dimension of fine-tuning is a real, architecture-dependent quantity that varies per model and, crucially, per layer (as SAID significantly outperforms DID in their ablation). What this means for our hypothesis is actually *encouraging*: if layer-wise intrinsic dimension is real, and if sparsity is even a moderate proxy for it (not perfect — just correlated), then sparsity-guided rank allocation is occupying a genuinely unexplored position in the design space.

Now let's position this against the field. Every existing method — AdaLoRA, ARD-LoRA, La-LoRA, Sensitivity-LoRA — requires at minimum a full forward+backward pass to compute rank allocation. Even DyLoRA, the most efficient of the lot, trains across a rank range simultaneously (still requiring multiple gradient updates to learn the rank). This work proposes rank allocation from a SINGLE forward pass on unlabeled calibration data. That is a qualitative improvement in the cost curve. Practitioners fine-tuning LLMs on edge devices or under strict compute budgets currently cannot afford AdaLoRA-style rank search. A static sparsity-based schedule that achieves 95% of uniform-r=16 quality at 60% parameter count is genuinely deployable in those settings.

This matters because the field is moving toward *foundation model personalization at scale*: thousands of users fine-tuning the same base model for different tasks. In that setting, a one-time sparsity measurement per model architecture (not per task, not per user) becomes a shared infrastructure resource. Every user benefits from the sparsity profile of LLaMA-3-8B measured once. That's a network effect that training-time methods cannot replicate.

The research opens new questions that will advance the field: Does the sparsity-rank correlation generalize across model families (Mistral, Gemma, Phi)? Does quantization (QLoRA with NF4) change the activation geometry and thus the sparsity profile? These are genuinely interesting follow-on directions. This matters because it opens a new characterization of LLM layers by their activation density as a fine-tuning-relevant property.

**Key Points:**
- Contribution is qualitatively distinct: zero training overhead for rank allocation — from calibration forward pass, not gradient
- Field significance: enables personalized fine-tuning at scale (one sparsity measurement benefits all users of a base model)
- Opens new research directions: cross-architecture generalization, quantization-sparsity interaction, continual fine-tuning rank re-estimation

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Alright. Let's tighten this until it either survives or collapses cleanly.

Here's where this still breaks down: you are implicitly treating *layer rank requirement* as a structural property of the pretrained model, while DyLoRA's evidence makes it clear that rank sensitivity is task-conditioned. In their GLUE results, SST-2 barely moves between rank 1 and rank 8 (94.5 → 94.36), while CoLA shows larger sensitivity [Valipour et al., 2022]. That's not noise — that's task–rank interaction. So show me the evidence that your sparsity profile, measured once on Alpaca, predicts rank sensitivity on both SST-2 *and* CoLA. If it only predicts one and not the other, your claim must be narrowed to "distribution-aligned tasks," not "intrinsic layer property."

Second fracture line: you are still conflating *marginal* and *joint* rank sensitivity. If you measure minimal rank per layer while all other layers are fixed at high rank, you are estimating marginal importance. But real fine-tuning runs allocate rank jointly under a global parameter budget. A layer that looks unimportant alone may become critical when others are compressed. What would convince me is this: under a fixed total budget (say equivalent to uniform r=8), compare three allocations — (A) uniform, (B) sparsity-proportional, (C) oracle allocation derived from exhaustive search. If sparsity achieves ≥95% of oracle performance across two tasks, then you've demonstrated joint predictive power. Without this, the hypothesis is under-tested.

Now let's address the core theoretical gap Pax raised. Activation sparsity is a per-sample first-order statistic. LoRA rank governs how many independent weight-space directions can alter outputs. The missing bridge is the *Jacobian spectrum*. If sparsity really proxies required rank, then layers with higher sparsity should exhibit a faster decay in singular values of the empirical Jacobian with respect to LoRA parameters. That's a measurable prediction. Estimate the top-k singular values of the layer output Jacobian on a calibration set. If sparsity correlates with Jacobian spectral decay rate (top-4 singular values explaining ≥80% variance), you've mechanistically grounded the claim.

Here's what would convince me: Spearman ρ ≤ −0.5 between sparsity and minimal joint rank across *two distinct tasks*; sparsity-based allocation achieving ≥95% of oracle joint allocation under equal parameter budget; a demonstrated link between sparsity and Jacobian spectral decay.

**Key Points:**
- Rank sensitivity is task-conditioned (per DyLoRA); sparsity must predict across multiple tasks or the claim must narrow.
- Marginal rank sensitivity is insufficient — joint budgeted allocation must be evaluated against oracle.
- A mechanistic bridge (e.g., correlation with Jacobian spectral decay) is required to justify sparsity as a proxy for required LoRA rank.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — and I think Prof. Rex's challenges, precisely because they're so sharp, give us exactly the path to a bulletproof hypothesis. Let me defend the core and propose concrete refinements to each concern.

On the Jacobian spectral decay point: Prof. Rex is asking for a mechanistic bridge, and [Aghajanyan et al., 2021] in their Methodology provides it. They demonstrate that intrinsic dimensionality is estimated by measuring at what subspace dimension d a random projection achieves 90% of full fine-tuning performance. The SAID approach scales intrinsic dimension per-layer, and the Experiments & Results show RoBERTa-Large needs only d=207 on MRPC (structure-aware). Now: what predicts low intrinsic dimension at the layer level? Their Discussion & Conclusion is explicit: "pre-training appears to simplify subsequent learning tasks by optimizing the intrinsic dimension of representations." The mathematical story is this — after pre-training, layers whose MLP activations are sparse have already compressed their representation to a low-dimensional attractor. The relevant fine-tuning directions live in this compressed subspace. Sparsity is NOT a proxy for Jacobian rank directly — it IS a proxy for the dimensionality of the attractor subspace that pre-training produced. And that attractor dimension IS what determines the intrinsic fine-tuning dimension. The chain is tighter than Prof. Rex suggests.

On task-conditioned rank sensitivity: Prof. Rex is right that SST-2 and CoLA show different rank sensitivity in DyLoRA. But notice what DyLoRA's results actually imply: SST-2's rank insensitivity means MOST layers are low-rank-sufficient for sentiment. CoLA's sensitivity means SOME layers genuinely need higher rank for grammaticality. Our hypothesis doesn't claim that ALL tasks will show identical sparsity-rank correlation — it claims that sparsity identifies WHICH layers need higher rank within each task. A layer that is 80% sparse should need low rank for BOTH SST-2 AND CoLA; a layer that is 20% sparse may need higher rank for CoLA but less so for SST-2. The correlation direction should hold across tasks even if the magnitude varies.

I propose refining the hypothesis as follows: "Under LLaMA-3-8B, layer-wise MLP activation sparsity (measured on 512 Alpaca samples) negatively correlates with per-layer joint LoRA rank sensitivity (Pearson r ≤ -0.4) on both SST-2 and MNLI under a fixed total budget equal to 60% of uniform-r=16 parameters, achieving ≥95% aggregate GLUE performance." This addresses Prof. Rex's joint vs. marginal concern by specifying a fixed total budget experiment, and narrows to two representative GLUE tasks with different task types (classification + NLI) to test cross-task transfer.

The Jaccard active-set stability concern can be added as a diagnostic sub-hypothesis: "Layer-wise sparsity and active-set stability (cross-sample Jaccard similarity of neurons above threshold) together explain ≥60% of variance in minimal rank across layers." This keeps the main hypothesis clean while validating the confound Prof. Rex and Prof. Pax identified.

**Key Points:**
- Theoretical chain via [Aghajanyan et al., 2021] SAID: sparsity → attractor subspace dimensionality → fine-tuning intrinsic dimension → required LoRA rank
- Refined hypothesis scope: joint budget allocation (not marginal), two tasks (SST-2 + MNLI), 60% parameter budget, ≥95% GLUE threshold
- Active-set stability as diagnostic sub-hypothesis to address the sparse-but-high-dimensional confound

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The refined hypothesis is now close to testable, but precision must increase further. The evidence from [Aghajanyan et al., 2021] establishes that intrinsic dimension can be operationalized as the minimal subspace dimension d required to reach 90% of full fine-tuning performance using a projection. SAID results demonstrate that layer-aware scaling significantly reduces required dimension (e.g., RoBERTa-Large MRPC: 207 vs. 774 under DID). This confirms that *layer structure matters*. However, they do not measure activation sparsity. Therefore, your claim introduces a new proxy variable. The burden is to demonstrate that sparsity predicts the *same quantity* that SAID operationalizes — minimal effective subspace dimension.

To avoid ambiguity, we must define the dependent variable rigorously. "Minimal joint LoRA rank" should be defined as: the smallest per-layer rank allocation under a fixed global parameter budget B such that validation performance ≥95% of full fine-tuning. Then, for each layer ℓ, define joint sensitivity as the performance drop when its allocated rank is reduced by Δr while holding total budget constant via redistribution. The central prediction: Spearman ρ ≤ -0.5 between layer sparsity and joint sensitivity across layers, replicated on two tasks with distinct supervision signals (SST-2 and MNLI). If ρ > -0.2 on either task, the hypothesis fails.

The mechanistic bridge is critical. For each layer, compute the empirical Jacobian of outputs with respect to LoRA parameters on a calibration set. If sparsity truly proxies intrinsic dimension, then higher sparsity should predict steeper spectral decay (top-4 singular values explaining ≥80% variance). This is the Achilles' heel: if Jacobian spectra are flat in highly sparse layers, the theoretical chain collapses regardless of downstream performance. Also control for gradient magnitude concentration as an alternative mechanism — perform variance partitioning with sparsity, active-set stability, and gradient norm as predictors. Sparsity must explain unique variance ≥20% beyond gradient norm.

Cross-task generalization must be explicitly falsifiable: measure sparsity once on Alpaca, derive allocation, apply unchanged to SST-2 and MNLI, predefine success as ≥95% of oracle joint allocation on *both* tasks. One task passing and one failing means distribution-aligned, not intrinsic — not partial credit.

**Key Points:**
- Define minimal joint LoRA rank and joint sensitivity precisely under a fixed global budget with binary success criteria.
- Mechanistic falsification: sparsity must predict Jacobian spectral decay (ρ ≤ −0.5; ≥80% variance in top-4 singular values) or the theory collapses.
- Control for alternative explanation (gradient magnitude); require sparsity to explain unique variance in minimal rank across two distinct tasks.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! And I want to use Prof. Vera's rigorous framework to actually reframe the hypothesis in a way that makes it STRONGER, not just more cautious.

Here's the creative pivot: we've been debating whether sparsity predicts rank because of theoretical purity. But DyLoRA's Discussion & Conclusion reveals something we've been underutilizing [Valipour et al., 2022]: DyLoRA explicitly acknowledges that "careful selection of distribution parameters" (the rank sampling distribution p_B) influences which rank range is learned. Their most interesting limitation is that they still need to set r_min and r_max by hand. What if sparsity doesn't need to perfectly predict intrinsic dimension — it just needs to predict the *ordering* of layers by rank sensitivity? If high-sparsity layers consistently rank among the bottom-k in rank sensitivity (regardless of exact rank values), the allocation problem becomes much more tractable.

This is a ranking-based framing, not a correlation-based one. We don't need Pearson r ≤ -0.5 on an absolute scale — we need Kendall's τ ≥ 0.4 on the ordinal ranking of layers by rank sensitivity vs. by activation sparsity. That's a weaker but more practically useful claim: "if you sort layers by sparsity and allocate ranks in inverse order, you'll get close to optimal." This is directly testable without Jacobian spectral analysis, without covariance estimation — just sort layers by sparsity, allocate ranks inversely, and compare to uniform LoRA on SST-2/MNLI under 60% parameter budget.

The Jacobian spectral decay test Prof. Vera proposes is excellent but complex to implement. The pragmatic test is much simpler and more publishable in an ICLR workshop context: (1) measure sparsity via forward hooks in one pass, (2) sort layers, (3) allocate ranks inversely proportional to sparsity under 60% budget constraint, (4) fine-tune with HF PEFT rank_pattern, (5) compare against uniform r=16. If performance ≥ 95%, the claim is: "Layer sparsity ranking provides a sufficient proxy for rank allocation without training-time computation." That's clean, falsifiable, and practically impactful.

What's genuinely new here — and I can't emphasize this enough — is the zero-training-cost paradigm. DyLoRA costs O(training_iterations × rank_range) comparisons. AdaLoRA costs O(training_iterations) with SVD overhead. Our approach costs O(calibration_forward_passes). That's a fundamentally different point on the cost curve. The novelty isn't the correlation per se — it's that a static architectural property (sparsity) can substitute for a dynamic optimization signal (training gradients) for rank allocation. THAT is what makes this publishable even if the correlation is moderate.

**Key Points:**
- Reframe to ranking-based claim (Kendall's τ ≥ 0.4) — weaker but more robust and practically useful than exact correlation
- Pragmatic experiment: sort layers by sparsity → allocate ranks inversely → fine-tune with HF PEFT rank_pattern → compare vs. uniform r=16
- Core novelty is zero-training-cost paradigm, not the correlation magnitude — this is the publishable claim regardless of exact correlation strength

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. The ranking pivot is smarter. But here's where this still breaks down.

You're proposing Kendall's τ ≥ 0.4 between sparsity ranking and rank-sensitivity ranking. Fine. But rank-sensitivity itself must be defined *jointly under budget*, or the ranking is meaningless. DyLoRA's GLUE results show task-conditioned rank behavior — SST-2 barely moves from rank 1 to 8 (94.5 → 94.36), while CoLA shifts more noticeably [Valipour et al., 2022]. That tells us rank effects are subtle and sometimes flat. In a flat regime, any ranking signal will look "good" because the ground-truth ordering is noisy. So show me this: compute Kendall's τ only on layers whose joint sensitivity exceeds a minimal effect size (≥0.5% accuracy drop when perturbed under fixed budget). Otherwise, you're correlating sparsity with noise.

Second issue: you're celebrating "zero-training-cost," but DyLoRA already reduces search cost by training once across a rank distribution [Valipour et al., 2022, Discussion & Conclusion]. Your advantage is only real if sparsity-based allocation *outperforms uniform rank under equal parameter count without any tuning*. So I want three baselines under identical 60% budget: (A) uniform allocation, (B) random allocation averaged over 10 seeds, (C) sparsity-ranked allocation. If (C) does not significantly beat (A) and (B) on both SST-2 and MNLI, then your signal isn't practically useful.

Now the distribution-robustness claim. Measure sparsity on *two* calibration sets (Alpaca and WikiText). If the induced layer rankings differ substantially (Kendall's τ < 0.6 between calibration sources), then sparsity is distribution-sensitive and your "intrinsic layer property" framing collapses. Stability across calibration distributions is non-negotiable. And don't dodge mechanism entirely: after fine-tuning with r=16, compute the singular values of learned ΔW per layer. If high-sparsity layers have faster singular value decay (top-4 explaining ≥80% Frobenius norm), you've demonstrated they *use* less rank in practice. That's a tractable mechanistic check.

**Key Points:**
- Ranking must be evaluated only on layers with meaningful joint sensitivity (≥0.5% accuracy drop); otherwise τ is inflated by noise.
- Sparsity allocation must beat uniform and random baselines under identical parameter budgets on multiple tasks.
- Distribution stability and alignment with learned ΔW spectral decay are required to justify sparsity as a structural, mechanistic signal.

---

### Exchange 11

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me separate what's technically achievable from what Prof. Rex has asked for, because some of his requirements are very tractable and others need clarification.

Looking at DyLoRA's Experiments & Results: they evaluate on GLUE (SST-2, CoLA, QQP) with RoBERTa and GPT-2 across more than 200 experiments. The key insight I draw is that their training regime runs once with rank sampling across [r_min, r_max] — still requiring full fine-tuning. Our approach needs only ONE additional step before training: the calibration forward pass. This is genuinely architecturally simpler. The question is whether "simpler" translates to "competitive." Prof. Rex's three-baseline demand (uniform, random, sparsity-ranked under identical 60% budget) is exactly the right feasibility check, and it's implementable with HF PEFT's rank_pattern in a straightforward way.

The ΔW spectral decay check is also tractable. After fine-tuning with r=16, compute torch.linalg.svd on each layer's ΔW = B×A. The singular value spectrum is cheap to compute and directly tests whether high-sparsity layers learned low-effective-rank updates. This doesn't require Jacobian computation — just SVD of the learned adapter matrices post-hoc. If top-4 singular values explain ≥80% Frobenius norm in high-sparsity layers vs. <60% in low-sparsity layers, that's a mechanistically grounded finding. This is both feasible and theoretically clean.

The calibration distribution stability check (Alpaca vs. WikiText Kendall's τ ≥ 0.6) is also tractable and takes less than 10 minutes — just one additional forward pass on WikiText samples. This should be included as a validation step, not an afterthought.

What IS technically important: the SiLU activation in LLaMA-3-8B is not hard-sparse like ReLU. It produces soft sparsity where values are small but nonzero. The threshold ε (epsilon for "near-zero") needs careful calibration. The TEAL paper [Liu et al., 2024] uses magnitude-based thresholding at 40-50% model-wide sparsity with minimal degradation — we should use a comparable threshold (|activation| < 0.01 or 0.1) and report sensitivity to ε as a robustness check. This is a non-trivial implementation detail but technically sound.

**Key Points:**
- Three-baseline comparison (uniform, random, sparsity-ranked under 60% budget) is technically feasible with HF PEFT rank_pattern
- ΔW spectral decay check is tractable post-hoc (torch.linalg.svd on learned adapter matrices) — clean mechanistic validation
- SiLU soft-sparsity threshold selection needs calibration; use TEAL methodology as reference and report ε sensitivity

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

The ranking reformulation is acceptable — but only if we preserve a strict definition of the quantity being ranked. In [Aghajanyan et al., 2021], intrinsic dimension is operationalized as the minimal subspace dimension d required to reach 90% of full fine-tuning performance. SAID demonstrates that incorporating layer structure reduces required d substantially (RoBERTa-Large MRPC: 207 vs. 774 under DID). The evidence suggests that *layer structure changes effective dimensionality*. Your proposal must therefore define "rank sensitivity" analogously: for each layer ℓ, measure the minimal decrement Δr_ℓ under a fixed global budget B that causes ≥0.5% absolute validation accuracy drop relative to the joint optimum. Only layers exceeding this threshold enter the Kendall's τ computation.

Falsifiability: Under a 60% global LoRA parameter budget, sparsity-ranked allocation will achieve ≥95% of the oracle joint allocation performance on *both* SST-2 and MNLI, and will significantly outperform (p < 0.05 over 5 seeds) both uniform and random allocations. If this condition fails on either dataset, the hypothesis is rejected. Calibration-source stability: compute sparsity rankings from Alpaca and WikiText. If Kendall's τ < 0.6 between these rankings, sparsity is distribution-dependent and cannot be framed as an intrinsic architectural signal.

Mechanistically: after training with r=16, compute SVD of each learned ΔW_ℓ. If sparsity genuinely proxies effective dimension, then high-sparsity layers should exhibit steeper spectral decay (top-4 singular values explaining ≥80% Frobenius norm) while low-sparsity layers do not. If spectral decay does not differ systematically by sparsity ranking (Spearman ρ < 0.4), the mechanistic bridge collapses. Performance alone is insufficient; mechanism matters. Also control for gradient magnitude — sparsity must explain ≥20% unique variance beyond gradient norm in multiple regression.

**Key Points:**
- Define rank sensitivity under fixed global budget with ≥0.5% effect threshold; compute Kendall's τ only on sensitive layers.
- Require sparsity-ranked allocation to outperform uniform and random baselines under identical 60% budget on two tasks, with calibration-source stability (τ ≥ 0.6).
- Mechanistic validation: sparsity must predict steeper ΔW spectral decay and explain unique variance beyond gradient magnitude.

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me bring this to the question of significance — because I think the discussion has been so focused on falsification criteria that we've lost sight of why this matters to the field.

[Aghajanyan et al., 2021] in their Introduction & Motivation state a striking finding: "pre-trained models already reside close to the solution" — the intrinsic dimension of fine-tuning is small because pre-training has done much of the representational work. Their Discussion & Conclusion makes this explicit: the success of parameter-efficient fine-tuning is explained by the fact that optimal fine-tuning directions are already encoded in the model's geometry. This is the theoretical foundation that makes our hypothesis scientifically significant: if layer-wise geometry (proxied by sparsity) predicts rank requirements, then we are exploiting a property the model acquired during pre-training, not during fine-tuning. This is a finding about *how* pre-training shapes fine-tuning efficiency — that's a genuine scientific contribution beyond parameter-efficiency.

The field significance is this: today, practitioners choosing LoRA rank face an uninformed decision. They pick r=8 or r=16 based on memory budget and hope. AdaLoRA improves on this but requires a full training run. Our work offers a new option: measure the model's activation geometry once (10 minutes, no gradients), get a rank schedule that transfers across tasks, and deploy it. This opens the door to a new class of "structural priors" for PEFT — properties of the pre-trained model that inform fine-tuning configuration without any task-specific computation. That's a research direction, not just a technique.

Prof. Vera and Prof. Rex have now defined a very rigorous experimental protocol. I endorse the full criterion set — but I want to add one positive framing: if we pass, we've demonstrated that pre-training geometry (activation sparsity as a proxy for layer-wise intrinsic dimension) is a sufficient statistic for rank allocation. That's a theorem-like claim about the structure of fine-tuning, not just a benchmark result. The paper writes itself: "We show that the activation sparsity profile of a pre-trained LLM encodes sufficient information to allocate LoRA ranks without training, achieving X% of oracle allocation at Y% of parameter count."

The hypothesis is now well-specified. It should be validated as a package: EXISTENCE (CV > 0.3 sparsity variation), MECHANISM (Pearson r ≤ -0.4 / Kendall's τ ≥ 0.4 sparsity-rank correlation, ΔW spectral alignment), and EFFICIENCY (≥95% GLUE at ≤60% parameters vs. uniform baseline).

**Key Points:**
- Scientific significance: exploiting pre-training geometry for fine-tuning configuration — opens a "structural priors for PEFT" research direction
- Practical significance: zero-gradient rank schedule that transfers across tasks — qualitatively different from AdaLoRA/DyLoRA cost curve
- Hypothesis is now well-packaged as three sub-hypotheses: EXISTENCE (CV > 0.3), MECHANISM (sparsity-rank correlation + ΔW spectral), EFFICIENCY (≥95% GLUE at ≤60% params)

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally tightening. But I'm not done.

Here's where your framing still risks collapsing: you are implicitly claiming that *static, pre-training-induced activation sparsity* can substitute for AdaLoRA's *task-conditioned importance scoring*. In AdaLoRA, rank allocation is driven by a sensitivity-aware importance metric over singular values, with pruning governed during training under a global budget scheduler. That is dynamic, task-aware, and gradient-informed. You are proposing a zero-gradient proxy measured before training. That is an enormous causal leap. Show me why a *task-agnostic* signal should approximate a *task-conditioned* one.

What would convince me: compute the final per-layer effective rank selected by AdaLoRA under the same 60% budget. Then correlate that distribution with your sparsity ranking. If Kendall's τ ≥ 0.4 between sparsity-based ranking and AdaLoRA's learned allocation on MNLI and SST-2, you've demonstrated that sparsity approximates a state-of-the-art adaptive allocator. If not, then you are competing with a strawman. The comparison baseline should also include AdaLoRA at matched parameter count (≈0.3M for MNLI-scale tasks). If AdaLoRA achieves 90.76 MNLI and you achieve 90.2, that gap matters. Don't hide behind "zero-training-cost" unless performance parity is within statistical noise.

On mechanism: include both average gradient norm during fine-tuning and activation sparsity in multiple regression predicting ΔW rank. If sparsity loses significance (p ≥ 0.05) once gradient norm is included, your mechanistic story collapses into "low-signal layers get small updates." Also test calibration stability across sequence length (128 vs. 512 tokens) — if ranking flips, you're measuring context utilization, not structural geometry. Intrinsic means invariant to superficial input statistics.

**Key Points:**
- Correlate sparsity-based rank allocation with AdaLoRA's learned per-layer ranks under identical budgets; otherwise you're avoiding the real competitor.
- Define oracle rigorously and compare directly to AdaLoRA at matched parameter count, not just uniform/random LoRA.
- Demonstrate mechanistic validity beyond gradient norm confounds and prove calibration stability across domain AND sequence length.

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — and Prof. Rex's demand to compare against AdaLoRA is actually the strongest possible version of our hypothesis, not a weakness! Let me turn this into our advantage.

DyLoRA [Valipour et al., 2022] in Methodology shows that its training across rank range [r_min, r_max] effectively functions as a Pareto frontier over rank-performance tradeoffs. Their Discussion & Conclusion acknowledges "the need for careful selection of distribution parameters" as the main limitation. What we can do: frame our work not as "competing with AdaLoRA" but as "providing AdaLoRA's initialization without training." If sparsity ranking correlates with AdaLoRA's final learned allocation at Kendall's τ ≥ 0.4, then sparsity is a *zero-cost approximation to AdaLoRA* — that's the cleanest possible novelty statement. "We show that activation sparsity provides a free approximation to AdaLoRA's learned rank allocation."

Prof. Rex's gradient norm confound concern is legitimate and I address it directly: the multiple regression test (sparsity + gradient norm + parameter count predicting ΔW effective rank) with unique variance threshold is exactly right. I propose we include this as our mechanistic sub-hypothesis H-M: "Activation sparsity explains ≥20% unique variance in learned LoRA update rank (measured as top-4 singular values of ΔW / total Frobenius norm) beyond gradient norm and parameter count." This is our causal claim in a format that directly addresses Prof. Rex's challenge.

The calibration stability extension (sequence length 128 vs. 512) is trivially implementable — add one parameter sweep to the calibration script. I propose we narrow the hypothesis scope to explicitly claim stability under input length variation but not claim cross-architecture generalization (save that for follow-up work). This keeps the scope tight and testable within a single experiment.

Here is the refined hypothesis statement: "Under LLaMA-3-8B, layer-wise MLP activation sparsity (measured once on 512 Alpaca samples, threshold |a| < 0.01, stable across 128-512 token lengths at Kendall's τ_calibration ≥ 0.6) negatively predicts per-layer LoRA rank sensitivity (Pearson r ≤ -0.4 on sensitive layers, joint budget = 60% of uniform r=16), achieves ≥95% of oracle joint allocation on SST-2 and MNLI, outperforms uniform and random baselines (p < 0.05), and explains ≥20% unique variance in ΔW spectral decay beyond gradient norm."

That's every falsification criterion incorporated. Now we have a bulletproof hypothesis.

**Key Points:**
- Frame against AdaLoRA: "sparsity provides a free approximation to AdaLoRA's learned allocation" — this is the strongest novelty framing
- H-M mechanistic sub-hypothesis: sparsity explains ≥20% unique variance in ΔW spectral decay beyond gradient norm (direct response to Prof. Rex's confound concern)
- Narrowed scope: calibration stability under length variation (128-512 tokens) but NOT cross-architecture (save for follow-up) — keeps hypothesis tight and testable

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis occupies a genuinely unexplored position in the design space: static pre-training activation sparsity as a zero-gradient proxy for per-layer LoRA rank allocation. All prior adaptive rank methods (AdaLoRA, ARD-LoRA, DyLoRA, Sensitivity-LoRA) require training-time signals. The framing as "free approximation to AdaLoRA's learned allocation" is both novel and publishable. The cross-domain connection (pre-training geometry → fine-tuning efficiency) opens a new "structural priors for PEFT" research direction.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now fully falsifiable with explicit thresholds: CV > 0.3 (EXISTENCE), Pearson r ≤ -0.4 on sensitive layers with Kendall's τ ≥ 0.4 against AdaLoRA allocation (MECHANISM), ≥95% oracle performance at 60% parameter budget on SST-2 and MNLI (EFFICIENCY), Kendall's τ_calibration ≥ 0.6 across Alpaca/WikiText and 128/512 tokens (STABILITY). Failure conditions are binary and pre-specified. The multiple regression control for gradient norm provides a mechanistic falsification test beyond performance outcomes.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Scientific significance is two-fold: (1) practical — zero-gradient rank scheduling that transfers across tasks enables personalized fine-tuning at scale; (2) theoretical — if confirmed, demonstrates that pre-training geometry encodes sufficient information for fine-tuning rank decisions, a theorem-like claim about the structure of LLM adaptation. The field currently lacks this understanding. Results position directly against LoRA, AdaLoRA, DyLoRA on GLUE, providing directly comparable evaluation.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Technically sound and implementable. Core components: (1) activation sparsity measurement via register_forward_hook on LLaMA-3-8B MLP layers — trivial; (2) rank allocation via HF PEFT rank_pattern dict — well-documented; (3) ΔW spectral decay via torch.linalg.svd post-training — cheap; (4) calibration stability test (Alpaca vs. WikiText, 128 vs. 512 tokens) — adds <10 minutes. The SiLU soft-sparsity threshold ε requires careful calibration (recommend following TEAL methodology). No fundamental theoretical or implementation barriers exist.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a well-specified, falsifiable hypothesis with genuine novelty and scientific significance. Here is the consensus:

**Hypothesis Title:** SparsityLoRA — Activation Sparsity as a Pre-Training Structural Prior for LoRA Rank Allocation

**Core Claim:** Under LLaMA-3-8B, layer-wise MLP activation sparsity (measured once on 512 Alpaca samples, threshold |a| < 0.01, stable across input lengths at Kendall's τ_calibration ≥ 0.6) negatively predicts per-layer LoRA rank sensitivity. A sparsity-guided rank allocation (inverse-sparsity proportional, total budget = 60% of uniform r=16) achieves ≥95% of oracle joint allocation performance on GLUE SST-2 and MNLI, outperforms uniform and random baselines (p < 0.05 over 5 seeds), and correlates with AdaLoRA's learned allocation at Kendall's τ ≥ 0.4 under matched parameter budget.

**Proposed Mechanism:** Pre-training drives MLP layers toward low-dimensional activation attractors. Layers with high activation sparsity operate in a compressed representational subspace that requires low LoRA rank to redirect effectively. This is validated mechanistically by: (1) Pearson r ≤ -0.4 between sparsity and per-layer rank sensitivity on sensitive layers; (2) sparsity explaining ≥20% unique variance in ΔW spectral decay (ratio of top-4 singular values to total Frobenius norm) beyond gradient norm; (3) calibration stability under domain and length variation.

**Key Predictions:**
- P1 (EXISTENCE): Layer-wise sparsity CV > 0.3 across LLaMA-3-8B's 32 MLP layers on Alpaca calibration set (512 samples)
- P2 (MECHANISM): Pearson r ≤ -0.4 between sparsity and per-layer joint rank sensitivity on sensitive layers (≥0.5% accuracy drop); Kendall's τ ≥ 0.4 between sparsity ranking and AdaLoRA learned allocation
- P3 (EFFICIENCY): Sparsity-guided allocation achieves ≥95% of oracle performance on SST-2 and MNLI at 60% parameter budget, outperforming uniform r=~10 and random allocation (p < 0.05)

**Experimental Setup:** LLaMA-3-8B on GLUE SST-2 and MNLI. Calibration: 512 Alpaca samples. Baselines: uniform LoRA, random allocation (10 seeds), AdaLoRA at matched budget. Infrastructure: HF PEFT rank_pattern, register_forward_hook for sparsity, torch.linalg.svd for ΔW spectra.

**Novelty:** First work to use static pre-training activation sparsity as a rank predictor before fine-tuning begins. All prior adaptive rank methods require training-time signals. Framed as: "zero-cost approximation to AdaLoRA's learned allocation using pre-training geometry."

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- SiLU soft-sparsity produces non-binary activations — threshold ε selection affects sparsity measurement and must be justified empirically (test ε ∈ {0.001, 0.01, 0.05, 0.1})
- Marginal vs. joint rank sensitivity: experiment must clearly specify joint allocation protocol (fix total budget, redistribute when perturbing one layer)
- Task-rank interaction is real (DyLoRA shows task-conditioned sensitivity) — if results differ substantially between SST-2 and MNLI, the claim must be narrowed to the validated task types
- **Mitigation Strategy:** Include ε sensitivity analysis as robustness check; pre-register exact joint sensitivity protocol; report per-task results separately and test statistical significance with 5-seed repetition
