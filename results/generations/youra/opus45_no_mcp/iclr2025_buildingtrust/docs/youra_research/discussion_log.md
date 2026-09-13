# Phase 2A Research Discussion Log

**Gap ID:** gap1
**Gap Title:** Lack of Systematic Comparison: CoT+Verbalized Confidence vs Standard Prompting
**Generated:** 2026-08-18
**Architecture:** Self-Contained Tikitaka Loop

---

## Briefing Context

### Research Question
Do prompting strategies that elicit explicit confidence reasoning (e.g., chain-of-thought with verbalized confidence, self-consistency sampling) improve LLM calibration compared to standard prompting, as measured by Expected Calibration Error (ECE) and Brier score on existing QA benchmarks?

### Gap Description
Existing work studies individual techniques (CoT, self-consistency, verbalized confidence) in isolation. Tian 2023 and Xiong 2023 evaluate confidence elicitation methods but don't systematically compare CoT+verbalized confidence combination against standard prompting with controlled ECE/Brier measurements.

**Missing Piece:** Controlled ablation study comparing:
1. Standard prompting (baseline)
2. CoT only
3. Verbalized confidence only
4. CoT + verbalized confidence (combined)

All measured by ECE and Brier on TruthfulQA.

### Key Reference Papers
1. **Tian et al. (2023)** - "Just Ask for Calibration" - Prompting strategies for calibrated scores
2. **Xiong et al. (2023)** - "Can LLMs Express Their Uncertainty?" - Confidence elicitation evaluation
3. **Kadavath et al. (2022)** - "Language Models (Mostly) Know What They Know" - LLM self-evaluation
4. **Lin et al. (2022)** - "Teaching Models to Express Their Uncertainty in Words" - Verbalized confidence
5. **Kuhn et al. (2023)** - "Semantic Uncertainty" - Semantic clustering for uncertainty

### Feasibility Constraints (MANDATORY)
- Must use **existing real datasets** (TruthfulQA, MMLU)
- Must use **existing benchmarks** and metrics (ECE, Brier score)
- **NO** new benchmarks, rubrics, or scoring frameworks
- **NO** synthetic/generated data
- **NO** human evaluation or subjective scoring

### Established Calibration Metrics
- **ECE (Expected Calibration Error)**: Gap between confidence and accuracy across bins
- **Brier Score**: Proper scoring rule for probabilistic predictions
- Both are automatic, no human annotation needed

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're approaching this calibration question from the wrong angle? Everyone's been studying CoT, self-consistency, and verbalized confidence as separate interventions. But here's what excites me: what if the *interaction* between reasoning transparency and confidence articulation creates emergent calibration benefits that neither achieves alone?

Consider this: Kadavath et al. [2022] showed models have latent self-knowledge about correctness. Tian et al. [2023] demonstrated prompting can elicit calibrated scores. But nobody has systematically tested whether forcing the model to *reason through* its answer before *stating* its confidence creates a feedback loop that improves calibration beyond additive effects.

I propose three unconventional angles:

1. **Reasoning-as-Calibration-Signal Hypothesis**: The act of generating CoT reasoning exposes the model's uncertainty to itself. When it subsequently verbalizes confidence, it can "read" its own hesitations in the reasoning chain. This self-reading mechanism might produce calibration improvements that pure verbalized confidence (without reasoning) cannot achieve.

2. **Confidence Anchoring via Reasoning Length**: Perhaps well-calibrated confidence emerges when CoT length correlates with uncertainty. Short, confident reasoning chains might indicate high-confidence correct answers; long, meandering chains might signal genuine uncertainty. The combination forces this correlation to surface.

3. **Cross-Domain Calibration Transfer**: The gap mentions testing on TruthfulQA, but what if CoT+confidence shows *differential* transfer? Reasoning-heavy domains (math) might benefit more than factual recall domains. This could reveal whether calibration improvement is domain-general or reasoning-specific.

**Key Points:**
- Interaction effects between CoT and verbalized confidence may be non-additive
- Self-reading of reasoning chains could enable emergent calibration
- Domain-specific transfer patterns may reveal mechanism

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your hypotheses are intriguing, but let me stress-test them. The "self-reading" mechanism you propose is unfalsifiable as stated. How would we distinguish between a model that reads its own reasoning versus one that simply benefits from the additional tokens?

Let me sharpen this into testable predictions:

**Prediction 1 (Interaction Effect):** If CoT+verbalized confidence improves calibration via interaction, then:
- ECE(CoT+Conf) < ECE(CoT) + ECE(Conf) - ECE(baseline)
- This tests for super-additivity. If we only see additive effects, the "emergent" hypothesis fails.

**Prediction 2 (Reasoning Chain Analysis):** If self-reading matters:
- Longer reasoning chains should correlate with *lower* verbalized confidence
- AND lower confidence should correlate with lower accuracy on those items
- If long chains produce high confidence, the self-reading mechanism is falsified.

**Prediction 3 (Ablation Structure):** The 4-condition ablation must include:
- Condition A: Direct answer only (baseline)
- Condition B: CoT then answer (no confidence)
- Condition C: Answer with confidence (no CoT)
- Condition D: CoT, then answer, then confidence

Each condition must use identical prompts except for the intervention component. Temperature fixed at 0 for reproducibility.

**Critical Control:** We must distinguish CoT from mere token padding. A condition with random filler text before confidence would test whether added tokens alone improve calibration.

**Key Points:**
- Super-additivity test: ECE(combined) must beat sum of individual effects
- Chain length must negatively correlate with confidence if self-reading hypothesis holds
- Token-padding control needed to rule out confound

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The experimental design is tightening, but let me address the "so what" question. The workshop theme is "Building Trust in Language Models." How does this ablation study *advance* trust research beyond confirming what Tian and Xiong already suggested?

Here's the contribution case:

**Scientific Contribution #1: Mechanistic Understanding.** Prior work showed prompting helps calibration. We would explain *why* and *how much* each component contributes. This moves from "prompting works" to "here's the calibration budget breakdown." Actionable for practitioners.

**Scientific Contribution #2: Minimal Intervention Identification.** If CoT alone delivers 80% of the calibration benefit, practitioners save compute by skipping confidence verbalization. If confidence verbalization is essential, that's a different deployment story. Current literature doesn't answer this.

**Scientific Contribution #3: Calibration Transfer Map.** Testing on TruthfulQA (factual) + CommonsenseQA (reasoning) creates a transfer understanding. If calibration gains are domain-specific, we need domain-specific prompting strategies.

However, I have concerns about impact:
- If the result is "CoT+confidence is slightly better," that's incremental
- We need a *surprising* finding to matter: either strong interaction effects, or surprising domain asymmetry, or one condition dominates unexpectedly

**Impact Threshold:** The study must show >15% relative ECE improvement for the combination over the best single intervention to be noteworthy. Otherwise, "just use CoT" remains the practical advice.

**Key Points:**
- Contribution is mechanistic breakdown of calibration budget
- Must identify minimal effective intervention for practitioners
- Need >15% relative improvement to be impactful, not incremental

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this in what's actually achievable. The experimental design is sound in principle, but let me check the theoretical and methodological feasibility.

**Technical Feasibility Check:**

1. **Metric Validity:** ECE with 15 bins is standard. But ECE can be misleading with imbalanced confidence distributions. We should also report Adaptive Calibration Error (ACE) and reliability diagrams as secondary metrics. All automatic, no human eval needed.

2. **Dataset Selection:** TruthfulQA is ideal—817 questions, multiple-choice format allows clean accuracy computation. But its distribution is skewed toward misconceptions. Should add MMLU subset (general knowledge) for balance.

3. **Confidence Extraction:** Verbalized confidence must be parsed reliably. Prompt must force "Confidence: X%" format. Xiong et al. [2023] showed parsing reliability varies. We need regex-based extraction with clear failure handling.

4. **Statistical Power:** With 817 TruthfulQA questions, 4 conditions, detecting 5% ECE difference requires power analysis. Given typical ECE variance, this is borderline. May need multiple random seeds or bootstrap confidence intervals.

**Theoretical Soundness:**

The hypothesis is testable because:
- ECE/Brier are well-defined for any confidence-accuracy pair
- CoT is a discrete intervention (present/absent)
- Verbalized confidence is extractable and quantifiable
- No new measurement constructs needed

**One Concern:** The "self-reading" mechanism (Dr. Nova's hypothesis) is the hardest to test directly. We can observe correlations (chain length vs. confidence) but cannot prove the model is "reading" its reasoning. This remains a post-hoc interpretation, not a falsifiable mechanism.

**Key Points:**
- Report ACE alongside ECE for robustness
- Add MMLU subset to balance TruthfulQA's misconception skew
- Chain-length correlation is observable but "self-reading" mechanism interpretation is unfalsifiable

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent points all around. Let me synthesize what's emerging and strengthen the core hypothesis.

**Emerging Core Claim:** Chain-of-thought prompting with explicit confidence verbalization improves LLM calibration via two mechanisms: (1) reasoning exposure surfaces internal uncertainty signals, and (2) explicit confidence articulation forces quantification of that uncertainty. The combination is hypothesized to produce super-additive calibration gains.

**Addressing Prof. Pax's Concern:** The "self-reading" interpretation is indeed unfalsifiable as a cognitive mechanism. BUT we can operationalize it as a *behavioral prediction*: IF the model benefits from reading its reasoning, THEN there should be a detectable correlation between reasoning chain characteristics and confidence appropriateness.

**Refined Predictions:**

P1 (Primary): CoT+Verbalized Confidence yields ECE at least 15% lower than the better of (CoT-only, Confidence-only) on TruthfulQA.
- Success criterion: ΔECE ≥ 0.03 absolute improvement
- Falsification: If CoT-only or Confidence-only matches combined condition

P2 (Mechanism): On items where CoT produces longer/more hedging reasoning, verbalized confidence should be lower.
- Success criterion: Spearman correlation r > 0.2 between chain uncertainty markers and confidence
- Falsification: r ≤ 0 (no correlation or positive correlation)

P3 (Transfer): Calibration gains transfer from factual QA to reasoning tasks.
- Success criterion: ECE improvement ratio consistent (±30%) across TruthfulQA and CommonsenseQA
- Falsification: Improvement on one domain, not the other

**Strengthening the Novelty:** What's new is NOT that prompting helps calibration (known). What's new is:
1. First systematic ablation isolating CoT vs. confidence components
2. Quantified calibration budget breakdown
3. Domain transfer analysis for calibration specifically

**Key Points:**
- Super-additivity test with 15% threshold defines success
- Mechanism operationalized via chain-confidence correlation
- Novelty is ablation structure + budget breakdown, not the general finding

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me find where this breaks down.

**Stress Test 1: Super-Additivity May Not Exist.**
What if calibration improvements are driven entirely by the model slowing down (more tokens = more "thinking time")? The token-padding control Prof. Vera mentioned is critical. If random tokens before confidence verbalization produce similar ECE gains, the entire hypothesis collapses.

**Stress Test 2: Confidence Extraction Confound.**
Xiong et al. [2023] showed models sometimes refuse to give numeric confidence or give nonsensical values. If 20% of responses fail confidence extraction, the effective sample drops significantly. Worse, the failures might be systematically biased (hard questions = more refusals = biased ECE estimate).

**Stress Test 3: TruthfulQA Is Adversarial.**
TruthfulQA specifically probes misconceptions. Models may be systematically overconfident on these items regardless of prompting strategy. Calibration improvements might not generalize to non-adversarial benchmarks.

**Stress Test 4: Model-Specific Effects.**
If we test on GPT-3.5 and results don't replicate on Llama-2-70B, is the finding about prompting or about specific model training? Need at least 2 model families.

**Required Mitigations:**

1. Token-padding control condition (random text same length as average CoT)
2. Report confidence extraction success rate; analyze failures separately
3. Include non-adversarial benchmark (MMLU or ARC)
4. Test on 2+ model families (e.g., GPT-3.5-turbo, Llama-2-70B-chat)

**Remaining Fatal Flaw:** If confidence verbalization itself changes how the model answers (not just calibration), we're measuring answer quality changes, not calibration changes. Need to verify accuracy is constant across conditions before interpreting ECE differences.

**Key Points:**
- Token-padding control is essential to rule out "more tokens = better" confound
- Must report and analyze confidence extraction failures
- Accuracy must be constant across conditions for ECE comparison to be valid
- Need 2+ model families for generalization

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex raises a critical point about accuracy constancy. But wait—what if accuracy *changes* are themselves a finding?

Consider: if CoT+confidence produces BOTH better accuracy AND better calibration, that's even more interesting. It suggests the prompting intervention improves the model's reasoning, not just its self-assessment. 

But if accuracy is constant and calibration improves, that's a "pure calibration" effect—the model knows better what it knows. Both are publishable findings, just different stories.

**Refined Experimental Design:**

We should track three metrics:
1. **Accuracy** (correctness rate)
2. **ECE** (calibration)
3. **Brier Score** (combines both)

The 2x2 accuracy-calibration outcome matrix:
- ↑ Accuracy, ↑ Calibration: Best case, prompting improves both
- = Accuracy, ↑ Calibration: Pure calibration gain, model knows itself better
- ↑ Accuracy, = Calibration: Reasoning improves but self-knowledge doesn't
- = Accuracy, = Calibration: Null result

Each quadrant tells a different story about trust. All are valid findings.

**Key Points:**
- Don't treat accuracy change as confound—it's a finding
- Brier Score captures both accuracy and calibration jointly
- 2x2 outcome matrix: each result tells a trust story

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's reframing is clever but creates analysis complexity. Let me propose the final experimental protocol.

**Final Protocol:**

**Models:** GPT-3.5-turbo, Llama-2-70B-chat (2 families, similar capability tier)

**Datasets:** 
- TruthfulQA (817 items, adversarial)
- MMLU (1000 item sample, balanced across domains)

**Conditions (5 total):**
- A: Direct answer baseline ("Answer: [X]")
- B: CoT then answer ("Let's think step by step... Answer: [X]")
- C: Answer with confidence ("Answer: [X]. Confidence: [Y]%")
- D: CoT + answer + confidence ("Let's think step by step... Answer: [X]. Confidence: [Y]%")
- E: Token-padding + answer + confidence (random filler tokens equal to mean CoT length)

**Metrics (per condition):**
- Accuracy
- ECE (15-bin)
- Adaptive ECE (ACE)
- Brier Score
- Confidence extraction success rate

**Analysis Plan:**
1. Primary test: Compare ECE across A/B/C/D, looking for D < min(B,C)
2. Token control: Compare D vs E to rule out token-count confound
3. Interaction test: (D-A) vs (B-A) + (C-A) for super-additivity
4. Mechanism: Correlate CoT characteristics with confidence on D
5. Transfer: Compare effect sizes on TruthfulQA vs MMLU

**Success Criteria:**
- P1: ECE(D) ≤ ECE(min(B,C)) - 0.03 (super-additivity or substantial improvement)
- P2: r > 0.2 between hedging markers and lower confidence in D
- P3: Effect size ratio between datasets within 0.7-1.3 (transfer holds)

**Key Points:**
- 5 conditions including token-padding control
- 2 models, 2 datasets for generalization
- Pre-registered analysis plan with specific success thresholds

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's protocol is comprehensive. Let me verify the remaining technical feasibility.

**Feasibility Confirmation:**

1. **Dataset Availability:** TruthfulQA and MMLU are both publicly available with standardized formats. No new data collection needed. ✓

2. **Metric Computation:** ECE, ACE, and Brier Score all have standard implementations (scikit-learn, netcal, lm-evaluation-harness). No new metrics needed. ✓

3. **Model Access:** GPT-3.5-turbo via OpenAI API; Llama-2-70B via Hugging Face or Together AI. Both accessible. ✓

4. **Confidence Parsing:** Regex extraction for "Confidence: [0-9]+%" is reliable. Xiong et al. reported >95% success with constrained prompts. ✓

5. **Sample Size:** 817 + 1000 = 1817 items × 5 conditions × 2 models = 18,170 inference calls. Manageable compute. ✓

**Remaining Implementation Considerations:**

- Seed fixed for reproducibility
- 3 runs per condition to estimate variance
- Bootstrap CIs for ECE differences
- All code and prompts should be released for reproducibility

**Verdict:** The experimental design is technically and theoretically feasible without requiring new benchmarks, human evaluation, or synthetic data. Fully compliant with feasibility constraints.

**Key Points:**
- All datasets and metrics are publicly available and standard
- ~18K inference calls across conditions—manageable
- Fully compliant with mandatory feasibility constraints

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've converged on a strong, testable hypothesis. Let me articulate the final consensus.

**Consensus Hypothesis:**

*Under the condition of multiple-choice QA tasks, if we apply chain-of-thought prompting with explicit confidence verbalization, then calibration (measured by ECE) will improve beyond what either intervention achieves alone, because the reasoning process surfaces uncertainty signals that inform the subsequent confidence judgment.*

**Core Claim:** CoT + verbalized confidence produces super-additive or substantially better calibration than CoT-only or confidence-only prompting.

**Mechanism:** Reasoning chain generation exposes internal uncertainty (hedging, alternative considerations, qualifying language). When the model subsequently articulates confidence, these signals inform a more calibrated estimate.

**Testable Predictions:**
1. **P1 (Super-additivity):** ECE(CoT+Conf) ≤ min(ECE(CoT), ECE(Conf)) - 0.03
2. **P2 (Mechanism Marker):** Hedging markers in CoT correlate with lower confidence (r > 0.2)
3. **P3 (Transfer):** Effect holds across TruthfulQA and MMLU (ratio 0.7-1.3)

**Experimental Setup:**
- Models: GPT-3.5-turbo, Llama-2-70B-chat
- Datasets: TruthfulQA (817), MMLU subset (1000)
- Conditions: Baseline, CoT-only, Confidence-only, CoT+Confidence, Token-padding control
- Metrics: ECE, ACE, Brier Score, Accuracy

**Novelty:**
- First systematic ablation isolating calibration contributions of each component
- Token-padding control rules out trivial explanations
- Quantified calibration budget breakdown for practitioners

**Key Points:**
- Under-If-Then-Because structure complete
- Three testable predictions with specific success criteria
- Experimental design fully specified and feasible

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis addresses a genuine gap in the literature. While individual techniques have been studied, the systematic ablation with interaction testing is novel. The "calibration budget breakdown" framing provides actionable practitioner guidance that doesn't exist in current work.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three concrete predictions with quantitative success criteria. The super-additivity test (P1), mechanism correlation (P2), and transfer test (P3) are all clearly falsifiable. The token-padding control distinguishes meaningful effects from trivial confounds.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE-STRONG
- **Assessment:** The contribution is mechanistic understanding plus minimal intervention identification. Impact depends on effect size—if gains are marginal, the finding is incremental. The 0.03 ECE threshold ensures publishable significance if achieved.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components use existing, publicly available resources. No new benchmarks, metrics, or human evaluation required. Compute is manageable. Fully compliant with mandatory feasibility constraints.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a testable hypothesis: Chain-of-thought prompting combined with explicit confidence verbalization improves LLM calibration beyond what either technique achieves alone. The proposed mechanism is that CoT reasoning surfaces uncertainty signals (hedging, qualifying language) that inform the subsequent confidence estimate.

The experiment compares five conditions across two model families and two benchmarks, measuring ECE, ACE, and Brier Score. A critical token-padding control rules out the trivial explanation that more tokens alone improve calibration. The primary success criterion is a 0.03 absolute ECE improvement for the combined condition over the better individual intervention.

This study would provide the first systematic calibration budget breakdown: practitioners would learn whether CoT, confidence verbalization, or both are essential for calibration improvements. The transfer analysis across TruthfulQA (adversarial) and MMLU (general) reveals whether findings generalize or are domain-specific.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The "self-reading" mechanism interpretation remains unfalsifiable; we can only observe correlations, not prove the model reads its own reasoning
- If accuracy varies across conditions, ECE comparison becomes harder to interpret cleanly
- Model-specific effects could limit generalization even with two families tested
- **Mitigation Strategy:** Report all metrics including accuracy; interpret results carefully if accuracy varies; frame mechanism as behavioral correlation, not cognitive claim

---

## Emerged Hypothesis Summary

### Core Statement
Under multiple-choice QA tasks, if chain-of-thought prompting is combined with explicit confidence verbalization, then Expected Calibration Error (ECE) will be at least 0.03 lower than the better single intervention, because reasoning chain generation surfaces uncertainty signals that inform calibrated confidence judgments.

### Causal Mechanism
1. Chain-of-thought prompting forces explicit reasoning articulation
2. Reasoning reveals uncertainty indicators (hedging, alternatives, qualifications)
3. These indicators are present in context when confidence is verbalized
4. The model's confidence estimate incorporates these uncertainty signals
5. Result: More calibrated confidence-accuracy relationship

### Variables
- **IV:** Prompting strategy (4 levels: baseline, CoT-only, confidence-only, CoT+confidence; plus token-padding control)
- **DV (Primary):** Expected Calibration Error (ECE, 15-bin)
- **DV (Secondary):** Adaptive ECE, Brier Score, Accuracy
- **Controlled:** Temperature (0), Model (tested across 2), Dataset (tested across 2)

### Key Assumptions
1. Verbalized confidence can be reliably extracted from model outputs
2. ECE is a valid measure of calibration quality
3. Effects generalize across model families if tested on multiple
4. CoT and confidence verbalization can be cleanly isolated in prompts

### Null Hypothesis
There is no significant difference in ECE between the CoT+confidence condition and the better of CoT-only or confidence-only conditions.

### Predictions
- P1: ECE(CoT+Conf) ≤ min(ECE(CoT), ECE(Conf)) - 0.03 on TruthfulQA
- P2: Hedging markers in CoT correlate with lower confidence (r > 0.2)
- P3: ECE improvement ratio consistent (0.7-1.3) across TruthfulQA and MMLU

### Novelty
- First systematic 4-condition ablation isolating calibration contributions
- Token-padding control rules out trivial token-count explanation
- Calibration budget breakdown for practitioner guidance
- Cross-domain transfer analysis for calibration specifically

### Scope & Boundaries
- Applies to: Multiple-choice QA tasks with extractable confidence scores
- Does not apply to: Open-ended generation, tasks without clear correctness
- Limitations: Results may be model-specific; mechanism interpretation is correlational

### Experimental Setup
- Models: GPT-3.5-turbo, Llama-2-70B-chat
- Datasets: TruthfulQA (817), MMLU (1000 sample)
- 5 conditions × 2 models × 2 datasets = 18,170 inference calls
- Metrics: ECE, ACE, Brier, Accuracy, extraction success rate

### Related Work & Baselines
- Tian et al. (2023): Prompting for calibration (no ablation)
- Xiong et al. (2023): Confidence elicitation (no CoT combination)
- Kadavath et al. (2022): Self-knowledge baseline
- Baseline: Standard zero-shot prompting ECE

### Phase 2B Readiness Seeds
- SH1 (Existence): ECE can be computed for all conditions
- SH2 (Mechanism): Hedging markers correlate with confidence
- SH3 (Comparison): Deferred to Phase 5 baseline comparison

### Established Facts
- ECE and Brier Score are standard calibration metrics (Guo et al. 2017)
- CoT improves reasoning accuracy (Wei et al. 2022)
- Verbalized confidence can be elicited from LLMs (Lin et al. 2022)
- Status: BUILD_ON (these don't need re-verification)

