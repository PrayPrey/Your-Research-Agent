# Related Work

## Parameter-Efficient Fine-Tuning

LoRA [@hu2021lora] introduced low-rank adaptation for transformers, demonstrating that weight updates can be decomposed as $\Delta W = BA$ where $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$ with $r \ll \min(d,k)$. The original paper used rank $r \in \{1, 2, 4, 8, 64\}$ with $r=8$ as default, acknowledging this as a hyperparameter requiring tuning. Subsequent work adopted $r=16$ as a de facto standard without systematic justification.

RoRA [@rora2025] identified that the $\alpha/r$ scaling in original LoRA causes magnitude collapse at higher ranks, proposing $\alpha/\sqrt{r}$ scaling to stabilize training. This work demonstrated rank-dependent behavior exists but did not study how optimal rank varies with model size.

LoRA-drop [@loradrop2024] showed that up to 50% of LoRA parameters can be pruned post-hoc via output evaluation, suggesting over-parameterization is common. However, this is a pruning method rather than an a-priori rank selection strategy.

AdaLoRA [@adalora2023] proposed adaptive rank allocation across layers, dynamically adjusting rank during training. While addressing rank as a design variable, it does not characterize how aggregate optimal rank scales with model capacity.

## Neural Scaling Laws

Kaplan et al. [@kaplan2020scaling] established power-law relationships between model size, data, compute, and loss: $L(N) \propto N^{-\alpha}$. This paradigm inspired our investigation: if loss scales predictably with parameters, might optimal LoRA rank follow similar laws?

Chinchilla [@hoffmann2022training] refined compute-optimal scaling, showing that data and model size should scale together. Our work extends scaling analysis to the adaptation regime—how should adaptation capacity (rank) scale with base model size?

## Attention Analysis

The relationship between model scale and attention patterns remains underexplored. Studies of attention entropy typically focus on sequence length effects [@child2019sparse] or head pruning [@voita2019heads], not model-size dependency. Our finding that attention entropy *decreases* with scale—larger models exhibit more focused attention—appears novel and warrants further investigation.

## Gap Analysis

Prior work addresses LoRA mechanism design (rank selection methods, $\alpha$ scaling) or post-hoc pruning, but **no systematic study characterizes optimal rank as a function of model size**. We fill this gap with controlled experiments across four Pythia scales (1B-12B), two task types, and six rank values, enabling log-linear regression for scaling law estimation.
