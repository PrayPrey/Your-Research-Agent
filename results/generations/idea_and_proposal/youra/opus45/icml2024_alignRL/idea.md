# Research Idea

## Title
Learned Environment Complexity: Meta-Training Neural Predictors for Algorithm-Specific RL Performance

## Motivation
A critical gap exists between RL theory and practice: theoretical complexity measures focus on worst-case scenarios and ignore algorithm-specific behaviors, while empirical successes rely on heuristics that don't generalize. Existing hand-crafted measures like Effective Horizon achieve only moderate correlation (r ≈ 0.5) with actual deep RL performance because they treat all algorithms identically, missing the crucial algorithm-environment interaction. Practitioners need reliable methods to predict which algorithm will succeed on a given task without exhaustive experimentation.

## Main Idea
We propose Learned Environment Complexity (LEC), a meta-learned predictor that estimates algorithm-specific RL performance from MDP structural features and early training signals. The core insight is that algorithm-environment interaction patterns—which static measures miss—can be learned from diverse training data rather than manually designed.

**Methodology:** Train a neural network on MDP-algorithm pairs across Atari, MuJoCo, Procgen, and BRIDGE benchmarks, using structural features (state-action space, reward sparsity, transition entropy) combined with early training signals (first 10% of training: returns, gradient norms, policy entropy).

**Predictions:** LEC will achieve Pearson r > 0.70 correlation with final performance, significantly exceeding Effective Horizon (r ≈ 0.50), and enable >70% accuracy in algorithm selection. Falsification occurs if r ≤ 0.55.

**Impact:** Bridges theory-practice gap by providing practitioners with principled algorithm selection while offering theorists data-driven insights into what makes RL problems tractable.