# Research Proposal: PAC-Bayesian Sample Complexity Bounds for Active Learning via Martingale Analysis

## 1. Title

**PAC-Bayesian Sample Complexity Bounds for Active Learning via Martingale Analysis: Theoretical Foundations and Empirical Validation of Information-Theoretic Query Selection**

## 2. Introduction

### 2.1 Background

Active learning has emerged as a critical paradigm for reducing labeling costs in machine learning applications where obtaining labeled data is expensive or time-consuming. Unlike passive learning, where training examples are sampled uniformly at random, active learning algorithms strategically select the most informative queries to label, potentially achieving comparable performance with significantly fewer labeled examples. This capability is particularly valuable in domains such as medical diagnosis, drug discovery, and autonomous systems, where expert annotation is costly and scarce.

Despite the empirical success of information-theoretic active learning strategies such as Bayesian Active Learning by Disagreement (BALD), the theoretical understanding of their sample efficiency remains limited. Classical active learning theory, exemplified by the disagreement coefficient framework (Hanneke, 2014), provides worst-case guarantees but does not capture the Bayesian nature of modern probabilistic query selection strategies. Meanwhile, PAC-Bayesian theory has proven highly effective for analyzing probabilistic learning algorithms and has recently been extended to sequential settings through martingale analysis (Rivasplata et al., 2020). However, existing PAC-Bayesian frameworks assume passive data collection and do not account for the adaptive, learner-controlled query selection that characterizes active learning.

This gap between theory and practice is problematic for several reasons. First, practitioners lack principled methods to predict label complexity and estimate annotation budgets for cost-sensitive applications. Second, without theoretical justification, it remains unclear whether the computational overhead of sophisticated query strategies is warranted. Third, the absence of rigorous bounds prevents the development of new algorithms with provable guarantees. Bridging PAC-Bayesian theory with active learning's adaptive query selection addresses these critical needs and aligns perfectly with the workshop's goal of advancing PAC-Bayesian theory in interactive learning settings.

### 2.2 Research Objectives

This research aims to establish the first PAC-Bayesian theoretical framework for active learning that explicitly accounts for adaptive query selection and provides rigorous sample complexity guarantees. Our specific objectives are:

**Objective 1 (Theoretical Foundation):** Extend martingale PAC-Bayesian theory to active learning by deriving generalization bounds that incorporate a query-dependent mutual information term, formally accounting for the impact of adaptive query selection on sample complexity.

**Objective 2 (Optimality Analysis):** Prove that information gain maximization strategies (e.g., BALD) provably minimize the query-dependent term in our bounds, establishing their theoretical optimality within the PAC-Bayesian framework.

**Objective 3 (Sample Complexity Characterization):** Derive explicit label complexity bounds of the form $O(d \log(1/\delta)/\varepsilon^2)$ with query-strategy-dependent constants, demonstrating that information-theoretic strategies achieve tighter constants than random sampling.

**Objective 4 (Empirical Validation):** Validate our theoretical predictions through comprehensive experiments on benchmark datasets, demonstrating that our bounds correctly predict label complexity ordering across query strategies and achieve measurable reductions in the query-dependent term.

### 2.3 Significance

This research makes several significant contributions to both theory and practice:

**Theoretical Significance:** We provide the first PAC-Bayesian analysis that rigorously accounts for adaptive query selection in active learning, filling a critical gap at the intersection of PAC-Bayesian theory and interactive learning. Our framework extends the applicability of PAC-Bayesian theory to learner-controlled sampling scenarios, opening new avenues for analyzing exploration-exploitation trade-offs in interactive settings.

**Methodological Significance:** By proving the optimality of information gain maximization within our framework, we provide the first rigorous theoretical justification for widely-used heuristics like BALD. This bridges the gap between empirically successful methods and theoretical understanding, enabling principled algorithm design.

**Practical Significance:** Our bounds enable practitioners to estimate label complexity with theoretical guarantees, facilitating budget planning for cost-sensitive applications. The explicit characterization of query-strategy-dependent constants provides actionable guidance for selecting appropriate active learning strategies based on problem characteristics.

**Broader Impact:** This work contributes to the workshop's mission by demonstrating how PAC-Bayesian theory can explain the success of existing interactive learning algorithms and guide the development of new algorithms with provable guarantees. The martingale analysis techniques we develop may generalize to other interactive learning settings involving adaptive data collection, such as bandits and reinforcement learning.

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Problem Formulation

We consider pool-based active learning for binary classification. Let $\mathcal{X}$ denote the input space and $\mathcal{Y} = \{0, 1\}$ the label space. We assume access to an unlabeled pool $\mathcal{U} = \{x_1, \ldots, x_m\}$ drawn i.i.d. from an unknown distribution $\mathcal{D}$ over $\mathcal{X}$, and an oracle that provides labels $y = f^*(x)$ for queried examples, where $f^*: \mathcal{X} \to \mathcal{Y}$ is the true labeling function.

The active learning algorithm proceeds in rounds $t = 1, \ldots, n$:
1. Maintain a posterior distribution $Q_t$ over hypotheses $h \in \mathcal{H}$
2. Select query $x_t \in \mathcal{U}$ based on $Q_t$ and history $\mathcal{H}_{t-1} = \{(x_1, y_1), \ldots, (x_{t-1}, y_{t-1})\}$
3. Receive label $y_t = f^*(x_t)$ from oracle
4. Update posterior: $Q_{t+1} \propto Q_t \cdot \mathbb{1}[h(x_t) = y_t]$ (realizability) or via Bayesian update (agnostic)

Our goal is to derive generalization bounds on the true risk $R(h) = \mathbb{E}_{x \sim \mathcal{D}}[\mathbb{1}[h(x) \neq f^*(x)]]$ in terms of the empirical risk $\hat{R}(h) = \frac{1}{n}\sum_{i=1}^n \mathbb{1}[h(x_i) \neq y_i]$ and query selection strategy.

#### 3.1.2 Martingale PAC-Bayes Extension

We extend the martingale PAC-Bayesian framework (Rivasplata et al., 2020) to active learning. The key challenge is that query selection introduces dependence between the data distribution and the learner's hypothesis, violating standard i.i.d. assumptions.

**Theorem 1 (Active Learning PAC-Bayes Bound):** Let $P$ be a prior distribution over $\mathcal{H}$ independent of the data. For any $\delta \in (0, 1)$, with probability at least $1 - \delta$ over the random oracle responses, for all posterior distributions $Q$ and all $h \in \mathcal{H}$:

$$R(h) \leq \hat{R}(h) + \sqrt{\frac{\text{KL}(Q \| P) + I_{\text{query}}(Q) + \log(2\sqrt{n}/\delta)}{2n}}$$

where the query-dependent information term is:

$$I_{\text{query}}(Q) = \sum_{i=1}^n I(Q_i; Y_i \mid \mathcal{H}_{i-1})$$

and $I(Q_i; Y_i \mid \mathcal{H}_{i-1})$ denotes the mutual information between the posterior at round $i$ and the label $Y_i$ conditioned on the history.

**Proof Sketch:** We construct a martingale sequence based on the loss process and apply Ville's inequality. The key innovation is properly accounting for the adaptive query selection through conditional mutual information terms. The filtration $\mathcal{F}_t = \sigma(\mathcal{H}_t, \mathcal{U})$ includes both the labeled history and the unlabeled pool, ensuring measurability of the query selection strategy.

#### 3.1.3 Information Gain Optimality

**Theorem 2 (Information Gain Minimizes Query Term):** Under realizability (i.e., $f^* \in \mathcal{H}$ and $Q_t$ supported on consistent hypotheses), the query strategy that minimizes the expected query-dependent term is:

$$x_t^* = \arg\max_{x \in \mathcal{U}} I(Q_t; Y \mid X = x) = \arg\max_{x \in \mathcal{U}} H[Y \mid X = x, Q_t]$$

where $H[Y \mid X = x, Q_t] = -\sum_{y \in \{0,1\}} p(y \mid x, Q_t) \log p(y \mid x, Q_t)$ is the predictive entropy, and $p(y \mid x, Q_t) = \mathbb{E}_{h \sim Q_t}[\mathbb{1}[h(x) = y]]$.

**Proof Sketch:** We show that under realizability, the conditional mutual information $I(Q_i; Y_i \mid \mathcal{H}_{i-1})$ equals the expected reduction in posterior entropy. Information gain maximization greedily minimizes this term at each round, leading to faster posterior concentration and tighter bounds.

#### 3.1.4 Label Complexity Analysis

**Corollary 1 (Label Complexity Bound):** Under realizability with VC dimension $d$, to achieve $R(h) \leq \varepsilon$ with probability $1 - \delta$, information gain query selection requires:

$$n_{\text{IG}} = O\left(\frac{d \log(1/\delta)}{\varepsilon^2}\right)$$

labels, with constant factor $C_{\text{IG}} \leq 0.7 \cdot C_{\text{rand}}$ compared to random sampling.

This follows from bounding $I_{\text{query}}(Q)$ using the posterior entropy reduction and applying standard VC dimension arguments for the KL term.

### 3.2 Algorithmic Implementation

#### 3.2.1 Posterior Approximation

For practical implementation with neural networks, we approximate the posterior $Q_t$ using:

1. **MC Dropout:** Interpret dropout as variational Bayesian approximation (Gal & Ghahramani, 2016)
2. **Deep Ensembles:** Maintain ensemble of $K$ independently trained networks
3. **Variational Inference:** Optimize variational distribution $Q_\phi$ to minimize $\text{KL}(Q_\phi \| P_{\text{posterior}})$

The information gain for query $x$ is approximated as:

$$\hat{I}(x) = H\left[\frac{1}{K}\sum_{k=1}^K p_k(y \mid x)\right] - \frac{1}{K}\sum_{k=1}^K H[p_k(y \mid x)]$$

where $p_k(y \mid x)$ is the predictive distribution from the $k$-th posterior sample.

#### 3.2.2 Bound Computation

We compute the PAC-Bayesian bound empirically:

1. **KL Term:** For Gaussian variational posteriors, $\text{KL}(Q \| P) = \sum_i \frac{(\mu_i - \mu_{0,i})^2 + \sigma_i^2 - \sigma_{0,i}^2 - 2\log(\sigma_i/\sigma_{0,i})}{2\sigma_{0,i}^2}$

2. **Query Term:** Track cumulative information gain: $\hat{I}_{\text{query}} = \sum_{i=1}^n \hat{I}(x_i)$

3. **Empirical Risk:** $\hat{R}(h) = \frac{1}{n}\sum_{i=1}^n \mathbb{1}[h(x_i) \neq y_i]$ on labeled queries

4. **Bound:** $\text{Bound}(n) = \hat{R}(h) + \sqrt{\frac{\text{KL}(Q \| P) + \hat{I}_{\text{query}} + \log(2\sqrt{n}/\delta)}{2n}}$

### 3.3 Experimental Design

#### 3.3.1 Datasets and Tasks

**Realizable Setting:**
- **MNIST 3vs8:** Binary classification with RBF SVM (realizable by construction)
- **UCI Benchmarks:** Ionosphere, Sonar, Breast Cancer (linear separable subsets)

**Agnostic Setting:**
- **MNIST Full:** 10-class classification (non-realizable)
- **CIFAR-10 Binary:** Airplane vs. Automobile with ResNet-18

**Pool Sizes:** $m \in \{1000, 5000, 10000\}$, Budget: $n \in \{50, 100, 200, 500\}$

#### 3.3.2 Query Strategies (Baselines)

1. **Random:** Uniform sampling from pool
2. **Uncertainty:** $x_t = \arg\max_{x} H[p(y \mid x, Q_t)]$ (predictive entropy)
3. **BALD (Information Gain):** $x_t = \arg\max_{x} I(Q_t; Y \mid X = x)$
4. **Query-by-Committee:** Disagreement among ensemble members
5. **Core-Set:** Diversity-based selection (geometric coverage)

#### 3.3.3 Evaluation Metrics

**Primary Metrics:**

1. **Label Complexity:** Number of queries $n_\varepsilon$ to achieve test error $\leq \varepsilon$
   - Measure: $n_\varepsilon = \min\{n : R_{\text{test}}(h_n) \leq \varepsilon\}$
   - Target: $n_{\text{IG}} \leq 0.8 \cdot n_{\text{rand}}$ (20% reduction)

2. **Query-Dependent Term:** Cumulative information gain $I_{\text{query}}$
   - Measure: $I_{\text{query}}(n) = \sum_{i=1}^n I(Q_i; Y_i \mid \mathcal{H}_{i-1})$
   - Prediction: $I_{\text{IG}} \leq 0.7 \cdot I_{\text{rand}}$ (30% reduction)

3. **Bound Tightness:** Gap between bound and actual error
   - Measure: $\Delta(n) = \text{Bound}(n) - R_{\text{test}}(h_n)$
   - Target: $\Delta_{\text{IG}} \leq \Delta_{\text{rand}}$

**Secondary Metrics:**

4. **Bound Validity:** Empirical coverage probability
   - Measure: Fraction of runs where $R_{\text{test}} \leq \text{Bound}$
   - Target: $\geq 1 - \delta$ (e.g., 95% for $\delta = 0.05$)

5. **Label Complexity Ordering:** Rank correlation with predicted ordering
   - Measure: Spearman's $\rho$ between predicted and observed $n_\varepsilon$
   - Target: $\rho \geq 0.8$

#### 3.3.4 Statistical Validation

**Sample Size:** $N = 25$ independent runs per configuration (different random seeds)

**Hypothesis Testing:**
- **H1:** $I_{\text{IG}} < I_{\text{rand}}$ (paired t-test, $\alpha = 0.05$)
- **H2:** $n_{\text{IG}} < n_{\text{rand}}$ (paired t-test, $\alpha = 0.05$)
- **Power Analysis:** $N = 25$ provides 90% power to detect 30% effect size

**Confounding Control:**
1. **Computational Budget:** Normalize by wall-clock time, not just query count
2. **Initialization:** Fixed random seeds for reproducibility
3. **Hyperparameters:** Grid search with validation set (separate from test)
4. **Pool Composition:** Stratified sampling to ensure class balance

**Sensitivity Analysis:**
1. **Prior Specification:** Test Gaussian priors with $\sigma_0 \in \{0.1, 1.0, 10.0\}$
2. **Posterior Approximation:** Compare MC Dropout ($K \in \{10, 50, 100\}$) vs. Deep Ensembles
3. **Realizability Violation:** Inject label noise $\eta \in \{0, 0.05, 0.1, 0.2\}$
4. **VC Dimension:** Vary network capacity (width $\in \{64, 128, 256\}$)

#### 3.3.5 Reproducibility Protocol

1. **Code Release:** Public GitHub repository with MIT license
2. **Environment:** Docker container with fixed dependencies (PyTorch 2.0, Python 3.10)
3. **Data:** Public datasets with fixed train/test splits
4. **Seeds:** Document all random seeds for data splits, initialization, dropout
5. **Compute:** Single NVIDIA RTX 3090 GPU (24GB), estimated 200 GPU-hours total
6. **Documentation:** Detailed README with step-by-step reproduction instructions

### 3.4 Theoretical Validation

#### 3.4.1 Formal Proofs

We will provide complete formal proofs for:

1. **Theorem 1 (Bound Validity):** Martingale construction, Ville's inequality application, union bound over queries
2. **Theorem 2 (Information Gain Optimality):** Entropy reduction analysis, greedy optimality under realizability
3. **Corollary 1 (Label Complexity):** VC dimension bounds, constant factor analysis

**Proof Verification:** Formalize key results in Lean 4 theorem prover (stretch goal)

#### 3.4.2 Assumption Validation

**Realizability Testing:**
- Construct synthetic datasets where $f^* \in \mathcal{H}$ by design
- Measure posterior consistency: $\mathbb{P}(f^* \in \text{supp}(Q_t)) \to 1$

**Martingale Property:**
- Verify $\mathbb{E}[M_{t+1} \mid \mathcal{F}_t] = M_t$ empirically via Monte Carlo
- Check filtration measurability of query selection

**Variational Approximation Error:**
- Compare $\text{KL}(Q_{\text{approx}} \| Q_{\text{true}})$ on small problems with exact inference
- Quantify bound degradation: $\Delta_{\text{approx}} = \text{Bound}_{\text{approx}} - \text{Bound}_{\text{true}}$

## 4. Expected Outcomes & Impact

### 4.1 Expected Theoretical Outcomes

**Primary Theoretical Contributions:**

1. **Novel PAC-Bayesian Framework:** We expect to establish the first PAC-Bayesian generalization bounds that explicitly account for adaptive query selection in active learning, extending martingale analysis to learner-controlled sampling scenarios.

2. **Optimality Characterization:** Our proofs will rigorously demonstrate that information gain maximization provably minimizes the query-dependent term in our bounds, providing the first theoretical justification for BALD and related methods within a PAC-Bayesian framework.

3. **Sample Complexity Guarantees:** We anticipate deriving explicit label complexity bounds with query-strategy-dependent constants, demonstrating that information-theoretic strategies achieve $O(d \log(1/\delta)/\varepsilon^2)$ complexity with constants at least 30% smaller than random sampling.

4. **Agnostic Extension:** We expect to characterize graceful degradation under realizability violations, showing that label noise $\eta$ increases complexity by an additive $O(\eta/\varepsilon^2)$ term.

### 4.2 Expected Empirical Outcomes

**Quantitative Predictions:**

1. **Query Term Reduction:** Information gain will achieve $I_{\text{IG}} \leq 0.7 \cdot I_{\text{rand}}$ (30% reduction, $p < 0.01$)

2. **Label Complexity Improvement:** BALD will require $n_{\text{IG}} \leq 0.8 \cdot n_{\text{rand}}$ queries to reach target accuracy (20% reduction, $p < 0.05$)

3. **Bound Validity:** Empirical coverage will match theoretical guarantee: $\geq 95\%$ for $\delta = 0.05$

4. **Ordering Prediction:** Bound-predicted label complexity ranking will correlate with empirical ranking at $\rho \geq 0.8$ (Spearman correlation)

**Qualitative Insights:**

- Bound tightness will improve with query budget (posterior concentration)
- Realizability violations will be detectable via bound degradation
- Computational overhead of information gain will be justified by label savings in high-cost annotation scenarios

### 4.3 Broader Impact

**Theoretical Impact:**

This research will bridge two important communities—PAC-Bayesian theory and active learning—fostering new collaborations and research directions. The martingale analysis techniques we develop may generalize to other interactive learning settings (bandits, reinforcement learning), contributing to the workshop's goal of advancing PAC-Bayesian theory in interactive learning.

**Methodological Impact:**

By providing rigorous theoretical foundations for information-theoretic active learning, we enable principled algorithm design with provable guarantees. Practitioners will gain tools to:
- Estimate annotation budgets with confidence intervals
- Select query strategies based on problem characteristics (realizability, noise level)
- Trade off computational cost against label savings with theoretical guidance

**Practical Impact:**

In cost-sensitive domains (medical imaging, drug discovery, autonomous systems), our bounds enable:
- **Budget Planning:** Predict required labels to achieve target accuracy
- **Strategy Selection:** Choose between random, uncertainty, and information gain based on cost-benefit analysis
- **Quality Control:** Detect distribution shift or annotation errors via bound violations

**Societal Impact:**

Reducing labeling costs democratizes machine learning by making high-quality models accessible to organizations with limited annotation budgets. In healthcare, this could accelerate development of diagnostic tools for rare diseases where expert annotations are scarce.

### 4.4 Limitations and Future Work

**Known Limitations:**

1. **Computational Complexity:** Information gain requires $O(|\mathcal{U}| \cdot K)$ posterior evaluations per query, limiting scalability to large pools
2. **Variational Approximation:** Gap between approximate and exact posteriors introduces bound looseness
3. **Realizability Assumption:** Tightest bounds require $f^* \in \mathcal{H}$, which may not hold in practice

**Future Research Directions:**

1. **Computational Efficiency:** Develop sublinear-time approximations for information gain (e.g., via coresets, random projections)
2. **Beyond Classification:** Extend framework to regression, structured prediction, and multi-task learning
3. **Distribution Shift:** Incorporate PAC-Bayes under covariate shift to handle pool-test distribution mismatch
4. **Adversarial Robustness:** Combine with PAC-Bayes under adversarial corruptions for robust active learning
5. **Deep Learning Theory:** Tighten bounds using neural network-specific capacity measures (e.g., compression-based bounds)

### 4.5 Success Criteria

This research will be considered successful if:

1. **Theoretical:** Formal proofs of Theorems 1-2 and Corollary 1 are complete and verified
2. **Empirical:** At least 2 of 3 primary predictions (query term reduction, label complexity improvement, bound validity) are confirmed at $p < 0.05$
3. **Practical:** Bounds enable label complexity estimation within 50% error on benchmark datasets
4. **Dissemination:** Results published at top-tier venue (ICML, NeurIPS, COLT) and code released publicly

**Falsification Criteria:**

The hypothesis will be rejected if:
- Information gain does NOT reduce query-dependent term: $I_{\text{IG}} \geq I_{\text{rand}}$
- Label complexity is NOT improved: $n_{\text{IG}} \geq n_{\text{rand}}$
- Bounds systematically violate coverage: empirical coverage $< 1 - \delta - 0.1$

This research represents a significant step toward unifying PAC-Bayesian theory with active learning, providing both theoretical insights and practical tools for sample-efficient interactive learning with provable guarantees.