# Phase 2A Discussion Log

**Date:** 2026-08-19
**Architecture:** Self-Contained Tikitaka Loop
**Execution Mode:** UNATTENDED

---

## Research Briefing

### Selected Gap

**Gap ID:** Gap-1
**Title:** Paraphrase-Resistant Detection at Scale
**Priority:** HIGH | **Relevance:** PRIMARY

**Current State:** N-gram overlap (13-gram) is industry standard but trivially bypassed by paraphrasing. Llama-2-13B trained on rephrased MMLU achieves 85.9% accuracy while evading detection.

**Missing Piece:** Scalable semantic similarity methods that detect paraphrased contamination without prohibitive compute on trillion-token datasets.

**Potential Impact:** Would close primary evasion vector; enable trustworthy benchmark evaluation even for models trained on web data.

### Research Question

What automated methods can reliably detect n-gram and semantic overlap between foundation model training data and standard benchmark test sets (MMLU, GSM8K, HumanEval), and how does contamination level correlate with inflated benchmark performance?

### Key Papers

1. **Rethinking Benchmark and Contamination (2023)** - arXiv:2311.04850 - Demonstrates paraphrase evasion
2. **Data Contamination Quiz (2023)** - arXiv:2311.06233 - Quiz-based detection without training data
3. **Benchmark Data Contamination Survey (2024)** - arXiv:2406.04244 - Up to 45% contamination in LLMs
4. **Does Data Contamination Detection Work (2024)** - arXiv:2410.18966 - Detection assumptions evaluation

### Available Tools

- N-gram overlap: overlapy, wellecks/overlap (exact match only)
- Quiz-based: DCQ repository
- Evaluation: lm-evaluation-harness decontamination module

### Mandatory Feasibility Constraints

- Must use existing real datasets and benchmarks
- No synthetic data or new benchmark creation
- No human evaluation required
- Testable immediately with existing resources

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting challenge! The paraphrase evasion problem is fundamentally about the gap between syntactic matching and semantic understanding. N-gram methods work at the surface level — they see tokens, not meaning. But here's what gets me excited: **what if we flip the detection paradigm entirely?**

Instead of asking "does the training data contain this benchmark item?" we could ask "does the model BEHAVE as if it memorized this item?" The Data Contamination Quiz paper (Golchin & Surdeanu, 2023) hints at this — they test model behavior rather than corpus content. But they still work at the item level.

Here's my wild idea: **Embedding-Space Density Analysis**. If a model was trained on paraphrased benchmark data, the embedding space around those concepts should show abnormal density or clustering. Models develop "attractors" around memorized content. We could detect contamination by measuring embedding space topology — specifically, whether benchmark items fall into unusually dense or low-perplexity regions compared to truly novel items from the same distribution.

The beauty? This scales beautifully. You don't scan trillion tokens — you probe the model's internal geometry. One forward pass per benchmark item, then compare the embedding landscape. Cross-domain thinking from dynamical systems: attractors reveal what the system has "learned" too well.

**Key Points:**
- N-gram detection fails because it matches syntax, not semantics
- Behavioral detection (how model acts) may beat content detection (what corpus contains)
- Embedding space topology could reveal memorization through abnormal clustering
- Scalability advantage: probe model geometry, don't scan corpus

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your embedding-space density idea is intriguing, but let me stress-test it. The critical question: **what would disprove this hypothesis?**

If we claim "contaminated models show abnormal embedding density around benchmark items," we need precise falsification criteria. Consider: models develop dense embedding regions around ANY frequently-seen concepts. How do we distinguish "memorized benchmark item" from "well-learned common knowledge"? MMLU contains many general facts that appear naturally across web data.

The DCQ paper (Golchin & Surdeanu, 2023) addresses this by using word-level perturbations — if a model completes "The capital of France is ___" but fails on "The primary city of France is ___", that signals memorization over understanding. But even this has confounds: some phrasings are simply more common.

For your embedding density approach, I propose these falsification tests:
1. **Calibration baseline**: Measure embedding density on items the model CANNOT have seen (post-training-cutoff facts). If these also show high density, the metric is invalid.
2. **Paraphrase consistency**: If truly memorized, paraphrased versions should show LOWER density than verbatim. If density is similar, we're measuring concept familiarity, not contamination.
3. **Known contamination validation**: Test on Llama-2-13B trained on rephrased MMLU — does your method detect what n-gram misses?

The evidence suggests we need a two-stage approach: behavioral detection (your embedding idea) validated against known contamination cases.

**Key Points:**
- Need falsification criteria distinguishing memorization from general knowledge
- Calibration baseline using post-cutoff items is essential
- Paraphrased vs. verbatim density difference could be diagnostic
- Must validate on known contamination cases (rephrased MMLU experiment)

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me step back and ask: **what does this mean for the field?**

The contamination detection problem matters because it threatens benchmark validity itself. If we can't trust MMLU scores, the entire FM evaluation ecosystem crumbles. But significance isn't just about the problem — it's about whether our solution enables new research directions.

Dr. Nova's embedding density approach is promising, but I see a more impactful framing: **contamination detection as a special case of memorization vs. generalization**. This connects to fundamental questions in ML theory that the field has struggled with for decades.

The "Rethinking Benchmark and Contamination" paper (2023) showed Llama-2-13B reaches 85.9% on rephrased MMLU while evading n-gram detection. This isn't just a detection failure — it raises the question: **is there any functional difference between a model that memorized benchmark items and one that genuinely understands the domain?**

If our detection method also predicts performance degradation on novel items from the same distribution, we've made a contribution beyond contamination detection. We'd be providing a general test for "does this model understand or just remember?"

The question we must ask is: can we design a detection method that simultaneously:
1. Identifies paraphrased contamination
2. Predicts performance gap on truly novel items
3. Quantifies the "generalization deficit" from contamination

This matters because it transforms contamination detection from a binary cleanup task into a principled measure of benchmark validity.

**Key Points:**
- Contamination detection impacts entire FM evaluation ecosystem
- Deeper significance: memorization vs. generalization is a fundamental ML question
- Detection method should predict performance on novel items, not just flag contamination
- "Generalization deficit" metric would be a genuine field contribution

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Dr. Nova's embedding density idea and Dr. Sage's generalization deficit framing are intellectually appealing, but I need to check the fundamental barriers.

**Technical feasibility assessment:**

1. **Embedding extraction scalability**: For behavioral detection, we need forward passes on benchmark items. MMLU has ~14K questions — that's trivial. But if we're computing embedding statistics, we also need reference distributions. What's our reference set? Random web samples? How many?

2. **Statistical power for density detection**: Embedding spaces are high-dimensional (768-4096). Detecting "abnormal density" in high-D spaces is notoriously hard — curse of dimensionality means most points look equally distant. We'd need robust density estimators designed for this setting.

3. **Known contamination ground truth**: Prof. Vera rightly demands validation on known cases. The Llama-2-13B rephrased MMLU experiment exists. Can we access those model checkpoints? The paper is from 2023 — models may not be publicly available.

4. **Causal mechanism validity**: The hypothesis assumes contamination creates detectable embedding signatures. But transformer embeddings are learned end-to-end — a model trained on paraphrased content might NOT show different geometry than one trained on original. The embedding space adapts to whatever the model sees.

What would convince me: a pilot study showing embedding density differs between contaminated and clean models on the SAME benchmark items. Without this proof-of-concept, the mechanism remains theoretical.

I propose a minimal viable test: Take a small model (GPT-2), fine-tune one copy on 100 verbatim MMLU items, another on 100 paraphrased versions. Measure embedding density on the original items. If density differs, the mechanism is physically possible.

**Key Points:**
- Embedding density estimation in high-D spaces is technically challenging
- Need reference distribution for comparison — what constitutes "normal" density?
- Ground truth validation requires access to contaminated model checkpoints
- Minimal viable test: fine-tune small models on verbatim vs. paraphrased, compare embeddings

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and we can strengthen this! Prof. Pax raises valid concerns, but I see clear paths forward.

**Addressing the high-dimensional density challenge:**
Instead of raw density estimation, we could use **relative density comparison**. For each benchmark item, compare its embedding to:
- (a) Its own paraphrased versions
- (b) Semantically similar but distinct items
If contaminated, the model should show tighter clustering around (a) and looser around (b). This becomes a **contrastive test** rather than absolute density measurement.

**Solving the reference distribution problem:**
We don't need external references. Use the benchmark itself: create paraphrase sets for each item (existing NLP paraphrasers like T5-based models). The reference IS the paraphrase set. Contaminated models should show asymmetric behavior — high confidence on original, lower on paraphrases.

**Ground truth validation path:**
The Llama-2-13B checkpoint concern is valid, but we can create our OWN ground truth:
1. Take an open model (LLaMA-3, Mistral, Qwen)
2. Fine-tune on 500 verbatim MMLU items (known contamination)
3. Fine-tune another on 500 paraphrased MMLU items (known contamination, different form)
4. Keep third copy clean
5. Test our detection method on all three

This gives us perfect ground truth without requiring external checkpoints. The "Rethinking Benchmark" paper's setup is replicable.

**Synthesis with Dr. Sage's framing:**
The contrastive test naturally extends to generalization assessment. If a model shows high asymmetry (loves originals, struggles with paraphrases), that's both contamination signal AND generalization deficit. One metric, two purposes.

**Key Points:**
- Contrastive density (original vs. paraphrase) avoids absolute density estimation problems
- Self-referential paraphrase sets provide the reference distribution
- Create own ground truth via controlled fine-tuning experiment
- Contrastive asymmetry measures both contamination and generalization deficit

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me show you the gaps.

**Gap 1: Paraphrase quality confound**
Dr. Ally proposes using T5-based paraphrasers to generate reference paraphrases. But paraphrase quality varies wildly. If the paraphraser produces awkward or unnatural phrasings, ALL models (contaminated or not) will show asymmetry — confident on natural phrasing, uncertain on awkward rewrites. You're measuring paraphrase naturalness, not contamination.

**Gap 2: Memorization granularity**
The hypothesis assumes models memorize at the item level. But what if memorization is sub-item? A model might memorize "the mitochondria is the powerhouse of the cell" as a phrase, not as an MMLU question. Your item-level embedding density won't detect phrase-level memorization that happens to appear in benchmark items.

**Gap 3: Threshold problem**
Prof. Vera asked for falsification criteria. Even if the mechanism works, what asymmetry threshold indicates contamination? 10% confidence drop on paraphrases? 30%? This isn't a rhetorical question — without principled thresholds, the method produces continuous scores without actionable decisions.

**Gap 4: False negative risk**
Models trained on high-quality paraphrases (like the Llama-2-13B experiment) might show NO asymmetry — they've seen both styles. Your method would miss exactly the contamination case we care most about: sophisticated paraphrase-based data augmentation.

What would convince me: demonstrate that contrastive asymmetry correlates with KNOWN contamination level in a controlled experiment. Not just "contaminated models show asymmetry" but "5% contamination produces X asymmetry, 20% produces Y" — a calibrated relationship.

**Key Points:**
- Paraphrase quality confound: awkward paraphrases cause asymmetry regardless of contamination
- Phrase-level vs. item-level memorization may evade item-level detection
- Threshold problem: need principled cutoffs for actionable decisions
- Models trained on paraphrases may show no asymmetry — false negatives on sophisticated contamination

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, your critique about phrase-level memorization just sparked something. What if we're thinking about this wrong?

The asymmetry approach assumes contamination is about SURFACE FORM — original vs. paraphrase. But "Rethinking Benchmark" showed models trained on paraphrased MMLU still perform well on original items. This means **knowledge transfer occurs** — the model learned the underlying concept, not just the specific words.

New angle: **Semantic Saturation Detection**. Instead of measuring asymmetry between original and paraphrase, measure **saturation depth** — how many DIFFERENT phrasings of the same concept produce confident responses?

Clean model on novel concept: confident only on common phrasings, uncertain on unusual ones.
Contaminated model: confident across MANY phrasings — the semantic region is "saturated" because training included diverse expressions.

This flips the problem: instead of looking for asymmetry (which paraphrase-trained models won't show), look for UNUSUAL uniformity. A model shouldn't be equally confident on "What's the capital of France?", "Name the French capital city", "Paris is the ___ of France", "Which city serves as France's seat of government" — unless it's been trained on all variants.

Cross-domain insight: this is like coverage analysis in software testing. Contaminated models have "high coverage" of the semantic space around benchmark items. Clean models have spotty coverage — confident on common phrasings, uncertain on rare ones.

**Key Points:**
- Asymmetry fails for paraphrase-trained models (they're symmetric!)
- Semantic saturation: abnormal uniformity across diverse phrasings
- Clean models should show confidence variance; contaminated show uniformity
- Coverage metaphor: contamination = high coverage of semantic space

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, semantic saturation is more defensible than asymmetry. Let me design the falsification protocol.

**Testable Prediction:**
"Models contaminated with benchmark items (verbatim or paraphrased) will show lower variance in confidence across semantic paraphrases of those items, compared to clean models."

**Experimental Design:**
1. Generate K paraphrases (K=10-20) for each benchmark item using diverse methods
2. For each model: measure confidence (probability of correct answer) on all K+1 versions
3. Compute confidence variance within each item's paraphrase set
4. **Contaminated models should show LOWER variance** (more uniform confidence)

**Falsification Criteria:**
- If clean models also show low variance: concept is already well-known, not contamination
- If contaminated models show high variance: mechanism is invalid
- Threshold derivation: use distribution of variances from controlled experiment (known clean vs. known contaminated)

**Control for concept familiarity:**
Use MMLU category as stratification. High-school level facts (likely in pretraining) vs. specialized domain facts (less likely). If method only works on specialized domains, it's confounded with prior exposure.

**Addressing Prof. Rex's paraphrase quality concern:**
Use MULTIPLE paraphrasers (T5, GPT-4, rule-based synonym replacement) and measure inter-method variance. If specific paraphraser causes artifacts, it will show as outlier in multi-paraphraser analysis.

**Key Points:**
- Testable prediction: contaminated = lower confidence variance across paraphrases
- Multi-paraphraser approach controls for paraphrase quality artifacts
- Stratification by concept difficulty distinguishes contamination from prior exposure
- Principled threshold via controlled comparison (known clean vs. known contaminated)

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The hypothesis is maturing. Let me articulate why "Semantic Saturation Detection" is a genuine contribution.

**What makes this genuinely new:**
1. **Paradigm shift from detection to characterization**: N-gram methods ask "is there overlap?" We're asking "how does the model's semantic representation of benchmark items differ from novel items?"
2. **Paraphrase-resistance by design**: Instead of trying to match surface forms (which fails), we exploit the CONSEQUENCE of paraphrase training — semantic uniformity.
3. **Quantitative metric**: Confidence variance is continuous and interpretable. Higher variance = more "genuine understanding", lower variance = potential contamination.

**How this advances the field:**
- Enables contamination-adjusted benchmark scores: "Model X scores 85% on MMLU with saturation index 0.2 (suspicious) vs. Model Y with 80% and saturation index 0.8 (clean)"
- Opens research direction: what IS the relationship between training exposure and semantic saturation? This could inform data curation strategies.
- Applicable beyond contamination: the same metric could assess overfitting to specific domains.

**But here's the critical gap:**
We've been discussing detection, but the Phase 1 research also asked about **correlation with inflated performance**. Our method detects contamination — but does detected contamination actually correlate with score inflation?

The ultimate validation: show that high saturation index items contribute disproportionately to benchmark scores. If contamination doesn't inflate scores, detection is academic.

**Key Points:**
- Semantic saturation is paradigm shift: characterization over surface matching
- Continuous metric enables contamination-adjusted benchmark scores
- Research impact: opens data curation and overfitting detection directions
- Must validate: does detected contamination correlate with score inflation?

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me verify the mechanism is scientifically sound.

**Mechanism validation:**
The claim is: "Training on diverse phrasings of concept X causes lower confidence variance across phrasings of X at inference time."

This is plausible. Neural networks generalize from training distribution. If training includes many paraphrases, the learned representation should be robust to phrasing variation — manifesting as uniform confidence. If training only saw one phrasing, the representation is phrasing-specific — manifesting as variance.

**Technically sound? Yes, in principle.**

**Remaining feasibility concerns:**

1. **Paraphrase diversity requirement**: We need genuinely diverse paraphrases. Simple synonym replacement isn't enough — we need syntactic, lexical, AND semantic variation while preserving meaning. Can existing paraphrasers do this reliably for 14K MMLU items?

2. **Confidence calibration**: We're measuring confidence variance. But LLM confidences are notoriously miscalibrated. A model might show uniform confidence because it's overconfident on everything. Need to verify: does variance in calibrated probability (not raw logits) still distinguish contamination?

3. **Compute scale**: 14K items × 20 paraphrases × 21 model calls = 6M forward passes per model tested. For API-based models, this is expensive. For open-weight models, it's tractable but not trivial.

**What I now believe:**
The mechanism is physically possible. The main feasibility barriers are (a) paraphrase generation quality at scale, and (b) ensuring confidence metrics are meaningful (calibration). Neither is fundamental — both are engineering.

**Key Points:**
- Mechanism is scientifically sound: diverse training reduces inference-time variance
- Paraphrase generation at scale is main engineering challenge
- Confidence calibration must be addressed — use calibrated probabilities
- Compute is tractable for open-weight models (~6M forward passes per model)

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converging! Let me synthesize the emerging hypothesis.

**Core Claim (Under-If-Then-Because format):**
Under standard foundation model evaluation settings, if a model was trained on benchmark items (verbatim or paraphrased), then it will exhibit lower confidence variance across diverse paraphrases of those items compared to clean models, because exposure to diverse phrasings during training creates robust semantic representations that generalize uniformly across phrasing variations.

**Key Variables:**
- **Independent Variable**: Contamination status (clean, verbatim-contaminated, paraphrase-contaminated) + contamination level (percentage of benchmark in training)
- **Dependent Variable**: Semantic Saturation Index (SSI) = inverse of mean confidence variance across paraphrase sets
- **Controlled**: Model architecture, paraphrase generation method, benchmark difficulty distribution

**Predictions:**
1. **P1 (Primary)**: SSI will be significantly higher for contaminated models than clean models on contaminated benchmark items (effect size d > 0.5)
2. **P2**: SSI will correlate positively with contamination level (r > 0.6)
3. **P3**: Items with high SSI will show disproportionately high accuracy contribution (validating score inflation connection)

**Experimental Setup:**
- Dataset: MMLU (14K items, stratified by difficulty)
- Models: Create controlled contamination (clean, 5%, 10%, 20% contaminated versions of open model)
- Paraphrases: K=20 per item using multi-paraphraser approach
- Baselines: N-gram overlap (GPT-3 style), DCQ (quiz-based)

**Key Points:**
- Hypothesis formulated in testable Under-If-Then-Because structure
- Semantic Saturation Index (SSI) is proposed metric
- Three predictions: detection capability, dose-response, score inflation correlation
- Controlled experiment design with known contamination levels

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is solid. Let me stress-test the remaining assumptions.

**Assumption A1: Paraphrase quality is sufficient**
Show me the evidence that existing paraphrasers preserve meaning while varying form sufficiently. The multi-paraphraser approach helps, but if ALL paraphrasers cluster in similar syntactic space, we haven't achieved true diversity. Need pilot study measuring paraphrase diversity metrics.

**Assumption A2: Confidence variance is robust to model scale**
Will this work equally for 7B and 70B models? Larger models might show lower variance everywhere due to better generalization. The metric might need scale normalization.

**Assumption A3: Contamination creates detectable signal above noise**
At 5% contamination (typical real-world level), the SSI difference might be tiny. Need power analysis: what contamination level is DETECTABLE given measurement noise?

**Remaining concern:**
The score inflation correlation (P3) is critical but harder to establish. Even if contaminated items show high SSI, proving they "disproportionately contribute" to scores requires counterfactual: what WOULD the score be without those items? We can approximate by excluding high-SSI items and recomputing scores, but that's circular.

**What would convince me:**
1. Pilot study with K=20 paraphrases showing variance difference between clean/contaminated on same items
2. Power analysis establishing minimum detectable contamination level
3. Correlation between item-level SSI and item-level accuracy (across models)

If these three hold, the hypothesis is defensible.

**Key Points:**
- Paraphrase diversity needs pilot validation
- Scale sensitivity requires normalization strategy
- Power analysis needed for minimum detectable contamination
- Score inflation correlation requires careful causal design

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let me formalize the experimental protocol addressing Prof. Rex's concerns.

**Phase 1: Paraphrase Diversity Validation (Pilot)**
- Generate paraphrases for 100 MMLU items using 5 methods
- Measure diversity: syntactic (parse tree edit distance), lexical (word overlap), semantic (embedding cosine)
- Accept if mean pairwise diversity > threshold in all three dimensions

**Phase 2: Controlled Contamination Experiment**
- Base model: Mistral-7B (open, replicable)
- Create 5 versions: clean, 5%, 10%, 20%, 50% contamination (verbatim)
- Create 3 paraphrase variants: 10% paraphrase-contaminated using different paraphrasers
- Total: 8 model variants with known ground truth

**Phase 3: SSI Computation and Validation**
- For each item × model: compute confidence on original + 20 paraphrases
- SSI = 1 / variance(confidence)
- Compare SSI distributions across contamination levels
- Test P1: ANOVA with contamination status as factor
- Test P2: Pearson correlation between contamination % and mean SSI
- Test P3: Regression of accuracy on SSI, controlling for item difficulty

**Falsification criteria:**
- P1 fails: effect size < 0.3 or p > 0.05
- P2 fails: r < 0.4 or non-monotonic relationship
- P3 fails: SSI doesn't predict accuracy after controlling for difficulty

**What result would convince us the hypothesis is wrong:**
If clean models show SSI distributions overlapping substantially with contaminated models (AUC < 0.6 for binary classification), the method lacks discriminative power.

**Key Points:**
- Three-phase protocol: paraphrase validation, controlled experiment, SSI validation
- Eight model variants provide ground truth for all contamination types
- Explicit falsification thresholds for each prediction
- Discrimination benchmark: AUC > 0.6 for clean vs. contaminated classification

---

### Exchange 14

🎯 **Dr. Sage** (Research Impact Evaluator):

The hypothesis and experimental design are now mature. Let me articulate the novelty and impact.

**Preserved Novelty:**
1. **First behavioral contamination metric resistant to paraphrase evasion**: N-gram fails; DCQ needs item-level probing; SSI uses paraphrase diversity as the TEST, not vulnerability.
2. **Continuous, interpretable metric**: Unlike binary detection, SSI provides magnitude — enabling contamination-adjusted benchmark scores.
3. **Mechanistic grounding**: The metric is derived from learning theory (training diversity reduces inference variance), not just empirical correlation.

**Differentiation from Prior Work:**
| Method | Paraphrase-Resistant | Scalable | Continuous | Mechanism-Based |
|--------|---------------------|----------|------------|-----------------|
| N-gram (GPT-3) | No | Yes | No | No |
| DCQ Quiz | Partial | Medium | No | Yes |
| SSI (ours) | Yes | Yes | Yes | Yes |

**Research Directions Opened:**
1. **Contamination-severity spectrum**: Instead of binary clean/contaminated, measure degree
2. **Data curation guidance**: If low-SSI items indicate clean learning, curate for SSI
3. **Benchmark design**: Create benchmarks with built-in SSI baselines

**What this means for the field:**
The contamination problem has blocked trustworthy FM evaluation. SSI provides a principled solution that doesn't require training data access, resists paraphrase evasion, and quantifies rather than just flags. This enables the field to resume meaningful benchmark-based comparison.

**Key Points:**
- Novel: first paraphrase-resistant behavioral contamination metric
- Differentiated: continuous, mechanism-based, scalable
- Impact: enables contamination-adjusted benchmark scores
- Opens directions in data curation and benchmark design

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility confirmation. The hypothesis is now testable with existing resources.

**Resource Check:**
- Model: Mistral-7B — open-weight, no API cost
- Compute: 8 model variants × 14K items × 21 paraphrases = ~2.4M forward passes. On A100, ~10 hours.
- Paraphrasers: T5-paraphrase, GPT-4-API (1000 items for validation), rule-based — all available
- Benchmark: MMLU — publicly available
- Ground truth: self-generated via controlled fine-tuning

**Barriers Resolved:**
- High-D density estimation: replaced with variance (simple, well-understood)
- Reference distribution: self-referential via paraphrases
- Ground truth access: create our own
- Paraphrase quality: multi-method + pilot validation

**Remaining engineering tasks (not feasibility blockers):**
- Implement paraphrase generation pipeline
- Set up fine-tuning infrastructure for contamination creation
- Develop calibration procedure for confidence extraction

**Verdict:** Technically and theoretically feasible. No fundamental barriers. Ready for Phase 2B.

**Key Points:**
- All resources available: open model, public benchmark, accessible paraphrasers
- Compute tractable: ~10 hours on single A100
- No fundamental barriers remain — only engineering
- Ready for Phase 2B implementation planning

---

### Exchange 16

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've reached convergence. Let me summarize the final hypothesis.

**Title:** Semantic Saturation Index for Paraphrase-Resistant Contamination Detection

**Core Hypothesis Statement:**
Under standard foundation model evaluation settings, if a model was trained on benchmark items (verbatim or paraphrased), then it will exhibit significantly higher Semantic Saturation Index (SSI = inverse confidence variance across paraphrases) on those items compared to clean models, because training exposure creates robust semantic representations that generalize uniformly across phrasing variations.

**Mechanism:**
Neural network representations generalize from training distribution. Models trained on diverse phrasings of concept X develop representations invariant to surface form variations. This manifests as low confidence variance when evaluating paraphrased versions of X. The SSI metric captures this invariance as a contamination signal.

**Key Predictions:**
1. P1: SSI discriminates clean from contaminated models (AUC > 0.7)
2. P2: SSI correlates with contamination level (r > 0.6)
3. P3: High-SSI items predict accuracy contribution

**Null Hypothesis:**
There is no significant difference in SSI between clean and contaminated models on the same benchmark items.

**Experimental Design:**
- Controlled contamination of Mistral-7B (clean, 5%, 10%, 20%, 50%)
- MMLU benchmark with K=20 multi-method paraphrases per item
- Baselines: 13-gram overlap, DCQ

**Key Points:**
- Hypothesis: contamination causes high SSI via representation invariance
- Three testable predictions with quantified success criteria
- Null hypothesis clearly stated
- Experimental design uses controlled ground truth

---

### Exchange 17

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Final review. The hypothesis is now defensible. Remaining objections are addressable:

**Addressed:**
- Paraphrase quality: multi-method approach + pilot validation
- Threshold problem: controlled experiment provides empirical thresholds
- Scale sensitivity: normalization via per-model baseline
- False negatives: SSI detects paraphrase-contamination BY DESIGN (it's the signal)

**Residual concerns (for Phase 2B):**
1. **Domain transfer**: Will SSI trained thresholds on MMLU transfer to GSM8K or HumanEval? Likely needs per-benchmark calibration.
2. **Partial contamination**: What if only some paraphrases of an item were in training? SSI might be intermediate — threshold interpretation unclear.
3. **API model access**: For closed models, confidence extraction may be limited (token probabilities not always available).

**Mitigation:**
- Domain transfer: include GSM8K in validation
- Partial contamination: treat as intermediate contamination level
- API access: use available logprob endpoints; flag limitation for closed models

**Final Assessment:**
The hypothesis is STRONG. The mechanism is sound, predictions are testable, and feasibility is established. Proceed to Phase 2B.

**Key Points:**
- All major objections addressed
- Residual concerns are implementation details, not hypothesis flaws
- Domain transfer and API access are Phase 2B considerations
- Verdict: STRONG hypothesis, ready for verification protocol

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Semantic Saturation Index represents a genuine paradigm shift from surface-form detection to behavioral characterization. By exploiting paraphrase uniformity as the signal rather than vulnerability, SSI inverts the detection problem in a novel way. Cross-domain insight from coverage analysis provides theoretical grounding.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear falsification criteria: AUC < 0.6, r < 0.4, or effect size < 0.3 would each disprove specific predictions. The three-phase experimental protocol (paraphrase validation, controlled contamination, SSI validation) provides rigorous testing framework with explicit thresholds.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** SSI addresses a critical field need — trustworthy benchmark evaluation. The continuous, mechanism-based metric enables contamination-adjusted scores, opening new research directions in data curation and benchmark design. Impact extends beyond detection to understanding memorization vs. generalization.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All resources available: open models (Mistral-7B), public benchmarks (MMLU), accessible paraphrasers. Compute tractable (~10 hours on A100 for full experiment). No fundamental technical barriers — remaining work is engineering implementation.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **Semantic Saturation Index (SSI)** as a paraphrase-resistant contamination detection method. The core insight is that models trained on benchmark items (verbatim or paraphrased) develop semantic representations that generalize uniformly across phrasing variations, manifesting as low confidence variance on paraphrase sets.

SSI = 1 / variance(confidence across K paraphrases)

High SSI indicates potential contamination because clean models show natural confidence variance — confident on common phrasings, less so on unusual ones — while contaminated models are uniformly confident having seen diverse expressions during training.

The hypothesis predicts: (1) SSI discriminates clean from contaminated models with AUC > 0.7, (2) SSI correlates with contamination level r > 0.6, and (3) high-SSI items contribute disproportionately to benchmark scores. Validation uses controlled contamination of Mistral-7B at 5/10/20/50% levels with multi-method paraphrases (K=20) on MMLU.

This approach is novel because it exploits paraphrase diversity as the TEST rather than vulnerability, provides continuous measurement rather than binary detection, and is grounded in learning theory (training diversity creates inference-time invariance).

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Domain transfer: SSI thresholds may not transfer from MMLU to GSM8K/HumanEval
- Partial contamination: Items with partial paraphrase exposure may show intermediate SSI
- API access limitation: Closed models may not expose confidence scores
- **Mitigation Strategy:** Include GSM8K in validation, treat partial as intermediate contamination, document API limitations clearly

---

## Emerged Hypothesis Summary

### Core Statement
Under standard FM evaluation settings, if a model was trained on benchmark items (verbatim or paraphrased), then it will exhibit significantly higher SSI (lower confidence variance across paraphrases) on those items, because training exposure creates representations invariant to phrasing.

### Causal Mechanism
1. Training includes benchmark items (in various phrasings)
2. Model develops robust semantic representation for those concepts
3. Representation invariance manifests as uniform confidence across paraphrases
4. SSI captures this invariance as contamination signal

### Variables
- **IV**: Contamination status/level (clean, 5%, 10%, 20%, 50%)
- **DV**: Semantic Saturation Index (SSI)
- **Controlled**: Model architecture, paraphrase method, benchmark difficulty

### Key Assumptions
- A1: Paraphrasers generate sufficiently diverse variations
- A2: Confidence variance is meaningful (calibration matters)
- A3: Effect size detectable at practical contamination levels (5%+)
- A4: Mechanism generalizes across model scales

### Null Hypothesis
H0: There is no significant difference in SSI between clean and contaminated models on the same benchmark items.

### Predictions
- P1: SSI discriminates clean vs. contaminated (AUC > 0.7)
- P2: SSI ~ contamination level (r > 0.6)
- P3: High-SSI items predict accuracy contribution

### Novelty
First paraphrase-resistant behavioral contamination metric that exploits uniformity rather than asymmetry.

### Scope & Boundaries
- Applies to: Open-weight models with accessible confidence scores, standard NLP benchmarks
- Does not apply to: Closed API models without logprobs, multimodal benchmarks

### Experimental Setup
- Dataset: MMLU (14K items, stratified), GSM8K (validation)
- Model: Mistral-7B with controlled contamination variants
- Baselines: 13-gram overlap, DCQ quiz-based method

### Related Work & Baselines
- 13-gram overlap (GPT-3): fails on paraphrases
- DCQ (Golchin 2023): partial paraphrase resistance, not scalable
- SSI (proposed): paraphrase-resistant, scalable, continuous

### Phase 2B Readiness Seeds
- SH1 (Existence): SSI metric produces measurable variance differences
- SH2 (Mechanism): Variance reduction follows from training distribution invariance
- SH3 (Comparison): SSI outperforms n-gram baseline on paraphrased contamination

### Established Facts
- N-gram methods fail on paraphrased contamination (2311.04850)
- Llama-2 on rephrased MMLU: 85.9% while evading detection
- Up to 45% contamination in popular LLMs (survey 2024)

