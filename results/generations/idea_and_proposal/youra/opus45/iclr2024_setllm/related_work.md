## Related Work

**Related Papers**
1. **Title**: RAILS: A Robust Adversarial Immune-inspired Learning System (arXiv:2107.02840)
   - **Authors**: Wang, Chen, Lindsly, Stansbury, Rehemtulla, Rajapakse, Hero
   - **Summary**: Proposes an immune-inspired defense mechanism incorporating B-cell evolution, clonal expansion, and affinity maturation to provide robustness against evolving adversarial attacks in computer vision systems.
   - **Year**: 2022

2. **Title**: Optimization-based Prompt Injection Attack to LLM-as-a-Judge (Semantic Scholar ID: e56f14ced9f7ce344ed14bdcb46860ccac72ac83)
   - **Authors**: Shi et al.
   - **Summary**: Introduces JudgeDeceiver, an attack that defeats perplexity-based and known-answer detection methods, demonstrating the need for representation-level defense mechanisms against prompt injection.
   - **Year**: 2024

3. **Title**: Cognitive Overload Attack: Prompt Injection for Long Context (Semantic Scholar ID: 6d4070ca0ba7ccdedb044c9a15301ad41f6aeb05)
   - **Authors**: Upadhayay et al.
   - **Summary**: Demonstrates a cognitive load exploitation attack achieving 99.99% attack success rate against GPT-4 and Claude-3.5, revealing attention-based vulnerabilities in large language models.
   - **Year**: 2024

4. **Title**: Comparative Benchmarking of Deep Learning Architectures for Detecting Adversarial Attacks on LLMs
   - **Authors**: Kushnerov, Shevchuk, Yevseiev, Karpiński
   - **Summary**: Benchmarks deep learning architectures for adversarial attack detection, finding that character-level BiLSTM achieves perfect robustness (ρ=1.0) and validating representation-level analysis approaches.
   - **Year**: 2026

5. **Title**: SPIN: Self-Supervised Prompt Injection Defense (Semantic Scholar ID: 3a8ae0fe18fd081416b58065c4e618ad28836a4b)
   - **Authors**: Zhou et al.
   - **Summary**: Proposes a self-supervised defense mechanism achieving 87.9% reduction in prompt injection success, though limited to single-vector detection approaches.
   - **Year**: 2024

6. **Title**: NeMo Guardrails / LLM-Guard
   - **Authors**: Not specified
   - **Summary**: Production guardrail systems for LLM security that employ pattern-matching approaches for detecting and preventing malicious inputs.
   - **Year**: Not specified

7. **Title**: Dialogue Injection Attack (Semantic Scholar ID: e998d2b09b2677fb7c76a771ca4253175bc4c3c5)
   - **Authors**: Meng et al.
   - **Summary**: Demonstrates an attack that bypasses six existing defense mechanisms through context manipulation, revealing fundamental weaknesses in current multi-vector defense approaches.
   - **Year**: 2025

8. **Title**: Enhancing Security in IoT Architecture through Defense-in-Depth
   - **Authors**: Onyagu et al.
   - **Summary**: Presents a multi-layer architecture pattern for selective monitoring in IoT security contexts, providing design principles applicable to layered defense systems.
   - **Year**: 2024

**Key Challenges**
1. **Single-Vector Detection Limitations**: Current defense methods like SPIN operate on single-vector approaches, limiting their ability to capture complex, multi-faceted attack patterns.
2. **Perplexity-Based Detection Bypass**: Sophisticated attacks like JudgeDeceiver can defeat perplexity and known-answer detection methods, necessitating representation-level defenses.
3. **Attention-Based Vulnerabilities**: LLMs exhibit fundamental vulnerabilities to cognitive load exploitation attacks that manipulate attention mechanisms in long-context scenarios.
4. **Multi-Vector Defense Failures**: Existing multi-vector defense mechanisms can be systematically bypassed through context manipulation techniques, as demonstrated by dialogue injection attacks.
5. **Static Defense Inadequacy**: Current defenses lack adaptive mechanisms to evolve against novel and evolving adversarial attacks, unlike immune-inspired systems that can adapt over time.
6. **Pattern-Matching Limitations**: Production guardrail systems relying on pattern-matching approaches struggle against sophisticated, semantically-crafted injection attacks.
