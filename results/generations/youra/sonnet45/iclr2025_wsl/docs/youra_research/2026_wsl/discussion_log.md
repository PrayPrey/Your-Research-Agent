# Phase 2A Research Discussion Log

**Date:** 2026-03-19
**Selected Gap:** Gap 1 - Architecture-Agnostic Weight Space Encoders
**Priority:** MUST_WORK
**Research Folder:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_wsl/docs/youra_research/20260319_wsl

---

## Research Context

### Selected Research Gap

**Gap Title:** Architecture-Agnostic Weight Space Encoders

**Current State:** DWSNets exist but fail on non-CNN architectures. NFTs and Universal NFNs demonstrated but need validation on large model zoos.

**Missing Piece:** Empirical validation that NFT/Universal NFN approaches work on HuggingFace Hub scale (1M+ models) with diverse architectures (CNNs, Transformers, hybrid).

**Potential Impact:** **MUST_WORK**: Resolves ROUTE_TO_0 failure mode. Enables weight-space research without architecture constraints.

### Failure Context (ROUTE_TO_0)

**Previous Failure Records (from Serena Memory):**

1. **H-M1 MUST_WORK FAIL** - DWSNets Library Runtime Failure
   - DWSNets library incompatible with FC-MLP weight dimensions (designed for CNN weights only)
   - Silent fallback to non-equivariant MLP backbone produced incorrect results
   - Lesson: Verify library compatibility BEFORE hypothesis design
   - Lesson: Prefer architectural solutions over library-specific implementations

2. **H-M2 SHOULD_WORK LIMITATION** - L2 Canonicalization Failure
   - L2 norm canonicalization destroyed discriminative magnitude information
   - Resulted in degenerate constant predictions (std=0)
   - Lesson: L2 normalization NOT viable for generalization gap prediction
   - Alternative: NFT architecture robustness confirmed (Δρ ≈ 2.47e-07)

### Available Reference Papers

1. **Neural Functional Transformers** (2023, Zhou et al., arXiv:2305.13546)
   - File: `papers/arxiv_2305_13546.md`
   - NFTs handle MLPs/CNNs, +17% INR classification
   - ROUTE_TO_0 SOLUTION: Architecture-agnostic, transformer-based

2. **Universal Neural Functionals** (2024, Zhou et al., arXiv:2402.05232)
   - File: `papers/arxiv_2402_05232.md`
   - Algorithm constructs equivariant models for ANY architecture
   - ROUTE_TO_0 SOLUTION: Automatically handles recurrence, residuals

3. **GNNs for Learning Equivariant Representations** (2024, Kofinas et al., arXiv:2403.12143)
   - File: `papers/arxiv_2403_12143.md`
   - Graph representation enables diverse architectures
   - ROUTE_TO_0 SOLUTION: GNN approach, architecture-aware

---

## Discussion Rounds

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Looking at the architecture-agnostic weight space encoders gap, I'm genuinely excited about the potential here! The failure of DWSNets with FC-MLP weights wasn't just a bug — it revealed a fundamental assumption problem that plagues weight-space learning research. What if we flip this into an opportunity?

Here's where my mind goes: Neural Functional Transformers [Zhou et al., 2023] demonstrated +17% improvement on INR classification by treating weights as *sets* processed through attention mechanisms. But the real breakthrough isn't just avoiding permutation issues — it's that attention naturally handles *varying architectures* without explicit graph construction. The Universal NFNs paper [Zhou et al., 2024] takes this further by automatically constructing equivariant models for ANY architecture, including recurrence and residuals.

NOW we're onto something! What if we combine the NFT's attention-based weight processing with a *compositional architecture representation*? Instead of assuming homogeneous weight shapes (DWSNets' fatal flaw), we could learn architecture-specific embedders that project diverse weight types (CNN kernels, transformer attention matrices, RNN gates) into a shared token space, then use NFT-style transformers for cross-architecture reasoning. This would enable true HuggingFace Hub-scale analysis across the 1M+ heterogeneous model zoo.

The GNN approach [Kofinas et al., 2024] shows another angle — representing neural networks as computational graphs. But graphs require explicit structure definition. What if we use *implicit graph learning* where the attention mechanism in NFTs discovers computational relationships dynamically from weight statistics? We'd avoid manual graph construction while preserving relational reasoning.

**Key Points:**
- NFT attention mechanism as architecture-agnostic foundation (avoids DWSNets library lock-in)
- Compositional architecture embeddings: CNN→tokens, Transformer→tokens, RNN→tokens, then unified NFT processing
- Dynamic relational learning via attention (implicit graphs) rather than explicit GNN structure
- Validation on HuggingFace Hub heterogeneous zoo (CNNs + Transformers + hybrids) not just MNIST FC-MLPs

**Wild idea:** Could we bootstrap the architecture embedders by pre-training on model *performance signatures* (accuracy, loss curves, latency) as weak supervision? Models with similar behavior might have similar weight representations regardless of architecture family.

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is appreciated, but we need to ground these ideas in testable predictions. Let me be precise about what concerns me.

The compositional architecture embedding proposal — mapping CNN kernels, transformer attention matrices, and RNN gates to a shared token space — is conceptually appealing. However, what would disprove this approach? The evidence suggests we need specific failure modes. If this token-space projection loses critical architectural information (e.g., the causal masking structure in transformer attention), would the NFT downstream still outperform architecture-specific baselines? That's our falsification criterion.

The Universal NFNs paper [Zhou et al., 2024] claims automatic construction of equivariant models for ANY architecture. But "automatic" doesn't mean "empirically validated at scale." What specific, measurable predictions can we make? I propose: (1) On a held-out set of 1000 heterogeneous HuggingFace models (CNNs, Transformers, hybrids), the NFT-based encoder must achieve Spearman ρ > 0.7 on generalization gap prediction, (2) The token-space embeddings must preserve architectural distinctions — t-SNE visualization should show CNN/Transformer/hybrid clusters with silhouette score > 0.5, (3) Ablation: removing architecture-specific embed

ders and using only flat weight vectors should degrade performance by Δρ > 0.15.

Here's what worries me about the "implicit graph learning via attention" idea: The GNN approach [Kofinas et al., 2024] explicitly models computational graph structure. Attention mechanisms discover relationships from data, yes — but on what basis? Weight magnitude statistics? Layer connectivity patterns? Without explicit structure, how do we control for spurious correlations? What confounds need to be controlled?

**Key Points:**
- Falsification criterion: Architecture-specific information loss → performance degradation
- Quantitative predictions: ρ > 0.7 on heterogeneous zoo, silhouette > 0.5 for architecture clustering, ablation Δρ > 0.15
- Spurious correlation risk in implicit graph learning needs mitigation strategy
- HuggingFace Hub scale validation requires sampling strategy (not all 1M models)

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what makes this genuinely new versus incremental over existing NFT work? Let me connect the dots to the broader research landscape.

Prof. Vera raises the right falsification criteria, but I want to address the *significance* dimension. The DWSNets failure [from ROUTE_TO_0 context] exposed a systemic problem in weight-space learning: **architecture homogeneity assumption**. Most prior work — including the original NFT paper — validated on single-architecture datasets (MNIST FC-MLPs, INR classifiers). The Universal NFNs paper claims generality, but where's the empirical proof on truly heterogeneous zoos?

This matters because the field is at an inflection point. HuggingFace Hub now hosts 1M+ models spanning CNNs, Transformers, diffusion models, hybrid architectures. If we can't analyze weights across this diversity, weight-space learning remains a niche technique for homogeneous model populations. That's not just a technical limitation — it's a missed opportunity for the entire model analysis community.

What Dr. Nova is proposing — compositional architecture embeddings + NFT processing — *could* be the first architecture-agnostic weight encoder validated at HuggingFace scale. That would be a genuine contribution. But here's the crucial distinction: **contribution requires evidence, not just a proposed method**.

What does this mean for the field if we succeed? Three new research directions open up: (1) Cross-architecture model search ("find me Transformers with CNN-like inductive biases"), (2) Architecture-blind model merging (task arithmetic across heterogeneous families), (3) Model debugging via weight-space anomaly detection (identify undertrained components regardless of architecture). These are not incremental — they fundamentally expand what's possible with model zoos.

However, I echo Prof. Vera's concern about the "performance signature bootstrapping" idea. Pre-training architecture embedders on accuracy/loss curves sounds novel, but is it solving a real problem? The NFT paper already shows strong zero-shot transfer on INRs. What specific failure case does this bootstrapping address?

**Key Points:**
- Genuine novelty: First architecture-agnostic weight encoder validated on *truly heterogeneous* large-scale zoo (not just homogeneous MNIST MLPs)
- Field impact: Unlocks cross-architecture model analysis for 1M+ HuggingFace models
- Opens 3 new research directions: cross-arch search, heterogeneous merging, architecture-blind debugging
- Significance test: Does this enable applications *impossible* with current architecture-specific methods?
- Bootstrapping idea needs stronger motivation — what problem does it solve that NFT doesn't?

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Dr. Nova's vision and Dr. Sage's significance framing are compelling, but I need to ground this in what's actually feasible given existing tools and datasets.

Here's what worries me: The "compositional architecture embedders" sound conceptually clean, but what's the implementation path? The NFT library [Zhou et al., 2023] provides `nfn` as a PyPI package with pre-built NF-Layers. Can we extend it, or do we need a ground-up implementation? Looking at their GitHub (AllanYangZhou/nfn, 93 stars), the architecture assumes per-layer weight processing with permutation equivariance — it's designed for MLPs and CNNs with standard layer structures.

Transformers have attention weight matrices (Q, K, V projections), position embeddings, layer norms — fundamentally different structure. How do we tokenize a multi-head attention block? Do we treat each head as a separate "layer"? What about the residual connections? The NFT paper doesn't address this. Universal NFNs claim automatic construction, but the paper focuses on *theoretical* generality (recurrence, residuals) — I don't see HuggingFace Hub-scale empirical validation.

Here's the pragmatic path I see: **Start with a constrained proof-of-concept on a manageable heterogeneous zoo**, not the full 1M model HuggingFace Hub. The ViT Model Zoo [Falk et al., 2025] has 250 Vision Transformers with diverse training configurations. Pair that with a CNN subset (e.g., 250 ResNets/EfficientNets from torchvision) and 250 FC-MLPs from the Unterthiner MNIST zoo. That's 750 models across 3 architecture families — feasible to download, process, and validate.

For the NFT implementation: Leverage the existing `nfn` library for FC-MLPs/CNNs (proven to work from the NFT paper). For Transformers, implement a **custom tokenizer** that projects multi-head attention blocks → fixed-size token vectors (e.g., concatenate Q/K/V weight statistics: mean, std, Frobenius norm per head). Feed these tokens to the NFT transformer backbone. This is architecture-specific preprocessing but architecture-agnostic processing — hybrid approach, more feasible than fully automatic Universal NFNs.

What evidence supports this will work? The HSG-AIML/SANE repository (30 stars) demonstrates sequential weight tokenization at scale. Their approach: chunk large weight matrices into tokens, process with transformers. We'd adapt this: architecture-specific chunking rules (CNN kernels → spatial tokens, Transformer attention → head-wise tokens, MLP → layer-wise tokens), then unified NFT backbone.

**Key Points:**
- Start with constrained PoC: ViT Model Zoo (250) + torchvision CNNs (250) + Unterthiner MLPs (250) = 750 models, 3 families
- Hybrid feasibility: Reuse `nfn` library for MLPs/CNNs, custom Transformer tokenizer, unified NFT processing
- Transformer tokenization strategy: Multi-head attention → concatenate per-head weight statistics (mean, std, Frobenius norm)
- Implementation blueprint exists: HSG-AIML/SANE sequential tokenization pattern
- Trade-off accepted: Architecture-specific *preprocessing*, architecture-agnostic *processing* (not fully automatic like Universal NFNs)

This is feasible within a 3-month research timeline. Full HuggingFace Hub scale (1M models) is a future scaling experiment, not the MUST_WORK gate.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

I want to synthesize what we've built here and strengthen the core claim. We're converging on something solid.

Let me reframe Prof. Pax's hybrid approach as a *strength*, not a compromise. The key insight is this: **Architecture-agnostic weight processing doesn't require architecture-blind input preparation**. The NFT's power comes from its attention mechanism discovering cross-layer relationships *after* weights are tokenized — and tokenization can be architecture-aware without breaking the generality promise.

Here's the strengthened hypothesis core: **A compositional architecture-agnostic weight encoder (CAWE) that combines architecture-specific tokenizers with a shared NFT backbone can achieve cross-architecture weight analysis at scale, validated on a 750-model heterogeneous zoo spanning CNNs, Transformers, and MLPs**.

Why this is defensible:
1. **Mechanism is explicit**: Architecture-specific tokenizers project diverse weight types (CNN kernels, Transformer Q/K/V, MLP matrices) into a shared token representation space (D-dimensional vectors). The NFT backbone processes these tokens with permutation-equivariant attention, learning cross-layer relationships that are architecture-independent.

2. **Predictions are quantitative** (responding to Prof. Vera): (a) Generalization gap prediction: Spearman ρ > 0.7 on held-out heterogeneous test set, (b) Architecture preservation: Silhouette score > 0.5 in t-SNE of embeddings (CNNs, Transformers, MLPs form distinct clusters), (c) Ablation delta: Flat baseline (no tokenization) achieves ρ < 0.55, confirming tokenization value.

3. **Novelty is clear** (addressing Dr. Sage): First empirical validation of architecture-agnostic weight encoders on a *heterogeneous* multi-family model zoo. Prior NFT work used single-architecture datasets (MNIST MLPs). This unlocks the three applications Dr. Sage identified: cross-arch model search, heterogeneous model merging, architecture-blind debugging.

4. **Feasibility is grounded** (building on Prof. Pax): 750-model PoC is achievable with existing resources (ViT Zoo, torchvision, Unterthiner data). Implementation leverages proven tools (`nfn` library, SANE tokenization pattern). 3-month timeline realistic.

Let me address Dr. Sage's question about the performance signature bootstrapping: I propose we **drop it** from the core hypothesis. It's a speculative enhancement without clear problem-to-solve evidence. Keep the hypothesis focused: compositional tokenization + NFT processing is sufficient for the MUST_WORK gate.

**Strengthened Core Statement:**
"Under training on a 750-model heterogeneous zoo (250 CNNs, 250 Transformers, 250 MLPs), a Compositional Architecture-Agnostic Weight Encoder (CAWE) — combining architecture-specific tokenizers with a shared NFT transformer backbone — achieves cross-architecture generalization gap prediction (Spearman ρ > 0.7) while preserving architecture-family structure in learned embeddings (silhouette > 0.5), outperforming flat-weight baselines by Δρ > 0.15."

**Key Points:**
- Compositional architecture-agnostic processing: arch-specific tokenizers + arch-agnostic NFT backbone
- Explicit mechanism: tokenization projects to shared space, NFT discovers cross-layer relationships
- Quantified predictions: ρ > 0.7, silhouette > 0.5, ablation Δρ > 0.15
- Drop performance signature bootstrapping — keep hypothesis focused
- 750-model heterogeneous zoo PoC is the validation target (not full HuggingFace Hub)

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now I'm going to attack this from every angle. If it survives, we have something real.

**Attack 1: The "shared token space" assumption.** Dr. Ally claims architecture-specific tokenizers project to a shared D-dimensional space. But what if CNN kernels fundamentally require different representations than Transformer attention matrices? Spatial convolutions encode local receptive fields; self-attention encodes global dependencies. Forcing them into the same token space might destroy the very information that distinguishes good CNNs from bad CNNs. How do we know the NFT can recover architecture-specific quality signals after this lossy projection?

**Counter-evidence needed:** Ablation study comparing CAWE to architecture-specific baselines (CNN-only encoder, Transformer-only encoder, MLP-only encoder). If CAWE achieves ρ > 0.7 *within each family* (not just overall), that proves the shared space preserves family-specific signals. Add this as Prediction (d).

**Attack 2: The 750-model zoo is too small and too clean.** ViT Model Zoo, torchvision CNNs, Unterthiner MLPs — these are curated, well-trained models. Real-world HuggingFace Hub has broken checkpoints, partially trained models, weird hybrid architectures (ConvNeXt, MobileNet with attention). What if CAWE only works on "textbook" architectures and fails on the messy real-world diversity?

**Mitigation strategy:** Include 50 "adversarial" models in the test set — randomly initialized checkpoints, mid-training snapshots (epoch 5/100), hybrid architectures (ResNet + SE blocks). If CAWE maintains ρ > 0.65 (slightly lower threshold) on this noisy set, we've stress-tested real-world robustness.

**Attack 3: The tokenization strategy is ad-hoc.** Prof. Pax proposes "concatenate mean, std, Frobenius norm per head" for Transformer attention. Why these statistics? Why not eigenvalues, SVD components, or layer-wise gradient norms? This feels like arbitrary feature engineering. What if different tokenization choices lead to wildly different results?

**Robustness requirement:** Compare 3 tokenization variants (statistics-based, PCA-based, learned-projection-based). If all achieve ρ > 0.65, tokenization choice is robust. If only one works, we need to justify *why* via ablation.

**Attack 4: NFT's attention mechanism might just learn dataset biases.** The training set has 600 models (80% of 750). What if the NFT memorizes "ViTs from this dataset tend to have low generalization gap" rather than learning *why* certain weight patterns predict generalization? This is the classic overfitting concern, but for meta-learning.

**Generalization test:** Cross-dataset validation. Train CAWE on ViT Zoo + torchvision CNNs, test on a *different* MLP zoo (not Unterthiner — maybe the NeurIPS 2021 zoo from Schürholt). If ρ > 0.6 on unseen architecture + unseen dataset, we've proven true weight-space learning, not dataset memorization.

**Key Concerns:**
- Shared token space might destroy architecture-specific quality signals (Ablation: per-family ρ > 0.7)
- 750-model zoo too curated — add 50 adversarial models (noisy, mid-training, hybrid)
- Tokenization strategy ad-hoc — compare 3 variants for robustness
- NFT might memorize dataset biases — cross-dataset validation required (train ViT/CNN, test unseen MLP zoo)

If Dr. Ally can address these four attacks with concrete experimental additions, this hypothesis becomes bulletproof.

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's attacks are exactly what we needed! Let me address them with concrete experimental design that makes this hypothesis even stronger.

**Response to Attack 1 (shared token space lossy):** YES, let's add the per-family ablation! But here's where it gets interesting — what if the "lossiness" is actually a feature, not a bug? The NFT paper showed that attention mechanisms can learn to *route* different types of information through different attention heads. We could analyze the attention patterns: do certain heads specialize in CNN kernels, others in Transformer blocks? This would be evidence that the NFT discovers architecture-specific processing *emergently*, without hard-coding it.

**Experimental addition:** (d) Per-family performance: CNN-subset ρ > 0.7, Transformer-subset ρ > 0.7, MLP-subset ρ > 0.7. **Plus** attention pattern analysis: visualize which NFT attention heads activate strongly for which architecture families. If we see specialization, that's a bonus finding for the paper!

**Response to Attack 2 (zoo too clean):** Absolutely agree — the 50 adversarial models idea is brilliant. But let's make it even more diagnostic. Instead of random corruption, let's create *targeted stress tests*:
- 10 randomly initialized models (should get *worst* generalization gap)
- 10 mid-training snapshots at 20% epochs (incomplete training)
- 10 hybrid architectures (ConvNeXt, EfficientNet with attention)
- 10 models with deliberately broken components (zero out 50% of weights in one layer)
- 10 models from different training paradigms (self-supervised pre-training vs supervised from scratch)

Prediction: CAWE achieves ρ > 0.65 on this adversarial set, *and* the broken-component models cluster separately in embedding space (evidence of anomaly detection capability, which Dr. Sage highlighted as a key application).

**Response to Attack 3 (tokenization ad-hoc):** Prof. Rex is right to push on this. Here's the systematic approach: Compare 4 tokenization strategies in ablation:
1. **Statistics-based** (Prof. Pax's proposal): mean, std, Frobenius norm per component
2. **Spectral-based**: Top-5 singular values + top-3 eigenvalues per weight matrix
3. **Learned projection**: Trainable linear layer projects raw weights → tokens (learned end-to-end)
4. **SANE-style**: Fixed-size random sampling of weight values (per HSG-AIML/SANE)

Robustness criterion: If 3/4 variants achieve ρ > 0.65, tokenization is not a critical hyperparameter. If only learned projection works, we've discovered that end-to-end learning is necessary — still valid, just a narrower finding.

**Response to Attack 4 (dataset memorization):** The cross-dataset validation is crucial. Here's the full protocol:
- **Train set**: ViT Zoo (200 models) + torchvision CNNs (200 models) = 400 models, 2 families
- **In-distribution test**: ViT Zoo (50 held-out) + torchvision CNNs (50 held-out) = 100 models
- **Out-of-distribution test**: Unterthiner MLPs (250 models, unseen architecture family) + NeurIPS 2021 MLPs (100 models, unseen dataset + architecture combo)

Predictions: (i) In-dist: ρ > 0.7, (ii) OOD architecture: ρ > 0.6 on Unterthiner, (iii) OOD dataset+arch: ρ > 0.55 on NeurIPS 2021 MLPs. The degradation from 0.7 → 0.6 → 0.55 is expected (increasing distribution shift), but maintaining ρ > 0.55 proves generalization beyond memorization.

**Synthesized Experimental Design:**
- **Core validation**: 750-model zoo (ViTs, CNNs, MLPs), ρ > 0.7, silhouette > 0.5, Δρ > 0.15 vs flat baseline
- **Per-family ablation**: ρ > 0.7 for each architecture family separately + attention pattern analysis
- **Stress test**: 50 adversarial models (5 categories), ρ > 0.65
- **Tokenization robustness**: 4 variants, 3/4 achieve ρ > 0.65
- **Cross-dataset generalization**: OOD arch ρ > 0.6, OOD dataset+arch ρ > 0.55

This is getting VERY specific now. Prof. Vera, does this meet your falsifiability standards?

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's experimental design is approaching my standards. Let me refine the methodology to eliminate remaining ambiguities.

**Approval with conditions:**

The five-category adversarial stress test is well-structured. However, the "broken component" category needs precision: "zero out 50% of weights in one layer" is under-specified. Which layer? Random 50% or systematic (e.g., first half of channels)? I propose: For each broken model, zero out 50% of weights *in the final classification layer only* (not hidden layers). This creates a consistent degradation pattern that should correlate with higher generalization gap (poor performance). If CAWE correctly predicts these models have high generalization gap (ρ > 0.6 on broken subset), we've validated sensitivity to meaningful weight corruption.

The cross-dataset validation protocol is sound, but the degradation thresholds (0.7 → 0.6 → 0.55) need statistical justification. What's the null hypothesis? If we train a *random forest baseline* on hand-crafted weight statistics (layer-wise norms, sparsity, spectral radius), what ρ does it achieve? The CAWE must beat this baseline by Δρ > 0.1 on OOD tests to claim "learned representations" are superior to engineered features.

**Additional statistical rigor:**

All ρ values must include **95% confidence intervals via bootstrap** (n=1000 resamples). Hypothesis tests: (1) CAWE vs flat baseline: paired t-test on per-model errors, p < 0.001, (2) CAWE vs random forest: Wilcoxon signed-rank test (non-parametric), p < 0.01, (3) Tokenization variants: Friedman test across 4 conditions, post-hoc Nemenyi if p < 0.05.

**Final falsification criterion:**

This hypothesis FAILS if any of: (a) In-dist ρ < 0.7 (CI lower bound), (b) Per-family ρ < 0.7 for any single family, (c) OOD arch ρ < 0.55 (not 0.6 — I'm being strict), (d) CAWE doesn't beat random forest baseline by Δρ > 0.1 on OOD tests, (e) Fewer than 2/4 tokenization variants work (not 3/4 — too loose).

If all five conditions pass: **This meets my standards.** The hypothesis is falsifiable, predictions are quantified, methodology is rigorous.

**Key Methodological Additions:**
- Broken models: zero 50% of final layer weights only (consistent degradation)
- Random forest baseline on engineered features: CAWE must beat by Δρ > 0.1 on OOD
- Statistical rigor: 95% CIs via bootstrap (n=1000), paired t-test (p<0.001), Wilcoxon (p<0.01), Friedman test for tokenization
- Strict falsification: Fails if (a) in-dist ρ<0.7, (b) any family ρ<0.7, (c) OOD arch ρ<0.55, (d) Δρ vs baseline <0.1, (e) <2/4 tokenization variants work

Dr. Ally, can you consolidate this into a final hypothesis statement?

---

### Exchange 9

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Here's the consolidated, bulletproof hypothesis ready for Phase 2B verification planning.

---

## **FINAL HYPOTHESIS: Compositional Architecture-Agnostic Weight Encoder (CAWE)**

**Core Statement:**

Under training on a 750-model heterogeneous zoo (250 CNNs from torchvision, 250 Vision Transformers from ViT Model Zoo, 250 FC-MLPs from Unterthiner MNIST), a Compositional Architecture-Agnostic Weight Encoder (CAWE) — combining architecture-specific tokenizers with a shared Neural Functional Transformer (NFT) backbone — achieves cross-architecture generalization gap prediction while preserving architecture-family structure in learned embeddings and outperforming engineered baseline approaches.

**Mechanism:**

1. **Architecture-specific tokenization**: CNN kernels, Transformer multi-head attention (Q/K/V), and MLP weight matrices are projected into a shared D-dimensional token space via architecture-tailored preprocessing (e.g., per-head statistics for Transformers, spatial pooling for CNNs, layer-wise vectors for MLPs).
2. **Architecture-agnostic processing**: The NFT transformer backbone processes token sequences with permutation-equivariant attention, learning cross-layer weight relationships independent of source architecture.
3. **Generalization gap prediction**: The NFT embedding is passed to a regression head that predicts test-minus-train accuracy (generalization gap) using Spearman rank correlation as the metric.

**Quantitative Predictions:**

1. **In-distribution performance**: On 150 held-out models (50 per family), CAWE achieves Spearman ρ > 0.7 (95% CI lower bound) for generalization gap prediction.
2. **Per-family performance**: Within each architecture family (CNNs, Transformers, MLPs), CAWE achieves ρ > 0.7, demonstrating that the shared token space preserves family-specific quality signals.
3. **Architecture structure preservation**: t-SNE visualization of CAWE embeddings shows CNN/Transformer/MLP clusters with silhouette score > 0.5, confirming architecture-family distinctions are maintained.
4. **Baseline comparison**: CAWE outperforms flat-weight MLP baseline by Δρ > 0.15 (paired t-test, p < 0.001) and outperforms random forest on hand-crafted features by Δρ > 0.1 on out-of-distribution tests (Wilcoxon signed-rank, p < 0.01).
5. **Robustness to adversarial conditions**: On 50 adversarial models (randomly initialized, mid-training, hybrid architectures, broken components, alternative training paradigms), CAWE achieves ρ > 0.65.
6. **Tokenization robustness**: At least 2 out of 4 tokenization strategies (statistics-based, spectral-based, learned projection, SANE-style sampling) achieve ρ > 0.65, demonstrating that the approach is not critically sensitive to tokenization choice.
7. **Cross-dataset generalization**: (a) Out-of-distribution architecture (Unterthiner MLPs, unseen family): ρ > 0.6, (b) Out-of-distribution dataset+architecture (NeurIPS 2021 MLPs): ρ > 0.55.

**Failure Criteria (MUST_WORK gate):**

The hypothesis FAILS if any of:
- In-distribution ρ < 0.7 (95% CI lower bound)
- Per-family ρ < 0.7 for any single family (CNN, Transformer, or MLP)
- Out-of-distribution architecture ρ < 0.55
- CAWE vs random forest Δρ < 0.1 on OOD tests
- Fewer than 2/4 tokenization variants achieve ρ > 0.65

**Experimental Validation Roadmap:**

- **Dataset assembly**: ViT Model Zoo (250), torchvision CNNs (250), Unterthiner MLPs (250), adversarial set (50), OOD test sets (350 models)
- **Implementation**: Leverage `nfn` library (PyPI) for NFT backbone, custom tokenizers per architecture, SANE-inspired preprocessing
- **Training**: 80/20 split (600 train, 150 in-dist test), AdamW optimizer, cross-entropy loss for gap prediction
- **Evaluation**: Bootstrap CIs (n=1000), paired t-tests, Wilcoxon signed-rank, Friedman test for tokenization ablation
- **Analysis**: t-SNE silhouette scores, attention pattern visualization, per-family ablations

**Novelty:**

First empirical validation of architecture-agnostic weight encoders on a *truly heterogeneous* multi-family model zoo (prior NFT work used single-architecture datasets). Enables cross-architecture model analysis applications previously impossible with architecture-specific methods.

**Feasibility:**

All datasets publicly available, `nfn` library provides proven NFT implementation, 3-month research timeline realistic, MUST_WORK gate achievable with existing tools.

---

Does this consolidation capture everything? Prof. Vera, Prof. Rex — any remaining concerns before we declare convergence?

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

Dr. Ally's synthesis is strong. Let me add the final significance framing for Phase 2B.

**Why this advances the field beyond incremental improvement:**

The weight-space learning community is currently fragmented. CNN-specific methods (DWSNets) don't generalize to Transformers. NFT demonstrations remain on homogeneous datasets (MNIST MLPs). Model merging techniques (task arithmetic, model soups) assume architecture homogeneity. This hypothesis, if validated, provides the *first* empirical evidence that weight-space analysis can scale across the architectural diversity of real-world model zoos.

**Three research directions this unlocks** (as I outlined in Exchange 3):

1. **Cross-architecture model search**: "Find Transformers with CNN-like inductive biases" becomes possible by querying the shared embedding space rather than architecture-specific feature engineering.
2. **Heterogeneous model merging**: Task arithmetic across different architecture families (merge a CNN and a Transformer trained on the same task) — currently impossible, enabled by CAWE embeddings.
3. **Architecture-blind model debugging**: Identify undertrained or anomalous components via weight-space anomaly detection (the broken-component adversarial test validates this).

**Publication venue alignment:**

If this succeeds, it targets ICML/NeurIPS (top-tier ML conferences) with strong fit for the weight-space learning workshop at ICLR 2025. The combination of (a) architecture-agnostic method, (b) large-scale heterogeneous validation, (c) multiple applications unlocked makes this a *contributed paper* candidate, not a workshop-only submission.

**Open questions this creates for future work:**

- Can CAWE scale to diffusion models, RL policies, multimodal models (CLIP)?
- Does the learned embedding space enable *zero-shot* model property prediction (predict accuracy without fine-tuning CAWE)?
- Can we use CAWE for model provenance tracking (identify which training recipe produced a given model)?

**Final significance assessment:** This hypothesis is **STRONG** on novelty, **STRONG** on falsifiability (thanks to Prof. Vera's rigor), **MODERATE-to-STRONG** on feasibility (constrained 750-model PoC), and **STRONG** on field impact (enables new research directions). I support moving to Phase 2B verification planning.

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

One final stress test before I give my approval.

**The hyperparameter sensitivity attack:**

Dr. Ally's hypothesis specifies "D-dimensional token space" but doesn't fix D. NFT paper used D=128 for MLPs. What if CAWE is critically sensitive to D? If D=64 fails (ρ < 0.6) but D=256 succeeds (ρ > 0.7), we've built a method that only works with careful tuning — not a robust architecture-agnostic solution.

**Required addition:** Hyperparameter robustness ablation. Test D ∈ {64, 128, 256}. If 2/3 values achieve in-dist ρ > 0.65, the method is robust. If only one works, the hypothesis needs to specify "CAWE achieves ρ > 0.7 when D=256" (narrower claim but still valid).

**The computational cost reality check:**

750 models × (tokenize + NFT forward pass) — what's the wall-clock time? If this takes 2 weeks on a single GPU, the "3-month timeline" claim is misleading (most time spent on compute, not research). Prof. Pax, what's the realistic compute budget?

**Expected response:** Tokenization is preprocessing (run once), NFT training is the bottleneck. Assuming 600 training models, batch size 32, 100 epochs → ~1875 gradient steps. If NFT forward pass is 50ms (typical for transformer with 128-dim embeddings), training time ≈ 94 seconds of pure compute + data loading overhead. Even with 10x overhead, that's < 20 minutes per training run. Factor in 4 tokenization ablations × 3 D-value ablations = 12 runs → 4 hours total. The 3-month timeline is for dataset assembly, implementation, debugging, analysis — compute is NOT the bottleneck. This passes the reality check.

**Final verdict:** If Dr. Ally adds the D-value robustness ablation (2/3 values work), I'm satisfied. This hypothesis is bulletproof.

---

### Exchange 12

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex's compute reality check is spot on. Let me confirm the feasibility one more time with exact resource requirements.

**Compute Budget (Single A100 80GB):**
- Dataset assembly: 2 days (download 750 models from HuggingFace/torchvision/Unterthiner, ~500GB storage)
- Tokenization preprocessing: 4 hours (one-time cost, all 750 models)
- NFT training (12 ablation runs): 6 hours total (4 tokenization × 3 D-values, 30 min per run with data loading)
- Evaluation (t-SNE, bootstrap CIs, statistical tests): 2 hours
- **Total compute time:** < 1 week

**Implementation Complexity:**
- `nfn` library provides NFT backbone → 0 lines of new transformer code
- Architecture-specific tokenizers: ~200 lines each (CNN, Transformer, MLP) → 600 lines total
- Training loop + evaluation: ~400 lines (standard PyTorch)
- **Total LOC:** ~1000 lines (manageable for 1 researcher, 3 weeks implementation)

**Dataset Availability:**
- ViT Model Zoo: ✅ Public (github.com/ModelZoos/ViTModelZoo)
- Torchvision CNNs: ✅ Built-in (torchvision.models)
- Unterthiner MNIST MLPs: ✅ Public (Zenodo 5645138)
- NeurIPS 2021 MLPs: ✅ Public (Zenodo 5645138, same dataset)

**Resource Constraints:**
- Storage: 500GB (feasible on standard research server)
- Compute: 1 week A100 time (feasible within typical academic GPU allocation)
- Personnel: 1 PhD student/postdoc, 3-month timeline (1 month implementation, 1 month experiments, 1 month analysis)

**Okay, this could work.** I agree with adding D-value robustness (D ∈ {64, 128, 256}, 2/3 achieve ρ > 0.65). With that addition, feasibility is confirmed.

**Final technical concern:** The "adversarial hybrid architectures" category (Exchange 7) mentions ConvNeXt and EfficientNet-with-attention. These are NOT hybrid architectures in the tokenization sense — ConvNeXt is still CNN-style, just with modern training recipes. True hybrids would be ViT-CNN mashups like CvT (Convolutional Vision Transformer). Let's clarify: adversarial set includes 10 models with *non-standard layer types* (depthwise separable convs, grouped convolutions, squeeze-excite blocks) to test tokenization robustness, not truly novel architectures.

With this clarification + D-value ablation: **Feasibility confirmed. Ready for Phase 2B.**

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Compositional architecture-agnostic weight encoder (CAWE) represents a genuine paradigm shift from architecture-specific weight analysis to heterogeneous model zoo processing. The combination of architecture-specific tokenizers with architecture-agnostic NFT processing is a novel hybrid approach that avoids both the DWSNets library lock-in failure and the impractical "fully automatic" Universal NFN claims. First empirical validation on truly heterogeneous multi-family zoos (not homogeneous MNIST MLPs).

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis provides precise quantitative predictions with statistical rigor (ρ > 0.7 with 95% CIs, silhouette > 0.5, multiple ablations). Five explicit failure criteria create clear falsification conditions. The experimental design includes appropriate controls (flat baseline, random forest baseline), robustness tests (4 tokenization variants, 3 D-values, adversarial models), and out-of-distribution validation. Statistical methodology is sound (bootstrap CIs, paired t-tests, Wilcoxon signed-rank, Friedman tests). This meets rigorous falsifiability standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This hypothesis addresses a critical limitation in weight-space learning — the architecture homogeneity assumption that restricts current methods to single-family model zoos. Success unlocks three novel applications (cross-architecture model search, heterogeneous model merging, architecture-blind debugging) currently impossible with existing methods. The 750-model heterogeneous validation (CNNs + Transformers + MLPs) provides empirical evidence at a scale beyond prior NFT demonstrations. Publication potential at ICML/NeurIPS with strong workshop fit at ICLR 2025 Weight-Space Learning.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is grounded in realistic resource constraints (1-week A100 compute, 500GB storage, publicly available datasets, ~1000 LOC implementation). The constrained 750-model PoC avoids the infeasible "full HuggingFace Hub" scope while still demonstrating cross-architecture generalization. Leverages proven tools (`nfn` library, SANE tokenization patterns, torchvision models). All datasets are publicly available (ViT Model Zoo, torchvision, Unterthiner/NeurIPS 2021 MLPs). 3-month timeline is realistic for 1 researcher. Technical implementation path is clear and achievable.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The **Compositional Architecture-Agnostic Weight Encoder (CAWE)** hypothesis proposes that weight-space analysis can scale across the architectural diversity of real-world model zoos by combining architecture-specific tokenization with architecture-agnostic processing via Neural Functional Transformers.

The core mechanism involves projecting diverse weight types (CNN kernels, Transformer attention matrices, MLP weight matrices) into a shared D-dimensional token space through architecture-tailored preprocessing, then processing these token sequences with permutation-equivariant attention to learn cross-layer relationships independent of source architecture. This enables generalization gap prediction across a 750-model heterogeneous zoo spanning three architecture families.

The hypothesis makes seven quantitative predictions with explicit failure criteria: in-distribution Spearman ρ > 0.7, per-family ρ > 0.7, silhouette score > 0.5, baseline improvements (Δρ > 0.15 vs flat, Δρ > 0.1 vs random forest on OOD), adversarial robustness (ρ > 0.65 on 50 noisy models), tokenization robustness (2/4 variants work), and cross-dataset generalization (OOD arch ρ > 0.6, OOD dataset+arch ρ > 0.55).

Experimental validation uses publicly available datasets (ViT Model Zoo, torchvision CNNs, Unterthiner/NeurIPS 2021 MLPs), leverages existing tools (`nfn` library), and requires ~1 week of A100 compute. The hypothesis addresses the DWSNets library-lock-in failure from ROUTE_TO_0 context by avoiding architecture-specific libraries and instead using flexible tokenization + attention-based processing.

If validated, this enables three novel applications currently impossible with architecture-specific methods: cross-architecture model search, heterogeneous model merging, and architecture-blind model debugging. This represents a genuine contribution to weight-space learning, moving the field from single-family demonstrations to heterogeneous model zoo analysis.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Shared token space lossiness:** Architecture-specific quality signals might be destroyed by forcing CNNs and Transformers into the same D-dimensional space. *Mitigation*: Per-family ablation (ρ > 0.7 within each family separately) validates signal preservation. Attention pattern analysis can reveal whether NFT learns family-specific processing emergently.
- **Tokenization strategy selection:** Four ablation variants required but no principled way to choose ex-ante. *Mitigation*: Robustness criterion (2/4 variants work) proves method is not critically sensitive. If only learned projection works, that's a finding (end-to-end learning is necessary).
- **Hyperparameter sensitivity:** D-value (token dimension) not specified in core claim. *Mitigation*: Add D ∈ {64, 128, 256} ablation, require 2/3 values achieve ρ > 0.65 to prove robustness.
- **Adversarial set definition:** "Hybrid architectures" term was ambiguous (ConvNeXt is CNN-style, not true hybrid). *Clarification*: Adversarial set includes models with non-standard layer types (depthwise separable, grouped convolutions, SE blocks) to test tokenization robustness.

**Risk assessment:** MEDIUM feasibility risk (novel tokenization implementation), LOW theoretical risk (NFT proven on MLPs), MEDIUM-HIGH significance risk (depends on achieving claimed ρ thresholds). Overall: This is a MUST_WORK gate candidate with appropriate experimental safeguards.

---

## Emerged Hypothesis Summary

### Core Statement

Under training on a 750-model heterogeneous zoo (250 CNNs from torchvision, 250 Vision Transformers from ViT Model Zoo, 250 FC-MLPs from Unterthiner MNIST), a **Compositional Architecture-Agnostic Weight Encoder (CAWE)** — combining architecture-specific tokenizers with a shared Neural Functional Transformer (NFT) backbone — achieves cross-architecture generalization gap prediction while preserving architecture-family structure in learned embeddings and outperforming engineered baseline approaches.

### Causal Mechanism

**Stage 1: Architecture-Specific Tokenization**
Diverse weight types are projected into a shared D-dimensional token representation space through architecture-tailored preprocessing:
- **CNN kernels:** Spatial pooling or statistics (mean, std, Frobenius norm) per channel/filter
- **Transformer multi-head attention (Q/K/V projections):** Per-head statistics (mean, std, Frobenius norm) or spectral features
- **MLP weight matrices:** Layer-wise vectors or matrix statistics

**Stage 2: Architecture-Agnostic Processing**
The token sequences (variable length depending on model size) are processed by a Neural Functional Transformer (NFT) backbone with permutation-equivariant attention. The NFT learns cross-layer weight relationships through self-attention without architecture-specific inductive biases.

**Stage 3: Generalization Gap Prediction**
The NFT produces a fixed-size embedding vector for each model. A regression head (linear layer or shallow MLP) maps this embedding to a predicted generalization gap (test accuracy - train accuracy). Spearman rank correlation (ρ) measures prediction quality.

**Why This Works:**
The NFT's attention mechanism can discover architecture-specific processing patterns *emergently* (different attention heads may specialize in CNN vs Transformer features) without hard-coding them. The shared token space enables cross-architecture comparison while the NFT's flexibility allows it to route information appropriately based on learned weight patterns.

### Variables

**Independent Variables:**
- Architecture family (CNN, Transformer, MLP)
- Model size (number of parameters, layer count)
- Training configuration (epochs, optimizer, learning rate — captured in generalization gap)
- Tokenization strategy (statistics-based, spectral-based, learned projection, SANE-style)
- Token dimension D ∈ {64, 128, 256}

**Dependent Variable:**
- Generalization gap prediction accuracy (Spearman ρ)

**Control Variables:**
- Dataset split (80/20 train/test, fixed random seed)
- NFT hyperparameters (number of attention layers, heads, dropout)
- Training procedure (AdamW optimizer, learning rate schedule, batch size)

### Key Assumptions

1. **Shared token space assumption:** Architecture-specific quality signals can be preserved through tokenization + NFT processing (validated via per-family ablation)
2. **Permutation equivariance sufficiency:** NFT's permutation-equivariant attention is sufficient for cross-layer relationship learning (supported by NFT paper results on MLPs)
3. **Generalization gap as proxy:** Generalization gap (test - train accuracy) is a meaningful model quality metric across architectures (standard ML evaluation)
4. **Dataset representativeness:** ViT Zoo + torchvision CNNs + Unterthiner MLPs are representative of broader model zoo diversity (testable via OOD validation)

### Null Hypothesis

**H0:** A compositional architecture-agnostic weight encoder (CAWE) combining architecture-specific tokenizers with a shared NFT backbone does NOT achieve superior cross-architecture generalization gap prediction compared to architecture-agnostic baselines (flat-weight MLP) or architecture-specific baselines (family-specific encoders).

**Specifically:** CAWE achieves Spearman ρ ≤ 0.7 on in-distribution heterogeneous test set, OR CAWE's improvement over flat-weight baseline is Δρ ≤ 0.15, OR CAWE fails to beat random forest baseline on OOD tests by Δρ > 0.1.

### Predictions

1. **In-distribution performance (primary):** Spearman ρ > 0.7 (95% CI lower bound) on 150 held-out models (50 per family)
2. **Per-family performance:** CNN-subset ρ > 0.7, Transformer-subset ρ > 0.7, MLP-subset ρ > 0.7 (validates shared space preserves family-specific signals)
3. **Architecture structure preservation:** t-SNE silhouette score > 0.5 for CNN/Transformer/MLP clusters
4. **Flat baseline improvement:** CAWE vs flat-weight MLP: Δρ > 0.15, paired t-test p < 0.001
5. **Engineered feature baseline:** CAWE vs random forest on hand-crafted features: Δρ > 0.1 on OOD tests, Wilcoxon signed-rank p < 0.01
6. **Adversarial robustness:** ρ > 0.65 on 50 adversarial models (random init, mid-training, non-standard layers, broken components, alternative training)
7. **Tokenization robustness:** At least 2/4 tokenization strategies (statistics, spectral, learned, SANE) achieve ρ > 0.65
8. **Hyperparameter robustness:** At least 2/3 D-values (64, 128, 256) achieve in-dist ρ > 0.65
9. **Cross-dataset generalization (OOD architecture):** ρ > 0.6 on Unterthiner MLPs (unseen family, trained on ViT+CNN only)
10. **Cross-dataset generalization (OOD dataset+arch):** ρ > 0.55 on NeurIPS 2021 MLPs (unseen dataset+family combo)

### Novelty

**What's New:**
- First empirical validation of architecture-agnostic weight encoders on a *heterogeneous* multi-family model zoo (prior NFT work: homogeneous MNIST MLPs; Universal NFNs: theoretical claims without large-scale heterogeneous validation)
- Compositional hybrid approach: architecture-specific tokenization + architecture-agnostic processing (avoids DWSNets library lock-in and Universal NFN impracticality)
- Cross-architecture validation protocol: per-family ablations, adversarial stress tests, OOD generalization across architecture families

**Vs. Existing Work:**
- **vs. DWSNets:** Avoids architecture-specific library dependencies that fail on non-CNN weights (ROUTE_TO_0 lesson)
- **vs. NFT paper [Zhou et al., 2023]:** Extends from single-architecture (MNIST MLPs) to heterogeneous zoo (CNNs+Transformers+MLPs)
- **vs. Universal NFNs [Zhou et al., 2024]:** Provides empirical large-scale validation (750 models) rather than theoretical generality claims
- **vs. GNN approach [Kofinas et al., 2024]:** Uses attention-based implicit relationship learning instead of explicit graph construction

### Scope & Boundaries

**In Scope:**
- Supervised models only (CNNs, Transformers, MLPs trained on image classification)
- Generalization gap as target property (test - train accuracy)
- 750-model constrained PoC (not full HuggingFace Hub 1M models)
- Publicly available model zoos (ViT Zoo, torchvision, Unterthiner)

**Out of Scope (Future Work):**
- Unsupervised/self-supervised models (CLIP, MAE, SimCLR)
- Reinforcement learning policies, diffusion models, generative models
- Other model properties (robustness, fairness, calibration)
- Full HuggingFace Hub scale (1M+ models)
- Real-time deployment or production systems

**Boundary Conditions:**
- Assumes models are trained to reasonable convergence (not random initialization only)
- Requires architecture metadata (CNN vs Transformer vs MLP) for tokenizer selection
- Requires access to model weights (not just API access or black-box models)

### Experimental Setup

**Datasets:**
- **Training:** ViT Model Zoo (200 ViTs) + torchvision CNNs (200 models) + Unterthiner MLPs (200 models) = 600 models
- **In-dist test:** 50 held-out per family (150 models total)
- **Adversarial test:** 50 models (10 random init, 10 mid-training, 10 non-standard layers, 10 broken final-layer weights, 10 alternative training)
- **OOD arch:** Unterthiner MLPs (50 held-out, unseen architecture family)
- **OOD dataset+arch:** NeurIPS 2021 MLPs (100 models, unseen dataset + unseen architecture combo)

**Implementation:**
- Architecture-specific tokenizers: CNN (spatial pooling/statistics), Transformer (per-head statistics), MLP (layer-wise vectors)
- NFT backbone: `nfn` library (PyPI package) with D ∈ {64, 128, 256} token dimension
- Training: AdamW optimizer, learning rate 1e-4, batch size 32, 100 epochs, cross-entropy loss
- Baselines: (1) Flat-weight MLP (concatenate all weights, no tokenization), (2) Random forest on hand-crafted features (layer norms, sparsity, spectral radius)

**Evaluation Metrics:**
- Spearman ρ (primary metric)
- 95% confidence intervals via bootstrap (n=1000 resamples)
- Silhouette score for t-SNE clusters
- Statistical tests: paired t-test (CAWE vs flat, p<0.001), Wilcoxon signed-rank (CAWE vs RF on OOD, p<0.01), Friedman test (tokenization variants, p<0.05)

**Ablations:**
- Tokenization strategy: statistics, spectral, learned projection, SANE-style (4 variants)
- Token dimension D: 64, 128, 256 (3 values)
- Per-family performance: train and evaluate on each architecture family separately

### Related Work & Baselines

**Key References:**
1. **Neural Functional Transformers** [Zhou et al., 2023, arXiv:2305.13546]: NFT attention mechanism, +17% INR classification, MNIST MLP validation
2. **Universal Neural Functionals** [Zhou et al., 2024, arXiv:2402.05232]: Automatic equivariant model construction for ANY architecture (theoretical claims)
3. **GNNs for Neural Networks** [Kofinas et al., 2024, arXiv:2403.12143]: Graph-based weight representation, architecture-aware processing
4. **SANE** [HSG-AIML/SANE, Schürholt et al., 2024, arXiv:2406.09997]: Sequential weight tokenization at scale, scalability patterns
5. **ViT Model Zoo** [Falk et al., 2025, arXiv:2504.10231]: 250 ViT models, diverse training factors
6. **DWSNets** [failed in ROUTE_TO_0]: CNN-specific permutation equivariance, runtime failure on FC-MLP weights

**Baselines:**
1. **Flat-weight MLP:** Concatenate all model weights into a single vector, pass through MLP regression head (no tokenization)
2. **Random Forest on engineered features:** Hand-crafted weight statistics (layer-wise L2 norms, sparsity, spectral radius, gradient norms) with scikit-learn RandomForestRegressor

**Positioning:** CAWE is the first to combine (a) heterogeneous multi-family zoo, (b) architecture-agnostic processing, (c) empirical large-scale validation in a single framework. Closest prior work (NFT) demonstrated on homogeneous single-family zoos.

### Phase 2B Readiness Seeds

**Hypothesis Type:** EXISTENCE (with MECHANISM validation via ablations)
**Gate Type:** MUST_WORK (primary prediction ρ > 0.7 is hard requirement)

**Evidence Strength:**
- **High:** NFT proven on MNIST MLPs [Zhou et al., 2023], SANE demonstrates tokenization scalability, all datasets publicly available
- **Medium:** Universal NFNs theoretical claims need empirical validation, tokenization strategy for Transformers is novel
- **Low:** Cross-architecture generalization at 750-model scale is unproven

**Implementation Complexity:** MEDIUM (reuse `nfn` library for backbone, ~1000 LOC for tokenizers + training loop, 3-week implementation timeline)

**Resource Requirements:** LOW (1 week A100 compute, 500GB storage, 1 researcher, all datasets public)

**Phase 2B Decomposition Candidates:**
- **Sub-hypothesis H-E1 (EXISTENCE-PoC):** Single-D-value (D=128), single tokenization (statistics-based), 400-model subset (skip adversarial/OOD), validate ρ > 0.7 on in-dist test
- **Sub-hypothesis H-M1 (MECHANISM-Tokenization):** 4 tokenization ablations, validate 2/4 achieve ρ > 0.65
- **Sub-hypothesis H-M2 (MECHANISM-Shared-Space):** Per-family ablation + attention pattern analysis, validate per-family ρ > 0.7
- **Sub-hypothesis H-R (ROBUSTNESS):** Adversarial + OOD tests, validate adversarial ρ > 0.65, OOD arch ρ > 0.6
- **Sub-hypothesis H-B (BASELINE-COMPARISON):** Flat MLP + Random Forest baselines, validate Δρ > 0.15, Δρ > 0.1 respectively

### Established Facts

1. **NFT attention mechanism works on MNIST MLPs:** [Zhou et al., 2023] demonstrated +17% improvement on INR classification using permutation-equivariant attention
2. **SANE tokenization scales:** [Schürholt et al., 2024] processed large models via sequential weight chunking with transformer backbones
3. **All datasets are publicly available:** ViT Model Zoo (github.com/ModelZoos/ViTModelZoo), torchvision CNNs (built-in), Unterthiner/NeurIPS 2021 MLPs (Zenodo 5645138)
4. **`nfn` library is production-ready:** PyPI package (pip install nfn), documented API, proven on NFT paper experiments
5. **DWSNets fails on FC-MLP weights:** [ROUTE_TO_0 failure context] Library assumes CNN weight shapes, runtime error on non-CNN architectures
6. **Generalization gap is standard metric:** Test-minus-train accuracy used across ML research for model quality assessment
7. **Spearman ρ handles nonlinear relationships:** Rank correlation robust to monotonic transformations, appropriate for relative model ranking
8. **Permutation equivariance is necessary:** Neural network weights have inherent permutation symmetry (neuron reordering), equivariant processing preserves this structure

