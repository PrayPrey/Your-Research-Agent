# 2. Related Work

## Preference Learning for Language Model Alignment

RLHF emerged as the dominant alignment paradigm through InstructGPT (Ouyang et al., 2022) and Anthropic's Constitutional AI work (Bai et al., 2022). The standard pipeline involves supervised fine-tuning (SFT), reward model training from human preference pairs, and policy optimization via PPO. This approach established the Helpful-Harmless-Honest (HHH) framework as a multi-dimensional alignment target.

Rafailov et al. (2023) introduced DPO as an alternative that bypasses explicit reward modeling. By deriving a closed-form objective from the RLHF optimization problem, DPO directly optimizes the policy from preferences. The original paper demonstrated comparable performance to RLHF on individual benchmarks, motivating the question of whether these methods are functionally equivalent.

## Alignment Evaluation Benchmarks

TruthfulQA (Lin et al., 2022) evaluates model truthfulness using adversarial questions designed to elicit common misconceptions. BIG-bench (Srivastava et al., 2023) provides 200+ tasks including safety-relevant subtasks. The HHH framework evaluates helpfulness and harmlessness dimensions separately.

Prior comparisons between RLHF and DPO have focused on aggregate benchmark performance, finding similar results (Rafailov et al., 2023; Tunstall et al., 2023). Our work differs by examining *cross-benchmark profiles* and *mechanistic signatures* rather than single-benchmark accuracy.

## Optimization Landscape Analysis

The connection between optimization landscape geometry and model behavior remains underexplored in alignment. Work on neural network loss landscapes (Li et al., 2018) suggests that different optimization paths can lead to qualitatively different solutions. We extend this intuition to preference learning, testing whether smooth (RLHF) versus sharp (DPO) preference encoding creates distinct behavioral attractors.

Our work provides the first controlled comparison of RLHF and DPO mechanistic signatures on identical data and model, finding that theoretical differences in training dynamics do not reliably translate to distinct behavioral outcomes at 7B scale.
