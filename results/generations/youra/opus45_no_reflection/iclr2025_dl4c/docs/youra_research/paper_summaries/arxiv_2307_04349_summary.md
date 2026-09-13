---
source_paper: "arxiv_2307_04349.md"
generated_at: "2026-08-18T13:34:03.965610"
model: "openai/gpt-5.2"
summary_chars: 13689
---

# RLTF: Reinforcement Learning from Unit Test Feedback

## Key Metadata
- **Authors:** Jiate Liu et al.
- **Year:** 2023
- **Venue:** *Transactions on Machine Learning Research (TMLR), 11/2023*
- **Core Contribution:** An **online** RL fine-tuning framework for code LLMs that converts **unit test feedback into multi-granularity rewards** (coarse, fine-grained error-localized, and adaptive pass-rate) and achieves SOTA on APPS and MBPP.

## Section Summaries

### Abstract
The goal of program synthesis, or code generation, is to generate executable code based
on given descriptions. Recently, there has been an increasing number of studies employing
reinforcement learning (RL) to improve the performance of large language models (LLMs) for
code. However, current representative works either rely solely on offline frameworks, limiting
the exploration of new sample spaces, or fall short in the utilization of unit test signals, not
accounting for specific error locations within the code. To address these issues, we propose
RLTF, i.e., Reinforcement Learning from Unit Test Feedback, a novel online RL framework
with unit test feedback of multi-granularity for refining code LLMs. Our approach generates
data in real-time during training and simultaneously utilizes fine-grained feedback signals to
guide the model towards producing higher-quality code. Extensive experiments show that
RLTF achieves state-of-the-art performance on the APPS and the MBPP benchmarks. Our
code is available at: https://github.com/Zyq-scut/RLTF.

### Introduction & Motivation
Program synthesis with LLMs often produces code that looks plausible but fails on **syntactic correctness** (compile/runtime errors) or **functional correctness** (unit tests). Existing RL-for-code methods (e.g., CodeRL, PPOCoder) either operate in an **offline RL** setting (limited exploration, distribution shift) or use **coarse episode-level rewards** that ignore *where* errors occur inside code. RLTF is motivated by the fact that in code generation, **unit test feedback is cheap** and can be exploited online to continually generate new training samples and to extract **more informative signals**, including error locations and pass ratios. The goal is to improve exploration and learning stability while making rewards more diagnostic than “pass/fail/error”.

### Methodology
RLTF frames program synthesis as conditional sequence generation. Given a description \(D\), the model generates code \(W=(w_1,\dots,w_T)\) and is trained to maximize:
\[
\max P(W\mid D,\theta)=\max \prod_{t=1}^{T} p(w_t\mid D,\theta,w_{1:t-1}) \tag{1}
\]
**Online RL framework.** RLTF uses two LLM instances with **shared weights** (actor/learner-style): (i) a *generation* process samples programs \(\hat W\) from the latest model, executes them against compiler+unit tests, obtains feedback \(FB(\hat W)\), and stores tuples \((D,\hat W, FB(\hat W))\) into an **online buffer**; (ii) a *training* process consumes (a mix of ground-truth pairs and buffer-generated pairs) and updates \(\theta\). The buffer is maintained as a queue: new samples arrive continuously and old ones are evicted, enabling **on-the-fly exploration** and reducing reliance on fixed offline data.

**RL objective from unit test feedback.** RLTF applies a REINFORCE-style loss over selected token ranges:
\[
L_{\text{rl}}=-R(\hat W)\log P(\hat W\mid D,\theta)=-R(\hat W)\sum_{t=S}^{E}\log p(\hat w_t\mid D,\theta,\hat w_{1:t-1}) \tag{2}
\]
where \(S,E\) define the span to penalize (entire program or a line span), and \(R(\hat W)\) is derived from unit test outcomes.

**Multi-granularity rewards.**
1) **Coarse-grained feedback** (episode-level, same as CodeRL/PPOCoder): unit-test outcome is in {pass, failure, error, syntax error} with:
\[
R_{\text{coarse}}(\hat W)=
\begin{cases}
1.0,& FB(\hat W)=\text{pass}\\
-0.3,& FB(\hat W)=\text{failure}\\
-0.6,& FB(\hat W)=\text{error (non-syntax)}\\
-1.0,& FB(\hat W)=\text{syntax error}
\end{cases}
,\quad S_{\text{coarse}}=0,\ E_{\text{coarse}}=T \tag{3}
\]

2) **Fine-grained feedback** (error-localized): the compiler traceback is parsed to extract error subtype and (when available) the **error line**. Error subtypes are manually categorized into \(U_{\text{global}}\) (penalize whole program, e.g., Timeout Error, Recursion Error), \(U_{\text{line}}\) (penalize the specific line span, e.g., IndexError/TypeError/NameError), and \(U_{\text{ignore}}\) (skip penalization due to ambiguity, e.g., Triple-quoted Error, Indentation Error). Reward:
\[
R_{\text{fine}}(\hat W)=
\begin{cases}
0.0,& \hat W\in U_{\text{ignore}}\\
-0.3,& \text{else}
\end{cases}
,\quad
S_{\text{fine}}=
\begin{cases}
t_{\text{line\_start}},& \hat W\in U_{\text{line}}\\
0,& \text{else}
\end{cases}
,\quad
E_{\text{fine}}=
\begin{cases}
t_{\text{line\_end}},& \hat W\in U_{\text{line}}\\
T,& \text{else}
\end{cases} \tag{4}
\]
Special handling: Syntax Error is treated as \(U_{\text{global}}\) if caused by truncation at max length; otherwise \(U_{\text{line}}\).

3) **Adaptive feedback** (partial-credit from pass ratio): if the program doesn’t pass all tests, reward varies with test pass rate:
\[
R_{\text{adaptive}}(\hat W) = -0.3 + 1.3\cdot \frac{N_{\text{pass}}}{N_{\text{pass}}+N_{\text{fail}}}
,\quad S_{\text{adaptive}}=0,\ E_{\text{adaptive}}=T \tag{5}
\]

**Total training objective.** RLTF mixes supervised cross-entropy with three RL losses:
\[
L_{\text{total}} = L_{\text{sl}} + L_{\text{coarse}} + L_{\text{fine}} + L_{\text{adaptive}} \tag{6}
\]
Supervised term:
\[
L_{\text{sl}} = -\log P(W\mid D,\theta)= -\sum_{t=1}^{T}\log p(w_t\mid D,\theta,w_{1:t-1}) \tag{7}
\]
Coarse/adaptive use an advantage against a **per-problem historical best baseline** \(\hat W_{\text{baseline}}\):
\[
L_{\text{coarse}} = -\big(R_{\text{coarse}}(\hat W)-R_{\text{coarse}}(\hat W_{\text{baseline}})\big)\sum_{t=S_{\text{coarse}}}^{E_{\text{coarse}}}\log p(\hat w_t\mid \cdot) \tag{8}
\]
\[
L_{\text{adaptive}} = -\big(R_{\text{adaptive}}(\hat W)-R_{\text{adaptive}}(\hat W_{\text{baseline}})\big)\sum_{t=S_{\text{adaptive}}}^{E_{\text{adaptive}}}\log p(\hat w_t\mid \cdot) \tag{10}
\]
Fine-grained lacks a baseline (hard to define), but is reweighted to control span-length variance:
\[
L_{\text{fine}} = -\alpha R_{\text{fine}}(\hat W)\sum_{t=S_{\text{fine}}}^{E_{\text{fine}}}\log p(\hat w_t\mid \cdot),\quad
\alpha=\frac{T}{E_{\text{fine}}-S_{\text{fine}}} \tag{9}
\]
**Novelty vs prior work.** Compared to CodeRL’s offline RL and episode-level rewards, RLTF adds: (i) an **online buffer** that continually refreshes model-generated training data; (ii) **fine-grained, error-type-and-location-conditioned** penalties; (iii) **adaptive** partial-credit rewards based on unit test pass ratio.

### Experiments & Results
**Benchmarks.**
- **APPS** (Hendrycks et al., 2021): 10,000 problems with equal train/test split; avg **23.2** reference solutions and **21.2** unit tests; avg problem length **293.2 words**, avg program **18.0 lines**. Difficulty subsets: Introductory (3,639 total; train/test **2,639/1,000**), Interview (5,000; **2,000/3,000**), Competition (1,361; **361/1,000**). Typically ~20 unit tests per sample. Authors adopt APPS preprocessing; additionally, they patch APPS evaluation by running unit tests via **subprocess** to avoid **segmentation fault** hanging the online generation loop.
- **MBPP** (Austin et al., 2021): 974 problems split into **374 train / 90 val / 500 test** (plus 10 reserved for few-shot in the dataset). Each problem has 1 reference solution (~6.8 LOC) and 3 visible assert tests. RLTF is evaluated **zero-shot** on MBPP after training on APPS.

**Models / baselines.**
- Base models: **CodeT5 770M** (primary), **CodeGen 2.7B** (robustness).
- Compared against: **CodeRL** (Le et al., 2022), **PPOCoder** (Shojaee et al., 2023), plus large LMs (Codex 12B, AlphaCode 1B, GPT-3 175B, GPT-2 0.1/1.5B, GPT-Neo 2.7B) with numbers as reported/compiled in their Table 3.
- Post-processing: they reproduce **Critic Sampling** (CodeRL) due to missing official code; they clarify a missing parameter \(N\) (total samples per refine/repair), using \(N=5\) for pass@1, \(20\) for pass@5, \(1000\) for pass@1000.

**Training setup (APPS, CodeT5 770M).**
- Hardware: **8× NVIDIA V100 32GB** for training; **3 additional 8×V100** machines for sample generation.
- Batch size: **32 per GPU**; learning rate **\(2\times10^{-6}\)**.
- Duration: ~**24 hours**.
- Online buffer: length **6400**; start training after initially filling 6400 samples; buffer updated every **50 steps**; SL and RL steps split **50/50**.
- Decoding at test time: nucleus sampling **top-p=0.95**, temperature **0.6** (APPS).
- For MBPP sample generation: nucleus **top-p=0.95**, temperature **1.2**.

**Main APPS results (CodeT5 770M; without Critic Sampling unless specified).** The key headline is RLTF > CodeRL > PPOCoder(scale) on overall pass@k.
  
| Method (CodeT5 770M) | pass@1 (all) | pass@5 (all) | pass@1000 (all) |
|---|---:|---:|---:|
| CodeRL (no CS) | 1.32 | 3.32 | 17.84 |
| **RLTF (no CS)** | **1.45** | **3.78** | **19.92** |
| CodeRL (with CS) | 3.27 | 7.80 | 35.42 |
| **RLTF (with CS)** | **3.70** | **8.09** | **39.70** |

Per-difficulty (with CS), RLTF improves over CodeRL:  
- pass@1: Intro **8.40** vs 8.40? (table shows CodeRL w CS 8.40 and RLTF w CS 8.09? but overall is higher for RLTF; note Table 3 formatting is noisy—authors’ stated conclusion is RLTF best overall).  
- pass@1000 (all): **39.70** (RLTF) vs **38.30** (CodeRL).  
Given the table irregularities, the most reliable comparisons are the “all” aggregates explicitly listed above.

**Ablations (APPS, overall).**
- **Framework (online vs offline)** (all use \(L_{\text{sl}}+L_{\text{coarse}}\)): best is **Online+RLTF** with pass@1 **1.45**, pass@5 **3.78**, pass@10 **5.21**; worst is Offline with pass@1 **1.29**, pass@5 **3.43**, pass@10 **4.76** (Table 4). This supports that online generation improves exploration, and RLTF feedback helps more in the online regime.
- **Feedback components** (Table 5; overall metrics):
  - SL only: pass@1 **1.30**, pass@5 **3.39**, pass@10 **4.68**, pass@1000 **17.80**
  - +Coarse: pass@1 **1.37**, pass@5 **3.50**, pass@10 **4.92**, pass@1000 **18.31**
  - +Coarse+Fine: pass@1 **1.41**, pass@5 **3.67**, pass@10 **5.10**, pass@1000 **19.32**
  - +Coarse+Fine+Adaptive (full): pass@1 **1.45**, pass@5 **3.78**, pass@10 **5.21**, pass@1000 **19.92**
  Authors note **fine-grained feedback contributes the largest boost** among reward designs.
- **Fine reward magnitude \(R_{\text{fine}}(\hat W)\)** (Table 6): varying penalties \(\{ -0.1, -0.2, -0.3, -0.4, -0.5\}\) improves over 0.0; best pass@5 around **3.68** (at \(-0.4\)) and best pass@10 **5.10** (at \(-0.2\)).
- **Training sampling temperature** (Table 7): higher temperature improves exploration; temp **1.0** yields best pass@1 **1.45**, pass@5 **3.78**, pass@10 **5.21** vs temp 0.2/0.6.
- **Backbone model** (Table 8): RLTF improves both CodeT5 and CodeGen; on **CodeGen 2.7B**, pass@10 increases from **5.79** to **6.80** (~+1.01), pass@1 **1.64→2.04**, pass@1000 **21.44→23.96**. They claim larger models benefit more.

**MBPP zero-shot (Table 9).** CodeT5 trained with RLTF on APPS transfers best among CodeT5-based methods:
- CodeT5+CodeRL: pass@1 **25.7**, pass@80 **68.1**
- CodeT5+PPOCoder: pass@1 **26.1**, pass@80 **68.2**
- **CodeT5+RLTF:** pass@1 **30.4**, pass@80 **71.3**

**Qualitative unit-test outcome shifts.** On APPS with CodeGen, RLTF reduces the fraction of **Error** outcomes and increases **Pass**; **Failure** can rise because some “errors” are fixed into “failures” (semantic mistakes remain). Sub-error proportions generally decrease, especially **syntax errors**; **timeout** slightly increases as other errors are corrected into longer-running programs.

### Discussion & Conclusion
RLTF shows that **online RL with unit-test-driven, multi-granularity rewards** can reliably improve functional code generation over prior RL-for-code baselines, especially by reducing compiler/runtime errors via line-level penalties. Limitations include reliance on **manually crafted Python error subtype categories**, which harms transfer to other languages, and benchmark unit tests that may be insufficiently diverse/faithful for final correctness. Future work suggested: richer IO examples (possibly LLM-generated), and adding even finer feedback (e.g., static analyzers) plus automated error categorization.

## Key Contributions
- Introduces an **online RL framework with an online buffer** for program synthesis, enabling continual on-policy-ish data generation and improved exploration/stability vs offline-only methods.
- Proposes **multi-granularity unit test feedback**: (i) coarse episode rewards, (ii) **fine-grained error-localized penalties** using traceback line spans and error subtype classes, and (iii) **adaptive rewards** proportional to unit test pass rate.
- Demonstrates **SOTA improvements** on **APPS** and **MBPP** for CodeT5-based systems, with consistent gains across backbones (CodeT5 770M, CodeGen 2.7B) and detailed ablations isolating which feedback matters most.

## Potential Relevance
RLTF provides a concrete recipe for converting **execution feedback into token-level training signals**, which is useful for hypotheses about (a) whether *localizing* credit assignment (line spans) improves sample efficiency, and (b) when **online generation buffers** outperform offline RL for code. The ablations (feedback combinations, temperature, reward magnitudes) are directly reusable as experimental knobs for designing new RLHF-style training pipelines for code with automated, cheap evaluators.