## Name

verifier_error_taxonomy_curriculum

## Title

Learning from Formal Failures: Error-Taxonomy-Guided Curriculum Learning for Neural Theorem Proving

## Short Hypothesis

LLM failures in formal theorem proving exhibit systematic, categorizable patterns that can be identified through formal verifier error messages. By constructing a fine-grained taxonomy of these errors (e.g., type mismatches, missing hypotheses, incorrect tactic application, scope violations) and creating targeted synthetic training examples that specifically address each error category, we can achieve more sample-efficient improvements in theorem proving compared to undifferentiated verifier-guided RL. This approach tests whether targeted curriculum learning based on error categories outperforms uniform exposure to verification feedback.

## Related Work

Recent work like Goedel-Prover-V2 and Leanabell-Prover-V2 use verifier feedback for RL training, treating all errors uniformly as negative signals. APOLLO and Hilbert use compiler feedback for proof repair but don't systematically categorize errors. ProofNet++ combines verification with self-correction but doesn't leverage error taxonomies. The closest work is an empirical study on reasoning steps in thinking LLMs (Xue et al., 2025) which develops a 'reasoning-problematic taxonomy' for code generation, but this hasn't been done for formal theorem proving with formal verifier feedback. Our work differs by: (1) systematically categorizing errors using structured verifier messages from Lean/Isabelle, (2) creating targeted synthetic training data for each error category, and (3) evaluating whether error-aware curriculum learning outperforms uniform RL approaches.

## Abstract

Neural theorem provers have made remarkable progress through verifier-guided reinforcement learning, yet current approaches treat all verification failures uniformly, missing opportunities for targeted improvement. We propose Error-Taxonomy-Guided Curriculum Learning (ETCL), a framework that systematically categorizes LLM failures in formal theorem proving using structured error messages from proof assistants like Lean 4. We first construct a comprehensive taxonomy of proof errors by analyzing thousands of failed proof attempts, categorizing them into semantic classes (type errors, missing hypotheses, incorrect lemma application, scope violations, etc.). We then create targeted synthetic training examples for each error category by: (1) taking successful proofs and systematically introducing category-specific errors, (2) pairing these with verifier feedback and corrections, and (3) training models on a curriculum that progressively addresses error categories from most to least frequent. We evaluate ETCL on miniF2F and PutnamBench, comparing against standard verifier-guided RL baselines. Our experiments test whether error-aware training achieves better sample efficiency and final performance than uniform feedback approaches. We also analyze whether models trained with ETCL exhibit more interpretable failure modes and whether the taxonomy transfers across proof domains. This work bridges formal verification and machine learning by demonstrating how structured verification feedback can enable more principled training of neural theorem provers.

## Experiments

**Experiment 1: Error Taxonomy Construction**
- Collect 50,000+ failed proof attempts from a base LLM (e.g., Llama-3-8B fine-tuned on Lean proofs) on mathlib theorems
- Parse Lean 4 error messages and cluster into categories using a combination of regex patterns and LLM-based classification
- Expected categories: type mismatch, unknown identifier, tactic failure (with subcategories), goal mismatch, timeout, syntax errors
- Validate taxonomy with manual annotation of 500 samples
- Metric: Inter-annotator agreement (Cohen's kappa > 0.8)

**Experiment 2: Synthetic Error-Correction Data Generation**
- Take 10,000 successful proofs from mathlib
- For each error category, create perturbation functions that introduce that specific error type
- Generate (incorrect_proof, error_message, correct_proof) triples
- Create 5,000 examples per major error category

**Experiment 3: Curriculum Learning Comparison**
- Baseline 1: Standard SFT on correct proofs only
- Baseline 2: Verifier-guided RL (uniform error signal, similar to Goedel-Prover-V2)
- ETCL-Frequency: Curriculum ordered by error frequency (most common first)
- ETCL-Difficulty: Curriculum ordered by error difficulty (easiest to fix first)
- Train Llama-3-8B variants with each approach using same compute budget
- Metrics: Pass@1, Pass@8, Pass@32 on miniF2F-test and PutnamBench
- Sample efficiency: Performance vs. training steps curves

**Experiment 4: Error-Specific Analysis**
- For each trained model, analyze error distribution on held-out test set
- Test hypothesis: ETCL models show more balanced error distributions (fewer catastrophic failures)
- Measure: Error category distribution shift, reduction in each error type

**Experiment 5: Transfer Analysis**
- Train on mathlib-derived curriculum, test on FVELER (code verification) benchmark
- Evaluate whether error taxonomy transfers across domains

## Risk Factors And Limitations

1. **Taxonomy granularity**: Error categories may be too coarse or too fine-grained; finding the right level of abstraction is challenging. We mitigate by testing multiple granularity levels.

2. **Synthetic data quality**: Artificially introduced errors may not match the distribution of natural LLM errors. We validate by comparing synthetic error distributions to actual LLM failure modes.

3. **Curriculum ordering effects**: The optimal curriculum order is unclear and may be task-dependent. We test multiple orderings and report sensitivity analysis.

4. **Compute constraints**: Training multiple model variants requires significant compute. We use 8B parameter models and limit to 4 main comparisons to stay within academic lab budgets.

5. **Generalization**: The taxonomy may be Lean-specific and not transfer to other proof assistants. We acknowledge this limitation and focus on Lean 4 as the primary testbed.

6. **Baseline strength**: Recent methods like Goedel-Prover-V2 are very strong; improvements may be marginal. We focus on sample efficiency as a key metric where gains are more likely.

