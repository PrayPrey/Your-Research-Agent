# 1. Introduction

What if the key to safer AI isn't teaching models what *not* to do, but teaching them to follow any constraint—including implicit ones they've never seen?

Reinforcement Learning from Human Feedback (RLHF) has become the dominant paradigm for aligning language models with human preferences [1]. Current approaches optimize a single objective: helpfulness as judged by human annotators or proxy reward models. This *unidirectional* alignment (AI→Human) has produced increasingly capable assistants, yet a fundamental gap remains: models follow instructions inconsistently, particularly explicit constraints on format, length, and structure [2].

Sun et al. [3] propose a *bidirectional* alignment framework distinguishing two directions: AI→Human (helpfulness, harmlessness) and Human→AI (controllability, steerability). While the theoretical framework is compelling, no existing work implements bidirectional training signals. IFEval [2] measures instruction-following for evaluation; AlpacaEval [4] measures helpfulness—but these metrics remain siloed, each used only for post-hoc evaluation rather than as integrated training signals.

We address this gap with a simple intervention: augmenting the standard helpfulness reward with an IFEval-derived controllability signal. Our combined reward takes the form:

$$R = \alpha \cdot R_{\text{helpfulness}} + \beta \cdot R_{\text{IFEval}}$$

where $\alpha, \beta$ control the trade-off between objectives. We convert discrete IFEval constraint checks into continuous, differentiable rewards via sigmoid soft thresholds, enabling gradient-based optimization.

Our experiments validate three predictions:

1. **P1 (Controllability):** Bidirectional models achieve higher held-out IFEval accuracy than helpfulness-only baselines (+3.4pp strict accuracy).

2. **P2 (Helpfulness Maintenance):** At $\alpha \geq 0.8$, bidirectional models retain $\geq$95% of baseline AlpacaEval performance (96.4% observed).

3. **P3 (Safety Transfer):** Explicit constraint training transfers to implicit safety constraints, with 2-4pp gains on TruthfulQA and BBQ and strong positive correlation ($r=0.85$–$0.94$) between IFEval improvement and safety improvement.

The transfer finding (P3) is our most surprising result. Models trained to follow explicit format constraints—"respond in exactly 3 paragraphs," "include the word 'conclusion'"—show improved performance on safety benchmarks measuring truthfulness and bias. This suggests that controllability training builds general constraint-following capacity that extends beyond the explicit constraints seen during training.

**Contributions.** We provide:
- The first empirical test of bidirectional alignment training signals, validating the theoretical framework of Sun et al. [3]
- A methodology for repurposing rule-based evaluation metrics (IFEval) as differentiable RLHF training rewards
- A quantified estimate of explicit→implicit transfer: ~15% of IFEval improvement transfers to safety metrics
- Pareto characterization of the helpfulness-controllability trade-off, identifying viable operating points for different deployment priorities

The paper proceeds as follows: §2 surveys related work on RLHF and multi-objective alignment; §3 describes our methodology for converting IFEval to a training signal and integrating it with PPO; §4 details our experimental setup; §5 presents results; §6 discusses implications and limitations; §7 concludes.
