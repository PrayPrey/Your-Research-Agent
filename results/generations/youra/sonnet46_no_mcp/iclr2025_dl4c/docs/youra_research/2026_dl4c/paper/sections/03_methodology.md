# 3. Methodology

## 3.1 Overview

Our methodology is designed around a single question: does task granularity determine GRPO advantage variance through the reward sparsity pathway? To answer this cleanly, we hold constant every factor except task granularity: same model, same GRPO configuration ($G=8$), same training duration (120 steps per condition), same evaluation protocol. Only the task source — and hence the expected positive reward rate — varies.

This design follows directly from our key insight: if GRPO advantage collapse is driven by reward sparsity (near-zero positive reward rates), then comparing two conditions with different structural positive rates under otherwise identical settings will isolate the granularity effect. The function-level condition (APPS+CodeContests competitive programming) is expected to produce near-zero positive rates for a 7B model; the repo-level condition (SWE-bench Verified) allows partial credit through file-path overlap, producing non-zero positive rates even for an unspecialized model.

## 3.2 Model

We use **CodeLlama-7b-Instruct-hf** [Rozière et al., 2023] as the representative 7B-class model. The instruction-tuned variant is chosen to ensure the model can follow task formatting requirements and generate syntactically plausible code, isolating reward sparsity from formatting failures. We use the HuggingFace Hub checkpoint (`codellama/CodeLlama-7b-Instruct-hf`) with no additional fine-tuning.

**Rationale:** CodeLlama-7b-Instruct is a well-characterized baseline for function-level code generation. Its known capability limits at competitive programming difficulty (near-zero solve rates on APPS) make it a reliable test case for reward sparsity effects. Using an instruction-tuned variant controls for the confound that a base model may fail to generate syntactically valid code entirely.

## 3.3 Datasets

**Function-level condition:** We use **APPS** [Hendrycks et al., 2021] (`codeparrot/apps`, train split, 5,000 problems) and **CodeContests** [Li et al., 2022] (`deepmind/code_contests`, train split, 13,328 problems). APPS provides problems from competitive programming competitions with stdin/stdout test cases and difficulty labels (tiers 0–4). CodeContests provides Codeforces problems with public test cases. Both datasets require writing self-contained Python programs solving algorithmic problems.

**Repo-level condition:** We use **SWE-bench Verified** [Jimenez et al., 2024] (`princeton-nlp/SWE-bench_Verified`, test split, 500 GitHub issues). Each task requires generating a unified diff patch that resolves a real software engineering issue in a Python repository. The reward function validates that the generated patch modifies at least one file mentioned in the gold patch (partial credit structure).

**Rationale for dataset pairing:** APPS+CodeContests and SWE-bench Verified represent the two dominant paradigms in execution-feedback code RL. The function/repo-level distinction captures a structural difference in task granularity that determines expected positive reward rates: competitive programming problems require fully correct algorithmic solutions (binary), while repository-level tasks allow partial reward through file-path overlap (non-binary). This pairing maximally contrasts the reward sparsity variable while using standard, widely-cited benchmarks.

## 3.4 GRPO Configuration

Both conditions use identical GRPO hyperparameters:

| Hyperparameter | Value |
|---|---|
| Group size $G$ | 8 |
| Batch size $B$ | 4 prompts/step |
| Training steps | 120 |
| Temperature (sampling) | 0.8 |
| Max new tokens | 512 |
| Framework | TRL 1.3.0 GRPOTrainer |
| GPU | NVIDIA H100 NVL |

**Rationale for $G=8$:** Consistent with DeepSeek-R1 [DeepSeek-AI, 2025] and standard GRPO practice. $G=8$ provides a meaningful group size — small enough to be computationally feasible, large enough that the probability of all-zero groups is informative about the underlying positive rate.

**Rationale for 120 steps:** Sufficient to compute stable variance estimates (120 independent per-step observations) without the cost of full training runs. The advantage variance is a property of the reward distribution at initialization, not of learned behavior, so it stabilizes quickly.

## 3.5 Reward Functions

**Function-level reward:** Binary execution reward. Each of the $G=8$ completions is executed against the problem's test cases via subprocess. Reward = 1.0 if all test cases pass, 0.0 otherwise. Execution timeout: 3 seconds per test case.

**Repo-level reward:** Partial credit reward based on file-path overlap. The generated unified diff is parsed to extract modified file paths. Reward = fraction of gold patch file paths that appear in the generated patch. This non-binary structure provides reward signal even for incomplete solutions, which is why repo-level conditions maintain non-zero positive rates.

## 3.6 Advantage Variance Measurement

At each training step $t$, we record the per-step GRPO advantage variance:

$$\text{adv\_var}(t) = \text{Var}\left(\left\{ A_i^{(j)} : i \in [G], j \in [B] \right\}\right)$$

where $A_i^{(j)} = (r_i^{(j)} - \bar{r}^{(j)}) / \text{std}(r^{(j)})$ is the normalized advantage for completion $i$ in group $j$. For degenerate groups where $\text{std}(r^{(j)}) = 0$, advantages are set to 0.0.

This per-step variance is logged by the `RewardDensityCallback` at every training step. We aggregate across all $BG = 32$ advantage values per step to produce a scalar variance estimate.

## 3.7 Statistical Analysis

We compare per-step advantage variance between the two conditions using **Welch's two-sample t-test** on log-transformed variance values. Log transformation is applied because advantage variance is right-skewed (bounded below at zero, with heavy upper tail). Welch's t-test is used over Student's t-test because the two conditions have substantially different variances (this is precisely what we are measuring).

**Null hypothesis $H_0$:** Mean advantage variance is equal between function-level and repo-level conditions.

**Alternative hypothesis $H_1$:** Mean advantage variance differs between conditions (two-tailed; directional prediction is repo > function, but two-tailed is conservative).

Effect size is reported as Cohen's $d$ computed from the log-transformed means and pooled standard deviation.

## 3.8 Curriculum GRPO Infrastructure (H-E1)

In parallel with the H-M1 mechanism study, we implement and validate the training infrastructure for a full 4-condition curriculum GRPO experiment:

- **CurriculumDataset**: Wraps APPS+CodeContests with a `set_step()` interface that changes the difficulty tier sampling at configurable step thresholds.
- **CurriculumCallback**: Triggers difficulty tier transitions at pre-specified steps (e.g., easy tiers 0–2 for steps 0–2500, hard tiers 3–4 for steps 2501–5000).
- **RewardDensityCallback**: Logs per-step reward density (fraction of batches with non-zero reward std) and advantage variance to CSV files for downstream analysis.

A 10-step smoke test confirms all 4 conditions (curriculum, uniform, easy\_only, hard\_only) run without errors, dataset loading is correct, the CurriculumCallback transitions are functional, and all logging artifacts are produced. This infrastructure is the foundation for the full 5000-step training run that will empirically test the primary behavioral hypothesis.
