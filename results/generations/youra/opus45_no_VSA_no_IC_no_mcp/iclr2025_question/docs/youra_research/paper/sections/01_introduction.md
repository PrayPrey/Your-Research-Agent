# Introduction

On 18% of factuality questions, token entropy and answer consistency point in opposite directions—and each method is right about its own subset. This counterintuitive finding reveals that current uncertainty quantification approaches for detecting hallucinations capture fundamentally different failure modes, suggesting that relying on any single signal leaves a substantial fraction of errors undetected.

Large language models (LLMs) generate fluent text that can be factually incorrect, a phenomenon termed *hallucination*. Detecting hallucinations before deployment is critical for high-stakes applications such as medical diagnosis, legal advice, and scientific research. Two prominent approaches have emerged: entropy-based methods that measure uncertainty in the model's token probability distribution, and consistency-based methods that measure agreement across multiple sampled responses.

The deeper problem is that these approaches have been developed and evaluated independently. Kuhn et al. (2023) introduced semantic entropy for natural language generation tasks, while Manakul et al. (2023) developed SelfCheckGPT for consistency-based detection on biography generation. Neither work directly compared these methods on the same factuality benchmark with the same model. This leaves a critical gap: we do not know whether entropy and consistency capture redundant information or complementary signals.

Our key insight is that token entropy and N-sample consistency capture orthogonal uncertainty signals. Entropy reflects *epistemic uncertainty*—diffuse logit distributions when the model lacks knowledge about the answer. Consistency reflects *generation stability*—whether the model's sampling process produces semantically similar answers across multiple runs. When these signals disagree, each detects a different type of hallucination: knowledge gaps versus generation artifacts.

We demonstrate this empirically on TruthfulQA with LLaMA-2-7B. The correlation between entropy and consistency scores is only r = 0.228 (sharing just 5% of variance), confirming orthogonality. For consistency, correct answers score significantly higher than incorrect answers (Cohen's d = 1.068, exceeding our threshold by 5×). Most strikingly, on the 18.1% of questions where the methods disagree substantially, each achieves AUROC > 0.75 on its "winning" subset—demonstrating genuine complementary detection capability.

Our contributions are:

1. **First systematic comparison** of entropy and consistency methods on the same factuality benchmark (TruthfulQA) with the same model (LLaMA-2-7B), establishing a fair comparison baseline.

2. **Empirical demonstration of orthogonality** (r = 0.228), showing these methods measure fundamentally different phenomena with only 5% shared variance.

3. **Complementarity analysis framework** showing that 18.1% of questions exhibit method disagreement, with each method achieving AUROC > 0.75 on its winning subset.

4. **Mechanistic interpretation** connecting entropy to epistemic uncertainty and consistency to generation stability, providing theoretical grounding for multi-signal approaches.

These findings motivate combining both signals for more robust hallucination detection. We organize the remainder as follows: Section 2 surveys related work on uncertainty quantification for LLMs; Section 3 describes our methodology; Section 4 presents experimental setup; Section 5 reports results; Section 6 discusses implications and limitations; Section 7 concludes.
