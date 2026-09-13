# Related Work

## Consistency-Based Uncertainty Quantification

Consistency-based methods measure uncertainty by detecting generative inconsistency across multiple model samples. **SelfCheckGPT** (Manakul et al., 2023) pioneered this approach, using NLI and n-gram overlap to score consistency between an initial response and multiple resampled outputs, achieving strong hallucination detection without external knowledge bases (1,061 citations). The method operates purely in the generation space: generate k samples from the model, compare them pairwise, and flag low-consistency outputs as uncertain. This captures epistemic uncertainty—whether the model "knows" the answer—without requiring labeled validation data during inference.

Subsequent work extended this paradigm: **MIND Framework** (Chen et al., 2024) analyzes internal LLM states for real-time detection, while **MetaQA** (Guo et al., 2024) applies metamorphic testing to achieve 112% F1 improvement on hallucination detection. **ESI** (Yin et al., 2024) introduces semantic-preserving interventions to isolate epistemic versus aleatoric uncertainty. These methods share a common limitation: they provide binary or scalar uncertainty scores but lack statistical guarantees on calibration quality or coverage.

**Gap**: Consistency methods are computationally efficient (5-10 samples typically suffice) and capture epistemic structure, but cannot answer "what is the probability this confidence interval contains the true answer?" This limits their application in risk-sensitive domains requiring rigorous statistical bounds.

## Statistical Uncertainty Quantification

Statistical UQ methods provide calibration guarantees through rigorous probabilistic frameworks. **Conformal prediction** (Vovk et al., 2005; Shafer & Vovk, 2008) offers distribution-free coverage guarantees: given miscoverage rate α and an exchangeable calibration set, conformal intervals contain the true label with probability ≥ 1-α. **COIN** (Wang et al., 2025) applies conformal prediction to LLM factuality, achieving 90%+ coverage with false discovery rate (FDR) control (17 citations). The method constructs prediction sets by ranking candidate answers via conformity scores computed on a held-out calibration set.

**FactTest** (Nie et al., 2024) extends this with hypothesis testing frameworks providing Type I/II error control. Conformal methods guarantee coverage independent of model architecture or training procedure, making them attractive for safety-critical applications. However, they require large labeled calibration sets (typically 500-1000 examples) and incur significant computational cost: COIN performs ~4000 forward passes per 1000 queries to maintain coverage guarantees.

**Gap**: Statistical methods provide rigorous bounds but ignore epistemic structure. A query where the model is highly inconsistent (low epistemic confidence) receives the same statistical treatment as one where the model is certain, leading to computational inefficiency.

## Integrated Approaches

Prior work has explored combining multiple UQ signals, primarily through independent cascades. **DiverseAgentEntropy** (Liu et al., 2024) estimates uncertainty via multi-agent voting for black-box LLMs. **C-LoRA** (Jin et al., 2024) introduces parameter-efficient contextual uncertainty through LoRA adapters. These methods apply different UQ techniques sequentially or in parallel but lack joint calibration: signals are computed independently and combined post-hoc through thresholding or weighted averaging.

The closest prior work is independent cascade (SelfCheckGPT → COIN), where consistency filtering precedes conformal calibration. However, cascades treat the two methods as separate stages: consistency thresholds and conformal parameters are tuned independently on the same validation set, with no bidirectional information flow. This achieves modest improvements (estimated ECE ~0.06-0.08 on TruthfulQA) but misses efficiency gains from mutual calibration.

**Gap**: No prior work integrates consistency and statistical methods through joint calibration where each signal informs and updates the other. Cascades achieve "integration" only in execution order, not in the Bayesian sense where priors and likelihoods interact.

## Theoretical Foundations

The relationship between consistency-based and statistical UQ methods has been unclear due to theoretical tensions. **Impossibility results** (Karbasi et al., 2025) prove that absolute hallucination detection is computationally equivalent to language identification, requiring expert-labeled negative examples (14 citations). This appears to contradict the empirical success of SelfCheckGPT-style methods.

We resolve this paradox by recognizing that consistency methods measure epistemic structure (generative inconsistency), not absolute truth. The impossibility result applies to detecting hallucinations without any oracle; consistency methods implicitly use the model itself as an imperfect oracle through multi-sample agreement. Conformal methods, meanwhile, provide aleatoric bounds through calibration set statistics, not epistemic guarantees. The two methods operate on complementary dimensions.

Recent surveys (Kang et al., 2025) catalog UQ methods but note the lack of unified theoretical frameworks (11 citations). Our work addresses this gap by formalizing the relationship between epistemic (consistency) and aleatoric (conformal) uncertainty, showing they capture distinct information with moderate correlation (ρ ≈ 0.43-0.46), enabling hierarchical Bayesian integration.

## Positioning of Our Work

Our hierarchical Bayesian calibration (HBC) framework differs from prior work in three key aspects:

1. **vs. SelfCheckGPT**: We extend consistency-only detection by integrating with statistical calibration, providing both epistemic signals and coverage guarantees. HBC achieves ECE = 0.043 (vs. no calibration metric for SelfCheckGPT).

2. **vs. COIN**: We reduce computational cost by 30% through consistency-informed conformal scoring, while maintaining 92% coverage. COIN achieves coverage but at ~4000 forward passes per 1000 queries; HBC uses consistency priors to reduce calibration requirements.

3. **vs. Independent Cascade**: We implement joint calibration via Bayesian updating (consistency informs conformal prior, coverage updates consistency threshold), not independent tuning. This mutual calibration exploits complementarity (ρ ≈ 0.43) to improve both signals beyond cascade performance.

Our theoretical contribution is formalizing complementarity: by quantifying correlation between consistency and conformal signals (ρ ≈ 0.43-0.46 across datasets), we establish empirical bounds (0.3 < ρ < 0.7) for when joint calibration provides value over independent application.
