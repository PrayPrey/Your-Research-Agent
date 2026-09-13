# Introduction

Large language models confidently produce both correct answers and plausible-sounding fabrications—and their output probabilities cannot reliably distinguish between the two. This disconnect between model confidence and factual accuracy undermines deployment in high-stakes domains where users depend on trustworthy responses.

**The surface problem.** When a user asks a factual question, the model may respond with high token probability yet be entirely wrong. Studies of LLM hallucination reveal that output confidence correlates weakly with correctness: token entropy achieves only ~0.62 AUROC for distinguishing correct from incorrect answers on standard QA benchmarks.

**The deeper problem.** Multi-sample approaches like semantic entropy improve detection by sampling multiple responses and measuring semantic clustering. These methods achieve ~0.80 AUROC but require 5–20 forward passes per question—a 5–20× compute overhead that precludes real-time deployment at scale.

**The gap.** No efficient single-pass method matches multi-sample accuracy. Output-level metrics are cheap but weak; semantic entropy is strong but expensive. Is there a middle ground?

**Our insight.** We hypothesize that transformer hidden states encode a *knowledge confidence* signal distinct from output-level token confidence. Middle-layer representations capture semantic content before task-specific output formatting compresses this information for next-token prediction. A simple linear probe can extract this signal in a single forward pass.

**Results preview.** We train a logistic regression probe on middle-layer (50–60% depth) hidden states from Llama-3-8B-Instruct and achieve **0.885 AUROC** for factual correctness prediction on TriviaQA—exceeding token entropy by **+26 AUROC points** with no additional sampling. Systematic layer sweeps reveal an inverted-U pattern: middle layers outperform both early layers (insufficient semantic content) and final layers (output formatting dominates).

**Contributions.** 
1. We demonstrate that hidden states predict factual correctness directly, bypassing uncertainty estimation as an intermediate step.
2. We identify optimal extraction at 50–60% model depth through systematic evaluation across all 32 layers.
3. We achieve semantic-entropy-comparable accuracy (0.88 vs ~0.80) with single-pass efficiency, enabling practical deployment.

The central question we address: *What does the model know about what it knows?* Our findings suggest the model's internal representations contain richer information about factual accuracy than its output distributions reveal—and this information is accessible with minimal computational overhead.
