# Related Work

Prior work has studied verification strategies for LLM code generation in isolation. We review three streams—grammar-constrained decoding, static analysis feedback, and SMT-guided repair—and identify the gap our work addresses.

## Grammar-Constrained Decoding

Grammar-constrained decoding enforces syntactic validity during generation by masking logits that would produce invalid tokens. Mündler et al. (2025) introduced type-constrained decoding using prefix automata, reducing compilation errors by over 50% on HumanEval and MBPP. SynCode (Qu et al., 2025) extends this to general-purpose programming languages with soundness and completeness guarantees. CRANE (Banerjee et al., 2025) adds reasoning augmentation to constrained decoding, achieving 10% accuracy improvement on GSM-symbolic and FOLIO.

These approaches operate at the token level during generation, preventing syntax errors before they occur. However, they do not address semantic issues (security vulnerabilities, type confusion) or specification violations. Our work tests whether grammar constraints target an independent error class from semantic verification.

## Static Analysis Feedback Loops

Post-generation static analysis identifies semantic patterns that grammar constraints cannot catch. Blyth et al. (2025) demonstrated that static analysis-driven prompting reduces security issues from over 40% to 13% and reliability issues from over 50% to 11% on PythonSecurityEval. PropertyGPT (Liu et al., 2024) combines retrieval-augmented generation with static analysis feedback for smart contract property generation, achieving 80% recall and detecting 26 CVEs.

These approaches rely on the LLM using feedback to repair code. Blyth et al. used instruction-tuned models; our experiments reveal that completion models cannot use such feedback productively—a critical prerequisite not previously documented.

## SMT-Guided Repair

SMT-guided approaches enforce formal specification satisfaction. ContractEval (Lim et al., 2025) demonstrated that SMT solver integration achieves 75-82% pass@1 on contract-satisfying assertions, compared to 0% with standard prompting. Classical SMT-based repair tools like Nopol (SpoonLabs) and Angelix (Mechtaev et al.) target human-written buggy code using Z3 constraint solving.

Hybrid approaches combining LLMs with SMT solvers are emerging. Holey (Namin et al.) uses Z3/CVC5 with LLMs for hole-filling program synthesis. However, these focus on specification satisfaction for problems with formal contracts—a subset of code generation benchmarks.

## Gap in Existing Work

Each strategy stream has demonstrated effectiveness in isolation, but on different benchmarks with different metrics:

- Grammar constraints: HumanEval/MBPP with compilation rate
- Static analysis: PythonSecurityEval with security/reliability metrics  
- SMT-guided: ContractEval with contract satisfaction

No existing work compares all three strategies on identical benchmarks with consistent metrics. More fundamentally, no prior work measures whether these strategies target independent error classes (enabling multiplicative gains) or overlapping classes (diminishing returns).

We address this gap by measuring pairwise Jaccard indices on improvement sets across HumanEval, revealing that error classes are largely independent—but that translating this independence into combined improvement requires matching model capability to verification stage requirements.
