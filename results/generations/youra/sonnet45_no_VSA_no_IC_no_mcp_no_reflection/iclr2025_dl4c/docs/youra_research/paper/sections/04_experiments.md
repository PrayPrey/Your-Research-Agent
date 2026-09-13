# Experimental Setup

We design experiments to answer the following questions:

**RQ1:** Does fix-impact-ratio discriminate strategic debugging (targeting root causes) from sequential trial-and-error (addressing failures one-by-one)?

**RQ2:** Do agents cluster errors by shared characteristics (measured via clustering coefficient > 0.3) compared to random ordering?

**RQ3:** Does error clustering enable prioritization of high-impact fixes (modifications resolving ≥2 test failures simultaneously)?

**RQ4:** Do agents transfer learned patterns to held-out test cases (passing unseen tests without error messages) at rates exceeding random baseline?

## Datasets

We evaluate on synthetic multi-test programming problems to establish metric sensitivity before real-world deployment.

**Mock Synthetic Dataset:**
- **Problems:** 50 programming tasks (sum, max, array operations, string manipulation, basic algorithms)
- **Test Cases:** 15-25 per problem (mean 20.3, median 19)
- **Error Types:** Balanced distribution — syntax (24.3%), runtime (25.3%), logic (27.4%), edge_case (23.0%)
- **Rationale:** Controlled environment validates whether metrics *can* detect strategic behavior when engineered. Balanced error types ensure clustering signal detectable. Mock validation precedes production deployment with GPT-4 + Codeforces.

## Baselines

**Random Sampling:** Agent generates code variations without error feedback (temperature=0.7), no access to test failure information. Establishes null model for fix-impact-ratio (expected ratio ≈ 1.0 if no strategic behavior).

**Sequential Trial-and-Error:** Agent addresses test failures one-by-one in test index order, no error clustering or root-cause analysis. Baseline for clustering coefficient (expected ≈ 1.0 under random error ordering).

Baselines represent non-strategic approaches, enabling discrimination of clustering and prioritization behaviors.

## Implementation Details

**Mock Agent Architecture:**
- **Framework:** Python simulation with controlled parameters (`clustering_strength`, `fix_success_rate`, `pattern_memory_enabled`)
- **Clustering Simulation:** `clustering_strength=0.5` yields 50% probability of clustering same-type errors consecutively vs random ordering
- **Fix Success:** `fix_success_rate=0.6` (baseline) vs `0.7` (proposed method), simulating root-cause prioritization effectiveness
- **Iteration Budget:** `max_iterations=10` per problem, `temperature=0.7`
- **Seed:** Fixed random seed (`seed=1`) for reproducibility

**Hyperparameters (by hypothesis):**
- **h-e1:** N=10 problems, controlled trajectories (strategic vs sequential)
- **h-m1:** N=50 problems, `clustering_strength=0.5`, permutation test with 1000 samples
- **h-m2:** N=50 problems, `baseline_fix_success=0.6`, `proposed_fix_success=0.7`, `cluster_bonus_probability=0.6`
- **h-m3:** N=50 problems, `revealed_fraction=0.5`, `pattern_memory_enabled=True`, `max_iterations=10`

**Compute Resources:** Local execution, <1 hour total runtime (mock agents, no GPU required)

**Reproducibility:** Code available in `h-{id}/code/` directories. Implementation uses controlled parameters to validate metric sensitivity, not production agent behavior.

## Evaluation Metrics

**Fix-Impact-Ratio (FIR):** Tests passed per modification, $\text{FIR} = \frac{1}{k} \sum_{i=1}^{k} \Delta_{\text{passing}}(m_i)$. Strategic agents achieve ratio > 2.0 (one fix resolves 2+ failures), sequential agents ≈ 1.0. Evaluated via t-test or Mann-Whitney U (p < 0.05). **Why:** Directly measures debugging efficiency — core metric validating strategic vs sequential discrimination (RQ1).

**Clustering Coefficient (CC):** Consecutive same-type errors vs expected under random permutation, $\text{CC} = \frac{C_{\text{observed}}}{C_{\text{random}}}$. Coefficient > 0.3 indicates clustering above chance. Evaluated via permutation test (1000 shuffles, p < 0.05). **Why:** Tests whether agents recognize error patterns (RQ2), validating mechanism Stage 1 (clustering enables prioritization).

**High-Impact Proportion:** Percentage of modifications with $\Delta_{\text{passing}} \geq 2$ (multi-test fixes). Proposed method expected > baseline. Evaluated via proportion test (p < 0.05). **Why:** Tests prioritization effectiveness (RQ3), validating mechanism Stage 2 (clustering → high-impact fixes).

**Held-Out Test Slope Ratio:** Agent slope (held-out pass rate vs iteration) divided by random-mutation slope. Ratio > 1.5 with p < 0.05 indicates transfer learning. **Why:** Tests pattern transfer to unseen tests without error messages (RQ4), attempting to validate mechanism Stage 3 (clustering → transfer).

**Effect Size:** Cohen's d for fix-impact-ratio (0.2=small, 0.5=medium, 0.8=large). Large effect size (d > 0.8) demonstrates strong discriminative power.

Statistical significance threshold p < 0.05 for all tests. Permutation tests control for problem-specific error distributions (clustering coefficient, held-out slope). Directional tests used where appropriate (high-impact proportion: proposed > baseline).
