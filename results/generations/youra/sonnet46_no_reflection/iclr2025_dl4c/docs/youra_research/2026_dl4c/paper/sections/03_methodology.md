# 3. Methodology

Building on the insight that policy change budget (KL divergence) should be
spent on structurally meaningful code transformations, we define structural
efficiency as a ratio and describe the four-component framework that operationalizes it.

## 3.1 Problem Setup

Let $\pi_\theta$ denote a code generation model fine-tuned from a base model
$\pi_\text{ref}$ using a post-training algorithm $\mathcal{A}$ (e.g., GRPO or DPO).
Given a prompt $x$ and a generated completion $y$, define:

- **KL divergence:** $D_\text{KL}(\pi_\theta \| \pi_\text{ref}) = \mathbb{E}_{x,y \sim \pi_\theta}[\log \pi_\theta(y|x) - \log \pi_\text{ref}(y|x)]$, measuring total policy divergence from the base model at checkpoint step $t$.
- **Semantic AST edit distance:** $d_\text{sem}(y, y')$, measuring minimum-cost tree edit operations restricted to control-flow and data-flow AST nodes between two code completions.

**Definition (Structural Efficiency):**
$$\text{SE}(\pi_\theta, \pi_\text{ref}) = \frac{\mathbb{E}[d_\text{sem}(y_\theta, y_\text{ref})]}{D_\text{KL}(\pi_\theta \| \pi_\text{ref})}$$

where $y_\theta \sim \pi_\theta(\cdot|x)$ and $y_\text{ref} \sim \pi_\text{ref}(\cdot|x)$
are completions from the fine-tuned and reference models respectively.

A high structural efficiency indicates that the method concentrates its policy
change budget on semantically meaningful code transformations. A low structural
efficiency indicates that the KL budget is consumed by surface-level changes
(variable naming, whitespace, comment style) that do not affect program behavior.

## 3.2 FA-AST Node Classification

**Rationale:** To restrict edit distance to semantically relevant nodes, we need
a principled classification of AST node types. Rather than ad hoc rules, we use
the FA-AST taxonomy [Wang et al., 2020], which classifies Python AST nodes into:

- **CONTROL_FLOW nodes:** `{If, For, While, Try, With}` — nodes governing execution branching and looping
- **DATA_FLOW nodes:** `{Assign, Call, Return, FunctionDef}` — nodes governing data transformation and function structure
- **SURFACE nodes:** all other node types (constants, names, operators, formatting)

**Why this taxonomy:** Control-flow and data-flow nodes are the nodes that
determine whether a program is functionally correct. Surface nodes affect style
and readability but not execution behavior. The FA-AST classification is grounded
in program analysis theory, validated in code clone detection and program repair
literature, and reproducible across implementations.

The Semantic Edit Proportion (SEP) measures what fraction of total edits targets
semantic (CF+DF) nodes:
$$\text{SEP} = \frac{d_\text{CF}(y_\theta, y_\text{ref}) + d_\text{DF}(y_\theta, y_\text{ref})}{d_\text{total}(y_\theta, y_\text{ref})}$$

where $d_\text{CF}$, $d_\text{DF}$, $d_\text{total}$ are edit distances restricted
to control-flow nodes, data-flow nodes, and all nodes respectively.

## 3.3 ZSS Tree Edit Distance

**Rationale:** AST-level edit distance captures structural program changes that
token-level metrics miss. Two code completions that differ only in variable names
are structurally identical at the AST level; two completions with different loop
structures are structurally distinct regardless of surface similarity.

We use the ZSS algorithm [Zhang & Shasha, 1989], which computes minimum-cost
tree edit distance in $O(n^2 m^2)$ time for trees of sizes $n$ and $m$. Edit
operations are node insertion, deletion, and relabeling, each with unit cost.
Crucially, we restrict the edit distance computation to the semantic node types
defined in Section 3.2: an insertion or deletion of a control-flow or data-flow
node counts; an insertion of a `Name` node (surface) does not.

**Why not token-level metrics:** BLEU/CodeBLEU operate on token sequences and
are sensitive to variable renaming and formatting. Line-level diffs miss
structural equivalences (e.g., a refactored loop). Graph edit distance for
program dependence graphs is NP-hard. ZSS on ASTs provides a tractable,
semantically grounded distance.

## 3.4 KL-Matched Checkpoint Comparison

**Rationale:** GRPO and DPO diverge from the base model at different rates per
training step. Step-aligned comparison (comparing checkpoint at step $t$ for both
methods) confounds training speed with structural quality. We instead compare
checkpoints at matched KL divergence levels.

**KL matching procedure:**
1. During training, log KL divergence at each checkpoint step $t$: $\kappa_t = D_\text{KL}(\pi_t \| \pi_\text{ref})$
2. For each GRPO checkpoint $\pi_t^\text{GRPO}$ with $\kappa_t^\text{GRPO}$, find a DPO checkpoint $\pi_{t'}^\text{DPO}$ such that $|\kappa_{t'}^\text{DPO} - \kappa_t^\text{GRPO}| \leq \epsilon$
3. Form matched pairs $(\pi_t^\text{GRPO}, \pi_{t'}^\text{DPO})$ for statistical comparison

We use tolerance $\epsilon = 0.05$ (±5%, per experimental specification), though
our preliminary run used $\epsilon = 0.15$ due to limited checkpoint availability.

**Checkpoint diversity requirement:** KL matching requires sufficient checkpoint
density. We impose a pre-flight check: $|\{t : \text{checkpoint}_t \text{ is unique}\}| \geq N_\text{min}$
(we recommend $N_\text{min} = 10$) before proceeding to analysis. This check
prevents the checkpoint aliasing confound described in Section 5.3.

## 3.5 Statistical Testing

For a collection of $K$ matched pairs $\{(\pi_k^\text{GRPO}, \pi_k^\text{DPO})\}_{k=1}^K$,
we compare SEP distributions using:

**Mann-Whitney U test** (primary): Tests whether $P(\text{SEP}^\text{GRPO} > \text{SEP}^\text{DPO}) > 0.5$
without assuming normality. Requires $K \geq 10$ unique pairs for adequate power.

**Bootstrap confidence interval** (secondary): 10,000 bootstrap resamples of
the mean SEP differential $\Delta = \overline{\text{SEP}}^\text{GRPO} - \overline{\text{SEP}}^\text{DPO}$,
yielding a 95% CI that does not rely on the matched-pairs assumption.

**Significance threshold:** $\alpha = 0.05$ for the Mann-Whitney test.

## 3.6 Implementation

The framework is implemented as a Python pipeline with five modules:

| Module | Function |
|--------|----------|
| `ast_decomposition.py` | FA-AST node classification; SEP computation |
| `ast_metric.py` | ZSS semantic edit distance (CF+DF nodes only) |
| `kl_metric.py` | KL log computation; checkpoint matching |
| `sep_analysis.py` | SEP analysis across matched checkpoint pairs |
| `statistical_tests.py` | Mann-Whitney U, Spearman correlation, bootstrap CI |

All modules are designed for reuse: given any two sets of checkpoints from
GRPO and DPO training runs (or any two post-training methods), the pipeline
produces a structural efficiency comparison with statistical tests and figures
(Figure 6, AST node heatmap, illustrates the FA-AST classification across
checkpoint pairs).

**Training infrastructure:** We use TRL v1.3.0 [von Werra et al., 2020]
GRPOTrainer and DPOTrainer on DeepSeek-Coder-7B-instruct-v1.5
[Guo et al., 2024] with the following configuration:

| Parameter | GRPO | DPO |
|-----------|------|-----|
| Learning rate | 1e-6 | 5e-7 |
| Batch size | 4 | 2 |
| Gradient accumulation | 4 | 8 |
| KL penalty $\beta$ | 0.04 | 0.1 |
| Training steps | 1000 | 1000 |
| Checkpoint save interval | Every 100 steps | Every 100 steps |

Execution rewards use the `evalplus` harness [Liu et al., 2023]:
binary (+1/0) and error-type rewards (categorized by exception class:
SyntaxError, RuntimeError, AssertionError, etc.).

**Evaluation dataset:** HumanEval+ (164 problems) and MBPP+ (378 problems)
from evalplus [Liu et al., 2023], covering standard function-level Python
code generation.
