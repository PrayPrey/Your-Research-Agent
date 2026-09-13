# Research Idea

## Title
Code-Switching Augmented Safety Alignment: Learning Language-Invariant Safety Representations for Multilingual LLMs

## Motivation
Current LLM safety mechanisms exhibit critical vulnerabilities when users employ code-switching—mixing languages within prompts—achieving 46.7% higher attack success rates than monolingual attacks. This disparity disproportionately affects low-resource language speakers and creates exploitable security gaps. Existing safety training relies predominantly on English data, failing to generalize across linguistic variations. This research addresses the urgent need for equitable, robust multilingual safety alignment.

## Main Idea
We propose Code-Switching Augmented Safety Alignment (CSASA), which applies linguistically-principled code-switching augmentation during safety training to develop language-invariant safety representations. The core mechanism operates through three steps: (1) generating code-switched training data following sociolinguistic patterns (inter-sentential, intra-sentential, tag-switching) across five strategic language pairs; (2) applying contrastive learning that forces the safety encoder to recognize semantic intent across diverse surface forms; (3) producing language-invariant embeddings that transfer safety knowledge cross-lingually.

We will compare CSASA against English-only and random code-switching baselines, measuring attack success rates on the CSRT benchmark, safety classification F1 on multilingual benchmarks, and cross-lingual transfer gaps. Expected outcomes include ≥30% reduction in code-switching attack success and ≥40% improvement in low-resource language safety, while maintaining low false refusal rates. This approach offers a practical, training-time intervention for equitable multilingual LLM safety.