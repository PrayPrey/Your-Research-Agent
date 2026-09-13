# Discussion

Our pilot study yields several findings with implications for hallucination detection research and practice.

## Key Findings

**Finding 1: Benchmark sensitivity exists.** Semantic entropy shows marginal detection ability on HaluEval (AUROC 0.551) but inverted results on TruthfulQA (AUROC 0.289). This suggests that method performance depends on benchmark-specific factors—potentially labeling methodology, hallucination type distribution, or task characteristics.

*Implication:* Practitioners should not assume method performance transfers across benchmarks. Evaluating on multiple benchmarks with different hallucination definitions is essential before deployment.

**Finding 2: Self-consistency near random.** BERTScore-based consistency achieved AUROC 0.444-0.474 across both datasets, statistically indistinguishable from chance. This suggests surface-level similarity may not capture hallucination-relevant uncertainty.

*Implication:* Self-consistency may require different similarity metrics (e.g., NLI-based pairwise agreement) to effectively detect hallucinations in QA settings.

**Finding 3: Controlled comparison reveals inconsistencies.** Published results suggest both methods achieve AUROC 0.70-0.85. Our matched-budget pilot finds neither method consistently exceeds 0.55. While sample size differences may account for some discrepancy, this highlights the need for standardized evaluation protocols.

*Implication:* Method papers should report performance on multiple benchmarks under matched conditions to enable practitioner decision-making.

## Limitations

We acknowledge several limitations that qualify our findings:

**L1: Insufficient sample size.** Our PoC mode uses N=20 samples per dataset, far below the full dataset sizes (817 TruthfulQA, 10K HaluEval). This yields wide confidence intervals (spanning 0.5+ AUROC) and prevents statistically powered conclusions.
- *Why acceptable:* PoC mode validates experimental pipeline before committing computational resources to full-scale runs.
- *Future work:* Full-scale evaluation with complete datasets.

**L2: TruthfulQA labeling mismatch hypothesis.** Our interpretation that TruthfulQA's inverted results stem from labeling methodology is speculative. The "Best Answer" matching protocol may differ from the original semantic entropy paper's evaluation approach.
- *Why acceptable:* This identifies a concrete methodological question for the field.
- *Future work:* Compare labeling protocols; run with original paper's evaluation code.

**L3: Single model family.** We evaluate only Llama-3-8B-Instruct. Results may not generalize to other model families (GPT, Claude, Mistral) or model scales.
- *Why acceptable:* Standard practice for PoC; isolates method comparison from model confounds.
- *Future work:* Multi-model evaluation across architectures and scales.

**L4: Single seed.** All experiments use seed 42. Variance across random seeds is not captured.
- *Why acceptable:* PoC mode prioritizes rapid iteration; multi-seed evaluation planned for full run.
- *Future work:* 5-seed evaluation with averaged results and standard errors.

## Relation to Prior Work

Our findings complement rather than contradict prior work:

- Kuhn et al. [2023] report strong semantic entropy performance on TruthfulQA. Our inverted result may reflect model differences (Llama-3-8B vs original models), sample size effects, or labeling protocol differences—not necessarily method failure.

- Manakul et al. [2023] report strong SelfCheckGPT performance on WikiBio. Our near-random results on TruthfulQA/HaluEval may reflect benchmark-task mismatch—WikiBio biography generation differs substantially from factual QA.

These observations reinforce our central finding: method performance is benchmark-sensitive, and controlled cross-benchmark comparison is essential.

## Broader Impact

**Positive impacts:** Our work promotes more rigorous evaluation practices for hallucination detection. By revealing benchmark sensitivity, we encourage practitioners to evaluate methods on task-relevant benchmarks before deployment.

**Potential concerns:** Our pilot results might be misinterpreted as "methods don't work," discouraging adoption of uncertainty-based detection. We emphasize that our findings are preliminary (N=20) and that methods may perform well on full-scale evaluation.

**Mitigation:** We frame results as pilot findings requiring validation, not definitive method assessments. We encourage the community to conduct full-scale matched-budget comparisons.
