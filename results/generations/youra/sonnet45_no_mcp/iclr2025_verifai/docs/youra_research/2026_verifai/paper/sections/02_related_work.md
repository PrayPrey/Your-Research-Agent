# Related Work

Our work bridges three research areas: neural theorem proving, uncertainty quantification in neural systems, and resource allocation for automated reasoning. We position our confidence geometry approach relative to these foundations.

## Neural Theorem Proving

Recent advances in neural theorem proving have demonstrated the potential of LLMs to assist in formal mathematics. **LeanDojo** (Yang et al., 2023) introduced a retrieval-augmented neural prover achieving 48.9% success rate on held-out theorems from the Lean mathematical library, establishing a strong baseline for LLM-based tactic suggestion. GPT-f (Polu & Sutskever, 2020) and subsequent work have shown that transformers can learn effective proof search strategies from large corpora of formal proofs. PACT (Han et al., 2022) explored proof artifact co-training to improve generalization.

However, these approaches focus primarily on **what tactic to suggest next** (the forward inference problem) rather than **when to terminate a search** (the meta-reasoning problem). They inherit fixed timeout strategies from symbolic provers, treating resource allocation as an engineering parameter rather than a learnable component. Our work is orthogonal and complementary: confidence-based termination detection can enhance any base prover by improving compute efficiency without modifying the tactic suggestion architecture. We build directly on LeanDojo's infrastructure, using their DojoCritic plugin interface to extract confidence signals, but address a distinct problem they leave unresolved.

## Fixed Timeout Strategies in Automated Reasoning

Traditional automated theorem provers and satisfiability solvers employ non-adaptive timeout strategies. Z3 (de Moura & Bjørner, 2008) uses resource limits based on clause counts and proof depth. Vampire (Kovács & Voronkov, 2013) applies heuristic cutoffs derived from search tree characteristics. These approaches are **theorem-agnostic**: the same timeout applies regardless of problem-specific characteristics, leading to either wasted compute (conservative timeouts) or missed solutions (aggressive cutoffs).

While effective for symbolic reasoning where state spaces have clearer structure, these heuristics fail to leverage the rich semantic information available in neural provers. Our confidence geometry approach is **content-aware**: it adapts termination decisions based on learned patterns in proof space, exploiting the LLM's implicit knowledge of successful proof manifolds. Unlike fixed heuristics that require domain expertise to tune, our detector learns from data what constitutes geometric divergence.

## Uncertainty Quantification and Out-of-Distribution Detection

Confidence calibration in neural networks has been extensively studied for prediction uncertainty (Guo et al., 2017). Methods like temperature scaling and Platt scaling aim to align predicted probabilities with empirical frequencies. However, this work treats confidence primarily as a **calibration metric**—ensuring predicted success rates match actual rates—rather than as a geometric signal for structured reasoning.

Out-of-distribution (OOD) detection methods (Hendrycks & Gimpel, 2017; Liang et al., 2018) use model uncertainty to identify inputs from unseen distributions. Techniques based on maximum softmax probability, ODIN (output distribution calibration), and Mahalanobis distance have shown promise for image and text classification. Yet these methods have not been applied to **sequential decision problems** where confidence trajectories over time carry geometric information about search space navigation.

Our contribution connects these threads: we recognize that in theorem proving, confidence is not merely about prediction accuracy but encodes **implicit geometry**. Entropy variance captures trajectory stability, analogous to how language model perplexity detects distribution shift (Jelinek et al., 1977). By interpreting confidence instability as manifold departure, we reframe termination detection from explicit pattern recognition (which requires training on failures) to geometric deviation detection (which exploits the model's learned familiarity structure).

## Symbolic Divergence Detection

Symbolic theorem provers have long employed divergence detection heuristics. Cycle detection via state hashing identifies when search revisits identical proof states, signaling potential non-termination (Nieuwenhuis & Rubio, 1995). Proof state growth metrics (exponentially increasing term size) flag syntactic explosion. These **structural signals** are orthogonal to neural confidence: they detect syntactic patterns (hash collisions, term expansion) rather than semantic familiarity.

Our hybrid approach strategically combines neural geometric signals (confidence variance) with symbolic structural signals (state collisions). The ablation study reveals an important finding: the **pairwise combination** (confidence + symbolic) achieves F1=0.97, outperforming the 3-signal voting mechanism (F1=0.80) we originally hypothesized. This demonstrates that carefully selected complementary signals outperform exhaustive signal aggregation—a lesson for future neuro-symbolic integration work.

## Positioning and Novelty

No prior work treats proof search resource allocation as a **learnable meta-reasoning problem using LLM confidence geometry**. While LeanDojo revolutionized tactic suggestion and fixed timeouts remain standard practice, the gap between these approaches—adaptive, content-aware termination detection—has remained unfilled. Our confidence geometry principle establishes that neural models implicitly learn geometric structure of successful reasoning spaces, and this structure can be exploited for meta-level decisions without explicit supervision on failure cases.

This principle has implications beyond theorem proving. Any neural search problem with compute constraints—program synthesis (Chen et al., 2021), automated planning, constraint solving—faces similar challenges: when to abandon futile search paths without explicit training on failure patterns. Confidence geometry provides a general framework grounded in the observation that model uncertainty reflects familiarity with training distribution manifolds, offering a path toward learned allocators that generalize across domains.
