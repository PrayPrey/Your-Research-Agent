# Causal Probing for Mechanistic Understanding of Hallucinations in Large Language Models

## 1. Introduction

### Background

Foundation models, particularly large language models (LLMs), have achieved remarkable success across diverse applications, from content generation and information retrieval to complex reasoning tasks. However, a critical reliability issue undermines their deployment in high-stakes domains: hallucinations—instances where models generate fluent, contextually plausible, yet factually incorrect information. Recent studies estimate that even state-of-the-art models hallucinate in 15-30% of factual queries, with rates increasing dramatically in specialized domains and under distributional shift.

The prevalence of hallucinations poses severe risks in critical applications. In healthcare, an LLM suggesting non-existent drug interactions could endanger patient safety. In legal contexts, fabricated case citations undermine judicial processes. In financial advisory, incorrect market analysis could lead to substantial economic losses. Despite these risks, current understanding of hallucinations remains largely phenomenological—we can detect them post-hoc but lack fundamental insight into their causal mechanisms.

Recent literature has approached hallucinations from multiple angles. CIP (Ma et al., 2025) proposes causal prompting frameworks to mitigate hallucinations through better context structuring. CausalGuard (Patel, 2025) combines causal reasoning with symbolic logic for detection. However, these works focus primarily on mitigation rather than mechanistic understanding. The Distributional Semantics Tracing framework (Bhatia et al., 2025) makes progress toward mechanistic analysis by identifying "commitment layers" where representations diverge from factuality, while Cheang et al. (2025) demonstrate that LLMs cannot reliably distinguish their own hallucinations because they employ identical recall processes for both factual and hallucinated content.

These findings reveal a critical gap: while we have developed increasingly sophisticated detection and mitigation techniques, we lack a comprehensive causal understanding of *why* specific neural mechanisms produce hallucinations. This gap prevents us from developing principled interventions that address root causes rather than symptoms.

### Research Objectives

This research proposes a systematic causal intervention framework to establish mechanistic understanding of hallucinations in LLMs. Our specific objectives are:

1. **Establish causal links** between specific neural components (attention heads, feed-forward networks, residual streams) and hallucination behaviors through systematic ablation and intervention experiments.

2. **Develop a mechanistic taxonomy** that maps different hallucination types (factual inconsistency, entity confabulation, logical incoherence, temporal/spatial errors) to distinct computational pathways within transformer architectures.

3. **Identify interpretable precursors** that reliably predict impending hallucinations based on internal model states, enabling proactive intervention.

4. **Design targeted intervention strategies** that modify specific circuits to reduce hallucinations while preserving model capabilities on factual tasks.

5. **Validate findings** across multiple model families, scales, and task domains to ensure generalizability.

### Significance

This research directly addresses the R2-FM workshop's central question: "How can we pinpoint and understand the causes behind known sources of FM unreliability?" By establishing causal—not merely correlational—relationships between model components and hallucinations, we enable:

- **Theoretical advancement**: A mechanistic theory of knowledge retrieval and confabulation in neural language models, grounded in causal analysis rather than behavioral observation.

- **Practical reliability**: Surgical editing techniques that modify hallucination-prone circuits without expensive retraining, and runtime monitoring systems that flag unreliable outputs before deployment.

- **Responsible AI development**: Principled design guidelines for next-generation foundation models that architecturally mitigate hallucination risks from inception.

- **High-stakes applications**: Enabling safe deployment in medicine, law, finance, and other domains where factual accuracy is non-negotiable.

## 2. Methodology

### 2.1 Research Design Overview

Our methodology employs three complementary causal intervention techniques: (1) systematic ablation studies to identify necessary components, (2) activation patching to isolate sufficient mechanisms, and (3) mechanistic circuit analysis to understand information flow. We will conduct experiments across multiple model families (GPT-2, Llama-2, GPT-J) and scales (125M to 13B parameters) to ensure robustness.

### 2.2 Data Collection and Curation

**Hallucination Dataset Construction**: We will curate a diverse dataset of 10,000+ query-response pairs spanning multiple hallucination types:

- **Factual hallucinations**: Queries about verifiable facts (e.g., "When was the Eiffel Tower built?") paired with both correct and hallucinated completions.
- **Entity confabulations**: Prompts requiring entity attributes where models frequently fabricate properties.
- **Logical inconsistencies**: Multi-hop reasoning tasks where models generate internally contradictory statements.
- **Temporal/spatial errors**: Questions about time-sensitive information or geographic facts.

Each instance will be annotated with:
- Ground truth factual status (verified against knowledge bases like Wikidata)
- Hallucination type classification
- Confidence scores from the model
- Semantic plausibility ratings

**Controlled Generation Pairs**: For each query, we will generate multiple completions and identify minimal pairs—responses that differ only in factual correctness—to enable precise causal comparisons.

### 2.3 Causal Intervention Framework

#### 2.3.1 Targeted Ablation Studies

We systematically deactivate model components to identify which are causally necessary for hallucinations. For a transformer layer $l$ with attention heads $h_1, ..., h_H$ and feed-forward network $\text{FFN}_l$:

**Attention Head Ablation**: Zero out the output of specific attention head $h_i$ at layer $l$:
$$\text{Attn}_l^{(-h_i)}(x) = \sum_{j \neq i} \text{head}_j + \text{residual}$$

**Feed-Forward Ablation**: Replace FFN activations with mean activations from a reference distribution:
$$\text{FFN}_l^{\text{ablated}}(x) = \mathbb{E}_{x' \sim \mathcal{D}_{\text{ref}}}[\text{FFN}_l(x')]$$

**Layer-wise Ablation**: Completely bypass a layer by copying residual stream:
$$h_{l+1} = h_l \text{ (skip layer } l \text{)}$$

**Metrics**: For each ablation, we measure:
- **Hallucination rate change**: $\Delta H = H_{\text{ablated}} - H_{\text{baseline}}$
- **Factual accuracy preservation**: Accuracy on known-factual completions
- **Fluency degradation**: Perplexity increase on general text

Components where ablation significantly reduces hallucinations ($\Delta H < -0.1$) without severely impacting factual accuracy indicate causal involvement in hallucination generation.

#### 2.3.2 Activation Patching Experiments

Activation patching isolates sufficient mechanisms by transplanting activations from factual to hallucinated contexts:

**Procedure**: Given a factual completion $C_{\text{factual}}$ and hallucinated completion $C_{\text{halluc}}$ for the same query:

1. Run forward pass for both, caching activations at all layers
2. For target layer $l$ and position $p$, replace activations:
$$h_l^{\text{patched}}(C_{\text{halluc}}, p) = h_l(C_{\text{factual}}, p)$$
3. Continue generation from patched state
4. Measure if patching "recovers" factual completion

**Causal Mediation Analysis**: Quantify how much hallucination is mediated through specific components:
$$\text{CME}_{l,p} = \mathbb{P}(\text{factual} | \text{patch}_{l,p}) - \mathbb{P}(\text{factual} | \text{no patch})$$

High causal mediation effect indicates the component is on the causal pathway from input to hallucination.

#### 2.3.3 Mechanistic Circuit Analysis

Building on causal intervention results, we trace complete computational circuits:

**Information Flow Tracking**: Use attention pattern analysis and gradient-based attribution to track how factual information flows (or fails to flow) through the network:
$$\text{IF}(h_i \rightarrow h_j) = \sum_{t,t'} \alpha_{t,t'}^{(i,j)} \cdot \left\| \frac{\partial h_j^{t'}}{\partial h_i^t} \right\|$$

**Knowledge Retrieval vs. Confabulation Pathways**: Compare circuits activated during:
- Correct factual recall (retrieving stored knowledge)
- Hallucinated responses (generating plausible but incorrect content)

**Hypothesis**: We expect to find specialized "fact retrieval heads" (similar to those identified in prior work on factual associations) that are bypassed during hallucinations, with alternative "pattern completion heads" compensating through spurious correlations.

### 2.4 Mechanistic Taxonomy Development

Based on intervention results, we will construct a taxonomy mapping hallucination types to neural mechanisms:

**Taxonomy Structure**:
- **Hallucination Type** → **Causal Mechanism** → **Model Components**
- Example: Entity Confabulation → Failed Attribute Binding → Specific late-layer attention heads

**Validation**: Cross-validate taxonomy through:
1. Predictive modeling: Train probes to detect hallucination types from component activation patterns
2. Cross-model verification: Verify mechanisms generalize across architectures
3. Intervention consistency: Confirm targeted component modifications affect predicted hallucination types

### 2.5 Predictive Indicator Development

Develop interpretable features from internal states that predict impending hallucinations:

**Candidate Indicators**:
- **Attention entropy**: High entropy in fact-retrieval heads suggests uncertain knowledge access
$$S_{\text{attn}} = -\sum_{i} \alpha_i \log \alpha_i$$
- **Representation confidence**: Distance to training distribution in activation space
$$d_{\text{conf}} = \min_{x \in \mathcal{D}_{\text{train}}} \|h_l(x_{\text{query}}) - h_l(x)\|$$
- **Circuit activation mismatch**: Difference between fact-retrieval and pattern-completion pathway activations
- **Commitment layer divergence**: Following Bhatia et al., measure representational divergence at identified commitment layers

**Predictive Model**: Train lightweight classifiers on these features to predict hallucination before generation completes:
$$P(\text{hallucination} | h_1, ..., h_L) = \sigma(W^T \phi(h_1, ..., h_L))$$

where $\phi$ extracts the candidate indicators.

### 2.6 Targeted Intervention Design

Design interventions that modify hallucination-prone circuits:

**Surgical Model Editing**: Use rank-one model editing (ROME) or mass-editing memory (MEMIT) to modify specific fact associations identified as hallucination sources.

**Circuit Dampening**: Reduce activation strength of confabulation pathways during inference:
$$h_l^{\text{dampened}} = h_l - \beta \cdot \text{proj}_{\text{confab}}(h_l)$$

**Reinforcement Steering**: Fine-tune with RL to penalize activation of hallucination circuits while preserving factual pathways.

### 2.7 Experimental Design and Evaluation

**Experimental Conditions**:
- Models: GPT-2 (125M, 1.5B), Llama-2 (7B, 13B), GPT-J (6B)
- Tasks: Factual QA (TruthfulQA, PopQA), multi-hop reasoning (HotpotQA), biographical generation
- Baselines: Standard generation, existing hallucination mitigation (CIP, CausalGuard)

**Evaluation Metrics**:
1. **Hallucination Rate**: Percentage of factually incorrect claims
2. **Factual Accuracy**: Precision/recall on verifiable facts
3. **Causal Necessity Score**: Ablation impact on hallucination rate
4. **Causal Sufficiency Score**: Patching recovery rate
5. **Intervention Efficiency**: Hallucination reduction per model parameter modified
6. **Capability Preservation**: Performance on general language tasks (GLUE, HellaSwag)

**Statistical Analysis**: Use mixed-effects models to account for variability across models, tasks, and hallucination types. Establish causal claims through randomization tests and sensitivity analysis.

### 2.8 Validation and Generalization

**Cross-model Validation**: Verify that mechanisms identified in smaller models (GPT-2) transfer to larger models (Llama-2 13B).

**Cross-domain Validation**: Test whether interventions effective on factual QA generalize to other hallucination-prone domains (medical questions, code generation).

**Adversarial Robustness**: Evaluate whether identified mechanisms remain consistent under adversarial prompting designed to elicit hallucinations.

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Scientific Contributions**:

1. **Mechanistic Taxonomy**: A comprehensive mapping between hallucination types and causal neural mechanisms, providing the first systematic mechanistic account of why LLMs hallucinate. This taxonomy will specify which attention heads, feed-forward networks, and residual stream components are causally responsible for different hallucination modes.

2. **Predictive Framework**: Validated interpretable indicators that predict hallucinations from internal model states with >80% accuracy before generation completes, enabling proactive intervention rather than post-hoc detection.

3. **Causal Circuit Diagrams**: Detailed computational pathways distinguishing factual knowledge retrieval from confabulation, revealing how models compensate for missing knowledge through pattern completion rather than epistemic uncertainty.

4. **Intervention Techniques**: Targeted editing methods that reduce hallucinations by 40-60% while preserving >95% of capability on factual tasks, demonstrating that hallucinations arise from modifiable circuits rather than fundamental architectural limitations.

**Technical Deliverables**:

- Open-source toolkit implementing causal intervention methods (ablation, patching, circuit analysis) for hallucination analysis
- Curated benchmark dataset of 10,000+ annotated hallucination instances across diverse types
- Pre-trained predictive models for hallucination detection across multiple architectures
- Detailed documentation of hallucination-prone circuits in popular open models

### Broader Impact

**Advancing Theoretical Understanding**: This research establishes a causal—rather than correlational—framework for understanding foundation model unreliability. By moving beyond behavioral observation to mechanistic explanation, we enable principled reasoning about when and why models fail, informing theoretical frameworks for guaranteed reliability.

**Enabling Safe Deployment**: The predictive indicators and intervention techniques directly address practical barriers to deploying LLMs in high-stakes domains. Healthcare providers can integrate runtime monitoring systems that flag uncertain outputs. Legal researchers can verify that citations are retrieved from genuine knowledge rather than confabulated. Financial analysts can distinguish grounded predictions from pattern-based extrapolations.

**Informing Next-Generation Design**: Mechanistic insights guide architectural innovations. If we discover that hallucinations arise primarily from specific attention patterns, we can design attention mechanisms that architecturally prevent such patterns. If feed-forward networks store factual knowledge in separable subspaces from pattern knowledge, we can build models with explicit epistemic representations.

**Ethical and Responsible AI**: By establishing causal understanding of unreliability, this research enables more honest communication about model limitations. Rather than vague warnings about "possible errors," we can specify conditions under which models are likely to hallucinate and provide uncertainty estimates grounded in mechanistic understanding.

**Broader Applicability**: While focused on hallucinations, the causal intervention methodology generalizes to other reliability challenges—prompt sensitivity, spurious correlations, lack of self-consistency. The toolkit and framework we develop will enable the research community to conduct similar mechanistic analyses across diverse failure modes.

**Societal Benefits**: Reliable foundation models are essential for equitable AI deployment. Hallucinations disproportionately harm users with less ability to verify outputs—non-experts, users in low-resource languages, and those accessing specialized information. By improving fundamental reliability, this research promotes more equitable access to AI capabilities.

### Limitations and Future Directions

We acknowledge several limitations. First, our analysis focuses on transformer-based language models; findings may not generalize to other architectures (e.g., state-space models, diffusion models). Second, causal interventions reveal correlations under specific distributional assumptions; adversarial inputs may activate different mechanisms. Third, the relationship between hallucinations in language models and multimodal foundation models requires separate investigation.

Future work should extend this framework to: (1) vision-language models where hallucinations manifest as misalignment between visual content and textual descriptions, (2) agent-based systems where hallucinations compound through multi-step reasoning, and (3) continually learning systems where the causal structure may evolve over time.

### Conclusion

This research addresses a critical gap in foundation model reliability by establishing causal mechanistic understanding of hallucinations. Through systematic intervention experiments, we will identify the neural circuits responsible for generating factually incorrect content, develop predictive indicators of impending hallucinations, and design targeted interventions that improve reliability without sacrificing capabilities. The resulting mechanistic taxonomy, predictive framework, and intervention techniques will advance both theoretical understanding and practical deployment of trustworthy AI systems, directly contributing to the responsible development of foundation models for high-stakes applications.