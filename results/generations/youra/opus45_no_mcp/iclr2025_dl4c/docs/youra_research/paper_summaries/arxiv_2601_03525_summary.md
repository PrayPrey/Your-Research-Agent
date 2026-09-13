---
source_paper: "arxiv_2601_03525.md"
generated_at: "2026-08-19T01:58:37.357942"
model: "openai/gpt-5.2"
summary_chars: 14777
---

# Beyond Binary: Turning Partial Success into Dense Verifiable Rewards for Reinforcement Learning in Code Generation

## Key Metadata
- **Authors:** Longwen Wang et al.
- **Year:** 2026
- **Venue:** arXiv (preprint)
- **Core Contribution:** Proposes **VeRPO**, a group-based RL framework that converts **verifiable partial test-case success** into **dense, bias-corrected rewards** (via density calibration + difficulty weighting) and fuses them with **binary global outcomes** to improve code-generation pass@1 with negligible overhead.

## Section Summaries

### Abstract
Effective reward design is a central challenge
in Reinforcement Learning (RL) for code gen-
eration. Mainstream test-suite-level outcome
rewards enforce functional correctness but in-
duce sparsity, while external Reward Models
(RMs) provide dense supervision at the cost of
misalignment and additional overhead. Since
code evaluation naturally yields multiple test-
case-level outcomes, partial success—passing
a subset of test cases—offers an intrinsic, ver-
ifiable source of dense supervision.
In this
paper, we propose VeRPO (Verifiable Dense
Reward Policy Optimization), an RL frame-
work that systematically turns verifiable partial
success into reliable dense rewards. We analyze
partial-success rewards using a weighted sum
formulation, theoretically identifying a critical
cardinality bias that causes policy updates to
disproportionately favor gains from easy-test
successes over progress on frontier tests. Based
on this, VeRPO introduces a dynamic, density-
calibrated local reward that explicitly corrects
this bias and provides robust dense supervision
from partial success. To enhance alignment
with end-to-end functional correctness, VeRPO
further integrates the local dense reward with
global execution outcomes. Extensive experi-
ments across diverse benchmarks and settings
demonstrate that VeRPO outperforms outcome-
driven and RM-based baselines, achieving up
to +8.83 pass@1 gain with negligible time cost
(< 0.02%) and zero GPU memory overhead.

### Introduction & Motivation
RL fine-tuning for code generation typically uses **verifiable execution feedback** as reward, but common **binary test-suite outcome rewards** are extremely sparse under group-based RL (e.g., GRPO) because many rollout groups receive identical rewards, yielding **zero relative advantages** and no gradient signal. External **Reward Models (RMs)** densify supervision but introduce **misalignment risk**, reward hacking vulnerabilities, and substantial compute overhead. The paper observes that code execution inherently provides **per-test-case pass/fail outcomes**, so **partial success** (passing a subset of tests) is a natural, verifiable source of dense feedback. However, naïvely using pass rate can *hurt* final pass@1, motivating a principled analysis of why partial-success rewards can misguide optimization and how to correct them.

### Methodology
**Setting (MDP + group-based RL).** Code generation is modeled as an MDP where, for a prompt \(x\), the policy \(\pi_\theta\) produces up to \(T\) solution attempts; each attempt is executed on a test suite \(U_x=\{u_1,\dots,u_{|U_x|}\}\), yielding per-test outcomes. Group-based RL samples a rollout group \(G_x=\{\tau_1,\dots,\tau_N\}\) under \(\pi_{\theta_\text{old}}\) and forms relative advantages via the group mean:
\[
A(\tau_i)=\big(R(\tau_i)-\mathrm{mean}(\{R(\tau_j)\}_{j=1}^N)\big)/F_\text{norm}.
\tag{1}
\]
They default to **fixed** \(F_\text{norm}=1\) (instead of std) to avoid difficulty bias, yielding an unbiased leave-one-out estimator.

**Partial-success reward as a weighted sum (turn-level).** For turn \(t\) in trajectory \(\tau_i\), define a general partial-success reward:
\[
r_{t,i}=\sum_{j=1}^{|U_x|} w_j\, p^{(j)}_{t,i},
\quad p^{(j)}_{t,i}\in\{0,1\},
\tag{2}
\]
which subsumes pass-rate rewards (uniform \(w_j\)) and other test-weighted schemes.

**Cardinality bias (key diagnosis).** Let \(\rho_j\) be the empirical pass rate of test \(u_j\) over the rollout group:
\[
\rho_j=\frac{1}{M_x}\sum_{i=1}^{|G_x|}\sum_{t=1}^{|\tau_i|} p^{(j)}_{t,i},\quad
M_x=\sum_{i=1}^{|G_x|}|\tau_i|.
\tag{3}
\]
The group-mean baseline at turn granularity is
\[
\bar r_{\text{turn}}=\frac{1}{M_x}\sum_{i,t} r_{t,i}=\sum_{j=1}^{|U_x|} w_j\rho_j.
\tag{4–5}
\]
Rewriting in “density” form:
\[
\bar r_{\text{turn}}=\int_0^1 \bar w(\rho)\,\rho\,N(\rho)\,d\rho,
\tag{6}
\]
where \(N(\rho)\) is the empirical density of tests with pass rate \(\rho\). Because real test suites are **skewed toward easy tests** (large mass near \(\rho\approx 1\)), \(N(\rho)\) makes the baseline dominated by high-\(\rho\) (easy) regions “by sheer count,” so improving reward above the baseline tends to come from marginally more easy-test passes rather than progress on frontier tests. This systematic misallocation of learning signal is termed **cardinality bias**.

**VeRPO: Verifiable Dense Reward Policy Optimization.** VeRPO adds a **local dense reward** that corrects cardinality bias and fuses it with a **global outcome reward** for end-to-end correctness.

1) **Density-calibrated local reward (per turn).** Estimate the local test-density at \(\rho_j\) via a Gaussian KDE:
\[
\hat N(\rho_j)=\sum_{j'=1}^{|U_x|}\exp\!\left(-\frac{(\rho_j-\rho_{j'})^2}{2\sigma^2}\right),
\tag{7}
\]
with bandwidth \(\sigma\). Define difficulty-aware weights that emphasize rarely-passed tests:
\[
w_j=\exp(-\alpha \rho_j),\quad \alpha>0,
\tag{8}
\]
and then density-calibrate them:
\[
w'_j=\frac{\exp(-\alpha \rho_j)}{\hat N(\rho_j)+\delta},
\quad \delta>0,
\tag{9}
\]
yielding the **local partial-success reward**:
\[
R_{\text{turn}}(\tau_i,t)=\sum_{j=1}^{|U_x|} w'_j\,p^{(j)}_{t,i}.
\tag{10}
\]
Intuition: dividing by \(\hat N(\rho_j)\) counteracts the \(N(\rho)\) factor in Eq. (6), preventing dense easy-test regions from dominating the baseline; the exponential term pushes optimization toward the frontier.

2) **Outcome-driven global reward (trajectory-level).** Define binary full-suite correctness:
\[
R_{\text{traj}}(\tau_i)\in\{0,1\},
\]
and apply an efficiency-aware decay favoring fewer turns:
\[
\tilde R_{\text{traj}}(\tau_i)=R_{\text{traj}}(\tau_i)\cdot \gamma^{|\tau_i|},\quad \gamma\in(0,1].
\tag{11}
\]

3) **Unified advantage fusion (turn-level objective).**
Local relative advantage over all turns in the group:
\[
A_{\text{turn}}(\tau_i,t)=R_{\text{turn}}(\tau_i,t)-\mathrm{mean}\big(\mathcal G(G_x)\big),
\quad
\mathcal G(G_x)=\{R_{\text{turn}}(\tau_i,t)\}.
\tag{12}
\]
Global relative advantage over trajectories:
\[
A_{\text{traj}}(\tau_i)=\tilde R_{\text{traj}}(\tau_i)-\mathrm{mean}(\{\tilde R_{\text{traj}}(\tau_j)\}_{j=1}^N).
\tag{13}
\]
Fuse them (broadcasting trajectory-level advantage to each turn):
\[
A(\tau_i,t)=A_{\text{traj}}(\tau_i)+\beta\,A_{\text{turn}}(\tau_i,t),\quad \beta\ge 0.
\tag{14}
\]
VeRPO then performs a **clipped group-based policy optimization** step using this unified turn-level advantage (the paper notes the full objective is in Appendix D.3). Key difference vs GRPO-with-pass-rate: VeRPO’s local reward is **dynamic** (depends on current \(\rho_j\)), **density-corrected** (via \(\hat N\)), and **frontier-emphasizing** (via \(\exp(-\alpha\rho_j)\)), while still being **fully verifiable** from execution.

**Inputs/outputs & preprocessing.** Input is a coding prompt \(x\); outputs are full code solutions \(y_t\) (single-turn \(T=1\) or multi-turn \(T=4\)). Each output is executed against \(U_x\) to produce per-test pass/fail \(p^{(j)}_{t,i}\), from which VeRPO computes \(R_{\text{turn}}\), \(\tilde R_{\text{traj}}\), and then the fused advantage for optimization.

### Experiments & Results
**Training data.** RL training uses a subset dataset from (Luo et al., 2025): **7.4K verified code problems** from **TACO** (Li et al., 2023). (The provided excerpt does not specify an explicit train/val/test split for this training set; evaluation is on separate benchmark suites below.)

**Evaluation benchmarks (functional correctness).**
1) **HumanEval** and **HumanEval-Plus**  
2) **BigCodeBench** (Full and Hard subsets)  
3) **LiveCodeBench (LCB) V6 (2023.05–2025-04)**  
4) **Codeforces** problems from **CodeElo**

**Metric.** Primary metric is **pass@1**, computed using the **unbiased estimator** from Chen et al. (2021).

**Methods / baselines.**
- **GRPO** (Guo et al., 2025) with **binary outcome-driven reward** (full test suite pass/fail).
- **GRPO + RM-based dense rewards** using **AceCodeRM-7B** (Zeng et al., 2025) to score intermediate turns (named “AceCoder” in the table).
- **VeRPO**, which uses verifiable execution only (no external RM).

**Backbone model & rollout/training protocol.**
- Backbone: **Qwen3-8B**
- Horizons: **single-turn (ST, \(T=1\))** and **multi-turn (MT, \(T=4\))**; results reported for matched and mismatched train/eval horizons.
- Rollout batch: **32 problems** per iteration, **10 responses per problem**.
- Max response length: **16,384 tokens**.
- Sampling temperature: **1.0** for training rollouts; **0.6** for evaluation.
- Advantage normalization: default **\(F_\text{norm}=1\)** (fixed), unless ablated.

**Main results (pass@1).** Below is the core comparison for the most relevant matched settings, extracted from Table 1.

| Method | Train→Eval | HumanEval | HumanEval-Plus | BigCodeBench Full | BigCodeBench Hard | LCB V6 | Codeforces (CodeElo) | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GRPO (outcome) | ST→ST | 91.99 | 88.03 | 36.33 | 16.87 | 28.35 | 28.49 | 48.34 |
| AceCoder (AceCodeRM-7B) | ST→ST | 92.04 | 88.71 | 36.07 | 14.86 | 27.78 | 25.06 | 47.42 |
| **VeRPO** | **ST→ST** | **92.73** | **89.32** | **37.42** | **17.91** | **29.72** | **30.50** | **49.60** |
| GRPO (outcome) | MT→MT | 96.41 | 91.23 | 60.91 | 43.32 | 30.50 | 31.61 | 59.00 |
| AceCoder (AceCodeRM-7B) | MT→MT | **Training collapse** | **Training collapse** | **Training collapse** | **Training collapse** | **Training collapse** | **Training collapse** | — |
| **VeRPO** | **MT→MT** | **97.87** | **93.14** | **62.52** | **45.69** | **33.07** | **40.44** | **62.12** |

Key observations reported by the authors:
- In **ST→ST**, VeRPO is best on all benchmarks, with average gains of **+1.26** over outcome-driven GRPO and **+2.18** over RM-based AceCoder.
- In **MT→MT**, VeRPO’s advantage grows: vs execution-based GRPO it improves average pass@1 by **+3.12**, with the largest gain on **Codeforces: +8.83** (40.44 vs 31.61).
- **AceCoder MT training collapses**, attributed to instability from optimizing against a black-box learned RM in iterative settings (details referenced to Appendix F.1).

**Ablations (what matters).**
- **Advantage fusion components (Table 2, MT setting):**
  - Removing **local** dense advantage \(A_{\text{turn}}\) drops Codeforces from **40.44 → 34.68**, and reduces other benchmarks as well, indicating local partial-success feedback is a major driver.
  - Removing **global** anchor \(A_{\text{traj}}\) also hurts (Codeforces **40.44 → 37.62**), showing end-to-end correctness reward remains important.
  - Replacing fixed \(F_\text{norm}=1\) with **std normalization** underperforms (Codeforces **40.44 → 38.05**), consistent with the paper’s claim that std introduces task-difficulty bias.

- **Local reward design (Table 3):** comparing raw pass-rate (PS), difficulty-only (Diff), and full VeRPO (density+diff), both with/without global \(A_{\text{traj}}\).
  - Using **uncalibrated partial success** alone can be harmful: e.g., “VeRPO PS” (only pass rate) underperforms GRPO on several hard benchmarks (e.g., LCB V6 **29.41** vs GRPO **31.61**).
  - Adding \(A_{\text{traj}}\) helps, but full **density calibration** is still needed to match/best VeRPO (e.g., Codeforces: “VeRPO+PS” **35.75**, “VeRPO+Diff” **35.11**, vs **VeRPO** **40.44**), supporting the cardinality-bias correction claim.

**Signal efficiency analysis.**
- They measure **degenerate group ratio**: fraction of rollout groups with identical rewards (thus zero relative advantage).
- Outcome-driven GRPO stays around **60–70%** degenerate groups (MT setting), while **VeRPO keeps it below 25% for most of training**, and decreases further as optimization proceeds—evidence that VeRPO converts partial success into usable gradient signal without sacrificing verifiability.

**Computational cost.**
- VeRPO shares GRPO’s rollout and update pipeline and uses only execution feedback—**zero GPU memory overhead** relative to GRPO.
- Extra compute is only density-calibrated reward/advantage estimation; computing \(A_{\text{turn}}\) adds **0.10s per iteration**, **< 0.02%** of total training time (rollout + policy updates dominate).

### Discussion & Conclusion
VeRPO shows that partial test-case success can be a strong, fully verifiable dense reward source, but only after correcting the **cardinality bias** caused by skewed test difficulty distributions. The combined design—**density-calibrated local reward** plus **binary global outcome anchor**—improves pass@1 (up to **+8.83** on Codeforces) while avoiding RM instability and overhead. A key limitation implied by the method is dependence on estimating per-problem test difficulty (\(\rho_j\)) from rollout statistics, which may vary with group size and sampling; the paper positions density calibration and global anchoring as necessary stabilizers.

## Key Contributions
- Identifies and formalizes **cardinality bias** in partial-success reward optimization via the group-mean baseline and difficulty-density skew, explaining why naïve pass-rate rewards can hurt.
- Proposes **VeRPO**, introducing a **density-calibrated** and **difficulty-aware** local reward \(R_{\text{turn}}\) (Eqs. 7–10) and fusing it with an **efficiency-decayed global outcome** reward (Eq. 11) through a unified advantage (Eqs. 12–14).
- Demonstrates consistent pass@1 gains across HumanEval(+), BigCodeBench, LiveCodeBench, and Codeforces, with **negligible time overhead (<0.02%)**, **zero GPU memory overhead**, and improved optimization signal efficiency (lower degenerate group ratio).

## Potential Relevance
VeRPO is directly useful for hypotheses about **reward shaping from intrinsic verifiable signals**: it provides a concrete, analyzable mechanism (density calibration over pass-rate distributions) for turning multi-test execution into stable dense supervision. The **cardinality-bias lens** suggests broader research directions: any setting with many heterogeneous binary checks (unit tests, constraints, subgoals) may need density-aware correction to avoid over-optimizing redundant “easy” checks. The reported **RM collapse in multi-turn RL** also motivates hypotheses on when learned reward models destabilize iterative optimization and how verifiable anchors (global outcomes) can mitigate that.