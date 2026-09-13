# On the Effect of Uncertainty on Layer-wise Inference Dynamics

## Key Metadata
- **Authors:** Sunwoo Kim et al. (KAIST; with Haneul Yoo, Alice Oh)
- **Year:** 2025
- **Venue:** ICML 2025 (PMLR 267)
- **Core Contribution:** Adversarial finding — layer-wise probability trajectories of final prediction tokens (via Tuned Lens) are largely ALIGNED for certain vs uncertain (correct vs incorrect) predictions, challenging simplistic layer-trajectory-based uncertainty detection.

## Section Summaries

### Abstract
Understanding how large language models (LLMs) internally represent and process their predictions is central to detecting uncertainty and preventing hallucinations. While several studies have shown that models encode uncertainty in their hidden states, it is underexplored how this affects the way they process such hidden states. In this work, we demonstrate that the dynamics of output token probabilities across layers for certain and uncertain outputs are largely aligned, revealing that uncertainty does not seem to affect inference dynamics. Specifically, we use the Tuned Lens, a variant of the Logit Lens, to analyze the layer-wise probability trajectories of final prediction tokens across 11 datasets and 5 models. Using incorrect predictions as those with higher epistemic uncertainty, our results show aligned trajectories for certain and uncertain predictions that both observe abrupt increases in confidence at similar layers. We balance this finding by showing evidence that more competent models may learn to process uncertainty differently. Our findings challenge the feasibility of leveraging simplistic methods for detecting uncertainty at inference.

### Introduction & Motivation
Prior mechanistic-interpretability work shows models ENCODE uncertainty in hidden states (probes, SAEs), but whether uncertainty changes HOW models process — their inference dynamics — is unexplored. If uncertain outputs used layers differently, that difference could itself be a detection signal. Two RQs: (RQ1) does uncertainty affect inference dynamics? (RQ2) does model competence modulate this adaptivity? Focus is epistemic uncertainty, operationalized as incorrect answers on multiple-choice questions.

### Methodology
[DETAILED] Uses **Tuned Lens** (Belrose et al. 2023 — per-layer trained affine probes decoding residual-stream hidden states to vocabulary logits) on single-token answers to multiple-choice questions. Two analyses: (1) **Probability trajectory analysis** — softmax over ONLY the answer-label token logits per layer; for each question, extract the trajectory of the label ranked top at the FINAL layer, condense remaining labels into one trajectory; average separately over correctly and incorrectly answered questions → 4 average trajectories per model (top/low rank × correct/incorrect). (2) **Prediction depth (PD) analysis** (Baldock et al. 2021) — earliest layer where the top prediction differs from the previous layer's and persists through all subsequent layers; compute Pearson correlation of answer incorrectness with PD per model-dataset pair; relate Cohen's Kappa (chance-adjusted accuracy) to the correct-vs-incorrect mean-PD gap. Models: Llama-3-8B, Llama-3-8B-Instruct, Vicuna-13B (pre-trained lenses); Mistral-7B-Instruct-v0.1, Mistral-Nemo-Instruct-2407 (newly trained lenses). Datasets: ANLI, ARC, BoolQ, CommonsenseQA, HellaSwag, LogiQA, MMLU, QASC, QuAIL, RACE, SciQ (11 tasks, MCQ format).

### Experiments & Results
[DETAILED] **Main negative result:** average probability trajectories for correct and incorrect predictions are strikingly aligned — both show abrupt confidence increases at the SAME layers; the incorrect-question top trajectory sits consistently lower after the jump but never diverges qualitatively. PD distributions peak at the same layers regardless of correctness — the model commits at similar depth whether right or wrong. **Correlations (Table 1):** Pearson correlation between incorrectness and PD is weak — 80% of model×dataset cells below 0.300 — but 97% positive (range roughly −0.17 to 0.48; e.g., Llama-3-8B: ARC-Easy 0.449, SciQ 0.480, HellaSwag 0.010; Mistral-Nemo: ANLI-R2 0.464). **Competence effect (Figure 3):** per-dataset Kappa correlates positively with the correct-vs-incorrect PD gap; statistically significant (p < 0.05) for Llama-3-8B and Mistral-7B-Instruct, p = 0.06 for Llama-3-8B-Instruct — preliminary evidence that adaptive inference dynamics emerge with competence.

### Discussion & Conclusion
Inference is characterized by abrupt decision-making largely unaffected by uncertainty; simplistic trajectory-based uncertainty detection is challenged. But weak-yet-consistent positive PD-incorrectness correlations and the competence effect leave room for signal. Future work: more/larger models, varying uncertainty levels, hallucination on known knowledge, aleatoric uncertainty.

## Key Contributions
- Layer-wise final-prediction-token probability trajectories are aligned across certain/uncertain outputs (5 models × 11 MCQ datasets) — an adversarial bound for trajectory-based detection.
- Prediction depth correlates weakly (mostly < 0.3) but near-universally positively (97%) with incorrectness.
- Competence effect: better task performance (Kappa) → larger PD gap between correct/incorrect, significant for 2/5 models.

## Potential Relevance
This is the KEY ADVERSARIAL paper for our hypothesis and must shape falsifiability framing. Critical scoping: it tracks the FINAL-prediction-token probability trajectory (a single token's probability across layers, via TUNED lens, on MCQ single-token answers) — NOT per-layer full-distribution statistics (entropy, max-prob over the whole vocabulary, adjacent-layer KL) with per-model layer selection and AUROC direction correction on open-ended QA. The weak-but-consistent positive PD correlations (up to 0.48 on SciQ/ARC-Easy) actually DEMONSTRATE that depth-of-commitment carries some correctness signal. Our hypothesis must explain why per-layer distributional statistics could succeed where final-token trajectories aligned: full-vocabulary entropy captures candidate-set breadth (see Entropy-Lens), not just one token's probability path. If our per-layer signals fail on LLaMA-2, Kim et al.'s alignment result would be the parsimonious explanation.
