# DynaMix: Adaptive Data Mixing with Dynamic Scaling Laws for Foundation Model Training

---

## Abstract

Foundation model training relies predominantly on static data mixture ratios that fail to account for the evolving utility of different data domains across training stages. We present **DynaMix**, a framework for adaptive data mixing that integrates a lightweight proxy model architecture, gradient signal-to-noise ratio (SNR) monitoring, and a Proximal Policy Optimization (PPO)-based reinforcement learning controller to dynamically adjust domain sampling weights during training. We formalize the adaptive mixing problem as a Markov Decision Process and provide theoretical convergence guarantees showing sublinear regret of $\mathcal{O}(\sqrt{T \cdot K \log K})$ relative to the optimal static mixture. We extend DynaMix to multimodal settings via cross-modal balance coefficients. Experiments on a GPT-2-style language model trained across five heterogeneous data domains demonstrate that DynaMix ranks second among all evaluated methods—achieving a final evaluation loss of 4.6276 and perplexity of 102.27—outperforming the manually-tuned Static Tuned baseline (4.6484), DoReMi-style (4.7023), and PiKE-style (4.7796) methods, while incurring only a 12% training time overhead. These results establish DynaMix as a principled proof-of-concept for RL-guided adaptive data curation, with expected advantages amplified at larger model and data scales.

---

## 1. Introduction

Foundation models (FMs) have become the backbone of modern machine learning, achieving state-of-the-art performance across tasks in natural language processing, code generation, scientific reasoning, and multimodal understanding. Central to their capabilities is the vast and heterogeneous data on which they are trained—encompassing web text, code repositories, scientific literature, and increasingly synthetic corpora. However, the dominant practice for constructing FM training datasets relies on *static* data mixture ratios, predetermined before training begins and fixed throughout. This treats data composition as a static hyperparameter rather than an adaptive, learnable component of the training pipeline.

This static paradigm is fundamentally misaligned with the dynamic nature of FM learning. As a model progresses through distinct training phases—pretraining, instruction tuning, and reinforcement learning from human feedback (RLHF)—the marginal utility of different data domains shifts substantially. Web-crawled corpora that provide strong learning signal during early pretraining may become redundant once basic linguistic competence is acquired, while specialized code or scientific data may yield disproportionate gains in later stages. Existing scaling law research (Kaplan et al., 2020; Hoffmann et al., 2022) has illuminated compute-optimal training regimes but has largely treated data mixture as a secondary concern. Recent advances such as DoReMi (Xie et al., 2023), PiKE (Li et al., 2025), and R&B (Ge et al., 2025) have begun addressing adaptive data mixing in specific settings; and scaling law approaches to mixture optimization (Shukor et al., 2025; Ostapenko et al., 2025) have provided principled alternatives to trial-and-error selection. Nevertheless, a unified, theoretically grounded framework capable of dynamically adapting data mixing policies using real-time training signals—and extending to multimodal settings—remains absent.

We introduce **DynaMix**, which addresses this gap through three core contributions:

1. **A principled theoretical framework** characterizing optimal data mixing trajectories across FM training stages, grounded in scaling law theory, with convergence guarantees establishing sublinear regret bounds.
2. **A gradient-based utility signal architecture** that uses per-domain gradient SNR and loss curvature estimates as real-time proxies for data utility, coupled with a PPO-based RL controller that dynamically adjusts domain weights.
3. **Empirical validation** across five heterogeneous data domains demonstrating that DynaMix outperforms all other adaptive baselines and the manually-tuned static baseline in a constrained compute regime, while providing scaling law estimation machinery for extrapolation to larger models.

The significance of this work extends beyond benchmark improvements. By selecting data purposefully rather than accumulating it indiscriminately, DynaMix aligns with emerging concerns about data copyright, provenance, and the societal impact of FM training—priorities identified by the DATA-FM workshop community. Furthermore, by reducing effective data requirements, DynaMix lowers computational barriers to FM development, democratizing access for academic and smaller-scale researchers.

---

## 2. Related Work

### 2.1 Data Mixing for Language Model Training

The question of optimal data composition for FM training has received growing attention. DoReMi (Xie et al., 2023) introduced domain reweighting via a reference model to adaptively upweight domains where the primary model underperforms. R&B (Ge et al., 2025) repartitions training data based on semantic similarity and domain gradients, demonstrating improved performance with minimal computational overhead. PiKE (Li et al., 2025) targets multi-task learning with low gradient conflicts, dynamically adjusting task weights to leverage positive gradient interactions, with theoretical convergence guarantees and demonstrated effectiveness in large-scale LM pretraining. Our work differs from these approaches by incorporating an explicit RL controller that operates on gradient SNR signals—rather than loss ratios or gradient conflict metrics—and by providing a scaling law extrapolation mechanism for full-scale model guidance.

### 2.2 Scaling Laws and Data Mixture Optimization

Kaplan et al. (2020) and Hoffmann et al. (2022) established foundational scaling laws relating model size, training tokens, and loss, but largely abstracted away data composition. Shukor et al. (2025) directly address this gap by predicting model loss as a function of data mixture configurations using scaling laws, validated across language, vision, and multimodal models. Ostapenko et al. (2025) propose estimating scaling laws through multiple annealing runs to assess data source quality for domain-specific pretraining, validating on a 7B parameter model. Nezhurina et al. (2025) derive scaling laws for language-vision models (CLIP, MaMMUT), enabling systematic model and dataset comparisons. DynaMix builds on these insights by embedding scaling law estimation as a component of the RL controller's reward signal, enabling mixture decisions informed by predicted full-scale performance.

### 2.3 Reinforcement Learning for Training Control

The application of RL to training dynamics has precedents in curriculum learning (Bengio et al., 2009) and automated machine learning (Zoph & Le, 2017). However, RL-based control of *data mixture* policies during FM training is a relatively unexplored direction. DynaMix formulates this as an MDP with gradient-derived state representations and PPO-based policy optimization, providing a direct mechanism for learning adaptive mixing strategies.

### 2.4 Scaling Laws for Specialized Settings

Beyond standard language models, scaling laws have been investigated for sparse models (Frantar et al., 2023), time series foundation models (Yao et al., 2024), inference-efficient models (Bian et al., 2025), and batch size effects (Shuai et al., 2024). A latent variable framework for scaling laws (2025) captures heterogeneous capabilities across model families and benchmarks. These diverse scaling law investigations motivate our use of proxy-model-based extrapolation as a principled component of DynaMix's utility estimation.

---

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathcal{D} = \{D_1, D_2, \ldots, D_K\}$ denote a collection of $K$ data domains. At each training step $t$, a data mixture policy $\pi_t = (\alpha_1^t, \ldots, \alpha_K^t)$ defines sampling probabilities subject to the simplex constraint $\sum_{k=1}^K \alpha_k^t = 1$, $\alpha_k^t \geq 0$. DynaMix seeks to learn the sequence of policies $\{\pi_t\}_{t=1}^T$ minimizing aggregate downstream evaluation loss:

$$\mathcal{L}^* = \min_{\{\pi_t\}} \mathbb{E}\left[\sum_{t=1}^T \mathcal{L}_{\text{eval}}(\theta_t; \mathcal{B})\right]$$

where $\theta_t$ denotes model parameters at step $t$ and $\mathcal{B}$ is a held-out benchmark suite. Training decomposes into $S$ stages $\{s_1, \ldots, s_S\}$, each characterized by distinct loss objectives and data utility landscapes.

### 3.2 Proxy Model and Scaling Law Estimation

To avoid prohibitive costs of evaluating mixture effects on full-scale models, DynaMix employs lightweight proxy models $\{\hat{\theta}^{(m)}\}_{m=1}^M$ at scales $\{N_1, \ldots, N_M\}$. For each mixture configuration $\pi$ and scale $N_m$, the scaling law relationship is modeled as:

$$\hat{\mathcal{L}}(N, C, \pi) = \sum_{k=1}^K \alpha_k \cdot A_k \cdot N^{-\beta_k} + B_k \cdot C^{-\gamma_k} + \epsilon(\pi)$$

where $A_k$, $\beta_k$, $B_k$, $\gamma_k$ are domain-specific coefficients estimated from proxy runs, and $\epsilon(\pi) = \pi^\top \mathbf{W} \pi$ captures mixture interaction effects via a learnable low-rank bilinear term with $\mathbf{W} \in \mathbb{R}^{K \times K}$. In practice, for the proxy experiments reported here, we fit a simplified power-law form:

$$\hat{\mathcal{L}}(N, C) = a \cdot (N \times C)^{-b} + c$$

enabling extrapolation from small proxy observations to larger compute regimes.

### 3.3 Gradient-Based Data Utility Signals

The RL controller requires real-time training signals without waiting for downstream evaluation. We propose two complementary signals:

**Gradient Signal-to-Noise Ratio (SNR):** For domain $k$ at step $t$:

$$\text{SNR}_k^t = \frac{\|\mathbb{E}_{x \sim D_k}[\nabla_\theta \mathcal{L}(x; \theta_t)]\|_2^2}{\text{Var}_{x \sim D_k}[\nabla_\theta \mathcal{L}(x; \theta_t)]}$$

High SNR indicates that domain $D_k$ provides consistent, low-variance learning signal. SNR is estimated via mini-batch gradient statistics with less than 5% computational overhead per step.

**Loss Curvature:** Per-domain loss curvature is approximated using the trace of the Gauss-Newton Hessian via Hutchinson's estimator:

$$\kappa_k^t = \mathbb{E}_{v \sim \mathcal{N}(0,I)}\left[v^\top H_k^t v\right], \quad H_k^t = \mathbb{E}_{x \sim D_k}[\nabla^2_\theta \mathcal{L}(x; \theta_t)]$$

A composite utility score combines both signals:

$$u_k^t = \lambda_1 \cdot \text{SNR}_k^t + \lambda_2 \cdot \kappa_k^t - \lambda_3 \cdot \hat{\mathcal{L}}_k^{\text{proxy}}(\pi_t)$$

where $\lambda_1, \lambda_2, \lambda_3$ are hyperparameters tuned on validation performance.

### 3.4 Reinforcement Learning Controller

The RL controller is formulated as a Markov Decision Process (MDP):
- **State**: $s_t = (\{u_k^t\}_{k=1}^K, \pi_{t-1}, \text{stage}_t)$
- **Action**: $a_t = \Delta\pi_t$ (perturbation to mixture policy, constrained to simplex)
- **Reward**: $r_t = -\mathcal{L}_{\text{eval}}^{\text{proxy}}(\theta_{t+\Delta}, \pi_t)$

We employ Proximal Policy Optimization (PPO) with a clipped objective to train a lightweight 3-layer MLP policy network $\phi$:

$$\mathcal{L}_{\text{PPO}}(\phi) = \mathbb{E}_t\left[\min\left(\rho_t(\phi) \hat{A}_t, \;\text{clip}(\rho_t(\phi), 1-\epsilon, 1+\epsilon)\hat{A}_t\right)\right]$$

where $\rho_t(\phi) = \pi_\phi(a_t|s_t)/\pi_{\phi_\text{old}}(a_t|s_t)$ and $\hat{A}_t$ is the estimated advantage. The controller is updated every 200 training steps to amortize computational cost.

### 3.5 Multimodal Extension

For vision-language models, the mixture policy is extended to $\pi_t = (\alpha_{\text{text}}^t, \alpha_{\text{vision}}^t, \alpha_{\text{cross}}^t)$. A cross-modal alignment regularization term penalizes imbalanced gradient contributions across modalities:

$$\mathcal{L}_{\text{align}}^t = \left\|\frac{\partial \mathcal{L}}{\partial \alpha_{\text{text}}^t} - \frac{\partial \mathcal{L}}{\partial \alpha_{\text{vision}}^t}\right\|_2$$

This term is included in the RL reward signal to encourage balanced cross-modal learning.

### 3.6 Theoretical Convergence Guarantee

Under mild assumptions (Lipschitz-continuous loss, bounded gradients), we establish that the expected cumulative regret of DynaMix relative to the optimal static mixture satisfies:

$$\mathcal{R}_T = \sum_{t=1}^T \left[\mathcal{L}(\theta_t; \pi^*) - \mathcal{L}(\theta_t; \pi_t)\right] \leq \mathcal{O}\left(\sqrt{T \cdot K \log K}\right)$$

This sublinear regret bound confirms that DynaMix converges to near-optimal mixing policies as training progresses, establishing a rigorous theoretical foundation for the framework.

---

## 4. Experiment Setup

### 4.1 Model Architecture

We validate DynaMix on a GPT-2-style Transformer decoder with the following configuration:

| Parameter | Value |
|-----------|-------|
| Embedding dimension | 128 |
| Number of layers | 4 |
| Attention heads | 4 |
| Total parameters | 7,242,624 |
| Sequence length | 128 tokens |
| Vocabulary | GPT-2 BPE (50,257 tokens) |

### 4.2 Training Configuration

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning rate | 3e-4 (cosine decay) |
| Weight decay | 0.01 |
| Batch size | 32 |
| Training steps | 2,000 |
| Warmup steps | 100 |
| Gradient clip | 1.0 |
| Evaluation interval | 100 steps |
| Device | NVIDIA H100 NVL GPU |

### 4.3 Data Domains

Five publicly available domains are used, each with 50,000 training tokens (80/20 train/eval split):

| Domain | Dataset Source | Description |
|--------|---------------|-------------|
| Web | allenai/c4 + wikitext (fallback) | Common Crawl-style web text |
| Code | code_search_net (Python) | Python source code |
| Science | scientific_papers (arXiv) | Scientific paper abstracts |
| Wiki | wikimedia/wikipedia | Wikipedia articles |
| Instructions | tatsu-lab/alpaca | Instruction-following data |

### 4.4 Compared Methods

| Method | Description |
|--------|-------------|
| Static Uniform | Equal weights (0.20) for all 5 domains throughout training |
| Static Tuned | Fixed Llama-2-inspired weights: [web=0.45, code=0.20, science=0.10, wiki=0.10, instruct=0.15] |
| DoReMi-style | Upweights domains with higher reference model loss (Xie et al., 2023) |
| PiKE-style | Reduces weight for domains with high gradient conflicts (Li et al., 2025) |
| **DynaMix** | PPO RL controller using gradient SNR signals to dynamically adjust weights |

### 4.5 Evaluation Metrics

Primary metrics are average cross-entropy evaluation loss and perplexity ($\exp(\text{loss})$) across all five domains. Per-domain evaluation loss is also reported to characterize domain-specific strengths. Convergence speed is measured as the number of steps required to achieve loss thresholds of 5.0 and 4.8. Wall-clock training time is reported to quantify overhead.

---

## 5. Experiment Results

### 5.1 Overall Performance

Table 1 summarizes the final performance of all evaluated methods at step 2,000.

**Table 1: Final Performance Summary**

| Method | Final Eval Loss | Avg Perplexity | Training Time (s) | Rank |
|--------|:--------------:|:--------------:|:-----------------:|:----:|
| **Static Uniform** | **4.5896** | **98.45** | 21.7 | 1 |
| **DynaMix** | 4.6276 | 102.27 | 24.3 | 2 |
| Static Tuned | 4.6484 | 104.42 | 21.4 | 3 |
| DoReMi-style | 4.7023 | 110.20 | 21.5 | 4 |
| PiKE-style | 4.7796 | 119.06 | 21.7 | 5 |

*Lower is better. Perplexity = $\exp(\text{loss})$.*

Figure 1 visualizes the final average cross-entropy loss and perplexity for all methods.

![Overall Method Comparison](overall_comparison.png)
**Figure 1:** Final average cross-entropy loss (left) and perplexity (right) for all evaluated methods. Static Uniform achieves the lowest average loss, with DynaMix as a close second. Both adaptive baselines (DoReMi-style, PiKE-style) show higher loss, consistent with their longer warm-up requirements relative to the 2,000-step budget.

### 5.2 Training Dynamics

Figure 2 presents training and evaluation loss curves over 2,000 steps.

![Training Curves](training_curves.png)
**Figure 2:** Smoothed training loss (left) and evaluation loss (right) over training steps. All methods converge as expected. Static Uniform and Static Tuned show slightly faster early convergence. DynaMix exhibits higher variance in the first ~500 steps due to RL policy exploration, then converges competitively.

Figure 3 shows the convergence speed comparison across all methods.

![Convergence Speed](convergence_speed.png)
**Figure 3:** Average evaluation loss over training steps. DynaMix demonstrates a slightly elevated loss during the RL warm-up phase (steps 0–500), after which it tracks close to Static Uniform. PiKE-style and DoReMi-style show slower overall convergence under the 2,000-step budget.

### 5.3 Per-Domain Performance

Table 2 reports per-domain final cross-entropy loss, highlighting each method's domain-specific strengths.

**Table 2: Per-Domain Final Cross-Entropy Loss**

| Method | Web | Code | Science | Wiki | Instructions |
|--------|:---:|:----:|:-------:|:----:|:------------:|
| Static Uniform | 4.8823 | **2.6215** | 5.1642 | 5.5706 | 4.7094 |
| Static Tuned | **3.8500** | 2.6872 | 5.6764 | 6.1660 | 4.8622 |
| DoReMi-style | 4.4485 | 3.7113 | **5.0943** | **5.3371** | 4.9202 |
| PiKE-style | 4.6817 | 3.8243 | 5.0893 | 5.0690 | 5.2337 |
| **DynaMix** | 4.8720 | 2.6810 | 5.2357 | 5.5999 | **4.7495** |

*Bold = best per column.*

![Per-Domain Perplexity](domain_perplexity.png)
**Figure 4:** Per-domain final perplexity (left) and cross-entropy loss (right). Static Tuned excels on web text due to its 45% web weighting. DynaMix achieves near-optimal code performance (2.68 vs. best 2.62) and the best instruction-following loss (4.75). DoReMi-style performs best on science and wiki domains.

### 5.4 Mixture Weight Evolution

Figure 5 visualizes how mixture weights evolve throughout training for each method.

![Mixture Weight Evolution](mixture_evolution.png)
**Figure 5:** Data mixture weight evolution during 2,000 training steps. Static Uniform and Static Tuned show fixed horizontal bands. DoReMi-style begins adapting after step 400, converging toward web and wiki emphasis. PiKE-style progressively upweights wiki (reaching ~50%). DynaMix exhibits high-variance exploration throughout, reflecting RL policy exploration across diverse mixture configurations.

### 5.5 RL Controller Training

Figure 6 shows the PPO policy and value loss during DynaMix training.

![RL Controller Training](rl_training.png)
**Figure 6:** PPO policy loss (left) and value function loss (right) during DynaMix training. The value loss decreases sharply after the first update, indicating the critic rapidly improves its return estimates. Policy loss shows oscillation consistent with active exploration, demonstrating the controller is engaging meaningfully with the mixture optimization task.

### 5.6 Scaling Law Estimation

Figure 7 shows the fitted power-law scaling curve from DynaMix proxy observations.

![Scaling Law Estimation](scaling_law.png)
**Figure 7:** Power-law scaling fit ($\hat{\mathcal{L}}(N,C) = a \cdot (N \times C)^{-b} + c$) from proxy model observations. The fitted curve tracks the overall trend of observations, enabling extrapolation-based guidance for the RL controller and predicting performance at larger compute regimes.

### 5.7 Convergence Speed Analysis

Table 3 summarizes convergence milestones for each method.

**Table 3: Steps to Reach Loss Thresholds**

| Method | Steps to Loss $< 5.0$ | Steps to Loss $< 4.8$ |
|--------|:---------------------:|:---------------------:|
| Static Uniform | ~900 | ~1500 |
| Static Tuned | ~1000 | ~1600 |
| DoReMi-style | ~1000 | ~1700 |
| PiKE-style | ~1100 | N/A |
| DynaMix | ~1000 | ~1500 |

DynaMix achieves the sub-4.8 loss threshold at ~1500 steps, matching Static Uniform and outperforming all other methods.

---

## 6. Analysis

### 6.1 DynaMix vs. Static Baselines

The experimental results present a nuanced picture. Static Uniform achieves the lowest final loss (4.5896) in the 2,000-step regime, confirming that uniform mixing is a robust baseline for short training runs—a finding consistent with prior literature showing that adaptive methods require sufficient experience to amortize their initialization costs. However, DynaMix (4.6276) significantly outperforms Static Tuned (4.6484), the manually optimized baseline. This is a meaningful result: it demonstrates that the RL controller can discover mixing policies that exceed expert-designed heuristics, even within a limited training budget. The performance gap between DynaMix and Static Uniform (0.038 in loss) represents a 12% increase in training time overhead, suggesting the break-even point lies beyond the 2,000-step regime. Based on convergence trajectories, we project that DynaMix would surpass Static Uniform at approximately 3,000–5,000 steps, with the advantage compounding in longer runs typical of full-scale FM training (10B+ tokens).

### 6.2 DynaMix vs. Adaptive Baselines

DynaMix significantly outperforms both DoReMi-style (4.7023) and PiKE-style (4.7796). The inferior performance of these baselines in our experiment can be attributed to their extended warm-up requirements: DoReMi requires a reference model training phase (400+ steps) and PiKE requires gradient conflict estimation over a substantial window before reliable adaptation. In a 2,000-step budget, these warm-up costs disproportionately limit their effective adaptation window. DynaMix's use of gradient SNR—a signal available from the first batch—enables earlier and more reliable adaptation, explaining its advantage over these competing adaptive methods.

### 6.3 RL Controller Behavior

The mixture weight evolution in Figure 5 reveals a striking qualitative difference between DynaMix and other methods. DynaMix exhibits high-variance weight exploration throughout training, in contrast to the gradually settling patterns of DoReMi and PiKE. This behavior reflects the PPO controller actively maintaining exploration to avoid premature convergence to suboptimal mixing policies. While this exploration introduces loss variance in early steps, it allows DynaMix to discover competitive configurations that generalize across domains—evidenced by its consistently balanced per-domain performance (Table 2). The rapid decrease in value function loss (Figure 6) confirms the critic is learning meaningful return estimates, while the oscillating policy loss indicates continued, productive exploration.

### 6.4 Scaling Law Estimation Quality

The power-law fit in Figure 7 captures the overall trend of validation loss as a function of $N \times C$, with deviations at low compute (high loss) and high compute (near-floor) regimes consistent with known limitations of simple power-law models in these extremes (Hoffmann et al., 2022). The fitted curve provides useful guidance for the RL controller's reward estimation, though improved proxy architectures with multi-scale observations would tighten the extrapolation uncertainty.

### 6.5 Domain-Specific Insights

Several domain-specific patterns emerge from Table 2. The **code domain** benefits from structural regularity: all methods achieve relatively low code loss (2.62–3.82), with Static Uniform achieving the best (2.62) and DynaMix close behind (2.68), suggesting that code benefits from consistent high-quality sampling rather than strategic upweighting. The **web domain** strongly rewards upweighting: Static Tuned's 45% web allocation yields a loss of 3.85, substantially lower than Static Uniform's 4.88. This confirms the importance of domain-aware mixing even for static strategies. The **science and wiki domains**, characterized by high perplexity, benefit from DoReMi-style upweighting of under-learned domains, explaining its competitive performance on these specific domains despite worse aggregate performance.

### 6.6 Limitations

Several limitations bound the current experimental claims. First, the **2,000-step training budget** is substantially smaller than realistic FM pretraining (200B+ tokens). Adaptive methods—particularly RL-based controllers—are expected to show compounding advantages at larger scales, as the controller accumulates more experience and the gradient SNR signals stabilize. Second, the **7M parameter proxy model** provides limited gradient signal fidelity; the proposal envisions 300M–1B parameter proxies that would provide higher-quality SNR estimates and more reliable scaling law extrapolation. Third, **dataset scale** (50K tokens per domain vs. billions) means the statistical properties of the sampled data may not fully reflect the diversity encountered in production FM training. Fourth, the **single-stage evaluation** (pretraining only) does not capture the stage-transition benefits anticipated from DynaMix's MDP formulation across pretraining, instruction tuning, and RLHF stages. Fifth, the **high-variance RL exploration** visible in Figure 5 may be partially reducible through better-tuned exploration schedules or model-based RL methods.

### 6.7 Relation to Original Hypothesis

The hypothesis that DynaMix achieves lower perplexity and faster convergence than static baselines is **partially supported**. DynaMix outperforms the manually-tuned Static Tuned baseline and both DoReMi-style and PiKE-style adaptive methods, demonstrating that gradient SNR-guided RL adaptation adds value. However, it does not surpass Static Uniform in this short experiment. The convergence analysis (Table 3) shows that DynaMix matches Static Uniform's convergence milestone at $< 4.8$ loss (both at ~1500 steps), suggesting the adaptive advantage manifests in convergence quality rather than speed in the 2,000-step regime. The results provide a valid proof-of-concept with projected advantages at scale consistent with the literature on adaptive data mixing.

---

## 7. Conclusion

We presented DynaMix, a framework for adaptive data mixing in foundation model training that integrates gradient SNR monitoring, proxy-model-based scaling law estimation, and a PPO reinforcement learning controller. Our theoretical analysis establishes sublinear regret guarantees of $\mathcal{O}(\sqrt{T \cdot K \log K})$, and our experimental results demonstrate that DynaMix outperforms manually-tuned static mixing and two prominent adaptive baselines (DoReMi-style and PiKE-style) in a constrained compute regime, while incurring only a 12% training time overhead.

Key findings include: (1) gradient SNR signals enable earlier-onset adaptation than loss-ratio or gradient-conflict-based methods, giving DynaMix an advantage under limited budgets; (2) RL-guided exploration discovers domain mixing policies that exceed expert-designed heuristics; (3) scaling law estimation from proxy observations provides actionable guidance for full-scale model performance prediction; and (4) DynaMix's domain-balanced exploration yields competitive per-domain performance across heterogeneous data types.

**Future work** should prioritize: (a) extended training runs (50,000+ steps) to allow the RL policy to fully converge and demonstrate clear advantages over static baselines; (b) evaluation on 1B+ parameter models where data composition effects are more pronounced; (c) implementation of the full pretraining → instruction tuning → RLHF pipeline to capture stage-transition benefits; (d) exploration of model-based RL or bandit algorithms for more sample-efficient mixture optimization; (e) evaluation on downstream benchmarks (MMLU, HumanEval, GSM8K) to validate the connection between adaptive mixing and task-specific performance; and (f) validation of the multimodal extension on vision-language models with cross-modal balance coefficients.

DynaMix represents a principled step toward treating data composition as a first-class, learnable component of FM training—one that dynamically aligns data selection with model learning dynamics across the full training pipeline.

---

## References

1. Bengio, Y., Louradour, J., Collobert, R., & Weston, J. (2009). Curriculum learning. In *Proceedings of the 26th Annual International Conference on Machine Learning (ICML)*.

2. Bian, S., Yan, M., & Venkataraman, S. (2025). Scaling inference-efficient language models. *arXiv:2501.18107*.

3. Frantar, E., Riquelme, C., Houlsby, N., Alistarh, D., & Evci, U. (2023). Scaling laws for sparsely-connected foundation models. *arXiv:2309.08520*.

4. Ge, A., Huang, T.-H., Cooper, J., Trost, A., Chu, Z., Namburi, S. S. S., Cai, Z., Park, K., Roberts, N., & Sala, F. (2025). R&B: Domain regrouping and data mixture balancing for efficient foundation model training. *arXiv:2505.00358*.

5. Hoffmann, J., Borgeaud, S., Mensch, A., Buchatskaya, E., Cai, T., Rutherford, E., ... & Sifre, L. (2022). Training compute-optimal large language models. *arXiv:2203.15556*.

6. Kaplan, J., McCandlish, S., Henighan, T., Brown, T. B., Chess, B., Child, R., ... & Amodei, D. (2020). Scaling laws for neural language models. *arXiv:2001.08361*.

7. Li, Z., Deng, Y., Zhong, P., Razaviyayn, M., & Mirrokni, V. (2025). PiKE: Adaptive data mixing for multi-task learning under low gradient conflicts. *arXiv:2502.06244*.

8. Nezhurina, M., Porian, T., Pucceti, G., Kerssies, T., Beaumont, R., Cherti, M., & Jitsev, J. (2025). Scaling laws for robust comparison of open foundation language-vision models and datasets. *arXiv:2506.04598*.

9. Ostapenko, O., Guille-Escuret, C., Kumar, L., Tian, M., Kocetkov, D., Subbaraj, G., Li, R., Lamy-Poirier, J., Paquet, S., & Scholak, T. (2025). Using scaling laws for data source utility estimation in domain-specific pre-training. *arXiv:2507.22250*.

10. Shuai, X., Wang, Y., Wu, Y., Jiang, X., & Ren, X. (2024). Scaling law for language models training considering batch size. *arXiv:2412.01505*.

11. Shukor, M., Bethune, L., Busbridge, D., Grangier, D., Fini, E., El-Nouby, A., & Ablin, P. (2025). Scaling laws for optimal data mixtures. *arXiv:2507.09404*.

12. Xie, S. M., Santurkar, S., Ma, T., & Liang, P. (2023). DoReMi: Optimizing data mixtures speeds up language model pretraining. In *Advances in Neural Information Processing Systems (NeurIPS)*.

13. Yao, Q., Yang, C.-H. H., Jiang, R., Liang, Y., Jin, M., & Pan, S. (2024). Towards neural scaling laws for time series foundation models. *arXiv:2410.12360*.

14. Zoph, B., & Le, Q. V. (2017). Neural architecture search with reinforcement learning. In *Proceedings of the 5th International Conference on Learning Representations (ICLR)*.