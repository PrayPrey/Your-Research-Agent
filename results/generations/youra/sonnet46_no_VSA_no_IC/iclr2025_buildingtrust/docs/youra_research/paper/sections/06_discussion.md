## 6. Discussion

### 6.1 Key Findings and Their Implications

**Finding 1: Trustworthiness rankings are stable latent model properties.**

The core empirical result — high partial ρ for both fairness and adversarial robustness after capability control — indicates that trustworthiness properties are not test-specific artifacts. A model's relative fairness standing in evaluations transfers to harder evaluation conditions (ambiguous contexts, adversarially constructed rounds). This validates the implicit assumption in LLM safety evaluation: that in-distribution evaluations are informative about OOD trustworthiness behavior.

For practitioners: model selection decisions based on trustworthiness rankings are more robust than one might have assumed. The relative ordering of models on fairness and robustness benchmarks is preserved when those benchmarks become harder or shift context.

**Finding 2: The adversarial disruption hypothesis is wrong at the model-ranking level.**

Our original mechanism — that adversarial benchmark construction (ANLI R3, AdvGLUE) would disrupt rank stability — was grounded in a theoretically compelling argument and a two-model observation from DecodingTrust. At N=13 with diverse model families, the disruption disappears. Both adversarial pairs show substantially positive partial ρ with zero rank reversals.

This has a specific implication for benchmark design: creating harder adversarial evaluation conditions does not reshuffle the model ranking. The models that are most robust to adversarial perturbation in easy conditions remain the most robust in hard conditions. If the goal of adversarial benchmarks is to reveal *different* models as best, this goal is not being achieved — at least for robustness ranking purposes.

**Finding 3: Capability control reveals hidden differential structure.**

Without MMLU control, raw ρ is near-ceiling for all dimensions and the fairness-robustness comparison is invisible (Δρ_raw ≈ −0.005). The partial analysis reveals the hidden structure (Δρ_partial = 0.192). This is a methodological argument: evaluators who report only raw cross-benchmark correlations are missing dimension-specific information. Capability control is the key tool for separating trustworthiness-specific rank preservation from general capability-driven rank preservation.

### 6.2 Limitations

**Limitation 1: GLUE/AdvGLUE arm structurally unavailable for decoder-only LLMs.**

GLUE-X [Yang et al., 2023], which provides the GLUE→AdvGLUE benchmark pair at scale, evaluates encoder-only PLMs (BERT, RoBERTa, ELECTRA) — not the decoder-only LLMs in TrustLLM. Zero model overlap precluded this pair from the primary analysis. We used TrustLLM's OOD robustness task as a proxy for the second robustness pair. The architectural divergence between encoder-only PLMs and decoder-only LLMs reflects a structural shift in the NLP landscape that makes direct comparison impossible with published data. Decoder-only LLM evaluation on AdvGLUE tasks would require new data collection.

**Limitation 2: Δρ = 0.192 falls marginally below the preregistered 0.200 criterion; Fisher z applied to same-N=13 subset.**

The fairness-robustness differential is real and directionally significant (Fisher z p = 0.024) but does not reach the preregistered confirmation threshold. The 0.008 shortfall falls within the measurement uncertainty of N=13 robustness analysis. Two contributing factors: three models missing robustness scores reduce power, and ρ_ANLI = 0.684 is higher than our theoretical expectation, compressing Δρ. We report this as directional evidence requiring replication with a larger, complete model set.

Note on statistical validity: The Meng et al. [1992] Fisher z-test for dependent correlations requires that both correlations come from the same sample. We therefore re-estimated ρ_fairness on the N=13 robustness subset (yielding ρ=0.967) before computing Δρ and Fisher z, ensuring same-sample validity. The N=16 fairness estimate (ρ=0.962) is reported separately as the primary RQ1 result. The Δρ of 0.192 = 0.967 − 0.776 is computed on the N=13 common subset.

**Limitation 3: Causal mechanism for the fairness advantage is unknown.**

We proposed that adversarial design disrupts robustness rankings (explaining why fairness > robustness stability). This mechanism is falsified. The directional fairness advantage, when present, has no confirmed mechanistic explanation. Two alternatives remain viable:

- *Stable latent bias hypothesis:* Fairness biases are more deeply encoded in weights than robustness properties, leading to stronger preservation. (Plausibility: HIGH)
- *Benchmark overlap hypothesis:* BBQ-Disambig and BBQ-Ambig share sufficient item-level structure that the high ρ partially reflects benchmark design rather than model mechanism. (Plausibility: MEDIUM — requires item-level analysis to test)

The covariate sensitivity (Winogrande control reduces Δρ from 0.192 to 0.073) suggests that the robustness ρ values may be partially driven by general reasoning dimensions not fully captured by MMLU rank. Future work with richer capability covariates (BIG-Bench, GSM8K) would clarify this.

**Limitation 4: Scope restricted to 2023–2024 model population.**

Results apply to the 16 models in TrustLLM, which covers the 2023–2024 evaluation landscape (LLaMA-2, Mistral, GPT-3.5/4, Falcon, Vicuna families). Post-2024 models with substantially different training methodologies (RLHF at scale, constitutional AI, large instruction-tuning datasets) may exhibit different stability patterns. The temporal validity of our findings is a scope boundary.

**Limitation 5: P3 (instruction-tuning effects) untested.**

The prediction that instruction-tuned models would show smaller trustworthiness generalization gap (TGG) for fairness but not robustness was not tested. This requires paired base/instruction-tuned analysis and was deferred as exploratory. It remains the most practically actionable prediction — whether RLHF alignment improves fairness generalization specifically — and is the clearest priority for follow-on work.

### 6.3 Broader Impact

This research provides empirical grounding for a widely-held but untested assumption in LLM safety evaluation. The finding that trustworthiness rankings are stable is positive for practitioners who rely on benchmark-based model selection. The mechanism falsification is scientifically valuable: correcting the adversarial disruption hypothesis prevents a misleading theoretical account from accumulating citations and policy influence.

The risk of misuse is low: demonstrating that adversarial robustness rankings are *stable* could be interpreted as reducing urgency for harder adversarial evaluation. We note that rank stability and absolute performance level are distinct — models maintaining their relative ordering on harder benchmarks while all performing worse on those harder benchmarks means adversarial evaluation still reveals genuine capability limits. Stability of rank does not imply adequacy of performance.
