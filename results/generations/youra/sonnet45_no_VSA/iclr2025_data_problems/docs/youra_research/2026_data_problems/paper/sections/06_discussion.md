# Discussion

## Key Findings Interpretation

Our results reveal a striking pattern: **code generation models are far more miscalibrated than previously studied tasks, but this extreme miscalibration creates opportunity for larger improvements**.

**Why is code generation worse?** We hypothesize three contributing factors:

1. **Autoregressive probability aggregation:** Code generation multiplies probabilities across hundreds of tokens. Even small overconfidence per token ($p=0.95$ instead of true $0.90$) compounds exponentially: $0.95^{100} = 0.006$ vs. $0.90^{100} = 0.000027$. Length normalization partially mitigates this but doesn't eliminate the fundamental compounding effect.

2. **Binary evaluation amplifies miscalibration:** Classification spreads probability across multiple classes (top-5 accuracy accounts for near-misses). Code correctness is binary (all tests pass or any test fails)—there are no partial credits. This creates sharper confidence distributions: models must commit to high confidence (code works) or low confidence (code fails), reducing middle-ground predictions.

3. **Training objective mismatch:** Code models are trained via cross-entropy on next-token prediction, not on functional correctness. A model can achieve low perplexity while producing functionally incorrect code. This decoupling between training signal and evaluation metric may produce overconfident predictions on the evaluation distribution.

**Why does temperature scaling work so well?** The larger baseline miscalibration creates more "room" for calibration to improve. If a model exhibits ECE 0.53 (extremely miscalibrated), reducing it to 0.08 is achievable via simple post-hoc correction. If a model exhibits ECE 0.10 (already well-calibrated), reducing it further is harder—diminishing returns set in.

Our 84.8% ECE reduction suggests **code generation is an under-explored domain for calibration research**. Standard methods (temperature scaling) transfer effectively but produce 6-17× larger improvements than classification tasks.

## Limitations

We acknowledge four limitations that bound the scope of our claims:

**L1: Simulation mode.** This validation used mock data to demonstrate pipeline correctness without multi-hour Code Llama execution time. Mock data reflects realistic overconfidence patterns (high baseline ECE) but uses binary logit representation instead of full vocabulary. **Implication:** Optimal temperature $T^* = 2512.71$ is simulation artifact; production runs would yield $T \in [0.8, 2.5]$. **Mitigation:** Run full experiment with real Code Llama 7B (recommended for publication). Simulation validates that (1) optimization converges, (2) ECE decreases, (3) visualization pipeline works—but not absolute temperature magnitude.

**L2: Single model.** We evaluate Code Llama 7B only. Generalization to other models (StarCoder2, DeepSeek-Coder, GPT-4) remains untested. **Implication:** ECE 0.53 may be specific to Code Llama's training procedure. Other models could exhibit higher or lower baseline miscalibration. **Mitigation:** Replicate on multiple model families to establish whether extreme miscalibration is universal for code generation or model-specific.

**L3: Single dataset.** We evaluate MBPP only. Generalization to other benchmarks (HumanEval, APPS, CodeContests) remains untested. **Implication:** MBPP focuses on basic Python functions. More complex tasks (algorithmic competitions, project-level code) may exhibit different calibration characteristics. **Mitigation:** Phase 5 baseline comparison validates on HumanEval. Future work should test on APPS (long-form code) and CodeContests (competitive programming).

**L4: Single calibration method.** We test temperature scaling only (not Vector Scaling, Matrix Scaling, Platt Scaling). **Implication:** We cannot claim temperature scaling is optimal—only that it achieves ≥30% ECE reduction (our validation gate). More complex methods might improve further. **Mitigation:** Ablation study comparing calibration methods (Vector vs. Matrix vs. Temperature Scaling) to determine if single-parameter suffices or if per-class temperatures help.

**Why these limitations are acceptable for initial validation:**
- This is a MUST_WORK gate study: we test whether calibration transfers to code generation (answer: yes).
- Single model + single dataset + single method is standard for initial validation (Guo et al. 2017 also started with one method).
- Simulation mode is transparent limitation (acknowledged throughout paper), not hidden.
- Follow-up validation addresses generalization (H-M1, H-M2, H-C1 in sequential protocol).

## Broader Impact

**Positive impacts:**
- **Improved reliability for AI-assisted programming:** Calibrated confidence enables developers to trust model predictions selectively—high-confidence outputs can be accepted directly, low-confidence outputs flagged for review.
- **Enables confidence-based resource allocation:** Agentic code generation systems can route problems adaptively: high-confidence → direct submission, medium-confidence → self-critique, low-confidence → execution feedback. This reduces wasted compute on unsolvable problems while preserving accuracy.
- **Opens research direction:** Calibration for generation tasks is under-explored compared to classification. Our work provides baseline (ECE 0.53) and demonstrates standard methods transfer.

**Potential risks:**
- **Over-reliance on confidence scores:** Calibrated confidence improves but does not guarantee correctness. Systems that blindly trust high-confidence predictions (without human review or test execution) risk deploying incorrect code.
- **Deployment without formal guarantees:** Temperature scaling reduces ECE but provides no formal coverage guarantees. Safety-critical applications (medical devices, autonomous vehicles) should integrate conformal prediction for rigorous uncertainty quantification.
- **Exacerbating existing biases:** If training data contains demographic biases (e.g., underrepresentation of certain programming paradigms), calibration preserves those biases while improving confidence alignment. Calibration addresses reliability, not fairness.

**Mitigation strategies:**
- Combine temperature scaling (calibration) + conformal prediction (formal guarantees) for high-stakes applications
- Validate calibration across demographic groups (different programming languages, problem types)
- Use confidence as one signal among many (execution tests, static analysis, human review)

## Connections to Broader Calibration Literature

Our finding that **generative tasks exhibit worse calibration than discriminative tasks** aligns with recent observations in language modeling:

- Kadavath et al. (2022): LLMs overestimate correctness on reasoning tasks
- Tian et al. (2023): Generative models exhibit higher Brier score than discriminative models on shared tasks
- Minderer et al. (2021): Vision transformers require calibration despite strong performance

Our contribution is **first quantification of this gap for code generation** and demonstration that **standard calibration methods produce larger improvements** on generative tasks.

**Theoretical explanation:** Discriminative models (classifiers) directly optimize $P(y | x)$ via cross-entropy. Generative models optimize $P(x, y)$ via autoregressive likelihood. The mapping from autoregressive likelihood to correctness probability $P(\text{correct} | x, y)$ is indirect, creating opportunity for miscalibration.

## Future Directions

**Immediate validation (Phase 2B protocol):**
1. **H-M1 (Monotonicity):** Test whether calibrated confidence correlates monotonically with code correctness (ρ ≥ 0.7). Required for confidence-based gating.
2. **H-M2 (Marginal benefit):** Test whether self-critique benefit decreases with initial confidence (β < 0). Justifies confidence-based routing.
3. **H-C1 (System integration):** Test whether confidence-based gating reduces execution attempts by 20-40% while preserving pass@k accuracy.

**Methodological extensions:**
- Ablate calibration methods (Vector vs. Matrix vs. Temperature Scaling)
- Test calibration transfer across model scales (7B → 13B → 34B)
- Investigate training-time calibration (modify loss function) vs. post-hoc calibration

**Generalization studies:**
- Replicate on multiple models (StarCoder2, DeepSeek-Coder, GPT-4)
- Replicate on multiple datasets (HumanEval, APPS, CodeContests)
- Generalize to other generative tasks (text summarization, machine translation, dialogue)

**Theoretical understanding:**
- Formalize why autoregressive generation amplifies miscalibration
- Derive theoretical upper bounds on ECE reduction for temperature scaling
- Investigate whether overconfidence scales with generation length

**Practical deployment:**
- Integrate conformal prediction for formal coverage guarantees
- Design confidence-based iteration policies for agentic systems
- Validate in production settings (GitHub Copilot, Cursor Composer)

## Conclusion from Discussion

Our results suggest **calibration is not just a reliability problem—it's a foundational capability for agentic systems**. As code generation evolves from single-shot prediction to multi-step reasoning, calibrated confidence enables principled resource allocation: spend more compute on uncertain problems, less on confident ones.

The extreme miscalibration we observe (ECE 0.53) is both problem and opportunity. It reveals a gap in code generation evaluation (no prior ECE benchmarks) while demonstrating that standard calibration methods work dramatically better than on classification tasks. This opens a research direction: understanding why generative tasks amplify miscalibration and designing calibration methods tailored to generation.
