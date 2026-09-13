# 1. Introduction

Large language models can now generate code that passes functional tests 90% of the time [1,2], yet formal verification—the gold standard for correctness—remains out of reach. When automated verifiers reject specifications for failing to prove safety or functional properties, current approaches typically discard the specification and regenerate from scratch, ignoring the rich semantic signal encoded in verifier feedback that could guide systematic refinement.

This limitation creates a bottleneck in deploying formal verification to safety-critical systems. Formal specifications provide mathematical correctness guarantees essential for medical devices, aerospace control systems, and cryptographic implementations, but synthesizing specifications that verify requires expert verification engineers—a skillset rarer than software developers. Without automated specification synthesis, formal verification cannot scale to meet the growing demand for provably correct software in AI-enabled safety-critical applications.

The challenge is not simply that LLMs struggle with formal reasoning. Rather, when verification fails, the semantic information in failure feedback is discarded rather than used to guide refinement. Prior work treats verification as a binary pass/fail oracle [3,4], missing the opportunity to extract structured learning signals from proof failures. A failed proof obligation contains rich information: witness counterexamples showing *where* specifications fail, proof obligation structures revealing *what* needs proving, and dependency chains indicating *why* proofs fail. Yet this multi-dimensional semantic signal is either

 discarded entirely or presented to LLMs as unstructured natural language.

**Our Key Insight:** Verifier feedback provides a *semantic gradient* for specification synthesis. By decomposing feedback into three informational dimensions—Witness Instantiation (concrete counterexamples), Logical Structure (proof obligation categories), and Dependency Preservation (causal chains)—we encode complementary semantic constraints that guide LLMs toward valid specifications via localized, targeted edits rather than global regeneration.

We demonstrate this insight through experiments validating an information-theoretic framework for verification-in-loop. Our contributions are:

1. **Information-theoretic decomposition of verifier feedback:** We formalize three feedback dimensions and quantify their additive information value through empirical validation. Across four feedback conditions (RawError baseline, TagOnly, ObligationSlice, FullStructured), discharge rates scale monotonically from 31.9% to 70.1% with a linear information gradient (β=12.49, R²=0.89, p<10⁻⁵⁰). Each dimension contributes 10-15pp independently, demonstrating non-redundant semantic constraints.

2. **Cross-verifier semantic normalization via minimal taxonomy:** We introduce an 8-primitive taxonomy achieving 100% error category coverage across Frama-C, Dafny, and Why3. This enables cross-verifier transfer with 84.9% performance retention (15.1% degradation), validating that verifiers share a semantic core despite syntactic differences.

3. **Causal evidence via compute-matched control:** Through controlled experiments isolating feedback quality from computational budget, we demonstrate that structured feedback drives systematic improvement beyond naive scaling. Under equal token budgets and verifier time, iterative feedback achieves 71.4% discharge vs. 60.8% for self-consistency sampling (10.7pp gap, p<0.0001, Cohen's d=7.10).

4. **Validation of non-vacuous specification strength:** Mutation testing demonstrates synthesized specifications achieve 63.3% mutation kill rate—105% of expert-written gold baseline (60%)—validating semantic meaningfulness beyond trivial "spec washing."

These contributions reframe verification-in-loop from an empirical observation [5] to a principled information-theoretic framework, providing quantitative basis for feedback design and cross-tool generalization. We validate our approach through comprehensive ablation studies isolating causal mechanisms and characterizing scope boundaries.

The remainder of this paper is organized as follows: Section 2 reviews related work in verification-in-loop, LLM-guided formal methods, and error taxonomies. Section 3 describes our three-dimensional feedback decomposition and 8-primitive semantic normalization layer. Section 4 details our experimental design testing five predictions about iterative refinement, information gradients, cross-verifier portability, non-vacuity, and causal mechanisms. Section 5 presents empirical results. Section 6 discusses interpretation, limitations, and broader impact. Section 7 concludes with future directions.
