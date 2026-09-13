## Title
Disentangling Task Structure from Architectural Bias in Representation Convergence through Controlled Synthetic Environments

## Motivation
While we observe that different neural models learn similar representations, a fundamental question remains unresolved: **what drives this convergence—the inherent structure of the task or the inductive biases shared across architectures?** Understanding this distinction is critical for: (1) predicting when models will naturally align, (2) designing architectures that accelerate convergence to optimal representations, and (3) identifying truly task-essential features versus architectural artifacts. This knowledge would directly inform model merging strategies and improve our understanding of biological-artificial correspondence.

## Main Idea
I propose creating a systematic framework using **parametrically controlled synthetic tasks** where task complexity, symmetries, and statistical structure can be precisely manipulated. Train diverse architectures (CNNs, Transformers, MLPs, RNNs) on these tasks while varying:
- Task properties: compositionality, hierarchical structure, required invariances
- Architectural constraints: capacity, inductive biases, initialization schemes

Apply representational similarity analysis (CKA, SVCCA) to quantify convergence across conditions. Use **ablation studies** to isolate which task properties necessitate specific representational structures versus which emerge from architectural convenience. Develop **predictive models** that forecast representation similarity given task and architecture specifications. Expected outcome: a taxonomy mapping task properties to representation convergence patterns, enabling principled model stitching and revealing universal versus contingent features in learned representations.