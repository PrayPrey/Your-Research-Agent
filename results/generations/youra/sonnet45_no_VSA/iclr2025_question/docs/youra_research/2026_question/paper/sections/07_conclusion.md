# 7. Conclusion

We began by asking whether CCP-based hallucination detection degrades when applied to creative text due to implicit factual-ontology assumptions. We end with a methodological requirement: **validate your measurement before testing your hypothesis**.

Our attempt to test ontology-dependent degradation encountered a measurement validity failure: claim-type mass ratio ($\rho_j$) values were 50× lower than expected (0.01–0.04 vs 0.75–0.85) across both factual (TruthfulQA) and creative (WritingPrompts) domains. Root cause analysis revealed that DeBERTa-v3-base NLI, trained on SNLI/MNLI semantic similarity tasks, does not generalize to factual verification tasks (claim-context consistency checking). The model assigns ~90% probability mass to the "neutral" class, mechanistically driving $\rho_j \to 0$.

This failure mode teaches a critical lesson: when a metric produces values far outside the expected range across ALL conditions, you face a logical impossibility—you cannot distinguish "hypothesis is wrong" from "measurement is broken." In our case, the uniform degradation across factual and creative domains could mean (a) creative text does NOT confuse CCP (hypothesis refuted), or (b) our CCP implementation does not work as described (measurement broken). Without baseline replication on the original domain, we cannot separate these explanations.

**Our contributions**, despite the gate failure, advance hallucination detection research in four ways:

1. **Transparent Failure Documentation**: We provide the first systematic replication attempt of CCP, documenting both what went wrong (NLI neutral-class dominance, claim decomposition gaps, no baseline validation) and why (task-domain gap: SNLI/MNLI ≠ factual verification).

2. **Root Cause Hierarchy**: We identify Tier 1 (NLI calibration: PRIMARY), Tier 2 (claim decomposition quality, context pairing strategy: CONTRIBUTORY), and Tier 3 (temperature/calibration: UNLIKELY) failure modes, with evidence strength rankings and falsifiability tests for each.

3. **Methodological Requirements**: We propose four actionable recommendations to prevent repetition of this failure: (R1) report raw metric distributions, not just ROC-AUC; (R2) validate NLI calibration on known examples; (R3) document claim decomposition methodology with inter-method agreement; (R4) provide public code with baseline replication notebooks.

4. **Theoretical Contribution**: We distinguish **task-domain gap** (SNLI/MNLI semantic similarity ≠ factual verification) from traditional **domain shift** (vocabulary/style differences), showing that hallucination detection methods inherit training objective assumptions, not just data distribution biases.

The broader lesson: hallucination detection papers optimize for **novelty** (reporting +0.05 ROC-AUC) over **reproducibility** (documenting how to achieve the baseline). This creates a field-wide replication crisis where methods cannot be extended to new domains because the baseline cannot be reproduced. Our negative result is itself a contribution—it exposes this gap and proposes concrete fixes.

**Returning to our opening question**: Does CCP degrade on creative text? We cannot answer this yet—measurement validity must precede hypothesis testing. But the journey revealed something more valuable: **implementation details are first-class contributions**, not afterthoughts. Raw metric distributions, NLI calibration diagnostics, and claim decomposition validation should be documented with the same rigor as novelty claims.

Transparent failures accelerate progress by preventing repetition of costly mistakes. If the field adopts our reproducibility recommendations (R1–R4), future researchers will spend less time debugging implementation gaps and more time testing hypotheses. That is the contribution we hope this work enables.
