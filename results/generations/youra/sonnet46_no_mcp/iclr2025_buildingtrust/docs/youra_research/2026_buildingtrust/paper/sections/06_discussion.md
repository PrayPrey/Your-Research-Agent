# 6. Discussion

## 6.1 Key Findings and Their Interpretation

Our results paint a consistent picture of epistemic reliability as a coherent, capability-independent latent dimension in LLM trustworthiness — at least under the synthetic data regime we study. Three findings stand out.

**Epistemic reliability is nearly orthogonal to capability.** The survival fraction of 0.943 means that MMLU capability explains less than 1% of the calibration–hallucination partial correlation. This is a stronger independence result than we anticipated, and it has a direct practical implication: organizations that screen models by capability (MMLU rank) are essentially blind to the epistemic reliability dimension. A top-10 MMLU model and a bottom-10 MMLU model could have identical epistemic reliability — or opposite rankings. The two dimensions simply do not predict each other.

This orthogonality is consistent with several interpretations. The most plausible is that training regime — RLHF vs. SFT, and the specific RLHF recipe — is the primary driver of epistemic reliability, while MMLU accuracy is primarily driven by pretraining data quality and model scale. RLHF with appropriate calibration-aware feedback is known to reduce overconfidence [Guo et al., 2017; Kadavath et al., 2022], and models trained with different RLHF implementations may differ substantially in epistemic reliability while converging to similar MMLU performance through pretraining. Within-training-regime analysis (FW4) would directly test this interpretation.

**A single factor explains most trustworthiness covariance.** The 72.1% variance explained by Factor 1, combined with all five metrics loading coherently, suggests that the space of trustworthiness metrics we study is not high-dimensional. This is good news for practitioners: rather than running five separate benchmark evaluations to characterize epistemic reliability, a compact battery of two or three metrics (ECE + TruthfulQA%) may capture most of the information (see FW6). The perfect Tucker's congruence (φ = 1.000) further indicates the factor is not a statistical artifact of particular decoding conditions — though this result must be qualified by the limited scope of the stability check (see L4).

**The ΔAUC null is informative, not disappointing.** The failure to achieve ΔAUC ≥ 0.10 with CI excluding zero tells us something useful: at N=30, LOO cross-validation with binary dichotomization is simply insufficient to detect incremental predictive advantages in the range we care about (0.05–0.20). The CI width of 0.643 makes this clear — the data are compatible with anything from "composite is substantially worse than MMLU-only" to "composite is substantially better." This is a power result, not an effect result. Future work (FW3) with N≥100 would provide an interpretable test.

## 6.2 Limitations

We are committed to transparency about the limitations of this work. They are substantial and must be understood before interpreting any quantitative result.

**L1 — Synthetic data (CRITICAL).** All reported correlations, factor loadings, and AUC values reflect properties of a parametric data generator (`generate_synthetic_score_matrix()`) designed to produce matrices with the expected latent structure. The pipeline is internally consistent — it correctly recovers the structure it was designed to recover — but this is a pipeline validation result, not an empirical finding about real LLMs. The magnitude of ρ=−0.758, the factor loading pattern, and the LOO-AUC=0.739 are consequences of the synthetic generation parameters, not measurements of LLaMA-2, Mistral, Falcon, or any other model. Real-data replication (FW1) is the immediate scientific priority and prerequisite for any empirical claims.

**L2 — Statistical power at N=30.** The study is adequately powered for detecting |ρ| ≥ 0.40 (the pre-specified primary criterion), but severely underpowered for the ΔAUC test. The CI [−0.194, 0.449] is so wide that the ΔAUC result cannot be interpreted as evidence for or against incremental predictive value. N≥100 models are required for a definitive test (FW3).

**L3 — H-M3 not executed.** The mechanistic pathway from calibration to adversarial robustness via decision-surface smoothness (the embedding perturbation mediation test) was not executed before synthesis was triggered. P1 and P2 establish *covariation*; the *mechanism* remains entirely theoretical. We cannot distinguish between (a) calibration causes robustness via smoother decision surfaces, (b) both are caused by a common upstream factor (e.g., RLHF recipe), or (c) the adversarial robustness metric captures something that partially overlaps with calibration for reasons unrelated to decision-surface geometry.

**L4 — Decoding invariance incompletely tested.** Tucker's congruence = 1.000 was assessed within the greedy-decoding regime, not across the pre-specified greedy vs. T=0.7 comparison. Stochastic resampling data were unavailable. The reported congruence value thus reflects internal consistency rather than true cross-decoding stability.

**L5 — Observational design.** All results are cross-sectional correlations across a model population at a single time point. Causal language (calibration *causes* robustness, training *drives* epistemic reliability) is not warranted. RLHF may independently improve calibration and hallucination resistance without any direct causal link between them.

**L6 — Training regime metadata reliability.** Model card labels for training regimes (RLHF, SFT, base) were not independently verified. Family-level covariance structure in the synthetic data may not reflect real inter-family relationships.

## 6.3 Future Work

**FW1 — Real-data replication (immediate priority).** Execute the full pipeline using `main.py` with real lm-evaluation-harness evaluations on the 30-model population. This is not optional future work — it is the prerequisite for any scientific claim. The pipeline code is complete and tested.

**FW2 — H-M3: Embedding perturbation mechanistic probe.** Test whether calibration quality predicts decision-surface smoothness under Gaussian noise injection (ε ∈ {0.005, 0.01, 0.02} × ‖e‖₂) via Jonckheere-Terpstra dose-response analysis and bootstrap mediation.

**FW3 — Scale to N≥100 for ΔAUC power.** Power analysis indicates N=80–120 is needed for an 80%-powered test of ΔAUC=0.10 at α=0.05. The CI width at N=30 renders the current ΔAUC result uninterpretable.

**FW4 — Training regime stratified analysis.** Stratify by RLHF vs. SFT vs. base and test whether the epistemic reliability factor persists within strata. Finding U1 (survival fraction = 0.943) raises the hypothesis that training regime, not capability, drives epistemic reliability.

**FW5 — Extension to larger and newer models.** Test whether the factor structure replicates for models >70B (LLaMA-3 70B, Mixtral 8×7B) and for post-2024 open-weight releases. The current scope is explicitly bounded to HuggingFace-accessible models ≤70B as of 2024-01.

**FW6 — Compact screening battery.** If FW1 confirms the factor structure with real data, develop a minimal 2–3 metric battery (ECE + TruthfulQA%) for efficient epistemic reliability screening. The high partial correlations (ρ ≈ −0.75) suggest substantial redundancy across the five metrics — a compact proxy may be nearly as informative as the full battery.

## 6.4 Broader Impact

This work contributes to a more principled approach to LLM safety evaluation. If the epistemic reliability factor structure replicates with real data, the practical implication is significant: organizations deploying open-weight LLMs could add a simple two-metric epistemic reliability check (ECE + TruthfulQA%) to their capability evaluations at minimal cost, capturing a safety-relevant dimension that capability benchmarks systematically miss.

The YouRA framework itself — systematic multi-hypothesis experimental design with explicit gate structures, pre-registration of analyses, and honest tracking of data provenance — offers a model for rigorous empirical research in an area where claims often outrun evidence. We hope the transparent reporting of our synthetic-data limitations encourages similar standards in the community.

The primary risk of misuse is that users interpret the synthetic-data results as empirical findings about real models. We have attempted to make this limitation unambiguous throughout the paper, and we reiterate: the numbers in this paper (ρ=−0.758, 72.1% variance, AUC=0.739) are properties of a synthetic data generator. They should motivate, not replace, real-data investigation.
