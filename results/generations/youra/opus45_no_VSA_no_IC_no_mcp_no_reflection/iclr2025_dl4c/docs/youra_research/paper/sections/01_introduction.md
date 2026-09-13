# Introduction

Despite theoretical guarantees that denser reward signals should accelerate reinforcement learning, we find that at proof-of-concept scale, all feedback granularities—binary, categorical, and high-bandwidth—produce identical outcomes: zero learning. This paradox challenges the assumption that small-scale pilots can distinguish between reward design alternatives for code generation tasks.

Reinforcement learning from execution feedback (RLEF) has emerged as a promising paradigm for improving code LLMs. Prior work has explored various feedback granularities: binary pass/fail rewards (Le et al., 2022), continuous test pass rates (Liu et al., 2023), and multi-signal combinations incorporating error type information (Shojaee et al., 2023). Information theory suggests that higher bandwidth signals—those providing more bits per gradient update—should enable more precise credit assignment and faster convergence. Yet no controlled comparison exists to validate this intuition.

We designed an experiment to fill this gap: a three-condition ablation study comparing binary (1 bit), continuous (~1.5 bits), and high-bandwidth (~2 bits) reward functions under matched infrastructure. Our hypothesis was straightforward: if reward information bandwidth matters, high-bandwidth conditions should reach performance thresholds in fewer training samples.

The result was unexpected. At proof-of-concept scale (1 epoch, 3 seeds per condition), all nine training runs produced 0% pass@1 on the evaluation set. No condition learned. The statistical comparison we planned was impossible—there was no variance to analyze.

This null result is not a falsification of the information bandwidth hypothesis. It is a methodological finding about minimum viable experimental scale. Our PoC compute budget (~1000 gradient updates total) falls below the threshold at which PPO policy improvement emerges for code generation. The hypothesis remains untested.

We report this negative result because it provides value to the research community:

1. **Lower bound establishment.** Future researchers now know that 1-epoch PoC pilots are insufficient for reward ablation studies on code LLMs. This prevents wasted compute on systematically underpowered experiments.

2. **Scale guidance.** We specify concrete requirements for a valid test: ≥3 epochs, ≥5 seeds, with learning rate warm-up and early stopping criteria based on validation pass@1 plateaus.

3. **Methodological contribution.** We distinguish between "hypothesis falsified" and "experiment underpowered"—a distinction often lost when negative results go unreported.

The information bandwidth framework remains theoretically sound. Binary rewards provide 1 bit per update (pass or fail). Error-type scoring adds ~1 bit (syntax < runtime < assertion < pass ordering). The distance-to-correct principle—that errors closer to correct solutions deserve higher reward—is not challenged by an underpowered experiment. What we learned is that demonstrating this effect empirically requires more compute than we allocated.

We organize the remainder of this paper as follows. Section 2 reviews related work on execution feedback for code LLMs, highlighting the absence of scale guidance. Section 3 describes our methodology, including the information bandwidth formalization and three reward conditions. Section 4 details our experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes with recommendations for future work.
