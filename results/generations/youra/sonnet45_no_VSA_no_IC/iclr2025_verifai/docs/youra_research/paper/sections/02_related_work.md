# Related Work

Our mechanistic attribution approach builds on three research threads: LLM-guided theorem proving systems, evaluation benchmarks, and hybrid architectures. We position our work as complementary to these efforts — prior work establishes *that* LLMs succeed and *how much* they succeed, while we quantify *why* they succeed through controlled ablation.

## LLM-Guided Theorem Proving Systems

**DeepSeek-Prover-V2** (2025) achieves state-of-the-art 88.9% success on miniF2F-test through large-scale pretraining on formal mathematics corpora and Monte Carlo tree search. **AlphaProof** (DeepMind, 2024) reaches IMO medal-level performance by combining informal problem statements with multi-step proof search. **LeanCopilot** integrates LLMs into the Lean proof assistant, enabling tactic suggestions from natural language goals. These systems demonstrate LLM effectiveness but do not isolate which mechanisms (NL understanding, proof search, corpus learning) drive their advantage.

Our NL ablation (§4.2) provides mechanistic evidence for why these systems succeed: the 29.5pp contribution from NL hints explains AlphaProof's reliance on informal problem statements and LeanCopilot's tactic suggestion accuracy. Where prior work optimizes architectures to maximize success rates, we decompose the advantage into testable mechanisms.

## Theorem Proving Benchmarks

**MiniF2F** (Zheng et al., 2021) provides 488 Olympiad-level problems across Lean, Isabelle, and Metamath, establishing a standard evaluation benchmark. **FIMO** and **PutnamBench** extend coverage to IMO and undergraduate-level mathematics. These benchmarks report LLM success rates (65-89%) but lack baselines for pure automated provers, making mechanistic comparisons impossible.

Our contribution: we establish the first measured lean-auto baseline on miniF2F Lean 4 subset (15.6% [11.5%, 20.3%], N=244), quantify the 50pp LLM gap, and attribute 60% to NL understanding. This baseline enables future controlled studies of architectural innovations (e.g., "does longer context improve depth performance?" requires depth mechanism validation, which we reject at <8%).

## Hybrid LLM+Prover Systems

**Thor** (Jiang et al., 2022) combines LLMs with automated hammers (Sledgehammer in Isabelle), reporting 57.0% total success with 8.2% unique hybrid solutions (neither LLM nor hammer alone). This synergy suggests complementary strengths but does not explain *when* each component succeeds. **Baldur** (First et al., 2023) uses LLMs to repair hammer-generated proof sketches in Isabelle. **COPRA** (Sanchez-Stern et al., 2023) learns proof repair in Coq.

Our mechanistic attribution provides a routing hypothesis for hybrid systems: LLMs exploit NL hints (60% advantage) while automated provers provide deterministic formal reasoning. Thor's 8.2% unique solutions likely arise from problems with rich NL context (LLM strength) requiring reliable premise selection (hammer strength). Future hybrid designs should route NL-rich problems to LLMs and formal-only goals to automated provers, a strategy our ablation validates.

## Mechanistic Interpretability in Formal Methods

Prior work in neural theorem proving focuses on *improving* LLM performance rather than *explaining* it. **Polu et al. (2022)** scale expert iteration on Lean, **Lample et al. (2022)** train Transformer models on Metamath, **Mikula et al. (2023)** apply retrieval augmentation — all report success metrics without mechanistic decomposition. In contrast, we adopt controlled ablation methodology from ML interpretability (Geiger et al., 2021 on causal abstraction; Elhage et al., 2021 on transformer circuits) to quantify mechanism contributions in theorem proving.

Our work is the first to apply mechanistic interpretability to theorem proving evaluation, isolating NL understanding (29.5pp contribution, p<10⁻⁹), rejecting proof depth (<8%), and validating tactic budget as a fairness control metric (CV=0.36). This establishes a methodological template for future ablation studies in formal mathematics.
