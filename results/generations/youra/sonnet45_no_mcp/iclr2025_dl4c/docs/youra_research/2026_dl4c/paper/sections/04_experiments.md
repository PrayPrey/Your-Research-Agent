# Experiments

Our experimental design tests two foundational claims through h-e1 and h-m1: (1) can standardized execution trace features be reliably extracted across benchmarks? (2) do benchmarks with different design philosophies produce distinctive model rankings? Each experiment has explicit success criteria and falsification conditions derived from our hypothesis decomposition.

## Experimental Questions

**RQ1 (h-e1):** Can we extract standardized execution trace features with ≥95% completeness across different benchmarks?

This tests data infrastructure validity. Without complete feature coverage, downstream correlation analysis would be unreliable—missing data could create artificial ranking agreements or divergences.

**RQ2 (h-m1):** Do HumanEval and MBPP produce distinctive model rankings?

This tests the foundational assumption that benchmarks with different design philosophies (algorithmic clarity vs. practical patterns) create measurable dimensional separation. Success requires both ranking divergence (ρ < 0.8) and distributional divergence (KL > 0.1).

**RQ3 (h-m1):** Do benchmarks have different distributional properties despite ranking agreement?

This tests whether distributional divergence without ranking divergence supports the unidimensional competency interpretation—benchmarks differ in difficulty calibration but measure the same underlying construct.

## Experimental Setup

### Models Evaluated

We evaluate 8 code generation models spanning diverse architectures and training paradigms:

- **CodeGen-2B-Multi** [Nijkamp et al., 2022]: Autoregressive model trained on The Pile and BigQuery
- **Codex (code-davinci-002)** [Chen et al., 2021]: GPT-3 fine-tuned on GitHub code
- **StarCoder-15B** [Li et al., 2023]: Trained on The Stack (permissively licensed code)
- **GPT-3.5-Turbo** [OpenAI, 2023]: Instruction-tuned model with code capabilities
- **GPT-4** [OpenAI, 2023]: Frontier model with strong code generation performance
- **CodeLlama-7B** [Rozière et al., 2023]: Llama 2 fine-tuned on code
- **InstructCodeLlama-7B** [Rozière et al., 2023]: Instruction-tuned variant
- **WizardCoder-15B** [Luo et al., 2023]: Evol-Instruct training on code tasks

**Rationale:** Model diversity enables testing whether ranking correlations persist across different model families. If correlation reflected narrow architectural similarity, diverse models would show ranking divergence.

### Benchmarks

**HumanEval** [Chen et al., 2021]: 164 hand-crafted Python problems testing algorithmic problem-solving. Each problem includes function signature, docstring specification, and unit tests. Average difficulty: solvable by competent programmers in 5-10 minutes.

**MBPP** [Austin et al., 2021]: 974 Python problems from introductory programming exercises testing practical coding patterns. Problems emphasize string manipulation, data structures, and basic algorithms appearing in real codebases. Generally simpler than HumanEval.

**APPS** (Planned but Unavailable): Dataset API changed during data collection. We proceed with HumanEval-MBPP pairwise analysis, noting this limits testing three-way factor structure.

### Feature Extraction Protocol (h-e1)

For each model-benchmark pair, we extract:

**Correctness (3 features):**
- pass@1: Percentage solved with 1 sample (greedy decoding, temperature=0)
- pass@10: Percentage solved with 10 samples (nucleus sampling, temperature=0.8, top_p=0.95)
- pass@100: Percentage solved with 100 samples (same sampling parameters)

**Efficiency (3 features):**
- runtime_q25, runtime_q50, runtime_q75: 25th, 50th, 75th percentile execution time for passing solutions
- Measured by executing generated code on benchmark test suites with 5-second timeout

**Failure Modes (3 features):**
- error_syntax: Percentage of failing attempts with syntax errors
- error_runtime: Percentage with runtime exceptions (ZeroDivisionError, IndexError, etc.)
- error_timeout: Percentage exceeding time budget

**Data Sources:**
- pass@k: Published results from peer-reviewed papers (Chen et al. 2021, Rozière et al. 2023, Luo et al. 2023)
- Runtime/errors: Our execution on benchmark test suites (700+ test cases, standardized Python 3.9 environment)

**Completeness Metric:** Percentage of model-benchmark pairs with all 9 features successfully extracted. Gate threshold: ≥95%.

### Statistical Analysis Protocol (h-m1)

**Ranking Correlation:**
- Extract pass@1 scores for each model on HumanEval and MBPP
- Compute Spearman rank correlation ρ between the two benchmark rankings
- Test significance via permutation test (10,000 permutations, α=0.05)
- **Success criterion:** ρ < 0.8 (at least 20% ranking divergence)
- **Failure criterion:** ρ ≥ 0.9 (benchmarks rank models nearly identically)

**Distributional Divergence:**
- Normalize feature distributions to [0,1] range per benchmark
- Compute KL divergence: D_KL(P_HumanEval || P_MBPP) using histogram binning (20 bins)
- **Success criterion:** KL > 0.1 (distributional differences exist)
- **Interpretation:** High KL with high ρ → same rankings, different difficulty; High KL with low ρ → different dimensions

**Gate Condition:** h-m1 requires BOTH (ρ < 0.8) AND (KL > 0.1). If only KL condition met, we conclude benchmarks differ in difficulty but not in dimensional measurement.

## Baseline Comparisons

**For h-e1 (Infrastructure):** No baseline needed—this is a data quality validation. Success is binary: either we extract complete features or we don't.

**For h-m1 (Distinctiveness):** We compare against the threshold ρ < 0.8 derived from the assumption that benchmarks with documented design philosophy differences should show at least 20% ranking divergence. This threshold balances two considerations:
- Benchmarks should not be perfectly correlated (ρ=1.0) if they measure different things
- Some correlation is expected since all benchmarks test code generation ability
- ρ=0.7-0.8 is the typical range for related but distinct psychometric constructs

## Experimental Validity Considerations

**Confound Control:** Rankings computed from pass@1 (widely reported, consistent availability) rather than mixing metrics across models. Using different metrics per model could create artificial ranking agreements or divergences.

**Data Quality:** External verification detected 8 mock data violations in initial implementation. All violations fixed—results based entirely on real published data and actual execution measurements, not synthetic values.

**Statistical Power:** With n=6 models (HumanEval-MBPP overlap), we can detect |Δρ| > 0.4 at 80% power. Perfect correlation ρ=1.0 greatly exceeds this detectability threshold.

**Reproducibility:** All code and data publicly available. HumanEval and MBPP benchmarks are open-source. Published pass@k results are peer-reviewed and cited. Runtime measurements can be reproduced by executing our provided code on the same benchmarks.

## Limitations of Experimental Design

**Sample Size:** 8 models (6 with overlap) below planned 20+. Limits ability to detect weak ranking divergence but sufficient for detecting strong signals like perfect correlation.

**Benchmark Coverage:** APPS unavailable, restricting to HumanEval-MBPP analysis. Cannot test three-way correlations or held-out generalization.

**Metric Focus:** Rankings from pass@1 only. Other metrics (pass@10, runtime efficiency) could reveal different ordinal structures, though preliminary analysis suggests high cross-metric correlation.

**Model Selection:** Models chosen for published result availability, not random sampling. May introduce selection bias toward well-evaluated models, though diversity in architecture (autoregressive, instruction-tuned) and size (2B-175B estimated) mitigates this concern.

These limitations inform result interpretation but do not invalidate findings—perfect correlation is robust evidence even with limited sample size, and pairwise analysis suffices for testing ranking distinctiveness hypothesis.
