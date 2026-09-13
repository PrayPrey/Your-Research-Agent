## 6. Discussion

### 6.1 Why HumanEval Training Dominates Both Benchmarks

The most surprising finding — HumanEval-only SFT outperforms MBPP-only SFT on MBPP+ — demands
a mechanistic explanation. The embedding alignment framework provides one: HumanEval-only
training is embedding-closer to both test benchmarks than MBPP-only training is. But this
explanation requires a deeper account of why algorithmic function-completion problems are
embedding-closer to MBPP+ utility-script problems than MBPP-only training itself.

We propose that HumanEval-style problems develop more transferable Python programming
competence for two reasons. First, HumanEval problems require writing functions that pass
doctests — a general "write correct Python code" skill that transfers to any test-case-based
evaluation task. MBPP-only problems develop a narrower utility-script style (string
manipulation, list operations) that does not cultivate the same general function-writing
competence. Second, both HumanEval+ and MBPP+ evaluate Python functions that must pass test
cases; the test-case-passing format is structurally identical across benchmarks. HumanEval
training, by conditioning on doctest-driven function completion, directly prepares the model
for this format regardless of the specific problem type.

An alternative explanation — pretraining co-exposure — should be considered. DeepSeek-Coder's
2T token pretraining likely includes substantial MBPP-style utility code from GitHub. If the
base model already has strong MBPP representations, MBPP-only SFT may offer limited marginal
gain, while HumanEval SFT fills a gap in the pretrained distribution. This would partially
explain the asymmetry: MBPP utility scripting is "already learned" to some degree; HumanEval
algorithmic completion is a more targeted and effective specialization.

We note that the MBPP-only training condition used 120 problems from the sanitized split
(vs the expected ~374 from the full split). The smaller training set may have limited
MBPP-only specialization potential. However, the direction (HumanEval-only > MBPP-only on
MBPP+) is consistent across all 3 seeds — suggesting this is a genuine effect, not an artifact
of small sample size.

### 6.2 Equal-Mix Underperformance and Its Implications

Equal-mix training achieves 10.2% HumanEval+ pass@1 — substantially below both HumanEval-only
(35.0%) and MBPP-only (27.6%) — despite equal token budget. This is not simply a quantity
issue: all conditions receive the same token budget. The cause is distributional dilution: the
model receives a mixed training signal that is less aligned with any specific test distribution
than a focused single-source would be.

This has a direct practical implication: when optimizing for a specific benchmark, naïve
equal-proportion mixing is harmful rather than helpful at limited training scales. The model's
gradient updates are pulled in multiple distributional directions simultaneously, producing a
model that is mediocre on all benchmarks rather than excellent on any. This recapitulates the
intuition behind DoReMi and DomainPilot — source weights matter — but demonstrates it more
starkly through controlled single-source isolation.

### 6.3 Scale Effects and the η² Limitation

The collapse of within-condition seed variance at 7B scale (σ²=0.00043 vs 0.01655 at 1.3B)
is an underappreciated phenomenon with methodological implications. When seeds produce
near-identical pass@1 within a condition, the model is effectively deterministic — any
single training run is representative. This improves reproducibility but misleads η² as an
effect-size metric for cross-scale comparison.

Researchers comparing source identity effects at different scales should use absolute
condition spread (max mean − min mean pass@1) rather than η², because η² conflates
between-condition effects with within-condition noise. At 7B, the between-condition spread
is genuinely smaller (5.5pp vs 31.9pp), supporting scale-induced attenuation — but η²
inverts this conclusion by appearing larger due to noise collapse.

### 6.4 Limitations

**MBPP+ evaluation incomplete.** Our MBPP+ analysis relies on H-M1's per-seed two-condition
comparison (HumanEval-only vs MBPP-only only). The full 4-condition MBPP+ evaluation was
not saved in the H-E2 CSV output (likely an output path issue in the evaluation pipeline),
and 4/12 H-C1 MBPP evaluations failed due to tokenizer incompatibility. All SFT checkpoints
are preserved; re-running MBPP+ evaluation on existing checkpoints would complete the full
transfer matrix. Until then, MBPP+ claims are limited to the two-condition comparison.

**Statistical fragility at n=4.** With four source conditions, the minimum achievable
Spearman permutation p-value is 1/24 ≈ 0.042. Our observed ρ=1.0 achieves exactly this
minimum — barely satisfying p<0.05. One rank swap would lose significance. We interpret
the mechanistic alignment result as "highly consistent evidence for" rather than "definitive
proof of" the alignment mechanism. The perfect rank alignment (ρ=1.0) and dual-encoder
concordance (MiniLM ρ=0.8 in same direction) provide substantive evidence beyond the
marginal p-value, but replication with additional source conditions would strengthen the claim.

**Format normalization assumption unverified.** We applied a standardized instruction template
across all sources, assuming this eliminates format as a confound. If MBPP's native I/O example
format provides additional specialization signal, our format normalization may have
disadvantaged MBPP-only SFT, partially explaining the absence of MBPP+ inversion. Testing
with native MBPP format would clarify this.

**MBPP-train sample size.** The MBPP sanitized split yielded 120 problems vs the expected ~374
from the full split. This smaller training set adds uncertainty to the MBPP-only condition's
specialization potential. We cannot fully rule out that 374 MBPP training problems would
produce stronger MBPP+ specialization.

### 6.5 Broader Impact

This work has implications for benchmark evaluation practice. If pass@1 gains from SFT can
be largely attributed to source-benchmark embedding alignment, then reported benchmark
improvements are not exclusively about model architecture or training scale — they also reflect
the match between training data style and test benchmark style. We recommend that code SFT
papers report training source composition alongside benchmark results to enable proper
attribution and comparison.

On the positive side, our embedding alignment finding enables a more principled approach to
SFT data selection: measure CodeBERT similarity between candidate training data and the target
benchmark before training. This is computationally cheap (embedding inference) and could
prevent practitioners from wasting GPU time on misaligned training data.
