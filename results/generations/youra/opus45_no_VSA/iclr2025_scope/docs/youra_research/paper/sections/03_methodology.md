# Methodology

We introduce Instruction-Prefix-Conditioned Routing (IPCR), a minimal approach for zero-shot adapter selection. Our design philosophy is to test whether intrinsic alignment exists before adding architectural complexity.

## Overview

Given an instruction $x$, IPCR routes to a bank of $k$ task-specific LoRA adapters $\{\theta_1, ..., \theta_k\}$ through three steps:

1. **Embed:** Encode the instruction prefix using a frozen sentence encoder $f: \mathcal{X} \rightarrow \mathbb{R}^d$
2. **Route:** Apply a linear probe $W \in \mathbb{R}^{k \times d}$ to predict adapter scores
3. **Select:** Choose the highest-scoring adapter (hard routing) or compute weighted combination (soft routing)

**Rationale:** If instruction semantics and adapter specializations share geometric structure, a linear mapping should suffice. This tests our hypothesis directly—any success demonstrates intrinsic alignment, and failure would motivate more complex architectures.

## Instruction Embedding

We use MiniLM-L6-v2 [Wang et al., 2020], a 22M-parameter sentence encoder pretrained via contrastive learning, as our embedding function $f$. The encoder is completely frozen during both probe training and inference.

**Why MiniLM?** Three considerations:
1. **Efficiency:** 22M parameters, 384-dimensional output, negligible latency overhead
2. **Pretraining:** Contrastive objective should provide task-relevant semantic clusters
3. **Simplicity:** Tests whether off-the-shelf embeddings contain routing signal

We encode only the instruction prefix (first 128 tokens), excluding input/output content. This focuses routing on task semantics rather than instance-specific features.

## Linear Probe Training

The routing probe is a multinomial logistic regression classifier:

$$p(y = j | x) = \frac{\exp(W_j \cdot f(x))}{\sum_{i=1}^k \exp(W_i \cdot f(x))}$$

where $W_j$ is the weight vector for adapter $j$. Training uses L-BFGS optimization with balanced class weights to handle task-frequency imbalance in FLAN.

**Why linear?** A linear probe has minimal capacity—it can only exploit structure that already exists in the embedding space. If the probe succeeds, we have evidence that MiniLM embeddings encode task-relevant structure. A complex nonlinear router would conflate learned routing with intrinsic alignment.

## Adapter Bank

Each adapter $\theta_j$ is a task-specialized LoRA [Hu et al., 2021] with:
- Rank $r = 16$ 
- Scaling factor $\alpha = 32$
- Applied to query/value projections in all attention layers

Adapters are trained independently on their respective task families, then frozen for routing experiments. This ensures the routing probe cannot modify adapter behavior—it can only select among fixed options.

## Routing Strategies

**Hard routing:** Select adapter with highest probe score: $\hat{j} = \arg\max_j W_j \cdot f(x)$

**Soft routing:** Compute weighted combination of adapter outputs:
$$\Delta W = \sum_{j=1}^k \sigma(W_j \cdot f(x)) \cdot \theta_j$$

where $\sigma$ is the softmax function. We report hard routing results in main experiments and analyze soft routing in ablations.

## Baseline Comparisons

To isolate routing contribution, we compare against:
- **Oracle:** Always select the adapter trained on the input's task family (upper bound)
- **Uniform:** Equal weight to all adapters (no routing information)  
- **Random:** Uniformly random adapter selection

This setup tests whether IPCR extracts meaningful routing signal versus simple aggregation strategies.
