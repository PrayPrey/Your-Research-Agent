# Phase 2A Discussion Log

## Briefing

**Gap ID:** gap_1
**Gap Title:** Unified Benchmark for LLM Data Attribution Comparison
**Relevance:** PRIMARY - Directly blocks answering research question

**Current State:**
DATE-LM (2025) is the first unified benchmark but limited to 3 tasks. Existing evaluations use inconsistent metrics (LDS, LOO, counterfactual). No single method dominates across all settings.

**Missing Piece:**
Comprehensive benchmark spanning model scales (7B to 70B), multiple FM families, and standardized efficiency/accuracy tradeoff metrics.

**Related Papers:**
- P1: DATE-LM (Jiao et al., 2025) - First unified LLM benchmark
- P2: Intriguing Properties of Data Attribution on Diffusion Models (Zheng et al., 2023)
- P3: TRAK (MadryLab, 2023) - LDS benchmark included

**Available Implementations:**
- MadryLab/trak (243 stars) - CUDA-optimized TRAK
- pomonam/kronfluence (198 stars) - K-FAC for LLMs

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The benchmarking gap presents a fascinating opportunity! What if we flip the problem entirely? Instead of asking "which attribution method is most accurate," we ask "under what conditions does each method's inductive bias become advantageous?"

DATE-LM shows no single method dominates — but this isn't a failure, it's a clue! Each method embeds assumptions about what makes training data "influential." TRAK assumes gradient alignment matters; TracIn assumes checkpoint proximity matters; influence functions assume curvature matters.

Here's my wild idea: **Attribution Method Fingerprinting**. We characterize each method by the *type* of influence it detects best, not by raw accuracy. Think of it like spectroscopy — different wavelengths reveal different molecular properties. Similarly, different attribution methods might reveal different "influence modes" in training data.

Cross-domain connection: In causal inference, different estimators excel under different confounding structures. Maybe attribution methods similarly excel under different data-model interaction patterns!

**Key Points:**
- Reframe from "best method" to "method-task fit characterization"
- Each method's inductive bias may be a feature, not a bug
- Could create taxonomy of "influence modes" matched to method strengths

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's fingerprinting concept is creative, but let me stress-test it. The fundamental challenge: how do we validate that different methods detect *genuinely different* influence modes versus simply having different noise patterns?

DATE-LM's 3 tasks aren't just limited in number — they may not span the space of "influence modes" adequately. We need ground-truth labels for influence. The gold standard is leave-one-out retraining, but it's computationally prohibitive at 70B scale.

Here's what would convince me this is testable: Define exactly 3-4 influence modes with operational definitions. For each mode, design a *diagnostic task* where we can construct ground truth cheaply. For example:
1. **Memorization influence**: Duplicated training samples should rank highest
2. **Feature influence**: Samples sharing salient features with test point should rank high
3. **Spurious correlation influence**: Samples with spurious-but-predictive features

If method A consistently detects memorization but misses feature influence, while method B shows the opposite pattern, we have falsifiable evidence for distinct "influence modes."

**Key Points:**
- Need operational definitions of influence modes, not just intuitions
- Each mode requires a diagnostic task with cheap ground truth
- Prediction: Methods will show dissociable patterns across diagnostic tasks

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask: would "Attribution Method Fingerprinting" genuinely advance the field, or is it repackaging existing comparative studies?

Current comparative work (DATE-LM, TRAK paper) already shows method-task dependencies. The incrementalism trap awaits if we simply add more tasks. What would constitute a *contribution*?

I see potential significance if we achieve **predictive power**: Given a new task/model, can we predict which attribution method will perform best *without running all methods*? This transforms from descriptive taxonomy to actionable tool.

The practical impact: Practitioners currently must run multiple attribution methods and cross-validate. If fingerprinting enables principled method selection, we save significant compute. At 70B scale with LoRIF's 20x speedup, this still means massive resource savings.

For the community, the contribution is a **meta-benchmark** — not "which method wins" but "how to select methods." This opens new research direction: designing attribution methods for specific influence modes.

**Key Points:**
- Must go beyond descriptive taxonomy to predictive framework
- Contribution: Method selection without exhaustive evaluation
- Opens new research direction: mode-specific attribution design

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this in what's technically achievable. The diagnostic task approach Prof. Vera outlined is sound in principle, but I need to verify mechanisms.

**Memorization detection ground truth**: Feasible. We can inject controlled duplicates into training data and verify attribution correctly identifies them. Basu et al. (2020) already showed this for influence functions.

**Feature influence ground truth**: Harder. We'd need datasets where "salient features" are explicitly annotated. ImageNet with attribute labels exists, but for LLMs? This requires either:
- Synthetic datasets with controlled feature insertion (risks ecological validity)
- Natural datasets with post-hoc feature annotation (expensive, subjective)

**Computational feasibility at scale**: DATE-LM evaluated at 7B. LoRIF and GraSS enable 70B. But running *multiple* methods across *multiple* diagnostic tasks at 70B is still expensive. We need a staged approach: develop fingerprinting at 7B, validate scaling laws, then spot-check at 70B.

The mechanism is theoretically valid. The measurement approach needs careful design to avoid confounds between "method detects this influence type" vs "method is generally more/less accurate."

**Key Points:**
- Memorization diagnostic: Feasible with controlled injection
- Feature diagnostic: Requires careful dataset design (synthetic vs natural trade-off)
- Scale strategy: Develop at 7B, validate scaling, spot-check at 70B

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on the discussion, I see a converging hypothesis: **Attribution methods exhibit systematic performance signatures across influence modes, enabling predictive method selection.**

Let me strengthen this against Prof. Vera's testability concern. The key is to operationalize "influence mode" in terms of dataset-constructible properties:

1. **Mode-M (Memorization)**: Exact/near-duplicate training samples
   - Ground truth: Injection-based (we control duplicates)
   - Measurement: Rank correlation between duplicate frequency and attribution score

2. **Mode-F (Feature Transfer)**: Samples sharing task-relevant features
   - Ground truth: Use datasets with controlled feature overlap (e.g., SQuAD question-passage pairs with shared entities)
   - Measurement: Attribution scores correlate with feature overlap metrics

3. **Mode-S (Spurious Association)**: Samples with spurious correlations
   - Ground truth: Use known spurious correlation datasets (e.g., Waterbirds, CivilComments)
   - Measurement: Attribution identifies spurious vs causal features

Prof. Pax's scaling strategy is key: We don't need 70B for hypothesis validation. If the fingerprinting pattern holds at 7B across multiple model families (LLaMA, Mistral, Qwen), scaling behavior can be spot-checked.

**Key Points:**
- Three operationalized influence modes with constructible ground truth
- Existing datasets can serve as diagnostics (no new benchmark creation needed)
- 7B-scale validation is sufficient with multi-family coverage

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me challenge the emerging consensus. Several assumptions need scrutiny:

**Assumption 1: Influence modes are separable.** What if memorization, feature transfer, and spurious association are entangled in real data? A training sample could be influential via multiple modes simultaneously. The fingerprinting framework assumes clean separation — show me evidence this holds.

**Assumption 2: Method signatures are stable across model families.** Does TRAK's fingerprint on LLaMA-7B match its fingerprint on Mistral-7B? If signatures are model-specific, the predictive framework collapses to "run everything on each new model."

**Assumption 3: Existing datasets adequately span the mode space.** SQuAD for Mode-F, Waterbirds for Mode-S — these are classification/QA oriented. Do these modes transfer to generative tasks (completion, instruction-following)?

What would convince me:
1. Evidence that methods show *dissociable* patterns (high on Mode-M, low on Mode-F) rather than just overall accuracy differences
2. Cross-model stability of signatures (same method, same ranking across modes, different models)
3. Generative task validation, not just classification

**Key Points:**
- Mode entanglement threatens clean taxonomy
- Cross-model signature stability is untested assumption
- Must validate on generative tasks, not just discriminative

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex raises valid challenges! Let me propose solutions:

**Mode entanglement:** Rather than fighting it, embrace it! Instead of binary mode labels, compute a *mode profile* — continuous scores across all modes. Method fingerprints become vectors in mode-space, not categorical labels. This is more information-rich and handles entanglement naturally.

**Cross-model stability:** Actually, *variance* in signatures across models could itself be informative! If TRAK's fingerprint changes dramatically between LLaMA and Mistral, that tells us something about model-method interactions. We could build a *signature stability index* as part of the characterization.

**Generative tasks:** Here's the creative angle — use generation tasks *as* the diagnostic. For instruction-following, the "influential" training examples should be those whose instructions/responses pattern-match the test query. This is a natural Mode-F extension.

New idea: **Contrastive Mode Probing**. Instead of separate diagnostic datasets, use contrastive pairs within the same dataset:
- Test point A (memorization-likely): verbatim training repeat
- Test point B (feature-likely): paraphrase with shared concepts
- Compare attribution rankings between A and B

**Key Points:**
- Mode profiles instead of binary modes (handles entanglement)
- Signature stability index captures model-method interactions
- Contrastive probing within single dataset avoids task transfer issues

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's contrastive mode probing is elegant. It provides a falsifiable experimental design:

**Primary prediction:** For a given attribution method M, the correlation between attribution scores and mode-indicator (memorization vs feature-transfer) will be *consistent* across test points. That is, if M preferentially detects memorization on test point A, it should do so across many A-type points.

**Secondary prediction:** Different methods will show *dissociable* mode preferences. TRAK (gradient projection) may favor Mode-F; TracIn (checkpoint proximity) may favor Mode-M; Influence functions (curvature) may show task-dependent patterns.

**Falsification criteria:**
- If all methods show identical mode profiles, fingerprinting adds nothing
- If method profiles vary randomly across test points, no stable signature exists
- If profiles don't transfer across model families, predictive utility is limited

Experimental design:
1. Select 3 LLM families at 7B scale (LLaMA-2-7B, Mistral-7B, Qwen-7B)
2. Construct contrastive probe sets (1000 pairs each for memorization/feature)
3. Run TRAK, TracIn, Kronfluence on each model-probe combination
4. Compute mode profiles and cross-method dissociation statistics

**Key Points:**
- Contrastive probing yields direct mode-sensitivity measurement
- Falsifiable: identical profiles = no fingerprinting value
- 3-model, 3-method factorial design is tractable

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The experimental design is converging. Let me verify feasibility point by point.

**Contrastive probe construction:**
- Memorization pairs: Use near-duplicate detection (MinHash) on training data. Pick test points with high similarity to training samples (A) vs low similarity (B). Feasible with existing tools.
- Feature pairs: Use semantic similarity (sentence embeddings) without lexical overlap. STS-B style. Also feasible.

**Method implementations:**
- TRAK: MadryLab/trak (production-ready, CUDA optimized)
- TracIn: frederick0329/TracIn (needs adaptation for LLMs)
- Kronfluence: pomonam/kronfluence (designed for LLMs, good fit)

**Compute requirements at 7B:**
- Per model: ~50 GPU-hours for full attribution (estimating from TRAK docs)
- 3 models × 3 methods × 2 probe sets = 18 runs
- Total: ~900 GPU-hours — significant but not prohibitive for a research study

**What's NOT feasible without significant engineering:**
- Real-time method selection (fingerprinting is expensive; value comes from *one-time characterization* per method, then reuse)
- 70B validation (defer to future work; 7B is sufficient for proof-of-concept)

The mechanism is sound. Implementation requires TracIn adaptation but no fundamental barriers.

**Key Points:**
- Contrastive probe construction: feasible with MinHash + semantic similarity
- Implementation: TRAK and Kronfluence ready; TracIn needs LLM adaptation
- Compute: ~900 GPU-hours for full study (reasonable)

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

The hypothesis is maturing well. Let me assess contribution clarity.

**What we're claiming:**
1. Attribution methods have characteristic "fingerprints" — stable mode profiles across test points
2. These fingerprints differ between methods (dissociable)
3. Fingerprints are stable enough across model families to enable transfer

**Why this matters:**
- Practitioners: Select attribution method based on use case (debugging memorization vs understanding feature learning) without running all methods
- Researchers: Design new attribution methods targeting specific influence modes
- Field: Moves beyond "which method wins" to "what does each method measure"

**Positioning vs prior work:**
- DATE-LM: Comparative benchmark → We explain *why* methods differ
- TRAK paper: Single-method characterization → We provide cross-method taxonomy
- Basu 2020 fragility: Shows methods fail differently → We characterize the pattern

**Risk:** If fingerprints don't dissociate or aren't stable, the contribution becomes negative result ("methods don't have characteristic signatures"). Still publishable but lower impact.

**Verdict:** Clear contribution if positive result; informative if negative. Good hypothesis structure.

**Key Points:**
- Clear three-part claim: fingerprints exist, dissociate, transfer
- Practical value: Method selection for specific use cases
- Novel positioning: Taxonomy over ranking

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Synthesizing the discussion, here's the refined hypothesis:

**Hypothesis H-AttributionFingerprint-v1:**

Under the scope of LLM data attribution at 7B parameter scale, if we characterize attribution methods by their mode profiles (sensitivity to memorization vs feature transfer vs spurious association), then methods will exhibit stable, dissociable fingerprints across model families, because different attribution algorithms embed different inductive biases about what makes training data influential.

**Core Mechanism:**
1. Attribution methods compute influence differently (gradient projection, checkpoint proximity, Hessian inversion)
2. These computational differences translate to sensitivity differences across influence modes
3. Mode sensitivity constitutes a stable "fingerprint" characteristic of the method

**Testable Predictions:**
- P1: Contrastive probe analysis will show method-specific mode profiles (e.g., TRAK high on Mode-F, TracIn high on Mode-M)
- P2: Mode profiles will be consistent across test points within a model (profile stability)
- P3: Mode profiles will correlate across model families (cross-model transfer, r > 0.7)

**Null Hypothesis H0:** Attribution methods do not exhibit dissociable mode profiles; all methods show similar sensitivity patterns across influence modes.

**Experimental Approach:**
- 3 LLM families × 3 methods × 2 contrastive probe sets
- ~900 GPU-hours total
- Primary metric: Mode profile dissociation (inter-method variance > intra-method variance)

**Key Points:**
- Hypothesis follows Under-If-Then-Because structure
- Three falsifiable predictions with clear metrics
- Experimental design is specified and feasible

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is well-structured. Final stress test before I'm satisfied:

**Concern 1: Effect size.** Even if fingerprints exist, are differences large enough to matter? If TRAK scores 0.52 on Mode-F and TracIn scores 0.48, that's statistically detectable but practically useless.

**Mitigation:** Define minimum practical significance threshold (e.g., Cohen's d > 0.5 for mode profile differences). If effects are smaller, acknowledge as limitation.

**Concern 2: Confound — model training data overlap.** LLaMA, Mistral, Qwen likely have training data overlap. Cross-model "stability" might reflect shared training data, not method generalization.

**Mitigation:** Include at least one model with known distinct training corpus (e.g., a code-specialized model like CodeLLaMA vs general LLaMA). If fingerprints transfer across domain-specialized models, confound is reduced.

**Concern 3: Attribution method hyperparameters.** TRAK has projection dimension; Kronfluence has damping parameter. Fingerprints might be hyperparameter-dependent, not method-intrinsic.

**Mitigation:** Run sensitivity analysis with 2-3 hyperparameter settings per method. Report fingerprint stability across hyperparameter choices.

These are addressable concerns, not fatal flaws. With mitigations, the hypothesis is ready for Phase 2B.

**Key Points:**
- Effect size threshold needed (Cohen's d > 0.5)
- Include domain-specialized model to address training overlap confound
- Hyperparameter sensitivity analysis for robustness

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The reframe from "best method" to "method fingerprinting" is genuinely novel. Cross-domain connection to spectroscopy/causal inference adds conceptual depth. Mode profiles and contrastive probing are creative methodological contributions.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three clear predictions with falsification criteria. Contrastive probe design enables direct measurement. Statistical thresholds specified (r > 0.7 for transfer, Cohen's d > 0.5 for dissociation). Experimental design is rigorous.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Moves field beyond comparative benchmarking to explanatory taxonomy. Practical value for method selection. Opens new research direction (mode-specific attribution design). Clear positioning against DATE-LM, TRAK, Basu 2020.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All mechanisms are technically valid. Implementations exist (TRAK, Kronfluence). TracIn needs LLM adaptation but no fundamental barriers. ~900 GPU-hours is reasonable. 7B scale is sufficient for hypothesis validation.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on **H-AttributionFingerprint-v1**: Attribution methods exhibit characteristic and stable mode profiles that dissociate across methods and transfer across model families.

The core claim is that different attribution algorithms (gradient projection, checkpoint proximity, Hessian inversion) embed different inductive biases about influence, which manifest as measurable sensitivity differences to memorization, feature transfer, and spurious association modes. This transforms the benchmarking question from "which method is best" to "what does each method measure."

The experimental approach uses contrastive mode probing on 3 LLM families at 7B scale with 3 attribution methods. Primary predictions: (1) methods show dissociable profiles, (2) profiles are stable within models, (3) profiles transfer across models with r > 0.7. The study requires ~900 GPU-hours and leverages existing implementations (TRAK, Kronfluence) with TracIn adaptation.

Practical impact: Enables principled method selection based on use case (debugging memorization vs understanding feature learning). Research impact: Provides explanatory framework for why methods differ, opening new direction for mode-specific attribution design.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Effect size uncertainty: Fingerprint differences may be statistically significant but practically small
- Training data overlap confound: Need domain-specialized model validation
- Hyperparameter sensitivity: Must verify fingerprints are method-intrinsic, not hyperparameter-dependent

**Mitigation Strategy:** Include Cohen's d > 0.5 threshold, add CodeLLaMA as domain-shifted model, run 3-setting hyperparameter sensitivity analysis.

---

## Convergence

**Status:** CONVERGED
**Exchange Count:** 12
**Reason:** All 6 convergence criteria met:
- SPECIFIC: Core claim clearly stated (methods have dissociable mode profiles)
- MECHANISM: Causal chain explained (computational differences → sensitivity differences)
- PREDICTIONS: 3 testable predictions with criteria (P1, P2, P3)
- NOVELTY: Clear differentiation from prior work (taxonomy over ranking)
- FEASIBILITY: Technical approach validated (~900 GPU-hours, existing implementations)
- OBJECTIONS: Major concerns addressed with mitigations
