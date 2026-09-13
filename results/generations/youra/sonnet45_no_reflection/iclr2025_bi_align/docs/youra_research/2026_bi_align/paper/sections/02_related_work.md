# Related Work

Our framework integrates three research areas—AI alignment evaluation, automation bias from human factors, and signal detection theory—that have not been previously unified for bidirectional measurement. We position our work as the first to measure alignment-oversight coupling as a joint phenomenon rather than treating AI performance and human behavior as separate concerns.

## AI Alignment Evaluation

Modern alignment approaches focus on making AI systems conform to human values and preferences. RLHF (Reinforcement Learning from Human Feedback) trains language models to maximize human preference rankings, demonstrated effectively in InstructGPT [@Ouyang2022InstructGPT] and subsequent LLMs [@OpenAI2023GPT4; @Anthropic2024Claude3]. Constitutional AI extends this by training models to follow explicit constitutional principles, enabling principle-guided behavior without per-instance human feedback [@Bai2022ConstitutionalAI]. Red teaming and adversarial evaluation test alignment robustness by attempting to elicit harmful outputs [@Perez2022RedTeaming; @Ganguli2022RedTeamingLM].

However, these evaluation frameworks are fundamentally *unidirectional*: they measure whether AI outputs match human preferences (helpfulness, harmlessness, honesty scores) without measuring reciprocal effects on human oversight behavior. The implicit assumption is that optimizing the model's behavior is sufficient [@Amodei2016ConcreteProblems]. Human-in-the-loop systems are studied separately in human-computer interaction and human factors research, not integrated into alignment evaluation frameworks. **Limitation:** Cannot detect if alignment interventions inadvertently degrade human oversight quality through automation bias or trust miscalibration—the very phenomenon we aim to measure.

Our framework differs by treating alignment strength (ACE) and oversight quality (HOR) as coupled dependent variables. We leverage Constitutional AI's policy-layer architecture [@Bai2022ConstitutionalAI] but measure its effects bidirectionally: not just "does compliance improve?" but "does compliance improvement affect oversight?"

## Automation Bias and Trust in Human-Automation Interaction

Human factors research has extensively documented *automation bias*—the tendency for humans to over-rely on automated decision aids, reducing oversight effort and error detection sensitivity [@Parasuraman1997AutomationBias; @Skitka1999AutomationBias]. This phenomenon has been observed across domains including aviation [@Mosier2015Automation], medical diagnosis [@Goddard2012AutomationMedical], and process control [@Lee2004TrustAutomation]. The underlying mechanism is Bayesian trust calibration: humans rationally reduce verification effort when automation appears reliable, but this trust can be miscalibrated when reliability perceptions diverge from objective accuracy [@Lee2004TrustAutomation].

Signal detection theory provides a framework for measuring oversight quality via sensitivity (d') and response criterion (c), separating error detection ability from decision thresholds [@Swets1964SignalDetection; @Green1966SignalDetection]. This has been applied to vigilance tasks [@Parasuraman2009Vigilance], quality control inspection [@Wickens2015EngineeringPsychology], and security screening, but not to AI collaboration contexts where the "automation" can be dynamically modulated.

**Limitation:** This literature focuses on *traditional automation* where capability is static (e.g., autopilot algorithms, diagnostic decision aids). It does not address AI systems where compliance can be modulated independently of capability via policy-layer interventions. Existing studies cannot test whether automation bias mechanisms generalize to AI collaboration contexts, nor do they provide experimental protocols for varying compliance strength while holding capability constant.

Our framework operationalizes automation bias mechanisms (Bayesian trust calibration, verification effort reduction) in AI contexts by using Constitutional AI's architectural separation [@Bai2022ConstitutionalAI] to vary compliance (λ parameter) while freezing base capability (ICC > 0.95 validation). We measure HOR via signal detection d' on seeded within-distribution errors, adapting human factors methodology to AI collaboration.

## Capability Evaluation and Benchmarking

MMLU (Massive Multitask Language Understanding) evaluates language models across 57 subjects from elementary to professional knowledge domains [@Hendrycks2021MMLU], serving as a standard capability benchmark. HumanEval tests code generation via 164 hand-written programming problems [@Chen2021HumanEval], measuring functional correctness (pass@k metrics). These benchmarks enable cross-model comparisons and track capability improvements over time [@Liang2023HELM; @Srivastava2023BeyondImitationGame].

**Limitation:** Capability evaluation is separate from alignment evaluation in current practice. Alignment interventions (RLHF, Constitutional AI) are assumed to improve alignment without degrading capability, but this is rarely tested statistically. Confounding between alignment and capability changes makes it impossible to attribute human oversight effects specifically to alignment strength.

Our framework uses MMLU and HumanEval not just for capability measurement, but for *capability invariance testing*: we verify that policy-layer modulation maintains ICC > 0.95, ANOVA p > 0.05, and Cohen's f < 0.10 across compliance conditions. This architectural separation is a prerequisite for isolating ACE's effect on HOR. If capability varies with λ, ACE-HOR coupling measurements would be confounded and uninterpretable—our h-e1 gate enforces this validity check.

## Positioning: The Gap We Address

No existing work integrates these three areas—AI alignment architecture, human factors automation bias, and signal detection measurement—into a unified bidirectional evaluation framework. Alignment research measures AI performance; human factors research measures human oversight in traditional automation; capability benchmarks measure model ability. We are the first to:

1. Operationalize alignment strength and oversight quality as *coupled variables* (ACE and HOR)
2. Leverage architectural separation (Constitutional AI policy layer) to enable capability-invariant compliance manipulation
3. Apply signal detection d' to measure oversight degradation in AI collaboration contexts
4. Design experimental protocols with explicit falsification criteria (ICC > 0.95 gate for prerequisite validity)
5. Integrate automation bias mechanisms (Bayesian trust calibration) into AI alignment evaluation

This integration addresses a foundational measurement gap: alignment evaluation has been unidirectional because the tools to measure bidirectional effects did not exist. Our framework provides those tools.
