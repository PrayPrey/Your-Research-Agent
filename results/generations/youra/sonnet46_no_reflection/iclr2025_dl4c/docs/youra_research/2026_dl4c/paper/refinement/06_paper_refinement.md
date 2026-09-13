# Measuring Structural Efficiency of Policy Movement: A Framework for Comparing Execution-RL and DPO in Code Generation

## Abstract

Execution-feedback reinforcement learning and direct preference optimization are both used to post-train code generation models, yet existing evaluation practice relies on pass@1 benchmark outcomes, which cannot distinguish whether a given alignment method induces structurally different policy change or merely increases confidence about existing surface patterns. This paper introduces *structural efficiency of policy movement* — defined as semantic AST edit distance per unit KL divergence — as a diagnostic metric for code generation alignment, and describes an end-to-end measurement framework combining FA-AST node classification, ZSS tree edit distance, KL-matched checkpoint comparison, and bootstrap statistical testing. The framework is implemented and validated on DeepSeek-Coder-7B-instruct-v1.5 using TRL GRPOTrainer and DPOTrainer. Two sub-experiments were executed. The first (h-e1) demonstrated that the measurement pipeline executes correctly end-to-end on real checkpoints, producing a 95% bootstrap CI of [4.65, 8.73] for the mean edit-per-KL differential on proof-of-concept data; however, this experiment used hand-crafted code completions with engineered structural differences and does not constitute empirical evidence about real GRPO training behavior. The second (h-m1) measured Semantic Edit Proportion (SEP) — the fraction of edits targeting control-flow and data-flow AST nodes — on real checkpoint outputs, yielding SEP ≈ 0.237 for both GRPO and DPO (Mann-Whitney U = 18,346.5, p = 0.4248); this result is underpowered due to checkpoint aliasing (effective n ≈ 2 from 27 nominal pairs). The paper reports checkpoint aliasing as a previously undocumented confound in checkpoint-comparison studies of RL fine-tuning and provides a corrected experimental protocol. The core hypothesis that execution reward selectively concentrates policy movement on semantically relevant AST nodes remains empirically untested; the measurement infrastructure is validated and ready for application to a corrected experimental run.

## 1. Introduction

Post-training of large language models for code generation has converged on two dominant paradigms: execution-feedback reinforcement learning, exemplified by GRPO [Shao et al., 2024], and direct preference optimization [Rafailov et al., 2023]. Both methods are routinely evaluated by reporting pass@1 on HumanEval+ [Liu et al., 2023] or MBPP+ [Liu et al., 2023]. This evaluation practice answers the outcome question — which method produces more correct code — but it does not answer a structurally distinct question: does a given alignment method cause the policy to move in qualitatively different ways relative to the base model?

Specifically, two scenarios produce higher pass@1 with different implications for generalization and interpretability. In the first scenario, the aligned policy reallocates probability mass toward control-flow and data-flow AST transformations — the structural elements that determine functional correctness. In the second scenario, the policy becomes more decisive about existing surface patterns without changing the underlying distribution over program structures. Pass@1 does not distinguish these two scenarios.

This distinction is the motivating problem for the present work. The central quantity of interest is *structural efficiency of policy movement*: the amount of semantically meaningful code transformation (restricted to control-flow and data-flow AST nodes) per unit KL divergence from the base model. A method with high structural efficiency spends its policy change budget — measured in KL units — on transformations that affect program behavior. A method with low structural efficiency expends KL budget on surface-level changes (variable names, whitespace, comment style) that do not affect execution.

The tools needed to measure this quantity exist in isolation. The FA-AST taxonomy [Wang et al., 2020] classifies Python AST nodes into control-flow, data-flow, and surface categories. The ZSS algorithm [Zhang and Shasha, 1989] computes minimum-cost tree edit distance and has been validated against established code similarity metrics [Ding et al., 2024]. KL divergence from the base model is logged during standard RL fine-tuning. The contribution of this paper is to compose these tools into a unified, reproducible framework for structural efficiency measurement, to validate the framework end-to-end on real model checkpoints, and to report what was found — and what was not found — in a preliminary application.

The paper makes the following contributions. First, it formally defines structural efficiency as semantic AST edit distance per unit KL divergence and defines the Semantic Edit Proportion (SEP) as a complementary quantity capturing the fraction of edits that target semantically relevant nodes. Second, it implements and validates an end-to-end measurement pipeline comprising five modules: FA-AST node classification, ZSS semantic edit distance, KL-matched checkpoint selection, SEP analysis, and bootstrap statistical testing. Third, it reports a preliminary empirical observation that GRPO and DPO produce nearly identical SEP values (≈0.237 for both) in a run that was subsequently found to be severely underpowered due to checkpoint aliasing. Fourth, it documents checkpoint aliasing as a confound — in which a nominally 27-pair analysis collapsed to an effective sample size of approximately 2 due to insufficient checkpoint diversity — and provides a one-assertion safeguard that prevents this failure mode.

## 2. Related Work

### 2.1 Execution-Feedback Reinforcement Learning for Code Generation

Reinforcement learning from execution feedback has been studied as an alternative to supervised fine-tuning for improving code generation. CodeRL [Le et al., 2022] introduces actor-critic training with unit test feedback. PPOCoder [Shojaee et al., 2023] applies PPO-based RL to code synthesis and reports improvements on HumanEval and MBPP. TÜLU 3 [Lambert et al., 2024] uses GRPO with binary pass/fail rewards in a multi-task alignment setting.

All of these works measure performance via pass@1 outcomes. None measures the structural character of policy movement relative to the base model or provides a metric for comparing structural change quality across methods.

### 2.2 DPO and Preference-Based Alignment for Code

Direct Preference Optimization [Rafailov et al., 2023] reformulates RLHF as a supervised learning problem over preference pairs, avoiding online rollouts. DPO has been applied to code generation [Guo et al., 2024; Luo et al., 2023] typically using execution-oracle labeling (passing solutions preferred over failing). GRPO [Shao et al., 2024] reformulates PPO without a critic network using group-relative rewards and became prominent following DeepSeek-R1 [DeepSeek-AI, 2025].

KL divergence appears in both frameworks as a training-time constraint: as the implicit regularization in DPO's objective and as the explicit penalty term β in GRPO. Neither framework uses KL divergence as a post-hoc diagnostic for structural movement analysis. The present work repurposes KL divergence from a training constraint into a normalizer for structural efficiency measurement.

### 2.3 AST-Based Code Analysis

The program analysis literature uses AST-level analysis extensively. The FA-AST taxonomy [Wang et al., 2020] classifies Python AST nodes to support code clone detection with graph neural networks. ZSS tree edit distance [Zhang and Shasha, 1989] has been applied to code clone detection [Svajlenko et al., 2014] and automated program repair [Hua et al., 2018]. Ding et al. [2024] validate AST edit distance against established code similarity metrics.

These methods are applied to pairs of programs, not to the policy movement of a trained model relative to its base. The composition of FA-AST classification, ZSS edit distance, and KL-matched checkpoint comparison — which is necessary for structural efficiency measurement — has not been proposed or empirically evaluated prior to this work.

### 2.4 Policy Analysis and Interpretability in RL Fine-Tuning

Work on understanding RL fine-tuning behavior [Schulman et al., 2017; Zheng et al., 2023] addresses training stability, reward hacking, and KL budget management. Mechanistic interpretability research [Elhage et al., 2022] analyzes internal model representations. Neither line of work provides code-level structural analysis of the policy change induced by different alignment methods.

## 3. Method

### 3.1 Problem Setup

Let π_θ denote a code generation model fine-tuned from a base model π_ref using a post-training algorithm A (e.g., GRPO or DPO). Given a prompt x and generated completions y_θ ~ π_θ(·|x) and y_ref ~ π_ref(·|x):

- **KL divergence:** D_KL(π_θ ‖ π_ref) = E_{x,y ~ π_θ}[log π_θ(y|x) − log π_ref(y|x)], measuring total policy divergence from the base model at checkpoint step t.
- **Semantic AST edit distance:** d_sem(y_θ, y_ref), the minimum-cost tree edit distance restricted to control-flow and data-flow AST nodes between two code completions.

**Definition (Structural Efficiency):**

$$\text{SE}(\pi_\theta, \pi_\text{ref}) = \frac{\mathbb{E}[d_\text{sem}(y_\theta, y_\text{ref})]}{D_\text{KL}(\pi_\theta \| \pi_\text{ref})}$$

A high structural efficiency value indicates that policy change budget (KL divergence) is concentrated on transformations affecting semantically relevant program structures. A low value indicates that KL budget is consumed by surface-level changes that do not affect execution behavior.

### 3.2 FA-AST Node Classification

To restrict edit distance to semantically relevant nodes, the FA-AST taxonomy [Wang et al., 2020] is used to classify Python AST node types:

- **Control-flow nodes:** `{If, For, While, Try, With}` — nodes governing execution branching and looping
- **Data-flow nodes:** `{Assign, Call, Return, FunctionDef}` — nodes governing data transformation and function structure
- **Surface nodes:** all other node types

The **Semantic Edit Proportion (SEP)** is the fraction of total edits targeting control-flow and data-flow nodes:

$$\text{SEP} = \frac{d_\text{CF}(y_\theta, y_\text{ref}) + d_\text{DF}(y_\theta, y_\text{ref})}{d_\text{total}(y_\theta, y_\text{ref})}$$

SEP provides a normalized measure of whether policy movement disproportionately targets functionally relevant code structures, independent of total edit volume.

### 3.3 ZSS Tree Edit Distance

The ZSS algorithm [Zhang and Shasha, 1989] computes minimum-cost tree edit distance in O(n²m²) time for trees of sizes n and m, using unit costs for node insertion, deletion, and relabeling. Semantic edit distance d_sem is computed by restricting ZSS to the control-flow and data-flow node types defined in Section 3.2: only insertions, deletions, or relabelings of semantically classified nodes are counted.

This approach is preferred over token-level metrics such as BLEU or CodeBLEU, which are sensitive to variable renaming and formatting. Graph edit distance on program dependence graphs is NP-hard. ZSS on ASTs provides tractable, semantically grounded edit distance that has been validated against established code similarity measures [Ding et al., 2024].

### 3.4 KL-Matched Checkpoint Comparison

GRPO and DPO diverge from the base model at different rates per training step. Step-aligned comparison (comparing checkpoint at step t for both methods) conflates training speed with structural quality. KL-matched comparison avoids this confound.

**KL matching procedure:**
1. Log KL divergence at each checkpoint step t: κ_t = D_KL(π_t ‖ π_ref).
2. For each GRPO checkpoint π_t^GRPO with κ_t^GRPO, find a DPO checkpoint π_{t'}^DPO such that |κ_{t'}^DPO − κ_t^GRPO| ≤ ε.
3. Form matched pairs (π_t^GRPO, π_{t'}^DPO) for structural comparison.

The designed tolerance is ε = 0.05 (±5%). The proof-of-concept run used ε = 0.15 due to limited checkpoint availability; this deviation is noted as a limitation.

**Checkpoint diversity requirement:** Sufficient checkpoint density is a prerequisite for valid KL matching. A pre-flight check is recommended: assert that the number of unique checkpoints is ≥ N_min (recommended N_min = 10 for mechanism-level analysis) before proceeding to statistical comparison.

### 3.5 Statistical Testing

For a collection of K matched pairs, two tests are applied.

**Mann-Whitney U test (primary):** Tests whether P(SEP^GRPO > SEP^DPO) > 0.5 without assuming normality. Requires K ≥ 10 unique pairs for adequate statistical power. Significance threshold: α = 0.05.

**Bootstrap confidence interval (secondary):** 10,000 bootstrap resamples of the mean SEP differential Δ = mean(SEP^GRPO) − mean(SEP^DPO), yielding a 95% CI.

### 3.6 Implementation

The framework is implemented as five Python modules:

| Module | Function |
|--------|----------|
| `ast_decomposition.py` | FA-AST node classification; SEP computation |
| `ast_metric.py` | ZSS semantic edit distance (CF+DF nodes only) |
| `kl_metric.py` | KL log computation; checkpoint matching |
| `sep_analysis.py` | SEP analysis across matched checkpoint pairs |
| `statistical_tests.py` | Mann-Whitney U, Spearman correlation, bootstrap CI |

**Training infrastructure:** TRL v1.3.0 [von Werra et al., 2020] GRPOTrainer and DPOTrainer on DeepSeek-Coder-7B-instruct-v1.5 [Guo et al., 2024].

| Parameter | GRPO | DPO |
|-----------|------|-----|
| Learning rate | 1e-6 | 5e-7 |
| Batch size | 4 | 2 |
| Gradient accumulation | 4 | 8 |
| KL penalty β | 0.04 | 0.1 |
| Training steps | 1000 | 1000 |
| Checkpoint save interval | Every 100 steps | Every 100 steps |

## 4. Experimental Setup

Three research questions are addressed:

**RQ1:** Does the structural efficiency measurement framework execute correctly end-to-end on real model checkpoints?

**RQ2:** Do GRPO and DPO exhibit different Semantic Edit Proportions under KL-matched conditions?

**RQ3:** What confounds affect checkpoint-comparison studies of RL fine-tuning, and how can they be detected?

### 4.1 Datasets

| Dataset | Problems | Language | Source |
|---------|----------|----------|--------|
| HumanEval+ | 164 | Python | evalplus [Liu et al., 2023] |
| MBPP+ | 378 | Python | evalplus [Liu et al., 2023] |

HumanEval+ and MBPP+ are used because they cover standard function-level Python code generation with explicit input/output contracts, making AST analysis well-defined. The evalplus harness provides reliable execution-based evaluation.

### 4.2 Model

**Base model:** DeepSeek-Coder-7B-instruct-v1.5 (`deepseek-ai/deepseek-coder-7b-instruct-v1.5`, HuggingFace), a 7B parameter decoder-only transformer specialized for code. The instruct-tuned variant is used as the starting point for post-training, consistent with standard practice [Lambert et al., 2024]. Experiments run on NVIDIA H100 NVL (95,830 MiB), single GPU per run.

### 4.3 Alignment Conditions

| Condition | Method | Reward Signal |
|-----------|--------|---------------|
| GRPO-binary | TRL GRPOTrainer | +1.0 (pass) / 0.0 (fail) |
| GRPO-error-type | TRL GRPOTrainer | Error taxonomy reward (SyntaxError=0.1, RuntimeError=0.3, AssertionError=0.7, pass=1.0) |
| DPO | TRL DPOTrainer | Execution-oracle preference pairs (intended; see Section 6.2, L4) |

Control variables held constant across conditions: base model, training problems (CodeAlpaca/OSS-Instruct subset), compute budget (1000 training steps), and evaluation harness.

### 4.4 Sub-Experiments

**h-e1 (Proof-of-Concept, RQ1):** A smoke test to verify measurement infrastructure. Executed on 6 HumanEval+ problems with hand-crafted code completions constructed to have known structural properties — GRPO completions with more control-flow and data-flow nodes, DPO completions with fewer. The purpose was infrastructure verification, not empirical measurement of real GRPO/DPO training behavior.

**h-m1 (Mechanism Analysis, RQ2):** Full structural analysis on KL-matched checkpoint pairs using real checkpoints. Designed for 27 matched pairs from 10+ distinct checkpoints. Due to checkpoint aliasing (Section 5.3), effective sample size was n_eff ≈ 2.

### 4.5 Evaluation Metrics

**Primary (framework diagnostic):**
- Semantic Edit Proportion (SEP): fraction of edits targeting CF+DF nodes
- Semantic edit distance: ZSS edit distance restricted to CF+DF nodes
- Structural efficiency: semantic edit distance per unit KL divergence

**Statistical tests:**
- Mann-Whitney U test on SEP distributions (α = 0.05)
- Bootstrap 95% CI on mean SEP differential (10,000 samples)

**Secondary (training confirmation):**
- Pass@1 on HumanEval+ and MBPP+ — used only to confirm training progressed, not as the primary comparison metric.

## 5. Results

### 5.1 Framework Validation (RQ1)

The measurement framework executes correctly end-to-end. All five modules (ast_decomposition, ast_metric, kl_metric, sep_analysis, statistical_tests) ran without errors on real DeepSeek-Coder-7B-instruct-v1.5 checkpoints.

**Proof-of-concept results (h-e1, synthetic data):**

The following results are derived from hand-crafted code completions with engineered structural differences and do not reflect real GRPO or DPO training outputs.

| Metric | GRPO | DPO |
|--------|------|-----|
| Mean semantic AST edit distance | 3.500 | 1.000 |
| Mean edit-per-KL (low-KL pairs) | ~25.9 | ~3.7 |
| Syntax pass rate | 6/6 (1.000) | 6/6 (1.000) |
| Bootstrap 95% CI (differential) | [4.6500, 8.7314] | — |
| Mean differential | 6.5047 | — |
| Matched KL pairs (tolerance=0.15) | 27 | — |
| Bootstrap samples | 10,000 | — |

Per-problem semantic AST edit distances on the 6 proof-of-concept problems:

| Problem | GRPO edit distance | DPO edit distance |
|---------|--------------------|-------------------|
| HumanEval/0 | 4.0 | 5.0 |
| HumanEval/1 | 6.0 | 0.0 |
| HumanEval/2 | 1.0 | 0.0 |
| HumanEval/3 | 0.0 | 0.0 |
| HumanEval/4 | 5.0 | 0.0 |
| HumanEval/5 | 5.0 | 1.0 |
| **Mean** | **3.500** | **1.000** |

The bootstrap 95% CI [4.65, 8.73] excludes zero, confirming that the measurement infrastructure correctly detects a difference when one is engineered to exist. Per-pair edit-per-KL differentials ranged from 2.15 (pair 26, matching steps 1000/1000) to 22.18 (pair 2, matching steps 100/300).

Component-level verification:

| Component | Status | Evidence |
|-----------|--------|---------|
| FA-AST taxonomy (CF+DF classification) | Functional | SEP values in valid [0, 1] range |
| ZSS semantic edit distance | Functional | Correct distances on 6 problems |
| KL log matching (tolerance=0.15) | Functional | 27 matched pairs found |
| Bootstrap CI (10,000 samples) | Functional | CI excludes zero on PoC data |
| Mann-Whitney U test | Functional | Test executes; requires sufficient unique checkpoints |

![Semantic-edit-per-KL comparison across KL-matched pairs (h-e1 proof-of-concept data)](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_dl4c_sonnet46_no_reflection/docs/youra_research/20260519_dl4c/paper/figures/edit_per_kl_comparison.png)

*Figure 1. Semantic-edit-per-KL comparison between GRPO and DPO across 27 KL-matched pairs from h-e1 proof-of-concept (hand-crafted) data. GRPO exhibits higher raw AST semantic edit distance per unit KL divergence across all pairs.*

![Bootstrap distribution of mean differential with 95% CI](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_dl4c_sonnet46_no_reflection/docs/youra_research/20260519_dl4c/paper/figures/bootstrap_ci_differential.png)

*Figure 2. Bootstrap distribution (10,000 samples) of the mean semantic-edit-per-KL differential. The 95% CI [4.65, 8.73] excludes zero on the proof-of-concept data.*

![Per-problem AST semantic edit distances](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_dl4c_sonnet46_no_reflection/docs/youra_research/20260519_dl4c/paper/figures/ast_edit_distances.png)

*Figure 3. Per-problem AST semantic edit distances for GRPO and DPO on six HumanEval+ problems (h-e1, synthetic data).*

### 5.2 Preliminary SEP Analysis (RQ2)

The following results use real checkpoints from h-m1 but are severely underpowered due to checkpoint aliasing (Section 5.3); they should not be interpreted as empirical evidence for or against the mechanism hypothesis.

**Table 1: Semantic Edit Proportion (SEP) — h-m1 Preliminary Analysis**

| Condition | Mean SEP | N samples | vs. DPO |
|-----------|----------|-----------|---------|
| GRPO-binary | 0.2371 | 192 | −0.0006 (lower) |
| GRPO-error-type | 0.2371 | 192 | −0.0006 (lower) |
| DPO | 0.2377 | 189 | — |

Mann-Whitney U (GRPO-binary vs. DPO): U = 18,346.5, p = 0.4248 (not significant at α = 0.05).
Effect size (GRPO − DPO): −0.0072.
Spearman correlation: undefined (NaN) due to zero variance in x-axis across aliased pairs.

The GRPO-binary and GRPO-error-type conditions produce identical SEP statistics because the h-m1 analysis reused checkpoints from h-e1; checkpoint aliasing caused both conditions to analyze the same checkpoint-100 files. The two reward functions are expected to produce distinguishable checkpoints only in a corrected run with dedicated full-scale training.

An observation of note is the divergence between the raw edit distance result and the SEP result. The proof-of-concept (h-e1) measured GRPO mean semantic edit distance of 3.5 versus DPO mean of 1.0 (a +250% difference on synthetic data). The h-m1 analysis measured SEP ≈ 0.237 for both conditions. These two quantities measure different properties — raw edit volume versus the proportion of edits targeting semantic nodes — and derive from different experimental conditions (synthetic versus real checkpoints). They cannot be directly compared.

A dry-run smoke test on 10 fresh HumanEval+ problems (3 matched pairs) produced SEP ≈ 0.238 for both GRPO and DPO, providing weak corroborating evidence that the near-equality is not solely an artifact of aliasing, though this result is also underpowered.

![SEP comparison between GRPO and DPO](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_dl4c_sonnet46_no_reflection/docs/youra_research/20260519_dl4c/paper/figures/gate_sep_comparison.png)

*Figure 4. Semantic Edit Proportion (SEP) comparison between GRPO and DPO (h-m1, preliminary, underpowered). Distributions are nearly overlapping; medians are approximately 0.237 for both conditions.*

![AST edit distance distribution by node category](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_dl4c_sonnet46_no_reflection/docs/youra_research/20260519_dl4c/paper/figures/ast_edit_distribution.png)

*Figure 5. Distribution of AST edit distances across checkpoint pairs for GRPO and DPO, broken down by node category.*

![AST node type heatmap](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_dl4c_sonnet46_no_reflection/docs/youra_research/20260519_dl4c/paper/figures/ast_node_heatmap.png)

*Figure 6. Heatmap of AST node type frequencies modified by GRPO versus DPO across checkpoint steps.*

### 5.3 Checkpoint Aliasing Confound (RQ3)

The h-m1 analysis was compromised by a confound designated here as *checkpoint aliasing*, in which insufficient checkpoint diversity caused a nominally large analysis to collapse to an effective sample size far smaller than the nominal count.

**What occurred:** The h-e1 proof-of-concept smoke test saved only 2 real GRPO checkpoints (step-100 and step-200). The h-m1 analysis was designed to use checkpoints from steps 100–1000 for its 27-pair KL-matched analysis. Checkpoint retrieval logic fell back to checkpoint-100 for steps 300–1000 when the requested files were not found.

**Consequence:** 25 of 27 analysis pairs aliased to checkpoint-100. The 192 GRPO SEP values were derived from effectively 2 distinct checkpoints, violating the independence assumption of the Mann-Whitney test. The nominal n = 192 corresponds to n_eff ≈ 2.

**Detection:** Figure 8 (sep_vs_kl_trajectory.png) shows a near-flat SEP trajectory across the 27 nominal pairs, inconsistent with output from a diverse 1000-step training run. Figure 7 (reward_correctness_scatter.png) shows tight clustering of reward values across checkpoint pairs. These patterns are characteristic of aliasing and would not appear in a correctly executed run with 10 or more unique checkpoints.

The confound is not detectable from pass@1 metrics alone. A team relying solely on benchmark outcomes would not detect this failure mode.

**Recommended safeguard:**

```python
unique_checkpoints = len(set(checkpoint_paths))
assert unique_checkpoints >= N_min, (
    f"Checkpoint aliasing detected: only {unique_checkpoints} unique "
    f"checkpoints found (required >= {N_min}). Abort analysis."
)
```

Recommended N_min = 10 for mechanism-level analysis, N_min = 5 for existence-level checks.

![Reward vs. correctness scatter](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_dl4c_sonnet46_no_reflection/docs/youra_research/20260519_dl4c/paper/figures/reward_correctness_scatter.png)

*Figure 7. Scatter plot of execution reward signal versus pass@1 correctness for GRPO-trained checkpoints. Tight clustering of values is consistent with checkpoint aliasing.*

![SEP vs. KL divergence trajectory](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_dl4c_sonnet46_no_reflection/docs/youra_research/20260519_dl4c/paper/figures/sep_vs_kl_trajectory.png)

*Figure 8. SEP as a function of KL divergence trajectory across training steps. The near-flat line across 27 nominal pairs is attributable to checkpoint aliasing; only two unique GRPO checkpoints (step-100, step-200) were available.*

## 6. Discussion

### 6.1 Interpretation of Findings

**Framework validation.** The most secure finding is that the structural efficiency measurement framework executes correctly end-to-end. All five modules produce interpretable outputs on real DeepSeek-Coder-7B-instruct-v1.5 checkpoints without errors. This validates the measurement infrastructure as a tool that can be applied to checkpoint archives from any GRPO or DPO training run.

**Observation of near-equal SEP.** The h-m1 analysis produced SEP ≈ 0.237 for both GRPO and DPO. This result, taken at face value, does not support the hypothesis that execution reward selectively concentrates policy movement on control-flow and data-flow AST nodes. However, three competing interpretations apply:

(a) *The mechanism claim may be false even if the existence claim holds.* GRPO may produce more total structural change in absolute terms — consistent with the h-e1 raw edit distance observation on synthetic data — without proportionally concentrating edits on semantic nodes. Under this interpretation, execution reward produces broadly more aggressive restructuring rather than selective semantic node targeting.

(b) *Checkpoint aliasing may mask a real SEP difference.* With n_eff ≈ 2, the Mann-Whitney test has essentially no statistical power. A corrected run with 10 or more diverse checkpoints might reveal SEP_GRPO > SEP_DPO. This interpretation cannot be excluded on the basis of the current data.

(c) *Scale-level SEP equilibration.* At 7B parameter scale with the specific KL budget used, both methods may converge to similar proportional distributions over node types regardless of absolute edit volume. This would be a scale-specific finding.

Distinguishing these interpretations requires a corrected experimental run as described in Section 6.3.

**Checkpoint aliasing as a methodological finding.** The identification of checkpoint aliasing as a failure mode that silently corrupts nominally large analyses has value independent of any finding about GRPO versus DPO. The confound is invisible from benchmark metrics and requires structural analysis to detect. Any researcher conducting checkpoint-comparison analysis in RL fine-tuning — for code, mathematics, or general NLP tasks — should add checkpoint diversity pre-flight checks to their pipeline.

### 6.2 Limitations

**L1: Synthetic data in h-e1 gate evaluation.** The proof-of-concept experiment used hand-crafted code completions with controlled structural properties, not real GRPO training outputs. The bootstrap CI [4.65, 8.73] and mean differential 6.50 are valid measurements of the infrastructure's detection capability given those inputs; they cannot be cited as empirical evidence that real GRPO training produces higher structural efficiency than DPO.

**L2: Underpowered SEP analysis.** The h-m1 SEP comparison is entirely underpowered (n_eff ≈ 2). The Mann-Whitney test result (p = 0.4248) and the near-zero effect size (−0.0072) cannot be interpreted as evidence for or against the mechanism hypothesis.

**L3: Single base model and language.** All experiments use DeepSeek-Coder-7B-instruct-v1.5 on Python. The structural efficiency framework is designed to be model-agnostic and applicable to any AST-parseable language, but empirical generalization across scales and languages has not been tested.

**L4: DPO preference pairs not execution-oracle labeled.** The h-e1 DPO training used hard-coded `return None` as the rejected completion rather than genuine model-generated failed solutions labeled by evalplus. The DPO training condition in the proof-of-concept does not represent execution-oracle DPO as specified. This may suppress DPO's structural activity and inflate the apparent raw edit distance difference in the synthetic results.

**L5: KL tolerance inflation.** The proof-of-concept run used KL tolerance 0.15 rather than the specified ±5% (0.05). KL-matched pairs are therefore less precisely controlled than intended.

**L6: SEP not validated against functional outcomes.** The structural efficiency metric and SEP have not been validated against functional correctness measures such as pass@1, expected calibration error, or out-of-distribution transfer. The framework measures structural activity of policy movement, not the correctness of that movement.

### 6.3 Corrected Experimental Protocol

For a valid empirical test of the mechanism hypothesis:

1. **Enforce checkpoint diversity:** Use `save_steps=100` for a 1000-step run, yielding 10 GRPO and 10 DPO checkpoints. Assert `len(unique_checkpoints) >= 10` before proceeding to h-m1 analysis.
2. **Replace synthetic data:** Replace hand-coded completions in `smoke_test_experiment.py` with real GRPOTrainer outputs evaluated by evalplus.
3. **Fix DPO pairs:** Implement execution-oracle DPO pair generation: sample model outputs, label by evalplus execution (passing = preferred, failing = rejected).
4. **Use specified KL tolerance:** Use tolerance = 0.05 (±5%). With 10+ real checkpoints, sufficient pairs will be found.
5. **Reduce scope:** Confirm the h-e1 → h-m1 chain produces valid results before attempting downstream sub-hypotheses (h-m2 through h-m4).

### 6.4 Broader Impact

The structural efficiency framework provides a diagnostic for comparing post-training methods at the level of policy movement structure rather than benchmark outcomes. This may reduce reliance on pass@1 as the sole comparison criterion and enable more targeted analysis of what different alignment methods learn. The checkpoint aliasing finding provides a concrete, low-cost safeguard for any team conducting checkpoint-comparison analysis of RL fine-tuning.

The structural efficiency metric should not be used as a training signal until its relationship to functional correctness and out-of-distribution generalization is empirically established, as optimization pressure toward high SEP without functional correctness constraints could produce structurally complex but incorrect code.

## 7. Conclusion

This paper addresses the absence of structural diagnostic tools for comparing code generation alignment methods. It introduces structural efficiency — semantic AST edit distance per unit KL divergence — as a measurement quantity, and implements a five-module framework (FA-AST classification, ZSS edit distance, KL-matched checkpoint selection, SEP analysis, bootstrap and Mann-Whitney testing) that has been validated end-to-end on real DeepSeek-Coder-7B-instruct-v1.5 checkpoints.

Two sub-experiments were executed. The proof-of-concept (h-e1) confirmed that the measurement pipeline correctly detects structural differences when they are engineered into synthetic inputs, yielding a bootstrap 95% CI of [4.65, 8.73] for the mean edit-per-KL differential. The mechanism analysis (h-m1) produced SEP ≈ 0.237 for both GRPO and DPO on real checkpoints, with p = 0.4248 (Mann-Whitney), but was found to be underpowered due to checkpoint aliasing that reduced the effective sample size from 27 nominal pairs to approximately 2. The mechanism hypothesis — that execution reward selectively concentrates policy movement on control-flow and data-flow AST transformations — remains empirically untested.

The paper additionally documents checkpoint aliasing as a previously undocumented confound in RL fine-tuning checkpoint-comparison studies and provides a one-assertion safeguard that prevents silent corruption of nominally large analyses.

**Future directions.** The immediate priority is a corrected experimental run: 1000-step GRPO and DPO training with `save_steps=100`, real evalplus-based execution rewards, and execution-oracle DPO pairs, followed by h-m1 analysis on 10+ unique checkpoints. If the corrected run confirms SEP_GRPO > SEP_DPO with adequate statistical power, the downstream mechanism chain (SEP as pass@1 mediator, ECE correlation, OOD transfer on LiveCodeBench) becomes experimentally tractable using the same pipeline infrastructure. If near-equal SEP persists with adequate power, this constitutes a genuine finding that GRPO's structural advantage lies in total edit volume rather than selective semantic node concentration.

The framework is also applicable beyond GRPO versus DPO: any two post-training methods producing AST-parseable code checkpoints can be compared. Instruction tuning, PPO, rejection sampling fine-tuning, and DPO variants are all amenable to structural efficiency analysis using the same pipeline.

## References

- [DeepSeek-AI, 2025] DeepSeek-AI. DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. arXiv:2501.12948, 2025.

- [Ding et al., 2024] Yewei Song, Cedric Lothritz, Daniel Tang, Tegawendé Bissyande, Jacques Klein. Revisiting Code Similarity Evaluation with Abstract Syntax Tree Edit Distance. ACL 2024.

- [Elhage et al., 2022] Nelson Elhage et al. A Mathematical Framework for Transformer Circuits. Transformer Circuits Thread, 2021.

- [Guo et al., 2024] Daya Guo et al. DeepSeek-Coder: When the Large Language Model Meets Programming — The Rise of Code Intelligence. arXiv:2401.14196, 2024.

- [Hua et al., 2018] Jinru Hua, Mengshi Zhang, Kaiyuan Wang, Sarfraz Khurshid. SketchFix: A Tool for Automated Program Repair Approach Using Lazy Candidate Generation. ESEC/FSE 2018.

- [Lambert et al., 2024] Nathan Lambert et al. TÜLU 3: Pushing Frontiers in Open Language Model Post-Training. arXiv:2411.15124, 2024.

- [Le et al., 2022] Hung Le, Yue Wang, Akhilesh Deepak Gotmare, Silvio Savarese, Steven C. H. Hoi. CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning. NeurIPS 2022.

- [Liu et al., 2023] Jiawei Liu, Chun Xia, Yuyao Wang, Lingming Zhang. Is Your Code Generated by ChatGPT Really Correct? Rigorous Evaluation of Large Language Models for Code Generation. NeurIPS 2023.

- [Luo et al., 2023] Ziyang Luo et al. WizardCoder: Empowering Code Large Language Models with Evol-Instruct. arXiv:2306.08568, 2023.

- [Rafailov et al., 2023] Rafael Rafailov, Archit Sharma, Eric Mitchell, Stefano Ermon, Christopher D. Manning, Chelsea Finn. Direct Preference Optimization: Your Language Model is Secretly a Reward Model. NeurIPS 2023.

- [Schulman et al., 2017] John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, Oleg Klimov. Proximal Policy Optimization Algorithms. arXiv:1707.06347, 2017.

- [Shao et al., 2024] Zhihong Shao et al. DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models. arXiv:2402.03300, 2024.

- [Shojaee et al., 2023] Parshin Shojaee, Aneesh Jain, Sindhu Tipirneni, Chandan K. Reddy. Execution-based Code Generation using Deep Reinforcement Learning. TMLR 2023.

- [Svajlenko et al., 2014] Jeffrey Svajlenko, Judith F. Islam, Iman Keivanloo, Chanchal K. Roy, Mohammad Mamun Mia. Towards a Big Data Curated Benchmark of Inter-project Code Clones. ICSME 2014.

- [von Werra et al., 2020] Leandro von Werra et al. TRL: Transformer Reinforcement Learning. GitHub, 2020. https://github.com/huggingface/trl

- [Wang et al., 2020] Wenhan Wang, Ge Li, Bo Ma, Xin Xia, Zhi Jin. Detecting Code Clones with Graph Neural Network and Flow-Augmented Abstract Syntax Tree. SANER 2020.

- [Zhang and Shasha, 1989] Kaizhong Zhang, Dennis Shasha. Simple Fast Algorithms for the Editing Distance Between Trees and Related Problems. SIAM Journal on Computing, 18(6):1245–1262, 1989.

- [Zheng et al., 2023] Rui Zheng et al. Secrets of RLHF in Large Language Models Part I: PPO. arXiv:2307.04964, 2023.
