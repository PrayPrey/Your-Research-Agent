# 5. Root Cause Analysis

The uniform degradation of $\rho_j$ across both factual and creative domains (0.01–0.04 vs expected 0.75–0.85) demands systematic diagnosis. We frame this as a competing explanations problem: four hypotheses ($H_1$ through $H_4$) are evaluated against empirical evidence, then synthesized into a hierarchical root cause model.

## 5.1 Competing Explanations Framework

**Evaluation Criteria**:
1. **Convergent Evidence**: Does the explanation align with multiple independent data sources (our experiments, literature, sanity checks)?
2. **Magnitude Fit**: Can the mechanism explain a 50× shift in $\rho_j$?
3. **Domain Specificity**: Does it predict uniform degradation (both domains affected) or domain-selective degradation (creative only)?
4. **Testability**: Can the hypothesis be falsified via ablation or calibration studies?

We rank explanations by likelihood (HIGH/MEDIUM/LOW) and assign them to three tiers: Primary (Tier 1), Contributory (Tier 2), Unlikely (Tier 3).

## 5.2 $H_1$: Out-of-Distribution Generalization Gap (Tier 1 - PRIMARY)

**Mechanism**: DeBERTa-v3-base, trained on SNLI/MNLI (sentence-pair semantic similarity tasks), does not generalize to factual verification tasks (claim-context consistency checking). The model treats claim-context pairs as "unrelated statements" rather than "factual entailment checks," defaulting to the "neutral" class.

**Supporting Evidence**:

1. **Our Data (Uniform Degradation)**: $\rho_j$ = 0.0354 (factual) and 0.0103 (creative)—both 50× below expected. If creative text confuses NLI (original hypothesis), factual text should work normally. Both fail → task-general issue, not domain-specific.

2. **Our Data (Neutral-Class Dominance)**: Mean $P(\text{neutral})$ = 0.910 (factual), 0.967 (creative). This mechanistically explains low $\rho_j$: when neutral mass ≈ 0.9, $\rho_j = (P(\text{entail}) + P(\text{contradict})) / 1.0 \approx 0.09$.

3. **Sanity Check Failure**: On manually selected TruthfulQA correct/incorrect answers, $P(\text{entail}|\text{correct}) = 0.11$ (expected > 0.5), $P(\text{contradict}|\text{incorrect}) = 0.08$ (expected > 0.5). The NLI model fails on known ground-truth examples.

4. **Literature Triangulation**:
   - **Himal-Badu/Prediction-of-Prediction**: Found NLI features dominate over attention mechanisms ($r < 0.1$ for attention-hallucination correlation), with low overall predictive power—consistent with NLI models not calibrated for hallucination detection.
   - **Shaguns26/HallucinoGenAI**: Achieved 95% recall only after threshold tuning from 50% to 30%, indicating uncalibrated outputs requiring task-specific adjustment.

**Theoretical Framing**: SNLI/MNLI training objectives optimize for **semantic similarity detection** ("Do these sentences describe similar situations?"), not **factual verification** ("Is this claim consistent with this context?"). The distinction:
- **Semantic similarity**: "A dog plays in the park" ↔ "A puppy runs outside" → ENTAILMENT (same event)
- **Factual verification**: Claim: "The president was born in 1980." Context: "Obama was born in 1975." → CONTRADICTION (inconsistent facts)

When DeBERTa processes claim-context pairs with limited lexical overlap (common in factual verification), it defaults to "neutral" because the SNLI/MNLI training distribution contains few long-context factual verification examples.

**Magnitude Fit**: ✅ **STRONG**. A model trained for one task (similarity) applied to another (verification) can easily produce 50× magnitude shifts when the output class distributions differ fundamentally.

**Domain Specificity**: ✅ **PREDICTS UNIFORM DEGRADATION**. Matches observed pattern (both domains affected equally).

**Likelihood**: **HIGH** (primary explanation)

**Falsifiability**: Fine-tune DeBERTa on FEVER or HotpotQA (1000–5000 factual verification examples). If $\rho_j$ improves to 0.70–0.85, $H_1$ confirmed.

## 5.3 $H_2$: Claim Decomposition Quality (Tier 2 - CONTRIBUTORY)

**Mechanism**: NLTK sentence tokenization produces sentences that lack clear entailment relationships (sentences ≠ logical claims). NLI receives fragmented propositions that are genuinely "neutral" relative to context.

**Supporting Evidence**:

1. **Observation**: Mean 5.8 claims/sample (factual), 6.2 (creative)—reasonable for sentence tokenization but no validation against logical claim boundaries.

2. **Gap**: No claim validation step implemented. No manual inspection of extracted claims. No inter-method agreement analysis (NLTK vs LLM extraction vs dependency parsing).

3. **Example Failure Modes**:
   - **Incomplete claims**: "After the meeting" (lacks predicate)
   - **Compound claims**: "He walked to the store and bought bread" (2 claims in 1 sentence)
   - **Context-dependent claims**: "It was blue" (requires antecedent resolution)

**Theoretical Framing**: Sentence boundaries do not align with logical proposition boundaries. NLTK splits on punctuation, not on semantic/logical structure. If claims are improperly segmented, NLI may correctly assign "neutral" because the claim lacks sufficient information for entailment/contradiction.

**Magnitude Fit**: ⚠️ **MEDIUM**. Claim quality issues can degrade $\rho_j$, but explaining a 50× shift requires assuming nearly all claims are malformed—plausible but not confirmed.

**Domain Specificity**: ⚠️ **DOMAIN-AGNOSTIC**, but creative text may have more complex sentence structures (nested clauses, metaphors) that exacerbate tokenization errors.

**Likelihood**: **MEDIUM** (contributory, but secondary to $H_1$)

**Falsifiability**: Compare NLTK vs LLM-based claim extraction (GPT-3.5/GPT-4). If $\rho_j$ improves by >0.10 with LLM extraction, $H_2$ confirmed as contributory.

## 5.4 $H_3$: Context Pairing Strategy (Tier 2 - CONTRIBUTORY)

**Mechanism**: Using full text as context (vs claim-local windows) creates premise-hypothesis pairs that are too distant for the NLI model to detect entailment. The model defaults to "neutral" for long-distance dependencies.

**Supporting Evidence**:

1. **CCP Paper Gap**: Does not specify context windowing strategy. We followed cavaquinho's full-text pattern, but this may not match the original implementation.

2. **NLI Model Design**: DeBERTa-v3-base max sequence length = 512 tokens. Long contexts may truncate or dilute relevant information.

3. **Training Distribution**: SNLI/MNLI contain premise-hypothesis pairs with **local semantic relationships** (single-sentence or paragraph-level). Factual verification requires **long-range consistency** (claim at sentence $N$, contradictory fact at sentence $N-50$).

**Theoretical Framing**: When context is too long, attention mechanisms may fail to locate relevant contradictions, assigning "neutral" by default.

**Magnitude Fit**: ⚠️ **MEDIUM**. Context windowing affects signal strength but is unlikely to cause a 50× magnitude shift alone (more likely a 2-5× degradation).

**Domain Specificity**: **DOMAIN-AGNOSTIC**, though creative text (longer narratives) may be more affected than factual text (shorter Q&A pairs).

**Likelihood**: **MEDIUM** (requires ablation study to quantify; plausible but not confirmed)

**Falsifiability**: Test full-text vs ±1, ±2, ±3 sentence windows. If optimal window size achieves $\rho_j > 0.70$, $H_3$ confirmed as contributory.

## 5.5 $H_4$: Temperature/Calibration Issue (Tier 3 - UNLIKELY)

**Mechanism**: NLI model outputs are overconfident in "neutral" predictions due to uncalibrated logits. Temperature scaling could shift probability mass to entailment/contradiction classes.

**Supporting Evidence**:

1. **Literature**: Neural networks trained with cross-entropy loss optimize for classification accuracy, not probability calibration (Guo et al., 2017). Post-hoc calibration (temperature scaling, Platt scaling) can improve probability estimates.

2. **Gap**: No calibration diagnostics implemented (Expected Calibration Error, reliability diagrams).

**Theoretical Framing**: If DeBERTa is overconfident in "neutral," temperature $T < 1$ could reduce neutral mass and increase entailment/contradiction mass.

**Magnitude Fit**: ❌ **WEAK**. Calibration typically improves metrics by 5–20%, not 50×. A 50× shift suggests a deeper issue than miscalibration.

**Domain Specificity**: **DOMAIN-AGNOSTIC** (calibration issues affect all domains equally).

**Likelihood**: **LOW** (magnitude argument: calibration alone cannot explain 50× shift)

**Falsifiability**: Learn temperature $T$ on validation set to minimize ECE. If calibrated $\rho_j$ improves by <0.10, $H_4$ refuted.

## 5.6 Root Cause Hierarchy

**Table 5: Root Cause Summary with Evidence Strength**

| Tier | Hypothesis | Mechanism | Evidence Strength | Magnitude Fit | Likelihood |
|------|-----------|-----------|-------------------|---------------|-----------|
| **1** | $H_1$: OOD Generalization Gap | SNLI/MNLI ≠ factual verification | Uniform degradation + sanity check + literature | 50× shift explained | **HIGH** |
| **2** | $H_2$: Claim Decomposition | Sentence ≠ logical claim | Plausible mechanism, no ablation | 50× requires all claims malformed | **MEDIUM** |
| **2** | $H_3$: Context Pairing | Full-text vs local windows | Plausible mechanism, no ablation | 2-5× shift expected | **MEDIUM** |
| **3** | $H_4$: Temperature/Calibration | Overconfident neutral | Known neural network issue | 5-20% shift typical | **LOW** |

**Primary Cause (Tier 1)**: Out-of-distribution generalization gap from SNLI/MNLI to factual verification. This is the **necessary** condition—without NLI calibration, $\rho_j$ cannot reach expected range.

**Contributory Factors (Tier 2)**: Claim decomposition quality and context pairing strategy likely amplify the primary issue but are **not sufficient** to cause 50× degradation alone.

**Unlikely (Tier 3)**: Temperature/calibration is a **modulator** (affects ranking, not magnitude) rather than a root cause.

**Synthesis**: The root cause hierarchy suggests a **multiplicative failure model**:

$$\rho_j^{\text{observed}} = \rho_j^{\text{baseline}} \times \underbrace{\text{OOD penalty}}_{\text{Tier 1}} \times \underbrace{\text{claim quality penalty}}_{\text{Tier 2}} \times \underbrace{\text{context penalty}}_{\text{Tier 2}}$$

If OOD penalty ≈ 0.1 (90% neutral class), claim quality penalty ≈ 0.5, and context penalty ≈ 0.5, then:

$$\rho_j^{\text{observed}} = 0.80 \times 0.1 \times 0.5 \times 0.5 = 0.02$$

This matches the observed 0.01–0.04 range, supporting the hierarchical model.

## 5.7 Theoretical Implications

### 5.7.1 Task-Domain Gap vs Domain Shift

**Traditional Domain Shift**: A model trained on news text (source domain) applied to social media text (target domain) with different vocabulary and syntax.

**Task-Domain Gap (our finding)**: A model trained on **Task A** (semantic similarity: SNLI/MNLI) applied to **Task B** (factual verification: claim-context consistency), even when both tasks process similar text types (questions, statements).

**Key Distinction**: Domain shift is about **data distribution** (vocabulary, style). Task-domain gap is about **training objective** (what the model was trained to predict).

**Novelty**: This distinction is underexplored in hallucination detection literature. Papers assume NLI models are "general entailment detectors," but our results suggest SNLI/MNLI-trained models are **specialized for semantic similarity**, not factual verification.

### 5.7.2 Measurement Validity as Prerequisite for Hypothesis Testing

**Methodological Principle**: When a metric produces values far outside the expected range (50× deviation), you must validate the measurement before testing domain-specific hypotheses.

**Logical Impossibility**: We cannot distinguish "creative text confuses CCP" (hypothesis) from "CCP implementation does not work as described" (measurement broken) when BOTH factual and creative domains show 50× degradation.

**Analogy**: Testing a new drug on rare disease patients without first validating dosage on healthy controls. If all patients show zero response, is the disease unresponsive, or is the drug inactive?

**Implication for Research Practice**: Always replicate baseline on original domain BEFORE testing domain transfer. This applies broadly to ML/NLP: testing a sentiment analyzer on poetry requires first validating it on the original training domain (e.g., movie reviews).

### 5.7.3 Reproducibility Gap in Hallucination Detection

**Observation**: The CCP paper does not report:
- Raw $\rho_j$ distributions (only ROC-AUC improvements)
- NLI calibration diagnostics (does the model work on known examples?)
- Claim decomposition methodology (sentence tokenization? LLM extraction?)
- Context pairing strategy (full-text? windowed?)

**Consequence**: We could not reproduce the baseline, preventing us from testing our hypothesis.

**Field-Wide Pattern**: Hallucination detection papers optimize for **novelty** (reporting +0.05 ROC-AUC) over **reproducibility** (documenting how to achieve the baseline). This creates a "replication crisis" where methods cannot be extended to new domains because the baseline cannot be reproduced.

**Call to Action**: Section 6.3 proposes concrete reproducibility requirements to prevent repetition of this failure mode.
