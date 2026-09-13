# Abstract

Current RLHF optimizes language models for helpfulness alone, neglecting the Human→AI direction of alignment: controllability. We introduce **bidirectional alignment**, augmenting standard helpfulness rewards with IFEval-derived controllability signals via the combined reward $R = \alpha \cdot R_{\text{helpfulness}} + \beta \cdot R_{\text{IFEval}}$. We convert discrete constraint checks into differentiable rewards using sigmoid soft thresholds.

Experiments on Llama-3-8B-Instruct validate three predictions: (1) bidirectional models achieve **+3.4pp** held-out IFEval strict accuracy over helpfulness-only baselines; (2) at α=0.8, models retain **96.4%** of baseline AlpacaEval performance; (3) explicit constraint training transfers to implicit safety constraints, with **+2.7pp** TruthfulQA and **+4.2pp** BBQ improvements and strong positive correlation (**r=0.94**) between IFEval gains and safety gains.

Our most surprising finding is the explicit→implicit transfer: models trained on format and length constraints improve on safety benchmarks measuring truthfulness and bias—constraints never seen during training. We estimate a ~15% transfer coefficient: each 1pp IFEval improvement predicts ~0.15pp safety improvement.

This work provides the first empirical validation of the bidirectional alignment framework (Sun et al. 2024), introduces IFEval as a differentiable training signal, and characterizes the helpfulness-controllability Pareto frontier. Code and checkpoints available at [REDACTED].
