---
source_paper: "arxiv_2410_02089.md"
generated_at: "2026-08-19T01:57:19.702595"
model: "openai/gpt-5.2"
summary_chars: 14111
---

# RLEF: Execution-grounded LLM Training

## Key Metadata
- **Authors:** Jonas Gehring et al.
- **Year:** 2024
- **Venue:** arXiv (2410.02089)
- **Core Contribution:** Proposes **RLEF (reinforcement learning with execution feedback)**—an end-to-end PPO fine-tuning method that trains code LLMs to iteratively improve solutions using **textual execution feedback**, achieving SOTA on CodeContests with **~10× fewer samples** than prior agentic scaffolds.

## Section Summaries

### Abstract
Large language models (LLMs) deployed as agents solve user-specified tasks
over multiple steps while keeping the required manual engagement to a mini-
mum. Crucially, such LLMs need to ground their generations in any feedback
obtained to reliably achieve the desired outcomes. We propose an end-to-end re-
inforcement learning method for teaching models to leverage execution feedback
in the realm of code synthesis, where state-of-the-art LLMs struggle to improve
code iteratively compared to independent sampling. We benchmark on competi-
tive programming tasks, where we achieve new state-of-the-art results with both
small (8B parameters) and large (70B) models while reducing the amount of sam-
ples required by an order of magnitude. Our analysis of inference-time behavior
demonstrates that our method produces LLMs that effectively leverage automatic
feedback over multiple steps.

### Introduction & Motivation
The paper targets **agentic, multi-step LLM behavior** where intermediate **environment feedback** must be incorporated to reach correct outcomes—especially relevant for autonomous tools (web interaction, retrieval, software development). In **code synthesis**, execution provides natural feedback (errors, failing tests), but prior work finds **iterative repair often underperforms independent sampling** once inference cost is controlled. The gap: current code LLMs are not reliably trained to *use* execution feedback across turns. The authors therefore frame code generation as an **iterative MDP** and optimize models end-to-end with RL so that feedback becomes causally useful at inference time.

### Methodology
RLEF trains an instruction-tuned LLM to solve programming problems through **multi-turn iterative code synthesis** with **execution feedback** in the prompt, optimized via **PPO**.

**Environment / interaction loop (iterative code synthesis):**
1. Start a chat-style dialog with a **natural-language problem description** (CodeContests-style, includes textual public tests).
2. The LLM outputs a **Python 3 code solution** (turn 1).
3. Execute the code on a **public test set** to obtain feedback: passed/failed cases, runtime/syntax errors, timeouts.
4. If any public test fails, append a formatted **execution feedback message** to the conversation, then ask the model to try again (turn 2, turn 3, …).
5. Episode terminates when either: (i) public tests pass, or (ii) a **turn limit** is reached (default: 3 attempts).
6. The final candidate is evaluated on a **private (held-out) test set**; the reward is based on passing all tests.

**Why two test sets?** Public tests provide actionable feedback and early stopping at low cost; private tests prevent reward hacking/overfitting to public outputs and reflect true correctness.

**MDP / POMDP formulation:**
- Observation \(o_0\): problem statement. Subsequent observations include dialog history plus feedback.
- Action \(a_t\): a full textual response containing code.
- Context shorthand: \(c_t = o_0, a_0, o_1, a_1, \ldots, o_t\).
- No discounting: \(\gamma = 1\). Private tests make it partially observable.

**RL algorithm: PPO with KL-regularized reward and invalid-code penalty.**
The per-step shaped reward is:
\[
R(s_t, a_t) = r(s_t, a_t) - \beta \log \frac{\pi(a_t \mid c_t)}{\rho(a_t \mid c_t)}
\]
where \(\pi\) is the updated policy and \(\rho\) is the initial (reference) policy; \(\beta\) controls regularization.

Task reward:
\[
r(s_t, a_t) =
\begin{cases}
1, & \text{if end of episode and all tests pass}\\
-1, & \text{if end of episode and any test fails}\\
-0.2, & \text{if } a_t \text{ does not contain valid code}
\end{cases}
\]

**Advantage estimation (value baseline):**
They train a value function and use:
\[
A_t = -V(c_t) + \sum_{i=t}^{T} R(s_i, a_i)
\]
(implementation details referenced to appendix; core idea is standard PPO with a learned baseline).

**Action/value granularity (key design choice):**
- Policy operates at **token level** (standard LM).
- Value function is learned at **turn level**: value of response \(a_t\) is predicted from the *last token of the prompt* preceding that response.
- A **single advantage** is used for all tokens in a response (hybrid token-policy / turn-value), which outperformed pure token- or turn-level alternatives in early experiments.

**KL computation detail:** For response likelihood \(\pi(a_t \mid c_t)\), they compute a **geometric mean** over token probabilities (instead of the product), to reduce bias toward shorter generations—especially important for non-final repair attempts.

**Models trained:** Llama 3 Instruct family (3.0/3.1; **8B and 70B**). No extra SFT required prior to RL because models are already instruction-following and strong at code.

**Training schedule (reported in main text):**
- Turn limit during training/eval (unless noted): **3 attempts**.
- Updates: **12,000** (8B) and **8,000** (70B).
- Checkpoint selection: by CodeContests **valid** performance.
(Other hyperparameters—optimizer LR, batch sizes, PPO clip, etc.—are stated to be in Appendix A, not included in the provided excerpt.)

### Experiments & Results
**Primary benchmark: CodeContests (Li et al., 2022)** competitive programming.
- Splits: training + two evaluation splits:
  - **valid:** 117 problems
  - **test:** 165 problems
- Training preprocessing: discard **669** of **13,328** training problems due to missing public/private tests → train on **12,659** problems.
- Language: models prompted/trained to output **Python 3**.
- Interaction budget: default **3 turns** (each turn counts as one “sample” for budget accounting).

**Metric: \(n@k\) solve rate (Li et al., 2022).**
- Interpreted as the probability that among \(k\) samples, selecting \(n\) candidates yields at least one correct solution (passes all tests). In multi-turn, **each response = one sample**, enabling compute-fair comparisons.

**Sampling details (main table):**
- For **1@3**: temperature **0.2**
- For **10@100**: temperature **1.0**
- Nucleus sampling: **top-p = 0.95**
- Each solve rate estimated on **200 rollouts**, using Li et al.’s estimator.

**Baselines compared:**
- **AlphaCode 9B**, **AlphaCode 41B + clustering** (Li et al., 2022)
- **Code Llama 34B + PPO** with execution reward (Xu et al., 2024)
- Agentic scaffolds on proprietary GPTs: **AlphaCodium** (Ridnik et al., 2024), **MapCoder** (Islam et al., 2024)

#### Main CodeContests results (Table 1)
Key results (solve rates; “Valid / Test”):

| Model | Setting | n@k | Valid | Test |
|---|---:|---:|---:|---:|
| AlphaCode 9B | prior | 10@1000 | 16.9 | 13.3 |
| AlphaCode 41B + clustering | prior | 10@1000 | 21.0 | 16.4 |
| Code Llama 34B + PPO | prior | 10@1000 | 19.7 | 22.4 |
| AlphaCodium gpt-3.5-turbo-16k | prior | 5@100 | 25 | 17 |
| AlphaCodium gpt-4-0613 | prior | 5@100 | 44 | 29 |
| MapCoder gpt-3.5-turbo-1106 | prior | 1@23 | – | 12.7 |
| MapCoder gpt-4-1106-preview | prior | 1@19 | – | 28.5 |
| Llama 3.1 8B Instruct | ours init | 1@3 | 8.9 | 10.5 |
| **Llama 3.1 8B Instruct + RLEF** | **ours** | **1@3** | **17.2** | **16.0** |
| Llama 3.1 70B Instruct | ours init | 1@3 | 25.9 | 27.5 |
| **Llama 3.1 70B Instruct + RLEF** | **ours** | **1@3** | **37.5** | **40.1** |
| Llama 3.1 8B Instruct | ours init | 10@100 | 21.7 | 24.8 |
| **Llama 3.1 8B Instruct + RLEF** | **ours** | **10@100** | **29.8** | **28.7** |
| Llama 3.1 70B Instruct | ours init | 10@100 | 50.2 | 50.3 |
| **Llama 3.1 70B Instruct + RLEF** | **ours** | **10@100** | **54.5** | **54.5** |

**Compute/sample-efficiency claims from the paper text:**
- On CodeContests **test**, **70B + RLEF** achieves **38.0** (test set; mentioned in text for a comparison point) vs **AlphaCodium GPT-4** at **29** using **5@100**, i.e., RLEF reaches higher solve rate with far fewer samples.
- **8B + RLEF** beats **AlphaCode 9B** with **1@3** vs AlphaCode’s **10@1000**.
- Authors interpret smaller relative gains at large budgets (10@100) as consistent with RL potentially reducing output diversity (citing Kirk et al., 2024).

#### Inference-time behavior & generalization (Table 2, Fig. 3–4)
They compare **single-turn (ST)** independent sampling vs **multi-turn (MT)** iterative repair under the same **1@3** budget.

**CodeContests test (1@3):**
- Llama 3.1 8B: ST **11.8** → MT **9.7** (iterative hurts)
- 8B + RLEF: ST **10.5** → MT **16.0** (iterative helps after RLEF)
- Llama 3.1 70B: ST **26.2** → MT **30.3**
- 70B + RLEF: ST **27.4** → MT **40.1**

**HumanEval+ (1@3):**
- 8B: ST **65.3**, MT **67.5**
- 8B + RLEF: ST **73.2**, MT **78.6**
- 70B: ST **63.9**, MT **69.5**
- 70B + RLEF: ST **75.0**, MT **80.4**
- gpt-4o-2024-05-13: ST **82.8**, MT **80.7** (iterative slightly worse)

**MBPP+ (1@3):**
- 8B: ST **58.3**, MT **57.0**
- 8B + RLEF: ST **66.9**, MT **67.6**
- 70B: ST **60.5**, MT **63.1**
- 70B + RLEF: ST **70.2**, MT **72.2**
- gpt-4o-2024-05-13: ST **68.8**, MT **71.7**

**Key qualitative behavioral findings (Fig. 3):**
- After RLEF, models:
  - Make **fewer first-turn errors** on public tests.
  - **Fix errors more reliably** in turns 2–3 across error types (output mismatch, exception, timeout, OOM).
  - Perform **larger code edits** across turns, quantified by lower similarity via **chrF** (Popović, 2015).
- Base instruct models often **repeat near-identical code** even when feedback indicates failure.

**Feedback-sensitivity ablation (random feedback):**
- They replace true execution feedback with feedback from an unrelated faulty solution (while still stopping early if public tests pass).
- Random feedback **severely impairs** error recovery and reduces pass@1 increasingly with higher turn limits (Fig. 4a), indicating improvements are not just from “more samples within a rollout” but from **using correct feedback content**.

**Turn-limit scaling under fixed sample budget (Fig. 4b):**
- After RLEF, **3–5 turns** consistently outperform single-turn independent sampling for 10@k solve rates; **5 turns** is often compute-optimal.
- Increasing to **10 turns** provides no benefit under fixed sample budget.

#### Ablations on training approach (Table 3)
**(a) Learning iterative capability: Few-shot vs SFT vs RLEF (1@3, temp 0.2)**
- 8B Instruct:
  - baseline: Valid **8.9**, Test **10.5**
  - few-shot: Valid **8.5**, Test **8.5** (worse)
  - SFT (mined rollouts): Valid **10.3**, Test **10.0** (small/no gain)
  - **RLEF:** Valid **17.2**, Test **16.0** (best)
- 70B Instruct:
  - baseline: Valid **25.9**, Test **27.5**
  - few-shot: Valid **22.5**, Test **20.3** (worse)
  - SFT: Valid **27.7**, Test **27.2** (small/no gain)
  - **RLEF:** Valid **37.5**, Test **40.1** (best)

**(b) Single-turn (ST) training vs multi-turn (MT) training (1@3, temp 0.2)**
- 8B Instruct:
  - baseline “–”: Valid ST/MT **8.9 / 11.6**, Test ST/MT **10.5 / 9.4**
  - trained ST: Valid ST/MT **10.2 / 9.9**, Test ST/MT **10.9 / 10.3**
  - trained MT (RLEF): Valid ST/MT **17.2 / 9.5**, Test ST/MT **16.0 / 16.2**
  - Notably, they mention an exception: for 8B, some settings show single-turn performance drops even when MT improves elsewhere (also noted in Table 2 discussion).
- 70B Instruct:
  - baseline “–”: Valid ST/MT **25.9 / 25.9**, Test ST/MT **27.5 / 25.6**
  - trained ST: Valid ST/MT **31.1 / 27.3**, Test ST/MT **32.9 / 28.3**
  - trained MT (RLEF): Valid ST/MT **37.5 / 30.3**, Test ST/MT **40.1 / 25.8**
Overall conclusion from ablations: **RLEF multi-turn training** yields the strongest end performance and uniquely trains models to benefit from execution feedback.

**Compute cost / infra:** Mentioned as provided in Appendix A.1 (“compute infrastructure”), but not included in the supplied excerpt; no GPU-hours or throughput numbers are available here.

### Discussion & Conclusion
RLEF shows that end-to-end PPO in an **iterative, feedback-rich environment** can train code LLMs to *actually use* execution feedback, making multi-turn repair superior to independent sampling at low budgets and improving SOTA solve rates on CodeContests. Limitations include focus on improving a **single solution** rather than decomposing large tasks, and reliance on availability of **unit tests**; they suggest combining with **automatic unit test generation** as future work. They also note potential RL side-effects like reduced diversity at high sample budgets.

## Key Contributions
- Introduces **RLEF**, an end-to-end **PPO** method that grounds code LLMs in **textual execution feedback** across multiple turns using a **public/private test split** and KL-regularized rewards.
- Achieves **state-of-the-art** results on **CodeContests** with **Llama 3.1 70B + RLEF** (e.g., **40.1** on test at **1@3**, **54.5** at **10@100**), and large gains for **8B** models (e.g., **16.0** test at **1@3**).
- Provides behavioral evidence (random-feedback ablation, chrF change analysis, turn-limit scaling) that improvements arise from **targeted self-repair using feedback**, not merely increased within-rollout diversity.

## Potential Relevance
This paper is directly useful for hypotheses about **training LLM agents to condition on environment feedback**: it provides a concrete MDP formulation, reward shaping, and a practical value-function granularity choice (turn-level value with token-level policy). It also offers strong evidence that without explicit training, **iterative repair can be net harmful** under fixed compute—supporting hypotheses about the necessity of **closed-loop RL** (or similar credit assignment) to make feedback actionable. Finally, the random-feedback ablation is a clean template for testing whether an “agent” is truly feedback-grounded versus just resampling.