# Title: Federated Prompt Distillation: Efficient Knowledge Transfer from Heterogeneous Foundation Models

## Motivation
In practical federated learning scenarios, different clients often have access to different foundation models (e.g., varying sizes of LLaMA, GPT variants, or domain-specific models) due to computational constraints and licensing agreements. Current federated learning approaches assume model homogeneity, making them unsuitable when clients cannot share model architectures or parameters. This heterogeneity barrier prevents effective collaborative learning and knowledge sharing across organizations with diverse FM deployments.

## Main Idea
We propose **Federated Prompt Distillation (FPD)**, a novel framework that enables knowledge sharing across heterogeneous foundation models by operating in the prompt embedding space rather than model parameter space.

**Methodology:**
1. Each client learns task-specific soft prompts for their local foundation model using private data
2. Instead of aggregating model parameters, the server collects prompt-induced output distributions on a small public anchor dataset
3. A universal "meta-prompt generator" network is trained federally to produce effective prompts that capture collective knowledge
4. Clients receive the meta-prompt generator and adapt it to their specific FM architecture through local alignment

**Expected Outcomes:**
- Enable FL across organizations with different proprietary FMs
- Reduce communication costs by 100x compared to parameter-sharing approaches
- Preserve model IP while enabling collaborative improvement

**Impact:**
FPD democratizes federated FM adaptation, allowing smaller organizations with lightweight models to benefit from knowledge learned by participants with larger models, fostering inclusive AI development while maintaining privacy and model ownership.