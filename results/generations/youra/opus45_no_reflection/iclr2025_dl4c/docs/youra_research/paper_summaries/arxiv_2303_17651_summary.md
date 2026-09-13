---
source_paper: "arxiv_2303_17651.md"
generated_at: "2026-08-18T13:33:10.474770"
model: "openai/gpt-5.2"
summary_chars: 9670
---

# Self-Refine: Iterative Refinement with Self-Feedback

## Key Metadata
- **Authors:** Aman Madaan et al.
- **Year:** 2023
- **Venue:** arXiv (preprint; “Under review”)
- **Core Contribution:** A training-free, test-time algorithm where a *single* LLM alternates between generating *feedback on its own output* and *refining* that output iteratively, improving performance across diverse generation tasks.

## Section Summaries

### Abstract
Like humans, large language models (LLMs) do not always generate the best
output on their first try. Motivated by how humans refine their written text, we
introduce SELF-REFINE, an approach for improving initial outputs from LLMs
through iterative feedback and refinement. The main idea is to generate an initial
output using an LLM; then, the same LLM provides feedback for its output and
uses it to refine itself, iteratively. SELF-REFINE does not require any supervised
training data, additional training, or reinforcement learning, and instead uses a
single LLM as the generator, refiner and the feedback provider. We evaluate
SELF-REFINE across 7 diverse tasks, ranging from dialog response generation
to mathematical reasoning, using state-of-the-art (GPT-3.5 and GPT-4) LLMs.
Across all evaluated tasks, outputs generated with SELF-REFINE are preferred by
humans and automatic metrics over those generated with the same LLM using
conventional one-step generation, improving by ∼20% absolute on average in task
performance. Our work demonstrates that even state-of-the-art LLMs like GPT-4
can be further improved at test-time using our simple, standalone approach.1.

### Introduction & Motivation
LLMs often produce plausible but suboptimal first drafts, especially on tasks with multifaceted objectives (e.g., engaging dialog) or hard-to-specify goals (e.g., code readability). Prior iterative refinement methods frequently require training a separate refinement model and domain-specific supervision, or rely on external reward models/human feedback—both expensive and task-specific. The paper argues that human problem-solving commonly uses *self-feedback* and *iterative revision*, and proposes that LLMs can emulate this at test time. The goal is a general, supervision-free refinement procedure that uses only the base LLM and prompting—no finetuning, no RL.

### Methodology
SELF-REFINE is a **prompt-only, test-time iterative refinement** algorithm that uses a single language model \(M\) in three roles: **generator**, **feedback provider**, and **refiner**. It requires three task prompts: an initial generation prompt \(p_{\text{gen}}\), a feedback prompt \(p_{\text{fb}}\), and a refinement prompt \(p_{\text{refine}}\). Given input \(x\), the model first produces a draft:
\[
y_0 = M(p_{\text{gen}}\|x). \tag{1}
\]
Then for iteration \(t\), the same model critiques its current output \(y_t\) by generating *actionable, specific* natural-language feedback:
\[
fb_t = M(p_{\text{fb}}\|x\|y_t). \tag{2}
\]
Next, it produces a revised output conditioned on the feedback (and optionally the full history):
\[
y_{t+1} = M(p_{\text{refine}}\|x\|y_t\|fb_t), \tag{3}
\]
instantiated in practice with iterative history to avoid repeating mistakes:
\[
y_{t+1} = M(p_{\text{refine}}\|x\|y_0\|fb_0\|\ldots\|y_t\|fb_t). \tag{4}
\]
The loop alternates **FEEDBACK → REFINE** until a **stop condition** triggers (either a fixed iteration cap or a stop indicator parsed from feedback). The evaluation instantiation runs up to **4 iterations**. Prompts are **few-shot**: \(p_{\text{gen}}\) uses \(\langle x^{(k)},y^{(k)}\rangle\); \(p_{\text{fb}}\) uses \(\langle x^{(k)},y^{(k)},fb^{(k)}\rangle\); \(p_{\text{refine}}\) uses \(\langle x^{(k)},y^{(k)}_t,fb^{(k)}_t,y^{(k)}_{t+1}\rangle\). The method is architecture-agnostic (any instruction-/few-shot-capable LLM); experimentally they use GPT-3.5/ChatGPT/GPT-4 (and Codex for code). Decoding is described as “**greedy**” with **temperature \(0.7\)** (as reported), and the same base model is used for both feedback and refinement—no auxiliary critic model.

### Experiments & Results
**Tasks (7):** Dialogue Response Generation (Mehri & Eskenazi, 2020), Code Optimization (Madaan et al., 2023), Code Readability Improvement (Puri et al., 2021), Math Reasoning (GSM8K; Cobbe et al., 2021), Sentiment Reversal (Zhang et al., 2015), and two introduced tasks: Acronym Generation and Constrained Generation (a harder variant of Lin et al., 2020 with **20–30 keyword constraints**). **Dataset sizes and splits** are referenced as being in **Table 4 (Appendix A)** but are not present in the provided excerpt; the main text does not specify counts/splits.

**Base models:** GPT-3.5 (**text-davinci-003**), ChatGPT (**gpt-3.5-turbo**), GPT-4; plus Codex (**code-davinci-002**) on code tasks (Codex numbers deferred to appendix). Comparison is **SELF-REFINE vs. the same LLM** using conventional one-step generation (same prompts, no feedback/refine loop).

**Metrics (3 types):**
1. **Task-specific automatic** when available: Math Reasoning = **% solve rate**; Code Optimization = **% programs optimized**; Constrained Generation = **coverage %**.
2. **Human preference (blind A/B)** for Dialogue, Code Readability, Sentiment Reversal, Acronym Generation.
3. **GPT-4 preference** as proxy judge; reported correlations with human-pref: **82%** (Sentiment Reversal), **68%** (Acronym), **71%** (Dialogue). For Code Readability, GPT-4 is prompted to score fraction of variables appropriately named.

**Main results (Table 1):** consistent gains across tasks and base LLMs (often large absolute improvements).  

| Task | GPT-3.5 Base | GPT-3.5 + SR | ChatGPT Base | ChatGPT + SR | GPT-4 Base | GPT-4 + SR |
|---|---:|---:|---:|---:|---:|---:|
| Sentiment Reversal | 8.8 | 30.4 (↑21.6) | 11.4 | 43.2 (↑31.8) | 3.8 | 36.2 (↑32.4) |
| Dialogue Response | 36.4 | 63.6 (↑27.2) | 40.1 | 59.9 (↑19.8) | 25.4 | 74.6 (↑49.2) |
| Code Optimization | 14.8 | 23.0 (↑8.2) | 23.9 | 27.5 (↑3.6) | 27.3 | 36.0 (↑8.7) |
| Code Readability | 37.4 | 51.3 (↑13.9) | 27.7 | 63.1 (↑35.4) | 27.4 | 56.2 (↑28.8) |
| Math Reasoning | 64.1 | 64.1 (0) | 74.8 | 75.0 (↑0.2) | 92.9 | 93.1 (↑0.2) |
| Acronym Generation | 41.6 | 56.4 (↑14.8) | 27.2 | 37.2 (↑10.0) | 30.4 | 56.0 (↑25.6) |
| Constrained Generation | 28.0 | 37.0 (↑9.0) | 44.0 | 67.0 (↑23.0) | 15.0 | 45.0 (↑30.0) |

**Ablations / analysis:**
- **Feedback quality matters (Table 2):** replacing actionable feedback with generic feedback reduces scores; removing feedback hurts more (e.g., Sentiment Reversal: **43.2 → 31.2 → 0** for SELF-REFINE feedback → generic → no feedback; Acronym: **56.4 → 54.0 → 48.0**; Code Opt: **27.5 → 26.0 → 24.8**).
- **More iterations help with diminishing returns (Figure 4):** e.g., Code Opt \(y_0=22.0 \to y_3=28.8\); Sentiment Rev \(33.9 \to 36.8\); Constrained Gen \(29.0 \to 49.7\).
- **Not just “more samples”:** SELF-REFINE beats **\(k=4\)** independent samples from ChatGPT in human preference (1-vs-\(k\) comparison; details in appendix).
- **Failure mode diagnosis:** in manual analysis (70 samples across Code Opt + Math), failures mostly stem from **bad feedback** (33% wrong location; 61% wrong fix) vs only **6%** from refiner failing to apply good feedback.
- **Weaker model (Vicuna-13B):** struggles to follow the required feedback/refine formats; often repeats outputs or derails (suggesting SELF-REFINE relies on strong instruction/few-shot capability).
**Compute / cost:** GPU hours, latency, and token overhead are not reported in the provided excerpt; however, the method necessarily increases inference cost roughly proportional to the number of feedback+refine iterations (up to 4).

### Discussion & Conclusion
SELF-REFINE shows that substantial test-time improvements are achievable by prompting a single strong LLM to critique and revise its own outputs, without any parameter updates. Gains are largest on preference/constraint-heavy generation, while math reasoning improves only marginally because the model often fails to detect subtle errors (“everything looks good”). Limitations include reliance on strong proprietary instruction-tuned models, English-only evaluation, and the possibility that iterative prompting could be misused to steer toward harmful outputs.

## Key Contributions
- Introduces **SELF-REFINE**, a **training-free**, **single-LLM** iterative algorithm alternating **FEEDBACK** and **REFINE** steps, formalized by Eqs. (1)–(4) and Algorithm 1.
- Demonstrates broad empirical gains across **7 tasks** and multiple state-of-the-art LLMs (GPT-3.5, ChatGPT, GPT-4; plus Codex for code), with large absolute improvements in several human-/GPT-4-preference settings (e.g., Dialogue with GPT-4: **25.4 → 74.6**).
- Provides analysis showing that improvements come from **actionable self-feedback** and **iterative revision** (not merely sampling more outputs), and characterizes failure modes as primarily due to **incorrect feedback**.

## Potential Relevance
For hypothesis development, SELF-REFINE is a strong baseline for **test-time scaling via deliberation**: it isolates gains achievable purely by *structured self-critique* without training or external reward models. Its ablations suggest a key research lever is **feedback accuracy/grounding** (especially for math/program correctness), motivating hybrids that add verifiers, tool feedback, or uncertainty-aware stopping criteria. The weak-model failure (Vicuna-13B) also highlights a capability threshold: iterative self-refinement may require explicit instruction-following and format adherence, suggesting new training objectives or decoding constraints to enable SELF-REFINE-like loops in smaller/open models.