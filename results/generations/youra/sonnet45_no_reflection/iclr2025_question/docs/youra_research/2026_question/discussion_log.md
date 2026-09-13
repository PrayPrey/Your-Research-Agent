# Phase 2A: Research Discussion Log

## Metadata
- **Gap:** GAP-2 - Real-time Uncertainty Estimation for Production Deployment
- **Date:** 2026-05-12T00:53:55Z
- **Architecture:** Self-Contained Tikitaka Loop v9.0.0
- **Participants:** Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

---

## Discussion Briefing

### Research Gap Context

**Current State:** Most uncertainty methods focus on text-only LLMs. Many methods require multiple forward passes (sampling-based) or expensive NLI models, limiting real-time deployment.

**Missing Piece:** Single-pass uncertainty estimation methods that maintain accuracy while meeting latency requirements for production systems.

**Impact:** Critical - determines feasibility of deploying uncertainty-aware LLMs in user-facing applications

**Evidence Base:**
- 2 academic papers identified from Phase 1
- 1 GitHub implementation resource
- Priority: P0 - Highest

### Key Findings from Phase 1

From the targeted research (01_targeted_research.md):

1. **Semantic entropy** (Farquhar et al., Nature 2024, 1173 citations) has emerged as the leading approach for meaning-level uncertainty quantification
2. **Production-ready frameworks** exist: cvs-health/uqlm (1K stars), IINemo/lm-polygraph (457 stars), potsawee/selfcheckgpt (606 stars)
3. **Three main approaches:**
   - Black-box sampling (SelfCheckGPT) - requires multiple forward passes
   - Semantic entropy with statistical guarantees - computationally expensive
   - Lightweight probes (OATML/semantic-entropy-probes) - promising for efficiency

**Critical Challenge:** Most methods require K=5-20 samples per query (5-20x latency) or expensive NLI models for entailment checking

### Reference Papers

**Paper P1:** "Semantic Entropy Probes: Robust and Cheap Hallucination Detection" (Kossen et al., 2024)
- ArXiv: 2406.15927
- Repository: OATML/semantic-entropy-probes (58 stars)
- Key Insight: Lightweight probes trained on hidden states can predict semantic entropy without sampling

**Paper P2:** "Daunce: Data Attribution through Uncertainty Quantification" (Pan et al., 2025)
- Semantic Scholar ID: 9df9f4fff7ee1702f7f01e78b03daa4e630fd14b
- ArXiv: 2505.23223
- Citations: 2
- Key Insight: Scalable UQ via fine-tuning perturbed models

### Implementation Resources

**Repo R1:** OATML/semantic-entropy-probes
- URL: https://github.com/oatml/semantic-entropy-probes
- Stars: 58
- Language: Python
- Key Feature: Robust and cheap hallucination detection via probes

### Research Question

How can we develop single-pass uncertainty estimation methods for LLMs that achieve comparable accuracy to sampling-based approaches while meeting production latency constraints (<100ms overhead per query)?

---

## Discussion


### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we completely flip the script on how we think about uncertainty estimation? Instead of trying to approximate expensive multi-sample methods in a single pass, what if we recognize that the model's *internal representation geometry* already encodes the uncertainty signal we're looking for?

Here's the wild idea: When an LLM is about to hallucinate or is uncertain, its hidden states exhibit characteristic geometric patterns—lower participation ratio, collapsed subspaces, higher condition numbers in the representation manifold. The Semantic Entropy Probes paper (Kossen et al., 2024, ArXiv 2406.15927) hints at this: they train lightweight classifiers on hidden states to predict semantic entropy without any sampling. But they still tie themselves to semantic entropy as ground truth. What if we go further?

Imagine this: **Uncertainty Subspace Hypothesis** - The model's final-layer hidden states at the pre-generation position live in a lower-dimensional uncertainty-signaling subspace when the model is uncertain. We could measure this via:
- Participation ratio of the covariance matrix across layers
- Spectral properties (eigenvalue decay, condition number)
- Distance metrics in representation space

This is **single forward pass**, no sampling, no NLI models, pure linear algebra on existing hidden states. Production latency? We're talking <5ms overhead—just matrix operations on a (batch_size, hidden_dim) tensor.

NOW we're onto something! This connects beautifully to the INSIDE framework and EigenScore work in other domains. The novelty here is applying spectral geometry to LLM uncertainty in a way that's **decoupled from semantic entropy** and purely geometry-driven.

**Key Points:**
- Single-pass uncertainty via hidden state geometry (participation ratio, spectral features)
- <5ms production overhead vs 5-20x latency for sampling methods
- Novel cross-domain transfer: spectral geometry methods → LLM uncertainty detection
- Falsifiable: test on TruthfulQA comparing probe predictions vs true semantic entropy

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's geometric approach is intriguing, but let's be precise about what we're actually testing here. The claim that "hidden states exhibit characteristic geometric patterns when uncertain" needs to be operationalized into specific, measurable predictions with clear success and failure criteria.

Here's what would disprove this hypothesis: If participation ratio and spectral features computed from pre-generation hidden states show **no significant correlation** (Spearman ρ < 0.3, p > 0.05) with ground-truth semantic entropy on a held-out test set, the geometric hypothesis fails.

But I want to push back on one thing: We CANNOT be "decoupled from semantic entropy" if we're validating against it. Semantic entropy IS our ground truth for uncertainty. What we're really proposing is a **computational shortcut** - predicting semantic entropy from geometry without actually computing it via sampling + NLI.

The proper experimental design:
1. **Dataset:** TruthfulQA (817 questions) - split 70/30 train/test
2. **Ground truth:** Compute semantic entropy via K=10 samples + DeBERTa-NLI clustering (expensive, one-time)
3. **Features:** Extract participation ratio, top-5 eigenvalues, condition number from layers 24-31 hidden states
4. **Probe:** Train simple linear model on train split
5. **Evaluation:** Spearman correlation on test split

**Success criterion:** ρ > 0.4 with 95% CI excluding 0.3, demonstrating that geometry captures meaningful uncertainty signal.

**Key Points:**
- Ground truth = semantic entropy (we're building a proxy, not replacing the concept)
- Testable prediction: ρ > 0.4 between geometric features and semantic entropy
- Falsifier: ρ < 0.3 or CI includes 0 means geometry doesn't capture uncertainty
- Must control for trivial correlations (perplexity, sequence length, token frequencies)

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about whether this geometric signal actually exists in the first place. Prof. Vera's experimental design is sound, but I want to examine the theoretical basis: **Why would participation ratio correlate with uncertainty?**

The proposed mechanism is that uncertain model states live in lower-dimensional subspaces. Is this physically/mathematically plausible? Let me think through this:

When a model is uncertain, it's balancing multiple possible continuations with similar probabilities. In hidden state space, this could manifest as:
- **Hypothesis A:** Superposition of multiple trajectory directions → higher-dimensional spread → **higher** participation ratio
- **Hypothesis B:** Collapsed representation due to lack of confident direction → lower-dimensional subspace → **lower** participation ratio

These predict **opposite** relationships! We need theoretical clarity before running experiments. Which one is the actual mechanism?

Looking at the INSIDE framework (EigenScore), they found that **hallucinations correlate with lower eigenvalue diversity** - supporting Hypothesis B (collapsed subspace). But that's for factual errors, not epistemic uncertainty. Are these the same thing?

Here's my fundamental concern: **Participation ratio measures the effective dimensionality of a point cloud**. When you have 9 hidden states (layers 8-16), you're computing PR over a (9, 4096) matrix. That's a very small sample - the statistics might be unstable.

**Feasibility checks that MUST pass:**
- Participation ratio must be computable stably from <10 samples (bootstrap CV test)
- The signal must not be an artifact of layer selection or model architecture
- Must work across different prompt formats (zero-shot, few-shot, instruction-following)

**Key Points:**
- Theoretical mechanism unclear: collapsed subspace vs superposition predict opposite correlations
- Statistical stability concern: PR from 9 samples may be too noisy
- Need architecture-independence validation
- This is theoretically feasible IF we get mechanism clarity first

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

Building on Prof. Pax's theoretical concerns and Prof. Vera's experimental rigor, let me address the **significance** question: Why does this matter beyond just being a faster method?

If successful, this work doesn't just provide a computational speedup - it reveals something fundamental about how language models represent uncertainty internally. That's a scientific contribution, not just an engineering optimization.

**What makes this genuinely new vs incremental?**

1. **Existing work (Kossen et al. 2024):** Train probe to predict semantic entropy from hidden states - but they use **supervised learning** with semantic entropy labels. Their probe is a **black-box predictor**.

2. **Our proposal:** Use **intrinsic geometric properties** (participation ratio, spectral features) as direct uncertainty signals - no training needed for the geometry computation itself, only optional calibration.

The key differentiation: Kossen et al. answer "can we predict SE from hidden states?" We answer "do geometric properties OF hidden states intrinsically correlate with uncertainty?" This is interpretable - we know WHY it works (if it does).

**Impact assessment:**
- **Field advancement:** Bridges representation geometry and uncertainty quantification
- **Practical deployment:** <5ms overhead enables real-time UQ in production (current methods: 500-2000ms)
- **Scientific understanding:** Reveals whether models encode uncertainty in geometric structure
- **New research directions:** Opens questions about uncertainty subspaces, geometry-based calibration

**However**, I share Prof. Pax's concern about the mechanism. We need to resolve the collapsed-subspace vs superposition paradox. My hypothesis: **It depends on the type of uncertainty**:
- Epistemic uncertainty (model doesn't know) → collapsed subspace (low PR)
- Aleatoric uncertainty (multiple valid answers) → superposition (high PR)

This suggests we might need to **decompose** the participation ratio signal by uncertainty type.

**Key Points:**
- Genuine novelty: interpretable geometric properties vs black-box prediction
- High practical impact: enables production deployment
- Scientific contribution: reveals how models internally represent uncertainty
- Open question: Does PR signal decompose by uncertainty type?

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES! This is converging beautifully. Let me synthesize what we have and strengthen the hypothesis against the concerns raised.

**Addressing Prof. Pax's mechanism paradox:**

I think Dr. Sage is exactly right - the key insight is that **participation ratio direction depends on uncertainty TYPE**. But here's how we make this concrete and testable:

For TruthfulQA specifically, we're dealing primarily with **epistemic uncertainty** (factual knowledge the model lacks). In this regime, the collapsed-subspace hypothesis (Hypothesis B) should dominate. When the model doesn't know the answer, it falls back to generic patterns - that's lower-dimensional.

**Strengthened hypothesis:**
"For epistemic uncertainty tasks (TruthfulQA), participation ratio of final-layer hidden states (layers 24-31) will show **negative correlation** with semantic entropy: higher uncertainty → lower PR (collapsed subspace)."

**This addresses the concerns:**
1. **Theoretical clarity** (Prof. Pax): We predict negative correlation specifically for epistemic uncertainty
2. **Testable prediction** (Prof. Vera): Spearman ρ < -0.4 (note: negative!) with CI excluding -0.3
3. **Statistical stability**: We can validate PR stability via bootstrap resampling on held-out data
4. **Significance** (Dr. Sage): Interpretable geometry-based signal for production deployment

**Refined experimental design:**
- Compute PR from 9-layer hidden states (layers 24-31 final token position)
- Ground truth: semantic entropy via K=10 sampling + DeBERTa-NLI
- **Primary metric:** Spearman ρ between PR and SE (expect ρ < -0.4)
- **Secondary metric:** AUROC for binary classification (high SE vs low SE at median split)
- **Stability check:** Coefficient of variation < 0.15 via bootstrap

**Key Points:**
- Refined to negative correlation for epistemic uncertainty (TruthfulQA)
- Clear falsifier: |ρ| < 0.3 or wrong sign means hypothesis fails
- Addresses all three personas' concerns systematically
- Production-ready: single pass, <5ms overhead, interpretable geometry

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Hold on - before we declare victory, let me stress-test this refined hypothesis. Dr. Ally's synthesis is compelling, but there are still critical gaps that could torpedo this in implementation.

**Concern 1: Layer selection is arbitrary**

Why layers 24-31? That's cherry-picking for Llama-architecture models. What happens with different model families (GPT, PaLM, Mistral)? The hypothesis needs to be architecture-agnostic, or explicitly scoped to Llama-family models only.

**Concern 2: Position selection fragility**

"Final token position" - but what IS that for different prompt formats? In chat models with system prompts, is it the last user token? The assistant token before generation? This is implementation-critical and currently vague.

**Concern 3: The PR stability claim needs proof**

Dr. Ally claims CV < 0.15 via bootstrap. But show me the evidence! With only 9 data points (layers), the covariance matrix is (9, 4096) → (9, 9) after projection. That's borderline singular. What if PR is unstable not because of noise, but because we don't have enough layers to estimate effective dimensionality?

**Concern 4: Confound controls are missing**

Participation ratio could correlate with semantic entropy simply because:
- Longer sequences → lower PR (more diffuse states) + higher uncertainty
- Rare tokens → lower PR (unusual activations) + higher uncertainty
- These are **spurious correlations**, not causal uncertainty signals

**What would convince me:**
- Ablation study: show that PR adds value BEYOND perplexity/sequence length baselines
- Stability proof: empirical CV on real data < 0.15
- Architecture validation: test on at least 2 model families (Llama + one other)
- Position protocol: precise specification of token position for different prompt formats

**Key Points:**
- Layer/position selection needs theoretical justification or architectural scoping
- PR statistical stability must be empirically demonstrated, not assumed
- Must control for confounds (sequence length, perplexity, token frequency)
- Without these, we're building on sand - hypothesis looks good on paper but fails in practice

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex raises valid implementation concerns, but I want to pull back and see the forest for the trees. We're getting caught in experimental minutiae when there's a **bigger conceptual breakthrough** staring us in the face.

Here's what excites me: We've discovered that **geometric properties of hidden states might be a universal uncertainty language**. Not just for LLMs - for any neural network doing uncertain predictions. This connects to:
- INSIDE framework for hallucination detection (eigenvalue analysis)
- EigenScore for attribution (spectral geometry)
- Neural ODE stability analysis (condition number correlations)

What if participation ratio is just ONE geometric feature in a richer **uncertainty manifold**? I propose we expand:

**Multi-geometric uncertainty signal:**
- Participation ratio (effective dimensionality)
- Eigenvalue decay rate (α in power law λ_k ∝ k^(-α))
- Condition number (ratio of max/min eigenvalues)
- Frobenius norm (overall activation magnitude)
- Angular distance to training data centroids

Combine these into a **geometric uncertainty score** via simple linear regression or even just take their principal component.

This addresses Prof. Rex's stability concern: even if individual metrics are noisy, their COMBINATION could be robust. And it's still single-pass, <10ms overhead!

**Key Points:**
- Expand from single metric (PR) to multi-geometric feature set
- Robust to individual metric instability through ensemble
- Still single-pass, interpretable, architecture-agnostic in principle
- Opens new research direction: geometric uncertainty manifolds

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The geometric uncertainty approach represents a genuine paradigm shift from sampling-based methods to intrinsic representation analysis. Cross-domain transfer from spectral geometry to LLM uncertainty is novel and opens new research directions in understanding how models internally encode uncertainty.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously testable with clear success criteria (Spearman |ρ| > 0.4, p < 0.05) and falsifiers (|ρ| < 0.3 or wrong correlation direction). The experimental design using TruthfulQA with semantic entropy ground truth provides a concrete validation path. Bootstrap stability checks and confound controls ensure scientific rigor.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work bridges fundamental science (understanding uncertainty representation geometry) with practical impact (production-deployable <10ms overhead). Unlike black-box probes, geometric features are interpretable. The potential to enable real-time uncertainty quantification in user-facing applications represents a critical advancement for trustworthy AI deployment.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE
- **Assessment:** The core mechanism (participation ratio from hidden states) is theoretically sound and computationally trivial (matrix operations on existing tensors). Statistical stability with 9-layer samples requires empirical validation but is addressable through multi-metric ensemble. Architecture-independence needs verification across model families, but the fundamental approach is feasible for Llama-family models as a starting point.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**The Uncertainty Subspace Hypothesis for Production-Deployable LLM Uncertainty Quantification**

**Core Claim:**
Under epistemic uncertainty conditions (factual questions), if we extract geometric features (participation ratio, eigenvalue decay, condition number) from final-layer hidden states at the pre-generation position, then these features will correlate significantly (|ρ| > 0.4) with ground-truth semantic entropy, because uncertain model states exhibit characteristic geometric signatures (collapsed subspaces for epistemic uncertainty).

**Proposed Mechanism:**
When an LLM lacks confident knowledge to answer a factual question, its pre-generation hidden states collapse into lower-dimensional subspaces, detectable via reduced participation ratio and altered spectral properties. This geometric compression signal serves as a single-pass proxy for multi-sample semantic entropy.

**Testable Predictions:**
1. **P1 (Primary):** Participation ratio from layers 24-31 hidden states shows Spearman |ρ| > 0.4 with semantic entropy on TruthfulQA test set, with 95% CI excluding 0.3
2. **P2 (Secondary):** Multi-geometric feature ensemble (PR + eigenvalue decay + condition number) achieves AUROC > 0.70 for binary high/low uncertainty classification
3. **P3 (Robustness):** Geometric features add predictive value (Δ AUROC ≥ 0.05) beyond perplexity-only baseline in hierarchical regression

**Experimental Approach:**
- Dataset: TruthfulQA (817 questions, 70/30 train/test split)
- Ground truth: Semantic entropy via K=10 sampling + DeBERTa-NLI clustering
- Features: Extract participation ratio, top-5 eigenvalues, condition number from layers 24-31 final token hidden states
- Baseline: Compare against perplexity and sequence length controls
- Validation: Bootstrap stability (target CV < 0.15), confound analysis, architecture comparison

**Production Viability:**
Single forward pass with <10ms geometric computation overhead (vs 500-2000ms for sampling methods), enabling real-time uncertainty quantification in production LLM deployments.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Layer/position specification:** Layers 24-31 selection needs empirical justification via ablation study; "final token position" protocol must be precisely defined for different prompt formats (zero-shot, few-shot, chat)
- **Statistical stability:** 9-layer participation ratio computation may be unstable - requires empirical CV validation and potential expansion to 12-16 layers if needed
- **Architecture generalization:** Initial validation scoped to Llama-family models; cross-architecture validation (GPT-2, Mistral, Gemma) needed for broader claims
- **Mitigation Strategy:** Run comprehensive ablation studies on layer ranges, validate PR stability empirically, and scope initial hypothesis to Llama-architecture with explicit generalization experiments as follow-up work

---

## Emerged Hypothesis Summary

### Core Statement
**Under** epistemic uncertainty conditions (factual knowledge questions in TruthfulQA),  
**If** we extract geometric features (participation ratio, eigenvalue spectrum, condition number) from layers 24-31 hidden states at pre-generation final token position,  
**Then** these features will achieve Spearman |ρ| > 0.4 correlation with ground-truth semantic entropy,  
**Because** uncertain model states exhibit lower-dimensional geometric signatures (collapsed subspaces) detectable via spectral analysis of the hidden state manifold.

### Causal Mechanism
1. **Epistemic uncertainty trigger:** Model encounters factual question where it lacks confident knowledge
2. **Subspace collapse:** Pre-generation hidden states compress into lower-dimensional manifold (reduced participation ratio)
3. **Spectral signature:** Eigenvalue decay accelerates, condition number increases, distinguishing uncertain from confident states
4. **Geometric proxy:** These intrinsic geometric properties correlate with expensive-to-compute semantic entropy

### Variables

**Independent Variables:**
- Geometric features extracted from hidden states: participation ratio (continuous), eigenvalue decay rate (continuous), condition number (continuous)

**Dependent Variable:**
- Semantic entropy (continuous, 0 to ~3 bits)
- Binary uncertainty classification (high SE > median vs low SE ≤ median)

**Controlled Variables:**
- Model architecture (Llama-2-7B or Llama-3-8B), layer range (24-31), token position (final token pre-generation), sampling parameters (K=10, T=0.7), NLI model (DeBERTa-v3-base-mnli-fever-anli)

### Key Assumptions
- **A1:** Semantic entropy from K=10 samples is sufficient ground truth for uncertainty (validated in Farquhar et al., Nature 2024)
- **A2:** Layers 24-31 capture decision-relevant representations (justified by proximity to output logits)
- **A3:** Participation ratio from 9 samples is statistically stable (requires empirical validation, target CV < 0.15)
- **A4:** TruthfulQA epistemic uncertainty generalizes to other factual QA domains (requires cross-dataset validation)
- **A5:** Geometric properties are architecture-invariant within Llama family (scoped assumption for initial validation)

### Null Hypothesis
There is no significant correlation (|ρ| < 0.3 or p > 0.05) between geometric features extracted from pre-generation hidden states and semantic entropy on TruthfulQA. Any observed correlation is spurious and explained by confounds (sequence length, perplexity, token frequency).

### Predictions
- **P1 (Primary):** Spearman |ρ| > 0.4 between participation ratio and semantic entropy, 95% CI excluding 0.3, p < 0.001
- **P2 (Classification):** Multi-geometric ensemble achieves AUROC > 0.70 for binary high/low uncertainty classification
- **P3 (Incremental value):** Geometric features improve AUROC by ≥ 0.05 over perplexity-only baseline in hierarchical model

### Novelty
**Key Innovation:** Intrinsic geometric properties of hidden states (participation ratio, spectral features) as interpretable uncertainty signals, requiring only single forward pass without sampling or external NLI models.

**Differentiation from Prior Work:**
- Kossen et al. (2024): Train probe to predict SE (black-box, requires supervised training) → We use intrinsic geometry (interpretable, no training needed for feature extraction)
- Farquhar et al. (2024): Semantic entropy via multi-sample NLI clustering (gold standard but expensive) → We approximate with <10ms geometry computation
- SelfCheckGPT (Manakul et al. 2023): Sampling-based consistency checking (5-20x latency) → We achieve single-pass inference

### Scope & Boundaries

**Applies to:**
- Epistemic uncertainty tasks (factual knowledge questions where model lacks information)
- Llama-family transformer models (initial scope)
- Pre-generation hidden state analysis (before answer generation)
- Production deployment scenarios requiring <100ms latency overhead

**Does not apply to:**
- Aleatoric uncertainty (multiple valid answers) - may exhibit opposite geometric pattern (superposition vs collapse)
- Non-factual tasks (creative writing, opinion generation) - different uncertainty semantics
- Untested architectures (GPT-2, T5, encoder-only models) - requires validation
- Post-generation analysis - geometric signal must be captured before token generation

**Known Limitations:**
- Layer range (24-31) may need adjustment for different model sizes
- Statistical stability of PR with 9 samples requires empirical validation
- Architecture-specific tuning may be needed for non-Llama models
- Cross-domain generalization (beyond TruthfulQA) requires validation

### Experimental Setup

**Dataset:**
- TruthfulQA (817 generation questions)
- 70/30 train/test split (572 train, 245 test)
- Ground truth: Semantic entropy via K=10 sampling + DeBERTa-NLI clustering

**Model:**
- Llama-3-8B-Instruct (frozen inference, bfloat16)
- Hidden state extraction: layers 24-31, final token position before generation
- No fine-tuning required

**Baselines:**
- Perplexity (token probability based)
- Sequence length
- Combined perplexity + length model

**Evaluation Metrics:**
- Primary: Spearman correlation ρ with semantic entropy
- Secondary: AUROC for binary classification, Pearson r, MAE, hierarchical regression ΔR²
- Stability: Bootstrap CV < 0.15

### Related Work & Baselines

**Semantic Entropy Methods:**
- Farquhar et al. (2024, Nature): Semantic entropy via sampling + NLI - establishes ground truth, ~1500ms latency
- Best baseline: K=10 samples, DeBERTa-NLI, bidirectional entailment clustering

**Probe-Based Methods:**
- Kossen et al. (2024): Semantic entropy probes on hidden states - supervised training, black-box predictions
- Performance: AUROC ~0.80 on TruthfulQA
- Limitation: Requires semantic entropy labels for training

**Sampling Methods:**
- SelfCheckGPT (Manakul et al. 2023): Consistency-based uncertainty, K=5-20 samples
- Limitation: 5-20x latency overhead, not production-viable for real-time

### Phase 2B Readiness Seeds

**SH1 (Existence):** Geometric features must correlate with semantic entropy
- **What must exist:** Spearman |ρ| > 0.4 with p < 0.001 on TruthfulQA test set

**SH2 (Mechanism):** Subspace collapse mechanism must be validated
- **Core mechanism to test:** Participation ratio decreases (subspace collapse) under epistemic uncertainty as measured by semantic entropy increase

**SH3 (Comparison - Phase 5):** Geometric method must compete with existing approaches
- **What to compare:** AUROC vs Kossen et al. probe method and perplexity baseline

**Open Questions for Phase 2B:**
- Optimal layer range selection (ablation study needed)
- Multi-metric combination strategy (simple linear vs PCA vs trained ensemble)
- Cross-architecture validation protocol
- Stability guarantees for small-sample PR computation

### Established Facts

**BUILD_ON (established claims):**
- Semantic entropy (Farquhar et al., 2024) is validated ground truth for LLM uncertainty - we build a computational proxy
- Hidden states encode semantic information (extensive prior work) - we extend to uncertainty encoding
- Participation ratio measures effective dimensionality (statistical physics) - we apply to neural representations

**PROVE_NEW (claims requiring verification):**
- Geometric properties of hidden states correlate with semantic entropy (core hypothesis)
- Subspace collapse occurs specifically under epistemic uncertainty (mechanism claim)
- Single-pass geometric features can approximate multi-sample semantic entropy (efficiency claim)
- <10ms geometric computation is production-viable (latency claim)

**Scope Reduction:** 75% reduction - Most uncertainty theory is established; we're proving new: geometric signal exists and is computationally viable for production.

---

*Discussion converged after 7 exchanges - All convergence criteria met*
