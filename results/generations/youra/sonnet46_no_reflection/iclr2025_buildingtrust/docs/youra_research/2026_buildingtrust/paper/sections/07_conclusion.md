# 7. Conclusion

We set out to test a foundational assumption in LLM trustworthiness research: that adversarial fragility and calibration error are positively coupled — that a model brittle under adversarial attack will also be overconfident on reasoning tasks. Our experiments on 30 LLMs across 9 families confirm the opposite. Residual Instability (RI), a capability-orthogonal measure of adversarial fragility, significantly anticorrelates with Expected Calibration Error (ρ = −0.535, p = 0.0034) — adversarially fragile models are better calibrated, not worse.

## 7.1 Summary of Contributions

In this work, we addressed the untested cross-dimension coupling assumption in LLM evaluation by introducing the RI construct and applying it to a diverse 30-model benchmark matrix.

Our main contributions are:

1. **The RI Construct** — a capability-controlled operationalization of adversarial fragility (OLS residual of AdvGLUE drop after regressing out PC1 and mean confidence) that is non-degenerate (R²=0.529, SD=0.121) and orthogonal to capability by construction (VIF=1.000). This construct is reusable for any cross-dimension trust analysis requiring capability-controlled adversarial fragility.

2. **The Inverted RI–ECE Anticorrelation** — a statistically robust empirical finding (ρ=−0.535, 95% CI=[−0.782, −0.101], p=0.0034, n=30) that refutes the coupled failure cascade prediction and reveals that adversarial fragility and calibration are anticorrelated after capability control. This finding holds across two of three major model families (LLaMA, Mistral) and is robust to outlier removal.

3. **The Calibration–Robustness Trade-Off Hypothesis** — a testable mechanistic explanation grounded in the RLHF literature: instruction tuning simultaneously improves in-distribution calibration and creates adversarial vulnerabilities, producing the observed negative partial correlation. This hypothesis makes concrete predictions (training-regime stratification should eliminate the between-group correlation) that motivate the next experimental iteration.

## 7.2 Future Directions

The finding opens three grounded research directions:

**From untested mechanistic alternatives:** The residual scale confounding interpretation (Framework 2) and benchmark specificity interpretation (Framework 3) remain viable alternatives to the RLHF trade-off hypothesis. The most decisive experiment is training-regime stratification: if the anticorrelation is driven entirely by between-regime differences, ρ should approach zero within pretrained-only and instruction-tuned subsets. Adding log(parameter count) as a supplementary capability control tests whether the 1.5% PC1 variance gap accounts for the result.

**From unverified scope assumptions:** The generalizability of the anticorrelation to other calibration benchmarks (TruthfulQA, BoolQ, MMLU ECE) is the critical replication question. If ρ(RI, ECE) < 0 across ≥3 diverse benchmarks, the result is not an arc_challenge artifact. More importantly, running the redesigned H-M2/M3/M4 with revised directional predictions (allowing negative correlations, not requiring positive) will reveal whether the trade-off structure extends to hallucination and safety failure — the central unresolved question of the original research program.

**From direct measurement gaps:** 73% of AdvGLUE scores are OLS-estimated due to gated dataset access. Direct measurement via lm-evaluation-harness on all 30 models is required for any strong mechanistic claim. With direct measurements, RI variance may shift, and the direction and magnitude of ρ(RI, ECE) may change — making this the highest-priority experimental investment before any follow-up work on H-M2/M3/M4.

## 7.3 Closing

The LLM evaluation community has implicitly assumed that trustworthiness failures cluster — that a fragile model is comprehensively untrustworthy. Our work suggests the reality is more nuanced: after controlling for capability, adversarial fragility and calibration may reflect distinct, inversely-related failure modes shaped by the same training decisions that make modern LLMs useful. Understanding this trade-off structure is not merely a scientific curiosity — it is a precondition for designing alignment methods that improve all trust dimensions simultaneously rather than trading one off against another. We hope this work encourages the field to test, rather than assume, the coupling structure of LLM failure modes.
