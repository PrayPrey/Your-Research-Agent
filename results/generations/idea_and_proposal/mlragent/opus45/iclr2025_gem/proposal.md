# Research Proposal: Uncertainty-Guided Adaptive Experimental Design for Protein Engineering

## 1. Introduction

### Background

Protein engineering represents one of the most transformative applications of modern biotechnology, enabling the design of enzymes with enhanced catalytic activity, therapeutic proteins with improved efficacy, and biosensors with novel detection capabilities. Machine learning, particularly generative models, has emerged as a powerful tool for exploring the vast protein sequence space, which is estimated at $20^{100}$ possible sequences for a 100-residue protein. Recent advances in structure-conditioned sequence generators, variational autoencoders, and diffusion models have demonstrated remarkable capabilities in proposing novel protein sequences with desired structural and functional properties.

However, a critical disconnect persists between computational predictions and experimental validation. While generative models can propose thousands of candidate sequences, wet lab validation remains expensive, time-consuming, and resource-limited. A single round of protein synthesis, expression, and functional assay can cost hundreds to thousands of dollars per variant and take weeks to complete. This asymmetry creates a fundamental bottleneck: computational methods generate far more candidates than can feasibly be tested, yet there exists no principled framework for selecting which designs warrant experimental investment.

Current practice often relies on ad hoc selection criteria—choosing top-ranked predictions by fitness score, enforcing diversity through clustering, or applying arbitrary confidence thresholds. These approaches fail to leverage the rich uncertainty information embedded in modern generative models and ignore the sequential nature of experimental campaigns where early results should inform subsequent design choices.

### Research Objectives

This research proposes an **Uncertainty-Guided Adaptive Experimental Design (UGAED)** framework that explicitly integrates epistemic uncertainty quantification from generative protein models into a Bayesian optimization loop for wet lab validation. Our specific objectives are:

1. **Develop calibrated uncertainty quantification methods** for structure-conditioned protein sequence generators using ensemble-based approaches that capture both aleatoric and epistemic uncertainty.

2. **Design novel acquisition functions** that balance exploitation of high-fitness predictions with exploration of uncertain regions while accounting for sequence diversity and experimental batch constraints.

3. **Implement and validate a closed-loop adaptive experimental system** that iteratively updates generative models based on wet lab feedback, demonstrating improved sample efficiency compared to baseline selection strategies.

4. **Establish practical guidelines** for deploying uncertainty-guided design in real protein engineering campaigns with varying experimental budgets and throughput constraints.

### Significance

This work directly addresses the workshop's core theme of bridging generative ML and experimental biology. By providing experimentalists with principled, resource-aware recommendations for which designs to validate, we transform generative models from passive candidate generators into active partners in the design-build-test-learn cycle. The expected 2-3x improvement in identifying functional variants within fixed experimental budgets could translate to significant cost savings and accelerated development timelines across enzyme engineering, antibody optimization, and de novo protein design applications.

## 2. Methodology

### 2.1 Overview

Our framework consists of four interconnected modules: (1) an uncertainty-aware generative model ensemble, (2) a multi-objective acquisition function, (3) a batch selection algorithm with experimental constraints, and (4) an iterative model updating procedure. Figure 1 illustrates the overall workflow.

### 2.2 Uncertainty-Aware Generative Model Ensemble

#### Base Architecture

We employ structure-conditioned sequence generators based on the ProteinMPNN architecture, which models the conditional probability $p(S|X)$ where $S$ represents the amino acid sequence and $X$ represents the backbone structure. The model parameterizes this distribution autoregressively:

$$p(S|X) = \prod_{i=1}^{L} p(s_i | s_{<i}, X)$$

where $L$ is the sequence length and $s_i \in \{1, ..., 20\}$ denotes the amino acid at position $i$.

#### Ensemble Construction

To capture epistemic uncertainty, we train an ensemble of $M$ models $\{f_{\theta_1}, ..., f_{\theta_M}\}$ with different random initializations and training data subsamples. For each position $i$ and sequence context, the ensemble provides $M$ probability distributions over amino acids. We characterize uncertainty through:

**Predictive mean:**
$$\bar{p}(s_i | s_{<i}, X) = \frac{1}{M} \sum_{m=1}^{M} p_{\theta_m}(s_i | s_{<i}, X)$$

**Epistemic uncertainty (model disagreement):**
$$u_{epi}(i) = \frac{1}{M} \sum_{m=1}^{M} D_{KL}(p_{\theta_m} || \bar{p})$$

**Aleatoric uncertainty (inherent ambiguity):**
$$u_{ale}(i) = H[\bar{p}(s_i | s_{<i}, X)]$$

where $H[\cdot]$ denotes Shannon entropy. The total sequence-level uncertainty is computed as:

$$U(S) = \sum_{i=1}^{L} \left( \alpha \cdot u_{epi}(i) + (1-\alpha) \cdot u_{ale}(i) \right)$$

with $\alpha$ being a hyperparameter balancing uncertainty sources.

#### Uncertainty Calibration

Following recent work on conformal prediction for design problems, we calibrate uncertainty estimates using a held-out validation set. We compute the empirical coverage:

$$\text{Coverage}(\delta) = \frac{1}{N_{val}} \sum_{j=1}^{N_{val}} \mathbb{1}[y_j \in C_\delta(x_j)]$$

where $C_\delta(x_j)$ is the $\delta$-confidence prediction set. We adjust ensemble predictions to achieve nominal coverage using temperature scaling on the predictive distributions.

### 2.3 Fitness Prediction Module

Alongside sequence generation, we train a fitness predictor $g_\phi: S \rightarrow \mathbb{R}$ that estimates functional activity. We employ a Gaussian Process (GP) with a deep kernel:

$$g_\phi(S) \sim \mathcal{GP}(\mu_\phi(S), k_\phi(S, S'))$$

where the mean and kernel functions are parameterized by neural networks operating on protein language model embeddings (ESM-2). This provides both point predictions $\hat{y}(S) = \mu_\phi(S)$ and predictive variance $\sigma^2_\phi(S)$.

For settings with limited data, we incorporate meta-learning to calibrate the GP across related protein families, following recent advances in meta-learning for uncertainty estimation.

### 2.4 Multi-Objective Acquisition Function

We design an acquisition function $a(S)$ that integrates multiple objectives:

**Exploitation term:** High predicted fitness
$$a_{exploit}(S) = \hat{y}(S)$$

**Exploration term:** High uncertainty (epistemic)
$$a_{explore}(S) = \sqrt{\sigma^2_\phi(S) + \beta \cdot U(S)}$$

**Diversity term:** Sequence dissimilarity to previously tested variants
$$a_{diverse}(S) = \min_{S' \in \mathcal{D}_{tested}} d(S, S')$$

where $d(\cdot, \cdot)$ is a sequence distance metric (normalized edit distance or embedding distance).

The composite acquisition function is:

$$a(S) = \lambda_1 \cdot a_{exploit}(S) + \lambda_2 \cdot a_{explore}(S) + \lambda_3 \cdot a_{diverse}(S)$$

We also implement an Upper Confidence Bound (UCB) variant:

$$a_{UCB}(S) = \hat{y}(S) + \kappa \cdot \sqrt{\sigma^2_\phi(S) + \beta \cdot U(S)}$$

where $\kappa$ controls the exploration-exploitation trade-off.

### 2.5 Batch Selection with Experimental Constraints

Given experimental constraints, we select a batch $\mathcal{B}$ of $B$ sequences per round. We formulate this as a submodular optimization problem:

$$\mathcal{B}^* = \arg\max_{|\mathcal{B}|=B} \sum_{S \in \mathcal{B}} a(S) - \gamma \cdot R(\mathcal{B})$$

subject to:
- **Synthesis cost constraint:** $\sum_{S \in \mathcal{B}} c(S) \leq C_{max}$
- **Diversity constraint:** $\min_{S, S' \in \mathcal{B}} d(S, S') \geq d_{min}$

where $R(\mathcal{B})$ is a redundancy penalty encouraging batch diversity, $c(S)$ is the synthesis cost for sequence $S$, and $C_{max}$ is the budget.

We solve this using a greedy algorithm with lazy evaluations:

```
Algorithm: Constrained Batch Selection
Input: Candidate pool P, batch size B, constraints
Output: Selected batch B

1. B ← ∅
2. while |B| < B do
3.   for S in P \ B do
4.     Compute marginal gain: Δ(S) = a(B ∪ {S}) - a(B)
5.   end for
6.   S* ← argmax_S Δ(S) subject to constraints
7.   if S* satisfies constraints then
8.     B ← B ∪ {S*}
9.   else
10.    break
11.  end if
12. end while
13. return B
```

### 2.6 Iterative Model Updating

After each experimental round $t$, we update both the generative model ensemble and the fitness predictor with new data $\mathcal{D}_t = \{(S_i, y_i)\}_{i=1}^{B}$.

**Fitness predictor update:** We perform GP posterior update:

$$p(g | \mathcal{D}_{1:t}) \propto p(\mathcal{D}_t | g) \cdot p(g | \mathcal{D}_{1:t-1})$$

**Generative model update:** We fine-tune the ensemble using a reward-weighted likelihood objective:

$$\mathcal{L}_{update} = -\sum_{(S,y) \in \mathcal{D}_t} w(y) \cdot \log p_\theta(S|X)$$

where $w(y) = \exp(\tau \cdot y)$ upweights high-fitness sequences with temperature $\tau$.

To prevent catastrophic forgetting, we employ elastic weight consolidation (EWC):

$$\mathcal{L}_{total} = \mathcal{L}_{update} + \lambda_{EWC} \sum_i F_i (\theta_i - \theta_i^{old})^2$$

where $F_i$ is the Fisher information for parameter $\theta_i$.

### 2.7 Experimental Validation Design

#### Benchmark Tasks

We validate UGAED on three enzyme engineering tasks with increasing complexity:

1. **GFP fluorescence optimization:** Using the GFP dataset with ~50,000 variants and measured fluorescence values, we simulate experimental campaigns starting from 100 initial measurements.

2. **TEM-1 β-lactamase stability:** Optimizing thermostability using deep mutational scanning data with ~5,000 variants.

3. **AAV capsid tropism:** Engineering adeno-associated virus capsids for tissue-specific targeting, representing a harder optimization landscape.

#### Baselines

We compare against:
- **Random selection:** Uniform sampling from generated candidates
- **Greedy selection:** Top-$B$ by predicted fitness
- **Diversity-only:** Maximum diversity sampling via k-medoids
- **Standard Bayesian optimization:** UCB without generative model uncertainty
- **ProSpero:** State-of-the-art active learning for protein design

#### Evaluation Metrics

- **Hit rate:** Fraction of tested variants exceeding a fitness threshold
- **Max fitness found:** Best fitness achieved within budget
- **Sample efficiency:** Number of experiments to reach target fitness
- **Regret:** Cumulative difference from optimal selection
- **Uncertainty calibration:** Expected calibration error of predictions

#### Experimental Protocol

For wet lab validation, we will conduct a prospective study on enzyme engineering:

1. **Target:** Optimize catalytic activity of a thermostable esterase
2. **Budget:** 3 rounds × 96 variants = 288 total experiments
3. **Assays:** Colorimetric activity assay in 96-well format
4. **Comparison:** Split budget between UGAED and greedy baseline

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Quantitative improvements:** We anticipate 2-3x improvement in hit rate for identifying functional variants within fixed experimental budgets compared to greedy or random selection baselines.

2. **Calibrated uncertainty:** Our ensemble approach should achieve <10% expected calibration error, providing experimentalists with reliable confidence estimates.

3. **Practical guidelines:** We will establish recommendations for hyperparameter settings ($\alpha$, $\kappa$, $\lambda$ values) across different experimental budget regimes.

4. **Open-source framework:** Release of a modular Python library integrating with existing protein design tools (ProteinMPNN, ESMFold) and laboratory information management systems.

### Broader Impact

This work addresses a critical gap in translating ML advances to experimental impact. By providing principled uncertainty quantification and resource-aware candidate selection, we enable:

- **Cost reduction:** Estimated 50-70% reduction in experimental costs to achieve target fitness levels
- **Accelerated timelines:** Faster convergence to optimized variants in industrial enzyme development
- **Democratized access:** Lower barrier for smaller labs with limited experimental budgets to leverage generative ML

The framework generalizes beyond proteins to other biomolecular design problems including small molecules, nucleic acids, and synthetic biology circuits, potentially transforming how computational and experimental scientists collaborate across the life sciences.