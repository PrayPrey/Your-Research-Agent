# Phase 2A Research Discussion Log

**Generated:** 2026-03-28
**Architecture:** Self-Contained Tikitaka Loop v9.0.0
**Gap ID:** gap1
**Gap Title:** Single-Pass SE Proxy Without Multi-Sample Generation

---

## Briefing Context

### Research Gap Summary

**Current State:** Semantic entropy (SE) is the state-of-the-art for hallucination detection (AUROC 0.76-0.97, 1027 citations), but requires generating N=10-20 responses per query, creating 5-10x computational overhead.

**Missing Piece:** A single-pass method that can predict SE *without* generating multiple responses, while avoiding the pitfalls of previous failed approaches.

**Why Previous Approaches Failed (ROUTE_TO_0 Context):**
- PD-3 Embedding Dispersion: rho ≈ 0 — embeddings don't capture semantic equivalence
- MTLD Lexical Diversity: rho = -0.25 — OPPOSITE direction, inversely related
- Whitened Hidden States: rho = 0.188 — geometry doesn't encode uncertainty
- First-Token Entropy: rho = 0.13 — token-level ≠ semantic-level

**Key Insight:** All failed methods were *heuristic proxies* that didn't learn from actual SE signal. The emerging successful approaches (SEPs, SSD, UQ Heads) all *train on SE ground truth* to learn the mapping.

### Available Papers

| ID | Title | Year | Key Contribution |
|----|-------|------|------------------|
| P1 | Detecting hallucinations using semantic entropy | 2024 | SE as gold standard (1027 citations) |
| P2 | Semantic Entropy Probes | 2024 | Train probe on SE → single-pass |
| P3 | Semantic Self-Distillation | 2026 | Distill SE into student model |
| P4 | Pre-trained UQ Heads | 2025 | Attention-based auxiliary heads |
| P5 | Kernel Language Entropy | 2024 | Soft kernels vs hard clustering |

### Available Implementations

| Repo | Stars | Key Feature |
|------|-------|-------------|
| OATML/semantic-entropy-probes | 54 | Single-pass SEP implementation |
| cvs-health/uqlm | 1121 | Production UQ library |
| jlko/semantic_uncertainty | 408 | Official SE codebase |

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this problem entirely backwards? The failed approaches tried to find *existing* signals that correlate with SE — embeddings, lexical diversity, hidden states. But these were all hoping that the model *already encodes* uncertainty information in a form we can extract.

The breakthrough insight from the recent literature is fundamentally different: **we need to TEACH the model to encode SE-relevant information**. The Semantic Entropy Probes paper (Kossen et al., 2024) shows that you can train a simple linear probe on hidden states to predict SE — achieving comparable AUROC at 5-10x lower cost. The probe *learns* what features correlate with SE, rather than hoping they exist in some pre-specified form.

But here's where I see an unexplored angle: **What if we go beyond probes to actual architectural integration?** The Pre-trained UQ Heads paper (Shelmanov et al., 2025) trains auxiliary heads using attention maps. This suggests that uncertainty information IS latent in the model, but needs a learned decoder to extract it.

My creative proposal: **Cross-Entropy Distillation with Attention Routing**. Instead of just probing hidden states, what if we:
1. Generate multi-sample SE ground truth during training
2. Train an attention-based routing mechanism that learns to identify which attention heads carry uncertainty signal
3. Distill the SE prediction into this lightweight attention router

This would combine the strengths of SEPs (learned from SE), attention-based UQ heads (using attention patterns), and self-distillation (transferring multi-sample knowledge to single-pass).

**Key Points:**
- Failed approaches didn't learn from SE — they assumed correlations exist
- Successful approaches (SEPs, UQ Heads, SSD) all train on SE ground truth
- Novel direction: attention-based routing + SE distillation hybrid

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an interesting architectural proposal, but let's be precise about what would actually constitute evidence for this hypothesis. The evidence suggests the fundamental problem with previous failed approaches is they confused *correlation with causation* — just because embeddings *could* carry semantic information doesn't mean they carry *uncertainty* information.

What would disprove this "learned SE proxy" hypothesis? If we trained a probe on SE ground truth and it performed no better than random chance, that would suggest SE information simply isn't accessible from single-pass representations. The existing literature (SEPs achieving AUROC comparable to full SE) provides evidence against this null hypothesis.

However, I have concerns about the "attention routing" proposal that need precise experimental design:

1. **Testable Prediction 1:** If attention heads encode uncertainty, then probing attention patterns should outperform probing hidden states. The Pre-trained UQ Heads paper partially tests this, but a direct comparison on the same benchmark is needed.

2. **Testable Prediction 2:** If SE-trained probes generalize, they should transfer across model families (e.g., train on Llama, test on Mistral). The literature doesn't establish this — most evaluations are single-model.

3. **Testable Prediction 3:** The efficiency gain must be real. If the "attention router" requires expensive attention computation, the speedup over full SE may be marginal.

For falsification, I propose: **If the SE-probe correlation drops below rho=0.5 when tested on a different question distribution than training (e.g., train on TriviaQA, test on TruthfulQA), then the learned proxy overfits to surface patterns rather than genuine uncertainty.**

**Key Points:**
- Failed approaches confused correlation (embeddings have info) with causation (embeddings have uncertainty info)
- SEP literature provides positive evidence for learned proxies
- Need cross-distribution generalization test for falsification
- Transfer across model families is untested critical assumption

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what makes this genuinely new versus incremental improvement? Let me position this in the broader research landscape.

The field has evolved through clear phases:
1. **2023:** SE introduced (Kuhn, Gal, Farquhar) — established semantic-level uncertainty
2. **2024:** Extensions (KLE, VL-Uncertainty) — generalized SE to new domains
3. **2024-2026:** Efficiency (SEPs, SSD, UQ Heads) — reduced computational cost

We're now at a critical inflection point. The community has validated that SE *works*, and is actively seeking efficient alternatives. This matters because **production deployment is blocked by SE's computational cost**.

What would make a contribution significant vs. incremental?

**Incremental:** Another probe architecture with marginally better AUROC
**Significant:** A method that (1) achieves SE-comparable performance, (2) works single-pass, (3) transfers across models/domains

The ROUTE_TO_0 failure history actually *strengthens* the significance of getting this right. Seven failed approaches demonstrate this isn't a trivial problem — the naive solutions don't work. Any method that succeeds where seven others failed would be a genuine contribution.

From a state-of-the-art positioning perspective:
- SEPs (Kossen et al.) achieve 5-10x speedup but require per-model training
- SSD (Phillips et al.) shows promise but is very recent (2026)
- UQ Heads (Shelmanov et al.) use attention but need validation on more benchmarks

The gap I see: **No existing work combines transferable representations with attention-based uncertainty extraction.** If we could train once and deploy across models, that would be a paradigm shift from current per-model approaches.

**Key Points:**
- Field is at efficiency-focused inflection point
- Production deployment is the key unlock
- Transferability across models is the underexplored high-impact direction
- 7 failed approaches demonstrate non-triviality

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here about what's technically and theoretically achievable. I'll assess the proposed mechanism against fundamental barriers.

**Mechanism Feasibility Assessment:**

1. **Can probes learn SE from hidden states?**
   - ✅ VERIFIED: SEPs paper demonstrates this empirically
   - Linear probes on final-layer hidden states achieve AUROC close to full SE
   - This is not speculation — it's published evidence

2. **Can attention patterns encode uncertainty?**
   - ✅ PARTIALLY VERIFIED: UQ Heads paper shows attention-derived features predict uncertainty
   - The mechanism is plausible: attention entropy reflects model "confidence" in token relationships
   - However: most evidence is on short-form QA, not long-form generation

3. **Is cross-model transfer theoretically possible?**
   - ⚠️ UNCERTAIN: This is the key assumption that needs scrutiny
   - **Theoretical barrier:** Different models have different attention head specializations. A probe trained on Llama's attention patterns may not transfer to Mistral.
   - **Potential path:** Train on representation similarity (e.g., CKA alignment) rather than raw activations

4. **Can SE be computed efficiently as training signal?**
   - ✅ VERIFIED: The infrastructure exists (jlko/semantic_uncertainty, UQLM)
   - N=20 samples is the sweet spot (avoids saturation)
   - This is a one-time training cost, acceptable

**Fundamental barriers I see:**

The biggest risk is **overfitting to model-specific representations**. If the probe learns "when Llama's head 17 fires with high entropy, SE is high," this won't transfer to Mistral which has different head specializations.

**Proposed mitigation:** Instead of probing raw attention/hidden states, probe **normalized similarity structures** — e.g., the relative entropy across heads, or the agreement pattern between heads. These structural patterns may be more model-agnostic.

**Key Points:**
- SE-from-hidden-states is verified feasible (SEPs)
- Attention-as-uncertainty-signal is partially verified
- Cross-model transfer is the uncertain critical assumption
- Propose probing structural patterns (relative entropy) instead of raw activations

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this emerging hypothesis by synthesizing the discussion so far. Let me build on what's been established and address the concerns raised.

**What we have consensus on:**
1. Learned proxies (trained on SE ground truth) are the right approach (vs. heuristic correlations)
2. SEPs demonstrate this works for hidden states
3. Attention patterns show promise but need more validation
4. Cross-model transfer is the key uncertainty

**Strengthening the hypothesis against Prof. Pax's transfer concern:**

The concern about model-specific representations is valid, but I see evidence that suggests a path forward. The Kernel Language Entropy paper (Nikitin et al., 2024) uses **semantic similarity kernels** rather than raw representations. This is model-agnostic because it operates on the *output* semantic space, not internal representations.

What if we combine:
1. **SEP-style probing** for single-model efficiency (proven to work)
2. **Semantic similarity structure** for cross-model generalization (KLE insight)

Concrete refinement: Train a probe that predicts SE using **pairwise similarity patterns** among a small number of generated samples (e.g., N=3-5 instead of N=20). The similarity structure is computed using a shared embedding model (like SentenceBERT), which is model-agnostic.

**Evidence supporting this refinement:**
- The "Beyond SE" paper (Nguyen et al., 2025) shows intra/inter-cluster similarity matters
- Similarity-based approaches avoid the head-specialization problem Prof. Pax raised
- N=3-5 samples is a 4-6x cost reduction over N=20, making it practical

**Addressing Prof. Vera's falsification criteria:**
- Train/test distribution shift (TriviaQA→TruthfulQA) is a good test
- I propose adding: **train on Model A, test on Model B** as the cross-model transfer test
- Success criterion: rho ≥ 0.5 on held-out distribution AND held-out model

**Key Points:**
- Learned probes on SE ground truth is consensus approach
- Similarity structure (not raw activations) may solve transfer problem
- Propose hybrid: few-sample similarity + learned probe
- Refined falsification: cross-distribution AND cross-model transfer

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — let me stress-test the emerging hypothesis before we proceed.

**Critical Challenge 1: The N=3-5 Proposal May Be Insufficient**

Dr. Ally proposes using only N=3-5 samples to compute similarity structure. But the SE saturation data from our failure history (pivot_h-m2_h-m2-v2) shows that with too few samples, you don't get enough variance in cluster structure. The whole POINT of SE is that it captures when responses cluster into semantically distinct groups.

With N=3-5:
- High probability of all samples being semantically equivalent (especially for easy questions)
- Or all being different (for ambiguous questions)
- You lose the *gradient* of SE values that makes it informative

**What would convince me:** Evidence that N=3-5 preserves the rank-ordering of SE values (Spearman correlation with full N=20 SE should be ≥0.8).

**Critical Challenge 2: Similarity Embeddings Have Their Own Failure Mode**

We're proposing to use SentenceBERT or similar for semantic similarity. But recall that PD-3 (embedding dispersion) FAILED with rho ≈ 0. The failure wasn't that embeddings are bad — it's that **embedding distance doesn't equal semantic uncertainty**.

Two semantically different responses can be close in embedding space (paraphrases of wrong answers). Two semantically similar responses can be far in embedding space (same answer, different phrasing).

**What would convince me:** The similarity structure must use NLI-based equivalence (like the original SE) not just embedding distance. Show that NLI-based similarity with N=5 correlates better with full SE than embedding-based similarity.

**Critical Challenge 3: The "Structural Patterns" Proposal Is Vague**

Prof. Pax suggested probing "structural patterns" like relative entropy across heads. This sounds appealing but needs specificity:
- Which heads? All of them? A learned subset?
- What normalization? Layer-wise? Model-wise?
- How do you handle models with different numbers of heads/layers?

**What would convince me:** A concrete specification of the structural features that is architecture-agnostic (works for 32-head and 64-head models alike).

**Key Points:**
- N=3-5 may lose SE's gradient — need correlation evidence
- Embedding similarity failed before — must use NLI-based equivalence
- "Structural patterns" needs concrete, architecture-agnostic specification
- These are addressable challenges, not fundamental blockers

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Building on Prof. Rex's challenges, I see a creative synthesis emerging. What if we approach this from an entirely different angle?

**The Key Insight:** Prof. Rex correctly notes that N=3-5 may lose SE's gradient, and embedding similarity failed. But here's what I find exciting — the Semantic Self-Distillation paper (Phillips et al., 2026) solves EXACTLY this problem.

SSD doesn't use N=3-5 at inference time. Instead:
1. **Training phase:** Generate full SE labels (N=20) for training data
2. **Distillation:** Train a lightweight student model to predict SE from single-pass features
3. **Inference:** Student model predicts SE-like uncertainty in one forward pass

This addresses ALL of Prof. Rex's concerns:
- No N=3-5 approximation at inference — full SE is only needed for training
- No embedding similarity at inference — the student learns a direct mapping
- The "structural patterns" become whatever the student network learns

**Paradigm Shift Proposal: SE-Distilled Probes (SEDPs)**

Combine SEPs (proven to work) with SSD's distillation approach:

1. Generate SE labels using N=20 on training set (one-time cost)
2. Train probe on hidden states to predict SE (like SEPs)
3. **Key addition:** Also train on semantic similarity structure to enable transfer
4. Inference: single forward pass through probe

The novelty is in step 3 — using semantic similarity structure as an **auxiliary training signal** to encourage model-agnostic representations. The probe learns: "when responses have THIS similarity pattern, SE tends to be X."

**Testable Prediction:** SEDPs should transfer better than vanilla SEPs because the similarity structure is model-agnostic while hidden states are model-specific.

**Key Points:**
- SSD shows distillation from full SE (N=20) to single-pass is viable
- No need for N=3-5 approximation — full SE is training signal only
- Propose SEDPs: SEP + similarity structure for transfer
- Auxiliary training on similarity enables cross-model generalization

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's SEDP proposal is more precisely specified now. Let me formalize the testable predictions and experimental design.

**Hypothesis Statement (Under-If-Then-Because format):**

Under the condition of transformer-based LLMs performing question-answering tasks,
If we train a probe to predict semantic entropy (SE) using both hidden state features AND semantic similarity structure as inputs,
Then the probe will achieve (1) single-pass SE prediction with rho ≥ 0.7 vs true SE, AND (2) cross-model transfer with rho ≥ 0.5,
Because the similarity structure provides model-agnostic features that complement model-specific hidden states.

**Experimental Design:**

**Independent Variables:**
- Probe input type: {hidden states only, similarity only, hidden states + similarity}
- Training model: {Llama-3-8B, Mistral-7B}
- Test model: {same as training, different from training}

**Dependent Variables:**
- Primary: Spearman correlation with true SE (rho)
- Secondary: AUROC for hallucination detection
- Tertiary: Inference speedup vs full SE

**Controls:**
- Same training data distribution (TruthfulQA train split)
- Same SE computation parameters (N=20, DeBERTa-v3 for NLI)
- Same probe architecture (2-layer MLP)

**Success Criteria:**
- P1 (Primary): Single-model rho ≥ 0.7
- P2: Cross-model rho ≥ 0.5
- P3: ≥5x speedup over full SE

**Falsification Criteria:**
- If similarity-augmented probe performs no better than hidden-state-only probe for cross-model transfer, the similarity structure hypothesis is falsified
- If cross-model rho < 0.3, the entire transfer approach is falsified

**Key Points:**
- Formalized Under-If-Then-Because hypothesis
- Three IV levels: hidden, similarity, combined
- Cross-model transfer is key test (train A → test B)
- Clear success (rho ≥ 0.7/0.5) and falsification (rho < 0.3) thresholds

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me verify the technical feasibility of Prof. Vera's experimental design.

**Compute Requirements Assessment:**

1. **SE Label Generation (Training):**
   - N=20 samples per question
   - TruthfulQA: ~800 questions
   - Total: 16,000 generations
   - With Llama-3-8B: ~4-6 GPU-hours on A100
   - ✅ FEASIBLE (one-time cost)

2. **NLI-based Similarity Computation:**
   - DeBERTa-v3-large for entailment
   - 20×20 = 400 pairwise comparisons per question
   - 800 × 400 = 320,000 NLI calls
   - ~2-3 GPU-hours on A100
   - ✅ FEASIBLE

3. **Probe Training:**
   - 2-layer MLP with ~1M parameters
   - 800 training samples
   - ~10 minutes on any GPU
   - ✅ TRIVIALLY FEASIBLE

4. **Inference Speedup:**
   - Full SE: 20 generations + 400 NLI calls
   - SEDP: 1 generation + 1 probe forward pass
   - Theoretical speedup: 20-40x
   - ✅ SPEEDUP IS REAL

**Technical Barriers Addressed:**

Prof. Rex's concern about architecture-agnostic features: The similarity structure IS architecture-agnostic because it's computed on generated text, not internal representations. Whether the model has 32 or 64 heads doesn't matter — we're looking at output similarity.

The remaining technical question: How do we incorporate similarity structure at inference (when we only have 1 sample)?

**Proposed Solution:** During training, the probe learns to predict SE from hidden states while also learning what hidden state patterns correlate with high/low similarity diversity. At inference, it uses only hidden states but has learned the correlation with similarity patterns.

This is exactly what SSD does — distill multi-sample knowledge into single-sample predictor.

**Key Points:**
- All compute requirements are feasible (< 10 GPU-hours total)
- 20-40x inference speedup is achievable
- Similarity structure is computed on outputs → architecture-agnostic
- Inference uses only hidden states; similarity is auxiliary training signal

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

This discussion has converged on a clear hypothesis. Let me evaluate its scientific contribution.

**Contribution Assessment:**

What's genuinely new:
1. **Combining SEPs with similarity-augmented training** — SEPs use hidden states alone; we add similarity structure
2. **Explicit focus on cross-model transfer** — existing work evaluates single-model only
3. **Systematic comparison** of hidden state vs similarity vs combined approaches

What's incremental:
1. The probe architecture (standard MLP) — but this is appropriate for a proof-of-concept
2. The benchmark (TruthfulQA) — but it's the standard for hallucination

**Impact Evaluation:**

This matters because:
1. **Production deployment unlock:** 20-40x speedup enables real-time uncertainty estimation
2. **Cross-model transfer reduces cost:** Train once, deploy across model family
3. **Addresses 7 failed approaches:** First principled explanation of WHY they failed (no learning from SE) and HOW to succeed (distillation + similarity)

**State-of-the-Art Positioning:**

| Approach | Single-Pass | Cross-Model | SE Correlation |
|----------|-------------|-------------|----------------|
| Full SE | ❌ | ✅ (by definition) | 1.0 |
| SEPs (Kossen) | ✅ | ❌ (untested) | ~0.8 |
| SSD (Phillips) | ✅ | ❌ (untested) | ~0.75 |
| **SEDPs (Proposed)** | ✅ | 🎯 (key test) | Target: ≥0.7 |

The key differentiator is the explicit cross-model transfer focus. If we achieve rho ≥ 0.5 on train-A → test-B, that's a genuine advance.

**Key Points:**
- Combination of SEPs + similarity is novel
- Cross-model transfer is the key differentiator
- 20-40x speedup enables production deployment
- Clear positioning vs SEPs and SSD

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've reached convergence. Let me synthesize the final hypothesis.

**FINAL HYPOTHESIS: SE-Distilled Probes with Similarity Augmentation (SEDPs)**

**Core Claim (Under-If-Then-Because):**

Under the condition of transformer-based LLMs on QA tasks,
If we train a probe to predict semantic entropy using hidden states with similarity structure as auxiliary training signal,
Then the probe achieves SE-comparable uncertainty estimation in single-pass AND transfers across models,
Because similarity structure provides model-agnostic regularization that prevents overfitting to model-specific representations.

**Mechanism:**
1. Generate SE labels (N=20) on training data using standard SE computation
2. Compute pairwise semantic similarity (NLI-based) for each question's response set
3. Train probe on hidden states to predict SE, with similarity structure as auxiliary input
4. At inference: probe uses only hidden states (no additional generation needed)
5. The similarity-augmented training encourages learning generalizable patterns

**Testable Predictions:**

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Single-model SE correlation | rho ≥ 0.7 | rho < 0.5 |
| P2 | Cross-model transfer | rho ≥ 0.5 | rho < 0.3 |
| P3 | Inference speedup | ≥10x vs full SE | <5x speedup |

**Novelty:**
- First explicit focus on cross-model transfer for SE proxies
- Similarity structure as auxiliary training signal (not inference input)
- Principled explanation for why 7 previous approaches failed

**Key Points:**
- Hypothesis is fully specified with mechanism
- Three testable predictions with clear thresholds
- Novelty is cross-model transfer + similarity augmentation
- All feasibility concerns addressed

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is well-formed. I have remaining concerns but they're addressable, not fundamental blockers.

**Remaining Concern 1: Similarity Computation at Training**

Using NLI-based similarity (DeBERTa) for training data is fine. But I want clarity: we're NOT using similarity at inference, correct? The probe only takes hidden states at inference.

**Addressed:** Yes, confirmed. Similarity is auxiliary training signal only. This is the SSD paradigm.

**Remaining Concern 2: What If Transfer Doesn't Work?**

If cross-model transfer fails (rho < 0.3), what's the fallback?

**Mitigation:** Per-model probes still work (SEPs prove this). The fallback is: train separate probes per model family. Still valuable due to 20-40x speedup.

**Remaining Concern 3: Benchmark Diversity**

TruthfulQA is a good start but narrow. Need to test on:
- Long-form generation (not just QA)
- Domain-specific questions (medical, legal)

**Mitigation:** This is future work. Initial proof-of-concept on TruthfulQA is appropriate. If it fails there, it won't work elsewhere. If it succeeds, extend to other benchmarks.

**My Assessment:**

The hypothesis is ready for Phase 2B. The core mechanism is sound (learned SE proxy), the novelty is clear (cross-model transfer), and the experimental design is feasible.

**Key Points:**
- Similarity is training-only, not inference — confirmed
- Fallback if transfer fails: per-model probes (still valuable)
- TruthfulQA is appropriate initial benchmark
- Hypothesis is ready for Phase 2B decomposition

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The combination of SEP-style probing with similarity-augmented training for cross-model transfer is genuinely novel. No existing work explicitly targets transfer, and the similarity auxiliary signal is a creative solution to the model-specificity problem identified by Prof. Pax.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear, quantitative success criteria (rho ≥ 0.7 single-model, rho ≥ 0.5 cross-model) and explicit falsification thresholds (rho < 0.3). The experimental design with three IV levels (hidden, similarity, combined) enables clean causal inference about the contribution of each component.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work addresses a real production barrier (SE's 5-10x compute cost) with a clear path to deployment. Cross-model transfer would be a paradigm shift from current per-model approaches. The 7 failed prior approaches demonstrate non-triviality.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are technically feasible with modest compute (<10 GPU-hours). The mechanism is scientifically sound: probes can learn from hidden states (SEPs prove this), and similarity structure is model-agnostic by construction. No fundamental barriers remain.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on **SE-Distilled Probes with Similarity Augmentation (SEDPs)** as the hypothesis to test. The core insight is that previous failed approaches (embeddings, lexical metrics, token entropy) tried to find pre-existing correlations with SE, when the correct approach is to *learn* the mapping from model representations to SE.

The SEDP mechanism trains a probe on hidden states to predict SE, using semantic similarity structure as an auxiliary training signal. At inference, only hidden states are needed, achieving 20-40x speedup. The similarity augmentation is hypothesized to improve cross-model transfer by encouraging model-agnostic learned features.

The key testable prediction is cross-model transfer: if we train on Llama-3-8B and test on Mistral-7B, can we achieve rho ≥ 0.5 with true SE? This is the differentiating contribution versus existing single-model approaches like SEPs.

Experimental setup will use TruthfulQA with DeBERTa-v3 for NLI-based similarity and SE computation. Three probe variants (hidden-only, similarity-only, combined) will isolate the contribution of each component.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Cross-model transfer is unproven — this is the high-risk, high-reward component
- **Concern 2:** Benchmark diversity is limited (TruthfulQA only for initial test)
- **Concern 3:** The "similarity as auxiliary signal" mechanism needs empirical validation
- **Mitigation Strategy:** If transfer fails, fallback to per-model probes (still achieves speedup). Extend to diverse benchmarks in follow-up work. Ablation study comparing hidden-only vs combined will validate similarity contribution.

---

## Emerged Hypothesis Summary

### Core Statement

**Hypothesis ID:** H-SEDP-v1

**Under-If-Then-Because:**
Under the condition of transformer-based LLMs performing question-answering tasks, if we train a probe to predict semantic entropy (SE) using hidden state features with semantic similarity structure as an auxiliary training signal, then the probe will achieve (1) single-pass SE prediction with Spearman rho ≥ 0.7 versus true SE, AND (2) cross-model transfer with rho ≥ 0.5, because the similarity structure provides model-agnostic regularization that prevents overfitting to model-specific hidden state patterns.

### Causal Mechanism

1. **SE Label Generation:** Generate N=20 responses per question, compute true SE using NLI-based clustering
2. **Similarity Structure Extraction:** Compute pairwise semantic similarity (NLI entailment) for response sets
3. **Probe Training:** Train MLP probe on hidden states with similarity structure as auxiliary input
4. **Knowledge Distillation:** Probe learns to predict SE from single-pass hidden states
5. **Transfer via Similarity:** Similarity-augmented training encourages model-agnostic feature learning

### Variables

**Independent:**
- Probe input configuration: {hidden states only, similarity only, hidden + similarity}
- Training model: {Llama-3-8B, Mistral-7B}
- Test model: {same as training, different from training}

**Dependent (Primary):**
- Spearman correlation (rho) with true SE

**Dependent (Secondary):**
- AUROC for hallucination detection
- Inference latency (speedup factor)

**Controlled:**
- Training data: TruthfulQA train split
- SE computation: N=20 samples, DeBERTa-v3-large for NLI
- Probe architecture: 2-layer MLP with 256 hidden units

### Key Assumptions

- A1: Hidden states contain sufficient information to predict SE (supported by SEPs)
- A2: Semantic similarity structure is model-agnostic (true by construction — computed on text)
- A3: Similarity-augmented training improves generalization (to be tested)
- A4: TruthfulQA is representative of broader QA uncertainty patterns
- A5: DeBERTa-v3 NLI adequately captures semantic equivalence

### Null Hypothesis

H0: There is no significant difference in cross-model transfer performance between similarity-augmented probes and hidden-state-only probes (i.e., similarity augmentation provides no transfer benefit).

### Predictions

| ID | Primary | Statement | Test Method | Success | Falsification |
|----|---------|-----------|-------------|---------|---------------|
| P1 | Yes | SEDP achieves rho ≥ 0.7 with true SE on same-model test | Train on Llama, test on Llama | rho ≥ 0.7 | rho < 0.5 |
| P2 | No | SEDP achieves rho ≥ 0.5 on cross-model test | Train on Llama, test on Mistral | rho ≥ 0.5 | rho < 0.3 |
| P3 | No | SEDP provides ≥10x inference speedup | Time full SE vs SEDP inference | ≥10x | <5x |

### Novelty

**Key Innovation:** First SE proxy explicitly designed for cross-model transfer via similarity-augmented training.

**Differentiation from Prior Work:**
- vs SEPs: Adds similarity auxiliary signal; targets cross-model transfer
- vs SSD: Uses probe architecture instead of full student model; more efficient
- vs UQ Heads: Uses NLI-based similarity instead of attention patterns; architecture-agnostic

### Scope & Boundaries

**Applies to:**
- Transformer-based LLMs (decoder-only architecture)
- Question-answering tasks with factual ground truth
- English language generation

**Does not apply to:**
- Non-transformer architectures
- Open-ended creative generation (no notion of "correct" answer)
- Non-English languages (NLI model limitation)

### Experimental Setup

**Dataset:** TruthfulQA (817 questions, train/test split)
**Models:** Llama-3-8B-Instruct, Mistral-7B-Instruct-v0.2
**SE Computation:** N=20 samples, temperature=0.7, DeBERTa-v3-large for NLI
**Probe:** 2-layer MLP (hidden_dim=256), trained with MSE loss on SE prediction
**Evaluation:** Spearman correlation, AUROC, inference speedup

### Related Work & Baselines

**Baselines:**
- Full SE (N=20): Upper bound, rho=1.0 by definition
- First-Token Entropy: Lower bound, rho~0.13 (from failure history)
- SEPs (hidden-only): Comparison for transfer benefit

**Key Related Work:**
- Semantic Entropy (Farquhar et al., 2024): Foundation
- Semantic Entropy Probes (Kossen et al., 2024): Probe approach
- Semantic Self-Distillation (Phillips et al., 2026): Distillation paradigm

### Phase 2B Readiness Seeds

**SH1 (Existence):** Probe trained on SE + similarity produces meaningful predictions (rho > 0)
**SH2 (Mechanism):** Similarity augmentation improves cross-model transfer vs hidden-only
**SH3 (Comparison):** SEDP outperforms baseline SEPs on cross-model transfer

### Established Facts

| Claim | Status | Evidence |
|-------|--------|----------|
| SE is gold standard for hallucination detection | BUILD_ON | Farquhar et al. 2024, 1027 citations |
| SEPs achieve single-pass SE estimation | BUILD_ON | Kossen et al. 2024, OATML implementation |
| Embedding dispersion fails as SE proxy | BUILD_ON | ROUTE_TO_0 failure: rho ≈ 0 |
| Cross-model transfer of SE probes | PROVE_NEW | No existing evidence; key contribution |
| Similarity augmentation improves transfer | PROVE_NEW | Hypothesis to test |
