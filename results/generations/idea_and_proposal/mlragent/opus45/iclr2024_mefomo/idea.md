# Title: Understanding the Geometry of In-Context Learning Through Representation Dynamics

## Motivation
In-context learning (ICL) is a remarkable emergent capability of large language models where they can solve new tasks from just a few demonstrations without parameter updates. Despite its practical importance, we lack understanding of *how* representations evolve during ICL and *why* certain examples work better than others. Current theories either focus on simplified linear settings or treat the model as a black box. Understanding the geometric structure of ICL in representation space could explain example selection, predict ICL success, and enable principled prompt engineering.

## Main Idea
We propose analyzing ICL through the lens of representation geometry dynamics. Specifically, we will:

1. **Track representation trajectories**: Measure how hidden representations of the query evolve across layers as in-context examples are added, characterizing the "path" from initial encoding to task-adapted representation.

2. **Identify geometric signatures**: Hypothesize that successful ICL corresponds to representations converging toward task-specific subspaces, measurable through metrics like projection onto principal components of task exemplars.

3. **Develop predictive framework**: Use these geometric features to predict ICL performance before generation, enabling automatic example selection.

4. **Theoretical grounding**: Connect findings to function class learning theory, showing how geometric convergence relates to implicit Bayesian inference.

Expected outcomes include interpretable metrics for ICL quality and principled example selection algorithms, advancing both theoretical understanding and practical prompt optimization.