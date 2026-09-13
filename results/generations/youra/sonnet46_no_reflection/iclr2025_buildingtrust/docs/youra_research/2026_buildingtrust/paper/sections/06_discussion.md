# 6. Discussion

Our central finding — that Residual Instability (RI) significantly anticorrelates with Expected Calibration Error after capability control (ρ = −0.535, p = 0.0034) — requires careful interpretation. Three mechanistic frameworks can account for it, and distinguishing among them is the primary open question motivating future work.

## 6.1 Mechanistic Interpretations

**Framework 1: Calibration–Robustness Trade-off (Most Plausible)**

RLHF and instruction tuning improve in-distribution calibration: models learn to match confidence to accuracy on reasoning tasks through human feedback signals that reward well-calibrated, helpful responses [Ouyang et al., 2022; Ziegler et al., 2019]. Simultaneously, RLHF fine-tuning sharpens model behavior in ways that create specific adversarial vulnerabilities — reward hacking exploits, boundary sharpening near the edge of aligned behavior, and susceptibility to adversarial jailbreaks [Perez et al., 2022]. The training-regime confound that survives PC1 control is: instruction-tuned models have simultaneously lower RI (more robust after capability control) *and* lower ECE (better calibrated).

This framework predicts a training-regime interaction: stratifying the 30-model set into pretrained-only vs. instruction-tuned subsets should show ρ ≈ 0 within regimes and the negative RI–ECE correlation arising from *between-regime* differences. The family analysis provides supporting evidence: the Mistral family, dominated by Mistral-Instruct variants with heavy RLHF application, shows the strongest anticorrelation (ρ = −0.827). This test — stratifying by training regime — is the highest-priority future experiment.

**Framework 2: Residual Scale Confounding (Alternative)**

PC1 explains 68.5% of benchmark variance — marginally below our 70% target. If the 1.5% gap reflects residual large-model effects not captured by PC1, then larger models may have both lower RI (better robust after capability control) and lower ECE (better calibrated due to scale), creating a spurious negative partial correlation. Guo et al. [2017] found larger pre-RLHF networks are more overconfident, but Minderer et al. [2021] found modern architectures (post-RLHF era) show better calibration at scale — consistent with this confound being architecture-era dependent.

This framework predicts that supplementary control for log(parameter count) alongside PC1 should weaken or eliminate the RI–ECE anticorrelation. If ρ remains negative after this additional control, Framework 1 is the better explanation.

**Framework 3: Benchmark Specificity**

arc_challenge ECE measures calibration on 4-choice science reasoning. AdvGLUE measures adversarial fragility on NLI-style text perturbation attacks. These may tap orthogonal failure modes where the inverted correlation is a benchmark-combination artifact rather than a general property. If the anticorrelation is arc_challenge-specific and does not replicate on TruthfulQA, BoolQ, or MMLU ECE, Framework 3 is the correct explanation.

**Our Assessment:** Framework 1 (RLHF trade-off) is most consistent with the available evidence — the per-family pattern, the ECE value distributions by training regime, and the theoretical literature on RLHF side effects all point toward the training-regime confound. However, Frameworks 2 and 3 cannot be ruled out from the current data. All three are testable with the existing model matrix, requiring only additional benchmark data collection.

## 6.2 What the Finding Does Not Show

The inverted RI–ECE result does *not* demonstrate that adversarially fragile models are generally trustworthy. Our scope is limited to the RI–ECE dimension on arc_challenge:

- We cannot make claims about hallucination (HaluEval not tested)
- We cannot make claims about safety failure (HarmBench not tested)
- We cannot make claims about out-of-distribution calibration or open-ended generation calibration
- The cross-sectional design means we observe correlation, not causation

The finding also does not imply that robustness improvements will necessarily worsen calibration in practice — the trade-off hypothesis is correlational and cross-model. Within-model interventions (e.g., adversarial fine-tuning) may not exhibit the same trade-off structure.

## 6.3 Limitations

**L1 — OLS-Estimated AdvGLUE Scores (High Impact).** 73% of AdvGLUE values (22/30 models) are estimated via OLS trained on 11 anchor models from TrustLLM ICML 2024 Table 2, because the TrustLLM HuggingFace dataset is gated (HTTP 403). OLS imputation compresses AdvGLUE variance toward the regression mean and introduces correlation structure between RI and the OLS predictors — potentially biasing both the magnitude and direction of ρ(RI, ECE). Direct AdvGLUE measurement on all 30 models via lm-evaluation-harness is required before strong causal or mechanistic claims. This is the most important limitation for future work.

**L2 — Single-Benchmark ECE (Medium Impact).** ECE is computed from arc_challenge only — a specific reasoning task type. Whether the RI–ECE anticorrelation holds for open-ended generation, dialogue, or summarization calibration is unknown. Multi-benchmark ECE replication (TruthfulQA, BoolQ, MMLU) is required for generalizability.

**L3 — PC1 Below 70% Variance Threshold (Low-Medium Impact).** PC1 explains 68.5% of leaderboard v2 benchmark variance, marginally below the 70% target. This introduces potential residual capability confounding in RI. Supplementary analysis using log(parameter count) as an alternative capability control is planned for the camera-ready version.

**L4 — Underpowered Within-Family Analysis (Medium Impact).** Per-family partial correlations are based on n = 6–9 models, yielding power ≈ 0.61 at ρ = 0.4. The family sign consistency finding (1/3 positive) should be treated as exploratory, not confirmatory. Expanding the model set to N ≥ 60 with ≥15 models per family is needed for family-level confirmatory testing.

**L5 — H-M2/M3/M4 Not Executed (Critical — Scope Limitation).** Whether the RI–ECE anticorrelation generalizes to hallucination (HaluEval), safety failure (HarmBench), and output variance (OVI-GSM8K) is entirely unknown. The original hypothesis of a coupled failure cascade across all trust dimensions cannot be evaluated from current data. This is a fundamental scope limitation, not a finding — the paper makes no claims about HaluEval, HarmBench, or OVI.

**L6 — Cross-Sectional Design (Fundamental).** This is an observational cross-model study. Correlation ≠ causation. The negative RI–ECE correlation could reflect confounding by model generation (v1 vs. v2 architectures), training data composition, or other model-level properties not captured by PC1 or mean_confidence. Future longitudinal or interventional designs (e.g., comparing pre- and post-RLHF versions of the same model) would provide stronger causal evidence.

## 6.4 Broader Impact

This work has positive implications for the LLM evaluation community: it demonstrates that cross-dimension trust coupling assumptions should be empirically tested rather than assumed, and provides the RI construct as a reusable tool for doing so. The capability-controlled partial correlation methodology is applicable beyond adversarial robustness — any trust dimension can be residualized and tested against any other.

A potential concern is that our finding could be misinterpreted as endorsing adversarially fragile models as trustworthy. We emphasize: our result is domain-specific (calibration on reasoning tasks) and does not generalize to other trust dimensions. Models that are adversarially fragile remain dangerous in adversarial deployment contexts regardless of their calibration properties on reasoning benchmarks.
