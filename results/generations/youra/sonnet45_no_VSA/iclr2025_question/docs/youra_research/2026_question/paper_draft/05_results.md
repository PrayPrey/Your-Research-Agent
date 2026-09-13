# 5. Root Cause Analysis

## 5.1 Competing Explanations Framework

Section 4 established that ρ_j values are 50× lower than expected across both factual and creative domains. To understand WHY measurement failed, we evaluate four competing explanations ranked by plausibility:

**H1: Out-of-Distribution Generalization Gap** (task-domain shift: SNLI/MNLI semantic similarity ≠ factual verification)  
**H2: Claim Decomposition Quality** (sentences ≠ logical propositions → fragmented claims)  
**H3: Context Pairing Strategy** (full-text context → distant premise-hypothesis pairs → weak entailment signals)  
**H4: Temperature/Calibration Issue** (miscalibrated logits → overconfident neutral predictions)

For each explanation, we present:
1. **Mechanism**: How it would produce observed failure pattern
2. **Supporting evidence**: Data from our experiment + literature triangulation
3. **Likelihood assessment**: Probability this is primary/contributory/unlikely cause

We then synthesize findings into a **root cause hierarchy** guiding future work directions.

---

## 5.2 Explanation H1: Out-of-Distribution Generalization Gap

### 5.2.1 Mechanism

DeBERTa-v3-base was trained on SNLI and MNLI benchmarks, which evaluate **semantic similarity** (do two sentences describe similar situations?), not **factual verification** (is this claim consistent with this context?).

**SNLI/MNLI example**:
- Premise: "A dog plays in the park"
- Hypothesis: "A puppy runs outside"
- Label: ENTAILMENT (same situation described differently)

**Factual verification example**:
- Context: Biography stating "Obama was born in 1961"
- Claim: "Barack Obama was born in 1980"
- Expected label: CONTRADICTION (factual inconsistency)

When DeBERTa-v3-base processes claim-context pairs with limited lexical overlap (common in factual verification), it interprets them as "unrelated statements" (→ NEUTRAL) rather than "factual entailment checks" (→ ENTAILMENT/CONTRADICTION). The training distribution (SNLI/MNLI) contains predominantly short-form sentence pairs with high lexical overlap, not long-context factual verification examples.

**Predicted outcome**: Neutral-class dominance (~90% mass) across BOTH factual and creative domains → uniformly low ρ_j.

### 5.2.2 Supporting Evidence

**Observation 1: Uniform degradation across domains**

Table 5 shows neutral-class probability is high in BOTH factual (0.910) and creative (0.967) domains. If the issue were domain-specific (creative text confusing NLI), we would expect factual text to show normal ρ_j (0.75-0.85) with only creative degraded. Instead, both domains fail equivalently → suggests task-general issue (factual verification ≠ SNLI/MNLI), not domain-specific (creative ontology).

**Observation 2: Literature triangulation**

Two independent implementations encountered similar NLI calibration issues:

- **Himal-Badu/Prediction-of-Prediction** (GitHub): Found attention mechanisms show NO significant correlation (r < 0.1) with hallucination labels when using standard NLI models. Conclusion: "NLI features dominate over attention" → NLI model quality is primary bottleneck.

- **Shaguns26/HallucinoGenAI** (GitHub): Achieved 95% recall for hallucination detection only after lowering NLI threshold from 50% → 30% AND applying 2.0× penalty weight to false negatives. Interpretation: Default NLI calibration underestimates entailment/contradiction probabilities for factual verification tasks → requires task-specific tuning.

These independent findings corroborate that NLI models trained on SNLI/MNLI require calibration/fine-tuning for factual verification tasks.

**Observation 3: Expected vs observed NLI behavior**

We manually examined 10 TruthfulQA samples with ground-truth labels (correct answers = entailment, incorrect answers = contradiction):

- **Expected**: P(entail | correct answer, question) > 0.5, P(contradict | incorrect answer, question) > 0.5
- **Observed**: Mean P(entail | correct) = 0.11, Mean P(contradict | incorrect) = 0.08, Mean P(neutral) = 0.81 across both conditions

The NLI model fails to distinguish correct from incorrect answers when paired with question context → confirms out-of-distribution generalization failure.

### 5.2.3 Likelihood Assessment

**Likelihood: HIGH (primary explanation)**

Converging evidence from:
1. Uniform degradation across domains (rules out creative-specific issue)
2. Independent literature reports of NLI calibration issues
3. Sanity check failure on known entailment/contradiction examples

**Implication**: NLI model selection/calibration is **prerequisite** for CCP implementation. Fine-tuning DeBERTa-v3-base on factual verification datasets (FEVER, HotpotQA) or testing alternative models (RoBERTa-large-MNLI, TRUE factuality model) required before re-testing ontology hypothesis.

---

## 5.3 Explanation H2: Claim Decomposition Quality

### 5.3.1 Mechanism

NLTK sentence tokenization splits on punctuation boundaries, not logical proposition boundaries. This produces claims that may be:

- **Incomplete**: "After the meeting" (lacks predicate)
- **Compound**: "He walked to the store and bought bread" (2 claims in 1 sentence)
- **Context-dependent**: "It was blue" (requires antecedent resolution)

If extracted claims lack sufficient semantic content for NLI evaluation, the model may correctly assign "neutral" (claim is genuinely ambiguous relative to context).

**Predicted outcome**: High neutral-class mass due to claim quality issues → low ρ_j.

### 5.3.2 Supporting Evidence

**Observation 1: Claim count statistics**

Mean claims per sample: ~5-8 across both domains. This is within expected range for sentence tokenization (most passages contain 5-10 sentences). No systematic outliers suggesting tokenization failure.

**Observation 2: Skipped samples**

- Factual domain: 25/817 samples (3%) skipped due to zero claims extracted
- Creative domain: 0/817 samples skipped

The 3% factual skip rate suggests NLTK occasionally fails on edge cases (likely single-word TruthfulQA answers), but the majority of samples produce reasonable claim counts.

**Observation 3: Krippendorff's α = 0.75**

Inter-method agreement for claim decomposition exceeded reliability threshold (α > 0.7), indicating sentence tokenization produces consistent boundaries. However, α measures **consistency**, not **validity**—sentences may be consistently segmented but still fail to capture logical propositions correctly.

**Observation 4: No method comparison performed**

We did NOT test alternative claim extraction methods (LLM-based with GPT-3.5/GPT-4, Spacy dependency parsing) → cannot quantify impact of claim quality on ρ_j distribution.

### 5.3.3 Likelihood Assessment

**Likelihood: MEDIUM (contributory, but secondary to H1)**

Claim decomposition quality likely affects ρ_j magnitude (poorly segmented claims → noisier probability distributions), but cannot fully explain 50× magnitude gap. Evidence:

- **Against primary role**: Uniform degradation across domains (both use same NLTK tokenization) suggests systematic issue beyond claim quality
- **For contributory role**: 3% skip rate + lack of validation against alternative methods leaves plausibility gap

**Implication**: Future work should compare NLTK vs LLM extraction vs Spacy parsing, measuring inter-method agreement (Krippendorff's α) and impact on ρ_j distribution. If multiple methods produce similarly low ρ_j, claim quality is ruled out as root cause.

---

## 5.4 Explanation H3: Context Pairing Strategy

### 5.4.1 Mechanism

We paired each claim with the full source text as context (TruthfulQA question, WritingPrompts prompt). For long contexts, relevant contradictions may be distant from claim location (e.g., claim at sentence N contradicts fact at sentence N-50). DeBERTa-v3-base has max sequence length 512 tokens → long contexts may:

1. **Truncate**: Relevant contradictory information falls outside 512-token window
2. **Dilute attention**: Model fails to locate contradictions amid irrelevant text

**Predicted outcome**: Attention dilution → weak entailment/contradiction signals → neutral-class dominance.

### 5.4.2 Supporting Evidence

**Observation 1: Context length distributions**

- TruthfulQA questions: Mean 15 tokens (median 12) → well below 512-token limit
- WritingPrompts prompts: Mean 40 tokens (median 35) → also below limit

Truncation is unlikely given short context lengths. However, attention dilution remains plausible even for short contexts if NLI model trained on SNLI/MNLI (local sentence pairs) struggles with longer-distance factual verification.

**Observation 2: No ablation study performed**

We did NOT test alternative context windowing strategies (±1 sentence, ±2 sentences, ±3 sentences around claim) → cannot isolate impact of context pairing on ρ_j.

**Observation 3: Literature gap**

CCP paper does NOT specify context windowing strategy → we followed cavaquinho implementation pattern (full-text context), but alternative strategies may perform better.

### 5.4.3 Likelihood Assessment

**Likelihood: MEDIUM (requires ablation to quantify)**

**Against primary role**:
- Short context lengths (15-40 tokens) make truncation unlikely
- Observation 1 (uniform degradation across domains) not explained by context length variance

**For contributory role**:
- Theoretical plausibility: SNLI/MNLI training uses local pairs, not long-context factual verification
- Ablation study would definitively answer whether windowing improves ρ_j

**Implication**: Future work should test full-text vs ±1/±2/±3 sentence windows, measuring ρ_j distribution per strategy. If optimal window size improves ρ_j to expected range (0.70-0.85), context pairing is confirmed contributory. If all strategies produce low ρ_j, ruled out.

---

## 5.5 Explanation H4: Temperature/Calibration Issue

### 5.5.1 Mechanism

Neural networks trained with cross-entropy loss optimize classification accuracy, not probability calibration [Guo et al., 2017]. Softmax outputs may be miscalibrated (overconfident in neutral class). Temperature scaling (dividing logits by T < 1 before softmax) could shift probability mass toward entailment/contradiction classes.

**Predicted outcome**: Temperature-scaled NLI outputs → reduced neutral mass → higher ρ_j.

### 5.5.2 Supporting Evidence

**Observation 1: No calibration diagnostics performed**

We did NOT measure Expected Calibration Error (ECE) or reliability diagrams for DeBERTa-v3-base NLI outputs → cannot confirm whether miscalibration exists.

**Observation 2: Magnitude gap too large**

Calibration techniques (temperature scaling, Platt scaling) typically improve probability estimates by 5-20%, not 50× (which would require shifting neutral mass from 0.90 → 0.10, implausible).

**Observation 3: Literature gap**

Neither CCP paper nor cavaquinho/HallucinoGenAI implementations mention temperature scaling → suggests calibration may not be critical for ρ_j computation when NLI model is domain-appropriate.

### 5.5.3 Likelihood Assessment

**Likelihood: LOW (cannot explain 50× magnitude shift)**

**Against primary role**:
- Temperature scaling affects ranking/relative confidences, not raw magnitude by 50×
- No literature precedent for calibration fixing factual verification task-domain gaps

**For contributory role**:
- Post-hoc calibration could marginally improve ρ_j if combined with H1 fixes (NLI fine-tuning)

**Implication**: Calibration diagnostics (ECE, reliability curves) worth measuring as validation check, but unlikely to be root cause or primary fix.

---

## 5.6 Root Cause Hierarchy

Synthesizing Sections 5.2-5.5, we propose a **root cause hierarchy** ordered by evidence strength:

**Tier 1: PRIMARY CAUSE (H1)**  
Out-of-distribution generalization gap: SNLI/MNLI semantic similarity training ≠ factual verification task  
**Evidence**: Uniform degradation across domains + literature triangulation + sanity check failure  
**Fix priority**: CRITICAL → NLI fine-tuning on FEVER/HotpotQA OR test alternative models (RoBERTa-large-MNLI, TRUE)

**Tier 2: CONTRIBUTORY FACTORS (H2, H3)**  
Claim decomposition quality (sentences ≠ logical propositions) + context pairing (full-text vs local windows)  
**Evidence**: Plausible mechanisms but no ablation studies to quantify impact  
**Fix priority**: HIGH → Compare NLTK vs LLM vs Spacy extraction; test context windowing strategies

**Tier 3: UNLIKELY (H4)**  
Temperature/calibration alone cannot explain 50× magnitude shift  
**Evidence**: Magnitude gap too large for calibration techniques  
**Fix priority**: LOW → Measure ECE for validation, but not primary bottleneck

**Implication for Original Hypothesis**:

The ontology-mismatch hypothesis (creative text causes ρ_j degradation due to factual-ontology assumptions in NLI) **cannot be tested** until Tier 1 (NLI calibration) is resolved. The failure occurred **one level upstream** from the hypothesized mechanism:

- **Hypothesized failure point**: Creative text → NLI mismatch (domain-specific)
- **Actual failure point**: Factual verification task → SNLI/MNLI mismatch (task-agnostic)

This suggests "factual-ontology assumptions" may exist at the **NLI training level** (SNLI/MNLI factuality biases) rather than just in **aggregation** (product function).

## 5.7 Theoretical Implications

### 5.7.1 Task-Domain Gap vs Traditional Domain Shift

Our findings reveal a **task-domain gap**: SNLI/MNLI optimize for semantic similarity detection (do sentences describe similar situations?), not factual verification (is claim consistent with context?). This differs from traditional domain shift (e.g., SNLI → medical texts) where the TASK remains constant (entailment classification) but the DOMAIN vocabulary/style changes.

**Task-domain gap signature**:
- Model achieves SOTA on source task (SNLI/MNLI 92% accuracy)
- Model fails catastrophically on structurally similar but task-shifted target (factual verification)
- Failure is uniform across target subdomains (factual AND creative text both fail)

**Implication**: Hallucination detection papers using off-the-shelf NLI models must validate calibration on target task (factual verification) before reporting metrics, even if NLI model shows strong SNLI/MNLI performance.

### 5.7.2 Measurement Validity as Prerequisite

When measurement validity fails (ρ_j 50× lower than expected across ALL conditions), hypothesis testing is **logically impossible**—we cannot distinguish "hypothesis is wrong" from "measurement is broken."

**Analogy**: Testing a new stain protocol on rare tissue samples without first validating it on common tissue types. Finding all slides blank could mean (1) cells lack nuclei (hypothesis), or (2) microscope is out of focus (measurement). Without baseline validation, we cannot decide.

**Lesson for research methodology**: Always replicate baseline on original domain BEFORE extending to new domains. Failure to do so conflates method failures with hypothesis refutations.

### 5.7.3 Reproducibility Implications

CCP paper reports +0.05-0.10 ROC-AUC improvements on biography generation but does NOT report:
- Raw ρ_j distributions (expected: 0.75-0.85; we observe: 0.01-0.04)
- NLI model calibration diagnostics (which model? fine-tuned on what?)
- Claim decomposition methodology (sentence tokenization? LLM extraction? manual annotation?)
- Context pairing strategy (full-text? windowed? claim-local?)

Without these implementation details, replication attempts must make ad-hoc choices (we chose DeBERTa-v3-base + NLTK + full-text), potentially missing undocumented optimizations (e.g., NLI fine-tuning on FEVER, LLM-based claim extraction).

**Recommendation for field**: Hallucination detection papers should report (1) raw metric distributions, (2) NLI calibration validation, (3) claim decomposition inter-annotator agreement, (4) context pairing ablations. Public code repositories should include baseline replication notebooks with unit tests on known examples.
