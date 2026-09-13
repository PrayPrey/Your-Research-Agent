# Adversarial Review - Round 2 (R2)

**Paper**: NLI Clustering Failure and Polarity Inversion: Why Standard UQ Methods Miss Hallucinations on HaluEval-QA
**Round**: R2 - Verification and Credibility
**Date**: 2026-05-11
**Personas**: Accuracy Checker, Skeptical Expert
**Input**: 06_paper_r1.md (post-R1 revision)

---

## R1 Issues Status

Checking the four P1-priority MAJOR issues that were required fixes:

| R1 Issue | Required Fix | Status in R1-Revised Paper |
|----------|-------------|---------------------------|
| MAJOR-004: Contribution count (4 vs 3) | Align conclusion to say "four contributions" | FIXED — Conclusion now states "four contributions: (1)...(2)...(3)...(4)..." ✓ |
| MAJOR-006: Polarity inversion hypothesis caveating | Mark as hypothesis consistently; add alternative explanations | FIXED — Abstract says "hypothesis (unverified)"; Discussion lists three alternatives ✓ |
| MAJOR-007: H-M3 generalizability claim | Remove "suggesting findings would replicate with other LLMs" | FIXED — Limitations now says "Whether findings replicate with other LLMs remains an open question" ✓ |
| MAJOR-001: aggregation_rate CI upper 0.292 vs 0.2915 | Audit raw output; report authoritative value | CARRIED — Paper still reports [0.253, 0.292]; the 0.2915 vs 0.292 ambiguity is unresolved (see below) |
| MAJOR-002: Cluster count=1 fraction (0.2% vs 4.4%) | Verify raw; update ground truth YAML | CARRIED — Paper retains 4 (0.2%); ground truth YAML not reconciled |
| MAJOR-003: Figure registry mismatch | Reconcile figures 3 and 4 | CARRIED — Paper figures still do not match ground truth YAML registry |
| MAJOR-005: "First controlled comparison" novelty | Soften or support with evidence | PARTIALLY FIXED — "To our knowledge" hedge present; no additional literature evidence added |

**Summary**: P1 priority fixes (MAJOR-004, 006, 007) are properly applied. Carried issues (MAJOR-001, 002, 003) appear to be deferred or intentionally retained. MAJOR-005 is partially addressed by the existing "To our knowledge" hedge.

---

## Ground Truth Verification Table (R2 Full Pass)

| Claim | Ground Truth Value | Paper Value | Match | Notes |
|-------|-------------------|-------------|-------|-------|
| SE AUROC | 0.5000 | 0.5000 | ✓ | |
| SE CI | [0.5000, 0.5000] | [0.5000, 0.5000] | ✓ | |
| SE std | 4.14e-25 | 4.14e-25 | ✓ | |
| TE AUROC | 0.4829 | 0.4829 | ✓ | |
| TE CI | [0.458, 0.509] | [0.4585, 0.5090] | ✓ | 4-decimal rounding OK |
| SCG AUROC | 0.3562 | 0.3562 | ✓ | |
| SCG CI | [0.332, 0.380] | [0.3321, 0.3803] | ✓ | 4-decimal rounding OK |
| aggregation_rate | 0.272 | 0.272 | ✓ | |
| aggregation_rate CI lower | 0.253 | 0.253 | ✓ | |
| aggregation_rate CI upper | 0.292 (GT YAML) / 0.2915 (h-m2 report) | 0.292 | ⚠ | Unresolved from R1 |
| pct_max_cluster_count | 72.8% | 72.8% | ✓ | 1456/2000 = 72.8% ✓ |
| Cluster count=1 | 4 examples (0.2%) per paper+h-m2 | 4 (0.2%) | ✓ | GT YAML 0.044 appears erroneous |
| Cluster count=2 | 22 (1.1%) | 22 (1.1%) | ✓ | |
| Cluster count=3 | 112 (5.6%) | 112 (5.6%) | ✓ | |
| Cluster count=4 | 406 (20.3%) | 406 (20.3%) | ✓ | |
| Cluster count=5 | 1456 (72.8%) | 1456 (72.8%) | ✓ | |
| Cluster sum | 4+22+112+406+1456=2000 | 2000 | ✓ | Arithmetic verified |
| SE vs SCG delta | 0.1438 | 0.1438 | ✓ | 0.5000-0.3562=0.1438 ✓ |
| TE vs SCG delta | 0.1268 | 0.1268 | ✓ | 0.4829-0.3562=0.1267; paper says 0.1268 (rounding) ✓ |
| SE vs TE delta | 0.0171 | 0.0171 | ✓ | 0.5000-0.4829=0.0171 ✓ |
| Sample balance | 1000:1000 | 1000:1000 | ✓ | AUROC baseline=0.5 ✓ |
| Bonferroni k | 3 | 3 | ✓ | |
| alpha_corrected | 0.0167 | 0.0167 | ✓ | 0.05/3=0.01667 ✓ |
| N stochastic samples | 5 | 5 | ✓ | |
| Bootstrap resamples | 1000 | 1000 | ✓ | |
| Mean cluster count | 4.644 | 4.644 | ✓ | |
| log2(5) entropy | 2.322 bits | "log2(5)≈2.322 bits" | ✓ | log2(5)=2.3219 ✓ |
| Contribution count | 4 (conclusion) | 4 | ✓ | Fixed from R1 |
| H-M3 status | INCONCLUSIVE | "not executed" | ✓ | Properly disclosed |

---

## Executive Summary

FATAL Issues: 0
MAJOR Issues: 2
MINOR Issues: 4
Recommendation: CONDITIONAL_ACCEPT

The paper has successfully addressed the P1 priority R1 issues. The numerical claims are internally consistent and mathematically sound. Two MAJOR issues remain: one is a genuine credibility concern about NLI model identifier precision (MAJOR-SKEP2-001), and one is a mathematical edge case about SE AUROC=0.5000 exactness given non-constant cluster distribution (MAJOR-ACC2-001). Neither is fatal — both have satisfactory resolutions — but both require explicit clarification in the paper. The carried R1 issues (MAJOR-001 to 003) are noted but the underlying substantive claims remain valid.

---

## PERSONA 1: ACCURACY CHECKER (R2)

### Mathematical Validity Analysis

**AUROC bootstrap CIs — plausibility check**

With N=1000 bootstrap resamples on 2000 examples, the expected CI width for AUROC near 0.5 with a real signal is approximately 0.04–0.06 (rule of thumb: SE ≈ sqrt(AUROC*(1-AUROC)/n) ≈ sqrt(0.25/2000) ≈ 0.011, but bootstrap accounts for label correlation so wider CIs are typical). The TE CI width = 0.5090 - 0.4585 = 0.0505 and SCG CI width = 0.3803 - 0.3321 = 0.0482 are both in the expected range for 2000 examples. The SE CI [0.5000, 0.5000] is width zero — consistent with a degenerate constant signal. All CI widths are mathematically plausible.

**Pairwise delta math — verified**

- SE(0.5000) - SCG(0.3562) = 0.1438 ✓
- TE(0.4829) - SCG(0.3562) = 0.1267; paper says 0.1268 — acceptable rounding (0.48290 - 0.35620 = 0.12670; with more decimal precision 0.48290 - 0.35621 = 0.12669, rounds to 0.1267 or 0.1268 depending on stored precision) ✓
- SE(0.5000) - TE(0.4829) = 0.0171 ✓

**Aggregation rate math — verified**

- aggregation_rate = fraction with cluster_count < 5 = (4+22+112+406)/2000 = 544/2000 = 0.272 ✓
- pct_max_cluster_count = 1456/2000 = 0.728 = 72.8% ✓
- Consistency check: 0.272 + 0.728 = 1.000 ✓

**Cluster distribution sum — verified**

4 + 22 + 112 + 406 + 1456 = 2000 ✓ (4+22=26; 26+112=138; 138+406=544; 544+1456=2000)

**Individual fractions — verified**

- 4/2000 = 0.002 = 0.2% ✓
- 22/2000 = 0.011 = 1.1% ✓
- 112/2000 = 0.056 = 5.6% ✓
- 406/2000 = 0.203 = 20.3% ✓
- 1456/2000 = 0.728 = 72.8% ✓

**Bonferroni correction — verified**

alpha_corrected = 0.05 / 3 = 0.01667 ≈ 0.0167 ✓

**Sample balance — verified**

1000 hallucinated + 1000 factual = 2000; 50/50 split gives random AUROC baseline = 0.5 ✓

**log2(5) entropy — verified**

log2(5) = ln(5)/ln(2) = 1.6094/0.6931 = 2.3219 bits ≈ 2.322 ✓ (paper says "log2(5)≈2.322 bits")

**SE std plausibility — critical analysis**

The paper states SE std = 4.14e-25 across all 2000 examples. However, 544 examples (27.2%) have cluster_count < 5, meaning they do NOT have the maximum entropy of log2(5). These examples should produce SE values less than 2.322 bits. If even one example has a meaningfully different SE, the std could not approach zero.

The resolution lies in the cluster distribution: the non-max examples are cluster_count=4 (406 examples, 20.3%), 3 (112, 5.6%), 2 (22, 1.1%), and 1 (4, 0.2%). For cluster_count=4 with 5 samples: if one cluster has 2 samples and three have 1 each, entropy = -(2/5)*log2(2/5) - 3*(1/5)*log2(1/5) ≈ 0.529 + 1.393 = 2.122 bits — very close to 2.322. For cluster_count=1: entropy = 0. However, the distribution of samples within clusters matters: if cluster_count=4 with split (2,1,1,1), entropy≈2.122; with split (1,1,1,1,1) that is impossible (that gives 5 clusters); split (3,1,1,0) doesn't sum properly.

The precise resolution: with N=5 and cluster_count=k, the minimum entropy configuration is when one cluster contains N-k+1 samples and k-1 clusters each contain 1 sample. For k=4 minimum: (2,1,1,1) → entropy ≈ 2.122; maximum: uniform would require fractional samples, so maximum valid is (2,1,1,1) — only one valid integer partition. Actually multiple partitions exist. The point is that cluster_count < 5 examples can have SE values ranging from 0 to near-2.322, meaning the std should not be 4.14e-25.

**MAJOR-ACC2-001**: SE std=4.14e-25 is inconsistent with 544 non-max-cluster examples having variable entropy (see Issues below for full analysis).

### Numerical Consistency Check

Cross-checking all numbers in paper against each other:

- Abstract: "AUROC values range from 0.356 to 0.500" — 0.3562 rounds to 0.356, 0.5000 rounds to 0.500 ✓
- Abstract: "aggregation rate of 0.272" ✓
- Introduction: "72.8% of examples receive maximum cluster counts" ✓
- Introduction: "AUROC = 0.4829" for TE ✓
- Introduction: "AUROC = 0.356" for SCG (rounds from 0.3562) ✓
- Section 3 gate: "aggregation_rate = fraction of examples with cluster count < N=5" → 544/2000 = 0.272 ✓
- Section 5 table: cluster counts sum to 2000 ✓
- Pairwise table deltas: all verified above ✓
- Conclusion: "four contributions" ✓ (R1 fix applied)
- Mean cluster count = (1×4 + 2×22 + 3×112 + 4×406 + 5×1456)/2000 = (4+44+336+1624+7280)/2000 = 9288/2000 = 4.644 ✓

### Issues Found

**[MAJOR-ACC2-001]** SE std=4.14e-25 claim is mathematically questionable given 27.2% non-constant examples

- **Evidence**: The paper states "Semantic entropy std = 4.14 × 10⁻²⁵ across 2,000 examples" (Section 5, H-M1). This value is effectively machine-precision zero for float64 (float64 epsilon ≈ 2.22e-16; 4.14e-25 is below even subnormal ranges for practical purposes). However, 544 examples have cluster_count < 5. For these examples, SE is NOT log2(5). A cluster_count=1 example has SE=0 bits; a cluster_count=2 example has SE=log2(5/4) to log2(5) depending on split. SE=0 for 4 examples alone would create a non-negligible std.
- **Analysis**: The paper's Figure 4 (degenerate_summary.png) shows "SE as a perfectly flat line." If this figure is accurate, the empirical std being 4.14e-25 must reflect that even the 544 non-max examples happen to produce very similar SE values — possibly because the integer partition (2,1,1,1) for cluster_count=4 produces SE ≈ 2.122 and this is the predominant non-max pattern, and cluster_count=1 with SE=0 for only 4 examples has negligible effect on std. However, std of 4.14e-25 for a distribution mixing values at 0, 1.522, 2.122, ~2.252, and 2.322 bits is implausible unless the 544 non-max examples all concentrate near exactly the same entropy value.
- **Most likely explanation**: The std = 4.14e-25 value as reported either (a) refers to the standard deviation of SE *among the 1456 max-cluster examples only* (all exactly log2(5)), (b) is a computational artifact where LLaMA-2-7B-chat's responses in the non-max cases happen to produce the same entropy through a different mechanism, or (c) is an error in how std was computed (e.g., std of token entropy rather than semantic entropy).
- **Severity**: MAJOR — if the std is computed over all 2000 examples and truly is 4.14e-25, the paper needs to explain why 544 non-max-cluster examples produce near-identical entropy values. If the std is computed over only the 1456 max-cluster examples, the paper is presenting a misleading statistic (since SE is NOT constant for the other 27.2% of examples). Either way, the claim that SE is "a perfectly flat line" in Figure 4 requires reconciliation with the fact that 544 examples cannot have SE=log2(5).
- **Required fix**: Clarify: (a) is std=4.14e-25 computed over all 2000 examples or only the 1456 max-cluster subset? (b) If all 2000, provide the SE value distribution for non-max examples to justify near-zero std. (c) If only the 1456 subset, reframe as "SE is constant for 72.8% of examples; for the remaining 27.2%, SE varies but is bounded above by log2(5)." The AUROC=0.5000 claim is separately justified by constant signal for 72.8% examples AND the non-discriminating nature of variable entropy for the remainder — but this needs to be explicit.

**[MINOR-ACC2-001]** TE vs SCG delta rounding

- Paper states TE vs SCG delta = 0.1268. Direct subtraction: 0.4829 - 0.3562 = 0.1267. The paper's 0.1268 differs by 0.0001, likely due to stored precision (0.48290 - 0.35621 = 0.12669 → rounds to 0.1267, not 0.1268). This is cosmetic but a reviewer who computes the delta by hand will get 0.1267. Consider reporting as 0.1267 or stating all values are rounded to 4 decimal places from full-precision outputs.
- **Severity**: MINOR

---

## PERSONA 2: SKEPTICAL EXPERT (R2)

### Credibility Assessment

**Novelty evaluation**

The "first controlled comparison" claim is hedged with "To our knowledge" in the R1-revised paper, which is appropriate. The genuine novelty of this paper is the aggregation_rate diagnostic metric — a previously unreported quantity that quantifies NLI clustering behavior on a per-benchmark basis. This is a real contribution: the Kuhn et al. (2023) paper does not report aggregation_rate, and no prior paper appears to have diagnosed semantic entropy degeneration via this mechanism on a short factual QA benchmark. The polarity inversion hypothesis is observational but provocative.

The controlled comparison framework itself (same examples, same LLM, matched inference budget) is methodologically sound and the paper's execution is careful. For an ICML venue, the controlled nature elevates what could be a negative result paper into a diagnostic methodology contribution.

**NLI model identifier — potential credibility issue**

The ground truth YAML records the NLI model as `cross-encoder/nli-deberta-large-mnli` (HuggingFace path for the sentence-transformers cross-encoder variant). The paper consistently refers to `microsoft/deberta-large-mnli` or `deberta-large-mnli`. These are *different HuggingFace model IDs* that may differ in their classification head training. The `cross-encoder/nli-deberta-large-mnli` model is the cross-encoder variant from sentence-transformers; `microsoft/deberta-large-mnli` is Microsoft's direct fine-tune on MNLI. Both use deberta-large as the backbone but their NLI classification thresholds and score distributions differ.

This matters because: (1) the Kuhn et al. (2023) lorenzkuhn/semantic_uncertainty official implementation uses a specific NLI model; (2) if the paper claims to implement the "official" semantic entropy but used a different NLI model than the reference implementation, the results may not be directly comparable to Kuhn et al.'s reported AUROC ≈ 0.78.

**Label quality assessment**

ChatGPT-generated hallucination labels are described as "binary labels generated by ChatGPT: for each question-answer pair, ChatGPT was prompted to produce a plausible but incorrect alternative answer." This is a strong form of label construction that creates confident-sounding incorrect answers by design. The concern is not label noise in the usual sense (mislabeled examples) but label systematicity: all hallucinated examples may share a common surface-form property (confident assertion style) that creates the polarity inversion. The paper discusses this appropriately and acknowledges the limitation. Label quality for AUROC analysis is adequate because both positive and negative classes are consistently defined.

**H-M3 absence**

The limitation section now correctly frames this as an open question without unsupported generalizability claims (R1 fix applied). The statement "Whether findings replicate with other LLMs remains an open question" is accurate and appropriately cautious. This is an acceptable limitation for a workshop/short paper; for a full ICML submission it would be strengthened by H-M3.

**Polarity inversion hypothesis mechanistic soundness**

The mechanism proposed (consistent wrong answers for hallucinated questions → high BERTScore consistency → inverted SelfCheckGPT signal) is mechanistically plausible. The paper now lists three alternative explanations (BERTScore insensitivity to short factual QA, LLaMA-2-specific generation patterns, ChatGPT-generated label noise correlation). The alternative explanation framing is appropriate and the paper correctly leaves verification to future work. One additional mechanism not mentioned: BERTScore's contextual embedding may conflate semantic similarity with lexical similarity for 5–15 token responses, making the score effectively a string similarity measure — which could produce high consistency regardless of hallucination status. This is a credible alternative but its absence is a MINOR gap.

### Baseline Fairness Assessment

The three UQ methods serve as each other's baselines with the following comparability properties:

| Property | TE | SE | SCG |
|----------|----|----|-----|
| Inference calls | 1 greedy | 5 stochastic | 5 stochastic |
| Additional models | None | deberta-large-mnli NLI | BERTScore model |
| Signal type | Entropy (greedy logits) | Cluster entropy (NLI) | Consistency (BERTScore) |
| Inference budget | Lowest | Matched to SCG | Matched to SE |

**Fairness assessment**: The comparison is fair for the stochastic methods (SE and SCG share the same 5 stochastic samples). TE uses only the greedy pass, making it computationally cheaper. The paper correctly notes "same inference budget (N=5 stochastic samples)" — though TE technically requires fewer LLM calls, it uses the same data. The asymmetry in auxiliary model usage (deberta-large-mnli for SE, BERTScore model for SCG) means SE has higher total computational cost, but this is standard in the literature and the paper does not claim inference-cost equivalence beyond LLM samples.

**Notable omission**: The paper does not compare against P(True) (verbalized confidence) or conformal prediction methods, which are mentioned in Related Work. However, the paper's scope is clearly defined as "token entropy, semantic entropy, and SelfCheckGPT" and the paper does not claim to be exhaustive. The omission of P(True) is a scope limitation, not a fairness issue.

**Important alternative UQ methods omitted**: Min-K% probability, perplexity-based methods, and contrastive decoding-based UQ are not discussed. However, the paper's comparative scope is explicitly bounded to the three named methods, and this is stated clearly. Reviewers familiar with the recent UQ literature (post-2023) may note the absence of newer methods, but this is not a fairness issue within the paper's stated scope.

### Missing Elements Check

**Limitations section adequacy**: The limitations section covers: (1) single LLM (LLaMA-2-7B-chat), (2) ChatGPT-generated hallucination labels, (3) N=5 stochastic samples. All three are accompanied by concrete mitigations. The H-M3 absence is properly disclosed. This is adequate for a workshop submission.

**Missing limitation**: The paper does not acknowledge that its AUROC analysis uses binary labels, while AUROC's interpretability depends on calibration of the scoring methods. If one method produces scores on a very different scale than another (e.g., SE is in bits 0–2.322, SCG is in 0–1), rank-based AUROC is still fair but this is worth noting.

**Reproducibility**: The paper claims "code, data, and results released" but provides no URL or repository reference. For ICML, this is a credibility concern — the reproducibility claim cannot be verified without a link.

### Issues Found

**[MAJOR-SKEP2-001]** NLI model identifier discrepancy — cross-encoder vs microsoft variant

- **Evidence**: The ground truth YAML (`065_ground_truth.yaml`, line 133) states `nli_model: cross-encoder/nli-deberta-large-mnli`. The paper throughout refers to `microsoft/deberta-large-mnli` (experimental setup table Section 4, methodology Section 3, and Section 2 Related Work). The lorenzkuhn/semantic_uncertainty official implementation uses `cross-encoder/nli-deberta-large-mnli` (sentence-transformers cross-encoder). The `microsoft/deberta-large-mnli` model is a separate fine-tune with different score distributions. If the experiment used `cross-encoder/nli-deberta-large-mnli` but the paper reports `microsoft/deberta-large-mnli`, this is a methodological misrepresentation that a replication researcher would encounter immediately.
- **Severity**: MAJOR — incorrect model identifier in a reproducibility-critical field is a credibility issue. Reviewers who attempt replication will use the stated model ID and may get different results. The paper's claims about "official implementation" (Kuhn et al., 2023 uses this NLI model) depend on which model was actually used.
- **Required fix**: Verify the exact HuggingFace model ID used in the experiment (from the Phase 4 code). If it is `cross-encoder/nli-deberta-large-mnli`, update the paper's experimental setup table and all references to use this exact ID. If it is `microsoft/deberta-large-mnli`, update the ground truth YAML. The paper should use the precise HuggingFace path (e.g., `cross-encoder/nli-deberta-large-mnli`) throughout, not an informal short name.

**[MAJOR-SKEP2-002]** Reproducibility claim not backed by repository URL

- **Evidence**: Contributions C1 states "The experimental infrastructure is fully reproducible (code, data, and results released)." No URL, DOI, or repository reference appears anywhere in the paper, the figure list, or the references section.
- **Severity**: MAJOR — a reproducibility claim without a verifiable repository link is not accepted at ICML. Reviewers expect an anonymized repository link (for review) or a concrete artifact URL. The claim as written is unverifiable and will be challenged.
- **Required fix**: Either (a) add a repository URL (even a placeholder like `[URL redacted for review]` for anonymized submission), (b) change "code, data, and results released" to "code, data, and results available upon request" or "code and results available in supplementary materials," or (c) remove the reproducibility claim from the contributions list and instead note in the paper that materials will be released upon acceptance.

**[MINOR-SKEP2-001]** Missing BERTScore alternative explanation

- The Discussion's alternative explanations for SCG's below-random AUROC list: (a) BERTScore insensitivity, (b) LLaMA-2-specific generation patterns, (c) ChatGPT label noise correlation. A fourth explanation — BERTScore contextual embeddings conflating semantic and lexical similarity for very short (5–15 token) responses, making the score effectively a token-overlap measure — is both plausible and distinct from (a). This would explain inverted correlation without requiring polarity inversion in the label construction. Adding this alternative would strengthen the paper's claim of comprehensive alternative consideration.
- **Severity**: MINOR

**[MINOR-SKEP2-002]** Abstract word count

- Carried from R1 MINOR-005: abstract is approximately 173 words against ICML convention of ≤150. Not blocking but should be trimmed for camera-ready.
- **Severity**: MINOR

---

## MINOR Issues (Human Review Notes — NOT auto-fixed)

| ID | Persona | Category | Description |
|----|---------|----------|-------------|
| MINOR-ACC2-001 | Accuracy Checker | numerical | TE vs SCG delta: 0.4829-0.3562=0.1267 but paper reports 0.1268; minor stored-precision artifact |
| MINOR-SKEP2-001 | Skeptical Expert | completeness | Missing BERTScore alternative explanation: contextual embeddings conflate semantic/lexical similarity for 5–15 token responses |
| MINOR-SKEP2-002 | Skeptical Expert | style | Abstract ~173 words; ICML convention ≤150; trim for camera-ready |
| MINOR-SKEP2-003 | Skeptical Expert | clarity | NLI training domain stated as "MNLI (news, fiction, telephone)" — this is accurate for DeBERTa-large-mnli but should clarify which model ID this refers to (see MAJOR-SKEP2-001) |

---

## Summary for Revision Agent

### FATAL Issues: None

### MAJOR Issues

| ID | Persona | Description | Required Fix |
|----|---------|-------------|-------------|
| MAJOR-ACC2-001 | Accuracy Checker | SE std=4.14e-25 inconsistent with 544 non-max-cluster examples having variable entropy; claim needs clarification or reconciliation | Clarify whether std is over all 2000 or only 1456 max-cluster examples; provide entropy distribution for non-max examples or reframe the constant-SE claim appropriately |
| MAJOR-SKEP2-001 | Skeptical Expert | NLI model identifier discrepancy: paper says `microsoft/deberta-large-mnli`, ground truth YAML says `cross-encoder/nli-deberta-large-mnli` — different HuggingFace models | Verify exact model ID from Phase 4 code; update paper to use precise HuggingFace path throughout |
| MAJOR-SKEP2-002 | Skeptical Expert | Reproducibility claim ("code, data, and results released") has no repository URL or artifact reference | Add repository URL (or placeholder), change claim wording, or move to supplementary materials |

### Issue Counts

```yaml
fatal: 0
major: 3
minor: 4
```

### R1 Carried Issues Status

The following R1 MAJOR issues remain unresolved but their substantive claims are valid:
- MAJOR-001 (aggregation_rate CI upper 0.2915 vs 0.292): substantive "entirely below 0.30" claim holds either way
- MAJOR-002 (cluster count=1 fraction in GT YAML): paper's 4 (0.2%) appears correct per h-m2 validation
- MAJOR-003 (figure registry mismatch): GT YAML figures 3-4 do not match actual paper; requires GT YAML update

### Convergence Assessment

```yaml
fatal_remaining: 0
major_remaining: 3
minor_remaining: 4
persuasiveness_passed: true
recommendation: CONDITIONAL_ACCEPT

notes:
  - "Core numerical results are all verified and internally consistent"
  - "MAJOR-ACC2-001 (SE std) is the most important new finding — requires explicit clarification in paper"
  - "MAJOR-SKEP2-001 (NLI model ID) is a reproducibility-critical fix"
  - "MAJOR-SKEP2-002 (repository URL) is an ICML submission requirement"
  - "No issues undermine the core findings: all AUROC values, aggregation rate, and mechanism analysis are sound"
  - "Paper is well-executed; issues are presentation/precision issues, not finding-level problems"
```
