## Name

retrieval_augmented_invariant_transfer

## Title

RAIT: Retrieval-Augmented Invariant Transfer for Scalable Loop Invariant Generation

## Short Hypothesis

Loop invariants for new programs can be generated more efficiently and reliably by retrieving verified invariants from structurally similar programs and adapting them, rather than generating from scratch. We hypothesize that a self-growing library of (program, verified-invariant) pairs, combined with structure-aware retrieval and LLM-based adaptation, will reduce the number of LLM calls and SMT solver invocations needed to verify new programs, while achieving higher success rates than zero-shot or few-shot generation baselines. This setting — loop invariant generation with SMT-verified feedback — is ideal for testing this hypothesis because correctness is binary and checkable, enabling rigorous evaluation of transfer quality.

## Related Work

Existing approaches to LLM-based loop invariant generation (CLN2INV, G-CLN, LaM4Inv, NeuroInv, and the O1+Z3 pipeline) all treat each program in isolation: an LLM proposes candidate invariants, a verifier (SMT solver or BMC) checks them and returns counterexamples, and the LLM refines. While these achieve strong results on Code2Inv (133/133 with O1+Z3), they do not exploit the fact that many programs share structural patterns that imply similar invariant shapes. The closest related idea is few-shot prompting with example programs, but no existing work builds an explicit, verified, growing retrieval library or studies how invariant transfer scales with library size. SpecGen (Ma et al., 2024) generates specifications using LLMs but does not perform cross-program transfer. Our work is the first to frame loop invariant generation as a retrieval-and-adaptation problem, creating a self-improving system where each successfully verified program enriches future verification.

## Abstract

Loop invariant generation is a central challenge in automated program verification. Recent work combining large language models (LLMs) with SMT solvers has achieved impressive results on standard benchmarks, but these approaches generate invariants from scratch for each program, ignoring the rich structure shared across programs in the same domain. We introduce RAIT (Retrieval-Augmented Invariant Transfer), a framework that builds a self-growing library of verified (program, invariant) pairs and uses structure-aware retrieval to accelerate invariant generation for new programs. Given a target program, RAIT retrieves the k most structurally similar programs from the library using a code embedding model, presents their verified invariants as context to an LLM, and prompts the LLM to adapt these invariants to the target program. The adapted invariants are checked by an SMT solver; on success, the new pair is added to the library. On failure, counterexamples guide iterative refinement, as in prior work. We evaluate RAIT on the Code2Inv and SV-COMP benchmarks, measuring success rate, number of LLM queries, and solver calls as the library grows. We show that retrieval-augmented adaptation consistently outperforms zero-shot and random-retrieval baselines, requires fewer refinement iterations, and exhibits a positive scaling trend — the more programs verified, the faster new programs are solved. RAIT demonstrates that verified invariants are a transferable, reusable resource, opening a new direction for building cumulative formal verification knowledge bases.

## Experiments

1. **Library construction and evaluation protocol**: Split Code2Inv (133 programs) and SV-COMP (200+ programs) into 50% library seed / 50% test. Seed the library with verified invariants from the seed split using an existing tool (O1+Z3 pipeline). Evaluate RAIT on the test split. Metric: success rate (% programs verified), mean LLM queries per program, mean SMT calls per program.

2. **Retrieval method ablation**: Compare (a) no retrieval (zero-shot LLM), (b) random retrieval (k random library entries), (c) BM25 token-based retrieval, (d) CodeBERT embedding-based retrieval. All use the same LLM (GPT-4o or Claude 3.5 Sonnet) for adaptation. Metric: success rate and query efficiency.

3. **Library growth experiment**: Start with an empty library and process test programs sequentially, adding each successfully verified program to the library. Plot success rate and mean queries-per-program as a function of library size. This demonstrates the self-improving property.

4. **Adaptation vs. generation difficulty**: For each retrieved invariant, measure the edit distance between the retrieved invariant and the final verified invariant for the target program. Compare to the edit distance between a zero-shot LLM guess and the verified invariant. This quantifies how much retrieval reduces the adaptation burden.

5. **Cross-benchmark transfer**: Train the library on Code2Inv programs and test retrieval on SV-COMP programs (different distribution). Measure whether cross-benchmark transfer still helps vs. zero-shot baseline. This tests generalization of the approach.

6. **Baseline comparison**: Compare RAIT against LaM4Inv, NeuroInv, and the O1+Z3 pipeline on the same test split, using the same LLM backbone where possible. Primary metric: success rate; secondary: computational cost (API calls, wall-clock time).

## Risk Factors And Limitations

1. **Retrieval quality bottleneck**: If structurally similar programs do not have similar invariants (e.g., programs with similar syntax but different semantics), retrieval may introduce noise rather than signal. Mitigation: ablation study comparing retrieval methods; fallback to zero-shot if top-k similarity is below threshold.

2. **Library cold-start problem**: With an empty or small library, RAIT reduces to zero-shot generation. The self-improvement benefit only emerges with sufficient library coverage. Mitigation: seed the library with programs from existing benchmarks that have verified invariants.

3. **Scalability of embedding-based retrieval**: As the library grows to thousands of programs, retrieval must remain efficient. Mitigation: use approximate nearest-neighbor search (FAISS); this is a solved engineering problem.

4. **Benchmark saturation**: On Code2Inv, the O1+Z3 pipeline already achieves 100% success, leaving little room for improvement in success rate. RAIT's advantage may be primarily in efficiency (fewer queries). Mitigation: use harder benchmarks (SV-COMP, LIG-MM) where existing methods fail on 20-40% of programs.

5. **LLM adaptation failures**: The LLM may fail to correctly adapt retrieved invariants, especially when programs differ significantly. Mitigation: the SMT solver provides a correctness check, and counterexample-guided refinement serves as a fallback.

6. **Novelty perception**: Retrieval-augmented generation is a well-known technique in NLP; the novelty here is its application to verified invariant libraries. The paper must clearly articulate the unique challenges of retrieval in the formal verification setting (verified correctness, structured program representations, adaptation vs. generation).

