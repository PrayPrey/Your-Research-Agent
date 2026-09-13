# Related Work

Our work connects three research threads: neural network calibration methods, RLHF training dynamics and their effects on model behavior, and uncertainty quantification in large language models. We position our contribution relative to each, highlighting how existing work—while valuable—leaves the discriminative degradation problem unaddressed.

## Neural Network Calibration

The modern study of neural network calibration was catalyzed by Guo et al. [2017], who demonstrated that deep networks are often miscalibrated despite high accuracy, and that simple temperature scaling can substantially reduce Expected Calibration Error (ECE). This foundational work established temperature scaling as the default post-hoc calibration method, with subsequent extensions including histogram binning [Zadrozny and Elkan, 2001], isotonic regression [Niculescu-Mizil and Caruana, 2005], and focal loss training [Mukhoti et al., 2020].

Recent work has extended calibration methods to large language models. DACA [Luo et al., 2025] leverages disagreement between a pre-trained LM and a post-trained LM to detect samples requiring calibration, achieving 15% ECE improvement on MMLU. CCPS [Khanmohammadi et al., 2025] uses consistency under perturbation as a calibration signal, reducing ECE by 55% on standard benchmarks. ActCab [Liu et al., 2024] targets TruthfulQA with activation-based calibration, achieving 39% ECE reduction.

**Limitation:** These methods focus on ECE as the primary metric, which measures calibration (do predicted probabilities match observed frequencies?) rather than discrimination (can the model distinguish correct from incorrect predictions based on confidence?). Our work shows that ECE can improve while AUROC degrades—a failure mode invisible to calibration-centric evaluation.

## RLHF Training and Overconfidence

Reinforcement Learning from Human Feedback (RLHF) has become the dominant paradigm for aligning language models to human preferences [Ouyang et al., 2022; Bai et al., 2022]. The typical pipeline involves supervised fine-tuning (SFT) followed by preference optimization using a reward model trained on human comparisons.

Tian et al. [2023] documented that RLHF-tuned models exhibit systematic overconfidence compared to base models, finding that verbalized confidence (asking the model to state its confidence) often outperforms token-level probabilities for RLHF models. This suggests that RLHF disrupts the relationship between internal confidence signals and correctness. Kadavath et al. [2022] explored self-evaluation capabilities in language models, showing that models can assess their own uncertainty but that this ability is affected by training procedures.

Recent work has begun investigating the mechanisms underlying RLHF effects. Rafailov et al. [2023] introduced Direct Preference Optimization (DPO), which implicitly optimizes the same objective as RLHF without explicit reward modeling. Studies of DPO have shown it produces similar behavioral patterns to RLHF, including potential overconfidence [Xu et al., 2024].

**Limitation:** While these works document overconfidence, they do not characterize the type of distortion (scalar vs. geometric) or measure discriminative quality directly. The implicit assumption is that overconfidence is a scale shift correctable by temperature scaling—an assumption we empirically challenge.

## Uncertainty Quantification in LLMs

Uncertainty quantification in language models has received increasing attention as deployment scales. Kuhn et al. [2023] introduced semantic entropy as a measure of uncertainty that accounts for meaning equivalence across generations. Lin et al. [2022] studied selective prediction, showing that models can improve accuracy by abstaining on low-confidence predictions when confidence signals are reliable.

The Brier score decomposition framework [Murphy, 1973; DeGroot and Fienberg, 1983] provides a principled way to separate calibration (reliability) from discrimination (refinement). While widely used in meteorological forecasting and medical diagnosis, this decomposition has seen limited application to LLM confidence analysis. Notably, reliability and refinement can move independently: a model can become better calibrated while losing discriminative ability, or vice versa.

**Limitation:** Existing uncertainty quantification work typically treats confidence signals as given and focuses on how to use them effectively. Our work addresses the upstream question of whether RLHF corrupts these signals in ways that limit their usefulness.

## Positioning Our Contribution

We bridge these threads by asking a question that falls between them: *Does RLHF cause scalar or geometric distortion of confidence signals?* This question connects calibration (scalar shift → temperature scaling can fix) to uncertainty quantification (geometric distortion → discriminative ability lost) to RLHF analysis (mechanism → margin inflation for incorrect predictions).

Our methodological contribution—using AUROC as a discriminative metric, percentile normalization to isolate geometric effects, and Brier decomposition for independent confirmation—provides tools that complement rather than replace ECE-based calibration analysis. The finding that RLHF causes geometric distortion has direct implications for all three research threads:

- For calibration research: Temperature scaling is necessary but not sufficient for RLHF models
- For RLHF research: Preference optimization has confidence consequences beyond overconfidence
- For uncertainty quantification: Discriminative quality should be evaluated alongside calibration

To our knowledge, this is the first systematic study of discriminative degradation under RLHF, providing both a characterization framework (geometric vs. scalar) and empirical evidence across multiple model families.
