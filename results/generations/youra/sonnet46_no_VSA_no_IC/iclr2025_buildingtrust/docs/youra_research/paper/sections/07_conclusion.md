## 7. Conclusion

We began with a falsified mechanism and an unexpected empirical finding — and the unexpected finding turned out to be the contribution.

Our original hypothesis predicted that adversarial benchmark construction would disrupt cross-split rank stability for robustness, producing a meaningful and mechanistically-explained gap between fairness and adversarial robustness rank preservation. The mechanism was wrong. Both fairness and adversarial robustness rankings are highly stable after controlling for general capability — near-perfect for fairness (partial Spearman ρ = 0.962), substantial for robustness (ρ_ANLI = 0.684, ρ_AdvGLUE = 0.868), with zero rank reversals across N=13 models on adversarial pairs. The adversarial design of ANLI R3 and AdvGLUE does not reshuffle the model ordering.

### Summary of Contributions

In this work, we established that LLM trustworthiness benchmark rankings are stable across in-distribution to out-of-distribution shifts even after removing the general capability confound. Our three contributions:

1. **An empirical baseline** for trustworthiness benchmark predictive validity: both fairness and adversarial robustness dimensions exhibit high cross-split rank stability (ρ > 0.68), establishing that these evaluations measure stable model properties rather than context-specific artifacts.

2. **A methodological demonstration** that partial Spearman ρ (MMLU-controlled) is a tractable operationalization of trustworthiness benchmark predictive validity using published scores only — requiring no new model evaluation, no proprietary access, no annotation.

3. **A theoretical revision**: the adversarial disruption hypothesis is falsified. The correct characterization is that both fairness and robustness are stable latent model properties, with fairness showing a directional advantage (Δρ = 0.192, p = 0.024) whose mechanism remains unknown and whose magnitude fell marginally below the preregistered confirmation threshold.

### Future Directions

Three priority directions emerge from the evidence:

**From untested alternative explanations:** Does the near-perfect fairness ρ = 0.962 reflect stable model weights, or BBQ item-level overlap between Disambig and Ambig splits? Item-level Jaccard analysis on unique-item subsets would distinguish the model-mechanism account from the benchmark-structure account. This is the highest-priority open question.

**From unverified assumptions:** Richer capability covariates (BIG-Bench Lite, GSM8K, HumanEval) applied via residualized regression would test whether the covariate sensitivity of Δρ (Winogrande control collapses Δρ to 0.073) reflects genuine instability in the fairness-robustness differential or a limitation of MMLU as a proxy. This directly bears on the confirmability of P2.

**From scope extension:** The P3 prediction — that instruction-tuned models show smaller trustworthiness generalization gap for fairness but not robustness — was not tested and remains the most practically actionable open question. Do alignment training protocols (RLHF, constitutional AI) specifically improve fairness generalization? A paired base/instruction-tuned analysis using the LLaMA-2/Chat, Mistral/Instruct pairs would provide initial evidence.

Knowing that a model's trustworthiness ranking is stable across distribution shifts is a prerequisite for principled model selection. This study establishes that the prerequisite is met — while opening the question of why fairness maintains marginally stronger stability than adversarial robustness, and what that asymmetry means for how we build and evaluate trustworthy systems.
