# Methodology

## 3.1 Problem Formulation

Let $\mathcal{M}_{\text{base}}$ and $\mathcal{M}_{\text{aligned}}$ denote a base pretrained language model and its alignment-trained counterpart (SFT, DPO, or PPO), respectively. For a multiple-choice evaluation task with $K$ answer options, let $\mathbf{l} = (l_1, \ldots, l_K) \in \mathbb{R}^K$ denote the pre-softmax log-probability vector (logits) for the $K$ answer continuations. The predicted probability distribution is $\mathbf{p} = \text{softmax}(\mathbf{l})$, and the predicted answer is $\hat{y} = \arg\max_k p_k$.

For a dataset of $N$ items $\{(x_i, y_i^*)\}_{i=1}^N$, where $y_i^* \in \{1, \ldots, K\}$ is the correct answer, we compute:

$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

where $B_m$ is the $m$-th confidence bin, $\text{acc}(B_m)$ is the fraction of correct answers in the bin, and $\text{conf}(B_m)$ is the mean predicted confidence in the bin. We use $M = 15$ equal-width bins following standard practice \cite{guo2017calibration}.

**Brier score decomposition.** Following Murphy \cite{murphy1973brier}, the Brier score decomposes as:

$$\text{BS} = \text{REL} - \text{RES} + \text{UNC}$$

where REL (reliability) measures overconfidence, RES (resolution) measures discriminability, and UNC (uncertainty) reflects inherent label difficulty. We focus on $\Delta\text{REL} = \text{REL}_{\text{aligned}} - \text{REL}_{\text{base}}$ as our primary measure of alignment-induced calibration degradation, since it isolates overconfidence from accuracy changes.

**Alignment effect.** For each alignment method $a \in \{\text{SFT}, \text{DPO}, \text{PPO}\}$ and model size $s \in \{1.4\text{B}, 2.8\text{B}, 6.9\text{B}\}$, we define:

$$\Delta\text{REL}(a, s) = \text{REL}(\mathcal{M}_{a,s}) - \text{REL}(\mathcal{M}_{\text{base},s})$$

Bootstrap 95% confidence intervals for $\Delta\text{REL}$ are computed using $n = 1000$ bootstrap samples (seed = 42).

## 3.2 Competing Mechanistic Hypotheses

We pre-register three mutually exclusive mechanistic hypotheses for alignment-induced logit perturbation:

**H1 — Monotonic Scale Distortion.** Alignment training amplifies existing logit magnitudes proportionally, preserving the rank ordering of answer options. Formally, for item $i$:

$$\mathbf{l}^{(i)}_{\text{aligned}} \approx \lambda^{(i)} \cdot \mathbf{l}^{(i)}_{\text{base}} + \epsilon^{(i)}, \quad \lambda^{(i)} > 1$$

This produces high Spearman rank correlation $\rho$ between $\mathbf{l}^{(i)}_{\text{base}}$ and $\mathbf{l}^{(i)}_{\text{aligned}}$ across the $K=4$ answer options. **H1 diagnostic:** $\rho \geq 0.90$.

**H2 — Decision-Boundary Restructuring.** Alignment training selectively shifts probability mass toward particular answer patterns, changing which option is ranked first for substantial fractions of items. The rank ordering of options changes: $\arg\max_k l^{(i)}_{\text{base},k} \neq \arg\max_k l^{(i)}_{\text{aligned},k}$ for many items $i$. **H2 diagnostic:** $\rho < 0.85$ and substantial argmax redistribution.

**H3 — Framing Susceptibility Induction.** Alignment training makes the model's confidence allocation sensitive to framing, question type, or distractor presence. Calibration degradation would be larger on framing-sensitive tasks (e.g., TruthfulQA, which tests factual accuracy against socially-desirable false claims) than on general knowledge tasks (MMLU). **H3 diagnostic:** $\Delta\text{ECE}_{\text{TruthfulQA}} > \Delta\text{ECE}_{\text{MMLU}}$.

The discrimination thresholds $\rho_{\text{H1}} = 0.90$ and $\rho_{\text{H2}} = 0.85$ were pre-specified before any data was collected, based on the expected rank-preservation of a scale-only distortion and a threshold for "substantial" boundary shift, respectively.

## 3.3 Key Metrics

**Spearman rank correlation.** For each item $i$ and alignment pair $(a, s)$, we compute the Spearman ρ between the 4-dimensional base log-probability vector and the aligned log-probability vector:

$$\rho^{(i)}_{a,s} = \text{Spearman}(\mathbf{l}^{(i)}_{\text{base},s},\ \mathbf{l}^{(i)}_{\text{aligned},a,s})$$

We report the mean Spearman ρ across all $N = 14,042$ items for each of the 9 alignment-base pairs.

**Argmax partition.** We partition items into two subsets:
- *Shared-argmax*: $S = \{i : \arg\max \mathbf{l}^{(i)}_{\text{base},s} = \arg\max \mathbf{l}^{(i)}_{\text{aligned},a,s}\}$
- *Changed-argmax*: $C = \{i : \arg\max \mathbf{l}^{(i)}_{\text{base},s} \neq \arg\max \mathbf{l}^{(i)}_{\text{aligned},a,s}\}$

Under H1, reliability degradation would be concentrated in $S$ (pure confidence inflation). Under H2, the $|C|/N$ ratio is large and reliability degradation primarily arises from answer switching.

**Pre-softmax margin.** For item $i$, the logit margin is:

$$m^{(i)} = l^{(i)}_{(1)} - l^{(i)}_{(2)}$$

where $l^{(i)}_{(1)} \geq l^{(i)}_{(2)}$ are the top-2 log-probabilities before softmax normalization. The alignment-induced margin change is $\Delta m(a, s) = \bar{m}_{\text{aligned}} - \bar{m}_{\text{base}}$, where $\bar{m}$ denotes the mean over all items.

## 3.4 Experimental Design

**Models.** We evaluate the Pythia alignment ladder: 12 checkpoints comprising 3 base models (EleutherAI/pythia-1.4b, -2.8b, -6.9b) and 9 aligned variants (SFT, DPO, PPO for each size). Due to access constraints on the RLHFlow checkpoints from Li et al. \cite{li2024rlhf}, we use public fallback alignment checkpoints trained on the Anthropic HH dataset with Pythia base models: lomahony/pythia-\{size\}-helpful-sft (SFT), Leogrin/eleuther-pythia\{size\}-hh-dpo (DPO), and usvsnsp/pythia-\{size\}-ppo (PPO). All fallback models share the same base model and approximate training regime as the Li et al. checkpoints (see Limitation 1 in Section 6.4).

**Evaluation.** All models are evaluated on MMLU \cite{hendrycks2021mmlu} (cais/mmlu, standard configuration, 14,042 test items, 4-shot, 57 subjects) using lm-eval-harness v0.4.11 \cite{eval-harness} with greedy decoding (temperature = 1.0). Log-probability continuation scoring is used for both base and aligned models — not chat-template generation — providing a fair cross-model comparison. For the H3 diagnostic, we additionally evaluate all 12 models on TruthfulQA MC1 \cite{lin2022truthfulqa} (817 items, 0-shot).

**Calibration analysis.** ECE is computed using 15 equal-width bins on the max-probability confidence scores. Brier score decomposition into REL/RES/UNC follows Murphy \cite{murphy1973brier}. Bootstrap 95% confidence intervals use $n=1000$ samples with seed 42. Margin analysis uses the top-1 minus top-2 pre-softmax log-probability per item.

**Gate criteria.** We define a two-stage gate system following the YouRA verification framework:
- **H-E1 MUST_WORK gate:** $\Delta\text{REL}(a, s) > 0$ with $\text{CI}_{\text{lower}} > 0$ for PPO or DPO in $\geq 2/3$ Pythia sizes. Failure terminates the pipeline.
- **H-M1 MUST_WORK gate:** $\text{ECE}_{\text{base}}(s) < 0.15$ for all three sizes. Failure invalidates causal attribution.
- **H-M2 SHOULD_WORK gate:** $\Delta m_{\text{PPO}}(s) > 0$ with $\text{CI}_{\text{lower}} > 0$ for $\geq 2/3$ sizes.
- **H-M3 SHOULD_WORK gate:** Mean $\rho_{a,s} \geq 0.90$ for all 9 pairs (H1 confirmation).

## 3.5 Theoretical Justification

The three mechanisms are not merely theoretical constructs — they have distinct practical implications for calibration correction:

- **If H1 dominates:** Temperature scaling and ATS are well-matched to the distortion. Rescaling logit magnitudes without changing rank order directly corrects H1-type inflation.
- **If H2 dominates:** Temperature scaling is insufficient — it rescales confidence on whichever answer was selected, but cannot identify that the selection itself may have shifted incorrectly. H2-type correction may require representation-level interventions or rank-restoring regularization during alignment.
- **If H3 dominates:** Context-sensitive calibration methods are required; standard calibration methods applied at evaluation time may be benchmark-specific.

Our mechanistic discrimination framework thus serves both an empirical purpose (characterizing alignment effects) and a normative purpose (guiding the design of calibration correction methods matched to the dominant distortion type).
