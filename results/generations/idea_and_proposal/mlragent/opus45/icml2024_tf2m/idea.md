# Research Idea

## Title
Information-Theoretic Analysis of In-Context Learning Capacity in Transformers

## Motivation
In-context learning (ICL) enables LLMs to learn new tasks from few examples without parameter updates, yet we lack theoretical understanding of *how much* information can be effectively processed through context. Current analyses focus on whether ICL works, not its fundamental limits. Understanding the information-theoretic capacity of ICL would explain why performance plateaus with more examples, guide optimal context utilization, and inform efficient prompt engineering strategies.

## Main Idea
We propose analyzing ICL through the lens of information bottleneck theory, treating the transformer's attention mechanism as a channel with finite capacity for task-relevant information transmission.

**Methodology:**
1. Model ICL as an information channel where context examples are encoded into intermediate representations, and derive upper bounds on mutual information between context and predictions
2. Characterize how attention patterns compress task-relevant information across layers, identifying theoretical "saturation points"
3. Analyze the trade-off between number of examples and per-example information utilization

**Expected Outcomes:**
- Provable bounds on ICL capacity as a function of model dimensions and context length
- Theoretical explanation for diminishing returns with additional context examples
- Principled guidelines for context allocation in multi-task prompts

**Impact:** This framework would bridge the gap between empirical ICL observations and theoretical understanding, enabling more efficient use of limited context windows and informing architectural improvements for enhanced in-context learning.