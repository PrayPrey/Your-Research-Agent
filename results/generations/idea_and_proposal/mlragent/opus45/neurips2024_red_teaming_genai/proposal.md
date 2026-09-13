# Research Proposal: Adaptive Red Teaming via Reinforcement Learning with Evolving Attack Taxonomies

## 1. Introduction

### Background

The proliferation of Generative AI (GenAI) systems across critical domains—from healthcare and education to legal services and creative industries—has intensified concerns about their safety, security, and trustworthiness. These powerful models, while transformative, harbor latent vulnerabilities that malicious actors can exploit to generate harmful content, violate privacy, breach copyright, or circumvent ethical guidelines. Red teaming has emerged as the primary methodology for proactively identifying such vulnerabilities before deployment, simulating adversarial attacks to stress-test model robustness.

However, current red teaming paradigms face a fundamental limitation: they predominantly rely on static benchmarks and human-crafted adversarial prompts. This approach suffers from three critical shortcomings. First, as models are iteratively fine-tuned to resist known attacks, static benchmarks rapidly become obsolete, creating a perpetual "whack-a-mole" dynamic where safety measures chronically lag behind emerging threats. Second, human red teamers, despite their creativity, cannot systematically explore the combinatorial explosion of potential vulnerability spaces, leaving dangerous blind spots in safety evaluations. Third, existing frameworks lack structured categorization of discovered vulnerabilities, impeding systematic coverage analysis and the development of comprehensive defense strategies.

Recent advances in reinforcement learning (RL) for adversarial attack generation offer promising directions. Works such as Active Attacks (Yun et al., 2025) demonstrate that RL-based methods can adapt as victim models evolve, while AutoRedTeamer (Zhou et al., 2025) showcases the potential of multi-agent architectures with memory-guided attack selection. Red-Bandit (Ziakas et al., 2025) illustrates the value of bandit-guided expert selection for balancing exploration and exploitation. However, these approaches treat attack discovery and vulnerability categorization as separate concerns, missing opportunities for synergistic improvement.

### Research Objectives

This research proposes **AdaptiveRedTeam**, a novel reinforcement learning framework that unifies continuous attack discovery with dynamic taxonomy evolution. Our specific objectives are:

1. **Develop an RL-based attack generator** that maximizes policy violations across diverse harm categories while explicitly rewarding novelty and coverage.

2. **Design a hierarchical clustering module** that automatically organizes discovered attacks into an evolving, interpretable taxonomy of vulnerability types.

3. **Implement a novelty detection mechanism** that identifies under-explored vulnerability regions and guides exploration toward them.

4. **Create quantitative safety coverage metrics** that measure the comprehensiveness of red teaming efforts relative to the discovered attack taxonomy.

5. **Validate the framework** across multiple state-of-the-art LLMs, demonstrating discovery of previously unknown vulnerability clusters.

### Significance

This research addresses a critical gap in AI safety evaluation by shifting from reactive to proactive vulnerability discovery. By coupling attack generation with structured categorization, AdaptiveRedTeam enables security researchers to understand not just *whether* vulnerabilities exist, but *what kinds* of vulnerabilities remain unexplored. The framework provides actionable intelligence for defense prioritization and offers quantitative metrics for safety coverage—a crucial capability for regulatory compliance and responsible AI deployment.

## 2. Methodology

### 2.1 System Architecture Overview

AdaptiveRedTeam comprises three interconnected components: (1) a Reinforcement Learning Attack Generator (RLAG), (2) a Dynamic Taxonomy Clustering Module (DTCM), and (3) a Novelty-Guided Exploration Mechanism (NGEM). These components operate in a continuous feedback loop, where discovered attacks inform taxonomy updates, which in turn guide subsequent exploration strategies.

### 2.2 Reinforcement Learning Attack Generator (RLAG)

The RLAG formulates red teaming as a Markov Decision Process (MDP) defined by the tuple $\mathcal{M} = (\mathcal{S}, \mathcal{A}, \mathcal{T}, \mathcal{R}, \gamma)$, where:

- **State space** $\mathcal{S}$: Each state $s_t$ encodes the current attack prompt being constructed, represented as a sequence of tokens, along with contextual information including the target harm category $c \in \mathcal{C}$ and the current taxonomy embedding.

- **Action space** $\mathcal{A}$: Actions correspond to token selection from the vocabulary, with special actions for template application and semantic transformations.

- **Transition function** $\mathcal{T}$: Deterministic transitions append selected tokens to the current prompt sequence.

- **Reward function** $\mathcal{R}$: A composite reward function combining attack success, novelty, and coverage:

$$\mathcal{R}(s_t, a_t) = \lambda_1 R_{\text{success}}(p, M) + \lambda_2 R_{\text{novelty}}(p, \mathcal{T}_{\text{ax}}) + \lambda_3 R_{\text{coverage}}(p, \mathcal{T}_{\text{ax}})$$

where $p$ denotes the generated prompt, $M$ the target model, and $\mathcal{T}_{\text{ax}}$ the current taxonomy.

**Attack Success Reward**: We employ a learned safety classifier $f_\theta$ trained on existing jailbreak datasets to evaluate whether the target model's response $M(p)$ violates safety policies:

$$R_{\text{success}}(p, M) = \sigma(f_\theta(M(p))) \cdot H(c, M(p))$$

where $\sigma(\cdot)$ is the sigmoid function and $H(c, M(p))$ measures harm-category-specific severity using a harm taxonomy alignment score.

**Novelty Reward**: To encourage exploration of new attack strategies, we compute the minimum distance to existing attacks in the taxonomy embedding space:

$$R_{\text{novelty}}(p, \mathcal{T}_{\text{ax}}) = \min_{v \in V(\mathcal{T}_{\text{ax}})} \left(1 - \cos(e_p, e_v)\right)$$

where $e_p$ is the embedding of prompt $p$, $V(\mathcal{T}_{\text{ax}})$ is the set of taxonomy cluster centroids, and $\cos(\cdot, \cdot)$ denotes cosine similarity.

**Coverage Reward**: We incentivize balanced exploration across taxonomy branches:

$$R_{\text{coverage}}(p, \mathcal{T}_{\text{ax}}) = \log\left(\frac{1}{n_{\text{cluster}(p)} + 1}\right)$$

where $n_{\text{cluster}(p)}$ is the number of previously discovered attacks in the cluster to which $p$ would be assigned.

We optimize the policy $\pi_\phi$ using Proximal Policy Optimization (PPO) with an entropy bonus to maintain exploration:

$$\mathcal{L}(\phi) = \mathbb{E}_t\left[\min\left(r_t(\phi)\hat{A}_t, \text{clip}(r_t(\phi), 1-\epsilon, 1+\epsilon)\hat{A}_t\right)\right] + \beta H(\pi_\phi)$$

where $r_t(\phi) = \frac{\pi_\phi(a_t|s_t)}{\pi_{\phi_{\text{old}}}(a_t|s_t)}$, $\hat{A}_t$ is the generalized advantage estimate, and $H(\pi_\phi)$ is the policy entropy.

### 2.3 Dynamic Taxonomy Clustering Module (DTCM)

The DTCM maintains a hierarchical taxonomy of attack strategies that evolves as new vulnerabilities are discovered. We employ a modified hierarchical agglomerative clustering algorithm with online updates.

**Embedding Generation**: Each successful attack prompt $p$ is encoded using a fine-tuned sentence transformer $E_\psi: \mathcal{P} \rightarrow \mathbb{R}^d$, producing a dense semantic representation that captures attack strategy characteristics.

**Hierarchical Clustering**: The taxonomy $\mathcal{T}_{\text{ax}}$ is represented as a tree structure where leaf nodes correspond to individual attacks and internal nodes represent attack categories at varying granularity levels. We define the linkage criterion using Ward's method:

$$d(C_i, C_j) = \frac{n_i n_j}{n_i + n_j} \|\mu_i - \mu_j\|^2$$

where $C_i, C_j$ are clusters, $n_i, n_j$ their sizes, and $\mu_i, \mu_j$ their centroids.

**Online Taxonomy Update**: When a new attack $p$ is discovered, we compute its assignment and potentially restructure the taxonomy:

1. Compute embedding $e_p = E_\psi(p)$
2. Find nearest cluster $C^* = \arg\min_{C \in \mathcal{T}_{\text{ax}}} d(\{p\}, C)$
3. If $d(\{p\}, C^*) > \tau_{\text{new}}$, create new cluster branch
4. Otherwise, assign to $C^*$ and update centroid: $\mu_{C^*} \leftarrow \frac{n_{C^*} \mu_{C^*} + e_p}{n_{C^*} + 1}$
5. Periodically rebalance tree structure using batch re-clustering

**Taxonomy Labeling**: We employ GPT-4 to generate human-interpretable labels for newly formed clusters based on representative attack samples, enabling intuitive understanding of vulnerability types.

### 2.4 Novelty-Guided Exploration Mechanism (NGEM)

The NGEM addresses the exploration-exploitation tradeoff by maintaining uncertainty estimates over the taxonomy space and directing the attack generator toward under-explored regions.

**Coverage Tracking**: We maintain a visitation count $N(C)$ for each taxonomy cluster $C$ and compute a coverage score:

$$\text{Coverage}(\mathcal{T}_{\text{ax}}) = \frac{1}{|\mathcal{C}|} \sum_{C \in \mathcal{C}} \mathbb{I}[N(C) > \tau_{\text{min}}]$$

**Exploration Bonus**: Following the count-based exploration paradigm, we add an intrinsic motivation signal:

$$R_{\text{explore}}(p) = \frac{\eta}{\sqrt{N(\text{cluster}(p)) + 1}}$$

where $\eta$ is a scaling hyperparameter.

**Targeted Exploration**: For clusters with low visitation counts, we generate seed prompts by sampling from cluster centroids and applying controlled perturbations, biasing the initial state distribution of the RL agent toward unexplored regions.

### 2.5 Experimental Design

**Target Models**: We evaluate AdaptiveRedTeam on five state-of-the-art LLMs: GPT-4, Claude-3, Llama-3-70B, Gemini-Pro, and Mistral-Large. This selection spans both proprietary and open-source models with varying safety training approaches.

**Datasets and Baselines**: We compare against:
- Static benchmark evaluation (AdvBench, JailbreakBench)
- GCG (Greedy Coordinate Gradient) attack
- PAIR (Prompt Automatic Iterative Refinement)
- AutoDAN (Automated Jailbreak Generation)
- Active Attacks (Yun et al., 2025)
- AutoRedTeamer (Zhou et al., 2025)

**Evaluation Metrics**:

1. **Attack Success Rate (ASR)**: Percentage of generated prompts that elicit policy-violating responses, evaluated by both automated classifiers and human annotators:
$$\text{ASR} = \frac{\sum_{p \in P} \mathbb{I}[\text{violates}(M(p))]}{|P|}$$

2. **Taxonomy Coverage Score (TCS)**: Proportion of taxonomy clusters with at least $k$ successful attacks:
$$\text{TCS}_k = \frac{|\{C : N(C) \geq k\}|}{|\mathcal{C}|}$$

3. **Novel Cluster Discovery Rate (NCDR)**: Number of new taxonomy clusters discovered per unit time, measured as new clusters per 1000 attack attempts.

4. **Attack Diversity Index (ADI)**: Entropy over taxonomy cluster distribution:
$$\text{ADI} = -\sum_{C \in \mathcal{C}} \frac{N(C)}{N_{\text{total}}} \log \frac{N(C)}{N_{\text{total}}}$$

5. **Transfer Success Rate (TSR)**: ASR of attacks discovered on one model when applied to other models, measuring generalizability.

**Experimental Protocol**:
- Phase 1 (Warm-up): Train RLAG on existing jailbreak datasets for 10,000 steps
- Phase 2 (Exploration): Run full system for 100,000 attack generation steps per target model
- Phase 3 (Cross-validation): Evaluate transferability across models
- Phase 4 (Human evaluation): Expert annotation of 1,000 sampled successful attacks for harm severity and novelty assessment

**Ablation Studies**: We conduct ablations removing each component (novelty reward, coverage reward, dynamic taxonomy updates) to quantify individual contributions.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Novel Vulnerability Discovery**: We anticipate discovering 15-25 previously unknown vulnerability clusters across target models, including attack strategies that evade current safety measures. These discoveries will be responsibly disclosed to model developers.

2. **Improved Attack Success Rates**: Based on preliminary experiments and related work benchmarks, we expect AdaptiveRedTeam to achieve 40-60% higher ASR compared to static benchmarks and 15-25% improvement over existing RL-based methods.

3. **Comprehensive Attack Taxonomy**: The system will produce an interpretable, hierarchical taxonomy of 100+ attack categories, providing the research community with a structured understanding of vulnerability landscapes.

4. **Quantitative Coverage Metrics**: We will establish baseline coverage metrics for major LLMs, enabling standardized safety evaluation and comparison.

5. **Transferable Attack Strategies**: We expect 30-50% of discovered attacks to transfer across models, revealing fundamental vulnerabilities in current safety training paradigms.

### Broader Impact

**Scientific Contributions**: This research advances the theoretical understanding of adversarial robustness in language models by providing a systematic framework for vulnerability characterization. The dynamic taxonomy offers a living document of attack strategies that evolves with the field.

**Practical Applications**: AdaptiveRedTeam can be integrated into model development pipelines for continuous safety testing, enabling organizations to identify vulnerabilities before deployment. The coverage metrics provide actionable guidance for defense prioritization.

**Policy Implications**: Quantitative safety coverage metrics support regulatory frameworks by enabling objective assessment of model safety. The taxonomy provides a common vocabulary for discussing AI vulnerabilities across stakeholders.

**Ethical Considerations**: We acknowledge the dual-use nature of this research. To mitigate risks, we commit to responsible disclosure protocols, delayed publication of specific attack strings, and collaboration with model developers on remediation before public release. The ultimate goal is strengthening AI safety, not enabling malicious use.

**Future Directions**: This framework establishes foundations for automated safety verification, working toward formal safety guarantees through comprehensive vulnerability coverage. Extensions may include multi-modal red teaming, agent-based attack simulation, and integration with formal verification methods.