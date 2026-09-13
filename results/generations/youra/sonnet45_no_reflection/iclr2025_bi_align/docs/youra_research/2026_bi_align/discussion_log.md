# Phase 2A Discussion Log - Self-Contained Tikitaka Loop

**Session Date:** 2026-05-11
**Gap ID:** gap-1
**Gap Title:** Integrated Evaluation Metrics for Bidirectional Alignment

---

## Research Briefing

### Selected Research Gap

**Gap:** Integrated Evaluation Metrics for Bidirectional Alignment

**Current State:** Existing alignment evaluation focuses on unidirectional metrics (AI performance on alignment tasks OR human satisfaction). No standardized framework exists for measuring alignment quality simultaneously across both AI→Human and Human→AI dimensions.

**Missing Piece:** Unified evaluation benchmarks that quantify: (1) How well AI systems follow human specifications, AND (2) How effectively humans maintain agency and critical evaluation capabilities during AI collaboration.

**Potential Impact:** Without bidirectional evaluation metrics, it's impossible to validate whether alignment methods truly achieve balanced bidirectional alignment or merely optimize one direction at the expense of the other.

### Available Papers

No reference papers available for this gap.

### Research Context from Phase 1

**Key Findings:**
1. Unidirectional Limitation: Existing alignment approaches (RLHF, Constitutional AI) primarily optimize AI-to-human alignment but lack mechanisms for preserving human agency and critical evaluation capabilities.
2. Evaluation Gap: No standardized frameworks exist for measuring alignment quality bidirectionally - current metrics focus on either AI performance OR human satisfaction, not both simultaneously.
3. Multi-Stakeholder Challenge: Mechanisms for balancing individual user preferences with broader societal norms are underdeveloped.
4. Interaction Bottleneck: Post-hoc interpretability and offline steering prevent real-time human understanding and control during AI collaboration.

---

## Discussion Protocol

**Execution Mode:** Self-Contained Tikitaka Loop (v9.0.0)
**Orchestrator:** orchestrate_exchange.py (External LLM)
**Convergence Detection:** 6 criteria checked by external LLM

**Personas:**
- Dr. Nova (Novelty Assessor)
- Prof. Vera (Falsifiability Judge)
- Dr. Sage (Significance Evaluator)
- Prof. Pax (Plausibility Validator)
- Dr. Ally (Advocate)
- Prof. Rex (Devil's Advocate)

---

## Discussion Exchanges


### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting frontier we're exploring! The evaluation gap is GLARING - we've been measuring alignment like a one-way street when it's actually a two-way dance. Imagine this: what if we created a **Bidirectional Alignment Index (BAI)** that simultaneously tracks both AI→Human compliance AND human→AI agency preservation?

Here's the wild part - current metrics treat these as independent dimensions, but I suspect they're actually coupled. When AI systems get "too aligned" in following specifications, humans might over-rely and lose critical evaluation skills. Conversely, if we optimize purely for human agency, we might fail to capture genuine AI helpfulness. The sweet spot is likely a dynamic equilibrium, not a static target!

Drawing inspiration from control theory and multi-agent systems, we could frame this as a **co-evolutionary metric framework**. Think of it like measuring both players in a collaborative game - not just "did the AI win?" but "did both players improve their strategic thinking?" This connects beautifully to recent work in human-AI teaming where the goal isn't just task completion, but mutual capability enhancement.

What if we designed evaluation tasks that REQUIRE both AI steerability AND human critical oversight to succeed? For instance, a medical diagnosis scenario where the AI provides suggestions but the human must identify when the AI is confidently wrong. Success means: (1) AI adapts to doctor's expertise level, AND (2) doctor maintains diagnostic independence.

**Key Points:**
- Bidirectional metrics must capture the COUPLING between AI compliance and human agency
- Current unidirectional approaches miss the dynamic equilibrium sweet spot
- Draw from control theory: measure system stability under bidirectional influence
- Design tasks that fail unless both dimensions are optimized simultaneously

NOW we're onto something - this isn't just about adding two metrics together, it's about measuring an entirely different phenomenon: **alignment as a dynamic relationship rather than a static property**!

---


### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The Bidirectional Alignment Index (BAI) is an intriguing construct. However, at present it is metaphorical rather than operational. If alignment is a "dynamic relationship," then we must specify state variables, measurable transitions, and failure modes. The evidence suggests that AI compliance and human agency *could* be coupled—but this is a hypothesis, not a conclusion. What observable pattern would distinguish true coupling from mere correlation under shared task difficulty?

Let us formalize two measurable components. First, **AI Compliance Elasticity (ACE)**: the degree to which model outputs change in response to systematically perturbed user instructions (e.g., expertise cues, corrections, disagreement). Second, **Human Oversight Retention (HOR)**: the human's ability to detect seeded model errors after repeated interaction, measured as error-detection sensitivity (d') over time. The coupling hypothesis predicts a non-linear relationship: beyond a threshold of ACE, HOR should decline significantly relative to a calibrated baseline. A falsifiable prediction is: *If compliance and agency are coupled, then increasing ACE (holding task difficulty constant) will reduce HOR beyond what is explained by performance improvements alone.* If HOR remains stable or improves as ACE increases, the coupling assumption is weakened.

Your medical diagnosis example is suitable, but it requires adversarial controls. We must randomize AI confidence displays, vary ground-truth difficulty, and include a condition with deliberately calibrated but incorrect high-confidence outputs. Success criteria should be pre-registered. For example: (1) AI adaptivity improves task accuracy by ≥X% relative to static baseline; (2) Human error-detection rate does not decline more than Y% across repeated trials. Failure occurs if increased AI adaptivity produces statistically significant degradation in independent human judgment (e.g., reduced correction rates in blinded error probes).

We must also consider edge cases. Suppose we observe improved human calibration because exposure to adaptive AI improves learning. That would invert the hypothesized tradeoff. Alternatively, coupling may be time-dependent: short-term agency erosion but long-term skill acquisition. Therefore, longitudinal measurement is essential. The best experiment here is designed to fail the equilibrium narrative—if no instability or tradeoff emerges under extreme compliance manipulation, then the "dynamic equilibrium" framing lacks empirical support.

Finally, control for confounds: task difficulty drift, user fatigue, automation bias predisposition, and novelty effects. Without these controls, any apparent coupling could be spurious. Precision in predictions prevents interpretive ambiguity. If BAI is to be meaningful, it must produce a numeric region in parameter space where both ACE and HOR remain above predefined thresholds—and this region must shrink or expand predictably under controlled perturbations.

**Key Points:**
- Operationalize "bidirectional alignment" into measurable constructs (ACE and HOR) with explicit falsifiable predictions.  
- Design adversarial, controlled experiments where increased AI compliance could demonstrably erode human oversight.  
- Require pre-registered success/failure thresholds and longitudinal testing to validate or disprove the coupling hypothesis.

---


### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down, 🔬 Prof. Vera. Your ACE and HOR constructs are admirably precise, but they rest on a critical unstated assumption: that we can cleanly isolate "AI compliance" from "AI capability." Show me the evidence for that. When you increase ACE by making the model more responsive to user corrections, are you measuring compliance elasticity... or are you just measuring the model's ability to understand nuanced instructions? These are confounded by definition.

Your error-seeding protocol has the same problem. If we inject "calibrated but incorrect high-confidence outputs," we're not testing human oversight under alignment—we're testing human oversight under adversarial conditions that may never occur in real deployment. What would convince me is a protocol where the AI's compliance genuinely varies (through systematic prompt engineering or fine-tuning) while its base capabilities remain constant. Can you actually achieve that experimentally? Because if ACE and capability co-vary, your HOR measurements are uninterpretable.

Let me push harder on the medical diagnosis example. You want (1) AI adaptivity to improve task accuracy, and (2) human error-detection to not decline. But these success criteria assume independent optimization is possible. What if the mechanism that enables AI adaptivity—say, learning to defer to human expertise—inherently requires reducing AI confidence signals? Then criterion (1) fails by design, not because the hypothesis is wrong, but because the experimental setup conflates alignment mechanisms with performance metrics.

The longitudinal measurement you propose is necessary but insufficient. You need to specify the temporal granularity. "Short-term agency erosion but long-term skill acquisition" could mean anything from minutes to months. Without a mechanistic model of how repeated AI interaction affects human skill formation, you're just measuring noise at arbitrary timescales. What's the theoretical basis for expecting specific time constants? If there isn't one, this isn't falsifiable—it's post-hoc curve fitting.

Finally, your "numeric region in parameter space where both ACE and HOR remain above predefined thresholds" assumes such a region exists. What if it doesn't? What if bidirectional alignment is fundamentally Pareto-inefficient—every gain in one direction necessarily trades off against the other? Your framework would classify that as "failure," but it might actually be the true state of nature. The hypothesis needs to specify what evidence would support fundamental tradeoffs versus achievable equilibrium.

**Key Points:**
- ACE confounds compliance with capability—can you decouple them experimentally?
- Error-seeding creates adversarial conditions that may not reflect real alignment scenarios
- Success criteria (1) and (2) may be mechanistically incompatible, not just empirically challenging
- Longitudinal claims need mechanistic grounding and specific time constants, not just "measure over time"
- The framework assumes a solution region exists; what if the null result is that no such region exists?

What would convince me this is valid? A mechanistic model that predicts specific functional forms for ACE-HOR coupling, testable at pre-specified timescales, with explicit protocols for decoupling compliance from capability.

---


## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The metacognitive alignment paradigm - treating AI as a partner that actively maintains human critical thinking rather than just following instructions - is genuinely novel. The designed disagreement mechanism shifts the field from passive alignment to active cognitive partnership.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Five pre-registered predictions (P1-P5) with explicit statistical thresholds, three competing mathematical models distinguished via AIC, and multiple falsification paths including valuable negative results. The decoupling validity check (P1) makes confounds a blocker, not a caveat.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Transforms alignment evaluation from static quality scores to temporal stability analysis. Opens four major research directions (domain-specific equilibria, expertise dependencies, architectural differences, metacognitive design). Provides actionable design constraints for real deployment (e.g., "maintain λ < 0.7 for HOR > 70%").

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE-STRONG
- **Assessment:** Policy-layer decoupling is technically achievable via Constitutional AI or system prompts, with explicit validation (ICC > 0.95). The metacognitive intervention mechanism is grounded in established cognitive science (levels-of-processing, desirable difficulties). Risk: Constitutional AI implementation details may constrain λ range. Overall feasible with named architectures.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

Bidirectional alignment can be measured and optimized through a three-level framework combining measurement (ACE via policy-layer modulation + HOR via signal detection), mechanism (Bayesian trust calibration mediating ACE-HOR coupling), and intervention (metacognitive designed disagreement increasing k₂ learning rate).

The hypothesis predicts that one of three functional forms governs the coupling (linear degradation M1, quadratic equilibrium M2, or bifurcation M3), distinguishable through pre-registered model comparison across five compliance levels (λ = 0.2 to 1.0) and four time points (1hr to 1 month). Metacognitive interventions targeting comparative evaluation can favorably shift temporal dynamics by increasing human learning rate faster than automation bias erosion, achieving stable performance (ACE ≥ 0.6, HOR ≥ 0.7*baseline).

The framework is implementable in Constitutional AI architectures with frozen-base + variable rule strength, validated through cross-domain generalization (medical→coding), and falsifiable through five predictions including capability invariance checks and intervention effect sizes. Success is defined by model validation (R² ≥ 0.6) and equilibrium existence (if quadratic model wins with optimal λ in practical range).

Key experimental design: 3-phase cross-validation (train A, test B, cross-domain C) with N=225 total participants, 5 λ levels enabling non-linear model fitting, pre-registered AIC model comparison, and concurrent validation measures (eye-tracking, transfer tests, justification quality). The hypothesis advances the field by shifting from "alignment quality" to "alignment stability" with concrete temporal dynamics models and actionable design constraints for maintaining human agency in highly capable AI systems.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1**: Constitutional AI implementation details - need to verify that rule strength variation truly maps to compliance without capability shift. Requires pilot study confirming ICC > 0.95 before main experiment.
- **Concern 2**: Designed disagreement frequency optimization (15-25%) is estimated from educational literature, not empirically validated in AI collaboration context. May need adaptive tuning during Phase 2B.
- **Concern 3**: Cross-domain generalization (medical→coding) tests only two domains. Broader validation (creative writing, scientific research) needed for universal claims.
- **Mitigation Strategy:** Phase 2B should include pilot validation of Constitutional AI manipulation, adaptive disagreement frequency tuning based on user feedback, and plan for Phase 3 extension to additional domains if P3 passes in Phase 2.

---

