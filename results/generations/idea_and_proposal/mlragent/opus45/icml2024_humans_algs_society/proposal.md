# Research Proposal: Preference Drift Detection in Human-Algorithm Feedback Loops via Counterfactual Trajectory Analysis

## 1. Introduction

### Background

The proliferation of algorithmic decision-making systems in social technologies has created unprecedented interactions between humans, algorithms, and society. Recommendation systems, content curation platforms, job matching algorithms, and credit scoring models increasingly mediate human access to information, opportunities, and resources. While these systems are designed to learn from human behavior and optimize for user satisfaction, they simultaneously shape the very preferences they aim to serve. This bidirectional influence creates complex feedback loops with potentially profound implications for individual autonomy and societal outcomes.

When a recommendation algorithm surfaces certain content to users, it not only responds to existing preferences but also influences future preferences by determining what users are exposed to. Over time, users' expressed preferences may gradually converge toward what the algorithm consistently presents, a phenomenon we term "algorithm-induced preference drift." This drift is particularly insidious because it is largely invisible to both users and system designers, making it difficult to distinguish from genuine, autonomous preference evolution.

Current literature has addressed related concerns from various angles. Work on bias accumulation in feedback loops (Xu et al., 2023) demonstrates how exposure mechanisms lead to systematic biases in recommendation quality. Research on RLHF alignment (Xiao et al., 2024) reveals preference collapse phenomena where minority preferences are systematically suppressed. The Drift framework (Kim et al., 2025) introduces methods for personalization based on implicit preferences, while CausalTAD (Li et al., 2024) demonstrates the power of causal reasoning for debiasing trajectory analysis. However, no existing framework directly addresses the fundamental challenge of detecting and quantifying algorithm-induced preference drift in human-algorithm feedback loops.

### Research Objectives

This research aims to develop a comprehensive framework for detecting and quantifying algorithm-induced preference drift through counterfactual trajectory analysis. Our specific objectives are:

1. To formalize the distinction between endogenous preference dynamics (natural evolution) and exogenous algorithmic influence using causal modeling
2. To develop methods for constructing counterfactual preference trajectories representing how user preferences would have evolved absent algorithmic intervention
3. To create a "Preference Authenticity Score" (PAS) that quantifies the divergence between observed and counterfactual preference trajectories
4. To validate the framework using semi-synthetic datasets with known ground-truth preference mechanisms
5. To derive design principles for "preference-preserving" algorithms that optimize for user satisfaction while maintaining authentic preference expression

### Significance

This research addresses critical challenges at the intersection of machine learning, causal inference, and human-computer interaction. By providing tools to audit recommendation systems for preference manipulation, we enable more ethical algorithmic design and regulatory oversight. Understanding preference drift is essential for preserving human autonomy in an increasingly algorithmically-mediated world and for preventing the homogenization of societal preferences that could undermine democratic pluralism and cultural diversity.

## 2. Methodology

### 2.1 Theoretical Framework

We model the human-algorithm interaction as a dynamic system where user preferences evolve over discrete time steps $t \in \{0, 1, 2, ..., T\}$. Let $P_t \in \mathbb{R}^d$ represent a user's latent preference vector at time $t$, and let $A_t$ denote the algorithmic treatment (e.g., set of recommended items) received at time $t$.

We decompose preference dynamics into two components:

$$P_{t+1} = f_{endo}(P_t, X_t) + g_{exo}(P_t, A_t) + \epsilon_t$$

where:
- $f_{endo}(P_t, X_t)$ captures endogenous preference evolution driven by user characteristics $X_t$ (life events, inherent taste development)
- $g_{exo}(P_t, A_t)$ captures exogenous algorithmic influence
- $\epsilon_t$ represents stochastic noise

The counterfactual preference trajectory under no algorithmic intervention is defined as:

$$P^{cf}_{t+1} = f_{endo}(P^{cf}_t, X_t) + \epsilon_t$$

with $P^{cf}_0 = P_0$. Our goal is to estimate $P^{cf}_t$ and quantify the drift $\Delta_t = ||P_t - P^{cf}_t||$.

### 2.2 Causal Model Specification

We construct a structural causal model (SCM) representing the data-generating process:

**Structural Equations:**
$$X_t = h_X(X_{t-1}, U_X)$$
$$A_t = \pi(P_{t-1}, X_t, H_t, U_A)$$
$$B_t = \sigma(P_t, A_t, U_B)$$
$$P_{t+1} = \phi(P_t, X_t, A_t, B_t, U_P)$$

where $H_t$ represents interaction history, $B_t$ denotes observed behavior (clicks, engagement), $\pi$ is the algorithmic policy, $\sigma$ is the behavior response function, $\phi$ is the preference update function, and $U_*$ are exogenous noise terms.

The causal graph encodes the following key assumptions:
1. Preferences causally influence behavior
2. The algorithm assigns treatments based on observable history and inferred preferences
3. Both preferences and algorithmic exposure influence future preferences

### 2.3 Identification Strategy

To identify the causal effect of algorithmic intervention on preferences, we leverage natural experiments arising from:

**Randomized Variation:** Many platforms conduct A/B tests or employ exploration strategies that create quasi-random variation in algorithmic treatment:
$$A_t = \pi_{exploit}(P_{t-1}, H_t) \cdot (1-Z_t) + \pi_{explore}(U_A) \cdot Z_t$$

where $Z_t \sim Bernoulli(\epsilon)$ indicates exploration episodes.

**Instrumental Variables:** We use platform-level policy changes (algorithm updates, UI modifications) as instruments that affect treatment but not preferences directly except through treatment.

**Difference-in-Differences:** For users experiencing different treatment intensities due to exogenous factors (geographic variation, device differences), we employ difference-in-differences estimation.

### 2.4 Preference Trajectory Modeling

We model preference dynamics using a neural temporal point process framework combined with variational inference.

**Encoder Network:** We encode observed behavior sequences $\{B_1, ..., B_t\}$ and algorithmic treatments $\{A_1, ..., A_t\}$ into a latent preference representation:

$$h_t = \text{LSTM}(h_{t-1}, [B_t; A_t; X_t])$$
$$q(P_t | B_{1:t}, A_{1:t}) = \mathcal{N}(\mu_t, \Sigma_t)$$

where $\mu_t = W_\mu h_t + b_\mu$ and $\Sigma_t = \text{diag}(\text{softplus}(W_\sigma h_t + b_\sigma))$.

**Preference Dynamics Model:** We parameterize the preference evolution as:

$$P_{t+1} | P_t, X_t, A_t \sim \mathcal{N}(\mu_{t+1|t}, \Sigma_{t+1|t})$$

where:
$$\mu_{t+1|t} = P_t + \alpha \cdot f_\theta(P_t, X_t) + \beta \cdot g_\psi(P_t, A_t)$$

The functions $f_\theta$ and $g_\psi$ are neural networks representing endogenous and exogenous dynamics respectively. The parameters $\alpha$ and $\beta$ control the relative magnitudes of each component.

**Counterfactual Generation:** Given the trained model, we generate counterfactual trajectories by intervening on the algorithmic treatment:

$$P^{cf}_{t+1} = P^{cf}_t + \alpha \cdot f_\theta(P^{cf}_t, X_t) + \epsilon_t$$

This corresponds to the $do(A_t = \emptyset)$ intervention in our causal model.

### 2.5 Preference Authenticity Score (PAS)

We define the Preference Authenticity Score at time $t$ as:

$$\text{PAS}_t = 1 - \frac{D_{KL}(p(P_t) || p(P^{cf}_t))}{\log(|\mathcal{P}|)}$$

where $D_{KL}$ denotes Kullback-Leibler divergence and $|\mathcal{P}|$ is the cardinality of the preference space (for normalization).

For practical computation, we use a Monte Carlo approximation:

$$\widehat{\text{PAS}}_t = 1 - \frac{1}{N}\sum_{i=1}^{N}\left[\log p(P^{(i)}_t) - \log p(P^{cf,(i)}_t)\right]$$

where samples are drawn from the variational posterior.

Additionally, we compute a trajectory-level authenticity score:

$$\text{PAS}_{traj} = \frac{1}{T}\sum_{t=1}^{T} \text{PAS}_t \cdot \gamma^{T-t}$$

where $\gamma \in (0,1)$ is a discount factor emphasizing recent drift.

### 2.6 Training Procedure

The model is trained end-to-end by maximizing the evidence lower bound (ELBO):

$$\mathcal{L} = \mathbb{E}_{q(P_{1:T}|B,A)}\left[\sum_{t=1}^{T}\log p(B_t|P_t, A_t)\right] - D_{KL}(q(P_{1:T}|B,A) || p(P_{1:T}|A))$$

We augment this with a causal identification loss leveraging the instrumental variable structure:

$$\mathcal{L}_{IV} = ||g_\psi(P_t, A_t) - g_\psi(P_t, A'_t)||^2$$

where $A'_t$ represents the treatment under exploration, ensuring the model correctly attributes preference changes to algorithmic influence.

### 2.7 Experimental Design

**Dataset Construction:**

1. **Semi-Synthetic Data:** We create datasets with known ground-truth preference mechanisms by simulating:
   - A population of 100,000 users with diverse initial preferences drawn from a mixture of Gaussians
   - Natural preference evolution following an Ornstein-Uhlenbeck process
   - Algorithmic influence modeled as attraction toward popular item clusters
   - Varying treatment intensities (control, mild, moderate, strong algorithmic influence)

2. **Real-World Data with Proxy Ground Truth:** We utilize:
   - MovieLens dataset with temporal user ratings, leveraging periods before/after recommendation system deployment
   - Music streaming data with natural experiments from algorithm rollouts

**Validation Protocol:**

1. **Ground Truth Recovery:** On semi-synthetic data, we measure:
   - Mean squared error between estimated and true $g_{exo}$ function
   - Correlation between computed PAS and true preference drift magnitude
   - Counterfactual trajectory accuracy: $\text{MSE}(\hat{P}^{cf}_t, P^{cf,true}_t)$

2. **Predictive Validity:** We assess whether detected drift predicts:
   - Future preference instability
   - Susceptibility to preference reversal under intervention

3. **Ablation Studies:** We systematically evaluate:
   - Impact of exploration rate on identification accuracy
   - Model performance under varying observability conditions
   - Sensitivity to preference space dimensionality

**Evaluation Metrics:**

- **Drift Detection AUC:** Area under ROC curve for classifying users experiencing significant drift
- **Counterfactual MSE:** Mean squared error of counterfactual trajectory estimates
- **Preference Stability Index:** Correlation between PAS and user preference consistency over time
- **Calibration Error:** Expected calibration error of PAS confidence intervals

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Novel Theoretical Framework:** A rigorous causal framework formalizing preference drift in human-algorithm feedback loops, providing the research community with principled tools for studying this phenomenon.

2. **Practical Diagnostic Tools:** Open-source software implementing the Preference Authenticity Score, enabling platform audits and regulatory assessments of recommendation system impacts on user autonomy.

3. **Empirical Insights:** Quantitative characterization of preference drift across domains (content recommendation, e-commerce, social media), identifying platform design choices that exacerbate or mitigate drift.

4. **Design Principles:** Actionable guidelines for developing "preference-preserving" algorithms that balance personalization with authenticity preservation, including regularization techniques that penalize excessive preference manipulation.

5. **Benchmark Datasets:** Semi-synthetic datasets with ground-truth preference mechanisms for evaluating future methods in this space.

### Impact

**Scientific Impact:** This research bridges causal inference, recommender systems, and human-computer interaction, establishing new research directions in understanding algorithmic influence on human cognition and behavior. The counterfactual trajectory framework extends beyond preferences to other domains where algorithms shape human outcomes.

**Societal Impact:** By providing tools to detect and quantify preference manipulation, this work supports:
- Regulatory efforts to ensure algorithmic accountability
- Platform design that respects user autonomy
- User empowerment through transparency about algorithmic influence
- Prevention of preference homogenization that threatens cultural diversity

**Industry Impact:** The framework offers practical value for platforms seeking to build sustainable relationships with users, moving beyond short-term engagement optimization toward long-term trust and authentic satisfaction.

Ultimately, this research contributes to developing human-algorithm ecosystems where technology serves human flourishing rather than reshaping humanity to serve technological optimization objectives.