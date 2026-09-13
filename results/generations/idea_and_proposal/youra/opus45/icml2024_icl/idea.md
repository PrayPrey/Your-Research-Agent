# Research Idea

## Title
Developmental Transition of In-Context Learning Mechanisms: From Induction Heads to Function Vector Heads Across Model Scale

## Motivation
Understanding *how* transformers perform in-context learning (ICL) remains a fundamental open question. Prior work presents an apparent contradiction: Olsson et al. (2022) identified induction heads as the primary ICL mechanism, while Yin & Steinhardt (2025) found function vector (FV) heads dominate in larger models. This tension suggests a scale-dependent mechanism transition that has not been systematically characterized. Resolving this would unify competing theories and provide actionable insights for designing more efficient ICL-capable architectures.

## Main Idea
We hypothesize that ICL mechanisms undergo a developmental transition: as model scale increases from 100M to 7B parameters, the dominant mechanism shifts from induction heads (surface-level pattern matching) to function vector heads (abstract task encoding). This occurs because increased capacity enables more abstract representations, with FV heads emerging from induction head scaffolds during training.

**Methodology:** Using TransformerLens, we will systematically ablate induction and FV heads across five model scales (100M-7B) on standardized ICL benchmarks, measuring each mechanism's contribution via accuracy degradation.

**Key Predictions:** (1) FV/IH contribution ratio increases monotonically with scale (ρ > 0.8); (2) A crossover point exists between 500M-3B parameters where FV contribution exceeds IH.

**Impact:** This mechanistic understanding could guide efficient architecture design and training strategies for ICL capabilities.