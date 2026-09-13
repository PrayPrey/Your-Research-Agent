# Introduction

Not all execution feedback is created equal: fine-grained rewards that pinpoint the exact error location can backfire when that localization is unreliable. This counterintuitive observation motivates our work on error-type-gated feedback for reinforcement learning (RL) fine-tuning of code language models.

## Background

Recent advances in RL fine-tuning have enabled code LLMs to improve through execution feedback. Methods like CodeRL and RLTF leverage program execution outcomes to provide reward signals, with RLTF demonstrating that combining coarse (pass/fail) and fine-grained (token-level) feedback outperforms single-signal approaches. VeRPO further showed that how feedback is aggregated matters—cardinality bias in dense rewards can degrade performance. These findings establish that feedback granularity and aggregation strategy are critical design choices.

## The Problem

However, existing methods apply fine-grained feedback uniformly, regardless of whether the error localization is reliable. When a Python program raises a SyntaxError, the traceback points to the exact buggy token. But when it raises a RuntimeError—say, due to a mishandled edge case—the traceback often points to a symptom line far from the root cause. Applying token-level reward penalties at such misleading locations injects noise into gradient updates: the model receives credit assignment signals at wrong tokens, potentially learning incorrect corrections.

## Key Insight

We observe that Python exception types naturally partition into two categories with dramatically different localization reliability. U_line errors (SyntaxError, NameError, TypeError, etc.) have 100% traceback accuracy—the reported line matches the actual bug location. U_ignore errors (RuntimeError, RecursionError, MemoryError, etc.) have only 20% accuracy—tracebacks point to symptom locations. This 80-percentage-point gap, which we measure empirically (chi-square p=9.57×10⁻⁷⁴), suggests that conditioning feedback strategy on error type could substantially reduce gradient noise.

## Our Approach

We propose error-type-gated fine-grained feedback: apply token-level penalties only for errors where localization is reliable (U_line category), while falling back to coarse-only feedback for unreliably-localized errors (U_ignore category). This simple modification preserves the benefits of fine-grained credit assignment where it is accurate while avoiding noise injection where it would be misleading.

## Contributions

Through a systematic verification pipeline, we establish the causal mechanism underlying this approach. We first confirm that fine-grained penalties do concentrate gradients at traceback locations (16.11× concentration ratio). We then demonstrate that this localization varies dramatically by error type (100% vs 20% accuracy). We show that unreliable localization causes measurable gradient noise at ground-truth locations (p<10⁻¹³). Finally, we demonstrate that gating improves signal-to-noise ratio (+4.61%) and training efficiency (gated condition reaches 30% pass@1 while baseline does not).

Our work introduces credit assignment reliability as a lens for understanding feedback granularity in code RL, providing both theoretical framing and empirical validation for error-type-aware training strategies.
