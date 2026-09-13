# Phase 2A Discussion Log

## Briefing

**Research Gap:** Systematic Benchmark Comparison Missing
**Priority:** CRITICAL | **Relevance:** PRIMARY

**Context:** NFT and DWS architectures for permutation-equivariant weight processing have been evaluated on different tasks. No head-to-head comparison exists on TrojAI/ModelZoo benchmarks for model property prediction (accuracy, robustness, backdoor detection).

**Related Papers (from Phase 1):**
- Neural Functional Transformers (Zhou et al., 2024) - arXiv:2305.13546
- Deep Weight Space (Navon et al., 2023) - arXiv:2301.12780
- Hyper-representations (2022) - arXiv:2110.15288
- Deep Sets (Zaheer et al., 2017) - arXiv:1703.06114

**Recommended H0 from Phase 1:** "Permutation-equivariant processing improves accuracy prediction on ModelZoo vs flattened-weight baseline"

**Feasibility Constraints:**
- Must use existing real datasets and benchmarks
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation required

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we frame this not as "which architecture is better" but as "what inductive biases matter for weight-space learning"? The field has two competing paradigms — NFT's tokenization approach versus DWS's equivariant layers — but nobody has asked: under what conditions does each shine?

Here's my wild idea: permutation equivariance might be *necessary but not sufficient*. Both NFT and DWS respect weight permutation symmetry, yet they achieve this differently. NFT tokenizes weights and uses equivariant attention; DWS builds equivariance directly into layer operations. What if the *type* of property being predicted determines which approach wins? Accuracy prediction might favor different inductive biases than backdoor detection.

Imagine this — we design an experiment on ModelZoo that tests BOTH architectures on MULTIPLE property types: (1) accuracy prediction, (2) robustness estimation, (3) backdoor detection. The hypothesis becomes: "Architecture advantage depends on property type due to differing locality requirements."

**Key Points:**
- Frame as inductive bias study, not architecture horse-race
- Test multiple property types on same benchmark
- Hypothesis: property type × architecture interaction effect

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's interaction hypothesis is testable, but we need sharper operationalization. "Architecture advantage depends on property type" is vague — what exactly would we measure?

Let me propose a falsifiable prediction: If locality matters, then DWS (which processes weights locally before aggregation) should outperform NFT (which uses global attention) on properties requiring fine-grained weight pattern detection, like backdoor triggers. Conversely, NFT should excel on properties requiring global weight statistics, like overall accuracy prediction.

The evidence would need: (1) A 2×3 factorial design: {NFT, DWS} × {accuracy, robustness, backdoor}. (2) Primary metric: prediction error (RMSE for continuous, AUC for binary). (3) Success criterion: significant interaction effect (p < 0.05) with effect size d > 0.3.

What would disprove this? If both architectures perform identically across all property types, or if the interaction goes opposite to our locality prediction, the hypothesis fails.

**Key Points:**
- Factorial design: 2 architectures × 3 property types
- Primary metrics: RMSE (accuracy/robustness), AUC (backdoor)
- Falsification: no interaction effect or wrong direction

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: does this advance the field, or merely confirm what practitioners suspect?

The interaction hypothesis has genuine significance if it provides *actionable guidance*. Currently, researchers choosing between NFT and DWS have no principled basis — they pick based on paper recency or implementation availability. A systematic comparison that reveals which architecture suits which task type would be a real contribution.

However, I worry the hypothesis is too narrow. A horse-race on ModelZoo proves something about ModelZoo, not about weight-space learning generally. What makes this genuinely new vs. incremental? We need a mechanistic claim: *why* would locality matter? NFT's attention can theoretically learn local patterns too — it's not architecturally constrained to global processing.

The significance increases if we ground the comparison in a causal mechanism: "Equivariant layers with explicit locality inductive bias require less data to learn fine-grained patterns, because the bias encodes spatial weight structure that attention must learn from scratch."

**Key Points:**
- Significance requires actionable guidance, not just benchmark numbers
- Need mechanistic grounding: why would locality matter?
- Hypothesis: explicit locality bias reduces sample complexity for fine-grained patterns

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The mechanism Dr. Sage proposes — locality inductive bias affecting sample complexity — is theoretically sound. Equivariant architectures can encode structural priors that transformers must learn. This is established in CNN vs ViT literature.

But here's what worries me: ModelZoo datasets are small. The entire publicly available ModelZoo for property prediction might have ~1000 models at best. With a 2×3 design, we're looking at ~150 models per cell if we split evenly. Is that enough statistical power to detect interaction effects?

The measurement approach is scientifically valid — RMSE and AUC are standard. The intervention (comparing architectures) is straightforward. But the fundamental barrier is dataset size. Can we actually run this experiment with existing benchmarks?

Actually, wait — TrojAI has larger model sets specifically for backdoor detection. If we use TrojAI for the backdoor condition and ModelZoo for accuracy/robustness, we get more power. The comparison would need careful normalization, but it's technically feasible.

**Key Points:**
- Mechanism is theoretically sound (locality bias vs learned attention)
- Dataset size is a real concern for interaction effect power
- Solution: use TrojAI (larger) for backdoor, ModelZoo for accuracy/robustness
- Feasible with careful cross-benchmark normalization

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES! And we can strengthen this against Prof. Pax's power concerns. The key insight is that we don't need balanced cells — we need sufficient power *within* each property type to detect architecture differences.

Here's the refined hypothesis: **"Permutation-equivariant weight processing methods show property-type-dependent performance differences on standard model zoo benchmarks, with DWS-style explicit locality yielding better backdoor detection (AUC difference > 0.05) while NFT-style attention excels at accuracy prediction (RMSE reduction > 10%)."**

This addresses:
1. 🔭 Dr. Nova's paradigm framing — it's about inductive biases, not horse-racing
2. 🔬 Prof. Vera's falsifiability — specific thresholds (AUC +0.05, RMSE -10%)
3. 🎯 Dr. Sage's mechanism — grounds in locality vs global processing trade-off
4. ⚙️ Prof. Pax's feasibility — uses existing benchmarks (TrojAI + ModelZoo)

For evidence, the DWS paper shows equivariant layers preserve local weight structure. NFT's attention mechanism processes weights globally. These architectural differences should manifest in task-specific performance.

**Key Points:**
- Refined hypothesis with specific effect size thresholds
- Combines TrojAI (backdoor) + ModelZoo (accuracy/robustness)
- Mechanism grounded in locality vs attention trade-off
- All feasibility constraints satisfied: existing datasets, standard metrics

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down: the "locality" claim for DWS vs "global" for NFT is an assumption, not established fact.

Show me the evidence that NFT actually processes weights more globally than DWS. NFT uses attention, yes, but attention can be local — and DWS ultimately aggregates into a global representation anyway. The mechanism assumes a locality difference that may not exist in practice.

Second concern: the effect size thresholds (AUC +0.05, RMSE -10%) are arbitrary. Why not 3% or 15%? Without a principled basis, these are just numbers that happen to sound reasonable.

Third: confounds. NFT and DWS differ in more than just locality — they have different parameter counts, training procedures, and tokenization schemes. An observed difference could be explained by any of these, not just the hypothesized mechanism.

What would convince me: (1) ablation showing NFT with restricted attention behaves more like DWS, (2) effect sizes derived from prior benchmark variance, (3) controlled comparison with matched parameters.

**Key Points:**
- "Locality vs global" mechanism is assumed, not proven
- Effect size thresholds need principled justification
- Multiple confounds beyond locality (params, training, tokenization)
- Need ablations and controlled comparisons to isolate mechanism

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex's concerns are valid gifts. Let me address each:

**On mechanism evidence:** The DWS paper (Navon et al., 2023) explicitly designs layers to preserve weight locality via equivariant operations on weight-sharing patterns. NFT (Zhou et al., 2024) flattens weights into tokens and processes via full attention. This is architectural fact, not assumption. We can cite the papers directly.

**On effect size thresholds:** Fair point. Let's derive them from benchmark variance. If baseline (flattened-weight MLP) achieves AUC 0.70 ± 0.03 on TrojAI, a meaningful improvement is +0.05 (>1.5σ). For RMSE on accuracy prediction, if baseline is 5% ± 0.8%, then -10% relative (0.5 percentage points) is significant.

**On confounds:** We can't fully ablate in one experiment, but we CAN control for parameter count by using matched-capacity versions. Many confounds are addressed if we include a baseline condition: flattened-weight MLP. Then we're comparing {MLP baseline, NFT, DWS} rather than just NFT vs DWS.

**Refined prediction:** "Compared to a matched-parameter baseline, DWS achieves >1.5σ AUC improvement on TrojAI backdoor detection while NFT achieves >1.5σ RMSE improvement on ModelZoo accuracy prediction."

**Key Points:**
- Mechanism grounded in architectural facts from the papers
- Effect sizes derived from baseline variance (>1.5σ)
- Include MLP baseline to isolate equivariance contribution
- Three-way comparison: {Baseline, NFT, DWS} × {accuracy, backdoor}

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Now we have something testable. Let me formalize the experimental design:

**Independent Variable:** Architecture type (3 levels: MLP-baseline, NFT, DWS)
**Dependent Variables:** 
- Primary: Backdoor detection AUC (TrojAI), Accuracy prediction RMSE (ModelZoo)
- Secondary: Inference time, parameter count (to verify matching)

**Design:** 3×2 mixed design (Architecture × Property-Type)
- Within-subject: Property type (same model zoo tested on both)
- Between-subject: Architecture (different trained predictors)

**Predictions:**
- P1 (PRIMARY): DWS outperforms NFT and baseline on backdoor detection by >1.5σ
- P2: NFT outperforms DWS and baseline on accuracy prediction by >1.5σ  
- P3: Baseline underperforms both on at least one property type

**Falsification:** If NFT ≥ DWS on backdoor detection OR DWS ≥ NFT on accuracy prediction, the locality mechanism hypothesis fails. If baseline matches or exceeds both, equivariance provides no benefit.

**Key Points:**
- 3×2 mixed design with matched-parameter controls
- Specific predictions with >1.5σ thresholds derived from baseline variance
- Clear falsification criteria
- Uses existing benchmarks: TrojAI (backdoor) + ModelZoo (accuracy)

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis reframes a routine benchmark comparison into a principled study of inductive biases. The insight that property type may interact with architecture choice is novel and actionable. Cross-domain connection to CNN vs ViT locality debates strengthens the contribution.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear, quantitative predictions with derived effect size thresholds. The 3×2 design with matched baselines is methodologically sound. Falsification criteria are explicit: reversal of predicted architecture advantages would reject the mechanism.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE-STRONG
- **Assessment:** Provides actionable guidance for practitioners choosing between architectures. Grounds the comparison in a locality mechanism. Contribution is strongest if the interaction effect holds; if architectures perform similarly, significance reduces to a null result (still useful but less impactful).

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Uses existing benchmarks (TrojAI, ModelZoo). No new data collection required. Matched-parameter comparison is achievable with public implementations. Statistical power is adequate given effect size derivation from baseline variance.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a refined hypothesis: **Permutation-equivariant weight processing architectures exhibit property-type-dependent performance profiles on model zoo benchmarks, explained by their differing locality inductive biases.**

Core claim: DWS-style explicit locality in equivariant layers improves detection of fine-grained weight patterns (backdoor triggers), while NFT-style attention excels at capturing global weight statistics (accuracy prediction).

Mechanism: DWS encodes spatial weight structure directly in layer operations, reducing sample complexity for local pattern detection. NFT's full attention must learn locality from data, advantaging global property aggregation.

Predictions: (1) DWS > NFT > baseline on TrojAI backdoor detection AUC by >1.5σ; (2) NFT > DWS > baseline on ModelZoo accuracy prediction RMSE by >1.5σ; (3) Both equivariant methods outperform baseline on at least one task, validating the equivariance contribution.

Experimental approach: Train matched-parameter versions of NFT, DWS, and MLP-baseline on TrojAI and ModelZoo. Compare AUC (backdoor) and RMSE (accuracy) with statistical tests. Include inference time as secondary measure.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Cross-benchmark normalization between TrojAI and ModelZoo may introduce confounds (different model architectures in each zoo).
- **Concern 2:** The "locality" mechanism is plausible but indirect — we infer from architecture, not from probing internal representations.
- **Mitigation Strategy:** Include sensitivity analysis across model architecture subgroups within each benchmark. For mechanism, add attention pattern visualization in NFT to verify global vs local processing.

