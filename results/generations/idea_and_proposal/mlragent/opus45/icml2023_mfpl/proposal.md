# Research Proposal: Preference-Guided Pareto Navigation (PGPN): Learning Implicit Human Trade-offs for Multi-Objective Optimization

## 1. Introduction

### Background

Multi-objective optimization (MOO) addresses problems where multiple conflicting objectives must be simultaneously optimized, yielding a set of Pareto-optimal solutions representing different trade-offs. Traditional MOO methods either present users with overwhelming Pareto fronts containing hundreds of solutions or require explicit specification of weight vectors and utility functions—tasks that impose significant cognitive burden on decision-makers. Research in behavioral economics and cognitive psychology consistently demonstrates that humans struggle to articulate precise numerical trade-offs but excel at making relative judgments such as "I prefer Solution A over Solution B."

Preference-based learning has emerged as a powerful paradigm for capturing human intentions across diverse domains, from fine-tuning large language models to robotics and recommendation systems. The fundamental insight—that relative feedback is more reliable and less biased than absolute ratings—offers a promising avenue for bridging the gap between mathematical optimization frameworks and human decision-making capabilities. Recent advances in dueling bandits, preference learning, and evolutionary multi-objective algorithms have laid groundwork for preference-guided optimization, yet significant challenges remain in efficiently eliciting preferences, learning non-linear trade-off structures, and providing convergence guarantees.

### Research Objectives

This research proposes **Preference-Guided Pareto Navigation (PGPN)**, a novel framework that learns implicit human trade-off functions through strategic pairwise comparisons during the optimization process. Our specific objectives are:

1. **Develop an active learning strategy** that minimizes user queries while maximizing information gain about underlying preference structures, targeting 50-70% reduction in query complexity compared to uniform sampling approaches.

2. **Design a neural network-based preference model** capable of capturing non-linear, context-dependent trade-offs that vary across different regions of the Pareto front.

3. **Create an integrated evolutionary optimization algorithm** that leverages learned preferences to guide population search toward user-preferred Pareto regions.

4. **Establish theoretical convergence guarantees** ensuring the algorithm converges to user-optimal solutions under reasonable assumptions about preference consistency.

5. **Validate the framework** on synthetic benchmarks and real-world applications in healthcare treatment planning and engineering design.

### Significance

This research addresses a critical barrier to MOO deployment in real-world applications. By replacing explicit trade-off specification with intuitive pairwise comparisons, PGPN democratizes access to sophisticated multi-objective optimization tools. The framework has transformative potential in healthcare (personalized treatment planning balancing efficacy, side effects, and cost), sustainable engineering (optimizing performance, environmental impact, and manufacturing cost), and financial services (portfolio optimization reflecting individual risk-return preferences).

## 2. Methodology

### 2.1 Problem Formulation

Consider a multi-objective optimization problem with $m$ objectives:
$$\min_{\mathbf{x} \in \mathcal{X}} \mathbf{f}(\mathbf{x}) = (f_1(\mathbf{x}), f_2(\mathbf{x}), \ldots, f_m(\mathbf{x}))$$

where $\mathcal{X} \subseteq \mathbb{R}^n$ is the decision space. We assume there exists an implicit utility function $u^*: \mathbb{R}^m \rightarrow \mathbb{R}$ representing the user's true preferences, such that for any two solutions $\mathbf{x}_a, \mathbf{x}_b$:
$$P(\mathbf{x}_a \succ \mathbf{x}_b) = \sigma(u^*(\mathbf{f}(\mathbf{x}_a)) - u^*(\mathbf{f}(\mathbf{x}_b)))$$

where $\sigma(\cdot)$ is the sigmoid function and $\succ$ denotes preference. Our goal is to find $\mathbf{x}^* = \arg\max_{\mathbf{x} \in \mathcal{P}} u^*(\mathbf{f}(\mathbf{x}))$, where $\mathcal{P}$ denotes the Pareto-optimal set.

### 2.2 Framework Architecture

PGPN consists of three integrated components: (1) Pareto Front Approximation Module, (2) Active Preference Elicitation Module, and (3) Preference-Guided Search Module.

#### 2.2.1 Pareto Front Approximation Module

We employ NSGA-III as the base evolutionary algorithm to maintain a diverse population $\mathcal{P}_t = \{\mathbf{x}_1, \mathbf{x}_2, \ldots, \mathbf{x}_N\}$ approximating the Pareto front at generation $t$. The population undergoes standard evolutionary operations:

**Selection**: Tournament selection based on non-dominated ranking and crowding distance.

**Crossover**: Simulated binary crossover (SBX) with probability $p_c = 0.9$:
$$\mathbf{x}_{child} = \frac{1}{2}[(1 + \beta_q)\mathbf{x}_{p1} + (1 - \beta_q)\mathbf{x}_{p2}]$$

where $\beta_q$ is derived from a polynomial distribution with index $\eta_c = 20$.

**Mutation**: Polynomial mutation with probability $p_m = 1/n$ and distribution index $\eta_m = 20$.

#### 2.2.2 Active Preference Elicitation Module

The core innovation lies in our information-theoretic query selection strategy. We train a preference model $\hat{u}_\theta: \mathbb{R}^m \rightarrow \mathbb{R}$ parameterized by neural network weights $\theta$. To select maximally informative query pairs, we employ an acquisition function based on expected information gain.

**Preference Model Architecture**: We use a multi-layer perceptron with architecture $[m \rightarrow 64 \rightarrow 128 \rightarrow 64 \rightarrow 1]$, ReLU activations, and dropout regularization ($p = 0.1$). The model is trained using the Bradley-Terry loss:
$$\mathcal{L}(\theta) = -\sum_{(\mathbf{x}_a, \mathbf{x}_b, y) \in \mathcal{D}} \left[ y \log \hat{P}_{ab} + (1-y) \log(1 - \hat{P}_{ab}) \right]$$

where $\hat{P}_{ab} = \sigma(\hat{u}_\theta(\mathbf{f}(\mathbf{x}_a)) - \hat{u}_\theta(\mathbf{f}(\mathbf{x}_b)))$, $y = 1$ if $\mathbf{x}_a \succ \mathbf{x}_b$, and $\mathcal{D}$ is the collected preference dataset.

**Query Selection Strategy**: For candidate pair $(\mathbf{x}_i, \mathbf{x}_j)$, we compute the acquisition score:
$$\alpha(\mathbf{x}_i, \mathbf{x}_j) = H(\hat{P}_{ij}) \cdot d(\mathbf{f}(\mathbf{x}_i), \mathbf{f}(\mathbf{x}_j)) \cdot \text{Var}_\theta[\hat{u}(\mathbf{f}(\mathbf{x}_i)) - \hat{u}(\mathbf{f}(\mathbf{x}_j))]$$

where $H(\hat{P}_{ij}) = -\hat{P}_{ij}\log\hat{P}_{ij} - (1-\hat{P}_{ij})\log(1-\hat{P}_{ij})$ is the binary entropy capturing prediction uncertainty, $d(\cdot, \cdot)$ is the Euclidean distance in objective space ensuring diversity, and the variance term is estimated via Monte Carlo dropout.

The query pair is selected as:
$$(\mathbf{x}_i^*, \mathbf{x}_j^*) = \arg\max_{(\mathbf{x}_i, \mathbf{x}_j) \in \mathcal{P}_t \times \mathcal{P}_t, i \neq j} \alpha(\mathbf{x}_i, \mathbf{x}_j)$$

#### 2.2.3 Preference-Guided Search Module

We modify the evolutionary search to concentrate computational resources on user-preferred regions through a preference-informed fitness assignment:
$$F(\mathbf{x}) = \lambda \cdot \text{rank}_{ND}(\mathbf{x}) + (1 - \lambda) \cdot \hat{u}_\theta(\mathbf{f}(\mathbf{x}))$$

where $\text{rank}_{ND}(\mathbf{x})$ is the normalized non-dominated rank and $\lambda \in [0, 1]$ balances exploration (Pareto dominance) and exploitation (preference alignment). We implement an adaptive schedule:
$$\lambda(t) = \max(0.2, 1 - t/T_{max})$$

ensuring early-stage diversity and late-stage preference focus.

### 2.3 Complete Algorithm

**Algorithm: PGPN**
```
Input: Population size N, max generations T_max, query budget Q
Output: User-preferred Pareto-optimal solution x*

1. Initialize population P_0 randomly; D ← ∅
2. For t = 1 to T_max:
3.    Evaluate objectives f(x) for all x ∈ P_t
4.    Perform non-dominated sorting
5.    If |D| < Q and t mod k = 0:  // Query every k generations
6.       Select (x_i*, x_j*) = argmax α(x_i, x_j)
7.       Query user preference y for (x_i*, x_j*)
8.       D ← D ∪ {(x_i*, x_j*, y)}
9.       Update θ by minimizing L(θ) on D
10.   Compute F(x) for all x ∈ P_t using updated u_θ
11.   Select parents via tournament selection on F(x)
12.   Generate offspring via crossover and mutation
13.   P_{t+1} ← environmental selection from P_t ∪ offspring
14. Return x* = argmax_{x ∈ P_T} u_θ(f(x))
```

### 2.4 Theoretical Analysis

**Theorem 1 (Convergence)**: Under Assumptions (A1) preference transitivity with bounded noise, (A2) Lipschitz continuity of $u^*$, and (A3) sufficient query budget $Q = \Omega(m \log(1/\epsilon))$, PGPN converges to an $\epsilon$-optimal solution with probability at least $1 - \delta$.

The proof follows by establishing: (1) concentration bounds on the preference model error, (2) regret bounds on the active learning strategy, and (3) evolutionary algorithm convergence under approximate fitness functions.

### 2.5 Experimental Design

**Synthetic Benchmarks**: DTLZ1-7 and WFG1-9 test suites with $m \in \{2, 3, 5\}$ objectives, using synthetically generated utility functions (linear, quadratic, and piece-wise linear).

**Real-World Applications**:
- *Healthcare*: Treatment planning for cancer radiotherapy balancing tumor control, organ-at-risk sparing, and treatment time (using TROTS dataset).
- *Engineering Design*: Automobile crash-worthiness optimization (weight, acceleration characteristics, toe-board intrusion).

**Baselines**: (1) NSGA-III with post-hoc selection, (2) R-NSGA-II with reference point, (3) IBEA with hypervolume indicator, (4) MOEA/D-PBI, (5) FERERO, and (6) Dueling Bandit MOEA.

**Evaluation Metrics**:
- *Query Efficiency*: Number of comparisons to reach target solution quality
- *Solution Quality*: Distance to true optimal in utility space: $|u^*(\mathbf{f}(\mathbf{x}^*)) - u^*_{max}|$
- *Regret*: Cumulative regret over optimization iterations
- *User Study Metrics*: Satisfaction scores, cognitive load (NASA-TLX), and task completion time

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Algorithmic Contributions**: A novel framework integrating active preference learning with evolutionary multi-objective optimization, demonstrating 50-70% reduction in query complexity while achieving comparable or superior solution quality.

2. **Theoretical Contributions**: Formal convergence guarantees establishing conditions under which preference-guided search converges to user-optimal Pareto regions, including sample complexity bounds.

3. **Empirical Validation**: Comprehensive experimental evidence across synthetic benchmarks (15+ test problems) and two real-world domains, demonstrating practical applicability.

4. **Software Artifact**: Open-source Python implementation integrated with popular optimization libraries (pymoo, DEAP), facilitating adoption by practitioners.

### Broader Impact

PGPN addresses a fundamental barrier preventing wider adoption of multi-objective optimization in practice. By replacing cognitively demanding weight specification with intuitive comparisons, the framework enables:

- **Healthcare**: Clinicians can optimize treatment plans by comparing alternatives rather than specifying numerical trade-offs between efficacy and toxicity, potentially improving patient outcomes while reducing decision fatigue.

- **Sustainable Engineering**: Designers can navigate complex trade-offs between performance, environmental impact, and cost through natural preference expression, accelerating development of eco-friendly products.

- **Democratized Optimization**: Non-experts can leverage sophisticated MOO tools without mathematical expertise, broadening access to decision-support technology.

The research directly contributes to preference-based learning theory while demonstrating practical impact, aligning with the workshop's goal of connecting theory to practice and fostering cross-disciplinary collaboration between optimization, machine learning, and human-computer interaction communities.