# Title
Federated Prompt Evolution: Privacy-Preserving Adaptive Prompt Optimization for Heterogeneous Foundation Models

# Motivation
Fine-tuning foundation models in federated settings faces a critical challenge: clients often have heterogeneous model versions, computational constraints, and diverse data distributions. Traditional federated fine-tuning approaches require sharing model updates or adapters, which can be computationally expensive and still pose privacy risks. Prompt tuning offers a lightweight alternative, but current federated prompt learning methods assume homogeneous models and fail to adapt to client-specific contexts while maintaining global knowledge.

# Main Idea
We propose a federated prompt evolution framework that learns optimal prompts across heterogeneous clients without sharing sensitive model parameters or data. The methodology consists of:

1. **Local Prompt Adaptation**: Each client maintains a compact prompt embedding optimized on local data, treating the foundation model as a frozen black box.

2. **Evolutionary Aggregation**: Instead of averaging prompts directly, we employ a meta-learning approach where the server learns a prompt generator that produces client-specific initialization prompts based on metadata (e.g., domain type, model version) without accessing raw data.

3. **Cross-Model Knowledge Transfer**: Using a distillation-based approach, prompts learned on different model versions are made compatible through a shared semantic space.

**Expected outcomes**: Reduced communication costs (only prompts transferred), improved personalization, and compatibility across model versions. This enables practical FL deployment where clients use different foundation model variants while preserving privacy and achieving superior task performance compared to centralized prompt tuning.