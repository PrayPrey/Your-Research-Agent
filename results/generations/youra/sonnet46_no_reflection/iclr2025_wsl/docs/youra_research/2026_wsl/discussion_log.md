# Phase 2A Discussion Log
## Research Gap: Incomplete Symmetry Coverage Across Diverse Neural Network Architectures

**Gap ID:** gap-1
**Priority:** HIGH+PRIMARY
**Pipeline Project:** Anonymous Pipeline: Neural network weights as a new data modality
**Initialized:** 2026-05-20T23:14:00Z
**Architecture:** Self-Contained Tikitaka Loop v9.0.0

---

## Briefing Context

### Research Gap Summary

**Gap:** No unified equivariant framework handles permutation+scaling+sign-flip symmetries for MLP+CNN+Transformer simultaneously.

**Current State:**
- NFNs [Zhou et al., NeurIPS 2023] handle permutation symmetry for MLP/CNN weight spaces (arXiv:2302.14040)
- Monomial-NFN [Tran, Vo et al., 2024] adds scaling+sign-flip symmetries — but still MLP/CNN only (arXiv:2409.11697)
- Transformer-NFN [Tran-Viet et al., ICLR 2025] handles MHA symmetry separately — fragmented from MLP/CNN (arXiv:2410.04209)
- SANE [Schürholt et al., ICML 2024] achieves cross-architecture via tokenization — but NOT equivariant (arXiv:2406.09997)
- WSL Survey [Han, Wang et al., 2026] confirms fragmented symmetry coverage as open problem in WSR (arXiv:2603.10090)

**Missing Piece:** A unified equivariant architecture covering all symmetry types (permutation, scaling, sign-flip) × all architecture families (MLP, CNN, Transformer) simultaneously.

**Why This Matters:**
- Would make WSL universally applicable to any architecture on Hugging Face (>1M models)
- Enables cross-architecture weight representations for property prediction, transfer, and generation
- Blocks sub-questions Q1 (symmetries+equivariance) and Q2 (task-agnostic embeddings across families)

### Available Papers (P1-P5)

| ID | Paper | arXiv | Key Content |
|----|-------|-------|-------------|
| P1 | NFN: Permutation Equivariant Neural Functionals | 2302.14040 | NF-Layers, parameter sharing, MLP/CNN only |
| P2 | SANE: Scalable and Versatile WSL | 2406.09997 | Token-based, cross-architecture, not equivariant |
| P3 | Monomial-NFN | 2409.11697 | Scaling+sign-flip symmetries, MLP/CNN only |
| P4 | Transformer-NFN | 2410.04209 | MHA maximal symmetric group, Transformer zoo |
| P5 | WSL Survey 2026 | 2603.10090 | Taxonomy (WSU/WSR/WSG), open problems |

### Feasibility Constraints (MANDATORY)
- ❌ REJECT: New benchmarks, rubrics, or scoring frameworks
- ❌ REJECT: Synthetic/generated data or future follow-up data
- ❌ REJECT: Human evaluation, annotation, or subjective scoring
- ✅ ACCEPT: Hypotheses testable immediately using existing real datasets and existing benchmarks

### Available Datasets
- Small CNN Zoo (CIFAR-10, SVHN classifiers) — used in NFN paper
- Small Transformer Zoo (125K checkpoints, MNIST+AGNews) — from Transformer-NFN paper
- HSG-AIML Phase-Aware Model Zoos (12 large-scale, 2025)
- RNN weight zoo (Herrmann et al., 2024)

---

## Discussion Participants

| Icon | Name | Role |
|------|------|------|
| 🔭 | Dr. Nova | Creative Novelty Explorer |
| 🔬 | Prof. Vera | Rigorous Validation Architect |
| 🎯 | Dr. Sage | Research Impact Evaluator |
| ⚙️ | Prof. Pax | Feasibility & Reality Checker |
| 🛡️ | Dr. Ally | Hypothesis Strengthening Champion |
| 🔍 | Prof. Rex | Hypothesis Stress-Test Master |

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The fragmentation problem in weight space symmetry coverage is fascinating precisely because it reveals a hidden compositional structure that no one has fully exploited yet. Let me propose three angles that could lead to a genuinely novel unified framework.

**Angle 1 — Hierarchical Symmetry Decomposition:** Every neural architecture's weight space symmetry group can be decomposed into a product of local symmetries (per-layer) and global symmetries (across layers). NFNs [Zhou et al., 2023] captured local MLP permutation, Monomial-NFN extended to scaling/sign-flip locally, and Transformer-NFN [Tran-Viet et al., 2025] characterized the MHA group. What if we define a *meta-symmetry algebra* — a shared algebraic structure from which all three families' symmetry groups can be derived? The hypothesis would be: a unified equivariant layer parameterized by the architecture's symmetry group specification, instantiated differently for MLP, CNN, Transformer at inference time, can outperform architecture-specific NFNs on cross-architecture property prediction benchmarks.

**Angle 2 — Symmetry-Aware Tokenization as Bridge:** SANE [Schürholt et al., ICML 2024] achieved cross-architecture reach through tokenization without equivariance. What if we augment token embeddings with symmetry-group descriptors as positional information? Instead of architecture-blind tokens, each weight token carries a "symmetry fingerprint" encoding which permutation orbits, scaling symmetries, and head symmetries it belongs to. This is testable: does adding symmetry fingerprints to SANE's token representations improve model property prediction accuracy on existing Small CNN Zoo + Small Transformer Zoo benchmarks?

**Angle 3 — Transfer of Equivariance via Canonicalization:** Rather than building new equivariant layers, canonicalize weights into a symmetry-reduced form, then apply standard architectures. The WSL Survey [Han et al., 2026] notes canonicalization as an alternative to explicit equivariance. A canonicalized Transformer weight could be reduced to a canonical MLP-like form, enabling existing NFN layers to process it. Testable: does weight canonicalization before processing with standard NFN layers improve cross-architecture generalization prediction on Small Transformer Zoo?

My strongest bet for novelty: **Angle 2** (symmetry-aware tokenization) because it builds directly on existing SANE infrastructure, requires no new architecture, and is immediately testable on available model zoo datasets.

**Key Points:**
- Unified symmetry framework is achievable through meta-algebra, symmetry-augmented tokenization, or canonicalization
- All three angles are testable on existing Small CNN Zoo and Small Transformer Zoo datasets
- Symmetry-aware tokenization builds on SANE (already ICML 2024) with minimal new components
- Cross-architecture property prediction accuracy is the natural primary metric

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your Angle 2—symmetry-aware tokenization layered onto SANE—is promising, but at present it is a design intuition, not a falsifiable hypothesis. We must convert it into precise predictions. The evidence from Transformer-NFN [Tran-Viet et al., 2025] shows that explicitly encoding the maximal symmetry group \( G_U = S_h \times GL_{D_k}(R)^h \times GL_{D_v}(R)^h \times PD \times PD_A \) yields Kendall's τ ≈ 0.91 on AGNews and 0.905 on MNIST. Therefore, your approach must be evaluated against a strong baseline: (1) vanilla SANE, (2) Transformer-NFN, and (3) SANE + symmetry fingerprint.

Here is the first testable prediction: if symmetry fingerprints capture functionally invariant structure, then SANE + fingerprint should exhibit significantly smaller performance degradation under synthetic symmetry perturbations. Concretely, take checkpoints from Small Transformer Zoo and apply random head permutations (from \(S_h\)) and invertible linear transforms in \(GL_{D_k}\). Transformer-NFN is equivariant by construction [Tran-Viet et al., 2025]; vanilla SANE is not. Your method predicts that Kendall's τ should drop by <0.02 under such perturbations. If it drops comparably to vanilla SANE (>0.10), the fingerprint does not encode the correct invariants. That would disprove the core claim.

Second, we require a quantitative definition of "symmetry fingerprint." What is its dimensionality? Is it invariant under the full group \(G_U\), or only a subgroup? A critical stress test: construct two weight configurations that are provably functionally identical under \(G_U\) (per the necessary and sufficient conditions in the Methodology section). If your fingerprint embeddings differ significantly (e.g., cosine similarity <0.95), then they are not true invariants. Conversely, if two functionally distinct configurations map to nearly identical fingerprints, you risk collapsing discriminative signal. Both are measurable failure modes.

Third, scalability must be interrogated. Transformer-NFN relies on polynomial equivariant mappings \(I: U \to \mathbb{R}^{D'}\) [Tran-Viet et al., 2025], and the ablation shows the transformer block alone yields τ ≈ 0.902—indicating that most predictive signal resides in structured block-level relations. If your fingerprint is computed per-token, its computational cost must scale at most linearly in parameter count. I would require an explicit complexity analysis and an empirical scaling curve: τ versus model size.

Finally, we must isolate whether gains arise from symmetry information or merely additional features. An ablation is essential: (a) SANE + random fingerprint of identical dimensionality, (b) SANE + partial subgroup fingerprint (e.g., only head permutation), (c) full \(G_U\) fingerprint. The evidence suggests that if symmetry is the true driver, performance should monotonically increase with subgroup coverage.

**Key Points:**
- Define explicit invariance tests using synthetic group actions from \(G_U\); require <0.02 τ degradation under symmetry perturbations
- Validate fingerprints as true invariants via cosine similarity tests on provably equivalent weight configurations
- Use subgroup ablations and scaling curves to determine whether symmetry, not feature count, drives performance gains

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's falsifiability framework is exactly right, but I want to ground this in what SANE [Schürholt et al., ICML 2024] actually implements before we commit to an architecture direction. SANE tokenizes weights layer-by-layer into manageable subsets and uses a transformer backbone with reconstruction + contrastive loss. Crucially, it achieves linear scalability by processing weight subsets independently — this is both its strength and its limitation for our purposes.

The implementation challenge for symmetry-aware tokenization: SANE's tokenization is architecture-aware (it knows layer boundaries) but symmetry-agnostic within each layer. Adding a symmetry fingerprint to each token requires, at minimum, knowing which neurons are permutation-equivalent — which requires either (a) running a canonicalization step before tokenization, or (b) computing orbit membership analytically. Option (a) is feasible with existing tools: the nfn library already implements weight canonicalization for MLPs. Option (b) requires extending the group structure analysis from Transformer-NFN [Tran-Viet et al., 2025] to SANE's token format.

Here is the key feasibility assessment: the Small Transformer Zoo has 125K checkpoints with known architecture and task labels (MNIST + AGNews). SANE's codebase (HSG-AIML/SANE, 31★) is public and produces representations that can be directly evaluated on these checkpoints. Adding a symmetry fingerprint is a modular extension — you compute the fingerprint separately and concatenate with the SANE embedding. This is a 2-4 week engineering task, not a fundamental algorithmic redesign. The AllanYangZhou/nfn library provides the NF-Layer primitives that compute permutation-orbit features; these could serve as symmetry fingerprints.

The one concern I have: the CNN Zoo and Transformer Zoo are architecturally distinct. SANE works across both, but the symmetry fingerprints will be qualitatively different (MLP/CNN: head permutation over neurons; Transformer: head permutation over attention heads + GL_Dk symmetry). We need a fingerprint representation that is *comparable* across architecture families — otherwise we are just concatenating incommensurable vectors. I propose representing the fingerprint as a fixed-size summary of orbit structure (e.g., top-k orbit sizes, degree sequence of equivalence classes) that is architecture-agnostic in format even if architecture-specific in content.

**Key Points:**
- SANE's modular tokenization makes symmetry fingerprint augmentation an engineering-feasible extension (2-4 weeks)
- nfn library provides permutation-orbit primitives directly usable as MLP/CNN fingerprints
- Cross-architecture fingerprint comparability requires a normalized orbit-summary representation
- Both Small CNN Zoo and Small Transformer Zoo datasets are available for immediate benchmarking

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Alright. This is getting sharper—but here's where this still breaks down.

Your core claim in Angle 2 is that a *symmetry fingerprint* appended to SANE will meaningfully close the gap to explicitly equivariant models like Transformer-NFN. But Transformer-NFN doesn't just "encode symmetry information"—it enforces equivariance under the full group \( G_U = S_h \times GL_{D_k}^h \times GL_{D_v}^h \times PD \times PD_A \) [Tran-Viet et al., 2025]. That's a *structural constraint* baked into polynomial mappings. You're proposing a learned model with additional features. Those are not equivalent interventions.

First demand: **What is the theoretical ceiling of a fingerprint-augmented non-equivariant model?** If I apply a head permutation or a GL_Dk transform to a checkpoint, Transformer-NFN is provably equivariant. Your SANE+fingerprint is not. At best, it can *learn* invariance statistically. What would convince me: train only on canonical representatives of each orbit, test on random group-transformed variants, show <0.02 τ degradation. If performance collapses, your fingerprint is cosmetic.

Second: you are mixing invariants and descriptors without clarity. If the fingerprint is an invariant map, you risk destroying discriminative information—Transformer-NFN's ablation shows structured block-level interactions give τ ≈ 0.902 on MNIST [Tran-Viet et al., 2025]. That means relational polynomial structure is where the signal lives, not orbit summaries. Orbit size histograms alone would give marginal gains (<0.01 τ).

Third — and here is the most important challenge — cross-architecture comparability is hand-wavy. If symmetry statistics differ semantically across MLPs vs Transformers, concatenation just adds noise. The critical experiment: train on Small CNN Zoo only, evaluate zero-shot on Small Transformer Zoo. If fingerprints encode architecture-agnostic invariants, τ should degrade gracefully (<0.05 relative drop). Otherwise you've built architecture-conditioned features.

The real scientific win must be one of three things: (1) comparable τ to Transformer-NFN with lower compute, (2) robustness to symmetry perturbations beyond G_U, or (3) cross-architecture transfer that architecture-specific NFNs cannot achieve. Right now only (3) is plausible — but the experiment is not yet tight enough.

**Key Points:**
- Fingerprint augmentation is statistically learned invariance, not structural equivariance — test orbit-level robustness explicitly
- Orbit summaries alone may be weak predictors; the signal lives in polynomial relational structure per Transformer-NFN ablation
- Cross-architecture transfer experiment is the decisive test: CNN Zoo → Transformer Zoo zero-shot

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex's critique crystallizes the key question: is this hypothesis scientifically impactful enough to pursue, or are we chasing incremental gains over Transformer-NFN (τ ≈ 0.91 already)? Let me assess from a research impact perspective.

The WSL Survey [Han et al., 2026] identifies cross-architecture weight representation as the **core unsolved problem** in WSR — explicitly calling out the fragmentation of MLP/CNN equivariance from Transformer equivariance as a major barrier to universal WSL applicability. This is not an incremental gap. The 1M+ models on Hugging Face span every architecture family — transformers, CNNs, hybrid models, state-space models — and no current method can provide equivariant representations across all of them. Even Transformer-NFN is architecture-restricted; it cannot directly process ResNet weights.

So the impact opportunity is genuinely high — *if* the hypothesis targets cross-architecture transfer rather than within-architecture improvement. Prof. Rex identified the right frame: the real win is (3) — cross-architecture generalization that architecture-specific NFNs cannot achieve by design.

This reframes the hypothesis from "SANE + fingerprint improves τ by X%" to something more impactful: **"Symmetry-augmented weight representations enable cross-architecture model property prediction without retraining, achieving >Z% accuracy retention when transferring from models trained on CNN Zoo to Transformer Zoo."** That is a qualitatively new capability that no existing method provides.

The WSL Survey framework also clarifies why this matters for downstream tasks. The WSU taxonomy shows that cross-architecture understanding is prerequisite to: federated learning over heterogeneous models, continual learning across architectures, and model merging across families. A hypothesis that unlocks cross-architecture weight representations unlocks all of these.

From an impact lens: the NFN paper's key result was τ > 0.93 on CNN generalization prediction. Transformer-NFN's key result was extending this to transformers. The next milestone the field needs is *cross-architecture* generalization prediction with a *single model*. That is the paper this hypothesis can become — and it would be publishable at a top venue (NeurIPS/ICML) as a systematic study.

**Key Points:**
- WSL Survey [Han et al., 2026] explicitly identifies cross-architecture representation as the primary open problem in WSR
- The impactful target is cross-architecture property prediction with a single model — not within-architecture τ improvement
- This is the natural third chapter after NFN (MLP/CNN equivariance) and Transformer-NFN (Transformer equivariance)
- Impact is high if hypothesis targets the CNN Zoo → Transformer Zoo transfer scenario

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let us sharpen the hypothesis to a form that can fail decisively. The Transformer-NFN paper defines the maximal symmetry group of a transformer block as \( G_U = S_h \times GL_{D_k}(R)^h \times GL_{D_v}(R)^h \times PD \times PD_A \) and constructs an explicitly equivariant polynomial map \( I: U \to \mathbb{R}^{D'} \) [Tran-Viet et al., 2025]. Therefore, our symmetry fingerprint must be evaluated not on overall τ improvement alone, but on *orbit-level consistency*.

**Test 1: Orbit Invariance Consistency.** Construct equivalence classes by sampling checkpoint U from Small Transformer Zoo and applying random elements g ~ G_U. Define the Orbit Variance Ratio: OVR = E_g ||f(g·U) - f(U)||_2 / E_{U'≠U} ||f(U') - f(U)||_2. A valid invariant fingerprint requires OVR < 0.05.

**Test 2: Cross-Architecture Transfer.** Train a single SANE+fingerprint model on Small CNN Zoo only. Evaluate zero-shot on Small Transformer Zoo. Hypothesis predicts τ_cross ≥ 0.75·τ_in. This is the clean comparative advantage: Transformer-NFN cannot perform this test at all due to architecture restriction [Tran-Viet et al., 2025].

**Test 3: Structural vs Statistical Invariance.** Train on canonicalized checkpoints only. At test time, evaluate on randomly transformed variants g·U. Require prediction variance across orbit < 10^{-3}.

On mechanism: orbit size histograms alone will not suffice. The fingerprint should include low-degree invariant traces such as tr(W^{Q,i} W^{K,i T}) aggregated over heads — quantities invariant under S_h and appropriate linear transforms, computable in O(|U|) time. These are explicitly tied to the group structure in Transformer-NFN's Methodology.

**Key Points:**
- OVR < 0.05 is a strict invariance falsification test under G_U actions
- Cross-architecture CNN→Transformer zero-shot transfer with ≥75% τ retention is the decisive impact criterion
- Fingerprints must include low-degree invariant polynomials (trace-based relations), not mere orbit summaries

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Vera has given us exactly the falsification framework we needed. Now let me consolidate and propose a sharpened hypothesis that incorporates all the constraints while preserving what is genuinely novel.

The key insight from SANE [Schürholt et al., ICML 2024] is that its tokenization — weight vectors chunked layer-by-layer — is *already* partially symmetry-aware in that it respects layer boundaries (the source of most symmetry structure). SANE's encoder maps these tokens to a latent z via g_θ(T), optimized with reconstruction + contrastive loss. The limitation is that tokens within a layer are treated as an unordered bag of features — no orbit structure is encoded.

What if instead of appending fingerprints, we *replace SANE's positional encodings* with symmetry-group-derived orbit embeddings? Specifically: for MLP layers, the orbit of neuron i under the permutation group defines a canonical ordering; for CNN layers, filter permutations define orbits; for Transformer MHA layers, head permutations define orbits over attention head indices. Each token's "position" would be its orbit-membership vector rather than its sequential index. This is a lightweight architectural modification to SANE: same transformer backbone, same loss, different positional encoding.

This is testable immediately: the SANE codebase (HSG-AIML/SANE) is open source. Orbit-based positional encodings require computing neuron equivalence classes — tractable with the nfn library for MLP/CNN layers and with the Transformer-NFN group characterization for attention heads. The key prediction: SANE with orbit-PE achieves ≥75% τ retention in CNN→Transformer zero-shot transfer, compared to <30% retention for vanilla SANE (which would use sequence-position embeddings that are architecture-specific).

This also addresses Prof. Rex's concern about theoretical ceiling: orbit-PE is provably invariant to the permutation component of G_U (S_h × layer permutations) by construction, even if it approximates rather than enforces the GL_Dk component. The falsification criteria are concrete: OVR < 0.05 for S_h-actions, ≥75% τ cross-architecture retention, and prediction variance < 10^{-3} under orbit-equivalent transforms.

**Key Points:**
- Replace SANE's positional encodings with orbit-membership vectors (orbit-PE): provably invariant to permutation components of G_U
- SANE+orbit-PE is a minimal architectural change testable on existing open-source codebase and existing model zoo datasets
- Core prediction: ≥75% τ retention in CNN-only training → Transformer Zoo zero-shot evaluation
- OVR < 0.05 under S_h actions is provable by construction for the permutation subgroup

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. Replacing positional encodings with orbit-based embeddings is the first proposal in this thread that actually changes inductive bias rather than sprinkling features on top. But here's where this still breaks down.

You are leaning heavily on permutation invariance (the S_h component), while the real expressive jump in Transformer-NFN comes from handling the *full* group G_U = S_h × GL_Dk^h × GL_Dv^h × PD × PDA [Tran-Viet et al., 2025]. Their ablation shows the transformer block structure alone reaches τ ≈ 0.902 on MNIST — that's from structured polynomial interactions among Q,K,V,O blocks, not head permutation invariance alone. So: why should orbit-PE over permutations close any meaningful fraction of the gap when the dominant symmetry mass lies in the GL_Dk and GL_Dv factors?

Define G_perm = S_h × neuron permutations explicitly. Prove invariance to G_perm, then *measure* OVR separately for random g ∈ GL_Dk. I predict OVR_perm ≈ 0 but OVR_GL >> 0.1. That gap is the theoretical ceiling of your approach. What would convince me otherwise: empirical evidence that GL-style transformations are rare in real training trajectories — that most checkpoint variation lies along permutation orbits, not GL orbits.

The decisive control for cross-architecture leakage: remove architecture labels entirely, shuffle architecture types at test time, evaluate CNN→Transformer zero-shot with no architecture token. If τ collapses, your invariants were architecture-conditioned.

I want four numbers before belief: (1) vanilla SANE CNN→Transformer τ_retention baseline, (2) SANE+orbit-PE τ_retention, (3) OVR_perm and OVR_GL separately, (4) training cost relative to Transformer-NFN (wall-clock, memory). If τ_retention ≥ 0.75 with OVR_perm < 0.05 and modest compute overhead, then we're talking about a real third chapter in this line of work.

**Key Points:**
- Orbit-PE only guarantees invariance to permutation subgroups; GL symmetries in G_U remain unaddressed — measure OVR separately
- Cross-architecture invariants risk encoding architecture-conditioned features; test without architecture identifiers
- Hypothesis stands or falls on concrete τ_retention, OVR_perm vs OVR_GL, and compute comparisons to Transformer-NFN

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex raises the right challenge about GL_Dk symmetries, and I want to address it with a practical resolution that keeps the hypothesis feasible.

Here's the key empirical fact from SANE [Schürholt et al., ICML 2024] that matters: SANE achieves high linear probe accuracy (0.978 on MNIST, 0.991 on SVHN, 0.991 on CIFAR-10) without any equivariance — purely through architecture-aware tokenization + contrastive learning. This means SANE's contrastive loss already learns to cluster functionally-equivalent checkpoints regardless of some degree of weight reparameterization. The GL_Dk symmetries that Transformer-NFN explicitly handles — SANE partially approximates them implicitly via training on diverse orbits.

So the practical research question isn't "does orbit-PE achieve perfect GL-equivariance?" — it's "does orbit-PE meaningfully improve cross-architecture transfer over vanilla SANE's already-reasonable baseline?" If vanilla SANE achieves τ_retention = 0.45 in CNN→Transformer transfer (a plausible baseline given architecture distribution shift), and orbit-PE achieves τ_retention = 0.70, that's a paper. We don't need to match Transformer-NFN's within-architecture τ ≈ 0.91.

The feasibility roadmap is concrete: (1) Run vanilla SANE on Small CNN Zoo + Small Transformer Zoo — straightforward, codebase is public. (2) Implement orbit-PE: for MLP layers, use nfn library's permutation orbit computation; for Transformer attention heads, use Transformer-NFN's group characterization to compute head-orbit embeddings. Estimated implementation: 3-4 weeks in PyTorch. (3) Cross-architecture experiment: train on CNN Zoo, zero-shot eval on Transformer Zoo. (4) Ablation: sequence-PE vs orbit-PE vs random-PE. (5) OVR measurement under S_h and synthetic GL transforms.

The GL_Dk OVR gap that Prof. Rex predicts (OVR_GL >> 0.1) is real — but it's not a falsification of the hypothesis, it's a scope clarification. The hypothesis would read: "Orbit-PE improves cross-architecture transfer by encoding permutation-group invariants, achieving ≥X% τ_retention improvement over vanilla SANE." The GL gap becomes future work toward full G_U equivariance.

**Key Points:**
- SANE already approximates some GL invariance implicitly via contrastive training on diverse orbits — orbit-PE adds permutation-level structure on top
- Feasible 3-4 week implementation using existing nfn + SANE codebases on existing Small CNN Zoo + Transformer Zoo datasets
- Hypothesis should target τ_retention improvement over vanilla SANE baseline, not parity with Transformer-NFN
- GL_Dk OVR gap is a known limitation to acknowledge, not a falsification criterion for permutation-level orbit-PE

---

### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging, but I want to prevent a subtle drift in the hypothesis. The claim must not be "orbit-PE improves performance," but rather: *encoding permutation-group structure improves cross-architecture generalization in a measurable, falsifiable way.*

The evidence from Transformer-NFN shows that explicit handling of the full symmetry group G_U = S_h × GL_Dk^h × GL_Dv^h × PD × PDA yields τ ≈ 0.905–0.910 on in-architecture prediction tasks [Tran-Viet et al., 2025]. Their ablation demonstrates that architectural structure alone already achieves τ ≈ 0.902 on MNIST. This sets a ceiling for what symmetry-aware structure can contribute *within* a fixed architecture. Our scientific question is different: does partial symmetry encoding (permutation subgroup only) produce robust *cross-architecture* invariance?

Three disjoint OVR measurements: (1) OVR_perm: apply g ∈ S_h × neuron permutations only. (2) OVR_GL: apply synthetic g ∈ GL_Dk^h × GL_Dv^h transforms that preserve function. (3) OVR_mixed: sample from full G_U.

The hypothesis predicts: Vanilla SANE OVR_perm > 0.1; Orbit-PE OVR_perm < 0.05; both methods OVR_GL > 0.1. If Orbit-PE fails to reduce OVR_perm below 0.05, the invariance claim is false.

Pre-register τ_retention thresholds: τ_retention = τ_{CNN→Transformer} / τ_{CNN→CNN}. Vanilla SANE: expected τ_retention ≈ 0.4–0.5. Orbit-PE success: τ_retention ≥ 0.7. Strong success: τ_retention ≥ 0.75. If τ_retention improves by <0.1 absolute over baseline, the hypothesis does not justify architectural modification.

Control architecture confounds: remove architecture identifiers, match marginal distributions by parameter count, perform label-permutation sanity check. If we adhere to pre-registered thresholds and subgroup-isolated tests, the experiment becomes capable of failing.

**Key Points:**
- Separate OVR_perm, OVR_GL, OVR_mixed to isolate subgroup effects within G_U
- Pre-register τ_retention thresholds (≥0.7 success; <0.1 absolute gain = failure)
- Control architecture confounds and shuffled-label sanity checks

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

SANE's cross-architecture results [Schürholt et al., ICML 2024] provide a crucial baseline reference point for impact assessment. SANE achieved linear probe accuracy of 0.978 on MNIST, 0.991 on SVHN/CIFAR-10, and 0.931 on Tiny-ImageNet — all within-architecture. Critically, SANE's experiments cross architectures *within* the same task family (MLP variants), not across MLP vs Transformer boundaries. This gap is the exact niche our hypothesis targets.

The impact calculation is now clearer: the Small CNN Zoo and Small Transformer Zoo datasets are publicly available, well-characterized, and used as the reference benchmarks in both NFN and Transformer-NFN papers. A result showing τ_retention ≥ 0.70 in CNN→Transformer zero-shot transfer would be the first demonstration of architecture-agnostic weight representations with provable subgroup invariance properties. This is a publishable result at NeurIPS or ICML for three reasons:

1. **First cross-architecture zero-shot transfer benchmark.** Neither NFN, Monomial-NFN, nor Transformer-NFN address this — they are all architecture-restricted. SANE addresses cross-architecture within one paradigm but without cross-paradigm zero-shot.

2. **Interpretability contribution.** The OVR decomposition (OVR_perm vs OVR_GL) provides a new tool for understanding which symmetry components matter most for generalization transfer. This has implications beyond the specific hypothesis — it is a measurement methodology applicable to any WSL method.

3. **Building block for practical WSL at Hugging Face scale.** If permutation invariance is the dominant transferable component (confirmed by OVR decomposition), then future methods can focus on efficiently encoding permutation structure, dramatically simplifying the path to universal WSL.

I agree with Prof. Vera: the hypothesis is now falsifiable with pre-registered thresholds. The scientific narrative is clean: "We show that encoding permutation-orbit structure in weight tokenization (orbit-PE) is sufficient to achieve robust cross-architecture model property prediction, addressing the primary bottleneck identified by the WSL Survey [Han et al., 2026]: fragmented symmetry coverage."

**Key Points:**
- SANE's cross-architecture results are within-architecture-family; CNN→Transformer zero-shot is genuinely new territory
- τ_retention ≥ 0.70 + OVR_perm < 0.05 = publishable at NeurIPS/ICML as a cross-architecture WSL benchmark
- OVR decomposition methodology itself is a reusable scientific contribution for measuring symmetry-transfer efficiency

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

We're getting sharper. But here's where it still breaks down conceptually: you are implicitly assuming that permutation symmetries are the dominant source of cross-checkpoint variation *within each architecture*, and therefore the dominant transferable structure *across architectures*. That is an empirical claim, not a theoretical one.

Transformer-NFN derived the full maximal symmetry group G_U = S_h × GL_Dk^h × GL_Dv^h × PD × PDA and constructed polynomial equivariant mappings over that space [Tran-Viet et al., 2025]. Their ablation shows that respecting transformer block structure alone gives τ ≈ 0.902 on MNIST. That means most predictive signal lives in structured algebraic interactions between Q/K/V/O and FFN weights, not just head permutations.

Three demands: (1) A geometric variance decomposition of checkpoint trajectories — compute tangent-space variance along permutation directions vs GL directions vs residual. If >60% variance lies along permutation orbits and <20% along GL orbits, your bet is justified. If not, your ceiling is hard. (2) OVR must be embedding-level, not performance-level: OVR_subgroup = E_{g~G_sub} ||f(W) - f(g·W)||_2. If OVR_GL ≈ OVR_perm, your orbit-PE is accidentally learning partial GL invariance — falsifying the "permutation-only" claim. (3) Architecture alignment: CNNs and Transformers don't share weight-space decomposition. You need a canonical architecture-agnostic decomposition — e.g., every layer as (input-channel permutation × output-channel permutation). Define this formally.

Compute bound: ≤1.2× wall-clock over vanilla SANE. If you creep toward NFN-level cost without matching τ ≈ 0.9 in-domain, reviewers will ask why not just use Transformer-NFN.

**Key Points:**
- Permutation-variance-dominates-GL-variance hypothesis must be validated via geometric variance decomposition
- OVR must be embedding-level and subgroup-isolated; accidental GL invariance would falsify the "permutation-only" claim
- Cross-architecture invariance requires a shared, architecture-agnostic linear-operator group definition

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex's three demands are fair and I want to show they are *all addressable* with what the Monomial-NFN paper [Tran, Vo et al., 2024] gives us — which is exactly the theoretical foundation we need.

The Monomial-NFN introduces a key insight: the monomial matrix group (permutation × diagonal scaling × sign-flip) contains *all* invariant symmetry groups of MLPs as a special case. Crucially, this paper proves that the maximal symmetry group of MLPs is a subgroup of the monomial matrix group — and the paper's framework demonstrates significant reduction in trainable parameters while maintaining competitive performance, precisely because it captures the relevant symmetry structure efficiently.

Here's how this resolves Prof. Rex's architecture alignment challenge: treat every linear layer (regardless of architecture) as a map from input-channel space to output-channel space, equipped with (input-channel permutation × output-channel permutation) symmetry. For MLP layers, this is the exact permutation group from NFN [Zhou et al., 2023]. For CNN filters, it's the convolutional channel permutation. For Transformer attention heads, the S_h head permutation permutes over the head-dimension. **This is a canonical architecture-agnostic decomposition** — the input/output channel permutation group is well-defined for every linear operator regardless of architecture family.

Now, the orbit-PE construction becomes: for each weight token (representing a single layer's parameters), encode its orbit membership under (input-channel permutation × output-channel permutation). This is computable for any architecture using simple canonicalization algorithms (sort neurons by activation magnitude, or use the Monomial-NFN's weight-ordering procedure). It doesn't require deriving architecture-specific maximal symmetry groups.

For the variance decomposition demand: the Monomial-NFN paper's empirical results show that permutation+scaling symmetries account for the dominant invariance structure in MLP/CNN weight spaces. We can extend this by computing checkpoint trajectories in the Small CNN Zoo and Small Transformer Zoo using orbit-PE distance vs raw weight distance as our metric. If orbit-PE distance correlates better with functional distance than raw distance — even without GL handling — that validates the permutation-dominance assumption.

**Key Points:**
- Monomial-NFN establishes that input/output channel permutation is the canonical architecture-agnostic symmetry for linear operators
- Orbit-PE using (input-channel perm × output-channel perm) is well-defined for MLP, CNN, and Transformer layers simultaneously
- Permutation-dominance assumption is testable via orbit-PE distance vs functional distance correlation on existing model zoos

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now at the point where the hypothesis can crystallize into a falsifiable scientific claim. I will restate it in its most testable form: *Encoding input/output channel permutation symmetry alone is sufficient to materially improve cross-architecture τ_retention relative to a non-equivariant baseline.*

Three pre-registered predictions:

**Prediction P1 (Subgroup Specificity):** OVR_perm < 0.05, OVR_GL > 0.15. If OVR_GL ≈ OVR_perm, then either (a) accidentally approximating GL invariance, or (b) insufficient subgroup isolation. Either falsifies the "permutation-only mechanism" claim.

**Prediction P2 (Dominance Condition):** Compute Var_perm = E_t ||W_t - Π_{O_perm}(W_t)||^2 and Var_GL similarly. If Var_perm / (Var_perm + Var_GL) < 0.6, permutation symmetry is not the dominant mode and τ_retention ≥ 0.7 is not expected. This gives an Achilles' heel before expensive experiments.

**Prediction P3 (Function Preservation Test):** For sampled CNN and Transformer checkpoints, apply random channel permutations consistent with canonical definition. Verify validation accuracy changes by <0.1%. If not, assumed symmetry is invalid.

Cost constraint: ≤1.2× wall-clock over vanilla SANE. What would disprove: OVR_perm not substantially smaller than baseline; GL variance comparable to permutation variance; τ_retention gain <0.1 absolute; or violation of functional invariance. If Orbit-PE survives these, this meets my standards.

**Key Points:**
- P1: OVR_perm < 0.05, OVR_GL > 0.15 — falsifies "permutation-only mechanism" if violated
- P2: Var_perm dominance > 60% before running expensive cross-architecture experiments
- P3: Function preservation <0.1% accuracy change under declared permutations

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

This is the most rigorous version of the hypothesis we've produced, and I want to give a final feasibility verdict. Based on SANE's published methodology [Schürholt et al., ICML 2024], the implementation path is clear and the experiments are achievable.

SANE processes weights via a transformer backbone with layer-wise tokenization and reconstruction+contrastive loss. Implementation of orbit-PE requires: (1) computing input/output channel permutation orbits per layer — standard for MLP/CNN using neuron ordering, and achievable for Transformer MHA heads using the Transformer-NFN characterization; (2) replacing SANE's sequential positional encodings with orbit-membership embeddings (fixed-size, computed offline); (3) running on existing Small CNN Zoo + Small Transformer Zoo datasets.

Predictions P1, P2, P3 from Prof. Vera are all computationally feasible on a single GPU. P2 (variance decomposition) requires computing orbital projections — this is a single-pass computation over the model zoo. P3 (function preservation) requires running permuted checkpoints through their training datasets — feasible with existing zoo datasets. P1 (OVR measurement) requires sampling random group elements — trivial for S_h (just permute head indices), approximate for GL (sample from O(n) or random orthogonal matrices).

The complete experiment fits within a 2-week compute window on a single modern GPU (A100 or similar). Anticipated compute cost: SANE baseline training (~6h), Orbit-PE training (~7h), P2 variance decomposition (~2h), P3 function preservation check (~4h), cross-architecture transfer evaluation (~3h). Total: ~22 GPU-hours. This is well within typical research compute budgets.

The hypothesis now meets the three criteria for a viable research project: (1) falsifiable with pre-registered thresholds, (2) implementable with existing codebases and datasets, (3) impactful if successful (first cross-architecture zero-shot weight-based property prediction).

Final hypothesis statement for Step 2 structuring: **"Encoding input/output channel permutation symmetry via orbit-based positional encodings in weight tokenization (orbit-PE) achieves ≥70% τ_retention in CNN→Transformer cross-architecture zero-shot model property prediction, compared to <50% for vanilla SANE, because permutation-orbit structure is the dominant transferable symmetry component across architecture families."**

**Key Points:**
- Complete experiment feasible in ~22 GPU-hours on single A100 using existing SANE + nfn codebases and model zoo datasets
- All three predictions (P1, P2, P3) are computationally tractable in 2-week window
- Final hypothesis: orbit-PE achieves ≥70% τ_retention in CNN→Transformer zero-shot transfer vs <50% for vanilla SANE

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The orbit-PE hypothesis is genuinely novel because it identifies a new design dimension in weight tokenization — symmetry-orbit-based positional encodings — that no prior work (NFN, SANE, Transformer-NFN, Monomial-NFN) has explored. The cross-architecture zero-shot transfer framing is a qualitatively new capability. The idea emerged organically from combining SANE's tokenization strength with equivariant NFN's symmetry insights, creating a hybrid that inherits the scalability of one and the principled symmetry handling of the other.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis arrived at three fully pre-registered, subgroup-isolated predictions (P1: OVR_perm < 0.05 and OVR_GL > 0.15; P2: permutation variance dominance >60%; P3: function preservation <0.1% accuracy change). The τ_retention threshold (≥70% improvement vs <50% vanilla SANE baseline) provides a crisp numerical criterion. Multiple distinct failure modes are specified, making this hypothesis genuinely falsifiable and not merely confirmatory.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This hypothesis directly addresses the primary open problem in WSR identified by the 2026 WSL Survey — fragmented symmetry coverage preventing cross-architecture weight representations. A successful result would be the first demonstration of architecture-agnostic zero-shot weight-based property prediction, publishable at NeurIPS/ICML. The OVR decomposition methodology itself would be a reusable scientific contribution. The practical implications for scaling WSL to Hugging Face's 1M+ model ecosystem are high.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The experiment is implementable in approximately 22 GPU-hours on a single A100 using existing open-source codebases (HSG-AIML/SANE, AllanYangZhou/nfn) and existing datasets (Small CNN Zoo, Small Transformer Zoo, 125K checkpoints). The orbit-PE modification is a minimal architectural change (replace positional encodings) that does not require redesigning SANE's backbone. Implementation timeline: 3-4 weeks for a competent ML researcher. No new datasets, benchmarks, or human evaluation required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a well-defined and testable hypothesis about cross-architecture weight space learning through symmetry-aware tokenization.

**Core Claim:** Replacing SANE's sequential positional encodings with orbit-based positional encodings (orbit-PE) derived from input/output channel permutation groups achieves ≥70% τ_retention in CNN→Transformer cross-architecture zero-shot model property prediction, compared to <50% for vanilla SANE, because permutation-orbit structure is the dominant transferable symmetry component across neural architecture families.

**Mechanism:** SANE [Schürholt et al., ICML 2024] tokenizes weights layer-by-layer into a transformer backbone with reconstruction+contrastive training. Its sequential positional encodings are architecture-specific (layer index). Orbit-PE replaces these with orbit-membership vectors: for each weight token, encode which permutation orbit (under input × output channel permutation group) each neuron/filter/head belongs to. This orbit structure is computable for any linear operator regardless of architecture (MLP, CNN, Transformer) using the canonical (input-channel perm × output-channel perm) group action. The Monomial-NFN paper [Tran, Vo et al., 2024] establishes that this group contains the dominant symmetry structure of MLP/CNN layers; the Transformer-NFN framework [Tran-Viet et al., 2025] extends it to attention heads via S_h. By encoding these orbits, the model's positional information becomes architecture-agnostic, enabling cross-architecture transfer.

**Testable Predictions:**
- P1: OVR_perm < 0.05 (orbit-PE achieves permutation invariance), OVR_GL > 0.15 (permutation-only, not accidentally GL-invariant)
- P2: Var_perm / (Var_perm + Var_GL) > 0.60 in model zoo checkpoint geometry
- P3: <0.1% accuracy change under canonical channel permutations on CNN and Transformer checkpoints

**Experimental Setup:** Small CNN Zoo (NFN paper benchmarks) + Small Transformer Zoo (125K checkpoints, MNIST+AGNews tasks, from Transformer-NFN paper). Baselines: vanilla SANE, Transformer-NFN (in-architecture only). Training: SANE+orbit-PE on CNN Zoo only, zero-shot evaluation on Transformer Zoo. ~22 GPU-hours on A100.

**Novelty:** First cross-architecture zero-shot weight-based property prediction; first use of orbit-PE for weight tokenization; OVR decomposition as a new diagnostic tool for symmetry-transfer efficiency in WSL.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- GL symmetry component (GL_Dk × GL_Dv) of the Transformer weight space is not handled by orbit-PE — may limit in-architecture performance vs Transformer-NFN (≈0.90 τ expected vs ≈0.905–0.910 Transformer-NFN)
- Variance dominance assumption (P2) must be verified before large-scale cross-architecture experiments; if GL variance > 40%, the ceiling is structurally limited
- Architecture confound risk: CNN Zoo and Transformer Zoo differ in parameter count and task — must remove architecture identifiers and match parameter distributions
- **Mitigation Strategy:** Run P2 variance decomposition as the gating pre-experiment before cross-architecture transfer. If Var_perm / (Var_perm + Var_GL) < 0.60, pivot to hybrid orbit-PE + low-degree invariant polynomial traces (tr(W^Q W^{K,T}) per head) to approximate GL structure, adding modest compute overhead but maintaining SANE's scalability advantage.

