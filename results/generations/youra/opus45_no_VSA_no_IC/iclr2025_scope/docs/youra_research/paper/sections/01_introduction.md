# Introduction

Despite LoRA's dominance as the parameter-efficient fine-tuning method of choice, practitioners universally default to rank $r=16$ without principled justification. This one-size-fits-all approach may waste 75% of adaptation capacity at scale or leave significant performance on the table. As language models grow from billions to hundreds of billions of parameters, the question becomes pressing: should LoRA rank scale with model size?

The surface-level answer might be "probably," but no systematic study has characterized this relationship. Prior work on LoRA has focused on the method itself—low-rank decomposition of weight updates, $\alpha/r$ scaling factors, and which layers to adapt—rather than how optimal rank varies across model scales. This gap leaves practitioners guessing: a 12B model may benefit from rank=64 while a 1B model saturates at rank=16, yet both typically receive the same default configuration.

We address this gap with a systematic empirical study across the Pythia model family (1B to 12B parameters). Our key insight is that **optimal LoRA rank scales sub-linearly with model size**: $r_{\text{opt}} \propto N^\alpha$ where $\alpha \in (0.3, 0.8)$ depending on task type. This sub-linear relationship suggests that task-relevant parameter subspaces grow more slowly than overall model capacity—larger models develop more efficient, focused representations requiring proportionally less adaptation.

Beyond the scaling law itself, we uncover two mechanistic findings:

1. **Phase transition in rank sensitivity**: Larger models (12B) exhibit >2× higher sensitivity to rank selection than smaller models (1B), meaning the penalty for suboptimal rank increases with scale.

2. **Inverted attention entropy**: Contrary to our initial hypothesis, larger models show *lower* attention entropy (more focused attention patterns), not higher. This suggests larger models develop specialized attention heads rather than broadly distributed patterns.

We also document an important scope limitation: the scaling exponent $\alpha$ is task-dependent. Single-hop QA (SQuAD-v2) yields $\alpha \approx 0.82$ while multi-hop reasoning (HotpotQA) yields $\alpha \approx 0.30$. There is no universal scaling law—task complexity modulates the relationship.

Our contributions are:

- **Empirical scaling law**: First systematic characterization of $r_{\text{opt}}$ vs model size $N$ under controlled conditions
- **Phase transition evidence**: Demonstration that rank sensitivity increases super-linearly with scale
- **Scope calibration**: Honest documentation of task-dependency, preventing overclaiming of a "universal" law
- **Mechanistic insight**: Discovery that attention entropy decreases with scale, informing future rank selection methods

These findings move LoRA rank selection from ad-hoc defaults toward principled prescriptions, enabling practitioners to configure rank based on model scale and task type.
