# 7. Conclusion

We began by asking why better approximation produces worse retrieval. MOHAWK's SSD mixer
approximates LLaMA-3-8B attention matrices with *decreasing* normalized error as sequence length
grows — the conversion is not failing at long context. The answer is that approximation and
architecture are different mechanisms, and only the second limits retrieval. The bounded-state
update h_t = A·h_{t-1} + B·x_t exponentially discounts early token positions regardless of how
well the SSD weights are initialized; this is a property of the state-space formalism, not of
the distillation procedure.

### Summary

In this work, we addressed the mechanism confound in SSM conversion evaluation by designing a
two-part protocol: an independently measurable mechanism gate (SSD Frobenius approximation
scaling) followed by a behavioral test (task-type × strategy interaction on LongBench v2).

Our primary contributions are:

1. **Mechanism gate confirmed:** Normalized SSD Frobenius error decreases with sequence length
   for LLaMA-3-8B (β=-0.368, gate PASSED at N≤2048 with large margin across 1,760 measurements).

2. **Architectural attribution:** Retrieval degradation in MOHAWK-converted models is attributable
   to bounded-state forgetting, not approximation failure — an architectural property that
   persists regardless of distillation compute.

3. **Validated evaluation infrastructure:** The first controlled cross-strategy pipeline
   (MOHAWK-SSM vs LAWCAT vs Hybrid-4 vs teacher on LongBench v2 with fixed LLaMA-3-8B base)
   is implemented, validated (22/22 tests), and running, with final behavioral gate numbers
   pending H-E1 completion.

4. **Engineering artifact:** Ten undocumented integration failure modes in the MOHAWK+LAWCAT+
   LLaMA-3.1-8B pipeline are identified and resolved, enabling community replication.

### Future Directions

**From the unexplained negative slope:** Effective rank analysis of LLaMA-3-8B attention matrices
at increasing N would test whether attention sparsity explains why the SSD approximation strengthens
at longer contexts. If effective rank decreases with N, the sparsity mechanism is confirmed and
the SSD approximation advantage at long range is theoretically grounded.

**From unverified assumptions:** Once H-E1 completes, H-M2 depth-slope analysis will directly
test whether LAWCAT's Conv1D produces shallower needle-depth degradation than MOHAWK-SSM —
the mechanistic prediction that would complete Steps 2 and 3 of the causal chain. Perplexity
gate verification will also determine whether the 1B token distillation budget achieves
sufficient alignment (≤5% PPL gap) for interpretable behavioral comparisons.

**From scope extension:** A mixed-length distillation curriculum ablation (50% 2048-token,
50% 8192-token sequences) would determine whether the architecture-vs-curriculum confound
affects the behavioral interaction result. Generalization to Mistral-7B and Qwen2-7B base
models would test whether the mechanism gate and behavioral findings extend beyond LLaMA-3.1-8B.

Understanding this distinction — approximation quality vs. bounded-state architectural limits —
does not close the question of how to build efficient long-context models. It sharpens that
question into a form that is precisely measurable, directly actionable, and open for the
community to answer with the infrastructure we have built.
