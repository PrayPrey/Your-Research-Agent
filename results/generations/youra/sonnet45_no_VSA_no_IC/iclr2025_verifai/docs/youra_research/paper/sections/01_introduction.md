# Introduction

LLM-guided theorem provers achieve 89% success on miniF2F olympiad problems (DeepSeek-Prover-V2, 2025) while pure automated provers manage only 16% — a 50-percentage-point gap that dominates recent theorem proving literature. Thor (Jiang et al., 2022) demonstrated that hybrid LLM+hammer systems produce 8.2% unique solutions where neither component succeeds alone, revealing complementary strengths. Yet no prior work has quantified *why* LLMs succeed where automated provers fail. Without mechanistic understanding, we cannot predict when synergy occurs or design targeted improvements to either approach.

Understanding LLM advantage mechanisms is critical for designing hybrid systems that combine LLM semantic understanding with automated prover formal reliability. If the gap originates from natural language hint parsing, we should invest in NL preprocessing and semantic tactic libraries. If it stems from long-range proof search, we should prioritize context window scaling. Existing work reports *that* LLMs outperform automated provers and *how much* they outperform, but not *which mechanisms* drive the advantage.

We hypothesize the 50pp gap decomposes into three testable mechanisms: (1) **natural language understanding** (60% contribution) — LLMs exploit informal hints in problem statements that automated provers ignore, (2) **proof depth capability** (30% contribution) — LLMs maintain context across multi-step proofs where automated provers timeout at shallow depths, and (3) **corpus pattern matching** (10% contribution) — LLMs learn human proof tactic distributions from Mathlib training data. Each mechanism is falsifiable via controlled ablation: remove NL hints, filter to shallow proofs, compare against random Mathlib sampling.

Our key finding: **Natural language understanding is the dominant mechanism**, contributing ~60% of LLM advantage (29.5pp drop when NL hints removed, p<10⁻⁹), while proof depth contributes <8% (below our 5% falsification threshold). This result shifts design priorities from architectural scaling (longer context for deep proofs) to NL-formal integration (better hint extraction, semantic tactic suggestion). For hybrid systems, the mechanistic attribution suggests a routing strategy: assign NL-rich problems to LLMs and formal-only goals to automated provers.

**Contributions.** Building on this mechanistic hypothesis, we:

1. **Establish the first measured baseline** for pure automated provers (lean-auto) on miniF2F Lean 4 subset: 15.6% [11.5%, 20.3%] (N=244), validating our 15% prediction and enabling controlled LLM comparisons.

2. **Quantify NL understanding contribution** via ablation study: removing docstring/comment hints drops LLM success from 62.3% to 32.8% (Δ=29.51% [20.90%, 38.11%], p<10⁻⁹), directly validating ~60% attribution (29.5pp / 50pp gap ≈ 59%).

3. **Reject the proof depth hypothesis**: post-hoc filtering to shallow proofs (≤3 tactics) drops success by only 3.7% [1.6%, 6.1%] (below our 5% gate threshold), forcing mechanistic model revision from 3-way attribution (NL=60%, depth=30%, corpus=10%) to 2-way (NL=60%, residual=40%).

4. **Validate tactic budget control framework**: tactic count coefficient of variation CV=0.36 (36% << 100% threshold) enables fair LLM vs automated prover comparisons by controlling for computational confounds (budget=15 captures 90.6% of baseline strategies).

Our mechanistic approach differs from prior systems work (Thor, LeanCopilot, DeepSeek-Prover-V2) in focus: we *explain* LLM advantage rather than maximize success rates. The remaining sections present our controlled ablation design (§3), quantified mechanistic evidence (§4-5), and implications for hybrid system design (§6).
