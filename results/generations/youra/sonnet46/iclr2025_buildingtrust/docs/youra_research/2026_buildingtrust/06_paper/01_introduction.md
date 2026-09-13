# Introduction

We trained an LLM to be helpful and harmless. In doing so, we made it unable to reliably identify the same answer as its pretrained counterpart. For 99.7% of MMLU multiple-choice questions — 13,998 of 14,042 items — a PPO-trained Pythia 1.4B model selects a different answer option than its base model. Its rank-ordering of the four answer choices correlates with the base model's at Spearman ρ = −0.324: the aligned model has learned to systematically *prefer* the options that the base model considered *least* likely.

This is not overconfidence in the sense that calibration researchers typically mean. Standard miscalibration — deep networks expressing 90% confidence when they are correct 70% of the time \cite{guo2017calibration} — involves inflated probability mass on whichever answer the model already preferred. What we observe is different: alignment training restructures *which* answer the model prefers, not merely how strongly. The consequences for calibration correction are profound: temperature scaling and other post-hoc methods designed for confidence inflation fail by design when the underlying miscalibration is an answer-switching phenomenon.

## The Problem at Three Levels

**At the surface level,** aligned LLMs are dangerously overconfident. Xie et al. \cite{xie2024ats} measured ECE = 0.298 on MMLU for LLaMA-2-Chat — more than double its base model's calibration error. Li et al. \cite{li2024rlhf} showed that RLHF alignment can *reduce* truthfulness accuracy by roughly 25% relative to SFT. The combination — lower accuracy with higher confidence — defines a safety-critical reliability failure mode.

**At the technical level,** existing approaches to understanding and correcting alignment-induced miscalibration make an implicit assumption: that alignment training amplifies the model's confidence in answers it already preferred, a monotonic scale distortion (H1). Under H1, calibration correction amounts to learning a rescaling function — which is precisely what temperature scaling and Adaptive Temperature Scaling (ATS, \cite{xie2024ats}) implement. But if alignment instead *restructures* which answers rank first (H2: decision-boundary shift), then the correction problem is fundamentally different: you cannot rescale your way out of a systematic answer-selection reordering.

**At the fundamental level,** the question of *which mechanism* drives alignment-induced miscalibration has never been directly tested with pre-specified, falsifiable predictions. Prior work has established that miscalibration occurs \cite{xie2024ats, chhikara2025confidence}; it has not established *how* it occurs in the logit space. This mechanistic gap limits our ability to design targeted corrections and to predict how calibration will degrade as alignment methods evolve.

## Why Existing Approaches Fall Short

Three prior lines of work bracket our contribution without filling it:

**Xie et al. 2024 \cite{xie2024ats}** confirms that RLHF degrades calibration for LLaMA-2-Chat and proposes ATS as a correction. ATS works by learning a per-input temperature function from the model's hidden states. However, ATS was designed and evaluated under an implicit H1 assumption: that calibration can be corrected by modulating confidence magnitudes. Our finding that the dominant mechanism is H2 (boundary restructuring) raises the question of whether ATS succeeds by correcting H1-type distortions, or whether it can also undo H2-type answer-reordering — a question our work directly motivates.

**Li et al. 2024 \cite{li2024rlhf}** provides the Pythia alignment ladder (SFT, DPO, PPO on HH data) and shows RLHF has inconsistent effects on trustworthiness dimensions (toxicity, truthfulness, bias). Li et al. do not measure ECE or Brier calibration — our work fills this gap using the same model family with a focus on the calibration component of trustworthiness and its mechanism.

**Chhikara et al. 2025 \cite{chhikara2025confidence}** study calibration across 9 LLMs using *verbally elicited* confidence (self-reported 0–100 scale), finding paradoxically increased miscalibration on easier queries for larger RLHF models. Verbal confidence calibration and softmax-based log-probability ECE measure different quantities. Our work demonstrates that the framing-susceptibility effects observed with verbal confidence (H3) do *not* appear in softmax log-probability ECE — the MMLU ΔECE consistently exceeds TruthfulQA ΔECE for all alignment types in our study.

## Our Approach and Key Insight

We conduct a fully controlled paired study on the Pythia alignment ladder (1.4B, 2.8B, 6.9B × base, SFT, DPO, PPO — 12 models total) evaluated on MMLU (14,042 items, 4-shot log-probability continuation via lm-eval-harness v0.4.11). We pre-register three competing mechanistic hypotheses:

- **H1 (Scale distortion):** Alignment amplifies confidence on existing answers; Spearman ρ ≥ 0.90 between base and aligned option log-probs.
- **H2 (Boundary shift):** Alignment restructures which answer ranks first; Spearman ρ < 0.85; argmax redistribution dominates.
- **H3 (Framing susceptibility):** Calibration degradation is framing-sensitive; TruthfulQA ΔECE exceeds MMLU ΔECE.

The **key insight** emerging from our experiments: **H2 is the dominant mechanism.** All 9 alignment-base pairs show Spearman ρ < 0.90; 8 of 9 fall below 0.85. Framing susceptibility (H3) is definitively ruled out. Alignment training on Pythia 1.4B–6.9B does not scale the model's existing answer preferences — it reorganizes them.

## Contributions

We make the following contributions:

- **Mechanistic discrimination framework:** A pre-registered H1/H2/H3 discrimination test using Spearman ρ thresholds and argmax partition analysis, applicable to any model family via lm-eval-harness without code changes.

- **H2 confirmed as dominant mechanism:** 0 of 9 alignment-base pairs achieve Spearman ρ ≥ 0.90; 8 of 9 show ρ < 0.85. PPO alignment causes near-complete argmax redistribution for the 1.4B model (99.7%; ρ = −0.324).

- **Counter-intuitive ordering:** DPO produces strictly larger calibration degradation than PPO in all three Pythia sizes (ΔReliability: 1.4B DPO = 0.1048, PPO = 0.0406; 2.8B DPO = 0.0437, PPO = 0.0423; 6.9B DPO = 0.0099, PPO = −0.0036). We hypothesize this reflects DPO's token-level direct preference reshaping being less KL-constrained than PPO's sequence-level reward optimization.

- **H3 definitively ruled out:** TruthfulQA ΔECE is consistently smaller than MMLU ΔECE for all alignment types (ratio 0.26–0.73), confirming that alignment-induced calibration degradation in softmax ECE is domain-general rather than framing-specific.

- **Clean causal baseline:** Pythia base models show ECE = 0.057–0.085 (well below 0.15 across all three sizes), providing unambiguous attribution of downstream miscalibration to alignment training.

## Paper Organization

Section 2 reviews related work on LLM calibration, RLHF trustworthiness, and post-hoc calibration correction. Section 3 defines our formal framework, the three competing mechanisms, and the discrimination tests. Section 4 describes the experimental setup. Section 5 presents results. Section 6 discusses mechanistic interpretation, limitations, and implications for calibration correction design. Section 7 concludes.
