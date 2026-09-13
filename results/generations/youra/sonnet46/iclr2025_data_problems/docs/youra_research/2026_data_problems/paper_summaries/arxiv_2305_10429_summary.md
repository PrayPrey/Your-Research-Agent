---
source_paper: "arxiv_2305_10429.md"
generated_at: "2026-03-14T16:47:10.270428"
model: "gpt-4o-mini"
summary_chars: 6243
---

# DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining

## Key Metadata
- **Authors:** Sang Michael Xie et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** The paper introduces DoReMi, a method that optimizes domain weights for language model training, enhancing performance and training efficiency without requiring downstream task-specific tuning.

## Section Summaries

### Abstract
The mixture proportions of pretraining data domains (e.g., Wikipedia, books, web text) greatly affect language model (LM) performance. In this paper, we propose Domain Reweighting with Minimax Optimization (DoReMi), which first trains a small proxy model using group distributionally robust optimization (Group DRO) over domains to produce domain weights (mixture proportions) without knowledge of downstream tasks. We then resample a dataset with these domain weights and train a larger, full-sized model. In our experiments, we use DoReMi on a 280M-parameter proxy model to set the domain weights for training an 8B-parameter model (30x larger) more efficiently. On The Pile, DoReMi improves perplexity across all domains, even when it downweights a domain. DoReMi improves average few-shot downstream accuracy by 6.5% points over a baseline model trained using The Pile’s default domain weights and reaches the baseline accuracy with 2.6x fewer training steps. On the GLaM dataset, DoReMi, which has no knowledge of downstream tasks, even matches the performance of using domain weights tuned on downstream tasks.

### Introduction & Motivation
Language models are trained on diverse datasets that consist of various domains, each contributing differently to model performance. Existing methods determine domain weights through intuition or tuning based on downstream tasks, often leading to suboptimal configurations. The paper presents DoReMi, a method using group distributionally robust optimization (Group DRO) to derive domain weights that improve model performance across all domains without requiring specific downstream evaluations. 

### Methodology
DoReMi comprises three steps:

1. **Reference Model Training:** A small reference model is trained based on initial domain weights \( \alpha_{ref} \) for \( T \) steps using standard training procedures. This model, with 280M parameters, captures a baseline distribution of performance over the training domains.

2. **Proxy Model with Group DRO:** A proxy model \( p_\theta \) is then trained using define domain weights that minimize the worst-case excess loss defined as:
   \[
   L(\theta, \alpha) = \mathbb{E}_{x \sim D_i} \left[ \alpha_i \cdot \left( \ell_\theta(x) - \ell_{ref}(x) \right) \right]
   \]
   where \( \ell_\theta(x) \) and \( \ell_{ref}(x) \) are the negative log likelihoods of the proxy and reference models respectively. The optimization is conducted using the Group DRO optimizer, which interleaves the updates of model parameters \( \theta \) and domain weights \( \alpha_t \) over \( T \) training steps. The final domain weights \( \bar{\alpha} \) are computed as the average over the training trajectory.

3. **Main Model Training:** The optimized domain weights \( \bar{\alpha} \) are used to resample the training data, and an 8B-parameter model is trained using a standard language modeling loss with the new training distribution.

Key hyperparameters include \( T = 200k \) steps and batch size \( b = 512 \). The optimizer used in training is Adafactor (Shazeer & Stern, 2018) with a step size \( \eta = 1 \) and smoothing parameter \( c = 1e-3 \).

### Experiments & Results
The experiments utilize two datasets: 
1. **The Pile**: An 800GB dataset with 22 domains. The baseline domain weights are heuristically determined.
2. **GLaM**: A dataset consisting of 8 domains with downstream-tuned domain weights.

Model training for both datasets is executed to maintain equal compute resources. Results from training show that DoReMi significantly improves downstream accuracy by 6.5% points on The Pile, achieving baseline performance 2.6x faster, and reduces perplexity across all domains. In the GLaM dataset, iterated DoReMi demonstrates performance comparable to that achieved using downstream-specific domain weights, confirming the efficacy of DoReMi even without downstream task awareness.

| Dataset        | Parameter Size | Downstream Accuracy Improvement | Training Step Efficiency |
|----------------|----------------|-------------------------------|--------------------------|
| The Pile       | 8B             | +6.5%                        | 2.6x faster              |
| GLaM           | 8B             | Comparable                    | —                        |

The ablation studies reveal that the DoReMi domain weights consistently enhance performance across various proxy model scales, illustrating robustness even when using suboptimal proxy models.

### Discussion & Conclusion
DoReMi effectively optimizes domain weights for language model training, achieving significant performance gains while conserving training resources. Limitations include potential inefficiencies in domain weight changes over iterations and sensitivity to the choice of reference model. Future work may expand domain definitions and investigate the transferability of weights across model scales.

## Key Contributions
- Introduction of DoReMi, a novel method for optimizing domain weights in pretraining a language model.
- Demonstrated significant improvements in training efficiency and downstream task performance compared to heuristic and downstream-task-tuned baselines.
- Extensive evaluation with large-scale experiments demonstrating the robustness of the proposed technique across various datasets and model sizes.

## Potential Relevance
The methodology proposed in DoReMi can inform future research on optimizing training protocols for large language models. The findings on performance improvements and training efficiencies, particularly the insights around domain weights, can guide the development of more efficient pretraining strategies in subsequent models. Additionally, the lack of requirement for downstream task knowledge may encourage wider applicability across diverse natural language processing tasks.