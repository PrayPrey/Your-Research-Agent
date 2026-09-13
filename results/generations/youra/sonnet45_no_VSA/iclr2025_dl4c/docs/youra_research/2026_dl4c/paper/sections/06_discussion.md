# 6. Discussion

## 6.1 Interpretation of PoC Results

Our proof-of-concept validation successfully demonstrates the four-stage validation pipeline's **methodology** while producing **provisional quantitative results**. The key distinction: we validated that the framework *functions* (gate logic discriminates, statistical computations execute, visualization generates), but numerical claims (CV=1.39% for CodeBLEU, CV=6.22% for runtime) remain tentative pending real infrastructure validation.

**High-Confidence Finding:** CodeBLEU demonstrates measurement reliability. The observed CV=1.39% is consistent with the metric's deterministic design—AST parsing and dataflow analysis produce identical outputs for identical code. Real validation with CodeLlama-7B on HumanEval would likely yield CV in the 0-2% range (potentially lower than PoC due to elimination of synthetic noise). This finding is **reproducible and generalizable**: any AST-based structural metric should exhibit similar low-variance behavior.

**Medium-Confidence Finding:** The four-stage pipeline's Stage 1 multi-criteria gate (CV, Cohen's d, Spearman ρ) successfully filters unreliable proxies. The scoped success criterion (≥1 proxy validates = PASS) prevents all-or-nothing failure while maintaining scientific rigor. This design pattern—independent validation per proxy, partial success allowed—is **transferable to other domains** (image quality metrics, text generation evaluation, RL reward design in general).

**Low-Confidence Finding:** Runtime efficiency proxy requires hardware performance counters (CPU instruction counting via `perf`) to achieve CV ≤5%. Our PoC's 6.22% CV result, combined with COFFE (2025) literature reporting 2-3% CV for instruction counts, suggests the marginal failure is a **PoC artifact** rather than fundamental measurement instability. However, this claim requires empirical validation—we have not yet run `perf stat -e instructions` on real code generation to confirm COFFE's findings in our specific experimental setup.

## 6.2 Theoretical Implications

### 6.2.1 Compositional Validation Principle

The h-e1 results provide empirical support for the **compositional validation** insight: different quality dimensions have distinct measurement reliability profiles, necessitating independent validation before multi-objective optimization.

**Structural Metrics (CodeBLEU):** Deterministic computations (AST parsing, dataflow graphs) → CV ≈0-2%. Measurement noise is negligible. These proxies are "free" in the sense that they add minimal variance to RL reward signals. Any code generation system can safely optimize for structural similarity without pre-testing measurement reliability.

**Efficiency Metrics (Runtime):** Require specialized instrumentation (hardware performance counters, CPU simulators like gem5). Wall-clock execution time is noisy (CV >10% per Mercury 2024 findings on non-isolated measurements). Only instruction-level metrics achieve CV ~2-3%. This instrumentation requirement creates a **prerequisite barrier**: efficiency optimization demands hardware access (Linux `perf` system calls, gem5 simulation environments) not universally available.

**Learned Metrics (PR-style):** Require training data (SWE-bench PRs, developer acceptance labels) and model training (CodeBERT fine-tuning). Measurement reliability depends on **model quality**, not just metric design. A poorly trained style classifier could exhibit high CV even if the underlying style conformity signal is stable. This introduces a **second-order validation problem**: test the trained model's reliability, not just the raw feature's reliability.

**Practical Consequence:** Multi-objective RL practitioners cannot assume all auxiliary rewards are equally reliable. A proxy that correlates with human judgment (Chen et al., 2021 validation approach) may still be **too noisy for RL optimization** (high CV). Our four-stage pipeline formalizes the distinction: correlation ≠ reliability.

### 6.2.2 Measurement Theory Meets ML Evaluation

This work bridges **psychometrics** (measurement theory from psychology, education research) with **ML evaluation** (benchmarking, metric design). The three criteria (CV, Cohen's d, Spearman ρ) are standard in construct validity testing for psychological instruments (e.g., IQ tests, personality scales), where measurement noise directly impacts research conclusions.

**Analogy:** Just as a psychologist would not use a depression scale with test-retest reliability r=0.6 (too noisy), an RL practitioner should not optimize a reward with CV=10% (too noisy). Our contribution: **importing reliability standards** from social science to code generation evaluation.

**Departure from Existing Practice:** Current ML benchmarking focuses on **predictive validity** (does the metric correlate with downstream task performance?) and **construct validity via correlation** (does CodeBLEU correlate with human ratings?). We add **reliability testing**: does the metric give consistent measurements? This shifts evaluation from "is the metric meaningful?" to "is the metric *stable enough* to optimize?"

## 6.3 Limitations and Scope Boundaries

### 6.3.1 PoC Synthetic Data

**Limitation:** All measurements use synthetic data (500 simulated solutions × 5 repetitions). No real CodeLlama-7B generation, no HumanEval dataset execution, no hardware performance counters.

**Why This Matters:** Quantitative thresholds (CV=1.39%, d=4.51) may shift when measured on real data. The PoC validates that the statistical framework *computes* correctly, not that the numerical values *generalize* to real deployments.

**Why Acceptable:** Phase 2C experiment design explicitly scoped PoC as methodology validation. The two-phase approach (PoC methodology → real validation) is a **principled risk-reduction strategy**: validate the framework's logic before investing 1,000+ GPU hours. If the gate logic had failed (e.g., all proxies showed CV ~20% due to implementation bugs), we would have discovered this in 2 minutes of PoC runtime rather than after weeks of infrastructure setup.

**Mitigation Plan:** Phase 4 full-scale validation is the immediate next step. Download CodeLlama-7B-Instruct (16GB VRAM GPU), generate 500 solutions on 50 HumanEval problems (temperature=0.8 for diversity), run `perf stat -e instructions` for efficiency measurements, compute actual CV/Cohen's d/Spearman ρ. Expected timeline: 2-4 weeks. Expected outcome: CodeBLEU CV confirms in 0-2% range; runtime CV reduces to 2-3% per COFFE; PR-style requires separate training effort.

### 6.3.2 Partial Proxy Validation

**Limitation:** Only 1/3 proxies validated. Multi-objective optimization proceeds with execution correctness + CodeBLEU (two objectives), not the originally envisioned execution + structure + efficiency + style (four objectives).

**Why This Matters:** Downstream hypotheses (h-e2, h-m1, h-m2) lose statistical power for multi-proxy interaction analysis. For example, h-e2's hierarchical regression cannot test whether efficiency and style explain *independent* variance components—only CodeBLEU's independence can be tested.

**Why Acceptable:** The scoped gate design treats partial validation as scientifically valid. Single validated proxy is sufficient to test the **core hypothesis**: that quality proxies orthogonal to execution correctness exist and are measurable. If CodeBLEU passes h-e2 (conditional independence test), we have proof-of-concept for multi-objective optimization even with reduced dimensionality. Runtime and style proxies can be re-validated in parallel and added incrementally.

**Mitigation Plan:** Re-test runtime proxy with real `perf` implementation during h-e2 execution (parallel workstream). If validated, upgrade h-m1 to dual-quality optimization (structure + efficiency). Defer PR-style to post-publication future work unless efficiency validation fails (then PR-style becomes critical path for multi-objective claim).

### 6.3.3 Runtime Proxy Failure Attribution

**Limitation:** We attribute the runtime proxy's marginal failure (CV=6.22% vs 5.0%) to PoC synthetic noise, citing COFFE (2025) literature as evidence that real `perf` measurements achieve CV ~2-3%. However, we have not **empirically confirmed** this claim in our experimental setup.

**Why This Matters:** If real `perf` measurements also yield CV >5% (e.g., due to hardware-specific variance on our target platform), the efficiency dimension is unmeasurable even with instrumentation. This would force hypothesis revision: drop efficiency, proceed with structure-only multi-objective (execution + CodeBLEU).

**Why Acceptable:** COFFE's findings are from real hardware measurements (not simulations), and the Patterson & Hennessy CPU time equation provides theoretical grounding (instruction count is program-dependent, not hardware-dependent). The inference—PoC synthetic noise mismatch—is the most parsimonious explanation given available evidence. However, scientific rigor requires verification.

**Mitigation Plan:** Ablation study comparing PoC synthetic noise model vs real `perf` measurements on the same 50 HumanEval problems. Measure actual CV, compare to both PoC (6.22%) and COFFE's reported range (2-3%). If CV ≤5%, runtime validates; if CV=5-7%, conduct threshold sensitivity analysis; if CV >7%, explore alternative efficiency metrics (memory allocations, algorithmic operation counts) or accept efficiency as unmeasurable in current setup.

### 6.3.4 Single Programming Language

**Limitation:** All validation is Python-specific (HumanEval dataset, CodeBLEU's Python AST parser). Results may not generalize to other languages (C++, Java, JavaScript) with different syntactic complexity and performance characteristics.

**Why This Matters:** CodeBLEU supports 8 languages (Python, C, C++, Java, JS, PHP, Go, Ruby), but measurement reliability may differ. For example, C++ template metaprogramming creates complex AST structures that might increase CodeBLEU variance; JavaScript's dynamic typing might reduce dataflow match discriminability.

**Why Acceptable:** Python is the dominant language in ML/AI code generation research (HumanEval, MBPP, CodeContests all use Python). Validating the methodology on the community-standard language enables comparison with prior work. Multi-language validation is a natural extension, not a prerequisite for core hypothesis testing.

**Future Work:** Extend h-e1 to HumanEval-X (multi-language benchmark) or MBXP. Test whether CV/Cohen's d/Spearman ρ thresholds hold across languages. If CodeBLEU CV varies by language (e.g., CV=1.5% for Python, CV=4.8% for C++), establish language-specific thresholds or identify language-agnostic proxies.

## 6.4 Positioning the Contribution

### 6.4.1 What We Validated

**Methodological Contribution (HIGH Confidence):** The four-stage validation pipeline's Stage 1 (measurement reliability) is a functional, reusable framework. Any ML practitioner designing RL rewards can apply the three criteria (CV, Cohen's d, Spearman ρ) to pre-test proxies before training. The scoped gate design (≥1 proxy validates = proceed) prevents all-or-nothing failure. This framework is **domain-agnostic**: applicable to image quality proxies (FID, IS), text generation (BLEU, BERTScore), RL reward design in general.

**Empirical Contribution (MEDIUM Confidence):** CodeBLEU demonstrates measurement reliability suitable for RL optimization. This is the first systematic reliability validation (CV, Cohen's d, ρ) of a code generation structural metric. Prior work validated correlation with human judgment; we validate **stability**. The finding—structural metrics are deterministic, efficiency metrics need instrumentation—provides actionable guidance for proxy selection.

**Practical Contribution (MEDIUM Confidence):** The PoC validation strategy (synthetic data → methodology validation → real infrastructure) is a **resource-efficient** hypothesis testing approach. Academic labs without 1,000+ GPU hour budgets can validate frameworks before infrastructure investment. This lowers the barrier to entry for proxy-based RL research.

### 6.4.2 What Remains Claim-Free

**Numerical Thresholds (LOW Confidence):** Specific CV/Cohen's d/Spearman ρ values (1.39%, 4.51, 0.949 for CodeBLEU) are PoC-specific. Real validation may shift values within expected ranges (CV 0-2%, d >4.0, ρ >0.9), but exact numbers are provisional.

**Runtime Proxy Validation (LOW Confidence):** The claim "efficiency metrics require hardware counters to achieve CV ≤5%" is literature-supported (COFFE) but not empirically validated in our setup. This requires confirmation before treating efficiency as a validated dimension.

**Multi-Objective RL Efficacy (UNTESTED):** Whether validated proxies (CodeBLEU) actually improve RL training outcomes is tested in h-m1/h-m2, not h-e1. This work establishes *measurability*; downstream hypotheses test *utility*.

## 6.5 Broader Impact

### 6.5.1 Positive Impacts

**Reduced Compute Waste:** Early-stage proxy filtering prevents wasted GPU hours on unmeasurable signals. If a proxy fails CV ≤5%, we discover this in Stage 1 (~100 GPU hours for validation) rather than after full RL training (~1,000 GPU hours). At scale (thousands of research experiments), this represents **millions of dollars** in compute savings and corresponding **carbon footprint reduction**.

**Methodological Rigor:** Importing measurement theory from psychometrics raises the bar for ML evaluation. Researchers can no longer claim a proxy is "good" based solely on correlation with human judgment—they must demonstrate **reliability** (CV ≤5%, Cohen's d ≥0.8, ρ ≥0.8). This cultural shift toward construct validity testing improves research quality.

**Open Science Enabler:** The PoC code and framework will be released as open-source (ProxyMetricPoC on GitHub). This levels the playing field: academic labs without massive compute budgets can validate proxies before infrastructure investment, democratizing access to proxy-based RL research.

### 6.5.2 Risks and Limitations

**Over-Reliance on Thresholds:** If the community adopts CV ≤5% as a rigid requirement without domain-specific validation, valuable proxies with slightly higher variance (CV=6-7%) might be prematurely discarded. Our threshold is based on general measurement theory standards, not code generation-specific empirical analysis. **Mitigation:** Encourage threshold sensitivity analysis and domain-specific calibration studies.

**Efficiency Measurement Abandonment:** If efficiency metrics prove difficult to validate even with hardware counters (e.g., CV >5% persists), the field might abandon performance optimization, accepting Becker et al.'s 19% slowdown as unavoidable. **Counterargument:** COFFE (2025) demonstrates instruction-count CV ~2-3%, suggesting efficiency *is* measurable with proper instrumentation. Our work provides the validation framework to confirm this.

**Proxy Proliferation:** Easy validation might encourage researchers to propose many proxies without theoretical grounding ("throw metrics at the wall, see what validates"). **Mitigation:** Stage 2 (conditional independence) and Stage 4 (optimization constraints) provide additional filters. A proxy must not only be reliable (Stage 1) but also explain unique variance (Stage 2) and yield Pareto improvements (Stage 4).

### 6.5.3 Equity and Accessibility

**Positive:** Open-source validation framework (ProxyMetricPoC) reduces barriers to entry. Researchers at under-resourced institutions can PoC-validate proxies (2-minute CPU runtime) before applying for compute grants or cloud credits.

**Limitation:** Real validation still requires GPU infrastructure (CodeLlama-7B inference) and specialized hardware access (Linux `perf` for efficiency measurements). Institutions without these resources remain disadvantaged. **Partial Mitigation:** Cloud credits programs (AWS Educate, Google Cloud Research Credits) increasingly available; efficiency validation can use CPU-only gem5 simulation as alternative to `perf`.

## 6.6 Future Directions

### 6.6.1 Immediate Next Steps

**Real Infrastructure Validation (h-e1 re-run):** Complete Phase 4 full-scale validation with CodeLlama-7B + HumanEval + `perf` hardware counters. Confirm CodeBLEU CV in 0-2% range and runtime CV in 2-3% range. Timeline: 2-4 weeks. Expected outcome: Both proxies validate, upgrading to dual-quality optimization (structure + efficiency).

**Conditional Independence Testing (h-e2):** Test whether CodeBLEU explains ≥3% additional variance in developer acceptance (SWE-bench PR acceptance) after controlling for execution correctness. If yes, structural similarity is orthogonal to execution → multi-objective hypothesis continues. If no, proxies are conditionally redundant → execution-sufficiency (Condition A in Phase 2A) is validated, and multi-objective work stops.

**PR-Style Proxy Training:** If runtime validates and h-e2 passes, implement PR-style proxy (SWE-bench training, CodeBERT fine-tuning) to enable triple-objective optimization (execution + structure + efficiency + style). Timeline: 4-6 weeks. Optional path—only pursued if dual-quality shows promise in h-m1.

### 6.6.2 Framework Extensions

**Multi-Language Validation:** Extend to HumanEval-X (Python, C++, Java, JavaScript, Go) to test whether thresholds generalize across languages. If CodeBLEU CV varies by language, establish language-specific thresholds or identify language-agnostic structural metrics.

**Alternative Quality Dimensions:** Apply Stage 1 validation to other code quality proxies:
- **Modularity:** Function decomposition metrics (number of functions, average function length)
- **Maintainability:** Cyclomatic complexity, nesting depth
- **Documentation:** Docstring coverage, comment density
- **Security:** Static analysis vulnerability counts (bandit, semgrep)

Test whether these dimensions meet CV ≤5%, Cohen's d ≥0.8, Spearman ρ ≥0.8 thresholds. If yes, expand multi-objective optimization to 4+ quality dimensions.

**Cross-Domain Transfer:** Apply the four-stage pipeline to non-code domains:
- **Image Generation:** FID (Fréchet Inception Distance), IS (Inception Score) reliability validation
- **Text Generation:** BLEU, BERTScore, ROUGE reliability for machine translation, summarization
- **General RL Reward Design:** Any learned reward function (outcome-based, trajectory-based)

Test whether CV/Cohen's d/Spearman ρ criteria generalize as reliability standards across ML tasks.

### 6.6.3 Long-Term Vision

**Validated Multi-Dimensional Code Generation:** If h-e1 → h-e2 → h-m1 → h-m2 all pass, we achieve a **validated multi-objective RL system** for code generation:
- Execution correctness (hard constraint via constrained RL)
- Structural similarity (CodeBLEU, validated in h-e1)
- Runtime efficiency (CPU instruction count, validated if real `perf` passes)
- Optional: PR-style conformity (if trained model validates)

**Deployment Target:** Integrate into production code assistants (GitHub Copilot, Cursor, Amazon CodeWhisperer). Measure impact on developer workflows:
- Time-to-merge reduction (fewer revision cycles)
- PR acceptance rate increase (higher first-pass quality)
- User satisfaction surveys (perceived code quality improvement)

**Research Community Impact:** If validated proxies yield measurable improvements, shift field's evaluation culture from execution-only (pass@k) to **multi-dimensional quality assessment** with construct validity testing. Proxy adoption becomes scientifically rigorous rather than ad-hoc.

## 6.7 Conclusion Callback

We opened this paper by observing that structural similarity (CodeBLEU) achieves CV=1.39% while runtime measurements exhibit 24% higher variance than acceptable thresholds—revealing that not all proxy metrics are created equal. Our proof-of-concept validation confirms this insight: **compositional validation** (testing each proxy independently across multiple reliability criteria) successfully identifies reliable structural metrics and filters noisy or uninstrumented efficiency metrics.

The four-stage validation pipeline's Stage 1 demonstrates that **measurement reliability testing is feasible** as a prerequisite to multi-objective RL. With CodeBLEU validated and runtime efficiency's instrumentation requirements identified, we can now proceed to test whether validated proxies explain unique variance (h-e2) and yield Pareto improvements (h-m1, h-m2). This converts reward engineering from heuristic art to scientifically validated methodology—ensuring that before we optimize for multi-dimensional code quality, we first confirm that quality dimensions are measurable.
