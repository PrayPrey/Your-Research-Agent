# Discussion

## Interpretation of Results

Our results validate the lifecycle-shift mechanism: executable API contracts shift defect detection from training-stage (67.9% baseline) to environment-stage (75.0%), achieving 9.57-hour median TTFF reduction. This shift is causally mediated by three-tier validation—structural (50.3% of defects), metamorphic (30.2%), and composition (19.5%)—with complementary coverage demonstrated by minimal tier overlap (12.0%).

The 74.8% contractability rate establishes that *most* environment-stage API defects violate documented, version-stable invariants testable before training. This finding challenges the implicit assumption in prior work [1, 2] that ML reproducibility failures are inherently unpredictable or require domain expertise to diagnose. Instead, we show that failures are *systematic* (they violate documented invariants) and *preventable* (contracts catch them at environment-setup).

The composition contract evolution (0% → 89.7%) reveals a broader insight about design space exploration: initial proof-of-concept limitations do not always indicate fundamental impossibility. The unidirectional design (h-e1) failed not because composition contracts are infeasible, but because the architecture was insufficient. Bidirectional propagation (h-c3) resolved this through forward compatibility validation and backward recovery verification—an innovation applicable beyond our specific context to any multi-library integration testing scenario.

## Limitations and Scope Boundaries

We acknowledge five principled limitations that bound the generalizability of our findings:

**L1: Computer Vision Domain Scope.** All experiments used CV datasets and defects (68% of Jiang et al.'s corpus). NLP and RL workflows may exhibit different API usage patterns—tokenization APIs, environment simulators, and distributed training primitives remain untested. We expect 50-60% contractability in these domains based on similar documentation quality, but empirical validation is future work.

**L2: Version Stability CI Uncertainty.** Our version-stability FPR of 4.0% [1.6%, 9.8%] meets the threshold at the point estimate, but the CI upper bound (9.8%) exceeds our <5% criterion due to small sample size (N=100). Production deployment should validate on N≥500 test cases across more version transitions to tighten confidence intervals. The wide CI reflects experimental constraint (20 version transitions available at evaluation time), not a fundamental limitation of contracts.

**L3: Prospective Trial Simulation.** The 9.57-hour TTFF reduction (h-m4) comes from simulated pull requests based on Jiang et al.'s defect distributions, not live GitHub deployment. While our retrospective analysis (3.75h observed reduction on 20 historical PRs) confirms the direction of effect, the simulated magnitude may overestimate real-world savings if repositories adopt contracts selectively (e.g., only for critical paths). Live deployment to 10-15 production repositories is essential future work.

**L4: Composition Mechanism Refinement Required.** Composition contracts are not straightforward extensions of structural/metamorphic patterns. The h-e1 → h-c3 iteration demonstrates that achieving 89.7% detection required bidirectional propagation architecture, explicit forward/backward compatibility checks, and context manager integration. This complexity may hinder adoption if practitioners expect composition contracts to work out-of-the-box without architectural considerations.

**L5: Opaque C++ Extension Ceiling.** 10.3% of composition defects (3/29) involve opaque C++ extensions (e.g., custom PyTorch operators) where Python-level introspection is impossible without vendor cooperation. This represents a theoretical contractability ceiling absent library ecosystem changes (e.g., libraries shipping contract specifications alongside implementations).

### When Contracts Do Not Apply

Contracts validate *documented behavioral invariants* at environment-stage. They do not address:

- **Training-stage stochasticity:** Contracts cannot detect gradient explosion, divergence, or hyperparameter sensitivity issues that emerge only after multiple training epochs.
- **Semantic drift:** If a library changes behavior in an undocumented way that does not violate mathematical invariants (e.g., subtle tokenization changes in NLP), contracts will not flag it.
- **Undocumented APIs:** Internal/private APIs lacking docstring specifications are non-contractable absent auto-inference from execution traces (future work).
- **Performance defects:** Contracts validate correctness, not efficiency—a function may pass all contracts while being 10× slower than expected.

## Broader Impact

**Positive Impacts:** Contracts reduce researcher time waste on preventable errors, improving ML research efficiency. By codifying library behavioral specifications, contracts also improve documentation quality—library authors must explicitly state invariants they previously left implicit. The 75% of ML repositories lacking testing (Wolter et al. [2]) represent a high-impact deployment target.

**Potential Risks:** False positives (4.0% rate) may frustrate researchers if error messages are unclear or if contracts flag "acceptable" violations of informal conventions. To mitigate this, we invested significant effort in actionable error message design (Section 3.1)—contracts specify *why* a violation occurred and *how* to fix it (e.g., "Expected device=cuda, got device=cpu. Insert .to('cuda') before line 42.").

**Ecosystem Changes:** Widespread contract adoption could incentivize libraries to ship behavioral specifications alongside code—similar to how type hints (PEP 484) became standard after tooling (mypy) demonstrated value. This would enable auto-generated contracts covering 60-70% of APIs (Section 3.6).

## Comparison to Concurrent Work

Since our evaluation began (July 2024), two related works appeared:

**Zhang et al. (2025) "Runtime Assertion Checking for ML Pipelines":** Validates data quality at pipeline boundaries via runtime assertions. Complementary to our work—their focus is data validation, ours is API behavioral validation. Contracts + assertions together could cover both environmental correctness (contracts) and input data quality (assertions).

**Li et al. (2024) "Automated Test Generation for ML Libraries":** Uses symbolic execution to generate tests for ML library functions. Differs in deployment—their tests run during CI (training-stage detection), ours run at environment-setup (earlier detection). Their approach may generate contracts automatically (future integration direction).

## Implications for ML Reproducibility Research

Our work establishes a fourth reproducibility tier:

1. **Environment Isolation:** Containers (Docker), virtual environments (conda)
2. **Dependency Pinning:** Version locking (requirements.txt, Pipfile.lock)
3. **Integration Testing:** Repository-specific regression tests (pytest, tox)
4. **API Behavioral Validation (Ours):** Library-level executable contracts

Each tier addresses complementary failure modes—isolation prevents system-level conflicts, pinning stabilizes versions, testing validates repo-specific logic, contracts validate library behavior. The 72% marginal detection improvement (P2) demonstrates that contracts provide value beyond tiers 1-3.

**Methodological Contribution:** Our contractability measurement framework (3-question filter with blinded coding) provides a reusable protocol for evaluating whether other defect types (e.g., NLP tokenization errors, RL environment mismatches) are contractable. Future work can apply this protocol to expand contract coverage beyond CV+PyTorch.

## Future Work Directions

**Immediate Extensions (1-2 years):**

1. **Auto-Contract Generation:** Implement docstring → contract pipeline targeting ≥60% coverage. Preliminary analysis (Section 3.6) suggests 60-70% of contracts are mechanically derivable from documentation.
2. **NLP/RL Domain Validation:** Collect defect corpora, test contracts on tokenizer/environment APIs. Expected contractability: 50-60% based on similar documentation patterns.
3. **Production Inference Validation:** Deploy contracts at model-load time in serving systems. Challenge: async validation to meet latency SLAs (<10ms overhead).

**Longer-Term Vision (3-5 years):**

1. **Trace-Based Contract Synthesis:** Infer implicit invariants from execution traces, distinguish genuine invariants from coincidences (≥95% pattern stability across traces).
2. **Contract-Aware Library Ecosystems:** Libraries ship `.contract` files alongside `.py` files, enabling cross-library composition checking at install time (similar to type stubs `.pyi`).
3. **Semantic Drift Detection:** Extend contracts to detect behavior changes that preserve mathematical invariants but violate semantic expectations (e.g., tokenizer output format changes in NLP).

---

**References (Section 6 only - full list in Section 7)**

[1] Jiang et al. (2023). An Empirical Study of Bugs in PyTorch-Based Deep Learning Systems.  
[2] Wolter et al. (2025). Reproducibility Practices in Machine Learning Research.
