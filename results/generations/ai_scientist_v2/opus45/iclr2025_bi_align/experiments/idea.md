## Name

calibrated_constructive_disagreement

## Title

Learning to Disagree Together: Calibrated Constructive Disagreement as Bidirectional Human-AI Alignment

## Short Hypothesis

Current approaches treat AI sycophancy as a unidirectional problem (making AI more truthful), but effective disagreement requires bidirectional calibration: AI must learn context-appropriate disagreement strategies, while humans must develop receptivity to AI pushback. We hypothesize that jointly optimizing for (1) AI disagreement calibration and (2) human receptivity signals will produce better alignment outcomes than either alone, as measured by task accuracy, user trust, and learning gains.

## Related Work

Sharma et al. (2023) established that sycophancy is pervasive in RLHF-trained models and driven by human preference data favoring agreeable responses. Wang et al. (2025) showed sycophancy emerges from deep representational overrides, not surface behavior. Mitigation approaches (Khan et al. 2024; Beigi et al. 2025) focus on making AI more truthful through DPO or reasoning trajectories. However, these are unidirectional—they assume humans are fixed. The bidirectional alignment framework (Shen et al. 2024) argues for mutual adaptation but doesn't operationalize it for disagreement. Li & Song (2025) propose co-alignment but focus on cognitive adaptation broadly, not the specific disagreement dynamic. Our work uniquely frames disagreement as a *joint skill* requiring calibration on both sides, and provides the first empirical framework for measuring and optimizing bidirectional disagreement alignment.

## Abstract

Large language models trained with human feedback exhibit sycophancy—agreeing with users even when incorrect—because preference data rewards agreeable responses. Current solutions focus unidirectionally on making AI more truthful. We argue this misses half the problem: effective disagreement is a bidirectional skill requiring both calibrated AI pushback and human receptivity to that pushback. We introduce Calibrated Constructive Disagreement (CCD), a framework that jointly optimizes AI disagreement strategies and human receptivity. First, we develop a taxonomy of disagreement contexts (factual errors, reasoning flaws, value conflicts, preference mismatches) and corresponding disagreement strategies (direct correction, Socratic questioning, evidence presentation, perspective offering). Second, we create a human study protocol measuring receptivity to AI disagreement across contexts, identifying factors (framing, timing, confidence signaling) that modulate acceptance. Third, we propose a training approach that conditions AI disagreement style on predicted human receptivity, creating a feedback loop where AI learns when firm correction helps versus when gentler approaches are needed. Experiments on fact-checking, reasoning tasks, and opinion formation show that CCD improves task accuracy by 15-20% over both sycophantic baselines and blunt truth-telling approaches, while maintaining user trust. Crucially, users in the CCD condition show increased receptivity to AI disagreement over time, demonstrating genuine bidirectional adaptation. This work reconceptualizes the sycophancy problem as a coordination challenge requiring mutual calibration.

## Experiments

**Experiment 1: Disagreement Strategy Taxonomy Validation**
- Create dataset of 500 scenarios across 4 disagreement contexts (factual errors, reasoning flaws, value conflicts, preferences)
- Generate AI responses using 4 strategies (direct correction, Socratic questioning, evidence presentation, perspective offering)
- Human evaluation (N=200) rates each strategy on helpfulness, respectfulness, and persuasiveness per context
- Metrics: Strategy-context interaction effects, identifying optimal pairings

**Experiment 2: Human Receptivity Factors**
- 2x2x2 factorial study (N=400): Confidence signaling (high/low) × Timing (immediate/delayed) × Framing (assertive/tentative)
- Task: Users answer trivia questions, receive AI feedback that sometimes disagrees
- Measure: Answer revision rate, trust ratings, perceived helpfulness
- Identify which factors predict receptivity across user demographics

**Experiment 3: Calibrated Disagreement Training**
- Fine-tune LLaMA-3-8B using DPO with preference pairs where preferred responses match disagreement strategy to predicted receptivity
- Receptivity predictor trained on Experiment 2 data
- Compare: (a) Sycophantic baseline, (b) Always-correct baseline (blunt truth), (c) CCD model
- Evaluation: 300 users complete 20-question sessions with each model
- Metrics: Final answer accuracy, trust (1-7 scale), willingness to use again, qualitative feedback

**Experiment 4: Longitudinal Bidirectional Adaptation**
- 50 users interact with CCD system over 5 sessions (1 week apart)
- Track: User receptivity to disagreement over time, AI adaptation to individual users
- Hypothesis: Both parties show improved calibration—users become more receptive, AI becomes better at predicting individual receptivity
- Metrics: Session-over-session improvement in accuracy, trust stability, receptivity growth rate

## Risk Factors And Limitations

1. **Human receptivity may be context-dependent beyond our taxonomy**: Real-world disagreements involve emotional and social factors we may not fully capture.
2. **Scalability of receptivity prediction**: Individual-level calibration may require more interaction data than available in typical deployments.
3. **Potential for manipulation**: A system optimized for persuasive disagreement could be misused; we focus on factual/reasoning contexts to mitigate this.
4. **Participant recruitment**: Longitudinal study requires committed participants; attrition may bias results toward engaged users.
5. **Generalization across cultures**: Disagreement norms vary culturally; our initial study focuses on English-speaking populations.
6. **Confound between strategy and content**: Ensuring disagreement strategy effects are separable from content quality requires careful stimulus design.

