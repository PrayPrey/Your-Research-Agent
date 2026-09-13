---
source_paper: "arxiv_2307_04349.md"
generated_at: "2026-08-19T01:56:34.784298"
model: "openai/gpt-5.2"
summary_chars: 13270
---

# RLTF: Reinforcement Learning from Unit Test Feedback

## Key Metadata
- **Authors:** Jiate Liu et al.
- **Year:** 2023
- **Venue:** *Transactions on Machine Learning Research (TMLR)* (11/2023)
- **Core Contribution:** An **online RL fine-tuning framework** for code LLMs that uses **multi-granularity unit-test/exception feedback** (coarse, fine-grained localized penalties, and adaptive pass-rate rewards) to achieve SOTA on **APPS** and **MBPP**.

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
Program synthesis with LLMs often produces syntactically plausible code that still fails compilation or unit tests, and standard MLE training does not directly optimize functional correctness. Prior RL-for-code approaches (e.g., CodeRL, PPOCoder) are limited by (i) **offline RL** data collection that restricts exploration and can suffer distribution shift, and (ii) **coarse episodic rewards** that ignore *where* an error occurs in code. Because unit-test execution is relatively cheap, the paper argues online interaction is feasible and beneficial. RLTF addresses these gaps via an **online sampling buffer** and **multi-granularity rewards** extracted from compiler/unit-test feedback to target error locations and partial correctness.

### Methodology
RLTF formulates program synthesis as conditional generation of code \(W\) given description \(D\), maximizing:
\[
\max P(W|D,\theta)=\max \prod_{t=1}^{T} p(w_t|D,\theta,w_{1:t-1}) \tag{1}
\]
**Online RL framework.** Training uses two LLM instances with **shared weights**: (1) a *generator* that samples code \(\hat W\) for problems \(D\), executes unit tests/compilation to obtain feedback \(FB(\hat W)\), and pushes tuples \((D,\hat W, FB(\hat W))\) into an **online buffer**; (2) a *trainer* that draws both ground-truth (SL) data and buffer (RL) data to update parameters. The buffer is maintained as a queue: new samples are appended and old ones deleted, enabling on-the-fly exploration with the latest policy.

**RL objective from unit-test feedback.** RL loss uses REINFORCE-style sequence likelihood weighted by reward \(R(\hat W)\), potentially applied to a span \([S,E]\) of tokens:
\[
L_{rl}=-R(\hat W)\log P(\hat W|D,\theta)= -R(\hat W)\sum_{t=S}^{E}\log p(\hat w_t|D,\theta,\hat w_{1:t-1}) \tag{2}
\]

**Multi-granularity feedback signals.**
1. **Coarse-grained reward** (episode-level), identical to CodeRL/PPOCoder:
\[
R_{\text{coarse}}(\hat W)=
\begin{cases}
1.0 & FB(\hat W)\text{ is pass}\\
-0.3 & FB(\hat W)\text{ is failure}\\
-0.6 & FB(\hat W)\text{ is error except syntax error}\\
-1.0 & FB(\hat W)\text{ is syntax error}
\end{cases},
\quad S_{\text{coarse}}=0,\ E_{\text{coarse}}=T \tag{3}
\]
2. **Fine-grained feedback** localizes penalties using exception type + location parsing. Error subtypes are grouped into **\(U_{global}\)** (penalize whole program; logic-wide errors like Timeout/Recursion), **\(U_{line}\)** (penalize the specific line span causing the error; e.g., IndexError/TypeError/NameError), and **\(U_{ignore}\)** (skip due to unreliable localization; e.g., “Triple-quoted Error”, “Indentation Error”). Reward and penalized span:
\[
R_{\text{fine}}(\hat W)=
\begin{cases}
0.0 & \hat W\in U_{ignore}\\
-0.3 & \text{else}
\end{cases},
\quad
S_{\text{fine}}=
\begin{cases}
t_{\text{line\_start}} & \hat W\in U_{line}\\
0 & \text{else}
\end{cases},
\quad
E_{\text{fine}}=
\begin{cases}
t_{\text{line\_end}} & \hat W\in U_{line}\\
T & \text{else}
\end{cases} \tag{4}
\]
3. **Adaptive feedback** for partial correctness on failing solutions, proportional to pass rate over unit tests:
\[
R_{\text{adaptive}}(\hat W)= -0.3 + 1.3\cdot \frac{N_{pass}}{N_{pass}+N_{fail}},
\quad S_{\text{adaptive}}=0,\ E_{\text{adaptive}}=T \tag{5}
\]

**Combined optimization.** RLTF trains with both supervised cross-entropy and RL terms:
\[
L_{\text{total}}=L_{sl}+L_{\text{coarse}}+L_{\text{fine}}+L_{\text{adaptive}} \tag{6}
\]
\[
L_{sl}=-\log P(W|D,\theta) = -\sum_{t=1}^{T}\log p(w_t|D,\theta,w_{1:t-1}) \tag{7}
\]
Coarse and adaptive RL use **self-improvement baselines** \(\hat W_{\text{baseline}}\) (historical best under \(D\)) to reduce variance and encourage continual improvement:
\[
L_{\text{coarse}}=-(R_{\text{coarse}}(\hat W)-R_{\text{coarse}}(\hat W_{\text{baseline}}))\sum_{t=S_{\text{coarse}}}^{E_{\text{coarse}}}\log p(\hat w_t|\cdot) \tag{8}
\]
\[
L_{\text{fine}}=-\alpha R_{\text{fine}}(\hat W)\sum_{t=S_{\text{fine}}}^{E_{\text{fine}}}\log p(\hat w_t|\cdot) \tag{9}
\]
\[
L_{\text{adaptive}}=-(R_{\text{adaptive}}(\hat W)-R_{\text{adaptive}}(\hat W_{\text{baseline}}))\sum_{t=S_{\text{adaptive}}}^{E_{\text{adaptive}}}\log p(\hat w_t|\cdot) \tag{10}
\]
Because fine-grained spans vary in length, they scale it with an adaptive weight:
\[
\alpha=\frac{T}{E_{\text{fine}}-S_{\text{fine}}}
\]
to equalize magnitude relative to whole-episode losses.

**Input/output & preprocessing.** Input \(D\) is problem text formatted as in APPS preprocessing (per Hendrycks et al., 2021) and MBPP prompt format (problem + “Your code should satisfy these tests:” + asserts). Output is generated Python program text. For online generation robustness on APPS, they execute unit tests via **subprocess** to avoid segmentation-fault hangs that break online sampling.

**Implementation/training hyperparameters (APPS).** Base model: **CodeT5 770M** (also CodeGen 2.7B in ablations). Hardware: training on **8×V100 32GB**, plus **three additional 8×V100 machines** for concurrent online sampling. Batch size **32 per GPU**, learning rate **\(2\times 10^{-6}\)**, training time ~**24 hours**. Online buffer length **6400**, updated **every 50 steps**; training starts after filling 6400 initial samples. Training schedule: **50% steps SL**, **50% steps RL** (mirroring CodeRL). Sampling during evaluation: nucleus sampling top-\(p=0.95\), temperature **0.6** (APPS test); during MBPP sample generation: top-\(p=0.95\), temperature **1.2** (zero-shot eval setting).

### Experiments & Results
**Benchmarks.**
- **APPS** (Hendrycks et al., 2021): **10,000** problems, **50/50 train-test**. Difficulty subsets: Introductory **3,639** (train/test **2,639/1,000**), Interview **5,000** (train/test **2,000/3,000**), Competition **1,361** (train/test **361/1,000**). Avg **23.2** reference solutions/problem, **21.2** unit tests/problem, mean description length **293.2 words**, mean program length **18 lines**. Typically **20** unit tests per sample.
- **MBPP** (Austin et al., 2021): **974** problems (train/val/test **374/90/500**), plus **10** reserved for few-shot evaluations; each has 1 solution (~**6.8 lines**) and **3** visible assert unit tests. They evaluate **zero-shot** for CodeT5-based models trained on APPS.

**Metrics.**
- APPS: **pass@k** for \(k\in\{1,5,10,100,1000\}\) (reported in tables: pass@1, pass@5, pass@1000; ablations include pass@10/100).
- MBPP: **pass@1**, **pass@80**.

**Baselines.**
- RL-for-code: **CodeRL** (Le et al., 2022), **PPOCoder** (Shojaee et al., 2023).
- Large models: **Codex 12B** (Chen et al., 2021), **AlphaCode 1B** (Li et al., 2022), **GPT-3 175B** (Brown et al., 2020), **GPT-2** (Radford et al., 2019), **GPT-Neo 2.7B** (Black et al., 2021).
- Post-processing: **Critic Sampling** (Le et al., 2022) (authors reproduce; refine+repair with \(M=1\), max iterations 1; total samples \(N\) set to 5/20/1000 for pass@1/5/1000).

**Main APPS results (CodeT5 770M).** RLTF improves over CodeRL and PPOCoder and reports SOTA among CodeT5-based methods. Key numbers from Table 3:

| Method (CodeT5 770M) | Critic Sampling | pass@1 (All) | pass@5 (All) | pass@1000 (All) |
|---|---:|---:|---:|---:|
| CodeRL | w/o | 1.32 | 3.32 | 17.84 |
| RLTF | w/o | **1.45** | **3.78** | **19.92** |
| CodeRL | w | 3.37 | 6.81 | 35.42 |
| RLTF | w | **3.78** | **7.80** | **38.30** |

Per-difficulty (without CS) also improves: pass@1 Intro **4.06→4.16**, Interview **0.79→0.97**, Competition **0.15→0.20**.

**Ablations (APPS).**
- **Online vs offline framework** (Table 4; metrics are “All”):
  - Offline: pass@1 **1.29**, pass@5 **3.43**, pass@10 **4.76**
  - Offline + RLTF: pass@1 **1.34**, pass@5 **3.53**, pass@10 **4.92**
  - Online: pass@1 **1.37**, pass@5 **3.50**, pass@10 **4.92**
  - Online + RLTF: **best** pass@1 **1.45**, pass@5 **3.78**, pass@10 **5.21**
  → Online sampling and RLTF rewards are complementary; RLTF helps more in the online regime.
- **Feedback components** (Table 5; “All”):
  - SL only: pass@1 **1.30**, pass@5 **3.39**, pass@10 **4.68**, pass@1000 **17.80**
  - +Coarse: pass@1 **1.37**, pass@5 **3.50**, pass@10 **4.92**, pass@1000 **18.31**
  - +Coarse+Fine: pass@1 **1.41**, pass@5 **3.67**, pass@10 **5.10**, pass@1000 **19.32**
  - +Coarse+Fine+Adaptive (full): **pass@1 1.45**, **pass@5 3.78**, **pass@10 5.21**, **pass@1000 19.92**
  They note **fine-grained feedback contributes the largest gain** among reward additions.
- **Fine penalty magnitude \(R_{\text{fine}}(\hat W)\)** (Table 6): values from \(-0.1\) to \(-0.5\) all outperform no fine penalty; best pass@5 observed at \(-0.4\) (3.68) though differences are modest.
- **Sampling temperature during training** (Table 7): higher temperature improves (All) pass@1 **1.34 (0.2)** → **1.45 (1.0)**; pass@5 **3.56→3.78**; pass@10 **4.99→5.21**, suggesting exploration benefits online RL.
- **Backbone robustness (Table 8).** On APPS, CodeGen 2.7B benefits strongly:
  - CodeGen 2.7B w/o RLTF: pass@10 **5.79**, pass@1000 **21.44**
  - CodeGen 2.7B w/ RLTF: pass@10 **6.80**, pass@1000 **23.96**
  RLTF gains increase with model size (observed qualitatively by authors).

**MBPP zero-shot transfer (Table 9).** Model trained with RLTF on APPS then evaluated zero-shot on MBPP:
- CodeT5+CodeRL: pass@1 **25.7**, pass@80 **68.1**
- CodeT5+PPOCoder: pass@1 **26.1**, pass@80 **68.2**
- **CodeT5+RLTF:** pass@1 **30.4**, pass@80 **71.3** (best among CodeT5-based; also beats several GPT fine-tuned baselines listed in Austin et al., 2021).

**Computational cost / systems notes.** APPS training: ~**24 hours** on **8×V100**, plus **3 extra 8×V100** machines for continuous sample generation; online buffer update every **50 steps**, buffer size **6400**. They explicitly patch APPS evaluation to run unit tests in **subprocess** to avoid segfault deadlocks in online generation.

### Discussion & Conclusion
RLTF demonstrates that **online RL with richer, localized unit-test feedback** can meaningfully improve functional code generation over prior offline/coarse-reward RL approaches. The main limitation acknowledged is **manual error subtype categorization**, which reduces transferability to other languages; another limitation is benchmark unit-test diversity/coverage, which may cap achievable gains. Future work includes generating more diverse IO examples with LLMs and incorporating even finer feedback (e.g., static analyzers) plus automated error categorization.

## Key Contributions
- Introduces an **online RL framework with an online buffer** that continuously generates and trains on new code samples using the latest policy, improving exploration and stability vs offline RL.
- Proposes **multi-granularity unit-test feedback**: (i) coarse pass/fail/error rewards, (ii) **fine-grained line/global penalization** via parsed compiler exceptions, and (iii) **adaptive pass-rate rewards** for partially correct solutions.
- Achieves **state-of-the-art** results on **APPS** and **MBPP** with CodeT5 770M (and strong gains on CodeGen 2.7B), supported by extensive ablations isolating framework and reward contributions.

## Potential Relevance
RLTF is directly useful if your hypothesis involves **training LLMs with executable feedback**: it provides a concrete recipe for (a) **online data generation** during RL fine-tuning and (b) converting noisy compiler/unit-test outputs into **token-span-level learning signals**. The ablations suggest that **localizing blame (fine-grained penalties)** is particularly impactful, motivating research on automatic fault localization, richer traces, or language-agnostic error taxonomies. The systems workaround (subprocess unit tests to avoid segfault hangs) is also practically relevant for building robust online code-evaluation pipelines.