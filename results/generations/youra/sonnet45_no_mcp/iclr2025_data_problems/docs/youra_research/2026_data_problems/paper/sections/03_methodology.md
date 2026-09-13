# 3. Methodology

## 3.1 Problem Formulation

Let $\mathcal{D} = \{D_1, D_2, \ldots, D_K\}$ be a collection of $K$ training domains (e.g., web text, code, scientific papers), each with a fixed token budget $B_i$ for domain $D_i$. A **static mixture schedule** samples from each domain with constant probability $p_i$ throughout training such that $\sum_{i=1}^K p_i = 1$ and the total tokens consumed from domain $i$ equals $B_i$.

We generalize this to **temporal domain schedules** where sampling probabilities $p_i(t)$ vary with training progress $t \in [0, 1]$, subject to:
- **Non-negativity**: $p_i(t) \geq 0$ for all $i, t$
- **Normalization**: $\sum_{i=1}^K p_i(t) = 1$ for all $t$
- **Budget constraint**: $\int_0^1 p_i(t) \, dt = \frac{B_i}{\sum_j B_j}$ (total exposure per domain preserved)

**Objective**: Find a temporal schedule $\{p_i(t)\}$ that maximizes final model performance $\mathcal{P}(\theta_T)$ on multi-domain benchmarks, where $\theta_T$ denotes parameters after training to completion.

**Our hypothesis**: Ordering domains by corpus diversity (high to low) yields $\mathcal{P}_{\text{div-ranked}}(\theta_T) > \mathcal{P}_{\text{static}}(\theta_T)$ when total per-domain exposure is matched. We test this against three controls: static mixture (baseline), reversed ordering (low to high diversity), and shuffled ordering (random temporal order preserving per-step domain distribution).

## 3.2 Diversity Metrics

We quantify domain diversity using three corpus-level statistics, then combine them into a composite diversity score.

**Vocabulary Entropy.** For domain $D_i$ with unigram distribution $\mathbf{u}_i$ over a vocabulary of size $V$:
$$\text{VocabEntropy}(D_i) = -\sum_{v=1}^V u_i(v) \log u_i(v)$$
Higher entropy indicates broader lexical coverage. We normalize by $\log V$ to yield scores in $[0, 1]$.

**Syntactic Complexity.** We parse a sample of 10K sentences from each domain using a constituency parser and compute the variance of parse tree depths:
$$\text{SyntaxComplexity}(D_i) = \text{Var}(\{\text{depth}(s) : s \in \text{Sample}(D_i)\})$$
Higher variance indicates more diverse syntactic structures (simple and complex sentences intermixed). We normalize using min-max scaling across domains.

**Semantic Spread.** We embed 100K random spans (length 32 tokens) from each domain using a pretrained sentence encoder, then measure semantic coverage via k-means clustering with $k=1000$:
$$\text{SemanticSpread}(D_i) = \frac{\text{Number of non-empty clusters}}{1000}$$
This quantifies how broadly the domain covers semantic space. Higher spread indicates topically diverse content.

**Composite Diversity Score.** We compute the arithmetic mean of the three normalized metrics:
$$\text{Diversity}(D_i) = \frac{1}{3}\left(\text{VocabEntropy}(D_i) + \text{SyntaxComplexity}(D_i) + \text{SemanticSpread}(D_i)\right)$$

**Limitations.** These metrics are heuristics motivated by linguistic intuition. Alternative combinations (geometric mean, learned weights) or additional features (n-gram entropy, discourse structure) may improve ranking quality. Hypothesis h-m1 (pending) will validate whether diversity scores correlate with early gradient covariance rank ($\rho \geq 0.7$ required).

## 3.3 Diversity-Ranked Curriculum Scheduling

Given diversity scores $d_1 \geq d_2 \geq \ldots \geq d_K$ (ranked high to low), we define domain sampling probabilities using **Gaussian-weighted scheduling**:

$$p_i(t) = \frac{w_i(t)}{\sum_{j=1}^K w_j(t)}$$

where the unnormalized weight for domain $i$ at training progress $t$ is:

$$w_i(t) = \max\left(w_{\min}, \exp\left(-\frac{(t - \mu_i)^2}{2\sigma^2}\right)\right)$$

Here $\mu_i = (i-1)/(K-1)$ centers the Gaussian peak for domain $i$ (e.g., $\mu_1 = 0$ for highest-diversity domain, $\mu_K = 1$ for lowest), $\sigma$ controls transition smoothness (we use $\sigma = 0.3$ based on preliminary sweeps), and $w_{\min} = 0.05$ ensures all domains remain accessible throughout training.

**Intuition.** High-diversity domains (small $\mu_i$) peak early in training, while low-diversity domains (large $\mu_i$) peak late. The Gaussian shape provides smooth transitions rather than sharp phase boundaries. The minimum weight $w_{\min}$ prevents complete domain exclusion, which could harm final multi-domain performance.

**Budget matching.** We verify numerically that $\int_0^1 p_i(t) \, dt$ matches the static baseline budget for each domain (within 1% tolerance) by adjusting the budget constraint through iterative reweighting if needed.

## 3.4 Experimental Conditions

We compare four scheduling conditions, each with identical total per-domain token exposure:

1. **Static (Baseline)**: $p_i(t) = 1/K$ for all $i, t$ (uniform mixing throughout training)

2. **Diversity-Ranked (Proposed)**: Gaussian scheduling with $\mu_i = (i-1)/(K-1)$ where $i$ indexes domains in decreasing diversity order

3. **Reversed (Control)**: Gaussian scheduling with $\mu_i = (K-i)/(K-1)$ (low diversity → high diversity, tests if ordering direction matters)

4. **Shuffled (Control)**: Gaussian scheduling with $\mu_i$ assigned randomly each epoch (tests whether smooth monotonic structure matters, or only early-domain weighting)

**Rationale for controls.** Reversed tests the core hypothesis (high→low vs low→high). Shuffled disambiguates gradient primacy (early training importance) from curriculum coherence (monotonic ordering structure). If diversity-ranked outperforms reversed but equals shuffled, improvement comes from early high-diversity exposure, not temporal ordering per se.

## 3.5 Model Architecture

We use standard GPT-2 style decoder-only transformers at two scales:

**1B Scale:**
- Layers: 24
- Hidden dimension: 1536
- Attention heads: 16
- Context length: 2048 tokens
- Total parameters: ~760M (rounded to "1B" for convenience)

**7B Scale:**
- Layers: 32  
- Hidden dimension: 4096
- Attention heads: 32
- Context length: 2048 tokens
- Total parameters: ~7B

**Training configuration:**
- Optimizer: AdamW with $\beta_1 = 0.9, \beta_2 = 0.95$, weight decay $= 0.1$
- Learning rate: $3 \times 10^{-4}$ (1B), $1.5 \times 10^{-4}$ (7B) with cosine decay to 10% of peak
- Warmup: 2000 steps (linear)
- Batch size: 512 sequences (1B), 1024 sequences (7B) distributed across GPUs
- Gradient clipping: 1.0
- Precision: BFloat16 mixed precision
- Total steps: 100,000 (1B), 150,000 (7B)

All architectural choices match standard practice for foundation model pretraining to ensure comparability with prior work.

## 3.6 PoC Validation Protocol

**PoC Goal.** Confirm that diversity-ranked scheduling is **implementable and testable**, not that it achieves performance improvements (deferred to full-scale experiments).

**Validation Criteria:**
1. **Code executes without errors** (unit tests pass, no runtime exceptions)
2. **Mechanism correctly implemented** (curriculum scheduler produces valid probability distributions, domain transitions follow Gaussian weights)
3. **Metrics are measurable** (benchmark evaluation framework operational, composite scores computable)

**PoC Workflow:**
1. Implement diversity computation for 6 Pile domains
2. Implement curriculum data loader supporting all 4 conditions
3. Implement GPT-2 model architecture (1B scale)
4. Integrate lm-evaluation-harness for MMLU, Big-Bench, domain tasks
5. Run smoke test: single run (static condition, 1B scale, seed 42) for 10 steps
6. Validate outputs: model trains without errors, checkpoints save, evaluation executes

**What PoC Does NOT Validate:**
- Performance improvements (requires 100K+ steps to convergence, n=5 seeds for statistics)
- Gradient geometry mechanism (requires multi-checkpoint PR/CKA measurements across all conditions)
- Scaling behavior (7B experiments pending)
- Statistical significance (smoke test has n=1, no power)

**Success Criterion:** If all 22 unit tests pass and smoke test completes without errors, PoC validation succeeds and full-scale experiments (Phase 5) can proceed. If implementation has fundamental flaws preventing execution, PoC fails and hypothesis requires redesign.
