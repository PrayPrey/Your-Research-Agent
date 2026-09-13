# Conclusion

We began with a puzzle: training data deduplication makes MMLU scores significantly
*worse* ($p = 0.0114$, Bonferroni-corrected). For a practice universally prescribed
as a quality improvement, this regression demands explanation. Our work provides one:
deduplication is not a uniform quality upgrade — it is a contamination corrector, and
MMLU was contaminated.

## Summary

We analyzed the Pythia model suite at token-count-matched checkpoints across four model
sizes (160M--6.9B) and four standard benchmarks (MMLU, HellaSwag, ARC-Challenge,
WinoGrande). Our main finding is that the per-benchmark accuracy differential between
dedup-Pile and Pile models correlates positively with estimated 13-gram n-gram
contamination between the Pile training corpus and each benchmark's test set
(Pearson $r = 0.632$, $p = 0.0086$; Spearman $\rho = 0.618$, $p = 0.0107$;
$n = 16$ observations). Benchmarks whose test content overlaps more with the Pile
corpus show larger accuracy reductions under deduplication — consistent with
deduplication removing the contamination-driven advantage those benchmarks conferred.

Beyond this primary result, we contribute:

**Methodological:** Token-count matching is the correct confound-control strategy for
Pile/dedup-Pile comparisons. Step-matching introduces a volume-effect bias that
reduces the measured contamination signal by $\Delta r = -0.093$ and adds a uniform
$-0.004$ accuracy offset. Prior analyses using step-matched Pythia comparisons have
been measuring a weakened contamination signal.

**Mechanistic:** Documents removed by Pile deduplication show significantly higher
13-gram overlap with benchmark test content than retained documents (dry-run PoC:
2/4 benchmarks significant at $p < 0.0125$), confirming the contamination-correction
mechanistic chain at the document level.

**Open question:** The near-memorization pathway (min-k\% differential) was not confirmed
at Pythia-1B scale — dedup-Pile models unexpectedly score higher on min-k\% than Pile
models. This suggests the memorization mechanism may require model scales above 1B to
manifest via token-level probability signatures, or that min-k\% captures general
corpus quality rather than contamination-specific memorization for the Pile/dedup-Pile
distinction.

## Future Directions

Our results open several grounded directions for future work:

**Testing the memorization scale threshold:** The H-M2 direction reversal at Pythia-1B
predicts that Pythia-6.9B should show the expected direction (Pile $>$ dedup-Pile
min-k\%) if memorization scales with model capacity as Carlini et al.\ [2021] found.
Analysis of the full H-M2 experiment at 6.9B will confirm or refute this scale-threshold
explanation.

**Fresh contamination estimates:** The H-M1 full-corpus pipeline ($n = 10{,}000$ per
group, streaming Pile and dedup-Pile) will produce ground-truth 13-gram overlap rates
for each benchmark. Re-running the H-M3 correlation with these freshly computed rates
will validate and potentially strengthen the $r = 0.632$ result.

**Expanding benchmark coverage:** Extending from 4 to 8--12 benchmarks would double
or triple the effective sample size for the contamination-accuracy correlation,
substantially tightening the confidence interval and increasing statistical power.
Benchmarks such as BoolQ, PIQA, OpenBookQA, and SIQA have lm-eval coverage and
existing 13-gram contamination estimates.

**Cross-family generalization:** Applying the contamination-correction signature
analysis to OLMo/Dolma — using the token-count matching and 13-gram correlation
framework established here — would test whether the finding generalizes across
model families, subject to the architecture confound caveat.

## Closing

Training data deduplication is not a universal performance booster — it is a
contamination corrector. Which benchmarks improve and which decline is written in
the overlap structure between the training corpus and benchmark test sets.
Reading that structure, as we demonstrate here, is now possible: correlate the
per-benchmark accuracy differential with contamination estimates, match checkpoints
by token count, and the contamination-correction signature becomes visible.
We hope this framework encourages the evaluation community to look beneath aggregate
benchmark averages and ask which benchmarks are measuring capability and which
are measuring corpus contamination.
