# Introduction

Hallucination detection has become synonymous with generation overhead. SelfCheckGPT [Manakul et al., 2023] samples multiple LLM outputs to check consistency; chain-of-thought verification prompts the model to reason about its own claims; verbalized confidence elicitation asks the LLM to self-assess reliability. Each approach requires the model itself at inference time, creating a structural tension: the systems most prone to hallucination are the most expensive to monitor. We ask the opposite question — does the information needed to detect hallucinations already exist in a single forward pass of a frozen, off-the-shelf NLI classifier?

## The Problem: Three Levels Deep

**On the surface**, large language models hallucinate — generating plausible-sounding but factually incorrect or unsupported content with troubling frequency [Li et al., 2023]. For dialogue systems, QA assistants, and summarization pipelines deployed in production, reliable hallucination detection is a prerequisite for safe use.

**At a deeper level**, existing detection methods are architecturally coupled to LLM generation. SelfCheckGPT requires multiple stochastic samples; P(True) and verbalized confidence require instruction-following capabilities that vary by model and version [Kadavath et al., 2022]; probing classifiers require white-box access to internal states. This generation dependency creates a practical bottleneck: detection latency scales with LLM inference cost, rendering real-time monitoring economically prohibitive for high-throughput deployments.

**The gap in the literature** is more specific than it appears. Post-hoc, generation-free approaches using NLI models — notably SummaC [Laban et al., 2022] and TRUE [Honovich et al., 2022] — have demonstrated that DeBERTa-scale NLI classifiers can detect factual inconsistency between text pairs without any generation. Yet no prior work has: (1) established AUROC baselines for frozen NLI applied directly to HaluEval across all three task types; (2) characterized which NLI framing strategy (contradiction score, entailment negation, or net-contradiction) maximizes hallucination detection signal; or (3) identified *why* NLI-based detection works for some task types but fails structurally for others. The empirical question — can a frozen NLI model, used post-hoc on existing text pairs, detect hallucinations well enough to matter — remains unanswered.

## The Key Insight

NLI models trained to detect textual contradiction are, by design, detectors of *commission-type* hallucinations: fabricated facts, invented entities, and factual substitutions that directly contradict the grounding context. This alignment is architecturally deep, encoded in DeBERTa's MNLI training objective. It holds for commission-dominated tasks — dialogue (AUROC = 0.709) and QA (AUROC = 0.644) — but breaks structurally for summarization (AUROC = 0.530, near chance), where hallucinations are primarily *omissions*: text that fails to capture the source document's meaning without explicitly contradicting it. The commission/omission boundary is not a performance artifact; it is a principled architectural constraint that determines when and why NLI-based detection is viable.

## Contributions

This paper presents a systematic empirical and mechanistic study of generation-free post-hoc NLI hallucination detection on HaluEval [Li et al., 2023], yielding three contributions:

**1. Existence: NLI detection signal on HaluEval.** We establish, for the first time, AUROC baselines for frozen DeBERTa-v3-large NLI applied post-hoc to all three HaluEval task types (dialogue, QA, summarization). The approach achieves AUROC = 0.709 on dialogue and 0.644 on QA — outperforming generation-based SelfCheckGPT-NLI (0.48 and 0.53 respectively) without a single token of LLM generation at inference time. The method requires only a frozen NLI classifier and pre-existing (context, response) pairs.

**2. Mechanism: Graded support sensitivity confirmed.** We characterize the underlying mechanism via statistical analysis of pre-computed contradiction scores across 60,000 pairs. Wilcoxon rank-sum tests confirm that DeBERTa's scores monotonically track hallucination probability on all three tasks (p ≈ 0 on dialogue, p = 1.52e-271 on QA, p = 2.07e-13 on summarization), with large effect sizes on commission tasks (Cohen's d = 0.714 and 0.779). The mechanism is real, not artifactual.

**3. Boundary: The commission/omission structural limit.** We identify and explain why NLI-based detection fails on summarization: abstractive summarization hallucinations are predominantly omissions, architecturally outside the scope of contradiction-based detection. This commission/omission boundary unifies prior task-level observations in SummaC and TRUE under a single principled framework, guiding the design of future hybrid detectors.

The paper is organized as follows. Section 2 surveys related work on hallucination detection and NLI-based factual consistency. Section 3 describes the methodology. Sections 4 and 5 present experimental setup and results. Section 6 discusses implications. Section 7 concludes.
