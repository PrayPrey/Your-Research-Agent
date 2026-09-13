# Introduction

When LLM-generated code fails a test, conventional wisdom suggests that providing detailed error information—the exception type, error message, and exact line number—should help the model fix it. After all, human programmers benefit from precise error localization. We find the opposite: for CodeLlama-7B-Instruct repairing Python code, telling it simply "the test failed" yields 41.8% repair success, while providing the exact error line and message drops success to 16.8%—a 25 percentage point degradation.

This counterintuitive result challenges a fundamental assumption underlying LLM-based debugging tools. Systems like Self-Debug [Chen et al., 2023], TraceFixer [Bouzenia et al., 2024], and DynaFix [Huang et al., 2025] all provide detailed execution feedback to guide repair, implicitly assuming that more information enables better reasoning. Our controlled study reveals that this assumption may be wrong, at least for smaller instruction-tuned models. The implications extend to deployed coding assistants: if detailed error feedback actively hurts repair rates, current tools may need to adapt their feedback strategies based on model scale.

## The Error Feedback Granularity Problem

The challenge of LLM code repair is well-established. When generated code fails tests, models can attempt iterative refinement using execution feedback [Chen et al., 2023]. This approach has shown promise: Self-Debug improves MBPP benchmark performance by 12% using "rubber duck debugging" with error messages. However, this surface-level success obscures a deeper design question.

Existing approaches treat feedback granularity as an implementation detail rather than a design choice. Self-Debug uses error messages (G2-level feedback), TraceFixer uses full stack traces (G4-level), and DynaFix adds variable states (G4+ level). None systematically compare these choices. The implicit assumption is that more detailed feedback provides more useful signal—a reasonable intuition that turns out to be empirically wrong.

The gap we address is fundamental: **no prior work has conducted a controlled comparison of error feedback granularity levels for LLM code repair**. Without such comparison, the field cannot determine optimal feedback strategies, and tools may unknowingly operate at suboptimal configurations.

## Key Insight: Less Information, Better Repair

Our investigation reveals a surprising pattern. We defined five granularity levels spanning the full feedback spectrum:

- **G0**: Pass/fail only ("Test failed")
- **G1**: Error type ("Test failed: IndexError")
- **G2**: Error + message ("IndexError: list index out of range")
- **G3**: Error + line ("IndexError at line 7: list index out of range")
- **G4**: Full stack trace with context

We hypothesized that intermediate granularity (G3) would be optimal—providing a "pointer" to the bug without overwhelming the model with irrelevant trace details. This "attention window hypothesis" predicted a non-monotonic relationship with peak performance at G3.

The data told a different story. Repair success rates cluster into two distinct groups: **minimal feedback (G0, G1) achieves ~41% success**, while **detailed feedback (G2, G3, G4) achieves only 17-23%**. The transition happens sharply at the G1→G2 boundary—the moment we include the error message, performance drops by approximately 20 percentage points.

This pattern suggests that detailed error feedback may cause **cognitive interference** rather than helpful localization. The model appears to work better when reasoning about correctness globally rather than anchoring on specific error details. At the 7B parameter scale, the capacity to productively leverage detailed feedback may simply not exist.

## Contributions

Building on this insight, we make the following contributions:

**First**, we present the first systematic comparison of error feedback granularity (G0-G4) for LLM code repair, using a controlled experimental design where granularity is the only variable that changes across conditions.

**Second**, we provide strong statistical evidence (ANOVA F=23.89, p < 10⁻¹⁸) that granularity significantly affects repair success—but in the opposite direction predicted by conventional wisdom. Simpler feedback dramatically outperforms detailed feedback at the 7B scale.

**Third**, we discover a two-cluster pattern with a threshold effect at the G1→G2 boundary, suggesting that the transition from "what failed" to "how it failed" introduces harmful information for smaller models.

**Fourth**, we establish a methodological framework for granularity comparison experiments that future work can extend to larger models, alternative templates, and different benchmarks.

These findings have immediate practical implications: LLM coding assistants should consider adaptive feedback strategies that match granularity to model capacity, rather than assuming detailed feedback is universally beneficial.

The remainder of this paper proceeds as follows. Section 2 reviews related work on LLM code repair and execution feedback. Section 3 describes our experimental methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes with future directions.
