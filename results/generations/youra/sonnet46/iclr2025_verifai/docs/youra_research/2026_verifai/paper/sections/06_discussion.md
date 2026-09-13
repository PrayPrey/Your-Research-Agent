# 6. Discussion

## 6.1 Key Findings

Our experiments reveal three qualitatively distinct calibration patterns under self-contained difficulty stratification, corresponding to three architectural training regimes:

**Finding 1: Architecture determines ΔECE direction.** The most consequential result is not that P(True) calibration degrades on hard problems (as we hypothesized), but that the direction of the ΔECE is architecture-specific. Code-specialized pre-training (DeepSeek-Coder) produces the expected positive ΔECE (+0.298). Code-adapted fine-tuning (CodeLlama) inverts it (−0.249). General-purpose pre-training (Llama3) produces calibration insensitivity to difficulty (≈0). These three patterns are distinct, large, and reproducible across bin counts — making ΔECE a genuine architectural fingerprint, not a statistical artifact.

This finding changes how we should think about P(True) calibration in code verification contexts. The common assumption — "P(True) from hard problems is less reliable than from easy problems" — is valid only for code-specialized architectures. Deploying a code-adapted model under this assumption would lead to systematically wrong threshold decisions: the practitioner would over-trust easy-problem confidence signals that are, in fact, less reliable.

**Finding 2: Global temperature scaling is architecture-insufficient.** Temperature scaling is the canonical post-hoc calibration method [Guo et al., 2017], and it corrects global overconfidence in calibration. However, our results show that architecture-dependent ΔECE direction cannot be corrected by a single global T. For CodeLlama, T*=3.95 (far outside the typical 1.0–2.0 range) reflects pathological global overconfidence; applying this scaling worsens ΔECE rather than correcting it. For DeepSeek, positive ΔECE attenuates but persists after scaling. These results suggest that difficulty-conditioned miscalibration requires architecture-specific or tier-specific interventions.

**Finding 3: 24.5% of EvalPlus problems are universally hard.** The 133 problems hard for all three models represent a structural "iron core" of difficulty that is architecture-independent (Jaccard 0.456–0.546 across pairs). These problems are candidates for robust difficulty-stratified calibration benchmarks — they allow cross-architecture calibration comparison without the confound of different problem sets.

## 6.2 Mechanistic Interpretation

The architecture-dependent ΔECE pattern is consistent with a training data composition hypothesis:

- **DeepSeek-Coder** (code-specialized pre-training from scratch on large code corpora): This model has developed fine-grained code understanding that creates genuine uncertainty discrimination between hard and easy problems. Hard problems (where it fails 5/5 times) trigger authentic P(True) uncertainty; easy problems (where it succeeds 3–5/5 times) trigger appropriate confidence. The model's pre-training has aligned confidence magnitude with difficulty in the expected direction.

- **Llama3-8B** (general-purpose pre-training without code specialization): Code problems are outside the model's primary competence domain. Both hard and easy code problems appear similarly uncertain from the model's perspective, producing uniform calibration insensitivity (ECE ≈ 0.49 for both tiers). This is not good calibration — both tiers are highly miscalibrated — but the miscalibration does not depend on our difficulty stratification.

- **CodeLlama-7B** (code fine-tuning on Llama base): The fine-tuning on large code repositories, which include many common Python utilities similar to MBPP problems, creates pattern-matching overconfidence. Easy problems (which are MBPP-style problems that resemble the training distribution) receive high P(True) confidence regardless of correctness, because the model has been trained to recognize them as "correct-looking" code. Hard problems (more unusual algorithms or edge cases) do not match this pattern-matching overconfidence, so they receive lower (and more appropriate) confidence. The result: ECE(easy)=0.615 >> ECE(hard)=0.366.

We note that this mechanistic interpretation is exploratory (N=1 per architecture category; see limitations). The training data composition hypothesis should be tested directly by analyzing whether CodeLlama's high P(True) scores on easy-tier problems correlate with their similarity to CodeLlama's training corpus.

## 6.3 Implications for Practitioners

**For code verification pipeline designers:** Characterize your model's ΔECE direction before setting confidence thresholds. For code-specialized models (e.g., DeepSeek-Coder family), lower confidence thresholds on hard problems are appropriate — these signals are less reliable. For code-adapted models (e.g., CodeLlama family), lower confidence thresholds on easy-looking problems may be more appropriate. For general-purpose models, difficulty-stratified thresholding provides no benefit.

**For benchmark designers:** The 133-problem "iron core" (universally hard across architectures) provides a useful architecture-agnostic difficulty benchmark for calibration studies. These problems are hard because of their structural properties, not because of any single model's capability gap.

**For calibration researchers:** Global temperature scaling is insufficient for architecture-dependent miscalibration. Tier-specific temperature scaling (fitting separate T_hard and T_easy) may correct ΔECE direction for code-specialized models while avoiding the dramatic worsening seen with global T for code-adapted models.

## 6.4 Limitations

**L1: k=5 pilot methodology.** With only 6 discrete pass@1 values (0.0, 0.2, 0.4, 0.6, 0.8, 1.0), tier assignments are coarse and carry high binomial variance for individual problems near tier boundaries. We explicitly frame this as a pilot study. The M-sensitivity analysis confirms directional stability, and the large effect sizes (ΔECE=0.298, −0.249) are robust to this coarseness, but future work should use k≥20 for finer stratification.

**L2: CodeLlama easy tier underrepresentation (n=37).** The CodeLlama easy tier is based on only 37 MBPP problems (HumanEval contributes n_easy=0). While the effect size (−0.249) is large and the CI is entirely negative, small sample variance could inflate magnitude. The direction is robust; the precise magnitude should be confirmed with larger-sample replication. We recommend k=20–50 for a follow-up study specifically testing CodeLlama's inversion.

**L3: Three-model exploratory scope (N=1 per category).** Our architecture-specific interpretations are exploratory rather than confirmatory. With one model per category, we cannot distinguish between (a) architecture-category effects and (b) idiosyncratic properties of the specific models chosen. Adding Mistral-7B (second general model), WizardCoder-7B (second code-adapted model), and DeepSeek-Coder-33B (larger code-specialized model) would allow within-category comparison.

**L4: Weak P(True)-correctness correlation (r=0.14–0.20).** P(True) captures a genuine but weak confidence signal: correlation with correctness is statistically significant (p < 10⁻¹⁰) but modest (r < 0.20). The ECE calibration analysis is valid given this weak correlation — ECE measures whether confidence magnitudes correspond to accuracy rates, which is orthogonal to the correlation between individual confidence values and individual correctness. However, the weak signal means our ECE estimates partially reflect confidence noise rather than pure calibration properties.

## 6.5 Broader Impact

This work contributes to the responsible use of LLMs in automated software engineering workflows. As LLMs are deployed in code review, test generation, and automated refactoring pipelines, their confidence signals increasingly influence downstream decisions. Our finding that calibration behavior is architecture-dependent — rather than uniformly degrading on hard problems — suggests that practitioners should not apply uniform confidence thresholds across different model architectures. Characterizing a model's calibration fingerprint before deployment is a safety property of automated code review systems.

On potential negative impacts: the P(True) methodology we validate enables confidence-based filtering in automated code review. If practitioners incorrectly assume universal positive ΔECE (valid only for code-specialized models), they may deploy code-adapted models with hard-problem-adjusted thresholds that are actually inappropriate, increasing false negative rates for code verification. We explicitly address this risk by demonstrating the architecture-dependent nature of the assumption.
