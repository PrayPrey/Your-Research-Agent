# Research Proposal: Hierarchical Safe Multi-Fidelity Bayesian Optimization via Cross-Fidelity Safety Transfer

## 1. Title

**Hierarchical Safe Multi-Fidelity Bayesian Optimization via Cross-Fidelity Safety Transfer for Cost-Efficient Constrained Experimentation**

---

## 2. Introduction

### 2.1 Background

Bayesian optimization (BO) has emerged as a powerful framework for optimizing expensive black-box functions, finding widespread applications in drug discovery, materials design, robotics, and chemical engineering. In many of these high-stakes domains, optimization must respect safety constraints—certain regions of the design space may correspond to toxic compounds, unstable materials, or dangerous robot configurations. Violating these constraints during experimentation can result in catastrophic outcomes, wasted resources, or ethical concerns.

Safe Bayesian optimization methods, exemplified by SafeOpt and its variants, address this challenge by maintaining probabilistic safety guarantees throughout the optimization process. These methods construct confidence bounds on constraint functions using Gaussian processes (GPs) and only evaluate points that are predicted to be safe with high probability. While theoretically elegant and practically important, SafeOpt-style methods suffer from a critical limitation: they require all evaluations to be performed at the highest fidelity level, which is often prohibitively expensive.

Simultaneously, multi-fidelity Bayesian optimization (MF-BO) has demonstrated remarkable success in reducing optimization costs by leveraging cheap, approximate evaluations (e.g., computational simulations) to guide the search before committing to expensive high-fidelity evaluations (e.g., physical experiments). In drug discovery, for instance, computational toxicity predictions cost orders of magnitude less than experimental assays. However, existing MF-BO methods lack safety guarantees—they may query unsafe regions at any fidelity level, which is unacceptable when even low-fidelity evaluations carry risk or when low-fidelity safety violations correlate with high-fidelity dangers.

This creates a fundamental gap in the literature: **no existing method provides both provable safety guarantees AND multi-fidelity cost efficiency**. Bridging this gap could dramatically accelerate safe experimentation across computational biology, robotics, and chemical engineering, where both safety and cost are paramount concerns.

### 2.2 Research Objectives

This research proposes **Hierarchical Safe Multi-Fidelity Bayesian Optimization (HS-MFBO)**, a novel framework that enables safe exploration using cheap low-fidelity evaluations while preserving high-fidelity safety guarantees. Our specific objectives are:

1. **Develop a principled mechanism for cross-fidelity safety transfer** that quantifies the relationship between low-fidelity and high-fidelity constraint functions using a Linear Model of Coregionalization (LMC) kernel.

2. **Derive a transfer error bound** $\tau$ that captures the maximum discrepancy between fidelity levels, enabling conservative adjustment of safety predictions.

3. **Design a margin inflation strategy** that transforms low-fidelity safety predictions into high-fidelity safety guarantees through a tunable factor $\beta = 1 + \tau/\sigma_{LF}$.

4. **Validate the method empirically** on synthetic benchmarks and real-world drug toxicity screening datasets, demonstrating zero constraint violations with $\geq 40\%$ cost reduction compared to single-fidelity SafeOpt.

### 2.3 Significance

This research addresses a critical need in adaptive experimental design by reconciling two previously incompatible desiderata: safety and cost efficiency. The expected contributions include:

- **Theoretical:** A novel framework for transferring safety guarantees across fidelity levels with provable bounds.
- **Algorithmic:** A practical algorithm that integrates multi-fidelity modeling with safe exploration.
- **Empirical:** Demonstration of significant cost savings in drug discovery and materials design applications without compromising safety.

Success in this research could enable safer and more efficient experimentation in domains where both concerns are paramount, potentially accelerating the discovery of new therapeutics and materials while reducing experimental risks.

---

## 3. Methodology

### 3.1 Problem Formulation

We consider the constrained optimization problem:

$$\max_{x \in \mathcal{X}} f(x) \quad \text{subject to} \quad g(x) \geq 0$$

where $f: \mathcal{X} \rightarrow \mathbb{R}$ is the objective function and $g: \mathcal{X} \rightarrow \mathbb{R}$ is the safety constraint function. Both functions can be evaluated at multiple fidelity levels $m \in \{1, 2, \ldots, M\}$, where $m = M$ denotes the highest (most accurate and expensive) fidelity. We denote the cost of evaluation at fidelity $m$ as $c_m$, with $c_1 \ll c_M$.

**Key Assumption:** The safety constraints across fidelities are correlated, i.e., $g_m(x)$ and $g_M(x)$ share structural similarities that can be learned from data.

### 3.2 Multi-Fidelity Gaussian Process Model with LMC Kernel

We model the constraint function across fidelities using a multi-output Gaussian process with a Linear Model of Coregionalization (LMC) kernel. The LMC kernel decomposes the cross-fidelity covariance as:

$$k_{LMC}((x, m), (x', m')) = \sum_{q=1}^{Q} a_{m,q} a_{m',q} k_q(x, x')$$

where $a_{m,q}$ are mixing coefficients for fidelity $m$ and latent function $q$, and $k_q$ are base kernels (e.g., RBF with ARD). This formulation captures how different fidelities share common latent structure while allowing for fidelity-specific variations.

Let $\mathbf{A} = [a_{m,q}]$ be the mixing coefficient matrix. The cross-fidelity correlation between fidelities $m$ and $m'$ is encoded in the inner product $\mathbf{a}_m^\top \mathbf{a}_{m'}$.

### 3.3 Transfer Error Bound Computation

The core innovation of HS-MFBO is the explicit quantification of cross-fidelity prediction uncertainty. We define the **transfer error bound** $\tau$ as:

$$\tau \leq \|\mathbf{a}_{HF} - \mathbf{a}_{LF}\|_2 \cdot \sup_{x \in \mathcal{X}} \sqrt{\sum_{q=1}^{Q} k_q(x, x)}$$

This bound captures the maximum discrepancy between high-fidelity (HF) and low-fidelity (LF) constraint predictions due to differences in their mixing coefficients. In practice, we estimate $\tau$ from the posterior distribution:

$$\tau = \mathbb{E}\left[\sup_{x \in \mathcal{X}} |g_{HF}(x) - g_{LF}(x)| \mid \mathcal{D}\right] + \kappa \cdot \text{Std}\left[\sup_{x \in \mathcal{X}} |g_{HF}(x) - g_{LF}(x)| \mid \mathcal{D}\right]$$

where $\kappa$ is a confidence parameter (typically $\kappa = 2$ for 95% confidence) and $\mathcal{D}$ is the observed data.

### 3.4 Safety Margin Inflation Strategy

Given the transfer error bound $\tau$, we inflate the safety margin when making decisions based on low-fidelity evaluations. The **margin inflation factor** is:

$$\beta = 1 + \frac{\tau}{\sigma_{LF}(x)}$$

where $\sigma_{LF}(x)$ is the GP predictive standard deviation at fidelity LF. A point $x$ is deemed **safe for low-fidelity evaluation** if:

$$\mu_{LF}(x) - \beta \cdot \sigma_{LF}(x) \geq 0$$

where $\mu_{LF}(x)$ is the GP predictive mean. This inflated margin ensures that with high probability:

$$P(g_{HF}(x) \geq 0 \mid g_{LF}(x) \text{ predicted safe with margin } \beta) \geq 1 - \delta$$

for a user-specified confidence level $1 - \delta$.

### 3.5 HS-MFBO Algorithm

The complete algorithm proceeds as follows:

**Algorithm: Hierarchical Safe Multi-Fidelity Bayesian Optimization (HS-MFBO)**

**Input:** Initial safe set $\mathcal{S}_0$, budget $B$, fidelity costs $\{c_m\}$, confidence parameters $\kappa$, $\delta$

**Initialize:**
1. Evaluate initial safe points at high-fidelity: $\mathcal{D}_{HF} = \{(x_i, g_{HF}(x_i), f_{HF}(x_i))\}_{i=1}^{n_0}$
2. Fit LMC-GP model on $\mathcal{D} = \mathcal{D}_{HF}$
3. Compute initial transfer error bound $\tau_0$

**Main Loop:** While budget $B$ not exhausted:

**Step 1: Safe Set Expansion at Low-Fidelity**
- Compute margin inflation factor: $\beta_t = 1 + \tau_t / \sigma_{LF}(x)$
- Identify candidate safe set: $\mathcal{S}_{LF} = \{x : \mu_{LF}(x) - \beta_t \sigma_{LF}(x) \geq 0\}$
- Select exploration point: $x_{LF}^* = \arg\max_{x \in \mathcal{S}_{LF}} \alpha_{explore}(x)$
- Evaluate at low-fidelity: $g_{LF}(x_{LF}^*), f_{LF}(x_{LF}^*)$
- Update dataset: $\mathcal{D}_{LF} \leftarrow \mathcal{D}_{LF} \cup \{(x_{LF}^*, g_{LF}, f_{LF})\}$
- Update cost: $B \leftarrow B - c_{LF}$

**Step 2: Calibration Check**
- If sufficient LF data accumulated, validate LF predictions on held-out HF data
- Update transfer error bound: $\tau_{t+1}$ based on observed discrepancies
- Adjust $\beta$ adaptively if calibration indicates misspecification

**Step 3: High-Fidelity Exploitation**
- Identify high-confidence safe set: $\mathcal{S}_{HF} = \{x : \mu_{HF}(x) - \kappa \sigma_{HF}(x) \geq 0\}$
- Select exploitation point: $x_{HF}^* = \arg\max_{x \in \mathcal{S}_{HF}} \alpha_{exploit}(x)$
- Evaluate at high-fidelity: $g_{HF}(x_{HF}^*), f_{HF}(x_{HF}^*)$
- Update dataset: $\mathcal{D}_{HF} \leftarrow \mathcal{D}_{HF} \cup \{(x_{HF}^*, g_{HF}, f_{HF})\}$
- Update cost: $B \leftarrow B - c_{HF}$

**Step 4: Model Update**
- Refit LMC-GP on combined data $\mathcal{D} = \mathcal{D}_{LF} \cup \mathcal{D}_{HF}$
- Update transfer error bound $\tau_{t+1}$

**Output:** Best safe solution $x^* = \arg\max_{x \in \mathcal{S}_{HF}} f_{HF}(x)$

### 3.6 Acquisition Functions

We employ a multi-fidelity Upper Confidence Bound (MF-UCB) acquisition function weighted by safety probability:

$$\alpha(x, m) = \left(\mu_f^{(m)}(x) + \kappa_f \sigma_f^{(m)}(x)\right) \cdot P_{safe}^{(m)}(x) \cdot \frac{1}{c_m}$$

where:
- $\mu_f^{(m)}(x), \sigma_f^{(m)}(x)$ are the GP posterior mean and standard deviation for the objective at fidelity $m$
- $P_{safe}^{(m)}(x) = \Phi\left(\frac{\mu_g^{(m)}(x) - \beta_m \sigma_g^{(m)}(x)}{\sigma_g^{(m)}(x)}\right)$ is the inflated safety probability
- $c_m$ is the evaluation cost at fidelity $m$

### 3.7 Experimental Design

#### 3.7.1 Synthetic Benchmarks

We will evaluate HS-MFBO on synthetic test functions with known ground truth:

1. **Branin-Hoo with Safety Constraint:** 2D optimization with a circular unsafe region
2. **Hartmann-6D with Multi-Fidelity:** 6D optimization with fidelity-dependent noise and bias
3. **Ackley with Nonlinear Fidelity Relationship:** Tests robustness to LMC misspecification

For each benchmark, we construct multi-fidelity versions where:
- Low-fidelity: $g_{LF}(x) = g_{HF}(x) + \epsilon_{bias}(x) + \epsilon_{noise}$
- Fidelity cost ratio: $c_{HF}/c_{LF} \in \{10, 50, 100\}$

#### 3.7.2 Real-World Drug Toxicity Screening

We will use the ChEMBL and ToxCast databases to construct realistic multi-fidelity safety optimization problems:

- **High-fidelity:** Experimental toxicity assay results (IC50, LD50)
- **Low-fidelity:** Computational toxicity predictions (QSAR models, molecular descriptors)
- **Objective:** Optimize drug efficacy subject to toxicity constraints

Dataset preprocessing:
1. Select compounds with both computational and experimental toxicity data
2. Define safety threshold based on clinical relevance
3. Split into training (80%) and held-out validation (20%) sets

#### 3.7.3 Baselines

We compare HS-MFBO against:

1. **SafeOpt:** Single-fidelity safe Bayesian optimization (Sui et al., 2015)
2. **MF-BO (Naive Safety):** Multi-fidelity BO with post-hoc safety filtering
3. **MF-BO (No Safety):** Standard multi-fidelity BO ignoring constraints
4. **Random Safe:** Random sampling within known safe regions

#### 3.7.4 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Cumulative Violations | $\sum_{t=1}^{T} \mathbb{1}[g_{HF}(x_t) < 0]$ | 0 |
| Total Cost | $\sum_{t=1}^{T} c_{m_t}$ | ≥40% reduction vs SafeOpt |
| Simple Regret | $f(x^*) - f(x_{best})$ | Comparable to SafeOpt |
| Cost Efficiency | Regret per unit cost | Maximize |

#### 3.7.5 Statistical Analysis

- **Sample size:** $n = 30$ independent runs per method per benchmark
- **Statistical tests:** Paired t-tests for cost reduction, exact binomial test for violation counts
- **Significance level:** $\alpha = 0.05$ (one-tailed for cost reduction)
- **Effect size reporting:** Cohen's d with 95% confidence intervals

### 3.8 Implementation Details

- **GP Implementation:** GPyTorch with LMC kernel
- **Optimization:** L-BFGS-B for acquisition function maximization
- **Hyperparameter tuning:** Marginal likelihood maximization with restarts
- **Computational resources:** GPU-accelerated GP inference for scalability

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome (P1):** We expect HS-MFBO to achieve **zero cumulative constraint violations** across all experimental conditions while reducing total optimization cost by **≥40%** compared to single-fidelity SafeOpt. This prediction is grounded in:
- SafeOpt's proven ability to maintain safety through conservative confidence bounds
- MF-BO's demonstrated 50-70% cost reduction in unconstrained settings
- Our margin inflation mechanism's theoretical guarantee of cross-fidelity safety transfer

**Secondary Outcomes:**
- **P2 (Adaptive Calibration):** The adaptive calibration procedure will improve cost efficiency by 10-20% compared to fixed margin inflation, by tightening $\beta$ as more cross-fidelity data is observed.
- **P3 (Scaling with Cost Ratio):** Cost savings will scale positively with the fidelity cost ratio, with greater benefits when $c_{HF}/c_{LF} \geq 50$.

**Falsification Criteria:** The hypothesis will be rejected if:
1. Any constraint violation occurs (safety failure)
2. Cost reduction falls below 20% (efficiency failure)
3. Transfer error $\tau$ does not correlate with actual LF→HF discrepancy (mechanism failure)

### 4.2 Theoretical Contributions

1. **Cross-Fidelity Safety Transfer Theorem:** Formal proof that margin inflation by $\beta = 1 + \tau/\sigma_{LF}$ preserves high-fidelity safety guarantees when evaluating at low-fidelity.

2. **Transfer Error Bound:** Derivation of tight bounds on $\tau$ using LMC kernel structure, enabling practical computation.

3. **Regret Analysis:** Extension of SafeOpt's regret bounds to the multi-fidelity setting, characterizing the cost-safety trade-off.

### 4.3 Practical Impact

**Drug Discovery:** HS-MFBO could accelerate early-stage drug screening by enabling safe exploration using computational toxicity models before committing to expensive experimental assays. A 40% cost reduction translates to significant savings in pharmaceutical R&D.

**Materials Design:** In materials science, computational simulations (DFT, molecular dynamics) can guide experimental synthesis while respecting safety constraints on material stability or toxicity.

**Robotics:** Safe robot learning can leverage simulation (low-fidelity) to explore policies before real-world deployment (high-fidelity), reducing the risk of hardware damage.

### 4.4 Broader Impact

This research contributes to the broader goal of making machine learning methods practically relevant for real-world experimental design. By addressing the safety-efficiency trade-off, HS-MFBO enables:

- **Democratization of safe experimentation:** Reduced costs make safe optimization accessible to resource-constrained labs.
- **Accelerated scientific discovery:** Faster iteration cycles in drug and materials discovery.
- **Responsible AI deployment:** Principled safety guarantees for AI-guided experimentation.

### 4.5 Limitations and Future Work

**Limitations:**
- LMC kernel may not capture highly nonlinear fidelity relationships; deep GP extensions could address this.
- Initial safe set requirement limits cold-start scenarios; future work could explore safe initialization strategies.
- Calibration overhead requires some high-fidelity data; trade-off with total budget needs careful management.

**Future Directions:**
- Extension to multiple safety constraints with different fidelity structures
- Integration with batch/parallel evaluation strategies
- Application to reinforcement learning with safety constraints

---
