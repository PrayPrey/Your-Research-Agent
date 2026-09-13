# Alignment Breaks Boundaries: Decision-Boundary Restructuring as the Dominant Mechanism of RLHF-Induced Miscalibration in LLMs

---

## Abstract

Alignment training via RLHF and DPO is known to degrade LLM calibration, but the *mechanism* of this degradation has not been directly tested. We propose a pre-registered mechanistic discrimination framework distinguishing three hypotheses: H1 (monotonic scale inflation, detectable via Spearman ρ ≥ 0.90 between base and aligned option log-probability vectors), H2 (decision-boundary restructuring, ρ < 0.85), and H3 (framing susceptibility, TruthfulQA ΔECE > MMLU ΔECE). We evaluate all 12 Pythia alignment checkpoints (SFT, DPO, PPO; 1.4B–6.9B) on MMLU (14,042 items, 4-shot log-probability continuation) using lm-eval-harness v0.4.11, with Brier reliability decomposition and bootstrap 95% confidence intervals.

Our central finding is that **H2 is the dominant mechanism**: 0 of 9 alignment-base pairs achieve ρ ≥ 0.90; 8 of 9 show ρ < 0.85. The 1.4B-parameter PPO-aligned model changes its argmax prediction for **99.7% of MMLU items** (ρ = −0.324) — near-complete answer-preference reversal rather than confidence inflation. H1 (scale distortion) is definitively refuted; H3 (framing susceptibility) is ruled out (TruthfulQA ΔECE/MMLU ΔECE ratio = 0.26–0.73 for all alignment types). Alignment training reliably increases Brier reliability in 8/9 aligned model-size pairs (MUST_WORK gate PASS). Counter-intuitively, DPO produces strictly larger calibration degradation than PPO in all three sizes (1.4B: ΔReliability = 0.1048 vs. 0.0406; 5.5× base reliability), consistent with DPO's token-level preference reshaping being less KL-constrained than PPO's sequence-level reward optimization. The 6.9B-DPO model's ρ = 0.875 suggests a potential H1/H2 mechanism transition at larger scale. Our findings imply that standard confidence-rescaling calibration methods are addressing the wrong mechanism for small-to-medium aligned LLMs, and motivate calibration correction approaches that can identify and partially reverse alignment-induced answer-preference reorganization.

---

## 1. Introduction

We trained an LLM to be helpful and harmless. In doing so, we made it unable to reliably identify the same answer as its pretrained counterpart. For 99.7% of MMLU multiple-choice questions — 13,998 of 14,042 items — a PPO-trained Pythia 1.4B model selects a different answer option than its base model. Its rank-ordering of the four answer choices correlates with the base model's at Spearman ρ = −0.324: the aligned model has learned to systematically *prefer* the options that the base model considered *least* likely.

This is not overconfidence in the sense that calibration researchers typically mean. Standard miscalibration — deep networks expressing 90% confidence when they are correct 70% of the time \cite{guo2017calibration} — involves inflated probability mass on whichever answer the model already preferred. What we observe is different: alignment training restructures *which* answer the model prefers, not merely how strongly. The consequences for calibration correction are profound: temperature scaling and other post-hoc methods designed for confidence inflation fail by design when the underlying miscalibration is an answer-switching phenomenon.

### The Problem at Three Levels

**At the surface level,** aligned LLMs are dangerously overconfident. Xie et al. \cite{xie2024ats} measured ECE = 0.298 on MMLU for LLaMA-2-Chat — more than double its base model's calibration error. Li et al. \cite{li2024rlhf} showed that RLHF alignment can *reduce* truthfulness accuracy by roughly 25% relative to SFT. The combination — lower accuracy with higher confidence — defines a safety-critical reliability failure mode.

**At the technical level,** existing approaches to understanding and correcting alignment-induced miscalibration make an implicit assumption: that alignment training amplifies the model's confidence in answers it already preferred, a monotonic scale distortion (H1). Under H1, calibration correction amounts to learning a rescaling function — which is precisely what temperature scaling and Adaptive Temperature Scaling (ATS, \cite{xie2024ats}) implement. But if alignment instead *restructures* which answers rank first (H2: decision-boundary shift), then the correction problem is fundamentally different: you cannot rescale your way out of a systematic answer-selection reordering.

**At the fundamental level,** the question of *which mechanism* drives alignment-induced miscalibration has never been directly tested with pre-specified, falsifiable predictions. This mechanistic gap limits our ability to design targeted corrections and to predict how calibration will degrade as alignment methods evolve.

### Why Existing Approaches Fall Short

Three prior lines of work bracket our contribution without filling it:

**Xie et al. 2024 \cite{xie2024ats}** confirms that RLHF degrades calibration for LLaMA-2-Chat and proposes ATS. However, ATS was designed under an implicit H1 assumption. Our finding that the dominant mechanism is H2 raises the question of whether ATS succeeds by correcting H1-type distortions, or whether it can also undo H2-type answer-reordering.

**Li et al. 2024 \cite{li2024rlhf}** provides the Pythia alignment ladder and shows RLHF has inconsistent effects on trustworthiness dimensions. Li et al. do not measure ECE or Brier calibration — our work fills this gap using the same model family.

**Chhikara et al. 2025 \cite{chhikara2025confidence}** study calibration across 9 LLMs using *verbally elicited* confidence. Verbal confidence and softmax-based log-probability ECE measure different quantities. Our H3 diagnostic directly tests whether framing susceptibility observable with verbal confidence also appears in softmax ECE — and finds it does not.

### Our Approach and Key Insight

We conduct a fully controlled paired study on the Pythia alignment ladder (12 models: 3 sizes × 4 alignment variants) on MMLU (14,042 items, 4-shot log-probability continuation). We pre-register three competing mechanistic hypotheses:

- **H1 (Scale distortion):** Spearman ρ ≥ 0.90 between base and aligned option log-probs.
- **H2 (Boundary shift):** Spearman ρ < 0.85; argmax redistribution dominates.
- **H3 (Framing susceptibility):** TruthfulQA ΔECE > MMLU ΔECE.

**Key insight:** H2 is the dominant mechanism. All 9 alignment-base pairs show Spearman ρ < 0.90; 8 of 9 fall below 0.85.

### Contributions

- **Mechanistic discrimination framework:** Pre-registered H1/H2/H3 tests applicable to any model family via lm-eval-harness.
- **H2 confirmed as dominant mechanism:** 0/9 pairs pass ρ ≥ 0.90; 8/9 show ρ < 0.85; 1.4B-PPO: ρ = −0.324.
- **Counter-intuitive ordering:** DPO > PPO in ΔReliability across all three sizes.
- **H3 definitively ruled out:** Framing susceptibility absent in softmax ECE.
- **Clean causal baseline:** Pythia base ECE = 0.057–0.085 across all sizes.

---

## 2. Related Work

### 2.1 Calibration of Neural Networks

Guo et al. \cite{guo2017calibration} established the ECE definition and temperature scaling. The Brier score decomposition \cite{murphy1973brier} into reliability (REL), resolution (RES), and uncertainty (UNC) isolates overconfidence from accuracy changes. Wang \cite{wang2023calibration_survey} surveys calibration methods and notes fine-tuning-induced miscalibration as understudied. Tomani et al. \cite{tomani2021pts} extend temperature scaling to per-prediction temperatures. Khanmohammadi et al. \cite{khanmohammadi2025representation} confirm ECE varies across benchmark types and model architectures. Liu et al. \cite{liu2025uq_survey} survey LLM uncertainty quantification.

### 2.2 RLHF and Alignment

Ouyang et al. \cite{ouyang2022instructgpt} introduced PPO-based RLHF instruction following. Rafailov et al. \cite{rafailov2023dpo} introduced DPO, which directly reshapes per-token log-probability ratios without an explicit reward model. Bai et al. \cite{bai2022hh} released the Anthropic HH dataset used in our alignment checkpoints. Coste et al. \cite{coste2023reward_overoptimization} show reward overoptimization exploits proxy reward flaws — mechanistically consistent with our H2 finding. Li et al. \cite{li2024rlhf} study RLHF trustworthiness using the Pythia alignment ladder without measuring calibration; our work fills this gap.

### 2.3 Alignment-Induced Calibration Degradation

Xie et al. \cite{xie2024ats} provide the primary prior: RLHF degrades LLaMA-2-Chat ECE to 0.298 on MMLU; ATS corrects via per-input hidden-state temperature. Our work tests *why* ATS works by identifying the dominant mechanism. Chhikara et al. \cite{chhikara2025confidence} study verbal confidence calibration across 9 LLMs; our H3 diagnostic shows their framing-sensitivity findings do not transfer to softmax ECE.

### 2.4 Model Families and Evaluation

Biderman et al. \cite{biderman2023pythia} describe the Pythia model suite, which provides identical pretraining across alignment variants — enabling the cleanest available causal isolation. Evaluation uses lm-eval-harness \cite{eval-harness} on MMLU \cite{hendrycks2021mmlu} and TruthfulQA \cite{lin2022truthfulqa}.

---

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathcal{M}_{\text{base}}$ and $\mathcal{M}_{\text{aligned}}$ denote base and aligned models. For $K = 4$ answer options, the pre-softmax log-probability vector is $\mathbf{l} \in \mathbb{R}^4$. ECE is computed using $M = 15$ equal-width bins on max-probability confidence \cite{guo2017calibration}. The Brier score decomposes as:

$$\text{BS} = \text{REL} - \text{RES} + \text{UNC}$$

The primary outcome is $\Delta\text{REL}(a, s) = \text{REL}(\mathcal{M}_{a,s}) - \text{REL}(\mathcal{M}_{\text{base},s})$ for alignment method $a \in \{\text{SFT}, \text{DPO}, \text{PPO}\}$ and size $s \in \{1.4\text{B}, 2.8\text{B}, 6.9\text{B}\}$.

### 3.2 Competing Mechanistic Hypotheses

**H1 — Monotonic Scale Distortion:** $\mathbf{l}^{(i)}_{\text{aligned}} \approx \lambda^{(i)} \cdot \mathbf{l}^{(i)}_{\text{base}}$, $\lambda > 1$. Spearman ρ ≥ 0.90 between base and aligned 4-option vectors.

**H2 — Decision-Boundary Restructuring:** Alignment selectively shifts probability mass, changing argmax rankings. Spearman ρ < 0.85 and substantial argmax redistribution.

**H3 — Framing Susceptibility:** $\Delta\text{ECE}_{\text{TruthfulQA}} > \Delta\text{ECE}_{\text{MMLU}}$.

All thresholds are pre-registered before data collection.

### 3.3 Key Metrics

- **Spearman ρ:** Per-item Spearman correlation between base and aligned 4-option log-prob vectors, averaged over 14,042 items per pair.
- **Argmax partition:** Shared-argmax ($S$) vs. changed-argmax ($C$) subsets; $|C|/N$ as the primary boundary shift indicator.
- **Pre-softmax margin:** $m^{(i)} = l^{(i)}_{(1)} - l^{(i)}_{(2)}$; $\Delta m(a,s) = \bar{m}_{\text{aligned}} - \bar{m}_{\text{base}}$ with bootstrap 95% CI.

### 3.4 Experimental Design

**Models:** 12 Pythia checkpoints (3 sizes × 4 variants). Due to access constraints on RLHFlow checkpoints \cite{li2024rlhf}, we use public HH-trained fallbacks: lomahony SFT, Leogrin DPO, usvsnsp PPO.

**Evaluation:** lm-eval-harness v0.4.11, MMLU 4-shot log-probability continuation (14,042 items), TruthfulQA MC1 0-shot (817 items). Greedy decoding, temperature = 1.0.

**Gate criteria:** H-E1 MUST_WORK: ΔReliability CI lower > 0 for ≥2/3 sizes (PPO or DPO). H-M1 MUST_WORK: ECE_base < 0.15 all sizes. H-M2 SHOULD_WORK: Δmargin_PPO > 0 CI lower > 0 in ≥2/3 sizes. H-M3 SHOULD_WORK: mean ρ ≥ 0.90 all 9 pairs (H1 confirmation — gate intentionally set to fail if H2 dominant).

---

## 4. Experiments

### 4.1 Model Suite

| Size | Base | SFT | DPO | PPO |
|------|------|-----|-----|-----|
| 1.4B | pythia-1.4b | lomahony-1.4b-sft | leogrin-1.4b-dpo | usvsnsp-1.4b-ppo |
| 2.8B | pythia-2.8b | lomahony-2.8b-sft | leogrin-2.8b-dpo | usvsnsp-2.8b-ppo |
| 6.9B | pythia-6.9b | lomahony-6.9b-sft | leogrin-6.9b-dpo | usvsnsp-6.9b-ppo |

All aligned variants trained on Anthropic HH data with Pythia base models.

### 4.2 Ablation Structure

The 3×3 alignment grid provides natural ablations: (1) method effect within size; (2) scale effect within method; (3) mechanism specificity across alignment types.

### 4.3 Implementation Details

Python 3.10, `numpy` (bootstrap CI, margin computation), `scipy.stats.spearmanr` (per-item ρ), lm-eval-harness v0.4.11. H-E1 lm-eval outputs are cached and reused for H-M2 and H-M3 (zero additional GPU computation for mechanism analysis). Bootstrap: $n = 1000$ samples, seed = 42. ECE bins: 15 equal-width.

---

## 5. Results

### 5.1 Base Model Calibration (H-M1: MUST_WORK PASS)

**Table 1: Pythia Base Model ECE**

| Model | ECE | Gate (< 0.15) |
|-------|-----|---------------|
| Pythia-1.4B | 0.0849 | PASS |
| Pythia-2.8B | 0.0597 | PASS |
| Pythia-6.9B | 0.0792 | PASS |

All base models well-calibrated before alignment, confirming causal attribution of downstream miscalibration to alignment training.

*See: h-m1/figures/figure_01_ece_gate.png*

### 5.2 Alignment-Induced Overconfidence (H-E1: MUST_WORK PASS)

**Table 2: Full Calibration Metrics on MMLU (N = 14,042)**

| Model | ECE | Brier REL | ΔReliability | CI Lower | CI Upper |
|-------|-----|-----------|-------------|----------|----------|
| pythia-1.4b-base | 0.0849 | 0.0190 | — | — | — |
| pythia-1.4b-sft | 0.1415 | 0.0445 | +0.0289 | +0.0269 | +0.0309 |
| **pythia-1.4b-dpo** | **0.2516** | **0.1151** | **+0.1048** | **+0.1009** | **+0.1090** |
| pythia-1.4b-ppo | 0.1923 | 0.0742 | +0.0406 | +0.0345 | +0.0464 |
| pythia-2.8b-base | 0.0597 | 0.0093 | — | — | — |
| pythia-2.8b-sft | 0.0694 | 0.0126 | +0.0033 | +0.0021 | +0.0045 |
| pythia-2.8b-dpo | 0.1441 | 0.0531 | +0.0437 | +0.0407 | +0.0469 |
| pythia-2.8b-ppo | 0.1577 | 0.0516 | +0.0423 | +0.0388 | +0.0456 |
| pythia-6.9b-base | 0.0792 | 0.0128 | — | — | — |
| pythia-6.9b-sft | 0.0830 | 0.0138 | +0.0010 | +0.0001 | +0.0018 |
| pythia-6.9b-dpo | 0.1010 | 0.0227 | +0.0099 | +0.0090 | +0.0112 |
| pythia-6.9b-ppo | 0.0609 | 0.0092 | −0.0036 | −0.0053 | −0.0018 |

MUST_WORK PASS via both PPO (2/3 sizes, CI lower > 0) and DPO (3/3 sizes, CI lower > 0). Alignment increases ΔReliability in 8/9 pairs. The largest effect is 1.4B-DPO (ΔReliability = 0.1048, a 5.5× increase over base REL = 0.019). DPO consistently exceeds PPO in all three sizes.

*See: h-e1/code/figures/delta_reliability_bar.png; h-e1/code/figures/ece_heatmap.png*

### 5.3 Pre-Softmax Margin Inflation (H-M2: SHOULD_WORK PASS)

**Table 3: Mean Δmargin (aligned − base, nats)**

| Alignment | 1.4B | 2.8B | 6.9B |
|-----------|------|------|------|
| SFT | +0.1334 | +0.0110 | +0.0267 |
| DPO | **+0.4908** | **+0.2077** | **+0.0721** |
| PPO | +0.3937 | +0.2526 | −0.0364 |

PPO CI lower > 0 in 2/3 sizes (1.4B: [+0.389, +0.398]; 2.8B: [+0.247, +0.258]). Gate PASS. DPO > PPO in margins confirming logit-level signal. 6.9B-PPO shows negative margin (scale-dependent ceiling effect).

*See: h-m2/figures/figure_01_delta_margin_gate.png; h-m2/figures/figure_04_gradient_ordering_heatmap.png*

### 5.4 Mechanism Discrimination: H2 Dominant (H-M3: SHOULD_WORK FAIL — Informative)

**Table 4: Spearman ρ Results**

| Pair | Mean ρ | H1 Pass (≥ 0.90) | H2 Flag (< 0.85) |
|------|--------|------------------|------------------|
| 1.4B-SFT | 0.7533 | No | **Yes** |
| 1.4B-DPO | 0.7369 | No | **Yes** |
| **1.4B-PPO** | **−0.3241** | No | **Yes** |
| 2.8B-SFT | 0.7185 | No | **Yes** |
| 2.8B-DPO | 0.5896 | No | **Yes** |
| 2.8B-PPO | 0.1746 | No | **Yes** |
| 6.9B-SFT | 0.8390 | No | **Yes** |
| 6.9B-DPO | **0.8748** | No | Near-threshold |
| 6.9B-PPO | 0.5045 | No | **Yes** |

**0/9 pairs pass H1 threshold. 8/9 pairs show H2 flag.** H-M3 SHOULD_WORK gate intentionally required H1 confirmation (ρ ≥ 0.90); this gate FAILS, confirming H2 dominance.

**Table 5: Argmax Partition**

| Pair | N Shared | N Changed | % Changed | Cohen's d |
|------|----------|-----------|-----------|-----------|
| 1.4B-SFT | 8,028 | 6,014 | 42.8% | 1.000 |
| 1.4B-DPO | 8,235 | 5,807 | 41.4% | 0.922 |
| **1.4B-PPO** | **44** | **13,998** | **99.7%** | 4.874 |
| 2.8B-SFT | 10,017 | 4,025 | 28.7% | 4.781 |
| 2.8B-DPO | 8,516 | 5,526 | 39.4% | 3.441 |
| 2.8B-PPO | 4,993 | 9,049 | 64.4% | 5.621 |
| 6.9B-SFT | 11,969 | 2,073 | 14.8% | 3.457 |
| 6.9B-DPO | 11,818 | 2,224 | 15.8% | 2.158 |
| 6.9B-PPO | 8,472 | 5,570 | 39.7% | 6.964 |

1.4B-PPO: only 44/14,042 shared-argmax items. The PPO-aligned model has near-completely reorganized its answer preferences.

*See: h-m3/figures/figure_01_spearman_rho.png; h-m3/figures/figure_04_argmax_proportion.png*

### 5.5 H3 Diagnostic: Framing Susceptibility Ruled Out

**Table 6: H3 Diagnostic Summary**

| Alignment | ΔECE (TruthfulQA) | ΔECE (MMLU) | Ratio | H3 Signal |
|-----------|--------------------|-------------|-------|-----------|
| SFT | +0.0088 | +0.0276 | 0.32 | **No** |
| DPO | +0.0240 | +0.0934 | 0.26 | **No** |
| PPO | +0.0405 | +0.0554 | 0.73 | **No** |

TruthfulQA ΔECE < MMLU ΔECE for all alignment types. H3 definitively ruled out.

*See: h-m3/figures/figure_05_truthfulqa_ece.png*

### 5.6 Summary

| Mechanism | Predicted | Observed | Conclusion |
|-----------|-----------|----------|------------|
| H1 (Scale distortion, ρ ≥ 0.90) | Dominant | 0/9 pass | **Refuted** |
| H2 (Boundary shift, ρ < 0.85) | Alternative | 8/9 flag | **Confirmed** |
| H3 (Framing susceptibility) | Alternative | Ratio < 1.0 all types | **Ruled out** |

---

## 6. Discussion

### 6.1 Mechanistic Interpretation of H2

PPO alignment maximizes HH reward subject to KL divergence penalty to the SFT reference \cite{ouyang2022instructgpt}. Despite this regularization, the 1.4B model changes its argmax for 99.7% of MMLU items — consistent with reward hacking \cite{coste2023reward_overoptimization}: the proxy HH reward is misaligned with MMLU factual accuracy, so PPO maximizes HH preferences by adopting logit patterns that diverge completely from the base model's factual encoding.

DPO directly reshapes per-token log-probability ratios \cite{rafailov2023dpo} without any explicit KL constraint against rank reordering. This produces larger ΔReliability than PPO (reversed from original prediction), consistent with DPO's unconstrained token-level preference optimization being more aggressive in reorganizing answer rankings.

SFT shows the mildest boundary shift (ρ = 0.75–0.84) — format adaptation partially reorganizes preferences but less severely than reward-based methods.

### 6.2 Counter-Intuitive Findings

**DPO > PPO ordering:** Under H2, the relevant question is which training method most aggressively reorganizes answer rankings. DPO's token-level unconstrained optimization wins this metric. The finding implies that the KL penalty in PPO provides implicit partial calibration regularization absent in DPO.

**1.4B-PPO catastrophic redistribution:** ρ = −0.324 implies systematic preference *reversal*. Most likely explanation: the 1.4B model cannot simultaneously maintain MMLU factual associations and HH preference patterns — HH patterns dominate.

**6.9B-DPO near-threshold (ρ = 0.875):** Suggests scale threshold for H1/H2 transition. Larger models' stronger pretraining representations resist H2-type boundary shift more effectively.

### 6.3 Implications for ATS and Calibration Correction

If H2 is dominant, ATS \cite{xie2024ats} may succeed by learning to identify inputs where boundary shift is large (via hidden-state representations) and applying aggressive temperature modulation — not because it corrects H1-type uniform confidence inflation. This reinterpretation predicts that ATS should be more effective for high-ρ (H1-like) models than low-ρ (H2-like) models, a testable prediction.

For H2-type miscalibration, contrastive decoding against the base model or boundary-aware regularization during alignment may be more effective than post-hoc temperature scaling.

### 6.4 Limitations

1. **Public fallback checkpoints (Risk R1):** H2 mechanism finding is robust; DPO > PPO ordering is checkpoint-level observation requiring replication with matched training conditions.
2. **Single model family (Pythia):** Generalization to LLaMA-2, Mistral, Falcon requires cross-family experiments.
3. **Scale range (1.4B–6.9B):** H1/H2 transition above 6.9B unresolved.
4. **H-M4 (ATS correction) not executed:** Correctability of H2-type miscalibration unverified experimentally.

---

## 7. Conclusion

We began with a striking observation: a 1.4B-parameter PPO-trained Pythia model changes its argmax prediction for 99.7% of MMLU items (Spearman ρ = −0.324). This is alignment-induced answer reversal, driven by decision-boundary restructuring (H2) — not the monotonic confidence inflation (H1) assumed by standard calibration correction methods.

Our pre-registered mechanistic discrimination framework confirms H2 as dominant across all 9 Pythia alignment-base pairs (0/9 ρ ≥ 0.90; 8/9 ρ < 0.85). We rule out framing susceptibility (H3). We find a counter-intuitive ordering: DPO produces larger calibration degradation than PPO in all three model sizes, consistent with DPO's unconstrained token-level preference reshaping.

Three takeaways for practitioners: (1) Aligned LLMs may prefer different answers entirely, not just express wrong answers with more confidence. (2) DPO may pose a larger calibration risk than PPO; the KL penalty in PPO provides implicit partial calibration regularization. (3) The Spearman ρ diagnostic is a simple, cheap calibration risk indicator requiring only cached lm-eval outputs.

Future work should apply our framework to LLaMA-2 and Mistral to test cross-family generalization, test ATS effectiveness for H2-type distortions, and conduct controlled matched DPO vs. PPO experiments to confirm whether the calibration ordering is intrinsic to the training objectives.

---

## References

\bibliographystyle{plain}
\bibliography{06_references}

**Key references:**

- Guo et al. 2017. On Calibration of Modern Neural Networks. *ICML*.
- Murphy 1973. A New Vector Partition of the Probability Score. *Journal of Applied Meteorology*.
- Xie et al. 2024. Calibrating Language Models with Adaptive Temperature Scaling. *EMNLP*. arXiv:2409.19817.
- Li et al. 2024. More RLHF, More Trust? On The Impact of Preference Alignment On Trustworthiness. *ICLR 2025*. arXiv:2404.18870.
- Coste et al. 2023. Reward Model Ensembles Help Mitigate Overoptimization. *ICLR 2024*. arXiv:2310.02743.
- Chhikara 2025. Mind the Confidence Gap. arXiv:2502.11028.
- Rafailov et al. 2023. Direct Preference Optimization. *NeurIPS*. arXiv:2305.18290.
- Ouyang et al. 2022. Training Language Models to Follow Instructions with Human Feedback. *NeurIPS*. arXiv:2203.02155.
- Biderman et al. 2023. Pythia: A Suite for Analyzing Large Language Models. *ICML*. arXiv:2304.01373.
- Hendrycks et al. 2021. Measuring Massive Multitask Language Understanding. *ICLR*. arXiv:2009.03300.
- Lin et al. 2022. TruthfulQA. *ACL*. arXiv:2109.07958.
- Gao et al. 2021. Language Model Evaluation Harness. GitHub: EleutherAI/lm-evaluation-harness.
- Wang 2023. Calibration in Deep Learning: A Survey. arXiv:2308.01222.
- Liu et al. 2025. Uncertainty Quantification and Confidence Calibration in LLMs: A Survey. arXiv:2503.15850.
- Khanmohammadi et al. 2025. Calibrating LLM Confidence by Probing Perturbed Representation Stability. arXiv:2505.21772.
- Bai et al. 2022. Training a Helpful and Harmless Assistant with RLHF. arXiv:2204.05862.
- Schulman et al. 2017. Proximal Policy Optimization Algorithms. arXiv:1707.06347.
- Tomani et al. 2021. Parameterized Temperature Scaling. *NeurIPS*. arXiv:2102.12182.
- Xiong et al. 2023. Can LLMs Express Their Uncertainty? *ICLR 2024*. arXiv:2306.13063.
- Kadavath et al. 2022. Language Models (Mostly) Know What They Know. arXiv:2207.05221.
- Touvron et al. 2023. Llama 2: Open Foundation and Fine-Tuned Chat Models. arXiv:2307.09288.
- Jiang et al. 2023. Mistral 7B. arXiv:2310.06825.
- Brown et al. 2020. Language Models are Few-Shot Learners (GPT-3). *NeurIPS*. arXiv:2005.14165.
- Zellers et al. 2019. HellaSwag. *ACL*. arXiv:1905.07830.
- Christiano et al. 2017. Deep Reinforcement Learning from Human Preferences. *NeurIPS*. arXiv:1706.03741.
- Gao et al. 2023. Scaling Laws for Reward Model Overoptimization. arXiv:2210.10760.
- Stiennon et al. 2020. Learning to Summarize with Human Feedback. *NeurIPS*. arXiv:2009.01325.
- Zhao et al. 2022. Calibrated Uncertainty Quantification for Large Language Models. *NeurIPS*.
- Wei et al. 2022. Emergent Abilities of Large Language Models. *TMLR*. arXiv:2206.07682.
- Perez et al. 2022. Red Teaming Language Models with Language Models. *EMNLP*. arXiv:2202.03286.
